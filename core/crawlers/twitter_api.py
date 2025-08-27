"""
Twitter/X Advanced API Integration
=================================

Professional Twitter/X monitoring and content extraction system.
Combines Twitter API v2, Academic Research API with advanced scraping
for comprehensive content surveillance and rights protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, modification, or distribution is strictly prohibited.
Violators will face immediate legal action under German and international law.
"""

import asyncio
import logging
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import tweepy
import requests

from .base import BaseCrawler, CrawlResult
from ..config import ContentType
from ..security.encryption import SecurityManager
from ..utils.rate_limiter import RateLimiter
from ..utils.proxy_manager import ProxyManager

logger = logging.getLogger(__name__)

@dataclass
class TwitterTweetData:
    """Comprehensive Twitter/X tweet metadata structure."""
    
    tweet_id: str
    tweet_url: str
    text: str
    author_username: str
    author_display_name: str
    author_id: str
    author_verified: bool
    created_at: datetime
    retweet_count: int
    like_count: int
    reply_count: int
    quote_count: int
    bookmark_count: Optional[int]
    impression_count: Optional[int]
    hashtags: List[str]
    mentions: List[str]
    urls: List[str]
    
    # Media data
    media_urls: List[str] = None
    media_types: List[str] = None
    video_info: Optional[Dict[str, Any]] = None
    
    # Tweet metadata
    conversation_id: Optional[str] = None
    in_reply_to_user_id: Optional[str] = None
    referenced_tweets: List[Dict[str, Any]] = None
    context_annotations: List[Dict[str, Any]] = None
    
    # Advanced data
    lang: Optional[str] = None
    source: Optional[str] = None
    possibly_sensitive: bool = False
    withheld_copyright: bool = False
    withheld_in_countries: List[str] = None

@dataclass
class TwitterUserData:
    """Twitter/X user profile comprehensive information."""
    
    user_id: str
    username: str
    display_name: str
    description: str
    follower_count: int
    following_count: int
    tweet_count: int
    listed_count: int
    verified: bool
    verified_type: Optional[str]
    profile_image_url: str
    profile_banner_url: Optional[str]
    location: Optional[str]
    url: Optional[str]
    entities: Optional[Dict[str, Any]]
    created_at: datetime
    protected: bool
    
    # Business data
    business_account: bool = False
    professional_category: Optional[str] = None

