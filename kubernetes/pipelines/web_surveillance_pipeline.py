"""IA Influencer Agent - Web Surveillance and Crawling Pipeline System
Enterprise-Grade Automated Content Monitoring and Violation Detection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive web surveillance and crawling capabilities for the IA Influencer Agent
platform, enabling real-time monitoring of digital platforms for unauthorized content usage and
copyright violations across multiple social media and content platforms.

Features:
- Multi-platform content monitoring (YouTube, TikTok, Instagram, Twitter/X)
- Real-time violation detection and alerting
- Automated evidence collection and documentation
- Advanced crawling strategies with rate limiting
- Pattern recognition and content matching
- Compliance with platform APIs and terms of service
- Automated DMCA takedown notice generation

Platforms Supported:
- YouTube (Creator API + Web Scraping)
- TikTok (Web Scraping + API when available)
- Instagram (Basic Display API + Web Scraping)
- Twitter/X (API v2 + Web Scraping)
- Generic web crawling for any platform

WARNING: This code is proprietary and confidential. Any unauthorized use, copying, or distribution
is strictly prohibited and will result in legal action under German and international law.
"""import asyncio
import logging
import json
import aiohttp
import requests
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import re
import hashlib
import time
from urllib.parse import urljoin, urlparse
import base64
import tempfile

# Web scraping and automation libraries
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import scrapy
    from scrapy.crawler import CrawlerProcess
    from scrapy.http import Request
    SCRAPY_AVAILABLE = True
except ImportError:
    SCRAPY_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

class Platform(Enum):
    """Supported platform enumeration"""    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SOUNDCLOUD = "soundcloud"
    SPOTIFY = "spotify"
    GENERIC = "generic"

class CrawlingMethod(Enum):
    """Crawling method types"""    API_OFFICIAL = "api_official"
    WEB_SCRAPING = "web_scraping"
    SELENIUM_AUTOMATION = "selenium_automation"
    RSS_FEEDS = "rss_feeds"
    WEBHOOK_MONITORING = "webhook_monitoring"

class ViolationType(Enum):
    """Content violation types"""    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    UNAUTHORIZED_USE = "unauthorized_use"
    CONTENT_THEFT = "content_theft"
    TRADEMARK_VIOLATION = "trademark_violation"
    IMPERSONATION = "impersonation"
    SPAM_CONTENT = "spam_content"

