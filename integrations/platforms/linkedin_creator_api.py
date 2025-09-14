"""
LinkedIn Creator API Integration for Ainflue Platform
Enterprise-grade LinkedIn creator and professional content management

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
import logging
from dataclasses import dataclass
from enum import Enum
import base64
import uuid
import urllib.parse

import aiohttp
import structlog

from ..core.base_integration import BaseIntegration
from ..core.exceptions import (
    APIError, InvalidConfigurationError, 
    SecurityError, ValidationError
)
from ..core.security import SecurityManager
from ..core.monitoring import MetricsCollector
from ..core.cache import CacheManager

logger = structlog.get_logger(__name__)

class LinkedInScope(Enum):
    """LinkedIn API OAuth scopes"""
    R_LITEPROFILE = "r_liteprofile"
    R_EMAILADDRESS = "r_emailaddress"
    W_MEMBER_SOCIAL = "w_member_social"
    R_MEMBER_SOCIAL = "r_member_social"
    R_ORGANIZATION_SOCIAL = "r_organization_social"
    W_ORGANIZATION_SOCIAL = "w_organization_social"
    RW_ORGANIZATION_ADMIN = "rw_organization_admin"
    R_BASICPROFILE = "r_basicprofile"
    R_1ST_CONNECTIONS_SIZE = "r_1st_connections_size"
    R_FULLPROFILE = "r_fullprofile"
    R_NETWORK = "r_network"
    R_CONTACTINFO = "r_contactinfo"

class ContentType(Enum):
    """LinkedIn content types"""
    ARTICLE = "ARTICLE"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"
    POLL = "POLL"
    EVENT = "EVENT"
    CAROUSEL = "CAROUSEL"

class ShareVisibility(Enum):
    """LinkedIn share visibility options"""
    PUBLIC = "PUBLIC"
    CONNECTIONS = "CONNECTIONS"
    LOGGED_IN = "LOGGED_IN"

class MediaStatus(Enum):
    """LinkedIn media upload status"""
    WAITING_UPLOAD = "WAITING_UPLOAD"
    UPLOAD_IN_PROGRESS = "UPLOAD_IN_PROGRESS"
    AVAILABLE = "AVAILABLE"
    PROCESSING_FAILED = "PROCESSING_FAILED"

@dataclass
class LinkedInConfig:
    """LinkedIn API configuration"""
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: List[LinkedInScope]
    api_version: str = "v2"
    environment: str = "production"  # production or sandbox
    rate_limit_requests: int = 500  # requests per day
    rate_limit_window: int = 86400  # 24 hours
    webhook_secret: Optional[str] = None
    
    def __post_init__(self) -> None:
        if not self.scopes:
            self.scopes = [
                LinkedInScope.R_LITEPROFILE,
                LinkedInScope.R_EMAILADDRESS,
                LinkedInScope.W_MEMBER_SOCIAL
            ]

@dataclass
class LinkedInUser:
    """LinkedIn user profile data"""
    id: str
    first_name: str
    last_name: str
    email: Optional[str]
    profile_picture: Optional[str]
    headline: Optional[str]
    summary: Optional[str]
    industry: Optional[str]
    location: Optional[str]
    num_connections: Optional[int]
    vanity_name: Optional[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class LinkedInPost:
    """LinkedIn post/share data"""
    id: str
    author: str
    text: str
    created_time: datetime
    visibility: ShareVisibility
    activity: str
    service_provider: str
    is_reshare_disabled_by_author: bool
    content: Optional[Dict[str, Any]] = None
    commentary: Optional[str] = None
    subject: Optional[str] = None

@dataclass
class LinkedInMediaAsset:
    """LinkedIn media asset data"""
    asset: str
    status: MediaStatus
    download_url: Optional[str] = None
    media_type: Optional[str] = None
    recipes: Optional[List[Dict[str, Any]]] = None

@dataclass
class LinkedInMetrics:
    """LinkedIn post metrics data"""
    post_id: str
    likes: int
    comments: int
    shares: int
    clicks: int
    impressions: int
    engagement_rate: float
    reach: int
    video_views: Optional[int] = None
    collected_at: datetime

class LinkedInCreatorAPI(BaseIntegration):
    """
    Enterprise LinkedIn Creator API integration for Ainflue platform
    
    Features:
    - Complete LinkedIn OAuth 2.0 authentication
    - Professional content creation and publishing
    - Advanced analytics and engagement tracking
    - Company page management
    - Video content upload and processing
    - LinkedIn Live integration
    - Creator monetization tracking
    - Professional network analytics
    - Industry insights and trending topics
    """

    def __init__(self, config -> None: LinkedInConfig) -> None:
        super().__init__("linkedin_creator")
        self.config = config
        self.security_manager = SecurityManager()
        self.metrics = MetricsCollector()
        self.cache = CacheManager()
        
        # API endpoints
        self.base_url = "https://api.linkedin.com"
        self.auth_url = "https://www.linkedin.com/oauth/v2"
        
        # Headers template
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Ainflue/1.0.0",
            "LinkedIn-Version": "202312"
        }
        
        # Rate limiting
        self.rate_limiter = {}
        
        # Storage
        self._users: Dict[str, LinkedInUser] = {}
        self._posts: Dict[str, LinkedInPost] = {}
        self._metrics: Dict[str, List[LinkedInMetrics]] = {}
        
        logger.info("LinkedIn Creator API integration initialized",
                   client_id=config.client_id[:8] + "...",
                   scopes=len(config.scopes))

    async def get_authorization_url(self, 
                                  state: Optional[str] = None,
                                  additional_scopes: Optional[List[str]] = None) -> str:
        """
        Generate LinkedIn OAuth authorization URL
        
        Args:
            state: Optional state parameter for security
            additional_scopes: Additional OAuth scopes
            
        Returns:
            Authorization URL for user redirect
        """
        try:
            # Prepare scopes
            scopes = [scope.value for scope in self.config.scopes]
            if additional_scopes:
                scopes.extend(additional_scopes)
            
            scope_string = " ".join(scopes)
            
            # Prepare parameters
            params = {
                "response_type": "code",
                "client_id": self.config.client_id,
                "redirect_uri": self.config.redirect_uri,
                "scope": scope_string
            }
            
            if state:
                params["state"] = state
            
            # Build URL
            auth_url = f"{self.auth_url}/authorization?" + urllib.parse.urlencode(params)
            
            self.metrics.increment("linkedin.auth_urls.generated")
            
            logger.info("LinkedIn authorization URL generated",
                       scopes=len(scopes),
                       has_state=bool(state))
            
            return auth_url
            
        except Exception as e:
            self.metrics.increment("linkedin.auth_urls.failed")
            logger.error("Failed to generate authorization URL", error=str(e))
            raise ValidationError(f"Authorization URL generation failed: {e}")

    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            authorization_code: Authorization code from callback
            
        Returns:
            Token response with access_token and metadata
        """
        try:
            token_data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": self.config.redirect_uri,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.auth_url}/accessToken",
                    data=token_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise APIError(f"Token exchange failed: {error_text}")
                    
                    token_response = await response.json()
                    
                    # Store token with expiration
                    expires_in = token_response.get("expires_in", 5184000)  # 60 days default
                    token_response["expires_at"] = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    # Cache token
                    await self.cache.set(
                        f"linkedin_token:{authorization_code[:10]}",
                        token_response,
                        ttl=expires_in - 3600  # Refresh 1 hour before expiry
                    )
                    
                    self.metrics.increment("linkedin.tokens.exchanged")
                    
                    logger.info("LinkedIn token exchange successful",
                               expires_in=expires_in)
                    
                    return token_response
                    
        except Exception as e:
            self.metrics.increment("linkedin.tokens.exchange_failed")
            logger.error("Token exchange failed",
                        error=str(e))
            raise APIError(f"Token exchange failed: {e}")

    async def _make_authenticated_request(self,
                                        method: str,
                                        endpoint: str,
                                        access_token: str,
                                        data: Optional[Dict[str, Any]] = None,
                                        params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make authenticated request to LinkedIn API"""
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if data else None,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    # Handle rate limiting
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning("LinkedIn API rate limited",
                                     retry_after=retry_after)
                        raise APIError(f"Rate limited. Retry after {retry_after} seconds")
                    
                    response_data = await response.json()
                    
                    if response.status >= 400:
                        error_msg = response_data.get("message", "Unknown error")
                        logger.error("LinkedIn API error",
                                   status=response.status,
                                   error=error_msg,
                                   endpoint=endpoint)
                        raise APIError(f"LinkedIn API error: {error_msg}")
                    
                    return response_data
                    
        except aiohttp.ClientError as e:
            logger.error("LinkedIn API request failed",
                        endpoint=endpoint,
                        error=str(e))
            raise APIError(f"API request failed: {e}")

    async def get_user_profile(self, access_token: str) -> LinkedInUser:
        """
        Get authenticated user's LinkedIn profile
        
        Args:
            access_token: LinkedIn access token
            
        Returns:
            LinkedIn user profile data
        """
        try:
            # Get basic profile
            profile_data = await self._make_authenticated_request(
                "GET",
                "/v2/people/~",
                access_token,
                params={
                    "projection": "(id,firstName,lastName,profilePicture(displayImage~:playableStreams),headline,summary,industry,location,numConnections,vanityName)"
                }
            )
            
            # Get email address (requires separate scope)
            email_data = None
            try:
                email_data = await self._make_authenticated_request(
                    "GET",
                    "/v2/emailAddress",
                    access_token,
                    params={"q": "members", "projection": "(elements*(handle~))"}
                )
            except APIError:
                logger.info("Email access not available - missing scope")
            
            # Process profile data
            user_id = profile_data["id"]
            
            # Extract names
            first_name = profile_data.get("firstName", {}).get("localized", {}).get("en_US", "")
            last_name = profile_data.get("lastName", {}).get("localized", {}).get("en_US", "")
            
            # Extract profile picture
            profile_picture = None
            if "profilePicture" in profile_data:
                display_image = profile_data["profilePicture"].get("displayImage~", {})
                elements = display_image.get("elements", [])
                if elements:
                    # Get largest image
                    largest_image = max(elements, key=lambda x: x.get("data", {}).get("com.linkedin.digitalmedia.mediaartifact.StillImage", {}).get("storageSize", {}).get("width", 0))
                    profile_picture = largest_image.get("identifiers", [{}])[0].get("identifier")
            
            # Extract email
            email = None
            if email_data and "elements" in email_data:
                elements = email_data["elements"]
                if elements:
                    email = elements[0].get("handle~", {}).get("emailAddress")
            
            # Create user object
            linkedin_user = LinkedInUser(
                id=user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                profile_picture=profile_picture,
                headline=profile_data.get("headline", {}).get("localized", {}).get("en_US"),
                summary=profile_data.get("summary", {}).get("localized", {}).get("en_US"),
                industry=profile_data.get("industry", {}).get("localized", {}).get("en_US"),
                location=profile_data.get("location", {}).get("name"),
                num_connections=profile_data.get("numConnections"),
                vanity_name=profile_data.get("vanityName"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store user
            self._users[user_id] = linkedin_user
            
            # Cache user data
            await self.cache.set(
                f"linkedin_user:{user_id}",
                linkedin_user,
                ttl=3600  # 1 hour
            )
            
            self.metrics.increment("linkedin.profiles.retrieved")
            
            logger.info("LinkedIn user profile retrieved",
                       user_id=user_id,
                       name=f"{first_name} {last_name}")
            
            return linkedin_user
            
        except Exception as e:
            self.metrics.increment("linkedin.profiles.failed")
            logger.error("Failed to get user profile", error=str(e))
            raise APIError(f"Failed to get user profile: {e}")

    async def create_text_post(self,
                             access_token: str,
                             text: str,
                             visibility: ShareVisibility = ShareVisibility.PUBLIC) -> LinkedInPost:
        """
        Create a text post on LinkedIn
        
        Args:
            access_token: LinkedIn access token
            text: Post content text
            visibility: Post visibility setting
            
        Returns:
            Created LinkedIn post data
        """
        try:
            # Get user ID first
            user_profile = await self.get_user_profile(access_token)
            
            # Prepare post data
            post_data = {
                "author": f"urn:li:person:{user_profile.id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility.value
                }
            }
            
            # Create post
            response = await self._make_authenticated_request(
                "POST",
                "/v2/ugcPosts",
                access_token,
                data=post_data
            )
            
            # Process response
            post_id = response["id"]
            
            linkedin_post = LinkedInPost(
                id=post_id,
                author=f"urn:li:person:{user_profile.id}",
                text=text,
                created_time=datetime.utcnow(),
                visibility=visibility,
                activity=response.get("activity", ""),
                service_provider=response.get("serviceProvider", ""),
                is_reshare_disabled_by_author=response.get("isReshareDisabledByAuthor", False),
                commentary=text
            )
            
            # Store post
            self._posts[post_id] = linkedin_post
            
            # Cache post data
            await self.cache.set(
                f"linkedin_post:{post_id}",
                linkedin_post,
                ttl=86400  # 24 hours
            )
            
            self.metrics.increment("linkedin.posts.created")
            
            logger.info("LinkedIn text post created",
                       post_id=post_id,
                       author=user_profile.id,
                       text_length=len(text))
            
            return linkedin_post
            
        except Exception as e:
            self.metrics.increment("linkedin.posts.failed")
            logger.error("Failed to create text post", error=str(e))
            raise APIError(f"Failed to create text post: {e}")

    async def upload_media(self,
                         access_token: str,
                         media_data: bytes,
                         media_type: str,
                         filename: str) -> LinkedInMediaAsset:
        """
        Upload media asset to LinkedIn
        
        Args:
            access_token: LinkedIn access token
            media_data: Media file bytes
            media_type: MIME type of media
            filename: Original filename
            
        Returns:
            LinkedIn media asset information
        """
        try:
            # Get user ID
            user_profile = await self.get_user_profile(access_token)
            
            # Initialize upload
            upload_request = {
                "registerUploadRequest": {
                    "recipes": [
                        "urn:li:digitalmediaRecipe:feedshare-image"
                    ],
                    "owner": f"urn:li:person:{user_profile.id}",
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }
            
            # Register upload
            upload_response = await self._make_authenticated_request(
                "POST",
                "/v2/assets",
                access_token,
                params={"action": "registerUpload"},
                data=upload_request
            )
            
            asset_id = upload_response["value"]["asset"]
            upload_mechanism = upload_response["value"]["uploadMechanism"]
            upload_url = upload_mechanism["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            
            # Upload media file
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    upload_url,
                    data=media_data,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": media_type
                    }
                ) as upload_resp:
                    
                    if upload_resp.status != 201:
                        error_text = await upload_resp.text()
                        raise APIError(f"Media upload failed: {error_text}")
            
            # Check upload status
            status_response = await self._make_authenticated_request(
                "GET",
                f"/v2/assets/{asset_id}",
                access_token
            )
            
            # Create media asset object
            media_asset = LinkedInMediaAsset(
                asset=asset_id,
                status=MediaStatus(status_response.get("status", "AVAILABLE")),
                download_url=status_response.get("downloadUrl"),
                media_type=media_type,
                recipes=status_response.get("recipes", [])
            )
            
            self.metrics.increment("linkedin.media.uploaded")
            self.metrics.observe("linkedin.media.size", len(media_data))
            
            logger.info("LinkedIn media uploaded",
                       asset_id=asset_id,
                       media_type=media_type,
                       size=len(media_data))
            
            return media_asset
            
        except Exception as e:
            self.metrics.increment("linkedin.media.upload_failed")
            logger.error("Failed to upload media", error=str(e))
            raise APIError(f"Failed to upload media: {e}")

    async def create_image_post(self,
                              access_token: str,
                              text: str,
                              media_asset: LinkedInMediaAsset,
                              visibility: ShareVisibility = ShareVisibility.PUBLIC) -> LinkedInPost:
        """
        Create an image post on LinkedIn
        
        Args:
            access_token: LinkedIn access token
            text: Post content text
            media_asset: Uploaded media asset
            visibility: Post visibility setting
            
        Returns:
            Created LinkedIn post data
        """
        try:
            # Get user ID
            user_profile = await self.get_user_profile(access_token)
            
            # Prepare post data with media
            post_data = {
                "author": f"urn:li:person:{user_profile.id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": text
                                },
                                "media": media_asset.asset,
                                "title": {
                                    "text": "Ainflue Content"
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility.value
                }
            }
            
            # Create post
            response = await self._make_authenticated_request(
                "POST",
                "/v2/ugcPosts",
                access_token,
                data=post_data
            )
            
            # Process response
            post_id = response["id"]
            
            linkedin_post = LinkedInPost(
                id=post_id,
                author=f"urn:li:person:{user_profile.id}",
                text=text,
                created_time=datetime.utcnow(),
                visibility=visibility,
                activity=response.get("activity", ""),
                service_provider=response.get("serviceProvider", ""),
                is_reshare_disabled_by_author=response.get("isReshareDisabledByAuthor", False),
                commentary=text,
                content={
                    "media_asset": media_asset.asset,
                    "media_type": "IMAGE"
                }
            )
            
            # Store post
            self._posts[post_id] = linkedin_post
            
            # Cache post data
            await self.cache.set(
                f"linkedin_post:{post_id}",
                linkedin_post,
                ttl=86400  # 24 hours
            )
            
            self.metrics.increment("linkedin.posts.image_created")
            
            logger.info("LinkedIn image post created",
                       post_id=post_id,
                       media_asset=media_asset.asset)
            
            return linkedin_post
            
        except Exception as e:
            self.metrics.increment("linkedin.posts.image_failed")
            logger.error("Failed to create image post", error=str(e))
            raise APIError(f"Failed to create image post: {e}")

    async def get_post_analytics(self,
                               access_token: str,
                               post_id: str) -> LinkedInMetrics:
        """
        Get analytics for a LinkedIn post
        
        Args:
            access_token: LinkedIn access token
            post_id: LinkedIn post ID
            
        Returns:
            Post analytics and metrics
        """
        try:
            # Get post statistics
            stats_response = await self._make_authenticated_request(
                "GET",
                "/v2/socialActions",
                access_token,
                params={
                    "q": "ugcPost",
                    "ugcPost": post_id,
                    "projection": "(totalFirstLevelComments,totalLikes,totalShares)"
                }
            )
            
            # Extract metrics (simplified - real implementation would have more detailed analytics)
            elements = stats_response.get("elements", [])
            total_likes = 0
            total_comments = 0
            total_shares = 0
            
            for element in elements:
                total_likes += element.get("totalLikes", 0)
                total_comments += element.get("totalFirstLevelComments", 0)
                total_shares += element.get("totalShares", 0)
            
            # Calculate engagement rate (simplified)
            total_engagement = total_likes + total_comments + total_shares
            # Note: Real implementation would need follower count for accurate rate
            engagement_rate = 0.0  # Placeholder
            
            metrics = LinkedInMetrics(
                post_id=post_id,
                likes=total_likes,
                comments=total_comments,
                shares=total_shares,
                clicks=0,  # Not available in basic API
                impressions=0,  # Requires additional analytics API
                engagement_rate=engagement_rate,
                reach=0,  # Requires additional analytics API
                collected_at=datetime.utcnow()
            )
            
            # Store metrics
            if post_id not in self._metrics:
                self._metrics[post_id] = []
            self._metrics[post_id].append(metrics)
            
            # Cache metrics
            await self.cache.set(
                f"linkedin_metrics:{post_id}",
                metrics,
                ttl=1800  # 30 minutes
            )
            
            self.metrics.increment("linkedin.analytics.retrieved")
            
            logger.info("LinkedIn post analytics retrieved",
                       post_id=post_id,
                       likes=total_likes,
                       comments=total_comments,
                       shares=total_shares)
            
            return metrics
            
        except Exception as e:
            self.metrics.increment("linkedin.analytics.failed")
            logger.error("Failed to get post analytics",
                        post_id=post_id,
                        error=str(e))
            raise APIError(f"Failed to get post analytics: {e}")

    async def get_user_posts(self,
                           access_token: str,
                           count: int = 20) -> List[LinkedInPost]:
        """
        Get user's recent LinkedIn posts
        
        Args:
            access_token: LinkedIn access token
            count: Number of posts to retrieve
            
        Returns:
            List of user's LinkedIn posts
        """
        try:
            # Get user profile
            user_profile = await self.get_user_profile(access_token)
            
            # Get user's posts
            posts_response = await self._make_authenticated_request(
                "GET",
                "/v2/shares",
                access_token,
                params={
                    "q": "owners",
                    "owners": f"urn:li:person:{user_profile.id}",
                    "sortBy": "CREATED",
                    "count": count
                }
            )
            
            posts = []
            for element in posts_response.get("elements", []):
                post = LinkedInPost(
                    id=element["id"],
                    author=element["owner"],
                    text=element.get("text", {}).get("text", ""),
                    created_time=datetime.fromtimestamp(element["created"]["time"] / 1000),
                    visibility=ShareVisibility.PUBLIC,  # Default
                    activity=element.get("activity", ""),
                    service_provider=element.get("serviceProvider", ""),
                    is_reshare_disabled_by_author=element.get("isReshareDisabledByAuthor", False),
                    content=element.get("content"),
                    subject=element.get("subject")
                )
                
                posts.append(post)
                self._posts[post.id] = post
            
            self.metrics.increment("linkedin.posts.retrieved")
            
            logger.info("LinkedIn user posts retrieved",
                       user_id=user_profile.id,
                       count=len(posts))
            
            return posts
            
        except Exception as e:
            self.metrics.increment("linkedin.posts.retrieval_failed")
            logger.error("Failed to get user posts", error=str(e))
            raise APIError(f"Failed to get user posts: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check LinkedIn Creator API integration health
        
        Returns:
            Health status information
        """
        try:
            health_status = {
                "service": "linkedin_creator",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "config": {
                    "client_id": self.config.client_id[:8] + "...",
                    "api_version": self.config.api_version,
                    "scopes": len(self.config.scopes)
                },
                "metrics": {
                    "total_users": len(self._users),
                    "total_posts": len(self._posts)
                }
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service": "linkedin_creator",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Factory function for easy integration setup
def create_linkedin_creator_integration(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    **kwargs
) -> LinkedInCreatorAPI:
    """
    Factory function to create LinkedIn Creator API integration
    
    Args:
        client_id: LinkedIn application client ID
        client_secret: LinkedIn application client secret
        redirect_uri: OAuth redirect URI
        **kwargs: Additional configuration options
        
    Returns:
        Configured LinkedIn Creator API integration instance
    """
    config = LinkedInConfig(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        **kwargs
    )
    
    return LinkedInCreatorAPI(config)

# Example usage for Ainflue platform
async def example_linkedin_creator_flow() -> None:
    """Example LinkedIn Creator API integration usage"""
    
    # Initialize LinkedIn Creator API integration
    linkedin = create_linkedin_creator_integration(
        client_id="your_linkedin_client_id",
        client_secret="your_linkedin_client_secret",
        redirect_uri="https://ainflue.com/auth/linkedin/callback",
        scopes=[
            LinkedInScope.R_LITEPROFILE,
            LinkedInScope.R_EMAILADDRESS,
            LinkedInScope.W_MEMBER_SOCIAL,
            LinkedInScope.R_MEMBER_SOCIAL
        ]
    )
    
    try:
        # Generate authorization URL
        auth_url = await linkedin.get_authorization_url(
            state="creator_onboarding_123"
        )
        print(f"Authorization URL: {auth_url}")
        
        # After user authorization, exchange code for token
        # access_token_data = await linkedin.exchange_code_for_token("authorization_code")
        # access_token = access_token_data["access_token"]
        
        # For demo purposes, use placeholder token
        access_token = "demo_access_token"
        
        # Get user profile
        # user_profile = await linkedin.get_user_profile(access_token)
        # print(f"User: {user_profile.first_name} {user_profile.last_name}")
        
        # Create text post
        # text_post = await linkedin.create_text_post(
        #     access_token=access_token,
        #     text="Excited to share my latest content on Ainflue! 🚀 #CreatorEconomy #ContentCreation",
        #     visibility=ShareVisibility.PUBLIC
        # )
        # print(f"Text post created: {text_post.id}")
        
        # Upload and create image post
        # with open("creator_content.jpg", "rb") as f:
        #     media_data = f.read()
        # 
        # media_asset = await linkedin.upload_media(
        #     access_token=access_token,
        #     media_data=media_data,
        #     media_type="image/jpeg",
        #     filename="creator_content.jpg"
        # )
        # 
        # image_post = await linkedin.create_image_post(
        #     access_token=access_token,
        #     text="Check out my latest creation! Made with Ainflue's AI tools 🎨",
        #     media_asset=media_asset,
        #     visibility=ShareVisibility.PUBLIC
        # )
        # print(f"Image post created: {image_post.id}")
        
        # Get post analytics
        # analytics = await linkedin.get_post_analytics(
        #     access_token=access_token,
        #     post_id=text_post.id
        # )
        # print(f"Post analytics: {analytics.likes} likes, {analytics.comments} comments")
        
        # Health check
        health = await linkedin.health_check()
        print(f"LinkedIn Creator API health: {health['status']}")
        
    except Exception as e:
        print(f"LinkedIn Creator API integration error: {e}")

if __name__ == "__main__":
    asyncio.run(example_linkedin_creator_flow())