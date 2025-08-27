"""
Substack Crawler
================

Professional Substack content crawler with advanced monitoring capabilities.
Implements Substack RSS/API integration with intelligent rate limiting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import re
from urllib.parse import urljoin, urlparse

import aiohttp
import feedparser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..utils.rate_limiter import SubstackRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError
from ...database.models import CrawlResult, ContentMatch

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class SubstackPost:
    """Substack post data structure."""
    post_id: str
    title: str
    subtitle: str
    content: str
    excerpt: str
    author_name: str
    author_id: str
    publication_name: str
    publication_id: str
    published_at: datetime
    updated_at: Optional[datetime]
    url: str
    slug: str
    word_count: int
    reading_time_minutes: int
    is_paid: bool
    is_free: bool
    like_count: int
    comment_count: int
    share_count: int
    view_count: int
    subscriber_count: int
    tags: List[str]
    category: str
    cover_image_url: Optional[str]
    audio_url: Optional[str]
    podcast_duration: Optional[int]
    email_subject: Optional[str]
    reactions: Dict[str, int]
    cross_posts: List[str]

@dataclass
class SubstackPublication:
    """Substack publication data structure."""
    publication_id: str
    name: str
    subdomain: str
    custom_domain: Optional[str]
    description: str
    author_name: str
    author_bio: str
    founded_at: datetime
    subscriber_count: int
    post_count: int
    is_paid: bool
    is_free: bool
    pricing_monthly: Optional[float]
    pricing_yearly: Optional[float]
    categories: List[str]
    logo_url: Optional[str]
    cover_image_url: Optional[str]
    about_page_url: str
    rss_url: str
    language: str
    country: str
    social_links: Dict[str, str]
    top_posts: List[str]

@dataclass
class SubstackAuthor:
    """Substack author data structure."""
    author_id: str
    name: str
    bio: str
    photo_url: Optional[str]
    publication_ids: List[str]
    total_subscribers: int
    total_posts: int
    joined_at: datetime
    verified: bool
    twitter_handle: Optional[str]
    website_url: Optional[str]
    location: Optional[str]
    specialties: List[str]

class SubstackCrawler:
    """
    Professional Substack crawler implementation.
    
    Features:
    - RSS feed parsing for public content
    - Publication discovery and monitoring
    - Author profile analysis
    - Content similarity detection
    - Engagement metrics tracking
    - Newsletter subscription tracking
    - Paid content detection
    - Cross-platform content monitoring
    - Trending posts discovery
    - Publication analytics
    """
    
    def __init__(self):
        """Initialize Substack crawler."""
        self.rate_limiter = SubstackRateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.session = None
        
        # Base URLs
        self.base_url = "https://substack.com"
        self.api_base_url = "https://substack.com/api/v1"
        
        # Common headers
        self.headers = {
            'User-Agent': self.user_agent_rotator.get_user_agent(),
            'Accept': 'application/json, text/html, application/xhtml+xml, application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Selenium configuration
        self.selenium_options = webdriver.ChromeOptions()
        self.selenium_options.add_argument('--headless')
        self.selenium_options.add_argument('--no-sandbox')
        self.selenium_options.add_argument('--disable-dev-shm-usage')
        self.selenium_options.add_argument('--disable-gpu')
        self.selenium_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Content patterns
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def discover_publications(
        self,
        search_query: Optional[str] = None,
        category: Optional[str] = None,
        min_subscribers: int = 0,
        max_results: int = 50
    ) -> List[SubstackPublication]:
        """
        Discover Substack publications.
        
        Args:
            search_query: Search term for publications
            category: Filter by category (e.g., 'technology', 'politics', 'culture')
            min_subscribers: Minimum subscriber count
            max_results: Maximum number of publications to return
            
        Returns:
            List of Substack publication objects
        """
        try:
            await self.rate_limiter.wait_if_needed()
            
            publications = []
            
            # Try multiple discovery methods
            if search_query:
                search_results = await self._search_publications(search_query, max_results)
                publications.extend(search_results)
            
            # Discover from featured/trending
            if len(publications) < max_results:
                trending_results = await self._get_trending_publications(max_results - len(publications))
                publications.extend(trending_results)
            
            # Filter by criteria
            filtered_publications = []
            for pub in publications:
                if min_subscribers > 0 and pub.subscriber_count < min_subscribers:
                    continue
                if category and category.lower() not in [cat.lower() for cat in pub.categories]:
                    continue
                filtered_publications.append(pub)
            
            return filtered_publications[:max_results]
            
        except Exception as e:
            logger.error(f"Publication discovery failed: {e}")
            return []
    
    async def _search_publications(self, query: str, max_results: int) -> List[SubstackPublication]:
        """Search for publications using Substack search."""
        try:
            search_url = f"{self.base_url}/discover/search"
            params = {
                'query': query,
                'type': 'publication'
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                publications = []
                
                # Parse search results
                publication_elements = soup.find_all('div', class_='publication-card')
                
                for element in publication_elements[:max_results]:
                    try:
                        publication = await self._parse_publication_element(element)
                        if publication:
                            publications.append(publication)
                    except Exception as e:
                        logger.warning(f"Failed to parse publication element: {e}")
                        continue
                
                return publications
                
        except Exception as e:
            logger.error(f"Publication search failed: {e}")
            return []
    
    async def _get_trending_publications(self, max_results: int) -> List[SubstackPublication]:
        """Get trending/featured publications."""
        try:
            trending_url = f"{self.base_url}/discover"
            
            async with self.session.get(trending_url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                publications = []
                
                # Look for featured publications
                featured_sections = soup.find_all('section', class_=['featured', 'trending', 'recommended'])
                
                for section in featured_sections:
                    pub_elements = section.find_all('div', class_='publication-card')
                    
                    for element in pub_elements:
                        if len(publications) >= max_results:
                            break
                        
                        try:
                            publication = await self._parse_publication_element(element)
                            if publication:
                                publications.append(publication)
                        except:
                            continue
                
                return publications[:max_results]
                
        except Exception as e:
            logger.error(f"Trending publications fetch failed: {e}")
            return []
    
    async def _parse_publication_element(self, element) -> Optional[SubstackPublication]:
        """Parse publication data from HTML element."""
        try:
            # Extract basic information
            name_elem = element.find('h3') or element.find('h2') or element.find('.publication-name')
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            # Extract subdomain from link
            link_elem = element.find('a', href=True)
            subdomain = ""
            custom_domain = None
            
            if link_elem:
                href = link_elem['href']
                parsed_url = urlparse(href)
                if 'substack.com' in parsed_url.netloc:
                    subdomain = parsed_url.netloc.split('.')[0]
                else:
                    custom_domain = parsed_url.netloc
                    subdomain = name.lower().replace(' ', '-')
            
            # Extract description
            desc_elem = element.find('p', class_='description') or element.find('.publication-description')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract author
            author_elem = element.find('.author-name') or element.find('.by-author')
            author_name = author_elem.get_text(strip=True) if author_elem else ""
            
            # Extract subscriber count (if visible)
            subscriber_elem = element.find('.subscriber-count') or element.find('.subscribers')
            subscriber_text = subscriber_elem.get_text(strip=True) if subscriber_elem else "0"
            subscriber_count = self._parse_count_text(subscriber_text)
            
            publication_id = f"{subdomain}_substack"
            
            return SubstackPublication(
                publication_id=publication_id,
                name=name,
                subdomain=subdomain,
                custom_domain=custom_domain,
                description=description,
                author_name=author_name,
                author_bio="",
                founded_at=datetime.now(),  # Would need additional API call
                subscriber_count=subscriber_count,
                post_count=0,  # Would need additional API call
                is_paid=False,  # Would need to check pricing page
                is_free=True,
                pricing_monthly=None,
                pricing_yearly=None,
                categories=[],  # Would need content analysis
                logo_url=None,
                cover_image_url=None,
                about_page_url=f"https://{subdomain}.substack.com/about",
                rss_url=f"https://{subdomain}.substack.com/feed",
                language="en",
                country="",
                social_links={},
                top_posts=[]
            )
            
        except Exception as e:
            logger.error(f"Failed to parse publication element: {e}")
            return None
    
    def _parse_count_text(self, count_text: str) -> int:
        """Parse subscriber count text like '1.2K' or '5M'."""
        try:
            count_text = count_text.lower().replace(',', '').strip()
            
            if 'k' in count_text:
                return int(float(count_text.replace('k', '')) * 1000)
            elif 'm' in count_text:
                return int(float(count_text.replace('m', '')) * 1000000)
            else:
                # Extract just numbers
                numbers = re.findall(r'\d+', count_text)
                return int(numbers[0]) if numbers else 0
                
        except:
            return 0
    
    async def get_publication_posts(
        self,
        subdomain: str,
        max_posts: int = 50,
        include_paid: bool = False
    ) -> List[SubstackPost]:
        """
        Get posts from a Substack publication.
        
        Args:
            subdomain: Publication subdomain (e.g., 'newsletter' for newsletter.substack.com)
            max_posts: Maximum number of posts to retrieve
            include_paid: Whether to include paid content
            
        Returns:
            List of Substack post objects
        """
        try:
            await self.rate_limiter.wait_if_needed()
            
            # First try RSS feed (most reliable for public content)
            rss_posts = await self._get_posts_from_rss(subdomain, max_posts)
            
            if len(rss_posts) < max_posts:
                # Supplement with web scraping if needed
                scraped_posts = await self._scrape_publication_posts(
                    subdomain, 
                    max_posts - len(rss_posts),
                    include_paid
                )
                rss_posts.extend(scraped_posts)
            
            # Remove duplicates
            seen_urls = set()
            unique_posts = []
            for post in rss_posts:
                if post.url not in seen_urls:
                    unique_posts.append(post)
                    seen_urls.add(post.url)
            
            return unique_posts[:max_posts]
            
        except Exception as e:
            logger.error(f"Failed to get posts for {subdomain}: {e}")
            return []
    
    async def _get_posts_from_rss(self, subdomain: str, max_posts: int) -> List[SubstackPost]:
        """Get posts from RSS feed."""
        try:
            rss_url = f"https://{subdomain}.substack.com/feed"
            
            async with self.session.get(rss_url) as response:
                if response.status != 200:
                    return []
                
                rss_content = await response.text()
                feed = feedparser.parse(rss_content)
                
                posts = []
                
                for entry in feed.entries[:max_posts]:
                    try:
                        post = await self._parse_rss_entry(entry, subdomain)
                        if post:
                            posts.append(post)
                    except Exception as e:
                        logger.warning(f"Failed to parse RSS entry: {e}")
                        continue
                
                return posts
                
        except Exception as e:
            logger.error(f"RSS parsing failed for {subdomain}: {e}")
            return []
    
    async def _parse_rss_entry(self, entry, subdomain: str) -> Optional[SubstackPost]:
        """Parse RSS entry into SubstackPost object."""
        try:
            # Extract basic information
            title = entry.get('title', '')
            link = entry.get('link', '')
            content = entry.get('description', '') or entry.get('summary', '')
            author = entry.get('author', '')
            
            # Parse publication date
            published_at = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_at = datetime(*entry.updated_parsed[:6])
            
            # Extract post ID from URL
            post_id = link.split('/')[-1] if link else f"{subdomain}_{title[:50]}"
            
            # Clean content and extract text
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text(strip=True)
            
            # Calculate reading time (average 200 words per minute)
            word_count = len(text_content.split())
            reading_time = max(1, word_count // 200)
            
            # Extract slug from URL
            slug = link.split('/')[-1] if '/' in link else title.lower().replace(' ', '-')
            
            return SubstackPost(
                post_id=post_id,
                title=title,
                subtitle="",
                content=text_content,
                excerpt=text_content[:200] + "..." if len(text_content) > 200 else text_content,
                author_name=author,
                author_id=f"{subdomain}_author",
                publication_name=subdomain,
                publication_id=f"{subdomain}_substack",
                published_at=published_at,
                updated_at=None,
                url=link,
                slug=slug,
                word_count=word_count,
                reading_time_minutes=reading_time,
                is_paid=False,  # RSS usually only shows free content
                is_free=True,
                like_count=0,  # Not available in RSS
                comment_count=0,
                share_count=0,
                view_count=0,
                subscriber_count=0,
                tags=[],
                category="",
                cover_image_url=None,
                audio_url=None,
                podcast_duration=None,
                email_subject=title,
                reactions={},
                cross_posts=[]
            )
            
        except Exception as e:
            logger.error(f"Failed to parse RSS entry: {e}")
            return None
    
    async def _scrape_publication_posts(
        self,
        subdomain: str,
        max_posts: int,
        include_paid: bool
    ) -> List[SubstackPost]:
        """Scrape publication posts using Selenium."""
        try:
            driver = webdriver.Chrome(options=self.selenium_options)
            publication_url = f"https://{subdomain}.substack.com"
            driver.get(publication_url)
            
            await asyncio.sleep(3)
            
            posts = []
            scroll_count = 0
            max_scrolls = max_posts // 10 + 2
            
            while len(posts) < max_posts and scroll_count < max_scrolls:
                # Find post elements
                post_elements = driver.find_elements(By.CSS_SELECTOR, ".post-preview")
                
                for element in post_elements:
                    if len(posts) >= max_posts:
                        break
                    
                    try:
                        post = await self._extract_post_from_element(element, subdomain)
                        if post and (include_paid or post.is_free):
                            posts.append(post)
                    except Exception as e:
                        logger.warning(f"Failed to extract post: {e}")
                        continue
                
                # Scroll to load more posts
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                scroll_count += 1
            
            driver.quit()
            return posts[:max_posts]
            
        except Exception as e:
            logger.error(f"Post scraping failed for {subdomain}: {e}")
            if 'driver' in locals():
                driver.quit()
            return []
    
    async def _extract_post_from_element(self, element, subdomain: str) -> Optional[SubstackPost]:
        """Extract post data from DOM element."""
        try:
            # Extract title
            title_elem = element.find_element(By.CSS_SELECTOR, "h2, h3, .post-title")
            title = title_elem.text.strip() if title_elem else ""
            
            # Extract URL
            link_elem = element.find_element(By.CSS_SELECTOR, "a")
            url = link_elem.get_attribute("href") if link_elem else ""
            
            # Extract excerpt
            excerpt_elem = element.find_element(By.CSS_SELECTOR, ".post-preview-content, .excerpt")
            excerpt = excerpt_elem.text.strip() if excerpt_elem else ""
            
            # Check if paid content
            is_paid = bool(element.find_elements(By.CSS_SELECTOR, ".paywall-marker, .paid-content"))
            
            # Extract publication date
            date_elem = element.find_element(By.CSS_SELECTOR, ".post-date, .published-date")
            date_text = date_elem.text.strip() if date_elem else ""
            published_at = self._parse_date_text(date_text)
            
            post_id = url.split('/')[-1] if url else f"{subdomain}_{title[:50]}"
            
            return SubstackPost(
                post_id=post_id,
                title=title,
                subtitle="",
                content=excerpt,
                excerpt=excerpt,
                author_name="",
                author_id=f"{subdomain}_author",
                publication_name=subdomain,
                publication_id=f"{subdomain}_substack",
                published_at=published_at,
                updated_at=None,
                url=url,
                slug=url.split('/')[-1] if url else "",
                word_count=len(excerpt.split()),
                reading_time_minutes=max(1, len(excerpt.split()) // 200),
                is_paid=is_paid,
                is_free=not is_paid,
                like_count=0,
                comment_count=0,
                share_count=0,
                view_count=0,
                subscriber_count=0,
                tags=[],
                category="",
                cover_image_url=None,
                audio_url=None,
                podcast_duration=None,
                email_subject=title,
                reactions={},
                cross_posts=[]
            )
            
        except Exception as e:
            logger.warning(f"Failed to extract post from element: {e}")
            return None
    
    def _parse_date_text(self, date_text: str) -> datetime:
        """Parse date text into datetime object."""
        try:
            # Handle common Substack date formats
            if 'ago' in date_text.lower():
                # Handle relative dates like "2 days ago"
                if 'hour' in date_text:
                    hours = int(re.findall(r'\d+', date_text)[0])
                    return datetime.now() - timedelta(hours=hours)
                elif 'day' in date_text:
                    days = int(re.findall(r'\d+', date_text)[0])
                    return datetime.now() - timedelta(days=days)
                elif 'week' in date_text:
                    weeks = int(re.findall(r'\d+', date_text)[0])
                    return datetime.now() - timedelta(weeks=weeks)
                elif 'month' in date_text:
                    months = int(re.findall(r'\d+', date_text)[0])
                    return datetime.now() - timedelta(days=months * 30)
            
            # Handle absolute dates (would need more sophisticated parsing)
            return datetime.now()
            
        except:
            return datetime.now()
    
    async def monitor_publication(
        self,
        subdomain: str,
        check_interval: int = 1800,  # 30 minutes
        max_posts_per_check: int = 10
    ) -> AsyncGenerator[List[SubstackPost], None]:
        """
        Monitor publication for new posts.
        
        Args:
            subdomain: Publication subdomain to monitor
            check_interval: Check interval in seconds
            max_posts_per_check: Maximum posts to check per interval
            
        Yields:
            Lists of new posts
        """
        last_check = datetime.now()
        seen_posts = set()
        
        while True:
            try:
                # Get recent posts
                recent_posts = await self.get_publication_posts(
                    subdomain, 
                    max_posts_per_check
                )
                
                # Filter new posts
                new_posts = []
                for post in recent_posts:
                    if (post.post_id not in seen_posts and 
                        post.published_at > last_check):
                        new_posts.append(post)
                        seen_posts.add(post.post_id)
                
                if new_posts:
                    yield new_posts
                
                last_check = datetime.now()
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Publication monitoring error for {subdomain}: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def search_content(
        self,
        query: str,
        max_results: int = 100,
        content_type: str = 'all',  # 'all', 'free', 'paid'
        date_range: Optional[tuple] = None
    ) -> List[SubstackPost]:
        """
        Search Substack content across publications.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            content_type: Filter by content type
            date_range: (start_date, end_date) tuple
            
        Returns:
            List of matching posts
        """
        try:
            search_results = []
            
            # Use multiple search strategies
            strategies = [
                self._search_via_google_site_search,
                self._search_via_substack_discover,
                self._search_via_rss_aggregation
            ]
            
            for strategy in strategies:
                if len(search_results) >= max_results:
                    break
                
                try:
                    results = await strategy(query, max_results - len(search_results))
                    search_results.extend(results)
                except Exception as e:
                    logger.warning(f"Search strategy failed: {e}")
                    continue
            
            # Filter by criteria
            filtered_results = []
            for post in search_results:
                # Content type filter
                if content_type == 'free' and not post.is_free:
                    continue
                elif content_type == 'paid' and not post.is_paid:
                    continue
                
                # Date range filter
                if date_range:
                    start_date, end_date = date_range
                    if not (start_date <= post.published_at <= end_date):
                        continue
                
                filtered_results.append(post)
            
            # Remove duplicates
            unique_results = []
            seen_urls = set()
            for post in filtered_results:
                if post.url not in seen_urls:
                    unique_results.append(post)
                    seen_urls.add(post.url)
            
            return unique_results[:max_results]
            
        except Exception as e:
            logger.error(f"Content search failed: {e}")
            return []
    
    async def _search_via_google_site_search(self, query: str, max_results: int) -> List[SubstackPost]:
        """Search using Google site:substack.com search."""
        try:
            # This would require Google Search API or web scraping
            # Placeholder implementation
            logger.info(f"Google site search for: {query}")
            return []
            
        except Exception as e:
            logger.error(f"Google site search failed: {e}")
            return []
    
    async def _search_via_substack_discover(self, query: str, max_results: int) -> List[SubstackPost]:
        """Search using Substack's discover page."""
        try:
            search_url = f"{self.base_url}/discover/search"
            params = {
                'query': query,
                'type': 'post'
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Parse search results
                posts = []
                post_elements = soup.find_all('div', class_='post-preview')
                
                for element in post_elements[:max_results]:
                    try:
                        # Extract subdomain from element
                        link = element.find('a', href=True)
                        if link:
                            url = link['href']
                            subdomain = urlparse(url).netloc.split('.')[0]
                            
                            post = await self._extract_post_from_element(element, subdomain)
                            if post:
                                posts.append(post)
                    except:
                        continue
                
                return posts
                
        except Exception as e:
            logger.error(f"Substack discover search failed: {e}")
            return []
    
    async def _search_via_rss_aggregation(self, query: str, max_results: int) -> List[SubstackPost]:
        """Search by aggregating RSS feeds."""
        try:
            # This would involve maintaining a list of known publications
            # and searching their RSS feeds
            logger.info(f"RSS aggregation search for: {query}")
            return []
            
        except Exception as e:
            logger.error(f"RSS aggregation search failed: {e}")
            return []
    
    async def analyze_content_similarity(
        self,
        reference_post: SubstackPost,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Find posts similar to a reference post.
        
        Args:
            reference_post: Post to find similarities for
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar posts with similarity scores
        """
        try:
            similar_posts = []
            
            # Extract keywords from reference post
            keywords = self._extract_content_keywords(reference_post.content)
            
            # Search for potentially similar content
            for keyword_set in keywords[:3]:
                query = " ".join(keyword_set)
                search_results = await self.search_content(query, max_results=30)
                
                for post in search_results:
                    if post.post_id == reference_post.post_id:
                        continue
                    
                    similarity = self._calculate_content_similarity(reference_post, post)
                    
                    if similarity >= similarity_threshold:
                        similar_posts.append({
                            'post': post,
                            'similarity_score': similarity,
                            'match_factors': self._get_similarity_factors(reference_post, post)
                        })
            
            # Remove duplicates and sort
            unique_posts = {}
            for match in similar_posts:
                post_id = match['post'].post_id
                if post_id not in unique_posts or match['similarity_score'] > unique_posts[post_id]['similarity_score']:
                    unique_posts[post_id] = match
            
            return sorted(unique_posts.values(), key=lambda x: x['similarity_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Content similarity analysis failed: {e}")
            return []
    
    def _extract_content_keywords(self, content: str) -> List[List[str]]:
        """Extract important keywords from content."""
        try:
            # Simple keyword extraction (could be enhanced with NLP)
            words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
            
            # Filter common words
            stop_words = {
                'this', 'that', 'with', 'have', 'will', 'from', 'they', 'know',
                'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when',
                'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over',
                'such', 'take', 'than', 'them', 'well', 'were'
            }
            
            keywords = [word for word in words if word not in stop_words]
            
            # Create keyword combinations
            keyword_sets = []
            if len(keywords) >= 3:
                keyword_sets.append(keywords[:3])
            if len(keywords) >= 5:
                keyword_sets.append(keywords[1:4])
            if keywords:
                keyword_sets.append([keywords[0]])
            
            return keyword_sets
            
        except:
            return []
    
    def _calculate_content_similarity(self, post1: SubstackPost, post2: SubstackPost) -> float:
        """Calculate similarity score between two posts."""
        try:
            # Title similarity
            title1_words = set(post1.title.lower().split())
            title2_words = set(post2.title.lower().split())
            title_similarity = len(title1_words & title2_words) / len(title1_words | title2_words) if title1_words | title2_words else 0
            
            # Content similarity (first 500 chars)
            content1_words = set(post1.content[:500].lower().split())
            content2_words = set(post2.content[:500].lower().split())
            content_similarity = len(content1_words & content2_words) / len(content1_words | content2_words) if content1_words | content2_words else 0
            
            # Author similarity
            author_similarity = 1.0 if post1.author_name == post2.author_name else 0.0
            
            # Publication similarity
            pub_similarity = 1.0 if post1.publication_id == post2.publication_id else 0.0
            
            # Time proximity
            time_diff = abs((post1.published_at - post2.published_at).total_seconds())
            time_similarity = max(0, 1 - (time_diff / (7 * 24 * 3600)))  # 7 days max
            
            # Word count similarity
            if post1.word_count > 0 and post2.word_count > 0:
                word_diff = abs(post1.word_count - post2.word_count)
                word_similarity = max(0, 1 - (word_diff / max(post1.word_count, post2.word_count)))
            else:
                word_similarity = 0.0
            
            # Weighted average
            weights = {
                'title': 0.3,
                'content': 0.4,
                'author': 0.1,
                'publication': 0.1,
                'time': 0.05,
                'word_count': 0.05
            }
            
            similarity = (
                weights['title'] * title_similarity +
                weights['content'] * content_similarity +
                weights['author'] * author_similarity +
                weights['publication'] * pub_similarity +
                weights['time'] * time_similarity +
                weights['word_count'] * word_similarity
            )
            
            return similarity
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def _get_similarity_factors(self, post1: SubstackPost, post2: SubstackPost) -> List[str]:
        """Get factors contributing to similarity."""
        factors = []
        
        if post1.author_name == post2.author_name:
            factors.append('same_author')
        
        if post1.publication_id == post2.publication_id:
            factors.append('same_publication')
        
        # Check title overlap
        title1_words = set(post1.title.lower().split())
        title2_words = set(post2.title.lower().split())
        common_title_words = title1_words & title2_words
        if len(common_title_words) > 2:
            factors.append('similar_title')
        
        # Check content overlap
        content1_words = set(post1.content.lower().split())
        content2_words = set(post2.content.lower().split())
        if len(content1_words & content2_words) > 10:
            factors.append('similar_content')
        
        # Check publication time proximity
        time_diff = abs((post1.published_at - post2.published_at).total_seconds())
        if time_diff < 24 * 3600:  # Same day
            factors.append('published_same_day')
        elif time_diff < 7 * 24 * 3600:  # Same week
            factors.append('published_same_week')
        
        return factors
    
    async def get_publication_analytics(self, subdomain: str) -> Dict:
        """
        Get analytics for a Substack publication.
        
        Args:
            subdomain: Publication subdomain
            
        Returns:
            Analytics dictionary
        """
        try:
            # Get recent posts for analysis
            posts = await self.get_publication_posts(subdomain, max_posts=100)
            
            if not posts:
                return {}
            
            # Calculate metrics
            total_posts = len(posts)
            avg_word_count = sum(post.word_count for post in posts) / total_posts
            avg_reading_time = sum(post.reading_time_minutes for post in posts) / total_posts
            
            # Publishing frequency
            if len(posts) > 1:
                date_range = (max(post.published_at for post in posts) - 
                             min(post.published_at for post in posts)).days
                posting_frequency = total_posts / max(date_range, 1) if date_range > 0 else 0
            else:
                posting_frequency = 0
            
            # Content categories (basic keyword analysis)
            all_content = " ".join(post.content for post in posts)
            common_keywords = self._extract_content_keywords(all_content)
            
            # Free vs paid content ratio
            free_posts = sum(1 for post in posts if post.is_free)
            paid_posts = sum(1 for post in posts if post.is_paid)
            
            return {
                'total_posts_analyzed': total_posts,
                'average_word_count': round(avg_word_count, 0),
                'average_reading_time_minutes': round(avg_reading_time, 1),
                'posting_frequency_per_day': round(posting_frequency, 2),
                'free_content_ratio': round(free_posts / total_posts, 2) if total_posts > 0 else 0,
                'paid_content_ratio': round(paid_posts / total_posts, 2) if total_posts > 0 else 0,
                'content_themes': common_keywords[:5] if common_keywords else [],
                'most_recent_post': max(post.published_at for post in posts).isoformat(),
                'oldest_post_analyzed': min(post.published_at for post in posts).isoformat(),
                'publication_url': f"https://{subdomain}.substack.com",
                'rss_url': f"https://{subdomain}.substack.com/feed"
            }
            
        except Exception as e:
            logger.error(f"Publication analytics failed for {subdomain}: {e}")
            return {}
    
    async def get_trending_topics(self, time_period: str = 'week') -> List[Dict]:
        """
        Get trending topics on Substack.
        
        Args:
            time_period: 'day', 'week', 'month'
            
        Returns:
            List of trending topics with metadata
        """
        try:
            trending_url = f"{self.base_url}/discover"
            
            async with self.session.get(trending_url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                topics = []
                
                # Look for trending sections
                trending_sections = soup.find_all('section', class_=['trending', 'popular'])
                
                for section in trending_sections:
                    topic_elements = section.find_all('div', class_='topic-card')
                    
                    for element in topic_elements:
                        try:
                            topic_name = element.find('h3').get_text(strip=True)
                            post_count_elem = element.find('.post-count')
                            post_count = post_count_elem.get_text(strip=True) if post_count_elem else "0"
                            
                            topics.append({
                                'topic': topic_name,
                                'post_count': self._parse_count_text(post_count),
                                'time_period': time_period
                            })
                        except:
                            continue
                
                return topics
                
        except Exception as e:
            logger.error(f"Trending topics fetch failed: {e}")
            return []
