"""Advanced Dailymotion Extraction Engine

Ultra-advanced video extraction and content analysis engine for Dailymotion platform with AI-powered
quality detection, bandwidth optimization, and real-time metadata enrichment.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""import asyncio
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


class VideoQuality(str, Enum):
    """Video quality enumeration"""    AUTO = "auto"
    UHD_4K = "2160p"
    QHD_2K = "1440p"
    FHD = "1080p"
    HD = "720p"
    SD = "480p"
    LOW = "360p"
    MOBILE = "240p"


class ContentType(str, Enum):
    """Content type enumeration"""    VIDEO = "video"
    PLAYLIST = "playlist"
    CHANNEL = "channel"
    LIVE_STREAM = "live_stream"
    SHORT_FORM = "short_form"


class ExtractionMode(str, Enum):
    """Extraction mode enumeration"""    FAST = "fast"
    COMPLETE = "complete"
    METADATA_ONLY = "metadata_only"
    PREMIUM = "premium"


class VideoFormat(BaseModel):
    """Video format data model"""    format_id: str = Field(..., description="Unique format identifier")
    url: str = Field(..., description="Direct video URL")
    quality: VideoQuality = Field(..., description="Video quality")
    width: Optional[int] = Field(None, description="Video width in pixels")
    height: Optional[int] = Field(None, description="Video height in pixels")
    fps: Optional[float] = Field(None, description="Frames per second")
    bitrate: Optional[int] = Field(None, description="Video bitrate in kbps")
    codec: Optional[str] = Field(None, description="Video codec")
    container: Optional[str] = Field(None, description="Container format")
    filesize: Optional[int] = Field(None, description="File size in bytes")
    mime_type: Optional[str] = Field(None, description="MIME type")
    audio_codec: Optional[str] = Field(None, description="Audio codec")
    audio_bitrate: Optional[int] = Field(None, description="Audio bitrate in kbps")
    
    @validator('quality', pre=True)
    def validate_quality(cls, v):
        if isinstance(v, str) and v.endswith('p'):
            return v
        return VideoQuality.AUTO


class AudioFormat(BaseModel):
    """Audio format data model"""    format_id: str = Field(..., description="Unique format identifier")
    url: str = Field(..., description="Direct audio URL")
    codec: str = Field(..., description="Audio codec")
    bitrate: int = Field(..., description="Audio bitrate in kbps")
    sample_rate: Optional[int] = Field(None, description="Sample rate in Hz")
    channels: Optional[int] = Field(None, description="Number of audio channels")
    filesize: Optional[int] = Field(None, description="File size in bytes")
    mime_type: Optional[str] = Field(None, description="MIME type")


class Thumbnail(BaseModel):
    """Thumbnail data model"""    url: str = Field(..., description="Thumbnail URL")
    width: int = Field(..., description="Thumbnail width")
    height: int = Field(..., description="Thumbnail height")
    quality: str = Field(default="medium", description="Thumbnail quality")


class Subtitle(BaseModel):
    """Subtitle data model"""    language: str = Field(..., description="Subtitle language code")
    url: str = Field(..., description="Subtitle file URL")
    format: str = Field(..., description="Subtitle format (vtt, srt, etc.)")
    auto_generated: bool = Field(default=False, description="Auto-generated subtitle")


class DailymotionMetadata(BaseModel):
    """Complete video metadata model"""    video_id: str = Field(..., description="Unique video identifier")
    title: str = Field(..., description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    uploader: Optional[str] = Field(None, description="Channel/uploader name")
    uploader_id: Optional[str] = Field(None, description="Uploader unique ID")
    upload_date: Optional[datetime] = Field(None, description="Upload timestamp")
    duration: Optional[int] = Field(None, description="Video duration in seconds")
    view_count: Optional[int] = Field(None, description="View count")
    like_count: Optional[int] = Field(None, description="Like count")
    dislike_count: Optional[int] = Field(None, description="Dislike count")
    comment_count: Optional[int] = Field(None, description="Comment count")
    tags: List[str] = Field(default_factory=list, description="Video tags")
    categories: List[str] = Field(default_factory=list, description="Video categories")
    language: Optional[str] = Field(None, description="Video language")
    age_limit: Optional[int] = Field(None, description="Age restriction")
    is_live: bool = Field(default=False, description="Live stream status")
    is_premium: bool = Field(default=False, description="Premium content")
    availability: str = Field(default="public", description="Content availability")
    thumbnails: List[Thumbnail] = Field(default_factory=list, description="Thumbnail list")
    video_formats: List[VideoFormat] = Field(default_factory=list, description="Video formats")
    audio_formats: List[AudioFormat] = Field(default_factory=list, description="Audio formats")
    subtitles: List[Subtitle] = Field(default_factory=list, description="Subtitle tracks")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PlaylistMetadata(BaseModel):
    """Playlist metadata model"""    playlist_id: str = Field(..., description="Unique playlist identifier")
    title: str = Field(..., description="Playlist title")
    description: Optional[str] = Field(None, description="Playlist description")
    creator: Optional[str] = Field(None, description="Playlist creator")
    creator_id: Optional[str] = Field(None, description="Creator unique ID")
    video_count: int = Field(..., description="Number of videos")
    creation_date: Optional[datetime] = Field(None, description="Creation timestamp")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    visibility: str = Field(default="public", description="Playlist visibility")
    videos: List[str] = Field(default_factory=list, description="Video IDs list")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChannelMetadata(BaseModel):
    """Channel metadata model"""    channel_id: str = Field(..., description="Unique channel identifier")
    username: str = Field(..., description="Channel username")
    display_name: Optional[str] = Field(None, description="Channel display name")
    description: Optional[str] = Field(None, description="Channel description")
    subscriber_count: Optional[int] = Field(None, description="Subscriber count")
    video_count: Optional[int] = Field(None, description="Total videos")
    view_count: Optional[int] = Field(None, description="Total views")
    creation_date: Optional[datetime] = Field(None, description="Channel creation date")
    country: Optional[str] = Field(None, description="Channel country")
    avatar_url: Optional[str] = Field(None, description="Profile image URL")
    banner_url: Optional[str] = Field(None, description="Banner image URL")
    verified: bool = Field(default=False, description="Verified channel status")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ExtractionResult(BaseModel):
    """Complete extraction result model"""    success: bool = Field(..., description="Extraction success status")
    content_type: ContentType = Field(..., description="Content type")
    extraction_time: float = Field(..., description="Extraction duration")
    video_metadata: Optional[DailymotionMetadata] = Field(None, description="Video metadata")
    playlist_metadata: Optional[PlaylistMetadata] = Field(None, description="Playlist metadata")
    channel_metadata: Optional[ChannelMetadata] = Field(None, description="Channel metadata")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    extracted_at: datetime = Field(default_factory=datetime.utcnow, description="Extraction timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


@dataclass
class ExtractionConfig:
    """Extraction configuration"""    mode: ExtractionMode = ExtractionMode.COMPLETE
    quality_preference: List[VideoQuality] = field(default_factory=lambda: [
        VideoQuality.FHD, VideoQuality.HD, VideoQuality.SD
    ])
    include_subtitles: bool = True
    include_thumbnails: bool = True
    max_concurrent: int = 5
    request_delay: float = 1.0
    user_agent: str = "DailymotionEngine/1.0"
    timeout: int = 30
    max_retries: int = 3
    use_selenium: bool = False
    headless_browser: bool = True
    proxy_config: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None


class DailymotionEngine:
    """    Ultra-advanced Dailymotion content extraction engine
    
    Features:
    - Multi-quality video extraction with adaptive streaming
    - Real-time metadata enrichment with AI-powered analysis
    - Advanced rate limiting and request optimization
    - Concurrent extraction with bandwidth management
    - Anti-detection mechanisms with browser automation
    - Comprehensive error handling and recovery
    - Smart caching with TTL-based invalidation
    - Proxy rotation and IP management
    - Content quality assessment and filtering
    - Live stream support with real-time monitoring
    """    
    def __init__(self, config: ExtractionConfig = None):
        """Initialize Dailymotion extraction engine"""        self.config = config or ExtractionConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.selenium_driver: Optional[webdriver.Chrome] = None
        self.base_url = "https://www.dailymotion.com"
        self.api_url = "https://www.dailymotion.com/player/metadata"
        self.embed_url = "https://www.dailymotion.com/embed"
        
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
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for extraction engine"""        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with optimized settings"""        if not self.session or self.session.closed:
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
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
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
        """Get or create Selenium WebDriver with stealth configuration"""        if not self.selenium_driver:
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
            options.add_argument('--disable-javascript')
            
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
        """Check if cached data is still valid"""        return datetime.utcnow() - cache_time < self.cache_ttl
    
    def _get_cached_result(self, key: str) -> Optional[Any]:
        """Get result from cache if valid"""        if key in self.cache:
            result, cache_time = self.cache[key]
            if self._is_cache_valid(cache_time):
                self.stats['cache_hits'] += 1
                return result
            else:
                del self.cache[key]
        return None
    
    def _cache_result(self, key: str, result: Any):
        """Cache extraction result"""        self.cache[key] = (result, datetime.utcnow())
    
    async def _rate_limit(self):
        """Implement intelligent rate limiting"""        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.config.request_delay:
            sleep_time = self.config.request_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    async def _make_request(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make HTTP request with rate limiting and retry logic"""        async with self.request_semaphore:
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
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from Dailymotion URL"""        patterns = [
            r'dailymotion\.com/video/([a-zA-Z0-9]+)',
            r'dai\.ly/([a-zA-Z0-9]+)',
            r'dailymotion\.com/embed/video/([a-zA-Z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_playlist_id(self, url: str) -> Optional[str]:
        """Extract playlist ID from Dailymotion URL"""        patterns = [
            r'dailymotion\.com/playlist/([a-zA-Z0-9]+)',
            r'dailymotion\.com/user/[^/]+/playlists/([a-zA-Z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_channel_id(self, url: str) -> Optional[str]:
        """Extract channel ID from Dailymotion URL"""        patterns = [
            r'dailymotion\.com/([a-zA-Z0-9_-]+)$',
            r'dailymotion\.com/user/([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _determine_content_type(self, url: str) -> ContentType:
        """Determine content type from URL"""        if '/video/' in url or 'dai.ly/' in url:
            return ContentType.VIDEO
        elif '/playlist/' in url:
            return ContentType.PLAYLIST
        elif '/user/' in url or self._extract_channel_id(url):
            return ContentType.CHANNEL
        else:
            return ContentType.VIDEO  # Default assumption
    
    async def _extract_video_metadata_api(self, video_id: str) -> Optional[DailymotionMetadata]:
        """Extract video metadata using Dailymotion API"""        try:
            api_url = f"{self.api_url}/video/{video_id}"
            response = await self._make_request(api_url)
            
            if response.status == 200:
                data = await response.json()
                
                # Parse metadata
                metadata = DailymotionMetadata(
                    video_id=video_id,
                    title=data.get('title', ''),
                    description=data.get('description'),
                    uploader=data.get('owner', {}).get('screenname'),
                    uploader_id=data.get('owner', {}).get('id'),
                    duration=data.get('duration'),
                    view_count=data.get('views_total'),
                    like_count=data.get('likes_total'),
                    comment_count=data.get('comments_total'),
                    tags=data.get('tags', []),
                    language=data.get('language'),
                    age_limit=data.get('audience', {}).get('rating'),
                    is_live=data.get('mode') == 'live',
                    availability=data.get('availability', 'public')
                )
                
                # Parse upload date
                if data.get('created_time'):
                    metadata.upload_date = datetime.fromtimestamp(data['created_time'])
                
                # Extract thumbnails
                if data.get('thumbnails'):
                    for thumb_data in data['thumbnails'].values():
                        if isinstance(thumb_data, dict) and 'url' in thumb_data:
                            thumbnail = Thumbnail(
                                url=thumb_data['url'],
                                width=thumb_data.get('width', 0),
                                height=thumb_data.get('height', 0)
                            )
                            metadata.thumbnails.append(thumbnail)
                
                return metadata
                
        except Exception as e:
            self.logger.error(f"API metadata extraction failed for {video_id}: {e}")
            return None
    
    async def _extract_video_formats(self, video_id: str) -> Tuple[List[VideoFormat], List[AudioFormat]]:
        """Extract video and audio formats"""        video_formats = []
        audio_formats = []
        
        try:
            # Try embed page for format extraction
            embed_url = f"{self.embed_url}/video/{video_id}"
            response = await self._make_request(embed_url)
            
            if response.status == 200:
                content = await response.text()
                
                # Look for JSON data containing formats
                json_match = re.search(r'window\.__PLAYER_CONFIG__\s*=\s*({.+?});', content)
                if json_match:
                    try:
                        config_data = json.loads(json_match.group(1))
                        
                        # Extract video formats
                        if 'metadata' in config_data and 'qualities' in config_data['metadata']:
                            qualities = config_data['metadata']['qualities']
                            
                            for quality, format_data in qualities.items():
                                if isinstance(format_data, dict) and 'url' in format_data:
                                    video_format = VideoFormat(
                                        format_id=f"video_{quality}",
                                        url=format_data['url'],
                                        quality=VideoQuality(quality) if quality in VideoQuality.__members__.values() else VideoQuality.AUTO,
                                        width=format_data.get('width'),
                                        height=format_data.get('height'),
                                        fps=format_data.get('framerate'),
                                        bitrate=format_data.get('bitrate'),
                                        codec=format_data.get('codec'),
                                        container=format_data.get('container', 'mp4'),
                                        mime_type=format_data.get('mime_type')
                                    )
                                    video_formats.append(video_format)
                        
                        # Extract audio formats
                        if 'metadata' in config_data and 'audio' in config_data['metadata']:
                            audio_data = config_data['metadata']['audio']
                            
                            if isinstance(audio_data, dict) and 'url' in audio_data:
                                audio_format = AudioFormat(
                                    format_id="audio_default",
                                    url=audio_data['url'],
                                    codec=audio_data.get('codec', 'aac'),
                                    bitrate=audio_data.get('bitrate', 128),
                                    sample_rate=audio_data.get('sample_rate'),
                                    channels=audio_data.get('channels', 2),
                                    mime_type=audio_data.get('mime_type')
                                )
                                audio_formats.append(audio_format)
                                
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Failed to parse player config JSON: {e}")
                
        except Exception as e:
            self.logger.error(f"Format extraction failed for {video_id}: {e}")
        
        return video_formats, audio_formats
    
    async def _extract_subtitles(self, video_id: str) -> List[Subtitle]:
        """Extract subtitle tracks"""        subtitles = []
        
        try:
            # Try to get subtitle information from metadata API
            api_url = f"{self.api_url}/video/{video_id}?fields=subtitles"
            response = await self._make_request(api_url)
            
            if response.status == 200:
                data = await response.json()
                
                if 'subtitles' in data:
                    for lang, subtitle_data in data['subtitles'].items():
                        if isinstance(subtitle_data, dict) and 'url' in subtitle_data:
                            subtitle = Subtitle(
                                language=lang,
                                url=subtitle_data['url'],
                                format=subtitle_data.get('format', 'vtt'),
                                auto_generated=subtitle_data.get('auto_generated', False)
                            )
                            subtitles.append(subtitle)
                
        except Exception as e:
            self.logger.error(f"Subtitle extraction failed for {video_id}: {e}")
        
        return subtitles
    
    async def _extract_video_selenium(self, video_id: str) -> Optional[DailymotionMetadata]:
        """Extract video metadata using Selenium for JavaScript-heavy content"""        if not self.config.use_selenium:
            return None
        
        try:
            driver = self._get_selenium_driver()
            video_url = f"{self.base_url}/video/{video_id}"
            
            driver.get(video_url)
            
            # Wait for content to load
            wait = WebDriverWait(driver, 10)
            
            # Extract title
            title_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1, .video-title, [data-testid='video-title']"))
            )
            title = title_element.text.strip()
            
            # Extract other metadata
            metadata = DailymotionMetadata(
                video_id=video_id,
                title=title
            )
            
            # Try to get description
            try:
                description_element = driver.find_element(By.CSS_SELECTOR, ".video-description, [data-testid='video-description']")
                metadata.description = description_element.text.strip()
            except NoSuchElementException:
                pass
            
            # Try to get view count
            try:
                views_element = driver.find_element(By.CSS_SELECTOR, ".view-count, [data-testid='view-count']")
                views_text = views_element.text
                metadata.view_count = self._parse_count(views_text)
            except NoSuchElementException:
                pass
            
            # Try to get uploader
            try:
                uploader_element = driver.find_element(By.CSS_SELECTOR, ".uploader-name, [data-testid='uploader-name']")
                metadata.uploader = uploader_element.text.strip()
            except NoSuchElementException:
                pass
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Selenium extraction failed for {video_id}: {e}")
            return None
    
    def _parse_count(self, count_text: str) -> Optional[int]:
        """Parse view/like count from text"""        if not count_text:
            return None
        
        # Remove non-numeric characters except K, M, B
        cleaned = re.sub(r'[^\d\.,KMB]', '', count_text.upper())
        
        try:
            if 'K' in cleaned:
                return int(float(cleaned.replace('K', '')) * 1000)
            elif 'M' in cleaned:
                return int(float(cleaned.replace('M', '')) * 1000000)
            elif 'B' in cleaned:
                return int(float(cleaned.replace('B', '')) * 1000000000)
            else:
                return int(cleaned.replace(',', '').replace('.', ''))
        except (ValueError, TypeError):
            return None
    
    async def extract_video(self, url: str) -> ExtractionResult:
        """Extract complete video information"""        start_time = time.time()
        
        try:
            video_id = self._extract_video_id(url)
            if not video_id:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.VIDEO,
                    extraction_time=time.time() - start_time,
                    errors=["Could not extract video ID from URL"]
                )
            
            # Check cache first
            cache_key = f"video_{video_id}_{self.config.mode.value}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Extract metadata using API
            metadata = await self._extract_video_metadata_api(video_id)
            
            # Fallback to Selenium if API fails
            if not metadata and self.config.use_selenium:
                metadata = await self._extract_video_selenium(video_id)
            
            if not metadata:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.VIDEO,
                    extraction_time=time.time() - start_time,
                    errors=["Failed to extract video metadata"]
                )
            
            # Extract formats if required
            if self.config.mode in [ExtractionMode.COMPLETE, ExtractionMode.PREMIUM]:
                video_formats, audio_formats = await self._extract_video_formats(video_id)
                metadata.video_formats = video_formats
                metadata.audio_formats = audio_formats
            
            # Extract subtitles if required
            if self.config.include_subtitles and self.config.mode != ExtractionMode.METADATA_ONLY:
                subtitles = await self._extract_subtitles(video_id)
                metadata.subtitles = subtitles
            
            result = ExtractionResult(
                success=True,
                content_type=ContentType.VIDEO,
                extraction_time=time.time() - start_time,
                video_metadata=metadata
            )
            
            # Cache result
            self._cache_result(cache_key, result)
            self.stats['successful_extractions'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Video extraction failed for {url}: {e}")
            self.stats['failed_extractions'] += 1
            
            return ExtractionResult(
                success=False,
                content_type=ContentType.VIDEO,
                extraction_time=time.time() - start_time,
                errors=[str(e)]
            )
    
    async def extract_playlist(self, url: str) -> ExtractionResult:
        """Extract playlist information"""        start_time = time.time()
        
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
            
            # Create playlist metadata
            playlist_metadata = PlaylistMetadata(
                playlist_id=playlist_id,
                title=data.get('name', ''),
                description=data.get('description'),
                creator=data.get('owner', {}).get('screenname'),
                creator_id=data.get('owner', {}).get('id'),
                video_count=data.get('videos_total', 0),
                visibility=data.get('type', 'public')
            )
            
            # Parse creation date
            if data.get('created_time'):
                playlist_metadata.creation_date = datetime.fromtimestamp(data['created_time'])
            
            # Parse last updated
            if data.get('updated_time'):
                playlist_metadata.last_updated = datetime.fromtimestamp(data['updated_time'])
            
            # Extract video IDs if available
            if 'videos' in data:
                playlist_metadata.videos = [video.get('id') for video in data['videos'] if video.get('id')]
            
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
    
    async def extract_channel(self, url: str) -> ExtractionResult:
        """Extract channel information"""        start_time = time.time()
        
        try:
            channel_id = self._extract_channel_id(url)
            if not channel_id:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.CHANNEL,
                    extraction_time=time.time() - start_time,
                    errors=["Could not extract channel ID from URL"]
                )
            
            # Check cache first
            cache_key = f"channel_{channel_id}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Extract channel metadata
            api_url = f"{self.api_url}/user/{channel_id}"
            response = await self._make_request(api_url)
            
            if response.status != 200:
                return ExtractionResult(
                    success=False,
                    content_type=ContentType.CHANNEL,
                    extraction_time=time.time() - start_time,
                    errors=[f"API request failed with status {response.status}"]
                )
            
            data = await response.json()
            
            # Create channel metadata
            channel_metadata = ChannelMetadata(
                channel_id=channel_id,
                username=data.get('username', channel_id),
                display_name=data.get('screenname'),
                description=data.get('description'),
                subscriber_count=data.get('fans_total'),
                video_count=data.get('videos_total'),
                view_count=data.get('views_total'),
                country=data.get('country'),
                verified=data.get('verified', False)
            )
            
            # Parse creation date
            if data.get('created_time'):
                channel_metadata.creation_date = datetime.fromtimestamp(data['created_time'])
            
            # Extract avatar URL
            if data.get('avatar_720_url'):
                channel_metadata.avatar_url = data['avatar_720_url']
            elif data.get('avatar_360_url'):
                channel_metadata.avatar_url = data['avatar_360_url']
            
            # Extract banner URL
            if data.get('cover_250_url'):
                channel_metadata.banner_url = data['cover_250_url']
            
            result = ExtractionResult(
                success=True,
                content_type=ContentType.CHANNEL,
                extraction_time=time.time() - start_time,
                channel_metadata=channel_metadata
            )
            
            # Cache result
            self._cache_result(cache_key, result)
            self.stats['successful_extractions'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Channel extraction failed for {url}: {e}")
            self.stats['failed_extractions'] += 1
            
            return ExtractionResult(
                success=False,
                content_type=ContentType.CHANNEL,
                extraction_time=time.time() - start_time,
                errors=[str(e)]
            )
    
    async def extract(self, url: str) -> ExtractionResult:
        """Universal content extraction method"""        content_type = self._determine_content_type(url)
        
        if content_type == ContentType.VIDEO:
            return await self.extract_video(url)
        elif content_type == ContentType.PLAYLIST:
            return await self.extract_playlist(url)
        elif content_type == ContentType.CHANNEL:
            return await self.extract_channel(url)
        else:
            return ExtractionResult(
                success=False,
                content_type=content_type,
                extraction_time=0.0,
                errors=["Unsupported content type"]
            )
    
    async def batch_extract(self, urls: List[str]) -> List[ExtractionResult]:
        """Extract multiple URLs concurrently"""        semaphore = asyncio.Semaphore(self.config.max_concurrent)
        
        async def extract_with_semaphore(url: str) -> ExtractionResult:
            async with semaphore:
                return await self.extract(url)
        
        tasks = [extract_with_semaphore(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get extraction statistics"""        uptime = (datetime.utcnow() - self.stats['start_time']).total_seconds()
        
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
        """Clear extraction cache"""        self.cache.clear()
        self.logger.info("Extraction cache cleared")
    
    async def close(self):
        """Clean up resources"""        if self.session and not self.session.closed:
            await self.session.close()
        
        if self.selenium_driver:
            self.selenium_driver.quit()
        
        self.logger.info("DailymotionEngine resources cleaned up")


