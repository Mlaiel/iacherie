"""
Pinterest Platform Adapter for IA Influencer Agent Distribution System.
Handles visual content distribution, board management, and e-commerce integration.

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
class PinterestCredentials:
    """Pinterest API credentials configuration."""
    client_id: str
    client_secret: str
    access_token: str
    refresh_token: Optional[str] = None

class PinterestAdapter(BasePlatformAdapter):
    """
    Advanced Pinterest platform adapter for visual content distribution.
    Supports pins, boards, shopping features, and analytics.
    """
    
    PLATFORM_NAME = "pinterest"
    API_VERSION = "v5"
    BASE_URL = f"https://api.pinterest.com/{API_VERSION}"
    
    MAX_IMAGE_SIZE_MB = 20
    MAX_VIDEO_SIZE_MB = 2048
    MAX_PIN_DESCRIPTION_LENGTH = 500
    MAX_BOARD_DESCRIPTION_LENGTH = 500
    SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "gif", "webp"]
    SUPPORTED_VIDEO_FORMATS = ["mp4", "mov", "m4v"]
    
    def __init__(self, credentials: PinterestCredentials):
        super().__init__(self.PLATFORM_NAME)
        self.credentials = credentials
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {credentials.access_token}",
            "Content-Type": "application/json"
        })
        self._verify_credentials()
    
    def _verify_credentials(self):
        """Verify Pinterest API credentials."""



        try:
            # Test API connection
            response = self.session.get(f"{self.BASE_URL}/user_account")
            
            if response.status_code != 200:
                raise AuthenticationError(f"Pinterest API error: {response.status_code}")
            
            user_data = response.json()
            logger.info(f"Pinterest API connected for user: {user_data.get('username', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to verify Pinterest credentials: {e}")
            raise AuthenticationError(f"Pinterest authentication failed: {e}")
    
    async def authenticate_user(self, user_id: str) -> Dict[str, Any]:
        """Generate Pinterest OAuth URL for user authentication."""



        try:
            auth_params = {
                "response_type": "code",
                "client_id": self.credentials.client_id,
                "redirect_uri": "https://your-app.com/pinterest/callback",
                "scope": "ads:read,boards:read,boards:write,pins:read,pins:write,user_accounts:read"
            }
            
            auth_url = "https://www.pinterest.com/oauth/?" + "&".join([
                f"{key}={value}" for key, value in auth_params.items()
            ])
            
            return {
                "auth_url": auth_url,
                "platform": self.PLATFORM_NAME,
                "user_id": user_id,
                "expires_at": datetime.now() + timedelta(hours=2)
            }
            
        except Exception as e:
            logger.error(f"Pinterest user authentication failed: {e}")
            raise AuthenticationError(f"Failed to authenticate user: {e}")
    
    async def validate_content(self, content_metadata: ContentMetadata) -> Dict[str, Any]:
        """Validate content meets Pinterest requirements."""
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
            
            # Pinterest prefers vertical images (2:3 ratio)
            if hasattr(content_metadata, 'dimensions') and content_metadata.dimensions:
                width, height = content_metadata.dimensions
                ratio = height / width
                if ratio < 1.2:
                    validation_results["warnings"].append(
                        "Pinterest performs better with vertical images (2:3 aspect ratio recommended)"
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
            
            # Duration validation (4 seconds to 15 minutes)
            if content_metadata.duration_seconds < 4:
                validation_results["is_valid"] = False
                validation_results["errors"].append("Video too short. Minimum duration: 4 seconds")
            elif content_metadata.duration_seconds > 900:
                validation_results["is_valid"] = False
                validation_results["errors"].append("Video too long. Maximum duration: 15 minutes")
        
        # Description length validation
        description_length = len(content_metadata.description or "")
        if description_length > self.MAX_PIN_DESCRIPTION_LENGTH:
            validation_results["warnings"].append(
                f"Description is {description_length} characters. Pinterest recommends under {self.MAX_PIN_DESCRIPTION_LENGTH}"
            )
        
        return validation_results
    
    async def upload_content(self, distribution_request: DistributionRequest) -> DistributionResult:
        """Upload content (pin) to Pinterest."""



        try:
            # Validate content first
            validation = await self.validate_content(distribution_request.content_metadata)
            if not validation["is_valid"]:
                raise DistributionError(f"Content validation failed: {validation['errors']}")
            
            content_metadata = distribution_request.content_metadata
            
            # Get or create board
            board_id = await self._get_or_create_board(
                distribution_request.user_id,
                getattr(distribution_request, 'board_name', 'General'),
                getattr(distribution_request, 'board_description', '')
            )
            
            # Create pin
            pin_data = await self._create_pin(
                board_id,
                distribution_request.file_path if hasattr(distribution_request, 'file_path') else None,
                content_metadata
            )
            
            if "error" in pin_data:
                raise DistributionError(f"Pinterest API error: {pin_data['error']}")
            
            pin_id = pin_data["id"]
            pin_url = f"https://www.pinterest.com/pin/{pin_id}/"
            
            return DistributionResult(
                success=True,
                platform=self.PLATFORM_NAME,
                content_id=f"pinterest_{pin_id}",
                platform_content_id=pin_id,
                url=pin_url,
                metadata={
                    "pin_id": pin_id,
                    "pin_url": pin_url,
                    "board_id": board_id
                }
            )
            
        except Exception as e:
            logger.error(f"Pinterest content upload failed: {e}")
            return DistributionResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error=str(e),
                metadata={"error_type": "upload_failed"}
            )
    
    async def _get_or_create_board(self, user_id: str, board_name: str, board_description: str) -> str:
        """Get existing board or create new one."""



        try:
            # First, try to find existing board
            response = self.session.get(f"{self.BASE_URL}/boards")
            
            if response.status_code == 200:
                boards = response.json().get("items", [])
                for board in boards:
                    if board["name"].lower() == board_name.lower():
                        return board["id"]
            
            # Create new board if not found
            board_data = {
                "name": board_name,
                "description": board_description or f"Board created for {board_name}",
                "privacy": "PUBLIC"
            }
            
            response = self.session.post(f"{self.BASE_URL}/boards", json=board_data)
            
            if response.status_code == 201:
                return response.json()["id"]
            else:
                logger.error(f"Failed to create Pinterest board: {response.text}")
                # Fallback: use default board or create generic one
                return await self._create_default_board()
                
        except Exception as e:
            logger.error(f"Failed to get/create Pinterest board: {e}")
            return await self._create_default_board()
    
    async def _create_default_board(self) -> str:
        """Create a default board as fallback."""



        try:
            board_data = {
                "name": "IA Influencer Content",
                "description": "Content distributed via IA Influencer Agent",
                "privacy": "PUBLIC"
            }
            
            response = self.session.post(f"{self.BASE_URL}/boards", json=board_data)
            
            if response.status_code == 201:
                return response.json()["id"]
            else:
                raise DistributionError("Failed to create default Pinterest board")
                
        except Exception as e:
            logger.error(f"Failed to create default Pinterest board: {e}")
            raise DistributionError("Board creation failed")
    
    async def _create_pin(self, board_id: str, file_path: Optional[str], content_metadata: ContentMetadata) -> Dict:
        """Create pin on Pinterest."""



        try:
            pin_data = {
                "board_id": board_id,
                "description": self._prepare_pin_description(content_metadata),
                "title": content_metadata.title or "",
                "alt_text": getattr(content_metadata, 'alt_text', content_metadata.title or "")
            }
            
            # Add link if available
            if hasattr(content_metadata, 'source_url') and content_metadata.source_url:
                pin_data["link"] = content_metadata.source_url
            
            # Handle media upload
            if file_path:
                if content_metadata.content_type.lower() in ["image", "photo"]:
                    media_result = await self._upload_image_media(file_path)
                elif content_metadata.content_type.lower() == "video":
                    media_result = await self._upload_video_media(file_path)
                else:
                    return {"error": "Unsupported media type for Pinterest"}
                
                if "error" in media_result:
                    return media_result
                
                pin_data["media_source"] = media_result["media_source"]
            else:
                # Pin from URL (if available)
                if hasattr(content_metadata, 'image_url') and content_metadata.image_url:
                    pin_data["media_source"] = {
                        "source_type": "image_url",
                        "url": content_metadata.image_url
                    }
                else:
                    return {"error": "No media source provided for Pinterest pin"}
            
            response = self.session.post(f"{self.BASE_URL}/pins", json=pin_data)
            
            if response.status_code == 201:
                return response.json()
            else:
                return {"error": f"Failed to create pin: {response.text}"}
                
        except Exception as e:
            logger.error(f"Failed to create Pinterest pin: {e}")
            return {"error": str(e)}
    
    def _prepare_pin_description(self, content_metadata: ContentMetadata) -> str:
        """Prepare optimized pin description."""
        description_parts = []
        
        if content_metadata.title:
            description_parts.append(content_metadata.title)
        
        if content_metadata.description:
            # Truncate if too long
            desc = content_metadata.description
            if len(desc) > self.MAX_PIN_DESCRIPTION_LENGTH - 50:  # Leave space for hashtags
                desc = desc[:self.MAX_PIN_DESCRIPTION_LENGTH - 53] + "..."
            description_parts.append(desc)
        
        # Add relevant hashtags (Pinterest uses hashtags for discovery)
        if hasattr(content_metadata, 'tags') and content_metadata.tags:
            hashtags = [f"#{tag.replace(' ', '')}" for tag in content_metadata.tags[:10]]
            hashtag_text = " ".join(hashtags)
            
            current_length = len(" ".join(description_parts))
            if current_length + len(hashtag_text) <= self.MAX_PIN_DESCRIPTION_LENGTH:
                description_parts.append(hashtag_text)
        
        return " ".join(description_parts)
    
    async def _upload_image_media(self, file_path: str) -> Dict:
        """Upload image media for pin."""



        try:
            # Pinterest uses direct file upload
            with open(file_path, 'rb') as image_file:
                files = {"image": image_file}
                headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
                
                response = requests.post(
                    f"{self.BASE_URL}/media",
                    files=files,
                    headers=headers
                )
            
            if response.status_code == 201:
                media_data = response.json()
                return {
                    "media_source": {
                        "source_type": "image_upload",
                        "media_id": media_data["media_id"]
                    }
                }
            else:
                return {"error": f"Failed to upload image: {response.text}"}
                
        except Exception as e:
            logger.error(f"Failed to upload image to Pinterest: {e}")
            return {"error": str(e)}
    
    async def _upload_video_media(self, file_path: str) -> Dict:
        """Upload video media for pin."""



        try:
            # Pinterest video upload is similar to image
            with open(file_path, 'rb') as video_file:
                files = {"video": video_file}
                headers = {"Authorization": f"Bearer {self.credentials.access_token}"}
                
                response = requests.post(
                    f"{self.BASE_URL}/media",
                    files=files,
                    headers=headers
                )
            
            if response.status_code == 201:
                media_data = response.json()
                return {
                    "media_source": {
                        "source_type": "video_upload",
                        "media_id": media_data["media_id"]
                    }
                }
            else:
                return {"error": f"Failed to upload video: {response.text}"}
                
        except Exception as e:
            logger.error(f"Failed to upload video to Pinterest: {e}")
            return {"error": str(e)}
    
    async def get_analytics(self, content_id: str, date_range: tuple = None) -> PlatformAnalytics:
        """Retrieve analytics data for Pinterest pin."""



        try:
            pin_id = content_id.replace("pinterest_", "")
            
            # Get pin analytics
            if not date_range:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                date_range = (start_date, end_date)
            
            analytics_params = {
                "start_date": date_range[0].strftime("%Y-%m-%d"),
                "end_date": date_range[1].strftime("%Y-%m-%d"),
                "metric_types": "IMPRESSION,PIN_CLICK,OUTBOUND_CLICK,SAVE"
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/pins/{pin_id}/analytics",
                params=analytics_params
            )
            
            if response.status_code != 200:
                raise DistributionError(f"Failed to fetch Pinterest analytics: {response.text}")
            
            analytics_data = response.json()
            
            # Extract metrics
            impressions = analytics_data.get("IMPRESSION", 0)
            clicks = analytics_data.get("PIN_CLICK", 0)
            outbound_clicks = analytics_data.get("OUTBOUND_CLICK", 0)
            saves = analytics_data.get("SAVE", 0)
            
            # Calculate engagement rate
            total_engagements = clicks + outbound_clicks + saves
            engagement_rate = (total_engagements / impressions * 100) if impressions > 0 else 0
            
            return PlatformAnalytics(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                views=impressions,
                likes=saves,  # Pinterest "saves" are similar to likes
                shares=0,  # Pinterest doesn't have traditional shares
                comments=0,  # Pinterest comments are limited
                engagement_rate=engagement_rate,
                reach=impressions,  # For Pinterest, reach ≈ impressions
                impressions=impressions,
                revenue=0.0,  # Pinterest doesn't provide direct revenue data
                date_range=date_range,
                additional_metrics={
                    "pin_clicks": clicks,
                    "outbound_clicks": outbound_clicks,
                    "saves": saves,
                    "ctr": (clicks / impressions * 100) if impressions > 0 else 0,
                    "save_rate": (saves / impressions * 100) if impressions > 0 else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch Pinterest analytics: {e}")
            raise DistributionError(f"Analytics retrieval failed: {e}")
    
    async def get_revenue_data(self, content_id: str, date_range: tuple = None) -> RevenueData:
        """Estimate revenue from Pinterest content (shopping, affiliate, traffic)."""



        try:
            analytics = await self.get_analytics(content_id, date_range)
            
            # Pinterest revenue comes from e-commerce, affiliate, and traffic conversion
            traffic_value = analytics.additional_metrics.get("outbound_clicks", 0) * 0.50  # $0.50 per qualified click
            save_value = analytics.likes * 0.10  # $0.10 per save (potential future purchase)
            impression_value = (analytics.impressions / 1000) * 2.0  # $2 CPM equivalent
            
            estimated_revenue = traffic_value + save_value + impression_value
            platform_fee = 0.0  # No direct platform fee for organic pins
            net_revenue = estimated_revenue
            
            return RevenueData(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                gross_revenue=estimated_revenue,
                platform_fee=platform_fee,
                net_revenue=net_revenue,
                currency="USD",
                period_start=date_range[0] if date_range else datetime.now() - timedelta(days=30),
                period_end=date_range[1] if date_range else datetime.now(),
                payment_status="estimated",
                additional_data={
                    "traffic_value": traffic_value,
                    "save_value": save_value,
                    "impression_value": impression_value,
                    "monetization_potential": "high" if analytics.additional_metrics.get("outbound_clicks", 0) > 100 else "medium",
                    "e_commerce_focus": True
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate Pinterest revenue: {e}")
            raise DistributionError(f"Revenue calculation failed: {e}")
    
    async def update_content_metadata(self, content_id: str, metadata: Dict[str, Any]) -> bool:
        """Update Pinterest pin metadata."""



        try:
            pin_id = content_id.replace("pinterest_", "")
            
            update_data = {}
            
            # Pinterest allows updating certain fields
            if "description" in metadata:
                update_data["description"] = metadata["description"]
            
            if "title" in metadata:
                update_data["title"] = metadata["title"]
            
            if "board_id" in metadata:
                update_data["board_id"] = metadata["board_id"]
            
            if "link" in metadata:
                update_data["link"] = metadata["link"]
            
            if not update_data:
                logger.warning(f"No updatable metadata provided for Pinterest pin {content_id}")
                return False
            
            response = self.session.patch(f"{self.BASE_URL}/pins/{pin_id}", json=update_data)
            
            if response.status_code == 200:
                logger.info(f"Successfully updated Pinterest pin: {content_id}")
                return True
            else:
                logger.error(f"Failed to update Pinterest pin: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update Pinterest metadata: {e}")
            return False
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Pinterest pin."""



        try:
            pin_id = content_id.replace("pinterest_", "")
            
            response = self.session.delete(f"{self.BASE_URL}/pins/{pin_id}")
            
            if response.status_code == 204:
                logger.info(f"Successfully deleted Pinterest pin: {content_id}")
                return True
            else:
                logger.error(f"Failed to delete Pinterest pin: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete Pinterest content: {e}")
            return False
    
    def get_platform_limits(self) -> Dict[str, Any]:
        """Return platform-specific limits and requirements."""



        return {
            "max_image_size_mb": self.MAX_IMAGE_SIZE_MB,
            "max_video_size_mb": self.MAX_VIDEO_SIZE_MB,
            "max_pin_description_length": self.MAX_PIN_DESCRIPTION_LENGTH,
            "max_board_description_length": self.MAX_BOARD_DESCRIPTION_LENGTH,
            "supported_image_formats": self.SUPPORTED_IMAGE_FORMATS,
            "supported_video_formats": self.SUPPORTED_VIDEO_FORMATS,
            "video_duration_range": [4, 900],  # 4 seconds to 15 minutes
            "recommended_aspect_ratio": "2:3",  # Vertical images perform better
            "max_pins_per_day": 50,
            "max_boards_per_account": 2000,
            "rate_limits": {
                "api_calls_per_hour": 1000,
                "pins_per_hour": 50
            },
            "monetization_features": {
                "shopping_tags": True,
                "verified_merchant": "recommended",
                "rich_pins": True,
                "creator_rewards": True
            }
        }
