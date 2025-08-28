"""
LinkedIn Platform Adapter for IA Influencer Agent Distribution System.
Handles professional content distribution, company pages, and B2B networking.

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
class LinkedInCredentials:
    """LinkedIn API credentials configuration."""
    client_id: str
    client_secret: str
    access_token: str
    organization_id: Optional[str] = None

class LinkedInAdapter(BasePlatformAdapter):
    """
    Advanced LinkedIn platform adapter for professional content distribution.
    Supports posts, articles, video content, and company page management.
    """
    
    PLATFORM_NAME = "linkedin"
    API_VERSION = "v2"
    BASE_URL = f"https://api.linkedin.com/{API_VERSION}"
    
    MAX_POST_LENGTH = 3000
    MAX_ARTICLE_LENGTH = 110000
    MAX_IMAGE_SIZE_MB = 8
    MAX_VIDEO_SIZE_MB = 200
    SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "gif"]
    SUPPORTED_VIDEO_FORMATS = ["mp4", "mov", "wmv", "flv", "avi", "asf", "m4v"]
    
    def __init__(self, credentials: LinkedInCredentials):
        super().__init__(self.PLATFORM_NAME)
        self.credentials = credentials
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {credentials.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        })
        self._verify_credentials()
    
    def _verify_credentials(self):
        """Verify LinkedIn API credentials."""
        try:
            # Test API connection
            response = self.session.get(f"{self.BASE_URL}/me")
            
            if response.status_code != 200:
                raise AuthenticationError(f"LinkedIn API error: {response.status_code}")
            
            user_data = response.json()
            logger.info(f"LinkedIn API connected for user: {user_data.get('firstName', {}).get('localized', {}).get('en_US', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to verify LinkedIn credentials: {e}")
            raise AuthenticationError(f"LinkedIn authentication failed: {e}")
    
    async def authenticate_user(self, user_id: str) -> Dict[str, Any]:
        """Generate LinkedIn OAuth URL for user authentication."""
        try:
            auth_params = {
                "response_type": "code",
                "client_id": self.credentials.client_id,
                "redirect_uri": "https://your-app.com/linkedin/callback",
                "scope": "r_liteprofile r_emailaddress w_member_social w_organization_social"
            }
            
            auth_url = "https://www.linkedin.com/oauth/v2/authorization?" + "&".join([
                f"{key}={value}" for key, value in auth_params.items()
            ])
            
            return {
                "auth_url": auth_url,
                "platform": self.PLATFORM_NAME,
                "user_id": user_id,
                "expires_at": datetime.now() + timedelta(hours=2)
            }
            
        except Exception as e:
            logger.error(f"LinkedIn user authentication failed: {e}")
            raise AuthenticationError(f"Failed to authenticate user: {e}")
    
    async def validate_content(self, content_metadata: ContentMetadata) -> Dict[str, Any]:
        """Validate content meets LinkedIn requirements."""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        content_type = content_metadata.content_type.lower()
        
        # Post length validation
        if content_type in ["text", "post"]:
            text_length = len((content_metadata.title or "") + (content_metadata.description or ""))
            if text_length > self.MAX_POST_LENGTH:
                validation_results["is_valid"] = False
                validation_results["errors"].append(
                    f"Post too long: {text_length} characters. Max: {self.MAX_POST_LENGTH}"
                )
        
        # Article length validation
        elif content_type == "article":
            text_length = len((content_metadata.title or "") + (content_metadata.description or ""))
            if text_length > self.MAX_ARTICLE_LENGTH:
                validation_results["warnings"].append(
                    f"Article is {text_length} characters. Consider shorter content for better engagement."
                )
        
        # Image validation
        elif content_type in ["image", "photo"]:
            if content_metadata.file_format.lower() not in self.SUPPORTED_IMAGE_FORMATS:
                validation_results["is_valid"] = False
                validation_results["errors"].append(
                    f"Unsupported image format: {content_metadata.file_format}"
                )
            
            if content_metadata.file_size_mb > self.MAX_IMAGE_SIZE_MB:
                validation_results["is_valid"] = False
                validation_results["errors"].append(
                    f"Image too large: {content_metadata.file_size_mb}MB. Max: {self.MAX_IMAGE_SIZE_MB}MB"
                )
        
        # Video validation
        elif content_type == "video":
            if content_metadata.file_format.lower() not in self.SUPPORTED_VIDEO_FORMATS:
                validation_results["is_valid"] = False
                validation_results["errors"].append(
                    f"Unsupported video format: {content_metadata.file_format}"
                )
            
            if content_metadata.file_size_mb > self.MAX_VIDEO_SIZE_MB:
                validation_results["is_valid"] = False
                validation_results["errors"].append(
                    f"Video too large: {content_metadata.file_size_mb}MB. Max: {self.MAX_VIDEO_SIZE_MB}MB"
                )
            
            # Video duration validation (max 10 minutes)
            if content_metadata.duration_seconds > 600:
                validation_results["warnings"].append(
                    "Videos longer than 10 minutes may have lower engagement on LinkedIn"
                )
        
        return validation_results
    
    async def upload_content(self, distribution_request: DistributionRequest) -> DistributionResult:
        """Upload content to LinkedIn profile or company page."""
        try:
            # Validate content first
            validation = await self.validate_content(distribution_request.content_metadata)
            if not validation["is_valid"]:
                raise DistributionError(f"Content validation failed: {validation['errors']}")
            
            content_metadata = distribution_request.content_metadata
            
            # Determine author (person or organization)
            author_id = f"urn:li:person:{distribution_request.user_id}"
            if self.credentials.organization_id:
                author_id = f"urn:li:organization:{self.credentials.organization_id}"
            
            # Handle different content types
            if content_metadata.content_type.lower() == "article":
                result = await self._create_article(author_id, content_metadata)
            elif hasattr(distribution_request, 'file_path') and distribution_request.file_path:
                if content_metadata.content_type.lower() in ["image", "photo"]:
                    result = await self._create_image_post(author_id, distribution_request.file_path, content_metadata)
                elif content_metadata.content_type.lower() == "video":
                    result = await self._create_video_post(author_id, distribution_request.file_path, content_metadata)
                else:
                    result = await self._create_text_post(author_id, content_metadata)
            else:
                result = await self._create_text_post(author_id, content_metadata)
            
            if "error" in result:
                raise DistributionError(f"LinkedIn API error: {result['error']}")
            
            post_id = result.get("id") or result.get("activity", "unknown")
            post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
            
            return DistributionResult(
                success=True,
                platform=self.PLATFORM_NAME,
                content_id=f"linkedin_{post_id}",
                platform_content_id=post_id,
                url=post_url,
                metadata={
                    "post_id": post_id,
                    "post_url": post_url,
                    "author_type": "organization" if self.credentials.organization_id else "person"
                }
            )
            
        except Exception as e:
            logger.error(f"LinkedIn content upload failed: {e}")
            return DistributionResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error=str(e),
                metadata={"error_type": "upload_failed"}
            )
    
    async def _create_text_post(self, author_id: str, content_metadata: ContentMetadata) -> Dict:
        """Create text-only post on LinkedIn."""
        try:
            post_data = {
                "author": author_id,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": self._prepare_post_text(content_metadata)
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            response = self.session.post(f"{self.BASE_URL}/ugcPosts", json=post_data)
            return response.json() if response.status_code == 201 else {"error": response.text}
            
        except Exception as e:
            logger.error(f"Failed to create LinkedIn text post: {e}")
            return {"error": str(e)}
    
    async def _create_image_post(self, author_id: str, file_path: str, content_metadata: ContentMetadata) -> Dict:
        """Create image post on LinkedIn."""
        try:
            # First, upload the image
            image_upload_result = await self._upload_image(author_id, file_path)
            if "error" in image_upload_result:
                return image_upload_result
            
            # Create post with image
            post_data = {
                "author": author_id,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": self._prepare_post_text(content_metadata)
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [{
                            "status": "READY",
                            "description": {
                                "text": content_metadata.description or ""
                            },
                            "media": image_upload_result["asset"],
                            "title": {
                                "text": content_metadata.title or ""
                            }
                        }]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            response = self.session.post(f"{self.BASE_URL}/ugcPosts", json=post_data)
            return response.json() if response.status_code == 201 else {"error": response.text}
            
        except Exception as e:
            logger.error(f"Failed to create LinkedIn image post: {e}")
            return {"error": str(e)}
    
    async def _create_video_post(self, author_id: str, file_path: str, content_metadata: ContentMetadata) -> Dict:
        """Create video post on LinkedIn."""
        try:
            # First, upload the video
            video_upload_result = await self._upload_video(author_id, file_path)
            if "error" in video_upload_result:
                return video_upload_result
            
            # Create post with video
            post_data = {
                "author": author_id,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": self._prepare_post_text(content_metadata)
                        },
                        "shareMediaCategory": "VIDEO",
                        "media": [{
                            "status": "READY",
                            "description": {
                                "text": content_metadata.description or ""
                            },
                            "media": video_upload_result["asset"],
                            "title": {
                                "text": content_metadata.title or ""
                            }
                        }]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            response = self.session.post(f"{self.BASE_URL}/ugcPosts", json=post_data)
            return response.json() if response.status_code == 201 else {"error": response.text}
            
        except Exception as e:
            logger.error(f"Failed to create LinkedIn video post: {e}")
            return {"error": str(e)}
    
    async def _create_article(self, author_id: str, content_metadata: ContentMetadata) -> Dict:
        """Create long-form article on LinkedIn."""
        try:
            article_data = {
                "author": author_id,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "articleContent": {
                            "title": content_metadata.title or "",
                            "content": content_metadata.description or "",
                            "summary": content_metadata.description[:200] if content_metadata.description else ""
                        }
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            response = self.session.post(f"{self.BASE_URL}/articles", json=article_data)
            return response.json() if response.status_code == 201 else {"error": response.text}
            
        except Exception as e:
            logger.error(f"Failed to create LinkedIn article: {e}")
            return {"error": str(e)}
    
    def _prepare_post_text(self, content_metadata: ContentMetadata) -> str:
        """Prepare optimized post text for LinkedIn."""
        text_parts = []
        
        if content_metadata.title:
            text_parts.append(content_metadata.title)
        
        if content_metadata.description:
            text_parts.append(content_metadata.description)
        
        # Add professional hashtags
        if hasattr(content_metadata, 'tags') and content_metadata.tags:
            # LinkedIn prefers fewer, more relevant hashtags
            hashtags = [f"#{tag.replace(' ', '')}" for tag in content_metadata.tags[:5]]
            text_parts.append(" ".join(hashtags))
        
        return "\n\n".join(text_parts)
    
    async def _upload_image(self, author_id: str, file_path: str) -> Dict:
        """Upload image to LinkedIn."""
        try:
            # Register upload
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": author_id,
                    "serviceRelationships": [{
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }]
                }
            }
            
            response = self.session.post(f"{self.BASE_URL}/assets?action=registerUpload", json=register_data)
            
            if response.status_code != 200:
                return {"error": f"Failed to register image upload: {response.text}"}
            
            upload_info = response.json()
            upload_url = upload_info["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            asset_id = upload_info["value"]["asset"]
            
            # Upload file
            with open(file_path, 'rb') as image_file:
                upload_response = requests.post(upload_url, files={'file': image_file})
            
            if upload_response.status_code != 201:
                return {"error": f"Failed to upload image: {upload_response.text}"}
            
            return {"asset": asset_id}
            
        except Exception as e:
            logger.error(f"Failed to upload image to LinkedIn: {e}")
            return {"error": str(e)}
    
    async def _upload_video(self, author_id: str, file_path: str) -> Dict:
        """Upload video to LinkedIn."""
        try:
            # Register upload
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                    "owner": author_id,
                    "serviceRelationships": [{
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }]
                }
            }
            
            response = self.session.post(f"{self.BASE_URL}/assets?action=registerUpload", json=register_data)
            
            if response.status_code != 200:
                return {"error": f"Failed to register video upload: {response.text}"}
            
            upload_info = response.json()
            upload_url = upload_info["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            asset_id = upload_info["value"]["asset"]
            
            # Upload file
            with open(file_path, 'rb') as video_file:
                upload_response = requests.post(upload_url, files={'file': video_file})
            
            if upload_response.status_code != 201:
                return {"error": f"Failed to upload video: {upload_response.text}"}
            
            return {"asset": asset_id}
            
        except Exception as e:
            logger.error(f"Failed to upload video to LinkedIn: {e}")
            return {"error": str(e)}
    
    async def get_analytics(self, content_id: str, date_range: tuple = None) -> PlatformAnalytics:
        """Retrieve analytics data for LinkedIn content."""
        try:
            post_id = content_id.replace("linkedin_", "")
            
            # Get post statistics
            response = self.session.get(f"{self.BASE_URL}/socialMetadata/{post_id}")
            
            if response.status_code != 200:
                raise DistributionError(f"Failed to fetch LinkedIn analytics: {response.text}")
            
            data = response.json()
            
            # Extract metrics
            total_shares = data.get("totalShares", 0)
            likes = data.get("numLikes", 0)
            comments = data.get("numComments", 0)
            clicks = data.get("clickCount", 0)
            impressions = data.get("numViews", 0)
            
            # Calculate engagement rate
            total_engagements = likes + comments + total_shares + clicks
            engagement_rate = (total_engagements / impressions * 100) if impressions > 0 else 0
            
            return PlatformAnalytics(
                platform=self.PLATFORM_NAME,
                content_id=content_id,
                views=impressions,
                likes=likes,
                shares=total_shares,
                comments=comments,
                engagement_rate=engagement_rate,
                reach=impressions,  # LinkedIn doesn't distinguish reach from impressions in basic API
                impressions=impressions,
                revenue=0.0,  # LinkedIn doesn't provide direct revenue data
                date_range=date_range or (datetime.now() - timedelta(days=1), datetime.now()),
                additional_metrics={
                    "clicks": clicks,
                    "professional_engagement_score": total_engagements * 1.2,  # LinkedIn weights professional engagement higher
                    "industry_relevance": "high" if engagement_rate > 5 else "medium" if engagement_rate > 2 else "low"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch LinkedIn analytics: {e}")
            raise DistributionError(f"Analytics retrieval failed: {e}")
    
    async def get_revenue_data(self, content_id: str, date_range: tuple = None) -> RevenueData:
        """Estimate revenue from LinkedIn content (lead generation, sponsored content)."""
        try:
            analytics = await self.get_analytics(content_id, date_range)
            
            # Estimate revenue based on professional engagement
            # LinkedIn focuses on lead generation and B2B value
            lead_value = analytics.clicks * 5.0  # $5 per qualified click
            engagement_value = analytics.engagement_rate * 2.0  # Professional engagement value
            
            estimated_revenue = lead_value + engagement_value
            platform_fee = 0.0  # No direct platform fee for organic content
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
                    "lead_value": lead_value,
                    "engagement_value": engagement_value,
                    "monetization_potential": "high" if analytics.engagement_rate > 5 else "medium",
                    "b2b_focus": True
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate LinkedIn revenue: {e}")
            raise DistributionError(f"Revenue calculation failed: {e}")
    
    async def update_content_metadata(self, content_id: str, metadata: Dict[str, Any]) -> bool:
        """Update LinkedIn content metadata (very limited editing)."""
        try:
            # LinkedIn has very limited post editing capabilities
            # Most content cannot be edited after publication
            logger.info(f"LinkedIn content update requested for {content_id}")
            
            # For now, return success as metadata updates are tracked locally
            return True
            
        except Exception as e:
            logger.error(f"Failed to update LinkedIn metadata: {e}")
            return False
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete LinkedIn post."""
        try:
            post_id = content_id.replace("linkedin_", "")
            
            response = self.session.delete(f"{self.BASE_URL}/ugcPosts/{post_id}")
            
            if response.status_code == 204:
                logger.info(f"Successfully deleted LinkedIn content: {content_id}")
                return True
            else:
                logger.error(f"Failed to delete LinkedIn content: {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to delete LinkedIn content: {e}")
            return False
    
    def get_platform_limits(self) -> Dict[str, Any]:
        """Return platform-specific limits and requirements."""
        return {
            "max_post_length": self.MAX_POST_LENGTH,
            "max_article_length": self.MAX_ARTICLE_LENGTH,
            "max_image_size_mb": self.MAX_IMAGE_SIZE_MB,
            "max_video_size_mb": self.MAX_VIDEO_SIZE_MB,
            "supported_image_formats": self.SUPPORTED_IMAGE_FORMATS,
            "supported_video_formats": self.SUPPORTED_VIDEO_FORMATS,
            "max_video_duration_minutes": 10,
            "max_hashtags_recommended": 5,
            "professional_content_preferred": True,
            "rate_limits": {
                "posts_per_day": 150,
                "api_calls_per_day": 500
            },
            "content_guidelines": {
                "professional_tone": True,
                "industry_relevance": "preferred",
                "thought_leadership": "encouraged"
            }
        }
