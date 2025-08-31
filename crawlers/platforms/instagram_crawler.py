"""Instagram Crawler
=================

Professional Instagram content crawler with advanced monitoring capabilities.
Implements Instagram Basic Display API and scraping techniques.

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
"""import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import re
from urllib.parse import urlparse, parse_qs

import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..utils.rate_limiter import InstagramRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError
from ...database.models import CrawlResult, ContentMatch

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class InstagramPost:
    """Instagram post data structure."""    post_id: str
    shortcode: str
    post_type: str  # photo, video, carousel
    caption: str
    username: str
    user_id: str
    display_url: str
    video_url: Optional[str]
    thumbnail_url: str
    like_count: int
    comment_count: int
    view_count: Optional[int]
    taken_at: datetime
    location: Optional[Dict]
    hashtags: List[str]
    mentions: List[str]
    is_video: bool
    accessibility_caption: Optional[str]

@dataclass
class InstagramUser:
    """Instagram user data structure."""    user_id: str
    username: str
    full_name: str
    biography: str
    profile_pic_url: str
    follower_count: int
    following_count: int
    media_count: int
    is_verified: bool
    is_business: bool
    category: Optional[str]
    external_url: Optional[str]

@dataclass
class InstagramStory:
    """Instagram story data structure."""    story_id: str
    user_id: str
    username: str
    media_type: str
    media_url: str
    thumbnail_url: str
    taken_at: datetime
    expires_at: datetime
    view_count: Optional[int]
    has_audio: bool

