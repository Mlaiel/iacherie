"""
Apple Music Platform Connector
==============================

Enterprise-grade Apple Music API connector for Ainflue Distribution Platform.
Supports Apple Music Connect for artists, MusicKit integration, and Apple Podcasts.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import aiohttp
import json
import jwt
import time
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AppleMusicContentType(Enum):
    """Apple Music content types"""
    SONG = "song"
    ALBUM = "album"
    PLAYLIST = "playlist"
    PODCAST = "podcast"
    PODCAST_EPISODE = "podcast_episode"
    MUSIC_VIDEO = "music_video"
    ARTIST_POST = "artist_post"

class AppleMusicGenre(Enum):
    """Apple Music genres"""
    POP = "pop"
    ROCK = "rock"
    HIP_HOP = "hip_hop"
    ELECTRONIC = "electronic"
    COUNTRY = "country"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    R_AND_B = "r_and_b"
    INDIE = "indie"
    ALTERNATIVE = "alternative"

@dataclass
class AppleMusicCredentials:
    """Apple Music API credentials"""
    team_id: str
    key_id: str
    private_key: str  # Path to private key file or key content
    bundle_id: str
    storefront: str = "us"

@dataclass
class AppleMusicTrack:
    """Apple Music track metadata"""
    title: str
    artist: str
    album: str
    duration: int  # Duration in seconds
    genre: AppleMusicGenre
    release_date: datetime
    isrc: Optional[str] = None
    explicit: bool = False
    preview_url: Optional[str] = None
    artwork_url: Optional[str] = None
    copyright: Optional[str] = None

@dataclass
class AppleMusicUploadResult:
    """Result of Apple Music upload operation"""
    success: bool
    track_id: Optional[str] = None
    store_url: Optional[str] = None
    status: str = "pending"
    message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class AppleMusicConnector:
    """Apple Music platform connector with MusicKit and Apple Music Connect integration"""
    
    BASE_URL = "https://api.music.apple.com/v1"
    CONNECT_URL = "https://tools.applemusicforartists.com/api"
    TOKEN_ALGORITHM = "ES256"
    
    def __init__(self, credentials: AppleMusicCredentials):
        """Initialize Apple Music connector"""
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self._generate_token()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _generate_token(self) -> str:
        """Generate JWT token for Apple Music API"""
        try:
            # Read private key
            if self.credentials.private_key.startswith("-----"):
                private_key = self.credentials.private_key
            else:
                private_key_path = Path(self.credentials.private_key)
                if not private_key_path.exists():
                    raise FileNotFoundError(f"Private key file not found: {private_key_path}")
                private_key = private_key_path.read_text()
            
            # JWT payload
            now = int(time.time())
            payload = {
                "iss": self.credentials.team_id,
                "iat": now,
                "exp": now + 15777000,  # 6 months
                "aud": "appstoreconnect-v1",
                "sub": self.credentials.bundle_id
            }
            
            # JWT header
            headers = {
                "alg": self.TOKEN_ALGORITHM,
                "kid": self.credentials.key_id,
                "typ": "JWT"
            }
            
            # Generate token
            self.token = jwt.encode(
                payload, 
                private_key, 
                algorithm=self.TOKEN_ALGORITHM,
                headers=headers
            )
            
            self.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=15777000)
            
            logger.info("Apple Music JWT token generated successfully")
            return self.token
            
        except Exception as e:
            logger.error(f"Failed to generate Apple Music token: {e}")
            raise
    
    async def _ensure_valid_token(self):
        """Ensure we have a valid token"""
        if not self.token or not self.token_expires_at:
            await self._generate_token()
        elif datetime.now(timezone.utc) >= self.token_expires_at - timedelta(minutes=5):
            await self._generate_token()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        use_connect_api: bool = False
    ) -> Dict[str, Any]:
        """Make authenticated request to Apple Music API"""
        await self._ensure_valid_token()
        
        base_url = self.CONNECT_URL if use_connect_api else self.BASE_URL
        url = f"{base_url}/{endpoint.lstrip('/')}"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            ) as response:
                
                if response.status == 401:
                    # Token might be expired, regenerate and retry
                    await self._generate_token()
                    headers["Authorization"] = f"Bearer {self.token}"
                    
                    async with self.session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=data,
                        params=params
                    ) as retry_response:
                        return await retry_response.json()
                
                response.raise_for_status()
                return await response.json()
                
        except aiohttp.ClientError as e:
            logger.error(f"Apple Music API request failed: {e}")
            raise
    
    async def search_catalog(
        self, 
        query: str, 
        types: List[str] = None,
        limit: int = 25
    ) -> Dict[str, Any]:
        """Search Apple Music catalog"""
        if types is None:
            types = ["songs", "albums", "artists", "playlists"]
        
        params = {
            "term": query,
            "types": ",".join(types),
            "limit": limit
        }
        
        return await self._make_request("GET", "/catalog/us/search", params=params)
    
    async def get_track_details(self, track_id: str) -> Dict[str, Any]:
        """Get detailed information about a track"""
        return await self._make_request("GET", f"/catalog/us/songs/{track_id}")
    
    async def get_artist_catalog(self, artist_id: str) -> Dict[str, Any]:
        """Get artist's catalog information"""
        return await self._make_request("GET", f"/catalog/us/artists/{artist_id}")
    
    async def submit_track_for_distribution(
        self, 
        track: AppleMusicTrack,
        audio_file_path: str
    ) -> AppleMusicUploadResult:
        """Submit track for Apple Music distribution (via Apple Music Connect)"""
        try:
            # Prepare track metadata
            metadata = {
                "title": track.title,
                "artist": track.artist,
                "album": track.album,
                "duration": track.duration,
                "genre": track.genre.value,
                "releaseDate": track.release_date.isoformat(),
                "explicit": track.explicit,
                "storefront": self.credentials.storefront
            }
            
            if track.isrc:
                metadata["isrc"] = track.isrc
            if track.copyright:
                metadata["copyright"] = track.copyright
            
            # Submit metadata first
            response = await self._make_request(
                "POST", 
                "/catalog/submission", 
                data=metadata,
                use_connect_api=True
            )
            
            if response.get("success"):
                return AppleMusicUploadResult(
                    success=True,
                    track_id=response.get("trackId"),
                    store_url=response.get("storeUrl"),
                    status="submitted_for_review",
                    message="Track submitted successfully for Apple Music distribution",
                    metadata=response
                )
            else:
                return AppleMusicUploadResult(
                    success=False,
                    message=response.get("error", "Unknown error occurred"),
                    metadata=response
                )
                
        except Exception as e:
            logger.error(f"Failed to submit track to Apple Music: {e}")
            return AppleMusicUploadResult(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    async def create_playlist(
        self, 
        name: str, 
        description: str,
        track_ids: List[str],
        is_public: bool = True
    ) -> Dict[str, Any]:
        """Create a new playlist"""
        playlist_data = {
            "attributes": {
                "name": name,
                "description": description,
                "isPublic": is_public
            },
            "relationships": {
                "tracks": {
                    "data": [
                        {"id": track_id, "type": "songs"} 
                        for track_id in track_ids
                    ]
                }
            }
        }
        
        return await self._make_request(
            "POST", 
            "/me/library/playlists", 
            data={"data": [playlist_data]}
        )
    
    async def get_streaming_analytics(
        self, 
        track_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get streaming analytics for a track (Apple Music Connect)"""
        params = {
            "trackId": track_id,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "granularity": "day"
        }
        
        return await self._make_request(
            "GET", 
            "/analytics/streams", 
            params=params,
            use_connect_api=True
        )
    
    async def get_royalty_reports(
        self, 
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get royalty reports (Apple Music Connect)"""
        params = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat()
        }
        
        return await self._make_request(
            "GET", 
            "/financial/royalty-reports", 
            params=params,
            use_connect_api=True
        )
    
    async def validate_connection(self) -> bool:
        """Validate Apple Music API connection"""
        try:
            await self._ensure_valid_token()
            
            # Test with a simple catalog request
            result = await self.search_catalog("test", limit=1)
            return result is not None
            
        except Exception as e:
            logger.error(f"Apple Music connection validation failed: {e}")
            return False
    
    async def get_platform_limits(self) -> Dict[str, Any]:
        """Get Apple Music platform limits and guidelines"""
        return {
            "max_file_size_mb": 500,  # 500MB for audio files
            "supported_formats": ["mp3", "aac", "m4a", "wav", "flac"],
            "max_track_duration_seconds": 600,  # 10 minutes
            "min_track_duration_seconds": 30,
            "max_playlist_tracks": 100000,
            "rate_limit": {
                "requests_per_hour": 1000,
                "requests_per_day": 20000
            },
            "content_guidelines": {
                "explicit_content_allowed": True,
                "copyright_protection_required": True,
                "metadata_required_fields": [
                    "title", "artist", "album", "duration", "genre"
                ]
            }
        }


# Export main components
__all__ = [
    "AppleMusicConnector",
    "AppleMusicCredentials", 
    "AppleMusicTrack",
    "AppleMusicUploadResult",
    "AppleMusicContentType",
    "AppleMusicGenre"
]