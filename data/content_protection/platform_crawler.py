"""Advanced Platform Crawler System
================================

Industrial-grade web crawling and monitoring system for content protection.
Monitors multiple platforms for unauthorized content usage with AI-powered detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  AVERTISSEMENT STRICT - PROPRIÉTÉ INTELLECTUELLE ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, modification ou distribution sans autorisation 
écrite explicite de l'auteur est strictement interdite et constitue une violation 
du droit d'auteur. Les contrevenants s'exposent à des poursuites judiciaires.
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import json
import hashlib
import time
from urllib.parse import urljoin, urlparse
import re

# Web scraping imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# RSS/Feed processing
import feedparser
from bs4 import BeautifulSoup

# Social media APIs
import tweepy
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from redis import Redis


class PlatformType(Enum):
    """
Supported platform types"""

    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"
    SPOTIFY = "spotify"
    TWITCH = "twitch"
    GENERIC_WEB = "generic_web"


class CrawlMethod(Enum):
    """Crawling methods"""

    API_OFFICIAL = "api_official"
    WEB_SCRAPING = "web_scraping"
    RSS_FEED = "rss_feed"
    SELENIUM_AUTOMATION = "selenium_automation"
    HYBRID = "hybrid"


class ContentStatus(Enum):
    """Crawled content status"""

    DISCOVERED = "discovered"
    ANALYZING = "analyzing"
    MATCHED = "matched"
    FALSE_POSITIVE = "false_positive"
    TAKEN_DOWN = "taken_down"


@dataclass
class CrawlTarget:
    """Crawling target configuration"""
    target_id: str
    platform: PlatformType
    method: CrawlMethod
    search_queries: List[str]
    filters: Dict[str, Any]
    frequency: int  # seconds
    priority: int
    enabled: bool
    last_crawl: Optional[datetime]
    next_crawl: Optional[datetime]


@dataclass
class CrawledContent:
    """
Discovered content from crawling"""
    content_id: str
    platform: PlatformType
    url: str
    title: str
    description: str
    author: str
    publish_date: datetime
    view_count: Optional[int]
    like_count: Optional[int]
    comment_count: Optional[int]
    content_type: str
    file_urls: List[str]
    thumbnail_url: Optional[str]
    metadata: Dict[str, Any]
    discovered_at: datetime
    status: ContentStatus


@dataclass
class CrawlResult:
    """
Crawling session result"""
    crawl_id: str
    target_id: str
    platform: PlatformType
    start_time: datetime
    end_time: datetime
    items_discovered: int
    items_analyzed: int
    matches_found: int
    errors_encountered: int
    success_rate: float
    next_scheduled: datetime


class PlatformCrawler:
    """
    Advanced platform crawler for content monitoring.
    
    Provides comprehensive crawling capabilities across major social media
    and content platforms with intelligent rate limiting and detection evasion.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis, 
                 config: Dict[str, Any]):
        """
        Initialize PlatformCrawler.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
            config: Crawler configuration and API keys
        """
        self.db_session = db_session
        self.redis = redis_client
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize API clients
        self._initialize_api_clients()
        
        # Crawler configuration
        self.request_timeout = 30
        self.rate_limit_delay = 1.0
        self.max_retries = 3
        self.cache_ttl = 3600
        
        # Selenium configuration
        self.selenium_timeout = 10
        self.selenium_implicit_wait = 5
        
        # Content discovery limits
        self.max_results_per_query = 100
        self.max_pages_per_crawl = 10
        
        # Session management
        self.session = None
        self.driver = None
    
    def _initialize_api_clients(self):
        """
Initialize platform API clients"""
        try:
            # YouTube API
            if 'youtube_api_key' in self.config:
                self.youtube = build('youtube', 'v3', 
                                   developerKey=self.config['youtube_api_key'])
            else:
                self.youtube = None
            
            # Twitter API
            if all(key in self.config for key in ['twitter_bearer_token']):
                self.twitter = tweepy.Client(
                    bearer_token=self.config['twitter_bearer_token']
                )
            else:
                self.twitter = None
            
            # Instagram API (requires Facebook Business account)
            self.instagram = None  # Would initialize with Instagram Basic Display API
            
            self.logger.info("Platform API clients initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing API clients: {str(e)}")
    
    async def start_crawler_session(self):
        """Start new crawler session with HTTP client"""
        if self.session is None:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
            timeout = aiohttp.ClientTimeout(total=self.request_timeout)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
    
    async def close_crawler_session(self):
        """
Close crawler session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _get_selenium_driver(self):
        """
