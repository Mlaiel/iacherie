"""
Platform Integration Utilities for IA Influencer Agent Platform
Advanced integrations with social media platforms and streaming services

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform with Multi-Content Protection
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import aiohttp
import asyncio
import json
from typing import Dict, Any, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
import time
import hashlib
import hmac
import base64
import urllib.parse
from enum import Enum
import jwt
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import threading
import uuid

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Supported platform types"""
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"


class AuthType(Enum):
    """Authentication methods"""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    WEBHOOK_SIGNATURE = "webhook_signature"


class ContentType(Enum):
    """Content types for platform posting"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    STORY = "story"
    REEL = "reel"
    LIVE = "live"


@dataclass
class PlatformCredentials:
    """Platform authentication credentials"""
    platform: PlatformType
    auth_type: AuthType
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    webhook_secret: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_expired(self) -> bool:
        """Check if credentials are expired"""
        if self.expires_at:
            return datetime.utcnow() >= self.expires_at
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'platform': self.platform.value,
            'auth_type': self.auth_type.value,
            'client_id': self.client_id,
            'access_token': self.access_token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'scopes': self.scopes,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class PlatformProfile:
    """User profile from platform"""
    platform: PlatformType
    user_id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    verification_status: bool = False
    profile_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PlatformContent:
    """Content posted on platform"""
    content_id: str
    platform: PlatformType
    content_type: ContentType
    title: Optional[str] = None
    description: Optional[str] = None
    media_urls: List[str] = field(default_factory=list)
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    engagement_rate: float = 0.0
    posted_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    location: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PostingResult:
    """Result of content posting"""
    success: bool
    platform: PlatformType
    content_id: Optional[str] = None
    platform_url: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    posted_at: datetime = field(default_factory=datetime.utcnow)


class BasePlatformAPI:
    """Base class for platform API integrations"""
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.session = None
        self.rate_limiter = RateLimiter()
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> bool:
        """Authenticate with platform API"""
        raise NotImplementedError
    
    async def refresh_token(self) -> bool:
        """Refresh authentication token"""
        raise NotImplementedError
    
    async def get_profile(self) -> Optional[PlatformProfile]:
        """Get user profile"""
        raise NotImplementedError
    
    async def post_content(self, content_data: Dict[str, Any]) -> PostingResult:
        """Post content to platform"""
        raise NotImplementedError
    
    async def get_content_analytics(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get analytics for specific content"""
        raise NotImplementedError
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content from platform"""
        raise NotImplementedError
    
    def _prepare_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare authentication headers"""
        headers = {'User-Agent': 'IA-Influencer-Agent/1.0'}
        
        if self.credentials.auth_type == AuthType.BEARER_TOKEN:
            headers['Authorization'] = f'Bearer {self.credentials.access_token}'
        elif self.credentials.auth_type == AuthType.API_KEY:
            headers['X-API-Key'] = self.credentials.api_key
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    async def _make_request(self, method: str, url: str, 
                          headers: Optional[Dict[str, str]] = None,
                          data: Optional[Dict[str, Any]] = None,
                          json_data: Optional[Dict[str, Any]] = None,
                          params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any]]:
        """Make authenticated API request with rate limiting"""
        await self.rate_limiter.wait(self.credentials.platform)
        
        try:
            request_headers = self._prepare_headers(headers)
            
            async with self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                data=data,
                json=json_data,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_data = await response.json() if response.content_type == 'application/json' else {'text': await response.text()}
                
                if response.status < 400:
                    return True, response_data
                else:
                    logger.error(f"API request failed: {response.status} - {response_data}")
                    return False, {
                        'error': response_data,
                        'status_code': response.status
                    }
                    
        except Exception as e:
            logger.error(f"Request exception: {str(e)}")
            return False, {'error': str(e)}


