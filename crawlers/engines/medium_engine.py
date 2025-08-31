"""Medium Crawling Engine
======================

Advanced Medium crawler for article discovery, author analytics, and publication monitoring.
Handles article metadata extraction, author analysis, and content engagement tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.
"""import asyncio
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
from ..models.content_models import ArticleContent, UserContent
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class MediumArticle:
    """Medium article data structure"""    id: str
    title: str
    subtitle: Optional[str]
    author_id: str
    author_name: str
    author_username: str
    publication_id: Optional[str]
    publication_name: Optional[str]
    content: str
    content_preview: str
    reading_time: int
    published_at: datetime
    updated_at: Optional[datetime]
    url: str
    canonical_url: Optional[str]
    tags: List[str]
    topics: List[str]
    clap_count: int
    response_count: int
    voter_count: int
    is_locked: bool
    is_series: bool
    series_id: Optional[str]
    word_count: int
    image_count: int
    language: str
    license: str
    created_at: datetime


@dataclass
class MediumAuthor:
    """Medium author data structure"""    id: str
    username: str
    name: str
    bio: Optional[str]
    image_url: Optional[str]
    follower_count: int
    following_count: int
    is_writer_program_enrolled: bool
    is_suspended: bool
    top_writer_in: List[str]
    twitter_username: Optional[str]
    facebook_username: Optional[str]
    linkedin_url: Optional[str]
    website_url: Optional[str]
    joined_at: datetime
    last_post_at: Optional[datetime]
    total_posts: int
    total_responses: int
    url: str
    created_at: datetime


@dataclass
class MediumPublication:
    """Medium publication data structure"""    id: str
    name: str
    slug: str
    description: Optional[str]
    creator_id: str
    image_url: Optional[str]
    follower_count: int
    post_count: int
    tags: List[str]
    domain: Optional[str]
    newsletter_enabled: bool
    is_accepting_submissions: bool
    created_at: datetime
    url: str


@dataclass
class MediumResponse:
    """Medium response/comment data structure"""    id: str
    content: str
    author_id: str
    author_name: str
    parent_id: Optional[str]
    post_id: str
    created_at: datetime
    clap_count: int
    is_featured: bool


