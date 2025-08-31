"""Spotify Crawler
===============

Professional Spotify content crawler with Web API integration.
Implements Spotify Web API with intelligent rate limiting and monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import base64

import aiohttp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from ..utils.rate_limiter import SpotifyRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError
from ...database.models import CrawlResult, ContentMatch

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class SpotifyTrack:
    """Spotify track data structure."""    track_id: str
    name: str
    artists: List[Dict]
    album: Dict
    duration_ms: int
    explicit: bool
    external_ids: Dict
    external_urls: Dict
    href: str
    is_local: bool
    popularity: int
    preview_url: Optional[str]
    track_number: int
    type: str
    uri: str
    is_playable: bool
    linked_from: Optional[Dict]
    restrictions: Optional[Dict]
    disc_number: int

@dataclass
class SpotifyArtist:
    """Spotify artist data structure."""    artist_id: str
    name: str
    external_urls: Dict
    followers: Dict
    genres: List[str]
    href: str
    images: List[Dict]
    popularity: int
    type: str
    uri: str

@dataclass
class SpotifyAlbum:
    """Spotify album data structure."""    album_id: str
    name: str
    album_type: str
    total_tracks: int
    available_markets: List[str]
    external_urls: Dict
    href: str
    images: List[Dict]
    release_date: str
    release_date_precision: str
    restrictions: Optional[Dict]
    type: str
    uri: str
    artists: List[Dict]
    tracks: Optional[List[Dict]]
    copyrights: List[Dict]
    external_ids: Dict
    genres: List[str]
    label: str
    popularity: int

@dataclass
class SpotifyPlaylist:
    """Spotify playlist data structure."""    playlist_id: str
    name: str
    description: str
    collaborative: bool
    external_urls: Dict
    followers: Dict
    href: str
    images: List[Dict]
    owner: Dict
    primary_color: Optional[str]
    public: bool
    snapshot_id: str
    tracks: Dict
    type: str
    uri: str

class SpotifyCrawler:
    """    Professional Spotify crawler implementation.
    
    Features:
    - Spotify Web API integration
    - Track and artist monitoring
    - Playlist discovery and analysis
    - Advanced search capabilities
    - Audio feature analysis
    - Recommendation engine integration
    - Real-time streaming data
    - Market and genre analysis
    """    
    def __init__(self):
        """Initialize Spotify crawler."""        self.client_id = settings.SPOTIFY_CLIENT_ID
        self.client_secret = settings.SPOTIFY_CLIENT_SECRET
        self.access_token = None
        self.token_expires_at = None
        self.rate_limiter = SpotifyRateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.session = None
        
        # Initialize Spotify client
        self.spotify_client = None
        if self.client_id and self.client_secret:
            try:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.spotify_client = spotipy.Spotify(
                    client_credentials_manager=client_credentials_manager
                )
            except Exception as e:
                logger.error(f"Failed to initialize Spotify client: {e}")
        
        # Base URLs
        self.api_base_url = "https://api.spotify.com/v1"
        self.web_base_url = "https://open.spotify.com"
    
    async def __aenter__(self):
        """Async context manager entry."""        headers = {
            'User-Agent': self.user_agent_rotator.get_user_agent(),
            'Content-Type': 'application/json'
        }
        self.session = aiohttp.ClientSession(headers=headers)
        
        # Get access token
        if self.client_id and self.client_secret:
            await self._get_access_token()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""        if self.session:
            await self.session.close()
    
    async def _get_access_token(self):
        """Get Spotify access token using client credentials flow."""        try:
            if (self.access_token and self.token_expires_at and 
                datetime.now() < self.token_expires_at):
                return self.access_token
            
            # Prepare credentials
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials'
            }
            
            async with self.session.post(
                'https://accounts.spotify.com/api/token',
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data.get('access_token')
                    expires_in = token_data.get('expires_in', 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    
                    # Update session headers
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    
                    return self.access_token
                else:
                    logger.error(f"Failed to get Spotify access token: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Spotify token error: {e}")
            return None
    
    async def search_tracks(
        self,
        query: str,
        max_results: int = 50,
        market: str = 'US',
        include_external: str = None
    ) -> List[SpotifyTrack]:
        """        Search Spotify tracks.
        
        Args:
            query: Search query
            max_results: Maximum number of tracks to return
            market: Market for track availability
            include_external: Include external content
            
        Returns:
            List of Spotify track objects
        """        try:
            await self.rate_limiter.wait_if_needed()
            
            if self.spotify_client:
                return await self._search_tracks_spotipy(query, max_results, market)
            elif self.access_token:
                return await self._search_tracks_api(query, max_results, market, include_external)
            else:
                logger.warning("No Spotify API access available")
                return []
                
        except Exception as e:
            logger.error(f"Spotify track search error: {e}")
            return []
    
    async def _search_tracks_spotipy(self, query: str, max_results: int, market: str) -> List[SpotifyTrack]:
        """Search tracks using Spotipy library."""        try:
            tracks = []
            offset = 0
            limit = min(50, max_results)  # Spotify API limit
            
            while len(tracks) < max_results:
                results = self.spotify_client.search(
                    q=query,
                    type='track',
                    limit=limit,
                    offset=offset,
                    market=market
                )
                
                track_items = results.get('tracks', {}).get('items', [])
                
                if not track_items:
                    break
                
                for track_data in track_items:
                    if len(tracks) >= max_results:
                        break
                    
                    track = self._parse_track_data(track_data)
                    if track:
                        tracks.append(track)
                
                offset += limit
                await self.rate_limiter.update_usage(1)
            
            return tracks[:max_results]
            
        except Exception as e:
            logger.error(f"Spotipy track search failed: {e}")
            return []
    
    async def _search_tracks_api(
        self,
        query: str,
        max_results: int,
        market: str,
        include_external: str
    ) -> List[SpotifyTrack]:
        """Search tracks using direct API calls."""        try:
            await self._ensure_valid_token()
            
            tracks = []
            offset = 0
            limit = min(50, max_results)
            
            while len(tracks) < max_results:
                params = {
                    'q': query,
                    'type': 'track',
                    'limit': limit,
                    'offset': offset,
                    'market': market
                }
                
                if include_external:
                    params['include_external'] = include_external
                
                async with self.session.get(f"{self.api_base_url}/search", params=params) as response:
                    if response.status != 200:
                        break
                    
                    data = await response.json()
                    track_items = data.get('tracks', {}).get('items', [])
                    
                    if not track_items:
                        break
                    
                    for track_data in track_items:
                        if len(tracks) >= max_results:
                            break
                        
                        track = self._parse_track_data(track_data)
                        if track:
                            tracks.append(track)
                
                offset += limit
                await self.rate_limiter.update_usage(1)
            
            return tracks[:max_results]
            
        except Exception as e:
            logger.error(f"Spotify API track search failed: {e}")
            return []
    
    def _parse_track_data(self, track_data: dict) -> Optional[SpotifyTrack]:
        """Parse Spotify track data."""        try:
            return SpotifyTrack(
                track_id=track_data.get('id', ''),
                name=track_data.get('name', ''),
                artists=track_data.get('artists', []),
                album=track_data.get('album', {}),
                duration_ms=track_data.get('duration_ms', 0),
                explicit=track_data.get('explicit', False),
                external_ids=track_data.get('external_ids', {}),
                external_urls=track_data.get('external_urls', {}),
                href=track_data.get('href', ''),
                is_local=track_data.get('is_local', False),
                popularity=track_data.get('popularity', 0),
                preview_url=track_data.get('preview_url'),
                track_number=track_data.get('track_number', 1),
                type=track_data.get('type', 'track'),
                uri=track_data.get('uri', ''),
                is_playable=track_data.get('is_playable', True),
                linked_from=track_data.get('linked_from'),
                restrictions=track_data.get('restrictions'),
                disc_number=track_data.get('disc_number', 1)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse track data: {e}")
            return None
    
    async def get_artist_info(self, artist_id: str) -> Optional[SpotifyArtist]:
        """Get detailed artist information."""        try:
            await self.rate_limiter.wait_if_needed()
            await self._ensure_valid_token()
            
            async with self.session.get(f"{self.api_base_url}/artists/{artist_id}") as response:
                if response.status != 200:
                    return None
                
                artist_data = await response.json()
                
                await self.rate_limiter.update_usage(1)
                
                return SpotifyArtist(
                    artist_id=artist_data.get('id', ''),
                    name=artist_data.get('name', ''),
                    external_urls=artist_data.get('external_urls', {}),
                    followers=artist_data.get('followers', {}),
                    genres=artist_data.get('genres', []),
                    href=artist_data.get('href', ''),
                    images=artist_data.get('images', []),
                    popularity=artist_data.get('popularity', 0),
                    type=artist_data.get('type', 'artist'),
                    uri=artist_data.get('uri', '')
                )
                
        except Exception as e:
            logger.error(f"Failed to get artist info for {artist_id}: {e}")
            return None
    
    async def get_artist_top_tracks(self, artist_id: str, market: str = 'US') -> List[SpotifyTrack]:
        """Get artist's top tracks."""        try:
            await self.rate_limiter.wait_if_needed()
            await self._ensure_valid_token()
            
            params = {'market': market}
            
            async with self.session.get(
                f"{self.api_base_url}/artists/{artist_id}/top-tracks",
                params=params
            ) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                tracks = []
                
                for track_data in data.get('tracks', []):
                    track = self._parse_track_data(track_data)
                    if track:
                        tracks.append(track)
                
                await self.rate_limiter.update_usage(1)
                return tracks
                
        except Exception as e:
            logger.error(f"Failed to get artist top tracks: {e}")
            return []
    
    async def get_audio_features(self, track_ids: List[str]) -> List[Dict]:
        """Get audio features for tracks."""        try:
            await self.rate_limiter.wait_if_needed()
            await self._ensure_valid_token()
            
            # Spotify allows up to 100 track IDs per request
            batch_size = 100
            all_features = []
            
            for i in range(0, len(track_ids), batch_size):
                batch_ids = track_ids[i:i + batch_size]
                params = {'ids': ','.join(batch_ids)}
                
                async with self.session.get(
                    f"{self.api_base_url}/audio-features",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        all_features.extend(data.get('audio_features', []))
                
                await self.rate_limiter.update_usage(1)
            
            return all_features
            
        except Exception as e:
            logger.error(f"Failed to get audio features: {e}")
            return []
    
    async def search_playlists(
        self,
        query: str,
        max_results: int = 50,
        market: str = 'US'
    ) -> List[SpotifyPlaylist]:
        """Search Spotify playlists."""        try:
            await self.rate_limiter.wait_if_needed()
            await self._ensure_valid_token()
            
            playlists = []
            offset = 0
            limit = min(50, max_results)
            
            while len(playlists) < max_results:
                params = {
                    'q': query,
                    'type': 'playlist',
                    'limit': limit,
                    'offset': offset,
                    'market': market
                }
                
                async with self.session.get(f"{self.api_base_url}/search", params=params) as response:
                    if response.status != 200:
                        break
                    
                    data = await response.json()
                    playlist_items = data.get('playlists', {}).get('items', [])
                    
                    if not playlist_items:
                        break
                    
                    for playlist_data in playlist_items:
                        if len(playlists) >= max_results:
                            break
                        
                        playlist = self._parse_playlist_data(playlist_data)
                        if playlist:
                            playlists.append(playlist)
                
                offset += limit
                await self.rate_limiter.update_usage(1)
            
            return playlists[:max_results]
            
        except Exception as e:
            logger.error(f"Spotify playlist search failed: {e}")
            return []
    
    def _parse_playlist_data(self, playlist_data: dict) -> Optional[SpotifyPlaylist]:
        """Parse Spotify playlist data."""        try:
            return SpotifyPlaylist(
                playlist_id=playlist_data.get('id', ''),
                name=playlist_data.get('name', ''),
                description=playlist_data.get('description', ''),
                collaborative=playlist_data.get('collaborative', False),
                external_urls=playlist_data.get('external_urls', {}),
                followers=playlist_data.get('followers', {}),
                href=playlist_data.get('href', ''),
                images=playlist_data.get('images', []),
                owner=playlist_data.get('owner', {}),
                primary_color=playlist_data.get('primary_color'),
                public=playlist_data.get('public', True),
                snapshot_id=playlist_data.get('snapshot_id', ''),
                tracks=playlist_data.get('tracks', {}),
                type=playlist_data.get('type', 'playlist'),
                uri=playlist_data.get('uri', '')
            )
            
        except Exception as e:
            logger.error(f"Failed to parse playlist data: {e}")
            return None
    
    async def get_new_releases(self, country: str = 'US', max_results: int = 50) -> List[SpotifyAlbum]:
        """Get new album releases."""        try:
            await self.rate_limiter.wait_if_needed()
            await self._ensure_valid_token()
            
            albums = []
            offset = 0
            limit = min(50, max_results)
            
            while len(albums) < max_results:
                params = {
                    'country': country,
                    'limit': limit,
                    'offset': offset
                }
                
                async with self.session.get(
                    f"{self.api_base_url}/browse/new-releases",
                    params=params
                ) as response:
                    if response.status != 200:
                        break
                    
                    data = await response.json()
                    album_items = data.get('albums', {}).get('items', [])
                    
                    if not album_items:
                        break
                    
                    for album_data in album_items:
                        if len(albums) >= max_results:
                            break
                        
                        album = self._parse_album_data(album_data)
                        if album:
                            albums.append(album)
                
                offset += limit
                await self.rate_limiter.update_usage(1)
            
            return albums[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to get new releases: {e}")
            return []
    
    def _parse_album_data(self, album_data: dict) -> Optional[SpotifyAlbum]:
        """Parse Spotify album data."""        try:
            return SpotifyAlbum(
                album_id=album_data.get('id', ''),
                name=album_data.get('name', ''),
                album_type=album_data.get('album_type', ''),
                total_tracks=album_data.get('total_tracks', 0),
                available_markets=album_data.get('available_markets', []),
                external_urls=album_data.get('external_urls', {}),
                href=album_data.get('href', ''),
                images=album_data.get('images', []),
                release_date=album_data.get('release_date', ''),
                release_date_precision=album_data.get('release_date_precision', ''),
                restrictions=album_data.get('restrictions'),
                type=album_data.get('type', 'album'),
                uri=album_data.get('uri', ''),
                artists=album_data.get('artists', []),
                tracks=album_data.get('tracks'),
                copyrights=album_data.get('copyrights', []),
                external_ids=album_data.get('external_ids', {}),
                genres=album_data.get('genres', []),
                label=album_data.get('label', ''),
                popularity=album_data.get('popularity', 0)
            )
            
        except Exception as e:
            logger.error(f"Failed to parse album data: {e}")
            return None
    
    async def monitor_artist(
        self,
        artist_id: str,
        check_interval: int = 3600  # 1 hour
    ) -> AsyncGenerator[List[SpotifyAlbum], None]:
        """Monitor artist for new releases."""        seen_albums = set()
        
        while True:
            try:
                # Get artist's albums
                artist_albums = await self.get_artist_albums(artist_id, max_results=10)
                
                # Filter new albums
                new_albums = []
                for album in artist_albums:
                    if album.album_id not in seen_albums:
                        new_albums.append(album)
                        seen_albums.add(album.album_id)
                
                if new_albums:
                    yield new_albums
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Artist monitoring error for {artist_id}: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes on error
    
    async def get_artist_albums(
        self,
        artist_id: str,
        include_groups: str = 'album,single',
        market: str = 'US',
        max_results: int = 50
    ) -> List[SpotifyAlbum]:
        """Get artist's albums."""        try:
            await self.rate_limiter.wait_if_needed()
            await self._ensure_valid_token()
            
            albums = []
            offset = 0
            limit = min(50, max_results)
            
            while len(albums) < max_results:
                params = {
                    'include_groups': include_groups,
                    'market': market,
                    'limit': limit,
                    'offset': offset
                }
                
                async with self.session.get(
                    f"{self.api_base_url}/artists/{artist_id}/albums",
                    params=params
                ) as response:
                    if response.status != 200:
                        break
                    
                    data = await response.json()
                    album_items = data.get('items', [])
                    
                    if not album_items:
                        break
                    
                    for album_data in album_items:
                        if len(albums) >= max_results:
                            break
                        
                        album = self._parse_album_data(album_data)
                        if album:
                            albums.append(album)
                
                offset += limit
                await self.rate_limiter.update_usage(1)
            
            return albums[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to get artist albums: {e}")
            return []
    
    async def _ensure_valid_token(self):
        """Ensure we have a valid access token."""        if not self.access_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            await self._get_access_token()
    
    async def analyze_track_popularity(self, track: SpotifyTrack) -> Dict:
        """Analyze track popularity and metrics."""        try:
            # Get audio features
            audio_features = await self.get_audio_features([track.track_id])
            features = audio_features[0] if audio_features else {}
            
            # Analyze popularity
            popularity_category = "unknown"
            if track.popularity >= 80:
                popularity_category = "viral"
            elif track.popularity >= 60:
                popularity_category = "popular"
            elif track.popularity >= 40:
                popularity_category = "moderate"
            elif track.popularity >= 20:
                popularity_category = "emerging"
            else:
                popularity_category = "niche"
            
            # Artist analysis
            main_artist = track.artists[0] if track.artists else {}
            artist_info = None
            if main_artist.get('id'):
                artist_info = await self.get_artist_info(main_artist['id'])
            
            return {
                'popularity_score': track.popularity,
                'popularity_category': popularity_category,
                'duration_minutes': round(track.duration_ms / 60000, 2),
                'has_preview': bool(track.preview_url),
                'is_explicit': track.explicit,
                'artist_count': len(track.artists),
                'main_artist': main_artist.get('name', ''),
                'artist_popularity': artist_info.popularity if artist_info else 0,
                'artist_followers': artist_info.followers.get('total', 0) if artist_info else 0,
                'album_name': track.album.get('name', ''),
                'release_date': track.album.get('release_date', ''),
                'audio_features': {
                    'danceability': features.get('danceability', 0),
                    'energy': features.get('energy', 0),
                    'valence': features.get('valence', 0),
                    'tempo': features.get('tempo', 0),
                    'acousticness': features.get('acousticness', 0),
                    'instrumentalness': features.get('instrumentalness', 0),
                    'speechiness': features.get('speechiness', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze track popularity: {e}")
            return {}
