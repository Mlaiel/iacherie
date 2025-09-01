"""Twitter/X Crawler
=================

Professional Twitter/X content crawler with advanced monitoring capabilities.
Implements Twitter API v2 integration with intelligent rate limiting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import re

import aiohttp
import tweepy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..utils.rate_limiter import TwitterRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError
from ...database.models import CrawlResult, ContentMatch

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class TwitterTweet:
    """
Twitter tweet data structure."""
    tweet_id: str
    text: str
    author_id: str
    author_username: str
    author_name: str
    created_at: datetime
    public_metrics: Dict
    context_annotations: List[Dict]
    entities: Dict
    attachments: Dict
    referenced_tweets: List[Dict]
    lang: str
    reply_settings: str
    source: str
    geo: Optional[Dict]

@dataclass
class TwitterUser:
    """
Twitter user data structure."""
    user_id: str
    username: str
    name: str
    description: str
    profile_image_url: str
    verified: bool
    verified_type: str
    public_metrics: Dict
    created_at: datetime
    location: Optional[str]
    url: Optional[str]
    entities: Dict

@dataclass 
class TwitterSpace:
    """
Twitter Space data structure."""
    space_id: str
    title: str
    state: str
    host_ids: List[str]
    speaker_ids: List[str]
    is_ticketed: bool
    participant_count: int
    subscriber_count: int
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    topic_ids: List[str]
    lang: str

class TwitterCrawler:
    """
    Professional Twitter/X crawler implementation.
    
    Features:
    - Twitter API v2 integration
    - Real-time tweet monitoring
    - Advanced search and filtering
    - User profile analysis
    - Trending topics tracking
    - Space monitoring
    - Thread and conversation tracking
    - Sentiment analysis integration
    - Content similarity detection
    - Engagement rate calculations
    """
    
    def __init__(self):
        """
