"""Facebook Platform Adapter for IA Influencer Agent Distribution System.
Handles content distribution, page management, and monetization on Facebook.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
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
class FacebookCredentials:
    """
Facebook Graph API credentials configuration."""
    app_id: str
    app_secret: str
    access_token: str
    page_id: Optional[str] = None
    page_access_token: Optional[str] = None

class FacebookAdapter(BasePlatformAdapter):
    """
    Advanced Facebook platform adapter for content distribution and monetization.
    Supports posts, reels, stories, live videos, and comprehensive analytics.
    """

    
    PLATFORM_NAME = "facebook"
    API_VERSION = "v18.0"
    BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
    
    MAX_IMAGE_SIZE_MB = 4
    MAX_VIDEO_SIZE_MB = 4000
    MAX_POST_LENGTH = 63206
    SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "gif", "webp", "bmp"]
    SUPPORTED_VIDEO_FORMATS = ["mp4", "mov", "avi", "mkv", "webm", "flv"]
    
    def __init__(self, credentials: FacebookCredentials):
        super().__init__(self.PLATFORM_NAME)
        self.credentials = credentials
        self.session = requests.Session()
        self._verify_credentials()
    
    def _verify_credentials(self):
        """Verify Facebook API credentials."""
        try:
            # Test API connection
            response = self._make_api_request("GET", "/me", {
                "fields": "id,name",
                "access_token": self.credentials.access_token
            })
            
            if "error" in response:
                raise AuthenticationError(f"Facebook API error: {response['error']}")
            
            logger.info(f"Facebook API connected for user: {response.get('name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to verify Facebook credentials: {e}")
            raise AuthenticationError(f"Facebook authentication failed: {e}")
    
    def _make_api_request(self, method: str, endpoint: str, params: Dict = None, files: Dict = None) -> Dict:
        """Make authenticated request to Facebook Graph API."""
        url = f"{self.BASE_URL}{endpoint}"
        
        if method == "GET":
            response = self.session.get(url, params=params or {})
        elif method == "POST":
            if files:
                response = self.session.post(url, data=params or {}, files=files)
            else:
                response = self.session.post(url, json=params or {})
        elif method == "DELETE":
            response = self.session.delete(url, params=params or {})
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response.json()
    
    async def authenticate_user(self, user_id: str) -> Dict[str, Any]:
        """Generate Facebook OAuth URL for user authentication."""
        try:
            auth_params = {
                "client_id": self.credentials.app_id,
                "redirect_uri": "https://your-app.com/facebook/callback",
                "scope": "pages_manage_posts,pages_read_engagement,pages_show_list,publish_to_groups,user_posts",
                "response_type": "code"
            }
            
            auth_url = "https://www.facebook.com/v18.0/dialog/oauth?" + "&".join([
                f"{key}={value}" for key, value in auth_params.items()
            ])
            
            return {
                "auth_url": auth_url,
                "platform": self.PLATFORM_NAME,
                "user_id": user_id,
                "expires_at": datetime.now() + timedelta(hours=2)
            }
            
        except Exception as e:
            logger.error(f"Facebook user authentication failed: {e}")
            raise AuthenticationError(f"Failed to authenticate user: {e}")
    
    async def validate_content(self, content_metadata: ContentMetadata) -> Dict[str, Any]:
        """Validate content meets Facebook requirements."""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        content_type = content_metadata.content_type.lower()
        
        if content_type in ["image", "photo"]:
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
        
        elif content_type in ["video", "reel"]:
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
            
            # Duration validation for Reels (15 seconds to 90 seconds)
            if content_type == "reel":
                if content_metadata.duration_seconds < 15:
                    validation_results["warnings"].append(
                        "Reel shorter than 15 seconds may not perform well"
                    )
                elif content_metadata.duration_seconds > 90:
                    validation_results["warnings"].append(
                        "Reel longer than 90 seconds may be truncated"
                    )
        
        # Text length validation
        total_text_length = len((content_metadata.title or "") + (content_metadata.description or ""))
        if total_text_length > self.MAX_POST_LENGTH:
            validation_results["warnings"].append(
                f"Post text is {total_text_length} characters. Consider shortening for better engagement."
            )
        
        return validation_results
    
    async def upload_content(self, distribution_request: DistributionRequest) -> DistributionResult:
        """Upload content to Facebook page or profile."""
        try:
            # Validate content first
            validation = await self.validate_content(distribution_request.content_metadata)
            if not validation["is_valid"]:
                raise DistributionError(f"Content validation failed: {validation['errors']}")
            
            content_metadata = distribution_request.content_metadata
            
            # Determine target (page or user profile)
            target_id = self.credentials.page_id or "me"
            access_token = self.credentials.page_access_token or self.credentials.access_token
            
            # Prepare post content
            post_data = self._prepare_post_data(content_metadata, access_token)
            
            # Handle different content types
            if hasattr(distribution_request, 'file_path') and distribution_request.file_path:
                if content_metadata.content_type.lower() in ["image", "photo"]:
                    result = await self._upload_photo(target_id, distribution_request.file_path, post_data)
                elif content_metadata.content_type.lower() in ["video", "reel"]:
                    result = await self._upload_video(target_id, distribution_request.file_path, post_data)
                else:
                    result = await self._create_text_post(target_id, post_data)
            else:
                result = await self._create_text_post(target_id, post_data)
            
            if "error" in result:
                raise DistributionError(f"Facebook API error: {result['error']}")
            
            post_id = result["id"]
            post_url = f"https://www.facebook.com/{post_id}"
            
            return DistributionResult(
                success=True,
                platform=self.PLATFORM_NAME,
                content_id=f"facebook_{post_id}",
                platform_content_id=post_id,
                url=post_url,
                metadata={
                    "post_id": post_id,
                    "post_url": post_url,
                    "target_type": "page" if self.credentials.page_id else "profile"
                }
            )
            
        except Exception as e:
            logger.error(f"Facebook content upload failed: {e}")
            return DistributionResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error=str(e),
                metadata={"error_type": "upload_failed"}
            )
    
    def _prepare_post_data(self, content_metadata: ContentMetadata, access_token: str) -> Dict[str, Any]:
        """Prepare post data from content metadata."""
        message_parts = []
        
        if content_metadata.title:
            message_parts.append(content_metadata.title)
        
        if content_metadata.description:
            message_parts.append(content_metadata.description)
        
        # Add hashtags
        if hasattr(content_metadata, 'tags') and content_metadata.tags:
            hashtags = [f"#{tag.replace(' ', '')}" for tag in content_metadata.tags]
            message_parts.append(" ".join(hashtags))
        
        return {
            "message": "\n\n".join(message_parts),
            "access_token": access_token
        }
    
    async def _upload_photo(self, target_id: str, file_path: str, post_data: Dict) -> Dict:
        """Upload photo to Facebook."""
        try:
            with open(file_path, 'rb') as photo_file:
                files = {"source": photo_file}
                return self._make_api_request("POST", f"/{target_id}/photos", post_data, files)
        except Exception as e:
            logger.error(f"Failed to upload photo to Facebook: {e}")
            return {"error": str(e)}
    
    async def _upload_video(self, target_id: str, file_path: str, post_data: Dict) -> Dict:
        """Upload video to Facebook."""
        try:
            # For large videos, use resumable upload
            if self._get_file_size_mb(file_path) > 100:
                return await self._upload_large_video(target_id, file_path, post_data)
            
            with open(file_path, 'rb') as video_file:
                files = {"source": video_file}
                return self._make_api_request("POST", f"/{target_id}/videos", post_data, files)
                
        except Exception as e:
            logger.error(f"Failed to upload video to Facebook: {e}")
            return {"error": str(e)}
    
    async def _upload_large_video(self, target_id: str, file_path: str, post_data: Dict) -> Dict:
        """Upload large video using resumable upload."""
        try:
            # Initialize upload session
            init_params = {
                "upload_phase": "start",
                "file_size": self._get_file_size_bytes(file_path),
                **post_data
            }
            
            init_response = self._make_api_request("POST", f"/{target_id}/videos", init_params)
            
            if "error" in init_response:
                return init_response
            
            upload_session_id = init_response["upload_session_id"]
            
            # Upload video in chunks
            chunk_size = 8 * 1024 * 1024  # 8MB chunks
            with open(file_path, 'rb') as video_file:
                offset = 0
                while True:
                    chunk = video_file.read(chunk_size)
                    if not chunk:
                        break
                    
                    chunk_params = {
                        "upload_phase": "transfer",
                        "upload_session_id": upload_session_id,
                        "start_offset": offset,
                        **post_data
                    }
                    
                    files = {"video_file_chunk": chunk}
                    chunk_response = self._make_api_request("POST", f"/{target_id}/videos", chunk_params, files)
                    
                    if "error" in chunk_response:
                        return chunk_response
                    
                    offset += len(chunk)
            
            # Finalize upload
            finish_params = {
                "upload_phase": "finish",
                "upload_session_id": upload_session_id,
                **post_data
            }
            
            return self._make_api_request("POST", f"/{target_id}/videos", finish_params)
            
        except Exception as e:
            logger.error(f"Failed to upload large video to Facebook: {e}")
            return {"error": str(e)}
    
    async def _create_text_post(self, target_id: str, post_data: Dict) -> Dict:
        """Create text-only post on Facebook."""
        return self._make_api_request("POST", f"/{target_id}/feed", post_data)
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB."""
        import os
        return os.path.getsize(file_path) / (1024 * 1024)
    
    def _get_file_size_bytes(self, file_path: str) -> int:
        """
Get file size in bytes."""
        import os
        return os.path.getsize(file_path)
    
    async def get_analytics(self, content_id: str, date_range: tuple = None) -> PlatformAnalytics:
        """
Retrieve analytics data for Facebook content."""
        try:
            post_id = content_id.replace("facebook_", "")
            
            # Get post insights
            insights_params = {
                "metric": "post_impressions,post_engaged_users,post_clicks,post_reactions_like_total,post_reactions_love_total,post_reactions_wow_total,post_reactions_haha_total,post_reactions_sorry_total,post_reactions_anger_total",
                "access_token": self.credentials.page_access_token or self.credentials.access_token
            }
            
            insights_response = self._make_api_request("GET", f"/{post_id}/insights", insights_params)
            
            # Parse insights data
            insights_data = {}
            if "data" in insights_response:
                for insight in insights_response["data"]:
                    metric_name = insight["name"]
                    metric_value = insight["values"][0]["value"] if insight["values"] else 0
                    insights_data[metric_name] = metric_value
            
            # Get basic post data
            post_params = {
                "fields": "created_time,message,reactions.summary(total_count),comments.summary(total_count),shares",
                "access_token": self.credentials.page_access_token or self.credentials.access_token
            }
            
            post_response = self._make_api_request("GET", f"/{post_id}", post_params)
            
            # Calculate metrics
            impressions = insights_data.get("post_impressions", 0)
            engaged_users = insights_data.get("post_engaged_users", 0)
            likes = post_response.get("reactions", {}).get("summary", {}).get("total_count", 0)
            comments = post_response.get("comments", {}).get("summary", {}).get("total_count", 0)
            shares = post_response.get("shares", {}).get("count", 0)
            
            engagement_rate = (engaged_users / impressions * 100) if impressions > 0 else 0
            
            return PlatformAnalytics(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                views=impressions,
                likes=likes,
                shares=shares,
                comments=comments,
                engagement_rate=engagement_rate,
                reach=engaged_users,
                impressions=impressions,
                revenue=0.0,  # Facebook doesn't provide direct revenue data via API
                date_range=date_range or (datetime.now() - timedelta(days=1), datetime.now()),
                additional_metrics={
                    "clicks": insights_data.get("post_clicks", 0),
                    "love_reactions": insights_data.get("post_reactions_love_total", 0),
                    "wow_reactions": insights_data.get("post_reactions_wow_total", 0),
                    "haha_reactions": insights_data.get("post_reactions_haha_total", 0),
                    "sorry_reactions": insights_data.get("post_reactions_sorry_total", 0),
                    "anger_reactions": insights_data.get("post_reactions_anger_total", 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Facebook analytics: {e}")
            raise DistributionError(f"Analytics retrieval failed: {e}")
    
    async def get_revenue_data(self, content_id: str, date_range: tuple = None) -> RevenueData:
        """Estimate revenue from Facebook content (Creator Bonus, Stars, etc.)."""
        try:
            analytics = await self.get_analytics(content_id, date_range)
            
            # Estimate revenue based on engagement
            # Facebook Creator Bonus, Stars, and ad revenue sharing
            estimated_rpm = 2.5  # Revenue per mille (per 1000 views)
            estimated_revenue = (analytics.views / 1000) * estimated_rpm
            
            # Stars revenue (if applicable)
            stars_revenue = analytics.likes * 0.01  # $0.01 per star (hypothetical)
            
            total_revenue = estimated_revenue + stars_revenue
            platform_fee = total_revenue * 0.30  # 30% platform fee
            net_revenue = total_revenue - platform_fee
            
            return RevenueData(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                gross_revenue=total_revenue,
                platform_fee=platform_fee,
                net_revenue=net_revenue,
                currency="USD",
                period_start=date_range[0] if date_range else datetime.now() - timedelta(days=30),
                period_end=date_range[1] if date_range else datetime.now(),
                payment_status="estimated",
                additional_data={
                    "estimated_rpm": estimated_rpm,
                    "stars_revenue": stars_revenue,
                    "monetization_features": ["creator_bonus", "stars", "ad_breaks", "brand_content"]
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate Facebook revenue: {e}")
            raise DistributionError(f"Revenue calculation failed: {e}")
    
    async def update_content_metadata(self, content_id: str, metadata: Dict[str, Any]) -> bool:
        """Update Facebook post metadata (limited editing available)."""
        try:
            post_id = content_id.replace("facebook_", "")
            
            # Facebook allows limited post editing
            update_params = {
                "access_token": self.credentials.page_access_token or self.credentials.access_token
            }
            
            # Only message can be updated for most posts
            if "message" in metadata:
                update_params["message"] = metadata["message"]
            
            if update_params.keys() == {"access_token"}:
                logger.warning(f"No updatable metadata provided for Facebook post {content_id}")
                return False
            
            response = self._make_api_request("POST", f"/{post_id}", update_params)
            
            if "error" in response:
                logger.error(f"Failed to update Facebook post: {response['error']}")
                return False
            
            return response.get("success", False)
            
        except Exception as e:
            logger.error(f"Failed to update Facebook metadata: {e}")
            return False
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Facebook post."""
        try:
            post_id = content_id.replace("facebook_", "")
            
            delete_params = {
                "access_token": self.credentials.page_access_token or self.credentials.access_token
            }
            
            response = self._make_api_request("DELETE", f"/{post_id}", delete_params)
            
            if "error" in response:
                logger.error(f"Failed to delete Facebook post: {response['error']}")
                return False
            
            return response.get("success", False)
            
        except Exception as e:
            logger.error(f"Failed to delete Facebook content: {e}")
            return False
    
    def get_platform_limits(self) -> Dict[str, Any]:
        """Return platform-specific limits and requirements."""
        return {
            "max_image_size_mb": self.MAX_IMAGE_SIZE_MB,
            "max_video_size_mb": self.MAX_VIDEO_SIZE_MB,
            "max_post_length": self.MAX_POST_LENGTH,
            "supported_image_formats": self.SUPPORTED_IMAGE_FORMATS,
            "supported_video_formats": self.SUPPORTED_VIDEO_FORMATS,
            "max_video_duration_minutes": 240,  # 4 hours
            "max_images_per_post": 10,
            "reel_duration_range": [15, 90],  # seconds
            "story_duration_max": 15,  # seconds
            "rate_limits": {
                "posts_per_hour": 25,
                "api_calls_per_hour": 4800
            },
            "monetization_requirements": {
                "followers_minimum": 1000,
                "page_required": True,
                "creator_bonus_eligible_countries": ["US", "CA", "UK", "DE", "FR"]
            }
        }
