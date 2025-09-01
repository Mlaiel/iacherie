"""SoundCloud Crawler
==================

Professional SoundCloud content crawler for audio content monitoring and discovery.
Implements SoundCloud API integration with advanced audio content analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Project Team Specialties:
- Lead Dev IA: Advanced AI integration and machine learning
- Backend Senior: Scalable architecture and microservices  
- ML Engineer: Content analysis and recommendation systems
- DBA: High-performance database optimization
- Security Expert: Enterprise-grade security and encryption
- Microservices Architect: Distributed systems design
- Audio Engineer: Advanced audio processing and analysis
- DevOps Engineer: CI/CD and infrastructure automation
- IA Prompt Engineer: Intelligent prompt optimization
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import re
import hashlib

import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from ..utils.rate_limiter import SoundCloudRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ..utils.content_analyzer import ContentAnalyzer
from ..utils.audio_analyzer import AudioAnalyzer
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError
from ...database.models import CrawlResult, ContentMatch
from ...security.encryption import FieldEncryption

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class SoundCloudTrack:
    """
SoundCloud track data structure."""
    track_id: str
    title: str
    description: str
    user_id: str
    username: str
    user_permalink: str
    permalink_url: str
    stream_url: str
    download_url: Optional[str]
    waveform_url: str
    artwork_url: str
    created_at: datetime
    duration: int  # in milliseconds
    playback_count: int
    download_count: int
    favoritings_count: int
    comment_count: int
    genre: str
    bpm: Optional[float]
    key_signature: Optional[str]
    isrc: Optional[str]
    license: str
    tag_list: List[str]
    downloadable: bool
    streamable: bool
    public: bool
    monetization_model: str

@dataclass
class SoundCloudPlaylist:
    """
SoundCloud playlist data structure."""
    playlist_id: str
    title: str
    description: str
    user_id: str
    username: str
    permalink_url: str
    artwork_url: str
    created_at: datetime
    duration: int
    track_count: int
    playback_count: int
    favoritings_count: int
    tag_list: List[str]
    tracks: List[SoundCloudTrack]
    public: bool

@dataclass
class SoundCloudUser:
    """
SoundCloud user data structure."""
    user_id: str
    username: str
    permalink: str
    permalink_url: str
    avatar_url: str
    description: str
    country: str
    city: str
    website: str
    website_title: str
    followers_count: int
    followings_count: int
    track_count: int
    playlist_count: int
    public_favorites_count: int
    reposts_count: int
    verified: bool
    pro: bool
    pro_unlimited: bool

@dataclass
class SoundCloudComment:
    """
SoundCloud comment data structure."""
    comment_id: str
    track_id: str
    user_id: str
    username: str
    body: str
    timestamp: int  # position in track in milliseconds
    created_at: datetime

class SoundCloudCrawler:
    """
    Professional SoundCloud crawler implementation.
    
    Features:
    - SoundCloud API v2 integration
    - Audio content discovery and monitoring
    - Artist and label tracking
    - Playlist and album monitoring
    - Audio fingerprinting integration
    - Genre and tag analysis
    - Real-time upload monitoring
    - Comment and engagement analysis
    - Music trend detection
    - Audio quality assessment
    """
    
    def __init__(self):
        """
