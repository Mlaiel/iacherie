"""Substack Crawling Engine
========================

Advanced Substack crawler for newsletter discovery, writer analytics, and publication monitoring.
Handles post metadata extraction, subscriber analysis, and content engagement tracking.

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
from ..models.content_models import ArticleContent, UserContent
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class SubstackPost:
    """Substack post data structure"""    id: str
    title: str
    subtitle: Optional[str]
    slug: str
    publication_id: str
    publication_name: str
    author_name: str
    author_id: str
    content: str
    content_preview: str
    post_date: datetime
    updated_date: Optional[datetime]
    url: str
    canonical_url: str
    is_paid_only: bool
    audience: str  # everyone, paid, founding
    type: str  # newsletter, podcast, thread
    word_count: int
    reading_time: int
    reactions: Dict[str, int]
    comment_count: int
    share_count: int
    cover_image: Optional[str]
    tags: List[str]
    section_id: Optional[str]
    section_name: Optional[str]
    email_sent_at: Optional[datetime]
    created_at: datetime


@dataclass
class SubstackPublication:
    """Substack publication data structure"""    id: str
    name: str
    subdomain: str
    custom_domain: Optional[str]
    description: Optional[str]
    author_name: str
    author_id: str
    logo_url: Optional[str]
    cover_photo_url: Optional[str]
    theme_color: Optional[str]
    subscriber_count: Optional[int]
    post_count: int
    founded_at: datetime
    language: str
    categories: List[str]
    is_paid: bool
    pricing_plans: List[Dict[str, Any]]
    social_links: Dict[str, str]
    url: str
    created_at: datetime


@dataclass
class SubstackWriter:
    """Substack writer data structure"""    id: str
    name: str
    bio: Optional[str]
    photo_url: Optional[str]
    publications: List[str]
    total_subscribers: Optional[int]
    twitter_username: Optional[str]
    website_url: Optional[str]
    is_stripe_connected: bool
    created_at: datetime


class SubstackCrawlerEngine(BaseCrawlerEngine):
    """    Professional Substack crawler engine for newsletter and publication analysis.
    
    Features:
    - Newsletter discovery and monitoring
    - Writer performance analytics
    - Publication growth tracking
    - Content engagement analysis
    - Subscription trend monitoring
    - Content protection monitoring
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Substack crawler engine"""        super().__init__(platform="substack", config=config)
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            requests_per_minute=40,
            requests_per_hour=2400
        )
        
        # Cache configuration
        self.cache_manager = CacheManager(
            cache_ttl=timedelta(hours=2),
            max_cache_size=3000
        )
        
        # Base URLs
        self.base_url = "https://substack.com"
        self.api_base = "https://substack.com/api/v1"
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Selenium for dynamic content
        self.driver: Optional[webdriver.Chrome] = None
        
        logger.info("Substack crawler engine initialized")
    
    async def initialize(self) -> None:
        """Initialize the crawler engine"""        try:
            await self._create_session()
            self._setup_selenium()
            logger.info("Substack engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Substack engine: {e}")
            raise CrawlerError(f"Initialization failed: {e}")
    
    async def _create_session(self) -> None:
        """Create HTTP session with proper headers"""        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://substack.com/',
            'Origin': 'https://substack.com'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=50)
        )
    
    def _setup_selenium(self) -> None:
        """Setup Selenium WebDriver"""        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=options)
            logger.info("Selenium WebDriver initialized for Substack")
        except Exception as e:
            logger.warning(f"Failed to initialize Selenium: {e}")
    
    async def discover_publications(
        self,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[SubstackPublication]:
        """        Discover popular publications on Substack
        
        Args:
            category: Filter by category
            limit: Number of publications to return
            
        Returns:
            List of Substack publications
        """        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"discover_publications:{category}:{limit}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use Selenium to browse discovery page
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            discover_url = f"{self.base_url}/discover"
            if category:
                discover_url += f"/{category}"
            
            self.driver.get(discover_url)
            
            publications = []
            try:
                # Wait for publications to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="publication-item"]'))
                )
                
                # Scroll to load more publications
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    await asyncio.sleep(2)
                
                # Find publication elements
                pub_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="publication-item"]')
                
                for pub_element in pub_elements[:limit]:
                    publication = self._parse_publication_element(pub_element)
                    if publication:
                        publications.append(publication)
                
                # Cache results
                await self.cache_manager.set(cache_key, publications)
                
                logger.info(f"Discovered {len(publications)} publications")
                return publications
                
            except TimeoutException:
                logger.warning("No publications found on discovery page")
                return []
                
        except Exception as e:
            logger.error(f"Error discovering publications: {e}")
            raise CrawlerError(f"Publication discovery failed: {e}")
    
    async def get_publication_details(self, subdomain: str) -> Optional[SubstackPublication]:
        """        Get detailed information about a publication
        
        Args:
            subdomain: Publication subdomain
            
        Returns:
            Publication details or None if not found
        """        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"publication_details:{subdomain}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use Selenium to load publication page
            if not self.driver:
                raise CrawlerError("Selenium driver not available")
            
            pub_url = f"https://{subdomain}.substack.com"
            self.driver.get(pub_url)
            
            try:
                # Wait for publication page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="publication-header"]'))
                )
                
                publication = self._parse_publication_page(subdomain)
                
                # Cache result
                await self.cache_manager.set(cache_key, publication)
                
                return publication
                
            except TimeoutException:
                raise ContentNotFoundError(f"Publication not found: {subdomain}")
                
        except Exception as e:
            logger.error(f"Error getting publication details: {e}")
            raise CrawlerError(f"Publication details retrieval failed: {e}")
    
    async def get_publication_posts(
        self,
        subdomain: str,
        limit: int = 20
    ) -> List[SubstackPost]:
        """        Get recent posts from a publication
        
        Args:
            subdomain: Publication subdomain
            limit: Number of posts to retrieve
            
        Returns:
            List of recent posts
        """        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"publication_posts:{subdomain}:{limit}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use API if available, otherwise Selenium
            posts = []
            
            try:
                # Try API first
                api_url = f"https://{subdomain}.substack.com/api/v1/posts"
                params = {'limit': min(limit, 50)}
                
                async with self.session.get(api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        for post_data in data.get('posts', []):
                            post = self._parse_post_data(post_data, subdomain)
                            posts.append(post)
                    else:
                        # Fallback to Selenium scraping
                        posts = await self._scrape_publication_posts(subdomain, limit)
                        
            except Exception:
                # Fallback to Selenium scraping
                posts = await self._scrape_publication_posts(subdomain, limit)
            
            # Cache results
            await self.cache_manager.set(cache_key, posts)
            
            logger.info(f"Retrieved {len(posts)} posts from {subdomain}")
            return posts
            
        except Exception as e:
            logger.error(f"Error getting publication posts: {e}")
            raise CrawlerError(f"Publication posts retrieval failed: {e}")
    
    async def _scrape_publication_posts(self, subdomain: str, limit: int) -> List[SubstackPost]:
        """Scrape publication posts using Selenium"""        if not self.driver:
            return []
        
        posts = []
        pub_url = f"https://{subdomain}.substack.com"
        self.driver.get(pub_url)
        
        try:
            # Wait for posts to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article'))
            )
            
            # Scroll to load more posts
            for _ in range(2):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            # Find post elements
            post_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article')
            
            for post_element in post_elements[:limit]:
                post = self._parse_post_element(post_element, subdomain)
                if post:
                    posts.append(post)
                    
        except TimeoutException:
            logger.warning(f"No posts found for {subdomain}")
        
        return posts
    
    def _parse_publication_element(self, pub_element) -> Optional[SubstackPublication]:
        """Parse publication element from discovery page"""        try:
            # Extract publication name
            name_elem = pub_element.find_element(By.CSS_SELECTOR, '.publication-name')
            name = name_elem.text if name_elem else ""
            
            # Extract subdomain from link
            link_elem = pub_element.find_element(By.CSS_SELECTOR, 'a')
            url = link_elem.get_attribute('href') if link_elem else ""
            subdomain = ""
            if url:
                parsed_url = urlparse(url)
                subdomain = parsed_url.hostname.split('.')[0] if parsed_url.hostname else ""
            
            # Extract description
            desc_elem = pub_element.find_element(By.CSS_SELECTOR, '.publication-description')
            description = desc_elem.text if desc_elem else None
            
            # Extract author name
            author_elem = pub_element.find_element(By.CSS_SELECTOR, '.author-name')
            author_name = author_elem.text if author_elem else ""
            
            return SubstackPublication(
                id=hashlib.md5(subdomain.encode()).hexdigest(),
                name=name,
                subdomain=subdomain,
                custom_domain=None,
                description=description,
                author_name=author_name,
                author_id=hashlib.md5(author_name.encode()).hexdigest(),
                logo_url=None,  # Extract if available
                cover_photo_url=None,  # Extract if available
                theme_color=None,
                subscriber_count=None,  # Not publicly visible
                post_count=0,  # Would need to count
                founded_at=datetime.utcnow(),  # Placeholder
                language="en",  # Default
                categories=[],  # Extract if available
                is_paid=False,  # Determine from pricing info
                pricing_plans=[],  # Extract if available
                social_links={},  # Extract if available
                url=url,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.warning(f"Error parsing publication element: {e}")
            return None
    
    def _parse_publication_page(self, subdomain: str) -> SubstackPublication:
        """Parse publication page data"""        # Implementation for parsing full publication page
        # This would extract all available publication metadata
        pass
    
    def _parse_post_data(self, post_data: Dict[str, Any], subdomain: str) -> SubstackPost:
        """Parse post data from API response"""        try:
            return SubstackPost(
                id=str(post_data.get('id', '')),
                title=post_data.get('title', ''),
                subtitle=post_data.get('subtitle'),
                slug=post_data.get('slug', ''),
                publication_id=subdomain,
                publication_name=subdomain,  # Would need publication details
                author_name=post_data.get('author', {}).get('name', ''),
                author_id=str(post_data.get('author', {}).get('id', '')),
                content=post_data.get('body_html', ''),
                content_preview=post_data.get('description', ''),
                post_date=datetime.fromisoformat(post_data.get('post_date', '').replace('Z', '+00:00')) if post_data.get('post_date') else datetime.utcnow(),
                updated_date=datetime.fromisoformat(post_data.get('updated_date', '').replace('Z', '+00:00')) if post_data.get('updated_date') else None,
                url=f"https://{subdomain}.substack.com/p/{post_data.get('slug', '')}",
                canonical_url=post_data.get('canonical_url', ''),
                is_paid_only=post_data.get('audience') != 'everyone',
                audience=post_data.get('audience', 'everyone'),
                type=post_data.get('type', 'newsletter'),
                word_count=len(post_data.get('body_html', '').split()) if post_data.get('body_html') else 0,
                reading_time=post_data.get('reading_time', 0),
                reactions=post_data.get('reactions', {}),
                comment_count=post_data.get('comment_count', 0),
                share_count=0,  # Not available in API
                cover_image=post_data.get('cover_image'),
                tags=post_data.get('tags', []),
                section_id=post_data.get('section', {}).get('id') if post_data.get('section') else None,
                section_name=post_data.get('section', {}).get('name') if post_data.get('section') else None,
                email_sent_at=datetime.fromisoformat(post_data.get('email_sent_at', '').replace('Z', '+00:00')) if post_data.get('email_sent_at') else None,
                created_at=datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error parsing post data: {e}")
            raise CrawlerError(f"Post data parsing failed: {e}")
    
    def _parse_post_element(self, post_element, subdomain: str) -> Optional[SubstackPost]:
        """Parse post element from page"""        # Implementation for parsing post elements from scraped page
        pass
    
    async def analyze_newsletter_trends(self) -> Dict[str, Any]:
        """        Analyze newsletter trends and growth patterns
        
        Returns:
            Newsletter trend analysis
        """        try:
            trend_analysis = {
                'top_categories': [],
                'growth_leaders': [],
                'engagement_patterns': {},
                'pricing_trends': {},
                'analysis_date': datetime.utcnow().isoformat()
            }
            
            # Discover publications across different categories
            categories = ['technology', 'business', 'politics', 'culture', 'health']
            
            for category in categories:
                publications = await self.discover_publications(category, limit=20)
                
                if publications:
                    trend_analysis['top_categories'].append({
                        'category': category,
                        'publication_count': len(publications),
                        'avg_posts_per_pub': sum(pub.post_count for pub in publications) / len(publications),
                        'paid_percentage': sum(1 for pub in publications if pub.is_paid) / len(publications) * 100
                    })
            
            logger.info("Newsletter trend analysis completed")
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing newsletter trends: {e}")
            raise CrawlerError(f"Newsletter trend analysis failed: {e}")
    
    async def monitor_content_distribution(
        self,
        content_title: str,
        author_name: str
    ) -> Dict[str, Any]:
        """        Monitor for unauthorized distribution of newsletter content
        
        Args:
            content_title: Title of the content to monitor
            author_name: Original author name
            
        Returns:
            Content distribution monitoring results
        """        try:
            monitoring_results = {
                'content_title': content_title,
                'original_author': author_name,
                'potential_redistributions': [],
                'monitoring_timestamp': datetime.utcnow().isoformat()
            }
            
            # Search for similar content across publications
            # This would require a more sophisticated search mechanism
            # For now, return the structure
            
            logger.info(f"Content distribution monitoring completed for {content_title}")
            return monitoring_results
            
        except Exception as e:
            logger.error(f"Error monitoring content distribution: {e}")
            raise CrawlerError(f"Content distribution monitoring failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up resources"""        try:
            if self.session:
                await self.session.close()
            if self.driver:
                self.driver.quit()
            await super().cleanup()
            logger.info("Substack engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __str__(self) -> str:
        return f"SubstackCrawlerEngine(platform=substack)"
