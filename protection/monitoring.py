"""Advanced Content Protection Monitoring System
Real-time monitoring across multiple platforms with intelligent violation detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import hashlib
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
from urllib.parse import urljoin, urlparse
import json

# Web scraping
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Platform APIs
import google.auth
from googleapiclient.discovery import build
import tweepy

from ..config import settings
from ..core.logging import logger
from ..core.database import database_manager
from ..ai_engine.fingerprinting import fingerprint_engine
from ..ai_engine.vector_database import vector_database


@dataclass
class MonitoringTarget:
    """
Represents a content monitoring target"""
    user_id: str
    content_id: str
    content_type: str
    fingerprint_data: Dict[str, Any]
    platforms: List[str]
    monitoring_frequency: int  # hours
    alert_threshold: float
    created_at: datetime
    last_checked: Optional[datetime] = None


class PlatformCrawler:
    """
Base class for platform-specific crawlers"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.rate_limit_delay = 1.0  # seconds between requests
        self.session = None
        
        # Selenium driver for JavaScript-heavy sites
        self.driver = None
        self._setup_selenium()
    
    def _setup_selenium(self):
        """
Setup headless Chrome driver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
        except Exception as e:
            logger.warning(f"Selenium setup failed for {self.platform_name}: {str(e)}")
            self.driver = None
    
    async def initialize_session(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
    
    async def close_session(self):
        """
Close HTTP session"""
        if self.session:
            await self.session.close()
        if self.driver:
            self.driver.quit()
    
    async def search_content(self, query: str, content_type: str) -> List[Dict[str, Any]]:
        """
Search for content on platform - to be implemented by subclasses"""
        logger.info(f"Searching for {content_type} content with query: {query}")
        
        # Base implementation with generic web scraping approach
        try:
            results = []
            
            # Generic search implementation that subclasses can override
            if hasattr(self, 'api_client') and self.api_client:
                # API-based search if available
                api_results = await self._api_search(query, content_type)
                results.extend(api_results)
            
            # Fallback to web scraping search
            web_results = await self._web_search(query, content_type)
            results.extend(web_results)
            
            # Deduplicate results
            seen_urls = set()
            unique_results = []
            for result in results:
                url = result.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
            
            logger.info(f"Found {len(unique_results)} unique results for query: {query}")
            return unique_results
            
        except Exception as e:
            logger.error(f"Error searching content: {str(e)}")
            return []
    
    async def _api_search(self, query: str, content_type: str) -> List[Dict[str, Any]]:
        """API-based search implementation"""
        # To be overridden by platform-specific implementations
        return []
    
    async def _web_search(self, query: str, content_type: str) -> List[Dict[str, Any]]:
        """
