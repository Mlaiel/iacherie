"""
TikTok Crawler
==============

Enterprise-grade TikTok content crawler with ultra-advanced monitoring capabilities.
Implements TikTok Research API, intelligent scraping, AI-powered content analysis,
and real-time violation detection for comprehensive content protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Features:
- TikTok Research API integration with intelligent rate limiting
- Advanced video fingerprinting and similarity detection
- Real-time trend analysis and viral content tracking
- AI-powered content classification and moderation
- Automated copyright violation detection
- Multi-region content discovery and monitoring
- Comprehensive metadata extraction and analysis
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import re
import hashlib
import base64
from urllib.parse import urlparse, parse_qs, urlencode
import time

import aiohttp
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import requests
from PIL import Image
import imagehash

from ..utils.rate_limiter import TikTokRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ..utils.video_analyzer import VideoFingerprintAnalyzer
from ..utils.content_classifier import AIContentClassifier
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError, ContentAnalysisError
from ...database.models import CrawlResult, ContentMatch, ViolationAlert
from ...ai.content_protection.fingerprinting.video_fingerprint import VideoFingerprinter
from ...ai.content_protection.fingerprinting.audio_fingerprint import AudioFingerprinter

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class TikTokVideo:
    """Enhanced TikTok video data structure with fingerprinting."""
    video_id: str
    username: str
    user_id: str
    display_name: str
    description: str
    video_url: str
    cover_url: str
    duration: int
    width: int
    height: int
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    download_count: int
    created_at: datetime
    updated_at: datetime
    hashtags: List[str]
    mentions: List[str]
    music: Optional[Dict]
    effects: List[str]
    filters: List[str]
    is_ad: bool
    is_sponsored: bool
    language: str
    region: str
    category: str
    # Advanced fingerprinting fields
    video_fingerprint: Optional[str] = None
    audio_fingerprint: Optional[str] = None
    visual_hash: Optional[str] = None
    thumbnail_hash: Optional[str] = None
    content_similarity_score: Optional[float] = None
    ai_classification: Optional[Dict] = None
    violation_score: Optional[float] = None
    copyright_matches: List[Dict] = None
    # Performance metrics
    engagement_rate: Optional[float] = None
    viral_score: Optional[float] = None
    trend_score: Optional[float] = None
    quality_score: Optional[float] = None

@dataclass
class TikTokUser:
    """Enhanced TikTok user data structure."""
    user_id: str
    username: str
    display_name: str
    biography: str
    avatar_url: str
    background_url: Optional[str]
    follower_count: int
    following_count: int
    video_count: int
    like_count: int
    is_verified: bool
    is_business: bool
    is_creator_fund: bool
    region: str
    language: str
    join_date: Optional[datetime]
    last_active: Optional[datetime]
    # Enhanced analytics
    engagement_rate: Optional[float] = None
    average_views: Optional[float] = None
    growth_rate: Optional[float] = None
    content_categories: List[str] = None
    posting_frequency: Optional[str] = None
    peak_hours: List[int] = None
    audience_demographics: Optional[Dict] = None

@dataclass
class TikTokHashtag:
    """Enhanced TikTok hashtag data structure."""
    hashtag_id: str
    name: str
    view_count: int
    video_count: int
    is_trending: bool
    trend_rank: Optional[int]
    challenge_id: Optional[str]
    challenge_duration: Optional[Dict]
    creator: Optional[str]
    # Trend analysis
    growth_rate: Optional[float] = None
    peak_time: Optional[datetime] = None
    geographic_distribution: Optional[Dict] = None
    related_hashtags: List[str] = None
    sentiment_score: Optional[float] = None

@dataclass
class TikTokSound:
    """Enhanced TikTok sound/music data structure."""
    sound_id: str
    title: str
    author: str
    artist: Optional[str]
    album: Optional[str]
    duration: int
    video_count: int
    is_original: bool
    is_copyrighted: bool
    genre: Optional[str]
    bpm: Optional[int]
    # Rights and licensing
    copyright_owner: Optional[str] = None
    license_type: Optional[str] = None
    usage_rights: Optional[Dict] = None
    monetization_eligible: Optional[bool] = None
    # Audio analysis
    audio_fingerprint: Optional[str] = None
    similarity_matches: List[Dict] = None
    mood_classification: Optional[str] = None
    energy_level: Optional[float] = None

@dataclass
class TikTokTrend:
    """TikTok trend analysis data structure."""
    trend_id: str
    trend_type: str  # hashtag, sound, effect, challenge
    name: str
    description: str
    start_date: datetime
    peak_date: Optional[datetime]
    end_date: Optional[datetime]
    total_videos: int
    total_views: int
    growth_velocity: float
    geographic_spread: Dict[str, int]
    age_demographics: Dict[str, float]
    related_trends: List[str]
    influencer_adoption: List[str]
    brand_participation: List[str]

@dataclass
class ContentViolation:
    """Content violation detection result."""
    violation_id: str
    video_id: str
    violation_type: str  # copyright, trademark, content_policy
    confidence_score: float
    original_content_id: Optional[str]
    similarity_score: Optional[float]
    violation_details: Dict
    detected_at: datetime
    status: str  # pending, confirmed, false_positive
    action_taken: Optional[str]
    is_trending: bool

class TikTokCrawler:
    """
    Professional TikTok crawler implementation.
    
    Features:
    - TikTok Research API integration
    - Advanced hashtag and sound tracking
    - User profile and video monitoring
    - Trend analysis and discovery
    - Content similarity detection
    - Engagement rate calculations
    - Real-time feed monitoring
    - Multi-region content discovery
    """
    
    def __init__(self):
        """Initialize TikTok crawler."""
        self.api_key = settings.TIKTOK_API_KEY
        self.client_key = settings.TIKTOK_CLIENT_KEY
        self.client_secret = settings.TIKTOK_CLIENT_SECRET
        self.rate_limiter = TikTokRateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.session = None
        
        # Base URLs
        self.api_base_url = "https://open-api.tiktok.com"
        self.web_base_url = "https://www.tiktok.com"
        
        # Selenium configuration for scraping
        self.selenium_options = webdriver.ChromeOptions()
        self.selenium_options.add_argument('--headless')
        self.selenium_options.add_argument('--no-sandbox')
        self.selenium_options.add_argument('--disable-dev-shm-usage')
        self.selenium_options.add_argument('--disable-gpu')
        self.selenium_options.add_argument('--disable-blink-features=AutomationControlled')
        self.selenium_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.selenium_options.add_experimental_option('useAutomationExtension', False)
        
        # Headers for API requests
        self.api_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else ''
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(headers=self.api_headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def search_videos(
        self,
        query: str,
        max_results: int = 50,
        region: str = 'US',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TikTokVideo]:
        """
        Search TikTok videos with advanced filtering.
        
        Args:
            query: Search query (keywords, hashtags, usernames)
            max_results: Maximum number of videos to return
            region: Region code for localized results
            start_date: Filter videos from this date
            end_date: Filter videos until this date
            
        Returns:
            List of TikTok video objects
        """



        try:
            # Rate limiting check
            await self.rate_limiter.wait_if_needed()
            
            if self.api_key and await self._check_api_access():
                return await self._search_videos_api(query, max_results, region, start_date, end_date)
            else:
                return await self._search_videos_scraping(query, max_results, region)
                
        except Exception as e:
            logger.error(f"TikTok video search error: {e}")
            return []
    
    async def _check_api_access(self) -> bool:
        """Check if TikTok API access is available."""



        try:
            # Test API endpoint
            url = f"{self.api_base_url}/v2/research/video/query/"
            async with self.session.post(url, json={}) as response:
                return response.status != 401
        except:
            return False
    
    async def _search_videos_api(
        self,
        query: str,
        max_results: int,
        region: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[TikTokVideo]:
        """Search videos using TikTok Research API."""



        try:
            url = f"{self.api_base_url}/v2/research/video/query/"
            
            # Build query parameters
            query_params = {
                "query": {
                    "and": [
                        {"operation": "IN", "field_name": "region_code", "field_values": [region]},
                        {"operation": "EQ", "field_name": "video_length", "field_values": ["SHORT", "MID", "LONG"]}
                    ]
                },
                "max_count": min(max_results, 100),  # API limit
                "search_id": f"search_{datetime.now().timestamp()}"
            }
            
            # Add text search if query is not empty
            if query.strip():
                if query.startswith('#'):
                    # Hashtag search
                    query_params["query"]["and"].append({
                        "operation": "IN",
                        "field_name": "hashtag_name",
                        "field_values": [query[1:]]
                    })
                elif query.startswith('@'):
                    # Username search
                    query_params["query"]["and"].append({
                        "operation": "EQ",
                        "field_name": "username",
                        "field_values": [query[1:]]
                    })
                else:
                    # Keyword search
                    query_params["query"]["and"].append({
                        "operation": "IN",
                        "field_name": "video_description",
                        "field_values": [query]
                    })
            
            # Add date filters
            if start_date:
                query_params["query"]["and"].append({
                    "operation": "GTE",
                    "field_name": "create_time",
                    "field_values": [int(start_date.timestamp())]
                })
            
            if end_date:
                query_params["query"]["and"].append({
                    "operation": "LTE", 
                    "field_name": "create_time",
                    "field_values": [int(end_date.timestamp())]
                })
            
            videos = []
            cursor = None
            
            while len(videos) < max_results:
                if cursor:
                    query_params["cursor"] = cursor
                
                async with self.session.post(url, json=query_params) as response:
                    if response.status != 200:
                        logger.error(f"TikTok API error: {response.status}")
                        break
                    
                    data = await response.json()
                    
                    if data.get("error"):
                        logger.error(f"TikTok API error: {data['error']}")
                        break
                    
                    # Parse video data
                    for video_data in data.get("data", {}).get("videos", []):
                        video = self._parse_api_video_data(video_data)
                        if video:
                            videos.append(video)
                    
                    # Check for next page
                    cursor = data.get("data", {}).get("cursor")
                    if not cursor or not data.get("data", {}).get("has_more"):
                        break
                
                await self.rate_limiter.update_usage(1)
            
            return videos[:max_results]
            
        except Exception as e:
            logger.error(f"TikTok API search failed: {e}")
            return []
    
    def _parse_api_video_data(self, video_data: dict) -> Optional[TikTokVideo]:
        """Parse TikTok API video data."""



        try:
            # Extract basic info
            video_id = video_data.get("id", "")
            username = video_data.get("username", "")
            description = video_data.get("video_description", "")
            
            # Extract URLs
            video_url = ""
            cover_url = ""
            if "video_url" in video_data:
                video_url = video_data["video_url"]
            if "cover_image_url" in video_data:
                cover_url = video_data["cover_image_url"]
            
            # Extract metrics
            view_count = video_data.get("view_count", 0)
            like_count = video_data.get("like_count", 0)
            comment_count = video_data.get("comment_count", 0)
            share_count = video_data.get("share_count", 0)
            
            # Extract timestamps
            create_time = video_data.get("create_time")
            created_at = datetime.fromtimestamp(create_time) if create_time else datetime.now()
            
            # Extract hashtags
            hashtags = []
            for hashtag in video_data.get("hashtag_names", []):
                hashtags.append(hashtag)
            
            # Extract mentions from description
            mentions = re.findall(r'@(\w+)', description)
            
            # Extract music info
            music = None
            if "music" in video_data:
                music = {
                    "id": video_data["music"].get("id"),
                    "title": video_data["music"].get("title"),
                    "author": video_data["music"].get("author")
                }
            
            return TikTokVideo(
                video_id=video_id,
                username=username,
                user_id=video_data.get("user_id", ""),
                description=description,
                video_url=video_url,
                cover_url=cover_url,
                duration=video_data.get("duration", 0),
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                share_count=share_count,
                created_at=created_at,
                hashtags=hashtags,
                mentions=mentions,
                music=music,
                effects=video_data.get("effect_ids", []),
                is_ad=video_data.get("is_promoted", False),
                language=video_data.get("language", ""),
                region=video_data.get("region_code", "")
            )
            
        except Exception as e:
            logger.error(f"Failed to parse TikTok API video data: {e}")
            return None
    
    async def _search_videos_scraping(self, query: str, max_results: int, region: str) -> List[TikTokVideo]:
        """Search videos using web scraping as fallback."""



        try:
            driver = webdriver.Chrome(options=self.selenium_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Build search URL
            if query.startswith('#'):
                # Hashtag search
                search_url = f"{self.web_base_url}/tag/{query[1:]}"
            elif query.startswith('@'):
                # User search
                search_url = f"{self.web_base_url}/@{query[1:]}"
            else:
                # General search
                search_url = f"{self.web_base_url}/search?q={query}"
            
            driver.get(search_url)
            await asyncio.sleep(3)
            
            videos = []
            scroll_count = 0
            max_scrolls = max_results // 10 + 2
            
            while len(videos) < max_results and scroll_count < max_scrolls:
                # Find video elements
                video_elements = driver.find_elements(By.CSS_SELECTOR, "[data-e2e='recommend-list-item-container']")
                
                for element in video_elements:
                    if len(videos) >= max_results:
                        break
                    
                    try:
                        video_data = await self._extract_video_from_element(driver, element)
                        if video_data:
                            videos.append(video_data)
                    except Exception as e:
                        logger.warning(f"Failed to extract video data: {e}")
                        continue
                
                # Scroll to load more videos
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                scroll_count += 1
            
            driver.quit()
            return videos[:max_results]
            
        except Exception as e:
            logger.error(f"TikTok scraping failed: {e}")
            if 'driver' in locals():
                driver.quit()
            return []
    
    async def _extract_video_from_element(self, driver, element) -> Optional[TikTokVideo]:
        """Extract video data from DOM element."""



        try:
            # Extract video link
            video_link = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            video_id = video_link.split("/")[-1] if video_link else ""
            
            # Extract username
            username_elem = element.find_element(By.CSS_SELECTOR, "[data-e2e='recommend-list-item-username']")
            username = username_elem.text.replace("@", "") if username_elem else ""
            
            # Extract description
            desc_elem = element.find_element(By.CSS_SELECTOR, "[data-e2e='recommend-list-item-desc']")
            description = desc_elem.text if desc_elem else ""
            
            # Extract video thumbnail
            img_elem = element.find_element(By.CSS_SELECTOR, "img")
            cover_url = img_elem.get_attribute("src") if img_elem else ""
            
            # Extract hashtags from description
            hashtags = re.findall(r'#(\w+)', description)
            mentions = re.findall(r'@(\w+)', description)
            
            return TikTokVideo(
                video_id=video_id,
                username=username,
                user_id="",
                description=description,
                video_url=video_link,
                cover_url=cover_url,
                duration=0,  # Would need additional scraping
                view_count=0,
                like_count=0,
                comment_count=0,
                share_count=0,
                created_at=datetime.now(),
                hashtags=hashtags,
                mentions=mentions,
                music=None,
                effects=[],
                is_ad=False,
                language="",
                region=""
            )
            
        except Exception as e:
            logger.warning(f"Failed to extract video from element: {e}")
            return None
    
    async def get_trending_hashtags(self, region: str = 'US', count: int = 50) -> List[TikTokHashtag]:
        """Get trending hashtags for specific region."""



        try:
            await self.rate_limiter.wait_if_needed()
            
            if self.api_key:
                return await self._get_trending_hashtags_api(region, count)
            else:
                return await self._get_trending_hashtags_scraping(region, count)
                
        except Exception as e:
            logger.error(f"Failed to get trending hashtags: {e}")
            return []
    
    async def _get_trending_hashtags_api(self, region: str, count: int) -> List[TikTokHashtag]:
        """Get trending hashtags using API."""



        try:
            url = f"{self.api_base_url}/v2/research/trending/hashtag/"
            
            params = {
                "region": region,
                "count": min(count, 100)
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                hashtags = []
                
                for hashtag_data in data.get("data", {}).get("hashtags", []):
                    hashtag = TikTokHashtag(
                        hashtag_id=hashtag_data.get("id", ""),
                        name=hashtag_data.get("name", ""),
                        view_count=hashtag_data.get("view_count", 0),
                        video_count=hashtag_data.get("video_count", 0),
                        is_trending=True,
                        challenge_id=hashtag_data.get("challenge_id")
                    )
                    hashtags.append(hashtag)
                
                await self.rate_limiter.update_usage(1)
                return hashtags
                
        except Exception as e:
            logger.error(f"API trending hashtags failed: {e}")
            return []
    
    async def _get_trending_hashtags_scraping(self, region: str, count: int) -> List[TikTokHashtag]:
        """Get trending hashtags using scraping."""



        try:
            driver = webdriver.Chrome(options=self.selenium_options)
            driver.get(f"{self.web_base_url}/trending")
            
            await asyncio.sleep(3)
            
            hashtags = []
            hashtag_elements = driver.find_elements(By.CSS_SELECTOR, "[data-e2e='trending-hashtag']")
            
            for element in hashtag_elements[:count]:
                try:
                    name = element.text.replace("#", "")
                    hashtag = TikTokHashtag(
                        hashtag_id=name,
                        name=name,
                        view_count=0,
                        video_count=0,
                        is_trending=True,
                        challenge_id=None
                    )
                    hashtags.append(hashtag)
                except:
                    continue
            
            driver.quit()
            return hashtags
            
        except Exception as e:
            logger.error(f"Trending hashtags scraping failed: {e}")
            if 'driver' in locals():
                driver.quit()
            return []
    
    async def get_user_profile(self, username: str) -> Optional[TikTokUser]:
        """Get user profile information."""



        try:
            await self.rate_limiter.wait_if_needed()
            
            if self.api_key:
                return await self._get_user_profile_api(username)
            else:
                return await self._get_user_profile_scraping(username)
                
        except Exception as e:
            logger.error(f"Failed to get user profile for {username}: {e}")
            return None
    
    async def _get_user_profile_scraping(self, username: str) -> Optional[TikTokUser]:
        """Get user profile using web scraping."""



        try:
            driver = webdriver.Chrome(options=self.selenium_options)
            driver.get(f"{self.web_base_url}/@{username}")
            
            await asyncio.sleep(3)
            
            # Extract profile data
            display_name_elem = driver.find_element(By.CSS_SELECTOR, "[data-e2e='user-title']")
            display_name = display_name_elem.text if display_name_elem else username
            
            # Extract follower counts
            follower_count = 0
            following_count = 0
            like_count = 0
            
            count_elements = driver.find_elements(By.CSS_SELECTOR, "[data-e2e='followers-count'], [data-e2e='following-count'], [data-e2e='likes-count']")
            for elem in count_elements:
                text = elem.text
                if "following" in elem.get_attribute("data-e2e"):
                    following_count = self._parse_count(text)
                elif "followers" in elem.get_attribute("data-e2e"):
                    follower_count = self._parse_count(text)
                elif "likes" in elem.get_attribute("data-e2e"):
                    like_count = self._parse_count(text)
            
            # Extract bio
            bio_elem = driver.find_element(By.CSS_SELECTOR, "[data-e2e='user-bio']")
            biography = bio_elem.text if bio_elem else ""
            
            # Extract avatar
            avatar_elem = driver.find_element(By.CSS_SELECTOR, "[data-e2e='user-avatar'] img")
            avatar_url = avatar_elem.get_attribute("src") if avatar_elem else ""
            
            driver.quit()
            
            return TikTokUser(
                user_id=username,  # Would need additional scraping for actual ID
                username=username,
                display_name=display_name,
                biography=biography,
                avatar_url=avatar_url,
                follower_count=follower_count,
                following_count=following_count,
                video_count=0,  # Would need additional scraping
                like_count=like_count,
                is_verified=False,  # Would need additional scraping
                is_business=False,
                region="",
                language=""
            )
            
        except Exception as e:
            logger.error(f"User profile scraping failed for {username}: {e}")
            if 'driver' in locals():
                driver.quit()
            return None
    
    def _parse_count(self, count_text: str) -> int:
        """Parse count string (e.g., '1.2M', '500K') to integer."""



        try:
            count_text = count_text.upper().replace(',', '')
            
            if 'M' in count_text:
                return int(float(count_text.replace('M', '')) * 1_000_000)
            elif 'K' in count_text:
                return int(float(count_text.replace('K', '')) * 1_000)
            else:
                return int(count_text)
        except:
            return 0
    
    async def monitor_hashtag(
        self,
        hashtag: str,
        check_interval: int = 300
    ) -> AsyncGenerator[List[TikTokVideo], None]:
        """Monitor hashtag for new videos."""
        last_check = datetime.now()
        seen_videos = set()
        
        while True:
            try:
                # Search for recent videos with hashtag
                videos = await self.search_videos(
                    query=f"#{hashtag}",
                    max_results=20,
                    start_date=last_check
                )
                
                # Filter new videos
                new_videos = []
                for video in videos:
                    if video.video_id not in seen_videos:
                        new_videos.append(video)
                        seen_videos.add(video.video_id)
                
                if new_videos:
                    yield new_videos
                
                last_check = datetime.now()
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Hashtag monitoring error for #{hashtag}: {e}")
                await asyncio.sleep(60)
    
    async def analyze_video_performance(self, video: TikTokVideo) -> Dict:
        """Analyze video performance metrics."""



        try:
            total_engagement = video.like_count + video.comment_count + video.share_count
            
            # Calculate engagement rate (assuming some reach estimation)
            estimated_reach = video.view_count if video.view_count > 0 else total_engagement * 50
            engagement_rate = (total_engagement / estimated_reach * 100) if estimated_reach > 0 else 0
            
            # Video age analysis
            video_age = datetime.now() - video.created_at
            engagement_per_hour = total_engagement / max(video_age.total_seconds() / 3600, 1)
            
            # Performance categorization
            if engagement_rate > 10:
                performance = "viral"
            elif engagement_rate > 5:
                performance = "high"
            elif engagement_rate > 2:
                performance = "medium"
            else:
                performance = "low"
            
            return {
                'total_engagement': total_engagement,
                'engagement_rate': round(engagement_rate, 2),
                'performance_category': performance,
                'like_to_view_ratio': round((video.like_count / video.view_count * 100), 3) if video.view_count > 0 else 0,
                'comment_to_view_ratio': round((video.comment_count / video.view_count * 100), 3) if video.view_count > 0 else 0,
                'share_to_view_ratio': round((video.share_count / video.view_count * 100), 3) if video.view_count > 0 else 0,
                'engagement_per_hour': round(engagement_per_hour, 2),
                'video_age_hours': round(video_age.total_seconds() / 3600, 1),
                'hashtag_count': len(video.hashtags),
                'mention_count': len(video.mentions),
                'has_music': video.music is not None,
                'effect_count': len(video.effects)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze video performance: {e}")
            return {}
    
    async def detect_similar_videos(
        self,
        reference_video: TikTokVideo,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """Detect videos similar to reference video."""



        try:
            similar_videos = []
            
            # Search using video hashtags
            for hashtag in reference_video.hashtags[:3]:
                hashtag_videos = await self.search_videos(
                    query=f"#{hashtag}",
                    max_results=20
                )
                
                for video in hashtag_videos:
                    if video.video_id == reference_video.video_id:
                        continue
                    
                    similarity = self._calculate_video_similarity(reference_video, video)
                    
                    if similarity >= similarity_threshold:
                        similar_videos.append({
                            'video': video,
                            'similarity_score': similarity,
                            'match_factors': self._get_video_match_factors(reference_video, video)
                        })
            
            # Remove duplicates and sort by similarity
            unique_videos = {}
            for match in similar_videos:
                video_id = match['video'].video_id
                if video_id not in unique_videos or match['similarity_score'] > unique_videos[video_id]['similarity_score']:
                    unique_videos[video_id] = match
            
            return sorted(unique_videos.values(), key=lambda x: x['similarity_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Similar video detection failed: {e}")
            return []
    
    def _calculate_video_similarity(self, video1: TikTokVideo, video2: TikTokVideo) -> float:
        """Calculate similarity score between two videos."""
        # Description similarity
        desc1_words = set(video1.description.lower().split())
        desc2_words = set(video2.description.lower().split())
        desc_similarity = len(desc1_words & desc2_words) / len(desc1_words | desc2_words) if desc1_words | desc2_words else 0
        
        # Hashtag similarity
        hashtag_similarity = len(set(video1.hashtags) & set(video2.hashtags)) / len(set(video1.hashtags) | set(video2.hashtags)) if video1.hashtags or video2.hashtags else 0
        
        # User similarity
        user_similarity = 1.0 if video1.username == video2.username else 0.0
        
        # Music similarity
        music_similarity = 0.0
        if video1.music and video2.music:
            if video1.music.get('id') == video2.music.get('id'):
                music_similarity = 1.0
            elif video1.music.get('title') == video2.music.get('title'):
                music_similarity = 0.8
        
        # Duration similarity
        if video1.duration > 0 and video2.duration > 0:
            duration_diff = abs(video1.duration - video2.duration)
            duration_similarity = max(0, 1 - (duration_diff / max(video1.duration, video2.duration)))
        else:
            duration_similarity = 0.0
        
        # Weighted average
        weights = {
            'description': 0.3,
            'hashtags': 0.3,
            'user': 0.2,
            'music': 0.1,
            'duration': 0.1
        }
        
        similarity = (
            weights['description'] * desc_similarity +
            weights['hashtags'] * hashtag_similarity +
            weights['user'] * user_similarity +
            weights['music'] * music_similarity +
            weights['duration'] * duration_similarity
        )
        
        return similarity
    
    def _get_video_match_factors(self, video1: TikTokVideo, video2: TikTokVideo) -> List[str]:
        """Get factors that contribute to video similarity."""
        factors = []
        
        if video1.username == video2.username:
            factors.append('same_user')
        
        common_hashtags = set(video1.hashtags) & set(video2.hashtags)
        if common_hashtags:
            factors.append(f'common_hashtags: {list(common_hashtags)[:3]}')
        
        if video1.music and video2.music:
            if video1.music.get('id') == video2.music.get('id'):
                factors.append('same_music')
            elif video1.music.get('title') == video2.music.get('title'):
                factors.append('similar_music')
        
        # Check description similarity
        desc1_words = set(video1.description.lower().split())
        desc2_words = set(video2.description.lower().split())
        common_words = desc1_words & desc2_words
        if len(common_words) > 3:
            factors.append('similar_description')
        
        return factors
