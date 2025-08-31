"""MusicKit Engine - Apple Music Integration Core
==============================================

Core engine for Apple Music integration providing MusicKit API access,
catalog management, and intelligent music operations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: 2025 - All Rights Reserved
"""
import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aiohttp

logger = logging.getLogger(__name__)

class AppleMusicEndpoint(Enum):
    """Apple Music API endpoints"""
    CATALOG = "catalog"
    LIBRARY = "library"
    SEARCH = "search"
    CHARTS = "charts"
    RECOMMENDATIONS = "recommendations"

@dataclass
class AppleMusicTrack:
    """Apple Music track data structure"""
    id: str
    title: str
    artist: str
    album: str
    duration_ms: int
    preview_url: Optional[str] = None
    artwork_url: Optional[str] = None
    isrc: Optional[str] = None
    genres: List[str] = field(default_factory=list)
    release_date: Optional[datetime] = None
    play_params: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class AppleMusicPlaylist:
    """Apple Music playlist data structure"""
    id: str
    name: str
    description: str
    curator: str
    track_count: int
    tracks: List[AppleMusicTrack] = field(default_factory=list)
    artwork_url: Optional[str] = None
    created_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AppleMusicArtist:
    """Apple Music artist data structure"""
    id: str
    name: str
    genres: List[str] = field(default_factory=list)
    albums: List[str] = field(default_factory=list)
    artwork_url: Optional[str] = None
    biography: Optional[str] = None
    social_links: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MusicKitEngine:
    """
    MusicKit Engine for Apple Music Integration
    
    Provides comprehensive Apple Music capabilities including:
    - MusicKit API integration
    - Catalog search and discovery
    - Playlist management
    - User library access
    - Streaming analytics
    - Content metadata extraction
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.team_id = self.config.get('team_id')
        self.key_id = self.config.get('key_id') 
        self.private_key = self.config.get('private_key')
        self.user_token = None
        self.session = None
        
        # API configuration
        self.base_url = "https://api.music.apple.com/v1"
        self.storefront = self.config.get('storefront', 'us')
        
        # Rate limiting
        self.rate_limit = self.config.get('rate_limit', 100)  # requests per minute
        self.request_count = 0
        self.rate_limit_reset = datetime.utcnow()
        
        # Caching
        self.cache = {}
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 hour
        
    async def initialize(self):
        """Initialize the MusicKit engine"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession()
            
            # Generate developer token (JWT)
            await self._generate_developer_token()
            
            logger.info("MusicKit engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MusicKit engine: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the engine and cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def search_catalog(
        self, 
        query: str, 
        types: List[str] = None,
        limit: int = 25
    ) -> Dict[str, List[Any]]:
        """
        Search Apple Music catalog
        
        Args:
            query: Search query string
            types: Content types to search (songs, albums, artists, playlists)
            limit: Maximum results per type
            
        Returns:
            Dictionary with search results by type
        """
        try:
            if types is None:
                types = ['songs', 'albums', 'artists', 'playlists']
            
            # Check cache
            cache_key = f"search_{query}_{','.join(types)}_{limit}"
            if cache_key in self.cache:
                cached_result, timestamp = self.cache[cache_key]
                if datetime.utcnow() - timestamp < timedelta(seconds=self.cache_ttl):
                    return cached_result
            
            # Prepare API request
            params = {
                'term': query,
                'types': ','.join(types),
                'limit': limit,
                'l': 'en-us'
            }
            
            url = f"{self.base_url}/catalog/{self.storefront}/search"
            
            # Make API request
            response = await self._make_request('GET', url, params=params)
            
            # Process response
            results = {
                'songs': [],
                'albums': [],
                'artists': [],
                'playlists': []
            }
            
            if 'results' in response:
                # Process songs
                if 'songs' in response['results']:
                    for song_data in response['results']['songs']['data']:
                        track = self._parse_track_data(song_data)
                        results['songs'].append(track)
                
                # Process albums
                if 'albums' in response['results']:
                    for album_data in response['results']['albums']['data']:
                        album = self._parse_album_data(album_data)
                        results['albums'].append(album)
                
                # Process artists
                if 'artists' in response['results']:
                    for artist_data in response['results']['artists']['data']:
                        artist = self._parse_artist_data(artist_data)
                        results['artists'].append(artist)
                
                # Process playlists
                if 'playlists' in response['results']:
                    for playlist_data in response['results']['playlists']['data']:
                        playlist = self._parse_playlist_data(playlist_data)
                        results['playlists'].append(playlist)
            
            # Cache results
            self.cache[cache_key] = (results, datetime.utcnow())
            
            return results
            
        except Exception as e:
            logger.error(f"Catalog search failed: {e}")
            raise
    
    async def get_track_details(self, track_id: str) -> AppleMusicTrack:
        """Get detailed information about a specific track"""
        try:
            url = f"{self.base_url}/catalog/{self.storefront}/songs/{track_id}"
            response = await self._make_request('GET', url)
            
            if 'data' in response and len(response['data']) > 0:
                track_data = response['data'][0]
                return self._parse_track_data(track_data)
            else:
                raise ValueError(f"Track {track_id} not found")
                
        except Exception as e:
            logger.error(f"Failed to get track details for {track_id}: {e}")
            raise
    
    async def get_playlist_tracks(self, playlist_id: str) -> AppleMusicPlaylist:
        """Get all tracks from a playlist"""
        try:
            url = f"{self.base_url}/catalog/{self.storefront}/playlists/{playlist_id}/tracks"
            response = await self._make_request('GET', url)
            
            playlist_url = f"{self.base_url}/catalog/{self.storefront}/playlists/{playlist_id}"
            playlist_response = await self._make_request('GET', playlist_url)
            
            # Parse playlist info
            playlist_data = playlist_response['data'][0] if 'data' in playlist_response else {}
            playlist = self._parse_playlist_data(playlist_data)
            
            # Parse tracks
            if 'data' in response:
                for track_data in response['data']:
                    track = self._parse_track_data(track_data)
                    playlist.tracks.append(track)
            
            return playlist
            
        except Exception as e:
            logger.error(f"Failed to get playlist tracks for {playlist_id}: {e}")
            raise
    
    async def get_artist_top_songs(self, artist_id: str, limit: int = 10) -> List[AppleMusicTrack]:
        """Get top songs for an artist"""
        try:
            url = f"{self.base_url}/catalog/{self.storefront}/artists/{artist_id}/songs"
            params = {'limit': limit}
            
            response = await self._make_request('GET', url, params=params)
            
            tracks = []
            if 'data' in response:
                for track_data in response['data']:
                    track = self._parse_track_data(track_data)
                    tracks.append(track)
            
            return tracks
            
        except Exception as e:
            logger.error(f"Failed to get top songs for artist {artist_id}: {e}")
            raise
    
    async def get_recommendations(
        self, 
        seed_track_ids: List[str] = None,
        seed_artist_ids: List[str] = None,
        limit: int = 20
    ) -> List[AppleMusicTrack]:
        """Get music recommendations based on seeds"""
        try:
            # Apple Music doesn't have a direct recommendations endpoint like Spotify
            # This would require using the Charts endpoint or similar content
            
            url = f"{self.base_url}/catalog/{self.storefront}/charts"
            params = {
                'types': 'songs',
                'limit': limit
            }
            
            response = await self._make_request('GET', url, params=params)
            
            recommendations = []
            if 'results' in response and 'songs' in response['results']:
                for chart in response['results']['songs']:
                    if 'data' in chart:
                        for track_data in chart['data']:
                            track = self._parse_track_data(track_data)
                            recommendations.append(track)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            raise
    
    async def analyze_user_library(self, user_token: str) -> Dict[str, Any]:
        """Analyze user's Apple Music library"""
        try:
            self.user_token = user_token
            
            # Get user's library songs
            url = f"{self.base_url}/me/library/songs"
            headers = {'Music-User-Token': user_token}
            
            response = await self._make_request('GET', url, headers=headers)
            
            analysis = {
                'total_songs': 0,
                'genres': {},
                'artists': {},
                'decades': {},
                'most_played': [],
                'recently_added': []
            }
            
            if 'data' in response:
                analysis['total_songs'] = len(response['data'])
                
                for track_data in response['data']:
                    track = self._parse_track_data(track_data)
                    
                    # Analyze genres
                    for genre in track.genres:
                        analysis['genres'][genre] = analysis['genres'].get(genre, 0) + 1
                    
                    # Analyze artists
                    analysis['artists'][track.artist] = analysis['artists'].get(track.artist, 0) + 1
                    
                    # Analyze decades (if release date available)
                    if track.release_date:
                        decade = (track.release_date.year // 10) * 10
                        decade_key = f"{decade}s"
                        analysis['decades'][decade_key] = analysis['decades'].get(decade_key, 0) + 1
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze user library: {e}")
            raise
    
    # Private helper methods
    
    async def _generate_developer_token(self):
        """Generate JWT developer token for Apple Music API"""
        try:
            if not all([self.team_id, self.key_id, self.private_key]):
                logger.warning("Apple Music credentials not configured, using mock mode")
                return
                
            # In a real implementation, this would generate a proper JWT
            # For now, we'll use a placeholder
            self.developer_token = "mock_developer_token"
            
        except Exception as e:
            logger.error(f"Failed to generate developer token: {e}")
            raise
    
    async def _make_request(
        self, 
        method: str, 
        url: str, 
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Apple Music API"""
        try:
            # Check rate limit
            await self._check_rate_limit()
            
            # Prepare headers
            request_headers = {
                'Authorization': f'Bearer {getattr(self, "developer_token", "mock_token")}',
                'Content-Type': 'application/json'
            }
            
            if headers:
                request_headers.update(headers)
            
            # For demo purposes, return mock data
            if "mock_token" in request_headers.get('Authorization', ''):
                return await self._get_mock_response(method, url, params)
            
            # Make actual request (when properly configured)
            if self.session:
                async with self.session.request(
                    method, url, params=params, headers=request_headers, json=data
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        response.raise_for_status()
            else:
                raise RuntimeError("Session not initialized")
                
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        now = datetime.utcnow()
        
        # Reset counter if minute has passed
        if now - self.rate_limit_reset > timedelta(minutes=1):
            self.request_count = 0
            self.rate_limit_reset = now
        
        # Check if rate limit exceeded
        if self.request_count >= self.rate_limit:
            sleep_time = 60 - (now - self.rate_limit_reset).seconds
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                self.request_count = 0
                self.rate_limit_reset = datetime.utcnow()
        
        self.request_count += 1
    
    async def _get_mock_response(self, method: str, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate mock responses for testing"""
        import random
        
        if 'search' in url:
            return {
                'results': {
                    'songs': {
                        'data': [
                            {
                                'id': f'mock_song_{i}',
                                'type': 'songs',
                                'attributes': {
                                    'name': f'Mock Song {i}',
                                    'artistName': f'Mock Artist {i}',
                                    'albumName': f'Mock Album {i}',
                                    'durationInMillis': random.randint(180000, 300000),
                                    'genreNames': ['Pop', 'Rock'],
                                    'releaseDate': '2023-01-01',
                                    'isrc': f'MOCK{i:06d}'
                                }
                            }
                            for i in range(1, 6)
                        ]
                    },
                    'artists': {
                        'data': [
                            {
                                'id': f'mock_artist_{i}',
                                'type': 'artists',
                                'attributes': {
                                    'name': f'Mock Artist {i}',
                                    'genreNames': ['Pop', 'Rock']
                                }
                            }
                            for i in range(1, 4)
                        ]
                    }
                }
            }
        elif 'songs' in url or 'tracks' in url:
            return {
                'data': [
                    {
                        'id': 'mock_song_1',
                        'type': 'songs',
                        'attributes': {
                            'name': 'Mock Song',
                            'artistName': 'Mock Artist',
                            'albumName': 'Mock Album',
                            'durationInMillis': 240000,
                            'genreNames': ['Pop'],
                            'releaseDate': '2023-01-01',
                            'isrc': 'MOCK000001'
                        }
                    }
                ]
            }
        elif 'charts' in url:
            return {
                'results': {
                    'songs': [
                        {
                            'data': [
                                {
                                    'id': f'chart_song_{i}',
                                    'type': 'songs',
                                    'attributes': {
                                        'name': f'Chart Hit {i}',
                                        'artistName': f'Chart Artist {i}',
                                        'albumName': f'Chart Album {i}',
                                        'durationInMillis': random.randint(180000, 300000),
                                        'genreNames': ['Pop'],
                                        'releaseDate': '2023-01-01'
                                    }
                                }
                                for i in range(1, 11)
                            ]
                        }
                    ]
                }
            }
        
        return {'data': []}
    
    def _parse_track_data(self, track_data: Dict[str, Any]) -> AppleMusicTrack:
        """Parse track data from Apple Music API response"""
        try:
            attributes = track_data.get('attributes', {})
            
            return AppleMusicTrack(
                id=track_data.get('id', ''),
                title=attributes.get('name', 'Unknown'),
                artist=attributes.get('artistName', 'Unknown Artist'),
                album=attributes.get('albumName', 'Unknown Album'),
                duration_ms=attributes.get('durationInMillis', 0),
                preview_url=attributes.get('previews', [{}])[0].get('url') if attributes.get('previews') else None,
                artwork_url=self._get_artwork_url(attributes.get('artwork')),
                isrc=attributes.get('isrc'),
                genres=attributes.get('genreNames', []),
                release_date=self._parse_date(attributes.get('releaseDate')),
                play_params=attributes.get('playParams'),
                metadata=attributes
            )
            
        except Exception as e:
            logger.error(f"Failed to parse track data: {e}")
            raise
    
    def _parse_playlist_data(self, playlist_data: Dict[str, Any]) -> AppleMusicPlaylist:
        """Parse playlist data from Apple Music API response"""
        try:
            attributes = playlist_data.get('attributes', {})
            
            return AppleMusicPlaylist(
                id=playlist_data.get('id', ''),
                name=attributes.get('name', 'Unknown Playlist'),
                description=attributes.get('description', {}).get('standard', ''),
                curator=attributes.get('curatorName', 'Unknown'),
                track_count=attributes.get('trackCount', 0),
                artwork_url=self._get_artwork_url(attributes.get('artwork')),
                created_date=self._parse_date(attributes.get('lastModifiedDate')),
                metadata=attributes
            )
            
        except Exception as e:
            logger.error(f"Failed to parse playlist data: {e}")
            raise
    
    def _parse_album_data(self, album_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse album data from Apple Music API response"""
        attributes = album_data.get('attributes', {})
        
        return {
            'id': album_data.get('id', ''),
            'name': attributes.get('name', 'Unknown Album'),
            'artist': attributes.get('artistName', 'Unknown Artist'),
            'track_count': attributes.get('trackCount', 0),
            'genres': attributes.get('genreNames', []),
            'release_date': self._parse_date(attributes.get('releaseDate')),
            'artwork_url': self._get_artwork_url(attributes.get('artwork'))
        }
    
    def _parse_artist_data(self, artist_data: Dict[str, Any]) -> AppleMusicArtist:
        """Parse artist data from Apple Music API response"""
        try:
            attributes = artist_data.get('attributes', {})
            
            return AppleMusicArtist(
                id=artist_data.get('id', ''),
                name=attributes.get('name', 'Unknown Artist'),
                genres=attributes.get('genreNames', []),
                artwork_url=self._get_artwork_url(attributes.get('artwork')),
                metadata=attributes
            )
            
        except Exception as e:
            logger.error(f"Failed to parse artist data: {e}")
            raise
    
    def _get_artwork_url(self, artwork_data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract artwork URL from artwork data"""
        if not artwork_data:
            return None
        
        url_template = artwork_data.get('url', '')
        if url_template:
            # Replace placeholders with desired dimensions
            return url_template.replace('{w}', '600').replace('{h}', '600')
        
        return None
    
    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_string:
            return None
        
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except Exception:
            return None
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get engine statistics and status"""
        return {
            'initialized': self.session is not None,
            'storefront': self.storefront,
            'rate_limit': self.rate_limit,
            'requests_made': self.request_count,
            'cache_size': len(self.cache),
            'has_user_token': self.user_token is not None,
            'has_developer_token': hasattr(self, 'developer_token')
        }