Initialize Twitter crawler."""
        # API credentials
        self.bearer_token = settings.TWITTER_BEARER_TOKEN
        self.api_key = settings.TWITTER_API_KEY
        self.api_secret = settings.TWITTER_API_SECRET
        self.access_token = settings.TWITTER_ACCESS_TOKEN
        self.access_secret = settings.TWITTER_ACCESS_SECRET
        
        # Initialize rate limiter
        self.rate_limiter = TwitterRateLimiter()
        self.proxy_manager = ProxyManager()
        self.user_agent_rotator = UserAgentRotator()
        self.session = None
        
        # Initialize Twitter API client
        self.client = None
        if self.bearer_token:
            try:
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_secret,
                    wait_on_rate_limit=True
                )
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {e}")
        
        # Base URLs
        self.api_base_url = "https://api.twitter.com/2"
        self.web_base_url = "https://twitter.com"
        
        # Selenium configuration
        self.selenium_options = webdriver.ChromeOptions()
        self.selenium_options.add_argument('--headless')
        self.selenium_options.add_argument('--no-sandbox')
        self.selenium_options.add_argument('--disable-dev-shm-usage')
        self.selenium_options.add_argument('--disable-gpu')
    
    async def __aenter__(self):
        """Async context manager entry."""
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'User-Agent': self.user_agent_rotator.get_user_agent()
        }
        self.session = aiohttp.ClientSession(headers=headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        sort_order: str = 'relevancy',
        tweet_fields: List[str] = None,
        user_fields: List[str] = None,
        expansions: List[str] = None
    ) -> List[TwitterTweet]:
        """
        Search tweets with advanced filtering.
        
        Args:
            query: Twitter search query
            max_results: Maximum number of tweets to return
            start_time: Filter tweets from this time
            end_time: Filter tweets until this time
            sort_order: Sort order (recency, relevancy)
            tweet_fields: Additional tweet fields to retrieve
            user_fields: Additional user fields to retrieve
            expansions: Data expansions to include
            
        Returns:
            List of Twitter tweet objects
        """
        try:
            # Rate limiting check
            await self.rate_limiter.wait_if_needed()
            
            if self.client:
                return await self._search_tweets_api(
                    query, max_results, start_time, end_time, 
                    sort_order, tweet_fields, user_fields, expansions
                )
            else:
                return await self._search_tweets_scraping(query, max_results)
                
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
            return []
    
    async def _search_tweets_api(
        self,
        query: str,
        max_results: int,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        sort_order: str,
        tweet_fields: List[str],
        user_fields: List[str],
        expansions: List[str]
    ) -> List[TwitterTweet]:
        """Search tweets using Twitter API v2."""
        try:
            # Default fields
            if not tweet_fields:
                tweet_fields = [
                    'id', 'text', 'author_id', 'created_at', 'public_metrics',
                    'context_annotations', 'entities', 'attachments', 'lang',
                    'reply_settings', 'source', 'geo', 'referenced_tweets'
                ]
            
            if not user_fields:
                user_fields = [
                    'id', 'username', 'name', 'description', 'profile_image_url',
                    'verified', 'verified_type', 'public_metrics', 'created_at'
                ]
            
            if not expansions:
                expansions = ['author_id', 'referenced_tweets.id', 'attachments.media_keys']
            
            tweets = []
            next_token = None
            
            while len(tweets) < max_results:
                # Build search parameters
                search_params = {
                    'query': query,
                    'max_results': min(100, max_results - len(tweets)),
                    'sort_order': sort_order,
                    'tweet.fields': ','.join(tweet_fields),
                    'user.fields': ','.join(user_fields),
                    'expansions': ','.join(expansions)
                }
                
                if start_time:
                    search_params['start_time'] = start_time.isoformat()
                if end_time:
                    search_params['end_time'] = end_time.isoformat()
                if next_token:
                    search_params['next_token'] = next_token
                
                # Execute search
                response = self.client.search_recent_tweets(**search_params)
                
                if not response.data:
                    break
                
                # Parse tweets
                for tweet in response.data:
                    parsed_tweet = self._parse_api_tweet_data(tweet, response.includes)
                    if parsed_tweet:
                        tweets.append(parsed_tweet)
                
                # Check for next page
                if hasattr(response.meta, 'next_token'):
                    next_token = response.meta.next_token
                else:
                    break
                
                await self.rate_limiter.update_usage(1)
            
            return tweets[:max_results]
            
        except Exception as e:
            logger.error(f"Twitter API search failed: {e}")
            return []
    
    def _parse_api_tweet_data(self, tweet, includes: Dict = None) -> Optional[TwitterTweet]:
        """Parse Twitter API tweet data."""
        try:
            # Get author information from includes
            author_username = ""
            author_name = ""
            if includes and 'users' in includes:
                for user in includes['users']:
                    if user.id == tweet.author_id:
                        author_username = user.username
                        author_name = user.name
                        break
            
            return TwitterTweet(
                tweet_id=tweet.id,
                text=tweet.text,
                author_id=tweet.author_id,
                author_username=author_username,
                author_name=author_name,
                created_at=tweet.created_at,
                public_metrics=tweet.public_metrics or {},
                context_annotations=tweet.context_annotations or [],
                entities=tweet.entities or {},
                attachments=tweet.attachments or {},
                referenced_tweets=tweet.referenced_tweets or [],
                lang=tweet.lang or 'en',
                reply_settings=tweet.reply_settings or 'everyone',
                source=tweet.source or '',
                geo=tweet.geo
            )
            
        except Exception as e:
            logger.error(f"Failed to parse tweet data: {e}")
            return None
    
    async def _search_tweets_scraping(self, query: str, max_results: int) -> List[TwitterTweet]:
        """Search tweets using web scraping as fallback."""
        try:
            driver = webdriver.Chrome(options=self.selenium_options)
            
            # Navigate to search page
            search_url = f"{self.web_base_url}/search?q={query}&f=live"
            driver.get(search_url)
            
            await asyncio.sleep(3)
            
            tweets = []
            scroll_count = 0
            max_scrolls = max_results // 20 + 2
            
            while len(tweets) < max_results and scroll_count < max_scrolls:
                # Find tweet elements
                tweet_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
                
                for element in tweet_elements:
                    if len(tweets) >= max_results:
                        break
                    
                    try:
                        tweet_data = await self._extract_tweet_from_element(element)
                        if tweet_data:
                            tweets.append(tweet_data)
                    except Exception as e:
                        logger.warning(f"Failed to extract tweet data: {e}")
                        continue
                
                # Scroll to load more tweets
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                scroll_count += 1
            
            driver.quit()
            return tweets[:max_results]
            
        except Exception as e:
            logger.error(f"Twitter scraping failed: {e}")
            if 'driver' in locals():
                driver.quit()
            return []
    
    async def _extract_tweet_from_element(self, element) -> Optional[TwitterTweet]:
        """Extract tweet data from DOM element."""
        try:
            # Extract text
            text_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']")
            text = text_elem.text if text_elem else ""
            
            # Extract author information
            author_elem = element.find_element(By.CSS_SELECTOR, "[data-testid='User-Name'] a")
            author_username = author_elem.get_attribute("href").split("/")[-1] if author_elem else ""
            
            # Extract tweet ID from link
            tweet_link = element.find_element(By.CSS_SELECTOR, "a[href*='/status/']")
            tweet_id = tweet_link.get_attribute("href").split("/status/")[-1] if tweet_link else ""
            
            # Extract hashtags and mentions
            hashtags = re.findall(r'#(\w+)', text)
            mentions = re.findall(r'@(\w+)', text)
            
            entities = {
                'hashtags': [{'tag': tag} for tag in hashtags],
                'mentions': [{'username': mention} for mention in mentions]
            }
            
            return TwitterTweet(
                tweet_id=tweet_id,
                text=text,
                author_id="",
                author_username=author_username,
                author_name="",
                created_at=datetime.now(),
                public_metrics={},
                context_annotations=[],
                entities=entities,
                attachments={},
                referenced_tweets=[],
                lang="en",
                reply_settings="everyone",
                source="",
                geo=None
            )
            
        except Exception as e:
            logger.warning(f"Failed to extract tweet from element: {e}")
            return None
    
    async def get_user_profile(self, username: str) -> Optional[TwitterUser]:
        """Get user profile information."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            if self.client:
                return await self._get_user_profile_api(username)
            else:
                return await self._get_user_profile_scraping(username)
                
        except Exception as e:
            logger.error(f"Failed to get user profile for {username}: {e}")
            return None
    
    async def _get_user_profile_api(self, username: str) -> Optional[TwitterUser]:
        """Get user profile using Twitter API."""
        try:
            user_fields = [
                'id', 'username', 'name', 'description', 'profile_image_url',
                'verified', 'verified_type', 'public_metrics', 'created_at',
                'location', 'url', 'entities'
            ]
            
            user = self.client.get_user(
                username=username,
                user_fields=user_fields
            )
            
            if not user.data:
                return None
            
            user_data = user.data
            
            await self.rate_limiter.update_usage(1)
            
            return TwitterUser(
                user_id=user_data.id,
                username=user_data.username,
                name=user_data.name,
                description=user_data.description or "",
                profile_image_url=user_data.profile_image_url or "",
                verified=user_data.verified or False,
                verified_type=user_data.verified_type or "",
                public_metrics=user_data.public_metrics or {},
                created_at=user_data.created_at,
                location=user_data.location,
                url=user_data.url,
                entities=user_data.entities or {}
            )
            
        except Exception as e:
            logger.error(f"API user profile failed for {username}: {e}")
            return None
    
    async def get_trending_topics(self, woeid: int = 1) -> List[Dict]:
        """Get trending topics for specific location."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            if self.client:
                # Note: Trending topics require Twitter API v1.1
                # This would need additional implementation
                logger.info("Trending topics feature requires Twitter API v1.1")
                return []
            else:
                return await self._get_trending_topics_scraping()
                
        except Exception as e:
            logger.error(f"Failed to get trending topics: {e}")
            return []
    
    async def _get_trending_topics_scraping(self) -> List[Dict]:
        """Get trending topics using web scraping."""
        try:
            driver = webdriver.Chrome(options=self.selenium_options)
            driver.get(f"{self.web_base_url}/explore/tabs/trending")
            
            await asyncio.sleep(3)
            
            trends = []
            trend_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='trend']")
            
            for element in trend_elements:
                try:
                    trend_text = element.text
                    # Parse trend information
                    lines = trend_text.split('\n')
                    if len(lines) >= 2:
                        trend_name = lines[1]
                        tweet_count = lines[2] if len(lines) > 2 else "0"
                        
                        trends.append({
                            'name': trend_name,
                            'tweet_volume': tweet_count,
                            'rank': len(trends) + 1
                        })
                except:
                    continue
            
            driver.quit()
            return trends
            
        except Exception as e:
            logger.error(f"Trending topics scraping failed: {e}")
            if 'driver' in locals():
                driver.quit()
            return []
    
    async def monitor_user_timeline(
        self,
        username: str,
        check_interval: int = 300
    ) -> AsyncGenerator[List[TwitterTweet], None]:
        """Monitor user timeline for new tweets."""
        last_check = datetime.now()
        seen_tweets = set()
        
        while True:
            try:
                # Get recent tweets from user
                user_tweets = await self.get_user_tweets(username, max_results=20)
                
                # Filter new tweets
                new_tweets = []
                for tweet in user_tweets:
                    if (tweet.tweet_id not in seen_tweets and 
                        tweet.created_at > last_check):
                        new_tweets.append(tweet)
                        seen_tweets.add(tweet.tweet_id)
                
                if new_tweets:
                    yield new_tweets
                
                last_check = datetime.now()
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"User timeline monitoring error for {username}: {e}")
                await asyncio.sleep(60)
    
    async def get_user_tweets(self, username: str, max_results: int = 20) -> List[TwitterTweet]:
        """Get recent tweets from user."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            if self.client:
                # Get user ID first
                user = self.client.get_user(username=username)
                if not user.data:
                    return []
                
                user_id = user.data.id
                
                # Get user tweets
                tweets_response = self.client.get_users_tweets(
                    id=user_id,
                    max_results=max_results,
                    tweet_fields=['id', 'text', 'created_at', 'public_metrics', 'entities'],
                    expansions=['author_id']
                )
                
                if not tweets_response.data:
                    return []
                
                tweets = []
                for tweet in tweets_response.data:
                    parsed_tweet = self._parse_api_tweet_data(tweet, tweets_response.includes)
                    if parsed_tweet:
                        tweets.append(parsed_tweet)
                
                await self.rate_limiter.update_usage(2)
                return tweets
            else:
                # Fallback to scraping user timeline
                return await self._scrape_user_timeline(username, max_results)
                
        except Exception as e:
            logger.error(f"Failed to get user tweets for {username}: {e}")
            return []
    
    async def _scrape_user_timeline(self, username: str, max_results: int) -> List[TwitterTweet]:
        """Scrape user timeline as fallback."""
        try:
            driver = webdriver.Chrome(options=self.selenium_options)
            driver.get(f"{self.web_base_url}/{username}")
            
            await asyncio.sleep(3)
            
            tweets = []
            scroll_count = 0
            max_scrolls = max_results // 20 + 2
            
            while len(tweets) < max_results and scroll_count < max_scrolls:
                tweet_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
                
                for element in tweet_elements:
                    if len(tweets) >= max_results:
                        break
                    
                    try:
                        tweet_data = await self._extract_tweet_from_element(element)
                        if tweet_data:
                            tweets.append(tweet_data)
                    except:
                        continue
                
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                scroll_count += 1
            
            driver.quit()
            return tweets[:max_results]
            
        except Exception as e:
            logger.error(f"User timeline scraping failed for {username}: {e}")
            if 'driver' in locals():
                driver.quit()
            return []
    
    async def analyze_tweet_engagement(self, tweet: TwitterTweet) -> Dict:
        """Analyze tweet engagement metrics."""
        try:
            metrics = tweet.public_metrics
            
            if not metrics:
                return {}
            
            # Extract metrics
            retweet_count = metrics.get('retweet_count', 0)
            like_count = metrics.get('like_count', 0)
            reply_count = metrics.get('reply_count', 0)
            quote_count = metrics.get('quote_count', 0)
            impression_count = metrics.get('impression_count', 0)
            
            # Calculate engagement
            total_engagement = retweet_count + like_count + reply_count + quote_count
            
            # Calculate engagement rate (if impressions available)
            engagement_rate = 0
            if impression_count > 0:
                engagement_rate = (total_engagement / impression_count) * 100
            
            # Tweet age analysis
            tweet_age = datetime.now() - tweet.created_at
            engagement_per_hour = total_engagement / max(tweet_age.total_seconds() / 3600, 1)
            
            return {
                'total_engagement': total_engagement,
                'engagement_rate': round(engagement_rate, 2),
                'retweet_count': retweet_count,
                'like_count': like_count,
                'reply_count': reply_count,
                'quote_count': quote_count,
                'impression_count': impression_count,
                'engagement_per_hour': round(engagement_per_hour, 2),
                'tweet_age_hours': round(tweet_age.total_seconds() / 3600, 1),
                'hashtag_count': len(tweet.entities.get('hashtags', [])),
                'mention_count': len(tweet.entities.get('mentions', [])),
                'has_media': bool(tweet.attachments)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze tweet engagement: {e}")
            return {}
    
    async def detect_similar_tweets(
        self,
        reference_tweet: TwitterTweet,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """Detect tweets similar to reference tweet."""
        try:
            similar_tweets = []
            
            # Extract keywords from reference tweet
            keywords = self._extract_keywords(reference_tweet.text)
            
            # Search using extracted keywords
            for keyword_set in keywords[:3]:  # Limit to top 3 keyword combinations
                search_query = " ".join(keyword_set)
                search_results = await self.search_tweets(
                    query=search_query,
                    max_results=50
                )
                
                for tweet in search_results:
                    if tweet.tweet_id == reference_tweet.tweet_id:
                        continue
                    
                    similarity = self._calculate_tweet_similarity(reference_tweet, tweet)
                    
                    if similarity >= similarity_threshold:
                        similar_tweets.append({
                            'tweet': tweet,
                            'similarity_score': similarity,
                            'match_factors': self._get_tweet_match_factors(reference_tweet, tweet)
                        })
            
            # Remove duplicates and sort by similarity
            unique_tweets = {}
            for match in similar_tweets:
                tweet_id = match['tweet'].tweet_id
                if tweet_id not in unique_tweets or match['similarity_score'] > unique_tweets[tweet_id]['similarity_score']:
                    unique_tweets[tweet_id] = match
            
            return sorted(unique_tweets.values(), key=lambda x: x['similarity_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Similar tweet detection failed: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[List[str]]:
        """Extract important keywords from tweet text."""
        # Remove URLs, mentions, hashtags for keyword extraction
        clean_text = re.sub(r'http\S+|@\w+|#\w+', '', text)
        
        # Simple keyword extraction (in practice, you'd use more sophisticated NLP)
        words = clean_text.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Create keyword combinations
        keyword_sets = []
        if len(keywords) >= 2:
            keyword_sets.append(keywords[:2])
        if len(keywords) >= 3:
            keyword_sets.append(keywords[:3])
        if keywords:
            keyword_sets.append([keywords[0]])
        
        return keyword_sets
    
    def _calculate_tweet_similarity(self, tweet1: TwitterTweet, tweet2: TwitterTweet) -> float:
        """
Calculate similarity score between two tweets."""
        # Text similarity
        text1_words = set(tweet1.text.lower().split())
        text2_words = set(tweet2.text.lower().split())
        text_similarity = len(text1_words & text2_words) / len(text1_words | text2_words) if text1_words | text2_words else 0
        
        # Author similarity
        author_similarity = 1.0 if tweet1.author_id == tweet2.author_id else 0.0
        
        # Hashtag similarity
        hashtags1 = [h.get('tag', '') for h in tweet1.entities.get('hashtags', [])]
        hashtags2 = [h.get('tag', '') for h in tweet2.entities.get('hashtags', [])]
        hashtag_similarity = len(set(hashtags1) & set(hashtags2)) / len(set(hashtags1) | set(hashtags2)) if hashtags1 or hashtags2 else 0
        
        # Time proximity
        time_diff = abs((tweet1.created_at - tweet2.created_at).total_seconds())
        time_similarity = max(0, 1 - (time_diff / (24 * 3600)))  # 24 hours max
        
        # Weighted average
        weights = {
            'text': 0.5,
            'author': 0.2,
            'hashtags': 0.2,
            'time': 0.1
        }
        
        similarity = (
            weights['text'] * text_similarity +
            weights['author'] * author_similarity +
            weights['hashtags'] * hashtag_similarity +
            weights['time'] * time_similarity
        )
        
        return similarity
    
    def _get_tweet_match_factors(self, tweet1: TwitterTweet, tweet2: TwitterTweet) -> List[str]:
        """
Get factors that contribute to tweet similarity."""
        factors = []
        
        if tweet1.author_id == tweet2.author_id:
            factors.append('same_author')
        
        # Check hashtag overlap
        hashtags1 = [h.get('tag', '') for h in tweet1.entities.get('hashtags', [])]
        hashtags2 = [h.get('tag', '') for h in tweet2.entities.get('hashtags', [])]
        common_hashtags = set(hashtags1) & set(hashtags2)
        if common_hashtags:
            factors.append(f'common_hashtags: {list(common_hashtags)[:3]}')
        
        # Check text similarity
        text1_words = set(tweet1.text.lower().split())
        text2_words = set(tweet2.text.lower().split())
        common_words = text1_words & text2_words
        if len(common_words) > 3:
            factors.append('similar_text')
        
        # Check if both have media
        if tweet1.attachments and tweet2.attachments:
            factors.append('both_have_media')
        
        return factors
