"""
TikTok Crawler Implementation
============================

Professional TikTok content crawler for copyright protection and content monitoring.
Implements advanced web scraping and API integration for comprehensive video detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized use, 
reproduction, or distribution is strictly prohibited and may result in 
severe legal consequences.
"""

import asyncio
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, urljoin, quote
import hashlib
import random

import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .platform_crawler import PlatformCrawler, CrawlerConfig, ContentMatch, ContentMatchType
from ..fingerprinting.vector_matcher import VectorMatcher


class TikTokCrawler(PlatformCrawler):
    """
    Professional TikTok crawler for content monitoring and copyright protection.
    
    Features:
    - Advanced web scraping with anti-detection measures
    - Hashtag and sound-based searches
    - Video metadata extraction
    - User profile monitoring
    - Trend analysis and viral content detection
    - Mobile and desktop view simulation
    - Rate limiting and session rotation
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher: VectorMatcher):
        """
        Initialize TikTok crawler.
        
        Args:
            config: Crawler configuration
            vector_matcher: Vector matching service
        """
        super().__init__(config, vector_matcher)
        self.base_url = "https://www.tiktok.com"
        self.mobile_base_url = "https://m.tiktok.com"
        
        # TikTok-specific settings
        self.selenium_driver = None
        self.mobile_driver = None
        self.scraping_delay = (3.0, 7.0)  # Random delay range
        self.max_videos_per_user = 50
        self.max_hashtag_videos = 100
        
        # Anti-detection measures
        self.user_agents = [
            # Desktop user agents
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Mobile user agents
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:109.0) Gecko/109.0 Firefox/118.0'
        ]
        
        # TikTok video selectors (may change frequently)
        self.video_selectors = {
            'video_container': '[data-e2e="video-feed-item"]',
            'video_link': 'a[href*="/video/"]',
            'user_link': 'a[href*="/@"]',
            'caption': '[data-e2e="video-desc"]',
            'music': '[data-e2e="video-music"]',
            'hashtags': 'a[href*="/tag/"]',
            'like_count': '[data-e2e="like-count"]',
            'comment_count': '[data-e2e="comment-count"]',
            'share_count': '[data-e2e="share-count"]'
        }
    
    async def initialize_selenium(self, mobile_mode: bool = False):
        """Initialize Selenium WebDriver with anti-detection measures"""
        try:
            chrome_options = Options()
            
            # Anti-detection options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Random user agent
            user_agent = random.choice(self.user_agents)
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            if mobile_mode:
                # Mobile emulation
                mobile_emulation = {
                    "deviceMetrics": {"width": 375, "height": 812, "pixelRatio": 3.0},
                    "userAgent": user_agent
                }
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument('--window-size=375,812')
            else:
                chrome_options.add_argument('--window-size=1920,1080')
            
            # Headless mode for production
            if self.config.platform_name != "tiktok_debug":
                chrome_options.add_argument('--headless')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Add random mouse movements and delays to appear human-like
            driver.implicitly_wait(10)
            
            if mobile_mode:
                self.mobile_driver = driver
                self.logger.info("TikTok mobile Selenium driver initialized")
            else:
                self.selenium_driver = driver
                self.logger.info("TikTok desktop Selenium driver initialized")
            
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TikTok Selenium driver: {str(e)}")
            raise
    
    async def cleanup_selenium(self):
        """Cleanup Selenium WebDriver instances"""
        for driver in [self.selenium_driver, self.mobile_driver]:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    self.logger.error(f"Error cleaning up TikTok driver: {str(e)}")
        
        self.selenium_driver = None
        self.mobile_driver = None
        self.logger.info("TikTok Selenium drivers cleaned up")
    
    async def search_content(self, search_terms: List[str], 
                           max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Search for content on TikTok using multiple strategies.
        
        Args:
            search_terms: Terms to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of found video items
        """
        try:
            all_results = []
            
            # Strategy 1: Hashtag-based search
            hashtag_results = await self._search_by_hashtags(search_terms, max_results // 3)
            all_results.extend(hashtag_results)
            
            # Strategy 2: User-based search (if usernames detected in terms)
            user_results = await self._search_by_users(search_terms, max_results // 3)
            all_results.extend(user_results)
            
            # Strategy 3: General search using TikTok's discover page
            discover_results = await self._search_discover_page(search_terms, max_results // 3)
            all_results.extend(discover_results)
            
            # Remove duplicates based on video URL
            unique_results = {}
            for result in all_results:
                video_url = result.get('url', result.get('video_url', ''))
                if video_url and video_url not in unique_results:
                    unique_results[video_url] = result
            
            final_results = list(unique_results.values())[:max_results]
            
            self.logger.info(f"TikTok search found {len(final_results)} unique videos")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Error in TikTok search: {str(e)}")
            return []
    
    async def extract_content_metadata(self, content_url: str) -> Dict[str, Any]:
        """
        Extract detailed metadata from TikTok video URL.
        
        Args:
            content_url: TikTok video URL
            
        Returns:
            Detailed video metadata
        """
        try:
            # Initialize driver if needed
            if not self.selenium_driver:
                await self.initialize_selenium()
            
            self.selenium_driver.get(content_url)
            await self._random_delay()
            
            metadata = {}
            
            try:
                # Wait for page to load
                WebDriverWait(self.selenium_driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "video"))
                )
                
                # Extract video metadata
                metadata = await self._extract_video_metadata_from_page()
                metadata['url'] = content_url
                metadata['platform'] = 'tiktok'
                metadata['extracted_at'] = datetime.utcnow().isoformat()
                
                # Extract video ID from URL
                video_id = self._extract_video_id(content_url)
                if video_id:
                    metadata['video_id'] = video_id
                
            except TimeoutException:
                self.logger.warning(f"Timeout loading TikTok video: {content_url}")
            except Exception as e:
                self.logger.error(f"Error extracting TikTok metadata: {str(e)}")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting TikTok metadata for {content_url}: {str(e)}")
            return {}
    
    async def download_content_sample(self, content_url: str) -> Optional[bytes]:
        """
        Download video sample for fingerprinting.
        
        Args:
            content_url: TikTok video URL
            
        Returns:
            Video sample data or None
        """
        try:
            # Extract metadata first to get video URL
            metadata = await self.extract_content_metadata(content_url)
            if not metadata:
                return None
            
            # Try to get video download URL (TikTok makes this challenging)
            video_url = metadata.get('video_download_url')
            
            if not video_url:
                # Fallback: try to extract video URL from page source
                video_url = await self._extract_video_download_url(content_url)
            
            if not video_url:
                # Last resort: download thumbnail as sample
                thumbnail_url = metadata.get('thumbnail_url')
                if thumbnail_url:
                    return await self._download_thumbnail(thumbnail_url)
                return None
            
            # Download video sample (first few seconds)
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Referer': 'https://www.tiktok.com/',
                    'Range': 'bytes=0-1048576'  # First 1MB only
                }
                
                async with session.get(video_url, headers=headers) as response:
                    if response.status in [200, 206]:  # 206 for partial content
                        video_data = await response.read()
                        self.logger.debug(f"Downloaded TikTok video sample: {len(video_data)} bytes")
                        return video_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error downloading TikTok sample for {content_url}: {str(e)}")
            return None
    
    async def search_by_hashtag(self, hashtag: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search videos by specific hashtag.
        
        Args:
            hashtag: Hashtag to search (without #)
            max_results: Maximum number of videos to return
            
        Returns:
            List of videos with the hashtag
        """
        try:
            if not self.selenium_driver:
                await self.initialize_selenium()
            
            # Clean hashtag
            hashtag = hashtag.lstrip('#').lower()
            hashtag_url = f"{self.base_url}/tag/{hashtag}"
            
            self.selenium_driver.get(hashtag_url)
            await self._random_delay()
            
            videos = []
            scroll_attempts = 0
            max_scrolls = 5
            
            while len(videos) < max_results and scroll_attempts < max_scrolls:
                try:
                    # Find video containers
                    video_containers = self.selenium_driver.find_elements(By.CSS_SELECTOR, self.video_selectors['video_container'])
                    
                    for container in video_containers:
                        if len(videos) >= max_results:
                            break
                        
                        try:
                            video_data = await self._extract_video_data_from_container(container)
                            if video_data and video_data not in videos:
                                video_data['hashtag'] = hashtag
                                video_data['discovered_via'] = 'hashtag_search'
                                videos.append(video_data)
                        
                        except Exception as e:
                            continue
                    
                    # Scroll down to load more videos
                    if len(videos) < max_results:
                        self.selenium_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        await self._random_delay()
                        scroll_attempts += 1
                    
                except Exception as e:
                    self.logger.error(f"Error during hashtag search scrolling: {str(e)}")
                    break
            
            self.logger.info(f"Found {len(videos)} videos for hashtag #{hashtag}")
            return videos
            
        except Exception as e:
            self.logger.error(f"Error searching hashtag #{hashtag}: {str(e)}")
            return []
    
    async def search_by_user(self, username: str, max_results: int = 30) -> List[Dict[str, Any]]:
        """
        Search videos by specific user.
        
        Args:
            username: TikTok username (without @)
            max_results: Maximum number of videos to return
            
        Returns:
            List of user's videos
        """
        try:
            if not self.selenium_driver:
                await self.initialize_selenium()
            
            # Clean username
            username = username.lstrip('@').lower()
            profile_url = f"{self.base_url}/@{username}"
            
            self.selenium_driver.get(profile_url)
            await self._random_delay()
            
            videos = []
            
            try:
                # Check if profile exists
                WebDriverWait(self.selenium_driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, self.video_selectors['video_container'])),
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'user not found')]"))
                    )
                )
                
                # Check for "user not found" or private account
                error_elements = self.selenium_driver.find_elements(By.XPATH, "//*[contains(text(), 'not found') or contains(text(), 'private')]")
                if error_elements:
                    self.logger.warning(f"TikTok user @{username} not found or private")
                    return []
                
                # Scroll and collect videos
                scroll_attempts = 0
                max_scrolls = 3
                
                while len(videos) < max_results and scroll_attempts < max_scrolls:
                    # Find video containers
                    video_containers = self.selenium_driver.find_elements(By.CSS_SELECTOR, self.video_selectors['video_container'])
                    
                    for container in video_containers:
                        if len(videos) >= max_results:
                            break
                        
                        try:
                            video_data = await self._extract_video_data_from_container(container)
                            if video_data and video_data not in videos:
                                video_data['author'] = username
                                video_data['discovered_via'] = 'user_profile'
                                videos.append(video_data)
                        
                        except Exception as e:
                            continue
                    
                    # Scroll for more videos
                    if len(videos) < max_results:
                        self.selenium_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        await self._random_delay()
                        scroll_attempts += 1
                
            except TimeoutException:
                self.logger.warning(f"Timeout loading TikTok profile @{username}")
                return []
            
            self.logger.info(f"Found {len(videos)} videos for user @{username}")
            return videos
            
        except Exception as e:
            self.logger.error(f"Error searching user @{username}: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _search_by_hashtags(self, search_terms: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search by converting terms to hashtags"""
        results = []
        
        for term in search_terms[:3]:  # Limit to avoid being blocked
            # Convert term to hashtag format
            hashtag = re.sub(r'[^a-zA-Z0-9]', '', term.lower())
            if len(hashtag) > 2:
                hashtag_results = await self.search_by_hashtag(hashtag, max_results // len(search_terms))
                results.extend(hashtag_results)
            
            await self._random_delay()
        
        return results
    
    async def _search_by_users(self, search_terms: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search by detecting usernames in terms"""
        results = []
        
        for term in search_terms:
            # Check if term looks like a username
            if term.startswith('@') or re.match(r'^[a-zA-Z0-9._]+$', term):
                username = term.lstrip('@')
                user_results = await self.search_by_user(username, max_results // len(search_terms))
                results.extend(user_results)
                
                await self._random_delay()
        
        return results
    
    async def _search_discover_page(self, search_terms: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search using TikTok's discover/trending page"""
        try:
            if not self.selenium_driver:
                await self.initialize_selenium()
            
            discover_url = f"{self.base_url}/discover"
            self.selenium_driver.get(discover_url)
            await self._random_delay()
            
            videos = []
            
            # Look for trending or featured videos
            video_containers = self.selenium_driver.find_elements(By.CSS_SELECTOR, self.video_selectors['video_container'])
            
            for container in video_containers[:max_results]:
                try:
                    video_data = await self._extract_video_data_from_container(container)
                    if video_data:
                        video_data['discovered_via'] = 'discover_page'
                        videos.append(video_data)
                
                except Exception as e:
                    continue
            
            return videos
            
        except Exception as e:
            self.logger.error(f"Error searching discover page: {str(e)}")
            return []
    
    async def _extract_video_data_from_container(self, container) -> Optional[Dict[str, Any]]:
        """Extract video data from container element"""
        try:
            video_data = {}
            
            # Video URL
            video_link = container.find_element(By.CSS_SELECTOR, self.video_selectors['video_link'])
            video_data['url'] = video_link.get_attribute('href')
            video_data['video_id'] = self._extract_video_id(video_data['url'])
            
            # User link
            try:
                user_link = container.find_element(By.CSS_SELECTOR, self.video_selectors['user_link'])
                user_url = user_link.get_attribute('href')
                username = re.search(r'/@([^/]+)', user_url)
                if username:
                    video_data['author'] = username.group(1)
            except:
                pass
            
            # Caption/description
            try:
                caption_elem = container.find_element(By.CSS_SELECTOR, self.video_selectors['caption'])
                video_data['caption'] = caption_elem.text
            except:
                video_data['caption'] = ''
            
            # Music info
            try:
                music_elem = container.find_element(By.CSS_SELECTOR, self.video_selectors['music'])
                video_data['music'] = music_elem.text
            except:
                video_data['music'] = ''
            
            # Hashtags
            try:
                hashtag_elements = container.find_elements(By.CSS_SELECTOR, self.video_selectors['hashtags'])
                video_data['hashtags'] = [elem.text.lstrip('#') for elem in hashtag_elements]
            except:
                video_data['hashtags'] = []
            
            # Engagement metrics
            for metric, selector in [
                ('like_count', 'like_count'),
                ('comment_count', 'comment_count'),
                ('share_count', 'share_count')
            ]:
                try:
                    elem = container.find_element(By.CSS_SELECTOR, self.video_selectors[selector])
                    count_text = elem.text
                    video_data[metric] = self._parse_count(count_text)
                except:
                    video_data[metric] = 0
            
            video_data['platform'] = 'tiktok'
            video_data['extracted_at'] = datetime.utcnow().isoformat()
            
            return video_data
            
        except Exception as e:
            self.logger.error(f"Error extracting video data from container: {str(e)}")
            return None
    
    async def _extract_video_metadata_from_page(self) -> Dict[str, Any]:
        """Extract detailed metadata from video page"""
        metadata = {}
        
        try:
            # Try to find JSON-LD structured data
            script_elements = self.selenium_driver.find_elements(By.XPATH, "//script[@type='application/ld+json']")
            for script in script_elements:
                try:
                    json_data = json.loads(script.get_attribute('innerHTML'))
                    if isinstance(json_data, dict) and json_data.get('@type') == 'VideoObject':
                        metadata.update({
                            'title': json_data.get('name', ''),
                            'description': json_data.get('description', ''),
                            'thumbnail_url': json_data.get('thumbnailUrl', ''),
                            'upload_date': json_data.get('uploadDate', ''),
                            'duration': json_data.get('duration', ''),
                            'author': json_data.get('author', {}).get('name', '')
                        })
                        break
                except:
                    continue
            
            # Extract from meta tags if JSON-LD not available
            if not metadata:
                meta_tags = {
                    'og:title': 'title',
                    'og:description': 'description',
                    'og:image': 'thumbnail_url',
                    'og:video': 'video_url'
                }
                
                for property_name, metadata_key in meta_tags.items():
                    try:
                        meta_elem = self.selenium_driver.find_element(By.XPATH, f"//meta[@property='{property_name}']")
                        metadata[metadata_key] = meta_elem.get_attribute('content')
                    except:
                        pass
            
        except Exception as e:
            self.logger.error(f"Error extracting video metadata from page: {str(e)}")
        
        return metadata
    
    async def _extract_video_download_url(self, video_url: str) -> Optional[str]:
        """Attempt to extract video download URL"""
        try:
            # This is complex as TikTok protects video URLs
            # In practice, would need to use specialized tools or APIs
            # This is a placeholder implementation
            
            page_source = self.selenium_driver.page_source
            
            # Look for video URLs in page source
            video_url_patterns = [
                r'"playAddr":"([^"]*)"',
                r'"downloadAddr":"([^"]*)"',
                r'<video[^>]*src="([^"]*)"'
            ]
            
            for pattern in video_url_patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    # Decode URL and return first match
                    video_url = matches[0].replace('\\u0026', '&').replace('\\/', '/')
                    return video_url
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting video download URL: {str(e)}")
            return None
    
    async def _download_thumbnail(self, thumbnail_url: str) -> Optional[bytes]:
        """Download video thumbnail"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Referer': 'https://www.tiktok.com/'
                }
                
                async with session.get(thumbnail_url, headers=headers) as response:
                    if response.status == 200:
                        return await response.read()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error downloading thumbnail: {str(e)}")
            return None
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from TikTok URL"""
        patterns = [
            r'tiktok\.com/@[^/]+/video/(\d+)',
            r'tiktok\.com/t/([A-Za-z0-9]+)',
            r'vm\.tiktok\.com/([A-Za-z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _parse_count(self, count_text: str) -> int:
        """Parse engagement count from text (e.g., '1.2K' -> 1200)"""
        try:
            count_text = count_text.strip().upper()
            
            if 'K' in count_text:
                return int(float(count_text.replace('K', '')) * 1000)
            elif 'M' in count_text:
                return int(float(count_text.replace('M', '')) * 1000000)
            elif 'B' in count_text:
                return int(float(count_text.replace('B', '')) * 1000000000)
            else:
                return int(count_text)
        
        except:
            return 0
    
    async def _random_delay(self):
        """Apply random delay to appear human-like"""
        delay = random.uniform(self.scraping_delay[0], self.scraping_delay[1])
        await asyncio.sleep(delay)
    
    def get_anti_detection_status(self) -> Dict[str, Any]:
        """Get anti-detection measures status"""
        return {
            'platform': 'tiktok',
            'user_agents_count': len(self.user_agents),
            'scraping_delay_range': self.scraping_delay,
            'desktop_driver_active': self.selenium_driver is not None,
            'mobile_driver_active': self.mobile_driver is not None,
            'max_videos_per_user': self.max_videos_per_user,
            'max_hashtag_videos': self.max_hashtag_videos
        }
    
    async def close(self):
        """Cleanup crawler resources"""
        await self.cleanup_selenium()
        await self.cleanup_session()
