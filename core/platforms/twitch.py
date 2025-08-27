"""
Twitch Platform Integration

Twitch API integration for live streaming and content analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus
)

logger = logging.getLogger(__name__)


class TwitchPlatform(PlatformBase):
    """Twitch platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """Initialize Twitch platform"""
        super().__init__(config)
        self.api_base = "https://api.twitch.tv/helix"
        self.auth_base = "https://id.twitch.tv/oauth2"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Twitch using OAuth2"""
        try:
            session = await self._get_session()
            
            data = {
                'client_id': self.config.credentials.client_id,
                'client_secret': self.config.credentials.client_secret,
                'grant_type': 'client_credentials'
            }
            
            async with session.post(f"{self.auth_base}/token", data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.config.credentials.access_token = token_data['access_token']
                    
                    expires_in = token_data.get('expires_in', 3600)
                    self.config.credentials.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("Twitch authentication successful")
                    return True
                else:
                    logger.error(f"Twitch authentication failed: {response.status}")
                    self.increment_error_count()
                    return False
                    
        except Exception as e:
            logger.error(f"Twitch authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Twitch access token"""
        return await self.authenticate()  # Twitch uses client credentials flow
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Twitch API"""
        if not self.is_authenticated or self._token_expired():
            if not await self.authenticate():
                return None
        
        try:
            session = await self._get_session()
            headers = kwargs.get('headers', {})
            headers['Client-ID'] = self.config.credentials.client_id
            headers['Authorization'] = f'Bearer {self.config.credentials.access_token}'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    if await self.refresh_token():
                        headers['Authorization'] = f'Bearer {self.config.credentials.access_token}'
                        async with session.request(method, url, **kwargs) as retry_response:
                            if retry_response.status == 200:
                                return await retry_response.json()
                    return None
                
                elif response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 200:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Twitch API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Twitch request error: {e}")
            self.increment_error_count()
            return None
    
    def _token_expired(self) -> bool:
        """Check if token is expired"""
        if not self.config.credentials.expires_at:
            return True
        return datetime.utcnow() >= self.config.credentials.expires_at
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload content to Twitch (clips/highlights only)"""
        # Twitch doesn't support direct video uploads via API
        # Only supports creating clips from existing streams
        return UploadResult(
            success=False,
            platform_id=self.platform_id,
            error="Direct upload not supported by Twitch API. Use streaming or clip creation."
        )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Twitch analytics for streams/clips"""
        try:
            # Get video/clip data
            params = {'id': content_id}
            
            # Try as video first
            video_result = await self._make_request('GET', 'videos', params=params)
            
            if video_result and video_result.get('data'):
                video = video_result['data'][0]
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=video.get('view_count', 0),
                    likes=0,  # Not available in Twitch API
                    shares=0,  # Not available
                    comments=0,  # Would need separate API call
                    metadata={
                        'title': video.get('title'),
                        'description': video.get('description'),
                        'duration': video.get('duration'),
                        'created_at': video.get('created_at'),
                        'url': video.get('url'),
                        'thumbnail_url': video.get('thumbnail_url')
                    }
                )
            
            # Try as clip
            clip_result = await self._make_request('GET', 'clips', params=params)
            
            if clip_result and clip_result.get('data'):
                clip = clip_result['data'][0]
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=clip.get('view_count', 0),
                    likes=0,
                    shares=0,
                    comments=0,
                    metadata={
                        'title': clip.get('title'),
                        'duration': clip.get('duration'),
                        'created_at': clip.get('created_at'),
                        'url': clip.get('url'),
                        'thumbnail_url': clip.get('thumbnail_url'),
                        'creator_name': clip.get('creator_name'),
                        'game_id': clip.get('game_id')
                    }
                )
            
            raise Exception(f"Content {content_id} not found")
            
        except Exception as e:
            logger.error(f"Twitch analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Twitch"""
        try:
            results = []
            
            # Search streams
            stream_params = {'query': query, 'first': 20}
            stream_result = await self._make_request('GET', 'search/channels', params=stream_params)
            
            if stream_result and stream_result.get('data'):
                for channel in stream_result['data']:
                    results.append({
                        'id': channel.get('id'),
                        'type': 'channel',
                        'display_name': channel.get('display_name'),
                        'broadcaster_language': channel.get('broadcaster_language'),
                        'game_name': channel.get('game_name'),
                        'is_live': channel.get('is_live'),
                        'title': channel.get('title'),
                        'thumbnail_url': channel.get('thumbnail_url')
                    })
            
            # Search categories/games
            game_params = {'query': query, 'first': 20}
            game_result = await self._make_request('GET', 'search/categories', params=game_params)
            
            if game_result and game_result.get('data'):
                for game in game_result['data']:
                    results.append({
                        'id': game.get('id'),
                        'type': 'game',
                        'name': game.get('name'),
                        'box_art_url': game.get('box_art_url')
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Twitch search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's videos/clips from Twitch"""
        try:
            if not user_id:
                # Get current user
                user_result = await self._make_request('GET', 'users')
                if not user_result or not user_result.get('data'):
                    return []
                user_id = user_result['data'][0]['id']
            
            content = []
            
            # Get videos
            video_params = {'user_id': user_id, 'first': 20}
            video_result = await self._make_request('GET', 'videos', params=video_params)
            
            if video_result and video_result.get('data'):
                for video in video_result['data']:
                    content.append({
                        'id': video.get('id'),
                        'type': 'video',
                        'title': video.get('title'),
                        'description': video.get('description'),
                        'created_at': video.get('created_at'),
                        'published_at': video.get('published_at'),
                        'url': video.get('url'),
                        'thumbnail_url': video.get('thumbnail_url'),
                        'viewable': video.get('viewable'),
                        'view_count': video.get('view_count'),
                        'language': video.get('language'),
                        'type_detail': video.get('type'),
                        'duration': video.get('duration')
                    })
            
            # Get clips
            clip_params = {'broadcaster_id': user_id, 'first': 20}
            clip_result = await self._make_request('GET', 'clips', params=clip_params)
            
            if clip_result and clip_result.get('data'):
                for clip in clip_result['data']:
                    content.append({
                        'id': clip.get('id'),
                        'type': 'clip',
                        'title': clip.get('title'),
                        'created_at': clip.get('created_at'),
                        'url': clip.get('url'),
                        'embed_url': clip.get('embed_url'),
                        'thumbnail_url': clip.get('thumbnail_url'),
                        'duration': clip.get('duration'),
                        'view_count': clip.get('view_count'),
                        'language': clip.get('language'),
                        'creator_name': clip.get('creator_name'),
                        'creator_id': clip.get('creator_id')
                    })
            
            return content
            
        except Exception as e:
            logger.error(f"Error getting Twitch user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete video from Twitch"""
        try:
            # Only videos can be deleted, not clips
            params = {'id': content_id}
            result = await self._make_request('DELETE', 'videos', params=params)
            return result is not None
        except Exception as e:
            logger.error(f"Error deleting Twitch content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update video metadata on Twitch"""
        try:
            data = {
                'title': metadata.title,
                'description': metadata.description,
                'language': metadata.language
            }
            
            params = {'id': content_id}
            result = await self._make_request('PATCH', 'videos', params=params, json=data)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error updating Twitch content: {e}")
            return False
    
    async def get_stream_info(self, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get current stream information"""
        try:
            params = {}
            if user_id:
                params['user_id'] = user_id
            else:
                params['user_login'] = self.config.credentials.user_id
            
            result = await self._make_request('GET', 'streams', params=params)
            
            if result and result.get('data'):
                return result['data'][0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting Twitch stream info: {e}")
            return None
    
    async def create_clip(self, broadcaster_id: str) -> Optional[str]:
        """Create a clip from current stream"""
        try:
            data = {'broadcaster_id': broadcaster_id}
            result = await self._make_request('POST', 'clips', json=data)
            
            if result and result.get('data'):
                return result['data'][0].get('id')
            return None
            
        except Exception as e:
            logger.error(f"Error creating Twitch clip: {e}")
            return None
    
    async def get_followers(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get followers for a user"""
        try:
            params = {'to_id': user_id or self.config.credentials.user_id, 'first': 100}
            result = await self._make_request('GET', 'users/follows', params=params)
            
            if result and result.get('data'):
                return result['data']
            return []
            
        except Exception as e:
            logger.error(f"Error getting Twitch followers: {e}")
            return []
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