class TwitterAPIManager:
    """Professional Twitter API management with v2 API integration."""
    
    def __init__(
        self,
        bearer_token: str,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None
    ):
        """Initialize Twitter API service with v2 API credentials."""
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        
        # Initialize Tweepy client
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        
        self.rate_limiter = RateLimiter(
            max_calls=300,  # Twitter API rate limit
            time_window=900  # 15 minutes
        )
    
    async def get_tweet_details(self, tweet_id: str) -> Optional[TwitterTweetData]:
        """Fetch comprehensive tweet details from Twitter API v2."""
        await self.rate_limiter.acquire()
        
        try:
            # Define tweet fields to fetch
            tweet_fields = [
                'id', 'text', 'author_id', 'created_at', 'conversation_id',
                'in_reply_to_user_id', 'referenced_tweets', 'attachments',
                'context_annotations', 'entities', 'geo', 'lang',
                'possibly_sensitive', 'reply_settings', 'source',
                'withheld', 'public_metrics'
            ]
            
            user_fields = [
                'id', 'name', 'username', 'verified', 'verified_type',
                'description', 'profile_image_url', 'public_metrics'
            ]
            
            media_fields = [
                'media_key', 'type', 'url', 'duration_ms', 'height',
                'width', 'preview_image_url', 'public_metrics'
            ]
            
            # Fetch tweet data
            response = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=tweet_fields,
                user_fields=user_fields,
                media_fields=media_fields,
                expansions=['author_id', 'attachments.media_keys', 'referenced_tweets.id']
            )
            
            if not response.data:
                return None
            
            tweet = response.data
            includes = response.includes or {}
            
            # Get author information
            author = None
            if 'users' in includes:
                for user in includes['users']:
                    if user.id == tweet.author_id:
                        author = user
                        break
            
            # Process media
            media_urls = []
            media_types = []
            video_info = None
            
            if 'media' in includes:
                for media in includes['media']:
                    if media.type == 'photo':
                        media_urls.append(media.url)
                        media_types.append('photo')
                    elif media.type == 'video':
                        media_urls.append(media.preview_image_url)
                        media_types.append('video')
                        video_info = {
                            'duration_ms': getattr(media, 'duration_ms', None),
                            'height': getattr(media, 'height', None),
                            'width': getattr(media, 'width', None)
                        }
            
            # Extract entities
            entities = getattr(tweet, 'entities', {})
            hashtags = [tag['tag'] for tag in entities.get('hashtags', [])]
            mentions = [mention['username'] for mention in entities.get('mentions', [])]
            urls = [url['expanded_url'] for url in entities.get('urls', [])]
            
            # Get public metrics
            metrics = getattr(tweet, 'public_metrics', {})
            
            return TwitterTweetData(
                tweet_id=tweet.id,
                tweet_url=f"https://twitter.com/{author.username if author else 'user'}/status/{tweet.id}",
                text=tweet.text,
                author_username=author.username if author else '',
                author_display_name=author.name if author else '',
                author_id=tweet.author_id,
                author_verified=getattr(author, 'verified', False) if author else False,
                created_at=tweet.created_at,
                retweet_count=metrics.get('retweet_count', 0),
                like_count=metrics.get('like_count', 0),
                reply_count=metrics.get('reply_count', 0),
                quote_count=metrics.get('quote_count', 0),
                impression_count=metrics.get('impression_count'),
                hashtags=hashtags,
                mentions=mentions,
                urls=urls,
                media_urls=media_urls,
                media_types=media_types,
                video_info=video_info,
                conversation_id=getattr(tweet, 'conversation_id', None),
                in_reply_to_user_id=getattr(tweet, 'in_reply_to_user_id', None),
                referenced_tweets=[
                    {'type': ref.type, 'id': ref.id} 
                    for ref in getattr(tweet, 'referenced_tweets', [])
                ],
                context_annotations=getattr(tweet, 'context_annotations', []),
                lang=getattr(tweet, 'lang', None),
                source=getattr(tweet, 'source', None),
                possibly_sensitive=getattr(tweet, 'possibly_sensitive', False),
                withheld_copyright=getattr(tweet, 'withheld', {}).get('copyright', False),
                withheld_in_countries=getattr(tweet, 'withheld', {}).get('country_codes', [])
            )
            
        except Exception as e:
            logger.error(f"Twitter tweet fetch error {tweet_id}: {e}")
            return None
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[str]:
        """Search tweets using Twitter API v2."""
        await self.rate_limiter.acquire()
        
        try:
            search_params = {
                'query': query,
                'max_results': min(max_results, 100),  # API limit
                'tweet_fields': ['id', 'created_at', 'public_metrics']
            }
            
            if start_time:
                search_params['start_time'] = start_time.isoformat()
            if end_time:
                search_params['end_time'] = end_time.isoformat()
            
            # Use Academic Research API for better search capabilities
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                **search_params
            ).flatten(limit=max_results)
            
            tweet_ids = [tweet.id for tweet in tweets]
            return tweet_ids
            
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
            return []
    
    async def get_user_tweets(
        self,
        user_id: str,
        max_results: int = 100,
        start_time: Optional[datetime] = None
    ) -> List[str]:
        """Get tweets from a specific user."""
        await self.rate_limiter.acquire()
        
        try:
            params = {
                'max_results': min(max_results, 100),
                'tweet_fields': ['id', 'created_at']
            }
            
            if start_time:
                params['start_time'] = start_time.isoformat()
            
            tweets = tweepy.Paginator(
                self.client.get_users_tweets,
                id=user_id,
                **params
            ).flatten(limit=max_results)
            
            tweet_ids = [tweet.id for tweet in tweets]
            return tweet_ids
            
        except Exception as e:
            logger.error(f"User tweets fetch error: {e}")
            return []

