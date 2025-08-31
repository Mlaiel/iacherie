"""
Twitter/X Crawling Engine
========================

Advanced Twitter/X crawler for social media monitoring, tweet analysis, and trend tracking.
Handles tweet extraction, user analytics, and hashtag monitoring with API v2 integration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

  AVERTISSEMENT LÉGAL 
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.
"""

import asyncio
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
import tweepy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError,
    SuspendedAccountError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..utils.proxy_manager import ProxyManager
from ..models.content_models import Tweet, TwitterUser, TwitterThread
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class TwitterTweetData:
    """Twitter tweet data structure"""
    tweet_id: str
    url: str
    text: str
    created_at: datetime
    author_id: str
    author_username: str
    author_name: str
    conversation_id: str
    in_reply_to_user_id: Optional[str]
    referenced_tweets: List[Dict]
    public_metrics: Dict[str, int]  # retweet_count, like_count, etc.
    non_public_metrics: Optional[Dict[str, int]]
    organic_metrics: Optional[Dict[str, int]]
    promoted_metrics: Optional[Dict[str, int]]
    attachments: Optional[Dict]
    context_annotations: List[Dict]
    entities: Optional[Dict]
    geo: Optional[Dict]
    lang: str
    possibly_sensitive: bool
    reply_settings: str
    source: str
    withheld: Optional[Dict]
    hashtags: List[str]
    mentions: List[str]
    urls: List[str]
    media: List[Dict]
    is_quote_tweet: bool = False
    is_retweet: bool = False
    is_reply: bool = False
    thread_length: int = 1
    engagement_rate: float = 0.0
    sentiment_score: float = 0.0


@dataclass
class TwitterUserData:
    """Twitter user data structure"""
    user_id: str
    username: str
    name: str
    description: str
    location: str
    url: str
    profile_image_url: str
    protected: bool
    verified: bool
    verified_type: str
    created_at: datetime
    public_metrics: Dict[str, int]  # followers_count, following_count, etc.
    entities: Optional[Dict]
    pinned_tweet_id: Optional[str]
    withheld: Optional[Dict]
    bio_hashtags: List[str]
    bio_mentions: List[str]
    bio_urls: List[str]
    account_age_days: int
    tweets_per_day: float
    engagement_rate: float = 0.0
    influence_score: float = 0.0
    bot_probability: float = 0.0


@dataclass
class TwitterThreadData:
    """Twitter thread data structure"""
    thread_id: str
    author_id: str
    author_username: str
    tweets: List[TwitterTweetData]
    total_tweets: int
    total_engagement: int
    created_at: datetime
    last_updated: datetime
    topic: Optional[str]
    thread_hashtags: List[str]
    thread_mentions: List[str]