Initialize SoundCloud crawler."""
        self.client_id = settings.SOUNDCLOUD_CLIENT_ID
        self.client_secret = settings.SOUNDCLOUD_CLIENT_SECRET
        self.access_token = settings.SOUNDCLOUD_ACCESS_TOKEN
        self.rate_limiter = SoundCloudRateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.content_analyzer = ContentAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
        self.encryption = FieldEncryption()
        
        # API endpoints
        self.base_api_url = "https://api.soundcloud.com"
        self.api_v2_url = "https://api-v2.soundcloud.com"
        
        # Headers for API requests
        self.headers = {
            "Authorization": f"OAuth {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": self.user_agent_rotator.get_random()
        }
        
        # Genre mapping for categorization
        self.genre_categories = {
            "electronic": ["house", "techno", "dubstep", "trance", "drum & bass"],
            "hip_hop": ["rap", "trap", "hip hop", "drill"],
            "rock": ["alternative", "indie", "metal", "punk"],
            "pop": ["pop", "dance", "disco"],
            "ambient": ["ambient", "chill", "lo-fi", "downtempo"],
            "classical": ["classical", "orchestral", "piano", "violin"]
        }
    
    async def search_tracks(
        self,
        query: str,
        max_results: int = 100,
        genre: Optional[str] = None,
        duration_filter: Optional[tuple] = None,
        created_at_filter: Optional[tuple] = None
    ) -> AsyncGenerator[SoundCloudTrack, None]:
        """
        Search SoundCloud tracks with advanced filtering.
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            genre: Filter by genre
            duration_filter: Duration range (min_ms, max_ms)
            created_at_filter: Date range (start_date, end_date)
            
        Yields:
            SoundCloudTrack: Track data
        """
        await self.rate_limiter.wait_if_needed("search")
        
        try:
            params = {
                "q": query,
                "limit": min(max_results, 50),
                "offset": 0,
                "linked_partitioning": 1
            }
            
            if genre:
                params["filter"] = f"genre:{genre}"
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_api_url}/tracks"
                
                while params["offset"] < max_results:
                    async with session.get(url, headers=self.headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            tracks = data.get("collection", [])
                            
                            if not tracks:
                                break
                            
                            for track_data in tracks:
                                track = self._parse_track_data(track_data)
                                if track and self._filter_track(track, duration_filter, created_at_filter):
                                    yield track
                            
                            # Check for next page
                            next_href = data.get("next_href")
                            if not next_href:
                                break
                            
                            params["offset"] += len(tracks)
                        
                        elif response.status == 429:
                            raise RateLimitError("SoundCloud API rate limit exceeded")
                        else:
                            logger.error(f"SoundCloud API error: {response.status}")
                            break
                        
        except Exception as e:
            logger.error(f"Error searching SoundCloud tracks: {e}")
            raise CrawlerError(f"SoundCloud search failed: {e}")
    
    async def monitor_user(
        self,
        username: str,
        check_interval: int = 3600
    ) -> AsyncGenerator[SoundCloudTrack, None]:
        """
        Monitor SoundCloud user for new uploads.
        
        Args:
            username: SoundCloud username to monitor
            check_interval: Check interval in seconds
            
        Yields:
            SoundCloudTrack: New tracks from the user
        """
        user_id = await self._get_user_id(username)
        if not user_id:
            raise CrawlerError(f"User not found: {username}")
        
        last_check = datetime.now()
        
        while True:
            try:
                await self.rate_limiter.wait_if_needed("user_tracks")
                
                async with aiohttp.ClientSession() as session:
                    url = f"{self.base_api_url}/users/{user_id}/tracks"
                    params = {
                        "limit": 20,
                        "linked_partitioning": 1
                    }
                    
                    async with session.get(url, headers=self.headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            tracks = data.get("collection", [])
                            
                            for track_data in tracks:
                                track = self._parse_track_data(track_data)
                                if track and track.created_at > last_check:
                                    yield track
                            
                            last_check = datetime.now()
                        
                        elif response.status == 429:
                            logger.warning("Rate limit hit, backing off")
                            await asyncio.sleep(300)
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring SoundCloud user: {e}")
                await asyncio.sleep(60)
    
    async def get_track_comments(
        self,
        track_id: str,
        max_comments: int = 100
    ) -> List[SoundCloudComment]:
        """
        Get comments for a SoundCloud track.
        
        Args:
            track_id: SoundCloud track ID
            max_comments: Maximum number of comments
            
        Returns:
            List[SoundCloudComment]: Track comments
        """
        await self.rate_limiter.wait_if_needed("comments")
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_api_url}/tracks/{track_id}/comments"
                params = {
                    "limit": min(max_comments, 50),
                    "linked_partitioning": 1
                }
                
                comments = []
                
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        comment_data_list = data.get("collection", [])
                        
                        for comment_data in comment_data_list:
                            comment = self._parse_comment_data(comment_data)
                            if comment:
                                comments.append(comment)
                
                return comments
                
        except Exception as e:
            logger.error(f"Error getting SoundCloud comments: {e}")
            return []
    
    async def get_trending_tracks(
        self,
        genre: Optional[str] = None,
        region: str = "all-music",
        max_results: int = 50
    ) -> List[SoundCloudTrack]:
        """
        Get trending tracks from SoundCloud.
        
        Args:
            genre: Filter by genre
            region: Geographic region filter
            max_results: Maximum number of tracks
            
        Returns:
            List[SoundCloudTrack]: Trending tracks
        """
        await self.rate_limiter.wait_if_needed("trending")
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_v2_url}/charts"
                params = {
                    "kind": "trending",
                    "genre": f"soundcloud:genres:{genre}" if genre else "all-music",
                    "region": region,
                    "limit": min(max_results, 50)
                }
                
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        tracks = []
                        
                        for item in data.get("collection", []):
                            track_data = item.get("track")
                            if track_data:
                                track = self._parse_track_data(track_data)
                                if track:
                                    tracks.append(track)
                        
                        return tracks
                    
                    elif response.status == 429:
                        raise RateLimitError("SoundCloud API rate limit exceeded")
                    else:
                        logger.error(f"SoundCloud API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting trending tracks: {e}")
            return []
    
    async def analyze_audio_content(
        self,
        track_id: str
    ) -> Dict:
        """
        Analyze audio content for similarity detection.
        
        Args:
            track_id: SoundCloud track ID
            
        Returns:
            Dict: Audio analysis results
        """
        try:
            # Get track stream URL
            track = await self._get_track_by_id(track_id)
            if not track or not track.stream_url:
                return {}
            
            # Download and analyze audio
            audio_analysis = await self.audio_analyzer.analyze_from_url(track.stream_url)
            
            return {
                "track_id": track_id,
                "fingerprint": audio_analysis.get("fingerprint"),
                "spectral_features": audio_analysis.get("spectral_features"),
                "tempo": audio_analysis.get("tempo"),
                "key": audio_analysis.get("key"),
                "loudness": audio_analysis.get("loudness"),
                "energy": audio_analysis.get("energy"),
                "valence": audio_analysis.get("valence"),
                "similarity_hash": hashlib.md5(str(audio_analysis).encode()).hexdigest()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audio content: {e}")
            return {}
    
    async def scrape_with_selenium(
        self,
        search_query: str,
        max_scroll: int = 3
    ) -> List[SoundCloudTrack]:
        """
        Scrape SoundCloud using Selenium as fallback.
        
        Args:
            search_query: Search query
            max_scroll: Maximum number of scrolls
            
        Returns:
            List[SoundCloudTrack]: Scraped tracks
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-agent={self.user_agent_rotator.get_random()}")
        
        if self.proxy_manager.get_current_proxy():
            proxy = self.proxy_manager.get_current_proxy()
            chrome_options.add_argument(f"--proxy-server={proxy}")
        
        driver = None
        tracks = []
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to SoundCloud search
            search_url = f"https://soundcloud.com/search?q={search_query}"
            driver.get(search_url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "searchList"))
            )
            
            # Scroll to load more content
            for _ in range(max_scroll):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            # Extract track elements
            track_elements = driver.find_elements(By.CSS_SELECTOR, ".searchList__item")
            
            for element in track_elements:
                try:
                    track_data = self._extract_track_from_element(element)
                    if track_data:
                        tracks.append(track_data)
                except Exception as e:
                    logger.debug(f"Error extracting track: {e}")
                    continue
            
            return tracks
            
        except Exception as e:
            logger.error(f"Error in SoundCloud Selenium scraping: {e}")
            return tracks
            
        finally:
            if driver:
                driver.quit()
    
    async def _get_user_id(self, username: str) -> Optional[str]:
        """Get SoundCloud user ID from username."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_api_url}/resolve"
                params = {
                    "url": f"https://soundcloud.com/{username}",
                    "client_id": self.client_id
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return str(data.get("id"))
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user ID: {e}")
            return None
    
    async def _get_track_by_id(self, track_id: str) -> Optional[SoundCloudTrack]:
        """Get track data by ID."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_api_url}/tracks/{track_id}"
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_track_data(data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting track by ID: {e}")
            return None
    
    def _parse_track_data(self, track_data: Dict) -> Optional[SoundCloudTrack]:
        """Parse SoundCloud track data from API response."""
        try:
            user_data = track_data.get("user", {})
            
            # Parse tags
            tag_list = []
            if track_data.get("tag_list"):
                tag_list = [tag.strip().strip('"') for tag in track_data["tag_list"].split()]
            
            # Parse created_at
            created_at = datetime.now()
            if track_data.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(track_data["created_at"].replace("Z", "+00:00"))
                except:
                    pass
            
            return SoundCloudTrack(
                track_id=str(track_data["id"]),
                title=track_data.get("title", ""),
                description=track_data.get("description", ""),
                user_id=str(user_data.get("id", "")),
                username=user_data.get("username", ""),
                user_permalink=user_data.get("permalink", ""),
                permalink_url=track_data.get("permalink_url", ""),
                stream_url=track_data.get("stream_url", ""),
                download_url=track_data.get("download_url"),
                waveform_url=track_data.get("waveform_url", ""),
                artwork_url=track_data.get("artwork_url", ""),
                created_at=created_at,
                duration=track_data.get("duration", 0),
                playback_count=track_data.get("playback_count", 0),
                download_count=track_data.get("download_count", 0),
                favoritings_count=track_data.get("favoritings_count", 0),
                comment_count=track_data.get("comment_count", 0),
                genre=track_data.get("genre", ""),
                bpm=track_data.get("bpm"),
                key_signature=track_data.get("key_signature"),
                isrc=track_data.get("isrc"),
                license=track_data.get("license", ""),
                tag_list=tag_list,
                downloadable=track_data.get("downloadable", False),
                streamable=track_data.get("streamable", True),
                public=track_data.get("public", True),
                monetization_model=track_data.get("monetization_model", "")
            )
            
        except Exception as e:
            logger.error(f"Error parsing track data: {e}")
            return None
    
    def _parse_comment_data(self, comment_data: Dict) -> Optional[SoundCloudComment]:
        """Parse SoundCloud comment data from API response."""
        try:
            user_data = comment_data.get("user", {})
            
            created_at = datetime.now()
            if comment_data.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(comment_data["created_at"].replace("Z", "+00:00"))
                except:
                    pass
            
            return SoundCloudComment(
                comment_id=str(comment_data["id"]),
                track_id=str(comment_data.get("track_id", "")),
                user_id=str(user_data.get("id", "")),
                username=user_data.get("username", ""),
                body=comment_data.get("body", ""),
                timestamp=comment_data.get("timestamp", 0),
                created_at=created_at
            )
            
        except Exception as e:
            logger.error(f"Error parsing comment data: {e}")
            return None
    
    def _filter_track(
        self,
        track: SoundCloudTrack,
        duration_filter: Optional[tuple],
        created_at_filter: Optional[tuple]
    ) -> bool:
        """Filter track based on criteria."""
        try:
            # Duration filter
            if duration_filter:
                min_duration, max_duration = duration_filter
                if not (min_duration <= track.duration <= max_duration):
                    return False
            
            # Date filter
            if created_at_filter:
                start_date, end_date = created_at_filter
                if not (start_date <= track.created_at <= end_date):
                    return False
            
            return True
            
        except Exception:
            return True
    
    def _extract_track_from_element(self, element) -> Optional[SoundCloudTrack]:
        """
Extract track data from Selenium web element."""
        try:
            # Extract title
            title_element = element.find_element(By.CSS_SELECTOR, ".soundTitle__title")
            title = title_element.text if title_element else ""
            
            # Extract username
            user_element = element.find_element(By.CSS_SELECTOR, ".soundTitle__username")
            username = user_element.text if user_element else ""
            
            # Extract URL
            link_element = element.find_element(By.CSS_SELECTOR, ".sound__coverArt")
            permalink_url = link_element.get_attribute("href") if link_element else ""
            
            return SoundCloudTrack(
                track_id=f"scraped_{hash(title + username)}",
                title=title,
                description="",
                user_id="",
                username=username,
                user_permalink="",
                permalink_url=permalink_url,
                stream_url="",
                download_url=None,
                waveform_url="",
                artwork_url="",
                created_at=datetime.now(),
                duration=0,
                playback_count=0,
                download_count=0,
                favoritings_count=0,
                comment_count=0,
                genre="",
                bpm=None,
                key_signature=None,
                isrc=None,
                license="",
                tag_list=[],
                downloadable=False,
                streamable=True,
                public=True,
                monetization_model=""
            )
            
        except Exception as e:
            logger.debug(f"Error extracting track from element: {e}")
            return None
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, 'session') and self.session:
            await self.session.close()
        
        logger.info("SoundCloud crawler closed")

# Export for module
__all__ = ["SoundCloudCrawler", "SoundCloudTrack", "SoundCloudPlaylist", "SoundCloudUser", "SoundCloudComment"]
