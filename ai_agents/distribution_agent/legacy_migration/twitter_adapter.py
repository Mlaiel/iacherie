"""Twitter/X Platform Adapter for IA Influencer Agent Distribution System.
Handles content distribution, engagement tracking, and monetization on Twitter/X.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent. All rights reserved.
"""import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import tweepy
import requests
from dataclasses import dataclass
import json

from ..core.base_adapter import BasePlatformAdapter
from ..models.distribution_models import (
    DistributionRequest, DistributionResult, ContentMetadata,
    PlatformAnalytics, RevenueData
)
from ..utils.exceptions import DistributionError, AuthenticationError

logger = logging.getLogger(__name__)

@dataclass
class TwitterCredentials:
    """Twitter API v2 credentials configuration."""    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str
    bearer_token: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

class TwitterAdapter(BasePlatformAdapter):
    """    Advanced Twitter/X platform adapter for content distribution and engagement.
    Supports tweets, threads, media uploads, spaces, and revenue tracking.
    """    
    PLATFORM_NAME = "twitter"
    MAX_IMAGE_SIZE_MB = 5
    MAX_VIDEO_SIZE_MB = 512
    MAX_TWEET_LENGTH = 280
    SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "gif", "webp"]
    SUPPORTED_VIDEO_FORMATS = ["mp4", "mov", "avi", "webm"]
    
    def __init__(self, credentials: TwitterCredentials):
        super().__init__(self.PLATFORM_NAME)
        self.credentials = credentials
        self.api_v1 = None
        self.api_v2 = None
        self.client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Twitter API v1.1 and v2 clients."""        try:
            # Twitter API v1.1 for media upload
            auth = tweepy.OAuthHandler(
                self.credentials.api_key,
                self.credentials.api_secret
            )
            auth.set_access_token(
                self.credentials.access_token,
                self.credentials.access_token_secret
            )
            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Twitter API v2 for modern features
            self.client = tweepy.Client(
                bearer_token=self.credentials.bearer_token,
                consumer_key=self.credentials.api_key,
                consumer_secret=self.credentials.api_secret,
                access_token=self.credentials.access_token,
                access_token_secret=self.credentials.access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Verify credentials
            self.client.get_me()
            logger.info("Twitter API clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter clients: {e}")
            raise AuthenticationError(f"Twitter authentication failed: {e}")
    
    async def authenticate_user(self, user_id: str) -> Dict[str, Any]:
        """Authenticate user using OAuth 2.0 PKCE flow."""        try:
            # Generate OAuth 2.0 authorization URL
            oauth2_user_handler = tweepy.OAuth2UserHandler(
                client_id=self.credentials.client_id,
                redirect_uri="https://your-app.com/callback",
                scope=["tweet.read", "tweet.write", "users.read", "offline.access"]
            )
            
            auth_url = oauth2_user_handler.get_authorization_url()
            
            return {
                "auth_url": auth_url,
                "platform": self.PLATFORM_NAME,
                "user_id": user_id,
                "expires_at": datetime.now() + timedelta(hours=2)
            }
            
        except Exception as e:
            logger.error(f"Twitter user authentication failed: {e}")
            raise AuthenticationError(f"Failed to authenticate user: {e}")
    
    async def validate_content(self, content_metadata: ContentMetadata) -> Dict[str, Any]:
        """Validate content meets Twitter requirements."""        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        content_type = content_metadata.content_type.lower()
        
        if content_type == "text":
            # Text length validation
            if len(content_metadata.title + (content_metadata.description or "")) > self.MAX_TWEET_LENGTH:
                validation_results["warnings"].append(
                    f"Content may exceed tweet length limit of {self.MAX_TWEET_LENGTH} characters"
                )
        
        elif content_type == "image":
            # Image format validation
            if content_metadata.file_format.lower() not in self.SUPPORTED_IMAGE_FORMATS:
                validation_results["is_valid"] = False
                validation_results["errors"].append(
                    f"Unsupported image format: {content_metadata.file_format}"
                )
            
            # Image size validation
            if content_metadata.file_size_mb > self.MAX_IMAGE_SIZE_MB:
                validation_results["is_valid"] = False
                validation_results["errors"].append(
                    f"Image too large: {content_metadata.file_size_mb}MB. Max: {self.MAX_IMAGE_SIZE_MB}MB"
                )
        
        elif content_type == "video":
            # Video format validation
            if content_metadata.file_format.lower() not in self.SUPPORTED_VIDEO_FORMATS:
                validation_results["is_valid"] = False
                validation_results["errors"].append(
                    f"Unsupported video format: {content_metadata.file_format}"
                )
            
            # Video size validation
            if content_metadata.file_size_mb > self.MAX_VIDEO_SIZE_MB:
                validation_results["is_valid"] = False
                validation_results["errors"].append(
                    f"Video too large: {content_metadata.file_size_mb}MB. Max: {self.MAX_VIDEO_SIZE_MB}MB"
                )
            
            # Duration validation (max 2 minutes 20 seconds for regular users)
            if content_metadata.duration_seconds > 140:
                validation_results["warnings"].append(
                    "Video longer than 2:20 may require Twitter Blue subscription"
                )
        
        return validation_results
    
    async def upload_content(self, distribution_request: DistributionRequest) -> DistributionResult:
        """Upload content to Twitter/X."""        try:
            # Validate content first
            validation = await self.validate_content(distribution_request.content_metadata)
            if not validation["is_valid"]:
                raise DistributionError(f"Content validation failed: {validation['errors']}")
            
            content_metadata = distribution_request.content_metadata
            media_ids = []
            
            # Handle media upload if present
            if hasattr(distribution_request, 'file_path') and distribution_request.file_path:
                media_id = await self._upload_media(distribution_request.file_path, content_metadata)
                if media_id:
                    media_ids.append(media_id)
            
            # Prepare tweet text
            tweet_text = self._prepare_tweet_text(content_metadata)
            
            # Create tweet
            tweet_params = {"text": tweet_text}
            if media_ids:
                tweet_params["media_ids"] = media_ids
            
            response = self.client.create_tweet(**tweet_params)
            
            tweet_id = response.data["id"]
            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
            
            return DistributionResult(
                success=True,
                platform=self.PLATFORM_NAME,
                content_id=f"twitter_{tweet_id}",
                platform_content_id=tweet_id,
                url=tweet_url,
                metadata={
                    "tweet_id": tweet_id,
                    "tweet_url": tweet_url,
                    "media_ids": media_ids,
                    "character_count": len(tweet_text)
                }
            )
            
        except Exception as e:
            logger.error(f"Twitter content upload failed: {e}")
            return DistributionResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error=str(e),
                metadata={"error_type": "upload_failed"}
            )
    
    def _prepare_tweet_text(self, content_metadata: ContentMetadata) -> str:
        """Prepare optimized tweet text from content metadata."""        text_parts = []
        
        # Add title
        if content_metadata.title:
            text_parts.append(content_metadata.title)
        
        # Add description if space allows
        if content_metadata.description:
            current_length = len(" ".join(text_parts))
            remaining_space = self.MAX_TWEET_LENGTH - current_length - 10  # Buffer for hashtags
            
            if len(content_metadata.description) <= remaining_space:
                text_parts.append(content_metadata.description)
            else:
                # Truncate description
                truncated = content_metadata.description[:remaining_space-3] + "..."
                text_parts.append(truncated)
        
        # Add hashtags
        if hasattr(content_metadata, 'tags') and content_metadata.tags:
            hashtags = [f"#{tag.replace(' ', '')}" for tag in content_metadata.tags[:3]]
            current_length = len(" ".join(text_parts))
            hashtag_text = " " + " ".join(hashtags)
            
            if current_length + len(hashtag_text) <= self.MAX_TWEET_LENGTH:
                text_parts.append(hashtag_text.strip())
        
        return " ".join(text_parts)
    
    async def _upload_media(self, file_path: str, content_metadata: ContentMetadata) -> Optional[str]:
        """Upload media file to Twitter."""        try:
            # Determine media category
            media_category = self._get_media_category(content_metadata.content_type)
            
            # Upload media using v1.1 API
            media = self.api_v1.media_upload(
                filename=file_path,
                media_category=media_category
            )
            
            # Add alt text for accessibility if available
            if hasattr(content_metadata, 'alt_text') and content_metadata.alt_text:
                self.api_v1.create_media_metadata(
                    media.media_id,
                    alt_text=content_metadata.alt_text
                )
            
            return str(media.media_id)
            
        except Exception as e:
            logger.error(f"Failed to upload media to Twitter: {e}")
            return None
    
    def _get_media_category(self, content_type: str) -> str:
        """Determine Twitter media category based on content type."""        content_type = content_type.lower()
        
        if content_type in ["image", "photo"]:
            return "tweet_image"
        elif content_type in ["video", "gif"]:
            return "tweet_video"
        else:
            return "tweet_image"  # Default fallback
    
    async def get_analytics(self, content_id: str, date_range: tuple = None) -> PlatformAnalytics:
        """Retrieve analytics data for tweeted content."""        try:
            tweet_id = content_id.replace("twitter_", "")
            
            # Get tweet details with metrics
            tweet = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=[
                    "public_metrics", "created_at", "context_annotations",
                    "engagement_metrics", "non_public_metrics", "organic_metrics"
                ]
            )
            
            metrics = tweet.data.public_metrics
            
            # Calculate engagement rate
            total_engagements = (
                metrics.get("retweet_count", 0) +
                metrics.get("like_count", 0) +
                metrics.get("reply_count", 0) +
                metrics.get("quote_count", 0)
            )
            impressions = metrics.get("impression_count", 1)
            engagement_rate = (total_engagements / impressions) * 100 if impressions > 0 else 0
            
            return PlatformAnalytics(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                views=impressions,
                likes=metrics.get("like_count", 0),
                shares=metrics.get("retweet_count", 0),
                comments=metrics.get("reply_count", 0),
                engagement_rate=engagement_rate,
                reach=impressions,  # For Twitter, reach ≈ impressions
                impressions=impressions,
                revenue=0.0,  # Twitter doesn't have direct revenue sharing
                date_range=date_range or (datetime.now() - timedelta(days=1), datetime.now()),
                additional_metrics={
                    "quote_count": metrics.get("quote_count", 0),
                    "bookmark_count": metrics.get("bookmark_count", 0),
                    "click_count": metrics.get("url_link_clicks", 0),
                    "profile_visits": metrics.get("user_profile_clicks", 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Twitter analytics: {e}")
            raise DistributionError(f"Analytics retrieval failed: {e}")
    
    async def get_revenue_data(self, content_id: str, date_range: tuple = None) -> RevenueData:
        """Calculate potential revenue from Twitter content (Tips, Super Follows, etc.)."""        try:
            # Twitter doesn't have direct revenue sharing like YouTube
            # Revenue comes from tips, super follows, or promotional content
            
            analytics = await self.get_analytics(content_id, date_range)
            
            # Estimate revenue from engagement (hypothetical)
            engagement_value = (
                analytics.likes * 0.01 +  # $0.01 per like
                analytics.shares * 0.05 +  # $0.05 per retweet
                analytics.comments * 0.03   # $0.03 per reply
            )
            
            return RevenueData(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                gross_revenue=engagement_value,
                platform_fee=0.0,  # No platform fee for organic content
                net_revenue=engagement_value,
                currency="USD",
                period_start=date_range[0] if date_range else datetime.now() - timedelta(days=30),
                period_end=date_range[1] if date_range else datetime.now(),
                payment_status="estimated",
                additional_data={
                    "engagement_value": engagement_value,
                    "revenue_type": "estimated_engagement",
                    "monetization_features": ["tips", "super_follows", "creator_subscriptions"]
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate Twitter revenue: {e}")
            raise DistributionError(f"Revenue calculation failed: {e}")
    
    async def create_thread(self, content_list: List[str], media_paths: Optional[List[str]] = None) -> List[str]:
        """Create a Twitter thread with multiple tweets."""        try:
            tweet_ids = []
            reply_to_id = None
            
            for i, content in enumerate(content_list):
                media_ids = []
                
                # Upload media if provided for this tweet
                if media_paths and i < len(media_paths) and media_paths[i]:
                    # Create dummy metadata for media upload
                    dummy_metadata = ContentMetadata(
                        title="",
                        content_type="image",
                        file_format="jpg"
                    )
                    media_id = await self._upload_media(media_paths[i], dummy_metadata)
                    if media_id:
                        media_ids.append(media_id)
                
                # Create tweet parameters
                tweet_params = {"text": content}
                if media_ids:
                    tweet_params["media_ids"] = media_ids
                if reply_to_id:
                    tweet_params["in_reply_to_tweet_id"] = reply_to_id
                
                # Create tweet
                response = self.client.create_tweet(**tweet_params)
                tweet_id = response.data["id"]
                tweet_ids.append(tweet_id)
                reply_to_id = tweet_id
                
                # Rate limit protection
                await asyncio.sleep(1)
            
            return tweet_ids
            
        except Exception as e:
            logger.error(f"Failed to create Twitter thread: {e}")
            raise DistributionError(f"Thread creation failed: {e}")
    
    async def update_content_metadata(self, content_id: str, metadata: Dict[str, Any]) -> bool:
        """Update content metadata (limited options on Twitter)."""        try:
            # Twitter doesn't allow editing tweets, but we can update our tracking
            logger.info(f"Metadata update requested for Twitter content {content_id}")
            
            # Could potentially delete and repost if really needed
            # But generally Twitter content is immutable
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Twitter metadata: {e}")
            return False
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete tweet from Twitter."""        try:
            tweet_id = content_id.replace("twitter_", "")
            
            # Delete the tweet
            response = self.client.delete_tweet(id=tweet_id)
            
            if response.data.get("deleted"):
                logger.info(f"Successfully deleted Twitter content: {content_id}")
                return True
            else:
                logger.warning(f"Failed to delete Twitter content: {content_id}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to delete Twitter content: {e}")
            return False
    
    def get_platform_limits(self) -> Dict[str, Any]:
        """Return platform-specific limits and requirements."""        return {
            "max_image_size_mb": self.MAX_IMAGE_SIZE_MB,
            "max_video_size_mb": self.MAX_VIDEO_SIZE_MB,
            "max_tweet_length": self.MAX_TWEET_LENGTH,
            "supported_image_formats": self.SUPPORTED_IMAGE_FORMATS,
            "supported_video_formats": self.SUPPORTED_VIDEO_FORMATS,
            "max_images_per_tweet": 4,
            "max_video_duration_seconds": 140,
            "max_tweets_per_day": 2400,
            "rate_limits": {
                "tweets_per_15_min": 300,
                "media_uploads_per_15_min": 300
            },
            "monetization_requirements": {
                "followers_minimum": 500,
                "verified_account": False,
                "age_minimum_days": 90
            }
        }
