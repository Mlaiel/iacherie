"""
Instagram Crawler Implementation
===============================

Professional Instagram content crawler for copyright protection and content monitoring.
Integrates with Instagram Basic Display API and Graph API for comprehensive content detection.

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
from urllib.parse import urlparse, urljoin
import hashlib

import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .platform_crawler import PlatformCrawler, CrawlerConfig, ContentMatch, ContentMatchType
from ..fingerprinting.vector_matcher import VectorMatcher


class InstagramCrawler(PlatformCrawler):
    """
    Professional Instagram crawler for content monitoring and copyright protection.
    
    Features:
    - Instagram Graph API integration
    - Web scraping with Selenium for public content
    - Image and video detection
    - Story and Reel monitoring
    - Hashtag and location-based searches
    - User profile analysis
    - Advanced rate limiting and session management
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher: VectorMatcher, 
                 access_token: str = None, app_secret: str = None):
        """
        Initialize Instagram crawler.
        
        Args:
            config: Crawler configuration
            vector_matcher: Vector matching service
            access_token: Instagram Graph API access token
            app_secret: Instagram app secret
        """
        super().__init__(config, vector_matcher)
        self.access_token = access_token
        self.app_secret = app_secret
        self.base_api_url = "https://graph.instagram.com"
        self.base_web_url = "https://www.instagram.com"
        
        # Instagram-specific settings
        self.post_types = ['IMAGE', 'VIDEO', 'CAROUSEL_ALBUM']
        self.max_hashtags_per_search = 30
        self.selenium_driver = None
        
        # Rate limiting for web scraping
        self.scraping_delay = 2.0  # Seconds between requests
        self.max_posts_per_profile = 50
        
        # User agent rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
    
    async def initialize_selenium(self):
        """Initialize Selenium WebDriver for web scraping"""
        if not self.selenium_driver:
            try:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument(f'--user-agent={self.user_agents[0]}')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                self.selenium_driver = webdriver.Chrome(options=chrome_options)
                self.selenium_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                self.logger.info("Selenium WebDriver initialized for Instagram scraping")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize Selenium driver: {str(e)}")
                raise
    
    async def cleanup_selenium(self):
        """Cleanup Selenium WebDriver"""
        if self.selenium_driver:
            try:
                self.selenium_driver.quit()
                self.selenium_driver = None
                self.logger.info("Selenium WebDriver cleaned up")
            except Exception as e:
                self.logger.error(f"Error cleaning up Selenium driver: {str(e)}")
    
    async def search_content(self, search_terms: List[str], 
                           max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Search for content on Instagram using multiple methods.
        
        Args:
            search_terms: Terms to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of found content items
        """
        try:
            all_results = []
            
            # Method 1: API-based search (if access token available)
            if self.access_token:
                api_results = await self._search_via_api(search_terms, max_results // 2)
                all_results.extend(api_results)
            
            # Method 2: Web scraping for hashtags and public content
            web_results = await self._search_via_web_scraping(search_terms, max_results // 2)
            all_results.extend(web_results)
            
            # Remove duplicates based on post URL
            unique_results = {}
            for result in all_results:
                post_url = result.get('url', result.get('permalink', ''))
                if post_url and post_url not in unique_results:
                    unique_results[post_url] = result
            
            final_results = list(unique_results.values())[:max_results]
            
            self.logger.info(f"Instagram search found {len(final_results)} unique posts")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Error in Instagram search: {str(e)}")
            return []
    
    async def extract_content_metadata(self, content_url: str) -> Dict[str, Any]:
        """
        Extract detailed metadata from Instagram content URL.
        
        Args:
            content_url: Instagram post URL
            
        Returns:
            Detailed content metadata
        """
        try:
            # Extract post shortcode from URL
            shortcode = self._extract_post_shortcode(content_url)
            if not shortcode:
                return {}
            
            # Try API first, then web scraping
            metadata = {}
            
            if self.access_token:
                metadata = await self._extract_metadata_via_api(shortcode)
            
            if not metadata:
                metadata = await self._extract_metadata_via_scraping(content_url)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Instagram metadata for {content_url}: {str(e)}")
            return {}
    
    async def download_content_sample(self, content_url: str) -> Optional[bytes]:
        """
        Download content sample for fingerprinting.
        
        Args:
            content_url: Instagram content URL
            
        Returns:
            Content sample data or None
        """
        try:
            # Extract media URLs from post
            metadata = await self.extract_content_metadata(content_url)
            if not metadata:
                return None
            
            # Get media URL (image or video thumbnail)
            media_url = metadata.get('media_url')
            if not media_url:
                # Try thumbnail for videos
                media_url = metadata.get('thumbnail_url')
            
            if not media_url:
                return None
            
            # Download media sample
            async with aiohttp.ClientSession() as session:
                async with session.get(media_url, headers={'User-Agent': self.user_agents[0]}) as response:
                    if response.status == 200:
                        content_data = await response.read()
                        self.logger.debug(f"Downloaded Instagram media sample: {len(content_data)} bytes")
                        return content_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error downloading Instagram sample for {content_url}: {str(e)}")
            return None
    
    async def search_by_hashtag(self, hashtag: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search posts by specific hashtag.
        
        Args:
            hashtag: Hashtag to search (without #)
            max_results: Maximum number of posts to return
            
        Returns:
            List of posts with the hashtag
        """
        try:
            await self.initialize_selenium()
            
            # Clean hashtag
            hashtag = hashtag.lstrip('#').lower()
            hashtag_url = f"{self.base_web_url}/explore/tags/{hashtag}/"
            
            self.selenium_driver.get(hashtag_url)
            await asyncio.sleep(self.scraping_delay)
            
            posts = []
            
            # Scroll and collect posts
            for scroll in range(3):  # Limit scrolling to avoid being blocked
                try:
                    # Find post links
                    post_links = self.selenium_driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
                    
                    for link in post_links[:max_results]:
                        try:
                            post_url = link.get_attribute('href')
                            if post_url and post_url not in [p.get('url') for p in posts]:
                                
                                # Extract basic info from thumbnail
                                img_element = link.find_element(By.TAG_NAME, 'img')
                                post_data = {
                                    'url': post_url,
                                    'shortcode': self._extract_post_shortcode(post_url),
                                    'thumbnail_url': img_element.get_attribute('src'),
                                    'alt_text': img_element.get_attribute('alt'),
                                    'hashtag': hashtag,
                                    'platform': 'instagram',
                                    'discovered_via': 'hashtag_search'
                                }
                                
                                posts.append(post_data)
                                
                                if len(posts) >= max_results:
                                    break
                        
                        except Exception as e:
                            continue
                    
                    if len(posts) >= max_results:
                        break
                    
                    # Scroll down
                    self.selenium_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    await asyncio.sleep(self.scraping_delay)
                    
                except Exception as e:
                    self.logger.error(f"Error during hashtag scrolling: {str(e)}")
                    break
            
            self.logger.info(f"Found {len(posts)} posts for hashtag #{hashtag}")
            return posts
            
        except Exception as e:
            self.logger.error(f"Error searching hashtag #{hashtag}: {str(e)}")
            return []
    
    async def search_by_user(self, username: str, max_results: int = 30) -> List[Dict[str, Any]]:
        """
        Search posts by specific user.
        
        Args:
            username: Instagram username (without @)
            max_results: Maximum number of posts to return
            
        Returns:
            List of user's posts
        """
        try:
            await self.initialize_selenium()
            
            # Clean username
            username = username.lstrip('@').lower()
            profile_url = f"{self.base_web_url}/{username}/"
            
            self.selenium_driver.get(profile_url)
            await asyncio.sleep(self.scraping_delay)
            
            posts = []
            
            # Check if profile exists and is public
            try:
                # Look for private account indicator
                private_indicators = self.selenium_driver.find_elements(By.XPATH, "//*[contains(text(), 'This Account is Private')]")
                if private_indicators:
                    self.logger.warning(f"Profile @{username} is private")
                    return []
                
                # Find post links
                post_links = self.selenium_driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
                
                for link in post_links[:max_results]:
                    try:
                        post_url = link.get_attribute('href')
                        if post_url:
                            
                            # Extract thumbnail info
                            img_element = link.find_element(By.TAG_NAME, 'img')
                            post_data = {
                                'url': post_url,
                                'shortcode': self._extract_post_shortcode(post_url),
                                'thumbnail_url': img_element.get_attribute('src'),
                                'alt_text': img_element.get_attribute('alt'),
                                'author': username,
                                'platform': 'instagram',
                                'discovered_via': 'user_profile'
                            }
                            
                            posts.append(post_data)
                    
                    except Exception as e:
                        continue
                
            except Exception as e:
                self.logger.error(f"Error accessing profile @{username}: {str(e)}")
                return []
            
            self.logger.info(f"Found {len(posts)} posts for user @{username}")
            return posts
            
        except Exception as e:
            self.logger.error(f"Error searching user @{username}: {str(e)}")
            return []
    
    async def get_post_comments(self, post_url: str, max_comments: int = 50) -> List[Dict[str, Any]]:
        """
        Get comments for a specific post.
        
        Args:
            post_url: Instagram post URL
            max_comments: Maximum number of comments to retrieve
            
        Returns:
            List of post comments
        """
        try:
            await self.initialize_selenium()
            
            self.selenium_driver.get(post_url)
            await asyncio.sleep(self.scraping_delay)
            
            comments = []
            
            # Find comment elements
            comment_elements = self.selenium_driver.find_elements(By.XPATH, "//div[@data-testid='comment']")
            
            for comment_elem in comment_elements[:max_comments]:
                try:
                    # Extract comment text
                    comment_text_elem = comment_elem.find_element(By.XPATH, ".//span[contains(@class, 'comment-text')]")
                    comment_text = comment_text_elem.text if comment_text_elem else ""
                    
                    # Extract username
                    username_elem = comment_elem.find_element(By.XPATH, ".//a[contains(@href, '/')]")
                    username = username_elem.text if username_elem else ""
                    
                    if comment_text and username:
                        comments.append({
                            'username': username,
                            'text': comment_text,
                            'timestamp': datetime.utcnow().isoformat()  # Instagram doesn't expose exact timestamps easily
                        })
                
                except Exception as e:
                    continue
            
            return comments
            
        except Exception as e:
            self.logger.error(f"Error getting comments for {post_url}: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _search_via_api(self, search_terms: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search using Instagram Graph API"""
        try:
            if not self.access_token:
                return []
            
            results = []
            
            # Use Graph API to search user's own media (limited scope)
            # This is a simplified implementation - full implementation would require
            # proper app setup and user permissions
            
            api_url = f"{self.base_api_url}/me/media"
            params = {
                'fields': 'id,caption,media_type,media_url,thumbnail_url,permalink,timestamp',
                'access_token': self.access_token,
                'limit': max_results
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get('data', []):
                            # Filter by search terms in caption
                            caption = item.get('caption', '').lower()
                            if any(term.lower() in caption for term in search_terms):
                                results.append({
                                    'id': item.get('id'),
                                    'url': item.get('permalink'),
                                    'caption': item.get('caption'),
                                    'media_type': item.get('media_type'),
                                    'media_url': item.get('media_url'),
                                    'thumbnail_url': item.get('thumbnail_url'),
                                    'timestamp': item.get('timestamp'),
                                    'platform': 'instagram',
                                    'discovered_via': 'api'
                                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in API search: {str(e)}")
            return []
    
    async def _search_via_web_scraping(self, search_terms: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search using web scraping"""
        try:
            results = []
            
            # Search by hashtags derived from search terms
            for term in search_terms[:5]:  # Limit to avoid being blocked
                # Convert term to hashtag format
                hashtag = re.sub(r'[^a-zA-Z0-9]', '', term.lower())
                if len(hashtag) > 2:  # Minimum hashtag length
                    hashtag_results = await self.search_by_hashtag(hashtag, max_results // len(search_terms))
                    results.extend(hashtag_results)
                
                await asyncio.sleep(self.scraping_delay)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in web scraping search: {str(e)}")
            return []
    
    async def _extract_metadata_via_api(self, shortcode: str) -> Dict[str, Any]:
        """Extract metadata using Graph API"""
        try:
            # This would require the post ID, which is different from shortcode
            # In practice, this would need proper Graph API setup
            return {}
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata via API: {str(e)}")
            return {}
    
    async def _extract_metadata_via_scraping(self, post_url: str) -> Dict[str, Any]:
        """Extract metadata using web scraping"""
        try:
            await self.initialize_selenium()
            
            self.selenium_driver.get(post_url)
            await asyncio.sleep(self.scraping_delay)
            
            metadata = {}
            
            try:
                # Extract post data from page
                # Caption
                caption_elements = self.selenium_driver.find_elements(By.XPATH, "//meta[@property='og:description']")
                if caption_elements:
                    metadata['caption'] = caption_elements[0].get_attribute('content')
                
                # Title (usually caption preview)
                title_elements = self.selenium_driver.find_elements(By.XPATH, "//meta[@property='og:title']")
                if title_elements:
                    metadata['title'] = title_elements[0].get_attribute('content')
                
                # Media URL
                media_elements = self.selenium_driver.find_elements(By.XPATH, "//meta[@property='og:image']")
                if media_elements:
                    metadata['media_url'] = media_elements[0].get_attribute('content')
                
                # Video URL (for video posts)
                video_elements = self.selenium_driver.find_elements(By.XPATH, "//meta[@property='og:video']")
                if video_elements:
                    metadata['video_url'] = video_elements[0].get_attribute('content')
                
                # URL
                metadata['url'] = post_url
                metadata['shortcode'] = self._extract_post_shortcode(post_url)
                
                # Extract username from URL or title
                username_match = re.search(r'@(\w+)', metadata.get('title', ''))
                if username_match:
                    metadata['author'] = username_match.group(1)
                
                # Try to extract like count and other metrics
                # Note: Instagram heavily protects this data, so this might not work reliably
                
                metadata['platform'] = 'instagram'
                metadata['extracted_at'] = datetime.utcnow().isoformat()
                
            except Exception as e:
                self.logger.error(f"Error extracting post metadata: {str(e)}")
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error in metadata scraping: {str(e)}")
            return {}
    
    def _extract_post_shortcode(self, url: str) -> Optional[str]:
        """Extract post shortcode from Instagram URL"""
        patterns = [
            r'instagram\.com/p/([A-Za-z0-9_-]+)',
            r'instagram\.com/reel/([A-Za-z0-9_-]+)',
            r'instagram\.com/tv/([A-Za-z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limiting status"""
        return {
            'platform': 'instagram',
            'scraping_delay': self.scraping_delay,
            'max_posts_per_profile': self.max_posts_per_profile,
            'selenium_active': self.selenium_driver is not None,
            'api_available': self.access_token is not None
        }
    
    async def close(self):
        """Cleanup crawler resources"""
        await self.cleanup_selenium()
        await self.cleanup_session()
