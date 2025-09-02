"""Spotify Platform Integration

Complete Spotify Web API integration for music distribution and analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import base64
import json

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus
)

logger = logging.getLogger(__name__)


class SpotifyPlatform(PlatformBase):
    """
Spotify platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """
        try:
            logger.info(f"Executing __init__")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
Initialize Spotify platform"""
        super().__init__(config)
        self.api_base = "https://api.spotify.com/v1"
        self.auth_base = "https://accounts.spotify.com"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """
Authenticate with Spotify using Client Credentials flow"""
        try:
            session = await self._get_session()
            
            # Prepare client credentials
            client_creds = f"{self.config.credentials.client_id}:{self.config.credentials.client_secret}"
            client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {client_creds_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            async with session.post(
                f"{self.auth_base}/api/token",
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.config.credentials.access_token = token_data['access_token']
                    
                    # Calculate expiration time
                    expires_in = token_data.get('expires_in', 3600)
                    self.config.credentials.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("Spotify authentication successful")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Spotify authentication failed: {response.status} - {error_text}")
                    self.increment_error_count()
                    return False
                    
        except Exception as e:
            logger.error(f"Spotify authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Spotify access token"""
        if not self.config.credentials.refresh_token:
            # For client credentials flow, just re-authenticate
            return await self.authenticate()
        
        try:
            session = await self._get_session()
            
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"{self.config.credentials.client_id}:{self.config.credentials.client_secret}".encode()).decode()}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.config.credentials.refresh_token
            }
            
            async with session.post(
                f"{self.auth_base}/api/token",
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.config.credentials.access_token = token_data['access_token']
                    
                    if 'refresh_token' in token_data:
                        self.config.credentials.refresh_token = token_data['refresh_token']
                    
                    expires_in = token_data.get('expires_in', 3600)
                    self.config.credentials.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    logger.info("Spotify token refreshed successfully")
                    return True
                else:
                    logger.error(f"Spotify token refresh failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Spotify token refresh error: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Spotify API"""
        if not self.is_authenticated or self._token_expired():
            if not await self.authenticate():
                return None
        
        try:
            session = await self._get_session()
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.config.credentials.access_token}'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    # Token expired, try to refresh
                    if await self.refresh_token():
                        headers['Authorization'] = f'Bearer {self.config.credentials.access_token}'
                        async with session.request(method, url, **kwargs) as retry_response:
                            if retry_response.status == 200:
                                return await retry_response.json()
                    return None
                
                elif response.status == 429:
                    # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 1))
                    await self.handle_rate_limit(retry_after)
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 200:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Spotify API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Spotify request error: {e}")
            self.increment_error_count()
            return None
    
    def _token_expired(self) -> bool:
        """Check if token is expired"""
        if not self.config.credentials.expires_at:
            return True
        return datetime.utcnow() >= self.config.credentials.expires_at
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """
Upload content to Spotify (Note: Direct upload not supported by public API)"""
        # Spotify doesn't support direct file uploads via public API
        # This would typically be handled through Spotify for Artists or distribution services
        return UploadResult(
            success=False,
            platform_id=self.platform_id,
            error="Direct upload to Spotify not supported via public API. Use Spotify for Artists or distribution services."
        )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Spotify analytics (requires Spotify for Artists API)"""
        # This would require Spotify for Artists API access
        # For now, return basic track information
        track_data = await self._make_request('GET', f'tracks/{content_id}')
        
        if not track_data:
            raise Exception(f"Track {content_id} not found")
        
        return AnalyticsData(
            platform_id=self.platform_id,
            content_id=content_id,
            views=0,  # Not available in public API
            likes=0,  # Not available in public API
            shares=0,  # Not available in public API
            comments=0,  # Not available in public API
            metadata={
                'track_name': track_data.get('name'),
                'artist_name': track_data.get('artists', [{}])[0].get('name'),
                'popularity': track_data.get('popularity'),
                'duration_ms': track_data.get('duration_ms'),
                'explicit': track_data.get('explicit'),
                'external_urls': track_data.get('external_urls')
            }
        )
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Spotify"""
        search_types = []
        
        if content_type:
            if content_type == ContentType.TRACK:
                search_types = ['track']
            elif content_type == ContentType.ALBUM:
                search_types = ['album']
            elif content_type == ContentType.PLAYLIST:
                search_types = ['playlist']
            else:
                search_types = ['track', 'album', 'artist', 'playlist']
        else:
            search_types = ['track', 'album', 'artist', 'playlist']
        
        params = {
            'q': query,
            'type': ','.join(search_types),
            'limit': 50
        }
        
        results = await self._make_request('GET', 'search', params=params)
        
        if not results:
            return []
        
        formatted_results = []
        
        for search_type in search_types:
            items = results.get(f"{search_type}s", {}).get('items', [])
            for item in items:
                formatted_results.append({
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'type': search_type,
                    'uri': item.get('uri'),
                    'external_urls': item.get('external_urls'),
                    'popularity': item.get('popularity'),
                    'artists': [artist.get('name') for artist in item.get('artists', [])],
                    'image_url': item.get('images', [{}])[0].get('url') if item.get('images') else None
                })
        
        return formatted_results
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's content from Spotify"""
        if not user_id:
            # Get current user's playlists
            user_data = await self._make_request('GET', 'me')
            if not user_data:
                return []
            user_id = user_data.get('id')
        
        # Get user's playlists
        playlists_data = await self._make_request('GET', f'users/{user_id}/playlists')
        
        if not playlists_data:
            return []
        
        playlists = []
        for playlist in playlists_data.get('items', []):
            playlists.append({
                'id': playlist.get('id'),
                'name': playlist.get('name'),
                'type': 'playlist',
                'description': playlist.get('description'),
                'tracks_total': playlist.get('tracks', {}).get('total'),
                'public': playlist.get('public'),
                'collaborative': playlist.get('collaborative'),
                'external_urls': playlist.get('external_urls'),
                'image_url': playlist.get('images', [{}])[0].get('url') if playlist.get('images') else None
            })
        
        return playlists
    
    async def delete_content(self, content_id: str) -> bool:
        """
Delete content from Spotify (limited to playlists you own)"""
        try:
            # Can only unfollow playlists, not delete tracks
            result = await self._make_request('DELETE', f'playlists/{content_id}/followers')
            return result is not None
        except Exception as e:
            logger.error(f"Error deleting Spotify content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update content metadata on Spotify (limited to playlists you own)"""
        try:
            data = {
                'name': metadata.title,
                'description': metadata.description,
                'public': True  # Can be made configurable
            }
            
            result = await self._make_request(
                'PUT', 
                f'playlists/{content_id}',
                json=data
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error updating Spotify content: {e}")
            return False
    
    async def get_track_features(self, track_id: str) -> Optional[Dict[str, Any]]:
        """Get audio features for a track"""
        return await self._make_request('GET', f'audio-features/{track_id}')
    
    async def get_track_analysis(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
Get audio analysis for a track"""
        return await self._make_request('GET', f'audio-analysis/{track_id}')
    
    async def get_recommendations(self, 
                                seed_tracks: List[str] = None,
                                seed_artists: List[str] = None,
                                seed_genres: List[str] = None,
                                **audio_features) -> List[Dict[str, Any]]:
        """
Get track recommendations"""
        params = {}
        
        if seed_tracks:
            params['seed_tracks'] = ','.join(seed_tracks[:5])  # Max 5
        if seed_artists:
            params['seed_artists'] = ','.join(seed_artists[:5])  # Max 5
        if seed_genres:
            params['seed_genres'] = ','.join(seed_genres[:5])  # Max 5
        
        # Add audio feature parameters
        for feature, value in audio_features.items():
            if feature.startswith(('min_', 'max_', 'target_')):
                params[feature] = value
        
        params['limit'] = 20
        
        result = await self._make_request('GET', 'recommendations', params=params)
        
        if not result:
            return []
        
        return result.get('tracks', [])
    
    async def create_playlist(self, user_id: str, name: str, description: str = "", public: bool = True) -> Optional[str]:
        """Create a new playlist"""
        data = {
            'name': name,
            'description': description,
            'public': public
        }
        
        result = await self._make_request('POST', f'users/{user_id}/playlists', json=data)
        
        if result:
            return result.get('id')
        return None
    
    async def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]) -> bool:
        """
Add tracks to a playlist"""
        data = {'uris': track_uris}
        
        result = await self._make_request('POST', f'playlists/{playlist_id}/tracks', json=data)
        return result is not None
    
    async def get_available_markets(self) -> List[str]:
        """
Get available markets"""
        result = await self._make_request('GET', 'markets')
        if result:
            return result.get('markets', [])
        return []
    
    async def close(self):
        """
Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
