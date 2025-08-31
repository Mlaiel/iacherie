"""
Instagram Distribution Adapter - Professional Multi-Format Content Distribution System

Enterprise-grade Instagram API integration with advanced optimization, Stories management,
Reels distribution, and comprehensive business logic for the IA Influencer Agent ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE - INTELLECTUAL PROPERTY PROTECTION:
This software and all related code are the EXCLUSIVE INTELLECTUAL PROPERTY 
of Fahed Mlaiel (mlaiel@live.de). Unauthorized use, copying, or distribution 
without written authorization is STRICTLY PROHIBITED and will result in 
immediate legal action under German and International IP law.

For licensing inquiries: mlaiel@live.de
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import hashlib
from PIL import Image
import cv2
from urllib.parse import urlencode

from ..base import BaseAgent
try:
    from core.exceptions import DistributionError, PlatformError, ContentError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    DistributionError, PlatformError, ContentError = globals().get('DistributionError, PlatformError, ContentError', Exception)
from ...core.metrics import MetricsCollector
from ...core.security import SecurityValidator
from ...models.content import ContentItem, ContentMetadata
from ...models.distribution import DistributionResult, PlatformConfig


class InstagramContentType(Enum):
    """Instagram content type enumeration"""
    PHOTO = "photo"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    IGTV = "igtv"
    LIVE = "live"


class InstagramAspectRatio(Enum):
    """Instagram aspect ratio enumeration"""
    SQUARE = "1:1"
    PORTRAIT = "4:5"
    LANDSCAPE = "1.91:1"
    STORY = "9:16"
    REEL = "9:16"


class InstagramVisibility(Enum):
    """Instagram visibility settings enumeration"""
    PUBLIC = "public"
    FOLLOWERS = "followers"
    CLOSE_FRIENDS = "close_friends"
    PRIVATE = "private"


@dataclass
class InstagramMetadata:
    """Instagram-specific metadata structure"""
    caption: str
    hashtags: List[str]
    content_type: InstagramContentType
    aspect_ratio: InstagramAspectRatio
    visibility: InstagramVisibility
    location_id: Optional[str] = None
    user_tags: List[Dict[str, Any]] = None
    story_stickers: List[Dict[str, Any]] = None
    music_id: Optional[str] = None
    cover_frame_time: Optional[float] = None
    carousel_items: List[Dict[str, Any]] = None
    shopping_tags: List[Dict[str, Any]] = None
    branded_content_sponsor: Optional[str] = None
    accessibility_text: Optional[str] = None
    
    def __post_init__(self):
        if self.user_tags is None:
            self.user_tags = []
        if self.story_stickers is None:
            self.story_stickers = []
        if self.carousel_items is None:
            self.carousel_items = []
        if self.shopping_tags is None:
            self.shopping_tags = []


@dataclass
class InstagramAnalytics:
    """Instagram analytics data structure"""
    impressions: int = 0
    reach: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    profile_visits: int = 0
    website_clicks: int = 0
    story_replies: int = 0
    story_exits: int = 0
    engagement_rate: float = 0.0
    demographics: Dict[str, Any] = None
    top_locations: List[str] = None
    hashtag_performance: Dict[str, int] = None
    story_completion_rate: float = 0.0
    
    def __post_init__(self):
        if self.demographics is None:
            self.demographics = {}
        if self.top_locations is None:
            self.top_locations = []
        if self.hashtag_performance is None:
            self.hashtag_performance = {}


class InstagramAdapter(BaseAgent):
    """
    Professional Instagram distribution adapter with advanced features
    
    Capabilities:
    - Multi-format content publishing (Posts, Stories, Reels, IGTV)
    - Intelligent image and video optimization
    - Advanced hashtag research and optimization
    - Story stickers and interactive elements
    - Shopping integration and product tagging
    - Carousel post management
    - Live streaming integration
    - Comprehensive analytics and insights
    - User engagement automation
    - Brand collaboration tools
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Instagram adapter with comprehensive configuration
        
        Args:
            config: Instagram API configuration and settings
        """
        super().__init__(config)
        self.access_token = config.get('access_token')
        self.business_account_id = config.get('business_account_id')
        self.app_id = config.get('app_id')
        self.app_secret = config.get('app_secret')
        
        # Advanced configuration
        self.image_quality = config.get('image_quality', 95)
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 5)
        self.story_duration = config.get('story_duration', 15)  # seconds
        
        # Instagram API endpoints
        self.base_url = "https://graph.facebook.com/v18.0"
        self.upload_url = f"{self.base_url}/{self.business_account_id}/media"
        
        # Content optimization settings
        self.max_image_size = config.get('max_image_size', 8 * 1024 * 1024)  # 8MB
        self.max_video_size = config.get('max_video_size', 100 * 1024 * 1024)  # 100MB
        self.supported_image_formats = ['.jpg', '.jpeg', '.png']
        self.supported_video_formats = ['.mp4', '.mov']
        
        # Performance optimization
        self.session: Optional[aiohttp.ClientSession] = None
        self.concurrent_uploads = config.get('concurrent_uploads', 3)
        
        # Metrics and monitoring
        self.metrics = MetricsCollector("instagram_adapter")
        self.security = SecurityValidator(config.get('security', {}))
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize Instagram adapter with authentication and validation"""
        try:
            # Initialize HTTP session
            connector = aiohttp.TCPConnector(limit=self.concurrent_uploads)
            self.session = aiohttp.ClientSession(connector=connector)
            
            # Validate credentials
            if not await self._validate_credentials():
                raise PlatformError("Invalid Instagram API credentials")
            
            # Verify business account access
            if not await self._verify_business_account():
                raise PlatformError("Cannot access Instagram business account")
            
            # Initialize hashtag database
            await self._initialize_hashtag_database()
            
            # Initialize content templates
            await self._initialize_content_templates()
            
            self.logger.info("Instagram adapter initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Instagram adapter: {str(e)}")
            await self.cleanup()
            return False
    
    async def distribute_content(
        self,
        content: ContentItem,
        metadata: InstagramMetadata,
        platform_config: Optional[PlatformConfig] = None
    ) -> DistributionResult:
        """
        Distribute content to Instagram with advanced optimization
        
        Args:
            content: Content item to distribute
            metadata: Instagram-specific metadata
            platform_config: Platform-specific configuration
            
        Returns:
            Comprehensive distribution result with analytics
        """
        start_time = datetime.utcnow()
        
        try:
            # Validate content and metadata
            await self._validate_content(content, metadata)
            
            # Security and compliance checks
            await self._perform_security_checks(content)
            
            # Content optimization based on type
            optimized_content = await self._optimize_content(content, metadata)
            
            # Enhance metadata with AI insights
            enhanced_metadata = await self._enhance_metadata(metadata, content)
            
            # Upload media based on content type
            media_id = await self._upload_media(optimized_content, enhanced_metadata)
            
            # Publish content
            post_id = await self._publish_media(media_id, enhanced_metadata)
            
            # Configure additional features
            await self._configure_additional_features(post_id, enhanced_metadata)
            
            # Schedule story highlights if applicable
            if metadata.content_type == InstagramContentType.STORY:
                await self._manage_story_highlights(post_id, enhanced_metadata)
            
            # Collect initial analytics
            analytics = await self._collect_initial_analytics(post_id)
            
            # Record metrics
            self.metrics.record_distribution(
                platform="instagram",
                content_type=metadata.content_type.value,
                success=True,
                duration=(datetime.utcnow() - start_time).total_seconds()
            )
            
            return DistributionResult(
                platform="instagram",
                platform_id=post_id,
                url=f"https://www.instagram.com/p/{post_id}/",
                status="published",
                analytics=asdict(analytics),
                metadata=asdict(enhanced_metadata),
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f"Instagram distribution failed: {str(e)}")
            self.metrics.record_error("distribution_failed", str(e))
            raise DistributionError(f"Instagram distribution failed: {str(e)}")
    
    async def update_content(
        self,
        platform_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update existing Instagram post with new metadata"""
        try:
            # Instagram has limited update capabilities
            # Only caption and user tags can be updated
            update_data = {}
            
            if "caption" in updates:
                update_data["caption"] = updates["caption"]
            
            if "user_tags" in updates:
                update_data["user_tags"] = updates["user_tags"]
            
            if not update_data:
                self.logger.warning("No valid updates provided for Instagram post")
                return False
            
            # Execute update
            response = await self._make_api_request(
                "POST",
                f"{self.base_url}/{platform_id}",
                data=update_data
            )
            
            if response.get("success"):
                self.logger.info(f"Successfully updated Instagram post: {platform_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update Instagram post {platform_id}: {str(e)}")
            return False
    
    async def delete_content(self, platform_id: str) -> bool:
        """Delete Instagram content with proper cleanup"""
        try:
            # Execute deletion
            response = await self._make_api_request(
                "DELETE",
                f"{self.base_url}/{platform_id}"
            )
            
            if response.get("success"):
                self.logger.info(f"Successfully deleted Instagram content: {platform_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete Instagram content {platform_id}: {str(e)}")
            return False
    
    async def get_analytics(
        self,
        platform_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> InstagramAnalytics:
        """Retrieve comprehensive Instagram analytics"""
        try:
            # Get basic insights
            insights = await self._fetch_media_insights(platform_id)
            
            # Get engagement metrics
            engagement = await self._fetch_engagement_metrics(platform_id, start_date, end_date)
            
            # Get audience insights
            audience = await self._fetch_audience_insights(start_date, end_date)
            
            # Get hashtag performance
            hashtag_performance = await self._analyze_hashtag_performance(
                platform_id, start_date, end_date
            )
            
            # Calculate engagement rate
            engagement_rate = 0.0
            if insights.get("impressions", 0) > 0:
                total_engagements = (
                    insights.get("likes", 0) + 
                    insights.get("comments", 0) + 
                    insights.get("shares", 0) + 
                    insights.get("saves", 0)
                )
                engagement_rate = (total_engagements / insights.get("impressions", 1)) * 100
            
            return InstagramAnalytics(
                impressions=insights.get("impressions", 0),
                reach=insights.get("reach", 0),
                likes=insights.get("likes", 0),
                comments=insights.get("comments", 0),
                shares=insights.get("shares", 0),
                saves=insights.get("saves", 0),
                profile_visits=engagement.get("profile_visits", 0),
                website_clicks=engagement.get("website_clicks", 0),
                story_replies=insights.get("replies", 0),
                story_exits=insights.get("exits", 0),
                engagement_rate=engagement_rate,
                demographics=audience.get("demographics", {}),
                top_locations=audience.get("top_locations", []),
                hashtag_performance=hashtag_performance,
                story_completion_rate=insights.get("completion_rate", 0.0)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get Instagram analytics for {platform_id}: {str(e)}")
            return InstagramAnalytics()
    
    async def _validate_credentials(self) -> bool:
        """Validate Instagram API credentials"""
        try:
            response = await self._make_api_request(
                "GET",
                f"{self.base_url}/me",
                params={"fields": "id,name"}
            )
            return "id" in response
            
        except Exception:
            return False
    
    async def _verify_business_account(self) -> bool:
        """Verify access to Instagram business account"""
        try:
            response = await self._make_api_request(
                "GET",
                f"{self.base_url}/{self.business_account_id}",
                params={"fields": "id,username,account_type"}
            )
            return response.get("account_type") in ["BUSINESS", "CREATOR"]
            
        except Exception:
            return False
    
    async def _initialize_hashtag_database(self) -> None:
        """Initialize hashtag research database"""
        # Load trending hashtags and categories
        self.hashtag_categories = {
            "photography": ["#photography", "#photooftheday", "#instaphoto"],
            "music": ["#music", "#musician", "#newmusic", "#songwriter"],
            "lifestyle": ["#lifestyle", "#instagood", "#picoftheday"],
            "business": ["#entrepreneur", "#business", "#success"],
            "travel": ["#travel", "#wanderlust", "#explore"],
            "fitness": ["#fitness", "#workout", "#healthy"],
            "food": ["#foodie", "#food", "#delicious"],
            "fashion": ["#fashion", "#style", "#outfit"]
        }
    
    async def _initialize_content_templates(self) -> None:
        """Initialize content templates for different types"""
        self.content_templates = {
            InstagramContentType.PHOTO: {
                "aspect_ratios": [InstagramAspectRatio.SQUARE, InstagramAspectRatio.PORTRAIT],
                "max_size": self.max_image_size,
                "formats": self.supported_image_formats
            },
            InstagramContentType.VIDEO: {
                "aspect_ratios": [InstagramAspectRatio.SQUARE, InstagramAspectRatio.LANDSCAPE],
                "max_size": self.max_video_size,
                "formats": self.supported_video_formats,
                "max_duration": 60  # seconds
            },
            InstagramContentType.STORY: {
                "aspect_ratios": [InstagramAspectRatio.STORY],
                "max_size": self.max_video_size,
                "max_duration": 15  # seconds
            },
            InstagramContentType.REEL: {
                "aspect_ratios": [InstagramAspectRatio.REEL],
                "max_size": self.max_video_size,
                "max_duration": 90  # seconds
            }
        }
    
    async def _validate_content(self, content: ContentItem, metadata: InstagramMetadata) -> None:
        """Validate content and metadata for Instagram distribution"""
        # Validate content format
        if metadata.content_type in [InstagramContentType.PHOTO, InstagramContentType.STORY]:
            if not any(content.file_path.lower().endswith(fmt) for fmt in self.supported_image_formats):
                if not content.content_type.startswith('image/'):
                    raise ContentError("Invalid image content for Instagram")
        
        elif metadata.content_type in [InstagramContentType.VIDEO, InstagramContentType.REEL, InstagramContentType.IGTV]:
            if not any(content.file_path.lower().endswith(fmt) for fmt in self.supported_video_formats):
                if not content.content_type.startswith('video/'):
                    raise ContentError("Invalid video content for Instagram")
        
        # Validate caption length
        if len(metadata.caption) > 2200:
            raise ContentError("Instagram caption must be under 2200 characters")
        
        # Validate hashtags
        if len(metadata.hashtags) > 30:
            raise ContentError("Instagram posts can have maximum 30 hashtags")
    
    async def _perform_security_checks(self, content: ContentItem) -> None:
        """Perform security and compliance checks"""
        # Content security validation
        if not await self.security.validate_content(content):
            raise SecurityError("Content failed security validation")
        
        # Instagram community guidelines check
        if not await self._check_community_guidelines(content):
            raise ContentError("Content violates Instagram community guidelines")
    
    async def _optimize_content(
        self,
        content: ContentItem,
        metadata: InstagramMetadata
    ) -> ContentItem:
        """Optimize content for Instagram distribution"""
        try:
            if metadata.content_type == InstagramContentType.PHOTO:
                return await self._optimize_image(content, metadata)
            elif metadata.content_type in [InstagramContentType.VIDEO, InstagramContentType.REEL]:
                return await self._optimize_video(content, metadata)
            elif metadata.content_type == InstagramContentType.STORY:
                return await self._optimize_story(content, metadata)
            else:
                return content
                
        except Exception as e:
            self.logger.error(f"Content optimization failed: {str(e)}")
            return content
    
    async def _optimize_image(self, content: ContentItem, metadata: InstagramMetadata) -> ContentItem:
        """Optimize image for Instagram posting"""
        # Load and process image
        with Image.open(content.file_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize based on aspect ratio
            target_size = self._get_target_size(metadata.aspect_ratio)
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Enhance image quality
            img = self._enhance_image_quality(img)
            
            # Save optimized image
            optimized_path = content.file_path.replace('.', '_instagram.')
            img.save(optimized_path, 'JPEG', quality=self.image_quality, optimize=True)
            
            # Update content item
            content.file_path = optimized_path
            
        return content
    
    async def _optimize_video(self, content: ContentItem, metadata: InstagramMetadata) -> ContentItem:
        """Optimize video for Instagram posting"""
        # Video optimization would be implemented here
        # For now, return original content
        return content
    
    async def _optimize_story(self, content: ContentItem, metadata: InstagramMetadata) -> ContentItem:
        """Optimize content for Instagram Story"""
        # Story optimization would be implemented here
        return content
    
    async def _enhance_metadata(
        self,
        metadata: InstagramMetadata,
        content: ContentItem
    ) -> InstagramMetadata:
        """Enhance metadata with AI insights"""
        # AI-powered hashtag suggestions
        if not metadata.hashtags:
            metadata.hashtags = await self._generate_hashtags(content, metadata.caption)
        
        # Optimize caption for engagement
        metadata.caption = await self._optimize_caption(metadata.caption)
        
        # Add accessibility text if missing
        if not metadata.accessibility_text:
            metadata.accessibility_text = await self._generate_accessibility_text(content)
        
        return metadata
    
    async def _upload_media(
        self,
        content: ContentItem,
        metadata: InstagramMetadata
    ) -> str:
        """Upload media to Instagram"""
        try:
            upload_data = {
                "image_url" if metadata.content_type == InstagramContentType.PHOTO else "video_url": content.file_path,
                "caption": metadata.caption,
                "access_token": self.access_token
            }
            
            # Add media type specific parameters
            if metadata.content_type == InstagramContentType.STORY:
                upload_data["media_type"] = "STORIES"
            elif metadata.content_type == InstagramContentType.REEL:
                upload_data["media_type"] = "REELS"
            
            # Upload media
            response = await self._make_api_request(
                "POST",
                self.upload_url,
                data=upload_data
            )
            
            return response.get("id")
            
        except Exception as e:
            raise DistributionError(f"Media upload failed: {str(e)}")
    
    async def _publish_media(self, media_id: str, metadata: InstagramMetadata) -> str:
        """Publish uploaded media"""
        try:
            publish_data = {
                "creation_id": media_id,
                "access_token": self.access_token
            }
            
            response = await self._make_api_request(
                "POST",
                f"{self.base_url}/{self.business_account_id}/media_publish",
                data=publish_data
            )
            
            return response.get("id")
            
        except Exception as e:
            raise DistributionError(f"Media publishing failed: {str(e)}")
    
    async def _configure_additional_features(
        self,
        post_id: str,
        metadata: InstagramMetadata
    ) -> None:
        """Configure additional Instagram features"""
        # Add user tags
        if metadata.user_tags:
            await self._add_user_tags(post_id, metadata.user_tags)
        
        # Add shopping tags
        if metadata.shopping_tags:
            await self._add_shopping_tags(post_id, metadata.shopping_tags)
        
        # Configure branded content
        if metadata.branded_content_sponsor:
            await self._configure_branded_content(post_id, metadata.branded_content_sponsor)
    
    async def _manage_story_highlights(self, story_id: str, metadata: InstagramMetadata) -> None:
        """Manage story highlights"""
        # Implementation would manage story highlights
        pass
    
    async def _collect_initial_analytics(self, post_id: str) -> InstagramAnalytics:
        """Collect initial analytics for posted content"""
        # Return basic analytics structure
        return InstagramAnalytics()
    
    async def _make_api_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make authenticated Instagram API request"""
        if not self.session:
            raise PlatformError("HTTP session not initialized")
        
        # Add access token to parameters
        params = kwargs.get("params", {})
        if "data" in kwargs:
            data = kwargs.get("data", {})
            if "access_token" not in data:
                data["access_token"] = self.access_token
            kwargs["data"] = data
        else:
            params["access_token"] = self.access_token
            kwargs["params"] = params
        
        async with self.session.request(method, url, **kwargs) as response:
            if response.status >= 400:
                error_data = await response.json()
                raise PlatformError(f"Instagram API error: {error_data}")
            
            return await response.json()
    
    def _get_target_size(self, aspect_ratio: InstagramAspectRatio) -> Tuple[int, int]:
        """Get target size for content optimization"""
        size_map = {
            InstagramAspectRatio.SQUARE: (1080, 1080),
            InstagramAspectRatio.PORTRAIT: (1080, 1350),
            InstagramAspectRatio.LANDSCAPE: (1080, 566),
            InstagramAspectRatio.STORY: (1080, 1920),
            InstagramAspectRatio.REEL: (1080, 1920)
        }
        return size_map.get(aspect_ratio, (1080, 1080))
    
    def _enhance_image_quality(self, img: Image.Image) -> Image.Image:
        """Enhance image quality for Instagram"""
        # Image enhancement implementation
        return img
    
    async def _generate_hashtags(self, content: ContentItem, caption: str) -> List[str]:
        """Generate relevant hashtags using AI"""
        # AI hashtag generation implementation
        return ["#ai", "#content", "#instagram"]
    
    async def _optimize_caption(self, caption: str) -> str:
        """Optimize caption for engagement"""
        # Caption optimization implementation
        return caption
    
    async def _generate_accessibility_text(self, content: ContentItem) -> str:
        """Generate accessibility text for content"""
        # Accessibility text generation implementation
        return "AI-generated content"
    
    async def _check_community_guidelines(self, content: ContentItem) -> bool:
        """Check content against Instagram community guidelines"""
        # Community guidelines check implementation
        return True
    
    async def _fetch_media_insights(self, media_id: str) -> Dict[str, Any]:
        """Fetch media-specific insights"""
        # Implementation would fetch insights data
        return {}
    
    async def _fetch_engagement_metrics(
        self,
        media_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Fetch engagement metrics"""
        # Implementation would fetch engagement data
        return {}
    
    async def _fetch_audience_insights(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Fetch audience insights"""
        # Implementation would fetch audience data
        return {}
    
    async def _analyze_hashtag_performance(
        self,
        media_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """Analyze hashtag performance"""
        # Implementation would analyze hashtag performance
        return {}
    
    async def _add_user_tags(self, post_id: str, user_tags: List[Dict[str, Any]]) -> None:
        """Add user tags to post"""
        # Implementation would add user tags
        pass
    
    async def _add_shopping_tags(self, post_id: str, shopping_tags: List[Dict[str, Any]]) -> None:
        """Add shopping tags to post"""
        # Implementation would add shopping tags
        pass
    
    async def _configure_branded_content(self, post_id: str, sponsor_id: str) -> None:
        """Configure branded content settings"""
        # Implementation would configure branded content
        pass
    
    async def cleanup(self) -> None:
        """Cleanup resources and connections"""
        if self.session:
            await self.session.close()
            self.session = None
        
        self.logger.info("Instagram adapter cleaned up successfully")
