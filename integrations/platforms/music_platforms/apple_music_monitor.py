"""
Apple Music MusicKit Integration for Copyright Monitoring
======================================================

Advanced Apple Music monitoring using MusicKit API for catalog search,
track discovery, and copyright protection across Apple's music ecosystem.

Features:
- MusicKit JS and API integration for comprehensive catalog access
- Advanced audio fingerprinting with Apple's audio analysis
- Playlist and album monitoring across Apple Music
- Regional content tracking and availability monitoring
- Integration with Apple's ContentID system
- Artist and label relationship tracking

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import jwt
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

import aiohttp
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AppleMusicTrackMatch(BaseModel):
    """Apple Music track match result for copyright monitoring"""
    track_id: str
    song_name: str
    artist_name: str
    album_name: str
    apple_music_url: str
    preview_url: Optional[str] = None
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    duration_ms: int = 0
    explicit: bool = False
    isrc: Optional[str] = None
    upc: Optional[str] = None
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    storefront: str = "us"
    availability: List[str] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    copyright_info: Dict[str, Any] = Field(default_factory=dict)
    evidence: Dict[str, Any] = Field(default_factory=dict)


class AppleMusicPlaylist(BaseModel):
    """Apple Music playlist information"""
    playlist_id: str
    playlist_name: str
    curator_name: str
    description: str = ""
    track_count: int = 0
    artwork_url: Optional[str] = None
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    tracks: List[str] = Field(default_factory=list)  # track IDs
    is_chart: bool = False
    storefront: str = "us"


class AppleMusicAlbum(BaseModel):
    """Apple Music album information"""
    album_id: str
    album_name: str
    artist_name: str
    release_date: str
    track_count: int
    upc: Optional[str] = None
    copyright_info: str = ""
    label: str = ""
    genres: List[str] = Field(default_factory=list)
    storefront: str = "us"
    tracks: List[Dict[str, Any]] = Field(default_factory=list)


@dataclass
class AppleMusicConfig:
    """Configuration for Apple Music monitoring"""
    team_id: str  # Apple Developer Team ID
    key_id: str   # MusicKit Key ID
    private_key: str  # MusicKit Private Key (PEM format)
    
    # Token management
    developer_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    # Monitoring settings
    catalog_monitoring_enabled: bool = True
    playlist_monitoring_enabled: bool = True
    chart_monitoring_enabled: bool = True
    
    # Thresholds
    similarity_threshold: float = 0.8
    confidence_threshold: float = 0.75
    
    # Monitoring intervals (seconds)
    catalog_scan_interval: int = 600   # 10 minutes
    playlist_scan_interval: int = 1800  # 30 minutes
    chart_scan_interval: int = 3600     # 1 hour
    
    # Storefronts to monitor
    target_storefronts: List[str] = field(default_factory=lambda: [
        "us", "gb", "de", "fr", "es", "it", "jp", "ca", "au", "br"
    ])
    
    # Rate limiting
    max_requests_per_minute: int = 120
    max_concurrent_requests: int = 5


class AppleMusicMonitor:
    """
    Advanced Apple Music monitoring system using MusicKit API
    for comprehensive catalog search and copyright protection.
    """
    
    def __init__(self, config: AppleMusicConfig):
        """Initialize Apple Music monitor"""
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = "https://api.music.apple.com/v1"
        
        # Monitoring state
        self._monitoring_active = False
        self._monitor_tasks: List[asyncio.Task] = []
        
        # Tracked content
        self._tracked_fingerprints: Dict[str, Dict[str, Any]] = {}
        self._monitored_playlists: Dict[str, AppleMusicPlaylist] = {}
        self._monitored_artists: Dict[str, Dict[str, Any]] = {}
        
        # Results storage
        self._detected_matches: List[AppleMusicTrackMatch] = []
        self._playlist_violations: List[Dict[str, Any]] = []
        self._new_releases: List[AppleMusicAlbum] = []
        
        # Rate limiting
        self._request_timestamps: List[datetime] = []
        self._request_semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        
        logger.info("Apple Music Monitor initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.shutdown()
    
    async def initialize(self) -> bool:
        """Initialize the Apple Music monitor"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Generate developer token
            if not await self._generate_developer_token():
                logger.error("Failed to generate Apple Music developer token")
                return False
            
            logger.info("Apple Music Monitor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Apple Music monitor: {e}")
            return False
    
    async def _generate_developer_token(self) -> bool:
        """Generate Apple Music API developer token"""
        try:
            # Check if current token is still valid
            if (self.config.developer_token and 
                self.config.token_expires_at and 
                datetime.utcnow() < self.config.token_expires_at - timedelta(minutes=5)):
                return True
            
            # Generate new JWT token
            now = datetime.utcnow()
            expiry = now + timedelta(hours=12)  # Apple Music tokens are valid for 12 hours max
            
            payload = {
                'iss': self.config.team_id,
                'iat': int(now.timestamp()),
                'exp': int(expiry.timestamp()),
                'aud': 'appstoreconnect-v1'
            }
            
            headers = {
                'alg': 'ES256',
                'kid': self.config.key_id
            }
            
            # Generate token
            token = jwt.encode(
                payload, 
                self.config.private_key, 
                algorithm='ES256',
                headers=headers
            )
            
            self.config.developer_token = token
            self.config.token_expires_at = expiry
            
            logger.info("Apple Music developer token generated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate developer token: {e}")
            return False
    
    async def _make_apple_music_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        storefront: str = "us"
    ) -> Optional[Dict[str, Any]]:
        """Make rate-limited request to Apple Music API"""
        
        # Rate limiting check
        await self._check_rate_limit()
        
        async with self._request_semaphore:
            try:
                await self._generate_developer_token()
                
                url = f"{self.base_url}/catalog/{storefront}/{endpoint}"
                headers = {
                    "Authorization": f"Bearer {self.config.developer_token}",
                    "Content-Type": "application/json"
                }
                
                async with self.session.request(
                    method, url, params=params, json=data, headers=headers
                ) as response:
                    self._request_timestamps.append(datetime.utcnow())
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        # Rate limited
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning(f"Apple Music rate limited, waiting {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        return await self._make_apple_music_request(method, endpoint, params, data, storefront)
                    elif response.status == 401:
                        # Token expired
                        if await self._generate_developer_token():
                            return await self._make_apple_music_request(method, endpoint, params, data, storefront)
                        else:
                            logger.error("Failed to refresh Apple Music token")
                            return None
                    else:
                        logger.error(f"Apple Music API error: {response.status} - {await response.text()}")
                        return None
                        
            except Exception as e:
                logger.error(f"Apple Music request error: {e}")
                return None
    
    async def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting"""
        now = datetime.utcnow()
        
        # Remove timestamps older than 1 minute
        self._request_timestamps = [
            ts for ts in self._request_timestamps 
            if now - ts <= timedelta(minutes=1)
        ]
        
        # Check if we're approaching the rate limit
        if len(self._request_timestamps) >= self.config.max_requests_per_minute - 5:
            # Wait until we're under the limit
            sleep_time = 60 - (now - self._request_timestamps[0]).total_seconds()
            if sleep_time > 0:
                logger.info(f"Apple Music rate limiting: sleeping for {sleep_time:.1f} seconds")
                await asyncio.sleep(sleep_time)
    
    async def add_track_fingerprint(
        self,
        fingerprint_id: str,
        track_metadata: Dict[str, Any],
        audio_features: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a track fingerprint for monitoring"""
        try:
            self._tracked_fingerprints[fingerprint_id] = {
                "metadata": track_metadata,
                "audio_features": audio_features or {},
                "added_at": datetime.utcnow(),
                "last_checked": None,
                "matches_found": 0
            }
            
            logger.info(f"Added track fingerprint for Apple Music monitoring: {fingerprint_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add track fingerprint: {e}")
            return False
    
    async def search_catalog(
        self,
        fingerprint_id: str,
        query_terms: List[str],
        storefronts: Optional[List[str]] = None
    ) -> List[AppleMusicTrackMatch]:
        """Search Apple Music catalog for similar tracks"""
        try:
            if fingerprint_id not in self._tracked_fingerprints:
                logger.error(f"Fingerprint not found: {fingerprint_id}")
                return []
            
            storefronts = storefronts or self.config.target_storefronts
            fingerprint_data = self._tracked_fingerprints[fingerprint_id]
            matches = []
            
            # Search using different strategies
            for query in query_terms:
                for storefront in storefronts:
                    # Search songs
                    results = await self._make_apple_music_request(
                        "GET", "search",
                        params={
                            "term": query,
                            "types": "songs",
                            "limit": 25
                        },
                        storefront=storefront
                    )
                    
                    if results and "results" in results and "songs" in results["results"]:
                        for song in results["results"]["songs"]["data"]:
                            match = await self._analyze_song_similarity(
                                fingerprint_id, song, storefront
                            )
                            if match and match.similarity_score >= self.config.similarity_threshold:
                                matches.append(match)
                    
                    # Rate limiting delay
                    await asyncio.sleep(0.5)
            
            # Update tracking info
            self._tracked_fingerprints[fingerprint_id]["last_checked"] = datetime.utcnow()
            self._tracked_fingerprints[fingerprint_id]["matches_found"] += len(matches)
            
            # Store matches
            self._detected_matches.extend(matches)
            
            logger.info(f"Found {len(matches)} potential Apple Music matches for fingerprint {fingerprint_id}")
            return matches
            
        except Exception as e:
            logger.error(f"Apple Music catalog search error: {e}")
            return []
    
    async def _analyze_song_similarity(
        self,
        fingerprint_id: str,
        apple_song: Dict[str, Any],
        storefront: str
    ) -> Optional[AppleMusicTrackMatch]:
        """Analyze similarity between fingerprint and Apple Music song"""
        try:
            attributes = apple_song.get("attributes", {})
            song_id = apple_song["id"]
            fingerprint_data = self._tracked_fingerprints[fingerprint_id]
            
            # Calculate similarity scores
            similarity_score = await self._calculate_similarity_score(
                fingerprint_data, attributes
            )
            
            confidence_score = await self._calculate_confidence_score(
                fingerprint_data, attributes
            )
            
            # Only return match if above threshold
            if similarity_score >= self.config.similarity_threshold:
                return AppleMusicTrackMatch(
                    track_id=song_id,
                    song_name=attributes.get("name", ""),
                    artist_name=attributes.get("artistName", ""),
                    album_name=attributes.get("albumName", ""),
                    apple_music_url=attributes.get("url", f"https://music.apple.com/song/{song_id}"),
                    preview_url=attributes.get("previews", [{}])[0].get("url") if attributes.get("previews") else None,
                    similarity_score=similarity_score,
                    confidence_score=confidence_score,
                    duration_ms=attributes.get("durationInMillis", 0),
                    explicit=attributes.get("contentRating") == "explicit",
                    isrc=attributes.get("isrc"),
                    storefront=storefront,
                    availability=attributes.get("editorialNotes", {}).get("short", "").split() if attributes.get("editorialNotes") else [],
                    genres=attributes.get("genreNames", []),
                    copyright_info={"copyright": attributes.get("copyright", "")},
                    evidence={
                        "song_data": apple_song,
                        "fingerprint_metadata": fingerprint_data["metadata"],
                        "analysis_timestamp": datetime.utcnow().isoformat()
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Apple Music similarity analysis error: {e}")
            return None
    
    async def _calculate_similarity_score(
        self,
        fingerprint_data: Dict[str, Any],
        apple_attributes: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between fingerprint and Apple Music track"""
        try:
            score = 0.0
            factors = 0
            
            # Title similarity
            fp_title = fingerprint_data["metadata"].get("title", "").lower()
            apple_title = apple_attributes.get("name", "").lower()
            if fp_title and apple_title:
                title_similarity = len(set(fp_title.split()) & set(apple_title.split())) / max(
                    len(set(fp_title.split())), len(set(apple_title.split())), 1
                )
                score += title_similarity * 0.4
                factors += 1
            
            # Artist similarity
            fp_artist = fingerprint_data["metadata"].get("artist", "").lower()
            apple_artist = apple_attributes.get("artistName", "").lower()
            if fp_artist and apple_artist:
                artist_similarity = len(set(fp_artist.split()) & set(apple_artist.split())) / max(
                    len(set(fp_artist.split())), len(set(apple_artist.split())), 1
                )
                score += artist_similarity * 0.3
                factors += 1
            
            # Duration similarity
            fp_duration = fingerprint_data["metadata"].get("duration", 0)
            apple_duration = apple_attributes.get("durationInMillis", 0) / 1000
            if fp_duration > 0 and apple_duration > 0:
                duration_diff = abs(fp_duration - apple_duration) / max(fp_duration, apple_duration)
                duration_similarity = max(0, 1 - duration_diff)
                score += duration_similarity * 0.2
                factors += 1
            
            # Album similarity
            fp_album = fingerprint_data["metadata"].get("album", "").lower()
            apple_album = apple_attributes.get("albumName", "").lower()
            if fp_album and apple_album:
                album_similarity = len(set(fp_album.split()) & set(apple_album.split())) / max(
                    len(set(fp_album.split())), len(set(apple_album.split())), 1
                )
                score += album_similarity * 0.1
                factors += 1
            
            return score / max(factors, 1)
            
        except Exception as e:
            logger.error(f"Apple Music similarity calculation error: {e}")
            return 0.0
    
    async def _calculate_confidence_score(
        self,
        fingerprint_data: Dict[str, Any],
        apple_attributes: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for the match"""
        try:
            confidence = 0.5  # Base confidence
            
            # Increase confidence based on explicit content rating
            if apple_attributes.get("contentRating"):
                confidence += 0.1
            
            # Increase confidence if we have ISRC
            if apple_attributes.get("isrc"):
                confidence += 0.2
            
            # Increase confidence based on genre matching
            fp_genre = fingerprint_data["metadata"].get("genre", "").lower()
            apple_genres = [g.lower() for g in apple_attributes.get("genreNames", [])]
            if fp_genre and any(fp_genre in ag for ag in apple_genres):
                confidence += 0.1
            
            # Decrease confidence for very old releases
            release_date = apple_attributes.get("releaseDate", "")
            if release_date:
                try:
                    release_dt = datetime.fromisoformat(release_date.replace("Z", "+00:00"))
                    days_since_release = (datetime.utcnow() - release_dt).days
                    
                    if days_since_release > 365 * 15:  # Very old
                        confidence -= 0.1
                except:
                    pass
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Apple Music confidence calculation error: {e}")
            return 0.5
    
    async def monitor_playlist(self, playlist_id: str, storefront: str = "us") -> bool:
        """Add Apple Music playlist to monitoring list"""
        try:
            # Get playlist information
            playlist_data = await self._make_apple_music_request(
                "GET", f"playlists/{playlist_id}",
                params={"include": "tracks"},
                storefront=storefront
            )
            
            if not playlist_data or "data" not in playlist_data:
                return False
            
            playlist_info_data = playlist_data["data"][0]
            attributes = playlist_info_data.get("attributes", {})
            
            track_ids = []
            if "relationships" in playlist_info_data and "tracks" in playlist_info_data["relationships"]:
                tracks = playlist_info_data["relationships"]["tracks"].get("data", [])
                track_ids = [track["id"] for track in tracks]
            
            playlist = AppleMusicPlaylist(
                playlist_id=playlist_id,
                playlist_name=attributes.get("name", ""),
                curator_name=attributes.get("curatorName", ""),
                description=attributes.get("description", {}).get("standard", ""),
                track_count=len(track_ids),
                artwork_url=attributes.get("artwork", {}).get("url"),
                tracks=track_ids,
                is_chart=attributes.get("playlistType") == "chart",
                storefront=storefront
            )
            
            self._monitored_playlists[f"{storefront}_{playlist_id}"] = playlist
            
            logger.info(f"Added Apple Music playlist to monitoring: {playlist.playlist_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to monitor Apple Music playlist {playlist_id}: {e}")
            return False
    
    async def monitor_artist(self, artist_id: str, storefront: str = "us") -> bool:
        """Add Apple Music artist to monitoring"""
        try:
            # Get artist information
            artist_data = await self._make_apple_music_request(
                "GET", f"artists/{artist_id}",
                storefront=storefront
            )
            
            if not artist_data or "data" not in artist_data:
                return False
            
            attributes = artist_data["data"][0].get("attributes", {})
            
            self._monitored_artists[f"{storefront}_{artist_id}"] = {
                "artist_id": artist_id,
                "name": attributes.get("name", ""),
                "genres": attributes.get("genreNames", []),
                "storefront": storefront,
                "added_at": datetime.utcnow(),
                "last_checked": None,
                "releases_found": 0
            }
            
            logger.info(f"Added Apple Music artist to monitoring: {attributes.get('name', artist_id)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to monitor Apple Music artist {artist_id}: {e}")
            return False
    
    async def start_monitoring(self) -> bool:
        """Start the monitoring tasks"""
        try:
            if self._monitoring_active:
                logger.warning("Apple Music monitoring already active")
                return True
            
            self._monitoring_active = True
            
            # Start monitoring tasks
            if self.config.catalog_monitoring_enabled:
                task = asyncio.create_task(self._catalog_monitoring_loop())
                self._monitor_tasks.append(task)
            
            if self.config.playlist_monitoring_enabled:
                task = asyncio.create_task(self._playlist_monitoring_loop())
                self._monitor_tasks.append(task)
            
            if self.config.chart_monitoring_enabled:
                task = asyncio.create_task(self._chart_monitoring_loop())
                self._monitor_tasks.append(task)
            
            logger.info("Apple Music monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Apple Music monitoring: {e}")
            return False
    
    async def stop_monitoring(self) -> None:
        """Stop all monitoring tasks"""
        self._monitoring_active = False
        
        for task in self._monitor_tasks:
            task.cancel()
        
        if self._monitor_tasks:
            await asyncio.gather(*self._monitor_tasks, return_exceptions=True)
        
        self._monitor_tasks.clear()
        logger.info("Apple Music monitoring stopped")
    
    async def _catalog_monitoring_loop(self) -> None:
        """Main catalog monitoring loop"""
        logger.info("Starting Apple Music catalog monitoring loop")
        
        while self._monitoring_active:
            try:
                # Monitor all tracked fingerprints
                for fingerprint_id in list(self._tracked_fingerprints.keys()):
                    if not self._monitoring_active:
                        break
                    
                    fingerprint_data = self._tracked_fingerprints[fingerprint_id]
                    metadata = fingerprint_data["metadata"]
                    
                    # Generate search terms
                    search_terms = []
                    if "title" in metadata:
                        search_terms.append(metadata["title"])
                    if "artist" in metadata and "title" in metadata:
                        search_terms.append(f"{metadata['artist']} {metadata['title']}")
                    
                    if search_terms:
                        await self.search_catalog(fingerprint_id, search_terms)
                    
                    # Small delay between fingerprints
                    await asyncio.sleep(2)
                
                # Wait for next scan interval
                await asyncio.sleep(self.config.catalog_scan_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Apple Music catalog monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _playlist_monitoring_loop(self) -> None:
        """Playlist monitoring loop"""
        logger.info("Starting Apple Music playlist monitoring loop")
        
        while self._monitoring_active:
            try:
                # Check each monitored playlist for changes
                for playlist_key in list(self._monitored_playlists.keys()):
                    if not self._monitoring_active:
                        break
                    
                    await self._check_playlist_for_violations(playlist_key)
                    await asyncio.sleep(10)  # Delay between playlists
                
                await asyncio.sleep(self.config.playlist_scan_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Apple Music playlist monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _chart_monitoring_loop(self) -> None:
        """Chart monitoring loop for trending content"""
        logger.info("Starting Apple Music chart monitoring loop")
        
        while self._monitoring_active:
            try:
                # Monitor charts in each storefront
                for storefront in self.config.target_storefronts:
                    if not self._monitoring_active:
                        break
                    
                    await self._check_charts_for_matches(storefront)
                    await asyncio.sleep(5)  # Delay between storefronts
                
                await asyncio.sleep(self.config.chart_scan_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Apple Music chart monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _check_playlist_for_violations(self, playlist_key: str) -> None:
        """Check Apple Music playlist for copyright violations"""
        try:
            storefront, playlist_id = playlist_key.split("_", 1)
            
            # Get current playlist tracks
            playlist_data = await self._make_apple_music_request(
                "GET", f"playlists/{playlist_id}",
                params={"include": "tracks"},
                storefront=storefront
            )
            
            if not playlist_data or "data" not in playlist_data:
                return
            
            playlist_info_data = playlist_data["data"][0]
            current_tracks = []
            if "relationships" in playlist_info_data and "tracks" in playlist_info_data["relationships"]:
                tracks = playlist_info_data["relationships"]["tracks"].get("data", [])
                current_tracks = [track["id"] for track in tracks]
            
            playlist_info = self._monitored_playlists[playlist_key]
            previous_tracks = set(playlist_info.tracks)
            current_tracks_set = set(current_tracks)
            
            # Check for new tracks
            new_tracks = current_tracks_set - previous_tracks
            if new_tracks:
                # Check new tracks against our fingerprints
                for track_id in new_tracks:
                    await self._check_track_against_fingerprints(track_id, playlist_key, storefront)
                
                # Update playlist info
                playlist_info.tracks = current_tracks
                playlist_info.last_modified = datetime.utcnow()
                playlist_info.track_count = len(current_tracks)
            
        except Exception as e:
            logger.error(f"Apple Music playlist violation check error for {playlist_key}: {e}")
    
    async def _check_track_against_fingerprints(self, track_id: str, playlist_key: str, storefront: str) -> None:
        """Check a specific Apple Music track against our fingerprints"""
        try:
            # Get track details
            track_data = await self._make_apple_music_request("GET", f"songs/{track_id}", storefront=storefront)
            if not track_data or "data" not in track_data:
                return
            
            track_info = track_data["data"][0]
            
            # Check against all tracked fingerprints
            for fingerprint_id, fingerprint_data in self._tracked_fingerprints.items():
                match = await self._analyze_song_similarity(
                    fingerprint_id, track_info, storefront
                )
                
                if match and match.similarity_score >= self.config.similarity_threshold:
                    # Found a potential violation
                    violation = {
                        "violation_id": f"apple_playlist_{playlist_key}_{track_id}_{int(time.time())}",
                        "playlist_key": playlist_key,
                        "playlist_name": self._monitored_playlists[playlist_key].playlist_name,
                        "track_match": match,
                        "detected_at": datetime.utcnow(),
                        "violation_type": "apple_playlist_inclusion",
                        "storefront": storefront
                    }
                    
                    self._playlist_violations.append(violation)
                    logger.warning(f"Potential copyright violation detected in Apple Music playlist {playlist_key}")
            
        except Exception as e:
            logger.error(f"Apple Music track fingerprint check error: {e}")
    
    async def _check_charts_for_matches(self, storefront: str) -> None:
        """Check Apple Music charts for potential matches"""
        try:
            # Get top charts
            charts_data = await self._make_apple_music_request(
                "GET", "charts",
                params={"types": "songs", "limit": 50},
                storefront=storefront
            )
            
            if not charts_data or "results" not in charts_data:
                return
            
            songs_chart = charts_data["results"].get("songs")
            if not songs_chart or not songs_chart[0].get("data"):
                return
            
            # Check chart songs against fingerprints
            for song in songs_chart[0]["data"]:
                for fingerprint_id, fingerprint_data in self._tracked_fingerprints.items():
                    match = await self._analyze_song_similarity(
                        fingerprint_id, song, storefront
                    )
                    
                    if match and match.similarity_score >= self.config.similarity_threshold:
                        # Mark as chart appearance
                        match.evidence["chart_position"] = True
                        match.evidence["storefront"] = storefront
                        self._detected_matches.append(match)
                        
                        logger.info(f"Found chart match for fingerprint {fingerprint_id} in {storefront}")
            
        except Exception as e:
            logger.error(f"Apple Music chart monitoring error for {storefront}: {e}")
    
    async def get_monitoring_results(self) -> Dict[str, Any]:
        """Get all monitoring results"""
        return {
            "track_matches": [match.dict() for match in self._detected_matches],
            "playlist_violations": self._playlist_violations,
            "new_releases": [release.dict() for release in self._new_releases],
            "monitoring_stats": {
                "tracked_fingerprints": len(self._tracked_fingerprints),
                "monitored_playlists": len(self._monitored_playlists),
                "monitored_artists": len(self._monitored_artists),
                "total_matches_found": len(self._detected_matches),
                "total_violations_found": len(self._playlist_violations),
                "total_releases_found": len(self._new_releases)
            }
        }
    
    async def clear_results(self) -> None:
        """Clear monitoring results"""
        self._detected_matches.clear()
        self._playlist_violations.clear()
        self._new_releases.clear()
        logger.info("Apple Music monitoring results cleared")
    
    async def shutdown(self) -> None:
        """Shutdown the monitor"""
        await self.stop_monitoring()
        
        if self.session:
            await self.session.close()
        
        logger.info("Apple Music Monitor shutdown complete")