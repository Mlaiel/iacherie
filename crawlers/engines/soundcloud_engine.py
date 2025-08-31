"""SoundCloud Crawling Engine
==========================

Advanced SoundCloud crawler for music discovery, artist analytics, and track monitoring.
Handles track metadata extraction, artist analysis, and playlist discovery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  AVERTISSEMENT LÉGAL ⚠️
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
from bs4 import BeautifulSoup
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
class SoundCloudTrack:
    """SoundCloud track data structure"""
    id: str
    title: str
    description: Optional[str]
    user_id: str
    user_username: str
    user_display_name: str
    duration: int
    genre: Optional[str]
    tag_list: List[str]
    label_name: Optional[str]
    release_date: Optional[datetime]
    created_at: datetime
    permalink_url: str
    stream_url: Optional[str]
    download_url: Optional[str]
    artwork_url: Optional[str]
    waveform_url: Optional[str]
    playback_count: int
    download_count: int
    favoritings_count: int
    reposts_count: int
    comment_count: int
    is_downloadable: bool
    is_streamable: bool
    license: str
    purchase_url: Optional[str]
    bpm: Optional[float]
    key_signature: Optional[str]


@dataclass
class SoundCloudUser:
    """SoundCloud user data structure"""
    id: str
    username: str
    permalink: str
    display_name: str
    description: Optional[str]
    city: Optional[str]
    country: Optional[str]
    avatar_url: Optional[str]
    banner_url: Optional[str]
    followers_count: int
    followings_count: int
    track_count: int
    playlist_count: int
    likes_count: int
    reposts_count: int
    is_verified: bool
    is_pro: bool
    is_pro_unlimited: bool
    website: Optional[str]
    website_title: Optional[str]
    created_at: datetime
    last_modified: datetime
    permalink_url: str


@dataclass
class SoundCloudPlaylist:
    """SoundCloud playlist data structure"""
    id: str
    title: str
    description: Optional[str]
    user_id: str
    user_username: str
    duration: int
    track_count: int
    tracks: List[str]
    created_at: datetime
    last_modified: datetime
    permalink_url: str
    artwork_url: Optional[str]
    is_album: bool
    genre: Optional[str]
    tag_list: List[str]
    label_name: Optional[str]
    release_date: Optional[datetime]
    license: str
    purchase_url: Optional[str]


class SoundCloudCrawlerEngine(BaseCrawlerEngine):
    """
    Professional SoundCloud crawler engine for music content analysis.
    
    Features:
    - Track discovery and analytics
    - Artist performance monitoring
    - Playlist analysis
    - Genre trend tracking
    - Audio content protection
    - Music recommendation analysis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize SoundCloud crawler engine"""
        super().__init__(platform="soundcloud", config=config)
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            requests_per_minute=60,
            requests_per_hour=3600
        )
        
        # Cache configuration
        self.cache_manager = CacheManager(
            cache_ttl=timedelta(hours=1),
            max_cache_size=5000
        )
        
        # API configuration
        self.base_url = "https://soundcloud.com"
        self.api_base = "https://api-v2.soundcloud.com"
        self.client_id = self.config.get("soundcloud_client_id")
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Selenium for web scraping
        self.driver: Optional[webdriver.Chrome] = None
        
        logger.info("SoundCloud crawler engine initialized")
    
    async def initialize(self) -> None:
        """Initialize the crawler engine"""
        try:
            await self._create_session()
            self._setup_selenium()
            if not self.client_id:
                await self._extract_client_id()
            logger.info("SoundCloud engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SoundCloud engine: {e}")
            raise CrawlerError(f"Initialization failed: {e}")
    
    async def _create_session(self) -> None:
        """Create HTTP session with proper headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://soundcloud.com/',
            'Origin': 'https://soundcloud.com'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=100)
        )
    
    def _setup_selenium(self) -> None:
        """Setup Selenium WebDriver"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("Selenium WebDriver initialized for SoundCloud")
        except Exception as e:
            logger.warning(f"Failed to initialize Selenium: {e}")
    
    async def _extract_client_id(self) -> None:
        """Extract client ID from SoundCloud website"""
        try:
            if not self.driver:
                logger.warning("Cannot extract client ID without Selenium")
                return
            
            self.driver.get(self.base_url)
            
            # Look for script tags containing client_id
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            
            for script in scripts:
                script_content = script.get_attribute("innerHTML")
                if script_content and "client_id" in script_content:
                    # Extract client_id using regex
                    match = re.search(r'"client_id":"([^"]+)"', script_content)
                    if match:
                        self.client_id = match.group(1)
                        logger.info("Successfully extracted SoundCloud client ID")
                        return
            
            logger.warning("Could not extract SoundCloud client ID")
            
        except Exception as e:
            logger.error(f"Error extracting client ID: {e}")
    
    async def search_tracks(
        self,
        query: str,
        limit: int = 50,
        genre: Optional[str] = None
    ) -> List[SoundCloudTrack]:
        """
        Search for tracks on SoundCloud
        
        Args:
            query: Search query
            limit: Number of tracks to return
            genre: Genre filter
            
        Returns:
            List of tracks matching the query
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"search_tracks:{hashlib.md5(f'{query}:{limit}:{genre}'.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            if not self.client_id:
                raise CrawlerError("SoundCloud client ID not available")
            
            # Build API URL
            url = f"{self.api_base}/search/tracks"
            params = {
                'q': query,
                'limit': min(limit, 200),
                'client_id': self.client_id
            }
            
            if genre:
                params['filter.genre_or_tag'] = genre
            
            async with self.session.get(url, params=params) as response:
                if response.status == 429:
                    raise RateLimitError("SoundCloud API rate limit exceeded")
                elif response.status == 401:
                    raise AuthenticationError("Invalid SoundCloud client ID")
                elif response.status != 200:
                    raise CrawlerError(f"Search request failed: {response.status}")
                
                data = await response.json()
                tracks = []
                
                if 'collection' in data:
                    for track_data in data['collection']:
                        track = self._parse_track_data(track_data)
                        tracks.append(track)
                
                # Cache results
                await self.cache_manager.set(cache_key, tracks)
                
                logger.info(f"Found {len(tracks)} tracks for query: {query}")
                return tracks
                
        except Exception as e:
            logger.error(f"Error searching tracks: {e}")
            raise CrawlerError(f"Track search failed: {e}")
    
    async def get_track_details(self, track_id: str) -> Optional[SoundCloudTrack]:
        """
        Get detailed information about a track
        
        Args:
            track_id: SoundCloud track ID
            
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
            
            if not self.client_id:
                raise CrawlerError("SoundCloud client ID not available")
            
            url = f"{self.api_base}/tracks/{track_id}"
            params = {'client_id': self.client_id}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 404:
                    raise ContentNotFoundError(f"Track not found: {track_id}")
                elif response.status == 429:
                    raise RateLimitError("SoundCloud API rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"Track request failed: {response.status}")
                
                data = await response.json()
                track = self._parse_track_data(data)
                
                # Cache result
                await self.cache_manager.set(cache_key, track)
                
                return track
                
        except Exception as e:
            logger.error(f"Error getting track details: {e}")
            raise CrawlerError(f"Track details retrieval failed: {e}")
    
    async def get_user_profile(self, username: str) -> Optional[SoundCloudUser]:
        """
        Get user profile information
        
        Args:
            username: SoundCloud username
            
        Returns:
            User profile data or None if not found
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"user_profile:{username}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            if not self.client_id:
                raise CrawlerError("SoundCloud client ID not available")
            
            # First, resolve username to user ID
            resolve_url = f"{self.api_base}/resolve"
            resolve_params = {
                'url': f"https://soundcloud.com/{username}",
                'client_id': self.client_id
            }
            
            async with self.session.get(resolve_url, params=resolve_params) as response:
                if response.status == 404:
                    raise ContentNotFoundError(f"User not found: {username}")
                elif response.status == 429:
                    raise RateLimitError("SoundCloud API rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"User resolve failed: {response.status}")
                
                user_data = await response.json()
                user = self._parse_user_data(user_data)
                
                # Cache result
                await self.cache_manager.set(cache_key, user)
                
                return user
                
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise CrawlerError(f"User profile retrieval failed: {e}")
    
    async def get_user_tracks(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[SoundCloudTrack]:
        """
        Get tracks from a user
        
        Args:
            user_id: SoundCloud user ID
            limit: Number of tracks to retrieve
            
        Returns:
            List of user's tracks
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"user_tracks:{user_id}:{limit}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            if not self.client_id:
                raise CrawlerError("SoundCloud client ID not available")
            
            url = f"{self.api_base}/users/{user_id}/tracks"
            params = {
                'limit': min(limit, 200),
                'client_id': self.client_id
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 404:
                    raise ContentNotFoundError(f"User not found: {user_id}")
                elif response.status == 429:
                    raise RateLimitError("SoundCloud API rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"User tracks request failed: {response.status}")
                
                data = await response.json()
                tracks = []
                
                if 'collection' in data:
                    for track_data in data['collection']:
                        track = self._parse_track_data(track_data)
                        tracks.append(track)
                
                # Cache results
                await self.cache_manager.set(cache_key, tracks)
                
                logger.info(f"Retrieved {len(tracks)} tracks for user: {user_id}")
                return tracks
                
        except Exception as e:
            logger.error(f"Error getting user tracks: {e}")
            raise CrawlerError(f"User tracks retrieval failed: {e}")
    
    def _parse_track_data(self, track_data: Dict[str, Any]) -> SoundCloudTrack:
        """Parse track data from API response"""
        try:
            user_data = track_data.get('user', {})
            
            return SoundCloudTrack(
                id=str(track_data.get('id', '')),
                title=track_data.get('title', ''),
                description=track_data.get('description'),
                user_id=str(user_data.get('id', '')),
                user_username=user_data.get('permalink', ''),
                user_display_name=user_data.get('username', ''),
                duration=track_data.get('duration', 0),
                genre=track_data.get('genre'),
                tag_list=track_data.get('tag_list', '').split() if track_data.get('tag_list') else [],
                label_name=track_data.get('label_name'),
                release_date=datetime.fromisoformat(track_data.get('release_date', '').replace('Z', '+00:00')) if track_data.get('release_date') else None,
                created_at=datetime.fromisoformat(track_data.get('created_at', '').replace('Z', '+00:00')) if track_data.get('created_at') else datetime.utcnow(),
                permalink_url=track_data.get('permalink_url', ''),
                stream_url=track_data.get('stream_url'),
                download_url=track_data.get('download_url'),
                artwork_url=track_data.get('artwork_url'),
                waveform_url=track_data.get('waveform_url'),
                playback_count=track_data.get('playback_count', 0),
                download_count=track_data.get('download_count', 0),
                favoritings_count=track_data.get('favoritings_count', 0),
                reposts_count=track_data.get('reposts_count', 0),
                comment_count=track_data.get('comment_count', 0),
                is_downloadable=track_data.get('downloadable', False),
                is_streamable=track_data.get('streamable', True),
                license=track_data.get('license', 'all-rights-reserved'),
                purchase_url=track_data.get('purchase_url'),
                bpm=track_data.get('bpm'),
                key_signature=track_data.get('key_signature')
            )
        except Exception as e:
            logger.error(f"Error parsing track data: {e}")
            raise CrawlerError(f"Track data parsing failed: {e}")
    
    def _parse_user_data(self, user_data: Dict[str, Any]) -> SoundCloudUser:
        """Parse user data from API response"""
        try:
            return SoundCloudUser(
                id=str(user_data.get('id', '')),
                username=user_data.get('username', ''),
                permalink=user_data.get('permalink', ''),
                display_name=user_data.get('full_name', ''),
                description=user_data.get('description'),
                city=user_data.get('city'),
                country=user_data.get('country'),
                avatar_url=user_data.get('avatar_url'),
                banner_url=user_data.get('banner_url'),
                followers_count=user_data.get('followers_count', 0),
                followings_count=user_data.get('followings_count', 0),
                track_count=user_data.get('track_count', 0),
                playlist_count=user_data.get('playlist_count', 0),
                likes_count=user_data.get('likes_count', 0),
                reposts_count=user_data.get('reposts_count', 0),
                is_verified=user_data.get('verified', False),
                is_pro=user_data.get('pro', False),
                is_pro_unlimited=user_data.get('pro_unlimited', False),
                website=user_data.get('website'),
                website_title=user_data.get('website_title'),
                created_at=datetime.fromisoformat(user_data.get('created_at', '').replace('Z', '+00:00')) if user_data.get('created_at') else datetime.utcnow(),
                last_modified=datetime.fromisoformat(user_data.get('last_modified', '').replace('Z', '+00:00')) if user_data.get('last_modified') else datetime.utcnow(),
                permalink_url=user_data.get('permalink_url', '')
            )
        except Exception as e:
            logger.error(f"Error parsing user data: {e}")
            raise CrawlerError(f"User data parsing failed: {e}")
    
    async def analyze_trending_genres(self) -> List[Dict[str, Any]]:
        """
        Analyze trending genres on SoundCloud
        
        Returns:
            List of trending genres with metadata
        """
        try:
            # Search for popular tracks in different genres
            genres = [
                'electronic', 'hip-hop', 'pop', 'rock', 'indie', 'ambient',
                'trap', 'house', 'techno', 'dubstep', 'jazz', 'classical'
            ]
            
            trending_data = []
            
            for genre in genres:
                tracks = await self.search_tracks(
                    query="",
                    limit=20,
                    genre=genre
                )
                
                if tracks:
                    total_plays = sum(track.playback_count for track in tracks)
                    avg_plays = total_plays / len(tracks)
                    total_likes = sum(track.favoritings_count for track in tracks)
                    
                    trending_data.append({
                        'genre': genre,
                        'track_count': len(tracks),
                        'total_plays': total_plays,
                        'average_plays': avg_plays,
                        'total_likes': total_likes,
                        'engagement_rate': (total_likes / total_plays) * 100 if total_plays > 0 else 0,
                        'analysis_date': datetime.utcnow().isoformat()
                    })
            
            # Sort by engagement rate
            trending_data.sort(key=lambda x: x['engagement_rate'], reverse=True)
            
            logger.info(f"Analyzed trends for {len(trending_data)} genres")
            return trending_data
            
        except Exception as e:
            logger.error(f"Error analyzing trending genres: {e}")
            raise CrawlerError(f"Trending genres analysis failed: {e}")
    
    async def monitor_audio_content_protection(
        self,
        track_title: str,
        artist_name: str
    ) -> Dict[str, Any]:
        """
        Monitor for unauthorized use of audio content
        
        Args:
            track_title: Title of the track to monitor
            artist_name: Name of the original artist
            
        Returns:
            Content protection monitoring results
        """
        try:
            protection_results = {
                'track_title': track_title,
                'original_artist': artist_name,
                'potential_violations': [],
                'monitoring_timestamp': datetime.utcnow().isoformat()
            }
            
            # Search for tracks with similar titles
            search_queries = [
                track_title,
                f"{track_title} remix",
                f"{track_title} cover",
                f"{artist_name} {track_title}"
            ]
            
            for query in search_queries:
                tracks = await self.search_tracks(query, limit=50)
                
                for track in tracks:
                    # Check if it's not by the original artist
                    if (track.user_display_name.lower() != artist_name.lower() and
                        track_title.lower() in track.title.lower()):
                        
                        similarity_score = self._calculate_title_similarity(
                            track_title, track.title
                        )
                        
                        if similarity_score > 0.6:  # High similarity threshold
                            protection_results['potential_violations'].append({
                                'track_id': track.id,
                                'track_title': track.title,
                                'artist_name': track.user_display_name,
                                'similarity_score': similarity_score,
                                'playback_count': track.playback_count,
                                'url': track.permalink_url
                            })
            
            logger.info(f"Content protection monitoring completed for {track_title}")
            return protection_results
            
        except Exception as e:
            logger.error(f"Error monitoring audio content protection: {e}")
            raise CrawlerError(f"Audio content protection monitoring failed: {e}")
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two track titles"""
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def cleanup(self) -> None:
        """Clean up resources"""
        try:
            if self.session:
                await self.session.close()
            if self.driver:
                self.driver.quit()
            await super().cleanup()
            logger.info("SoundCloud engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __str__(self) -> str:
        return f"SoundCloudCrawlerEngine(platform=soundcloud)"
