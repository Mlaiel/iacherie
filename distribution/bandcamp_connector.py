"""
Bandcamp Platform Connector
==========================

Enterprise-grade Bandcamp API connector for Ainflue Distribution Platform.
Supports music publishing, fan engagement, merchandise, and revenue tracking.

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
import hashlib
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class BandcampContentType(Enum):
    """Bandcamp content types"""
    ALBUM = "album"
    TRACK = "track"
    MERCH = "merchandise"
    FAN_UPDATE = "fan_update"
    CONCERT = "concert"
    LIVESTREAM = "livestream"

class BandcampGenre(Enum):
    """Bandcamp music genres"""
    ELECTRONIC = "electronic"
    ROCK = "rock"
    METAL = "metal"
    PUNK = "punk"
    INDIE = "indie"
    FOLK = "folk"
    JAZZ = "jazz"
    EXPERIMENTAL = "experimental"
    AMBIENT = "ambient"
    HIP_HOP = "hip_hop"

@dataclass
class BandcampTrack:
    """Bandcamp track data structure"""
    title: str
    artist: str
    album: Optional[str] = None
    genre: Optional[str] = None
    price: Optional[float] = None
    lyrics: Optional[str] = None
    credits: Optional[str] = None
    about: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    release_date: Optional[datetime] = None
    is_downloadable: bool = True
    is_streamable: bool = True

@dataclass
class BandcampAlbum:
    """Bandcamp album data structure"""
    title: str
    artist: str
    tracks: List[BandcampTrack]
    genre: Optional[str] = None
    price: Optional[float] = None
    about: Optional[str] = None
    credits: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    release_date: Optional[datetime] = None
    artwork_url: Optional[str] = None

@dataclass
class BandcampMerch:
    """Bandcamp merchandise data structure"""
    title: str
    type: str  # t-shirt, vinyl, cd, poster, etc.
    price: float
    description: str
    images: List[str] = field(default_factory=list)
    quantity: Optional[int] = None
    shipping_info: Optional[str] = None

class BandcampConnector:
    """
    Enterprise Bandcamp API Connector
    
    Provides comprehensive integration with Bandcamp platform for:
    - Music publishing and distribution
    - Fan engagement and updates
    - Merchandise management
    - Revenue tracking and analytics
    - Live streaming and concert promotion
    """
    
    def __init__(self, band_id: str, username: str, password: str):
        """
        Initialize Bandcamp connector
        
        Args:
            band_id: Bandcamp band identifier
            username: Bandcamp username
            password: Bandcamp password
        """
        self.band_id = band_id
        self.username = username
        self.password = password
        self.base_url = "https://bandcamp.com/api"
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_authenticated = False
        self.rate_limit_remaining = 100
        self.rate_limit_reset = datetime.now()
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def authenticate(self) -> bool:
        """
        Authenticate with Bandcamp
        
        Returns:
            bool: Authentication success status
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Bandcamp uses session-based authentication
            auth_data = {
                'username': self.username,
                'password': self.password
            }
            
            async with self.session.post(
                f"{self.base_url}/login",
                data=auth_data
            ) as response:
                if response.status == 200:
                    self.is_authenticated = True
                    logger.info(f"Successfully authenticated with Bandcamp for band: {self.band_id}")
                    return True
                else:
                    logger.error(f"Bandcamp authentication failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Bandcamp authentication error: {str(e)}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """
        Make authenticated API request with rate limiting
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Optional[Dict]: API response data
        """
        if not self.is_authenticated:
            await self.authenticate()
        
        # Check rate limits
        if self.rate_limit_remaining <= 0:
            if datetime.now() < self.rate_limit_reset:
                wait_time = (self.rate_limit_reset - datetime.now()).total_seconds()
                await asyncio.sleep(wait_time)
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            async with self.session.request(method, url, **kwargs) as response:
                # Update rate limiting info
                self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 100))
                reset_time = response.headers.get('X-RateLimit-Reset')
                if reset_time:
                    self.rate_limit_reset = datetime.fromtimestamp(int(reset_time))
                
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logger.warning("Bandcamp rate limit exceeded")
                    return None
                else:
                    logger.error(f"Bandcamp API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Bandcamp API request error: {str(e)}")
            return None
    
    async def publish_track(self, track: BandcampTrack, audio_file: Path) -> Optional[str]:
        """
        Publish a track to Bandcamp
        
        Args:
            track: Track metadata
            audio_file: Path to audio file
            
        Returns:
            Optional[str]: Track URL if successful
        """
        try:
            # Prepare track data
            track_data = {
                'band_id': self.band_id,
                'title': track.title,
                'artist': track.artist,
                'genre': track.genre,
                'price': track.price,
                'lyrics': track.lyrics,
                'credits': track.credits,
                'about': track.about,
                'tags': ','.join(track.tags),
                'release_date': track.release_date.isoformat() if track.release_date else None,
                'is_downloadable': track.is_downloadable,
                'is_streamable': track.is_streamable
            }
            
            # Upload audio file
            with open(audio_file, 'rb') as f:
                files = {'audio': f}
                
                response = await self._make_request(
                    'POST',
                    f'/band/{self.band_id}/tracks',
                    data=track_data,
                    files=files
                )
            
            if response and 'track_url' in response:
                logger.info(f"Successfully published track: {track.title}")
                return response['track_url']
            else:
                logger.error(f"Failed to publish track: {track.title}")
                return None
                
        except Exception as e:
            logger.error(f"Error publishing track: {str(e)}")
            return None
    
    async def publish_album(self, album: BandcampAlbum, audio_files: List[Path], artwork: Optional[Path] = None) -> Optional[str]:
        """
        Publish an album to Bandcamp
        
        Args:
            album: Album metadata
            audio_files: List of audio file paths
            artwork: Optional album artwork
            
        Returns:
            Optional[str]: Album URL if successful
        """
        try:
            # Prepare album data
            album_data = {
                'band_id': self.band_id,
                'title': album.title,
                'artist': album.artist,
                'genre': album.genre,
                'price': album.price,
                'about': album.about,
                'credits': album.credits,
                'tags': ','.join(album.tags),
                'release_date': album.release_date.isoformat() if album.release_date else None,
                'track_count': len(album.tracks)
            }
            
            # Upload files
            files = {}
            if artwork:
                with open(artwork, 'rb') as f:
                    files['artwork'] = f.read()
            
            for i, audio_file in enumerate(audio_files):
                with open(audio_file, 'rb') as f:
                    files[f'track_{i}'] = f.read()
            
            response = await self._make_request(
                'POST',
                f'/band/{self.band_id}/albums',
                data=album_data,
                files=files
            )
            
            if response and 'album_url' in response:
                logger.info(f"Successfully published album: {album.title}")
                return response['album_url']
            else:
                logger.error(f"Failed to publish album: {album.title}")
                return None
                
        except Exception as e:
            logger.error(f"Error publishing album: {str(e)}")
            return None
    
    async def add_merchandise(self, merch: BandcampMerch) -> Optional[str]:
        """
        Add merchandise item to Bandcamp
        
        Args:
            merch: Merchandise data
            
        Returns:
            Optional[str]: Merchandise item ID if successful
        """
        try:
            merch_data = {
                'band_id': self.band_id,
                'title': merch.title,
                'type': merch.type,
                'price': merch.price,
                'description': merch.description,
                'quantity': merch.quantity,
                'shipping_info': merch.shipping_info
            }
            
            response = await self._make_request(
                'POST',
                f'/band/{self.band_id}/merch',
                json=merch_data
            )
            
            if response and 'merch_id' in response:
                logger.info(f"Successfully added merchandise: {merch.title}")
                return response['merch_id']
            else:
                logger.error(f"Failed to add merchandise: {merch.title}")
                return None
                
        except Exception as e:
            logger.error(f"Error adding merchandise: {str(e)}")
            return None
    
    async def send_fan_update(self, title: str, message: str, send_email: bool = True) -> bool:
        """
        Send update to fans
        
        Args:
            title: Update title
            message: Update message
            send_email: Whether to send email notification
            
        Returns:
            bool: Success status
        """
        try:
            update_data = {
                'band_id': self.band_id,
                'title': title,
                'message': message,
                'send_email': send_email,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            response = await self._make_request(
                'POST',
                f'/band/{self.band_id}/fan_updates',
                json=update_data
            )
            
            if response:
                logger.info(f"Successfully sent fan update: {title}")
                return True
            else:
                logger.error(f"Failed to send fan update: {title}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending fan update: {str(e)}")
            return False
    
    async def get_analytics(self, start_date: datetime, end_date: datetime) -> Optional[Dict]:
        """
        Get Bandcamp analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Optional[Dict]: Analytics data
        """
        try:
            params = {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
            
            response = await self._make_request(
                'GET',
                f'/band/{self.band_id}/analytics',
                params=params
            )
            
            if response:
                logger.info("Successfully retrieved Bandcamp analytics")
                return response
            else:
                logger.error("Failed to retrieve Bandcamp analytics")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving analytics: {str(e)}")
            return None
    
    async def get_fan_insights(self) -> Optional[Dict]:
        """
        Get fan demographics and insights
        
        Returns:
            Optional[Dict]: Fan insights data
        """
        try:
            response = await self._make_request(
                'GET',
                f'/band/{self.band_id}/fans/insights'
            )
            
            if response:
                logger.info("Successfully retrieved fan insights")
                return response
            else:
                logger.error("Failed to retrieve fan insights")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving fan insights: {str(e)}")
            return None
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            self.is_authenticated = False

# Usage example
async def main():
    """Example usage of BandcampConnector"""
    async with BandcampConnector(
        band_id="my_band_123",
        username="my_username",
        password="my_password"
    ) as bandcamp:
        
        # Publish a track
        track = BandcampTrack(
            title="My New Song",
            artist="My Artist Name",
            genre="electronic",
            price=5.0,
            tags=["electronic", "ambient", "chill"]
        )
        
        track_url = await bandcamp.publish_track(track, Path("song.mp3"))
        print(f"Track published: {track_url}")
        
        # Send fan update
        await bandcamp.send_fan_update(
            "New Release!",
            "Check out my latest track on Bandcamp!"
        )
        
        # Get analytics
        analytics = await bandcamp.get_analytics(
            datetime.now() - timedelta(days=30),
            datetime.now()
        )
        print(f"Analytics: {analytics}")

if __name__ == "__main__":
    asyncio.run(main())