"""Instagram Crawling Engine
========================

Advanced Instagram crawler for content discovery, profile analysis, and Stories monitoring.
Handles media extraction, engagement analytics, and monetization tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import json
import hashlib
import time
import random
from urllib.parse import urljoin, urlparse, quote

import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup
import instaloader

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError,
    PrivateContentError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..utils.proxy_manager import ProxyManager
from ..models.content_models import InstagramPost, InstagramProfile, InstagramStory
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class InstagramPostData:
    """Instagram post data structure"""    post_id: str
    shortcode: str
    url: str
    caption: str
    media_type: str  # photo, video, carousel
    media_urls: List[str]
    thumbnail_url: str
    username: str
    user_id: str
    timestamp: datetime
    likes_count: int
    comments_count: int
    view_count: Optional[int]
    is_video: bool
    hashtags: List[str]
    mentions: List[str]
    location: Optional[Dict[str, Any]]
    accessibility_caption: Optional[str]
    is_sponsored: bool = False
    is_paid_partnership: bool = False
    engagement_rate: float = 0.0


@dataclass
class InstagramProfileData:
    """Instagram profile data structure"""    user_id: str
    username: str
    full_name: str
    biography: str
    profile_pic_url: str
    profile_pic_url_hd: str
    external_url: Optional[str]
    followers_count: int
    following_count: int
    posts_count: int
    is_verified: bool
    is_private: bool
    is_business_account: bool
    business_category: Optional[str]
    category_name: Optional[str]
    contact_phone_number: Optional[str]
    business_email: Optional[str]
    business_address: Optional[Dict]
    highlights_count: int
    mutual_followers_count: int = 0
    engagement_rate: float = 0.0
    average_likes: float = 0.0
    average_comments: float = 0.0


@dataclass
class InstagramStoryData:
    """Instagram story data structure"""    story_id: str
    user_id: str
    username: str
    media_type: str  # photo, video
    media_url: str
    thumbnail_url: str
    timestamp: datetime
    expires_at: datetime
    view_count: Optional[int]
    has_audio: bool = False
    duration: Optional[float] = None
    stickers: List[Dict] = None
    music: Optional[Dict] = None
    is_highlight: bool = False


class InstagramCrawlerEngine(BaseCrawlerEngine):
    """    Advanced Instagram crawler engine with comprehensive data extraction.
    
    Features:
    - Profile and post analytics extraction
    - Stories monitoring and archiving
    - Engagement metrics calculation
    - Content protection monitoring
    - Business account insights
    - Rate limiting and proxy rotation
    - Anti-detection mechanisms
    """    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize Instagram crawler engine"""        super().__init__(config)
        self.session = None
        self.loader = None
        self.rate_limiter = RateLimiter(
            requests_per_minute=30,  # Conservative rate limiting
            requests_per_hour=800,
            requests_per_day=5000
        )
        self.cache_manager = CacheManager(
            cache_duration=timedelta(minutes=30),
            max_cache_size=2000
        )
        self.proxy_manager = ProxyManager() if config and config.get('use_proxies') else None
        self._setup_session()
        self._setup_selenium_driver()
        self._setup_instaloader()
    
    def _setup_session(self) -> None:
        """Setup HTTP session with headers and cookies"""        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        logger.info("HTTP session initialized")
    
    def _setup_selenium_driver(self) -> None:
        """Setup Selenium WebDriver with stealth configuration"""        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Anti-detection measures
            chrome_options.add_argument('--disable-plugins-discovery')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-sync')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Execute stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            logger.info("Selenium WebDriver initialized with stealth configuration")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.driver = None
    
    def _setup_instaloader(self) -> None:
        """Setup Instaloader for API-based extraction"""        try:
            self.loader = instaloader.Instaloader(
                download_pictures=False,
                download_videos=False,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False,
                dirname_pattern='',
                filename_pattern=''
            )
            logger.info("Instaloader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Instaloader: {e}")
            self.loader = None
    
    async def get_profile_data(self, username: str) -> Optional[InstagramProfileData]:
        """        Get comprehensive profile data for a user
        
        Args:
            username: Instagram username
            
        Returns:
            Profile data or None if not found
        """        await self.rate_limiter.wait()
        
        cache_key = f"profile_{username.lower()}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Try Instaloader first
            if self.loader:
                profile_data = await self._get_profile_instaloader(username)
                if profile_data:
                    await self.cache_manager.set(cache_key, profile_data)
                    return profile_data
            
            # Fallback to Selenium scraping
            if self.driver:
                profile_data = await self._get_profile_selenium(username)
                if profile_data:
                    await self.cache_manager.set(cache_key, profile_data)
                    return profile_data
            
            raise ContentNotFoundError(f"Profile '{username}' not found or inaccessible")
            
        except Exception as e:
            logger.error(f"Error getting profile data for {username}: {e}")
            raise CrawlerError(f"Failed to get profile data: {e}")
    
    async def get_user_posts(
        self, 
        username: str, 
        max_posts: int = 50,
        include_stories: bool = False
    ) -> List[InstagramPostData]:
        """        Get recent posts from a user's profile
        
        Args:
            username: Instagram username
            max_posts: Maximum number of posts to retrieve
            include_stories: Whether to include story highlights
            
        Returns:
            List of post data
        """        await self.rate_limiter.wait()
        
        try:
            # Try Instaloader first
            if self.loader:
                posts = await self._get_posts_instaloader(username, max_posts)
                if posts:
                    return posts
            
            # Fallback to Selenium scraping
            if self.driver:
                posts = await self._get_posts_selenium(username, max_posts)
                return posts
            
            raise CrawlerError("No extraction method available")
            
        except Exception as e:
            logger.error(f"Error getting posts for {username}: {e}")
            raise CrawlerError(f"Failed to get posts: {e}")
    
    async def get_post_details(self, shortcode: str) -> Optional[InstagramPostData]:
        """        Get detailed information about a specific post
        
        Args:
            shortcode: Instagram post shortcode
            
        Returns:
            Detailed post data
        """        await self.rate_limiter.wait()
        
        cache_key = f"post_{shortcode}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            if self.loader:
                post_data = await self._get_post_details_instaloader(shortcode)
                if post_data:
                    await self.cache_manager.set(cache_key, post_data)
                    return post_data
            
            if self.driver:
                post_data = await self._get_post_details_selenium(shortcode)
                if post_data:
                    await self.cache_manager.set(cache_key, post_data)
                    return post_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting post details for {shortcode}: {e}")
            return None
    
    async def search_hashtag(self, hashtag: str, max_posts: int = 100) -> List[InstagramPostData]:
        """        Search posts by hashtag
        
        Args:
            hashtag: Hashtag to search for (without #)
            max_posts: Maximum number of posts to retrieve
            
        Returns:
            List of posts containing the hashtag
        """        await self.rate_limiter.wait()
        
        try:
            if self.loader:
                return await self._search_hashtag_instaloader(hashtag, max_posts)
            
            if self.driver:
                return await self._search_hashtag_selenium(hashtag, max_posts)
            
            raise CrawlerError("No extraction method available")
            
        except Exception as e:
            logger.error(f"Error searching hashtag #{hashtag}: {e}")
            raise CrawlerError(f"Hashtag search failed: {e}")
    
    async def monitor_stories(self, usernames: List[str]) -> List[InstagramStoryData]:
        """        Monitor stories from multiple users
        
        Args:
            usernames: List of usernames to monitor
            
        Returns:
            List of active stories
        """        stories = []
        
        for username in usernames:
            try:
                await self.rate_limiter.wait()
                user_stories = await self._get_user_stories(username)
                stories.extend(user_stories)
                
                # Add delay between users to avoid detection
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.error(f"Error monitoring stories for {username}: {e}")
                continue
        
        return stories
    
    async def detect_content_theft(
        self, 
        original_content: Dict, 
        search_hashtags: List[str]
    ) -> List[Dict]:
        """        Detect potential content theft using image similarity and metadata
        
        Args:
            original_content: Original content metadata
            search_hashtags: Hashtags to search for potential theft
            
        Returns:
            List of potential theft matches
        """        theft_candidates = []
        
        for hashtag in search_hashtags:
            try:
                posts = await self.search_hashtag(hashtag, max_posts=50)
                
                for post in posts:
                    if post.username.lower() == original_content.get('username', '').lower():
                        continue  # Skip original author's posts
                    
                    similarity_score = await self._calculate_content_similarity(
                        original_content, 
                        asdict(post)
                    )
                    
                    if similarity_score > 0.6:  # 60% similarity threshold
                        theft_candidates.append({
                            'post_data': post,
                            'similarity_score': similarity_score,
                            'detected_at': datetime.now(),
                            'search_hashtag': hashtag,
                            'potential_theft_type': await self._classify_theft_type(original_content, post)
                        })
                        
            except Exception as e:
                logger.error(f"Error detecting theft for hashtag #{hashtag}: {e}")
                continue
        
        return theft_candidates
    
    async def _get_profile_instaloader(self, username: str) -> Optional[InstagramProfileData]:
        """Get profile data using Instaloader"""        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            return InstagramProfileData(
                user_id=str(profile.userid),
                username=profile.username,
                full_name=profile.full_name,
                biography=profile.biography,
                profile_pic_url=profile.profile_pic_url,
                profile_pic_url_hd=profile.profile_pic_url_hd,
                external_url=profile.external_url,
                followers_count=profile.followers,
                following_count=profile.followees,
                posts_count=profile.mediacount,
                is_verified=profile.is_verified,
                is_private=profile.is_private,
                is_business_account=profile.is_business_account,
                business_category=profile.business_category_name,
                highlights_count=len(list(profile.get_highlights())),
                engagement_rate=await self._calculate_engagement_rate(profile)
            )
            
        except Exception as e:
            logger.error(f"Instaloader profile extraction failed for {username}: {e}")
            return None
    
    async def _get_profile_selenium(self, username: str) -> Optional[InstagramProfileData]:
        """Get profile data using Selenium scraping"""        try:
            url = f"https://www.instagram.com/{username}/"
            self.driver.get(url)
            
            # Wait for profile data to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            
            # Add random delay
            await asyncio.sleep(random.uniform(2, 4))
            
            # Extract profile data from page
            profile_data = {}
            
            # Get username and full name
            try:
                profile_data['username'] = username
                full_name_element = self.driver.find_element(
                    By.XPATH, 
                    "//section//h2"
                )
                profile_data['full_name'] = full_name_element.text
            except NoSuchElementError:
                profile_data['full_name'] = username
            
            # Get biography
            try:
                bio_element = self.driver.find_element(
                    By.XPATH,
                    "//section//span[contains(@class, '-vDIg')]"
                )
                profile_data['biography'] = bio_element.text
            except NoSuchElementException:
                profile_data['biography'] = ""
            
            # Get follower counts
            try:
                stats_elements = self.driver.find_elements(
                    By.XPATH,
                    "//section//ul//li//span//span"
                )
                if len(stats_elements) >= 3:
                    profile_data['posts_count'] = self._parse_count(stats_elements[0].text)
                    profile_data['followers_count'] = self._parse_count(stats_elements[1].text)
                    profile_data['following_count'] = self._parse_count(stats_elements[2].text)
            except (NoSuchElementException, IndexError):
                profile_data.update({
                    'posts_count': 0,
                    'followers_count': 0,
                    'following_count': 0
                })
            
            # Get profile picture
            try:
                profile_pic_element = self.driver.find_element(
                    By.XPATH,
                    "//img[contains(@alt, 'profile picture')]"
                )
                profile_data['profile_pic_url'] = profile_pic_element.get_attribute('src')
            except NoSuchElementException:
                profile_data['profile_pic_url'] = ""
            
            # Check if verified
            try:
                self.driver.find_element(
                    By.XPATH,
                    "//span[@title='Verified']"
                )
                profile_data['is_verified'] = True
            except NoSuchElementException:
                profile_data['is_verified'] = False
            
            # Check if private
            try:
                self.driver.find_element(
                    By.XPATH,
                    "//h2[contains(text(), 'This Account is Private')]"
                )
                profile_data['is_private'] = True
            except NoSuchElementException:
                profile_data['is_private'] = False
            
            return InstagramProfileData(
                user_id="selenium_extracted",
                username=profile_data['username'],
                full_name=profile_data['full_name'],
                biography=profile_data['biography'],
                profile_pic_url=profile_data['profile_pic_url'],
                profile_pic_url_hd=profile_data['profile_pic_url'],
                external_url=None,
                followers_count=profile_data['followers_count'],
                following_count=profile_data['following_count'],
                posts_count=profile_data['posts_count'],
                is_verified=profile_data['is_verified'],
                is_private=profile_data['is_private'],
                is_business_account=False,
                business_category=None,
                highlights_count=0
            )
            
        except Exception as e:
            logger.error(f"Selenium profile extraction failed for {username}: {e}")
            return None
    
    async def _get_posts_instaloader(self, username: str, max_posts: int) -> List[InstagramPostData]:
        """Get posts using Instaloader"""        posts = []
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            for post in profile.get_posts():
                if len(posts) >= max_posts:
                    break
                
                post_data = InstagramPostData(
                    post_id=str(post.mediaid),
                    shortcode=post.shortcode,
                    url=f"https://www.instagram.com/p/{post.shortcode}/",
                    caption=post.caption or "",
                    media_type="video" if post.is_video else "photo",
                    media_urls=[post.url],
                    thumbnail_url=post.url,
                    username=post.owner_username,
                    user_id=str(post.owner_id),
                    timestamp=post.date_utc,
                    likes_count=post.likes,
                    comments_count=post.comments,
                    view_count=post.video_view_count if post.is_video else None,
                    is_video=post.is_video,
                    hashtags=re.findall(r'#(\w+)', post.caption or ""),
                    mentions=re.findall(r'@(\w+)', post.caption or ""),
                    location={"name": post.location.name} if post.location else None,
                    accessibility_caption=post.accessibility_caption
                )
                posts.append(post_data)
                
        except Exception as e:
            logger.error(f"Instaloader posts extraction failed for {username}: {e}")
            
        return posts
    
    def _parse_count(self, count_str: str) -> int:
        """Parse Instagram count strings (e.g., '1.2K', '5M')"""        try:
            count_str = count_str.replace(',', '').replace(' ', '')
            if 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1000)
            elif 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1000000)
            else:
                return int(count_str)
        except ValueError:
            return 0
    
    async def _calculate_engagement_rate(self, profile) -> float:
        """Calculate engagement rate for a profile"""        try:
            total_engagement = 0
            post_count = 0
            
            for post in profile.get_posts():
                if post_count >= 12:  # Analyze last 12 posts
                    break
                total_engagement += post.likes + post.comments
                post_count += 1
            
            if post_count == 0 or profile.followers == 0:
                return 0.0
            
            avg_engagement = total_engagement / post_count
            engagement_rate = (avg_engagement / profile.followers) * 100
            return round(engagement_rate, 2)
            
        except Exception:
            return 0.0
    
    async def _calculate_content_similarity(
        self, 
        original: Dict, 
        candidate: Dict
    ) -> float:
        """Calculate similarity between original and candidate content"""        try:
            # Caption similarity
            original_caption = original.get('caption', '').lower()
            candidate_caption = candidate.get('caption', '').lower()
            
            caption_similarity = 0.0
            if original_caption and candidate_caption:
                original_words = set(original_caption.split())
                candidate_words = set(candidate_caption.split())
                if original_words and candidate_words:
                    common_words = original_words.intersection(candidate_words)
                    caption_similarity = len(common_words) / len(original_words.union(candidate_words))
            
            # Hashtag similarity
            original_hashtags = set(original.get('hashtags', []))
            candidate_hashtags = set(candidate.get('hashtags', []))
            
            hashtag_similarity = 0.0
            if original_hashtags and candidate_hashtags:
                common_hashtags = original_hashtags.intersection(candidate_hashtags)
                hashtag_similarity = len(common_hashtags) / len(original_hashtags.union(candidate_hashtags))
            
            # Media type similarity
            media_type_similarity = 1.0 if original.get('media_type') == candidate.get('media_type') else 0.0
            
            # Weighted average
            overall_similarity = (
                caption_similarity * 0.4 +
                hashtag_similarity * 0.4 +
                media_type_similarity * 0.2
            )
            
            return overall_similarity
            
        except Exception as e:
            logger.error(f"Error calculating content similarity: {e}")
            return 0.0
    
    async def _classify_theft_type(self, original: Dict, candidate: InstagramPostData) -> str:
        """Classify the type of potential content theft"""        try:
            # Exact repost
            if original.get('caption', '').strip() == candidate.caption.strip():
                return "exact_repost"
            
            # Hashtag theft (using same hashtags)
            original_hashtags = set(original.get('hashtags', []))
            candidate_hashtags = set(candidate.hashtags)
            
            if len(original_hashtags.intersection(candidate_hashtags)) > len(original_hashtags) * 0.8:
                return "hashtag_theft"
            
            # Caption modification
            if len(candidate.caption) > 0 and original.get('caption'):
                return "modified_caption"
            
            # Media repost
            if original.get('media_type') == candidate.media_type:
                return "media_repost"
            
            return "potential_theft"
            
        except Exception:
            return "unknown"
    
    async def cleanup(self) -> None:
        """Cleanup resources"""        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            if hasattr(self, 'session') and self.session:
                self.session.close()
            await self.cache_manager.cleanup()
            logger.info("Instagram crawler engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            if hasattr(self, 'session') and self.session:
                self.session.close()
        except:
            pass


# Export main class
__all__ = ['InstagramCrawlerEngine', 'InstagramPostData', 'InstagramProfileData', 'InstagramStoryData']
