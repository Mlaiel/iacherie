"""
SoundCloud API Integration for Copyright Monitoring
=================================================

Advanced SoundCloud monitoring using SoundCloud API for track discovery,
user content monitoring, and copyright protection across the platform.

Features:
- SoundCloud API v2 integration for comprehensive track access
- Real-time track upload monitoring and detection
- User profile and playlist monitoring
- Advanced audio waveform analysis integration
- Comment and engagement tracking for copyright violations
- Geographic and demographic content analysis

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import re
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

import aiohttp
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SoundCloudTrackMatch(BaseModel):
    """SoundCloud track match result for copyright monitoring"""
    track_id: str
    track_title: str
    username: str
    user_id: str
    soundcloud_url: str
    permalink_url: str
    stream_url: Optional[str] = None
    waveform_url: Optional[str] = None
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    duration_ms: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    play_count: int = 0
    download_count: int = 0
    likes_count: int = 0
    comment_count: int = 0
    is_downloadable: bool = False
    is_streamable: bool = True
    tags: List[str] = Field(default_factory=list)
    genre: str = ""
    description: str = ""
    copyright_info: Dict[str, Any] = Field(default_factory=dict)
    evidence: Dict[str, Any] = Field(default_factory=dict)


class SoundCloudUser(BaseModel):
    """SoundCloud user information for monitoring"""
    user_id: str
    username: str
    display_name: str
    permalink_url: str
    avatar_url: Optional[str] = None
    followers_count: int = 0
    followings_count: int = 0
    track_count: int = 0
    playlist_count: int = 0
    description: str = ""
    city: str = ""
    country: str = ""
    verified: bool = False
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class SoundCloudPlaylist(BaseModel):
    """SoundCloud playlist information"""
    playlist_id: str
    title: str
    user_id: str
    username: str
    permalink_url: str
    track_count: int = 0
    duration_ms: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    tracks: List[str] = Field(default_factory=list)  # track IDs
    tags: List[str] = Field(default_factory=list)
    description: str = ""
    artwork_url: Optional[str] = None


@dataclass
class SoundCloudConfig:
    """Configuration for SoundCloud monitoring"""
    client_id: str
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    
    # Monitoring settings
    track_monitoring_enabled: bool = True
    user_monitoring_enabled: bool = True
    playlist_monitoring_enabled: bool = True
    trending_monitoring_enabled: bool = True
    
    # Thresholds
    similarity_threshold: float = 0.8
    confidence_threshold: float = 0.75
    waveform_analysis_enabled: bool = True
    
    # Monitoring intervals (seconds)
    track_scan_interval: int = 300   # 5 minutes
    user_scan_interval: int = 900    # 15 minutes
    playlist_scan_interval: int = 1800  # 30 minutes
    trending_scan_interval: int = 3600  # 1 hour
    
    # Search parameters
    search_genres: List[str] = field(default_factory=lambda: [
        "all-music", "hip-hop-rap", "electronic", "rock", "pop", "r-b-soul"
    ])
    
    # Rate limiting
    max_requests_per_minute: int = 60
    max_concurrent_requests: int = 3


class SoundCloudMonitor:
    """
    Advanced SoundCloud monitoring system using SoundCloud API
    for comprehensive track discovery and copyright protection.
    """
    
    def __init__(self, config: SoundCloudConfig):
        """Initialize SoundCloud monitor"""
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = "https://api.soundcloud.com"
        
        # Monitoring state
        self._monitoring_active = False
        self._monitor_tasks: List[asyncio.Task] = []
        
        # Tracked content
        self._tracked_fingerprints: Dict[str, Dict[str, Any]] = {}
        self._monitored_users: Dict[str, SoundCloudUser] = {}
        self._monitored_playlists: Dict[str, SoundCloudPlaylist] = {}
        
        # Results storage
        self._detected_matches: List[SoundCloudTrackMatch] = []
        self._user_violations: List[Dict[str, Any]] = []
        self._playlist_violations: List[Dict[str, Any]] = []
        
        # Rate limiting
        self._request_timestamps: List[datetime] = []
        self._request_semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        
        logger.info("SoundCloud Monitor initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.shutdown()
    
    async def initialize(self) -> bool:
        """Initialize the SoundCloud monitor"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Test API connection
            if not await self._test_api_connection():
                logger.error("Failed to connect to SoundCloud API")
                return False
            
            logger.info("SoundCloud Monitor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SoundCloud monitor: {e}")
            return False
    
    async def _test_api_connection(self) -> bool:
        """Test SoundCloud API connection"""
        try:
            # Test with a simple tracks search
            result = await self._make_soundcloud_request(
                "GET", "/tracks",
                params={"q": "test", "limit": 1}
            )
            
            return result is not None and isinstance(result, list)
            
        except Exception as e:
            logger.error(f"SoundCloud API connection test failed: {e}")
            return False
    
    async def _make_soundcloud_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """Make rate-limited request to SoundCloud API"""
        
        # Rate limiting check
        await self._check_rate_limit()
        
        async with self._request_semaphore:
            try:
                url = f"{self.base_url}{endpoint}"
                
                # Add client_id to parameters
                if params is None:
                    params = {}
                params["client_id"] = self.config.client_id
                
                headers = {"Accept": "application/json"}
                if self.config.access_token:
                    headers["Authorization"] = f"OAuth {self.config.access_token}"
                
                async with self.session.request(
                    method, url, params=params, json=data, headers=headers
                ) as response:
                    self._request_timestamps.append(datetime.utcnow())
                    
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        # Rate limited
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning(f"SoundCloud rate limited, waiting {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                        return await self._make_soundcloud_request(method, endpoint, params, data)
                    elif response.status == 401:
                        logger.error("SoundCloud API authentication failed")
                        return None
                    else:
                        logger.error(f"SoundCloud API error: {response.status} - {await response.text()}")
                        return None
                        
            except Exception as e:
                logger.error(f"SoundCloud request error: {e}")
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
                logger.info(f"SoundCloud rate limiting: sleeping for {sleep_time:.1f} seconds")
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
            
            logger.info(f"Added track fingerprint for SoundCloud monitoring: {fingerprint_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add track fingerprint: {e}")
            return False
    
    async def search_tracks(
        self,
        fingerprint_id: str,
        query_terms: List[str],
        genres: Optional[List[str]] = None
    ) -> List[SoundCloudTrackMatch]:
        """Search SoundCloud for similar tracks"""
        try:
            if fingerprint_id not in self._tracked_fingerprints:
                logger.error(f"Fingerprint not found: {fingerprint_id}")
                return []
            
            genres = genres or self.config.search_genres
            fingerprint_data = self._tracked_fingerprints[fingerprint_id]
            matches = []
            
            # Search using different strategies
            for query in query_terms:
                for genre in genres:
                    # Search tracks
                    results = await self._make_soundcloud_request(
                        "GET", "/tracks",
                        params={
                            "q": query,
                            "genres": genre if genre != "all-music" else "",
                            "limit": 50,
                            "linked_partitioning": 1
                        }
                    )
                    
                    if results and isinstance(results, list):
                        for track in results:
                            match = await self._analyze_track_similarity(
                                fingerprint_id, track
                            )
                            if match and match.similarity_score >= self.config.similarity_threshold:
                                matches.append(match)
                    
                    # Rate limiting delay
                    await asyncio.sleep(1)
            
            # Update tracking info
            self._tracked_fingerprints[fingerprint_id]["last_checked"] = datetime.utcnow()
            self._tracked_fingerprints[fingerprint_id]["matches_found"] += len(matches)
            
            # Store matches
            self._detected_matches.extend(matches)
            
            logger.info(f"Found {len(matches)} potential SoundCloud matches for fingerprint {fingerprint_id}")
            return matches
            
        except Exception as e:
            logger.error(f"SoundCloud track search error: {e}")
            return []
    
    async def _analyze_track_similarity(
        self,
        fingerprint_id: str,
        soundcloud_track: Dict[str, Any]
    ) -> Optional[SoundCloudTrackMatch]:
        """Analyze similarity between fingerprint and SoundCloud track"""
        try:
            fingerprint_data = self._tracked_fingerprints[fingerprint_id]
            
            # Calculate similarity scores
            similarity_score = await self._calculate_similarity_score(
                fingerprint_data, soundcloud_track
            )
            
            confidence_score = await self._calculate_confidence_score(
                fingerprint_data, soundcloud_track
            )
            
            # Only return match if above threshold
            if similarity_score >= self.config.similarity_threshold:
                # Parse created_at timestamp
                created_at = datetime.utcnow()
                if soundcloud_track.get("created_at"):
                    try:
                        created_at = datetime.fromisoformat(
                            soundcloud_track["created_at"].replace("Z", "+00:00")
                        )
                    except:
                        pass
                
                return SoundCloudTrackMatch(
                    track_id=str(soundcloud_track["id"]),
                    track_title=soundcloud_track.get("title", ""),
                    username=soundcloud_track.get("user", {}).get("username", ""),
                    user_id=str(soundcloud_track.get("user", {}).get("id", "")),
                    soundcloud_url=soundcloud_track.get("permalink_url", ""),
                    permalink_url=soundcloud_track.get("permalink_url", ""),
                    stream_url=soundcloud_track.get("stream_url"),
                    waveform_url=soundcloud_track.get("waveform_url"),
                    similarity_score=similarity_score,
                    confidence_score=confidence_score,
                    duration_ms=soundcloud_track.get("duration", 0),
                    created_at=created_at,
                    play_count=soundcloud_track.get("playback_count", 0),
                    download_count=soundcloud_track.get("download_count", 0),
                    likes_count=soundcloud_track.get("likes_count", 0),
                    comment_count=soundcloud_track.get("comment_count", 0),
                    is_downloadable=soundcloud_track.get("downloadable", False),
                    is_streamable=soundcloud_track.get("streamable", True),
                    tags=soundcloud_track.get("tag_list", "").split() if soundcloud_track.get("tag_list") else [],
                    genre=soundcloud_track.get("genre", ""),
                    description=soundcloud_track.get("description", ""),
                    evidence={
                        "track_data": soundcloud_track,
                        "fingerprint_metadata": fingerprint_data["metadata"],
                        "analysis_timestamp": datetime.utcnow().isoformat(),
                        "waveform_analysis": await self._analyze_waveform(soundcloud_track) if self.config.waveform_analysis_enabled else None
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"SoundCloud similarity analysis error: {e}")
            return None
    
    async def _calculate_similarity_score(
        self,
        fingerprint_data: Dict[str, Any],
        soundcloud_track: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between fingerprint and SoundCloud track"""
        try:
            score = 0.0
            factors = 0
            
            # Title similarity
            fp_title = fingerprint_data["metadata"].get("title", "").lower()
            sc_title = soundcloud_track.get("title", "").lower()
            if fp_title and sc_title:
                title_similarity = len(set(fp_title.split()) & set(sc_title.split())) / max(
                    len(set(fp_title.split())), len(set(sc_title.split())), 1
                )
                score += title_similarity * 0.4
                factors += 1
            
            # Artist similarity (username)
            fp_artist = fingerprint_data["metadata"].get("artist", "").lower()
            sc_username = soundcloud_track.get("user", {}).get("username", "").lower()
            if fp_artist and sc_username:
                artist_similarity = len(set(fp_artist.split()) & set(sc_username.split())) / max(
                    len(set(fp_artist.split())), len(set(sc_username.split())), 1
                )
                score += artist_similarity * 0.3
                factors += 1
            
            # Duration similarity
            fp_duration = fingerprint_data["metadata"].get("duration", 0)
            sc_duration = soundcloud_track.get("duration", 0) / 1000
            if fp_duration > 0 and sc_duration > 0:
                duration_diff = abs(fp_duration - sc_duration) / max(fp_duration, sc_duration)
                duration_similarity = max(0, 1 - duration_diff)
                score += duration_similarity * 0.2
                factors += 1
            
            # Genre similarity
            fp_genre = fingerprint_data["metadata"].get("genre", "").lower()
            sc_genre = soundcloud_track.get("genre", "").lower()
            if fp_genre and sc_genre:
                genre_similarity = 1.0 if fp_genre == sc_genre else 0.5 if fp_genre in sc_genre or sc_genre in fp_genre else 0.0
                score += genre_similarity * 0.1
                factors += 1
            
            return score / max(factors, 1)
            
        except Exception as e:
            logger.error(f"SoundCloud similarity calculation error: {e}")
            return 0.0
    
    async def _calculate_confidence_score(
        self,
        fingerprint_data: Dict[str, Any],
        soundcloud_track: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for the match"""
        try:
            confidence = 0.5  # Base confidence
            
            # Increase confidence based on play count
            play_count = soundcloud_track.get("playback_count", 0)
            if play_count > 1000:
                confidence += 0.1
            if play_count > 10000:
                confidence += 0.1
            
            # Increase confidence if track is downloadable (official)
            if soundcloud_track.get("downloadable"):
                confidence += 0.1
            
            # Decrease confidence for very new tracks
            created_at = soundcloud_track.get("created_at", "")
            if created_at:
                try:
                    created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    days_since_creation = (datetime.utcnow() - created_dt).days
                    
                    if days_since_creation < 1:  # Very new
                        confidence += 0.2  # High interest in new uploads
                    elif days_since_creation > 365 * 5:  # Very old
                        confidence -= 0.1
                except:
                    pass
            
            # Increase confidence based on engagement
            likes = soundcloud_track.get("likes_count", 0)
            comments = soundcloud_track.get("comment_count", 0)
            if likes > 100 or comments > 10:
                confidence += 0.1
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"SoundCloud confidence calculation error: {e}")
            return 0.5
    
    async def _analyze_waveform(self, soundcloud_track: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze SoundCloud waveform data for additional matching"""
        try:
            waveform_url = soundcloud_track.get("waveform_url")
            if not waveform_url:
                return None
            
            # Download and analyze waveform data
            async with self.session.get(waveform_url) as response:
                if response.status == 200:
                    waveform_data = await response.json()
                    
                    # Basic waveform analysis
                    samples = waveform_data.get("samples", [])
                    if samples:
                        return {
                            "peak_amplitude": max(samples) if samples else 0,
                            "average_amplitude": sum(samples) / len(samples) if samples else 0,
                            "sample_count": len(samples),
                            "dynamic_range": max(samples) - min(samples) if samples else 0
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Waveform analysis error: {e}")
            return None
    
    async def monitor_user(self, user_id: str) -> bool:
        """Add SoundCloud user to monitoring list"""
        try:
            # Get user information
            user_data = await self._make_soundcloud_request("GET", f"/users/{user_id}")
            if not user_data:
                return False
            
            user = SoundCloudUser(
                user_id=str(user_data["id"]),
                username=user_data.get("username", ""),
                display_name=user_data.get("full_name", user_data.get("username", "")),
                permalink_url=user_data.get("permalink_url", ""),
                avatar_url=user_data.get("avatar_url"),
                followers_count=user_data.get("followers_count", 0),
                followings_count=user_data.get("followings_count", 0),
                track_count=user_data.get("track_count", 0),
                playlist_count=user_data.get("playlist_count", 0),
                description=user_data.get("description", ""),
                city=user_data.get("city", ""),
                country=user_data.get("country", ""),
                verified=user_data.get("verified", False)
            )
            
            self._monitored_users[user_id] = user
            
            logger.info(f"Added SoundCloud user to monitoring: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to monitor SoundCloud user {user_id}: {e}")
            return False
    
    async def monitor_playlist(self, playlist_id: str) -> bool:
        """Add SoundCloud playlist to monitoring list"""
        try:
            # Get playlist information
            playlist_data = await self._make_soundcloud_request("GET", f"/playlists/{playlist_id}")
            if not playlist_data:
                return False
            
            # Get playlist tracks
            tracks = []
            if "tracks" in playlist_data:
                tracks = [str(track["id"]) for track in playlist_data["tracks"] if track]
            
            # Parse created_at timestamp
            created_at = datetime.utcnow()
            if playlist_data.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(
                        playlist_data["created_at"].replace("Z", "+00:00")
                    )
                except:
                    pass
            
            playlist = SoundCloudPlaylist(
                playlist_id=str(playlist_data["id"]),
                title=playlist_data.get("title", ""),
                user_id=str(playlist_data.get("user", {}).get("id", "")),
                username=playlist_data.get("user", {}).get("username", ""),
                permalink_url=playlist_data.get("permalink_url", ""),
                track_count=playlist_data.get("track_count", len(tracks)),
                duration_ms=playlist_data.get("duration", 0),
                created_at=created_at,
                tracks=tracks,
                tags=playlist_data.get("tag_list", "").split() if playlist_data.get("tag_list") else [],
                description=playlist_data.get("description", ""),
                artwork_url=playlist_data.get("artwork_url")
            )
            
            self._monitored_playlists[playlist_id] = playlist
            
            logger.info(f"Added SoundCloud playlist to monitoring: {playlist.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to monitor SoundCloud playlist {playlist_id}: {e}")
            return False
    
    async def start_monitoring(self) -> bool:
        """Start the monitoring tasks"""
        try:
            if self._monitoring_active:
                logger.warning("SoundCloud monitoring already active")
                return True
            
            self._monitoring_active = True
            
            # Start monitoring tasks
            if self.config.track_monitoring_enabled:
                task = asyncio.create_task(self._track_monitoring_loop())
                self._monitor_tasks.append(task)
            
            if self.config.user_monitoring_enabled:
                task = asyncio.create_task(self._user_monitoring_loop())
                self._monitor_tasks.append(task)
            
            if self.config.playlist_monitoring_enabled:
                task = asyncio.create_task(self._playlist_monitoring_loop())
                self._monitor_tasks.append(task)
            
            if self.config.trending_monitoring_enabled:
                task = asyncio.create_task(self._trending_monitoring_loop())
                self._monitor_tasks.append(task)
            
            logger.info("SoundCloud monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start SoundCloud monitoring: {e}")
            return False
    
    async def stop_monitoring(self) -> None:
        """Stop all monitoring tasks"""
        self._monitoring_active = False
        
        for task in self._monitor_tasks:
            task.cancel()
        
        if self._monitor_tasks:
            await asyncio.gather(*self._monitor_tasks, return_exceptions=True)
        
        self._monitor_tasks.clear()
        logger.info("SoundCloud monitoring stopped")
    
    async def _track_monitoring_loop(self) -> None:
        """Main track monitoring loop"""
        logger.info("Starting SoundCloud track monitoring loop")
        
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
                        await self.search_tracks(fingerprint_id, search_terms)
                    
                    # Small delay between fingerprints
                    await asyncio.sleep(2)
                
                # Wait for next scan interval
                await asyncio.sleep(self.config.track_scan_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"SoundCloud track monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _user_monitoring_loop(self) -> None:
        """User monitoring loop"""
        logger.info("Starting SoundCloud user monitoring loop")
        
        while self._monitoring_active:
            try:
                # Check each monitored user for new tracks
                for user_id in list(self._monitored_users.keys()):
                    if not self._monitoring_active:
                        break
                    
                    await self._check_user_new_tracks(user_id)
                    await asyncio.sleep(5)  # Delay between users
                
                await asyncio.sleep(self.config.user_scan_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"SoundCloud user monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _playlist_monitoring_loop(self) -> None:
        """Playlist monitoring loop"""
        logger.info("Starting SoundCloud playlist monitoring loop")
        
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
                logger.error(f"SoundCloud playlist monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _trending_monitoring_loop(self) -> None:
        """Trending content monitoring loop"""
        logger.info("Starting SoundCloud trending monitoring loop")
        
        while self._monitoring_active:
            try:
                # Check trending/popular tracks
                await self._check_trending_tracks()
                await asyncio.sleep(self.config.trending_scan_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"SoundCloud trending monitoring loop error: {e}")
                await asyncio.sleep(60)
    
    async def _check_user_new_tracks(self, user_id: str) -> None:
        """Check user for new track uploads"""
        try:
            user_info = self._monitored_users[user_id]
            
            # Get user's tracks
            tracks_data = await self._make_soundcloud_request(
                "GET", f"/users/{user_id}/tracks",
                params={"limit": 20, "linked_partitioning": 1}
            )
            
            if not tracks_data or not isinstance(tracks_data, list):
                return
            
            # Check new tracks against fingerprints
            for track in tracks_data:
                # Check against all tracked fingerprints
                for fingerprint_id, fingerprint_data in self._tracked_fingerprints.items():
                    match = await self._analyze_track_similarity(fingerprint_id, track)
                    
                    if match and match.similarity_score >= self.config.similarity_threshold:
                        # Found a potential violation
                        violation = {
                            "violation_id": f"sc_user_{user_id}_{track['id']}_{int(time.time())}",
                            "user_id": user_id,
                            "username": user_info.username,
                            "track_match": match,
                            "detected_at": datetime.utcnow(),
                            "violation_type": "user_upload"
                        }
                        
                        self._user_violations.append(violation)
                        logger.warning(f"Potential copyright violation detected from user {user_info.username}")
            
            # Update last checked time
            user_info.last_checked = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"SoundCloud user track check error for {user_id}: {e}")
    
    async def _check_playlist_for_violations(self, playlist_id: str) -> None:
        """Check SoundCloud playlist for copyright violations"""
        try:
            # Get current playlist tracks
            playlist_data = await self._make_soundcloud_request("GET", f"/playlists/{playlist_id}")
            if not playlist_data:
                return
            
            current_tracks = []
            if "tracks" in playlist_data:
                current_tracks = [str(track["id"]) for track in playlist_data["tracks"] if track]
            
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
            logger.error(f"SoundCloud playlist violation check error for {playlist_id}: {e}")
    
    async def _check_track_against_fingerprints(self, track_id: str, playlist_id: str) -> None:
        """Check a specific SoundCloud track against our fingerprints"""
        try:
            # Get track details
            track_data = await self._make_soundcloud_request("GET", f"/tracks/{track_id}")
            if not track_data:
                return
            
            # Check against all tracked fingerprints
            for fingerprint_id, fingerprint_data in self._tracked_fingerprints.items():
                match = await self._analyze_track_similarity(fingerprint_id, track_data)
                
                if match and match.similarity_score >= self.config.similarity_threshold:
                    # Found a potential violation
                    violation = {
                        "violation_id": f"sc_playlist_{playlist_id}_{track_id}_{int(time.time())}",
                        "playlist_id": playlist_id,
                        "playlist_title": self._monitored_playlists[playlist_id].title,
                        "track_match": match,
                        "detected_at": datetime.utcnow(),
                        "violation_type": "playlist_inclusion"
                    }
                    
                    self._playlist_violations.append(violation)
                    logger.warning(f"Potential copyright violation detected in SoundCloud playlist {playlist_id}")
            
        except Exception as e:
            logger.error(f"SoundCloud track fingerprint check error: {e}")
    
    async def _check_trending_tracks(self) -> None:
        """Check trending/popular tracks for potential matches"""
        try:
            # Get trending tracks (using search with popular sorting)
            trending_data = await self._make_soundcloud_request(
                "GET", "/tracks",
                params={
                    "limit": 50,
                    "linked_partitioning": 1,
                    "created_at": f"from:{(datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')}"
                }
            )
            
            if not trending_data or not isinstance(trending_data, list):
                return
            
            # Check trending tracks against fingerprints
            for track in trending_data:
                for fingerprint_id, fingerprint_data in self._tracked_fingerprints.items():
                    match = await self._analyze_track_similarity(fingerprint_id, track)
                    
                    if match and match.similarity_score >= self.config.similarity_threshold:
                        # Mark as trending match
                        match.evidence["trending"] = True
                        match.evidence["trending_detected_at"] = datetime.utcnow().isoformat()
                        self._detected_matches.append(match)
                        
                        logger.info(f"Found trending match for fingerprint {fingerprint_id}")
            
        except Exception as e:
            logger.error(f"SoundCloud trending monitoring error: {e}")
    
    async def get_monitoring_results(self) -> Dict[str, Any]:
        """Get all monitoring results"""
        return {
            "track_matches": [match.dict() for match in self._detected_matches],
            "user_violations": self._user_violations,
            "playlist_violations": self._playlist_violations,
            "monitoring_stats": {
                "tracked_fingerprints": len(self._tracked_fingerprints),
                "monitored_users": len(self._monitored_users),
                "monitored_playlists": len(self._monitored_playlists),
                "total_matches_found": len(self._detected_matches),
                "total_user_violations": len(self._user_violations),
                "total_playlist_violations": len(self._playlist_violations)
            }
        }
    
    async def clear_results(self) -> None:
        """Clear monitoring results"""
        self._detected_matches.clear()
        self._user_violations.clear()
        self._playlist_violations.clear()
        logger.info("SoundCloud monitoring results cleared")
    
    async def shutdown(self) -> None:
        """Shutdown the monitor"""
        await self.stop_monitoring()
        
        if self.session:
            await self.session.close()
        
        logger.info("SoundCloud Monitor shutdown complete")