"""Audio Platforms Integration - Music Streaming Platform Integrations
=====================================================================

Professional integration for music streaming platforms including
Spotify Artists API, Apple Music, SoundCloud, and YouTube Music.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import json
import aiohttp
import hashlib
import hmac
import base64
import uuid

logger = logging.getLogger(__name__)


class AudioPlatform(str, Enum):
    """Supported audio streaming platforms."""
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    YOUTUBE_MUSIC = "youtube_music"
    AMAZON_MUSIC = "amazon_music"
    DEEZER = "deezer"
    TIDAL = "tidal"
    BANDCAMP = "bandcamp"


class ContentType(str, Enum):
    """Audio content types."""
    TRACK = "track"
    ALBUM = "album"
    PLAYLIST = "playlist"
    PODCAST = "podcast"
    AUDIOBOOK = "audiobook"
    SOUND_EFFECT = "sound_effect"


class ReleaseStatus(str, Enum):
    """Content release status."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"
    TAKEDOWN = "takedown"
    MONETIZING = "monetizing"


class RoyaltyType(str, Enum):
    """Types of royalty payments."""
    STREAMING = "streaming"
    DOWNLOAD = "download"
    SYNC_LICENSE = "sync_license"
    PERFORMANCE = "performance"
    MECHANICAL = "mechanical"
    MASTER_RECORDING = "master_recording"


class MetricType(str, Enum):
    """Audio engagement metrics."""
    STREAMS = "streams"
    DOWNLOADS = "downloads"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    SAVES = "saves"
    PLAYLIST_ADDS = "playlist_adds"
    SKIP_RATE = "skip_rate"


@dataclass
class AudioPlatformAccount:
    """Audio platform account configuration."""
    platform: AudioPlatform
    account_id: str
    artist_name: str
    account_type: str  # individual, label, distributor
    credentials: Dict[str, str]
    is_verified: bool
    is_monetized: bool
    follower_count: int
    monthly_listeners: int
    total_streams: int
    royalty_settings: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class AudioTrack:
    """Audio track information."""
    track_id: str
    platform: AudioPlatform
    title: str
    artist: str
    album: Optional[str]
    duration_seconds: int
    genre: str
    release_date: datetime
    isrc: Optional[str]  # International Standard Recording Code
    audio_url: Optional[str]
    artwork_url: Optional[str]
    lyrics: Optional[str]
    status: ReleaseStatus
    metadata: Dict[str, Any]


@dataclass
class StreamingMetrics:
    """Streaming metrics for audio content."""
    track_id: str
    platform: AudioPlatform
    period_start: datetime
    period_end: datetime
    streams: int
    unique_listeners: int
    skip_rate: float
    completion_rate: float
    geographical_data: Dict[str, int]
    demographic_data: Dict[str, Any]
    playlist_additions: int
    saves: int
    shares: int
    revenue_generated: Decimal
    metadata: Dict[str, Any]


@dataclass
class RoyaltyPayment:
    """Royalty payment information."""
    payment_id: str
    platform: AudioPlatform
    artist_id: str
    period_start: datetime
    period_end: datetime
    royalty_type: RoyaltyType
    total_streams: int
    total_revenue: Decimal
    rate_per_stream: Decimal
    currency: str
    payment_date: datetime
    payment_status: str
    breakdown: Dict[str, Decimal]
    metadata: Dict[str, Any]


@dataclass
class AudioAnalytics:
    """Comprehensive audio analytics."""
    platform: AudioPlatform
    period_start: datetime
    period_end: datetime
    total_streams: int
    total_revenue: Decimal
    top_tracks: List[Dict[str, Any]]
    audience_insights: Dict[str, Any]
    growth_metrics: Dict[str, float]
    geographical_breakdown: Dict[str, Any]
    platform_comparison: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any]


