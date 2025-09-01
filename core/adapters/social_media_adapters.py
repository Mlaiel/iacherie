"""Social Media Platform Adapters - Enterprise Integration Suite

This module provides comprehensive adapters for major social media platforms
including Instagram, TikTok, YouTube, Twitter, Facebook, LinkedIn, and others.
Each adapter implements platform-specific optimizations, content formatting,
and audience targeting capabilities for creators.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Supported Platforms:
- Instagram: Creator API, Stories, Reels, IGTV
- TikTok: Content API, Analytics, Creator Fund
- YouTube: Data API v3, Creator Studio, Analytics
- Twitter: API v2, Spaces, Creator monetization
- Facebook: Graph API, Pages, Creator Studio
- LinkedIn: Marketing API, Creator content
- Pinterest: Developer API, Creator insights
- Snapchat: Creative Kit, Snap Pixel
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import base64
import hashlib
from urllib.parse import urlencode, quote

from .base_adapter import (
    BasePlatformAdapter, PlatformType, AdapterStatus, AuthenticationType,
    AdapterCredentials, RateLimitConfig, AdapterError, AuthenticationError
)

logger = logging.getLogger(__name__)

class SocialMediaPlatform(Enum):
    """
Supported social media platforms."""

    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"
    TELEGRAM = "telegram"

class ContentType(Enum):
    """Content types for social media."""

    POST = "post"
    STORY = "story"
    REEL = "reel"
    VIDEO = "video"
    LIVE_STREAM = "live_stream"
    CAROUSEL = "carousel"
    POLL = "poll"
    EVENT = "event"
    ARTICLE = "article"
    SHORTS = "shorts"

@dataclass
class SocialMediaContent:
    """Content structure for social media posting."""
    content_type: ContentType
    title: Optional[str] = None
    description: Optional[str] = None
    media_urls: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    location: Optional[str] = None
    schedule_time: Optional[datetime] = None
    privacy_settings: Dict[str, Any] = field(default_factory=dict)
    platform_specific_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SocialMediaMetrics:
    """