class TwitterWebScraper:
    """Advanced Twitter web scraping with anti-detection measures."""
    
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        """Initialize Twitter web scraper with proxy support."""
        self.proxy_manager = proxy_manager
        self.session = None
        self.driver = None
        self._setup_selenium_driver()
    
    def _setup_selenium_driver(self):
        """Configure Selenium WebDriver with anti-detection measures."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Twitter-optimized user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        import random
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Proxy configuration
        if self.proxy_manager:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                chrome_options.add_argument(f'--proxy-server={proxy}')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    async def scrape_tweet_data(self, tweet_url: str) -> Optional[TwitterTweetData]:
        """Scrape comprehensive tweet data from Twitter page."""
        try:
            self.driver.get(tweet_url)
            
            # Wait for tweet content to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweet']"))
            )
            
            # Extract tweet ID from URL
            tweet_id_match = re.search(r'/status/(\d+)', tweet_url)
            if not tweet_id_match:
                return None
            
            tweet_id = tweet_id_match.group(1)
            
            # Extract tweet data from DOM
            tweet_data = self._extract_tweet_from_dom(tweet_id, tweet_url)
            
            return tweet_data
            
        except Exception as e:
            logger.error(f"Twitter tweet scraping error {tweet_url}: {e}")
            return None
    
    def _extract_tweet_from_dom(self, tweet_id: str, tweet_url: str) -> Optional[TwitterTweetData]:
        """Extract tweet data from DOM elements."""
        try:
            # Find main tweet element
            tweet_element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='tweet']")
            
            # Extract text content
            text_elements = tweet_element.find_elements(By.CSS_SELECTOR, "[data-testid='tweetText']")
            text = text_elements[0].text if text_elements else ""
            
            # Extract author information
            author_elements = tweet_element.find_elements(By.CSS_SELECTOR, "[data-testid='User-Name'] a")
            author_username = ""
            author_display_name = ""
            
            if author_elements:
                author_link = author_elements[0].get_attribute('href')
                author_username = author_link.split('/')[-1] if author_link else ""
                
                name_elements = author_elements[0].find_elements(By.TAG_NAME, "span")
                if name_elements:
                    author_display_name = name_elements[0].text
            
            # Extract engagement metrics
            engagement_elements = tweet_element.find_elements(By.CSS_SELECTOR, "[role='group'] span")
            
            retweet_count = 0
            like_count = 0
            reply_count = 0
            
            for element in engagement_elements:
                text = element.text.lower()
                if 'retweet' in text:
                    retweet_count = self._parse_count(element.text)
                elif 'like' in text:
                    like_count = self._parse_count(element.text)
                elif 'repl' in text:
                    reply_count = self._parse_count(element.text)
            
            # Extract media URLs
            media_urls = []
            media_types = []
            
            # Check for images
            img_elements = tweet_element.find_elements(By.CSS_SELECTOR, "img[src*='media']")
            for img in img_elements:
                media_urls.append(img.get_attribute('src'))
                media_types.append('photo')
            
            # Check for videos
            video_elements = tweet_element.find_elements(By.CSS_SELECTOR, "video")
            for video in video_elements:
                poster = video.get_attribute('poster')
                if poster:
                    media_urls.append(poster)
                    media_types.append('video')
            
            # Extract hashtags and mentions
            hashtags = re.findall(r'#\w+', text)
            mentions = re.findall(r'@\w+', text)
            
            # Extract URLs
            url_elements = tweet_element.find_elements(By.CSS_SELECTOR, "a[href*='http']")
            urls = [elem.get_attribute('href') for elem in url_elements]
            
            return TwitterTweetData(
                tweet_id=tweet_id,
                tweet_url=tweet_url,
                text=text,
                author_username=author_username,
                author_display_name=author_display_name,
                author_id='',  # Not available from scraping
                author_verified=False,  # Would need additional detection
                created_at=datetime.now(),  # Approximate
                retweet_count=retweet_count,
                like_count=like_count,
                reply_count=reply_count,
                quote_count=0,  # Not easily extractable
                hashtags=[tag.replace('#', '') for tag in hashtags],
                mentions=[mention.replace('@', '') for mention in mentions],
                urls=urls,
                media_urls=media_urls,
                media_types=media_types,
                lang=None,
                source=None,
                possibly_sensitive=False,
                withheld_copyright=False
            )
            
        except Exception as e:
            logger.error(f"Tweet DOM extraction error: {e}")
            return None
    
    def _parse_count(self, count_text: str) -> int:
        """Parse engagement count strings."""
        try:
            count_text = re.sub(r'[^\d.KM]', '', count_text.upper())
            if 'M' in count_text:
                return int(float(count_text.replace('M', '')) * 1_000_000)
            elif 'K' in count_text:
                return int(float(count_text.replace('K', '')) * 1_000)
            else:
                return int(count_text) if count_text.isdigit() else 0
        except ValueError:
            return 0
    
    async def search_hashtag_tweets(self, hashtag: str, limit: int = 50) -> List[str]:
        """Search tweets by hashtag and return tweet URLs."""
        try:
            search_url = f"https://twitter.com/search?q=%23{hashtag.replace('#', '')}&src=typed_query&f=live"
            self.driver.get(search_url)
            
            # Wait for tweets to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweet']"))
            )
            
            tweet_urls = []
            collected = 0
            scroll_attempts = 0
            max_scrolls = 10
            
            while collected < limit and scroll_attempts < max_scrolls:
                # Extract tweet links from current page
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/status/']")
                
                for element in tweet_elements:
                    if collected >= limit:
                        break
                    
                    href = element.get_attribute('href')
                    if href and href not in tweet_urls:
                        tweet_urls.append(href)
                        collected += 1
                
                # Scroll down to load more tweets
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                scroll_attempts += 1
            
            return tweet_urls
            
        except Exception as e:
            logger.error(f"Twitter hashtag search error: {e}")
            return []
    
    def close(self):
        """Clean up Selenium driver."""
        if self.driver:
            self.driver.quit()

class TwitterCrawler(BaseCrawler):
    """Professional Twitter crawler with comprehensive monitoring capabilities."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Twitter crawler with configuration."""
        super().__init__(config)
        self.api_manager = None
        
        # Initialize API manager if credentials provided
        if config.get('twitter_bearer_token'):
            self.api_manager = TwitterAPIManager(
                bearer_token=config['twitter_bearer_token'],
                api_key=config.get('twitter_api_key'),
                api_secret=config.get('twitter_api_secret'),
                access_token=config.get('twitter_access_token'),
                access_token_secret=config.get('twitter_access_token_secret')
            )
        
        self.web_scraper = TwitterWebScraper(
            proxy_manager=config.get('proxy_manager')
        )
        self.platform = 'twitter'
    
    async def crawl_tweet(self, tweet_url: str) -> Optional[CrawlResult]:
        """Crawl comprehensive data for a specific tweet."""
        try:
            tweet_data = None
            
            # Try API first if available
            if self.api_manager:
                tweet_id_match = re.search(r'/status/(\d+)', tweet_url)
                if tweet_id_match:
                    tweet_id = tweet_id_match.group(1)
                    tweet_data = await self.api_manager.get_tweet_details(tweet_id)
            
            # Fallback to web scraping
            if not tweet_data:
                tweet_data = await self.web_scraper.scrape_tweet_data(tweet_url)
            
            if not tweet_data:
                return None
            
            # Determine content type
            content_type = ContentType.TEXT.value
            if tweet_data.media_types:
                if 'video' in tweet_data.media_types:
                    content_type = ContentType.VIDEO.value
                elif 'photo' in tweet_data.media_types:
                    content_type = ContentType.IMAGE.value
                if len(set(tweet_data.media_types)) > 1:
                    content_type = ContentType.MIXED.value
            
            # Create standardized crawl result
            result = CrawlResult(
                url=tweet_url,
                platform=self.platform,
                content_type=content_type,
                title=tweet_data.text[:100] + "..." if len(tweet_data.text) > 100 else tweet_data.text,
                description=tweet_data.text,
                author=tweet_data.author_username,
                upload_date=tweet_data.created_at,
                view_count=tweet_data.impression_count or 0,
                duration_ms=tweet_data.video_info.get('duration_ms') if tweet_data.video_info else None,
                thumbnail_url=tweet_data.media_urls[0] if tweet_data.media_urls else None,
                tags=tweet_data.hashtags,
                metadata={
                    'tweet_data': asdict(tweet_data),
                    'platform_specific': {
                        'tweet_id': tweet_data.tweet_id,
                        'author_id': tweet_data.author_id,
                        'conversation_id': tweet_data.conversation_id,
                        'lang': tweet_data.lang,
                        'source': tweet_data.source
                    },
                    'engagement': {
                        'retweet_count': tweet_data.retweet_count,
                        'like_count': tweet_data.like_count,
                        'reply_count': tweet_data.reply_count,
                        'quote_count': tweet_data.quote_count
                    }
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Twitter tweet crawl error {tweet_url}: {e}")
            return None
    
    async def search_similar_content(
        self,
        query: str,
        limit: int = 100,
        time_range: Optional[timedelta] = None
    ) -> List[CrawlResult]:
        """Search for potentially infringing content on Twitter."""
        try:
            results = []
            
            # Try API search first
            if self.api_manager:
                start_time = None
                if time_range:
                    start_time = datetime.now() - time_range
                
                tweet_ids = await self.api_manager.search_tweets(
                    query=query,
                    max_results=limit,
                    start_time=start_time
                )
                
                for tweet_id in tweet_ids:
                    tweet_url = f"https://twitter.com/user/status/{tweet_id}"
                    result = await self.crawl_tweet(tweet_url)
                    if result:
                        results.append(result)
                    await asyncio.sleep(0.5)
            
            # Supplement with web scraping if needed
            if len(results) < limit:
                remaining = limit - len(results)
                hashtag_urls = await self.web_scraper.search_hashtag_tweets(query, remaining)
                
                for tweet_url in hashtag_urls:
                    result = await self.crawl_tweet(tweet_url)
                    if result:
                        results.append(result)
                    await asyncio.sleep(1)
            
            return results
            
        except Exception as e:
            logger.error(f"Twitter search crawl error: {e}")
            return []
    
    async def monitor_user(
        self,
        username: str,
        check_period: timedelta = timedelta(hours=24)
    ) -> List[CrawlResult]:
        """Monitor a specific user for new tweets."""
        try:
            results = []
            
            # Try API method first
            if self.api_manager:
                # Note: Would need user ID, not username
                # This is a simplified version
                pass
            
            # Web scraping method
            user_url = f"https://twitter.com/{username}"
            self.web_scraper.driver.get(user_url)
            
            # Wait for tweets to load
            WebDriverWait(self.web_scraper.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweet']"))
            )
            
            # Extract recent tweet URLs
            tweet_elements = self.web_scraper.driver.find_elements(
                By.CSS_SELECTOR, "a[href*='/status/']"
            )
            
            recent_tweets = []
            for element in tweet_elements[:20]:  # Check last 20 tweets
                href = element.get_attribute('href')
                if href and f"/{username}/" in href:
                    recent_tweets.append(href)
            
            # Crawl each tweet and filter by date
            cutoff_date = datetime.now() - check_period
            
            for tweet_url in recent_tweets:
                result = await self.crawl_tweet(tweet_url)
                if result and result.upload_date and result.upload_date > cutoff_date:
                    results.append(result)
                await asyncio.sleep(1)
            
            return results
            
        except Exception as e:
            logger.error(f"Twitter user monitoring error {username}: {e}")
            return []
    
    def cleanup(self):
        """Clean up resources."""
        if self.web_scraper:
            self.web_scraper.close()
