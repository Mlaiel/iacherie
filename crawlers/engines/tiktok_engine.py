"""TikTok Crawling Engine
=====================

Advanced TikTok crawler for viral content discovery, user analytics, and trend monitoring.
Handles video metadata extraction, hashtag tracking, and engagement analysis.

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
import base64
from urllib.parse import urljoin, urlparse, quote, unquote

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
import playwright
from playwright.async_api import async_playwright

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError,
    GeoBlockedError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..utils.proxy_manager import ProxyManager
from ..utils.stealth_manager import StealthManager
from ..models.content_models import TikTokVideo, TikTokUser, TikTokChallenge
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class TikTokVideoData:
    """TikTok video data structure"""    video_id: str
    url: str
    description: str
    username: str
    user_id: str
    nickname: str
    video_url: str
    cover_image_url: str
    dynamic_cover_url: str
    timestamp: datetime
    duration: float
    width: int
    height: int
    likes_count: int
    comments_count: int
    shares_count: int
    plays_count: int
    download_count: int
    hashtags: List[str]
    mentions: List[str]
    effects: List[Dict]
    music: Optional[Dict]
    is_ad: bool = False
    is_duet: bool = False
    is_stitch: bool = False
    original_video_id: Optional[str] = None
    engagement_rate: float = 0.0
    virality_score: float = 0.0


@dataclass
class TikTokUserData:
    """TikTok user data structure"""    user_id: str
    unique_id: str
    nickname: str
    signature: str
    avatar_url: str
    avatar_medium_url: str
    avatar_large_url: str
    followers_count: int
    following_count: int
    likes_count: int
    videos_count: int
    is_verified: bool
    is_private: bool
    custom_verify: str
    commerce_info: Optional[Dict]
    relation: int
    open_favorite: bool
    comment_setting: int
    duet_setting: int
    stitch_setting: int
    download_setting: int
    profile_tab_type: int
    language: str
    region: str
    engagement_rate: float = 0.0
    growth_rate: float = 0.0
    average_views: float = 0.0


@dataclass
class TikTokChallengeData:
    """TikTok challenge/hashtag data structure"""    challenge_id: str
    title: str
    description: str
    cover_image_url: str
    video_count: int
    view_count: int
    is_commerce: bool
    hashtag: str
    stats: Dict[str, Any]
    music: Optional[Dict]
    created_time: datetime
    trend_rank: Optional[int] = None


class TikTokCrawlerEngine(BaseCrawlerEngine):
    """    Advanced TikTok crawler engine with comprehensive data extraction.
    
    Features:
    - Video and user analytics extraction
    - Hashtag and challenge monitoring
    - Viral content detection
    - Trend analysis and prediction
    - Music and effect tracking
    - Rate limiting and geo-spoofing
    - Anti-detection mechanisms
    """    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize TikTok crawler engine"""        super().__init__(config)
        self.session = None
        self.playwright_page = None
        self.rate_limiter = RateLimiter(
            requests_per_minute=20,  # Very conservative for TikTok
            requests_per_hour=400,
            requests_per_day=2000
        )
        self.cache_manager = CacheManager(
            cache_duration=timedelta(minutes=15),
            max_cache_size=3000
        )
        self.proxy_manager = ProxyManager() if config and config.get('use_proxies') else None
        self.stealth_manager = StealthManager()
        self._setup_session()
        self._setup_selenium_driver()
    
    def _setup_session(self) -> None:
        """Setup HTTP session with TikTok-specific headers"""        self.session = requests.Session()
        
        # TikTok-specific headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.tiktok.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest',
        })
        
        logger.info("TikTok HTTP session initialized")
    
    def _setup_selenium_driver(self) -> None:
        """Setup Selenium WebDriver with TikTok-optimized stealth"""        try:
            chrome_options = webdriver.ChromeOptions()
            
            # Basic stealth options
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # TikTok-specific anti-detection
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--ignore-certificate-errors')
            
            # Mobile user agent (TikTok mobile is less restricted)
            mobile_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
            chrome_options.add_argument(f'--user-agent={mobile_ua}')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Advanced stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            logger.info("TikTok Selenium WebDriver initialized with stealth configuration")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.driver = None
    
    async def _setup_playwright(self) -> None:
        """Setup Playwright for advanced scraping"""        try:
            playwright_instance = await async_playwright().start()
            browser = await playwright_instance.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
                viewport={'width': 375, 'height': 812},  # iPhone viewport
                device_scale_factor=3,
                is_mobile=True,
                has_touch=True
            )
            
            self.playwright_page = await context.new_page()
            
            # Add stealth scripts
            await self.playwright_page.add_init_script("""                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            
            logger.info("Playwright initialized for TikTok scraping")
            
        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {e}")
            self.playwright_page = None
    
    async def get_user_profile(self, username: str) -> Optional[TikTokUserData]:
        """        Get comprehensive user profile data
        
        Args:
            username: TikTok username (with or without @)
            
        Returns:
            User profile data or None if not found
        """        await self.rate_limiter.wait()
        
        username = username.lstrip('@')  # Remove @ if present
        cache_key = f"user_{username.lower()}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Try web scraping first
            if self.driver:
                user_data = await self._get_user_selenium(username)
                if user_data:
                    await self.cache_manager.set(cache_key, user_data)
                    return user_data
            
            # Try Playwright as fallback
            if not self.playwright_page:
                await self._setup_playwright()
            
            if self.playwright_page:
                user_data = await self._get_user_playwright(username)
                if user_data:
                    await self.cache_manager.set(cache_key, user_data)
                    return user_data
            
            raise ContentNotFoundError(f"User '@{username}' not found or inaccessible")
            
        except Exception as e:
            logger.error(f"Error getting user profile for @{username}: {e}")
            raise CrawlerError(f"Failed to get user profile: {e}")
    
    async def get_user_videos(
        self, 
        username: str, 
        max_videos: int = 50
    ) -> List[TikTokVideoData]:
        """        Get recent videos from a user's profile
        
        Args:
            username: TikTok username
            max_videos: Maximum number of videos to retrieve
            
        Returns:
            List of video data
        """        await self.rate_limiter.wait()
        
        username = username.lstrip('@')
        
        try:
            if self.driver:
                videos = await self._get_user_videos_selenium(username, max_videos)
                if videos:
                    return videos
            
            if not self.playwright_page:
                await self._setup_playwright()
                
            if self.playwright_page:
                videos = await self._get_user_videos_playwright(username, max_videos)
                return videos
            
            raise CrawlerError("No extraction method available")
            
        except Exception as e:
            logger.error(f"Error getting videos for @{username}: {e}")
            raise CrawlerError(f"Failed to get videos: {e}")
    
    async def search_hashtag(self, hashtag: str, max_videos: int = 100) -> List[TikTokVideoData]:
        """        Search videos by hashtag
        
        Args:
            hashtag: Hashtag to search for (without #)
            max_videos: Maximum number of videos to retrieve
            
        Returns:
            List of videos with the hashtag
        """        await self.rate_limiter.wait()
        
        hashtag = hashtag.lstrip('#')  # Remove # if present
        
        try:
            if self.driver:
                return await self._search_hashtag_selenium(hashtag, max_videos)
            
            if not self.playwright_page:
                await self._setup_playwright()
                
            if self.playwright_page:
                return await self._search_hashtag_playwright(hashtag, max_videos)
            
            raise CrawlerError("No extraction method available")
            
        except Exception as e:
            logger.error(f"Error searching hashtag #{hashtag}: {e}")
            raise CrawlerError(f"Hashtag search failed: {e}")
    
    async def get_trending_hashtags(self, country: str = 'US') -> List[TikTokChallengeData]:
        """        Get trending hashtags/challenges
        
        Args:
            country: Country code for regional trends
            
        Returns:
            List of trending challenges
        """        await self.rate_limiter.wait()
        
        try:
            if self.driver:
                return await self._get_trending_selenium(country)
            
            if not self.playwright_page:
                await self._setup_playwright()
                
            if self.playwright_page:
                return await self._get_trending_playwright(country)
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting trending hashtags: {e}")
            return []
    
    async def detect_viral_content(
        self, 
        hashtags: List[str], 
        min_views: int = 100000
    ) -> List[TikTokVideoData]:
        """        Detect potentially viral content
        
        Args:
            hashtags: List of hashtags to monitor
            min_views: Minimum view count for viral consideration
            
        Returns:
            List of viral video candidates
        """        viral_videos = []
        
        for hashtag in hashtags:
            try:
                videos = await self.search_hashtag(hashtag, max_videos=20)
                
                for video in videos:
                    # Calculate virality score
                    virality_score = await self._calculate_virality_score(video)
                    video.virality_score = virality_score
                    
                    if video.plays_count >= min_views and virality_score > 0.7:
                        viral_videos.append(video)
                        
                # Add delay between hashtag searches
                await asyncio.sleep(random.uniform(3, 6))
                
            except Exception as e:
                logger.error(f"Error detecting viral content for #{hashtag}: {e}")
                continue
        
        # Sort by virality score
        viral_videos.sort(key=lambda x: x.virality_score, reverse=True)
        return viral_videos[:50]  # Return top 50
    
    async def monitor_content_theft(
        self, 
        original_video: Dict, 
        search_terms: List[str]
    ) -> List[Dict]:
        """        Monitor for potential content theft
        
        Args:
            original_video: Original video metadata
            search_terms: Terms to search for potential copies
            
        Returns:
            List of potential theft matches
        """        theft_candidates = []
        
        for term in search_terms:
            try:
                # Search by description keywords
                videos = await self._search_by_description(term, max_results=30)
                
                for video in videos:
                    if video.username.lower() == original_video.get('username', '').lower():
                        continue  # Skip original author
                    
                    similarity_score = await self._calculate_video_similarity(
                        original_video,
                        asdict(video)
                    )
                    
                    if similarity_score > 0.5:  # 50% similarity threshold
                        theft_candidates.append({
                            'video_data': video,
                            'similarity_score': similarity_score,
                            'detected_at': datetime.now(),
                            'search_term': term,
                            'theft_type': await self._classify_theft_type(original_video, video)
                        })
                        
            except Exception as e:
                logger.error(f"Error monitoring content theft for term '{term}': {e}")
                continue
        
        return theft_candidates
    
    async def _get_user_selenium(self, username: str) -> Optional[TikTokUserData]:
        """Get user data using Selenium"""        try:
            url = f"https://www.tiktok.com/@{username}"
            self.driver.get(url)
            
            # Wait for profile to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='user-page']"))
            )
            
            # Add random delay
            await asyncio.sleep(random.uniform(3, 6))
            
            # Extract user data
            user_data = {}
            
            # Get username and nickname
            try:
                nickname_element = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "[data-e2e='user-title']"
                )
                user_data['nickname'] = nickname_element.text
            except NoSuchElementException:
                user_data['nickname'] = username
            
            # Get bio/signature
            try:
                bio_element = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "[data-e2e='user-bio']"
                )
                user_data['signature'] = bio_element.text
            except NoSuchElementException:
                user_data['signature'] = ""
            
            # Get follower counts
            try:
                stats_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "[data-e2e='followers-count'], [data-e2e='following-count'], [data-e2e='likes-count']"
                )
                
                if len(stats_elements) >= 3:
                    user_data['followers_count'] = self._parse_tiktok_count(stats_elements[0].text)
                    user_data['following_count'] = self._parse_tiktok_count(stats_elements[1].text)
                    user_data['likes_count'] = self._parse_tiktok_count(stats_elements[2].text)
            except (NoSuchElementException, IndexError):
                user_data.update({
                    'followers_count': 0,
                    'following_count': 0,
                    'likes_count': 0
                })
            
            # Get avatar
            try:
                avatar_element = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "[data-e2e='user-avatar'] img"
                )
                user_data['avatar_url'] = avatar_element.get_attribute('src')
            except NoSuchElementException:
                user_data['avatar_url'] = ""
            
            # Check if verified
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR,
                    "[data-e2e='user-verified']"
                )
                user_data['is_verified'] = True
            except NoSuchElementException:
                user_data['is_verified'] = False
            
            return TikTokUserData(
                user_id="selenium_extracted",
                unique_id=username,
                nickname=user_data['nickname'],
                signature=user_data['signature'],
                avatar_url=user_data['avatar_url'],
                avatar_medium_url=user_data['avatar_url'],
                avatar_large_url=user_data['avatar_url'],
                followers_count=user_data['followers_count'],
                following_count=user_data['following_count'],
                likes_count=user_data['likes_count'],
                videos_count=0,  # Would need separate extraction
                is_verified=user_data['is_verified'],
                is_private=False,  # Default assumption
                custom_verify="",
                relation=0,
                open_favorite=False,
                comment_setting=0,
                duet_setting=0,
                stitch_setting=0,
                download_setting=0,
                profile_tab_type=0,
                language="en",
                region="US"
            )
            
        except Exception as e:
            logger.error(f"Selenium user extraction failed for @{username}: {e}")
            return None
    
    async def _get_user_videos_selenium(self, username: str, max_videos: int) -> List[TikTokVideoData]:
        """Get user videos using Selenium"""        videos = []
        
        try:
            url = f"https://www.tiktok.com/@{username}"
            self.driver.get(url)
            
            # Wait for videos to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='user-post-item']"))
            )
            
            # Scroll to load more videos
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scroll_attempts = 5
            
            while len(videos) < max_videos and scroll_attempts < max_scroll_attempts:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait for new content
                await asyncio.sleep(random.uniform(2, 4))
                
                # Get video elements
                video_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "[data-e2e='user-post-item']"
                )
                
                for element in video_elements[len(videos):]:
                    if len(videos) >= max_videos:
                        break
                    
                    try:
                        # Extract video data
                        video_link = element.find_element(By.TAG_NAME, "a")
                        video_url = video_link.get_attribute('href')
                        
                        # Extract video ID from URL
                        video_id = video_url.split('/')[-1] if video_url else ""
                        
                        # Get thumbnail
                        img_element = element.find_element(By.TAG_NAME, "img")
                        thumbnail_url = img_element.get_attribute('src')
                        
                        # Get view count if available
                        try:
                            view_element = element.find_element(
                                By.CSS_SELECTOR,
                                "[data-e2e='video-view-count']"
                            )
                            view_count = self._parse_tiktok_count(view_element.text)
                        except NoSuchElementException:
                            view_count = 0
                        
                        video_data = TikTokVideoData(
                            video_id=video_id,
                            url=video_url,
                            description="",  # Would need individual video page visit
                            username=username,
                            user_id="selenium_extracted",
                            nickname=username,
                            video_url=video_url,
                            cover_image_url=thumbnail_url,
                            dynamic_cover_url=thumbnail_url,
                            timestamp=datetime.now(),  # Approximation
                            duration=0.0,  # Would need video analysis
                            width=0,
                            height=0,
                            likes_count=0,  # Would need individual extraction
                            comments_count=0,
                            shares_count=0,
                            plays_count=view_count,
                            download_count=0,
                            hashtags=[],
                            mentions=[],
                            effects=[],
                            music=None
                        )
                        
                        videos.append(video_data)
                        
                    except Exception as e:
                        logger.warning(f"Error extracting video data: {e}")
                        continue
                
                # Check if page height changed
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                    last_height = new_height
            
        except Exception as e:
            logger.error(f"Error getting videos for @{username}: {e}")
        
        return videos
    
    def _parse_tiktok_count(self, count_str: str) -> int:
        """Parse TikTok count strings (e.g., '1.2K', '5.6M', '123.4K')"""        try:
            count_str = count_str.replace(' ', '').upper()
            
            if 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1000)
            elif 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1000000)
            elif 'B' in count_str:
                return int(float(count_str.replace('B', '')) * 1000000000)
            else:
                return int(count_str)
                
        except (ValueError, AttributeError):
            return 0
    
    async def _calculate_virality_score(self, video: TikTokVideoData) -> float:
        """Calculate virality score based on engagement metrics"""        try:
            # Basic virality factors
            total_engagements = video.likes_count + video.comments_count + video.shares_count
            
            if video.plays_count == 0:
                return 0.0
            
            # Engagement rate
            engagement_rate = total_engagements / video.plays_count
            
            # Time factor (newer videos get bonus)
            time_since_post = datetime.now() - video.timestamp
            time_factor = max(0, 1 - (time_since_post.days / 7))  # Decay over a week
            
            # Share factor (shares indicate viral potential)
            share_factor = min(1.0, video.shares_count / max(1, video.plays_count) * 100)
            
            # Comments factor (high engagement indicator)
            comment_factor = min(1.0, video.comments_count / max(1, video.plays_count) * 50)
            
            # Weighted score
            virality_score = (
                engagement_rate * 0.4 +
                time_factor * 0.2 +
                share_factor * 0.25 +
                comment_factor * 0.15
            )
            
            return min(1.0, virality_score)
            
        except Exception as e:
            logger.error(f"Error calculating virality score: {e}")
            return 0.0
    
    async def _calculate_video_similarity(self, original: Dict, candidate: Dict) -> float:
        """Calculate similarity between original and candidate videos"""        try:
            # Description similarity
            original_desc = original.get('description', '').lower()
            candidate_desc = candidate.get('description', '').lower()
            
            desc_similarity = 0.0
            if original_desc and candidate_desc:
                original_words = set(original_desc.split())
                candidate_words = set(candidate_desc.split())
                if original_words and candidate_words:
                    common_words = original_words.intersection(candidate_words)
                    desc_similarity = len(common_words) / len(original_words.union(candidate_words))
            
            # Hashtag similarity
            original_hashtags = set(original.get('hashtags', []))
            candidate_hashtags = set(candidate.get('hashtags', []))
            
            hashtag_similarity = 0.0
            if original_hashtags and candidate_hashtags:
                common_hashtags = original_hashtags.intersection(candidate_hashtags)
                hashtag_similarity = len(common_hashtags) / len(original_hashtags.union(candidate_hashtags))
            
            # Duration similarity (videos of similar length)
            duration_similarity = 0.0
            original_duration = original.get('duration', 0)
            candidate_duration = candidate.get('duration', 0)
            
            if original_duration > 0 and candidate_duration > 0:
                duration_diff = abs(original_duration - candidate_duration)
                max_duration = max(original_duration, candidate_duration)
                duration_similarity = 1 - (duration_diff / max_duration)
            
            # Music similarity
            music_similarity = 0.0
            original_music = original.get('music', {})
            candidate_music = candidate.get('music', {})
            
            if original_music and candidate_music:
                if original_music.get('id') == candidate_music.get('id'):
                    music_similarity = 1.0
                elif original_music.get('title') == candidate_music.get('title'):
                    music_similarity = 0.7
            
            # Weighted average
            overall_similarity = (
                desc_similarity * 0.3 +
                hashtag_similarity * 0.3 +
                duration_similarity * 0.2 +
                music_similarity * 0.2
            )
            
            return overall_similarity
            
        except Exception as e:
            logger.error(f"Error calculating video similarity: {e}")
            return 0.0
    
    async def _classify_theft_type(self, original: Dict, candidate: TikTokVideoData) -> str:
        """Classify the type of potential content theft"""        try:
            # Exact repost
            if original.get('description', '').strip() == candidate.description.strip():
                return "exact_repost"
            
            # Music duplication
            if original.get('music', {}).get('id') == candidate.music.get('id') if candidate.music else None:
                return "music_duplication"
            
            # Hashtag theft
            original_hashtags = set(original.get('hashtags', []))
            candidate_hashtags = set(candidate.hashtags)
            
            if len(original_hashtags.intersection(candidate_hashtags)) > len(original_hashtags) * 0.8:
                return "hashtag_theft"
            
            # Concept theft (similar description)
            if candidate.description and original.get('description'):
                return "concept_theft"
            
            return "potential_theft"
            
        except Exception:
            return "unknown"
    
    async def cleanup(self) -> None:
        """Cleanup resources"""        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            if hasattr(self, 'session') and self.session:
                self.session.close()
            if hasattr(self, 'playwright_page') and self.playwright_page:
                await self.playwright_page.close()
            await self.cache_manager.cleanup()
            logger.info("TikTok crawler engine cleanup completed")
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
__all__ = ['TikTokCrawlerEngine', 'TikTokVideoData', 'TikTokUserData', 'TikTokChallengeData']
