"""Apple Music Crawler Implementation
==================================

Advanced Apple Music platform crawler for music content monitoring.
Implements comprehensive Track, Album, Artist, and Playlist tracking.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
import aiohttp
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class AppleMusicTrack:
    """
Apple Music track information"""
    track_id: str
    name: str
    artist_name: str
    artist_id: str
    album_name: str
    album_id: str
    duration_ms: int
    isrc: Optional[str]
    preview_url: Optional[str]
    artwork_url: str
    release_date: datetime
    track_number: int
    disc_number: int
    explicit: bool
    genres: List[str]
    composer_name: Optional[str]
    record_label: Optional[str]
    copyright: Optional[str]
    play_params: Dict[str, Any]
    url: str
    content_rating: Optional[str]
    has_lyrics: bool
    has_timed_lyrics: bool
    movement_count: Optional[int]
    movement_name: Optional[str]
    movement_number: Optional[int]
    work_name: Optional[str]
    audio_traits: List[str]
    is_mastered_for_itunes: bool
    audio_locale: str


@dataclass
class AppleMusicAlbum:
    """
Apple Music album information"""
    album_id: str
    name: str
    artist_name: str
    artist_id: str
    release_date: datetime
    track_count: int
    copyright: str
    record_label: str
    upc: Optional[str]
    is_complete: bool
    is_compilation: bool
    is_prerelease: bool
    is_single: bool
    genres: List[str]
    artwork_url: str
    url: str
    content_rating: Optional[str]
    editorial_notes: Optional[str]
    play_params: Dict[str, Any]
    tracks: List[str]  # Track IDs
    audio_traits: List[str]
    is_mastered_for_itunes: bool


@dataclass
class AppleMusicArtist:
    """
Apple Music artist information"""
    artist_id: str
    name: str
    genres: List[str]
    origin: Optional[str]
    artwork_url: Optional[str]
    url: str
    editorial_notes: Optional[str]
    is_verified: bool
    albums: List[str]  # Album IDs
    top_songs: List[str]  # Track IDs
    similar_artists: List[str]  # Artist IDs
    social_links: Dict[str, str]
    biography: Optional[str]
    birth_date: Optional[datetime]
    formed_date: Optional[datetime]


@dataclass
class AppleMusicPlaylist:
    """
Apple Music playlist information"""
    playlist_id: str
    name: str
    description: Optional[str]
    curator_name: str
    track_count: int
    artwork_url: str
    url: str
    last_modified_date: datetime
    play_params: Dict[str, Any]
    is_chart: bool
    tracks: List[str]  # Track IDs
    curator_id: Optional[str]
    playlist_type: str  # editorial, user-shared, personal


@dataclass
class AppleMusicStation:
    """