class SpotifyAPI(BasePlatformAPI):
    """Spotify Web API integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://api.spotify.com/v1"
        
    async def authenticate(self) -> bool:
        """Authenticate with Spotify using Client Credentials flow"""
        try:
            auth_url = "https://accounts.spotify.com/api/token"
            
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret
            }
            
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            success, response = await self._make_request(
                'POST', auth_url, headers=headers, data=auth_data
            )
            
            if success and 'access_token' in response:
                self.credentials.access_token = response['access_token']
                self.credentials.expires_at = datetime.utcnow() + timedelta(seconds=response.get('expires_in', 3600))
                return True
                
        except Exception as e:
            logger.error(f"Spotify authentication failed: {str(e)}")
        
        return False
    
    async def get_profile(self) -> Optional[PlatformProfile]:
        """Get Spotify user profile"""
        success, response = await self._make_request('GET', f"{self.base_url}/me")
        
        if success:
            return PlatformProfile(
                platform=PlatformType.SPOTIFY,
                user_id=response.get('id'),
                username=response.get('display_name', ''),
                display_name=response.get('display_name', ''),
                follower_count=response.get('followers', {}).get('total', 0),
                profile_image_url=response.get('images', [{}])[0].get('url') if response.get('images') else None,
                profile_url=response.get('external_urls', {}).get('spotify'),
                metadata=response
            )
        
        return None
    
    async def get_user_playlists(self) -> List[Dict[str, Any]]:
        """Get user's Spotify playlists"""
        success, response = await self._make_request('GET', f"{self.base_url}/me/playlists")
        
        if success and 'items' in response:
            return response['items']
        
        return []
    
    async def create_playlist(self, name: str, description: str = "", 
                            public: bool = False) -> Optional[str]:
        """Create a new Spotify playlist"""
        user_profile = await self.get_profile()
        if not user_profile:
            return None
        
        playlist_data = {
            'name': name,
            'description': description,
            'public': public
        }
        
        success, response = await self._make_request(
            'POST', 
            f"{self.base_url}/users/{user_profile.user_id}/playlists",
            json_data=playlist_data
        )
        
        if success:
            return response.get('id')
        
        return None
    
    async def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]) -> bool:
        """Add tracks to Spotify playlist"""
        track_data = {'uris': track_uris}
        
        success, _ = await self._make_request(
            'POST',
            f"{self.base_url}/playlists/{playlist_id}/tracks",
            json_data=track_data
        )
        
        return success


class YouTubeAPI(BasePlatformAPI):
    """YouTube Data API integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
    async def get_profile(self) -> Optional[PlatformProfile]:
        """Get YouTube channel profile"""
        params = {
            'part': 'snippet,statistics',
            'mine': 'true'
        }
        
        success, response = await self._make_request('GET', f"{self.base_url}/channels", params=params)
        
        if success and response.get('items'):
            channel = response['items'][0]
            snippet = channel.get('snippet', {})
            statistics = channel.get('statistics', {})
            
            return PlatformProfile(
                platform=PlatformType.YOUTUBE,
                user_id=channel.get('id'),
                username=snippet.get('customUrl', ''),
                display_name=snippet.get('title', ''),
                bio=snippet.get('description', ''),
                profile_image_url=snippet.get('thumbnails', {}).get('default', {}).get('url'),
                follower_count=int(statistics.get('subscriberCount', 0)),
                post_count=int(statistics.get('videoCount', 0)),
                metadata={
                    'view_count': int(statistics.get('viewCount', 0)),
                    'channel': channel
                }
            )
        
        return None
    
    async def upload_video(self, video_file: str, title: str, description: str = "",
                          tags: List[str] = None, privacy_status: str = "private") -> PostingResult:
        """Upload video to YouTube"""
        # Note: This is a simplified version. Full YouTube upload requires multipart upload
        try:
            # Video snippet metadata
            video_metadata = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or []
                },
                'status': {
                    'privacyStatus': privacy_status
                }
            }
            
            # For actual implementation, you would use YouTube's resumable upload API
            # This is a placeholder for the upload process
            
            return PostingResult(
                success=True,
                platform=PlatformType.YOUTUBE,
                content_id="placeholder_video_id",
                platform_url=f"https://youtube.com/watch?v=placeholder_video_id"
            )
            
        except Exception as e:
            logger.error(f"YouTube upload failed: {str(e)}")
            return PostingResult(
                success=False,
                platform=PlatformType.YOUTUBE,
                error_message=str(e)
            )
    
    async def get_video_analytics(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get YouTube video analytics"""
        params = {
            'part': 'statistics,snippet',
            'id': video_id
        }
        
        success, response = await self._make_request('GET', f"{self.base_url}/videos", params=params)
        
        if success and response.get('items'):
            video = response['items'][0]
            statistics = video.get('statistics', {})
            
            return {
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'video_data': video
            }
        
        return None


