"""Apple Music Platform Integration

Apple Music API integration for music distribution and analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import jwt
import time

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus
)

logger = logging.getLogger(__name__)


class AppleMusicPlatform(PlatformBase):
    """Apple Music platform integration"""    
    def __init__(self, config: PlatformConfig):
        """Initialize Apple Music platform"""        super().__init__(config)
        self.api_base = "https://api.music.apple.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Apple Music using JWT"""        try:
            # Generate JWT token for Apple Music API
            token = self._generate_jwt_token()
            if token:
                self.config.credentials.access_token = token
                self.config.credentials.expires_at = datetime.utcnow() + timedelta(hours=1)
                self.status = PlatformStatus.ACTIVE
                self.reset_error_count()
                logger.info("Apple Music authentication successful")
                return True
            else:
                logger.error("Failed to generate Apple Music JWT token")
                return False
                
        except Exception as e:
            logger.error(f"Apple Music authentication error: {e}")
            self.increment_error_count()
            return False
    
    def _generate_jwt_token(self) -> Optional[str]:
        """Generate JWT token for Apple Music API"""        try:
            # JWT payload
            payload = {
                'iss': self.config.credentials.client_id,  # Team ID
                'iat': int(time.time()),
                'exp': int(time.time()) + 3600,  # 1 hour
                'aud': 'appstoreconnect-v1'
            }
            
            # JWT headers
            headers = {
                'alg': 'ES256',
                'kid': self.config.credentials.api_key  # Key ID
            }
            
            # Sign JWT with private key
            # Note: In production, you'd load the private key from a secure location
            private_key = self.config.credentials.api_secret  # Private key content
            
            token = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
            return token
            
        except Exception as e:
            logger.error(f"Error generating Apple Music JWT: {e}")
            return None
    
    async def refresh_token(self) -> bool:
        """Refresh Apple Music JWT token"""        return await self.authenticate()  # JWT tokens are regenerated
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Apple Music API"""        if not self.is_authenticated or self._token_expired():
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
                    logger.error(f"Apple Music API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Apple Music request error: {e}")
            self.increment_error_count()
            return None
    
    def _token_expired(self) -> bool:
        """Check if token is expired"""        if not self.config.credentials.expires_at:
            return True
        return datetime.utcnow() >= self.config.credentials.expires_at
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload content to Apple Music (not supported via public API)"""        # Apple Music doesn't support direct content uploads via public API
        # Content must be distributed through Apple Music for Artists or music distributors
        return UploadResult(
            success=False,
            platform_id=self.platform_id,
            error="Direct upload not supported by Apple Music API. Use Apple Music for Artists or music distributors."
        )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Apple Music analytics (limited public API access)"""        try:
            # Get song/album data
            result = await self._make_request('GET', f'catalog/us/songs/{content_id}')
            
            if not result or 'data' not in result:
                raise Exception(f"Content {content_id} not found")
            
            song = result['data'][0]
            attributes = song.get('attributes', {})
            
            # Apple Music public API doesn't provide play counts or detailed analytics
            # This would require Apple Music for Artists API access
            
            return AnalyticsData(
                platform_id=self.platform_id,
                content_id=content_id,
                views=0,  # Not available in public API
                likes=0,  # Not available
                shares=0,  # Not available
                comments=0,  # Not available
                metadata={
                    'name': attributes.get('name'),
                    'artist_name': attributes.get('artistName'),
                    'album_name': attributes.get('albumName'),
                    'duration_ms': attributes.get('durationInMillis'),
                    'release_date': attributes.get('releaseDate'),
                    'genre_names': attributes.get('genreNames'),
                    'isrc': attributes.get('isrc'),
                    'url': attributes.get('url'),
                    'artwork_url': attributes.get('artwork', {}).get('url'),
                    'preview_url': attributes.get('previews', [{}])[0].get('url') if attributes.get('previews') else None
                }
            )
            
        except Exception as e:
            logger.error(f"Apple Music analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Apple Music"""        try:
            search_types = []
            
            if content_type:
                if content_type == ContentType.TRACK:
                    search_types = ['songs']
                elif content_type == ContentType.ALBUM:
                    search_types = ['albums']
                elif content_type == ContentType.PLAYLIST:
                    search_types = ['playlists']
                else:
                    search_types = ['songs', 'albums', 'artists', 'playlists']
            else:
                search_types = ['songs', 'albums', 'artists', 'playlists']
            
            params = {
                'term': query,
                'types': ','.join(search_types),
                'limit': 25
            }
            
            result = await self._make_request('GET', 'catalog/us/search', params=params)
            
            if not result or 'results' not in result:
                return []
            
            formatted_results = []
            results = result['results']
            
            for search_type in search_types:
                items = results.get(search_type, {}).get('data', [])
                for item in items:
                    attributes = item.get('attributes', {})
                    formatted_results.append({
                        'id': item.get('id'),
                        'type': search_type.rstrip('s'),  # Remove plural
                        'name': attributes.get('name'),
                        'artist_name': attributes.get('artistName'),
                        'album_name': attributes.get('albumName'),
                        'release_date': attributes.get('releaseDate'),
                        'genre_names': attributes.get('genreNames'),
                        'duration_ms': attributes.get('durationInMillis'),
                        'track_count': attributes.get('trackCount'),
                        'url': attributes.get('url'),
                        'artwork_url': attributes.get('artwork', {}).get('url'),
                        'preview_url': attributes.get('previews', [{}])[0].get('url') if attributes.get('previews') else None
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Apple Music search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's content from Apple Music (limited public API access)"""        # Apple Music public API doesn't provide user-specific content
        # This would require user authentication and Apple Music subscription
        logger.warning("User content not available via Apple Music public API")
        return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content from Apple Music (not supported)"""        logger.warning("Content deletion not supported by Apple Music API")
        return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update content metadata on Apple Music (not supported)"""        logger.warning("Content update not supported by Apple Music public API")
        return False
    
    async def get_album_tracks(self, album_id: str) -> List[Dict[str, Any]]:
        """Get tracks from an album"""        try:
            result = await self._make_request('GET', f'catalog/us/albums/{album_id}/tracks')
            
            if not result or 'data' not in result:
                return []
            
            tracks = []
            for track in result['data']:
                attributes = track.get('attributes', {})
                tracks.append({
                    'id': track.get('id'),
                    'name': attributes.get('name'),
                    'artist_name': attributes.get('artistName'),
                    'album_name': attributes.get('albumName'),
                    'track_number': attributes.get('trackNumber'),
                    'duration_ms': attributes.get('durationInMillis'),
                    'isrc': attributes.get('isrc'),
                    'url': attributes.get('url'),
                    'preview_url': attributes.get('previews', [{}])[0].get('url') if attributes.get('previews') else None
                })
            
            return tracks
            
        except Exception as e:
            logger.error(f"Error getting Apple Music album tracks: {e}")
            return []
    
    async def get_artist_albums(self, artist_id: str) -> List[Dict[str, Any]]:
        """Get albums by an artist"""        try:
            result = await self._make_request('GET', f'catalog/us/artists/{artist_id}/albums')
            
            if not result or 'data' not in result:
                return []
            
            albums = []
            for album in result['data']:
                attributes = album.get('attributes', {})
                albums.append({
                    'id': album.get('id'),
                    'name': attributes.get('name'),
                    'artist_name': attributes.get('artistName'),
                    'release_date': attributes.get('releaseDate'),
                    'genre_names': attributes.get('genreNames'),
                    'track_count': attributes.get('trackCount'),
                    'copyright': attributes.get('copyright'),
                    'url': attributes.get('url'),
                    'artwork_url': attributes.get('artwork', {}).get('url')
                })
            
            return albums
            
        except Exception as e:
            logger.error(f"Error getting Apple Music artist albums: {e}")
            return []
    
    async def get_playlist_tracks(self, playlist_id: str) -> List[Dict[str, Any]]:
        """Get tracks from a playlist"""        try:
            result = await self._make_request('GET', f'catalog/us/playlists/{playlist_id}/tracks')
            
            if not result or 'data' not in result:
                return []
            
            tracks = []
            for track in result['data']:
                attributes = track.get('attributes', {})
                tracks.append({
                    'id': track.get('id'),
                    'name': attributes.get('name'),
                    'artist_name': attributes.get('artistName'),
                    'album_name': attributes.get('albumName'),
                    'duration_ms': attributes.get('durationInMillis'),
                    'url': attributes.get('url'),
                    'preview_url': attributes.get('previews', [{}])[0].get('url') if attributes.get('previews') else None
                })
            
            return tracks
            
        except Exception as e:
            logger.error(f"Error getting Apple Music playlist tracks: {e}")
            return []
    
    async def get_charts(self, chart_type: str = 'songs', genre: str = None) -> List[Dict[str, Any]]:
        """Get Apple Music charts"""        try:
            endpoint = f'catalog/us/charts'
            params = {'types': chart_type}
            
            if genre:
                params['genre'] = genre
            
            result = await self._make_request('GET', endpoint, params=params)
            
            if not result or 'results' not in result:
                return []
            
            charts = []
            chart_data = result['results'].get(chart_type, [])
            
            for chart in chart_data:
                chart_info = {
                    'name': chart.get('name'),
                    'chart': chart.get('chart'),
                    'data': []
                }
                
                for item in chart.get('data', []):
                    attributes = item.get('attributes', {})
                    chart_info['data'].append({
                        'id': item.get('id'),
                        'name': attributes.get('name'),
                        'artist_name': attributes.get('artistName'),
                        'album_name': attributes.get('albumName'),
                        'url': attributes.get('url'),
                        'artwork_url': attributes.get('artwork', {}).get('url')
                    })
                
                charts.append(chart_info)
            
            return charts
            
        except Exception as e:
            logger.error(f"Error getting Apple Music charts: {e}")
            return []
    
    async def get_genres(self) -> List[Dict[str, Any]]:
        """Get available genres"""        try:
            result = await self._make_request('GET', 'catalog/us/genres')
            
            if not result or 'data' not in result:
                return []
            
            genres = []
            for genre in result['data']:
                attributes = genre.get('attributes', {})
                genres.append({
                    'id': genre.get('id'),
                    'name': attributes.get('name'),
                    'url': attributes.get('url')
                })
            
            return genres
            
        except Exception as e:
            logger.error(f"Error getting Apple Music genres: {e}")
            return []
    
    async def close(self):
        """Close HTTP session"""        if self.session and not self.session.closed:
            await self.session.close()