Web scraping search implementation"""
        try:
            if not self.driver:
                return []
            
            # Generic web search approach
            search_url = f"{self.base_url}/search?q={quote(query)}"
            self.driver.get(search_url)
            
            # Wait for results to load
            time.sleep(2)
            
            results = []
            
            # Generic content extraction (to be customized by subclasses)
            content_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                                                       "a[href*='watch'], a[href*='video'], a[href*='post']")
            
            for element in content_elements[:20]:  # Limit to first 20 results
                try:
                    url = element.get_attribute('href')
                    title = element.get_attribute('title') or element.text
                    
                    if url and title:
                        results.append({
                            'url': url,
                            'title': title.strip(),
                            'platform': self.platform_name,
                            'content_type': content_type,
                            'discovered_at': datetime.now().isoformat()
                        })
                except Exception:
                    continue
            
            return results
            
        except Exception as e:
            logger.warning(f"Web search failed: {str(e)}")
            return []
    
    async def extract_content_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract content data from URL - to be implemented by subclasses"""
        logger.info(f"Extracting content data from URL: {url}")
        
        try:
            if not self.driver:
                await self.init_selenium()
            
            # Navigate to the content URL
            self.driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Extract basic metadata
            content_data = {
                'url': url,
                'platform': self.platform_name,
                'extracted_at': datetime.now().isoformat(),
                'title': '',
                'description': '',
                'author': '',
                'view_count': 0,
                'like_count': 0,
                'publish_date': '',
                'duration': '',
                'tags': [],
                'thumbnail_url': ''
            }
            
            # Extract title
            try:
                title_selectors = ['h1', 'title', '[data-title]', '.title']
                for selector in title_selectors:
                    title_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if title_element and title_element.text.strip():
                        content_data['title'] = title_element.text.strip()
                        break
            except Exception:
                content_data['title'] = self.driver.title
            
            # Extract description
            try:
                desc_selectors = ['[name="description"]', '.description', '[data-description]']
                for selector in desc_selectors:
                    if selector.startswith('[name'):
                        desc_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        content_data['description'] = desc_element.get_attribute('content') or ''
                    else:
                        desc_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        content_data['description'] = desc_element.text.strip()
                    if content_data['description']:
                        break
            except Exception:
                pass
            
            # Extract author/creator info
            try:
                author_selectors = ['.author', '.creator', '.channel-name', '[data-author]']
                for selector in author_selectors:
                    author_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if author_element and author_element.text.strip():
                        content_data['author'] = author_element.text.strip()
                        break
            except Exception:
                pass
            
            # Extract view count
            try:
                view_selectors = ['.view-count', '[data-views]', '.views']
                for selector in view_selectors:
                    view_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if view_element:
                        view_text = view_element.text or view_element.get_attribute('data-views') or ''
                        # Extract numeric values from text like "1.2K views" or "1,234 views"
                        import re
                        view_match = re.search(r'([\d,.]+)([KMB]?)', view_text.replace(',', ''))
                        if view_match:
                            num = float(view_match.group(1))
                            unit = view_match.group(2)
                            if unit == 'K':
                                num *= 1000
                            elif unit == 'M':
                                num *= 1000000
                            elif unit == 'B':
                                num *= 1000000000
                            content_data['view_count'] = int(num)
                        break
            except Exception:
                pass
            
            # Extract thumbnail
            try:
                thumb_selectors = ['meta[property="og:image"]', '.thumbnail img', 'video', 'img[src*="thumb"]']
                for selector in thumb_selectors:
                    thumb_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if thumb_element:
                        thumb_url = thumb_element.get_attribute('content') or thumb_element.get_attribute('src')
                        if thumb_url:
                            content_data['thumbnail_url'] = thumb_url
                            break
            except Exception:
                pass
            
            # Platform-specific extraction (can be overridden by subclasses)
            platform_data = await self._extract_platform_specific_data(url)
            content_data.update(platform_data)
            
            logger.info(f"Successfully extracted content data for: {content_data.get('title', 'Unknown')}")
            return content_data
            
        except Exception as e:
            logger.error(f"Error extracting content data from {url}: {str(e)}")
            return None
    
    async def _extract_platform_specific_data(self, url: str) -> Dict[str, Any]:
        """Extract platform-specific data - to be overridden by subclasses"""
        return {}


