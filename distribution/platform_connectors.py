"""Platform Connectors Manager

Advanced API connectors for all major social media and content platforms.
Handles authentication, content publishing, and API rate limiting across
multiple platforms simultaneously.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
try:
    import aiohttp
except ImportError:
    aiohttp = None
import logging
import json
import hashlib
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import mimetypes
from pathlib import Path

logger = logging.getLogger(__name__)


class SocialPlatform(Enum):
    """Supported social media platforms"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    DISCORD = "discord"


class ContentFormat(Enum):
    """Content format types"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    CAROUSEL = "carousel"
    STORY = "story"
    LIVE = "live"
    REEL = "reel"
    SHORT = "short"


class PublicationStatus(Enum):
    """Publication status states"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class PlatformCredentials:
    """Platform authentication credentials"""
    platform: SocialPlatform
    access_token: str
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = None
    webhook_url: Optional[str] = None


@dataclass
class ContentPayload:
    """Content data for publication"""
    title: Optional[str] = None
    description: Optional[str] = None
    media_url: Optional[str] = None
    media_data: Optional[bytes] = None
    media_type: Optional[str] = None
    thumbnail_url: Optional[str] = None
    tags: List[str] = None
    category: Optional[str] = None
    visibility: str = "public"
    schedule_time: Optional[datetime] = None
    location: Optional[Dict[str, Any]] = None
    collaborators: List[str] = None


@dataclass
class PublicationResult:
    """Result of content publication"""
    platform: SocialPlatform
    status: PublicationStatus
    content_id: Optional[str] = None
    platform_url: Optional[str] = None
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    published_at: Optional[datetime] = None
    moderation_status: Optional[str] = None