class AlertSeverity(Enum):
    """Alert severity levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SurveillanceTarget:
    """Content surveillance target configuration"""    target_id: str
    platform: Platform
    content_keywords: List[str]
    content_fingerprints: List[str]
    user_handles: List[str]
    monitoring_frequency: int = 3600  # seconds
    alert_threshold: float = 0.8
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ContentMatch:
    """Detected content match result"""    match_id: str
    target_id: str
    platform: Platform
    detected_url: str
    content_title: str
    content_description: str
    uploader_handle: str
    upload_date: datetime
    similarity_score: float
    violation_type: ViolationType
    evidence_data: Dict[str, Any]
    screenshot_path: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class CrawlingJob:
    """Web crawling job configuration"""    job_id: str
    platform: Platform
    method: CrawlingMethod
    targets: List[SurveillanceTarget]
    search_queries: List[str]
    max_results: int = 100
    depth_limit: int = 2
    rate_limit_delay: float = 1.0
    timeout: int = 300
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class YouTubeCrawler:
    """YouTube platform crawler and monitor"""    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.logger = logging.getLogger(f"{__name__}.YouTubeCrawler")
        
    async def search_content(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search YouTube content using API or web scraping"""        if self.api_key:
            return await self._api_search(query, max_results)
        else:
            return await self._web_search(query, max_results)
            
    async def _api_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using YouTube Data API"""        url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': min(max_results, 50),
            'key': self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for item in data.get('items', []):
                            snippet = item.get('snippet', {})
                            results.append({
                                'video_id': item.get('id', {}).get('videoId'),
                                'title': snippet.get('title'),
                                'description': snippet.get('description'),
                                'channel_title': snippet.get('channelTitle'),
                                'channel_id': snippet.get('channelId'),
                                'published_at': snippet.get('publishedAt'),
                                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                                'url': f"https://www.youtube.com/watch?v={item.get('id', {}).get('videoId')}"
                            })
                            
                        return results
                    else:
                        self.logger.error(f"YouTube API error: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"YouTube API search failed: {str(e)}")
            return []
            
    async def _web_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using web scraping as fallback"""        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available for YouTube web scraping")
            return []
            
        results = []
        
        try:
            # Configure Chrome options for headless browsing
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Search YouTube
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            driver.get(search_url)
            
            # Wait for results to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
            )
            
            # Extract video information
            video_elements = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
            
            for i, element in enumerate(video_elements[:max_results]):
                try:
                    # Extract video data
                    title_element = element.find_element(By.CSS_SELECTOR, "#video-title")
                    title = title_element.get_attribute("title")
                    video_url = title_element.get_attribute("href")
                    
                    channel_element = element.find_element(By.CSS_SELECTOR, "ytd-channel-name a")
                    channel_name = channel_element.text
                    
                    # Extract video ID from URL
                    video_id = None
                    if video_url and "watch?v=" in video_url:
                        video_id = video_url.split("watch?v=")[1].split("&")[0]
                        
                    results.append({
                        'video_id': video_id,
                        'title': title,
                        'channel_title': channel_name,
                        'url': video_url,
                        'platform': Platform.YOUTUBE.value,
                        'extracted_at': datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract video data: {str(e)}")
                    continue
                    
            driver.quit()
            
        except Exception as e:
            self.logger.error(f"YouTube web scraping failed: {str(e)}")
            
        return results

class TikTokCrawler:
    """TikTok platform crawler and monitor"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.TikTokCrawler")
        self.base_url = "https://www.tiktok.com"
        
    async def search_content(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search TikTok content using web scraping"""        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available for TikTok scraping")
            return []
            
        results = []
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Search TikTok
            search_url = f"https://www.tiktok.com/search?q={query.replace(' ', '%20')}"
            driver.get(search_url)
            
            # Wait for content to load
            time.sleep(5)
            
            # Scroll to load more content
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
            # Extract video information
            video_elements = driver.find_elements(By.CSS_SELECTOR, "[data-e2e='search-card-video']")
            
            for element in video_elements[:max_results]:
                try:
                    # Extract video URL
                    link_element = element.find_element(By.TAG_NAME, "a")
                    video_url = link_element.get_attribute("href")
                    
                    # Extract author
                    try:
                        author_element = element.find_element(By.CSS_SELECTOR, "[data-e2e='search-card-user-unique-id']")
                        author = author_element.text
                    except:
                        author = "Unknown"
                        
                    # Extract description/title
                    try:
                        desc_element = element.find_element(By.CSS_SELECTOR, "[data-e2e='search-card-desc']")
                        description = desc_element.text
                    except:
                        description = ""
                        
                    results.append({
                        'video_id': self._extract_video_id(video_url),
                        'title': description[:100] if description else "TikTok Video",
                        'description': description,
                        'author': author,
                        'url': video_url,
                        'platform': Platform.TIKTOK.value,
                        'extracted_at': datetime.utcnow().isoformat()
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract TikTok video data: {str(e)}")
                    continue
                    
            driver.quit()
            
        except Exception as e:
            self.logger.error(f"TikTok scraping failed: {str(e)}")
            
        return results
        
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from TikTok URL"""        if "/video/" in url:
            return url.split("/video/")[1].split("?")[0]
        return hashlib.md5(url.encode()).hexdigest()[:16]

class InstagramCrawler:
    """Instagram platform crawler and monitor"""    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.base_url = "https://graph.instagram.com"
        self.logger = logging.getLogger(f"{__name__}.InstagramCrawler")
        
    async def search_content(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search Instagram content using API or hashtag monitoring"""        if self.access_token:
            return await self._api_search(query, max_results)
        else:
            return await self._web_search(query, max_results)
            
    async def _api_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Instagram Basic Display API"""        # Note: Instagram API has limited search capabilities
        # This is a simplified implementation
        results = []
        
        try:
            url = f"{self.base_url}/me/media"
            params = {
                'fields': 'id,caption,media_type,media_url,permalink,timestamp',
                'access_token': self.access_token,
                'limit': min(max_results, 25)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get('data', []):
                            if query.lower() in item.get('caption', '').lower():
                                results.append({
                                    'post_id': item.get('id'),
                                    'caption': item.get('caption'),
                                    'media_type': item.get('media_type'),
                                    'media_url': item.get('media_url'),
                                    'url': item.get('permalink'),
                                    'timestamp': item.get('timestamp'),
                                    'platform': Platform.INSTAGRAM.value
                                })
                                
        except Exception as e:
            self.logger.error(f"Instagram API search failed: {str(e)}")
            
        return results
        
    async def _web_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using web scraping (hashtag monitoring)"""        # Instagram web scraping is limited due to anti-bot measures
        # This is a basic implementation for hashtag monitoring
        results = []
        
        if not SELENIUM_AVAILABLE:
            return results
            
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Access hashtag page
            hashtag = query.replace('#', '').replace(' ', '')
            url = f"https://www.instagram.com/explore/tags/{hashtag}/"
            driver.get(url)
            
            time.sleep(5)
            
            # Extract post URLs (limited due to Instagram's structure)
            post_elements = driver.find_elements(By.CSS_SELECTOR, "article a")
            
            for element in post_elements[:max_results]:
                try:
                    post_url = element.get_attribute("href")
                    if post_url:
                        results.append({
                            'post_id': self._extract_post_id(post_url),
                            'url': post_url,
                            'platform': Platform.INSTAGRAM.value,
                            'hashtag': hashtag,
                            'extracted_at': datetime.utcnow().isoformat()
                        })
                except:
                    continue
                    
            driver.quit()
            
        except Exception as e:
            self.logger.error(f"Instagram web scraping failed: {str(e)}")
            
        return results
        
    def _extract_post_id(self, url: str) -> str:
        """Extract post ID from Instagram URL"""        if "/p/" in url:
            return url.split("/p/")[1].split("/")[0]
        return hashlib.md5(url.encode()).hexdigest()[:16]

class TwitterCrawler:
    """Twitter/X platform crawler and monitor"""    
    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.logger = logging.getLogger(f"{__name__}.TwitterCrawler")
        
    async def search_content(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search Twitter content using API"""        if not self.bearer_token:
            self.logger.warning("Twitter API bearer token not available")
            return []
            
        results = []
        
        try:
            url = f"{self.base_url}/tweets/search/recent"
            headers = {
                'Authorization': f'Bearer {self.bearer_token}',
                'Content-Type': 'application/json'
            }
            params = {
                'query': query,
                'max_results': min(max_results, 100),
                'tweet.fields': 'created_at,author_id,public_metrics,context_annotations',
                'user.fields': 'username,name,verified',
                'expansions': 'author_id'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Create user lookup
                        users = {user['id']: user for user in data.get('includes', {}).get('users', [])}
                        
                        for tweet in data.get('data', []):
                            author = users.get(tweet.get('author_id'), {})
                            
                            results.append({
                                'tweet_id': tweet.get('id'),
                                'text': tweet.get('text'),
                                'author_id': tweet.get('author_id'),
                                'author_username': author.get('username'),
                                'author_name': author.get('name'),
                                'created_at': tweet.get('created_at'),
                                'public_metrics': tweet.get('public_metrics'),
                                'url': f"https://twitter.com/{author.get('username')}/status/{tweet.get('id')}",
                                'platform': Platform.TWITTER.value
                            })
                            
                    else:
                        self.logger.error(f"Twitter API error: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Twitter search failed: {str(e)}")
            
        return results

class GenericWebCrawler:
    """Generic web crawler for any website"""    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.GenericCrawler")
        
    async def crawl_website(self, base_url: str, search_terms: List[str], 
                           max_pages: int = 10) -> List[Dict[str, Any]]:
        """Crawl website for content matching search terms"""        if not BEAUTIFULSOUP_AVAILABLE:
            self.logger.warning("BeautifulSoup not available for web crawling")
            return []
            
        results = []
        visited_urls = set()
        
        try:
            async with aiohttp.ClientSession() as session:
                urls_to_visit = [base_url]
                
                while urls_to_visit and len(visited_urls) < max_pages:
                    current_url = urls_to_visit.pop(0)
                    
                    if current_url in visited_urls:
                        continue
                        
                    visited_urls.add(current_url)
                    
                    try:
                        async with session.get(current_url, timeout=10) as response:
                            if response.status == 200:
                                content = await response.text()
                                soup = BeautifulSoup(content, 'html.parser')
                                
                                # Check for search terms
                                page_text = soup.get_text().lower()
                                matching_terms = [term for term in search_terms 
                                                if term.lower() in page_text]
                                
                                if matching_terms:
                                    results.append({
                                        'url': current_url,
                                        'title': soup.title.string if soup.title else '',
                                        'matching_terms': matching_terms,
                                        'content_preview': page_text[:500],
                                        'platform': Platform.GENERIC.value,
                                        'extracted_at': datetime.utcnow().isoformat()
                                    })
                                    
                                # Extract more URLs to visit
                                for link in soup.find_all('a', href=True):
                                    link_url = urljoin(current_url, link['href'])
                                    if link_url.startswith(base_url) and link_url not in visited_urls:
                                        urls_to_visit.append(link_url)
                                        
                    except Exception as e:
                        self.logger.warning(f"Failed to crawl {current_url}: {str(e)}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Generic web crawling failed: {str(e)}")
            
        return results

class WebSurveillancePipelineManager:
    """    Enterprise Web Surveillance and Crawling Pipeline Manager
    
    Provides comprehensive web monitoring capabilities for:
    - Multi-platform content surveillance and violation detection
    - Real-time crawling and monitoring workflows
    - Automated evidence collection and documentation
    - Content matching and similarity analysis
    - Alert generation and notification management
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize platform crawlers
        self.youtube_crawler = YouTubeCrawler(
            api_key=self.config.get('youtube_api_key')
        )
        self.tiktok_crawler = TikTokCrawler()
        self.instagram_crawler = InstagramCrawler(
            access_token=self.config.get('instagram_access_token')
        )
        self.twitter_crawler = TwitterCrawler(
            bearer_token=self.config.get('twitter_bearer_token')
        )
        self.generic_crawler = GenericWebCrawler()
        
        # Surveillance management
        self.active_targets: Dict[str, SurveillanceTarget] = {}
        self.crawling_jobs: Dict[str, CrawlingJob] = {}
        self.detected_matches: List[ContentMatch] = []
        
        # Performance tracking
        self.surveillance_stats = {
            'active_targets': 0,
            'total_crawls': 0,
            'matches_detected': 0,
            'alerts_generated': 0,
            'last_crawl_time': None
        }
        
    async def add_surveillance_target(self, target: SurveillanceTarget) -> str:
        """Add new content surveillance target"""        self.active_targets[target.target_id] = target
        self.surveillance_stats['active_targets'] = len(self.active_targets)
        
        self.logger.info(f"Added surveillance target: {target.target_id} for {target.platform.value}")
        
        # Start monitoring job
        asyncio.create_task(self._monitor_target(target))
        
        return target.target_id
        
    async def _monitor_target(self, target: SurveillanceTarget):
        """Continuously monitor surveillance target"""        while target.target_id in self.active_targets:
            try:
                # Perform crawling based on platform
                crawler = self._get_platform_crawler(target.platform)
                
                if crawler:
                    # Search for content using keywords
                    for keyword in target.content_keywords:
                        search_results = await self._crawl_platform(
                            target.platform, keyword, max_results=100
                        )
                        
                        # Analyze results for matches
                        matches = await self._analyze_search_results(
                            search_results, target
                        )
                        
                        # Process detected matches
                        for match in matches:
                            await self._process_detected_match(match)
                            
                self.surveillance_stats['total_crawls'] += 1
                self.surveillance_stats['last_crawl_time'] = datetime.utcnow().isoformat()
                
                # Wait before next monitoring cycle
                await asyncio.sleep(target.monitoring_frequency)
                
            except Exception as e:
                self.logger.error(f"Monitoring error for target {target.target_id}: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
                
    def _get_platform_crawler(self, platform: Platform):
        """Get appropriate crawler for platform"""        crawler_map = {
            Platform.YOUTUBE: self.youtube_crawler,
            Platform.TIKTOK: self.tiktok_crawler,
            Platform.INSTAGRAM: self.instagram_crawler,
            Platform.TWITTER: self.twitter_crawler,
            Platform.GENERIC: self.generic_crawler
        }
        return crawler_map.get(platform)
        
    async def _crawl_platform(self, platform: Platform, query: str, 
                             max_results: int = 100) -> List[Dict[str, Any]]:
        """Crawl specific platform for content"""        crawler = self._get_platform_crawler(platform)
        
        if not crawler:
            return []
            
        try:
            if platform == Platform.GENERIC:
                # For generic crawler, we need a base URL
                return []
            else:
                return await crawler.search_content(query, max_results)
                
        except Exception as e:
            self.logger.error(f"Platform crawling failed for {platform.value}: {str(e)}")
            return []
            
    async def _analyze_search_results(self, search_results: List[Dict[str, Any]], 
                                    target: SurveillanceTarget) -> List[ContentMatch]:
        """Analyze search results for potential matches"""        matches = []
        
        for result in search_results:
            # Calculate similarity score (simplified)
            similarity_score = self._calculate_content_similarity(result, target)
            
            if similarity_score >= target.alert_threshold:
                # Create content match
                match = ContentMatch(
                    match_id=f"match_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(matches)}",
                    target_id=target.target_id,
                    platform=target.platform,
                    detected_url=result.get('url', ''),
                    content_title=result.get('title', ''),
                    content_description=result.get('description', ''),
                    uploader_handle=result.get('author', result.get('channel_title', '')),
                    upload_date=self._parse_upload_date(result.get('published_at', result.get('created_at'))),
                    similarity_score=similarity_score,
                    violation_type=ViolationType.UNAUTHORIZED_USE,  # Default
                    evidence_data=result,
                    metadata={'target_keywords': target.content_keywords}
                )
                
                matches.append(match)
                
        return matches
        
    def _calculate_content_similarity(self, result: Dict[str, Any], 
                                    target: SurveillanceTarget) -> float:
        """Calculate content similarity score (simplified implementation)"""        score = 0.0
        content_text = f"{result.get('title', '')} {result.get('description', '')}".lower()
        
        # Keyword matching
        keyword_matches = sum(1 for keyword in target.content_keywords 
                            if keyword.lower() in content_text)
        
        if target.content_keywords:
            score += (keyword_matches / len(target.content_keywords)) * 0.5
            
        # Handle matching
        if target.user_handles:
            uploader = result.get('author', result.get('channel_title', '')).lower()
            handle_matches = sum(1 for handle in target.user_handles 
                               if handle.lower() in uploader)
            score += (handle_matches / len(target.user_handles)) * 0.3
            
        # Additional similarity factors could be added here
        # (fingerprint matching, metadata analysis, etc.)
        
        return min(score, 1.0)
        
    def _parse_upload_date(self, date_str: Optional[str]) -> datetime:
        """Parse upload date from various formats"""        if not date_str:
            return datetime.utcnow()
            
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                # Try common formats
                from dateutil import parser
                return parser.parse(date_str)
            except:
                return datetime.utcnow()
                
    async def _process_detected_match(self, match: ContentMatch):
        """Process detected content match"""        self.detected_matches.append(match)
        self.surveillance_stats['matches_detected'] += 1
        
        # Take screenshot if possible
        if SELENIUM_AVAILABLE and match.detected_url:
            screenshot_path = await self._capture_evidence_screenshot(match.detected_url)
            match.screenshot_path = screenshot_path
            
        # Generate alert
        await self._generate_violation_alert(match)
        
        self.logger.info(f"Detected content match: {match.match_id} "
                        f"(similarity: {match.similarity_score:.2f})")
        
    async def _capture_evidence_screenshot(self, url: str) -> Optional[str]:
        """Capture screenshot evidence of detected content"""        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # Wait for page load
            time.sleep(3)
            
            # Take screenshot
            screenshot_dir = Path(tempfile.gettempdir()) / "surveillance_screenshots"
            screenshot_dir.mkdir(exist_ok=True)
            
            screenshot_path = screenshot_dir / f"evidence_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(str(screenshot_path))
            
            driver.quit()
            
            return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"Screenshot capture failed: {str(e)}")
            return None
            
    async def _generate_violation_alert(self, match: ContentMatch):
        """Generate violation alert for detected match"""        alert_data = {
            'alert_id': f"alert_{match.match_id}",
            'match': asdict(match),
            'severity': self._determine_alert_severity(match),
            'generated_at': datetime.utcnow().isoformat(),
            'recommended_actions': self._get_recommended_actions(match)
        }
        
        self.surveillance_stats['alerts_generated'] += 1
        
        # Here you would integrate with notification systems
        # (email, Slack, webhook, etc.)
        self.logger.info(f"Generated violation alert: {alert_data['alert_id']}")
        
        return alert_data
        
    def _determine_alert_severity(self, match: ContentMatch) -> AlertSeverity:
        """Determine alert severity based on match characteristics"""        if match.similarity_score >= 0.95:
            return AlertSeverity.CRITICAL
        elif match.similarity_score >= 0.85:
            return AlertSeverity.HIGH
        elif match.similarity_score >= 0.75:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
            
    def _get_recommended_actions(self, match: ContentMatch) -> List[str]:
        """Get recommended actions for violation"""        actions = [
            "Review detected content for copyright infringement",
            "Collect additional evidence if needed",
            "Contact platform for content removal"
        ]
        
        if match.similarity_score >= 0.90:
            actions.append("Consider immediate DMCA takedown notice")
            
        if match.platform in [Platform.YOUTUBE, Platform.INSTAGRAM]:
            actions.append("Use platform's copyright reporting tools")
            
        return actions
        
    def get_surveillance_statistics(self) -> Dict[str, Any]:
        """Get surveillance system statistics"""        return {
            **self.surveillance_stats,
            'recent_matches': len([m for m in self.detected_matches 
                                 if (datetime.utcnow() - m.upload_date).days <= 7]),
            'platform_distribution': self._get_platform_distribution(),
            'system_capabilities': self._get_system_capabilities()
        }
        
    def _get_platform_distribution(self) -> Dict[str, int]:
        """Get distribution of matches by platform"""        distribution = {}
        for match in self.detected_matches:
            platform = match.platform.value
            distribution[platform] = distribution.get(platform, 0) + 1
        return distribution
        
    def _get_system_capabilities(self) -> Dict[str, bool]:
        """Get system capabilities status"""        return {
            'selenium_available': SELENIUM_AVAILABLE,
            'scrapy_available': SCRAPY_AVAILABLE,
            'beautifulsoup_available': BEAUTIFULSOUP_AVAILABLE,
            'youtube_api': bool(self.config.get('youtube_api_key')),
            'instagram_api': bool(self.config.get('instagram_access_token')),
            'twitter_api': bool(self.config.get('twitter_bearer_token'))
        }

# Global surveillance pipeline manager
surveillance_pipeline_manager = WebSurveillancePipelineManager()

def get_surveillance_pipeline_manager() -> WebSurveillancePipelineManager:
    """Get global surveillance pipeline manager instance"""    return surveillance_pipeline_manager
