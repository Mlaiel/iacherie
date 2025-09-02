"""Bandcamp Crawling Engine
========================

Advanced Bandcamp crawler for independent music discovery and artist analytics.
Handles album metadata extraction, artist analysis, and fan engagement data.

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
from ..models.content_models import MusicContent, ArtistContent, AlbumContent
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class BandcampTrack:
    """
Bandcamp track data structure"""
    id: str
    title: str
    artist_name: str
    artist_url: str
    album_title: str
    album_url: str
    duration: Optional[int]
    file_url: Optional[str]
    lyrics: Optional[str]
    tags: List[str]
    price: Optional[float]
    currency: str
    stream_url: Optional[str]
    download_available: bool
    track_number: int
    release_date: Optional[str]
    url: str
    created_at: datetime


@dataclass
class BandcampAlbum:
    """
Bandcamp album data structure"""
    id: str
    title: str
    artist_name: str
    artist_url: str
    description: Optional[str]
    artwork_url: Optional[str]
    release_date: str
    tags: List[str]
    genre: str
    track_count: int
    tracks: List[str]
    price: Optional[float]
    currency: str
    sold_count: Optional[int]
    fan_funding_goal: Optional[float]
    fan_funding_current: Optional[float]
    url: str
    created_at: datetime


@dataclass
class BandcampArtist:
    """
Bandcamp artist data structure"""
    id: str
    name: str
    url: str
    bio: Optional[str]
    location: Optional[str]
    profile_image_url: Optional[str]
    banner_image_url: Optional[str]
    discography: List[str]
    follower_count: Optional[int]
    following_count: Optional[int]
    tags: List[str]
    social_links: Dict[str, str]
    verified: bool
    created_at: datetime


class BandcampCrawlerEngine(BaseCrawlerEngine):
    """
    Professional Bandcamp crawler engine for independent music data extraction.
    
    Features:
    - Artist and album discovery
    - Track metadata extraction
    - Fan engagement analytics
    - Independent music monitoring
    - Advanced web scraping
    - Content protection monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