class AudioPlatformsIntegration:
    """Professional audio platforms integration."""
    
    def __init__(
        self,
        # Spotify credentials
        spotify_client_id -> None: Optional[str] = None,
        spotify_client_secret -> None: Optional[str] = None,
        spotify_refresh_token -> None: Optional[str] = None,
        # Apple Music credentials
        apple_music_team_id -> None: Optional[str] = None,
        apple_music_key_id -> None: Optional[str] = None,
        apple_music_private_key -> None: Optional[str] = None,
        # SoundCloud credentials
        soundcloud_client_id -> None: Optional[str] = None,
        soundcloud_client_secret -> None: Optional[str] = None,
        soundcloud_access_token -> None: Optional[str] = None,
        # YouTube Music credentials
        youtube_api_key -> None: Optional[str] = None,
        youtube_channel_id -> None: Optional[str] = None,
        # General settings
        timeout -> None: int = 30
    ) -> None:
        # Credentials storage
        self.spotify_client_id = spotify_client_id
        self.spotify_client_secret = spotify_client_secret
        self.spotify_refresh_token = spotify_refresh_token
        self.apple_music_team_id = apple_music_team_id
        self.apple_music_key_id = apple_music_key_id
        self.apple_music_private_key = apple_music_private_key
        self.soundcloud_client_id = soundcloud_client_id
        self.soundcloud_client_secret = soundcloud_client_secret
        self.soundcloud_access_token = soundcloud_access_token
        self.youtube_api_key = youtube_api_key
        self.youtube_channel_id = youtube_channel_id
        
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Connected accounts storage
        self.audio_accounts: Dict[str, AudioPlatformAccount] = {}
        self.uploaded_tracks: Dict[str, AudioTrack] = {}
        
        # Usage tracking
        self.total_uploads = 0
        self.total_streams_tracked = 0
        self.total_revenue_tracked = Decimal('0')
        self.request_count = 0
        self.platform_usage = {}
        
        # Platform URLs
        self.platform_urls = {
            AudioPlatform.SPOTIFY: {
                "api": "https://api.spotify.com/v1",
                "accounts": "https://accounts.spotify.com",
                "artists": "https://api.spotify.com/v1/me"
            },
            AudioPlatform.APPLE_MUSIC: {
                "api": "https://api.music.apple.com/v1",
                "connect": "https://api.appstoreconnect.apple.com/v1"
            },
            AudioPlatform.SOUNDCLOUD: {
                "api": "https://api.soundcloud.com",
                "upload": "https://api.soundcloud.com/tracks"
            },
            AudioPlatform.YOUTUBE_MUSIC: {
                "api": "https://www.googleapis.com/youtube/v3",
                "upload": "https://www.googleapis.com/upload/youtube/v3/videos"
            }
        }
        
        logger.info("Audio Platforms integration initialized")
    
    async def __aenter__(self) -> None:
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure HTTP session is available."""
        if self.session is None or self.session.closed:
            headers = {
                "User-Agent": "Ainflue/1.0 Audio Platform Hub",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def initialize_spotify_account(self) -> AudioPlatformAccount:
        """Initialize Spotify artist account."""
        await self._ensure_session()
        
        if not self.spotify_client_id or not self.spotify_client_secret:
            raise ValueError("Spotify credentials not configured")
        
        try:
            # Get access token
            access_token = await self._get_spotify_access_token()
            
            # Get artist information
            headers = {"Authorization": f"Bearer {access_token}"}
            
            async with self.session.get(
                f"{self.platform_urls[AudioPlatform.SPOTIFY]['artists']}",
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Spotify artist info error: {error_data}")
                
                artist_info = await response.json()
                
                # Get artist stats if available
                stats = {}
                if artist_info.get("type") == "artist":
                    async with self.session.get(
                        f"{self.platform_urls[AudioPlatform.SPOTIFY]['api']}/artists/{artist_info['id']}",
                        headers=headers
                    ) as stats_response:
                        if stats_response.status == 200:
                            stats = await stats_response.json()
                
                account = AudioPlatformAccount(
                    platform=AudioPlatform.SPOTIFY,
                    account_id=artist_info.get("id", "unknown"),
                    artist_name=artist_info.get("display_name", artist_info.get("name", "Unknown Artist")),
                    account_type="artist",
                    credentials={"access_token": access_token},
                    is_verified=artist_info.get("verified", False),
                    is_monetized=True,  # Spotify artists can be monetized
                    follower_count=stats.get("followers", {}).get("total", 0),
                    monthly_listeners=0,  # Would need Spotify for Artists API
                    total_streams=0,  # Would need detailed analytics API
                    royalty_settings={"rate_per_stream": Decimal("0.003")},  # Approximate rate
                    metadata={"artist_info": artist_info, "stats": stats}
                )
                
                self.audio_accounts[f"{AudioPlatform.SPOTIFY}_{account.account_id}"] = account
                self.platform_usage[AudioPlatform.SPOTIFY] = 0
                self.request_count += 2
                
                logger.info(f"Spotify account initialized: {account.artist_name}")
                return account
        
        except Exception as e:
            logger.error(f"Spotify account initialization failed: {e}")
            raise
    
    async def _get_spotify_access_token(self) -> str:
        """Get Spotify access token."""
        if self.spotify_refresh_token:
            # Use refresh token to get new access token
            auth = base64.b64encode(
                f"{self.spotify_client_id}:{self.spotify_client_secret}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.spotify_refresh_token
            }
            
            async with self.session.post(
                f"{self.platform_urls[AudioPlatform.SPOTIFY]['accounts']}/api/token",
                data=data,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Spotify token error: {error_data}")
                
                token_data = await response.json()
                return token_data["access_token"]
        else:
            # Use client credentials flow for public data
            auth = base64.b64encode(
                f"{self.spotify_client_id}:{self.spotify_client_secret}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = "grant_type=client_credentials"
            
            async with self.session.post(
                f"{self.platform_urls[AudioPlatform.SPOTIFY]['accounts']}/api/token",
                data=data,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Spotify token error: {error_data}")
                
                token_data = await response.json()
                return token_data["access_token"]
    
    async def initialize_soundcloud_account(self) -> AudioPlatformAccount:
        """Initialize SoundCloud account."""
        await self._ensure_session()
        
        if not self.soundcloud_access_token:
            raise ValueError("SoundCloud access token not configured")
        
        try:
            headers = {"Authorization": f"OAuth {self.soundcloud_access_token}"}
            
            # Get user information
            async with self.session.get(
                f"{self.platform_urls[AudioPlatform.SOUNDCLOUD]['api']}/me",
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"SoundCloud user info error: {error_data}")
                
                user_info = await response.json()
                
                account = AudioPlatformAccount(
                    platform=AudioPlatform.SOUNDCLOUD,
                    account_id=str(user_info.get("id", "unknown")),
                    artist_name=user_info.get("username", "Unknown Artist"),
                    account_type="creator",
                    credentials={"access_token": self.soundcloud_access_token},
                    is_verified=user_info.get("verified", False),
                    is_monetized=user_info.get("monetization_enabled", False),
                    follower_count=user_info.get("followers_count", 0),
                    monthly_listeners=0,  # Not directly available
                    total_streams=user_info.get("playback_count", 0),
                    royalty_settings={"rate_per_stream": Decimal("0.0025")},  # Approximate rate
                    metadata={"user_info": user_info}
                )
                
                self.audio_accounts[f"{AudioPlatform.SOUNDCLOUD}_{account.account_id}"] = account
                self.platform_usage[AudioPlatform.SOUNDCLOUD] = 0
                self.request_count += 1
                
                logger.info(f"SoundCloud account initialized: {account.artist_name}")
                return account
        
        except Exception as e:
            logger.error(f"SoundCloud account initialization failed: {e}")
            raise
    
    async def initialize_youtube_music_account(self) -> AudioPlatformAccount:
        """Initialize YouTube Music account."""
        await self._ensure_session()
        
        if not self.youtube_api_key or not self.youtube_channel_id:
            raise ValueError("YouTube Music credentials not configured")
        
        try:
            params = {
                "part": "snippet,statistics",
                "id": self.youtube_channel_id,
                "key": self.youtube_api_key
            }
            
            async with self.session.get(
                f"{self.platform_urls[AudioPlatform.YOUTUBE_MUSIC]['api']}/channels",
                params=params
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"YouTube channel info error: {error_data}")
                
                channel_data = await response.json()
                
                if not channel_data.get("items"):
                    raise Exception("YouTube channel not found")
                
                channel = channel_data["items"][0]
                stats = channel.get("statistics", {})
                
                account = AudioPlatformAccount(
                    platform=AudioPlatform.YOUTUBE_MUSIC,
                    account_id=channel["id"],
                    artist_name=channel["snippet"]["title"],
                    account_type="channel",
                    credentials={"api_key": self.youtube_api_key},
                    is_verified=channel["snippet"].get("verified", False),
                    is_monetized=True,  # Assume monetized if API key provided
                    follower_count=int(stats.get("subscriberCount", 0)),
                    monthly_listeners=0,  # Not directly available
                    total_streams=int(stats.get("viewCount", 0)),
                    royalty_settings={"rate_per_stream": Decimal("0.001")},  # Approximate rate
                    metadata={"channel": channel}
                )
                
                self.audio_accounts[f"{AudioPlatform.YOUTUBE_MUSIC}_{account.account_id}"] = account
                self.platform_usage[AudioPlatform.YOUTUBE_MUSIC] = 0
                self.request_count += 1
                
                logger.info(f"YouTube Music account initialized: {account.artist_name}")
                return account
        
        except Exception as e:
            logger.error(f"YouTube Music account initialization failed: {e}")
            raise
    
    async def upload_track(
        self,
        platform: AudioPlatform,
        title: str,
        artist: str,
        audio_file_path: str,
        artwork_path: Optional[str] = None,
        album: Optional[str] = None,
        genre: Optional[str] = None,
        release_date: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AudioTrack:
        """Upload audio track to platform."""
        await self._ensure_session()
        
        track_id = str(uuid.uuid4())
        
        if platform == AudioPlatform.SOUNDCLOUD:
            return await self._upload_soundcloud_track(
                track_id, title, artist, audio_file_path, artwork_path, 
                album, genre, release_date, metadata
            )
        elif platform == AudioPlatform.YOUTUBE_MUSIC:
            return await self._upload_youtube_track(
                track_id, title, artist, audio_file_path, artwork_path,
                album, genre, release_date, metadata
            )
        else:
            # For platforms like Spotify and Apple Music, direct upload isn't available
            # These typically require distribution services
            raise ValueError(f"Direct upload not supported for {platform}. Use distribution service.")
    
    async def _upload_soundcloud_track(
        self,
        track_id: str,
        title: str,
        artist: str,
        audio_file_path: str,
        artwork_path: Optional[str],
        album: Optional[str],
        genre: Optional[str],
        release_date: Optional[datetime],
        metadata: Dict[str, Any]
    ) -> AudioTrack:
        """Upload track to SoundCloud."""
        try:
            if not self.soundcloud_access_token:
                raise ValueError("SoundCloud not configured")
            
            # Prepare form data for upload
            form_data = aiohttp.FormData()
            form_data.add_field('oauth_token', self.soundcloud_access_token)
            form_data.add_field('track[title]', title)
            form_data.add_field('track[genre]', genre or 'Other')
            form_data.add_field('track[description]', f"By {artist}")
            
            if album:
                form_data.add_field('track[tag_list]', album)
            
            # Add audio file
            with open(audio_file_path, 'rb') as audio_file:
                form_data.add_field('track[asset_data]', audio_file, 
                                  filename=f"{title}.mp3", content_type='audio/mpeg')
                
                # Add artwork if provided
                if artwork_path:
                    with open(artwork_path, 'rb') as artwork_file:
                        form_data.add_field('track[artwork_data]', artwork_file,
                                          filename=f"{title}_artwork.jpg", content_type='image/jpeg')
                
                async with self.session.post(
                    self.platform_urls[AudioPlatform.SOUNDCLOUD]['upload'],
                    data=form_data
                ) as response:
                    if response.status not in [200, 201]:
                        error_data = await response.json()
                        raise Exception(f"SoundCloud upload error: {error_data}")
                    
                    result = await response.json()
                    
                    track = AudioTrack(
                        track_id=str(result["id"]),
                        platform=AudioPlatform.SOUNDCLOUD,
                        title=title,
                        artist=artist,
                        album=album,
                        duration_seconds=result.get("duration", 0) // 1000,  # SoundCloud returns milliseconds
                        genre=genre or "Other",
                        release_date=release_date or datetime.now(),
                        isrc=None,
                        audio_url=result.get("stream_url"),
                        artwork_url=result.get("artwork_url"),
                        lyrics=None,
                        status=ReleaseStatus.PUBLISHED,
                        metadata=metadata or {}
                    )
                    
                    self.uploaded_tracks[track.track_id] = track
                    self.total_uploads += 1
                    self.request_count += 1
                    self.platform_usage[AudioPlatform.SOUNDCLOUD] = self.platform_usage.get(AudioPlatform.SOUNDCLOUD, 0) + 1
                    
                    logger.info(f"SoundCloud track uploaded: {title} ({track.track_id})")
                    return track
        
        except Exception as e:
            logger.error(f"SoundCloud track upload failed: {e}")
            raise
    
    async def _upload_youtube_track(
        self,
        track_id: str,
        title: str,
        artist: str,
        audio_file_path: str,
        artwork_path: Optional[str],
        album: Optional[str],
        genre: Optional[str],
        release_date: Optional[datetime],
        metadata: Dict[str, Any]
    ) -> AudioTrack:
        """Upload track to YouTube Music (simplified example)."""
        try:
            # Note: This is a simplified example. Real YouTube upload requires OAuth and video file
            # For audio-only content, you'd typically create a video with static artwork
            
            track = AudioTrack(
                track_id=track_id,
                platform=AudioPlatform.YOUTUBE_MUSIC,
                title=title,
                artist=artist,
                album=album,
                duration_seconds=0,  # Would be determined from audio file
                genre=genre or "Music",
                release_date=release_date or datetime.now(),
                isrc=None,
                audio_url=None,  # YouTube would provide video URL
                artwork_url=artwork_path,
                lyrics=None,
                status=ReleaseStatus.PENDING_REVIEW,  # YouTube content goes through review
                metadata=metadata or {}
            )
            
            self.uploaded_tracks[track.track_id] = track
            self.total_uploads += 1
            self.platform_usage[AudioPlatform.YOUTUBE_MUSIC] = self.platform_usage.get(AudioPlatform.YOUTUBE_MUSIC, 0) + 1
            
            logger.info(f"YouTube Music track prepared: {title} ({track.track_id})")
            return track
        
        except Exception as e:
            logger.error(f"YouTube Music track upload failed: {e}")
            raise
    
    async def get_streaming_metrics(
        self,
        platform: AudioPlatform,
        track_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> StreamingMetrics:
        """Get streaming metrics for a track."""
        await self._ensure_session()
        
        if platform == AudioPlatform.SPOTIFY:
            return await self._get_spotify_metrics(track_id, start_date, end_date)
        elif platform == AudioPlatform.SOUNDCLOUD:
            return await self._get_soundcloud_metrics(track_id, start_date, end_date)
        elif platform == AudioPlatform.YOUTUBE_MUSIC:
            return await self._get_youtube_metrics(track_id, start_date, end_date)
        else:
            raise ValueError(f"Metrics not available for {platform}")
    
    async def _get_spotify_metrics(
        self,
        track_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> StreamingMetrics:
        """Get Spotify streaming metrics."""
        try:
            access_token = await self._get_spotify_access_token()
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Get track details
            async with self.session.get(
                f"{self.platform_urls[AudioPlatform.SPOTIFY]['api']}/tracks/{track_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"Spotify track error: {error_data}")
                
                track_data = await response.json()
                
                # Note: Real metrics would require Spotify for Artists API
                # This is a simplified example with mock data
                
                metrics = StreamingMetrics(
                    track_id=track_id,
                    platform=AudioPlatform.SPOTIFY,
                    period_start=start_date,
                    period_end=end_date,
                    streams=track_data.get("popularity", 0) * 1000,  # Mock calculation
                    unique_listeners=int(track_data.get("popularity", 0) * 800),
                    skip_rate=0.15,  # Mock data
                    completion_rate=0.75,  # Mock data
                    geographical_data={"US": 40, "GB": 20, "CA": 15, "AU": 10, "DE": 15},
                    demographic_data={"18-24": 30, "25-34": 35, "35-44": 20, "45+": 15},
                    playlist_additions=int(track_data.get("popularity", 0) * 50),
                    saves=int(track_data.get("popularity", 0) * 30),
                    shares=int(track_data.get("popularity", 0) * 10),
                    revenue_generated=Decimal(str(track_data.get("popularity", 0) * 3)),  # Mock revenue
                    metadata={"track_data": track_data}
                )
                
                self.total_streams_tracked += metrics.streams
                self.total_revenue_tracked += metrics.revenue_generated
                self.request_count += 1
                
                logger.info(f"Spotify metrics retrieved for track: {track_id}")
                return metrics
        
        except Exception as e:
            logger.error(f"Spotify metrics retrieval failed: {e}")
            raise
    
    async def _get_soundcloud_metrics(
        self,
        track_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> StreamingMetrics:
        """Get SoundCloud streaming metrics."""
        try:
            headers = {"Authorization": f"OAuth {self.soundcloud_access_token}"}
            
            # Get track stats
            async with self.session.get(
                f"{self.platform_urls[AudioPlatform.SOUNDCLOUD]['api']}/tracks/{track_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"SoundCloud track error: {error_data}")
                
                track_data = await response.json()
                
                metrics = StreamingMetrics(
                    track_id=track_id,
                    platform=AudioPlatform.SOUNDCLOUD,
                    period_start=start_date,
                    period_end=end_date,
                    streams=track_data.get("playback_count", 0),
                    unique_listeners=int(track_data.get("playback_count", 0) * 0.8),  # Estimate
                    skip_rate=0.20,  # Mock data
                    completion_rate=0.70,  # Mock data
                    geographical_data={"US": 35, "GB": 15, "DE": 20, "FR": 15, "Other": 15},
                    demographic_data={"18-24": 40, "25-34": 30, "35-44": 20, "45+": 10},
                    playlist_additions=track_data.get("reposts_count", 0),
                    saves=track_data.get("favoritings_count", 0),
                    shares=track_data.get("reposts_count", 0),
                    revenue_generated=Decimal(str(track_data.get("playback_count", 0) * 0.0025)),  # Estimated revenue
                    metadata={"track_data": track_data}
                )
                
                self.total_streams_tracked += metrics.streams
                self.total_revenue_tracked += metrics.revenue_generated
                self.request_count += 1
                
                logger.info(f"SoundCloud metrics retrieved for track: {track_id}")
                return metrics
        
        except Exception as e:
            logger.error(f"SoundCloud metrics retrieval failed: {e}")
            raise
    
    async def _get_youtube_metrics(
        self,
        track_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> StreamingMetrics:
        """Get YouTube Music streaming metrics."""
        try:
            params = {
                "part": "statistics",
                "id": track_id,
                "key": self.youtube_api_key
            }
            
            async with self.session.get(
                f"{self.platform_urls[AudioPlatform.YOUTUBE_MUSIC]['api']}/videos",
                params=params
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"YouTube video error: {error_data}")
                
                video_data = await response.json()
                
                if not video_data.get("items"):
                    raise Exception("YouTube video not found")
                
                stats = video_data["items"][0].get("statistics", {})
                
                metrics = StreamingMetrics(
                    track_id=track_id,
                    platform=AudioPlatform.YOUTUBE_MUSIC,
                    period_start=start_date,
                    period_end=end_date,
                    streams=int(stats.get("viewCount", 0)),
                    unique_listeners=int(int(stats.get("viewCount", 0)) * 0.85),  # Estimate
                    skip_rate=0.25,  # Mock data
                    completion_rate=0.65,  # Mock data
                    geographical_data={"US": 30, "IN": 20, "BR": 15, "GB": 10, "Other": 25},
                    demographic_data={"18-24": 45, "25-34": 25, "35-44": 20, "45+": 10},
                    playlist_additions=0,  # Not directly available
                    saves=int(stats.get("likeCount", 0)),
                    shares=0,  # Not directly available
                    revenue_generated=Decimal(str(int(stats.get("viewCount", 0)) * 0.001)),  # Estimated revenue
                    metadata={"video_data": video_data["items"][0]}
                )
                
                self.total_streams_tracked += metrics.streams
                self.total_revenue_tracked += metrics.revenue_generated
                self.request_count += 1
                
                logger.info(f"YouTube Music metrics retrieved for track: {track_id}")
                return metrics
        
        except Exception as e:
            logger.error(f"YouTube Music metrics retrieval failed: {e}")
            raise
    
    async def calculate_royalty_payments(
        self,
        platform: AudioPlatform,
        artist_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> RoyaltyPayment:
        """Calculate royalty payments for period."""
        
        # Get account for royalty rates
        account_key = f"{platform}_{artist_id}"
        if account_key not in self.audio_accounts:
            raise ValueError(f"Account not found: {platform} - {artist_id}")
        
        account = self.audio_accounts[account_key]
        rate_per_stream = account.royalty_settings.get("rate_per_stream", Decimal("0.003"))
        
        # Get all tracks for this artist and calculate total
        total_streams = 0
        total_revenue = Decimal('0')
        breakdown = {}
        
        for track_id, track in self.uploaded_tracks.items():
            if track.platform == platform:
                try:
                    metrics = await self.get_streaming_metrics(platform, track_id, start_date, end_date)
                    track_revenue = Decimal(str(metrics.streams)) * rate_per_stream
                    
                    total_streams += metrics.streams
                    total_revenue += track_revenue
                    breakdown[track.title] = track_revenue
                
                except Exception as e:
                    logger.warning(f"Failed to get metrics for track {track_id}: {e}")
                    continue
        
        payment_id = str(uuid.uuid4())
        
        royalty_payment = RoyaltyPayment(
            payment_id=payment_id,
            platform=platform,
            artist_id=artist_id,
            period_start=start_date,
            period_end=end_date,
            royalty_type=RoyaltyType.STREAMING,
            total_streams=total_streams,
            total_revenue=total_revenue,
            rate_per_stream=rate_per_stream,
            currency="USD",
            payment_date=datetime.now() + timedelta(days=30),  # Typical payment delay
            payment_status="pending",
            breakdown=breakdown,
            metadata={"calculation_date": datetime.now().isoformat()}
        )
        
        logger.info(f"Royalty payment calculated: {payment_id} - ${total_revenue}")
        return royalty_payment
    
    async def get_comprehensive_analytics(
        self,
        platforms: List[AudioPlatform],
        start_date: datetime,
        end_date: datetime
    ) -> AudioAnalytics:
        """Get comprehensive analytics across platforms."""
        
        total_streams = 0
        total_revenue = Decimal('0')
        platform_breakdown = {}
        top_tracks = []
        
        for platform in platforms:
            platform_streams = 0
            platform_revenue = Decimal('0')
            platform_tracks = []
            
            for track_id, track in self.uploaded_tracks.items():
                if track.platform == platform:
                    try:
                        metrics = await self.get_streaming_metrics(platform, track_id, start_date, end_date)
                        platform_streams += metrics.streams
                        platform_revenue += metrics.revenue_generated
                        
                        platform_tracks.append({
                            "track_id": track_id,
                            "title": track.title,
                            "streams": metrics.streams,
                            "revenue": float(metrics.revenue_generated)
                        })
                    
                    except Exception as e:
                        logger.warning(f"Failed to get metrics for track {track_id}: {e}")
                        continue
            
            platform_breakdown[platform.value] = {
                "streams": platform_streams,
                "revenue": float(platform_revenue),
                "tracks": len(platform_tracks)
            }
            
            total_streams += platform_streams
            total_revenue += platform_revenue
            top_tracks.extend(platform_tracks)
        
        # Sort top tracks by streams
        top_tracks.sort(key=lambda x: x["streams"], reverse=True)
        top_tracks = top_tracks[:10]  # Top 10 tracks
        
        # Calculate growth metrics (simplified)
        growth_metrics = {
            "streams_growth": 15.5,  # Mock data - would calculate from historical data
            "revenue_growth": 12.3,
            "new_listeners_growth": 8.7
        }
        
        # Generate recommendations
        recommendations = [
            "Focus on promoting your top-performing tracks on social media",
            "Consider releasing similar content to your most successful tracks",
            "Optimize release timing based on your audience engagement patterns",
            "Explore playlist placement opportunities for better discovery"
        ]
        
        analytics = AudioAnalytics(
            platform=AudioPlatform.SPOTIFY,  # Primary platform
            period_start=start_date,
            period_end=end_date,
            total_streams=total_streams,
            total_revenue=total_revenue,
            top_tracks=top_tracks,
            audience_insights={
                "primary_demographics": {"18-24": 35, "25-34": 30, "35-44": 25, "45+": 10},
                "top_countries": ["US", "GB", "CA", "AU", "DE"],
                "peak_listening_hours": ["20:00", "21:00", "22:00"]
            },
            growth_metrics=growth_metrics,
            geographical_breakdown={"US": 35, "GB": 20, "CA": 15, "AU": 10, "Other": 20},
            platform_comparison=platform_breakdown,
            recommendations=recommendations,
            metadata={"analysis_date": datetime.now().isoformat()}
        )
        
        logger.info(f"Comprehensive analytics generated: {total_streams} streams, ${total_revenue} revenue")
        return analytics
    
    async def optimize_release_strategy(
        self,
        track_title: str,
        genre: str,
        target_platforms: List[AudioPlatform]
    ) -> Dict[str, Any]:
        """Optimize release strategy based on platform analytics."""
        
        # Analyze historical performance by genre and platform
        platform_performance = {}
        
        for platform in target_platforms:
            # Mock analysis - would use real historical data
            performance_score = 0.75  # Base score
            
            if platform == AudioPlatform.SPOTIFY:
                performance_score += 0.15 if genre in ["pop", "rock", "hip-hop"] else 0.05
            elif platform == AudioPlatform.SOUNDCLOUD:
                performance_score += 0.20 if genre in ["electronic", "indie", "experimental"] else 0.05
            elif platform == AudioPlatform.YOUTUBE_MUSIC:
                performance_score += 0.10  # Generally good for all genres
            
            platform_performance[platform.value] = {
                "performance_score": min(performance_score, 1.0),
                "recommended_release_time": "Friday 00:00 UTC",  # Standard music release time
                "expected_streams_30d": int(10000 * performance_score),
                "expected_revenue_30d": float(Decimal("30.00") * Decimal(str(performance_score)))
            }
        
        # Generate release strategy
        best_platform = max(platform_performance.items(), key=lambda x: x[1]["performance_score"])
        
        strategy = {
            "recommended_primary_platform": best_platform[0],
            "platform_performance": platform_performance,
            "release_timeline": {
                "announcement": "7 days before release",
                "pre_save_campaign": "14 days before release",
                "release_date": "Friday",
                "promotion_period": "30 days post-release"
            },
            "promotional_recommendations": [
                f"Focus initial promotion on {best_platform[0]} due to highest performance score",
                "Create platform-specific content for each release",
                "Utilize playlist placement opportunities",
                "Engage with your audience through live sessions"
            ],
            "estimated_totals": {
                "total_streams_30d": sum([p["expected_streams_30d"] for p in platform_performance.values()]),
                "total_revenue_30d": sum([p["expected_revenue_30d"] for p in platform_performance.values()])
            }
        }
        
        logger.info(f"Release strategy optimized for {track_title} - Primary platform: {best_platform[0]}")
        return strategy
    
    async def get_audio_accounts(self) -> List[AudioPlatformAccount]:
        """Get all connected audio platform accounts."""
        return list(self.audio_accounts.values())
    
    async def get_uploaded_tracks(self) -> List[AudioTrack]:
        """Get all uploaded tracks."""
        return list(self.uploaded_tracks.values())
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get audio platforms usage statistics."""
        return {
            "total_requests": self.request_count,
            "total_uploads": self.total_uploads,
            "total_streams_tracked": self.total_streams_tracked,
            "total_revenue_tracked": float(self.total_revenue_tracked),
            "platform_usage": dict(self.platform_usage),
            "connected_accounts": len(self.audio_accounts),
            "uploaded_tracks": len(self.uploaded_tracks),
            "average_revenue_per_stream": float(self.total_revenue_tracked / max(self.total_streams_tracked, 1))
        }