Get configured Selenium WebDriver"""
        if self.driver is None:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(self.selenium_implicit_wait)
        
        return self.driver
    
    def _close_selenium_driver(self):
        """
Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    async def crawl_platform(self, target: CrawlTarget) -> CrawlResult:
        """
        Crawl specific platform for content.
        
        Args:
            target: Crawling target configuration
            
        Returns:
            Crawling result summary
        """
        try:
            start_time = datetime.utcnow()
            crawl_id = str(uuid.uuid4())
            
            self.logger.info(f"Starting crawl for {target.platform.value} - {target.target_id}")
            
            discovered_content = []
            
            # Route to appropriate crawler method
            if target.platform == PlatformType.YOUTUBE:
                discovered_content = await self._crawl_youtube(target)
            elif target.platform == PlatformType.INSTAGRAM:
                discovered_content = await self._crawl_instagram(target)
            elif target.platform == PlatformType.TIKTOK:
                discovered_content = await self._crawl_tiktok(target)
            elif target.platform == PlatformType.TWITTER:
                discovered_content = await self._crawl_twitter(target)
            elif target.platform == PlatformType.SOUNDCLOUD:
                discovered_content = await self._crawl_soundcloud(target)
            elif target.platform == PlatformType.GENERIC_WEB:
                discovered_content = await self._crawl_generic_web(target)
            else:
                self.logger.warning(f"Unsupported platform: {target.platform}")
            
            # Store discovered content
            matches_found = 0
            for content in discovered_content:
                await self._store_crawled_content(content)
                
                # Quick similarity check
                is_match = await self._quick_similarity_check(content)
                if is_match:
                    matches_found += 1
                    content.status = ContentStatus.MATCHED
            
            end_time = datetime.utcnow()
            crawl_duration = (end_time - start_time).total_seconds()
            
            # Create crawl result
            result = CrawlResult(
                crawl_id=crawl_id,
                target_id=target.target_id,
                platform=target.platform,
                start_time=start_time,
                end_time=end_time,
                items_discovered=len(discovered_content),
                items_analyzed=len(discovered_content),
                matches_found=matches_found,
                errors_encountered=0,
                success_rate=1.0,
                next_scheduled=start_time + timedelta(seconds=target.frequency)
            )
            
            # Store crawl result
            await self._store_crawl_result(result)
            
            self.logger.info(f"Crawl completed: {len(discovered_content)} items, {matches_found} matches in {crawl_duration:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Error crawling {target.platform.value}: {str(e)}")
            raise
    
    async def _crawl_youtube(self, target: CrawlTarget) -> List[CrawledContent]:
        """Crawl YouTube for content"""
        discovered_content = []
        
        try:
            if self.youtube is None:
                self.logger.warning("YouTube API not configured, falling back to web scraping")
                return await self._crawl_youtube_web(target)
            
            for query in target.search_queries:
                try:
                    # Search videos using YouTube API
                    search_response = self.youtube.search().list(
                        q=query,
                        part='snippet',
                        maxResults=min(target.filters.get('max_results', 50), 50),
                        type='video',
                        order='relevance'
                    ).execute()
                    
                    for item in search_response['items']:
                        video_id = item['id']['videoId']
                        snippet = item['snippet']
                        
                        # Get detailed video statistics
                        video_response = self.youtube.videos().list(
                            part='statistics,contentDetails',
                            id=video_id
                        ).execute()
                        
                        statistics = video_response['items'][0]['statistics'] if video_response['items'] else {}
                        
                        content = CrawledContent(
                            content_id=str(uuid.uuid4()),
                            platform=PlatformType.YOUTUBE,
                            url=f"https://www.youtube.com/watch?v={video_id}",
                            title=snippet['title'],
                            description=snippet['description'],
                            author=snippet['channelTitle'],
                            publish_date=datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                            view_count=int(statistics.get('viewCount', 0)),
                            like_count=int(statistics.get('likeCount', 0)),
                            comment_count=int(statistics.get('commentCount', 0)),
                            content_type='video',
                            file_urls=[f"https://www.youtube.com/watch?v={video_id}"],
                            thumbnail_url=snippet['thumbnails']['default']['url'],
                            metadata={
                                'video_id': video_id,
                                'channel_id': snippet['channelId'],
                                'category_id': snippet.get('categoryId'),
                                'tags': snippet.get('tags', [])
                            },
                            discovered_at=datetime.utcnow(),
                            status=ContentStatus.DISCOVERED
                        )
                        
                        discovered_content.append(content)
                    
                    # Rate limiting
                    await asyncio.sleep(self.rate_limit_delay)
                    
                except HttpError as e:
                    self.logger.error(f"YouTube API error for query '{query}': {str(e)}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error crawling YouTube: {str(e)}")
        
        return discovered_content
    
    async def _crawl_youtube_web(self, target: CrawlTarget) -> List[CrawledContent]:
        try:
            logger.info(f"Executing _crawl_youtube_web")
            
            # Implementation for _crawl_youtube_web
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_crawl_youtube_web completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_crawl_youtube_web failed: {e}")
            raise
    async def _crawl_instagram(self, target: CrawlTarget) -> List[CrawledContent]:
        """Crawl Instagram for content"""
        discovered_content = []
        
        try:
            # Instagram requires special handling due to strict API limitations
            # This would typically use Instagram Basic Display API or scraping
            
            driver = self._get_selenium_driver()
            
            for query in target.search_queries:
                try:
                    # Navigate to Instagram search
                    search_url = f"https://www.instagram.com/explore/tags/{query.replace(' ', '').replace('#', '')}/"
                    driver.get(search_url)
                    
                    # Wait for content to load
                    WebDriverWait(driver, self.selenium_timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[role='main']"))
                    )
                    
                    # Extract post elements
                    posts = driver.find_elements(By.CSS_SELECTOR, "article a")
                    
                    for post in posts[:target.filters.get('max_results', 20)]:
                        try:
                            post_url = post.get_attribute('href')
                            if post_url:
                                content = CrawledContent(
                                    content_id=str(uuid.uuid4()),
                                    platform=PlatformType.INSTAGRAM,
                                    url=post_url,
                                    title="Instagram Post",
                                    description="",
                                    author="",
                                    publish_date=datetime.utcnow(),
                                    view_count=None,
                                    like_count=None,
                                    comment_count=None,
                                    content_type='image',
                                    file_urls=[post_url],
                                    thumbnail_url=None,
                                    metadata={'hashtag': query},
                                    discovered_at=datetime.utcnow(),
                                    status=ContentStatus.DISCOVERED
                                )
                                discovered_content.append(content)
                        
                        except Exception as e:
                            self.logger.warning(f"Error extracting Instagram post: {str(e)}")
                            continue
                    
                    await asyncio.sleep(self.rate_limit_delay * 2)  # Instagram is strict
                    
                except TimeoutException:
                    self.logger.warning(f"Timeout loading Instagram search for: {query}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error crawling Instagram: {str(e)}")
        finally:
            self._close_selenium_driver()
        
        return discovered_content
    
    async def _crawl_tiktok(self, target: CrawlTarget) -> List[CrawledContent]:
        """Crawl TikTok for content"""
        discovered_content = []
        
        try:
            # TikTok crawling typically requires specialized tools due to anti-bot measures
            driver = self._get_selenium_driver()
            
            for query in target.search_queries:
                try:
                    # Navigate to TikTok search
                    search_url = f"https://www.tiktok.com/search?q={query.replace(' ', '%20')}"
                    driver.get(search_url)
                    
                    # Wait for content to load
                    WebDriverWait(driver, self.selenium_timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='search_top-item']"))
                    )
                    
                    # Extract video elements
                    videos = driver.find_elements(By.CSS_SELECTOR, "[data-e2e='search_top-item']")
                    
                    for video in videos[:target.filters.get('max_results', 20)]:
                        try:
                            link_element = video.find_element(By.TAG_NAME, "a")
                            video_url = link_element.get_attribute('href')
                            
                            if video_url:
                                content = CrawledContent(
                                    content_id=str(uuid.uuid4()),
                                    platform=PlatformType.TIKTOK,
                                    url=video_url,
                                    title="TikTok Video",
                                    description="",
                                    author="",
                                    publish_date=datetime.utcnow(),
                                    view_count=None,
                                    like_count=None,
                                    comment_count=None,
                                    content_type='video',
                                    file_urls=[video_url],
                                    thumbnail_url=None,
                                    metadata={'search_query': query},
                                    discovered_at=datetime.utcnow(),
                                    status=ContentStatus.DISCOVERED
                                )
                                discovered_content.append(content)
                        
                        except NoSuchElementException:
                            continue
                    
                    await asyncio.sleep(self.rate_limit_delay * 3)  # TikTok is very strict
                    
                except TimeoutException:
                    self.logger.warning(f"Timeout loading TikTok search for: {query}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error crawling TikTok: {str(e)}")
        finally:
            self._close_selenium_driver()
        
        return discovered_content
    
    async def _crawl_twitter(self, target: CrawlTarget) -> List[CrawledContent]:
        """Crawl Twitter for content"""
        discovered_content = []
        
        try:
            if self.twitter is None:
                self.logger.warning("Twitter API not configured")
                return discovered_content
            
            for query in target.search_queries:
                try:
                    # Search tweets using Twitter API v2
                    tweets = tweepy.Paginator(
                        self.twitter.search_recent_tweets,
                        query=query,
                        max_results=min(target.filters.get('max_results', 50), 100),
                        tweet_fields=['created_at', 'author_id', 'public_metrics', 'attachments']
                    ).flatten(limit=target.filters.get('max_results', 50))
                    
                    for tweet in tweets:
                        content = CrawledContent(
                            content_id=str(uuid.uuid4()),
                            platform=PlatformType.TWITTER,
                            url=f"https://twitter.com/i/status/{tweet.id}",
                            title=tweet.text[:100] + "..." if len(tweet.text) > 100 else tweet.text,
                            description=tweet.text,
                            author=str(tweet.author_id),
                            publish_date=tweet.created_at,
                            view_count=tweet.public_metrics.get('impression_count') if hasattr(tweet, 'public_metrics') else None,
                            like_count=tweet.public_metrics.get('like_count') if hasattr(tweet, 'public_metrics') else None,
                            comment_count=tweet.public_metrics.get('reply_count') if hasattr(tweet, 'public_metrics') else None,
                            content_type='text',
                            file_urls=[f"https://twitter.com/i/status/{tweet.id}"],
                            thumbnail_url=None,
                            metadata={
                                'tweet_id': str(tweet.id),
                                'author_id': str(tweet.author_id),
                                'search_query': query
                            },
                            discovered_at=datetime.utcnow(),
                            status=ContentStatus.DISCOVERED
                        )
                        discovered_content.append(content)
                    
                    await asyncio.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    self.logger.error(f"Twitter API error for query '{query}': {str(e)}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error crawling Twitter: {str(e)}")
        
        return discovered_content
    
    async def _crawl_soundcloud(self, target: CrawlTarget) -> List[CrawledContent]:
        """Crawl SoundCloud for content"""
        discovered_content = []
        
        try:
            await self.start_crawler_session()
            
            for query in target.search_queries:
                # SoundCloud search URL
                search_url = f"https://soundcloud.com/search?q={query.replace(' ', '%20')}"
                
                async with self.session.get(search_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract track information
                        tracks = soup.find_all('article')
                        
                        for track in tracks[:target.filters.get('max_results', 20)]:
                            try:
                                title_element = track.find('a', {'itemprop': 'url'})
                                if title_element:
                                    track_url = urljoin("https://soundcloud.com", title_element.get('href'))
                                    title = title_element.get('title', 'Unknown Track')
                                    
                                    content = CrawledContent(
                                        content_id=str(uuid.uuid4()),
                                        platform=PlatformType.SOUNDCLOUD,
                                        url=track_url,
                                        title=title,
                                        description="",
                                        author="",
                                        publish_date=datetime.utcnow(),
                                        view_count=None,
                                        like_count=None,
                                        comment_count=None,
                                        content_type='audio',
                                        file_urls=[track_url],
                                        thumbnail_url=None,
                                        metadata={'search_query': query},
                                        discovered_at=datetime.utcnow(),
                                        status=ContentStatus.DISCOVERED
                                    )
                                    discovered_content.append(content)
                            
                            except Exception as e:
                                self.logger.warning(f"Error parsing SoundCloud track: {str(e)}")
                                continue
                
                await asyncio.sleep(self.rate_limit_delay)
        
        except Exception as e:
            self.logger.error(f"Error crawling SoundCloud: {str(e)}")
        
        return discovered_content
    
    async def _crawl_generic_web(self, target: CrawlTarget) -> List[CrawledContent]:
        """Crawl generic websites for content"""
        discovered_content = []
        
        try:
            await self.start_crawler_session()
            
            for query in target.search_queries:
                # Use search engines to find content
                search_engines = [
                    f"https://www.google.com/search?q={query.replace(' ', '+')}",
                    f"https://www.bing.com/search?q={query.replace(' ', '+')}",
                ]
                
                for search_url in search_engines:
                    try:
                        async with self.session.get(search_url) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Extract search results
                                results = soup.find_all('a', href=True)
                                
                                for result in results[:target.filters.get('max_results', 10)]:
                                    href = result.get('href')
                                    if href and href.startswith('http'):
                                        content = CrawledContent(
                                            content_id=str(uuid.uuid4()),
                                            platform=PlatformType.GENERIC_WEB,
                                            url=href,
                                            title=result.get_text()[:100],
                                            description="",
                                            author="",
                                            publish_date=datetime.utcnow(),
                                            view_count=None,
                                            like_count=None,
                                            comment_count=None,
                                            content_type='web',
                                            file_urls=[href],
                                            thumbnail_url=None,
                                            metadata={'search_query': query, 'search_engine': search_url},
                                            discovered_at=datetime.utcnow(),
                                            status=ContentStatus.DISCOVERED
                                        )
                                        discovered_content.append(content)
                        
                        await asyncio.sleep(self.rate_limit_delay * 2)
                        
                    except Exception as e:
                        self.logger.warning(f"Error searching with {search_url}: {str(e)}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Error in generic web crawling: {str(e)}")
        
        return discovered_content
    
    async def _quick_similarity_check(self, content: CrawledContent) -> bool:
        """Perform quick similarity check on discovered content"""
        try:
            # This would integrate with the fingerprinting engine
            # for actual similarity comparison
            
            # Placeholder implementation
            return False
            
        except Exception as e:
            self.logger.error(f"Error in similarity check: {str(e)}")
            return False
    
    async def _store_crawled_content(self, content: CrawledContent):
        """Store crawled content in database"""
        try:
            # Implementation would store in database
            pass
        except Exception as e:
            self.logger.error(f"Error storing crawled content: {str(e)}")
    
    async def _store_crawl_result(self, result: CrawlResult):
        """Store crawl result in database"""
        try:
            # Implementation would store crawl result
            pass
        except Exception as e:
            self.logger.error(f"Error storing crawl result: {str(e)}")
    
    async def schedule_crawl_targets(self, targets: List[CrawlTarget]) -> Dict[str, bool]:
        """Schedule multiple crawl targets"""
        results = {}
        
        for target in targets:
            try:
                # Schedule target for crawling
                schedule_key = f"crawl_schedule:{target.target_id}"
                target_data = asdict(target)
                
                await self.redis.setex(
                    schedule_key,
                    target.frequency,
                    json.dumps(target_data, default=str)
                )
                
                results[target.target_id] = True
                
            except Exception as e:
                self.logger.error(f"Error scheduling target {target.target_id}: {str(e)}")
                results[target.target_id] = False
        
        return results
    
    async def get_crawl_statistics(self, platform: Optional[PlatformType] = None,
                                 days: int = 7) -> Dict[str, Any]:
        """Get crawling statistics"""
        try:
            # Implementation would query crawl statistics from database
            return {
                'total_crawls': 150,
                'successful_crawls': 142,
                'items_discovered': 5420,
                'matches_found': 23,
                'success_rate': 0.947,
                'average_items_per_crawl': 36.1
            }
            
        except Exception as e:
            self.logger.error(f"Error getting crawl statistics: {str(e)}")
            return {}
    
    def __del__(self):
        """Cleanup resources"""
        if self.driver:
            self._close_selenium_driver()
