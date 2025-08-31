"""Apple Music Crawler
==================

Enterprise-grade Apple Music content crawler with ultra-advanced monitoring capabilities.
Implements Apple Music API integration, intelligent content discovery, and 
real-time music rights protection monitoring with AI-powered analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Features:
- Apple Music API integration with JWT authentication
- Advanced audio fingerprinting and similarity detection
- Real-time music release monitoring and tracking
- AI-powered music classification and genre analysis
- Automated copyright violation detection for music content
- Multi-region content discovery and availability tracking
- Comprehensive music metadata extraction and analysis
"""import asyncio
import json
import re
import jwt
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Union, AsyncGenerator
from urllib.parse import urljoin, urlparse, urlencode, quote
from dataclasses import dataclass, asdict

import aiohttp
import pandas as pd
from pydantic import BaseModel, Field
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
import requests

from ..base_crawler import BaseCrawler
from ..utils.rate_limiter import AppleMusicRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ....core.config import get_settings
from ....core.logging import get_logger
from ....core.exceptions import CrawlerError, RateLimitError, AuthenticationError
from ....models.content import ContentMatch, PlatformContent
from ....utils.rate_limiter import RateLimiter
from ....security.encryption import encrypt_sensitive_data
from ....ai.content_protection.fingerprinting.audio_fingerprint import AudioFingerprinter

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class AppleMusicTrack:
    """Enhanced Apple Music track data structure with fingerprinting."""    track_id: str
    name: str
    artist_name: str
    artist_id: str
    album_name: str
    album_id: str
    duration_ms: int
    explicit: bool
    genre: str
    release_date: datetime
    preview_url: Optional[str]
    artwork_url: str
    isrc: Optional[str]
    upc: Optional[str]
    copyright_info: str
    label: str
    track_number: int
    disc_number: int
    popularity: Optional[int]
    # Rights and licensing
    rights_holder: Optional[str] = None
    publishing_info: Optional[Dict] = None
    mechanical_rights: Optional[Dict] = None
    sync_rights: Optional[Dict] = None
    # Audio analysis
    audio_fingerprint: Optional[str] = None
    spectral_hash: Optional[str] = None
    bpm: Optional[int] = None
    key: Optional[str] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None
    valence: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    loudness: Optional[float] = None
    # Copyright protection
    similarity_matches: List[Dict] = None
    copyright_violations: List[Dict] = None
    protection_status: Optional[str] = None
    monitoring_enabled: bool = False

@dataclass
class AppleMusicArtist:
    """Apple Music artist data structure."""    artist_id: str
    name: str
    biography: Optional[str]
    genres: List[str]
    origin: Optional[str]
    website_url: Optional[str]
    social_links: Dict[str, str]
    artwork_url: str
    # Career information
    career_start: Optional[datetime] = None
    label: Optional[str] = None
    related_artists: List[str] = None
    # Analytics
    monthly_listeners: Optional[int] = None
    top_tracks: List[str] = None
    latest_release: Optional[str] = None
    total_albums: Optional[int] = None
    total_tracks: Optional[int] = None
    # Rights information
    management_contact: Optional[str] = None
    booking_contact: Optional[str] = None
    publishing_company: Optional[str] = None

@dataclass
class AppleMusicAlbum:
    """Apple Music album data structure."""    album_id: str
    name: str
    artist_name: str
    artist_id: str
    release_date: datetime
    track_count: int
    genre: str
    label: str
    copyright_info: str
    upc: Optional[str]
    artwork_url: str
    # Album details
    album_type: str  # album, single, ep, compilation
    explicit: bool
    # Rights and licensing
    rights_holder: Optional[str] = None
    distribution_info: Optional[Dict] = None
    # Analytics
    total_duration: Optional[int] = None
    popularity_score: Optional[float] = None
    chart_positions: Optional[Dict] = None
    editorial_notes: Optional[str] = None
    content_rating: Optional[str] = None
    available_countries: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AppleMusicArtist(BaseModel):
    """Apple Music Artist data model"""    artist_id: str
    name: str
    url: str
    artwork: Optional[Dict[str, str]] = None
    genres: List[str] = Field(default_factory=list)
    origin: Optional[str] = None
    biography: Optional[str] = None
    born: Optional[str] = None
    formed: Optional[str] = None
    influences: List[str] = Field(default_factory=list)
    similar_artists: List[str] = Field(default_factory=list)
    album_count: int = 0
    single_count: int = 0
    music_video_count: int = 0


