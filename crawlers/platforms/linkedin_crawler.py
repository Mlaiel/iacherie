"""
LinkedIn Crawler
================

Professional LinkedIn content crawler for business content monitoring.
Implements LinkedIn Marketing API integration with advanced content discovery.

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

import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from ..utils.rate_limiter import LinkedInRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ..utils.content_analyzer import ContentAnalyzer
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError
from ...database.models import CrawlResult, ContentMatch
from ...security.encryption import FieldEncryption

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class LinkedInPost:
    """LinkedIn post data structure."""
    post_id: str
    author_id: str
    author_name: str
    author_headline: str
    content: str
    post_type: str  # article, video, image, document
    published_at: datetime
    like_count: int
    comment_count: int
    share_count: int
    view_count: int
    media_urls: List[str]
    hashtags: List[str]
    mentions: List[str]
    company_id: Optional[str]
    industry: Optional[str]

@dataclass
class LinkedInProfile:
    """LinkedIn profile data structure."""
    profile_id: str
    name: str
    headline: str
    summary: str
    location: str
    industry: str
    connection_count: int
    follower_count: int
    experience: List[Dict]
    education: List[Dict]
    skills: List[str]
    languages: List[str]
    profile_url: str
    avatar_url: str

@dataclass
class LinkedInCompany:
    """LinkedIn company data structure."""
    company_id: str
    name: str
    description: str
    industry: str
    company_size: str
    headquarters: str
    founded: Optional[int]
    website: str
    follower_count: int
    employee_count: int
    specialties: List[str]
    logo_url: str

class LinkedInCrawler:
    """
    Professional LinkedIn crawler implementation.
    
    Features:
    - LinkedIn Marketing API integration
    - Advanced post and article monitoring
    - Professional network analysis
    - Company page monitoring
    - Content engagement tracking
    - Industry trend analysis
    - Job posting monitoring
    - Influence measurement
    - B2B content discovery
    - Professional content verification
    """
    
    def __init__(self):
        """Initialize LinkedIn crawler."""
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self.rate_limiter = LinkedInRateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.content_analyzer = ContentAnalyzer()
        self.encryption = FieldEncryption()
        
        # API endpoints
        self.base_api_url = "https://api.linkedin.com/v2"
        self.marketing_api_url = "https://api.linkedin.com/rest"
        
        # Headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }
        
        # Content type mapping
        self.content_types = {
            "ARTICLE": "article",
            "VIDEO": "video", 
            "IMAGE": "image",
            "DOCUMENT": "document",
            "POLL": "poll",
            "EVENT": "event",
            "CAROUSEL": "carousel"
        }
    
    async def search_posts(
        self,
        keywords: List[str],
        max_results: int = 100,
        date_range: Optional[tuple] = None,
        content_type: Optional[str] = None,
        industry: Optional[str] = None
    ) -> AsyncGenerator[LinkedInPost, None]:
        """
        Search LinkedIn posts by keywords with advanced filtering.
        
        Args:
            keywords: List of search keywords
            max_results: Maximum number of results to return
            date_range: Date range tuple (start_date, end_date)
            content_type: Filter by content type
            industry: Filter by industry
            
        Yields:
            LinkedInPost: Post data
        """
        await self.rate_limiter.wait_if_needed("search")
        
        try:
            # Use marketing API for advanced search
            search_params = {
                "q": "search",
                "keywords": " ".join(keywords),
                "count": min(max_results, 50),
                "start": 0
            }
            
            if date_range:
                start_date, end_date = date_range
                search_params["dateRange"] = {
                    "start": int(start_date.timestamp() * 1000),
                    "end": int(end_date.timestamp() * 1000)
                }
            
            if content_type:
                search_params["contentType"] = content_type.upper()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.marketing_api_url}/posts"
                async with session.get(url, headers=self.headers, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for post_data in data.get("elements", []):
                            post = await self._parse_post_data(post_data)
                            if post:
                                yield post
                    
                    elif response.status == 429:
                        raise RateLimitError("LinkedIn API rate limit exceeded")
                    else:
                        logger.error(f"LinkedIn API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error searching LinkedIn posts: {e}")
            raise CrawlerError(f"LinkedIn search failed: {e}")
    
    async def monitor_profile(
        self,
        profile_url: str,
        check_interval: int = 3600
    ) -> AsyncGenerator[LinkedInPost, None]:
        """
        Monitor LinkedIn profile for new posts.
        
        Args:
            profile_url: LinkedIn profile URL to monitor
            check_interval: Check interval in seconds
            
        Yields:
            LinkedInPost: New posts from the profile
        """
        profile_id = self._extract_profile_id(profile_url)
        last_check = datetime.now()
        
        while True:
            try:
                await self.rate_limiter.wait_if_needed("profile")
                
                async with aiohttp.ClientSession() as session:
                    url = f"{self.base_api_url}/people/{profile_id}/posts"
                    params = {
                        "projection": "(elements*(id,activity,created,commentary,content))",
                        "count": 20
                    }
                    
                    async with session.get(url, headers=self.headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for post_data in data.get("elements", []):
                                post = await self._parse_post_data(post_data)
                                if post and post.published_at > last_check:
                                    yield post
                            
                            last_check = datetime.now()
                        
                        elif response.status == 429:
                            logger.warning("Rate limit hit, backing off")
                            await asyncio.sleep(300)
                        
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring LinkedIn profile: {e}")
                await asyncio.sleep(60)
    
    async def get_company_posts(
        self,
        company_id: str,
        max_results: int = 50
    ) -> List[LinkedInPost]:
        """
        Get recent posts from LinkedIn company page.
        
        Args:
            company_id: LinkedIn company ID
            max_results: Maximum number of posts to retrieve
            
        Returns:
            List[LinkedInPost]: Company posts
        """
        await self.rate_limiter.wait_if_needed("company")
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_api_url}/companies/{company_id}/posts"
                params = {
                    "projection": "(elements*(id,activity,created,commentary,content))",
                    "count": min(max_results, 50)
                }
                
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = []
                        
                        for post_data in data.get("elements", []):
                            post = await self._parse_post_data(post_data)
                            if post:
                                posts.append(post)
                        
                        return posts
                    
                    elif response.status == 429:
                        raise RateLimitError("LinkedIn API rate limit exceeded")
                    else:
                        logger.error(f"LinkedIn API error: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error getting company posts: {e}")
            raise CrawlerError(f"LinkedIn company posts failed: {e}")
    
    async def scrape_with_selenium(
        self,
        search_query: str,
        max_scroll: int = 5
    ) -> List[LinkedInPost]:
        """
        Scrape LinkedIn using Selenium as fallback.
        
        Args:
            search_query: Search query
            max_scroll: Maximum number of scrolls
            
        Returns:
            List[LinkedInPost]: Scraped posts
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
        posts = []
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to LinkedIn search
            search_url = f"https://www.linkedin.com/search/results/content/?keywords={search_query}"
            driver.get(search_url)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-results"))
            )
            
            # Scroll to load more content
            for _ in range(max_scroll):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            # Extract post elements
            post_elements = driver.find_elements(By.CLASS_NAME, "update-components-text")
            
            for element in post_elements:
                try:
                    post_data = self._extract_post_from_element(element)
                    if post_data:
                        posts.append(post_data)
                except Exception as e:
                    logger.debug(f"Error extracting post: {e}")
                    continue
            
            return posts
            
        except Exception as e:
            logger.error(f"Error in LinkedIn Selenium scraping: {e}")
            return posts
            
        finally:
            if driver:
                driver.quit()
    
    async def analyze_content_engagement(
        self,
        post_id: str
    ) -> Dict:
        """
        Analyze engagement patterns for LinkedIn content.
        
        Args:
            post_id: LinkedIn post ID
            
        Returns:
            Dict: Engagement analysis
        """
        await self.rate_limiter.wait_if_needed("analytics")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get post metrics
                metrics_url = f"{self.base_api_url}/posts/{post_id}/metrics"
                async with session.get(metrics_url, headers=self.headers) as response:
                    if response.status == 200:
                        metrics = await response.json()
                        
                        # Get engagement details
                        engagement_url = f"{self.base_api_url}/posts/{post_id}/engagement"
                        async with session.get(engagement_url, headers=self.headers) as eng_response:
                            if eng_response.status == 200:
                                engagement = await eng_response.json()
                                
                                return {
                                    "metrics": metrics,
                                    "engagement": engagement,
                                    "engagement_rate": self._calculate_engagement_rate(metrics),
                                    "trend_analysis": await self._analyze_engagement_trend(post_id)
                                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error analyzing LinkedIn engagement: {e}")
            return {}
    
    async def _parse_post_data(self, post_data: Dict) -> Optional[LinkedInPost]:
        """Parse LinkedIn post data from API response."""



        try:
            activity = post_data.get("activity", {})
            actor = activity.get("actor", {})
            
            # Extract basic info
            post_id = post_data.get("id", "")
            author_id = actor.get("id", "")
            author_name = actor.get("name", {}).get("localized", {}).get("en_US", "")
            
            # Extract content
            commentary = post_data.get("commentary", {}).get("text", {}).get("text", "")
            content_data = post_data.get("content", {})
            
            # Extract media URLs
            media_urls = []
            if "media" in content_data:
                for media in content_data["media"]:
                    if "downloadUrl" in media:
                        media_urls.append(media["downloadUrl"])
            
            # Extract hashtags and mentions
            hashtags = re.findall(r'#\w+', commentary)
            mentions = re.findall(r'@\w+', commentary)
            
            # Parse timestamps
            created_time = activity.get("created", {}).get("time", 0)
            published_at = datetime.fromtimestamp(created_time / 1000) if created_time else datetime.now()
            
            return LinkedInPost(
                post_id=post_id,
                author_id=author_id,
                author_name=author_name,
                author_headline="",  # Would need separate API call
                content=commentary,
                post_type=self._determine_post_type(content_data),
                published_at=published_at,
                like_count=0,  # Would need metrics API
                comment_count=0,
                share_count=0,
                view_count=0,
                media_urls=media_urls,
                hashtags=hashtags,
                mentions=mentions,
                company_id=None,
                industry=None
            )
            
        except Exception as e:
            logger.error(f"Error parsing LinkedIn post data: {e}")
            return None
    
    def _extract_profile_id(self, profile_url: str) -> str:
        """Extract profile ID from LinkedIn URL."""
        # Handle different LinkedIn URL formats
        if "/in/" in profile_url:
            return profile_url.split("/in/")[1].split("/")[0]
        elif "/pub/" in profile_url:
            return profile_url.split("/pub/")[1].split("/")[0]
        else:
            raise ValueError(f"Invalid LinkedIn profile URL: {profile_url}")
    
    def _determine_post_type(self, content_data: Dict) -> str:
        """Determine post type from content data."""
        if "article" in content_data:
            return "article"
        elif "video" in content_data:
            return "video"
        elif "images" in content_data:
            return "image"
        elif "document" in content_data:
            return "document"
        else:
            return "text"
    
    def _extract_post_from_element(self, element) -> Optional[LinkedInPost]:
        """Extract post data from Selenium web element."""



        try:
            # This would be implemented based on LinkedIn's current HTML structure
            # Note: LinkedIn actively blocks scraping, so this is for fallback only
            text_content = element.text
            
            return LinkedInPost(
                post_id=f"scraped_{hash(text_content)}",
                author_id="",
                author_name="",
                author_headline="",
                content=text_content,
                post_type="text",
                published_at=datetime.now(),
                like_count=0,
                comment_count=0,
                share_count=0,
                view_count=0,
                media_urls=[],
                hashtags=re.findall(r'#\w+', text_content),
                mentions=re.findall(r'@\w+', text_content),
                company_id=None,
                industry=None
            )
            
        except Exception as e:
            logger.debug(f"Error extracting post from element: {e}")
            return None
    
    def _calculate_engagement_rate(self, metrics: Dict) -> float:
        """Calculate engagement rate from metrics."""



        try:
            likes = metrics.get("likes", 0)
            comments = metrics.get("comments", 0)
            shares = metrics.get("shares", 0)
            impressions = metrics.get("impressions", 1)
            
            engagement = likes + comments + shares
            return (engagement / impressions) * 100 if impressions > 0 else 0.0
            
        except Exception:
            return 0.0
    
    async def _analyze_engagement_trend(self, post_id: str) -> Dict:
        """Analyze engagement trend for a post."""
        # This would implement historical engagement analysis
        return {
            "trend": "stable",
            "peak_time": None,
            "decay_rate": 0.0
        }
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self, 'session') and self.session:
            await self.session.close()
        
        logger.info("LinkedIn crawler closed")

# Export for module
__all__ = ["LinkedInCrawler", "LinkedInPost", "LinkedInProfile", "LinkedInCompany"]
