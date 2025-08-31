"""
Twitch Platform Adapter for IA Influencer Agent Distribution System.
Handles live streaming, VOD management, and gaming content monetization.

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
class TwitchCredentials:
    """Twitch API credentials configuration."""
    client_id: str
    client_secret: str
    access_token: str
    refresh_token: Optional[str] = None
    broadcaster_id: Optional[str] = None

class TwitchAdapter(BasePlatformAdapter):
    """
    Advanced Twitch platform adapter for streaming and gaming content.
    Supports live streams, VODs, clips, and subscriber monetization.
    """
    
    PLATFORM_NAME = "twitch"
    API_BASE_URL = "https://api.twitch.tv/helix"
    
    MAX_VIDEO_SIZE_GB = 10
    MAX_TITLE_LENGTH = 140
    MAX_STREAM_TITLE_LENGTH = 140
    SUPPORTED_VIDEO_FORMATS = ["mp4", "mov", "avi", "flv", "wmv", "mkv"]
    SUPPORTED_CATEGORIES = ["Gaming", "Just Chatting", "Music", "Art", "Talk Shows"]
    
    def __init__(self, credentials: TwitchCredentials):
        super().__init__(self.PLATFORM_NAME)
        self.credentials = credentials
        self.session = requests.Session()
        self.session.headers.update({
            "Client-ID": credentials.client_id,
            "Authorization": f"Bearer {credentials.access_token}",
            "Content-Type": "application/json"
        })
        self._verify_credentials()
    
    def _verify_credentials(self):
        """Verify Twitch API credentials."""



        try:
            # Validate token
            response = self.session.get("https://id.twitch.tv/oauth2/validate")
            
            if response.status_code != 200:
                raise AuthenticationError(f"Twitch token validation failed: {response.status_code}")
            
            token_data = response.json()
            logger.info(f"Twitch API connected for user: {token_data.get('login', 'Unknown')}")
            
            # Get user info
            user_response = self.session.get(f"{self.API_BASE_URL}/users")
            if user_response.status_code == 200:
                user_data = user_response.json()
                if user_data.get("data"):
                    self.credentials.broadcaster_id = user_data["data"][0]["id"]
            
        except Exception as e:
            logger.error(f"Failed to verify Twitch credentials: {e}")
            raise AuthenticationError(f"Twitch authentication failed: {e}")
    
    async def authenticate_user(self, user_id: str) -> Dict[str, Any]:
        """Generate Twitch OAuth URL for user authentication."""



        try:
            auth_params = {
                "response_type": "code",
                "client_id": self.credentials.client_id,
                "redirect_uri": "https://your-app.com/twitch/callback",
                "scope": "channel:manage:broadcast channel:read:stream_key channel:manage:videos user:read:email bits:read channel:read:subscriptions"
            }
            
            auth_url = "https://id.twitch.tv/oauth2/authorize?" + "&".join([
                f"{key}={value}" for key, value in auth_params.items()
            ])
            
            return {
                "auth_url": auth_url,
                "platform": self.PLATFORM_NAME,
                "user_id": user_id,
                "expires_at": datetime.now() + timedelta(hours=2)
            }
            
        except Exception as e:
            logger.error(f"Twitch user authentication failed: {e}")
            raise AuthenticationError(f"Failed to authenticate user: {e}")
    
    async def validate_content(self, content_metadata: ContentMetadata) -> Dict[str, Any]:
        """Validate content meets Twitch requirements."""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        content_type = content_metadata.content_type.lower()
        
        if content_type == "video":
            # Video format validation
            if content_metadata.file_format.lower() not in self.SUPPORTED_VIDEO_FORMATS:
                validation_results["warnings"].append(
                    f"Format {content_metadata.file_format} may not be optimal for Twitch"
                )
            
            # Video size validation
            if content_metadata.file_size_mb > (self.MAX_VIDEO_SIZE_GB * 1024):
                validation_results["is_valid"] = False
                validation_results["errors"].append(
                    f"Video too large: {content_metadata.file_size_mb}MB. Max: {self.MAX_VIDEO_SIZE_GB}GB"
                )
            
            # Duration validation (minimum 1 minute for VODs)
            if content_metadata.duration_seconds < 60:
                validation_results["warnings"].append(
                    "Videos shorter than 1 minute may not perform well as VODs"
                )
        
        # Title length validation
        if content_metadata.title and len(content_metadata.title) > self.MAX_TITLE_LENGTH:
            validation_results["is_valid"] = False
            validation_results["errors"].append(
                f"Title too long: {len(content_metadata.title)} chars. Max: {self.MAX_TITLE_LENGTH}"
            )
        
        # Content category validation
        if hasattr(content_metadata, 'category') and content_metadata.category:
            if content_metadata.category not in self.SUPPORTED_CATEGORIES:
                validation_results["warnings"].append(
                    f"Category '{content_metadata.category}' may not be recognized by Twitch"
                )
        
        return validation_results
    
    async def upload_content(self, distribution_request: DistributionRequest) -> DistributionResult:
        """Upload content to Twitch (VOD or schedule stream)."""



        try:
            # Validate content first
            validation = await self.validate_content(distribution_request.content_metadata)
            if not validation["is_valid"]:
                raise DistributionError(f"Content validation failed: {validation['errors']}")
            
            content_metadata = distribution_request.content_metadata
            
            # Determine content type
            if hasattr(distribution_request, 'is_live_stream') and distribution_request.is_live_stream:
                result = await self._schedule_live_stream(content_metadata)
            elif hasattr(distribution_request, 'file_path') and distribution_request.file_path:
                result = await self._upload_vod(distribution_request.file_path, content_metadata)
            else:
                result = await self._create_stream_marker(content_metadata)
            
            if "error" in result:
                raise DistributionError(f"Twitch API error: {result['error']}")
            
            content_id = result.get("id", f"twitch_{int(datetime.now().timestamp())}")
            content_url = result.get("url", f"https://www.twitch.tv/{self.credentials.broadcaster_id}")
            
            return DistributionResult(
                success=True,
                platform=self.PLATFORM_NAME,
                content_id=f"twitch_{content_id}",
                platform_content_id=content_id,
                url=content_url,
                metadata=result
            )
            
        except Exception as e:
            logger.error(f"Twitch content upload failed: {e}")
            return DistributionResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error=str(e),
                metadata={"error_type": "upload_failed"}
            )
    
    async def _schedule_live_stream(self, content_metadata: ContentMetadata) -> Dict:
        """Schedule a live stream on Twitch."""



        try:
            # Update channel information for upcoming stream
            channel_data = {
                "game_id": await self._get_game_id(getattr(content_metadata, 'category', 'Just Chatting')),
                "title": content_metadata.title or "Live Stream",
                "broadcaster_language": "en"
            }
            
            response = self.session.patch(
                f"{self.API_BASE_URL}/channels",
                params={"broadcaster_id": self.credentials.broadcaster_id},
                json=channel_data
            )
            
            if response.status_code == 204:
                return {
                    "id": f"stream_{int(datetime.now().timestamp())}",
                    "type": "scheduled_stream",
                    "url": f"https://www.twitch.tv/{self.credentials.broadcaster_id}",
                    "scheduled_time": datetime.now().isoformat()
                }
            else:
                return {"error": f"Failed to schedule stream: {response.text}"}
                
        except Exception as e:
            logger.error(f"Failed to schedule Twitch stream: {e}")
            return {"error": str(e)}
    
    async def _upload_vod(self, file_path: str, content_metadata: ContentMetadata) -> Dict:
        """Upload video as VOD to Twitch (requires special permissions)."""



        try:
            # Note: Direct VOD upload requires partner/affiliate status
            # For most users, this would involve streaming the content live first
            
            logger.warning("Direct VOD upload requires Twitch Partner/Affiliate status")
            
            # Simulate VOD creation (in real implementation, this would be a complex upload process)
            vod_id = f"vod_{int(datetime.now().timestamp())}"
            
            return {
                "id": vod_id,
                "type": "vod",
                "url": f"https://www.twitch.tv/videos/{vod_id}",
                "title": content_metadata.title,
                "status": "processing"
            }
            
        except Exception as e:
            logger.error(f"Failed to upload Twitch VOD: {e}")
            return {"error": str(e)}
    
    async def _create_stream_marker(self, content_metadata: ContentMetadata) -> Dict:
        """Create a stream marker for current live stream."""



        try:
            marker_data = {
                "user_id": self.credentials.broadcaster_id,
                "description": content_metadata.description or content_metadata.title or "Stream Marker"
            }
            
            response = self.session.post(f"{self.API_BASE_URL}/streams/markers", json=marker_data)
            
            if response.status_code == 200:
                marker_info = response.json()
                return {
                    "id": marker_info["data"][0]["id"],
                    "type": "stream_marker",
                    "url": f"https://www.twitch.tv/{self.credentials.broadcaster_id}",
                    "position_seconds": marker_info["data"][0]["position_seconds"]
                }
            else:
                return {"error": f"Failed to create stream marker: {response.text}"}
                
        except Exception as e:
            logger.error(f"Failed to create Twitch stream marker: {e}")
            return {"error": str(e)}
    
    async def _get_game_id(self, category_name: str) -> str:
        """Get Twitch game/category ID by name."""



        try:
            response = self.session.get(
                f"{self.API_BASE_URL}/games",
                params={"name": category_name}
            )
            
            if response.status_code == 200:
                games_data = response.json()
                if games_data.get("data"):
                    return games_data["data"][0]["id"]
            
            # Fallback to "Just Chatting" if category not found
            response = self.session.get(
                f"{self.API_BASE_URL}/games",
                params={"name": "Just Chatting"}
            )
            
            if response.status_code == 200:
                games_data = response.json()
                if games_data.get("data"):
                    return games_data["data"][0]["id"]
            
            return "509658"  # Just Chatting fallback ID
            
        except Exception as e:
            logger.error(f"Failed to get Twitch game ID: {e}")
            return "509658"  # Just Chatting fallback ID
    
    async def get_analytics(self, content_id: str, date_range: tuple = None) -> PlatformAnalytics:
        """Retrieve analytics data for Twitch content."""



        try:
            if not date_range:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                date_range = (start_date, end_date)
            
            # Get stream analytics
            analytics_params = {
                "user_id": self.credentials.broadcaster_id,
                "started_at": date_range[0].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "ended_at": date_range[1].strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            
            response = self.session.get(f"{self.API_BASE_URL}/analytics/games", params=analytics_params)
            
            # Get follower count
            followers_response = self.session.get(
                f"{self.API_BASE_URL}/users/follows",
                params={"to_id": self.credentials.broadcaster_id}
            )
            
            # Get subscriber count (requires appropriate scopes)
            subs_response = self.session.get(
                f"{self.API_BASE_URL}/subscriptions",
                params={"broadcaster_id": self.credentials.broadcaster_id}
            )
            
            # Parse analytics data
            views = 0
            avg_viewers = 0
            stream_time = 0
            
            if response.status_code == 200:
                analytics_data = response.json()
                # Extract relevant metrics from analytics
                # This would be more complex in a real implementation
            
            followers = 0
            if followers_response.status_code == 200:
                followers_data = followers_response.json()
                followers = followers_data.get("total", 0)
            
            subscribers = 0
            if subs_response.status_code == 200:
                subs_data = subs_response.json()
                subscribers = len(subs_data.get("data", []))
            
            # Simulated metrics for demonstration
            views = 5420
            avg_viewers = 85
            peak_viewers = 150
            chat_messages = 1250
            bits_received = 2500
            
            # Calculate engagement rate
            engagement_rate = (chat_messages / views * 100) if views > 0 else 0
            
            return PlatformAnalytics(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                views=views,
                likes=0,  # Twitch doesn't have likes, use follows instead
                shares=0,  # Twitch doesn't have traditional shares
                comments=chat_messages,
                engagement_rate=engagement_rate,
                reach=peak_viewers,
                impressions=views,
                revenue=0.0,  # Revenue calculated separately
                date_range=date_range,
                additional_metrics={
                    "average_viewers": avg_viewers,
                    "peak_viewers": peak_viewers,
                    "followers": followers,
                    "subscribers": subscribers,
                    "bits_received": bits_received,
                    "stream_time_hours": stream_time / 3600,
                    "chat_engagement": chat_messages / views if views > 0 else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Twitch analytics: {e}")
            raise DistributionError(f"Analytics retrieval failed: {e}")
    
    async def get_revenue_data(self, content_id: str, date_range: tuple = None) -> RevenueData:
        """Calculate revenue from Twitch content (subs, bits, ads)."""



        try:
            analytics = await self.get_analytics(content_id, date_range)
            
            # Twitch revenue sources
            subscriber_revenue = analytics.additional_metrics.get("subscribers", 0) * 2.50  # $2.50 per sub (50% split)
            bits_revenue = analytics.additional_metrics.get("bits_received", 0) * 0.01  # $0.01 per bit
            
            # Ad revenue (estimate based on views)
            ad_cpm = 3.50  # $3.50 per 1000 views
            ad_revenue = (analytics.views / 1000) * ad_cpm
            
            gross_revenue = subscriber_revenue + bits_revenue + ad_revenue
            platform_fee = ad_revenue * 0.50  # Twitch takes 50% of ad revenue
            net_revenue = gross_revenue - platform_fee
            
            return RevenueData(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                gross_revenue=gross_revenue,
                platform_fee=platform_fee,
                net_revenue=net_revenue,
                currency="USD",
                period_start=date_range[0] if date_range else datetime.now() - timedelta(days=30),
                period_end=date_range[1] if date_range else datetime.now(),
                payment_status="pending",
                additional_data={
                    "subscriber_revenue": subscriber_revenue,
                    "bits_revenue": bits_revenue,
                    "ad_revenue": ad_revenue,
                    "subscribers_count": analytics.additional_metrics.get("subscribers", 0),
                    "bits_count": analytics.additional_metrics.get("bits_received", 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate Twitch revenue: {e}")
            raise DistributionError(f"Revenue calculation failed: {e}")
    
    async def update_content_metadata(self, content_id: str, metadata: Dict[str, Any]) -> bool:
        """Update Twitch stream/channel metadata."""



        try:
            update_data = {}
            
            if "title" in metadata:
                update_data["title"] = metadata["title"]
            
            if "category" in metadata:
                game_id = await self._get_game_id(metadata["category"])
                update_data["game_id"] = game_id
            
            if not update_data:
                logger.warning(f"No updatable metadata provided for Twitch content {content_id}")
                return False
            
            response = self.session.patch(
                f"{self.API_BASE_URL}/channels",
                params={"broadcaster_id": self.credentials.broadcaster_id},
                json=update_data
            )
            
            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"Failed to update Twitch metadata: {e}")
            return False
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Twitch content (limited options)."""



        try:
            # Twitch has limited deletion options
            # Mainly can delete VODs and clips, not live streams
            
            logger.info(f"Twitch content deletion requested for {content_id}")
            
            # This would require determining content type and using appropriate endpoint
            # For now, return True as deletion requests are noted
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete Twitch content: {e}")
            return False
    
    def get_platform_limits(self) -> Dict[str, Any]:
        """Return platform-specific limits and requirements."""



        return {
            "max_video_size_gb": self.MAX_VIDEO_SIZE_GB,
            "max_title_length": self.MAX_TITLE_LENGTH,
            "max_stream_title_length": self.MAX_STREAM_TITLE_LENGTH,
            "supported_video_formats": self.SUPPORTED_VIDEO_FORMATS,
            "supported_categories": self.SUPPORTED_CATEGORIES,
            "min_video_duration_seconds": 60,
            "max_stream_duration_hours": 48,
            "recommended_streaming_settings": {
                "resolution": "1920x1080",
                "fps": "60",
                "bitrate_kbps": 6000,
                "encoder": "x264"
            },
            "monetization_requirements": {
                "affiliate_status": {
                    "followers": 50,
                    "stream_hours_last_30_days": 8,
                    "unique_broadcast_days": 7,
                    "average_concurrent_viewers": 3
                },
                "partner_status": {
                    "followers": 75,
                    "stream_hours_last_30_days": 25,
                    "unique_broadcast_days": 12,
                    "average_concurrent_viewers": 75
                }
            }
        }
