"""YouTube Music Platform Crawler - Ultra-Advanced Implementation
Music Streaming Platform Monitoring System

This module provides comprehensive crawling capabilities for YouTube Music platform,
focusing on music discovery, playlist monitoring, and artist analytics.

PROPRIETARY SOFTWARE - CONFIDENTIAL AND PROTECTED
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Created by: Fahed Mlaiel <mlaiel@live.de>

WARNING: This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import hashlib
import base64
from urllib.parse import urljoin, urlparse, quote
from pydantic import BaseModel, Field, validator
from difflib import SequenceMatcher

from ..base import BaseCrawler
from ...utils.rate_limiter import RateLimiter
from ...utils.cache import CacheManager
from ...utils.encryption import ContentEncryption
from ...utils.fingerprinting import ContentFingerprinter

logger = logging.getLogger(__name__)


class YouTubeMusicContentType(str, Enum):
    """YouTube Music content types"""    SONG = "song"
    ALBUM = "album"
    PLAYLIST = "playlist"
    ARTIST = "artist"
    PODCAST = "podcast"
    RADIO_STATION = "radio_station"
    MIX = "mix"


class YouTubeMusicQuality(str, Enum):
    """YouTube Music audio quality"""    LOW = "low"  # 128 kbps
    MEDIUM = "medium"  # 256 kbps
    HIGH = "high"  # 320 kbps
    LOSSLESS = "lossless"  # FLAC


class YouTubeMusicPlaylistType(str, Enum):
    """YouTube Music playlist types"""    USER_CREATED = "user_created"
    OFFICIAL = "official"
    GENERATED = "generated"
    LIKED_SONGS = "liked_songs"
    WATCH_LATER = "watch_later"
    HISTORY = "history"


class YouTubeMusicArtist(BaseModel):
    """YouTube Music artist data model"""    artist_id: str
    name: str
    channel_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    banner_url: Optional[str] = None
    description: Optional[str] = None
    subscriber_count: Optional[int] = None
    is_verified: bool = False
    is_official_artist: bool = False
    genres: List[str] = Field(default_factory=list)
    monthly_listeners: Optional[int] = None
    total_views: Optional[int] = None
    albums_count: int = 0
    songs_count: int = 0
    playlists_count: int = 0
    similar_artists: List[str] = Field(default_factory=list)
    top_songs: List[str] = Field(default_factory=list)  # song IDs
    latest_release: Optional[Dict[str, Any]] = None
    tour_dates: List[Dict[str, Any]] = Field(default_factory=list)
    social_links: Dict[str, str] = Field(default_factory=dict)


class YouTubeMusicSong(BaseModel):
    """YouTube Music song data model"""    song_id: str
    title: str
    artists: List[YouTubeMusicArtist] = Field(default_factory=list)
    album_id: Optional[str] = None
    album_title: Optional[str] = None
    duration_seconds: int
    thumbnail_url: Optional[str] = None
    play_count: Optional[int] = None
    like_count: Optional[int] = None
    is_explicit: bool = False
    is_premium: bool = False
    release_date: Optional[datetime] = None
    genres: List[str] = Field(default_factory=list)
    lyrics: Optional[str] = None
    language: Optional[str] = None
    isrc: Optional[str] = None
    audio_quality: YouTubeMusicQuality = YouTubeMusicQuality.MEDIUM
    stream_url: Optional[str] = None
    download_url: Optional[str] = None
    is_available: bool = True
    availability_regions: List[str] = Field(default_factory=list)
    track_number: Optional[int] = None
    disc_number: Optional[int] = None
    bpm: Optional[int] = None
    key: Optional[str] = None
    mood: Optional[str] = None
    energy_level: Optional[float] = None
    danceability: Optional[float] = None
    valence: Optional[float] = None
    similarity_score: Optional[float] = None
    protection_status: str = "unprotected"


class YouTubeMusicAlbum(BaseModel):
    """YouTube Music album data model"""    album_id: str
    title: str
    artists: List[YouTubeMusicArtist] = Field(default_factory=list)
    release_date: datetime
    thumbnail_url: Optional[str] = None
    total_tracks: int
    duration_seconds: int
    genre: Optional[str] = None
    label: Optional[str] = None
    copyright_info: Optional[str] = None
    is_explicit: bool = False
    album_type: str = "album"  # album, single, EP
    tracks: List[YouTubeMusicSong] = Field(default_factory=list)
    play_count: Optional[int] = None
    description: Optional[str] = None
    upc: Optional[str] = None
    is_available: bool = True
    availability_regions: List[str] = Field(default_factory=list)


class YouTubeMusicPlaylist(BaseModel):
    """YouTube Music playlist data model"""    playlist_id: str
    title: str
    description: Optional[str] = None
    creator_name: str
    creator_id: str
    thumbnail_url: Optional[str] = None
    playlist_type: YouTubeMusicPlaylistType
    is_public: bool = True
    total_tracks: int
    total_duration_seconds: int
    created_at: datetime
    updated_at: datetime
    tracks: List[YouTubeMusicSong] = Field(default_factory=list)
    followers_count: Optional[int] = None
    play_count: Optional[int] = None
    like_count: Optional[int] = None
    is_collaborative: bool = False
    tags: List[str] = Field(default_factory=list)
    mood: Optional[str] = None
    activity: Optional[str] = None
    genre: Optional[str] = None


class YouTubeMusicPodcast(BaseModel):
    """YouTube Music podcast data model"""    podcast_id: str
    title: str
    description: Optional[str] = None
    creator_name: str
    creator_id: str
    thumbnail_url: Optional[str] = None
    total_episodes: int
    subscriber_count: Optional[int] = None
    is_explicit: bool = False
    language: Optional[str] = None
    category: Optional[str] = None
    latest_episode: Optional[Dict[str, Any]] = None
    episodes: List[Dict[str, Any]] = Field(default_factory=list)
    rss_feed: Optional[str] = None


class YouTubeMusicSearchResults(BaseModel):
    """YouTube Music search results data model"""    query: str
    total_results: int
    songs: List[YouTubeMusicSong] = Field(default_factory=list)
    albums: List[YouTubeMusicAlbum] = Field(default_factory=list)
    artists: List[YouTubeMusicArtist] = Field(default_factory=list)
    playlists: List[YouTubeMusicPlaylist] = Field(default_factory=list)
    podcasts: List[YouTubeMusicPodcast] = Field(default_factory=list)
    search_type: str
    filters_applied: Dict[str, Any]
    search_timestamp: datetime
    has_more: bool = False
    next_cursor: Optional[str] = None


class YouTubeMusicAnalytics(BaseModel):
    """YouTube Music analytics data model"""    user_id: str
    analysis_period: Tuple[datetime, datetime]
    total_listening_time_seconds: int
    total_songs_played: int
    unique_songs_played: int
    total_artists_listened: int
    unique_artists_listened: int
    top_songs: List[str]  # song IDs
    top_artists: List[str]  # artist IDs
    top_albums: List[str]  # album IDs
    top_genres: List[str]
    listening_patterns: Dict[str, Any]
    peak_listening_hours: List[int]
    average_session_duration: float
    skip_rate: float
    repeat_rate: float
    discovery_rate: float
    playlist_creation_count: int
    liked_songs_count: int
    shared_content_count: int
    mood_distribution: Dict[str, int]
    device_usage: Dict[str, int]
    offline_listening_percentage: float
    premium_features_usage: Dict[str, int]
    similarity_violations: int
    protection_violations: int


class YouTubeMusicCrawler(BaseCrawler):
    """    Ultra-Advanced YouTube Music Platform Crawler
    
    Provides comprehensive crawling and monitoring capabilities for YouTube Music platform,
    specializing in music discovery, playlist monitoring, and artist analytics.
    """    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.base_url = "https://music.youtube.com"
        self.api_base = "https://music.youtube.com/youtubei/v1"
        
        # Authentication
        self.api_key: Optional[str] = config.get('api_key')
        self.access_token: Optional[str] = None
        self.user_agent: str = config.get('user_agent', 'Mozilla/5.0 (compatible; YouTubeMusicCrawler/1.0)')
        self.client_name = "WEB_REMIX"
        self.client_version = "1.20231127.01.00"
        
        # Rate limiting - YouTube Music API limits
        self.rate_limiter = RateLimiter(
            requests_per_minute=100,
            requests_per_hour=10000,
            burst_limit=20
        )
        
        # Cache management
        self.cache_manager = CacheManager(
            cache_ttl=3600,  # 1 hour for music data
            max_cache_size=10000
        )
        
        # Content protection
        self.content_encryption = ContentEncryption()
        self.content_fingerprinter = ContentFingerprinter()
        
        # Monitoring configuration
        self.monitored_artists: Set[str] = set()
        self.monitored_playlists: Set[str] = set()
        self.protected_content: Set[str] = set()
        self.similarity_threshold = config.get('similarity_threshold', 0.85)
        
        # YouTube Music-specific settings
        self.track_lyrics = config.get('track_lyrics', True)
        self.monitor_new_releases = config.get('monitor_new_releases', True)
        self.analyze_audio_features = config.get('analyze_audio_features', True)
        self.quality_preference = YouTubeMusicQuality(config.get('quality_preference', 'high'))
        
        # Client context for API requests
        self.client_context = {
            "client": {
                "clientName": self.client_name,
                "clientVersion": self.client_version,
                "gl": "US",
                "hl": "en"
            }
        }
        
        logger.info("YouTube Music crawler initialized with ultra-advanced music monitoring")

    async def authenticate(self, api_key: str = None, access_token: str = None) -> bool:
        """        Authenticate with YouTube Music API
        
        Args:
            api_key: YouTube Data API key
            access_token: OAuth access token
            
        Returns:
            bool: Authentication success status
        """        try:
            if api_key:
                self.api_key = api_key
            
            if access_token:
                self.access_token = access_token
                self.session.headers.update({
                    'Authorization': f'Bearer {access_token}'
                })
            
            self.session.headers.update({
                'User-Agent': self.user_agent,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
            
            # Verify authentication with a simple request
            test_params = {
                'key': self.api_key,
                'part': 'snippet',
                'maxResults': 1,
                'q': 'test',
                'type': 'video'
            }
            
            async with self.session.get(
                "https://www.googleapis.com/youtube/v3/search",
                params=test_params
            ) as response:
                if response.status == 200:
                    logger.info("YouTube Music authentication successful")
                    return True
                else:
                    logger.error(f"Authentication verification failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def search_content(
        self,
        query: str = "",
        content_type: Optional[YouTubeMusicContentType] = None,
        genre: Optional[str] = None,
        limit: int = 100
    ) -> YouTubeMusicSearchResults:
        """        Search YouTube Music content with advanced filtering
        
        Args:
            query: Search query
            content_type: Type of content to search
            genre: Genre filter
            limit: Maximum results
            
        Returns:
            YouTubeMusicSearchResults: Comprehensive search results
        """        await self.rate_limiter.acquire()
        
        try:
            results = YouTubeMusicSearchResults(
                query=query,
                total_results=0,
                search_type="comprehensive",
                filters_applied={
                    "content_type": content_type.value if content_type else None,
                    "genre": genre
                },
                search_timestamp=datetime.utcnow()
            )
            
            # Search songs
            if not content_type or content_type == YouTubeMusicContentType.SONG:
                songs = await self._search_songs(query, genre, limit // 5)
                results.songs = songs
                results.total_results += len(songs)
            
            # Search albums
            if not content_type or content_type == YouTubeMusicContentType.ALBUM:
                albums = await self._search_albums(query, genre, limit // 5)
                results.albums = albums
                results.total_results += len(albums)
            
            # Search artists
            if not content_type or content_type == YouTubeMusicContentType.ARTIST:
                artists = await self._search_artists(query, genre, limit // 5)
                results.artists = artists
                results.total_results += len(artists)
            
            # Search playlists
            if not content_type or content_type == YouTubeMusicContentType.PLAYLIST:
                playlists = await self._search_playlists(query, limit // 5)
                results.playlists = playlists
                results.total_results += len(playlists)
            
            # Search podcasts
            if not content_type or content_type == YouTubeMusicContentType.PODCAST:
                podcasts = await self._search_podcasts(query, limit // 5)
                results.podcasts = podcasts
                results.total_results += len(podcasts)
            
            # Process content for protection
            for song in results.songs:
                song.similarity_score = await self._calculate_similarity(song)
                song.protection_status = await self._check_protection_status(song)
            
            logger.info(f"YouTube Music search completed: {results.total_results} total results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return YouTubeMusicSearchResults(
                query=query,
                total_results=0,
                search_type="error",
                filters_applied={},
                search_timestamp=datetime.utcnow()
            )

    async def monitor_content(
        self,
        artist_ids: List[str] = None,
        playlist_ids: List[str] = None,
        keywords: List[str] = None,
        check_interval: int = 3600  # 1 hour for music content
    ) -> AsyncGenerator[YouTubeMusicSong, None]:
        """        Real-time content monitoring for YouTube Music
        
        Args:
            artist_ids: Artists to monitor for new releases
            playlist_ids: Playlists to monitor for updates
            keywords: Keywords to monitor
            check_interval: Check interval in seconds
            
        Yields:
            YouTubeMusicSong: New songs detected
        """        artist_ids = artist_ids or []
        playlist_ids = playlist_ids or []
        keywords = keywords or []
        
        self.monitored_artists.update(artist_ids)
        self.monitored_playlists.update(playlist_ids)
        
        logger.info(f"Starting YouTube Music monitoring for {len(artist_ids)} artists, {len(playlist_ids)} playlists")
        
        seen_songs = set()
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                
                # Monitor artists for new releases
                for artist_id in artist_ids:
                    try:
                        new_releases = await self._get_artist_new_releases(artist_id)
                        
                        for song in new_releases:
                            if song.song_id not in seen_songs:
                                # Enhanced monitoring analysis
                                song.similarity_score = await self._calculate_similarity(song)
                                song.protection_status = await self._check_protection_status(song)
                                
                                seen_songs.add(song.song_id)
                                
                                logger.info(f"New release from artist {artist_id}: {song.title}")
                                yield song
                    
                    except Exception as e:
                        logger.error(f"Error monitoring artist {artist_id}: {str(e)}")
                        continue
                
                # Monitor playlists for updates
                for playlist_id in playlist_ids:
                    try:
                        playlist_updates = await self._get_playlist_updates(playlist_id)
                        
                        for song in playlist_updates:
                            if song.song_id not in seen_songs:
                                song.similarity_score = await self._calculate_similarity(song)
                                song.protection_status = await self._check_protection_status(song)
                                
                                seen_songs.add(song.song_id)
                                
                                logger.info(f"New song in playlist {playlist_id}: {song.title}")
                                yield song
                    
                    except Exception as e:
                        logger.error(f"Error monitoring playlist {playlist_id}: {str(e)}")
                        continue
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(300)

    async def detect_similarity(
        self,
        target_song: YouTubeMusicSong,
        comparison_set: List[YouTubeMusicSong],
        threshold: float = None
    ) -> List[Tuple[YouTubeMusicSong, float]]:
        """        Detect song similarity for content protection
        
        Args:
            target_song: Song to compare
            comparison_set: Songs to compare against
            threshold: Similarity threshold
            
        Returns:
            List[Tuple[YouTubeMusicSong, float]]: Similar songs with scores
        """        threshold = threshold or self.similarity_threshold
        similar_songs = []
        
        try:
            target_features = await self._extract_song_features(target_song)
            
            for song in comparison_set:
                if song.song_id == target_song.song_id:
                    continue
                
                comp_features = await self._extract_song_features(song)
                similarity_score = await self._calculate_feature_similarity(
                    target_features, comp_features
                )
                
                if similarity_score >= threshold:
                    similar_songs.append((song, similarity_score))
            
            similar_songs.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Similarity detection: {len(similar_songs)} matches found")
            return similar_songs
            
        except Exception as e:
            logger.error(f"Similarity detection error: {str(e)}")
            return []

    async def get_analytics(
        self,
        user_id: str,
        analysis_period: Tuple[datetime, datetime]
    ) -> YouTubeMusicAnalytics:
        """        Generate comprehensive analytics for YouTube Music user
        
        Args:
            user_id: User ID to analyze
            analysis_period: Analysis time period
            
        Returns:
            YouTubeMusicAnalytics: Comprehensive analytics data
        """        try:
            start_time, end_time = analysis_period
            
            # Get user's listening history
            listening_history = await self._get_user_listening_history(user_id, start_time, end_time)
            
            if not listening_history:
                return YouTubeMusicAnalytics(
                    user_id=user_id,
                    analysis_period=analysis_period,
                    total_listening_time_seconds=0,
                    total_songs_played=0,
                    unique_songs_played=0,
                    total_artists_listened=0,
                    unique_artists_listened=0,
                    top_songs=[],
                    top_artists=[],
                    top_albums=[],
                    top_genres=[],
                    listening_patterns={},
                    peak_listening_hours=[],
                    average_session_duration=0.0,
                    skip_rate=0.0,
                    repeat_rate=0.0,
                    discovery_rate=0.0,
                    playlist_creation_count=0,
                    liked_songs_count=0,
                    shared_content_count=0,
                    mood_distribution={},
                    device_usage={},
                    offline_listening_percentage=0.0,
                    premium_features_usage={},
                    similarity_violations=0,
                    protection_violations=0
                )
            
            # Calculate basic metrics
            total_songs_played = len(listening_history)
            unique_songs = set(entry['song_id'] for entry in listening_history)
            unique_songs_played = len(unique_songs)
            
            # Calculate listening time
            total_listening_time = sum(entry.get('duration_played', 0) for entry in listening_history)
            
            # Artist analysis
            artist_counts = {}
            for entry in listening_history:
                for artist in entry.get('artists', []):
                    artist_counts[artist] = artist_counts.get(artist, 0) + 1
            
            top_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            top_artists = [artist[0] for artist in top_artists]
            unique_artists_listened = len(artist_counts)
            
            # Song popularity
            song_counts = {}
            for entry in listening_history:
                song_id = entry['song_id']
                song_counts[song_id] = song_counts.get(song_id, 0) + 1
            
            top_songs = sorted(song_counts.items(), key=lambda x: x[1], reverse=True)[:50]
            top_songs = [song[0] for song in top_songs]
            
            # Genre analysis
            genre_counts = {}
            for entry in listening_history:
                for genre in entry.get('genres', []):
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
            
            top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_genres = [genre[0] for genre in top_genres]
            
            # Listening patterns
            hour_counts = {}
            for entry in listening_history:
                hour = entry.get('timestamp', datetime.utcnow()).hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            peak_listening_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            peak_listening_hours = [hour[0] for hour in peak_listening_hours]
            
            # Calculate rates
            completed_plays = sum(1 for entry in listening_history if entry.get('completion_rate', 0) > 0.8)
            skip_rate = 1.0 - (completed_plays / total_songs_played) if total_songs_played > 0 else 0.0
            
            repeat_songs = sum(1 for count in song_counts.values() if count > 1)
            repeat_rate = repeat_songs / unique_songs_played if unique_songs_played > 0 else 0.0
            
            # Session analysis
            sessions = await self._group_listening_sessions(listening_history)
            average_session_duration = sum(s['duration'] for s in sessions) / len(sessions) if sessions else 0.0
            
            analytics = YouTubeMusicAnalytics(
                user_id=user_id,
                analysis_period=analysis_period,
                total_listening_time_seconds=total_listening_time,
                total_songs_played=total_songs_played,
                unique_songs_played=unique_songs_played,
                total_artists_listened=sum(artist_counts.values()),
                unique_artists_listened=unique_artists_listened,
                top_songs=top_songs,
                top_artists=top_artists,
                top_albums=[],  # Would need album data
                top_genres=top_genres,
                listening_patterns={
                    "hourly_distribution": hour_counts,
                    "daily_average": total_songs_played / max((end_time - start_time).days, 1)
                },
                peak_listening_hours=peak_listening_hours,
                average_session_duration=average_session_duration,
                skip_rate=skip_rate,
                repeat_rate=repeat_rate,
                discovery_rate=0.0,  # Would need discovery tracking
                playlist_creation_count=0,  # Would need playlist data
                liked_songs_count=0,  # Would need likes data
                shared_content_count=0,  # Would need sharing data
                mood_distribution={},  # Would need mood analysis
                device_usage={},  # Would need device data
                offline_listening_percentage=0.0,  # Would need offline data
                premium_features_usage={},  # Would need premium feature data
                similarity_violations=0,  # Would need similarity analysis
                protection_violations=0  # Would need protection analysis
            )
            
            logger.info(f"Analytics generated for user {user_id}: {total_songs_played} songs, {unique_artists_listened} artists")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics generation error: {str(e)}")
            return YouTubeMusicAnalytics(
                user_id=user_id,
                analysis_period=analysis_period,
                total_listening_time_seconds=0,
                total_songs_played=0,
                unique_songs_played=0,
                total_artists_listened=0,
                unique_artists_listened=0,
                top_songs=[],
                top_artists=[],
                top_albums=[],
                top_genres=[],
                listening_patterns={},
                peak_listening_hours=[],
                average_session_duration=0.0,
                skip_rate=0.0,
                repeat_rate=0.0,
                discovery_rate=0.0,
                playlist_creation_count=0,
                liked_songs_count=0,
                shared_content_count=0,
                mood_distribution={},
                device_usage={},
                offline_listening_percentage=0.0,
                premium_features_usage={},
                similarity_violations=0,
                protection_violations=0
            )

    # Helper methods
    
    async def _search_songs(self, query: str, genre: Optional[str], limit: int) -> List[YouTubeMusicSong]:
        """Search for songs"""        try:
            search_params = {
                'key': self.api_key,
                'part': 'snippet',
                'maxResults': limit,
                'q': f"{query} {genre}" if genre else query,
                'type': 'video',
                'videoCategoryId': '10'  # Music category
            }
            
            async with self.session.get(
                "https://www.googleapis.com/youtube/v3/search",
                params=search_params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    songs = []
                    
                    for item in data.get('items', []):
                        song = await self._parse_song_from_video(item)
                        if song:
                            songs.append(song)
                    
                    return songs
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Song search error: {str(e)}")
            return []

    async def _search_albums(self, query: str, genre: Optional[str], limit: int) -> List[YouTubeMusicAlbum]:
        """Search for albums"""        # Implementation would require YouTube Music specific album search
        return []

    async def _search_artists(self, query: str, genre: Optional[str], limit: int) -> List[YouTubeMusicArtist]:
        """Search for artists"""        try:
            search_params = {
                'key': self.api_key,
                'part': 'snippet',
                'maxResults': limit,
                'q': f"artist {query} {genre}" if genre else f"artist {query}",
                'type': 'channel'
            }
            
            async with self.session.get(
                "https://www.googleapis.com/youtube/v3/search",
                params=search_params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    artists = []
                    
                    for item in data.get('items', []):
                        artist = await self._parse_artist_from_channel(item)
                        if artist:
                            artists.append(artist)
                    
                    return artists
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Artist search error: {str(e)}")
            return []

    async def _search_playlists(self, query: str, limit: int) -> List[YouTubeMusicPlaylist]:
        """Search for playlists"""        try:
            search_params = {
                'key': self.api_key,
                'part': 'snippet',
                'maxResults': limit,
                'q': query,
                'type': 'playlist'
            }
            
            async with self.session.get(
                "https://www.googleapis.com/youtube/v3/search",
                params=search_params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    playlists = []
                    
                    for item in data.get('items', []):
                        playlist = await self._parse_playlist_from_search(item)
                        if playlist:
                            playlists.append(playlist)
                    
                    return playlists
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Playlist search error: {str(e)}")
            return []

    async def _search_podcasts(self, query: str, limit: int) -> List[YouTubeMusicPodcast]:
        """Search for podcasts"""        # Implementation would require podcast-specific search
        return []

    async def _parse_song_from_video(self, video_data: Dict[str, Any]) -> Optional[YouTubeMusicSong]:
        """Parse song data from YouTube video"""        try:
            snippet = video_data.get('snippet', {})
            video_id = video_data.get('id', {}).get('videoId', '')
            
            # Extract artist and title from video title
            title = snippet.get('title', '')
            channel_title = snippet.get('channelTitle', '')
            
            # Create simplified artist
            artist = YouTubeMusicArtist(
                artist_id=snippet.get('channelId', ''),
                name=channel_title,
                channel_id=snippet.get('channelId', '')
            )
            
            # Get video details for duration
            duration_seconds = 0  # Would need additional API call
            
            song = YouTubeMusicSong(
                song_id=video_id,
                title=title,
                artists=[artist],
                duration_seconds=duration_seconds,
                thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url'),
                release_date=datetime.fromisoformat(snippet.get('publishedAt', datetime.utcnow().isoformat()))
            )
            
            return song
            
        except Exception as e:
            logger.error(f"Error parsing song: {str(e)}")
            return None

    async def _parse_artist_from_channel(self, channel_data: Dict[str, Any]) -> Optional[YouTubeMusicArtist]:
        """Parse artist data from YouTube channel"""        try:
            snippet = channel_data.get('snippet', {})
            channel_id = channel_data.get('id', {}).get('channelId', '')
            
            artist = YouTubeMusicArtist(
                artist_id=channel_id,
                name=snippet.get('title', ''),
                channel_id=channel_id,
                description=snippet.get('description', ''),
                thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url')
            )
            
            return artist
            
        except Exception as e:
            logger.error(f"Error parsing artist: {str(e)}")
            return None

    async def _parse_playlist_from_search(self, playlist_data: Dict[str, Any]) -> Optional[YouTubeMusicPlaylist]:
        """Parse playlist data from search result"""        try:
            snippet = playlist_data.get('snippet', {})
            playlist_id = playlist_data.get('id', {}).get('playlistId', '')
            
            playlist = YouTubeMusicPlaylist(
                playlist_id=playlist_id,
                title=snippet.get('title', ''),
                description=snippet.get('description', ''),
                creator_name=snippet.get('channelTitle', ''),
                creator_id=snippet.get('channelId', ''),
                thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url'),
                playlist_type=YouTubeMusicPlaylistType.USER_CREATED,
                total_tracks=0,  # Would need additional API call
                total_duration_seconds=0,
                created_at=datetime.fromisoformat(snippet.get('publishedAt', datetime.utcnow().isoformat())),
                updated_at=datetime.utcnow()
            )
            
            return playlist
            
        except Exception as e:
            logger.error(f"Error parsing playlist: {str(e)}")
            return None

    async def _get_artist_new_releases(self, artist_id: str) -> List[YouTubeMusicSong]:
        """Get new releases from artist"""        try:
            # Get recent uploads from artist's channel
            search_params = {
                'key': self.api_key,
                'channelId': artist_id,
                'part': 'snippet',
                'order': 'date',
                'maxResults': 10,
                'publishedAfter': (datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'
            }
            
            async with self.session.get(
                "https://www.googleapis.com/youtube/v3/search",
                params=search_params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    new_releases = []
                    
                    for item in data.get('items', []):
                        song = await self._parse_song_from_video(item)
                        if song:
                            new_releases.append(song)
                    
                    return new_releases
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting new releases: {str(e)}")
            return []

    async def _get_playlist_updates(self, playlist_id: str) -> List[YouTubeMusicSong]:
        """Get recent updates to playlist"""        # Implementation would require tracking playlist changes
        return []

    async def _extract_song_features(self, song: YouTubeMusicSong) -> Dict[str, Any]:
        """Extract features for similarity comparison"""        features = {
            "title": song.title.lower(),
            "artists": set(artist.name.lower() for artist in song.artists),
            "album": (song.album_title or "").lower(),
            "duration": song.duration_seconds,
            "genres": set(genre.lower() for genre in song.genres),
            "language": song.language,
            "is_explicit": song.is_explicit,
            "release_year": song.release_date.year if song.release_date else None,
            "bpm": song.bpm,
            "key": song.key,
            "energy_level": song.energy_level or 0.0,
            "danceability": song.danceability or 0.0,
            "valence": song.valence or 0.0
        }
        return features

    async def _calculate_feature_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between song features"""        try:
            scores = []
            
            # Title similarity
            title_sim = SequenceMatcher(
                None, features1.get("title", ""), features2.get("title", "")
            ).ratio()
            scores.append(title_sim * 0.3)  # 30% weight
            
            # Artist similarity
            artists1 = features1.get("artists", set())
            artists2 = features2.get("artists", set())
            if artists1 and artists2:
                artist_sim = len(artists1.intersection(artists2)) / len(artists1.union(artists2))
                scores.append(artist_sim * 0.3)  # 30% weight
            
            # Duration similarity
            duration1 = features1.get("duration", 0)
            duration2 = features2.get("duration", 0)
            if duration1 and duration2:
                duration_diff = abs(duration1 - duration2) / max(duration1, duration2)
                duration_sim = 1.0 - min(duration_diff, 1.0)
                scores.append(duration_sim * 0.2)  # 20% weight
            
            # Genre similarity
            genres1 = features1.get("genres", set())
            genres2 = features2.get("genres", set())
            if genres1 and genres2:
                genre_sim = len(genres1.intersection(genres2)) / len(genres1.union(genres2))
                scores.append(genre_sim * 0.1)  # 10% weight
            
            # Audio features similarity
            audio_features = ["energy_level", "danceability", "valence"]
            audio_sim = 0.0
            for feature in audio_features:
                val1 = features1.get(feature, 0.0)
                val2 = features2.get(feature, 0.0)
                feature_sim = 1.0 - abs(val1 - val2)
                audio_sim += feature_sim
            
            if audio_features:
                scores.append((audio_sim / len(audio_features)) * 0.1)  # 10% weight
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Feature similarity calculation error: {str(e)}")
            return 0.0

    async def _get_user_listening_history(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Get user's listening history"""        # Implementation would require user data access
        return []

    async def _group_listening_sessions(self, listening_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group listening history into sessions"""        sessions = []
        current_session = []
        session_gap_threshold = 1800  # 30 minutes
        
        for entry in sorted(listening_history, key=lambda x: x.get('timestamp', datetime.utcnow())):
            if not current_session:
                current_session = [entry]
            else:
                last_entry = current_session[-1]
                time_gap = (entry.get('timestamp', datetime.utcnow()) - 
                          last_entry.get('timestamp', datetime.utcnow())).total_seconds()
                
                if time_gap <= session_gap_threshold:
                    current_session.append(entry)
                else:
                    # End current session, start new one
                    if current_session:
                        session_duration = sum(e.get('duration_played', 0) for e in current_session)
                        sessions.append({
                            'duration': session_duration,
                            'song_count': len(current_session),
                            'start_time': current_session[0].get('timestamp'),
                            'end_time': current_session[-1].get('timestamp')
                        })
                    current_session = [entry]
        
        # Add final session
        if current_session:
            session_duration = sum(e.get('duration_played', 0) for e in current_session)
            sessions.append({
                'duration': session_duration,
                'song_count': len(current_session),
                'start_time': current_session[0].get('timestamp'),
                'end_time': current_session[-1].get('timestamp')
            })
        
        return sessions

    async def _calculate_similarity(self, song: YouTubeMusicSong) -> float:
        """Calculate similarity score against protected content"""        # Simplified similarity calculation
        return 0.0

    async def _check_protection_status(self, song: YouTubeMusicSong) -> str:
        """Check protection status of song"""        if song.song_id in self.protected_content:
            return "protected"
        return "unprotected"

    async def close(self):
        """Close crawler and cleanup resources"""        try:
            await self.cache_manager.close()
            await super().close()
            logger.info("YouTube Music crawler closed successfully")
        except Exception as e:
            logger.error(f"Error closing crawler: {str(e)}")