class YouTubeCrawler(PlatformCrawler):
    """
YouTube content crawler using API and web scraping"""
    
    def __init__(self):
        super().__init__("youtube")
        self.api_key = settings.platforms.youtube_api_key
        self.youtube_service = None
        
        if self.api_key:
            try:
                self.youtube_service = build('youtube', 'v3', developerKey=self.api_key)
            except Exception as e:
                logger.warning(f"YouTube API setup failed: {str(e)}")
    
    async def search_content(self, query: str, content_type: str) -> List[Dict[str, Any]]:
        """Search YouTube for similar content"""
        results = []
        
        if self.youtube_service:
            try:
                # API search
                search_response = self.youtube_service.search().list(
                    q=query,
                    part='id,snippet',
                    maxResults=50,
                    type='video' if content_type in ['video', 'audio'] else 'video'
                ).execute()
                
                for item in search_response['items']:
                    video_data = {
                        'platform': 'youtube',
                        'id': item['id']['videoId'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'thumbnail': item['snippet']['thumbnails']['default']['url'],
                        'channel': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt'],
                        'found_via': 'api_search'
                    }
                    results.append(video_data)
                    
            except Exception as e:
                logger.error(f"YouTube API search failed: {str(e)}")
        
        # Fallback to web scraping if API fails
        if not results:
            results = await self._web_search(query)
        
        return results
    
    async def _web_search(self, query: str) -> List[Dict[str, Any]]:
        """Fallback web scraping search"""
        if not self.driver:
            return []
        
        try:
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            self.driver.get(search_url)
            
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "contents"))
            )
            
            # Parse results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            results = []
            
            # Extract video links and data
            video_elements = soup.find_all('a', {'href': lambda x: x and '/watch?v=' in x})
            
            for element in video_elements[:20]:  # Limit to first 20
                href = element.get('href')
                if href:
                    video_id = href.split('v=')[1].split('&')[0]
                    title_elem = element.find('span', {'id': 'video-title'})
                    title = title_elem.text.strip() if title_elem else "Unknown Title"
                    
                    video_data = {
                        'platform': 'youtube',
                        'id': video_id,
                        'url': f"https://www.youtube.com{href}",
                        'title': title,
                        'found_via': 'web_scraping'
                    }
                    results.append(video_data)
            
            return results
            
        except Exception as e:
            logger.error(f"YouTube web scraping failed: {str(e)}")
            return []
    
    async def extract_content_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract detailed content data from YouTube URL"""
        try:
            # Extract video ID from URL
            if 'watch?v=' in url:
                video_id = url.split('watch?v=')[1].split('&')[0]
            else:
                return None
            
            if self.youtube_service:
                # Get video details via API
                video_response = self.youtube_service.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=video_id
                ).execute()
                
                if video_response['items']:
                    video = video_response['items'][0]
                    return {
                        'id': video_id,
                        'title': video['snippet']['title'],
                        'description': video['snippet']['description'],
                        'channel': video['snippet']['channelTitle'],
                        'published_at': video['snippet']['publishedAt'],
                        'duration': video['contentDetails']['duration'],
                        'view_count': video['statistics'].get('viewCount', 0),
                        'like_count': video['statistics'].get('likeCount', 0),
                        'thumbnail': video['snippet']['thumbnails']['maxres']['url'] if 'maxres' in video['snippet']['thumbnails'] else video['snippet']['thumbnails']['high']['url']
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"YouTube content extraction failed: {str(e)}")
            return None


class InstagramCrawler(PlatformCrawler):
    """Instagram content crawler"""
    
    def __init__(self):
        super().__init__("instagram")
        self.access_token = settings.platforms.instagram_access_token
    
    async def search_content(self, query: str, content_type: str) -> List[Dict[str, Any]]:
        """Search Instagram for similar content"""
        # Instagram Graph API has limited search capabilities
        # This would require Instagram Business API access
        results = []
        
        # For now, implement basic hashtag search via web scraping
        if self.driver:
            try:
                hashtag = query.replace(' ', '').lower()
                search_url = f"https://www.instagram.com/explore/tags/{hashtag}/"
                
                self.driver.get(search_url)
                await asyncio.sleep(3)  # Wait for content to load
                
                # Extract post links
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                post_links = soup.find_all('a', {'href': lambda x: x and '/p/' in x})
                
                for link in post_links[:20]:
                    post_url = f"https://www.instagram.com{link['href']}"
                    results.append({
                        'platform': 'instagram',
                        'url': post_url,
                        'found_via': 'hashtag_search'
                    })
                
            except Exception as e:
                logger.error(f"Instagram search failed: {str(e)}")
        
        return results


class TikTokCrawler(PlatformCrawler):
    """TikTok content crawler"""
    
    def __init__(self):
        super().__init__("tiktok")
        self.api_key = settings.platforms.tiktok_api_key
    
    async def search_content(self, query: str, content_type: str) -> List[Dict[str, Any]]:
        """Search TikTok for similar content"""
        results = []
        
        # TikTok's API is more restrictive, use web scraping
        if self.driver:
            try:
                search_url = f"https://www.tiktok.com/search?q={query.replace(' ', '%20')}"
                self.driver.get(search_url)
                await asyncio.sleep(5)  # Wait for JavaScript to load
                
                # Extract video links
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                video_links = soup.find_all('a', {'href': lambda x: x and '/@' in x and '/video/' in x})
                
                for link in video_links[:15]:
                    video_url = f"https://www.tiktok.com{link['href']}"
                    results.append({
                        'platform': 'tiktok',
                        'url': video_url,
                        'found_via': 'search'
                    })
                
            except Exception as e:
                logger.error(f"TikTok search failed: {str(e)}")
        
        return results


class TwitterCrawler(PlatformCrawler):
    """Twitter/X content crawler"""
    
    def __init__(self):
        super().__init__("twitter")
        self.api_key = settings.platforms.twitter_api_key
        self.api_secret = settings.platforms.twitter_api_secret
        self.access_token = settings.platforms.twitter_access_token
        self.access_secret = settings.platforms.twitter_access_secret
        
        self.twitter_api = None
        if all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            try:
                auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
                auth.set_access_token(self.access_token, self.access_secret)
                self.twitter_api = tweepy.API(auth, wait_on_rate_limit=True)
            except Exception as e:
                logger.warning(f"Twitter API setup failed: {str(e)}")
    
    async def search_content(self, query: str, content_type: str) -> List[Dict[str, Any]]:
        """Search Twitter for similar content"""
        results = []
        
        if self.twitter_api:
            try:
                tweets = tweepy.Cursor(self.twitter_api.search_tweets,
                                     q=query, lang="en", result_type="recent").items(50)
                
                for tweet in tweets:
                    tweet_data = {
                        'platform': 'twitter',
                        'id': tweet.id_str,
                        'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}",
                        'text': tweet.text,
                        'user': tweet.user.screen_name,
                        'created_at': tweet.created_at.isoformat(),
                        'retweet_count': tweet.retweet_count,
                        'favorite_count': tweet.favorite_count,
                        'found_via': 'api_search'
                    }
                    results.append(tweet_data)
                    
            except Exception as e:
                logger.error(f"Twitter search failed: {str(e)}")
        
        return results


class ProtectionMonitor:
    """Main content protection monitoring system"""
    
    def __init__(self):
        self.crawlers = {
            'youtube': YouTubeCrawler(),
            'instagram': InstagramCrawler(),
            'tiktok': TikTokCrawler(),
            'twitter': TwitterCrawler()
        }
        
        self.active_monitors: Dict[str, MonitoringTarget] = {}
        self.monitoring_active = False
        self.check_interval = 3600  # 1 hour default
    
    async def initialize(self):
        """
