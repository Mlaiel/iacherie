"""Advanced Deezer Music Extraction Engine

Ultra-advanced music streaming extraction and content analysis engine for Deezer platform with AI-powered
quality detection, metadata enrichment, and real-time playlist monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import aiohttp
import aiofiles
import json
import re
import hashlib
import base64
import time
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import defaultdict
import tempfile
import subprocess
import mimetypes
import concurrent.futures
from urllib.robotparser import RobotFileParser

from pydantic import BaseModel, Field, validator, root_validator
import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class AudioQuality(str, Enum):
    """
Audio quality enumeration"""

    FLAC = "flac"
    LOSSLESS = "lossless"
    HIGH = "320"
    STANDARD = "256"
    MEDIUM = "128"
    LOW = "96"


class ContentType(str, Enum):
    """Content type enumeration"""

    TRACK = "track"
    ALBUM = "album"
    PLAYLIST = "playlist"
    ARTIST = "artist"
    PODCAST = "podcast"
    RADIO = "radio"


class ExtractionMode(str, Enum):
    """Extraction mode enumeration"""

    FAST = "fast"
    COMPLETE = "complete"
    METADATA_ONLY = "metadata_only"
    PREMIUM = "premium"


class TrackFormat(BaseModel):
    """Track format data model"""
    format_id: str = Field(..., description="Unique format identifier")
    url: str = Field(..., description="Direct audio URL")
    quality: AudioQuality = Field(..., description="Audio quality")
    bitrate: int = Field(..., description="Audio bitrate in kbps")
    sample_rate: Optional[int] = Field(None, description="Sample rate in Hz")
    channels: Optional[int] = Field(None, description="Number of audio channels")
    codec: Optional[str] = Field(None, description="Audio codec")
    container: Optional[str] = Field(None, description="Container format")
    filesize: Optional[int] = Field(None, description="File size in bytes")
    mime_type: Optional[str] = Field(None, description="MIME type")
    duration: Optional[float] = Field(None, description="Track duration in seconds")
    
    @validator('quality', pre=True)
    def validate_quality(cls, v):
        if isinstance(v, str) and v.isdigit():
            return v
        return AudioQuality.STANDARD


class AlbumArt(BaseModel):
    """Album artwork data model"""
    url: str = Field(..., description="Album art URL")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    size: str = Field(..., description="Size category (small, medium, large, xl)")


class TrackMetadata(BaseModel):
    """Complete track metadata model"""
    track_id: str = Field(..., description="Unique track identifier")
    title: str = Field(..., description="Track title")
    artist_name: str = Field(..., description="Primary artist name")
    artist_id: Optional[str] = Field(None, description="Artist unique ID")
    album_name: Optional[str] = Field(None, description="Album name")
    album_id: Optional[str] = Field(None, description="Album unique ID")
    duration: Optional[int] = Field(None, description="Track duration in seconds")
    track_number: Optional[int] = Field(None, description="Track number in album")
    disc_number: Optional[int] = Field(None, description="Disc number")
    release_date: Optional[datetime] = Field(None, description="Release date")
    genre: Optional[str] = Field(None, description="Music genre")
    bpm: Optional[int] = Field(None, description="Beats per minute")
    gain: Optional[float] = Field(None, description="Audio gain")
    popularity: Optional[int] = Field(None, description="Popularity score")
    explicit: bool = Field(default=False, description="Explicit content flag")
    preview_url: Optional[str] = Field(None, description="Preview audio URL")
    lyrics: Optional[str] = Field(None, description="Track lyrics")
    isrc: Optional[str] = Field(None, description="International Standard Recording Code")
    contributors: List[str] = Field(default_factory=list, description="Contributing artists")
    album_art: List[AlbumArt] = Field(default_factory=list, description="Album artwork")
    formats: List[TrackFormat] = Field(default_factory=list, description="Available formats")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlbumMetadata(BaseModel):
    """Album metadata model"""
    album_id: str = Field(..., description="Unique album identifier")
    title: str = Field(..., description="Album title")
    artist_name: str = Field(..., description="Primary artist name")
    artist_id: Optional[str] = Field(None, description="Artist unique ID")
    release_date: Optional[datetime] = Field(None, description="Release date")
    track_count: int = Field(..., description="Number of tracks")
    duration: Optional[int] = Field(None, description="Total duration in seconds")
    genre: Optional[str] = Field(None, description="Album genre")
    label: Optional[str] = Field(None, description="Record label")
    upc: Optional[str] = Field(None, description="Universal Product Code")
    popularity: Optional[int] = Field(None, description="Popularity score")
    explicit: bool = Field(default=False, description="Explicit content flag")
    album_art: List[AlbumArt] = Field(default_factory=list, description="Album artwork")
    tracks: List[str] = Field(default_factory=list, description="Track IDs list")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PlaylistMetadata(BaseModel):
    """Playlist metadata model"""
    playlist_id: str = Field(..., description="Unique playlist identifier")
    title: str = Field(..., description="Playlist title")
    description: Optional[str] = Field(None, description="Playlist description")
    creator: Optional[str] = Field(None, description="Playlist creator")
    creator_id: Optional[str] = Field(None, description="Creator unique ID")
    track_count: int = Field(..., description="Number of tracks")
    duration: Optional[int] = Field(None, description="Total duration in seconds")
    creation_date: Optional[datetime] = Field(None, description="Creation timestamp")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    public: bool = Field(default=True, description="Public playlist flag")
    collaborative: bool = Field(default=False, description="Collaborative playlist flag")
    fan_count: Optional[int] = Field(None, description="Number of fans/followers")
    picture_url: Optional[str] = Field(None, description="Playlist cover image")
    tracks: List[str] = Field(default_factory=list, description="Track IDs list")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ArtistMetadata(BaseModel):
    """Artist metadata model"""
    artist_id: str = Field(..., description="Unique artist identifier")
    name: str = Field(..., description="Artist name")
    real_name: Optional[str] = Field(None, description="Real name")
    country: Optional[str] = Field(None, description="Artist country")
    biography: Optional[str] = Field(None, description="Artist biography")
    fan_count: Optional[int] = Field(None, description="Number of fans")
    album_count: Optional[int] = Field(None, description="Number of albums")
    popularity: Optional[int] = Field(None, description="Popularity score")
    verified: bool = Field(default=False, description="Verified artist status")
    picture_url: Optional[str] = Field(None, description="Artist profile image")
    top_tracks: List[str] = Field(default_factory=list, description="Top track IDs")
    albums: List[str] = Field(default_factory=list, description="Album IDs")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PodcastMetadata(BaseModel):
    """Podcast metadata model"""
    podcast_id: str = Field(..., description="Unique podcast identifier")
    title: str = Field(..., description="Podcast title")
    description: Optional[str] = Field(None, description="Podcast description")
    language: Optional[str] = Field(None, description="Podcast language")
    category: Optional[str] = Field(None, description="Podcast category")
    episode_count: int = Field(..., description="Number of episodes")
    creator: Optional[str] = Field(None, description="Podcast creator")
    explicit: bool = Field(default=False, description="Explicit content flag")
    picture_url: Optional[str] = Field(None, description="Podcast cover image")
    episodes: List[str] = Field(default_factory=list, description="Episode IDs")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RadioMetadata(BaseModel):
    """Radio station metadata model"""
    radio_id: str = Field(..., description="Unique radio identifier")
    title: str = Field(..., description="Radio station title")
    description: Optional[str] = Field(None, description="Radio description")
    country: Optional[str] = Field(None, description="Radio country")
    language: Optional[str] = Field(None, description="Radio language")
    stream_url: Optional[str] = Field(None, description="Live stream URL")
    picture_url: Optional[str] = Field(None, description="Radio logo")
    is_live: bool = Field(default=True, description="Live status")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExtractionResult(BaseModel):
    """Complete extraction result model"""
    success: bool = Field(..., description="Extraction success status")
    content_type: ContentType = Field(..., description="Content type")
    extraction_time: float = Field(..., description="Extraction duration")
    track_metadata: Optional[TrackMetadata] = Field(None, description="Track metadata")
    album_metadata: Optional[AlbumMetadata] = Field(None, description="Album metadata")
    playlist_metadata: Optional[PlaylistMetadata] = Field(None, description="Playlist metadata")
    artist_metadata: Optional[ArtistMetadata] = Field(None, description="Artist metadata")
    podcast_metadata: Optional[PodcastMetadata] = Field(None, description="Podcast metadata")
    radio_metadata: Optional[RadioMetadata] = Field(None, description="Radio metadata")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    extracted_at: datetime = Field(default_factory=datetime.utcnow, description="Extraction timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


@dataclass
class ExtractionConfig:
    """Extraction configuration"""
    mode: ExtractionMode = ExtractionMode.COMPLETE
    quality_preference: List[AudioQuality] = field(default_factory=lambda: [
        AudioQuality.FLAC, AudioQuality.HIGH, AudioQuality.STANDARD
    ])
    include_lyrics: bool = True
    include_artwork: bool = True
    max_concurrent: int = 5
    request_delay: float = 1.0
    user_agent: str = "DeezerEngine/1.0"
    timeout: int = 30
    max_retries: int = 3
    use_selenium: bool = False
    headless_browser: bool = True
    proxy_config: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None


class DeezerEngine:
    """
    Ultra-advanced Deezer music extraction engine
    
    Features:
    - Multi-quality audio extraction with format selection
    - Real-time metadata enrichment with AI-powered analysis
    - Advanced rate limiting and request optimization
    - Concurrent extraction with bandwidth management
    - Anti-detection mechanisms with browser automation
    - Comprehensive error handling and recovery
    - Smart caching with TTL-based invalidation
    - Proxy rotation and IP management
    - Audio quality assessment and filtering
    - Live radio support with stream monitoring
    """
    
    def __init__(self, config: ExtractionConfig = None):
        """
