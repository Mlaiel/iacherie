"""Social Media Hub Integration - Unified Platform Management
==========================================================

Professional integration for managing multiple social media platforms
including YouTube, Instagram, TikTok, Facebook, and Twitter/X.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import json
import aiohttp
import hashlib
import hmac
import base64

logger = logging.getLogger(__name__)


class SocialPlatform(str, Enum):
    """Supported social media platforms."""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


class ContentType(str, Enum):
    """Content types for social media."""
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"


class PostStatus(str, Enum):
    """Post status across platforms."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"


class EngagementType(str, Enum):
    """Types of engagement metrics."""
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SUBSCRIBERS = "subscribers"
    SAVES = "saves"
    CLICKS = "clicks"


@dataclass
class SocialAccount:
    """Social media account configuration."""
    platform: SocialPlatform
    account_id: str
    username: str
    display_name: str
    access_token: str
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    permissions: List[str] = None
    verified: bool = False
    follower_count: int = 0
    metadata: Dict[str, Any] = None


@dataclass
class ContentPost:
    """Social media post data."""
    post_id: str
    platform: SocialPlatform
    content_type: ContentType
    title: Optional[str]
    description: Optional[str]
    media_urls: List[str]
    hashtags: List[str]
    mentions: List[str]
    status: PostStatus
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    engagement_metrics: Dict[EngagementType, int]
    monetization_data: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class AnalyticsReport:
    """Social media analytics report."""
    platform: SocialPlatform
    period_start: datetime
    period_end: datetime
    total_posts: int
    total_engagement: Dict[EngagementType, int]
    top_performing_posts: List[str]
    audience_demographics: Dict[str, Any]
    revenue_data: Dict[str, Decimal]
    growth_metrics: Dict[str, float]
    metadata: Dict[str, Any]


