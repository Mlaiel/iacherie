"""
Snapchat Snap Kit API Integration
=================================

Complete Snapchat Snap Kit integration for story monitoring, user management, and analytics.
Handles Snap Kit Login, Story Kit, and Bitmoji Kit functionalities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urlencode
import base64
import hashlib
import hmac

from .platform_oauth_manager import OAuthTokens
from .api_rate_limiter import APIRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class SnapchatUser:
    """Snapchat user information"""
    user_id: str
    username: str
    display_name: str
    email: str = None
    phone_number: str = None
    birthday: str = None
    country: str = None
    language: str = None
    bitmoji_avatar_url: str = None
    profile_link: str = None
    is_verified: bool = False


@dataclass
class SnapchatStory:
    """Snapchat story information"""
    story_id: str
    user_id: str
    title: str
    description: str
    media_url: str
    media_type: str  # "image", "video"
    created_at: datetime
    expires_at: datetime
    view_count: int = 0
    screenshot_count: int = 0
    is_public: bool = True
    location: Dict[str, Any] = None
    stickers: List[Dict[str, Any]] = None


@dataclass
class SnapchatMedia:
    """Snapchat media content"""
    media_id: str
    media_type: str  # "photo", "video"
    media_url: str
    thumbnail_url: str = None
    duration: float = 0.0  # For videos
    width: int = 0
    height: int = 0
    created_at: datetime = None
    download_link: str = None


@dataclass
class SnapchatAnalytics:
    """Snapchat analytics data"""
    user_id: str
    date_range: Dict[str, str]
    total_stories: int = 0
    total_views: int = 0
    total_screenshots: int = 0
    unique_viewers: int = 0
    story_completion_rate: float = 0.0
    engagement_rate: float = 0.0
    top_performing_stories: List[Dict[str, Any]] = None
    audience_demographics: Dict[str, Any] = None


@dataclass
class BitmojiAvatar:
    """Bitmoji avatar information"""
    avatar_id: str
    user_id: str
    avatar_url: str
    template_id: str = None
    selfie_url: str = None
    is_friendmoji: bool = False
    friend_id: str = None


class SnapchatSnapKitAPI:
    """Snapchat Snap Kit API integration"""
    
    def __init__(self, rate_limiter: Optional[APIRateLimiter] = None):
        self.session = None
        self.rate_limiter = rate_limiter or APIRateLimiter()
        self.base_url = "https://adsapi.snapchat.com/v1"
        self.kit_base_url = "https://kit.snapchat.com/v1"
        self.login_base_url = "https://accounts.snapchat.com/login/oauth2"
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.rate_limiter.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        await self.rate_limiter.__aexit__(exc_type, exc_val, exc_tb)
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        tokens: OAuthTokens,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting"""
        
        # Check rate limit
        rate_status = await self.rate_limiter.check_rate_limit("snapchat", endpoint)
        if rate_status.is_limited:
            wait_time = await self.rate_limiter.get_wait_time("snapchat", endpoint)
            if wait_time > 0:
                logger.info(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        url = f"{base_url or self.kit_base_url}/{endpoint}"
        
        # Default headers
        request_headers = {
            "Authorization": f"{tokens.token_type} {tokens.access_token}",
            "Accept": "application/json",
            "User-Agent": "Ainflue/1.0"
        }
        
        if headers:
            request_headers.update(headers)
            
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=request_headers) as response:
                    await self.rate_limiter.record_request("snapchat", endpoint, None, response.status)
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        raise Exception("Rate limit exceeded")
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() == "POST":
                request_headers["Content-Type"] = "application/json"
                async with self.session.post(url, json=data, headers=request_headers, params=params) as response:
                    await self.rate_limiter.record_request("snapchat", endpoint, None, response.status)
                    
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() in ["PUT", "PATCH", "DELETE"]:
                if data:
                    request_headers["Content-Type"] = "application/json"
                    
                async with self.session.request(
                    method, url, json=data, headers=request_headers, params=params
                ) as response:
                    await self.rate_limiter.record_request("snapchat", endpoint, None, response.status)
                    
                    if response.status in [200, 204]:
                        if response.content_length and response.content_length > 0:
                            return await response.json()
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Snapchat API request failed: {e}")
            raise
            
    async def get_user_info(self, tokens: OAuthTokens) -> SnapchatUser:
        """Get current user information using Login Kit"""
        
        response = await self._make_request("GET", "me", tokens)
        
        data = response.get("data", {})
        
        user = SnapchatUser(
            user_id=data.get("me", {}).get("id", ""),
            username=data.get("me", {}).get("username", ""),
            display_name=data.get("me", {}).get("display_name", ""),
            email=data.get("me", {}).get("email", ""),
            birthday=data.get("me", {}).get("birthday", ""),
            country=data.get("me", {}).get("country", ""),
            language=data.get("me", {}).get("language", ""),
            bitmoji_avatar_url=data.get("me", {}).get("bitmoji", {}).get("avatar", "")
        )
        
        return user
        
    async def get_user_bitmoji(self, tokens: OAuthTokens) -> BitmojiAvatar:
        """Get user's Bitmoji information using Bitmoji Kit"""
        
        response = await self._make_request("GET", "bitmoji/me", tokens)
        
        data = response.get("data", {})
        bitmoji_data = data.get("me", {}).get("bitmoji", {})
        
        avatar = BitmojiAvatar(
            avatar_id=bitmoji_data.get("id", ""),
            user_id=data.get("me", {}).get("id", ""),
            avatar_url=bitmoji_data.get("avatar", ""),
            template_id=bitmoji_data.get("template_id"),
            selfie_url=bitmoji_data.get("selfie")
        )
        
        return avatar
        
    async def get_bitmoji_stickers(
        self,
        tokens: OAuthTokens,
        template_id: Optional[str] = None,
        friend_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get Bitmoji stickers for templates"""
        
        params = {}
        if template_id:
            params["template_id"] = template_id
        if friend_id:
            params["friend_id"] = friend_id
            
        endpoint = "bitmoji/stickers"
        if friend_id:
            endpoint = "bitmoji/friendmoji"
            
        response = await self._make_request("GET", endpoint, tokens, params=params)
        
        return response.get("data", {}).get("stickers", [])
        
    async def create_story_sharing_url(
        self,
        tokens: OAuthTokens,
        media_url: str,
        caption: Optional[str] = None,
        attachment_url: Optional[str] = None,
        sticker_url: Optional[str] = None
    ) -> str:
        """Create a Story Kit sharing URL"""
        
        # Story Kit uses URL scheme for sharing
        base_url = "https://www.snapchat.com/add/"
        
        params = {
            "media": media_url
        }
        
        if caption:
            params["caption"] = caption
        if attachment_url:
            params["attachment_url"] = attachment_url
        if sticker_url:
            params["sticker_url"] = sticker_url
            
        query_string = urlencode(params)
        sharing_url = f"{base_url}?{query_string}"
        
        logger.info(f"Created Snapchat story sharing URL: {sharing_url}")
        return sharing_url
        
    async def get_media_insights(
        self,
        tokens: OAuthTokens,
        media_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get insights for shared media (limited API access)"""
        
        # Note: Snapchat has very limited analytics API access
        # Most analytics would require Snapchat Ads API or business account
        
        params = {
            "media_id": media_id,
            "start_time": start_date.isoformat(),
            "end_time": end_date.isoformat()
        }
        
        try:
            response = await self._make_request("GET", "insights/media", tokens, params=params)
            return response.get("data", {})
        except Exception as e:
            logger.warning(f"Could not get media insights for {media_id}: {e}")
            return {}
            
    async def get_friends_list(self, tokens: OAuthTokens) -> List[Dict[str, Any]]:
        """Get user's friends list (limited access)"""
        
        try:
            response = await self._make_request("GET", "friends", tokens)
            return response.get("data", {}).get("friends", [])
        except Exception as e:
            logger.warning(f"Could not get friends list: {e}")
            return []
            
    async def send_friend_request(self, tokens: OAuthTokens, username: str) -> bool:
        """Send a friend request"""
        
        data = {"username": username}
        
        try:
            await self._make_request("POST", "friends/add", tokens, data=data)
            logger.info(f"Sent friend request to {username}")
            return True
        except Exception as e:
            logger.error(f"Failed to send friend request to {username}: {e}")
            return False
            
    async def get_user_stories(
        self,
        tokens: OAuthTokens,
        user_id: Optional[str] = None
    ) -> List[SnapchatStory]:
        """Get user's stories (very limited access)"""
        
        params = {}
        if user_id:
            params["user_id"] = user_id
            
        try:
            response = await self._make_request("GET", "stories", tokens, params=params)
            
            stories = []
            for item in response.get("data", {}).get("stories", []):
                story = SnapchatStory(
                    story_id=item.get("id", ""),
                    user_id=item.get("user_id", ""),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    media_url=item.get("media_url", ""),
                    media_type=item.get("media_type", "image"),
                    created_at=datetime.fromisoformat(item.get("created_at", datetime.now().isoformat())),
                    expires_at=datetime.fromisoformat(item.get("expires_at", (datetime.now() + timedelta(hours=24)).isoformat())),
                    view_count=item.get("view_count", 0),
                    is_public=item.get("is_public", True)
                )
                stories.append(story)
                
            return stories
            
        except Exception as e:
            logger.warning(f"Could not get user stories: {e}")
            return []
            
    async def share_to_story(
        self,
        tokens: OAuthTokens,
        media_url: str,
        caption: Optional[str] = None,
        stickers: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Share content to user's story using Story Kit"""
        
        # This would typically redirect to Snapchat app
        # or use deep linking for mobile apps
        
        story_data = {
            "media_url": media_url,
            "caption": caption or "",
            "stickers": stickers or []
        }
        
        try:
            response = await self._make_request("POST", "stories/share", tokens, data=story_data)
            story_id = response.get("data", {}).get("story_id", "")
            logger.info(f"Shared to Snapchat story: {story_id}")
            return story_id
        except Exception as e:
            logger.error(f"Failed to share to story: {e}")
            return ""
            
    async def get_analytics(
        self,
        tokens: OAuthTokens,
        start_date: datetime,
        end_date: datetime,
        metrics: Optional[List[str]] = None
    ) -> SnapchatAnalytics:
        """Get analytics data (limited access)"""
        
        default_metrics = ["views", "screenshots", "completion_rate"]
        metrics = metrics or default_metrics
        
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "metrics": ",".join(metrics)
        }
        
        try:
            response = await self._make_request("GET", "analytics", tokens, params=params)
            
            analytics_data = response.get("data", {})
            
            analytics = SnapchatAnalytics(
                user_id=analytics_data.get("user_id", ""),
                date_range={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                },
                total_views=analytics_data.get("total_views", 0),
                total_screenshots=analytics_data.get("total_screenshots", 0),
                unique_viewers=analytics_data.get("unique_viewers", 0),
                story_completion_rate=analytics_data.get("completion_rate", 0.0),
                engagement_rate=analytics_data.get("engagement_rate", 0.0)
            )
            
            return analytics
            
        except Exception as e:
            logger.warning(f"Could not get analytics: {e}")
            return SnapchatAnalytics(
                user_id="",
                date_range={
                    "start": start_date.strftime("%Y-%m-%d"),
                    "end": end_date.strftime("%Y-%m-%d")
                }
            )
            
    async def upload_media(
        self,
        tokens: OAuthTokens,
        media_file_path: str,
        media_type: str = "image"
    ) -> SnapchatMedia:
        """Upload media for stories (limited functionality)"""
        
        # Note: Direct media upload is very limited in Snapchat Kit
        # Most sharing is done through URL schemes or deep links
        
        if not os.path.exists(media_file_path):
            raise FileNotFoundError(f"Media file not found: {media_file_path}")
            
        # Read media file
        with open(media_file_path, "rb") as media_file:
            media_content = media_file.read()
            
        # Encode media for upload
        media_b64 = base64.b64encode(media_content).decode()
        
        upload_data = {
            "media_type": media_type,
            "media_data": media_b64,
            "filename": os.path.basename(media_file_path)
        }
        
        try:
            response = await self._make_request("POST", "media/upload", tokens, data=upload_data)
            
            media_data = response.get("data", {})
            
            media = SnapchatMedia(
                media_id=media_data.get("media_id", ""),
                media_type=media_type,
                media_url=media_data.get("media_url", ""),
                thumbnail_url=media_data.get("thumbnail_url", ""),
                created_at=datetime.now()
            )
            
            logger.info(f"Uploaded Snapchat media: {media.media_id}")
            return media
            
        except Exception as e:
            logger.error(f"Failed to upload media: {e}")
            # Return placeholder media object
            return SnapchatMedia(
                media_id="",
                media_type=media_type,
                media_url="",
                created_at=datetime.now()
            )
            
    async def create_lens_sharing_url(
        self,
        lens_id: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a Lens sharing URL"""
        
        base_url = f"https://www.snapchat.com/unlock/?type=SNAPCODE&uuid={lens_id}"
        
        if parameters:
            query_string = urlencode(parameters)
            base_url += f"&{query_string}"
            
        logger.info(f"Created Snapchat lens sharing URL: {base_url}")
        return base_url
        
    async def get_lens_views(
        self,
        tokens: OAuthTokens,
        lens_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get lens view analytics (limited access)"""
        
        params = {
            "lens_id": lens_id,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        try:
            response = await self._make_request("GET", "lenses/analytics", tokens, params=params)
            return response.get("data", {})
        except Exception as e:
            logger.warning(f"Could not get lens analytics for {lens_id}: {e}")
            return {}
            
    def generate_login_url(
        self,
        client_id: str,
        redirect_uri: str,
        scope: List[str] = None,
        state: str = None
    ) -> str:
        """Generate Snapchat Login Kit authorization URL"""
        
        default_scope = ["user.external_id", "user.display_name", "user.bitmoji.avatar"]
        scope = scope or default_scope
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scope)
        }
        
        if state:
            params["state"] = state
            
        query_string = urlencode(params)
        login_url = f"{self.login_base_url}/authorize?{query_string}"
        
        logger.info(f"Generated Snapchat login URL: {login_url}")
        return login_url