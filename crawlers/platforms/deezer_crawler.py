"""
Deezer Music Crawler
Advanced industrial-grade Deezer crawler for music content protection and analytics
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 - All rights reserved
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from urllib.parse import urljoin, urlparse

import aiohttp
import pandas as pd
from pydantic import BaseModel, Field

from ..base_crawler import BaseCrawler
from ....core.config import get_settings
from ....core.logging import get_logger
from ....models.content import ContentMatch, PlatformContent
from ....utils.rate_limiter import RateLimiter
from ....security.encryption import encrypt_sensitive_data

logger = get_logger(__name__)
settings = get_settings()


class DeezerTrack(BaseModel):
    """Deezer Track data model"""
    track_id: str
    title: str
    artist_name: str
    artist_id: str
    album_title: str
    album_id: str
    duration: int  # in seconds
    release_date: Optional[datetime] = None
    track_position: Optional[int] = None
    disk_number: Optional[int] = None
    explicit_lyrics: bool = False
    preview_url: Optional[str] = None
    track_url: str
    bpm: Optional[float] = None
    gain: Optional[float] = None
    genre: Optional[str] = None
    contributors: List[Dict[str, str]] = Field(default_factory=list)
    isrc: Optional[str] = None
    rank: int = 0
    available: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DeezerArtist(BaseModel):
    """Deezer Artist data model"""
    artist_id: str
    name: str
    link: str
    picture_url: Optional[str] = None
    picture_small: Optional[str] = None
    picture_medium: Optional[str] = None
    picture_big: Optional[str] = None
    picture_xl: Optional[str] = None
    nb_album: int = 0
    nb_fan: int = 0
    radio: bool = False
    tracklist: Optional[str] = None
    type: str = "artist"


class DeezerAlbum(BaseModel):
    """Deezer Album data model"""
    album_id: str
    title: str
    artist_name: str
    artist_id: str
    cover_url: Optional[str] = None
    cover_small: Optional[str] = None
    cover_medium: Optional[str] = None
    cover_big: Optional[str] = None
    cover_xl: Optional[str] = None
    genre_id: Optional[int] = None
    genre_name: Optional[str] = None
    nb_tracks: int = 0
    duration: int = 0
    fans: int = 0
    rating: int = 0
    release_date: Optional[datetime] = None
    record_type: str = "album"  # album, single, ep
    available: bool = True
    alternative: Optional[str] = None
    tracklist: Optional[str] = None
    explicit_lyrics: bool = False
    label: Optional[str] = None
    upc: Optional[str] = None


class DeezerPlaylist(BaseModel):
    """Deezer Playlist data model"""
    playlist_id: str
    title: str
    description: Optional[str] = None
    duration: int = 0
    public: bool = True
    is_loved_track: bool = False
    collaborative: bool = False
    nb_tracks: int = 0
    fans: int = 0
    link: str
    picture_url: Optional[str] = None
    picture_small: Optional[str] = None
    picture_medium: Optional[str] = None
    picture_big: Optional[str] = None
    picture_xl: Optional[str] = None
    checksum: Optional[str] = None
    creator_name: str
    creator_id: str
    creation_date: Optional[datetime] = None


class DeezerCrawler(BaseCrawler):
    """
    Advanced Deezer crawler for comprehensive music content monitoring
    
    Features:
    - Music track analysis with audio fingerprinting
    - Artist profile monitoring and analytics
    - Album release tracking
    - Playlist monitoring and curation analysis
    - Copyright infringement detection
    - Music trend analysis and recommendation
    - Chart tracking and popularity metrics
    - Advanced audio analysis integration
    """
    
    def __init__(self):
        super().__init__()
        self.platform = "deezer"
        self.base_url = "https://www.deezer.com"
        self.api_base = "https://api.deezer.com"
        self.rate_limiter = RateLimiter(
            requests_per_minute=50,  # Deezer's rate limit
            requests_per_hour=1000
        )
        self.session_headers = {
            'User-Agent': 'IA-Influencer-Agent/2.0 (Music Protection)',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
    async def authenticate(self, access_token: str) -> bool:
        """Authenticate with Deezer API (if available)"""
        try:
            # Note: Deezer API is mostly public, OAuth for user-specific data
            if access_token:
                self.session_headers['Authorization'] = f'Bearer {access_token}'
            
            # Test API access
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(f"{self.api_base}/infos") as response:
                    if response.status == 200:
                        logger.info("Deezer API access confirmed")
                        return True
                    else:
                        logger.error(f"Deezer API access failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Deezer authentication error: {str(e)}")
            return False
    
    async def search_tracks(
        self,
        query: str,
        limit: int = 100,
        strict: bool = False
    ) -> List[Dict]:
        """
        Search Deezer tracks
        
        Args:
            query: Search query
            limit: Maximum results to return
            strict: Enable strict search mode
            
        Returns:
            List of matching tracks
        """
        await self.rate_limiter.wait()
        
        try:
            search_params = {
                'q': query,
                'limit': min(limit, 100),  # Deezer API limit
                'strict': 'on' if strict else 'off'
            }
            
            endpoint = f"{self.api_base}/search"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        tracks = data.get('data', [])
                        
                        logger.info(f"Found {len(tracks)} tracks for query: {query}")
                        return tracks
                    else:
                        logger.error(f"Deezer track search failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Deezer track search error: {str(e)}")
            return []
    
    async def search_artists(self, query: str, limit: int = 50) -> List[Dict]:
        """Search Deezer artists"""
        await self.rate_limiter.wait()
        
        try:
            search_params = {
                'q': query,
                'limit': min(limit, 100)
            }
            
            endpoint = f"{self.api_base}/search/artist"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        artists = data.get('data', [])
                        
                        logger.info(f"Found {len(artists)} artists for query: {query}")
                        return artists
                    else:
                        logger.error(f"Deezer artist search failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Deezer artist search error: {str(e)}")
            return []
    
    async def search_albums(self, query: str, limit: int = 50) -> List[Dict]:
        """Search Deezer albums"""
        await self.rate_limiter.wait()
        
        try:
            search_params = {
                'q': query,
                'limit': min(limit, 100)
            }
            
            endpoint = f"{self.api_base}/search/album"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        albums = data.get('data', [])
                        
                        logger.info(f"Found {len(albums)} albums for query: {query}")
                        return albums
                    else:
                        logger.error(f"Deezer album search failed: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Deezer album search error: {str(e)}")
            return []
    
    async def get_track_details(self, track_id: str) -> Optional[DeezerTrack]:
        """Get detailed information about a specific track"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/track/{track_id}"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        track_data = await response.json()
                        return await self._parse_track_data(track_data)
                    else:
                        logger.error(f"Failed to get track details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting track details: {str(e)}")
            return None
    
    async def get_artist_details(self, artist_id: str) -> Optional[DeezerArtist]:
        """Get detailed information about a specific artist"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/artist/{artist_id}"
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        artist_data = await response.json()
                        return await self._parse_artist_data(artist_data)
                    else:
                        logger.error(f"Failed to get artist details: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting artist details: {str(e)}")
            return None
    
    async def get_artist_top_tracks(self, artist_id: str, limit: int = 50) -> List[DeezerTrack]:
        """Get top tracks from a specific artist"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/artist/{artist_id}/top"
            params = {'limit': min(limit, 100)}
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        tracks = []
                        
                        for track_data in data.get('data', []):
                            track = await self._parse_track_data(track_data)
                            if track:
                                tracks.append(track)
                        
                        logger.info(f"Retrieved {len(tracks)} top tracks for artist {artist_id}")
                        return tracks
                    else:
                        logger.error(f"Failed to get artist top tracks: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting artist top tracks: {str(e)}")
            return []
    
    async def get_album_tracks(self, album_id: str) -> List[DeezerTrack]:
        """Get all tracks from a specific album"""
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/album/{album_id}/tracks"
            
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
    
    async def get_charts(self, chart_type: str = "tracks", limit: int = 100) -> List[Dict]:
        """
        Get Deezer charts
        
        Args:
            chart_type: Type of chart (tracks, albums, artists, playlists)
            limit: Maximum results to return
            
        Returns:
            List of chart items
        """
        await self.rate_limiter.wait()
        
        try:
            endpoint = f"{self.api_base}/chart/0/{chart_type}"
            params = {'limit': min(limit, 100)}
            
            async with aiohttp.ClientSession(headers=self.session_headers) as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        chart_items = data.get('data', [])
                        
                        logger.info(f"Retrieved {len(chart_items)} {chart_type} from charts")
                        return chart_items
                    else:
                        logger.error(f"Failed to get charts: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting charts: {str(e)}")
            return []
    
    async def monitor_content_infringement(
        self,
        protected_content: Dict,
        similarity_threshold: float = 0.8
    ) -> List[ContentMatch]:
        """
        Monitor Deezer for potential copyright infringement
        
        Args:
            protected_content: Content to protect
            similarity_threshold: Minimum similarity for match detection
            
        Returns:
            List of potential copyright matches
        """
        matches = []
        
        try:
            # Generate search queries from protected content
            search_queries = self._generate_search_queries(protected_content)
            
            for query in search_queries:
                results = await self.search_tracks(query, limit=50)
                
                for result in results:
                    track = await self._parse_track_data(result)
                    if track:
                        similarity_score = await self._calculate_content_similarity(
                            protected_content, track
                        )
                        
                        if similarity_score >= similarity_threshold:
                            match = ContentMatch(
                                platform="deezer",
                                content_id=track.track_id,
                                url=track.track_url,
                                title=track.title,
                                description=f"{track.artist_name} - {track.album_title}",
                                creator=track.artist_name,
                                similarity_score=similarity_score,
                                detection_date=datetime.utcnow(),
                                content_type="track",
                                metadata={
                                    'artist_id': track.artist_id,
                                    'album_id': track.album_id,
                                    'duration': track.duration,
                                    'rank': track.rank,
                                    'isrc': track.isrc,
                                    'preview_url': track.preview_url
                                }
                            )
                            matches.append(match)
            
            logger.info(f"Found {len(matches)} potential copyright matches on Deezer")
            return matches
            
        except Exception as e:
            logger.error(f"Error monitoring Deezer content infringement: {str(e)}")
            return []
    
    async def analyze_artist_performance(self, artist_id: str) -> Dict[str, Any]:
        """
        Analyze artist performance metrics on Deezer
        
        Args:
            artist_id: Deezer artist ID
            
        Returns:
            Comprehensive artist performance analysis
        """
        try:
            artist = await self.get_artist_details(artist_id)
            if not artist:
                return {}
            
            top_tracks = await self.get_artist_top_tracks(artist_id, limit=20)
            
            # Calculate performance metrics
            avg_rank = sum(track.rank for track in top_tracks) / len(top_tracks) if top_tracks else 0
            total_duration = sum(track.duration for track in top_tracks)
            
            performance_analysis = {
                'artist_id': artist.artist_id,
                'artist_name': artist.name,
                'basic_metrics': {
                    'fan_count': artist.nb_fan,
                    'album_count': artist.nb_album,
                    'top_tracks_count': len(top_tracks)
                },
                'popularity_metrics': {
                    'average_track_rank': avg_rank,
                    'top_track_rank': min((track.rank for track in top_tracks), default=0),
                    'popularity_category': self._categorize_artist_popularity(artist.nb_fan)
                },
                'content_analysis': {
                    'total_duration_minutes': total_duration // 60,
                    'average_track_duration': total_duration // len(top_tracks) if top_tracks else 0,
                    'content_diversity_score': len(set(track.genre for track in top_tracks if track.genre)) / max(len(top_tracks), 1)
                },
                'engagement_analysis': {
                    'fan_growth_potential': self._calculate_fan_growth_potential(artist),
                    'market_presence': 'high' if artist.nb_fan > 100000 else 'medium' if artist.nb_fan > 10000 else 'low'
                },
                'top_tracks': [
                    {
                        'title': track.title,
                        'rank': track.rank,
                        'duration': track.duration,
                        'album': track.album_title
                    }
                    for track in top_tracks[:10]
                ]
            }
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing artist performance: {str(e)}")
            return {}
    
    async def analyze_music_trends(
        self,
        genre: str = None,
        time_period: str = "current",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Analyze music trends on Deezer
        
        Args:
            genre: Specific genre to analyze
            time_period: Time period for analysis
            limit: Maximum items to analyze
            
        Returns:
            Comprehensive trend analysis
        """
        try:
            # Get chart data
            trending_tracks = await self.get_charts("tracks", limit)
            trending_albums = await self.get_charts("albums", 50)
            trending_artists = await self.get_charts("artists", 50)
            
            # Analyze trends
            trends_analysis = {
                'trending_tracks': [
                    {
                        'title': track.get('title', ''),
                        'artist': track.get('artist', {}).get('name', ''),
                        'rank': track.get('position', 0),
                        'duration': track.get('duration', 0)
                    }
                    for track in trending_tracks[:20]
                ],
                'trending_artists': [
                    {
                        'name': artist.get('name', ''),
                        'fan_count': artist.get('nb_fan', 0),
                        'album_count': artist.get('nb_album', 0)
                    }
                    for artist in trending_artists[:10]
                ],
                'genre_analysis': await self._analyze_genre_trends(trending_tracks),
                'duration_trends': await self._analyze_duration_trends(trending_tracks),
                'artist_diversity': len(set(track.get('artist', {}).get('name', '') for track in trending_tracks)),
                'market_insights': {
                    'avg_track_duration': sum(track.get('duration', 0) for track in trending_tracks) / len(trending_tracks) if trending_tracks else 0,
                    'most_popular_genres': await self._get_popular_genres(trending_tracks),
                    'emerging_artists': await self._identify_emerging_artists(trending_artists)
                }
            }
            
            return trends_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing music trends: {str(e)}")
            return {}
    
    async def bulk_track_analysis(self, track_ids: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple tracks in bulk for efficiency"""
        results = []
        
        # Process tracks in batches to respect rate limits
        batch_size = 20
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i + batch_size]
            
            batch_tasks = [self.get_track_details(track_id) for track_id in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for track in batch_results:
                if isinstance(track, DeezerTrack):
                    analysis = await self._analyze_track_performance(track)
                    results.append(analysis)
                elif isinstance(track, Exception):
                    logger.error(f"Error in bulk analysis: {str(track)}")
            
            # Rate limiting between batches
            await asyncio.sleep(1)
        
        return results
    
    async def _parse_track_data(self, track_data: Dict) -> Optional[DeezerTrack]:
        """Parse Deezer API track data into DeezerTrack model"""
        try:
            # Parse artist information
            artist_info = track_data.get('artist', {})
            
            # Parse album information
            album_info = track_data.get('album', {})
            
            # Parse contributors
            contributors = track_data.get('contributors', [])
            
            track = DeezerTrack(
                track_id=str(track_data.get('id', '')),
                title=track_data.get('title', ''),
                artist_name=artist_info.get('name', ''),
                artist_id=str(artist_info.get('id', '')),
                album_title=album_info.get('title', ''),
                album_id=str(album_info.get('id', '')),
                duration=track_data.get('duration', 0),
                release_date=datetime.fromisoformat(track_data['release_date']) if track_data.get('release_date') else None,
                track_position=track_data.get('track_position'),
                disk_number=track_data.get('disk_number'),
                explicit_lyrics=track_data.get('explicit_lyrics', False),
                preview_url=track_data.get('preview'),
                track_url=track_data.get('link', ''),
                bpm=track_data.get('bpm'),
                gain=track_data.get('gain'),
                genre=album_info.get('genre', {}).get('name') if album_info.get('genre') else None,
                contributors=[
                    {
                        'id': str(contrib.get('id', '')),
                        'name': contrib.get('name', ''),
                        'role': contrib.get('role', '')
                    }
                    for contrib in contributors
                ],
                isrc=track_data.get('isrc'),
                rank=track_data.get('rank', 0),
                available=track_data.get('available', True),
                metadata={
                    'readable': track_data.get('readable', True),
                    'alternative': track_data.get('alternative'),
                    'md5_image': track_data.get('md5_image')
                }
            )
            
            return track
            
        except Exception as e:
            logger.error(f"Error parsing track data: {str(e)}")
            return None
    
    async def _parse_artist_data(self, artist_data: Dict) -> Optional[DeezerArtist]:
        """Parse Deezer API artist data into DeezerArtist model"""
        try:
            artist = DeezerArtist(
                artist_id=str(artist_data.get('id', '')),
                name=artist_data.get('name', ''),
                link=artist_data.get('link', ''),
                picture_url=artist_data.get('picture'),
                picture_small=artist_data.get('picture_small'),
                picture_medium=artist_data.get('picture_medium'),
                picture_big=artist_data.get('picture_big'),
                picture_xl=artist_data.get('picture_xl'),
                nb_album=artist_data.get('nb_album', 0),
                nb_fan=artist_data.get('nb_fan', 0),
                radio=artist_data.get('radio', False),
                tracklist=artist_data.get('tracklist'),
                type=artist_data.get('type', 'artist')
            )
            
            return artist
            
        except Exception as e:
            logger.error(f"Error parsing artist data: {str(e)}")
            return None
    
    def _generate_search_queries(self, protected_content: Dict) -> List[str]:
        """Generate search queries for content protection"""
        queries = []
        
        if 'title' in protected_content:
            queries.append(protected_content['title'])
        
        if 'artist' in protected_content:
            queries.append(protected_content['artist'])
        
        if 'album' in protected_content:
            queries.append(f"{protected_content['artist']} {protected_content['album']}")
        
        if 'isrc' in protected_content:
            queries.append(protected_content['isrc'])
        
        return queries[:5]
    
    async def _calculate_content_similarity(
        self,
        protected_content: Dict,
        track: DeezerTrack
    ) -> float:
        """Calculate similarity between protected content and Deezer track"""
        from difflib import SequenceMatcher
        
        similarity_scores = []
        
        # Title similarity
        if 'title' in protected_content and track.title:
            title_similarity = SequenceMatcher(
                None,
                protected_content['title'].lower(),
                track.title.lower()
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
                similarity_scores.append(1.0 * 0.8)  # High weight for ISRC match
        
        # Duration similarity (within 10 seconds)
        if 'duration' in protected_content and track.duration:
            duration_diff = abs(protected_content['duration'] - track.duration)
            if duration_diff <= 10:
                duration_similarity = 1.0 - (duration_diff / 60)  # Normalize by minute
                similarity_scores.append(duration_similarity * 0.2)
        
        return sum(similarity_scores) if similarity_scores else 0.0
    
    def _categorize_artist_popularity(self, fan_count: int) -> str:
        """Categorize artist popularity level"""
        if fan_count > 1000000:
            return "superstar"
        elif fan_count > 100000:
            return "popular"
        elif fan_count > 10000:
            return "emerging"
        elif fan_count > 1000:
            return "niche"
        else:
            return "new"
    
    def _calculate_fan_growth_potential(self, artist: DeezerArtist) -> str:
        """Calculate artist fan growth potential"""
        # Simple heuristic based on album count vs fan count ratio
        if artist.nb_album == 0:
            return "unknown"
        
        ratio = artist.nb_fan / artist.nb_album
        
        if ratio > 50000:
            return "established"
        elif ratio > 10000:
            return "growing"
        elif ratio > 1000:
            return "developing"
        else:
            return "emerging"
    
    async def _analyze_genre_trends(self, tracks: List[Dict]) -> Dict[str, int]:
        """Analyze genre trends from track list"""
        genre_counts = {}
        
        for track in tracks:
            album = track.get('album', {})
            genre = album.get('genre', {}).get('name') if album.get('genre') else 'Unknown'
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        return dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    async def _analyze_duration_trends(self, tracks: List[Dict]) -> Dict[str, Any]:
        """Analyze duration trends from track list"""
        durations = [track.get('duration', 0) for track in tracks if track.get('duration')]
        
        if not durations:
            return {}
        
        avg_duration = sum(durations) / len(durations)
        short_tracks = len([d for d in durations if d < 180])  # < 3 minutes
        medium_tracks = len([d for d in durations if 180 <= d <= 300])  # 3-5 minutes
        long_tracks = len([d for d in durations if d > 300])  # > 5 minutes
        
        return {
            'average_duration_seconds': avg_duration,
            'average_duration_minutes': avg_duration / 60,
            'short_tracks_percentage': (short_tracks / len(durations)) * 100,
            'medium_tracks_percentage': (medium_tracks / len(durations)) * 100,
            'long_tracks_percentage': (long_tracks / len(durations)) * 100
        }
    
    async def _get_popular_genres(self, tracks: List[Dict]) -> List[str]:
        """Get most popular genres from track list"""
        genre_analysis = await self._analyze_genre_trends(tracks)
        return list(genre_analysis.keys())[:5]
    
    async def _identify_emerging_artists(self, artists: List[Dict]) -> List[Dict]:
        """Identify emerging artists based on metrics"""
        emerging = []
        
        for artist in artists:
            fan_count = artist.get('nb_fan', 0)
            album_count = artist.get('nb_album', 0)
            
            # Criteria for emerging: moderate fan count, few albums
            if 10000 <= fan_count <= 100000 and album_count <= 3:
                emerging.append({
                    'name': artist.get('name', ''),
                    'fan_count': fan_count,
                    'album_count': album_count,
                    'growth_potential': 'high'
                })
        
        return emerging[:5]
    
    async def _analyze_track_performance(self, track: DeezerTrack) -> Dict[str, Any]:
        """Analyze individual track performance metrics"""
        return {
            'track_id': track.track_id,
            'title': track.title,
            'artist': track.artist_name,
            'popularity_score': track.rank,
            'duration_category': self._categorize_duration(track.duration),
            'availability': track.available,
            'explicit_content': track.explicit_lyrics,
            'commercial_potential': self._assess_commercial_potential(track),
            'metadata_completeness': self._assess_metadata_completeness(track)
        }
    
    def _categorize_duration(self, duration: int) -> str:
        """Categorize track duration"""
        if duration < 120:
            return "very_short"
        elif duration < 180:
            return "short"
        elif duration < 300:
            return "medium"
        elif duration < 420:
            return "long"
        else:
            return "extended"
    
    def _assess_commercial_potential(self, track: DeezerTrack) -> str:
        """Assess track commercial potential"""
        if track.rank > 500000:
            return "high"
        elif track.rank > 100000:
            return "medium"
        elif track.rank > 10000:
            return "low"
        else:
            return "minimal"
    
    def _assess_metadata_completeness(self, track: DeezerTrack) -> float:
        """Assess completeness of track metadata"""
        fields = [
            track.title, track.artist_name, track.album_title,
            track.duration, track.genre, track.isrc
        ]
        
        complete_fields = sum(1 for field in fields if field)
        return complete_fields / len(fields)
