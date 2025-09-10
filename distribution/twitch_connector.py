"""
Twitch Platform Connector
=========================

Enterprise-grade Twitch API connector for Ainflue Distribution Platform.
Supports Twitch streaming, clips, VODs, chat integration, and channel management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import aiohttp
import json
import urllib.parse
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

class TwitchStreamType(Enum):
    """Twitch stream types"""
    LIVE = "live"
    PLAYLIST = "playlist"
    WATCH_PARTY = "watch_party"
    PREMIERE = "premiere"
    RERUN = "rerun"

class TwitchContentType(Enum):
    """Twitch content types"""
    STREAM = "stream"
    CLIP = "clip"
    VIDEO = "video"
    HIGHLIGHT = "highlight"
    UPLOAD = "upload"
    ARCHIVE = "archive"

class TwitchChatBadge(Enum):
    """Twitch chat badges"""
    BROADCASTER = "broadcaster"
    MODERATOR = "moderator"
    VIP = "vip"
    SUBSCRIBER = "subscriber"
    FOLLOWER = "follower"
    TURBO = "turbo"
    PRIME = "prime"
    PARTNER = "partner"

@dataclass
class TwitchCredentials:
    """Twitch API credentials"""
    client_id: str
    client_secret: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    redirect_uri: Optional[str] = None
    scopes: List[str] = field(default_factory=lambda: [
        "channel:read:stream_key",
        "channel:manage:broadcast",
        "channel:manage:videos", 
        "clips:edit",
        "user:read:email",
        "chat:read",
        "chat:edit"
    ])

@dataclass
class TwitchStream:
    """Twitch stream information"""
    id: str
    user_id: str
    user_login: str
    user_name: str
    game_id: str
    game_name: str
    type: TwitchStreamType
    title: str
    viewer_count: int
    started_at: datetime
    language: str
    thumbnail_url: str
    tag_ids: List[str] = field(default_factory=list)
    is_mature: bool = False

@dataclass
class TwitchClip:
    """Twitch clip information"""
    id: str
    url: str
    embed_url: str
    broadcaster_id: str
    broadcaster_name: str
    creator_id: str
    creator_name: str
    video_id: str
    game_id: str
    language: str
    title: str
    view_count: int
    created_at: datetime
    thumbnail_url: str
    duration: float
    vod_offset: Optional[int] = None

@dataclass
class TwitchVideo:
    """Twitch video/VOD information"""
    id: str
    stream_id: Optional[str]
    user_id: str
    user_login: str
    user_name: str
    title: str
    description: str
    created_at: datetime
    published_at: datetime
    url: str
    thumbnail_url: str
    viewable: str
    view_count: int
    language: str
    type: str
    duration: str
    muted_segments: List[Dict[str, int]] = field(default_factory=list)

@dataclass
class TwitchPublishResult:
    """Result of Twitch publish operation"""
    success: bool
    content_id: Optional[str] = None
    content_url: Optional[str] = None
    content_type: Optional[TwitchContentType] = None
    status: str = "published"
    message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class TwitchConnector:
    """Twitch platform connector with streaming and content management"""
    
    BASE_URL = "https://api.twitch.tv/helix"
    AUTH_URL = "https://id.twitch.tv/oauth2"
    CHAT_URL = "wss://irc-ws.chat.twitch.tv:443"
    
    def __init__(self, credentials: TwitchCredentials):
        """Initialize Twitch connector"""
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.user_info: Optional[Dict[str, Any]] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        if not self.credentials.access_token:
            await self._authenticate()
        else:
            await self._validate_token()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _authenticate(self):
        """Authenticate with Twitch API using OAuth2"""
        try:
            # App Access Token for public API access
            auth_data = {
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "grant_type": "client_credentials"
            }
            
            async with self.session.post(
                f"{self.AUTH_URL}/token",
                data=auth_data
            ) as response:
                response.raise_for_status()
                token_data = await response.json()
                
                self.credentials.access_token = token_data["access_token"]
                logger.info("Twitch app access token obtained")
                
        except Exception as e:
            logger.error(f"Twitch authentication failed: {e}")
            raise
    
    async def _validate_token(self):
        """Validate current access token"""
        try:
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Client-Id": self.credentials.client_id
            }
            
            async with self.session.get(
                f"{self.AUTH_URL}/validate",
                headers=headers
            ) as response:
                if response.status == 401:
                    # Token expired, get new one
                    await self._authenticate()
                else:
                    response.raise_for_status()
                    token_info = await response.json()
                    logger.info(f"Twitch token valid, expires in {token_info.get('expires_in')} seconds")
                    
        except Exception as e:
            logger.error(f"Twitch token validation failed: {e}")
            await self._authenticate()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Twitch API"""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        request_headers = {
            "Authorization": f"Bearer {self.credentials.access_token}",
            "Client-Id": self.credentials.client_id,
            "Content-Type": "application/json"
        }
        
        if headers:
            request_headers.update(headers)
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                json=data,
                params=params
            ) as response:
                
                if response.status == 401:
                    # Token might be expired, refresh and retry
                    await self._authenticate()
                    request_headers["Authorization"] = f"Bearer {self.credentials.access_token}"
                    
                    async with self.session.request(
                        method=method,
                        url=url,
                        headers=request_headers,
                        json=data,
                        params=params
                    ) as retry_response:
                        retry_response.raise_for_status()
                        return await retry_response.json()
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"Twitch API request failed: {e}")
            raise
    
    async def get_user_info(self, user_login: Optional[str] = None) -> Dict[str, Any]:
        """Get user information"""
        params = {}
        if user_login:
            params["login"] = user_login
        
        response = await self._make_request("GET", "/users", params=params)
        
        if response.get("data"):
            self.user_info = response["data"][0]
            return self.user_info
        
        return {}
    
    async def get_stream_info(self, user_login: str) -> Optional[TwitchStream]:
        """Get current stream information"""
        params = {"user_login": user_login}
        response = await self._make_request("GET", "/streams", params=params)
        
        if response.get("data") and len(response["data"]) > 0:
            stream_data = response["data"][0]
            return TwitchStream(
                id=stream_data["id"],
                user_id=stream_data["user_id"],
                user_login=stream_data["user_login"],
                user_name=stream_data["user_name"],
                game_id=stream_data["game_id"],
                game_name=stream_data["game_name"],
                type=TwitchStreamType(stream_data["type"]),
                title=stream_data["title"],
                viewer_count=stream_data["viewer_count"],
                started_at=datetime.fromisoformat(stream_data["started_at"].replace("Z", "+00:00")),
                language=stream_data["language"],
                thumbnail_url=stream_data["thumbnail_url"],
                tag_ids=stream_data.get("tag_ids", []),
                is_mature=stream_data.get("is_mature", False)
            )
        
        return None
    
    async def update_stream_info(
        self, 
        broadcaster_id: str,
        title: Optional[str] = None,
        game_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> bool:
        """Update stream information"""
        try:
            data = {}
            if title:
                data["title"] = title
            if game_id:
                data["game_id"] = game_id
            if language:
                data["language"] = language
            
            params = {"broadcaster_id": broadcaster_id}
            
            await self._make_request("PATCH", "/channels", data=data, params=params)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update stream info: {e}")
            return False
    
    async def create_clip(
        self, 
        broadcaster_id: str,
        has_delay: bool = False
    ) -> TwitchPublishResult:
        """Create a clip from current live stream"""
        try:
            params = {
                "broadcaster_id": broadcaster_id,
                "has_delay": has_delay
            }
            
            response = await self._make_request("POST", "/clips", params=params)
            
            if response.get("data"):
                clip_data = response["data"][0]
                return TwitchPublishResult(
                    success=True,
                    content_id=clip_data["id"],
                    content_url=clip_data["edit_url"],
                    content_type=TwitchContentType.CLIP,
                    message="Clip created successfully",
                    metadata=clip_data
                )
            else:
                return TwitchPublishResult(
                    success=False,
                    message="Failed to create clip"
                )
                
        except Exception as e:
            logger.error(f"Failed to create clip: {e}")
            return TwitchPublishResult(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    async def get_clips(
        self, 
        broadcaster_id: str,
        game_id: Optional[str] = None,
        started_at: Optional[datetime] = None,
        ended_at: Optional[datetime] = None,
        first: int = 20
    ) -> List[TwitchClip]:
        """Get clips for a broadcaster"""
        params = {
            "broadcaster_id": broadcaster_id,
            "first": first
        }
        
        if game_id:
            params["game_id"] = game_id
        if started_at:
            params["started_at"] = started_at.isoformat()
        if ended_at:
            params["ended_at"] = ended_at.isoformat()
        
        response = await self._make_request("GET", "/clips", params=params)
        
        clips = []
        for clip_data in response.get("data", []):
            clips.append(TwitchClip(
                id=clip_data["id"],
                url=clip_data["url"],
                embed_url=clip_data["embed_url"],
                broadcaster_id=clip_data["broadcaster_id"],
                broadcaster_name=clip_data["broadcaster_name"],
                creator_id=clip_data["creator_id"],
                creator_name=clip_data["creator_name"],
                video_id=clip_data["video_id"],
                game_id=clip_data["game_id"],
                language=clip_data["language"],
                title=clip_data["title"],
                view_count=clip_data["view_count"],
                created_at=datetime.fromisoformat(clip_data["created_at"].replace("Z", "+00:00")),
                thumbnail_url=clip_data["thumbnail_url"],
                duration=clip_data["duration"],
                vod_offset=clip_data.get("vod_offset")
            ))
        
        return clips
    
    async def get_videos(
        self, 
        user_id: str,
        video_type: str = "all",  # "all", "upload", "archive", "highlight"
        period: str = "all",  # "all", "day", "month", "week"
        first: int = 20
    ) -> List[TwitchVideo]:
        """Get videos (VODs) for a user"""
        params = {
            "user_id": user_id,
            "type": video_type,
            "period": period,
            "first": first
        }
        
        response = await self._make_request("GET", "/videos", params=params)
        
        videos = []
        for video_data in response.get("data", []):
            videos.append(TwitchVideo(
                id=video_data["id"],
                stream_id=video_data.get("stream_id"),
                user_id=video_data["user_id"],
                user_login=video_data["user_login"],
                user_name=video_data["user_name"],
                title=video_data["title"],
                description=video_data["description"],
                created_at=datetime.fromisoformat(video_data["created_at"].replace("Z", "+00:00")),
                published_at=datetime.fromisoformat(video_data["published_at"].replace("Z", "+00:00")),
                url=video_data["url"],
                thumbnail_url=video_data["thumbnail_url"],
                viewable=video_data["viewable"],
                view_count=video_data["view_count"],
                language=video_data["language"],
                type=video_data["type"],
                duration=video_data["duration"],
                muted_segments=video_data.get("muted_segments", [])
            ))
        
        return videos
    
    async def delete_video(self, video_id: str) -> bool:
        """Delete a video"""
        try:
            params = {"id": video_id}
            await self._make_request("DELETE", "/videos", params=params)
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete video: {e}")
            return False
    
    async def get_game_info(self, game_name: str) -> Optional[Dict[str, Any]]:
        """Get game information by name"""
        params = {"name": game_name}
        response = await self._make_request("GET", "/games", params=params)
        
        if response.get("data") and len(response["data"]) > 0:
            return response["data"][0]
        
        return None
    
    async def get_top_games(self, first: int = 20) -> List[Dict[str, Any]]:
        """Get top games on Twitch"""
        params = {"first": first}
        response = await self._make_request("GET", "/games/top", params=params)
        
        return response.get("data", [])
    
    async def get_followers(
        self, 
        broadcaster_id: str,
        first: int = 20
    ) -> Dict[str, Any]:
        """Get followers for a broadcaster"""
        params = {
            "broadcaster_id": broadcaster_id,
            "first": first
        }
        
        return await self._make_request("GET", "/channels/followers", params=params)
    
    async def get_channel_analytics(
        self, 
        broadcaster_id: str,
        started_at: datetime,
        ended_at: datetime
    ) -> Dict[str, Any]:
        """Get channel analytics (requires appropriate scope)"""
        try:
            # Get stream analytics
            stream_params = {
                "user_id": broadcaster_id,
                "started_at": started_at.isoformat(),
                "ended_at": ended_at.isoformat()
            }
            streams = await self._make_request("GET", "/streams", params=stream_params)
            
            # Get videos analytics
            videos = await self.get_videos(broadcaster_id, first=100)
            
            # Get clips analytics
            clips = await self.get_clips(broadcaster_id, started_at=started_at, ended_at=ended_at, first=100)
            
            # Calculate basic analytics
            total_views = sum(video.view_count for video in videos)
            total_clip_views = sum(clip.view_count for clip in clips)
            
            return {
                "period": {
                    "start": started_at.isoformat(),
                    "end": ended_at.isoformat()
                },
                "streams": {
                    "total_streams": len(streams.get("data", [])),
                    "data": streams.get("data", [])
                },
                "videos": {
                    "total_videos": len(videos),
                    "total_views": total_views,
                    "data": [video.__dict__ for video in videos]
                },
                "clips": {
                    "total_clips": len(clips),
                    "total_clip_views": total_clip_views,
                    "data": [clip.__dict__ for clip in clips]
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get channel analytics: {e}")
            return {"error": str(e)}
    
    async def validate_connection(self) -> bool:
        """Validate Twitch connection"""
        try:
            await self._validate_token()
            return self.credentials.access_token is not None
            
        except Exception as e:
            logger.error(f"Twitch connection validation failed: {e}")
            return False
    
    async def get_platform_limits(self) -> Dict[str, Any]:
        """Get Twitch platform limits and guidelines"""
        return {
            "max_stream_title_length": 140,
            "max_clip_duration_seconds": 60,
            "max_video_file_size_gb": 10,
            "supported_streaming_resolutions": [
                "1920x1080", "1280x720", "854x480", "640x360"
            ],
            "supported_fps": [30, 60],
            "max_bitrate_kbps": 6000,
            "rate_limits": {
                "helix_api_requests_per_minute": 800,
                "chat_messages_per_30_seconds": 20,
                "whisper_messages_per_minute": 10,
                "mod_actions_per_minute": 100
            },
            "content_guidelines": {
                "mature_content_allowed": True,
                "copyright_music_restrictions": True,
                "community_guidelines_enforcement": True,
                "dmca_enforcement": True
            },
            "monetization": {
                "subscriber_tiers": ["Tier 1", "Tier 2", "Tier 3"],
                "bits_enabled": True,
                "ad_revenue_sharing": True,
                "sponsor_integration_allowed": True
            }
        }


# Export main components
__all__ = [
    "TwitchConnector",
    "TwitchCredentials",
    "TwitchStream",
    "TwitchClip", 
    "TwitchVideo",
    "TwitchPublishResult",
    "TwitchStreamType",
    "TwitchContentType",
    "TwitchChatBadge"
]