# Utility functions
async def create_audio_platforms_integration(
    spotify_client_id: Optional[str] = None,
    spotify_client_secret: Optional[str] = None,
    soundcloud_access_token: Optional[str] = None,
    youtube_api_key: Optional[str] = None
) -> AudioPlatformsIntegration:
    """Create and initialize audio platforms integration."""
    integration = AudioPlatformsIntegration(
        spotify_client_id=spotify_client_id,
        spotify_client_secret=spotify_client_secret,
        soundcloud_access_token=soundcloud_access_token,
        youtube_api_key=youtube_api_key
    )
    await integration._ensure_session()
    return integration


async def track_multi_platform_performance(
    integration: AudioPlatformsIntegration,
    track_title: str,
    platforms: List[AudioPlatform],
    period_days: int = 30
) -> Dict[str, Any]:
    """Track performance of the same track across multiple platforms."""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)
    
    platform_metrics = {}
    total_streams = 0
    total_revenue = Decimal('0')
    
    for platform in platforms:
        platform_tracks = [
            track for track in integration.uploaded_tracks.values()
            if track.platform == platform and track.title == track_title
        ]
        
        if platform_tracks:
            track = platform_tracks[0]  # Get first matching track
            try:
                metrics = await integration.get_streaming_metrics(
                    platform, track.track_id, start_date, end_date
                )
                
                platform_metrics[platform.value] = {
                    "streams": metrics.streams,
                    "revenue": float(metrics.revenue_generated),
                    "completion_rate": metrics.completion_rate,
                    "skip_rate": metrics.skip_rate,
                    "saves": metrics.saves,
                    "shares": metrics.shares
                }
                
                total_streams += metrics.streams
                total_revenue += metrics.revenue_generated
            
            except Exception as e:
                logger.warning(f"Failed to get metrics for {track_title} on {platform}: {e}")
                platform_metrics[platform.value] = None
        else:
            platform_metrics[platform.value] = None
    
    # Calculate performance comparison
    valid_platforms = {k: v for k, v in platform_metrics.items() if v is not None}
    
    if valid_platforms:
        best_performing = max(valid_platforms.items(), key=lambda x: x[1]["streams"])
        worst_performing = min(valid_platforms.items(), key=lambda x: x[1]["streams"])
        
        performance_analysis = {
            "track_title": track_title,
            "period_days": period_days,
            "platform_metrics": platform_metrics,
            "total_streams": total_streams,
            "total_revenue": float(total_revenue),
            "best_performing_platform": {
                "platform": best_performing[0],
                "streams": best_performing[1]["streams"],
                "revenue": best_performing[1]["revenue"]
            },
            "worst_performing_platform": {
                "platform": worst_performing[0],
                "streams": worst_performing[1]["streams"],
                "revenue": worst_performing[1]["revenue"]
            },
            "performance_variance": {
                "streams_ratio": best_performing[1]["streams"] / max(worst_performing[1]["streams"], 1),
                "revenue_ratio": best_performing[1]["revenue"] / max(worst_performing[1]["revenue"], 1)
            }
        }
    else:
        performance_analysis = {
            "track_title": track_title,
            "period_days": period_days,
            "platform_metrics": platform_metrics,
            "error": "No valid metrics found for any platform"
        }
    
    logger.info(f"Multi-platform performance tracked for {track_title}: {total_streams} total streams")
    return performance_analysis


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        import os
        
        async with AudioPlatformsIntegration(
            spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            spotify_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            soundcloud_access_token=os.getenv("SOUNDCLOUD_ACCESS_TOKEN"),
            youtube_api_key=os.getenv("YOUTUBE_API_KEY")
        ) as audio:
            # Initialize accounts
            try:
                if audio.spotify_client_id:
                    spotify_account = await audio.initialize_spotify_account()
                    print(f"Spotify account: {spotify_account.artist_name}")
            except Exception as e:
                print(f"Spotify initialization failed: {e}")
            
            # Get comprehensive analytics
            try:
                analytics = await audio.get_comprehensive_analytics(
                    platforms=[AudioPlatform.SPOTIFY, AudioPlatform.SOUNDCLOUD],
                    start_date=datetime.now() - timedelta(days=30),
                    end_date=datetime.now()
                )
                print(f"Total streams: {analytics.total_streams}")
                print(f"Total revenue: ${analytics.total_revenue}")
            except Exception as e:
                print(f"Analytics failed: {e}")
            
            # Check usage stats
            stats = audio.get_usage_stats()
            print(f"Usage stats: {stats}")
    
    asyncio.run(main())