class InstagramAPI(BasePlatformAPI):
    """Instagram Basic Display API integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://graph.instagram.com"
        
    async def get_profile(self) -> Optional[PlatformProfile]:
        """Get Instagram user profile"""
        params = {
            'fields': 'id,username,account_type,media_count'
        }
        
        success, response = await self._make_request('GET', f"{self.base_url}/me", params=params)
        
        if success:
            return PlatformProfile(
                platform=PlatformType.INSTAGRAM,
                user_id=response.get('id'),
                username=response.get('username', ''),
                display_name=response.get('username', ''),
                post_count=response.get('media_count', 0),
                metadata=response
            )
        
        return None
    
    async def get_media(self, limit: int = 25) -> List[PlatformContent]:
        """Get user's Instagram media"""
        params = {
            'fields': 'id,caption,media_type,media_url,permalink,timestamp',
            'limit': limit
        }
        
        success, response = await self._make_request('GET', f"{self.base_url}/me/media", params=params)
        
        media_list = []
        if success and response.get('data'):
            for item in response['data']:
                media_type_map = {
                    'IMAGE': ContentType.IMAGE,
                    'VIDEO': ContentType.VIDEO,
                    'CAROUSEL_ALBUM': ContentType.IMAGE
                }
                
                content = PlatformContent(
                    content_id=item.get('id'),
                    platform=PlatformType.INSTAGRAM,
                    content_type=media_type_map.get(item.get('media_type'), ContentType.IMAGE),
                    description=item.get('caption'),
                    media_urls=[item.get('media_url')] if item.get('media_url') else [],
                    posted_at=datetime.fromisoformat(item.get('timestamp', '').replace('Z', '+00:00')) if item.get('timestamp') else None,
                    metadata=item
                )
                media_list.append(content)
        
        return media_list


