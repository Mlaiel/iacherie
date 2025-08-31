"""SoundCloud Platform Integration

SoundCloud API integration for audio content sharing and analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""
import asyncio
import aiohttp
import aiofiles
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import json
import os

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus
)

logger = logging.getLogger(__name__)


class SoundCloudPlatform(PlatformBase):
    """SoundCloud platform integration"""    
    def __init__(self, config: PlatformConfig):
        """Initialize SoundCloud platform"""        super().__init__(config)
        self.api_base = "https://api.soundcloud.com"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with SoundCloud using OAuth2"""        try:
            if self.config.credentials.access_token:
                if await self._validate_token():
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    return True
            
            logger.error("SoundCloud authentication requires OAuth2 flow or valid access token")
            return False
            
        except Exception as e:
            logger.error(f"SoundCloud authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh SoundCloud access token"""        if not self.config.credentials.refresh_token:
            logger.error("No refresh token available for SoundCloud")
            return False
        
        try:
            session = await self._get_session()
            
            data = {
                'grant_type': 'refresh_token',
                'client_id': self.config.credentials.client_id,
                'client_secret': self.config.credentials.client_secret,
                'refresh_token': self.config.credentials.refresh_token
            }
            
            async with session.post(f"{self.api_base}/oauth2/token", data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.config.credentials.access_token = token_data['access_token']
                    
                    if 'refresh_token' in token_data:
                        self.config.credentials.refresh_token = token_data['refresh_token']
                    
                    expires_in = token_data.get('expires_in', 3600)
                    self.config.credentials.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("SoundCloud token refreshed successfully")
                    return True
                else:
                    logger.error(f"SoundCloud token refresh failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"SoundCloud token refresh error: {e}")
            return False
    
    async def _validate_token(self) -> bool:
        """Validate SoundCloud access token"""        try:
            result = await self._make_request('GET', '/me')
            return result is not None
            
        except Exception as e:
            logger.error(f"SoundCloud token validation error: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to SoundCloud API"""        if not self.is_authenticated:
            if not await self.authenticate():
                return None
        
        try:
            session = await self._get_session()
            
            # Add OAuth token to params
            params = kwargs.get('params', {})
            params['oauth_token'] = self.config.credentials.access_token
            kwargs['params'] = params
            
            url = f"{self.api_base}{endpoint}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    if await self.refresh_token():
                        params['oauth_token'] = self.config.credentials.access_token
                        async with session.request(method, url, **kwargs) as retry_response:
                            if retry_response.status == 200:
                                return await retry_response.json()
                    return None
                
                elif response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"SoundCloud API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"SoundCloud request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload audio content to SoundCloud"""        try:
            if not os.path.exists(content_path):
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Content file not found"
                )
            
            session = await self._get_session()
            
            # Prepare track data
            track_data = {
                'track[title]': metadata.title,
                'track[description]': metadata.description,
                'track[tag_list]': ' '.join(f'"{tag}"' for tag in metadata.tags),
                'track[genre]': metadata.category,
                'track[sharing]': 'public',  # Can be made configurable
                'oauth_token': self.config.credentials.access_token
            }
            
            # Create form data with file
            data = aiohttp.FormData()
            for key, value in track_data.items():
                data.add_field(key, value)
            
            async with aiofiles.open(content_path, 'rb') as audio_file:
                audio_content = await audio_file.read()
                data.add_field('track[asset_data]', audio_content, filename=os.path.basename(content_path))
            
            async with session.post(f"{self.api_base}/tracks", data=data) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    track_id = result.get('id')
                    
                    return UploadResult(
                        success=True,
                        platform_id=self.platform_id,
                        content_id=str(track_id),
                        url=result.get('permalink_url'),
                        message="Track uploaded successfully",
                        metadata={
                            'track_id': track_id,
                            'title': result.get('title'),
                            'duration': result.get('duration'),
                            'genre': result.get('genre'),
                            'waveform_url': result.get('waveform_url')
                        }
                    )
                else:
                    error_text = await response.text()
                    return UploadResult(
                        success=False,
                        platform_id=self.platform_id,
                        error=f"Upload failed: {error_text}"
                    )
                    
        except Exception as e:
            logger.error(f"SoundCloud upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get SoundCloud analytics for a track"""        try:
            # Get track data
            track_result = await self._make_request('GET', f'/tracks/{content_id}')
            
            if not track_result:
                raise Exception(f"Track {content_id} not found")
            
            # SoundCloud's public API has limited analytics
            # More detailed analytics require SoundCloud Pro/Premier
            
            return AnalyticsData(
                platform_id=self.platform_id,
                content_id=content_id,
                views=track_result.get('playback_count', 0),
                likes=track_result.get('favoritings_count', 0),
                shares=track_result.get('reposts_count', 0),
                comments=track_result.get('comment_count', 0),
                metadata={
                    'title': track_result.get('title'),
                    'description': track_result.get('description'),
                    'genre': track_result.get('genre'),
                    'duration': track_result.get('duration'),
                    'created_at': track_result.get('created_at'),
                    'permalink_url': track_result.get('permalink_url'),
                    'waveform_url': track_result.get('waveform_url'),
                    'download_count': track_result.get('download_count'),
                    'downloadable': track_result.get('downloadable'),
                    'tag_list': track_result.get('tag_list')
                }
            )
            
        except Exception as e:
            logger.error(f"SoundCloud analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on SoundCloud"""        try:
            search_type = 'tracks'  # Default to tracks
            if content_type == ContentType.PLAYLIST:
                search_type = 'playlists'
            
            params = {
                'q': query,
                'limit': 50,
                'linked_partitioning': 1
            }
            
            result = await self._make_request('GET', f'/{search_type}', params=params)
            
            if not result or 'collection' not in result:
                return []
            
            formatted_results = []
            for item in result['collection']:
                formatted_results.append({
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'description': item.get('description'),
                    'genre': item.get('genre'),
                    'duration': item.get('duration'),
                    'playback_count': item.get('playback_count'),
                    'favoritings_count': item.get('favoritings_count'),
                    'reposts_count': item.get('reposts_count'),
                    'comment_count': item.get('comment_count'),
                    'created_at': item.get('created_at'),
                    'permalink_url': item.get('permalink_url'),
                    'artwork_url': item.get('artwork_url'),
                    'waveform_url': item.get('waveform_url'),
                    'user': item.get('user', {}).get('username'),
                    'tag_list': item.get('tag_list')
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"SoundCloud search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's tracks from SoundCloud"""        try:
            if not user_id:
                # Get current user ID
                user_result = await self._make_request('GET', '/me')
                if not user_result:
                    return []
                user_id = user_result.get('id')
            
            params = {'limit': 100, 'linked_partitioning': 1}
            result = await self._make_request('GET', f'/users/{user_id}/tracks', params=params)
            
            if not result or 'collection' not in result:
                return []
            
            tracks = []
            for track in result['collection']:
                tracks.append({
                    'id': track.get('id'),
                    'title': track.get('title'),
                    'description': track.get('description'),
                    'genre': track.get('genre'),
                    'duration': track.get('duration'),
                    'playback_count': track.get('playback_count'),
                    'favoritings_count': track.get('favoritings_count'),
                    'reposts_count': track.get('reposts_count'),
                    'comment_count': track.get('comment_count'),
                    'created_at': track.get('created_at'),
                    'permalink_url': track.get('permalink_url'),
                    'artwork_url': track.get('artwork_url'),
                    'waveform_url': track.get('waveform_url'),
                    'downloadable': track.get('downloadable'),
                    'tag_list': track.get('tag_list'),
                    'sharing': track.get('sharing'),
                    'state': track.get('state')
                })
            
            return tracks
            
        except Exception as e:
            logger.error(f"Error getting SoundCloud user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete track from SoundCloud"""        try:
            result = await self._make_request('DELETE', f'/tracks/{content_id}')
            return result is not None
        except Exception as e:
            logger.error(f"Error deleting SoundCloud content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update track metadata on SoundCloud"""        try:
            data = {
                'track[title]': metadata.title,
                'track[description]': metadata.description,
                'track[tag_list]': ' '.join(f'"{tag}"' for tag in metadata.tags),
                'track[genre]': metadata.category
            }
            
            result = await self._make_request('PUT', f'/tracks/{content_id}', data=data)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error updating SoundCloud content: {e}")
            return False
    
    async def get_track_comments(self, track_id: str) -> List[Dict[str, Any]]:
        """Get comments for a track"""        try:
            params = {'limit': 100}
            result = await self._make_request('GET', f'/tracks/{track_id}/comments', params=params)
            
            if not result:
                return []
            
            comments = []
            for comment in result:
                comments.append({
                    'id': comment.get('id'),
                    'body': comment.get('body'),
                    'timestamp': comment.get('timestamp'),
                    'created_at': comment.get('created_at'),
                    'user': comment.get('user', {}).get('username'),
                    'user_id': comment.get('user', {}).get('id')
                })
            
            return comments
            
        except Exception as e:
            logger.error(f"Error getting SoundCloud track comments: {e}")
            return []
    
    async def create_playlist(self, title: str, description: str = "", tracks: List[str] = None) -> Optional[str]:
        """Create a new playlist"""        try:
            playlist_data = {
                'playlist[title]': title,
                'playlist[description]': description,
                'playlist[sharing]': 'public'
            }
            
            if tracks:
                # Add tracks to playlist
                track_list = []
                for track_id in tracks:
                    track_list.append({'id': track_id})
                playlist_data['playlist[tracks]'] = json.dumps(track_list)
            
            result = await self._make_request('POST', '/playlists', data=playlist_data)
            
            if result:
                return str(result.get('id'))
            return None
            
        except Exception as e:
            logger.error(f"Error creating SoundCloud playlist: {e}")
            return None
    
    async def add_track_to_playlist(self, playlist_id: str, track_id: str) -> bool:
        """Add track to playlist"""        try:
            # Get current playlist
            playlist = await self._make_request('GET', f'/playlists/{playlist_id}')
            if not playlist:
                return False
            
            # Add track to existing tracks
            tracks = playlist.get('tracks', [])
            tracks.append({'id': int(track_id)})
            
            data = {
                'playlist[tracks]': json.dumps(tracks)
            }
            
            result = await self._make_request('PUT', f'/playlists/{playlist_id}', data=data)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error adding track to SoundCloud playlist: {e}")
            return False
    
    async def get_user_info(self, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get user information"""        try:
            endpoint = f'/users/{user_id}' if user_id else '/me'
            return await self._make_request('GET', endpoint)
            
        except Exception as e:
            logger.error(f"Error getting SoundCloud user info: {e}")
            return None
    
    async def follow_user(self, user_id: str) -> bool:
        """Follow a user"""        try:
            result = await self._make_request('PUT', f'/me/followings/{user_id}')
            return result is not None
        except Exception as e:
            logger.error(f"Error following SoundCloud user: {e}")
            return False
    
    async def close(self):
        """Close HTTP session"""        if self.session and not self.session.closed:
            await self.session.close()