class PlatformConnectorManager:
    """Manages connections and publishing to all social platforms"""
    
    # Platform-specific API configurations
    PLATFORM_CONFIGS = {
        SocialPlatform.YOUTUBE: {
            "auth_url": "https://accounts.google.com/o/oauth2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "upload_url": "https://www.googleapis.com/upload/youtube/v3/videos",
            "api_base": "https://www.googleapis.com/youtube/v3",
            "scopes": ["https://www.googleapis.com/auth/youtube.upload"],
            "rate_limit": {"requests": 10000, "period": "daily"}
        },
        SocialPlatform.TIKTOK: {
            "auth_url": "https://www.tiktok.com/auth/authorize/",
            "token_url": "https://open-api.tiktok.com/oauth/access_token/",
            "upload_url": "https://open-api.tiktok.com/share/video/upload/",
            "api_base": "https://open-api.tiktok.com/v1",
            "scopes": ["user.info.basic", "video.upload"],
            "rate_limit": {"requests": 1000, "period": "daily"}
        },
        SocialPlatform.INSTAGRAM: {
            "auth_url": "https://api.instagram.com/oauth/authorize",
            "token_url": "https://api.instagram.com/oauth/access_token",
            "upload_url": "https://graph.instagram.com/me/media",
            "api_base": "https://graph.instagram.com",
            "scopes": ["user_profile", "user_media"],
            "rate_limit": {"requests": 200, "period": "hourly"}
        },
        SocialPlatform.TWITTER: {
            "auth_url": "https://twitter.com/i/oauth2/authorize",
            "token_url": "https://api.twitter.com/2/oauth2/token",
            "upload_url": "https://upload.twitter.com/1.1/media/upload.json",
            "api_base": "https://api.twitter.com/2",
            "scopes": ["tweet.read", "tweet.write", "users.read"],
            "rate_limit": {"requests": 300, "period": "15min"}
        },
        SocialPlatform.FACEBOOK: {
            "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
            "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
            "upload_url": "https://graph.facebook.com/me/photos",
            "api_base": "https://graph.facebook.com/v18.0",
            "scopes": ["pages_manage_posts", "pages_read_engagement"],
            "rate_limit": {"requests": 600, "period": "hourly"}
        },
        SocialPlatform.LINKEDIN: {
            "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
            "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
            "upload_url": "https://api.linkedin.com/v2/assets",
            "api_base": "https://api.linkedin.com/v2",
            "scopes": ["w_member_social"],
            "rate_limit": {"requests": 500, "period": "daily"}
        },
        SocialPlatform.SPOTIFY: {
            "auth_url": "https://accounts.spotify.com/authorize",
            "token_url": "https://accounts.spotify.com/api/token",
            "upload_url": "https://api.spotify.com/v1/me/player/queue",
            "api_base": "https://api.spotify.com/v1",
            "scopes": ["playlist-modify-public", "user-modify-playback-state"],
            "rate_limit": {"requests": 100, "period": "hourly"}
        },
        SocialPlatform.SOUNDCLOUD: {
            "auth_url": "https://soundcloud.com/connect",
            "token_url": "https://api.soundcloud.com/oauth2/token",
            "upload_url": "https://api.soundcloud.com/tracks",
            "api_base": "https://api.soundcloud.com",
            "scopes": ["non-expiring"],
            "rate_limit": {"requests": 15000, "period": "hourly"}
        }
    }
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.credentials: Dict[SocialPlatform, PlatformCredentials] = {}
        self.rate_limiters: Dict[SocialPlatform, Dict] = {}
        self.upload_progress_callbacks: Dict[str, callable] = {}
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def authenticate_platform(
        self,
        platform: SocialPlatform,
        auth_code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str = None
    ) -> PlatformCredentials:
        """Authenticate with a specific platform"""
        try:
            config = self.PLATFORM_CONFIGS.get(platform)
            if not config:
                raise ValueError(f"Platform {platform.value} not supported")
            
            # Platform-specific authentication
            if platform == SocialPlatform.YOUTUBE:
                return await self._authenticate_youtube(auth_code, client_id, client_secret, redirect_uri)
            elif platform == SocialPlatform.TIKTOK:
                return await self._authenticate_tiktok(auth_code, client_id, client_secret)
            elif platform == SocialPlatform.INSTAGRAM:
                return await self._authenticate_instagram(auth_code, client_id, client_secret, redirect_uri)
            elif platform == SocialPlatform.TWITTER:
                return await self._authenticate_twitter(auth_code, client_id, client_secret, redirect_uri)
            elif platform == SocialPlatform.FACEBOOK:
                return await self._authenticate_facebook(auth_code, client_id, client_secret, redirect_uri)
            elif platform == SocialPlatform.LINKEDIN:
                return await self._authenticate_linkedin(auth_code, client_id, client_secret, redirect_uri)
            elif platform == SocialPlatform.SPOTIFY:
                return await self._authenticate_spotify(auth_code, client_id, client_secret, redirect_uri)
            elif platform == SocialPlatform.SOUNDCLOUD:
                return await self._authenticate_soundcloud(auth_code, client_id, client_secret, redirect_uri)
            else:
                raise ValueError(f"Authentication not implemented for {platform.value}")
        
        except Exception as e:
            logger.error(f"Authentication failed for {platform.value}: {str(e)}")
            raise
    
    async def publish_content(
        self,
        platforms: List[SocialPlatform],
        content: ContentPayload,
        optimization_settings: Optional[Dict] = None
    ) -> Dict[SocialPlatform, PublicationResult]:
        """Publish content to multiple platforms simultaneously"""
        try:
            results = {}
            tasks = []
            
            for platform in platforms:
                if platform not in self.credentials:
                    results[platform] = PublicationResult(
                        platform=platform,
                        status=PublicationStatus.FAILED,
                        error_message="Platform not authenticated"
                    )
                    continue
                
                # Check rate limits
                if not await self._check_rate_limit(platform):
                    results[platform] = PublicationResult(
                        platform=platform,
                        status=PublicationStatus.FAILED,
                        error_message="Rate limit exceeded"
                    )
                    continue
                
                # Create publication task
                task = self._publish_to_platform(platform, content, optimization_settings)
                tasks.append((platform, task))
            
            # Execute all publications concurrently
            for platform, task in tasks:
                try:
                    result = await task
                    results[platform] = result
                except Exception as e:
                    logger.error(f"Publication failed for {platform.value}: {str(e)}")
                    results[platform] = PublicationResult(
                        platform=platform,
                        status=PublicationStatus.FAILED,
                        error_message=str(e)
                    )
            
            return results
        
        except Exception as e:
            logger.error(f"Multi-platform publication failed: {str(e)}")
            raise
    
    async def _publish_to_platform(
        self,
        platform: SocialPlatform,
        content: ContentPayload,
        optimization_settings: Optional[Dict] = None
    ) -> PublicationResult:
        """Publish content to a specific platform"""
        try:
            credentials = self.credentials[platform]
            
            # Platform-specific publishing logic
            if platform == SocialPlatform.YOUTUBE:
                return await self._publish_youtube(credentials, content, optimization_settings)
            elif platform == SocialPlatform.TIKTOK:
                return await self._publish_tiktok(credentials, content, optimization_settings)
            elif platform == SocialPlatform.INSTAGRAM:
                return await self._publish_instagram(credentials, content, optimization_settings)
            elif platform == SocialPlatform.TWITTER:
                return await self._publish_twitter(credentials, content, optimization_settings)
            elif platform == SocialPlatform.FACEBOOK:
                return await self._publish_facebook(credentials, content, optimization_settings)
            elif platform == SocialPlatform.LINKEDIN:
                return await self._publish_linkedin(credentials, content, optimization_settings)
            elif platform == SocialPlatform.SPOTIFY:
                return await self._publish_spotify(credentials, content, optimization_settings)
            elif platform == SocialPlatform.SOUNDCLOUD:
                return await self._publish_soundcloud(credentials, content, optimization_settings)
            else:
                raise ValueError(f"Publishing not implemented for {platform.value}")
        
        except Exception as e:
            logger.error(f"Platform publication failed for {platform.value}: {str(e)}")
            return PublicationResult(
                platform=platform,
                status=PublicationStatus.FAILED,
                error_message=str(e)
            )
    
    async def _authenticate_youtube(
        self,
        auth_code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ) -> PlatformCredentials:
        """Authenticate with YouTube API"""
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri or "urn:ietf:wg:oauth:2.0:oob"
        }
        
        async with self.session.post(token_url, data=data) as response:
            if response.status == 200:
                token_data = await response.json()
                
                credentials = PlatformCredentials(
                    platform=SocialPlatform.YOUTUBE,
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    client_id=client_id,
                    client_secret=client_secret,
                    expires_at=datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600)),
                    scopes=self.PLATFORM_CONFIGS[SocialPlatform.YOUTUBE]["scopes"]
                )
                
                self.credentials[SocialPlatform.YOUTUBE] = credentials
                return credentials
            else:
                error_text = await response.text()
                raise Exception(f"YouTube authentication failed: {response.status} - {error_text}")
    
    async def _publish_youtube(
        self,
        credentials: PlatformCredentials,
        content: ContentPayload,
        optimization_settings: Optional[Dict] = None
    ) -> PublicationResult:
        """Publish video content to YouTube"""
        try:
            # Refresh token if needed
            if credentials.expires_at and datetime.now() >= credentials.expires_at:
                await self._refresh_token(credentials)
            
            # Prepare video metadata
            snippet = {
                "title": content.title or "Untitled Video",
                "description": content.description or "",
                "tags": content.tags or [],
                "categoryId": "22",  # People & Blogs
                "defaultLanguage": "en",
                "defaultAudioLanguage": "en"
            }
            
            if optimization_settings and "category" in optimization_settings:
                snippet["categoryId"] = optimization_settings["category"]
            
            status = {
                "privacyStatus": content.visibility,
                "embeddable": True,
                "license": "youtube",
                "publicStatsViewable": True
            }
            
            # Schedule if specified
            if content.schedule_time:
                status["privacyStatus"] = "private"
                status["publishAt"] = content.schedule_time.isoformat() + "Z"
            
            metadata = {
                "snippet": snippet,
                "status": status
            }
            
            # Upload video
            upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"
            params = {
                "part": "snippet,status",
                "uploadType": "multipart"
            }
            
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Accept": "application/json"
            }
            
            # Create multipart upload
            boundary = f"----formdata{hash(content.media_url or 'default')}"
            
            # Metadata part
            metadata_part = (
                f"--{boundary}\r\n"
                f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
                f"{json.dumps(metadata)}\r\n"
            ).encode()
            
            # Video data part
            if content.media_data:
                video_data = content.media_data
            elif content.media_url:
                # Download video data
                async with self.session.get(content.media_url) as resp:
                    video_data = await resp.read()
            else:
                raise ValueError("No media data provided")
            
            video_part = (
                f"--{boundary}\r\n"
                f"Content-Type: {content.media_type or 'video/mp4'}\r\n\r\n"
            ).encode() + video_data + f"\r\n--{boundary}--\r\n".encode()
            
            upload_data = metadata_part + video_part
            
            headers["Content-Type"] = f"multipart/related; boundary={boundary}"
            headers["Content-Length"] = str(len(upload_data))
            
            async with self.session.post(
                upload_url,
                params=params,
                headers=headers,
                data=upload_data
            ) as response:
                if response.status == 200:
                    result_data = await response.json()
                    
                    return PublicationResult(
                        platform=SocialPlatform.YOUTUBE,
                        status=PublicationStatus.PUBLISHED,
                        content_id=result_data["id"],
                        platform_url=f"https://www.youtube.com/watch?v={result_data['id']}",
                        published_at=datetime.now(),
                        metrics={"views": 0, "likes": 0, "comments": 0}
                    )
                else:
                    error_text = await response.text()
                    return PublicationResult(
                        platform=SocialPlatform.YOUTUBE,
                        status=PublicationStatus.FAILED,
                        error_message=f"Upload failed: {response.status} - {error_text}"
                    )
        
        except Exception as e:
            logger.error(f"YouTube publication failed: {str(e)}")
            return PublicationResult(
                platform=SocialPlatform.YOUTUBE,
                status=PublicationStatus.FAILED,
                error_message=str(e)
            )
    
    async def _check_rate_limit(self, platform: SocialPlatform) -> bool:
        """Check if platform rate limit allows request"""
        try:
            config = self.PLATFORM_CONFIGS.get(platform, {})
            rate_limit = config.get("rate_limit", {})
            
            if not rate_limit:
                return True  # No rate limit configured
            
            current_time = datetime.now()
            platform_key = platform.value
            
            if platform_key not in self.rate_limiters:
                self.rate_limiters[platform_key] = {
                    "requests": 0,
                    "reset_time": current_time + self._get_period_delta(rate_limit["period"])
                }
            
            limiter = self.rate_limiters[platform_key]
            
            # Reset if period expired
            if current_time >= limiter["reset_time"]:
                limiter["requests"] = 0
                limiter["reset_time"] = current_time + self._get_period_delta(rate_limit["period"])
            
            # Check limit
            if limiter["requests"] >= rate_limit["requests"]:
                return False
            
            limiter["requests"] += 1
            return True
        
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return True  # Allow by default on error
    
    def _get_period_delta(self, period: str) -> timedelta:
        """Convert period string to timedelta"""
        if period == "daily":
            return timedelta(days=1)
        elif period == "hourly":
            return timedelta(hours=1)
        elif period == "15min":
            return timedelta(minutes=15)
        else:
            return timedelta(hours=1)  # Default
    
    async def _refresh_token(self, credentials: PlatformCredentials):
        """Refresh access token for platform"""
        try:
            if not credentials.refresh_token:
                logger.warning(f"No refresh token for {credentials.platform.value}")
                return
            
            config = self.PLATFORM_CONFIGS[credentials.platform]
            token_url = config["token_url"]
            
            data = {
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "refresh_token": credentials.refresh_token,
                "grant_type": "refresh_token"
            }
            
            async with self.session.post(token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    credentials.access_token = token_data["access_token"]
                    credentials.expires_at = datetime.now() + timedelta(
                        seconds=token_data.get("expires_in", 3600)
                    )
                    logger.info(f"Token refreshed for {credentials.platform.value}")
                else:
                    logger.error(f"Token refresh failed for {credentials.platform.value}")
        
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
    
    # Placeholder methods for other platforms - would be implemented similarly
    async def _authenticate_tiktok(self, auth_code: str, client_id: str, client_secret: str) -> PlatformCredentials:
        """TikTok authentication implementation"""
        # Implementation would follow TikTok API documentation
        pass
    
    async def _authenticate_instagram(self, auth_code: str, client_id: str, client_secret: str, redirect_uri: str) -> PlatformCredentials:
        """Instagram authentication implementation"""
        # Implementation would follow Instagram API documentation
        pass
    
    async def _authenticate_twitter(self, auth_code: str, client_id: str, client_secret: str, redirect_uri: str) -> PlatformCredentials:
        """Twitter authentication implementation"""
        # Implementation would follow Twitter API v2 documentation
        pass
    
    async def _authenticate_facebook(self, auth_code: str, client_id: str, client_secret: str, redirect_uri: str) -> PlatformCredentials:
        """Facebook authentication implementation"""
        # Implementation would follow Facebook Graph API documentation
        pass
    
    async def _authenticate_linkedin(self, auth_code: str, client_id: str, client_secret: str, redirect_uri: str) -> PlatformCredentials:
        """LinkedIn authentication implementation"""
        # Implementation would follow LinkedIn API documentation
        pass
    
    async def _authenticate_spotify(self, auth_code: str, client_id: str, client_secret: str, redirect_uri: str) -> PlatformCredentials:
        """Spotify authentication implementation"""
        # Implementation would follow Spotify Web API documentation
        pass
    
    async def _authenticate_soundcloud(self, auth_code: str, client_id: str, client_secret: str, redirect_uri: str) -> PlatformCredentials:
        """SoundCloud authentication implementation"""
        # Implementation would follow SoundCloud API documentation
        pass
    
    # Publishing method placeholders for other platforms
    async def _publish_tiktok(self, credentials: PlatformCredentials, content: ContentPayload, optimization_settings: Optional[Dict] = None) -> PublicationResult:
        """TikTok publishing implementation"""
        pass
    
    async def _publish_instagram(self, credentials: PlatformCredentials, content: ContentPayload, optimization_settings: Optional[Dict] = None) -> PublicationResult:
        """Instagram publishing implementation"""
        pass
    
    async def _publish_twitter(self, credentials: PlatformCredentials, content: ContentPayload, optimization_settings: Optional[Dict] = None) -> PublicationResult:
        """Twitter publishing implementation"""
        pass
    
    async def _publish_facebook(self, credentials: PlatformCredentials, content: ContentPayload, optimization_settings: Optional[Dict] = None) -> PublicationResult:
        """Facebook publishing implementation"""
        pass
    
    async def _publish_linkedin(self, credentials: PlatformCredentials, content: ContentPayload, optimization_settings: Optional[Dict] = None) -> PublicationResult:
        """LinkedIn publishing implementation"""
        pass
    
    async def _publish_spotify(self, credentials: PlatformCredentials, content: ContentPayload, optimization_settings: Optional[Dict] = None) -> PublicationResult:
        """Spotify publishing implementation"""
        pass
    
    async def _publish_soundcloud(self, credentials: PlatformCredentials, content: ContentPayload, optimization_settings: Optional[Dict] = None) -> PublicationResult:
        """SoundCloud publishing implementation"""
        pass
    
    async def get_platform_status(self, platform: SocialPlatform) -> Dict[str, Any]:
        """Get platform connection and status information"""
        try:
            credentials = self.credentials.get(platform)
            if not credentials:
                return {"connected": False, "error": "Not authenticated"}
            
            # Check token validity
            if credentials.expires_at and datetime.now() >= credentials.expires_at:
                if credentials.refresh_token:
                    await self._refresh_token(credentials)
                else:
                    return {"connected": False, "error": "Token expired"}
            
            # Check rate limits
            rate_limit_status = await self._check_rate_limit(platform)
            
            return {
                "connected": True,
                "platform": platform.value,
                "expires_at": credentials.expires_at.isoformat() if credentials.expires_at else None,
                "scopes": credentials.scopes,
                "rate_limit_available": rate_limit_status
            }
        
        except Exception as e:
            logger.error(f"Platform status check failed: {str(e)}")
            return {"connected": False, "error": str(e)}
    
    def disconnect_platform(self, platform: SocialPlatform):
        """Disconnect from a platform"""
        if platform in self.credentials:
            del self.credentials[platform]
        if platform.value in self.rate_limiters:
            del self.rate_limiters[platform.value]
        logger.info(f"Disconnected from {platform.value}")