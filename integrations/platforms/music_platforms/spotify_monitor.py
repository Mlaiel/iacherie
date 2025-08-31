"""
Spotify Advanced Copyright Monitoring System
==========================================

Enhanced Spotify Web API integration with advanced track monitoring,
copyright detection, playlist analysis, and release tracking capabilities.

Features:
- Real-time track monitoring with fingerprint matching
- Advanced audio feature analysis for similarity detection
- Playlist monitoring and copyright violation detection
- Artist release tracking and notification system
- Market-specific monitoring across regions
- Audio fingerprinting integration with Spotify's audio features

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

import aiohttp
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SpotifyTrackMatch(BaseModel):
    """Spotify track match result for copyright monitoring"""
    track_id: str
    track_name: str
    artist_name: str
    album_name: str
    spotify_url: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    audio_features: Dict[str, Any] = Field(default_factory=dict)
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    market: str = "US"
    copyright_status: str = "unknown"
    violation_type: str = "unknown"
    evidence: Dict[str, Any] = Field(default_factory=dict)


class SpotifyPlaylistInfo(BaseModel):
    """Spotify playlist information for monitoring"""
    playlist_id: str
    playlist_name: str
    owner_id: str
    owner_name: str
    track_count: int
    followers: int = 0
    description: str = ""
    public: bool = True
    collaborative: bool = False
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    tracks: List[str] = Field(default_factory=list)  # track IDs


class SpotifyReleaseInfo(BaseModel):
    """Spotify release tracking information"""
    album_id: str
    album_name: str
    artist_id: str
    artist_name: str
    release_date: str
    album_type: str  # album, single, compilation
    track_count: int
    markets: List[str] = Field(default_factory=list)
    genres: List[str] = Field(default_factory=list)
    popularity: int = 0
    tracks: List[Dict[str, Any]] = Field(default_factory=list)


@dataclass
class SpotifyMonitoringConfig:
    """Configuration for Spotify monitoring"""
    client_id: str
    client_secret: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    # Monitoring settings
    track_monitoring_enabled: bool = True
    playlist_monitoring_enabled: bool = True
    release_monitoring_enabled: bool = True
    audio_feature_analysis: bool = True
    
    # Thresholds
    similarity_threshold: float = 0.8
    confidence_threshold: float = 0.75
    audio_feature_tolerance: float = 0.1
    
    # Monitoring intervals (seconds)
    track_scan_interval: int = 300  # 5 minutes
    playlist_scan_interval: int = 1800  # 30 minutes
    release_scan_interval: int = 3600  # 1 hour
    
    # Markets to monitor
    target_markets: List[str] = field(default_factory=lambda: ["US", "GB", "DE", "FR", "ES", "IT", "JP", "CA", "AU"])
    
    # Rate limiting
    max_requests_per_minute: int = 100
    max_concurrent_requests: int = 10


class SpotifyMusicMonitor:
    """
    Advanced Spotify copyright monitoring system with enhanced track detection,
    playlist monitoring, and release tracking capabilities.
    """
    
    def __init__(self, config: SpotifyMonitoringConfig):
        """Initialize Spotify music monitor"""
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = "https://api.spotify.com/v1"
        
        # Monitoring state
        self._monitoring_active = False
        self._monitor_tasks: List[asyncio.Task] = []
        
        # Tracked content
        self._tracked_fingerprints: Dict[str, Dict[str, Any]] = {}  # fingerprint_id -> metadata
        self._monitored_playlists: Dict[str, SpotifyPlaylistInfo] = {}
        self._monitored_artists: Dict[str, Dict[str, Any]] = {}  # artist_id -> metadata
        
        # Results storage
        self._detected_matches: List[SpotifyTrackMatch] = []
        self._playlist_violations: List[Dict[str, Any]] = []
        self._new_releases: List[SpotifyReleaseInfo] = []
        
        # Rate limiting
        self._request_timestamps: List[datetime] = []
        self._request_semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        
        logger.info("Spotify Music Monitor initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.shutdown()
    
    async def initialize(self) -> bool:
        """Initialize the Spotify monitor"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Ensure we have a valid access token
            if not await self._ensure_valid_token():
                logger.error("Failed to obtain valid Spotify access token")
                return False
            
            logger.info("Spotify Music Monitor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Spotify monitor: {e}")
            return False
    
    async def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token"""
        try:
            # Check if current token is valid
            if (self.config.access_token and 
                self.config.token_expires_at and 
                datetime.utcnow() < self.config.token_expires_at - timedelta(minutes=5)):
                return True
            
            # Try to refresh token if we have a refresh token
            if self.config.refresh_token:
                return await self._refresh_access_token()
            
            # Otherwise, get a new token using client credentials
            return await self._get_client_credentials_token()
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False
    
    async def _refresh_access_token(self) -> bool:
        """Refresh Spotify access token"""
        try:
            async with self.session.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.config.refresh_token,
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.config.access_token = data["access_token"]
                    self.config.token_expires_at = datetime.utcnow() + timedelta(
                        seconds=data.get("expires_in", 3600)
                    )
                    if "refresh_token" in data:
                        self.config.refresh_token = data["refresh_token"]
                    return True
                else:
                    logger.error(f"Token refresh failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False
    
    async def _get_client_credentials_token(self) -> bool:
        """Get access token using client credentials flow"""
        try:
            async with self.session.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.config.access_token = data["access_token"]
                    self.config.token_expires_at = datetime.utcnow() + timedelta(
                        seconds=data.get("expires_in", 3600)
                    )
                    return True
                else:
                    logger.error(f"Client credentials failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Client credentials error: {e}")
            return False
    
    async def _make_spotify_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make rate-limited request to Spotify API"""
        
        # Rate limiting check
        await self._check_rate_limit()
        
        async with self._request_semaphore:
            try:
                await self._ensure_valid_token()
                
                url = f"{self.base_url}/{endpoint}"
                headers = {
                    "Authorization": f"Bearer {self.config.access_token}",
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
                        logger.warning(f"Rate limited, waiting {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        return await self._make_spotify_request(method, endpoint, params, data)
                    elif response.status == 401:
                        # Token expired, try to refresh
                        if await self._ensure_valid_token():
                            return await self._make_spotify_request(method, endpoint, params, data)
                        else:
                            logger.error("Failed to refresh token")
                            return None
                    else:
                        logger.error(f"Spotify API error: {response.status} - {await response.text()}")
                        return None
                        
            except Exception as e:
                logger.error(f"Spotify request error: {e}")
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
                logger.info(f"Rate limiting: sleeping for {sleep_time:.1f} seconds")
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
            
            logger.info(f"Added track fingerprint for monitoring: {fingerprint_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add track fingerprint: {e}")
            return False
    
    async def search_similar_tracks(
        self,
        fingerprint_id: str,
        query_terms: List[str],
        markets: Optional[List[str]] = None
    ) -> List[SpotifyTrackMatch]:
        """Search for similar tracks using multiple search strategies"""
        try:
            if fingerprint_id not in self._tracked_fingerprints:
                logger.error(f"Fingerprint not found: {fingerprint_id}")
                return []
            
            markets = markets or self.config.target_markets
            fingerprint_data = self._tracked_fingerprints[fingerprint_id]
            matches = []
            
            # Search using different strategies
            for query in query_terms:
                for market in markets:
                    # Search tracks
                    results = await self._make_spotify_request(
                        "GET", "search",
                        params={
                            "q": query,
                            "type": "track",
                            "market": market,
                            "limit": 50
                        }
                    )
                    
                    if results and "tracks" in results:
                        for track in results["tracks"]["items"]:
                            match = await self._analyze_track_similarity(
                                fingerprint_id, track, market
                            )
                            if match and match.similarity_score >= self.config.similarity_threshold:
                                matches.append(match)
                    
                    # Rate limiting delay
                    await asyncio.sleep(0.1)
            
            # Update last checked time
            self._tracked_fingerprints[fingerprint_id]["last_checked"] = datetime.utcnow()
            self._tracked_fingerprints[fingerprint_id]["matches_found"] += len(matches)
            
            # Store matches
            self._detected_matches.extend(matches)
            
            logger.info(f"Found {len(matches)} potential matches for fingerprint {fingerprint_id}")
            return matches
            
        except Exception as e:
            logger.error(f"Track search error: {e}")
            return []
    
    async def _analyze_track_similarity(
        self,
        fingerprint_id: str,
        spotify_track: Dict[str, Any],
        market: str
    ) -> Optional[SpotifyTrackMatch]:
        """Analyze similarity between fingerprint and Spotify track"""
        try:
            track_id = spotify_track["id"]
            fingerprint_data = self._tracked_fingerprints[fingerprint_id]
            
            # Get audio features if enabled
            audio_features = {}
            if self.config.audio_feature_analysis:
                features_result = await self._make_spotify_request(
                    "GET", f"audio-features/{track_id}"
                )
                if features_result:
                    audio_features = features_result
            
            # Calculate similarity scores
            similarity_score = await self._calculate_similarity_score(
                fingerprint_data, spotify_track, audio_features
            )
            
            confidence_score = await self._calculate_confidence_score(
                fingerprint_data, spotify_track, audio_features
            )
            
            # Only return match if above threshold
            if similarity_score >= self.config.similarity_threshold:
                return SpotifyTrackMatch(
                    track_id=track_id,
                    track_name=spotify_track["name"],
                    artist_name=", ".join([artist["name"] for artist in spotify_track["artists"]]),
                    album_name=spotify_track["album"]["name"],
                    spotify_url=spotify_track["external_urls"]["spotify"],
                    similarity_score=similarity_score,
                    confidence_score=confidence_score,
                    audio_features=audio_features,
                    market=market,
                    evidence={
                        "track_data": spotify_track,
                        "fingerprint_metadata": fingerprint_data["metadata"],
                        "analysis_timestamp": datetime.utcnow().isoformat()
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Similarity analysis error: {e}")
            return None
    
    async def _calculate_similarity_score(
        self,
        fingerprint_data: Dict[str, Any],
        spotify_track: Dict[str, Any],
        audio_features: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between fingerprint and track"""
        try:
            score = 0.0
            factors = 0
            
            # Title similarity (simple approach)
            fp_title = fingerprint_data["metadata"].get("title", "").lower()
            sp_title = spotify_track["name"].lower()
            if fp_title and sp_title:
                title_similarity = len(set(fp_title.split()) & set(sp_title.split())) / max(
                    len(set(fp_title.split())), len(set(sp_title.split())), 1
                )
                score += title_similarity * 0.4
                factors += 1
            
            # Artist similarity
            fp_artist = fingerprint_data["metadata"].get("artist", "").lower()
            sp_artists = ", ".join([artist["name"] for artist in spotify_track["artists"]]).lower()
            if fp_artist and sp_artists:
                artist_similarity = len(set(fp_artist.split()) & set(sp_artists.split())) / max(
                    len(set(fp_artist.split())), len(set(sp_artists.split())), 1
                )
                score += artist_similarity * 0.3
                factors += 1
            
            # Duration similarity
            fp_duration = fingerprint_data["metadata"].get("duration", 0)
            sp_duration = spotify_track.get("duration_ms", 0) / 1000
            if fp_duration > 0 and sp_duration > 0:
                duration_diff = abs(fp_duration - sp_duration) / max(fp_duration, sp_duration)
                duration_similarity = max(0, 1 - duration_diff)
                score += duration_similarity * 0.2
                factors += 1
            
            # Audio features similarity (if available)
            if (audio_features and 
                "audio_features" in fingerprint_data and 
                fingerprint_data["audio_features"]):
                
                audio_similarity = await self._calculate_audio_features_similarity(
                    fingerprint_data["audio_features"], audio_features
                )
                score += audio_similarity * 0.1
                factors += 1
            
            return score / max(factors, 1)
            
        except Exception as e:
            logger.error(f"Similarity calculation error: {e}")
            return 0.0
    
    async def _calculate_confidence_score(
        self,
        fingerprint_data: Dict[str, Any],
        spotify_track: Dict[str, Any],
        audio_features: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for the match"""
        try:
            confidence = 0.5  # Base confidence
            
            # Increase confidence based on popularity
            popularity = spotify_track.get("popularity", 0)
            confidence += (popularity / 100) * 0.2
            
            # Increase confidence if we have audio features
            if audio_features:
                confidence += 0.2
            
            # Decrease confidence if track is very new or very old
            release_date = spotify_track["album"].get("release_date", "")
            if release_date:
                try:
                    release_dt = datetime.fromisoformat(release_date + "T00:00:00")
                    days_since_release = (datetime.utcnow() - release_dt).days
                    
                    if days_since_release < 30:  # Very new
                        confidence += 0.1
                    elif days_since_release > 365 * 10:  # Very old
                        confidence -= 0.1
                except:
                    pass
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Confidence calculation error: {e}")
            return 0.5
    
    async def _calculate_audio_features_similarity(
        self,
        fp_features: Dict[str, Any],
        sp_features: Dict[str, Any]
    ) -> float:
        """Calculate similarity between audio features"""
        try:
            # Audio features to compare
            features_to_compare = [
                "danceability", "energy", "speechiness", "acousticness",
                "instrumentalness", "liveness", "valence", "tempo"
            ]
            
            similarities = []
            tolerance = self.config.audio_feature_tolerance
            
            for feature in features_to_compare:
                if feature in fp_features and feature in sp_features:
                    fp_val = fp_features[feature]
                    sp_val = sp_features[feature]
                    
                    if feature == "tempo":
                        # Tempo comparison (allow for BPM differences)
                        diff = abs(fp_val - sp_val) / max(fp_val, sp_val, 1)
                        similarity = max(0, 1 - diff)
                    else:
                        # Other features (0-1 scale)
                        diff = abs(fp_val - sp_val)
                        similarity = max(0, 1 - (diff / tolerance))
                    
                    similarities.append(similarity)
            
            return sum(similarities) / max(len(similarities), 1)
            
        except Exception as e:
            logger.error(f"Audio features similarity error: {e}")
            return 0.0
    
    async def monitor_playlist(self, playlist_id: str) -> bool:
        """Add playlist to monitoring list"""
        try:
            # Get playlist information
            playlist_data = await self._make_spotify_request("GET", f"playlists/{playlist_id}")
            if not playlist_data:
                return False
            
            # Get playlist tracks
            tracks_data = await self._make_spotify_request(
                "GET", f"playlists/{playlist_id}/tracks",
                params={"fields": "items(track(id,name,artists,album))"}
            )
            
            track_ids = []
            if tracks_data and "items" in tracks_data:
                track_ids = [
                    item["track"]["id"] for item in tracks_data["items"]
                    if item["track"] and item["track"]["id"]
                ]
            
            playlist_info = SpotifyPlaylistInfo(
                playlist_id=playlist_id,
                playlist_name=playlist_data["name"],
                owner_id=playlist_data["owner"]["id"],
                owner_name=playlist_data["owner"]["display_name"] or playlist_data["owner"]["id"],
                track_count=playlist_data["tracks"]["total"],
                followers=playlist_data["followers"]["total"],
                description=playlist_data["description"],
                public=playlist_data["public"],
                collaborative=playlist_data["collaborative"],
                tracks=track_ids
            )
            
            self._monitored_playlists[playlist_id] = playlist_info
            
            logger.info(f"Added playlist to monitoring: {playlist_info.playlist_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to monitor playlist {playlist_id}: {e}")
            return False
    
    async def monitor_artist_releases(self, artist_id: str) -> bool:
        """Add artist to release monitoring"""
        try:
            # Get artist information
            artist_data = await self._make_spotify_request("GET", f"artists/{artist_id}")
            if not artist_data:
                return False
            
            self._monitored_artists[artist_id] = {
                "name": artist_data["name"],
                "genres": artist_data["genres"],
                "popularity": artist_data["popularity"],
                "followers": artist_data["followers"]["total"],
                "added_at": datetime.utcnow(),
                "last_checked": None,
                "releases_found": 0
            }
            
            logger.info(f"Added artist to release monitoring: {artist_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to monitor artist {artist_id}: {e}")
            return False
    
    async def start_monitoring(self) -> bool:
        """Start the monitoring tasks"""
        try:
            if self._monitoring_active:
                logger.warning("Monitoring already active")
                return True
            
            self._monitoring_active = True
            
            # Start monitoring tasks
            if self.config.track_monitoring_enabled:
                task = asyncio.create_task(self._track_monitoring_loop())
                self._monitor_tasks.append(task)
            
            if self.config.playlist_monitoring_enabled:
                task = asyncio.create_task(self._playlist_monitoring_loop())
                self._monitor_tasks.append(task)
            
            if self.config.release_monitoring_enabled:
                task = asyncio.create_task(self._release_monitoring_loop())
                self._monitor_tasks.append(task)
            
            logger.info("Spotify monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False
    
    async def stop_monitoring(self) -> None:
        """Stop all monitoring tasks"""
        self._monitoring_active = False
        
        for task in self._monitor_tasks:
            task.cancel()
        
        if self._monitor_tasks:
            await asyncio.gather(*self._monitor_tasks, return_exceptions=True)
        
        self._monitor_tasks.clear()
        logger.info("Spotify monitoring stopped")
    
    async def _track_monitoring_loop(self) -> None:
        """Main track monitoring loop"""
        logger.info("Starting track monitoring loop")
        
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
                        await self.search_similar_tracks(fingerprint_id, search_terms)
                    
                    # Small delay between fingerprints
                    await asyncio.sleep(1)
                
                # Wait for next scan interval
                await asyncio.sleep(self.config.track_scan_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Track monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _playlist_monitoring_loop(self) -> None:
        """Playlist monitoring loop"""
        logger.info("Starting playlist monitoring loop")
        
        while self._monitoring_active:
            try:
                # Check each monitored playlist for changes
                for playlist_id in list(self._monitored_playlists.keys()):
                    if not self._monitoring_active:
                        break
                    
                    await self._check_playlist_for_violations(playlist_id)
                    await asyncio.sleep(5)  # Delay between playlists
                
                await asyncio.sleep(self.config.playlist_scan_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Playlist monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _release_monitoring_loop(self) -> None:
        """Release monitoring loop"""
        logger.info("Starting release monitoring loop")
        
        while self._monitoring_active:
            try:
                # Check each monitored artist for new releases
                for artist_id in list(self._monitored_artists.keys()):
                    if not self._monitoring_active:
                        break
                    
                    await self._check_artist_new_releases(artist_id)
                    await asyncio.sleep(2)  # Delay between artists
                
                await asyncio.sleep(self.config.release_scan_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Release monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _check_playlist_for_violations(self, playlist_id: str) -> None:
        """Check playlist for copyright violations"""
        try:
            # Get current playlist tracks
            tracks_data = await self._make_spotify_request(
                "GET", f"playlists/{playlist_id}/tracks",
                params={"fields": "items(track(id,name,artists,album))"}
            )
            
            if not tracks_data or "items" not in tracks_data:
                return
            
            current_tracks = [
                item["track"]["id"] for item in tracks_data["items"]
                if item["track"] and item["track"]["id"]
            ]
            
            playlist_info = self._monitored_playlists[playlist_id]
            previous_tracks = set(playlist_info.tracks)
            current_tracks_set = set(current_tracks)
            
            # Check for new tracks
            new_tracks = current_tracks_set - previous_tracks
            if new_tracks:
                # Check new tracks against our fingerprints
                for track_id in new_tracks:
                    await self._check_track_against_fingerprints(track_id, playlist_id)
                
                # Update playlist info
                playlist_info.tracks = current_tracks
                playlist_info.last_modified = datetime.utcnow()
                playlist_info.track_count = len(current_tracks)
            
        except Exception as e:
            logger.error(f"Playlist violation check error for {playlist_id}: {e}")
    
    async def _check_track_against_fingerprints(self, track_id: str, playlist_id: str) -> None:
        """Check a specific track against our fingerprints"""
        try:
            # Get track details
            track_data = await self._make_spotify_request("GET", f"tracks/{track_id}")
            if not track_data:
                return
            
            # Check against all tracked fingerprints
            for fingerprint_id, fingerprint_data in self._tracked_fingerprints.items():
                match = await self._analyze_track_similarity(
                    fingerprint_id, track_data, "US"
                )
                
                if match and match.similarity_score >= self.config.similarity_threshold:
                    # Found a potential violation
                    violation = {
                        "violation_id": f"playlist_{playlist_id}_{track_id}_{int(time.time())}",
                        "playlist_id": playlist_id,
                        "playlist_name": self._monitored_playlists[playlist_id].playlist_name,
                        "track_match": match,
                        "detected_at": datetime.utcnow(),
                        "violation_type": "playlist_inclusion"
                    }
                    
                    self._playlist_violations.append(violation)
                    logger.warning(f"Potential copyright violation detected in playlist {playlist_id}")
            
        except Exception as e:
            logger.error(f"Track fingerprint check error: {e}")
    
    async def _check_artist_new_releases(self, artist_id: str) -> None:
        """Check artist for new releases"""
        try:
            # Get artist's albums
            albums_data = await self._make_spotify_request(
                "GET", f"artists/{artist_id}/albums",
                params={
                    "include_groups": "album,single",
                    "limit": 20,
                    "market": "US"
                }
            )
            
            if not albums_data or "items" not in albums_data:
                return
            
            artist_data = self._monitored_artists[artist_id]
            last_check = artist_data.get("last_checked")
            
            new_releases = []
            for album in albums_data["items"]:
                release_date_str = album["release_date"]
                try:
                    # Parse release date
                    if len(release_date_str) == 4:  # Year only
                        release_date = datetime.strptime(release_date_str, "%Y")
                    elif len(release_date_str) == 7:  # Year-month
                        release_date = datetime.strptime(release_date_str, "%Y-%m")
                    else:  # Full date
                        release_date = datetime.strptime(release_date_str, "%Y-%m-%d")
                    
                    # Check if this is a new release
                    if not last_check or release_date > last_check:
                        # Get album tracks
                        album_tracks = await self._make_spotify_request(
                            "GET", f"albums/{album['id']}/tracks"
                        )
                        
                        tracks = []
                        if album_tracks and "items" in album_tracks:
                            tracks = album_tracks["items"]
                        
                        release_info = SpotifyReleaseInfo(
                            album_id=album["id"],
                            album_name=album["name"],
                            artist_id=artist_id,
                            artist_name=artist_data["name"],
                            release_date=release_date_str,
                            album_type=album["album_type"],
                            track_count=album["total_tracks"],
                            markets=album.get("available_markets", []),
                            tracks=tracks
                        )
                        
                        new_releases.append(release_info)
                        
                except ValueError:
                    continue
            
            if new_releases:
                self._new_releases.extend(new_releases)
                artist_data["releases_found"] += len(new_releases)
                logger.info(f"Found {len(new_releases)} new releases for {artist_data['name']}")
            
            # Update last checked time
            artist_data["last_checked"] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Artist release check error for {artist_id}: {e}")
    
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
        logger.info("Monitoring results cleared")
    
    async def shutdown(self) -> None:
        """Shutdown the monitor"""
        await self.stop_monitoring()
        
        if self.session:
            await self.session.close()
        
        logger.info("Spotify Music Monitor shutdown complete")