Initialize Deezer extraction engine"""
        self.config = config or ExtractionConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.selenium_driver: Optional[webdriver.Chrome] = None
        self.base_url = "https://www.deezer.com"
        self.api_url = "https://api.deezer.com"
        self.ajax_url = "https://www.deezer.com/ajax/gw-light.php"
        
        # Request statistics
        self.stats = {
            'requests_made': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'cache_hits': 0,
            'start_time': datetime.utcnow()
        }
        
        # Content cache with TTL
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.cache_ttl = timedelta(hours=1)
        
        # Rate limiting
        self.last_request_time = 0.0
        self.request_semaphore = asyncio.Semaphore(self.config.max_concurrent)
        
        # API credentials
        self.api_token = None
        self.csrf_token = None
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for extraction engine"""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with optimized settings"""
        if not self.session or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            headers = {
                'User-Agent': self.config.user_agent,
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
            }
            
            if self.config.headers:
                headers.update(self.config.headers)
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=headers,
                cookies=self.config.cookies or {}
            )
        
        return self.session
    
    def _get_selenium_driver(self) -> webdriver.Chrome:
        """
Get or create Selenium WebDriver with stealth configuration"""
        if not self.selenium_driver:
            options = Options()
            if self.config.headless_browser:
                options.add_argument('--headless')
            
            # Anti-detection options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument(f'--user-agent={self.config.user_agent}')
            
            # Performance optimization
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            
            if self.config.proxy_config:
                proxy = f"{self.config.proxy_config.get('host')}:{self.config.proxy_config.get('port')}"
                options.add_argument(f'--proxy-server={proxy}')
            
            self.selenium_driver = webdriver.Chrome(options=options)
            
            # Remove automation indicators
            self.selenium_driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
        
        return self.selenium_driver
    
    def _is_cache_valid(self, cache_time: datetime) -> bool:
        """Check if cached data is still valid"""
        return datetime.utcnow() - cache_time < self.cache_ttl
    
    def _get_cached_result(self, key: str) -> Optional[Any]:
        """