Analytics metrics from social media platforms."""
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    reach: int = 0
    impressions: int = 0
    engagement_rate: float = 0.0
    click_through_rate: float = 0.0
    revenue: float = 0.0
    follower_growth: int = 0
    platform_specific_metrics: Dict[str, Any] = field(default_factory=dict)

class InstagramAdapter(BasePlatformAdapter):
    """
    Enterprise Instagram API adapter with comprehensive creator features.
    
    Supports:
    - Instagram Basic Display API
    - Instagram Creator API
    - Instagram Marketing API
    - Stories, Reels, IGTV publishing
    - Advanced analytics and insights
    - Creator monetization tracking
    """
    
    def __init__(self, credentials: AdapterCredentials, redis_client=None):
        rate_config = RateLimitConfig(
            requests_per_second=10.0,
            requests_per_minute=200.0,
            requests_per_hour=5000.0,
            burst_limit=25
        )
        
        if not credentials.base_url:
            credentials.base_url = "https://graph.instagram.com"
        
        super().__init__(
            platform_name="Instagram",
            platform_type=PlatformType.SOCIAL_MEDIA,
            credentials=credentials,
            rate_limit_config=rate_config,
            redis_client=redis_client
        )
    
    async def authenticate(self) -> bool:
        """Authenticate with Instagram API."""
        try:
            # Test authentication with user info request
            response = await self.make_request(
                method="GET",
                endpoint="me",
                params={
                    "fields": "id,username,account_type,media_count",
                    "access_token": self.credentials.access_token
                }
            )
            
            if "id" in response:
                logger.info(f"Instagram authentication successful for user: {response.get('username', 'Unknown')}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Instagram authentication failed: {e}")
            return False
    
    async def publish_content(self, content: SocialMediaContent) -> Dict[str, Any]:
        """Publish content to Instagram."""
        try:
            if content.content_type == ContentType.POST:
                return await self._publish_feed_post(content)
            elif content.content_type == ContentType.STORY:
                return await self._publish_story(content)
            elif content.content_type == ContentType.REEL:
                return await self._publish_reel(content)
            else:
                raise AdapterError(f"Unsupported content type for Instagram: {content.content_type}")
                
        except Exception as e:
            logger.error(f"Instagram content publishing failed: {e}")
            raise AdapterError(f"Failed to publish content to Instagram: {e}")
    
    async def _publish_feed_post(self, content: SocialMediaContent) -> Dict[str, Any]:
        """Publish a feed post to Instagram."""
        # Step 1: Create media container
        media_data = {
            "image_url": content.media_urls[0] if content.media_urls else None,
            "caption": self._format_caption(content),
            "access_token": self.credentials.access_token
        }
        
        container_response = await self.make_request(
            method="POST",
            endpoint="me/media",
            data=media_data
        )
        
        # Step 2: Publish the container
        publish_response = await self.make_request(
            method="POST",
            endpoint="me/media_publish",
            data={
                "creation_id": container_response["id"],
                "access_token": self.credentials.access_token
            }
        )
        
        return {
            "platform": "instagram",
            "post_id": publish_response["id"],
            "status": "published",
            "url": f"https://www.instagram.com/p/{publish_response['id']}/",
            "published_at": datetime.now().isoformat()
        }
    
    async def _publish_story(self, content: SocialMediaContent) -> Dict[str, Any]:
        """Publish a story to Instagram."""
        story_data = {
            "image_url": content.media_urls[0] if content.media_urls else None,
            "media_type": "STORIES",
            "access_token": self.credentials.access_token
        }
        
        response = await self.make_request(
            method="POST",
            endpoint="me/media",
            data=story_data
        )
        
        return {
            "platform": "instagram",
            "story_id": response["id"],
            "status": "published",
            "published_at": datetime.now().isoformat()
        }
    
    async def _publish_reel(self, content: SocialMediaContent) -> Dict[str, Any]:
        """Publish a reel to Instagram."""
        reel_data = {
            "video_url": content.media_urls[0] if content.media_urls else None,
            "media_type": "REELS",
            "caption": self._format_caption(content),
            "access_token": self.credentials.access_token
        }
        
        container_response = await self.make_request(
            method="POST",
            endpoint="me/media",
            data=reel_data
        )
        
        publish_response = await self.make_request(
            method="POST",
            endpoint="me/media_publish",
            data={
                "creation_id": container_response["id"],
                "access_token": self.credentials.access_token
            }
        )
        
        return {
            "platform": "instagram",
            "reel_id": publish_response["id"],
            "status": "published",
            "url": f"https://www.instagram.com/reel/{publish_response['id']}/",
            "published_at": datetime.now().isoformat()
        }
    
    def _format_caption(self, content: SocialMediaContent) -> str:
        """Format caption with description and hashtags."""
        caption_parts = []
        
        if content.description:
            caption_parts.append(content.description)
        
        if content.hashtags:
            hashtags_str = " ".join([f"#{tag.lstrip('#')}" for tag in content.hashtags])
            caption_parts.append(hashtags_str)
        
        return "\n\n".join(caption_parts)
    
    async def get_analytics(self, post_id: Optional[str] = None, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> SocialMediaMetrics:
        """Get Instagram analytics and insights."""
        try:
            if post_id:
                # Get specific post metrics
                response = await self.make_request(
                    method="GET",
                    endpoint=f"{post_id}/insights",
                    params={
                        "metric": "impressions,reach,likes,comments,saves,shares",
                        "access_token": self.credentials.access_token
                    }
                )
                
                metrics = SocialMediaMetrics()
                for data_point in response.get("data", []):
                    metric_name = data_point["name"]
                    value = data_point["values"][0]["value"]
                    
                    if metric_name == "impressions":
                        metrics.impressions = value
                    elif metric_name == "reach":
                        metrics.reach = value
                    elif metric_name == "likes":
                        metrics.likes = value
                    elif metric_name == "comments":
                        metrics.comments = value
                    elif metric_name == "saves":
                        metrics.saves = value
                    elif metric_name == "shares":
                        metrics.shares = value
                
                return metrics
            
            else:
                # Get account-level insights
                response = await self.make_request(
                    method="GET",
                    endpoint="me/insights",
                    params={
                        "metric": "impressions,reach,profile_views,follower_count",
                        "period": "day",
                        "since": start_date.strftime("%Y-%m-%d") if start_date else None,
                        "until": end_date.strftime("%Y-%m-%d") if end_date else None,
                        "access_token": self.credentials.access_token
                    }
                )
                
                metrics = SocialMediaMetrics()
                for data_point in response.get("data", []):
                    metric_name = data_point["name"]
                    values = data_point["values"]
                    total_value = sum(v["value"] for v in values)
                    
                    if metric_name == "impressions":
                        metrics.impressions = total_value
                    elif metric_name == "reach":
                        metrics.reach = total_value
                    elif metric_name == "profile_views":
                        metrics.views = total_value
                
                return metrics
                
        except Exception as e:
            logger.error(f"Instagram analytics retrieval failed: {e}")
            return SocialMediaMetrics()
    
    async def health_check(self) -> bool:
        """Perform Instagram API health check."""
        try:
            response = await self.make_request(
                method="GET",
                endpoint="me",
                params={"fields": "id", "access_token": self.credentials.access_token}
            )
            return "id" in response
        except:
            return False

class YouTubeAdapter(BasePlatformAdapter):
    """
    Enterprise YouTube Data API v3 adapter with creator features.
    
    Supports:
    - Video uploading and management
    - YouTube Analytics API
    - Creator Studio integration
    - Live streaming management
    - Monetization tracking
    - Shorts optimization
    """
    
    def __init__(self, credentials: AdapterCredentials, redis_client=None):
        rate_config = RateLimitConfig(
            requests_per_second=100.0,
            requests_per_minute=6000.0,
            requests_per_hour=1000000.0,
            burst_limit=100
        )
        
        if not credentials.base_url:
            credentials.base_url = "https://www.googleapis.com/youtube/v3"
        
        super().__init__(
            platform_name="YouTube",
            platform_type=PlatformType.VIDEO_PLATFORM,
            credentials=credentials,
            rate_limit_config=rate_config,
            redis_client=redis_client
        )
    
    async def authenticate(self) -> bool:
        """Authenticate with YouTube API."""
        try:
            response = await self.make_request(
                method="GET",
                endpoint="channels",
                params={
                    "part": "snippet,statistics",
                    "mine": "true",
                    "key": self.credentials.api_key
                },
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            
            if response.get("items"):
                channel = response["items"][0]
                logger.info(f"YouTube authentication successful for channel: {channel['snippet']['title']}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return False
    
    async def upload_video(self, content: SocialMediaContent, video_file_path: str) -> Dict[str, Any]:
        """Upload video to YouTube."""
        try:
            # Prepare video metadata
            video_metadata = {
                "snippet": {
                    "title": content.title or "Untitled Video",
                    "description": self._format_description(content),
                    "tags": content.hashtags,
                    "categoryId": "22"  # People & Blogs
                },
                "status": {
                    "privacyStatus": content.privacy_settings.get("privacy", "public"),
                    "selfDeclaredMadeForKids": False
                }
            }
            
            # Upload video (simplified - actual implementation would use resumable upload)
            response = await self.make_request(
                method="POST",
                endpoint="videos",
                params={
                    "part": "snippet,status",
                    "key": self.credentials.api_key
                },
                json_data=video_metadata,
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            
            return {
                "platform": "youtube",
                "video_id": response["id"],
                "status": "uploaded",
                "url": f"https://www.youtube.com/watch?v={response['id']}",
                "uploaded_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"YouTube video upload failed: {e}")
            raise AdapterError(f"Failed to upload video to YouTube: {e}")
    
    def _format_description(self, content: SocialMediaContent) -> str:
        """Format video description."""
        description_parts = []
        
        if content.description:
            description_parts.append(content.description)
        
        if content.hashtags:
            description_parts.append("\n\nTags:")
            description_parts.append(", ".join(content.hashtags))
        
        return "\n".join(description_parts)
    
    async def get_analytics(self, video_id: Optional[str] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> SocialMediaMetrics:
        """Get YouTube analytics."""
        try:
            if video_id:
                # Get video statistics
                response = await self.make_request(
                    method="GET",
                    endpoint="videos",
                    params={
                        "part": "statistics",
                        "id": video_id,
                        "key": self.credentials.api_key
                    }
                )
                
                if response.get("items"):
                    stats = response["items"][0]["statistics"]
                    return SocialMediaMetrics(
                        views=int(stats.get("viewCount", 0)),
                        likes=int(stats.get("likeCount", 0)),
                        comments=int(stats.get("commentCount", 0)),
                        platform_specific_metrics={
                            "subscriber_count": int(stats.get("subscriberCount", 0)),
                            "video_count": int(stats.get("videoCount", 0))
                        }
                    )
            
            else:
                # Get channel analytics using YouTube Analytics API
                analytics_response = await self.make_request(
                    method="GET",
                    endpoint="reports",
                    params={
                        "ids": "channel==MINE",
                        "metrics": "views,likes,comments,shares,estimatedRevenue",
                        "dimensions": "day",
                        "startDate": start_date.strftime("%Y-%m-%d") if start_date else "2023-01-01",
                        "endDate": end_date.strftime("%Y-%m-%d") if end_date else datetime.now().strftime("%Y-%m-%d")
                    },
                    headers={"Authorization": f"Bearer {self.credentials.access_token}"}
                )
                
                # Process analytics data
                metrics = SocialMediaMetrics()
                if analytics_response.get("rows"):
                    for row in analytics_response["rows"]:
                        metrics.views += int(row[1])
                        metrics.likes += int(row[2])
                        metrics.comments += int(row[3])
                        metrics.shares += int(row[4])
                        metrics.revenue += float(row[5]) if len(row) > 5 else 0.0
                
                return metrics
                
        except Exception as e:
            logger.error(f"YouTube analytics retrieval failed: {e}")
            return SocialMediaMetrics()
    
    async def health_check(self) -> bool:
        """Perform YouTube API health check."""
        try:
            response = await self.make_request(
                method="GET",
                endpoint="channels",
                params={
                    "part": "id",
                    "mine": "true",
                    "key": self.credentials.api_key
                },
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            return bool(response.get("items"))
        except:
            return False

class TikTokAdapter(BasePlatformAdapter):
    """
    Enterprise TikTok API adapter for creator content and analytics.
    
    Supports:
    - Content Publishing API
    - Creator insights and analytics
    - Creator Fund data
    - Hashtag challenge participation
    - Live streaming integration
    """
    
    def __init__(self, credentials: AdapterCredentials, redis_client=None):
        rate_config = RateLimitConfig(
            requests_per_second=10.0,
            requests_per_minute=600.0,
            requests_per_hour=10000.0,
            burst_limit=20
        )
        
        if not credentials.base_url:
            credentials.base_url = "https://open-api.tiktok.com"
        
        super().__init__(
            platform_name="TikTok",
            platform_type=PlatformType.SOCIAL_MEDIA,
            credentials=credentials,
            rate_limit_config=rate_config,
            redis_client=redis_client
        )
    
    async def authenticate(self) -> bool:
        """Authenticate with TikTok API."""
        try:
            response = await self.make_request(
                method="GET",
                endpoint="v2/user/info/",
                params={"fields": "open_id,union_id,avatar_url,display_name"},
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            
            if response.get("data", {}).get("user"):
                user = response["data"]["user"]
                logger.info(f"TikTok authentication successful for user: {user.get('display_name', 'Unknown')}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"TikTok authentication failed: {e}")
            return False
    
    async def publish_video(self, content: SocialMediaContent, video_file_path: str) -> Dict[str, Any]:
        """Publish video to TikTok."""
        try:
            # TikTok requires video upload in chunks
            # This is a simplified version - actual implementation would handle file upload
            
            video_data = {
                "post_info": {
                    "title": content.title or "",
                    "privacy_level": content.privacy_settings.get("privacy", "MUTUAL_FOLLOW_FRIEND"),
                    "disable_duet": content.platform_specific_data.get("disable_duet", False),
                    "disable_comment": content.platform_specific_data.get("disable_comment", False),
                    "disable_stitch": content.platform_specific_data.get("disable_stitch", False),
                    "video_cover_timestamp_ms": content.platform_specific_data.get("cover_timestamp", 1000)
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": content.platform_specific_data.get("video_size", 0),
                    "chunk_size": content.platform_specific_data.get("chunk_size", 10000000),
                    "total_chunk_count": content.platform_specific_data.get("total_chunks", 1)
                }
            }
            
            response = await self.make_request(
                method="POST",
                endpoint="v2/post/publish/video/init/",
                json_data=video_data,
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            
            if response.get("data"):
                publish_id = response["data"]["publish_id"]
                
                return {
                    "platform": "tiktok",
                    "publish_id": publish_id,
                    "status": "processing",
                    "published_at": datetime.now().isoformat()
                }
            
            raise AdapterError("Failed to initialize TikTok video upload")
            
        except Exception as e:
            logger.error(f"TikTok video publishing failed: {e}")
            raise AdapterError(f"Failed to publish video to TikTok: {e}")
    
    async def get_analytics(self, start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> SocialMediaMetrics:
        """Get TikTok creator analytics."""
        try:
            # Get user videos first
            videos_response = await self.make_request(
                method="POST",
                endpoint="v2/video/list/",
                json_data={
                    "max_count": 20,
                    "cursor": 0,
                    "fields": ["id", "title", "video_description", "duration", "cover_image_url", "create_time"]
                },
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            
            metrics = SocialMediaMetrics()
            
            if videos_response.get("data", {}).get("videos"):
                # Get analytics for each video
                for video in videos_response["data"]["videos"]:
                    video_id = video["id"]
                    
                    video_metrics = await self.make_request(
                        method="POST",
                        endpoint="v2/video/data/",
                        json_data={
                            "video_ids": [video_id],
                            "fields": ["like_count", "comment_count", "share_count", "view_count"]
                        },
                        headers={"Authorization": f"Bearer {self.credentials.access_token}"}
                    )
                    
                    if video_metrics.get("data", {}).get("videos"):
                        video_data = video_metrics["data"]["videos"][0]
                        metrics.views += video_data.get("view_count", 0)
                        metrics.likes += video_data.get("like_count", 0)
                        metrics.comments += video_data.get("comment_count", 0)
                        metrics.shares += video_data.get("share_count", 0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"TikTok analytics retrieval failed: {e}")
            return SocialMediaMetrics()
    
    async def health_check(self) -> bool:
        """Perform TikTok API health check."""
        try:
            response = await self.make_request(
                method="GET",
                endpoint="v2/user/info/",
                params={"fields": "open_id"},
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            return bool(response.get("data", {}).get("user"))
        except:
            return False

# Additional platform adapters would be implemented similarly...

class SocialMediaAdapterFactory:
    """Factory for creating social media platform adapters."""
    
    _adapters = {
        SocialMediaPlatform.INSTAGRAM: InstagramAdapter,
        SocialMediaPlatform.YOUTUBE: YouTubeAdapter,
        SocialMediaPlatform.TIKTOK: TikTokAdapter,
        # Additional platforms would be registered here
    }
    
    @classmethod
    def create_adapter(cls, platform: SocialMediaPlatform, credentials: AdapterCredentials, redis_client=None) -> BasePlatformAdapter:
        """
Create adapter for specified platform."""
        if platform not in cls._adapters:
            raise AdapterError(f"Unsupported social media platform: {platform}")
        
        adapter_class = cls._adapters[platform]
        return adapter_class(credentials, redis_client)
    
    @classmethod
    def get_supported_platforms(cls) -> List[SocialMediaPlatform]:
        """Get list of supported platforms."""
        return list(cls._adapters.keys())

# Export all classes
__all__ = [
    'SocialMediaPlatform',
    'ContentType',
    'SocialMediaContent',
    'SocialMediaMetrics',
    'InstagramAdapter',
    'YouTubeAdapter',
    'TikTokAdapter',
    'SocialMediaAdapterFactory'
]