Initialize monitoring system"""
        try:
            # Initialize all crawlers
            for crawler in self.crawlers.values():
                await crawler.initialize_session()
            
            # Load existing monitoring targets from database
            await self._load_monitoring_targets()
            
            logger.info("Protection monitoring system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize protection monitor: {str(e)}")
            raise
    
    async def add_content_monitoring(self, user_id: str, content_id: str, 
                                   content_type: str, fingerprint_data: Dict[str, Any],
                                   platforms: List[str], monitoring_frequency: int = 24,
                                   alert_threshold: float = 0.85) -> bool:
        """Add content to monitoring system"""
        try:
            target = MonitoringTarget(
                user_id=user_id,
                content_id=content_id,
                content_type=content_type,
                fingerprint_data=fingerprint_data,
                platforms=platforms,
                monitoring_frequency=monitoring_frequency,
                alert_threshold=alert_threshold,
                created_at=datetime.utcnow()
            )
            
            # Store in database
            async with database_manager.get_postgres_session() as session:
                await session.execute(
                    """
                    INSERT INTO content_monitoring 
                    (user_id, content_id, content_type, fingerprint_data, platforms, 
                     monitoring_frequency, alert_threshold, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, content_id, content_type, json.dumps(fingerprint_data),
                     json.dumps(platforms), monitoring_frequency, alert_threshold, 
                     datetime.utcnow())
                )
            
            # Add to active monitoring
            self.active_monitors[content_id] = target
            
            logger.info(f"Added content {content_id} to monitoring system")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add content monitoring: {str(e)}")
            return False
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        logger.info("Starting content protection monitoring")
        
        while self.monitoring_active:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Monitoring cycle error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.monitoring_active = False
        
        # Close all crawler sessions
        for crawler in self.crawlers.values():
            await crawler.close_session()
        
        logger.info("Content protection monitoring stopped")
    
    async def _monitoring_cycle(self):
        """Execute one monitoring cycle"""
        logger.info(f"Starting monitoring cycle for {len(self.active_monitors)} targets")
        
        for content_id, target in self.active_monitors.items():
            try:
                # Check if it's time to monitor this content
                if await self._should_check_content(target):
                    await self._check_content_violations(target)
                    
                    # Update last checked time
                    target.last_checked = datetime.utcnow()
                    await self._update_last_checked(content_id, target.last_checked)
                    
            except Exception as e:
                logger.error(f"Error checking content {content_id}: {str(e)}")
    
    async def _should_check_content(self, target: MonitoringTarget) -> bool:
        """Determine if content should be checked in this cycle"""
        if not target.last_checked:
            return True
        
        time_since_check = datetime.utcnow() - target.last_checked
        return time_since_check.total_seconds() >= (target.monitoring_frequency * 3600)
    
    async def _check_content_violations(self, target: MonitoringTarget):
        """
Check for violations of specific content"""
        logger.info(f"Checking content {target.content_id} for violations")
        
        # Generate search queries based on content
        search_queries = await self._generate_search_queries(target)
        
        for platform in target.platforms:
            if platform not in self.crawlers:
                continue
            
            crawler = self.crawlers[platform]
            
            for query in search_queries:
                try:
                    # Search for potentially infringing content
                    search_results = await crawler.search_content(query, target.content_type)
                    
                    # Check each result for similarity
                    for result in search_results:
                        similarity_score = await self._check_content_similarity(
                            target, result, platform
                        )
                        
                        if similarity_score >= target.alert_threshold:
                            await self._handle_violation_detected(target, result, similarity_score)
                    
                    # Rate limiting
                    await asyncio.sleep(crawler.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Error searching {platform} for {query}: {str(e)}")
    
    async def _generate_search_queries(self, target: MonitoringTarget) -> List[str]:
        """Generate search queries based on content fingerprint"""
        queries = []
        
        # Basic content ID search
        queries.append(target.content_id)
        
        # Add user-specific terms if available
        if target.user_id:
            queries.append(f"user_{target.user_id}")
        
        # Content-type specific queries
        if target.content_type == "audio":
            queries.extend(["music", "song", "audio", "track"])
        elif target.content_type == "video":
            queries.extend(["video", "clip", "movie", "content"])
        elif target.content_type == "image":
            queries.extend(["image", "photo", "picture", "art"])
        elif target.content_type == "text":
            queries.extend(["article", "text", "content", "post"])
        
        return queries[:5]  # Limit to 5 queries per platform
    
    async def _check_content_similarity(self, target: MonitoringTarget, 
                                      search_result: Dict[str, Any], 
                                      platform: str) -> float:
        """Check similarity between original content and search result"""
        try:
            # For demonstration, we'll use a simplified similarity check
            # In production, this would involve downloading/analyzing the found content
            
            # Basic text similarity for titles/descriptions
            original_title = target.fingerprint_data.get("title", "")
            found_title = search_result.get("title", "")
            
            if original_title and found_title:
                # Simple word overlap similarity
                original_words = set(original_title.lower().split())
                found_words = set(found_title.lower().split())
                
                if len(original_words.union(found_words)) > 0:
                    similarity = len(original_words.intersection(found_words)) / len(original_words.union(found_words))
                    return similarity
            
            # For actual implementation, would need to:
            # 1. Download the found content
            # 2. Generate fingerprint
            # 3. Compare with original fingerprint using vector database
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Similarity check failed: {str(e)}")
            return 0.0
    
    async def _handle_violation_detected(self, target: MonitoringTarget, 
                                       violation_data: Dict[str, Any], 
                                       similarity_score: float):
        """Handle detected violation"""
        try:
            # Create violation record
            violation_record = {
                "original_content_id": target.content_id,
                "user_id": target.user_id,
                "platform": violation_data["platform"],
                "violation_url": violation_data["url"],
                "similarity_score": similarity_score,
                "detected_at": datetime.utcnow(),
                "status": "pending_review",
                "evidence_data": violation_data
            }
            
            # Store in database
            async with database_manager.get_postgres_session() as session:
                await session.execute(
                    """
                    INSERT INTO protection_violations 
                    (original_content_id, user_id, platform, violation_url, 
                     similarity_score, detected_at, status, evidence_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (violation_record["original_content_id"], violation_record["user_id"],
                     violation_record["platform"], violation_record["violation_url"],
                     violation_record["similarity_score"], violation_record["detected_at"],
                     violation_record["status"], json.dumps(violation_record["evidence_data"]))
                )
            
            # Trigger alert
            from .alert_system import alert_system
            await alert_system.send_violation_alert(target.user_id, violation_record)
            
            logger.warning(f"Violation detected: {similarity_score:.2f} similarity for content {target.content_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle violation: {str(e)}")
    
    async def _load_monitoring_targets(self):
        """Load existing monitoring targets from database"""
        try:
            async with database_manager.get_postgres_session() as session:
                result = await session.execute(
                    """
                    SELECT user_id, content_id, content_type, fingerprint_data, 
                           platforms, monitoring_frequency, alert_threshold, 
                           created_at, last_checked
                    FROM content_monitoring 
                    WHERE active = true
                    """
                )
                
                for row in result.fetchall():
                    target = MonitoringTarget(
                        user_id=row[0],
                        content_id=row[1],
                        content_type=row[2],
                        fingerprint_data=json.loads(row[3]),
                        platforms=json.loads(row[4]),
                        monitoring_frequency=row[5],
                        alert_threshold=row[6],
                        created_at=row[7],
                        last_checked=row[8]
                    )
                    
                    self.active_monitors[target.content_id] = target
            
            logger.info(f"Loaded {len(self.active_monitors)} monitoring targets")
            
        except Exception as e:
            logger.error(f"Failed to load monitoring targets: {str(e)}")
    
    async def _update_last_checked(self, content_id: str, last_checked: datetime):
        """Update last checked timestamp in database"""
        try:
            async with database_manager.get_postgres_session() as session:
                await session.execute(
                    "UPDATE content_monitoring SET last_checked = %s WHERE content_id = %s",
                    (last_checked, content_id)
                )
        except Exception as e:
            logger.error(f"Failed to update last checked: {str(e)}")
    
    async def remove_content_monitoring(self, content_id: str) -> bool:
        """Remove content from monitoring"""
        try:
            # Remove from active monitors
            if content_id in self.active_monitors:
                del self.active_monitors[content_id]
            
            # Mark as inactive in database
            async with database_manager.get_postgres_session() as session:
                await session.execute(
                    "UPDATE content_monitoring SET active = false WHERE content_id = %s",
                    (content_id,)
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove content monitoring: {str(e)}")
            return False
    
    async def get_monitoring_status(self, user_id: str) -> Dict[str, Any]:
        """Get monitoring status for user"""
        try:
            user_targets = [t for t in self.active_monitors.values() if t.user_id == user_id]
            
            return {
                "total_monitored_content": len(user_targets),
                "monitoring_active": self.monitoring_active,
                "last_check_times": {
                    t.content_id: t.last_checked.isoformat() if t.last_checked else None
                    for t in user_targets
                },
                "platforms_monitored": list(set(
                    platform for t in user_targets for platform in t.platforms
                ))
            }
            
        except Exception as e:
            logger.error(f"Failed to get monitoring status: {str(e)}")
            return {}


# Global protection monitor instance
protection_monitor = ProtectionMonitor()