Initialize Bandcamp crawler engine"""
        super().__init__(platform="bandcamp", config=config)
        
        # Rate limiting (more conservative for web scraping)
        self.rate_limiter = RateLimiter(
            requests_per_minute=30,
            requests_per_hour=1800
        )
        
        # Cache configuration
        self.cache_manager = CacheManager(
            cache_ttl=timedelta(hours=2),
            max_cache_size=5000
        )
        
        # Base URL
        self.base_url = "https://bandcamp.com"
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Selenium driver for dynamic content
        self.driver: Optional[webdriver.Chrome] = None
        
        logger.info("Bandcamp crawler engine initialized")
    
    async def initialize(self) -> None:
        """Initialize the crawler engine"""
        try:
            await self._create_session()
            self._setup_selenium()
            logger.info("Bandcamp engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Bandcamp engine: {e}")
            raise CrawlerError(f"Initialization failed: {e}")
    
    async def _create_session(self) -> None:
        """Create HTTP session with proper headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=50)
        )
    
    def _setup_selenium(self) -> None:
        """
Setup Selenium WebDriver for dynamic content"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("Selenium WebDriver initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Selenium: {e}")
    
    async def search_music(
        self,
        query: str,
        search_type: str = "all",
        location: Optional[str] = None,
        sort: str = "pop"
    ) -> List[Dict[str, Any]]:
        """
        Search for music on Bandcamp
        
        Args:
            query: Search query
            search_type: Type of search (all, artists, albums, tracks, fans)
            location: Geographic location filter
            sort: Sort order (pop, date, name)
            
        Returns:
            List of search results
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"search:{hashlib.md5(f'{query}:{search_type}:{location}:{sort}'.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Build search URL
            search_url = f"{self.base_url}/search"
            params = {
                'q': query,
                'item_type': search_type,
                'sort_field': sort
            }
            
            if location:
                params['location'] = location
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 429:
                    raise RateLimitError("Bandcamp rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"Search request failed: {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                search_results = soup.find_all('li', class_='searchresult')
                
                for result in search_results:
                    parsed_result = self._parse_search_result(result)
                    if parsed_result:
                        results.append(parsed_result)
                
                # Cache results
                await self.cache_manager.set(cache_key, results)
                
                logger.info(f"Found {len(results)} results for query: {query}")
                return results
                
        except Exception as e:
            logger.error(f"Error searching music: {e}")
            raise CrawlerError(f"Music search failed: {e}")
    
    async def get_artist_info(self, artist_url: str) -> Optional[BandcampArtist]:
        """
        Get detailed information about an artist
        
        Args:
            artist_url: Bandcamp artist URL
            
        Returns:
            Artist information or None if not found
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"artist_info:{hashlib.md5(artist_url.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            async with self.session.get(artist_url) as response:
                if response.status == 404:
                    raise ContentNotFoundError(f"Artist not found: {artist_url}")
                elif response.status == 429:
                    raise RateLimitError("Bandcamp rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"Request failed: {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                artist = self._parse_artist_page(soup, artist_url)
                
                # Cache result
                await self.cache_manager.set(cache_key, artist)
                
                return artist
                
        except Exception as e:
            logger.error(f"Error getting artist info: {e}")
            raise CrawlerError(f"Artist info retrieval failed: {e}")
    
    async def get_album_info(self, album_url: str) -> Optional[BandcampAlbum]:
        """
        Get detailed information about an album
        
        Args:
            album_url: Bandcamp album URL
            
        Returns:
            Album information or None if not found
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"album_info:{hashlib.md5(album_url.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            async with self.session.get(album_url) as response:
                if response.status == 404:
                    raise ContentNotFoundError(f"Album not found: {album_url}")
                elif response.status == 429:
                    raise RateLimitError("Bandcamp rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"Request failed: {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                album = self._parse_album_page(soup, album_url)
                
                # Cache result
                await self.cache_manager.set(cache_key, album)
                
                return album
                
        except Exception as e:
            logger.error(f"Error getting album info: {e}")
            raise CrawlerError(f"Album info retrieval failed: {e}")
    
    async def get_track_info(self, track_url: str) -> Optional[BandcampTrack]:
        """
        Get detailed information about a track
        
        Args:
            track_url: Bandcamp track URL
            
        Returns:
            Track information or None if not found
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"track_info:{hashlib.md5(track_url.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            async with self.session.get(track_url) as response:
                if response.status == 404:
                    raise ContentNotFoundError(f"Track not found: {track_url}")
                elif response.status == 429:
                    raise RateLimitError("Bandcamp rate limit exceeded")
                elif response.status != 200:
                    raise CrawlerError(f"Request failed: {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                track = self._parse_track_page(soup, track_url)
                
                # Cache result
                await self.cache_manager.set(cache_key, track)
                
                return track
                
        except Exception as e:
            logger.error(f"Error getting track info: {e}")
            raise CrawlerError(f"Track info retrieval failed: {e}")
    
    def _parse_search_result(self, result_element) -> Optional[Dict[str, Any]]:
        """Parse a search result element"""
        try:
            result_type = "unknown"
            
            # Determine result type
            if result_element.find('div', class_='artistname'):
                result_type = "artist"
            elif result_element.find('div', class_='albumname'):
                result_type = "album"
            elif result_element.find('div', class_='trackname'):
                result_type = "track"
            
            # Extract common data
            art_elem = result_element.find('div', class_='art')
            img_elem = art_elem.find('img') if art_elem else None
            
            name_elem = result_element.find('div', class_='heading')
            link_elem = name_elem.find('a') if name_elem else None
            
            return {
                'type': result_type,
                'title': link_elem.get_text(strip=True) if link_elem else '',
                'url': link_elem.get('href') if link_elem else '',
                'image_url': img_elem.get('src') if img_elem else None,
                'artist_name': self._extract_artist_name(result_element),
                'location': self._extract_location(result_element),
                'tags': self._extract_tags(result_element)
            }
            
        except Exception as e:
            logger.warning(f"Error parsing search result: {e}")
            return None
    
    def _parse_artist_page(self, soup: BeautifulSoup, url: str) -> BandcampArtist:
        """Parse artist page data"""
        try:
            # Extract artist name
            name_elem = soup.find('p', id='band-name-location')
            name = name_elem.find('span', class_='title').get_text(strip=True) if name_elem else ''
            
            # Extract bio
            bio_elem = soup.find('div', class_='bio')
            bio = bio_elem.get_text(strip=True) if bio_elem else None
            
            # Extract location
            location_elem = soup.find('span', class_='location')
            location = location_elem.get_text(strip=True) if location_elem else None
            
            # Extract profile image
            profile_img = soup.find('div', class_='bio-pic')
            profile_img_url = profile_img.find('img').get('src') if profile_img and profile_img.find('img') else None
            
            # Extract discography
            discography = []
            music_items = soup.find_all('li', class_='music-grid-item')
            for item in music_items:
                link = item.find('a')
                if link:
                    discography.append(urljoin(url, link.get('href')))
            
            # Extract tags
            tags = self._extract_page_tags(soup)
            
            # Extract social links
            social_links = self._extract_social_links(soup)
            
            return BandcampArtist(
                id=hashlib.md5(url.encode()).hexdigest(),
                name=name,
                url=url,
                bio=bio,
                location=location,
                profile_image_url=profile_img_url,
                banner_image_url=None,  # Extract if available
                discography=discography,
                follower_count=None,  # Not publicly available
                following_count=None,  # Not publicly available
                tags=tags,
                social_links=social_links,
                verified=False,  # Bandcamp doesn't have verification
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error parsing artist page: {e}")
            raise CrawlerError(f"Artist page parsing failed: {e}")
    
    def _parse_album_page(self, soup: BeautifulSoup, url: str) -> BandcampAlbum:
        """Parse album page data"""
        try:
            # Extract album title
            title_elem = soup.find('h2', class_='trackTitle')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract artist name
            artist_elem = soup.find('h3', class_='albumTitle')
            artist_link = artist_elem.find('a') if artist_elem else None
            artist_name = artist_link.get_text(strip=True) if artist_link else ''
            artist_url = artist_link.get('href') if artist_link else ''
            
            # Extract description
            desc_elem = soup.find('div', class_='tralbumData')
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            # Extract artwork
            artwork_elem = soup.find('div', id='tralbumArt')
            artwork_img = artwork_elem.find('img') if artwork_elem else None
            artwork_url = artwork_img.get('src') if artwork_img else None
            
            # Extract tracks
            tracks = []
            track_table = soup.find('table', class_='track_list')
            if track_table:
                track_rows = track_table.find_all('tr', class_='track_row_view')
                for row in track_rows:
                    track_title_elem = row.find('span', class_='track-title')
                    if track_title_elem:
                        tracks.append(track_title_elem.get_text(strip=True))
            
            # Extract tags
            tags = self._extract_page_tags(soup)
            
            # Extract price information
            price_elem = soup.find('span', class_='buyItemExtra')
            price = self._extract_price(price_elem) if price_elem else None
            
            return BandcampAlbum(
                id=hashlib.md5(url.encode()).hexdigest(),
                title=title,
                artist_name=artist_name,
                artist_url=artist_url,
                description=description,
                artwork_url=artwork_url,
                release_date='',  # Extract if available
                tags=tags,
                genre=tags[0] if tags else '',
                track_count=len(tracks),
                tracks=tracks,
                price=price,
                currency='USD',  # Default, extract if available
                sold_count=None,  # Not publicly available
                fan_funding_goal=None,  # Extract if available
                fan_funding_current=None,  # Extract if available
                url=url,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error parsing album page: {e}")
            raise CrawlerError(f"Album page parsing failed: {e}")
    
    def _parse_track_page(self, soup: BeautifulSoup, url: str) -> BandcampTrack:
        """Parse track page data"""
        try:
            # Extract track title
            title_elem = soup.find('h2', class_='trackTitle')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract artist name and URL
            artist_elem = soup.find('h3', class_='albumTitle')
            artist_link = artist_elem.find('a') if artist_elem else None
            artist_name = artist_link.get_text(strip=True) if artist_link else ''
            artist_url = artist_link.get('href') if artist_link else ''
            
            # Extract album info
            album_elem = soup.find('span', class_='fromAlbum')
            album_link = album_elem.find('a') if album_elem else None
            album_title = album_link.get_text(strip=True) if album_link else ''
            album_url = album_link.get('href') if album_link else ''
            
            # Extract lyrics
            lyrics_elem = soup.find('div', class_='lyricsText')
            lyrics = lyrics_elem.get_text(strip=True) if lyrics_elem else None
            
            # Extract tags
            tags = self._extract_page_tags(soup)
            
            # Extract price
            price_elem = soup.find('span', class_='buyItemExtra')
            price = self._extract_price(price_elem) if price_elem else None
            
            return BandcampTrack(
                id=hashlib.md5(url.encode()).hexdigest(),
                title=title,
                artist_name=artist_name,
                artist_url=artist_url,
                album_title=album_title,
                album_url=album_url,
                duration=None,  # Extract if available
                file_url=None,  # Not publicly available
                lyrics=lyrics,
                tags=tags,
                price=price,
                currency='USD',  # Default
                stream_url=None,  # Extract if available
                download_available=price is not None,
                track_number=1,  # Extract if available
                release_date=None,  # Extract if available
                url=url,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error parsing track page: {e}")
            raise CrawlerError(f"Track page parsing failed: {e}")
    
    def _extract_artist_name(self, element) -> str:
        """Extract artist name from search result"""
        artist_elem = element.find('div', class_='subhead')
        return artist_elem.get_text(strip=True) if artist_elem else ''
    
    def _extract_location(self, element) -> Optional[str]:
        """
Extract location from search result"""
        location_elem = element.find('div', class_='geo')
        return location_elem.get_text(strip=True) if location_elem else None
    
    def _extract_tags(self, element) -> List[str]:
        """
Extract tags from search result"""
        tags = []
        tag_elements = element.find_all('div', class_='tag')
        for tag in tag_elements:
            tags.append(tag.get_text(strip=True))
        return tags
    
    def _extract_page_tags(self, soup: BeautifulSoup) -> List[str]:
        """
Extract tags from page"""
        tags = []
        tag_elements = soup.find_all('a', class_='tag')
        for tag in tag_elements:
            tags.append(tag.get_text(strip=True))
        return tags
    
    def _extract_social_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
Extract social media links"""
        social_links = {}
        social_section = soup.find('div', id='bio-links')
        if social_section:
            links = social_section.find_all('a')
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if href:
                    social_links[text] = href
        return social_links
    
    def _extract_price(self, price_elem) -> Optional[float]:
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess__extract_price_input(price_elem)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess__extract_price_result(result)
            
                    logger.info(f"AI processing _extract_price completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing _extract_price failed: {e}")
                    raise
    async def monitor_independent_releases(
        self,
        genre: str,
        location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Monitor new independent releases in specific genre/location
        
        Args:
            genre: Music genre to monitor
            location: Geographic location filter
            
        Returns:
            List of new releases
        """
        try:
            # Search for recent releases
            results = await self.search_music(
                query=genre,
                search_type="albums",
                location=location,
                sort="date"
            )
            
            # Filter for recent releases
            recent_releases = []
            for result in results[:20]:  # Limit to top 20
                if result['type'] == 'album':
                    album_info = await self.get_album_info(result['url'])
                    if album_info:
                        recent_releases.append({
                            'album': album_info,
                            'discovery_date': datetime.utcnow().isoformat(),
                            'genre': genre,
                            'location': location
                        })
            
            logger.info(f"Found {len(recent_releases)} recent releases for {genre}")
            return recent_releases
            
        except Exception as e:
            logger.error(f"Error monitoring independent releases: {e}")
            raise CrawlerError(f"Independent release monitoring failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up resources"""
        try:
            if self.session:
                await self.session.close()
            if self.driver:
                self.driver.quit()
            await super().cleanup()
            logger.info("Bandcamp engine cleanup completed")
        except Exception as e:
        try:
            logger.info(f"Executing __str__")
            
            # Implementation for __str__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__str__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__str__ failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __str__(self) -> str:
        return f"BandcampCrawlerEngine(platform=bandcamp)"