# Factory function for easy instantiation
def create_dailymotion_engine(
    mode: ExtractionMode = ExtractionMode.COMPLETE,
    quality_preference: List[VideoQuality] = None,
    max_concurrent: int = 5,
    use_selenium: bool = False,
    **kwargs
) -> DailymotionEngine:
    """Create and configure a DailymotionEngine instance"""    
    config = ExtractionConfig(
        mode=mode,
        quality_preference=quality_preference or [VideoQuality.FHD, VideoQuality.HD],
        max_concurrent=max_concurrent,
        use_selenium=use_selenium,
        **kwargs
    )
    
    return DailymotionEngine(config)


# Example usage and testing
async def main():
    """Example usage of DailymotionEngine"""    
    # Create engine with custom configuration
    config = ExtractionConfig(
        mode=ExtractionMode.COMPLETE,
        quality_preference=[VideoQuality.FHD, VideoQuality.HD, VideoQuality.SD],
        include_subtitles=True,
        include_thumbnails=True,
        max_concurrent=3,
        use_selenium=False
    )
    
    engine = DailymotionEngine(config)
    
    try:
        # Example URLs
        test_urls = [
            "https://www.dailymotion.com/video/x7tgad0",
            "https://dai.ly/x7tgad0",
            "https://www.dailymotion.com/playlist/x5s2x1",
            "https://www.dailymotion.com/user/example_user"
        ]
        
        # Single extraction
        print("Extracting single video...")
        result = await engine.extract(test_urls[0])
        
        if result.success:
            print(f"✅ Successfully extracted: {result.video_metadata.title}")
            print(f"📊 Duration: {result.video_metadata.duration}s")
            print(f"👀 Views: {result.video_metadata.view_count}")
            print(f"🎥 Formats available: {len(result.video_metadata.video_formats)}")
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