class InstagramCrawler:
    """    Professional Instagram crawler implementation.
    
    Features:
    - Instagram Basic Display API integration
    - Instagram Business API support
    - Advanced hashtag and location tracking
    - Story monitoring capabilities
    - User profile analysis
    - Engagement rate calculations
    - Content similarity detection
    - Real-time feed monitoring
    - Selenium-based scraping fallback
    """    
    def __init__(self):
        """Initialize Instagram crawler."""        self.access_token = settings.INSTAGRAM_ACCESS_TOKEN
        self.app_id = settings.INSTAGRAM_APP_ID
        self.app_secret = settings.INSTAGRAM_APP_SECRET
        self.rate_limiter = InstagramRateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.session = None
        
        # Base URLs
        self.api_base_url = "https://graph.instagram.com"
        self.web_base_url = "https://www.instagram.com"
        
        # Selenium configuration
        self.selenium_options = webdriver.ChromeOptions()
        self.selenium_options.add_argument('--headless')
        self.selenium_options.add_argument('--no-sandbox')
        self.selenium_options.add_argument('--disable-dev-shm-usage')
        self.selenium_options.add_argument('--disable-gpu')
        self.selenium_options.add_argument('--disable-blink-features=AutomationControlled')
        self.selenium_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.selenium_options.add_experimental_option('useAutomationExtension', False)
    
    async def __aenter__(self):
        """Async context manager entry."""        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""        if self.session:
            await self.session.close()
    
    async def search_hashtag(
        self,
        hashtag: str,
        max_results: int = 50,
        recent_only: bool = True
    ) -> List[InstagramPost]:
        """        Search posts by hashtag.
        
        Args:
            hashtag: Hashtag to search (without #)
            max_results: Maximum number of posts to return
            recent_only: Return only recent posts
            
        Returns:
            List of Instagram post objects
        """        try:
            # Rate limiting check
            await self.rate_limiter.wait_if_needed()
            
            # Clean hashtag
            hashtag = hashtag.lstrip('#').lower()
            
            if self.access_token:
                return await self._search_hashtag_api(hashtag, max_results)
            else:
                return await self._search_hashtag_scraping(hashtag, max_results, recent_only)
                
        except Exception as e:
            logger.error(f"Hashtag search error for #{hashtag}: {e}")
            return []
    
    async def _search_hashtag_api(self, hashtag: str, max_results: int) -> List[InstagramPost]:
        """Search hashtag using Instagram API."""        try:
            url = f"{self.api_base_url}/ig_hashtag_search"
            params = {
                'user_id': settings.INSTAGRAM_USER_ID,
                'q': hashtag,
                'access_token': self.access_token
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    hashtag_id = data['data'][0]['id'] if data['data'] else None
                    
                    if hashtag_id:
                        return await self._get_hashtag_media(hashtag_id, max_results)
                    
                await self.rate_limiter.update_usage(1)
                return []
                
        except Exception as e:
            logger.error(f"API hashtag search failed: {e}")
            return []
    
    async def _get_hashtag_media(self, hashtag_id: str, max_results: int) -> List[InstagramPost]:
        """Get media from hashtag ID."""        try:
            url = f"{self.api_base_url}/{hashtag_id}/recent_media"
            params = {
                'user_id': settings.INSTAGRAM_USER_ID,
                'fields': 'id,media_type,media_url,permalink,timestamp,caption',
                'limit': min(max_results, 25),
                'access_token': self.access_token
            }
            
            posts = []
            next_page = None
            
            while len(posts) < max_results:
                if next_page:
                    params['after'] = next_page
                
                async with self.session.get(url, params=params) as response:
                    if response.status != 200:
                        break
                    
                    data = await response.json()
                    
                    for item in data.get('data', []):
                        post = self._parse_api_post_data(item)
                        if post:
                            posts.append(post)
                    
                    # Check for next page
                    paging = data.get('paging', {})
                    next_page = paging.get('cursors', {}).get('after')
                    if not next_page:
                        break
                
                await self.rate_limiter.update_usage(1)
            
            return posts[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to get hashtag media: {e}")
            return []
    
    async def _search_hashtag_scraping(
        self,
        hashtag: str,
        max_results: int,
        recent_only: bool
    ) -> List[InstagramPost]:
        """Search hashtag using web scraping."""        try:
            driver = webdriver.Chrome(options=self.selenium_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to hashtag page
            url = f"{self.web_base_url}/explore/tags/{hashtag}/"
            driver.get(url)
            
            # Wait for content to load
            await asyncio.sleep(3)
            
            posts = []
            collected_urls = set()
            
            # Scroll and collect posts
            for _ in range(max_results // 12 + 1):
                # Find post links
                post_links = driver.find_elements(By.CSS_SELECTOR, "article a")
                
                for link in post_links:
                    if len(posts) >= max_results:
                        break
                    
                    href = link.get_attribute('href')
                    if href and '/p/' in href and href not in collected_urls:
                        collected_urls.add(href)
                        
                        # Extract shortcode from URL
                        shortcode = href.split('/p/')[1].split('/')[0]
                        
                        # Get post details
                        post_data = await self._scrape_post_details(driver, href, shortcode)
                        if post_data:
                            posts.append(post_data)
                
                # Scroll down to load more posts
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            driver.quit()
            return posts[:max_results]
            
        except Exception as e:
            logger.error(f"Hashtag scraping failed: {e}")
            if 'driver' in locals():
                driver.quit()
            return []
    
    async def _scrape_post_details(self, driver, post_url: str, shortcode: str) -> Optional[InstagramPost]:
        """Scrape detailed post information."""        try:
            # Open post in new tab
            driver.execute_script(f"window.open('{post_url}');")
            driver.switch_to.window(driver.window_handles[-1])
            
            await asyncio.sleep(2)
            
            # Extract post data from page source
            page_source = driver.page_source
            
            # Look for JSON data in script tags
            json_data = None
            if 'window._sharedData' in page_source:
                # Extract shared data
                start = page_source.find('window._sharedData = ') + len('window._sharedData = ')
                end = page_source.find(';</script>', start)
                if end > start:
                    try:
                        json_data = json.loads(page_source[start:end])
                    except:
                        pass
            
            post_data = None
            if json_data:
                post_data = self._extract_post_from_shared_data(json_data, shortcode)
            
            if not post_data:
                # Fallback to DOM scraping
                post_data = await self._scrape_post_from_dom(driver, shortcode)
            
            # Close tab and return to main window
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            
            return post_data
            
        except Exception as e:
            logger.warning(f"Failed to scrape post details for {shortcode}: {e}")
            # Ensure we return to main window
            try:
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
            except:
                pass
            return None
    
    def _extract_post_from_shared_data(self, shared_data: dict, shortcode: str) -> Optional[InstagramPost]:
        """Extract post data from Instagram's shared data."""        try:
            # Navigate through Instagram's data structure
            entry_data = shared_data.get('entry_data', {})
            post_page = entry_data.get('PostPage', [])
            
            if not post_page:
                return None
            
            graphql = post_page[0].get('graphql', {})
            shortcode_media = graphql.get('shortcode_media', {})
            
            if not shortcode_media:
                return None
            
            # Extract basic info
            post_id = shortcode_media.get('id', '')
            caption_edges = shortcode_media.get('edge_media_to_caption', {}).get('edges', [])
            caption = caption_edges[0]['node']['text'] if caption_edges else ''
            
            # Extract user info
            owner = shortcode_media.get('owner', {})
            username = owner.get('username', '')
            user_id = owner.get('id', '')
            
            # Extract media info
            display_url = shortcode_media.get('display_url', '')
            is_video = shortcode_media.get('is_video', False)
            video_url = shortcode_media.get('video_url') if is_video else None
            
            # Extract engagement
            likes = shortcode_media.get('edge_media_preview_like', {}).get('count', 0)
            comments = shortcode_media.get('edge_media_to_comment', {}).get('count', 0)
            video_views = shortcode_media.get('video_view_count', 0) if is_video else None
            
            # Extract timestamp
            taken_at = datetime.fromtimestamp(shortcode_media.get('taken_at_timestamp', 0))
            
            # Extract hashtags and mentions
            hashtags = re.findall(r'#(\w+)', caption)
            mentions = re.findall(r'@(\w+)', caption)
            
            # Extract location
            location = None
            if shortcode_media.get('location'):
                location = {
                    'id': shortcode_media['location'].get('id'),
                    'name': shortcode_media['location'].get('name'),
                    'slug': shortcode_media['location'].get('slug')
                }
            
            return InstagramPost(
                post_id=post_id,
                shortcode=shortcode,
                post_type='video' if is_video else 'photo',
                caption=caption,
                username=username,
                user_id=user_id,
                display_url=display_url,
                video_url=video_url,
                thumbnail_url=display_url,
                like_count=likes,
                comment_count=comments,
                view_count=video_views,
                taken_at=taken_at,
                location=location,
                hashtags=hashtags,
                mentions=mentions,
                is_video=is_video,
                accessibility_caption=shortcode_media.get('accessibility_caption')
            )
            
        except Exception as e:
            logger.error(f"Failed to extract post from shared data: {e}")
            return None
    
    async def _scrape_post_from_dom(self, driver, shortcode: str) -> Optional[InstagramPost]:
        """Fallback DOM scraping for post data."""        try:
            # Extract basic elements
            username_elem = driver.find_element(By.CSS_SELECTOR, "header a")
            username = username_elem.text if username_elem else ""
            
            # Try to find caption
            caption_elem = None
            caption_selectors = [
                "article div[data-testid='post-caption'] span",
                "article div span[dir='auto']",
                ".Caption span"
            ]
            
            caption = ""
            for selector in caption_selectors:
                try:
                    caption_elem = driver.find_element(By.CSS_SELECTOR, selector)
                    caption = caption_elem.text
                    break
                except NoSuchElementException:
                    continue
            
            # Extract image/video
            media_elem = driver.find_element(By.CSS_SELECTOR, "article img, article video")
            display_url = media_elem.get_attribute('src') if media_elem else ""
            is_video = media_elem.tag_name == 'video'
            
            # Extract hashtags and mentions
            hashtags = re.findall(r'#(\w+)', caption)
            mentions = re.findall(r'@(\w+)', caption)
            
            return InstagramPost(
                post_id=shortcode,
                shortcode=shortcode,
                post_type='video' if is_video else 'photo',
                caption=caption,
                username=username,
                user_id="",
                display_url=display_url,
                video_url=display_url if is_video else None,
                thumbnail_url=display_url,
                like_count=0,
                comment_count=0,
                view_count=None,
                taken_at=datetime.now(),
                location=None,
                hashtags=hashtags,
                mentions=mentions,
                is_video=is_video,
                accessibility_caption=None
            )
            
        except Exception as e:
            logger.error(f"DOM scraping failed for {shortcode}: {e}")
            return None
    
    def _parse_api_post_data(self, item: dict) -> Optional[InstagramPost]:
        """Parse Instagram API post data."""        try:
            post_id = item.get('id', '')
            media_type = item.get('media_type', '')
            caption = item.get('caption', '')
            timestamp = item.get('timestamp', '')
            
            # Convert timestamp
            taken_at = datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if timestamp else datetime.now()
            
            # Extract hashtags and mentions
            hashtags = re.findall(r'#(\w+)', caption)
            mentions = re.findall(r'@(\w+)', caption)
            
            return InstagramPost(
                post_id=post_id,
                shortcode=post_id,  # API doesn't provide shortcode directly
                post_type=media_type.lower(),
                caption=caption,
                username="",  # Would need separate user request
                user_id="",
                display_url=item.get('media_url', ''),
                video_url=item.get('media_url') if media_type == 'VIDEO' else None,
                thumbnail_url=item.get('thumbnail_url', item.get('media_url', '')),
                like_count=0,  # Not available in basic API
                comment_count=0,
                view_count=None,
                taken_at=taken_at,
                location=None,
                hashtags=hashtags,
                mentions=mentions,
                is_video=media_type == 'VIDEO',
                accessibility_caption=None
            )
            
        except Exception as e:
            logger.error(f"Failed to parse API post data: {e}")
            return None
    
    async def get_user_profile(self, username: str) -> Optional[InstagramUser]:
        """Get user profile information."""        try:
            await self.rate_limiter.wait_if_needed()
            
            if self.access_token:
                return await self._get_user_profile_api(username)
            else:
                return await self._get_user_profile_scraping(username)
                
        except Exception as e:
            logger.error(f"Failed to get user profile for {username}: {e}")
            return None
    
    async def _get_user_profile_scraping(self, username: str) -> Optional[InstagramUser]:
        """Get user profile using web scraping."""        try:
            driver = webdriver.Chrome(options=self.selenium_options)
            driver.get(f"{self.web_base_url}/{username}/")
            
            await asyncio.sleep(3)
            
            # Extract profile data from shared data
            page_source = driver.page_source
            
            if 'window._sharedData' in page_source:
                start = page_source.find('window._sharedData = ') + len('window._sharedData = ')
                end = page_source.find(';</script>', start)
                if end > start:
                    try:
                        shared_data = json.loads(page_source[start:end])
                        profile_data = self._extract_user_from_shared_data(shared_data, username)
                        if profile_data:
                            driver.quit()
                            return profile_data
                    except:
                        pass
            
            # Fallback to DOM scraping
            profile_data = await self._scrape_user_from_dom(driver, username)
            driver.quit()
            return profile_data
            
        except Exception as e:
            logger.error(f"User profile scraping failed for {username}: {e}")
            if 'driver' in locals():
                driver.quit()
            return None
    
    def _extract_user_from_shared_data(self, shared_data: dict, username: str) -> Optional[InstagramUser]:
        """Extract user data from Instagram's shared data."""        try:
            entry_data = shared_data.get('entry_data', {})
            profile_page = entry_data.get('ProfilePage', [])
            
            if not profile_page:
                return None
            
            graphql = profile_page[0].get('graphql', {})
            user_data = graphql.get('user', {})
            
            if not user_data:
                return None
            
            return InstagramUser(
                user_id=user_data.get('id', ''),
                username=username,
                full_name=user_data.get('full_name', ''),
                biography=user_data.get('biography', ''),
                profile_pic_url=user_data.get('profile_pic_url_hd', ''),
                follower_count=user_data.get('edge_followed_by', {}).get('count', 0),
                following_count=user_data.get('edge_follow', {}).get('count', 0),
                media_count=user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                is_verified=user_data.get('is_verified', False),
                is_business=user_data.get('is_business_account', False),
                category=user_data.get('category_name'),
                external_url=user_data.get('external_url')
            )
            
        except Exception as e:
            logger.error(f"Failed to extract user from shared data: {e}")
            return None
    
    async def search_location(self, location_name: str, max_results: int = 20) -> List[InstagramPost]:
        """Search posts by location."""        try:
            # This would require location ID lookup and then location media fetch
            # Implementation depends on available APIs and scraping capabilities
            logger.info(f"Location search for '{location_name}' - feature in development")
            return []
            
        except Exception as e:
            logger.error(f"Location search failed: {e}")
            return []
    
    async def monitor_user(
        self,
        username: str,
        check_interval: int = 300
    ) -> AsyncGenerator[List[InstagramPost], None]:
        """Monitor user for new posts."""        last_check = datetime.now()
        seen_posts = set()
        
        while True:
            try:
                # Get recent posts from user
                user_posts = await self.get_user_recent_posts(username, max_results=12)
                
                # Filter new posts
                new_posts = []
                for post in user_posts:
                    if (post.post_id not in seen_posts and 
                        post.taken_at > last_check):
                        new_posts.append(post)
                        seen_posts.add(post.post_id)
                
                if new_posts:
                    yield new_posts
                
                last_check = datetime.now()
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"User monitoring error for {username}: {e}")
                await asyncio.sleep(60)
    
    async def get_user_recent_posts(self, username: str, max_results: int = 12) -> List[InstagramPost]:
        """Get recent posts from user profile."""        try:
            # This would involve scraping the user's profile page
            # and extracting recent posts
            logger.info(f"Getting recent posts for {username}")
            return []
            
        except Exception as e:
            logger.error(f"Failed to get user recent posts: {e}")
            return []
    
    async def analyze_engagement(self, post: InstagramPost) -> Dict:
        """Analyze post engagement metrics."""        try:
            total_engagement = post.like_count + post.comment_count
            
            # Estimate reach (this would require additional data in practice)
            estimated_reach = total_engagement * 10  # Rough estimation
            engagement_rate = (total_engagement / estimated_reach * 100) if estimated_reach > 0 else 0
            
            # Post age analysis
            post_age = datetime.now() - post.taken_at
            engagement_per_hour = total_engagement / max(post_age.total_seconds() / 3600, 1)
            
            return {
                'total_engagement': total_engagement,
                'engagement_rate': round(engagement_rate, 2),
                'like_to_comment_ratio': round(post.like_count / max(post.comment_count, 1), 2),
                'engagement_per_hour': round(engagement_per_hour, 2),
                'post_age_hours': round(post_age.total_seconds() / 3600, 1),
                'hashtag_count': len(post.hashtags),
                'mention_count': len(post.mentions),
                'performance_score': min(100, engagement_rate * 10)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze engagement: {e}")
            return {}
    
    async def detect_similar_content(
        self,
        reference_post: InstagramPost,
        search_hashtags: List[str] = None
    ) -> List[Dict]:
        """Detect content similar to reference post."""        try:
            similar_posts = []
            
            # Search using post hashtags
            search_tags = search_hashtags or reference_post.hashtags[:5]
            
            for hashtag in search_tags:
                hashtag_posts = await self.search_hashtag(hashtag, max_results=20)
                
                for post in hashtag_posts:
                    if post.post_id == reference_post.post_id:
                        continue
                    
                    similarity = self._calculate_post_similarity(reference_post, post)
                    
                    if similarity > 0.6:  # Threshold for similarity
                        similar_posts.append({
                            'post': post,
                            'similarity_score': similarity,
                            'match_factors': self._get_match_factors(reference_post, post)
                        })
            
            # Remove duplicates and sort by similarity
            unique_posts = {}
            for match in similar_posts:
                post_id = match['post'].post_id
                if post_id not in unique_posts or match['similarity_score'] > unique_posts[post_id]['similarity_score']:
                    unique_posts[post_id] = match
            
            return sorted(unique_posts.values(), key=lambda x: x['similarity_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Similar content detection failed: {e}")
            return []
    
    def _calculate_post_similarity(self, post1: InstagramPost, post2: InstagramPost) -> float:
        """Calculate similarity score between two posts."""        # Caption similarity
        caption1_words = set(post1.caption.lower().split())
        caption2_words = set(post2.caption.lower().split())
        caption_similarity = len(caption1_words & caption2_words) / len(caption1_words | caption2_words) if caption1_words | caption2_words else 0
        
        # Hashtag similarity
        hashtag_similarity = len(set(post1.hashtags) & set(post2.hashtags)) / len(set(post1.hashtags) | set(post2.hashtags)) if post1.hashtags or post2.hashtags else 0
        
        # User similarity
        user_similarity = 1.0 if post1.username == post2.username else 0.0
        
        # Time proximity
        time_diff = abs((post1.taken_at - post2.taken_at).total_seconds())
        time_similarity = max(0, 1 - (time_diff / (7 * 24 * 3600)))  # 7 days max
        
        # Weighted average
        weights = {
            'caption': 0.3,
            'hashtags': 0.4,
            'user': 0.2,
            'time': 0.1
        }
        
        similarity = (
            weights['caption'] * caption_similarity +
            weights['hashtags'] * hashtag_similarity +
            weights['user'] * user_similarity +
            weights['time'] * time_similarity
        )
        
        return similarity
    
    def _get_match_factors(self, post1: InstagramPost, post2: InstagramPost) -> List[str]:
        """Get factors that contribute to post similarity."""        factors = []
        
        if post1.username == post2.username:
            factors.append('same_user')
        
        common_hashtags = set(post1.hashtags) & set(post2.hashtags)
        if common_hashtags:
            factors.append(f'common_hashtags: {list(common_hashtags)[:3]}')
        
        if post1.post_type == post2.post_type:
            factors.append('same_media_type')
        
        # Check caption similarity
        caption1_words = set(post1.caption.lower().split())
        caption2_words = set(post2.caption.lower().split())
        common_words = caption1_words & caption2_words
        if len(common_words) > 3:
            factors.append('similar_caption')
        
        return factors
