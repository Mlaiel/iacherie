"""
Apple Music Crawling Engine
==========================

Advanced Apple Music crawler for music discovery, artist analytics, and playlist data.
Handles track metadata extraction, artist analysis, and Apple Music API integration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

  AVERTISSEMENT LÉGAL 
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import hashlib
import json
from urllib.parse import urljoin, urlparse, parse_qs

import aiohttp
import jwt
from cryptography.hazmat.primitives import serialization
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..models.content_models import MusicContent, ArtistContent, PlaylistContent
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class AppleMusicTrack:
    """Apple Music track data structure"""
    id: str
    name: str
    artist_name: str
    artist_id: str
    album_name: str
    album_id: str
    duration_ms: int
    preview_url: Optional[str]
    artwork_url: Optional[str]
    release_date: str
    genre: List[str]
    isrc: Optional[str]
    explicit: bool
    play_count: Optional[int]
    popularity_score: Optional[float]
    url: str
    created_at: datetime


@dataclass
class AppleMusicArtist:
    """Apple Music artist data structure"""
    id: str
    name: str
    artwork_url: Optional[str]
    genre: List[str]
    url: str
    biography: Optional[str]
    follower_count: Optional[int]
    monthly_listeners: Optional[int]
    top_tracks: List[str]
    albums: List[str]
    verified: bool
    created_at: datetime


@dataclass
class AppleMusicPlaylist:
    """Apple Music playlist data structure"""
    id: str
    name: str
    description: Optional[str]
    curator_name: str
    artwork_url: Optional[str]
    track_count: int
    tracks: List[str]
    url: str
    last_modified: datetime
    created_at: datetime


class AppleMusicCrawlerEngine(BaseCrawlerEngine):
    """
    Professional Apple Music crawler engine for comprehensive music data extraction.
    
    Features:
    - Apple Music API integration
    - Track metadata extraction
    - Artist analytics and insights
    - Playlist data analysis
    - Advanced rate limiting
    - Content protection monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Apple Music crawler engine"""
        super().__init__(platform="apple_music", config=config)
        
        # Apple Music API configuration
        self.team_id = self.config.get("apple_team_id")
        self.key_id = self.config.get("apple_key_id")
        self.private_key_path = self.config.get("apple_private_key_path")
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            requests_per_minute=120,  # Apple Music API limits
            requests_per_hour=6000
        )
        
        # Cache configuration
        self.cache_manager = CacheManager(
            cache_ttl=timedelta(hours=1),
            max_cache_size=10000
        )
        
        # API endpoints
        self.base_url = "https://api.music.apple.com/v1"
        self.storefront = self.config.get("storefront", "us")
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        
        logger.info("Apple Music crawler engine initialized")
    
    async def initialize(self) -> None:
        """Initialize the crawler engine"""



        try:
            await self._generate_jwt_token()
            await self._create_session()
            logger.info("Apple Music engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Apple Music engine: {e}")
            raise CrawlerError(f"Initialization failed: {e}")
    
    async def _generate_jwt_token(self) -> None:
        """Generate JWT token for Apple Music API authentication"""



        try:
            if not all([self.team_id, self.key_id, self.private_key_path]):
                raise AuthenticationError("Missing Apple Music API credentials")
            
            # Load private key
            with open(self.private_key_path, 'rb') as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )
            
            # JWT payload
            now = datetime.utcnow()
            payload = {
                'iss': self.team_id,
                'iat': int(now.timestamp()),
                'exp': int((now + timedelta(hours=12)).timestamp()),
                'aud': 'appstoreconnect-v1'
            }
            
            # Generate token
            self.auth_token = jwt.encode(
                payload,
                private_key,
                algorithm='ES256',
                headers={'kid': self.key_id}
            )
            
            logger.info("JWT token generated successfully")
            
        except Exception as e:
            logger.error(f"Failed to generate JWT token: {e}")
            raise AuthenticationError(f"JWT generation failed: {e}")
    
    async def _create_session(self) -> None:
        """Create HTTP session with proper headers"""
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'User-Agent': self.config.get('user_agent', 'IA-Influencer-Agent/1.0'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=100)
        )
    
    async def search_tracks(
        self,
        query: str,
        limit: int = 25,
        offset: int = 0
    ) -> List[AppleMusicTrack]:
        """
        Search for tracks on Apple Music
        
        Args:
            query: Search query
            limit: Number of results to return
            offset: Offset for pagination
            
        Returns:
            List of track data
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"search_tracks:{hashlib.md5(f'{query}:{limit}:{offset}'.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # API request
            params = {
                'term': query,
                'types': 'songs',
                'limit': min(limit, 50),
                'offset': offset
            }
            
            url = f"{self.base_url}/catalog/{self.storefront}/search"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 429:
                    raise RateLimitError("Apple Music API rate limit exceeded")
                elif response.status == 401:
                    raise AuthenticationError("Invalid Apple Music API credentials")
                elif response.status != 200:
                    raise CrawlerError(f"API request failed: {response.status}")
                
                data = await response.json()
                tracks = []
                
                if 'results' in data and 'songs' in data['results']:
                    for song_data in data['results']['songs']['data']:
                        track = self._parse_track_data(song_data)
                        tracks.append(track)
                
                # Cache results
                await self.cache_manager.set(cache_key, tracks)
                
                logger.info(f"Found {len(tracks)} tracks for query: {query}")
                return tracks
                
        except Exception as e:
            logger.error(f"Error searching tracks: {e}")
            raise CrawlerError(f"Track search failed: {e}")
    
    async def get_track_details(self, track_id: str) -> Optional[AppleMusicTrack]:
        """
        Get detailed information about a specific track
        
        Args:
            track_id: Apple Music track ID
            
        Returns:
            Track details or None if not found
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"track_details:{track_id}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            url = f"{self.base_url}/catalog/{self.storefront}/songs/{track_id}"
            
            async with self.session.get(url) as response:
                if response.status == 404:
                    raise ContentNotFoundError(f"Track not found: {track_id}")
                elif response.status == 429:
                    raise RateLimitError("Apple Music API rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"API request failed: {response.status}")
                
                data = await response.json()
                
                if 'data' in data and data['data']:
                    track = self._parse_track_data(data['data'][0])
                    
                    # Cache result
                    await self.cache_manager.set(cache_key, track)
                    
                    return track
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting track details: {e}")
            raise CrawlerError(f"Track details retrieval failed: {e}")
    
    async def get_artist_info(self, artist_id: str) -> Optional[AppleMusicArtist]:
        """
        Get detailed information about an artist
        
        Args:
            artist_id: Apple Music artist ID
            
        Returns:
            Artist information or None if not found
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"artist_info:{artist_id}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            url = f"{self.base_url}/catalog/{self.storefront}/artists/{artist_id}"
            
            async with self.session.get(url) as response:
                if response.status == 404:
                    raise ContentNotFoundError(f"Artist not found: {artist_id}")
                elif response.status == 429:
                    raise RateLimitError("Apple Music API rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"API request failed: {response.status}")
                
                data = await response.json()
                
                if 'data' in data and data['data']:
                    artist = self._parse_artist_data(data['data'][0])
                    
                    # Cache result
                    await self.cache_manager.set(cache_key, artist)
                    
                    return artist
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting artist info: {e}")
            raise CrawlerError(f"Artist info retrieval failed: {e}")
    
    async def get_playlist_info(self, playlist_id: str) -> Optional[AppleMusicPlaylist]:
        """
        Get detailed information about a playlist
        
        Args:
            playlist_id: Apple Music playlist ID
            
        Returns:
            Playlist information or None if not found
        """



        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"playlist_info:{playlist_id}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            url = f"{self.base_url}/catalog/{self.storefront}/playlists/{playlist_id}"
            
            async with self.session.get(url) as response:
                if response.status == 404:
                    raise ContentNotFoundError(f"Playlist not found: {playlist_id}")
                elif response.status == 429:
                    raise RateLimitError("Apple Music API rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"API request failed: {response.status}")
                
                data = await response.json()
                
                if 'data' in data and data['data']:
                    playlist = self._parse_playlist_data(data['data'][0])
                    
                    # Cache result
                    await self.cache_manager.set(cache_key, playlist)
                    
                    return playlist
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting playlist info: {e}")
            raise CrawlerError(f"Playlist info retrieval failed: {e}")
    
    def _parse_track_data(self, track_data: Dict[str, Any]) -> AppleMusicTrack:
        """Parse Apple Music track data"""
        attributes = track_data.get('attributes', {})
        
        return AppleMusicTrack(
            id=track_data.get('id', ''),
            name=attributes.get('name', ''),
            artist_name=attributes.get('artistName', ''),
            artist_id='',  # Would need additional API call
            album_name=attributes.get('albumName', ''),
            album_id='',  # Would need additional API call
            duration_ms=attributes.get('durationInMillis', 0),
            preview_url=attributes.get('previews', [{}])[0].get('url') if attributes.get('previews') else None,
            artwork_url=attributes.get('artwork', {}).get('url', '').replace('{w}x{h}', '400x400') if attributes.get('artwork') else None,
            release_date=attributes.get('releaseDate', ''),
            genre=attributes.get('genreNames', []),
            isrc=attributes.get('isrc'),
            explicit=attributes.get('contentRating') == 'explicit',
            play_count=None,  # Not available in public API
            popularity_score=None,  # Would need to calculate
            url=attributes.get('url', ''),
            created_at=datetime.utcnow()
        )
    
    def _parse_artist_data(self, artist_data: Dict[str, Any]) -> AppleMusicArtist:
        """Parse Apple Music artist data"""
        attributes = artist_data.get('attributes', {})
        
        return AppleMusicArtist(
            id=artist_data.get('id', ''),
            name=attributes.get('name', ''),
            artwork_url=attributes.get('artwork', {}).get('url', '').replace('{w}x{h}', '400x400') if attributes.get('artwork') else None,
            genre=attributes.get('genreNames', []),
            url=attributes.get('url', ''),
            biography=None,  # Not available in public API
            follower_count=None,  # Not available in public API
            monthly_listeners=None,  # Not available in public API
            top_tracks=[],  # Would need additional API call
            albums=[],  # Would need additional API call
            verified=False,  # Not available in public API
            created_at=datetime.utcnow()
        )
    
    def _parse_playlist_data(self, playlist_data: Dict[str, Any]) -> AppleMusicPlaylist:
        """Parse Apple Music playlist data"""
        attributes = playlist_data.get('attributes', {})
        
        return AppleMusicPlaylist(
            id=playlist_data.get('id', ''),
            name=attributes.get('name', ''),
            description=attributes.get('description', {}).get('standard'),
            curator_name=attributes.get('curatorName', ''),
            artwork_url=attributes.get('artwork', {}).get('url', '').replace('{w}x{h}', '400x400') if attributes.get('artwork') else None,
            track_count=attributes.get('trackCount', 0),
            tracks=[],  # Would need additional API call
            url=attributes.get('url', ''),
            last_modified=datetime.fromisoformat(attributes.get('lastModifiedDate', '').replace('Z', '+00:00')) if attributes.get('lastModifiedDate') else datetime.utcnow(),
            created_at=datetime.utcnow()
        )
    
    async def monitor_content_protection(
        self,
        artist_name: str,
        track_title: str
    ) -> Dict[str, Any]:
        """
        Monitor for unauthorized use of artist content
        
        Args:
            artist_name: Name of the artist
            track_title: Title of the track
            
        Returns:
            Protection monitoring results
        """



        try:
            # Search for potential unauthorized use
            search_queries = [
                f"{artist_name} {track_title}",
                f"{track_title} cover",
                f"{track_title} remix"
            ]
            
            protection_results = {
                'artist_name': artist_name,
                'track_title': track_title,
                'potential_violations': [],
                'monitoring_timestamp': datetime.utcnow().isoformat()
            }
            
            for query in search_queries:
                tracks = await self.search_tracks(query, limit=50)
                
                for track in tracks:
                    # Check for potential unauthorized use
                    if (track.name.lower() != track_title.lower() and 
                        track_title.lower() in track.name.lower() and
                        track.artist_name.lower() != artist_name.lower()):
                        
                        protection_results['potential_violations'].append({
                            'track_id': track.id,
                            'track_name': track.name,
                            'artist_name': track.artist_name,
                            'similarity_score': self._calculate_similarity(track_title, track.name),
                            'url': track.url
                        })
            
            logger.info(f"Content protection monitoring completed for {artist_name} - {track_title}")
            return protection_results
            
        except Exception as e:
            logger.error(f"Error in content protection monitoring: {e}")
            raise CrawlerError(f"Content protection monitoring failed: {e}")
    
    def _calculate_similarity(self, original: str, candidate: str) -> float:
        """Calculate similarity score between two strings"""
        original_words = set(original.lower().split())
        candidate_words = set(candidate.lower().split())
        
        if not original_words:
            return 0.0
        
        intersection = original_words.intersection(candidate_words)
        return len(intersection) / len(original_words)
    
    async def cleanup(self) -> None:
        """Clean up resources"""



        try:
            if self.session:
                await self.session.close()
            await super().cleanup()
            logger.info("Apple Music engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __str__(self) -> str:
        return f"AppleMusicCrawlerEngine(platform=apple_music, storefront={self.storefront})"