class MediumCrawlerEngine(BaseCrawlerEngine):
    """    Professional Medium crawler engine for content and author analytics.
    
    Features:
    - Article discovery and analysis
    - Author performance metrics
    - Publication monitoring
    - Content engagement tracking
    - Topic trend analysis
    - Content protection monitoring
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Medium crawler engine"""        super().__init__(platform="medium", config=config)
        
        # Rate limiting (conservative due to anti-bot measures)
        self.rate_limiter = RateLimiter(
            requests_per_minute=30,
            requests_per_hour=1800
        )
        
        # Cache configuration
        self.cache_manager = CacheManager(
            cache_ttl=timedelta(hours=1),
            max_cache_size=5000
        )
        
        # Base URLs
        self.base_url = "https://medium.com"
        self.api_base = "https://medium.com/_/api"
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Selenium driver for dynamic content
        self.driver: Optional[webdriver.Chrome] = None
        
        logger.info("Medium crawler engine initialized")
    
    async def initialize(self) -> None:
        """Initialize the crawler engine"""        try:
            await self._create_session()
            self._setup_selenium()
            logger.info("Medium engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Medium engine: {e}")
            raise CrawlerError(f"Initialization failed: {e}")
    
    async def _create_session(self) -> None:
        """Create HTTP session with proper headers"""        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://medium.com/',
            'Origin': 'https://medium.com'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=50)
        )
    
    def _setup_selenium(self) -> None:
        """Setup Selenium WebDriver for dynamic content"""        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("Selenium WebDriver initialized for Medium")
        except Exception as e:
            logger.warning(f"Failed to initialize Selenium: {e}")
    
    async def search_articles(
        self,
        query: str,
        limit: int = 50
    ) -> List[MediumArticle]:
        """        Search for articles on Medium
        
        Args:
            query: Search query
            limit: Number of articles to return
            
        Returns:
            List of articles matching the query
        """        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"search_articles:{hashlib.md5(f'{query}:{limit}'.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use Selenium for search since Medium's search is heavily JS-based
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            search_url = f"{self.base_url}/search?q={query}"
            self.driver.get(search_url)
            
            articles = []
            try:
                # Wait for search results to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="search-results"]'))
                )
                
                # Find article elements
                article_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article')
                
                for article_element in article_elements[:limit]:
                    article = self._parse_article_element(article_element)
                    if article:
                        articles.append(article)
                
                # Cache results
                await self.cache_manager.set(cache_key, articles)
                
                logger.info(f"Found {len(articles)} articles for query: {query}")
                return articles
                
            except TimeoutException:
                logger.warning(f"Search results not found for query: {query}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            raise CrawlerError(f"Article search failed: {e}")
    
    async def get_article_details(self, article_url: str) -> Optional[MediumArticle]:
        """        Get detailed information about a specific article
        
        Args:
            article_url: Medium article URL
            
        Returns:
            Article details or None if not found
        """        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"article_details:{hashlib.md5(article_url.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use Selenium to load the article
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            self.driver.get(article_url)
            
            try:
                # Wait for article to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "article"))
                )
                
                article = self._parse_article_page()
                
                # Cache result
                await self.cache_manager.set(cache_key, article)
                
                return article
                
            except TimeoutException:
                raise ContentNotFoundError(f"Article not found: {article_url}")
                
        except Exception as e:
            logger.error(f"Error getting article details: {e}")
            raise CrawlerError(f"Article details retrieval failed: {e}")
    
    async def get_author_profile(self, username: str) -> Optional[MediumAuthor]:
        """        Get author profile information
        
        Args:
            username: Medium username (with or without @)
            
        Returns:
            Author profile data or None if not found
        """        try:
            await self.rate_limiter.acquire()
            
            # Clean username
            username = username.lstrip('@')
            
            # Check cache
            cache_key = f"author_profile:{username}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use Selenium to load profile
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            profile_url = f"{self.base_url}/@{username}"
            self.driver.get(profile_url)
            
            try:
                # Wait for profile to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="user-profile"]'))
                )
                
                author = self._parse_author_profile()
                
                # Cache result
                await self.cache_manager.set(cache_key, author)
                
                return author
                
            except TimeoutException:
                raise ContentNotFoundError(f"Author profile not found: {username}")
                
        except Exception as e:
            logger.error(f"Error getting author profile: {e}")
            raise CrawlerError(f"Author profile retrieval failed: {e}")
    
    async def get_author_articles(
        self,
        username: str,
        limit: int = 50
    ) -> List[MediumArticle]:
        """        Get articles by a specific author
        
        Args:
            username: Medium username
            limit: Number of articles to retrieve
            
        Returns:
            List of author's articles
        """        try:
            await self.rate_limiter.acquire()
            
            # Clean username
            username = username.lstrip('@')
            
            # Check cache
            cache_key = f"author_articles:{username}:{limit}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use Selenium to load author's articles
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            profile_url = f"{self.base_url}/@{username}"
            self.driver.get(profile_url)
            
            articles = []
            try:
                # Wait for articles to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'article'))
                )
                
                # Scroll to load more articles
                for _ in range(3):  # Scroll 3 times to load more content
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    await asyncio.sleep(2)
                
                # Find article elements
                article_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article')
                
                for article_element in article_elements[:limit]:
                    article = self._parse_article_element(article_element)
                    if article:
                        articles.append(article)
                
                # Cache results
                await self.cache_manager.set(cache_key, articles)
                
                logger.info(f"Found {len(articles)} articles for author: {username}")
                return articles
                
            except TimeoutException:
                logger.warning(f"No articles found for author: {username}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting author articles: {e}")
            raise CrawlerError(f"Author articles retrieval failed: {e}")
    
    async def get_publication_info(self, publication_slug: str) -> Optional[MediumPublication]:
        """        Get publication information
        
        Args:
            publication_slug: Publication slug
            
        Returns:
            Publication information or None if not found
        """        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"publication_info:{publication_slug}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use Selenium to load publication
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            pub_url = f"{self.base_url}/{publication_slug}"
            self.driver.get(pub_url)
            
            try:
                # Wait for publication page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="publication-header"]'))
                )
                
                publication = self._parse_publication_page()
                
                # Cache result
                await self.cache_manager.set(cache_key, publication)
                
                return publication
                
            except TimeoutException:
                raise ContentNotFoundError(f"Publication not found: {publication_slug}")
                
        except Exception as e:
            logger.error(f"Error getting publication info: {e}")
            raise CrawlerError(f"Publication info retrieval failed: {e}")
    
    def _parse_article_element(self, article_element) -> Optional[MediumArticle]:
        """Parse article element from page"""        try:
            # Extract title
            title_elem = article_element.find_element(By.CSS_SELECTOR, 'h2, h3')
            title = title_elem.text if title_elem else ""
            
            # Extract author info
            author_elem = article_element.find_element(By.CSS_SELECTOR, '[data-testid="author-name"]')
            author_name = author_elem.text if author_elem else ""
            
            # Extract reading time
            reading_time_elem = article_element.find_element(By.CSS_SELECTOR, '[data-testid="reading-time"]')
            reading_time_text = reading_time_elem.text if reading_time_elem else "0 min read"
            reading_time = int(re.search(r'\d+', reading_time_text).group()) if re.search(r'\d+', reading_time_text) else 0
            
            # Extract URL
            link_elem = article_element.find_element(By.CSS_SELECTOR, 'a[href*="/"]')
            article_url = link_elem.get_attribute('href') if link_elem else ""
            
            # Extract clap count (if visible)
            clap_elem = article_element.find_element(By.CSS_SELECTOR, '[data-testid="clap-count"]')
            clap_count = 0
            if clap_elem:
                clap_text = clap_elem.text
                clap_count = int(re.search(r'\d+', clap_text).group()) if re.search(r'\d+', clap_text) else 0
            
            return MediumArticle(
                id=hashlib.md5(article_url.encode()).hexdigest(),
                title=title,
                subtitle=None,  # Extract if available
                author_id=hashlib.md5(author_name.encode()).hexdigest(),
                author_name=author_name,
                author_username="",  # Extract if available
                publication_id=None,
                publication_name=None,
                content="",  # Would need full page load
                content_preview="",  # Extract preview if available
                reading_time=reading_time,
                published_at=datetime.utcnow(),  # Would need to parse actual date
                updated_at=None,
                url=article_url,
                canonical_url=None,
                tags=[],  # Extract if available
                topics=[],  # Extract if available
                clap_count=clap_count,
                response_count=0,  # Extract if available
                voter_count=0,  # Extract if available
                is_locked=False,  # Determine from paywall indicators
                is_series=False,  # Extract if available
                series_id=None,
                word_count=0,  # Would need full content
                image_count=0,  # Count images if available
                language="en",  # Default
                license="",  # Extract if available
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.warning(f"Error parsing article element: {e}")
            return None
    
    def _parse_article_page(self) -> MediumArticle:
        """Parse full article page"""        # Implementation for parsing complete article page
        # This would extract all available article metadata and content
        pass
    
    def _parse_author_profile(self) -> MediumAuthor:
        """Parse author profile page"""        # Implementation for parsing author profile page
        # This would extract all available author data
        pass
    
    def _parse_publication_page(self) -> MediumPublication:
        """Parse publication page"""        # Implementation for parsing publication page
        # This would extract all available publication data
        pass
    
    async def analyze_trending_topics(self) -> List[Dict[str, Any]]:
        """        Analyze trending topics on Medium
        
        Returns:
            List of trending topics with metadata
        """        try:
            trending_data = []
            
            # Use Selenium to access trending page
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            trending_url = f"{self.base_url}/topic/popular"
            self.driver.get(trending_url)
            
            try:
                # Wait for trending content to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="trending-topics"]'))
                )
                
                # Extract trending topics
                topic_elements = self.driver.find_elements(By.CSS_SELECTOR, '.topic-item')
                
                for topic_elem in topic_elements:
                    topic_name = topic_elem.find_element(By.CSS_SELECTOR, '.topic-name').text
                    follower_count_elem = topic_elem.find_element(By.CSS_SELECTOR, '.follower-count')
                    follower_count = int(re.search(r'\d+', follower_count_elem.text).group()) if follower_count_elem else 0
                    
                    trending_data.append({
                        'topic': topic_name,
                        'follower_count': follower_count,
                        'platform': 'medium',
                        'detected_at': datetime.utcnow().isoformat()
                    })
                
            except TimeoutException:
                logger.warning("Trending topics not found")
            
            logger.info(f"Analyzed {len(trending_data)} trending topics")
            return trending_data
            
        except Exception as e:
            logger.error(f"Error analyzing trending topics: {e}")
            raise CrawlerError(f"Trending topics analysis failed: {e}")
    
    async def monitor_content_plagiarism(
        self,
        content_snippet: str,
        author_name: str
    ) -> Dict[str, Any]:
        """        Monitor for potential plagiarism of content
        
        Args:
            content_snippet: Text snippet to search for
            author_name: Original author name
            
        Returns:
            Plagiarism monitoring results
        """        try:
            plagiarism_results = {
                'original_author': author_name,
                'content_snippet': content_snippet[:100] + "...",
                'potential_matches': [],
                'monitoring_timestamp': datetime.utcnow().isoformat()
            }
            
            # Search for the content snippet
            search_results = await self.search_articles(content_snippet, limit=20)
            
            for article in search_results:
                # Check if it's not by the original author
                if article.author_name.lower() != author_name.lower():
                    # Calculate similarity (simplified)
                    similarity_score = self._calculate_content_similarity(
                        content_snippet,
                        article.content_preview
                    )
                    
                    if similarity_score > 0.7:  # High similarity threshold
                        plagiarism_results['potential_matches'].append({
                            'article_title': article.title,
                            'article_url': article.url,
                            'author_name': article.author_name,
                            'similarity_score': similarity_score,
                            'published_at': article.published_at.isoformat()
                        })
            
            logger.info(f"Plagiarism monitoring completed. Found {len(plagiarism_results['potential_matches'])} potential matches")
            return plagiarism_results
            
        except Exception as e:
            logger.error(f"Error monitoring content plagiarism: {e}")
            raise CrawlerError(f"Content plagiarism monitoring failed: {e}")
    
    def _calculate_content_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text snippets"""        # Simple word-based similarity calculation
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def cleanup(self) -> None:
        """Clean up resources"""        try:
            if self.session:
                await self.session.close()
            if self.driver:
                self.driver.quit()
            await super().cleanup()
            logger.info("Medium engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __str__(self) -> str:
        return f"MediumCrawlerEngine(platform=medium)"