class AppleMusicAlbum(BaseModel):
    """Apple Music Album data model"""    album_id: str
    name: str
    artist_name: str
    artist_id: Optional[str] = None
    artwork_url: Optional[str] = None
    release_date: Optional[datetime] = None
    track_count: int = 0
    genres: List[str] = Field(default_factory=list)
    record_label: Optional[str] = None
    copyright: Optional[str] = None
    editorial_notes: Optional[str] = None
    is_single: bool = False
    is_compilation: bool = False
    is_complete: bool = True
    content_rating: Optional[str] = None
    url: str
    upc: Optional[str] = None


class AppleMusicPlaylist(BaseModel):
    """Apple Music Playlist data model"""    playlist_id: str
    name: str
    description: Optional[str] = None
    artwork_url: Optional[str] = None
    curator_name: Optional[str] = None
    track_count: int = 0
    last_modified: Optional[datetime] = None
    is_public: bool = True
    play_params: Optional[Dict] = None
    url: str


class AppleMusicCrawler(BaseCrawler):
    """    Advanced Apple Music crawler for comprehensive music content monitoring
    
    Features:
    - Music track analysis with advanced metadata extraction
    - Artist profile monitoring and analytics
    - Album release tracking and analysis
    - Playlist monitoring and curation insights
    - Copyright infringement detection with ISRC matching
    - Music trend analysis and chart tracking
    - Editorial content and review monitoring
    - Integration with Apple Music API and MusicKit
    """    
    def __init__(self):
        super().__init__()
        self.platform = "apple_music"
        self.base_url = "https://music.apple.com"
        self.api_base = "https://api.music.apple.com/v1"
        self.rate_limiter = RateLimiter(
            requests_per_minute=120,  # Apple Music API rate limit
            requests_per_hour=3000
        )
        self.session_headers = {
            'User-Agent': 'IA-Influencer-Agent/2.0 (Music Protection)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.storefront = "us"  # Default storefront
        
    async def authenticate(self, developer_token: str, music_user_token: str = None) -> bool:
        """Authenticate with Apple Music API using developer token"""        try:
            self.session_headers['Authorization'] = f'Bearer {developer_token}'
            if music_user_token:
                self.session_headers['Music-User-Token'] = music_user_token
            
            # Test API access with a simple request
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(f"{self.api_base}/storefronts") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Apple Music API access confirmed. Available storefronts: {len(data.get('data', []))}")
                        return True
                    else:
                        logger.error(f"Apple Music authentication failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Apple Music authentication error: {str(e)}")
            return False
    
    async def set_storefront(self, storefront: str):
        """Set the storefront for API requests"""        self.storefront = storefront
        logger.info(f"Storefront set to: {storefront}")
    
    async def search_catalog(
        self,
        query: str,
        types: List[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, List[Dict]]:
        """        Search Apple Music catalog
        
        Args:
            query: Search query
            types: Types to search (songs, albums, artists, playlists, music-videos)
            limit: Maximum results per type
            offset: Results offset
            
        Returns:
            Dictionary with results by type
        """        await self.rate_limiter.wait()
        
        if types is None:
            types = ["songs", "albums", "artists"]
        
        try:
            search_params = {
                'term': query,
                'types': ','.join(types),
                'limit': min(limit, 25),  # Apple Music API limit per type
                'offset': offset
            }
            
            endpoint = f"{self.api_base}/catalog/{self.storefront}/search"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('results', {})
                        
                        total_found = sum(len(results.get(t, {}).get('data', [])) for t in types)
                        logger.info(f"Found {total_found} items for query: {query}")
                        
                        return results
                    else:
                        logger.error(f"Apple Music search failed: {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Apple Music search error: {str(e)}")
            return {}
    
    async def get_song_details(self, song_id: str) -> Optional[AppleMusicTrack]:
        """Get detailed information about a specific song"""        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/catalog/{self.storefront}/songs/{song_id}"
            params = {
                'include': 'artists,albums'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        song_data = data.get('data', [{}])[0]
                        
                        return await self._parse_track_data(song_data)
                    else:
                        logger.error(f"Failed to get song details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting song details: {str(e)}")
            return None
    
    async def get_artist_details(self, artist_id: str) -> Optional[AppleMusicArtist]:
        """Get detailed information about a specific artist"""        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/catalog/{self.storefront}/artists/{artist_id}"
            params = {
                'include': 'albums,singles'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        artist_data = data.get('data', [{}])[0]
                        
                        return await self._parse_artist_data(artist_data)
                    else:
                        logger.error(f"Failed to get artist details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting artist details: {str(e)}")
            return None
    
    async def get_album_details(self, album_id: str) -> Optional[AppleMusicAlbum]:
        """Get detailed information about a specific album"""        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/catalog/{self.storefront}/albums/{album_id}"
            params = {
                'include': 'artists,tracks'
            }
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        album_data = data.get('data', [{}])[0]
                        
                        return await self._parse_album_data(album_data)
                    else:
                        logger.error(f"Failed to get album details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting album details: {str(e)}")
            return None
    
    async def get_album_tracks(self, album_id: str) -> List[AppleMusicTrack]:
        """Get all tracks from a specific album"""        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/catalog/{self.storefront}/albums/{album_id}/tracks"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        tracks = []
                        
                        for track_data in data.get('data', []):
                            track = await self._parse_track_data(track_data)
                            if track:
                                tracks.append(track)
                        
                        logger.info(f"Retrieved {len(tracks)} tracks from album {album_id}")
                        return tracks
                    else:
                        logger.error(f"Failed to get album tracks: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting album tracks: {str(e)}")
            return []
    
    async def get_charts(
        self,
        chart_type: str = "songs",
        genre: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """        Get Apple Music charts
        
        Args:
            chart_type: Type of chart (songs, albums, playlists)
            genre: Specific genre filter
            limit: Maximum results to return
            
        Returns:
            List of chart items
        """        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/catalog/{self.storefront}/charts"
            params = {
                'types': chart_type,
                'limit': min(limit, 50)
            }
            
            if genre:
                params['genre'] = genre
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        chart_data = data.get('results', {}).get(chart_type, [])
                        
                        if chart_data:
                            chart_items = chart_data[0].get('data', [])
                            logger.info(f"Retrieved {len(chart_items)} {chart_type} from charts")
                            return chart_items
                        else:
                            return []
                    else:
                        logger.error(f"Failed to get charts: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting charts: {str(e)}")
            return []
    
    async def get_curated_playlists(
        self,
        category: str = None,
        limit: int = 50
    ) -> List[AppleMusicPlaylist]:
        """Get curated playlists from Apple Music"""        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/catalog/{self.storefront}/playlists"
            params = {
                'limit': min(limit, 50)
            }
            
            if category:
                # This would require the specific category endpoint
                endpoint = f"{self.api_base}/catalog/{self.storefront}/genres/{category}/playlists"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        playlists = []
                        
                        for playlist_data in data.get('data', []):
                            playlist = await self._parse_playlist_data(playlist_data)
                            if playlist:
                                playlists.append(playlist)
                        
                        logger.info(f"Retrieved {len(playlists)} curated playlists")
                        return playlists
                    else:
                        logger.error(f"Failed to get curated playlists: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting curated playlists: {str(e)}")
            return []
    
    async def monitor_content_infringement(
        self,
        protected_content: Dict,
        similarity_threshold: float = 0.8
    ) -> List[ContentMatch]:
        """        Monitor Apple Music for potential copyright infringement
        
        Args:
            protected_content: Content to protect
            similarity_threshold: Minimum similarity for match detection
            
        Returns:
            List of potential copyright matches
        """        matches = []
        
        try:
            # Generate search queries from protected content
            search_queries = self._generate_search_queries(protected_content)
            
            for query in search_queries:
                results = await self.search_catalog(query, ["songs"], limit=50)
                
                for song_data in results.get('songs', {}).get('data', []):
                    track = await self._parse_track_data(song_data)
                    if track:
                        similarity_score = await self._calculate_content_similarity(
                            protected_content, track
                        )
                        
                        if similarity_score >= similarity_threshold:
                            match = ContentMatch(
                                platform="apple_music",
                                content_id=track.track_id,
                                url=track.url,
                                title=track.name,
                                description=f"{track.artist_name} - {track.album_name}",
                                creator=track.artist_name,
                                similarity_score=similarity_score,
                                detection_date=datetime.utcnow(),
                                content_type="song",
                                metadata={
                                    'artist_id': track.artist_id,
                                    'album_id': track.album_id,
                                    'duration_ms': track.duration_ms,
                                    'isrc': track.isrc,
                                    'genres': track.genres,
                                    'explicit': track.explicit
                                }
                            )
                            matches.append(match)
            
            logger.info(f"Found {len(matches)} potential copyright matches on Apple Music")
            return matches
            
        except Exception as e:
            logger.error(f"Error monitoring Apple Music content infringement: {str(e)}")
            return []
    
    async def analyze_artist_performance(self, artist_id: str) -> Dict[str, Any]:
        """        Analyze artist performance on Apple Music
        
        Args:
            artist_id: Apple Music artist ID
            
        Returns:
            Comprehensive artist performance analysis
        """        try:
            artist = await self.get_artist_details(artist_id)
            if not artist:
                return {}
            
            # Get artist's albums and songs
            albums_search = await self.search_catalog(artist.name, ["albums"], limit=50)
            songs_search = await self.search_catalog(artist.name, ["songs"], limit=100)
            
            albums = albums_search.get('albums', {}).get('data', [])
            songs = songs_search.get('songs', {}).get('data', [])
            
            # Calculate performance metrics
            total_tracks = len(songs)
            avg_track_duration = sum(song.get('attributes', {}).get('durationInMillis', 0) for song in songs) / max(total_tracks, 1)
            
            performance_analysis = {
                'artist_id': artist.artist_id,
                'artist_name': artist.name,
                'catalog_metrics': {
                    'album_count': len(albums),
                    'song_count': total_tracks,
                    'music_video_count': artist.music_video_count
                },
                'content_analysis': {
                    'avg_track_duration_ms': avg_track_duration,
                    'avg_track_duration_minutes': avg_track_duration / 60000,
                    'genre_diversity': len(artist.genres),
                    'primary_genres': artist.genres[:3]
                },
                'release_pattern': await self._analyze_release_pattern(albums),
                'content_rating_analysis': await self._analyze_content_ratings(songs),
                'market_presence': {
                    'genres_covered': artist.genres,
                    'recent_activity': await self._analyze_recent_activity(albums, songs)
                }
            }
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing artist performance: {str(e)}")
            return {}
    
    async def analyze_music_trends(
        self,
        time_period: str = "current",
        genres: List[str] = None,
        chart_types: List[str] = None
    ) -> Dict[str, Any]:
        """        Analyze music trends on Apple Music
        
        Args:
            time_period: Time period for analysis
            genres: Specific genres to analyze
            chart_types: Types of charts to analyze
            
        Returns:
            Comprehensive trend analysis
        """        try:
            if chart_types is None:
                chart_types = ["songs", "albums"]
            
            trends_data = {}
            
            for chart_type in chart_types:
                chart_data = await self.get_charts(chart_type, limit=100)
                trends_data[f"{chart_type}_trends"] = await self._analyze_chart_trends(chart_data, chart_type)
            
            # Overall trend analysis
            overall_trends = {
                'trending_genres': await self._get_trending_genres(trends_data),
                'duration_trends': await self._analyze_duration_trends(trends_data.get('songs_trends', [])),
                'release_patterns': await self._analyze_release_patterns(trends_data),
                'content_rating_trends': await self._analyze_content_rating_trends(trends_data),
                'artist_diversity': await self._calculate_artist_diversity(trends_data),
                'market_insights': {
                    'dominant_labels': await self._identify_dominant_labels(trends_data),
                    'emerging_artists': await self._identify_emerging_artists(trends_data),
                    'genre_crossover': await self._analyze_genre_crossover(trends_data)
                }
            }
            
            trends_data['overall_analysis'] = overall_trends
            
            return trends_data
            
        except Exception as e:
            logger.error(f"Error analyzing music trends: {str(e)}")
            return {}
    
    async def bulk_song_analysis(self, song_ids: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple songs in bulk for efficiency"""        results = []
        
        # Process songs in batches to respect rate limits
        batch_size = 20
        for i in range(0, len(song_ids), batch_size):
            batch = song_ids[i:i + batch_size]
            
            # Use batch API endpoint if available
            try:
                endpoint = f"{self.api_base}/catalog/{self.storefront}/songs"
                params = {
                    'ids': ','.join(batch),
                    'include': 'artists,albums'
                }
                
                async with aiohttp.ClientSession(headers=self.session_headers) as session:
                    async with session.get(endpoint, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for song_data in data.get('data', []):
                                track = await self._parse_track_data(song_data)
                                if track:
                                    analysis = await self._analyze_track_performance(track)
                                    results.append(analysis)
                        else:
                            logger.error(f"Batch request failed: {response.status}")
                            
            except Exception as e:
                logger.error(f"Error in bulk analysis: {str(e)}")
            
            # Rate limiting between batches
            await asyncio.sleep(1)
        
        return results
    
    async def _parse_track_data(self, track_data: Dict) -> Optional[AppleMusicTrack]:
        """Parse Apple Music API track data into AppleMusicTrack model"""        try:
            attributes = track_data.get('attributes', {})
            relationships = track_data.get('relationships', {})
            
            # Extract artist information
            artist_name = attributes.get('artistName', '')
            artist_id = None
            if 'artists' in relationships:
                artists_data = relationships['artists'].get('data', [])
                if artists_data:
                    artist_id = artists_data[0].get('id')
            
            # Extract album information
            album_name = attributes.get('albumName', '')
            album_id = None
            if 'albums' in relationships:
                albums_data = relationships['albums'].get('data', [])
                if albums_data:
                    album_id = albums_data[0].get('id')
            
            # Parse artwork URL
            artwork = attributes.get('artwork', {})
            artwork_url = None
            if artwork:
                artwork_url = artwork.get('url', '').replace('{w}', '1000').replace('{h}', '1000')
            
            # Parse release date
            release_date = None
            if attributes.get('releaseDate'):
                try:
                    release_date = datetime.fromisoformat(attributes['releaseDate'])
                except:
                    pass
            
            track = AppleMusicTrack(
                track_id=track_data.get('id', ''),
                name=attributes.get('name', ''),
                artist_name=artist_name,
                artist_id=artist_id,
                album_name=album_name,
                album_id=album_id,
                duration_ms=attributes.get('durationInMillis', 0),
                release_date=release_date,
                track_number=attributes.get('trackNumber'),
                disc_number=attributes.get('discNumber'),
                explicit=attributes.get('contentRating') == 'explicit',
                preview_url=attributes.get('previews', [{}])[0].get('url') if attributes.get('previews') else None,
                artwork_url=artwork_url,
                url=attributes.get('url', ''),
                isrc=attributes.get('isrc'),
                genres=attributes.get('genreNames', []),
                composer_name=attributes.get('composerName'),
                copyright=attributes.get('copyright'),
                playback_params=attributes.get('playParams'),
                editorial_notes=attributes.get('editorialNotes', {}).get('standard'),
                content_rating=attributes.get('contentRating'),
                metadata={
                    'has_lyrics': attributes.get('hasLyrics', False),
                    'has_credits': attributes.get('hasCredits', False),
                    'movement_count': attributes.get('movementCount'),
                    'movement_name': attributes.get('movementName'),
                    'movement_number': attributes.get('movementNumber'),
                    'work_name': attributes.get('workName')
                }
            )
            
            return track
            
        except Exception as e:
            logger.error(f"Error parsing track data: {str(e)}")
            return None
    
    async def _parse_artist_data(self, artist_data: Dict) -> Optional[AppleMusicArtist]:
        """Parse Apple Music API artist data into AppleMusicArtist model"""        try:
            attributes = artist_data.get('attributes', {})
            
            # Parse artwork
            artwork = attributes.get('artwork')
            
            # Parse editorial notes for biography
            editorial_notes = attributes.get('editorialNotes', {})
            biography = editorial_notes.get('standard', '') or editorial_notes.get('short', '')
            
            artist = AppleMusicArtist(
                artist_id=artist_data.get('id', ''),
                name=attributes.get('name', ''),
                url=attributes.get('url', ''),
                artwork=artwork,
                genres=attributes.get('genreNames', []),
                origin=attributes.get('origin'),
                biography=biography,
                born=attributes.get('bornOrFormed'),
                metadata={
                    'editorial_artwork': editorial_notes.get('artwork'),
                    'has_editorial_notes': bool(editorial_notes)
                }
            )
            
            return artist
            
        except Exception as e:
            logger.error(f"Error parsing artist data: {str(e)}")
            return None
    
    async def _parse_album_data(self, album_data: Dict) -> Optional[AppleMusicAlbum]:
        """Parse Apple Music API album data into AppleMusicAlbum model"""        try:
            attributes = album_data.get('attributes', {})
            
            # Parse artwork URL
            artwork = attributes.get('artwork', {})
            artwork_url = None
            if artwork:
                artwork_url = artwork.get('url', '').replace('{w}', '1000').replace('{h}', '1000')
            
            # Parse release date
            release_date = None
            if attributes.get('releaseDate'):
                try:
                    release_date = datetime.fromisoformat(attributes['releaseDate'])
                except:
                    pass
            
            album = AppleMusicAlbum(
                album_id=album_data.get('id', ''),
                name=attributes.get('name', ''),
                artist_name=attributes.get('artistName', ''),
                artwork_url=artwork_url,
                release_date=release_date,
                track_count=attributes.get('trackCount', 0),
                genres=attributes.get('genreNames', []),
                record_label=attributes.get('recordLabel'),
                copyright=attributes.get('copyright'),
                editorial_notes=attributes.get('editorialNotes', {}).get('standard'),
                is_single=attributes.get('isSingle', False),
                is_compilation=attributes.get('isCompilation', False),
                is_complete=attributes.get('isComplete', True),
                content_rating=attributes.get('contentRating'),
                url=attributes.get('url', ''),
                upc=attributes.get('upc')
            )
            
            return album
            
        except Exception as e:
            logger.error(f"Error parsing album data: {str(e)}")
            return None
    
    async def _parse_playlist_data(self, playlist_data: Dict) -> Optional[AppleMusicPlaylist]:
        """Parse Apple Music API playlist data into AppleMusicPlaylist model"""        try:
            attributes = playlist_data.get('attributes', {})
            
            # Parse artwork URL
            artwork = attributes.get('artwork', {})
            artwork_url = None
            if artwork:
                artwork_url = artwork.get('url', '').replace('{w}', '1000').replace('{h}', '1000')
            
            # Parse last modified date
            last_modified = None
            if attributes.get('lastModifiedDate'):
                try:
                    last_modified = datetime.fromisoformat(attributes['lastModifiedDate'].replace('Z', '+00:00'))
                except:
                    pass
            
            playlist = AppleMusicPlaylist(
                playlist_id=playlist_data.get('id', ''),
                name=attributes.get('name', ''),
                description=attributes.get('description', {}).get('standard'),
                artwork_url=artwork_url,
                curator_name=attributes.get('curatorName'),
                track_count=attributes.get('trackCount', 0),
                last_modified=last_modified,
                is_public=not attributes.get('isPrivate', False),
                play_params=attributes.get('playParams'),
                url=attributes.get('url', '')
            )
            
            return playlist
            
        except Exception as e:
            logger.error(f"Error parsing playlist data: {str(e)}")
            return None
    
    def _generate_search_queries(self, protected_content: Dict) -> List[str]:
        """Generate search queries for content protection"""        queries = []
        
        if 'title' in protected_content:
            queries.append(protected_content['title'])
        
        if 'artist' in protected_content:
            queries.append(protected_content['artist'])
            if 'title' in protected_content:
                queries.append(f"{protected_content['artist']} {protected_content['title']}")
        
        if 'album' in protected_content:
            queries.append(protected_content['album'])
        
        if 'isrc' in protected_content:
            queries.append(protected_content['isrc'])
        
        return queries[:5]
    
    async def _calculate_content_similarity(
        self,
        protected_content: Dict,
        track: AppleMusicTrack
    ) -> float:
        """Calculate similarity between protected content and Apple Music track"""        from difflib import SequenceMatcher
        
        similarity_scores = []
        
        # Title similarity
        if 'title' in protected_content and track.name:
            title_similarity = SequenceMatcher(
                None,
                protected_content['title'].lower(),
                track.name.lower()
            ).ratio()
            similarity_scores.append(title_similarity * 0.5)
        
        # Artist similarity
        if 'artist' in protected_content and track.artist_name:
            artist_similarity = SequenceMatcher(
                None,
                protected_content['artist'].lower(),
                track.artist_name.lower()
            ).ratio()
            similarity_scores.append(artist_similarity * 0.3)
        
        # ISRC exact match
        if 'isrc' in protected_content and track.isrc:
            if protected_content['isrc'] == track.isrc:
                return 1.0  # Perfect match for ISRC
        
        # Duration similarity (within 5 seconds)
        if 'duration_ms' in protected_content and track.duration_ms:
            duration_diff = abs(protected_content['duration_ms'] - track.duration_ms)
            if duration_diff <= 5000:  # 5 seconds in milliseconds
                duration_similarity = 1.0 - (duration_diff / 30000)  # Normalize by 30 seconds
                similarity_scores.append(duration_similarity * 0.2)
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    async def _analyze_release_pattern(self, albums: List[Dict]) -> Dict[str, Any]:
        """Analyze artist's release pattern"""        if not albums:
            return {}
        
        release_dates = []
        for album in albums:
            release_date_str = album.get('attributes', {}).get('releaseDate')
            if release_date_str:
                try:
                    release_date = datetime.fromisoformat(release_date_str)
                    release_dates.append(release_date)
                except:
                    continue
        
        if len(release_dates) < 2:
            return {'pattern': 'insufficient_data'}
        
        release_dates.sort()
        intervals = [(release_dates[i+1] - release_dates[i]).days for i in range(len(release_dates)-1)]
        avg_interval = sum(intervals) / len(intervals)
        
        return {
            'total_releases': len(albums),
            'avg_interval_days': avg_interval,
            'release_frequency': 'frequent' if avg_interval < 365 else 'moderate' if avg_interval < 730 else 'sporadic',
            'latest_release': max(release_dates).isoformat() if release_dates else None
        }
    
    async def _analyze_content_ratings(self, songs: List[Dict]) -> Dict[str, Any]:
        """Analyze content ratings distribution"""        ratings = {}
        for song in songs:
            rating = song.get('attributes', {}).get('contentRating', 'clean')
            ratings[rating] = ratings.get(rating, 0) + 1
        
        total = sum(ratings.values())
        return {
            'distribution': ratings,
            'explicit_percentage': (ratings.get('explicit', 0) / max(total, 1)) * 100,
            'total_songs': total
        }
    
    async def _analyze_recent_activity(self, albums: List[Dict], songs: List[Dict]) -> Dict[str, Any]:
        """Analyze recent activity"""        recent_threshold = datetime.now() - timedelta(days=365)
        
        recent_albums = 0
        for album in albums:
            release_date_str = album.get('attributes', {}).get('releaseDate')
            if release_date_str:
                try:
                    release_date = datetime.fromisoformat(release_date_str)
                    if release_date > recent_threshold:
                        recent_albums += 1
                except:
                    continue
        
        return {
            'recent_albums_count': recent_albums,
            'activity_level': 'high' if recent_albums > 2 else 'medium' if recent_albums > 0 else 'low'
        }
    
    async def _analyze_chart_trends(self, chart_data: List[Dict], chart_type: str) -> List[Dict]:
        """Analyze trends from chart data"""        trends = []
        
        for item in chart_data[:20]:  # Top 20 items
            attributes = item.get('attributes', {})
            
            trend_item = {
                'name': attributes.get('name', ''),
                'artist': attributes.get('artistName', ''),
                'position': len(trends) + 1,  # Chart position
                'genres': attributes.get('genreNames', []),
                'release_date': attributes.get('releaseDate'),
                'content_rating': attributes.get('contentRating', 'clean')
            }
            
            if chart_type == 'songs':
                trend_item['duration_ms'] = attributes.get('durationInMillis', 0)
                trend_item['album'] = attributes.get('albumName', '')
            
            trends.append(trend_item)
        
        return trends
    
    async def _get_trending_genres(self, trends_data: Dict) -> List[str]:
        """Extract trending genres from trend data"""        genre_counts = {}
        
        for trend_type, trends in trends_data.items():
            if isinstance(trends, list):
                for item in trends:
                    for genre in item.get('genres', []):
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        return sorted(genre_counts.keys(), key=genre_counts.get, reverse=True)[:10]
    
    async def _analyze_duration_trends(self, songs_trends: List[Dict]) -> Dict[str, Any]:
        """Analyze duration trends from songs"""        if not songs_trends:
            return {}
        
        durations = [item.get('duration_ms', 0) for item in songs_trends if item.get('duration_ms')]
        
        if not durations:
            return {}
        
        avg_duration = sum(durations) / len(durations)
        short_songs = len([d for d in durations if d < 180000])  # < 3 minutes
        medium_songs = len([d for d in durations if 180000 <= d <= 300000])  # 3-5 minutes
        long_songs = len([d for d in durations if d > 300000])  # > 5 minutes
        
        return {
            'avg_duration_ms': avg_duration,
            'avg_duration_minutes': avg_duration / 60000,
            'short_songs_percentage': (short_songs / len(durations)) * 100,
            'medium_songs_percentage': (medium_songs / len(durations)) * 100,
            'long_songs_percentage': (long_songs / len(durations)) * 100
        }
    
    async def _analyze_release_patterns(self, trends_data: Dict) -> Dict[str, Any]:
        """Analyze release patterns from trends"""        current_year = datetime.now().year
        year_counts = {}
        
        for trend_type, trends in trends_data.items():
            if isinstance(trends, list):
                for item in trends:
                    release_date_str = item.get('release_date')
                    if release_date_str:
                        try:
                            year = datetime.fromisoformat(release_date_str).year
                            year_counts[year] = year_counts.get(year, 0) + 1
                        except:
                            continue
        
        return {
            'releases_by_year': year_counts,
            'current_year_releases': year_counts.get(current_year, 0),
            'trend': 'increasing' if year_counts.get(current_year, 0) > year_counts.get(current_year-1, 0) else 'stable'
        }
    
    async def _analyze_content_rating_trends(self, trends_data: Dict) -> Dict[str, Any]:
        """Analyze content rating trends"""        rating_counts = {}
        
        for trend_type, trends in trends_data.items():
            if isinstance(trends, list):
                for item in trends:
                    rating = item.get('content_rating', 'clean')
                    rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        total = sum(rating_counts.values())
        return {
            'distribution': rating_counts,
            'explicit_percentage': (rating_counts.get('explicit', 0) / max(total, 1)) * 100,
            'clean_percentage': (rating_counts.get('clean', 0) / max(total, 1)) * 100
        }
    
    async def _calculate_artist_diversity(self, trends_data: Dict) -> int:
        """Calculate artist diversity in trends"""        unique_artists = set()
        
        for trend_type, trends in trends_data.items():
            if isinstance(trends, list):
                for item in trends:
                    artist = item.get('artist')
                    if artist:
                        unique_artists.add(artist.lower())
        
        return len(unique_artists)
    
    async def _identify_dominant_labels(self, trends_data: Dict) -> List[str]:
        """Identify dominant record labels (would need additional API calls)"""        # This would require fetching album details for label information
        return ["Universal Music Group", "Sony Music", "Warner Music Group"]  # Placeholder
    
    async def _identify_emerging_artists(self, trends_data: Dict) -> List[str]:
        """Identify emerging artists from trends"""        artist_positions = {}
        
        for trend_type, trends in trends_data.items():
            if isinstance(trends, list):
                for item in trends:
                    artist = item.get('artist')
                    position = item.get('position', 999)
                    if artist and position <= 50:  # Top 50 positions
                        if artist not in artist_positions or position < artist_positions[artist]:
                            artist_positions[artist] = position
        
        # Sort by chart position and return top emerging (assuming lower positions are new entries)
        emerging = sorted(artist_positions.items(), key=lambda x: x[1])
        return [artist for artist, pos in emerging[20:30]]  # Artists in positions 20-30
    
    async def _analyze_genre_crossover(self, trends_data: Dict) -> Dict[str, int]:
        """Analyze genre crossover patterns"""        genre_combinations = {}
        
        for trend_type, trends in trends_data.items():
            if isinstance(trends, list):
                for item in trends:
                    genres = item.get('genres', [])
                    if len(genres) > 1:
                        combo = '+'.join(sorted(genres[:2]))  # Take first 2 genres
                        genre_combinations[combo] = genre_combinations.get(combo, 0) + 1
        
        return dict(sorted(genre_combinations.items(), key=lambda x: x[1], reverse=True)[:10])
    
    async def _analyze_track_performance(self, track: AppleMusicTrack) -> Dict[str, Any]:
        """Analyze individual track performance metrics"""        return {
            'track_id': track.track_id,
            'name': track.name,
            'artist': track.artist_name,
            'album': track.album_name,
            'duration_category': self._categorize_duration(track.duration_ms),
            'genre_count': len(track.genres),
            'primary_genre': track.genres[0] if track.genres else 'Unknown',
            'explicit_content': track.explicit,
            'has_preview': track.preview_url is not None,
            'release_year': track.release_date.year if track.release_date else None,
            'metadata_completeness': self._assess_metadata_completeness(track)
        }
    
    def _categorize_duration(self, duration_ms: int) -> str:
        """Categorize track duration"""        duration_seconds = duration_ms / 1000
        
        if duration_seconds < 120:
            return "very_short"
        elif duration_seconds < 180:
            return "short"
        elif duration_seconds < 300:
            return "medium"
        elif duration_seconds < 420:
            return "long"
        else:
            return "extended"
    
    def _assess_metadata_completeness(self, track: AppleMusicTrack) -> float:
        """Assess completeness of track metadata"""        fields = [
            track.name, track.artist_name, track.album_name,
            track.duration_ms, track.genres, track.isrc,
            track.release_date, track.composer_name
        ]
        
        complete_fields = sum(1 for field in fields if field)
        return complete_fields / len(fields)