class TikTokAPI(BasePlatformAPI):
    """TikTok API integration (Business API)"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3"
        
    async def get_profile(self) -> Optional[PlatformProfile]:
        """Get TikTok user profile"""
        # TikTok Business API endpoint for user info
        success, response = await self._make_request('GET', f"{self.base_url}/user/info")
        
        if success and response.get('data'):
            user_data = response['data']
            return PlatformProfile(
                platform=PlatformType.TIKTOK,
                user_id=user_data.get('user_id'),
                username=user_data.get('username', ''),
                display_name=user_data.get('display_name', ''),
                profile_image_url=user_data.get('avatar_url'),
                follower_count=user_data.get('follower_count', 0),
                following_count=user_data.get('following_count', 0),
                metadata=user_data
            )
        
        return None


class TwitterAPI(BasePlatformAPI):
    """Twitter API v2 integration"""
    
    def __init__(self, credentials: PlatformCredentials):
        super().__init__(credentials)
        self.base_url = "https://api.twitter.com/2"
        
    async def get_profile(self) -> Optional[PlatformProfile]:
        """Get Twitter user profile"""
        params = {
            'user.fields': 'created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified'
        }
        
        success, response = await self._make_request('GET', f"{self.base_url}/users/me", params=params)
        
        if success and response.get('data'):
            user = response['data']
            public_metrics = user.get('public_metrics', {})
            
            return PlatformProfile(
                platform=PlatformType.TWITTER,
                user_id=user.get('id'),
                username=user.get('username', ''),
                display_name=user.get('name', ''),
                bio=user.get('description', ''),
                profile_image_url=user.get('profile_image_url'),
                follower_count=public_metrics.get('followers_count', 0),
                following_count=public_metrics.get('following_count', 0),
                post_count=public_metrics.get('tweet_count', 0),
                verification_status=user.get('verified', False),
                metadata=user
            )
        
        return None
    
    async def post_tweet(self, text: str, media_ids: List[str] = None) -> PostingResult:
        """Post a tweet"""
        tweet_data = {'text': text}
        
        if media_ids:
            tweet_data['media'] = {'media_ids': media_ids}
        
        success, response = await self._make_request('POST', f"{self.base_url}/tweets", json_data=tweet_data)
        
        if success and response.get('data'):
            tweet_id = response['data']['id']
            return PostingResult(
                success=True,
                platform=PlatformType.TWITTER,
                content_id=tweet_id,
                platform_url=f"https://twitter.com/i/web/status/{tweet_id}"
            )
        else:
            return PostingResult(
                success=False,
                platform=PlatformType.TWITTER,
                error_message=response.get('error', 'Unknown error')
            )


class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self):
        self.limits = {
            PlatformType.SPOTIFY: {'requests': 0, 'reset_time': datetime.utcnow(), 'max_per_minute': 100},
            PlatformType.YOUTUBE: {'requests': 0, 'reset_time': datetime.utcnow(), 'max_per_minute': 100},
            PlatformType.INSTAGRAM: {'requests': 0, 'reset_time': datetime.utcnow(), 'max_per_minute': 200},
            PlatformType.TIKTOK: {'requests': 0, 'reset_time': datetime.utcnow(), 'max_per_minute': 100},
            PlatformType.TWITTER: {'requests': 0, 'reset_time': datetime.utcnow(), 'max_per_minute': 300},
        }
        self._lock = threading.Lock()
    
    async def wait(self, platform: PlatformType):
        """Wait if rate limit would be exceeded"""
        with self._lock:
            if platform not in self.limits:
                return
            
            limit = self.limits[platform]
            now = datetime.utcnow()
            
            # Reset counter if a minute has passed
            if (now - limit['reset_time']).total_seconds() >= 60:
                limit['requests'] = 0
                limit['reset_time'] = now
            
            # If at limit, wait until reset time
            if limit['requests'] >= limit['max_per_minute']:
                sleep_time = 60 - (now - limit['reset_time']).total_seconds()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                limit['requests'] = 0
                limit['reset_time'] = datetime.utcnow()
            
            limit['requests'] += 1


class CredentialsManager:
    """Manage platform credentials securely"""
    
    def __init__(self, database_path: str = "platform_credentials.db"):
        self.database_path = database_path
        self._init_database()
        self._lock = threading.Lock()
    
    def _init_database(self):
        """Initialize credentials database"""
        with sqlite3.connect(self.database_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS platform_credentials (
                    credential_id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    auth_type TEXT NOT NULL,
                    client_id TEXT,
                    client_secret TEXT,
                    access_token TEXT,
                    refresh_token TEXT,
                    api_key TEXT,
                    webhook_secret TEXT,
                    expires_at TEXT,
                    scopes TEXT,
                    user_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_credentials_platform ON platform_credentials (platform)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_credentials_user ON platform_credentials (user_id)
            ''')
    
    def save_credentials(self, credentials: PlatformCredentials) -> bool:
        """Save platform credentials"""
        try:
            with self._lock:
                with sqlite3.connect(self.database_path) as conn:
                    credential_id = str(uuid.uuid4())
                    conn.execute('''
                        INSERT OR REPLACE INTO platform_credentials
                        (credential_id, platform, auth_type, client_id, client_secret,
                         access_token, refresh_token, api_key, webhook_secret,
                         expires_at, scopes, user_id, created_at, updated_at, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        credential_id,
                        credentials.platform.value,
                        credentials.auth_type.value,
                        credentials.client_id,
                        credentials.client_secret,
                        credentials.access_token,
                        credentials.refresh_token,
                        credentials.api_key,
                        credentials.webhook_secret,
                        credentials.expires_at.isoformat() if credentials.expires_at else None,
                        json.dumps(credentials.scopes),
                        credentials.user_id,
                        credentials.created_at.isoformat(),
                        credentials.updated_at.isoformat(),
                        True
                    ))
            return True
        except Exception as e:
            logger.error(f"Failed to save credentials: {str(e)}")
            return False
    
    def get_credentials(self, platform: PlatformType, user_id: str) -> Optional[PlatformCredentials]:
        """Get platform credentials for user"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM platform_credentials 
                    WHERE platform = ? AND user_id = ? AND is_active = 1
                    ORDER BY updated_at DESC LIMIT 1
                ''', (platform.value, user_id))
                
                row = cursor.fetchone()
                if row:
                    return PlatformCredentials(
                        platform=PlatformType(row['platform']),
                        auth_type=AuthType(row['auth_type']),
                        client_id=row['client_id'],
                        client_secret=row['client_secret'],
                        access_token=row['access_token'],
                        refresh_token=row['refresh_token'],
                        api_key=row['api_key'],
                        webhook_secret=row['webhook_secret'],
                        expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
                        scopes=json.loads(row['scopes']) if row['scopes'] else [],
                        user_id=row['user_id'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        updated_at=datetime.fromisoformat(row['updated_at'])
                    )
        except Exception as e:
            logger.error(f"Failed to get credentials: {str(e)}")
        
        return None


class PlatformIntegrationManager:
    """Main platform integration management system"""
    
    def __init__(self, credentials_manager: CredentialsManager):
        self.credentials_manager = credentials_manager
        self.api_classes = {
            PlatformType.SPOTIFY: SpotifyAPI,
            PlatformType.YOUTUBE: YouTubeAPI,
            PlatformType.INSTAGRAM: InstagramAPI,
            PlatformType.TIKTOK: TikTokAPI,
            PlatformType.TWITTER: TwitterAPI,
        }
        self.active_sessions = {}
    
    async def get_platform_api(self, platform: PlatformType, user_id: str) -> Optional[BasePlatformAPI]:
        """Get authenticated platform API instance"""
        try:
            # Get credentials
            credentials = self.credentials_manager.get_credentials(platform, user_id)
            if not credentials:
                logger.error(f"No credentials found for {platform.value} user {user_id}")
                return None
            
            # Check if credentials are expired
            if credentials.is_expired():
                logger.warning(f"Credentials expired for {platform.value} user {user_id}")
                return None
            
            # Get API class
            api_class = self.api_classes.get(platform)
            if not api_class:
                logger.error(f"No API class found for platform {platform.value}")
                return None
            
            # Create API instance
            api_instance = api_class(credentials)
            
            # Authenticate if needed
            if credentials.auth_type in [AuthType.OAUTH2, AuthType.API_KEY]:
                authenticated = await api_instance.authenticate()
                if not authenticated:
                    logger.error(f"Authentication failed for {platform.value} user {user_id}")
                    return None
            
            return api_instance
            
        except Exception as e:
            logger.error(f"Failed to get platform API: {str(e)}")
            return None
    
    async def get_all_profiles(self, user_id: str) -> Dict[str, PlatformProfile]:
        """Get profiles from all connected platforms"""
        profiles = {}
        
        for platform in PlatformType:
            try:
                api = await self.get_platform_api(platform, user_id)
                if api:
                    async with api:
                        profile = await api.get_profile()
                        if profile:
                            profiles[platform.value] = profile
                            
            except Exception as e:
                logger.error(f"Failed to get profile for {platform.value}: {str(e)}")
        
        return profiles
    
    async def cross_post_content(self, user_id: str, 
                               platforms: List[PlatformType],
                               content_data: Dict[str, Any]) -> Dict[str, PostingResult]:
        """Post content to multiple platforms"""
        results = {}
        
        # Create posting tasks
        tasks = []
        for platform in platforms:
            task = self._post_to_platform(platform, user_id, content_data)
            tasks.append((platform, task))
        
        # Execute posts concurrently
        completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Process results
        for i, (platform, _) in enumerate(tasks):
            result = completed_tasks[i]
            if isinstance(result, Exception):
                results[platform.value] = PostingResult(
                    success=False,
                    platform=platform,
                    error_message=str(result)
                )
            else:
                results[platform.value] = result
        
        return results
    
    async def _post_to_platform(self, platform: PlatformType, user_id: str,
                              content_data: Dict[str, Any]) -> PostingResult:
        """Post content to specific platform"""
        try:
            api = await self.get_platform_api(platform, user_id)
            if not api:
                return PostingResult(
                    success=False,
                    platform=platform,
                    error_message="Failed to get platform API"
                )
            
            async with api:
                if platform == PlatformType.TWITTER:
                    # Twitter-specific posting
                    return await api.post_tweet(
                        text=content_data.get('text', ''),
                        media_ids=content_data.get('media_ids', [])
                    )
                elif platform == PlatformType.YOUTUBE:
                    # YouTube-specific posting
                    return await api.upload_video(
                        video_file=content_data.get('video_file', ''),
                        title=content_data.get('title', ''),
                        description=content_data.get('description', ''),
                        tags=content_data.get('tags', [])
                    )
                else:
                    # Generic content posting
                    return await api.post_content(content_data)
                    
        except Exception as e:
            logger.error(f"Failed to post to {platform.value}: {str(e)}")
            return PostingResult(
                success=False,
                platform=platform,
                error_message=str(e)
            )
    
    async def sync_analytics(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """Sync analytics from all connected platforms"""
        analytics = {}
        
        for platform in PlatformType:
            try:
                api = await self.get_platform_api(platform, user_id)
                if api:
                    async with api:
                        profile = await api.get_profile()
                        if profile:
                            # Get platform-specific analytics
                            platform_analytics = {
                                'profile': profile.to_dict() if hasattr(profile, 'to_dict') else profile.__dict__,
                                'last_synced': datetime.utcnow().isoformat()
                            }
                            
                            # Add platform-specific data
                            if platform == PlatformType.INSTAGRAM:
                                media = await api.get_media()
                                platform_analytics['recent_media'] = [m.__dict__ for m in media[:10]]
                            elif platform == PlatformType.SPOTIFY:
                                playlists = await api.get_user_playlists()
                                platform_analytics['playlists'] = playlists[:10]
                            
                            analytics[platform.value] = platform_analytics
                            
            except Exception as e:
                logger.error(f"Failed to sync analytics for {platform.value}: {str(e)}")
                analytics[platform.value] = {'error': str(e)}
        
        return analytics
    
    def get_platform_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get aggregated statistics across all platforms"""
        # This would typically pull from a database of synced analytics
        # For now, return a placeholder structure
        return {
            'total_platforms_connected': len([p for p in PlatformType if self.credentials_manager.get_credentials(p, user_id)]),
            'last_sync': datetime.utcnow().isoformat(),
            'engagement_summary': {
                'total_followers': 0,
                'total_posts': 0,
                'avg_engagement_rate': 0.0
            }
        }


class WebhookHandler:
    """Handle webhooks from various platforms"""
    
    def __init__(self, credentials_manager: CredentialsManager):
        self.credentials_manager = credentials_manager
        self.webhook_handlers = {
            PlatformType.SPOTIFY: self._handle_spotify_webhook,
            PlatformType.YOUTUBE: self._handle_youtube_webhook,
            PlatformType.INSTAGRAM: self._handle_instagram_webhook,
            PlatformType.TIKTOK: self._handle_tiktok_webhook,
            PlatformType.TWITTER: self._handle_twitter_webhook,
        }
    
    async def handle_webhook(self, platform: PlatformType, 
                           request_data: Dict[str, Any],
                           headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle incoming webhook from platform"""
        try:
            handler = self.webhook_handlers.get(platform)
            if not handler:
                return {'error': f'No webhook handler for platform {platform.value}'}
            
            # Verify webhook signature if required
            if not await self._verify_webhook_signature(platform, request_data, headers):
                return {'error': 'Invalid webhook signature'}
            
            # Process webhook
            return await handler(request_data, headers)
            
        except Exception as e:
            logger.error(f"Webhook handling failed: {str(e)}")
            return {'error': str(e)}
    
    async def _verify_webhook_signature(self, platform: PlatformType,
                                      request_data: Dict[str, Any],
                                      headers: Dict[str, str]) -> bool:
        """Verify webhook signature"""
        # This would implement signature verification for each platform
        # For now, return True (implement based on platform requirements)
        return True
    
    async def _handle_spotify_webhook(self, data: Dict[str, Any], 
                                    headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle Spotify webhook"""
        # Process Spotify-specific webhook events
        return {'status': 'processed', 'platform': 'spotify'}
    
    async def _handle_youtube_webhook(self, data: Dict[str, Any],
                                    headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle YouTube webhook"""
        # Process YouTube-specific webhook events
        return {'status': 'processed', 'platform': 'youtube'}
    
    async def _handle_instagram_webhook(self, data: Dict[str, Any],
                                      headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle Instagram webhook"""
        # Process Instagram-specific webhook events
        return {'status': 'processed', 'platform': 'instagram'}
    
    async def _handle_tiktok_webhook(self, data: Dict[str, Any],
                                   headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle TikTok webhook"""
        # Process TikTok-specific webhook events
        return {'status': 'processed', 'platform': 'tiktok'}
    
    async def _handle_twitter_webhook(self, data: Dict[str, Any],
                                    headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle Twitter webhook"""
        # Process Twitter-specific webhook events
        return {'status': 'processed', 'platform': 'twitter'}


class PlatformIntegrationError(Exception):
    """Custom exception for platform integration errors"""
    pass