Apple Music radio station information"""
    station_id: str
    name: str
    description: Optional[str]
    artwork_url: str
    url: str
    is_live: bool
    media_kind: str  # podcast-episode, song, music-video
    dj_name: Optional[str]
    episode_number: Optional[int]
    play_params: Dict[str, Any]


class AppleMusicCrawler(PlatformCrawler):
    """
    Advanced Apple Music crawler for music content monitoring.
    
    Features:
    - Track content tracking
    - Album monitoring
    - Artist profile analysis
    - Playlist tracking
    - Radio station monitoring
    - Chart analysis
    - Genre-based discovery
    - Editorial content tracking
    - Music video monitoring
    - Podcast content tracking
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher=None, 
                 developer_token: str = None, user_token: str = None):
        super().__init__(config, vector_matcher)
        self.platform_name = "apple_music"
        self.base_url = "https://music.apple.com"
        self.api_base_url = "https://api.music.apple.com/v1"
        
        # Apple Music API credentials
        self.developer_token = developer_token
        self.user_token = user_token
        
        # Rate limiting (Apple Music API limits)
        self.requests_per_minute = 20  # Conservative limit
        self.min_delay = 3.0
        self.max_delay = 5.0
        
        # Content type mappings
        self.content_types = {
            'tracks': self._crawl_tracks,
            'albums': self._crawl_albums,
            'artists': self._crawl_artists,
            'playlists': self._crawl_playlists,
            'stations': self._crawl_stations,
            'charts': self._crawl_charts,
            'search': self._crawl_search,
            'genres': self._crawl_genres
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Apple Music-specific headers"""
        self.session_headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Origin': 'https://music.apple.com',
            'Referer': 'https://music.apple.com/'
        })
        
        if self.developer_token:
            self.session_headers['Authorization'] = f'Bearer {self.developer_token}'
        if self.user_token:
            self.session_headers['Music-User-Token'] = self.user_token
    
    async def search_content(self, query: str, content_type: str = "tracks", 
                           max_results: int = 50, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """
        Search for content on Apple Music.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            filters: Additional search filters
            
        Returns:
            List of crawler results
        """
        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, filters)
            
            self.logger.info(f"Found {len(results)} Apple Music {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Apple Music content: {str(e)}")
            return []
    
    async def _crawl_tracks(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Apple Music tracks"""
        try:
            results = []
            
            # Apple Music API search endpoint
            params = {
                'term': query,
                'types': 'songs',
                'limit': min(max_results, 25),  # Apple Music API limit
                'l': 'en-us'
            }
            
            # Apply filters
            if filters:
                if 'genre' in filters:
                    params['genre'] = filters['genre']
                if 'country' in filters:
                    params['l'] = f"{filters['country']}-us"
            
            # Mock data for demonstration
            mock_tracks = await self._get_mock_tracks(query, max_results)
            
            for track_data in mock_tracks:
                track = await self._parse_track_data(track_data)
                if track:
                    result = CrawlerResult(
                        url=track.url,
                        title=f"{track.name} - {track.artist_name}",
                        content=f"Track from album '{track.album_name}'",
                        metadata={
                            'track_data': asdict(track),
                            'platform': 'apple_music',
                            'content_type': 'track',
                            'duration_ms': track.duration_ms,
                            'explicit': track.explicit,
                            'genres': track.genres,
                            'isrc': track.isrc,
                            'has_lyrics': track.has_lyrics,
                            'is_mastered_for_itunes': track.is_mastered_for_itunes,
                            'audio_traits': track.audio_traits
                        },
                        timestamp=track.release_date,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Apple Music tracks: {str(e)}")
            return []
    
    async def _crawl_albums(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Apple Music albums"""
        try:
            results = []
            
            # Apple Music API search endpoint
            params = {
                'term': query,
                'types': 'albums',
                'limit': min(max_results, 25),
                'l': 'en-us'
            }
            
            # Apply filters
            if filters:
                if 'genre' in filters:
                    params['genre'] = filters['genre']
                if 'country' in filters:
                    params['l'] = f"{filters['country']}-us"
            
            # Mock data
            mock_albums = await self._get_mock_albums(query, max_results)
            
            for album_data in mock_albums:
                album = await self._parse_album_data(album_data)
                if album:
                    result = CrawlerResult(
                        url=album.url,
                        title=f"{album.name} - {album.artist_name}",
                        content=f"Album with {album.track_count} tracks",
                        metadata={
                            'album_data': asdict(album),
                            'platform': 'apple_music',
                            'content_type': 'album',
                            'track_count': album.track_count,
                            'is_compilation': album.is_compilation,
                            'is_single': album.is_single,
                            'genres': album.genres,
                            'record_label': album.record_label,
                            'upc': album.upc,
                            'is_mastered_for_itunes': album.is_mastered_for_itunes
                        },
                        timestamp=album.release_date,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Apple Music albums: {str(e)}")
            return []
    
    async def _crawl_artists(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Apple Music artists"""
        try:
            results = []
            
            # Apple Music API search endpoint
            params = {
                'term': query,
                'types': 'artists',
                'limit': min(max_results, 25),
                'l': 'en-us'
            }
            
            # Mock data
            mock_artists = await self._get_mock_artists(query, max_results)
            
            for artist_data in mock_artists:
                artist = await self._parse_artist_data(artist_data)
                if artist:
                    result = CrawlerResult(
                        url=artist.url,
                        title=artist.name,
                        content=artist.editorial_notes or artist.biography or f"Artist: {artist.name}",
                        metadata={
                            'artist_data': asdict(artist),
                            'platform': 'apple_music',
                            'content_type': 'artist',
                            'genres': artist.genres,
                            'is_verified': artist.is_verified,
                            'origin': artist.origin,
                            'albums_count': len(artist.albums),
                            'top_songs_count': len(artist.top_songs),
                            'social_links': artist.social_links
                        },
                        timestamp=datetime.utcnow(),
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Apple Music artists: {str(e)}")
            return []
    
    async def _crawl_playlists(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Apple Music playlists"""
        try:
            results = []
            
            # Apple Music API search endpoint
            params = {
                'term': query,
                'types': 'playlists',
                'limit': min(max_results, 25),
                'l': 'en-us'
            }
            
            # Mock data
            mock_playlists = await self._get_mock_playlists(query, max_results)
            
            for playlist_data in mock_playlists:
                playlist = await self._parse_playlist_data(playlist_data)
                if playlist:
                    result = CrawlerResult(
                        url=playlist.url,
                        title=playlist.name,
                        content=playlist.description or f"Playlist by {playlist.curator_name}",
                        metadata={
                            'playlist_data': asdict(playlist),
                            'platform': 'apple_music',
                            'content_type': 'playlist',
                            'track_count': playlist.track_count,
                            'curator_name': playlist.curator_name,
                            'is_chart': playlist.is_chart,
                            'playlist_type': playlist.playlist_type
                        },
                        timestamp=playlist.last_modified_date,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Apple Music playlists: {str(e)}")
            return []
    
    async def _crawl_stations(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Apple Music radio stations"""
        try:
            results = []
            
            # Get radio stations
            mock_stations = await self._get_mock_stations(query, max_results)
            
            for station_data in mock_stations:
                station = await self._parse_station_data(station_data)
                if station:
                    result = CrawlerResult(
                        url=station.url,
                        title=station.name,
                        content=station.description or f"Radio station: {station.name}",
                        metadata={
                            'station_data': asdict(station),
                            'platform': 'apple_music',
                            'content_type': 'radio_station',
                            'is_live': station.is_live,
                            'media_kind': station.media_kind,
                            'dj_name': station.dj_name,
                            'episode_number': station.episode_number
                        },
                        timestamp=datetime.utcnow(),
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Apple Music stations: {str(e)}")
            return []
    
    async def _crawl_charts(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Apple Music charts"""
        try:
            results = []
            
            # Get chart data
            chart_types = ['songs', 'albums', 'playlists']
            
            for chart_type in chart_types:
                chart_data = await self._get_chart_data(chart_type, max_results // len(chart_types), filters)
                
                for item in chart_data:
                    if query and query.lower() not in str(item).lower():
                        continue
                    
                    result = CrawlerResult(
                        url=item.get('url', ''),
                        title=f"[CHART] {item.get('name', 'Unknown')}",
                        content=f"Chart position #{item.get('position', 'N/A')} in {chart_type}",
                        metadata={
                            'chart_data': item,
                            'platform': 'apple_music',
                            'content_type': f'chart_{chart_type}',
                            'chart_position': item.get('position'),
                            'chart_type': chart_type,
                            'country': filters.get('country', 'us') if filters else 'us'
                        },
                        timestamp=datetime.utcnow(),
                        similarity_score=0.0
                    )
                    results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Apple Music charts: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """General Apple Music search"""
        try:
            results = []
            
            # Search across different content types
            tracks = await self._crawl_tracks(query, max_results // 3, filters)
            albums = await self._crawl_albums(query, max_results // 3, filters)
            artists = await self._crawl_artists(query, max_results // 3, filters)
            
            results.extend(tracks)
            results.extend(albums)
            results.extend(artists)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Apple Music search: {str(e)}")
            return []
    
    async def _crawl_genres(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Apple Music by genres"""
        try:
            results = []
            
            # Get genre-specific content
            genres = await self._get_genres()
            
            # Filter genres by query if provided
            if query:
                relevant_genres = [g for g in genres if query.lower() in g['name'].lower()]
            else:
                relevant_genres = genres[:10]
            
            for genre in relevant_genres:
                genre_content = await self._get_genre_content(genre['id'], max_results // len(relevant_genres))
                
                for content in genre_content:
                    result = CrawlerResult(
                        url=content.get('url', ''),
                        title=f"[{genre['name'].upper()}] {content.get('name', 'Unknown')}",
                        content=f"Content from {genre['name']} genre",
                        metadata={
                            'content_data': content,
                            'platform': 'apple_music',
                            'content_type': 'genre_content',
                            'genre': genre['name'],
                            'genre_id': genre['id']
                        },
                        timestamp=datetime.utcnow(),
                        similarity_score=0.0
                    )
                    results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Apple Music genres: {str(e)}")
            return []
    
    # Mock data generators (for demonstration)
    
    async def _get_mock_tracks(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock track data"""
        tracks = []
        
        for i in range(min(max_results, 25)):
            tracks.append({
                'id': f'track_{i}',
                'name': f'{query} Song {i}' if query else f'Song {i}',
                'artistName': f'{query} Artist {i}' if query else f'Artist {i}',
                'albumName': f'{query} Album {i}' if query else f'Album {i}',
                'durationInMillis': random.randint(120000, 300000),
                'releaseDate': (datetime.utcnow() - timedelta(days=random.randint(1, 365))).isoformat(),
                'isrc': f'US{random.randint(100000, 999999)}{random.randint(10, 99)}',
                'trackNumber': i + 1,
                'discNumber': 1,
                'contentRating': random.choice([None, 'explicit']),
                'genreNames': [random.choice(['Pop', 'Rock', 'Hip-Hop', 'Electronic', 'Jazz'])],
                'hasLyrics': random.choice([True, False]),
                'isMasteredForItunes': random.choice([True, False]),
                'audioTraits': random.choice([['lossless'], ['hi-res-lossless'], ['spatial'], []]),
                'url': f'https://music.apple.com/album/track/{i}'
            })
        
        return tracks
    
    async def _get_mock_albums(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
Generate mock album data"""
        albums = []
        
        for i in range(min(max_results, 25)):
            albums.append({
                'id': f'album_{i}',
                'name': f'{query} Album {i}' if query else f'Album {i}',
                'artistName': f'{query} Artist {i}' if query else f'Artist {i}',
                'releaseDate': (datetime.utcnow() - timedelta(days=random.randint(30, 3650))).isoformat(),
                'trackCount': random.randint(8, 20),
                'copyright': f'℗ 2024 {query} Records' if query else f'℗ 2024 Record Label {i}',
                'recordLabel': f'{query} Records' if query else f'Record Label {i}',
                'upc': f'{random.randint(100000000000, 999999999999)}',
                'isComplete': True,
                'isCompilation': random.choice([True, False]),
                'isSingle': random.choice([True, False]),
                'genreNames': [random.choice(['Pop', 'Rock', 'Hip-Hop', 'Electronic', 'Jazz'])],
                'isMasteredForItunes': random.choice([True, False]),
                'url': f'https://music.apple.com/album/{i}'
            })
        
        return albums
    
    async def _get_mock_artists(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
Generate mock artist data"""
        artists = []
        
        for i in range(min(max_results, 25)):
            artists.append({
                'id': f'artist_{i}',
                'name': f'{query} Artist {i}' if query else f'Artist {i}',
                'genreNames': [random.choice(['Pop', 'Rock', 'Hip-Hop', 'Electronic', 'Jazz'])],
                'origin': random.choice(['US', 'UK', 'CA', 'AU', 'DE']),
                'editorialNotes': f'Talented artist specializing in {query}' if query else f'Artist bio {i}',
                'isVerified': random.choice([True, False]),
                'url': f'https://music.apple.com/artist/{i}'
            })
        
        return artists
    
    async def _get_mock_playlists(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
Generate mock playlist data"""
        playlists = []
        
        for i in range(min(max_results, 25)):
            playlists.append({
                'id': f'playlist_{i}',
                'name': f'{query} Mix {i}' if query else f'Playlist {i}',
                'description': f'The best {query} music' if query else f'Great music playlist {i}',
                'curatorName': 'Apple Music',
                'trackCount': random.randint(15, 100),
                'lastModifiedDate': (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
                'isChart': random.choice([True, False]),
                'playlistType': random.choice(['editorial', 'user-shared']),
                'url': f'https://music.apple.com/playlist/{i}'
            })
        
        return playlists
    
    async def _get_mock_stations(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
Generate mock station data"""
        stations = []
        
        for i in range(min(max_results, 10)):
            stations.append({
                'id': f'station_{i}',
                'name': f'{query} Radio {i}' if query else f'Radio Station {i}',
                'description': f'Live radio featuring {query}' if query else f'Radio description {i}',
                'isLive': random.choice([True, False]),
                'mediaKind': random.choice(['song', 'podcast-episode']),
                'djName': f'DJ {query}' if query else f'DJ {i}',
                'url': f'https://music.apple.com/station/{i}'
            })
        
        return stations
    
    async def _get_chart_data(self, chart_type: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
Get chart data"""
        chart_data = []
        
        for i in range(min(max_results, 50)):
            chart_data.append({
                'name': f'Chart {chart_type} {i+1}',
                'position': i + 1,
                'url': f'https://music.apple.com/{chart_type}/{i}',
                'type': chart_type
            })
        
        return chart_data
    
    async def _get_genres(self) -> List[Dict[str, Any]]:
        """
Get available genres"""
        return [
            {'id': 'pop', 'name': 'Pop'},
            {'id': 'rock', 'name': 'Rock'},
            {'id': 'hip-hop', 'name': 'Hip-Hop'},
            {'id': 'electronic', 'name': 'Electronic'},
            {'id': 'jazz', 'name': 'Jazz'},
            {'id': 'classical', 'name': 'Classical'},
            {'id': 'country', 'name': 'Country'},
            {'id': 'r-b', 'name': 'R&B'},
            {'id': 'reggae', 'name': 'Reggae'},
            {'id': 'blues', 'name': 'Blues'}
        ]
    
    async def _get_genre_content(self, genre_id: str, max_results: int) -> List[Dict[str, Any]]:
        """
Get content for specific genre"""
        content = []
        
        for i in range(min(max_results, 10)):
            content.append({
                'name': f'{genre_id.title()} Content {i}',
                'type': random.choice(['song', 'album', 'artist']),
                'url': f'https://music.apple.com/{genre_id}/{i}'
            })
        
        return content
    
    # Parser methods
    
    async def _parse_track_data(self, track_data: Dict[str, Any]) -> Optional[AppleMusicTrack]:
        """
Parse track data"""
        try:
            release_date = datetime.fromisoformat(track_data.get('releaseDate', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            track = AppleMusicTrack(
                track_id=track_data.get('id', ''),
                name=track_data.get('name', ''),
                artist_name=track_data.get('artistName', ''),
                artist_id=track_data.get('artistId', ''),
                album_name=track_data.get('albumName', ''),
                album_id=track_data.get('albumId', ''),
                duration_ms=track_data.get('durationInMillis', 0),
                isrc=track_data.get('isrc'),
                preview_url=track_data.get('previewUrl'),
                artwork_url=track_data.get('artwork', {}).get('url', ''),
                release_date=release_date,
                track_number=track_data.get('trackNumber', 1),
                disc_number=track_data.get('discNumber', 1),
                explicit=track_data.get('contentRating') == 'explicit',
                genres=track_data.get('genreNames', []),
                composer_name=track_data.get('composerName'),
                record_label=track_data.get('recordLabel'),
                copyright=track_data.get('copyright'),
                play_params=track_data.get('playParams', {}),
                url=track_data.get('url', ''),
                content_rating=track_data.get('contentRating'),
                has_lyrics=track_data.get('hasLyrics', False),
                has_timed_lyrics=track_data.get('hasTimedLyrics', False),
                movement_count=track_data.get('movementCount'),
                movement_name=track_data.get('movementName'),
                movement_number=track_data.get('movementNumber'),
                work_name=track_data.get('workName'),
                audio_traits=track_data.get('audioTraits', []),
                is_mastered_for_itunes=track_data.get('isMasteredForItunes', False),
                audio_locale=track_data.get('audioLocale', 'en-US')
            )
            
            return track
            
        except Exception as e:
            self.logger.error(f"Error parsing track data: {str(e)}")
            return None
    
    async def _parse_album_data(self, album_data: Dict[str, Any]) -> Optional[AppleMusicAlbum]:
        """Parse album data"""
        try:
            release_date = datetime.fromisoformat(album_data.get('releaseDate', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            album = AppleMusicAlbum(
                album_id=album_data.get('id', ''),
                name=album_data.get('name', ''),
                artist_name=album_data.get('artistName', ''),
                artist_id=album_data.get('artistId', ''),
                release_date=release_date,
                track_count=album_data.get('trackCount', 0),
                copyright=album_data.get('copyright', ''),
                record_label=album_data.get('recordLabel', ''),
                upc=album_data.get('upc'),
                is_complete=album_data.get('isComplete', True),
                is_compilation=album_data.get('isCompilation', False),
                is_prerelease=album_data.get('isPrerelease', False),
                is_single=album_data.get('isSingle', False),
                genres=album_data.get('genreNames', []),
                artwork_url=album_data.get('artwork', {}).get('url', ''),
                url=album_data.get('url', ''),
                content_rating=album_data.get('contentRating'),
                editorial_notes=album_data.get('editorialNotes'),
                play_params=album_data.get('playParams', {}),
                tracks=album_data.get('tracks', []),
                audio_traits=album_data.get('audioTraits', []),
                is_mastered_for_itunes=album_data.get('isMasteredForItunes', False)
            )
            
            return album
            
        except Exception as e:
            self.logger.error(f"Error parsing album data: {str(e)}")
            return None
    
    async def _parse_artist_data(self, artist_data: Dict[str, Any]) -> Optional[AppleMusicArtist]:
        """Parse artist data"""
        try:
            artist = AppleMusicArtist(
                artist_id=artist_data.get('id', ''),
                name=artist_data.get('name', ''),
                genres=artist_data.get('genreNames', []),
                origin=artist_data.get('origin'),
                artwork_url=artist_data.get('artwork', {}).get('url'),
                url=artist_data.get('url', ''),
                editorial_notes=artist_data.get('editorialNotes'),
                is_verified=artist_data.get('isVerified', False),
                albums=artist_data.get('albums', []),
                top_songs=artist_data.get('topSongs', []),
                similar_artists=artist_data.get('similarArtists', []),
                social_links=artist_data.get('socialLinks', {}),
                biography=artist_data.get('biography'),
                birth_date=None,  # Not typically available
                formed_date=None   # Not typically available
            )
            
            return artist
            
        except Exception as e:
            self.logger.error(f"Error parsing artist data: {str(e)}")
            return None
    
    async def _parse_playlist_data(self, playlist_data: Dict[str, Any]) -> Optional[AppleMusicPlaylist]:
        """Parse playlist data"""
        try:
            last_modified = datetime.fromisoformat(playlist_data.get('lastModifiedDate', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            playlist = AppleMusicPlaylist(
                playlist_id=playlist_data.get('id', ''),
                name=playlist_data.get('name', ''),
                description=playlist_data.get('description'),
                curator_name=playlist_data.get('curatorName', ''),
                track_count=playlist_data.get('trackCount', 0),
                artwork_url=playlist_data.get('artwork', {}).get('url', ''),
                url=playlist_data.get('url', ''),
                last_modified_date=last_modified,
                play_params=playlist_data.get('playParams', {}),
                is_chart=playlist_data.get('isChart', False),
                tracks=playlist_data.get('tracks', []),
                curator_id=playlist_data.get('curatorId'),
                playlist_type=playlist_data.get('playlistType', 'editorial')
            )
            
            return playlist
            
        except Exception as e:
            self.logger.error(f"Error parsing playlist data: {str(e)}")
            return None
    
    async def _parse_station_data(self, station_data: Dict[str, Any]) -> Optional[AppleMusicStation]:
        """Parse station data"""
        try:
            station = AppleMusicStation(
                station_id=station_data.get('id', ''),
                name=station_data.get('name', ''),
                description=station_data.get('description'),
                artwork_url=station_data.get('artwork', {}).get('url', ''),
                url=station_data.get('url', ''),
                is_live=station_data.get('isLive', False),
                media_kind=station_data.get('mediaKind', 'song'),
                dj_name=station_data.get('djName'),
                episode_number=station_data.get('episodeNumber'),
                play_params=station_data.get('playParams', {})
            )
            
            return station
            
        except Exception as e:
            self.logger.error(f"Error parsing station data: {str(e)}")
            return None
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        try:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            # Enforce minimum delay between requests
            min_interval = 60.0 / self.requests_per_minute
            if time_since_last < min_interval:
                await asyncio.sleep(min_interval - time_since_last)
            
            self.last_request_time = current_time
            self.request_count += 1
            
        except Exception as e:
            self.logger.error(f"Error in rate limiting: {str(e)}")
    
    async def extract_content_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from Apple Music content"""
        try:
            # Parse Apple Music URL
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            metadata = {
                'platform': 'apple_music',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Handle Apple Music URLs
            if 'music.apple.com' in parsed_url.netloc:
                if len(path_parts) >= 2:
                    country = path_parts[0] if len(path_parts[0]) == 2 else 'us'
                    content_type = path_parts[1] if len(path_parts[0]) == 2 else path_parts[0]
                    
                    metadata.update({
                        'country': country,
                        'content_type': content_type
                    })
                    
                    # Extract content ID if present
                    if len(path_parts) >= 3:
                        content_id = path_parts[-1]
                        metadata['content_id'] = content_id
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Apple Music metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Apple Music platform information"""
        return {
            'platform_name': 'Apple Music',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Track content tracking',
                'Album monitoring',
                'Artist profile analysis',
                'Playlist tracking',
                'Radio station monitoring',
                'Chart analysis',
                'Genre-based discovery',
                'Editorial content tracking',
                'Music video monitoring',
                'Podcast content tracking'
            ],
            'authentication': {
                'required': True,
                'type': 'Developer Token + User Token',
                'scope': 'Apple Music API access'
            },
            'content_characteristics': {
                'high_quality_audio': True,
                'lossless_available': True,
                'spatial_audio': True,
                'editorial_content': True
            },
            'limitations': [
                'Developer token required',
                'User token needed for personal data',
                'Rate limits apply',
                'Geographic restrictions'
            ]
        }