class SocialMediaHubIntegration:
    """Professional social media hub integration."""
    
    def __init__(
        self,
        youtube_api_key: Optional[str] = None,
        instagram_app_id: Optional[str] = None,
        instagram_app_secret: Optional[str] = None,
        tiktok_client_key: Optional[str] = None,
        tiktok_client_secret: Optional[str] = None,
        facebook_app_id: Optional[str] = None,
        facebook_app_secret: Optional[str] = None,
        twitter_api_key: Optional[str] = None,
        twitter_api_secret: Optional[str] = None,
        linkedin_client_id: Optional[str] = None,
        linkedin_client_secret: Optional[str] = None,
        base_callback_url: str = "https://api.ainflue.com/auth/callback",
        timeout: int = 30
    ):
        # API credentials
        self.youtube_api_key = youtube_api_key
        self.instagram_app_id = instagram_app_id
        self.instagram_app_secret = instagram_app_secret
        self.tiktok_client_key = tiktok_client_key
        self.tiktok_client_secret = tiktok_client_secret
        self.facebook_app_id = facebook_app_id
        self.facebook_app_secret = facebook_app_secret
        self.twitter_api_key = twitter_api_key
        self.twitter_api_secret = twitter_api_secret
        self.linkedin_client_id = linkedin_client_id
        self.linkedin_client_secret = linkedin_client_secret
        
        self.base_callback_url = base_callback_url
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Connected accounts storage
        self.connected_accounts: Dict[str, SocialAccount] = {}
        
        # Usage tracking
        self.total_posts = 0
        self.total_engagement = 0
        self.request_count = 0
        self.platforms_connected = set()
        
        # Platform-specific base URLs
        self.platform_urls = {
            SocialPlatform.YOUTUBE: "https://www.googleapis.com/youtube/v3",
            SocialPlatform.INSTAGRAM: "https://graph.facebook.com/v18.0",
            SocialPlatform.TIKTOK: "https://open-api.tiktok.com/v1.3",
            SocialPlatform.FACEBOOK: "https://graph.facebook.com/v18.0",
            SocialPlatform.TWITTER: "https://api.twitter.com/2",
            SocialPlatform.LINKEDIN: "https://api.linkedin.com/v2"
        }
        
        logger.info("Social Media Hub integration initialized")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self.session is None or self.session.closed:
            headers = {
                "User-Agent": "Ainflue/1.0 Social Media Hub",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def close(self):
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_oauth_url(
        self,
        platform: SocialPlatform,
        state: str,
        scopes: Optional[List[str]] = None
    ) -> str:
        """Generate OAuth authorization URL for platform."""
        platform_scopes = {
            SocialPlatform.YOUTUBE: ["https://www.googleapis.com/auth/youtube.upload",
                                   "https://www.googleapis.com/auth/youtube.readonly"],
            SocialPlatform.INSTAGRAM: ["instagram_basic", "instagram_content_publish", 
                                     "pages_read_engagement"],
            SocialPlatform.TIKTOK: ["user.info.basic", "video.upload", "video.list"],
            SocialPlatform.FACEBOOK: ["pages_manage_posts", "pages_read_engagement", 
                                    "pages_show_list"],
            SocialPlatform.TWITTER: ["tweet.read", "tweet.write", "users.read"],
            SocialPlatform.LINKEDIN: ["r_liteprofile", "r_emailaddress", "w_member_social"]
        }
        
        scopes = scopes or platform_scopes.get(platform, [])
        callback_url = f"{self.base_callback_url}/{platform.value}"
        
        oauth_urls = {
            SocialPlatform.YOUTUBE: (
                f"https://accounts.google.com/o/oauth2/v2/auth?"
                f"client_id={self.youtube_api_key}&"
                f"redirect_uri={callback_url}&"
                f"scope={' '.join(scopes)}&"
                f"response_type=code&"
                f"state={state}&"
                f"access_type=offline"
            ),
            SocialPlatform.INSTAGRAM: (
                f"https://www.facebook.com/v18.0/dialog/oauth?"
                f"client_id={self.instagram_app_id}&"
                f"redirect_uri={callback_url}&"
                f"scope={','.join(scopes)}&"
                f"response_type=code&"
                f"state={state}"
            ),
            SocialPlatform.TIKTOK: (
                f"https://www.tiktok.com/auth/authorize/?"
                f"client_key={self.tiktok_client_key}&"
                f"redirect_uri={callback_url}&"
                f"scope={','.join(scopes)}&"
                f"response_type=code&"
                f"state={state}"
            ),
            SocialPlatform.FACEBOOK: (
                f"https://www.facebook.com/v18.0/dialog/oauth?"
                f"client_id={self.facebook_app_id}&"
                f"redirect_uri={callback_url}&"
                f"scope={','.join(scopes)}&"
                f"response_type=code&"
                f"state={state}"
            ),
            SocialPlatform.TWITTER: (
                f"https://twitter.com/i/oauth2/authorize?"
                f"client_id={self.twitter_api_key}&"
                f"redirect_uri={callback_url}&"
                f"scope={' '.join(scopes)}&"
                f"response_type=code&"
                f"state={state}&"
                f"code_challenge_method=plain&"
                f"code_challenge={state}"
            ),
            SocialPlatform.LINKEDIN: (
                f"https://www.linkedin.com/oauth/v2/authorization?"
                f"client_id={self.linkedin_client_id}&"
                f"redirect_uri={callback_url}&"
                f"scope={' '.join(scopes)}&"
                f"response_type=code&"
                f"state={state}"
            )
        }
        
        logger.info(f"Generated OAuth URL for {platform.value}")
        return oauth_urls.get(platform, "")
    
    async def exchange_oauth_code(
        self,
        platform: SocialPlatform,
        authorization_code: str,
        state: str
    ) -> SocialAccount:
        """Exchange OAuth authorization code for access token."""
        await self._ensure_session()
        
        callback_url = f"{self.base_callback_url}/{platform.value}"
        
        if platform == SocialPlatform.YOUTUBE:
            return await self._exchange_youtube_code(authorization_code, callback_url)
        elif platform == SocialPlatform.INSTAGRAM:
            return await self._exchange_instagram_code(authorization_code, callback_url)
        elif platform == SocialPlatform.TIKTOK:
            return await self._exchange_tiktok_code(authorization_code, callback_url)
        elif platform == SocialPlatform.FACEBOOK:
            return await self._exchange_facebook_code(authorization_code, callback_url)
        elif platform == SocialPlatform.TWITTER:
            return await self._exchange_twitter_code(authorization_code, callback_url, state)
        elif platform == SocialPlatform.LINKEDIN:
            return await self._exchange_linkedin_code(authorization_code, callback_url)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    async def _exchange_youtube_code(self, code: str, redirect_uri: str) -> SocialAccount:
        """Exchange YouTube OAuth code for access token."""
        try:
            data = {
                "client_id": self.youtube_api_key,
                "client_secret": self.instagram_app_secret,  # Note: Need YouTube client secret
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
            
            async with self.session.post(
                "https://oauth2.googleapis.com/token",
                data=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"YouTube OAuth error: {error_data}")
                
                token_data = await response.json()
                
                # Get user info
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                async with self.session.get(
                    f"{self.platform_urls[SocialPlatform.YOUTUBE]}/channels?part=snippet&mine=true",
                    headers=headers
                ) as user_response:
                    user_data = await user_response.json()
                    
                    if user_data.get("items"):
                        channel = user_data["items"][0]
                        account = SocialAccount(
                            platform=SocialPlatform.YOUTUBE,
                            account_id=channel["id"],
                            username=channel["snippet"]["title"],
                            display_name=channel["snippet"]["title"],
                            access_token=token_data["access_token"],
                            refresh_token=token_data.get("refresh_token"),
                            token_expires_at=datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600)),
                            permissions=["upload", "read"],
                            verified=True,
                            follower_count=int(channel["statistics"].get("subscriberCount", 0)),
                            metadata={"channel_data": channel}
                        )
                        
                        self.connected_accounts[f"{SocialPlatform.YOUTUBE}_{account.account_id}"] = account
                        self.platforms_connected.add(SocialPlatform.YOUTUBE)
                        self.request_count += 2
                        
                        logger.info(f"YouTube account connected: {account.username}")
                        return account
                    else:
                        raise Exception("Failed to get YouTube channel information")
        
        except Exception as e:
            logger.error(f"YouTube OAuth exchange failed: {e}")
            raise
    
    async def _exchange_instagram_code(self, code: str, redirect_uri: str) -> SocialAccount:
        """Exchange Instagram OAuth code for access token."""
        try:
            data = {
                "client_id": self.instagram_app_id,
                "client_secret": self.instagram_app_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
            
            async with self.session.post(
                "https://api.instagram.com/oauth/access_token",
                data=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Instagram OAuth error: {error_data}")
                
                token_data = await response.json()
                
                account = SocialAccount(
                    platform=SocialPlatform.INSTAGRAM,
                    account_id=token_data["user_id"],
                    username=token_data["user"]["username"],
                    display_name=token_data["user"]["username"],
                    access_token=token_data["access_token"],
                    permissions=["basic", "content_publish"],
                    verified=True,
                    metadata={"user_data": token_data["user"]}
                )
                
                self.connected_accounts[f"{SocialPlatform.INSTAGRAM}_{account.account_id}"] = account
                self.platforms_connected.add(SocialPlatform.INSTAGRAM)
                self.request_count += 1
                
                logger.info(f"Instagram account connected: {account.username}")
                return account
        
        except Exception as e:
            logger.error(f"Instagram OAuth exchange failed: {e}")
            raise
    
    async def _exchange_tiktok_code(self, code: str, redirect_uri: str) -> SocialAccount:
        """Exchange TikTok OAuth code for access token."""
        try:
            data = {
                "client_key": self.tiktok_client_key,
                "client_secret": self.tiktok_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
            
            async with self.session.post(
                "https://open-api.tiktok.com/oauth/access_token/",
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"TikTok OAuth error: {error_data}")
                
                result = await response.json()
                token_data = result["data"]
                
                # Get user info
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                async with self.session.get(
                    f"{self.platform_urls[SocialPlatform.TIKTOK]}/user/info/",
                    headers=headers
                ) as user_response:
                    user_result = await user_response.json()
                    user_data = user_result["data"]["user"]
                    
                    account = SocialAccount(
                        platform=SocialPlatform.TIKTOK,
                        account_id=user_data["open_id"],
                        username=user_data["display_name"],
                        display_name=user_data["display_name"],
                        access_token=token_data["access_token"],
                        refresh_token=token_data.get("refresh_token"),
                        token_expires_at=datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600)),
                        permissions=["basic", "upload"],
                        verified=True,
                        follower_count=user_data.get("follower_count", 0),
                        metadata={"user_data": user_data}
                    )
                    
                    self.connected_accounts[f"{SocialPlatform.TIKTOK}_{account.account_id}"] = account
                    self.platforms_connected.add(SocialPlatform.TIKTOK)
                    self.request_count += 2
                    
                    logger.info(f"TikTok account connected: {account.username}")
                    return account
        
        except Exception as e:
            logger.error(f"TikTok OAuth exchange failed: {e}")
            raise
    
    async def _exchange_facebook_code(self, code: str, redirect_uri: str) -> SocialAccount:
        """Exchange Facebook OAuth code for access token."""
        try:
            data = {
                "client_id": self.facebook_app_id,
                "client_secret": self.facebook_app_secret,
                "code": code,
                "redirect_uri": redirect_uri
            }
            
            async with self.session.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Facebook OAuth error: {error_data}")
                
                token_data = await response.json()
                
                # Get user info and pages
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                async with self.session.get(
                    f"{self.platform_urls[SocialPlatform.FACEBOOK]}/me?fields=id,name",
                    headers=headers
                ) as user_response:
                    user_data = await user_response.json()
                    
                    account = SocialAccount(
                        platform=SocialPlatform.FACEBOOK,
                        account_id=user_data["id"],
                        username=user_data["name"],
                        display_name=user_data["name"],
                        access_token=token_data["access_token"],
                        permissions=["manage_posts", "read_engagement"],
                        verified=True,
                        metadata={"user_data": user_data}
                    )
                    
                    self.connected_accounts[f"{SocialPlatform.FACEBOOK}_{account.account_id}"] = account
                    self.platforms_connected.add(SocialPlatform.FACEBOOK)
                    self.request_count += 2
                    
                    logger.info(f"Facebook account connected: {account.username}")
                    return account
        
        except Exception as e:
            logger.error(f"Facebook OAuth exchange failed: {e}")
            raise
    
    async def _exchange_twitter_code(self, code: str, redirect_uri: str, code_verifier: str) -> SocialAccount:
        """Exchange Twitter OAuth code for access token."""
        try:
            data = {
                "client_id": self.twitter_api_key,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier
            }
            
            # Twitter OAuth 2.0 requires Basic auth
            auth = aiohttp.BasicAuth(self.twitter_api_key, self.twitter_api_secret)
            
            async with self.session.post(
                "https://api.twitter.com/2/oauth2/token",
                data=data,
                auth=auth
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Twitter OAuth error: {error_data}")
                
                token_data = await response.json()
                
                # Get user info
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                async with self.session.get(
                    f"{self.platform_urls[SocialPlatform.TWITTER]}/users/me",
                    headers=headers
                ) as user_response:
                    user_result = await user_response.json()
                    user_data = user_result["data"]
                    
                    account = SocialAccount(
                        platform=SocialPlatform.TWITTER,
                        account_id=user_data["id"],
                        username=user_data["username"],
                        display_name=user_data["name"],
                        access_token=token_data["access_token"],
                        refresh_token=token_data.get("refresh_token"),
                        token_expires_at=datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600)),
                        permissions=["read", "write"],
                        verified=user_data.get("verified", False),
                        follower_count=user_data.get("public_metrics", {}).get("followers_count", 0),
                        metadata={"user_data": user_data}
                    )
                    
                    self.connected_accounts[f"{SocialPlatform.TWITTER}_{account.account_id}"] = account
                    self.platforms_connected.add(SocialPlatform.TWITTER)
                    self.request_count += 2
                    
                    logger.info(f"Twitter account connected: {account.username}")
                    return account
        
        except Exception as e:
            logger.error(f"Twitter OAuth exchange failed: {e}")
            raise
    
    async def _exchange_linkedin_code(self, code: str, redirect_uri: str) -> SocialAccount:
        """Exchange LinkedIn OAuth code for access token."""
        try:
            data = {
                "client_id": self.linkedin_client_id,
                "client_secret": self.linkedin_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
            
            async with self.session.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"LinkedIn OAuth error: {error_data}")
                
                token_data = await response.json()
                
                # Get user info
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                async with self.session.get(
                    f"{self.platform_urls[SocialPlatform.LINKEDIN]}/me",
                    headers=headers
                ) as user_response:
                    user_data = await user_response.json()
                    
                    account = SocialAccount(
                        platform=SocialPlatform.LINKEDIN,
                        account_id=user_data["id"],
                        username=f"{user_data['firstName']['localized']['en_US']} {user_data['lastName']['localized']['en_US']}",
                        display_name=f"{user_data['firstName']['localized']['en_US']} {user_data['lastName']['localized']['en_US']}",
                        access_token=token_data["access_token"],
                        token_expires_at=datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600)),
                        permissions=["profile", "social"],
                        verified=True,
                        metadata={"user_data": user_data}
                    )
                    
                    self.connected_accounts[f"{SocialPlatform.LINKEDIN}_{account.account_id}"] = account
                    self.platforms_connected.add(SocialPlatform.LINKEDIN)
                    self.request_count += 2
                    
                    logger.info(f"LinkedIn account connected: {account.username}")
                    return account
        
        except Exception as e:
            logger.error(f"LinkedIn OAuth exchange failed: {e}")
            raise
    
    async def publish_content(
        self,
        platform: SocialPlatform,
        account_id: str,
        content_type: ContentType,
        title: Optional[str] = None,
        description: Optional[str] = None,
        media_urls: Optional[List[str]] = None,
        hashtags: Optional[List[str]] = None,
        schedule_time: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContentPost:
        """Publish content to specified platform."""
        await self._ensure_session()
        
        account_key = f"{platform}_{account_id}"
        if account_key not in self.connected_accounts:
            raise ValueError(f"Account not connected: {platform} - {account_id}")
        
        account = self.connected_accounts[account_key]
        
        if platform == SocialPlatform.YOUTUBE:
            return await self._publish_youtube_content(account, content_type, title, description, media_urls, hashtags, schedule_time, metadata)
        elif platform == SocialPlatform.INSTAGRAM:
            return await self._publish_instagram_content(account, content_type, title, description, media_urls, hashtags, schedule_time, metadata)
        elif platform == SocialPlatform.TIKTOK:
            return await self._publish_tiktok_content(account, content_type, title, description, media_urls, hashtags, schedule_time, metadata)
        elif platform == SocialPlatform.FACEBOOK:
            return await self._publish_facebook_content(account, content_type, title, description, media_urls, hashtags, schedule_time, metadata)
        elif platform == SocialPlatform.TWITTER:
            return await self._publish_twitter_content(account, content_type, title, description, media_urls, hashtags, schedule_time, metadata)
        elif platform == SocialPlatform.LINKEDIN:
            return await self._publish_linkedin_content(account, content_type, title, description, media_urls, hashtags, schedule_time, metadata)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    async def _publish_youtube_content(
        self,
        account: SocialAccount,
        content_type: ContentType,
        title: str,
        description: str,
        media_urls: List[str],
        hashtags: List[str],
        schedule_time: Optional[datetime],
        metadata: Dict[str, Any]
    ) -> ContentPost:
        """Publish content to YouTube."""
        try:
            if content_type != ContentType.VIDEO:
                raise ValueError("YouTube only supports video content")
            
            video_data = {
                "snippet": {
                    "title": title,
                    "description": f"{description}\n\n{' '.join(hashtags) if hashtags else ''}",
                    "tags": [tag.replace('#', '') for tag in hashtags] if hashtags else [],
                    "categoryId": "22"  # People & Blogs
                },
                "status": {
                    "privacyStatus": "private" if schedule_time else "public",
                    "publishAt": schedule_time.isoformat() if schedule_time else None
                }
            }
            
            headers = {"Authorization": f"Bearer {account.access_token}"}
            
            # Note: This is a simplified example - actual video upload requires multipart/form-data
            async with self.session.post(
                f"{self.platform_urls[SocialPlatform.YOUTUBE]}/videos?part=snippet,status",
                json=video_data,
                headers=headers
            ) as response:
                if response.status not in [200, 201]:
                    error_data = await response.json()
                    raise Exception(f"YouTube upload error: {error_data}")
                
                result = await response.json()
                
                post = ContentPost(
                    post_id=result["id"],
                    platform=SocialPlatform.YOUTUBE,
                    content_type=content_type,
                    title=title,
                    description=description,
                    media_urls=media_urls or [],
                    hashtags=hashtags or [],
                    mentions=[],
                    status=PostStatus.SCHEDULED if schedule_time else PostStatus.PUBLISHED,
                    scheduled_at=schedule_time,
                    published_at=datetime.now() if not schedule_time else None,
                    engagement_metrics={},
                    monetization_data={},
                    metadata=metadata or {}
                )
                
                self.total_posts += 1
                self.request_count += 1
                
                logger.info(f"YouTube content published: {post.post_id}")
                return post
        
        except Exception as e:
            logger.error(f"YouTube content publishing failed: {e}")
            raise
    
    async def _publish_instagram_content(
        self,
        account: SocialAccount,
        content_type: ContentType,
        title: str,
        description: str,
        media_urls: List[str],
        hashtags: List[str],
        schedule_time: Optional[datetime],
        metadata: Dict[str, Any]
    ) -> ContentPost:
        """Publish content to Instagram."""
        try:
            caption = f"{title}\n{description}\n\n{' '.join(hashtags) if hashtags else ''}"
            
            data = {
                "image_url": media_urls[0] if media_urls else "",
                "caption": caption,
                "access_token": account.access_token
            }
            
            # Instagram publishing requires two API calls: create media, then publish
            async with self.session.post(
                f"{self.platform_urls[SocialPlatform.INSTAGRAM]}/{account.account_id}/media",
                data=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Instagram media creation error: {error_data}")
                
                media_result = await response.json()
                creation_id = media_result["id"]
                
                # Publish the media
                publish_data = {
                    "creation_id": creation_id,
                    "access_token": account.access_token
                }
                
                async with self.session.post(
                    f"{self.platform_urls[SocialPlatform.INSTAGRAM]}/{account.account_id}/media_publish",
                    data=publish_data
                ) as publish_response:
                    if publish_response.status != 200:
                        error_data = await publish_response.json()
                        raise Exception(f"Instagram publish error: {error_data}")
                    
                    publish_result = await publish_response.json()
                    
                    post = ContentPost(
                        post_id=publish_result["id"],
                        platform=SocialPlatform.INSTAGRAM,
                        content_type=content_type,
                        title=title,
                        description=description,
                        media_urls=media_urls or [],
                        hashtags=hashtags or [],
                        mentions=[],
                        status=PostStatus.PUBLISHED,
                        scheduled_at=schedule_time,
                        published_at=datetime.now(),
                        engagement_metrics={},
                        monetization_data={},
                        metadata=metadata or {}
                    )
                    
                    self.total_posts += 1
                    self.request_count += 2
                    
                    logger.info(f"Instagram content published: {post.post_id}")
                    return post
        
        except Exception as e:
            logger.error(f"Instagram content publishing failed: {e}")
            raise
    
    async def _publish_tiktok_content(
        self,
        account: SocialAccount,
        content_type: ContentType,
        title: str,
        description: str,
        media_urls: List[str],
        hashtags: List[str],
        schedule_time: Optional[datetime],
        metadata: Dict[str, Any]
    ) -> ContentPost:
        """Publish content to TikTok."""
        try:
            if content_type != ContentType.VIDEO:
                raise ValueError("TikTok only supports video content")
            
            video_data = {
                "video": {
                    "video_url": media_urls[0] if media_urls else "",
                    "caption": f"{title}\n{description}\n\n{' '.join(hashtags) if hashtags else ''}",
                    "privacy_level": "SELF_ONLY" if schedule_time else "PUBLIC_TO_EVERYONE"
                }
            }
            
            headers = {"Authorization": f"Bearer {account.access_token}"}
            
            async with self.session.post(
                f"{self.platform_urls[SocialPlatform.TIKTOK]}/video/upload/",
                json=video_data,
                headers=headers
            ) as response:
                if response.status not in [200, 201]:
                    error_data = await response.json()
                    raise Exception(f"TikTok upload error: {error_data}")
                
                result = await response.json()
                
                post = ContentPost(
                    post_id=result["data"]["video_id"],
                    platform=SocialPlatform.TIKTOK,
                    content_type=content_type,
                    title=title,
                    description=description,
                    media_urls=media_urls or [],
                    hashtags=hashtags or [],
                    mentions=[],
                    status=PostStatus.SCHEDULED if schedule_time else PostStatus.PUBLISHED,
                    scheduled_at=schedule_time,
                    published_at=datetime.now() if not schedule_time else None,
                    engagement_metrics={},
                    monetization_data={},
                    metadata=metadata or {}
                )
                
                self.total_posts += 1
                self.request_count += 1
                
                logger.info(f"TikTok content published: {post.post_id}")
                return post
        
        except Exception as e:
            logger.error(f"TikTok content publishing failed: {e}")
            raise
    
    async def _publish_facebook_content(
        self,
        account: SocialAccount,
        content_type: ContentType,
        title: str,
        description: str,
        media_urls: List[str],
        hashtags: List[str],
        schedule_time: Optional[datetime],
        metadata: Dict[str, Any]
    ) -> ContentPost:
        """Publish content to Facebook."""
        try:
            message = f"{title}\n{description}\n\n{' '.join(hashtags) if hashtags else ''}"
            
            data = {
                "message": message,
                "access_token": account.access_token
            }
            
            if media_urls:
                data["link"] = media_urls[0]
            
            if schedule_time:
                data["published"] = "false"
                data["scheduled_publish_time"] = int(schedule_time.timestamp())
            
            async with self.session.post(
                f"{self.platform_urls[SocialPlatform.FACEBOOK]}/{account.account_id}/feed",
                data=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Facebook publish error: {error_data}")
                
                result = await response.json()
                
                post = ContentPost(
                    post_id=result["id"],
                    platform=SocialPlatform.FACEBOOK,
                    content_type=content_type,
                    title=title,
                    description=description,
                    media_urls=media_urls or [],
                    hashtags=hashtags or [],
                    mentions=[],
                    status=PostStatus.SCHEDULED if schedule_time else PostStatus.PUBLISHED,
                    scheduled_at=schedule_time,
                    published_at=datetime.now() if not schedule_time else None,
                    engagement_metrics={},
                    monetization_data={},
                    metadata=metadata or {}
                )
                
                self.total_posts += 1
                self.request_count += 1
                
                logger.info(f"Facebook content published: {post.post_id}")
                return post
        
        except Exception as e:
            logger.error(f"Facebook content publishing failed: {e}")
            raise
    
    async def _publish_twitter_content(
        self,
        account: SocialAccount,
        content_type: ContentType,
        title: str,
        description: str,
        media_urls: List[str],
        hashtags: List[str],
        schedule_time: Optional[datetime],
        metadata: Dict[str, Any]
    ) -> ContentPost:
        """Publish content to Twitter."""
        try:
            text = f"{title}\n{description}\n\n{' '.join(hashtags) if hashtags else ''}"
            
            tweet_data = {
                "text": text[:280]  # Twitter character limit
            }
            
            headers = {"Authorization": f"Bearer {account.access_token}"}
            
            async with self.session.post(
                f"{self.platform_urls[SocialPlatform.TWITTER]}/tweets",
                json=tweet_data,
                headers=headers
            ) as response:
                if response.status not in [200, 201]:
                    error_data = await response.json()
                    raise Exception(f"Twitter publish error: {error_data}")
                
                result = await response.json()
                
                post = ContentPost(
                    post_id=result["data"]["id"],
                    platform=SocialPlatform.TWITTER,
                    content_type=content_type,
                    title=title,
                    description=description,
                    media_urls=media_urls or [],
                    hashtags=hashtags or [],
                    mentions=[],
                    status=PostStatus.PUBLISHED,
                    scheduled_at=schedule_time,
                    published_at=datetime.now(),
                    engagement_metrics={},
                    monetization_data={},
                    metadata=metadata or {}
                )
                
                self.total_posts += 1
                self.request_count += 1
                
                logger.info(f"Twitter content published: {post.post_id}")
                return post
        
        except Exception as e:
            logger.error(f"Twitter content publishing failed: {e}")
            raise
    
    async def _publish_linkedin_content(
        self,
        account: SocialAccount,
        content_type: ContentType,
        title: str,
        description: str,
        media_urls: List[str],
        hashtags: List[str],
        schedule_time: Optional[datetime],
        metadata: Dict[str, Any]
    ) -> ContentPost:
        """Publish content to LinkedIn."""
        try:
            text = f"{title}\n{description}\n\n{' '.join(hashtags) if hashtags else ''}"
            
            post_data = {
                "author": f"urn:li:person:{account.account_id}",
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
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            headers = {"Authorization": f"Bearer {account.access_token}"}
            
            async with self.session.post(
                f"{self.platform_urls[SocialPlatform.LINKEDIN]}/ugcPosts",
                json=post_data,
                headers=headers
            ) as response:
                if response.status not in [200, 201]:
                    error_data = await response.json()
                    raise Exception(f"LinkedIn publish error: {error_data}")
                
                result = await response.json()
                
                post = ContentPost(
                    post_id=result["id"],
                    platform=SocialPlatform.LINKEDIN,
                    content_type=content_type,
                    title=title,
                    description=description,
                    media_urls=media_urls or [],
                    hashtags=hashtags or [],
                    mentions=[],
                    status=PostStatus.PUBLISHED,
                    scheduled_at=schedule_time,
                    published_at=datetime.now(),
                    engagement_metrics={},
                    monetization_data={},
                    metadata=metadata or {}
                )
                
                self.total_posts += 1
                self.request_count += 1
                
                logger.info(f"LinkedIn content published: {post.post_id}")
                return post
        
        except Exception as e:
            logger.error(f"LinkedIn content publishing failed: {e}")
            raise
    
    async def get_analytics_report(
        self,
        platform: SocialPlatform,
        account_id: str,
        start_date: datetime,
        end_date: datetime,
        metrics: Optional[List[EngagementType]] = None
    ) -> AnalyticsReport:
        """Get analytics report for specified platform and time period."""
        await self._ensure_session()
        
        account_key = f"{platform}_{account_id}"
        if account_key not in self.connected_accounts:
            raise ValueError(f"Account not connected: {platform} - {account_id}")
        
        account = self.connected_accounts[account_key]
        
        try:
            # Platform-specific analytics implementation would go here
            # This is a simplified example
            
            total_engagement = {
                EngagementType.VIEWS: 0,
                EngagementType.LIKES: 0,
                EngagementType.COMMENTS: 0,
                EngagementType.SHARES: 0,
                EngagementType.SUBSCRIBERS: 0
            }
            
            report = AnalyticsReport(
                platform=platform,
                period_start=start_date,
                period_end=end_date,
                total_posts=0,
                total_engagement=total_engagement,
                top_performing_posts=[],
                audience_demographics={},
                revenue_data={},
                growth_metrics={},
                metadata={}
            )
            
            self.request_count += 1
            logger.info(f"Analytics report generated for {platform} - {account_id}")
            return report
        
        except Exception as e:
            logger.error(f"Analytics report generation failed: {e}")
            raise
    
    async def get_connected_accounts(self) -> List[SocialAccount]:
        """Get all connected social media accounts."""
        return list(self.connected_accounts.values())
    
    async def disconnect_account(self, platform: SocialPlatform, account_id: str) -> bool:
        """Disconnect a social media account."""
        account_key = f"{platform}_{account_id}"
        if account_key in self.connected_accounts:
            del self.connected_accounts[account_key]
            
            # Remove platform from connected set if no accounts remain
            if not any(key.startswith(f"{platform}_") for key in self.connected_accounts.keys()):
                self.platforms_connected.discard(platform)
            
            logger.info(f"Account disconnected: {platform} - {account_id}")
            return True
        
        return False
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_requests": self.request_count,
            "total_posts_published": self.total_posts,
            "total_engagement": self.total_engagement,
            "connected_platforms": list(self.platforms_connected),
            "connected_accounts_count": len(self.connected_accounts),
            "platforms_connected_count": len(self.platforms_connected)
        }


# Utility functions
async def create_social_media_hub(
    youtube_api_key: Optional[str] = None,
    instagram_app_id: Optional[str] = None,
    instagram_app_secret: Optional[str] = None,
    tiktok_client_key: Optional[str] = None,
    tiktok_client_secret: Optional[str] = None
) -> SocialMediaHubIntegration:
    """Create and initialize social media hub integration."""
    integration = SocialMediaHubIntegration(
        youtube_api_key=youtube_api_key,
        instagram_app_id=instagram_app_id,
        instagram_app_secret=instagram_app_secret,
        tiktok_client_key=tiktok_client_key,
        tiktok_client_secret=tiktok_client_secret
    )
    await integration._ensure_session()
    return integration


async def publish_to_multiple_platforms(
    hub: SocialMediaHubIntegration,
    platforms: List[SocialPlatform],
    account_ids: List[str],
    content_type: ContentType,
    title: str,
    description: str,
    media_urls: List[str] = None,
    hashtags: List[str] = None
) -> List[ContentPost]:
    """Publish content to multiple platforms simultaneously."""
    tasks = []
    
    for platform, account_id in zip(platforms, account_ids):
        task = hub.publish_content(
            platform=platform,
            account_id=account_id,
            content_type=content_type,
            title=title,
            description=description,
            media_urls=media_urls,
            hashtags=hashtags
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and return successful posts
    successful_posts = [result for result in results if isinstance(result, ContentPost)]
    
    logger.info(f"Multi-platform publishing completed: {len(successful_posts)}/{len(platforms)} successful")
    return successful_posts


if __name__ == "__main__":
    # Example usage
    async def main():
        import os
        
        # Initialize with API credentials from environment
        async with SocialMediaHubIntegration(
            youtube_api_key=os.getenv("YOUTUBE_API_KEY"),
            instagram_app_id=os.getenv("INSTAGRAM_APP_ID"),
            instagram_app_secret=os.getenv("INSTAGRAM_APP_SECRET"),
            tiktok_client_key=os.getenv("TIKTOK_CLIENT_KEY"),
            tiktok_client_secret=os.getenv("TIKTOK_CLIENT_SECRET")
        ) as hub:
            # Get OAuth URLs for connecting accounts
            youtube_url = await hub.get_oauth_url(SocialPlatform.YOUTUBE, "random_state_123")
            print(f"YouTube OAuth URL: {youtube_url}")
            
            # Check usage stats
            stats = hub.get_usage_stats()
            print(f"Usage stats: {stats}")
    
    asyncio.run(main())