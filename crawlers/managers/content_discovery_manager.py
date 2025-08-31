"""Content Discovery Manager
========================

Advanced content discovery engine for multi-platform crawling and content identification.
Manages intelligent content discovery across social media platforms and web services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import random
from urllib.parse import urljoin, urlparse

import aiohttp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

from ..utils.rate_limiter import RateLimiter
from ..utils.proxy_rotator import ProxyRotator
from ..config.discovery_config import DiscoveryConfig
from ...core.database import get_database_session
from ...core.logging import get_logger
from ...models.content import ContentDiscovery, ContentMetadata


class ContentType(Enum):
    """Content type enumeration for discovery targeting."""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"


class PlatformType(Enum):
    """Supported platform types for content discovery."""    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    GENERIC_WEB = "generic_web"


@dataclass
class DiscoveryTarget:
    """Content discovery target configuration."""    platform: PlatformType
    content_types: List[ContentType]
    keywords: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    usernames: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    date_range: Optional[Tuple[datetime, datetime]] = None
    max_results: int = 100
    priority: int = 1
    filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiscoveredContent:
    """Discovered content item with metadata."""    platform: PlatformType
    content_type: ContentType
    url: str
    title: str
    description: Optional[str]
    author: str
    author_url: Optional[str]
    thumbnail_url: Optional[str]
    duration: Optional[int]
    view_count: Optional[int]
    like_count: Optional[int]
    comment_count: Optional[int]
    publish_date: Optional[datetime]
    hashtags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    discovered_at: datetime = field(default_factory=datetime.utcnow)


class ContentDiscoveryManager:
    """    Advanced content discovery manager for multi-platform crawling.
    
    Provides intelligent content discovery, deduplication, and metadata extraction
    across multiple social media platforms and web services.
    """    
    def __init__(self, config: Optional[DiscoveryConfig] = None):
        """Initialize the content discovery manager."""        self.config = config or DiscoveryConfig()
        self.logger = get_logger(self.__class__.__name__)
        self.session = None
        self.driver = None
        self.rate_limiter = RateLimiter()
        self.proxy_rotator = ProxyRotator()
        
        # Discovery state
        self.discovered_content: Dict[str, DiscoveredContent] = {}
        self.discovered_urls: Set[str] = set()
        self.discovery_stats = {
            'total_discovered': 0,
            'by_platform': {},
            'by_content_type': {},
            'errors': 0,
            'duplicates_filtered': 0
        }
        
        # Platform handlers
        self.platform_handlers = {
            PlatformType.YOUTUBE: self._discover_youtube_content,
            PlatformType.TIKTOK: self._discover_tiktok_content,
            PlatformType.INSTAGRAM: self._discover_instagram_content,
            PlatformType.TWITTER: self._discover_twitter_content,
            PlatformType.SPOTIFY: self._discover_spotify_content,
            PlatformType.SOUNDCLOUD: self._discover_soundcloud_content,
            PlatformType.GENERIC_WEB: self._discover_web_content
        }
        
    async def __aenter__(self):
        """Async context manager entry."""        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""        await self.cleanup()
        
    async def initialize(self):
        """Initialize discovery manager resources."""        try:
            # Initialize HTTP session
            connector = aiohttp.TCPConnector(
                limit=self.config.MAX_CONCURRENT_REQUESTS,
                limit_per_host=self.config.MAX_REQUESTS_PER_HOST,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            timeout = aiohttp.ClientTimeout(total=self.config.REQUEST_TIMEOUT)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.config.DEFAULT_HEADERS
            )
            
            # Initialize Selenium driver if needed
            if self.config.USE_SELENIUM:
                await self._initialize_selenium_driver()
                
            self.logger.info("Content discovery manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize content discovery manager: {e}")
            raise
            
    async def _initialize_selenium_driver(self):
        """Initialize Selenium WebDriver for JavaScript-heavy sites."""        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'--user-agent={self.config.USER_AGENT}')
            
            if self.config.USE_PROXY:
                proxy = self.proxy_rotator.get_proxy()
                if proxy:
                    chrome_options.add_argument(f'--proxy-server={proxy}')
                    
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(self.config.SELENIUM_WAIT_TIME)
            
            self.logger.info("Selenium WebDriver initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Selenium driver: {e}")
            self.driver = None
            
    async def discover_content(self, targets: List[DiscoveryTarget]) -> List[DiscoveredContent]:
        """        Discover content across multiple platforms based on targets.
        
        Args:
            targets: List of discovery targets
            
        Returns:
            List of discovered content items
        """        discovered_items = []
        
        try:
            # Sort targets by priority
            sorted_targets = sorted(targets, key=lambda x: x.priority, reverse=True)
            
            # Process targets with concurrency control
            semaphore = asyncio.Semaphore(self.config.MAX_CONCURRENT_DISCOVERIES)
            
            async def process_target(target: DiscoveryTarget) -> List[DiscoveredContent]:
                async with semaphore:
                    return await self._discover_target_content(target)
                    
            # Execute discovery tasks
            tasks = [process_target(target) for target in sorted_targets]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Discovery failed for target {sorted_targets[i].platform}: {result}")
                    self.discovery_stats['errors'] += 1
                else:
                    discovered_items.extend(result)
                    
            # Remove duplicates
            unique_items = self._deduplicate_content(discovered_items)
            
            # Update statistics
            self._update_discovery_stats(unique_items)
            
            self.logger.info(f"Content discovery completed. Found {len(unique_items)} unique items from {len(targets)} targets")
            
            return unique_items
            
        except Exception as e:
            self.logger.error(f"Content discovery failed: {e}")
            raise
            
    async def _discover_target_content(self, target: DiscoveryTarget) -> List[DiscoveredContent]:
        """Discover content for a specific target."""        try:
            # Get platform handler
            handler = self.platform_handlers.get(target.platform)
            if not handler:
                self.logger.warning(f"No handler available for platform: {target.platform}")
                return []
                
            # Apply rate limiting
            await self.rate_limiter.wait_if_needed(target.platform.value)
            
            # Execute discovery
            content_items = await handler(target)
            
            # Filter and validate results
            validated_items = []
            for item in content_items:
                if self._validate_discovered_content(item, target):
                    validated_items.append(item)
                    
            self.logger.info(f"Discovered {len(validated_items)} items from {target.platform}")
            return validated_items
            
        except Exception as e:
            self.logger.error(f"Failed to discover content for {target.platform}: {e}")
            return []
            
    async def _discover_youtube_content(self, target: DiscoveryTarget) -> List[DiscoveredContent]:
        """Discover YouTube content using API and web scraping."""        content_items = []
        
        try:
            # Use YouTube Data API if available
            if self.config.YOUTUBE_API_KEY:
                api_items = await self._discover_youtube_api(target)
                content_items.extend(api_items)
                
            # Fallback to web scraping
            if len(content_items) < target.max_results and self.config.ENABLE_WEB_SCRAPING:
                scrape_items = await self._discover_youtube_scraping(target)
                content_items.extend(scrape_items)
                
        except Exception as e:
            self.logger.error(f"YouTube discovery error: {e}")
            
        return content_items[:target.max_results]
        
    async def _discover_youtube_api(self, target: DiscoveryTarget) -> List[DiscoveredContent]:
        """Discover YouTube content using official API."""        content_items = []
        
        try:
            base_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'key': self.config.YOUTUBE_API_KEY,
                'part': 'snippet',
                'maxResults': min(target.max_results, 50),
                'type': 'video',
                'order': 'relevance'
            }
            
            # Add search query
            if target.keywords:
                params['q'] = ' '.join(target.keywords)
            elif target.hashtags:
                params['q'] = ' '.join([f"#{tag}" for tag in target.hashtags])
                
            # Add date range filter
            if target.date_range:
                params['publishedAfter'] = target.date_range[0].isoformat() + 'Z'
                params['publishedBefore'] = target.date_range[1].isoformat() + 'Z'
                
            async with self.session.get(base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for item in data.get('items', []):
                        content = self._parse_youtube_api_item(item)
                        if content:
                            content_items.append(content)
                            
        except Exception as e:
            self.logger.error(f"YouTube API discovery error: {e}")
            
        return content_items
        
    async def _discover_youtube_scraping(self, target: DiscoveryTarget) -> List[DiscoveredContent]:
        """Discover YouTube content using web scraping."""        content_items = []
        
        if not self.driver:
            return content_items
            
        try:
            # Build search URL
            search_query = ' '.join(target.keywords + [f"#{tag}" for tag in target.hashtags])
            search_url = f"https://www.youtube.com/results?search_query={search_query}"
            
            self.driver.get(search_url)
            await asyncio.sleep(2)
            
            # Scroll to load more content
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                await asyncio.sleep(1)
                
            # Extract video elements
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div#contents ytd-video-renderer')
            
            for element in video_elements[:target.max_results]:
                try:
                    content = self._parse_youtube_element(element)
                    if content:
                        content_items.append(content)
                except Exception as e:
                    self.logger.debug(f"Failed to parse YouTube element: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"YouTube scraping error: {e}")
            
        return content_items
        
    async def _discover_tiktok_content(self, target: DiscoveryTarget) -> List[DiscoveredContent]:
        """Discover TikTok content using web scraping."""        content_items = []
        
        if not self.driver:
            return content_items
            
        try:
            # TikTok discovery logic
            search_query = ' '.join(target.keywords + target.hashtags)
            search_url = f"https://www.tiktok.com/search?q={search_query}"
            
            self.driver.get(search_url)
            await asyncio.sleep(3)
            
            # Handle TikTok's infinite scroll
            for _ in range(5):
                self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                await asyncio.sleep(2)
                
            # Extract video elements
            video_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-e2e="search_top-item"]')
            
            for element in video_elements[:target.max_results]:
                try:
                    content = self._parse_tiktok_element(element)
                    if content:
                        content_items.append(content)
                except Exception as e:
                    self.logger.debug(f"Failed to parse TikTok element: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"TikTok discovery error: {e}")
            
        return content_items
        
    async def _discover_instagram_content(self, target: DiscoveryTarget) -> List[DiscoveredContent]:
        """Discover Instagram content using web scraping."""        content_items = []
        
        # Instagram discovery implementation
        # Note: Instagram requires careful handling due to anti-bot measures
        
        return content_items
        
    async def _discover_twitter_content(self, target: DiscoveryTarget) -> List[DiscoveredContent]:
        """Discover Twitter/X content using API or scraping."""        content_items = []
        
        # Twitter discovery implementation
        # Note: May require Twitter API v2 or alternative methods
        
        return content_items
        
    async def _discover_spotify_content(self, target: DiscoveryTarget) -> List[DiscoveredContent]:
        """Discover Spotify content using Web API."""        content_items = []
        
        try:
            if not self.config.SPOTIFY_CLIENT_ID or not self.config.SPOTIFY_CLIENT_SECRET:
                self.logger.warning("Spotify credentials not configured")
                return content_items
                
            # Spotify discovery implementation using Web API
            # Implementation would go here
            
        except Exception as e:
            self.logger.error(f"Spotify discovery error: {e}")
            
        return content_items
        
    async def _discover_soundcloud_content(self, target: DiscoveryTarget) -> List[DiscoveredContent]:
        """Discover SoundCloud content using web scraping."""        content_items = []
        
        # SoundCloud discovery implementation
        
        return content_items
        
    async def _discover_web_content(self, target: DiscoveryTarget) -> List[DiscoveredContent]:
        """Discover content from generic web sources."""        content_items = []
        
        try:
            for url in target.urls:
                items = await self._crawl_website(url, target)
                content_items.extend(items)
                
        except Exception as e:
            self.logger.error(f"Web content discovery error: {e}")
            
        return content_items
        
    async def _crawl_website(self, url: str, target: DiscoveryTarget) -> List[DiscoveredContent]:
        """Crawl a website for content discovery."""        content_items = []
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract various content types
                    items = self._extract_content_from_html(soup, url, target)
                    content_items.extend(items)
                    
        except Exception as e:
            self.logger.error(f"Website crawling error for {url}: {e}")
            
        return content_items
        
    def _parse_youtube_api_item(self, item: Dict) -> Optional[DiscoveredContent]:
        """Parse YouTube API response item."""        try:
            snippet = item.get('snippet', {})
            video_id = item.get('id', {}).get('videoId')
            
            if not video_id:
                return None
                
            return DiscoveredContent(
                platform=PlatformType.YOUTUBE,
                content_type=ContentType.VIDEO,
                url=f"https://www.youtube.com/watch?v={video_id}",
                title=snippet.get('title', ''),
                description=snippet.get('description', ''),
                author=snippet.get('channelTitle', ''),
                author_url=f"https://www.youtube.com/channel/{snippet.get('channelId', '')}",
                thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url'),
                publish_date=datetime.fromisoformat(snippet.get('publishedAt', '').replace('Z', '+00:00')),
                metadata={
                    'video_id': video_id,
                    'channel_id': snippet.get('channelId'),
                    'category_id': snippet.get('categoryId'),
                    'default_language': snippet.get('defaultLanguage'),
                    'default_audio_language': snippet.get('defaultAudioLanguage')
                }
            )
            
        except Exception as e:
            self.logger.debug(f"Failed to parse YouTube API item: {e}")
            return None
            
    def _parse_youtube_element(self, element) -> Optional[DiscoveredContent]:
        """Parse YouTube web element."""        try:
            # Extract data from YouTube web element
            title_element = element.find_element(By.CSS_SELECTOR, 'a#video-title')
            url = title_element.get_attribute('href')
            title = title_element.get_attribute('title')
            
            # Extract additional metadata
            channel_element = element.find_element(By.CSS_SELECTOR, 'a.yt-simple-endpoint.style-scope.yt-formatted-string')
            author = channel_element.text
            author_url = channel_element.get_attribute('href')
            
            # Extract view count and other metadata
            metadata_elements = element.find_elements(By.CSS_SELECTOR, 'span.style-scope.ytd-video-meta-block')
            view_count = 0
            publish_date = None
            
            for meta in metadata_elements:
                text = meta.text
                if 'views' in text.lower():
                    view_count = self._parse_view_count(text)
                elif any(time_unit in text.lower() for time_unit in ['ago', 'day', 'week', 'month', 'year']):
                    publish_date = self._parse_relative_date(text)
                    
            return DiscoveredContent(
                platform=PlatformType.YOUTUBE,
                content_type=ContentType.VIDEO,
                url=url,
                title=title,
                description='',
                author=author,
                author_url=urljoin('https://www.youtube.com', author_url) if author_url else None,
                view_count=view_count,
                publish_date=publish_date,
                metadata={}
            )
            
        except Exception as e:
            self.logger.debug(f"Failed to parse YouTube element: {e}")
            return None
            
    def _parse_tiktok_element(self, element) -> Optional[DiscoveredContent]:
        """Parse TikTok web element."""        try:
            # Extract TikTok video data
            # Implementation would depend on TikTok's current DOM structure
            return None
            
        except Exception as e:
            self.logger.debug(f"Failed to parse TikTok element: {e}")
            return None
            
    def _extract_content_from_html(self, soup: BeautifulSoup, base_url: str, target: DiscoveryTarget) -> List[DiscoveredContent]:
        """Extract content from HTML using BeautifulSoup."""        content_items = []
        
        try:
            # Extract video content
            if ContentType.VIDEO in target.content_types:
                video_elements = soup.find_all(['video', 'iframe'])
                for element in video_elements:
                    content = self._parse_video_element(element, base_url)
                    if content:
                        content_items.append(content)
                        
            # Extract audio content
            if ContentType.AUDIO in target.content_types:
                audio_elements = soup.find_all('audio')
                for element in audio_elements:
                    content = self._parse_audio_element(element, base_url)
                    if content:
                        content_items.append(content)
                        
            # Extract image content
            if ContentType.IMAGE in target.content_types:
                img_elements = soup.find_all('img')
                for element in img_elements:
                    content = self._parse_image_element(element, base_url)
                    if content:
                        content_items.append(content)
                        
        except Exception as e:
            self.logger.error(f"Content extraction error: {e}")
            
        return content_items
        
    def _parse_video_element(self, element, base_url: str) -> Optional[DiscoveredContent]:
        """Parse video element from HTML."""        # Implementation for video parsing
        return None
        
    def _parse_audio_element(self, element, base_url: str) -> Optional[DiscoveredContent]:
        """Parse audio element from HTML."""        # Implementation for audio parsing
        return None
        
    def _parse_image_element(self, element, base_url: str) -> Optional[DiscoveredContent]:
        """Parse image element from HTML."""        # Implementation for image parsing
        return None
        
    def _validate_discovered_content(self, content: DiscoveredContent, target: DiscoveryTarget) -> bool:
        """Validate discovered content against target criteria."""        try:
            # Check content type
            if target.content_types and content.content_type not in target.content_types:
                return False
                
            # Check keywords
            if target.keywords:
                content_text = f"{content.title} {content.description}".lower()
                if not any(keyword.lower() in content_text for keyword in target.keywords):
                    return False
                    
            # Check hashtags
            if target.hashtags:
                content_hashtags = [tag.lower() for tag in content.hashtags]
                if not any(tag.lower() in content_hashtags for tag in target.hashtags):
                    # Also check in title and description
                    content_text = f"{content.title} {content.description}".lower()
                    if not any(f"#{tag.lower()}" in content_text for tag in target.hashtags):
                        return False
                        
            # Check date range
            if target.date_range and content.publish_date:
                if not (target.date_range[0] <= content.publish_date <= target.date_range[1]):
                    return False
                    
            # Apply custom filters
            for filter_key, filter_value in target.filters.items():
                if not self._apply_content_filter(content, filter_key, filter_value):
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.debug(f"Content validation error: {e}")
            return False
            
    def _apply_content_filter(self, content: DiscoveredContent, filter_key: str, filter_value: Any) -> bool:
        """Apply custom filter to content."""        try:
            if filter_key == 'min_views' and content.view_count is not None:
                return content.view_count >= filter_value
            elif filter_key == 'min_likes' and content.like_count is not None:
                return content.like_count >= filter_value
            elif filter_key == 'min_duration' and content.duration is not None:
                return content.duration >= filter_value
            elif filter_key == 'max_duration' and content.duration is not None:
                return content.duration <= filter_value
                
            return True
            
        except Exception:
            return True
            
    def _deduplicate_content(self, content_items: List[DiscoveredContent]) -> List[DiscoveredContent]:
        """Remove duplicate content items."""        unique_items = []
        seen_urls = set()
        seen_hashes = set()
        
        for item in content_items:
            # Check URL duplicates
            if item.url in seen_urls:
                self.discovery_stats['duplicates_filtered'] += 1
                continue
                
            # Check content hash duplicates
            content_hash = self._generate_content_hash(item)
            if content_hash in seen_hashes:
                self.discovery_stats['duplicates_filtered'] += 1
                continue
                
            seen_urls.add(item.url)
            seen_hashes.add(content_hash)
            unique_items.append(item)
            
        return unique_items
        
    def _generate_content_hash(self, content: DiscoveredContent) -> str:
        """Generate hash for content deduplication."""        content_string = f"{content.platform.value}:{content.title}:{content.author}:{content.url}"
        return hashlib.md5(content_string.encode()).hexdigest()
        
    def _parse_view_count(self, text: str) -> int:
        """Parse view count from text."""        try:
            # Remove non-numeric characters except for K, M, B
            clean_text = ''.join(c for c in text if c.isdigit() or c in 'KMB.,')
            
            # Extract number
            import re
            match = re.search(r'([\d.,]+)([KMB]?)', clean_text)
            if match:
                number_str, suffix = match.groups()
                number = float(number_str.replace(',', ''))
                
                if suffix == 'K':
                    return int(number * 1000)
                elif suffix == 'M':
                    return int(number * 1000000)
                elif suffix == 'B':
                    return int(number * 1000000000)
                else:
                    return int(number)
                    
        except Exception:
            pass
            
        return 0
        
    def _parse_relative_date(self, text: str) -> Optional[datetime]:
        """Parse relative date like '2 days ago'."""        try:
            import re
            
            # Common patterns for relative dates
            patterns = [
                (r'(\d+)\s+second[s]?\s+ago', lambda x: timedelta(seconds=int(x))),
                (r'(\d+)\s+minute[s]?\s+ago', lambda x: timedelta(minutes=int(x))),
                (r'(\d+)\s+hour[s]?\s+ago', lambda x: timedelta(hours=int(x))),
                (r'(\d+)\s+day[s]?\s+ago', lambda x: timedelta(days=int(x))),
                (r'(\d+)\s+week[s]?\s+ago', lambda x: timedelta(weeks=int(x))),
                (r'(\d+)\s+month[s]?\s+ago', lambda x: timedelta(days=int(x) * 30)),
                (r'(\d+)\s+year[s]?\s+ago', lambda x: timedelta(days=int(x) * 365))
            ]
            
            for pattern, delta_func in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    value = match.group(1)
                    delta = delta_func(value)
                    return datetime.utcnow() - delta
                    
        except Exception:
            pass
            
        return None
        
    def _update_discovery_stats(self, content_items: List[DiscoveredContent]):
        """Update discovery statistics."""        self.discovery_stats['total_discovered'] = len(content_items)
        
        # Count by platform
        for item in content_items:
            platform = item.platform.value
            self.discovery_stats['by_platform'][platform] = self.discovery_stats['by_platform'].get(platform, 0) + 1
            
            content_type = item.content_type.value
            self.discovery_stats['by_content_type'][content_type] = self.discovery_stats['by_content_type'].get(content_type, 0) + 1
            
    async def get_discovery_stats(self) -> Dict[str, Any]:
        """Get discovery statistics."""        return self.discovery_stats.copy()
        
    async def save_discovered_content(self, content_items: List[DiscoveredContent]) -> bool:
        """Save discovered content to database."""        try:
            async with get_database_session() as db:
                for item in content_items:
                    # Convert to database model
                    content_discovery = ContentDiscovery(
                        platform=item.platform.value,
                        content_type=item.content_type.value,
                        url=item.url,
                        title=item.title,
                        description=item.description,
                        author=item.author,
                        author_url=item.author_url,
                        thumbnail_url=item.thumbnail_url,
                        duration=item.duration,
                        view_count=item.view_count,
                        like_count=item.like_count,
                        comment_count=item.comment_count,
                        publish_date=item.publish_date,
                        hashtags=item.hashtags,
                        metadata=item.metadata,
                        confidence_score=item.confidence_score,
                        discovered_at=item.discovered_at
                    )
                    
                    db.add(content_discovery)
                    
                await db.commit()
                
            self.logger.info(f"Saved {len(content_items)} discovered content items to database")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save discovered content: {e}")
            return False
            
    async def cleanup(self):
        """Cleanup resources."""        try:
            if self.session:
                await self.session.close()
                
            if self.driver:
                self.driver.quit()
                
            self.logger.info("Content discovery manager cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")


# Factory function for easy instantiation
def create_content_discovery_manager(config: Optional[DiscoveryConfig] = None) -> ContentDiscoveryManager:
    """Create and return a content discovery manager instance."""    return ContentDiscoveryManager(config)


# Discovery utilities
async def discover_trending_content(platforms: List[PlatformType], content_types: List[ContentType], limit: int = 50) -> List[DiscoveredContent]:
    """Discover trending content across platforms."""    async with create_content_discovery_manager() as manager:
        targets = []
        for platform in platforms:
            target = DiscoveryTarget(
                platform=platform,
                content_types=content_types,
                keywords=['trending', 'viral', 'popular'],
                max_results=limit // len(platforms),
                priority=1
            )
            targets.append(target)
            
        return await manager.discover_content(targets)


async def discover_content_by_keywords(keywords: List[str], platforms: List[PlatformType], limit: int = 100) -> List[DiscoveredContent]:
    """Discover content by keywords across platforms."""    async with create_content_discovery_manager() as manager:
        targets = []
        for platform in platforms:
            target = DiscoveryTarget(
                platform=platform,
                content_types=list(ContentType),
                keywords=keywords,
                max_results=limit // len(platforms),
                priority=1
            )
            targets.append(target)
            
        return await manager.discover_content(targets)