class TwitterCrawlerEngine(BaseCrawlerEngine):
    """
    Advanced Twitter/X crawler engine with comprehensive data extraction.
    
    Features:
    - Twitter API v2 integration
    - Tweet and user analytics extraction
    - Thread detection and analysis
    - Hashtag and trend monitoring
    - Sentiment analysis integration
    - Bot detection algorithms
    - Rate limiting and error handling
    """
    
    def __init__(self, api_credentials: Dict, config: Optional[Dict] = None):
        """Initialize Twitter crawler engine"""
        super().__init__(config)
        self.api_credentials = api_credentials
        self.client = None
        self.session = None
        self.rate_limiter = RateLimiter(
            requests_per_minute=300,  # Twitter API v2 limits
            requests_per_hour=15000,
            requests_per_day=300000
        )
        self.cache_manager = CacheManager(
            cache_duration=timedelta(minutes=10),
            max_cache_size=5000
        )
        self.proxy_manager = ProxyManager() if config and config.get('use_proxies') else None
        self._setup_twitter_client()
        self._setup_session()
        self._setup_selenium_driver()
    
    def _setup_twitter_client(self) -> None:
        """Setup Twitter API v2 client"""



        try:
            self.client = tweepy.Client(
                bearer_token=self.api_credentials.get('bearer_token'),
                consumer_key=self.api_credentials.get('api_key'),
                consumer_secret=self.api_credentials.get('api_secret'),
                access_token=self.api_credentials.get('access_token'),
                access_token_secret=self.api_credentials.get('access_token_secret'),
                wait_on_rate_limit=True
            )
            
            # Test authentication
            me = self.client.get_me()
            if me.data:
                logger.info(f"Twitter API client authenticated as @{me.data.username}")
            else:
                raise AuthenticationError("Twitter API authentication failed")
                
        except Exception as e:
            logger.error(f"Failed to setup Twitter client: {e}")
            raise AuthenticationError(f"Twitter API setup failed: {e}")
    
    def _setup_session(self) -> None:
        """Setup HTTP session for web scraping"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://twitter.com/',
        })
        logger.info("Twitter HTTP session initialized")
    
    def _setup_selenium_driver(self) -> None:
        """Setup Selenium WebDriver for advanced scraping"""



        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Selenium WebDriver initialized for Twitter")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.driver = None
    
    async def get_user_profile(self, username: str) -> Optional[TwitterUserData]:
        """
        Get comprehensive user profile data
        
        Args:
            username: Twitter username (with or without @)
            
        Returns:
            User profile data or None if not found
        """
        await self.rate_limiter.wait()
        
        username = username.lstrip('@')  # Remove @ if present
        cache_key = f"user_{username.lower()}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Use Twitter API v2
            user_response = self.client.get_user(
                username=username,
                user_fields=[
                    'created_at', 'description', 'entities', 'id', 'location',
                    'name', 'pinned_tweet_id', 'profile_image_url', 'protected',
                    'public_metrics', 'url', 'username', 'verified', 'verified_type',
                    'withheld'
                ]
            )
            
            if not user_response.data:
                raise ContentNotFoundError(f"User @{username} not found")
            
            user = user_response.data
            user_data = await self._parse_user_data(user)
            
            await self.cache_manager.set(cache_key, user_data)
            return user_data
            
        except tweepy.NotFound:
            raise ContentNotFoundError(f"User @{username} not found")
        except tweepy.Unauthorized:
            raise SuspendedAccountError(f"User @{username} is suspended or protected")
        except tweepy.TooManyRequests:
            raise RateLimitError("Twitter API rate limit exceeded")
        except Exception as e:
            logger.error(f"Error getting user profile for @{username}: {e}")
            raise CrawlerError(f"Failed to get user profile: {e}")
    
    async def get_user_tweets(
        self, 
        username: str, 
        max_tweets: int = 100,
        include_retweets: bool = False
    ) -> List[TwitterTweetData]:
        """
        Get recent tweets from a user
        
        Args:
            username: Twitter username
            max_tweets: Maximum number of tweets to retrieve
            include_retweets: Whether to include retweets
            
        Returns:
            List of tweet data
        """
        await self.rate_limiter.wait()
        
        username = username.lstrip('@')
        
        try:
            # Get user ID first
            user = self.client.get_user(username=username)
            if not user.data:
                raise ContentNotFoundError(f"User @{username} not found")
            
            user_id = user.data.id
            
            # Get tweets
            tweets_response = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_tweets, 100),  # API limit
                tweet_fields=[
                    'created_at', 'author_id', 'conversation_id', 'in_reply_to_user_id',
                    'referenced_tweets', 'attachments', 'context_annotations', 'entities',
                    'geo', 'lang', 'possibly_sensitive', 'public_metrics', 'reply_settings',
                    'source', 'text', 'withheld'
                ],
                expansions=['author_id', 'referenced_tweets.id', 'attachments.media_keys'],
                exclude=['replies'] if not include_retweets else None
            )
            
            if not tweets_response.data:
                return []
            
            tweets = []
            for tweet in tweets_response.data:
                tweet_data = await self._parse_tweet_data(tweet)
                tweets.append(tweet_data)
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error getting tweets for @{username}: {e}")
            raise CrawlerError(f"Failed to get tweets: {e}")
    
    async def search_tweets(
        self, 
        query: str, 
        max_tweets: int = 100,
        result_type: str = 'recent'
    ) -> List[TwitterTweetData]:
        """
        Search for tweets using Twitter API
        
        Args:
            query: Search query
            max_tweets: Maximum number of tweets to retrieve
            result_type: Type of results ('recent', 'popular')
            
        Returns:
            List of matching tweets
        """
        await self.rate_limiter.wait()
        
        try:
            tweets_response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_tweets, 100),
                tweet_fields=[
                    'created_at', 'author_id', 'conversation_id', 'in_reply_to_user_id',
                    'referenced_tweets', 'attachments', 'context_annotations', 'entities',
                    'geo', 'lang', 'possibly_sensitive', 'public_metrics', 'reply_settings',
                    'source', 'text', 'withheld'
                ],
                expansions=['author_id', 'referenced_tweets.id', 'attachments.media_keys']
            )
            
            if not tweets_response.data:
                return []
            
            tweets = []
            for tweet in tweets_response.data:
                tweet_data = await self._parse_tweet_data(tweet)
                tweets.append(tweet_data)
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error searching tweets with query '{query}': {e}")
            raise CrawlerError(f"Tweet search failed: {e}")
    
    async def get_trending_topics(self, location_id: int = 1) -> List[Dict]:
        """
        Get trending topics for a specific location
        
        Args:
            location_id: WOEID (Where On Earth ID) for location (1 = worldwide)
            
        Returns:
            List of trending topics
        """
        await self.rate_limiter.wait()
        
        try:
            # Note: This requires Twitter API v1.1 which may need different setup
            # For now, return empty list and implement with web scraping if needed
            logger.warning("Trending topics API not implemented - requires Twitter API v1.1")
            return []
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []
    
    async def detect_thread(self, tweet_id: str) -> Optional[TwitterThreadData]:
        """
        Detect and extract a Twitter thread starting from a tweet
        
        Args:
            tweet_id: ID of the first tweet in the thread
            
        Returns:
            Thread data if thread detected, None otherwise
        """
        await self.rate_limiter.wait()
        
        try:
            # Get the initial tweet
            initial_tweet_response = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=[
                    'created_at', 'author_id', 'conversation_id', 'in_reply_to_user_id',
                    'referenced_tweets', 'public_metrics', 'text'
                ],
                expansions=['author_id']
            )
            
            if not initial_tweet_response.data:
                return None
            
            initial_tweet = initial_tweet_response.data
            author_id = initial_tweet.author_id
            conversation_id = initial_tweet.conversation_id
            
            # Search for other tweets in the conversation by the same author
            thread_tweets = []
            thread_tweets.append(await self._parse_tweet_data(initial_tweet))
            
            # Get conversation tweets
            conversation_response = self.client.search_recent_tweets(
                query=f"conversation_id:{conversation_id} from:{author_id}",
                max_results=100,
                tweet_fields=[
                    'created_at', 'author_id', 'conversation_id', 'in_reply_to_user_id',
                    'referenced_tweets', 'public_metrics', 'text'
                ]
            )
            
            if conversation_response.data:
                for tweet in conversation_response.data:
                    if tweet.id != tweet_id:  # Don't duplicate the initial tweet
                        thread_tweets.append(await self._parse_tweet_data(tweet))
            
            # Sort by creation time
            thread_tweets.sort(key=lambda x: x.created_at)
            
            if len(thread_tweets) > 1:
                # Calculate thread metrics
                total_engagement = sum(
                    tweet.public_metrics.get('like_count', 0) +
                    tweet.public_metrics.get('retweet_count', 0) +
                    tweet.public_metrics.get('reply_count', 0)
                    for tweet in thread_tweets
                )
                
                # Extract thread hashtags and mentions
                all_hashtags = set()
                all_mentions = set()
                for tweet in thread_tweets:
                    all_hashtags.update(tweet.hashtags)
                    all_mentions.update(tweet.mentions)
                
                return TwitterThreadData(
                    thread_id=tweet_id,
                    author_id=author_id,
                    author_username=thread_tweets[0].author_username,
                    tweets=thread_tweets,
                    total_tweets=len(thread_tweets),
                    total_engagement=total_engagement,
                    created_at=thread_tweets[0].created_at,
                    last_updated=thread_tweets[-1].created_at,
                    topic=None,  # Could be implemented with NLP
                    thread_hashtags=list(all_hashtags),
                    thread_mentions=list(all_mentions)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting thread for tweet {tweet_id}: {e}")
            return None
    
    async def monitor_hashtag(self, hashtag: str, duration_hours: int = 24) -> AsyncGenerator[TwitterTweetData, None]:
        """
        Monitor a hashtag for new tweets in real-time
        
        Args:
            hashtag: Hashtag to monitor (with or without #)
            duration_hours: How long to monitor in hours
            
        Yields:
            New tweets containing the hashtag
        """
        hashtag = hashtag.lstrip('#')
        query = f"#{hashtag} -is:retweet"
        
        end_time = datetime.now() + timedelta(hours=duration_hours)
        last_tweet_id = None
        
        while datetime.now() < end_time:
            try:
                await self.rate_limiter.wait()
                
                search_params = {
                    'query': query,
                    'max_results': 50,
                    'tweet_fields': [
                        'created_at', 'author_id', 'public_metrics', 'text', 'entities'
                    ],
                    'expansions': ['author_id']
                }
                
                if last_tweet_id:
                    search_params['since_id'] = last_tweet_id
                
                tweets_response = self.client.search_recent_tweets(**search_params)
                
                if tweets_response.data:
                    for tweet in reversed(tweets_response.data):  # Process oldest first
                        tweet_data = await self._parse_tweet_data(tweet)
                        yield tweet_data
                        last_tweet_id = tweet.id
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error monitoring hashtag #{hashtag}: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def detect_content_theft(
        self, 
        original_tweet: Dict, 
        search_keywords: List[str]
    ) -> List[Dict]:
        """
        Detect potential content theft or plagiarism
        
        Args:
            original_tweet: Original tweet metadata
            search_keywords: Keywords to search for potential copies
            
        Returns:
            List of potential theft matches
        """
        theft_candidates = []
        
        for keyword in search_keywords:
            try:
                tweets = await self.search_tweets(keyword, max_tweets=50)
                
                for tweet in tweets:
                    if tweet.author_username.lower() == original_tweet.get('username', '').lower():
                        continue  # Skip original author
                    
                    similarity_score = await self._calculate_tweet_similarity(
                        original_tweet,
                        asdict(tweet)
                    )
                    
                    if similarity_score > 0.7:  # 70% similarity threshold
                        theft_candidates.append({
                            'tweet_data': tweet,
                            'similarity_score': similarity_score,
                            'detected_at': datetime.now(),
                            'search_keyword': keyword,
                            'theft_type': await self._classify_theft_type(original_tweet, tweet)
                        })
                        
            except Exception as e:
                logger.error(f"Error detecting theft for keyword '{keyword}': {e}")
                continue
        
        return theft_candidates
    
    async def _parse_user_data(self, user) -> TwitterUserData:
        """Parse Twitter API user data into structured format"""



        try:
            # Extract hashtags, mentions, and URLs from bio
            bio_text = user.description or ""
            bio_hashtags = re.findall(r'#(\w+)', bio_text)
            bio_mentions = re.findall(r'@(\w+)', bio_text)
            
            # Extract URLs
            bio_urls = []
            if user.entities and 'description' in user.entities:
                urls = user.entities['description'].get('urls', [])
                bio_urls = [url['expanded_url'] for url in urls]
            
            # Calculate account age
            account_age = (datetime.now(user.created_at.tzinfo) - user.created_at).days
            
            # Calculate tweets per day
            tweets_per_day = 0.0
            if account_age > 0 and user.public_metrics:
                tweets_per_day = user.public_metrics.get('tweet_count', 0) / account_age
            
            return TwitterUserData(
                user_id=user.id,
                username=user.username,
                name=user.name,
                description=bio_text,
                location=user.location or "",
                url=user.url or "",
                profile_image_url=user.profile_image_url or "",
                protected=user.protected,
                verified=user.verified,
                verified_type=getattr(user, 'verified_type', 'none'),
                created_at=user.created_at,
                public_metrics=user.public_metrics or {},
                entities=user.entities,
                pinned_tweet_id=user.pinned_tweet_id,
                withheld=user.withheld,
                bio_hashtags=bio_hashtags,
                bio_mentions=bio_mentions,
                bio_urls=bio_urls,
                account_age_days=account_age,
                tweets_per_day=tweets_per_day,
                engagement_rate=await self._calculate_user_engagement_rate(user),
                influence_score=await self._calculate_influence_score(user),
                bot_probability=await self._calculate_bot_probability(user)
            )
            
        except Exception as e:
            logger.error(f"Error parsing user data: {e}")
            raise
    
    async def _parse_tweet_data(self, tweet) -> TwitterTweetData:
        """Parse Twitter API tweet data into structured format"""



        try:
            # Extract hashtags, mentions, and URLs
            hashtags = []
            mentions = []
            urls = []
            media = []
            
            if tweet.entities:
                hashtags = [tag['tag'] for tag in tweet.entities.get('hashtags', [])]
                mentions = [mention['username'] for mention in tweet.entities.get('mentions', [])]
                urls = [url['expanded_url'] for url in tweet.entities.get('urls', [])]
            
            if tweet.attachments and tweet.attachments.get('media_keys'):
                # Media details would need to be extracted from includes
                media = [{'media_key': key} for key in tweet.attachments['media_keys']]
            
            # Determine tweet type
            is_retweet = bool(tweet.referenced_tweets and 
                            any(ref['type'] == 'retweeted' for ref in tweet.referenced_tweets))
            is_quote_tweet = bool(tweet.referenced_tweets and 
                                any(ref['type'] == 'quoted' for ref in tweet.referenced_tweets))
            is_reply = bool(tweet.in_reply_to_user_id)
            
            # Calculate engagement rate
            engagement_rate = 0.0
            if tweet.public_metrics:
                total_engagement = (
                    tweet.public_metrics.get('like_count', 0) +
                    tweet.public_metrics.get('retweet_count', 0) +
                    tweet.public_metrics.get('reply_count', 0) +
                    tweet.public_metrics.get('quote_count', 0)
                )
                # Note: We don't have impression count in this context
                engagement_rate = total_engagement  # Absolute engagement for now
            
            return TwitterTweetData(
                tweet_id=tweet.id,
                url=f"https://twitter.com/user/status/{tweet.id}",
                text=tweet.text,
                created_at=tweet.created_at,
                author_id=tweet.author_id,
                author_username="",  # Would need to be filled from expansions
                author_name="",  # Would need to be filled from expansions
                conversation_id=tweet.conversation_id,
                in_reply_to_user_id=tweet.in_reply_to_user_id,
                referenced_tweets=tweet.referenced_tweets or [],
                public_metrics=tweet.public_metrics or {},
                non_public_metrics=getattr(tweet, 'non_public_metrics', None),
                organic_metrics=getattr(tweet, 'organic_metrics', None),
                promoted_metrics=getattr(tweet, 'promoted_metrics', None),
                attachments=tweet.attachments,
                context_annotations=tweet.context_annotations or [],
                entities=tweet.entities,
                geo=tweet.geo,
                lang=tweet.lang,
                possibly_sensitive=tweet.possibly_sensitive,
                reply_settings=tweet.reply_settings,
                source=tweet.source,
                withheld=tweet.withheld,
                hashtags=hashtags,
                mentions=mentions,
                urls=urls,
                media=media,
                is_quote_tweet=is_quote_tweet,
                is_retweet=is_retweet,
                is_reply=is_reply,
                engagement_rate=engagement_rate
            )
            
        except Exception as e:
            logger.error(f"Error parsing tweet data: {e}")
            raise
    
    async def _calculate_user_engagement_rate(self, user) -> float:
        """Calculate user's average engagement rate"""



        try:
            if not user.public_metrics:
                return 0.0
            
            followers_count = user.public_metrics.get('followers_count', 0)
            if followers_count == 0:
                return 0.0
            
            # This would need recent tweets analysis for accurate calculation
            # For now, return a basic estimate
            return 0.0
            
        except Exception:
            return 0.0
    
    async def _calculate_influence_score(self, user) -> float:
        """Calculate user's influence score"""



        try:
            if not user.public_metrics:
                return 0.0
            
            followers = user.public_metrics.get('followers_count', 0)
            following = user.public_metrics.get('following_count', 0)
            tweets = user.public_metrics.get('tweet_count', 0)
            
            # Simple influence score calculation
            if following == 0:
                follower_ratio = followers
            else:
                follower_ratio = followers / following
            
            # Normalize to 0-1 scale
            influence_score = min(1.0, (follower_ratio + tweets/10000) / 2)
            return influence_score
            
        except Exception:
            return 0.0
    
    async def _calculate_bot_probability(self, user) -> float:
        """Calculate probability that user is a bot"""



        try:
            bot_score = 0.0
            
            # Check various bot indicators
            if user.public_metrics:
                followers = user.public_metrics.get('followers_count', 0)
                following = user.public_metrics.get('following_count', 0)
                
                # High following to follower ratio
                if followers > 0 and following / followers > 10:
                    bot_score += 0.3
                
                # Very high or very low tweet count
                tweets = user.public_metrics.get('tweet_count', 0)
                account_age = (datetime.now(user.created_at.tzinfo) - user.created_at).days
                
                if account_age > 0:
                    tweets_per_day = tweets / account_age
                    if tweets_per_day > 50:  # Very high activity
                        bot_score += 0.2
                    elif tweets_per_day < 0.1:  # Very low activity
                        bot_score += 0.1
            
            # No profile picture
            if not user.profile_image_url or 'default_profile' in user.profile_image_url:
                bot_score += 0.2
            
            # Default display name
            if user.name == user.username:
                bot_score += 0.1
            
            # Very short or no bio
            if not user.description or len(user.description) < 10:
                bot_score += 0.1
            
            return min(1.0, bot_score)
            
        except Exception:
            return 0.0
    
    async def _calculate_tweet_similarity(self, original: Dict, candidate: Dict) -> float:
        """Calculate similarity between original and candidate tweets"""



        try:
            # Text similarity
            original_text = original.get('text', '').lower()
            candidate_text = candidate.get('text', '').lower()
            
            text_similarity = 0.0
            if original_text and candidate_text:
                original_words = set(original_text.split())
                candidate_words = set(candidate_text.split())
                if original_words and candidate_words:
                    common_words = original_words.intersection(candidate_words)
                    text_similarity = len(common_words) / len(original_words.union(candidate_words))
            
            # Hashtag similarity
            original_hashtags = set(original.get('hashtags', []))
            candidate_hashtags = set(candidate.get('hashtags', []))
            
            hashtag_similarity = 0.0
            if original_hashtags and candidate_hashtags:
                common_hashtags = original_hashtags.intersection(candidate_hashtags)
                hashtag_similarity = len(common_hashtags) / len(original_hashtags.union(candidate_hashtags))
            
            # URL similarity
            original_urls = set(original.get('urls', []))
            candidate_urls = set(candidate.get('urls', []))
            
            url_similarity = 0.0
            if original_urls and candidate_urls:
                common_urls = original_urls.intersection(candidate_urls)
                url_similarity = len(common_urls) / len(original_urls.union(candidate_urls))
            
            # Weighted average
            overall_similarity = (
                text_similarity * 0.6 +
                hashtag_similarity * 0.25 +
                url_similarity * 0.15
            )
            
            return overall_similarity
            
        except Exception as e:
            logger.error(f"Error calculating tweet similarity: {e}")
            return 0.0
    
    async def _classify_theft_type(self, original: Dict, candidate: TwitterTweetData) -> str:
        """Classify the type of potential content theft"""



        try:
            # Exact copy
            if original.get('text', '').strip() == candidate.text.strip():
                return "exact_copy"
            
            # Quote tweet without attribution
            if candidate.is_quote_tweet and candidate.text in original.get('text', ''):
                return "unattributed_quote"
            
            # Hashtag theft
            original_hashtags = set(original.get('hashtags', []))
            candidate_hashtags = set(candidate.hashtags)
            
            if len(original_hashtags.intersection(candidate_hashtags)) > len(original_hashtags) * 0.8:
                return "hashtag_theft"
            
            # Paraphrasing
            if len(candidate.text) > 0 and original.get('text'):
                return "paraphrasing"
            
            return "potential_theft"
            
        except Exception:
            return "unknown"
    
    async def cleanup(self) -> None:
        """Cleanup resources"""



        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            if hasattr(self, 'session') and self.session:
                self.session.close()
            await self.cache_manager.cleanup()
            logger.info("Twitter crawler engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""



        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
            if hasattr(self, 'session') and self.session:
                self.session.close()
        except:
            pass


# Export main class
__all__ = ['TwitterCrawlerEngine', 'TwitterTweetData', 'TwitterUserData', 'TwitterThreadData']