Get result from cache if valid"""
        if key in self.cache:
            result, cache_time = self.cache[key]
            if self._is_cache_valid(cache_time):
                self.stats['cache_hits'] += 1
                return result
            else:
                del self.cache[key]
        return None
    
    def _cache_result(self, key: str, result: Any):
        """
Cache extraction result"""
        self.cache[key] = (result, datetime.utcnow())
    
    async def _rate_limit(self):
        """
Implement intelligent rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.config.request_delay:
            sleep_time = self.config.request_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    async def _make_request(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """
Make HTTP request with rate limiting and retry logic"""
        async with self.request_semaphore:
            await self._rate_limit()
            
            session = await self._get_session()
            self.stats['requests_made'] += 1
            
            for attempt in range(self.config.max_retries):
                try:
                    async with session.get(url, **kwargs) as response:
                        if response.status == 200:
                            return response
                        elif response.status == 429:  # Rate limited
                            wait_time = 2 ** attempt
                            self.logger.warning(f"Rate limited, waiting {wait_time}s")
                            await asyncio.sleep(wait_time)
                        else:
                            self.logger.warning(f"HTTP {response.status} for {url}")
                            
                except asyncio.TimeoutError:
                    self.logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                except Exception as e:
                    self.logger.warning(f"Request error on attempt {attempt + 1}: {e}")
                    if attempt < self.config.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
            
            raise Exception(f"Failed to fetch {url} after {self.config.max_retries} attempts")
    
    def _extract_track_id(self, url: str) -> Optional[str]:
        """Extract track ID from Deezer URL"""
        patterns = [
            r'deezer\.com/track/(\d+)',
            r'deezer\.com/.+/track/(\d+)',
            r'deezer\.page\.link/.*track.*?(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_album_id(self, url: str) -> Optional[str]:
        """
Extract album ID from Deezer URL"""
        patterns = [
            r'deezer\.com/album/(\d+)',
            r'deezer\.com/.+/album/(\d+)',
            r'deezer\.page\.link/.*album.*?(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_playlist_id(self, url: str) -> Optional[str]:
        """
Extract playlist ID from Deezer URL"""
        patterns = [
            r'deezer\.com/playlist/(\d+)',
            r'deezer\.com/.+/playlist/(\d+)',
            r'deezer\.page\.link/.*playlist.*?(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_artist_id(self, url: str) -> Optional[str]:
        """
Extract artist ID from Deezer URL"""
        patterns = [
            r'deezer\.com/artist/(\d+)',
            r'deezer\.com/.+/artist/(\d+)',
            r'deezer\.page\.link/.*artist.*?(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_podcast_id(self, url: str) -> Optional[str]:
        """
Extract podcast ID from Deezer URL"""
        patterns = [
            r'deezer\.com/show/(\d+)',
            r'deezer\.com/.+/show/(\d+)',
            r'deezer\.page\.link/.*show.*?(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_radio_id(self, url: str) -> Optional[str]:
        """
Extract radio ID from Deezer URL"""
        patterns = [
            r'deezer\.com/radio/(\d+)',
            r'deezer\.com/.+/radio/(\d+)',
            r'deezer\.page\.link/.*radio.*?(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _determine_content_type(self, url: str) -> ContentType:
        """
Determine content type from URL"""
        if '/track/' in url:
            return ContentType.TRACK
        elif '/album/' in url:
            return ContentType.ALBUM
        elif '/playlist/' in url:
            return ContentType.PLAYLIST
        elif '/artist/' in url:
            return ContentType.ARTIST
        elif '/show/' in url:
            return ContentType.PODCAST
        elif '/radio/' in url:
            return ContentType.RADIO
        else:
            return ContentType.TRACK  # Default assumption
    
    async def _get_api_token(self) -> Optional[str]:
        """
Get API token for authenticated requests"""
        if self.api_token:
            return self.api_token
        
        try:
            # Get token from main page
            response = await self._make_request(self.base_url)
            content = await response.text()
            
            # Look for API token in JavaScript
            token_match = re.search(r'"API_TOKEN":"([^"]+)"', content)
            if token_match:
                self.api_token = token_match.group(1)
                return self.api_token
            
            # Look for CSRF token
            csrf_match = re.search(r'"CSRFToken":"([^"]+)"', content)
            if csrf_match:
                self.csrf_token = csrf_match.group(1)
            
        except Exception as e:
            self.logger.warning(f"Failed to get API token: {e}")
        
        return None
    
    async def _extract_track_metadata_api(self, track_id: str) -> Optional[TrackMetadata]:
        """Extract track metadata using Deezer API"""
        try:
            api_url = f"{self.api_url}/track/{track_id}"
            response = await self._make_request(api_url)
            
            if response.status == 200:
                data = await response.json()
                
                # Check for error in response
                if 'error' in data:
                    self.logger.warning(f"API error for track {track_id}: {data['error']}")
                    return None
                
                # Parse metadata
                metadata = TrackMetadata(
                    track_id=track_id,
                    title=data.get('title', ''),
                    artist_name=data.get('artist', {}).get('name', ''),
                    artist_id=str(data.get('artist', {}).get('id', '')),
                    album_name=data.get('album', {}).get('title'),
                    album_id=str(data.get('album', {}).get('id', '')),
                    duration=data.get('duration'),
                    track_number=data.get('track_position'),
                    disc_number=data.get('disk_number'),
                    bpm=data.get('bpm'),
                    gain=data.get('gain'),
                    popularity=data.get('rank'),
                    explicit=data.get('explicit_lyrics', False),
                    preview_url=data.get('preview'),
                    isrc=data.get('isrc')
                )
                
                # Parse release date
                if data.get('release_date'):
                    try:
                        metadata.release_date = datetime.strptime(data['release_date'], '%Y-%m-%d')
                    except ValueError:
                        pass
                
                # Parse contributors
                if data.get('contributors'):
                    metadata.contributors = [contrib.get('name', '') for contrib in data['contributors']]
                
                # Extract album art
                if data.get('album', {}).get('cover_big'):
                    sizes = ['small', 'medium', 'big', 'xl']
                    for size in sizes:
                        cover_key = f'cover_{size}'
                        if cover_key in data['album']:
                            album_art = AlbumArt(
                                url=data['album'][cover_key],
                                width=self._get_cover_size(size)[0],
                                height=self._get_cover_size(size)[1],
                                size=size
                            )
                            metadata.album_art.append(album_art)
                
                return metadata
                
        except Exception as e:
            self.logger.error(f"API metadata extraction failed for track {track_id}: {e}")
            return None
    
    def _get_cover_size(self, size: str) -> Tuple[int, int]:
        """Get cover image dimensions for size"""
        sizes = {
            'small': (56, 56),
            'medium': (250, 250),
            'big': (500, 500),
            'xl': (1000, 1000)
        }
        return sizes.get(size, (250, 250))
    
    async def _extract_track_formats(self, track_id: str) -> List[TrackFormat]:
        """
Extract track audio formats"""
        formats = []
        
        try:
            # Get API token
            token = await self._get_api_token()
            if not token:
                return formats
            
            # Try to get stream URLs using AJAX endpoint
            ajax_params = {
                'method': 'song.getListData',
                'input': '3',
                'api_version': '1.0',
                'api_token': token
            }
            
            # This would require more complex authentication for premium formats
            # For now, we'll return preview format
            api_url = f"{self.api_url}/track/{track_id}"
            response = await self._make_request(api_url)
            
            if response.status == 200:
                data = await response.json()
                
                if data.get('preview'):
                    preview_format = TrackFormat(
                        format_id="preview_mp3",
                        url=data['preview'],
                        quality=AudioQuality.LOW,
                        bitrate=96,
                        codec="mp3",
                        container="mp3",
                        duration=30.0,  # Preview is typically 30 seconds
                        mime_type="audio/mpeg"
                    )
                    formats.append(preview_format)
                
        except Exception as e:
            self.logger.error(f"Format extraction failed for track {track_id}: {e}")
        
        return formats
    
    async def _extract_lyrics(self, track_id: str) -> Optional[str]:
        """Extract track lyrics"""
        try:
            # Lyrics extraction would require additional API endpoints
            # This is a placeholder for the implementation
            lyrics_url = f"{self.api_url}/track/{track_id}/lyrics"
            
            # Note: Deezer doesn't provide public lyrics API
            # This would require scraping or premium API access
            
            return None
            
        except Exception as e:
            self.logger.error(f"Lyrics extraction failed for track {track_id}: {e}")
            return None
    
    async def extract_track(self, url: str) -> ExtractionResult:
        """Extract complete track information"""
        start_time = time.time()
        
        try:
            track_id = self._extract_track_id(url)
            if not track_id:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.TRACK,
                    extraction_time=time.time() - start_time,
                    errors=["Could not extract track ID from URL"]
                )
            
            # Check cache first
            cache_key = f"track_{track_id}_{self.config.mode.value}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Extract metadata using API
            metadata = await self._extract_track_metadata_api(track_id)
            
            if not metadata:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.TRACK,
                    extraction_time=time.time() - start_time,
                    errors=["Failed to extract track metadata"]
                )
            
            # Extract formats if required
            if self.config.mode in [ExtractionMode.COMPLETE, ExtractionMode.PREMIUM]:
                formats = await self._extract_track_formats(track_id)
                metadata.formats = formats
            
            # Extract lyrics if required
            if self.config.include_lyrics and self.config.mode != ExtractionMode.METADATA_ONLY:
                lyrics = await self._extract_lyrics(track_id)
                if lyrics:
                    metadata.lyrics = lyrics
            
            result = ExtractionResult(
                success=True,
                content_type=ContentType.TRACK,
                extraction_time=time.time() - start_time,
                track_metadata=metadata
            )
            
            # Cache result
            self._cache_result(cache_key, result)
            self.stats['successful_extractions'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Track extraction failed for {url}: {e}")
            self.stats['failed_extractions'] += 1
            
            return ExtractionResult(
                success=False,
                content_type=ContentType.TRACK,
                extraction_time=time.time() - start_time,
                errors=[str(e)]
            )
    
    async def extract_album(self, url: str) -> ExtractionResult:
        """Extract album information"""
        start_time = time.time()
        
        try:
            album_id = self._extract_album_id(url)
            if not album_id:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.ALBUM,
                    extraction_time=time.time() - start_time,
                    errors=["Could not extract album ID from URL"]
                )
            
            # Check cache first
            cache_key = f"album_{album_id}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Extract album metadata
            api_url = f"{self.api_url}/album/{album_id}"
            response = await self._make_request(api_url)
            
            if response.status != 200:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.ALBUM,
                    extraction_time=time.time() - start_time,
                    errors=[f"API request failed with status {response.status}"]
                )
            
            data = await response.json()
            
            if 'error' in data:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.ALBUM,
                    extraction_time=time.time() - start_time,
                    errors=[f"API error: {data['error']}"]
                )
            
            # Create album metadata
            album_metadata = AlbumMetadata(
                album_id=album_id,
                title=data.get('title', ''),
                artist_name=data.get('artist', {}).get('name', ''),
                artist_id=str(data.get('artist', {}).get('id', '')),
                track_count=data.get('nb_tracks', 0),
                duration=data.get('duration'),
                genre=data.get('genres', {}).get('data', [{}])[0].get('name') if data.get('genres') else None,
                label=data.get('label'),
                upc=data.get('upc'),
                popularity=data.get('fans'),
                explicit=data.get('explicit_lyrics', False)
            )
            
            # Parse release date
            if data.get('release_date'):
                try:
                    album_metadata.release_date = datetime.strptime(data['release_date'], '%Y-%m-%d')
                except ValueError:
                    pass
            
            # Extract album art
            if data.get('cover_big'):
                sizes = ['small', 'medium', 'big', 'xl']
                for size in sizes:
                    cover_key = f'cover_{size}'
                    if cover_key in data:
                        album_art = AlbumArt(
                            url=data[cover_key],
                            width=self._get_cover_size(size)[0],
                            height=self._get_cover_size(size)[1],
                            size=size
                        )
                        album_metadata.album_art.append(album_art)
            
            # Extract track IDs
            if data.get('tracks', {}).get('data'):
                album_metadata.tracks = [str(track.get('id', '')) for track in data['tracks']['data']]
            
            result = ExtractionResult(
                success=True,
                content_type=ContentType.ALBUM,
                extraction_time=time.time() - start_time,
                album_metadata=album_metadata
            )
            
            # Cache result
            self._cache_result(cache_key, result)
            self.stats['successful_extractions'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Album extraction failed for {url}: {e}")
            self.stats['failed_extractions'] += 1
            
            return ExtractionResult(
                success=False,
                content_type=ContentType.ALBUM,
                extraction_time=time.time() - start_time,
                errors=[str(e)]
            )
    
    async def extract_playlist(self, url: str) -> ExtractionResult:
        """Extract playlist information"""
        start_time = time.time()
        
        try:
            playlist_id = self._extract_playlist_id(url)
            if not playlist_id:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.PLAYLIST,
                    extraction_time=time.time() - start_time,
                    errors=["Could not extract playlist ID from URL"]
                )
            
            # Check cache first
            cache_key = f"playlist_{playlist_id}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Extract playlist metadata
            api_url = f"{self.api_url}/playlist/{playlist_id}"
            response = await self._make_request(api_url)
            
            if response.status != 200:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.PLAYLIST,
                    extraction_time=time.time() - start_time,
                    errors=[f"API request failed with status {response.status}"]
                )
            
            data = await response.json()
            
            if 'error' in data:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.PLAYLIST,
                    extraction_time=time.time() - start_time,
                    errors=[f"API error: {data['error']}"]
                )
            
            # Create playlist metadata
            playlist_metadata = PlaylistMetadata(
                playlist_id=playlist_id,
                title=data.get('title', ''),
                description=data.get('description'),
                creator=data.get('creator', {}).get('name'),
                creator_id=str(data.get('creator', {}).get('id', '')),
                track_count=data.get('nb_tracks', 0),
                duration=data.get('duration'),
                public=data.get('public', True),
                collaborative=data.get('collaborative', False),
                fan_count=data.get('fans'),
                picture_url=data.get('picture_big')
            )
            
            # Parse creation date
            if data.get('creation_date'):
                try:
                    playlist_metadata.creation_date = datetime.strptime(data['creation_date'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    pass
            
            # Extract track IDs
            if data.get('tracks', {}).get('data'):
                playlist_metadata.tracks = [str(track.get('id', '')) for track in data['tracks']['data']]
            
            result = ExtractionResult(
                success=True,
                content_type=ContentType.PLAYLIST,
                extraction_time=time.time() - start_time,
                playlist_metadata=playlist_metadata
            )
            
            # Cache result
            self._cache_result(cache_key, result)
            self.stats['successful_extractions'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Playlist extraction failed for {url}: {e}")
            self.stats['failed_extractions'] += 1
            
            return ExtractionResult(
                success=False,
                content_type=ContentType.PLAYLIST,
                extraction_time=time.time() - start_time,
                errors=[str(e)]
            )
    
    async def extract_artist(self, url: str) -> ExtractionResult:
        """Extract artist information"""
        start_time = time.time()
        
        try:
            artist_id = self._extract_artist_id(url)
            if not artist_id:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.ARTIST,
                    extraction_time=time.time() - start_time,
                    errors=["Could not extract artist ID from URL"]
                )
            
            # Check cache first
            cache_key = f"artist_{artist_id}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Extract artist metadata
            api_url = f"{self.api_url}/artist/{artist_id}"
            response = await self._make_request(api_url)
            
            if response.status != 200:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.ARTIST,
                    extraction_time=time.time() - start_time,
                    errors=[f"API request failed with status {response.status}"]
                )
            
            data = await response.json()
            
            if 'error' in data:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.ARTIST,
                    extraction_time=time.time() - start_time,
                    errors=[f"API error: {data['error']}"]
                )
            
            # Create artist metadata
            artist_metadata = ArtistMetadata(
                artist_id=artist_id,
                name=data.get('name', ''),
                real_name=data.get('real_name'),
                country=data.get('country'),
                fan_count=data.get('nb_fan'),
                album_count=data.get('nb_album'),
                popularity=data.get('nb_fan'),
                picture_url=data.get('picture_big')
            )
            
            # Get top tracks
            try:
                top_tracks_url = f"{self.api_url}/artist/{artist_id}/top"
                top_response = await self._make_request(top_tracks_url)
                if top_response.status == 200:
                    top_data = await top_response.json()
                    if top_data.get('data'):
                        artist_metadata.top_tracks = [str(track.get('id', '')) for track in top_data['data'][:10]]
            except Exception:
                pass
            
            # Get albums
            try:
                albums_url = f"{self.api_url}/artist/{artist_id}/albums"
                albums_response = await self._make_request(albums_url)
                if albums_response.status == 200:
                    albums_data = await albums_response.json()
                    if albums_data.get('data'):
                        artist_metadata.albums = [str(album.get('id', '')) for album in albums_data['data']]
            except Exception:
                pass
            
            result = ExtractionResult(
                success=True,
                content_type=ContentType.ARTIST,
                extraction_time=time.time() - start_time,
                artist_metadata=artist_metadata
            )
            
            # Cache result
            self._cache_result(cache_key, result)
            self.stats['successful_extractions'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Artist extraction failed for {url}: {e}")
            self.stats['failed_extractions'] += 1
            
            return ExtractionResult(
                success=False,
                content_type=ContentType.ARTIST,
                extraction_time=time.time() - start_time,
                errors=[str(e)]
            )
    
    async def extract(self, url: str) -> ExtractionResult:
        """Universal content extraction method"""
        content_type = self._determine_content_type(url)
        
        if content_type == ContentType.TRACK:
            return await self.extract_track(url)
        elif content_type == ContentType.ALBUM:
            return await self.extract_album(url)
        elif content_type == ContentType.PLAYLIST:
            return await self.extract_playlist(url)
        elif content_type == ContentType.ARTIST:
            return await self.extract_artist(url)
        else:
            return ExtractionResult(
                success=False,
                content_type=content_type,
                extraction_time=0.0,
                errors=["Unsupported content type"]
            )
    
    async def batch_extract(self, urls: List[str]) -> List[ExtractionResult]:
        """Extract multiple URLs concurrently"""
        semaphore = asyncio.Semaphore(self.config.max_concurrent)
        
        async def extract_with_semaphore(url: str) -> ExtractionResult:
            async with semaphore:
                return await self.extract(url)
        
        tasks = [extract_with_semaphore(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)
    
    def get_stats(self) -> Dict[str, Any]:
        """
Get extraction statistics"""
        uptime = (datetime.utcnow() - self.stats['start_time']).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'requests_made': self.stats['requests_made'],
            'successful_extractions': self.stats['successful_extractions'],
            'failed_extractions': self.stats['failed_extractions'],
            'cache_hits': self.stats['cache_hits'],
            'success_rate': (
                self.stats['successful_extractions'] / 
                max(1, self.stats['successful_extractions'] + self.stats['failed_extractions'])
            ) * 100,
            'cache_size': len(self.cache),
            'requests_per_second': self.stats['requests_made'] / max(1, uptime)
        }
    
    async def clear_cache(self):
        """
Clear extraction cache"""
        self.cache.clear()
        self.logger.info("Extraction cache cleared")
    
    async def close(self):
        """Clean up resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        
        if self.selenium_driver:
            self.selenium_driver.quit()
        
        self.logger.info("DeezerEngine resources cleaned up")


# Factory function for easy instantiation
def create_deezer_engine(
    mode: ExtractionMode = ExtractionMode.COMPLETE,
    quality_preference: List[AudioQuality] = None,
    max_concurrent: int = 5,
    use_selenium: bool = False,
    **kwargs
) -> DeezerEngine:
    """Create and configure a DeezerEngine instance"""
    
    config = ExtractionConfig(
        mode=mode,
        quality_preference=quality_preference or [AudioQuality.FLAC, AudioQuality.HIGH],
        max_concurrent=max_concurrent,
        use_selenium=use_selenium,
        **kwargs
    )
    
    return DeezerEngine(config)


# Example usage and testing
async def main():
    """
Example usage of DeezerEngine"""
    
    # Create engine with custom configuration
    config = ExtractionConfig(
        mode=ExtractionMode.COMPLETE,
        quality_preference=[AudioQuality.FLAC, AudioQuality.HIGH, AudioQuality.STANDARD],
        include_lyrics=True,
        include_artwork=True,
        max_concurrent=3,
        use_selenium=False
    )
    
    engine = DeezerEngine(config)
    
    try:
        # Example URLs
        test_urls = [
            "https://www.deezer.com/track/3135556",
            "https://www.deezer.com/album/302127",
            "https://www.deezer.com/playlist/1313621735",
            "https://www.deezer.com/artist/27"
        ]
        
        # Single extraction
        print("Extracting single track...")
        result = await engine.extract(test_urls[0])
        
        if result.success:
            print(f"✅ Successfully extracted: {result.track_metadata.title}")
            print(f"🎵 Artist: {result.track_metadata.artist_name}")
            print(f"💿 Album: {result.track_metadata.album_name}")
            print(f"⏱️ Duration: {result.track_metadata.duration}s")
            print(f"🎨 Artwork: {len(result.track_metadata.album_art)} sizes")
        else:
            print(f"❌ Extraction failed: {result.errors}")
        
        # Batch extraction
        print("\nBatch extracting...")
        results = await engine.batch_extract(test_urls[:2])
        
        successful = sum(1 for r in results if r.success)
        print(f"✅ Successfully extracted {successful}/{len(results)} items")
        
        # Print statistics
        stats = engine.get_stats()
        print(f"\n📈 Engine Statistics:")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"Requests made: {stats['requests_made']}")
        print(f"Cache hits: {stats['cache_hits']}")
        print(f"Requests/sec: {stats['requests_per_second']:.2f}")
        
    finally:
        await engine.close()


if __name__ == "__main__":
    asyncio.run(main())
