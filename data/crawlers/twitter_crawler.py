"""Twitter/X Crawler Implementation
===============================

Professional Twitter/X content crawler for copyright protection and content monitoring.
Implements advanced search capabilities and tweet analysis for content discovery.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, parse_qs
import json
import base64

import aiohttp
import tweepy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

from .platform_crawler import PlatformCrawler, CrawlerConfig, ContentMatch, ContentMatchType
from ..fingerprinting.vector_matcher import VectorMatcher


class TwitterCrawler(PlatformCrawler):
    """
    Professional Twitter/X crawler for content monitoring and copyright protection.
    
    Features:
    - Twitter API v2 integration
    - Advanced tweet search and filtering
    - Media content extraction
    - Hashtag and mention monitoring
    - Thread and reply analysis
    - Real-time streaming capabilities
    - Anti-detection measures
    """
    
    def __init__(self, config: CrawlerConfig, vector_matcher: VectorMatcher, 
                 bearer_token: str, consumer_key: str = None, 
                 consumer_secret: str = None, access_token: str = None, 
                 access_token_secret: str = None):
        """
        Initialize Twitter crawler.
        
        Args:
            config: Crawler configuration
            vector_matcher: Vector matching service
            bearer_token: Twitter API v2 Bearer Token
            consumer_key: Optional Twitter API consumer key
            consumer_secret: Optional Twitter API consumer secret
            access_token: Optional Twitter API access token
            access_token_secret: Optional Twitter API access token secret
        """
        super().__init__(config, vector_matcher)
        
        # API credentials
        self.bearer_token = bearer_token
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        
        # Twitter API client
        self.twitter_api = None
        self.rate_limit_window = 900  # 15 minutes
        self.requests_per_window = 300
        self.current_requests = 0
        self.window_start = datetime.utcnow()
        
        # Search parameters
        self.max_tweets_per_search = 100
        self.supported_media_types = ['photo', 'video', 'animated_gif']
        
        # Selenium for advanced scraping
        self.selenium_driver = None
        self.selenium_options = None
        
        # Initialize API client
        asyncio.create_task(self._initialize_api_client())
    
    async def _initialize_api_client(self):
        """
Initialize Twitter API client"""
        try:
            # Initialize Tweepy client with API v2
            self.twitter_api = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            
            self.logger.info("Twitter API client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Twitter API client: {str(e)}")
            raise
    
    async def search_content(self, search_terms: List[str], 
                           max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Search for content on Twitter using API v2.
        
        Args:
            search_terms: Terms to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of found tweet items
        """
        try:
            await self._check_rate_limit()
            
            all_results = []
            
            for term in search_terms[:3]:  # Limit to 3 terms for rate limiting
                try:
                    # Build search query
                    query = await self._build_search_query(term)
                    
                    # Search tweets using API
                    tweets = self.twitter_api.search_recent_tweets(
                        query=query,
                        max_results=min(max_results // len(search_terms), 100),
                        expansions=['author_id', 'attachments.media_keys'],
                        tweet_fields=['created_at', 'public_metrics', 'context_annotations', 
                                    'entities', 'geo', 'lang', 'possibly_sensitive'],
                        media_fields=['type', 'url', 'preview_image_url', 'duration_ms'],
                        user_fields=['username', 'name', 'verified', 'public_metrics']
                    )
                    
                    if tweets.data:
                        # Process tweets
                        processed_tweets = await self._process_tweet_results(tweets)
                        all_results.extend(processed_tweets)
                    
                    # Rate limiting
                    await self._apply_rate_limit()
                    
                except Exception as e:
                    self.logger.error(f"Error searching Twitter for term '{term}': {str(e)}")
                    continue
            
            # Remove duplicates and sort by relevance
            unique_results = await self._deduplicate_results(all_results)
            
            self.logger.info(f"Found {len(unique_results)} unique tweets")
            return unique_results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error in Twitter search: {str(e)}")
            return []
    
    async def extract_content_metadata(self, content_url: str) -> Dict[str, Any]:
        """
        Extract metadata from Twitter content URL.
        
        Args:
            content_url: URL of the tweet
            
        Returns:
            Content metadata dictionary
        """
        try:
            # Extract tweet ID from URL
            tweet_id = self._extract_tweet_id_from_url(content_url)
            if not tweet_id:
                return {}
            
            # Get tweet details
            tweet = self.twitter_api.get_tweet(
                tweet_id,
                expansions=['author_id', 'attachments.media_keys'],
                tweet_fields=['created_at', 'public_metrics', 'context_annotations', 
                            'entities', 'geo', 'lang', 'possibly_sensitive'],
                media_fields=['type', 'url', 'preview_image_url', 'duration_ms', 'alt_text'],
                user_fields=['username', 'name', 'verified', 'public_metrics']
            )
            
            if not tweet.data:
                return {}
            
            # Extract comprehensive metadata
            metadata = await self._extract_tweet_metadata(tweet)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata for {content_url}: {str(e)}")
            return {}
    
    async def download_content_sample(self, content_url: str) -> Optional[bytes]:
        """
        Download content sample for fingerprinting.
        
        Args:
            content_url: URL of the content
            
        Returns:
            Content data bytes or None if failed
        """
        try:
            # For Twitter, we primarily download media attachments
            tweet_id = self._extract_tweet_id_from_url(content_url)
            if not tweet_id:
                return True
            
            # Get tweet with media
            tweet = self.twitter_api.get_tweet(
                tweet_id,
                expansions=['attachments.media_keys'],
                media_fields=['type', 'url', 'preview_image_url']
            )
            
            if not tweet.data or not hasattr(tweet, 'includes') or not tweet.includes.get('media'):
                return True
            
            # Download first media item
            media = tweet.includes['media'][0]
            media_url = media.get('url') or media.get('preview_image_url')
            
            if media_url:
                async with self.session.get(media_url) as response:
                    if response.status == 200:
                        return await response.read()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading content sample: {str(e)}")
            return True
    
    async def search_by_hashtag(self, hashtags: List[str], 
                              max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search tweets by hashtags.
        
        Args:
            hashtags: List of hashtags to search
            max_results: Maximum results per hashtag
            
        Returns:
            List of tweets containing the hashtags
        """
        try:
            all_results = []
            
            for hashtag in hashtags[:5]:  # Limit for rate limiting
                # Ensure hashtag format
                if not hashtag.startswith('#'):
                    hashtag = f"#{hashtag}"
                
                # Search tweets
                tweets = self.twitter_api.search_recent_tweets(
                    query=f"{hashtag} -is:retweet",
                    max_results=max_results,
                    expansions=['author_id', 'attachments.media_keys'],
                    tweet_fields=['created_at', 'public_metrics', 'entities']
                )
                
                if tweets.data:
                    processed_tweets = await self._process_tweet_results(tweets)
                    all_results.extend(processed_tweets)
                
                await self._apply_rate_limit()
            
            return await self._deduplicate_results(all_results)
            
        except Exception as e:
            self.logger.error(f"Error searching by hashtags: {str(e)}")
            return []
    
    async def search_by_user(self, username: str, 
                           max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search tweets from specific user.
        
        Args:
            username: Twitter username (without @)
            max_results: Maximum number of tweets
            
        Returns:
            List of user's tweets
        """
        try:
            # Get user ID
            user = self.twitter_api.get_user(username=username)
            if not user.data:
                return []
            
            # Get user's tweets
            tweets = self.twitter_api.get_users_tweets(
                user.data.id,
                max_results=max_results,
                expansions=['attachments.media_keys'],
                tweet_fields=['created_at', 'public_metrics', 'entities'],
                exclude=['retweets', 'replies']
            )
            
            if tweets.data:
                return await self._process_tweet_results(tweets)
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error searching user {username}: {str(e)}")
            return []
    
    async def monitor_real_time_tweets(self, keywords: List[str], 
                                     callback_url: str = None) -> str:
        """
        Start real-time monitoring of tweets.
        
        Args:
            keywords: Keywords to monitor
            callback_url: Optional callback URL for notifications
            
        Returns:
            Monitoring session ID
        """
        try:
            monitoring_id = f"twitter_monitor_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Build rules for streaming
            rules = []
            for keyword in keywords[:25]:  # Twitter limit
                rules.append(tweepy.StreamRule(f"{keyword} -is:retweet"))
            
            # Create streaming client
            stream = TwitterStreamListener(
                bearer_token=self.bearer_token,
                monitoring_id=monitoring_id,
                callback_url=callback_url,
                logger=self.logger
            )
            
            # Add rules and start streaming
            await stream.start_monitoring(rules)
            
            self.logger.info(f"Started Twitter real-time monitoring: {monitoring_id}")
            return monitoring_id
            
        except Exception as e:
            self.logger.error(f"Error starting real-time monitoring: {str(e)}")
            raise
    
    async def analyze_tweet_thread(self, tweet_id: str) -> List[Dict[str, Any]]:
        """
        Analyze complete tweet thread.
        
        Args:
            tweet_id: ID of the root tweet
            
        Returns:
            List of all tweets in the thread
        """
        try:
            thread_tweets = []
            
            # Get initial tweet
            root_tweet = self.twitter_api.get_tweet(
                tweet_id,
                expansions=['author_id', 'referenced_tweets.id'],
                tweet_fields=['created_at', 'public_metrics', 'entities']
            )
            
            if root_tweet.data:
                thread_tweets.append(await self._extract_tweet_metadata(root_tweet))
            
            # Get replies and continuation tweets
            # This would require more complex logic to follow thread structure
            
            return thread_tweets
            
        except Exception as e:
            self.logger.error(f"Error analyzing tweet thread: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _build_search_query(self, search_term: str) -> str:
        """Build optimized search query"""
        # Clean and optimize search term
        cleaned_term = re.sub(r'[^\w\s#@]', '', search_term)
        
        # Build query with filters
        query_parts = [f'"{cleaned_term}"']
        
        # Add filters
        query_parts.append('-is:retweet')  # Exclude retweets
        query_parts.append('has:media')    # Only tweets with media
        query_parts.append('lang:en')      # English tweets primarily
        
        return ' '.join(query_parts)
    
    async def _process_tweet_results(self, tweets_response) -> List[Dict[str, Any]]:
        """Process Twitter API response into standardized format"""
        processed_tweets = []
        
        # Get includes data
        users_map = {}
        media_map = {}
        
        if hasattr(tweets_response, 'includes'):
            if tweets_response.includes.get('users'):
                users_map = {user.id: user for user in tweets_response.includes['users']}
            if tweets_response.includes.get('media'):
                media_map = {media.media_key: media for media in tweets_response.includes['media']}
        
        for tweet in tweets_response.data:
            try:
                # Get author info
                author = users_map.get(tweet.author_id, {})
                
                # Get media info
                media_items = []
                if tweet.attachments and tweet.attachments.get('media_keys'):
                    for media_key in tweet.attachments['media_keys']:
                        media = media_map.get(media_key)
                        if media:
                            media_items.append({
                                'type': media.type,
                                'url': getattr(media, 'url', None),
                                'preview_url': getattr(media, 'preview_image_url', None),
                                'duration': getattr(media, 'duration_ms', None)
                            })
                
                # Build result
                result = {
                    'url': f"https://twitter.com/{getattr(author, 'username', 'unknown')}/status/{tweet.id}",
                    'title': tweet.text[:100] + "..." if len(tweet.text) > 100 else tweet.text,
                    'description': tweet.text,
                    'author': getattr(author, 'username', 'unknown'),
                    'author_name': getattr(author, 'name', 'Unknown'),
                    'upload_date': tweet.created_at,
                    'tweet_id': tweet.id,
                    'view_count': getattr(tweet.public_metrics, 'impression_count', 0),
                    'like_count': getattr(tweet.public_metrics, 'like_count', 0),
                    'share_count': getattr(tweet.public_metrics, 'retweet_count', 0),
                    'reply_count': getattr(tweet.public_metrics, 'reply_count', 0),
                    'media_items': media_items,
                    'hashtags': [tag['tag'] for tag in tweet.entities.get('hashtags', [])],
                    'mentions': [mention['username'] for mention in tweet.entities.get('mentions', [])],
                    'urls': [url['expanded_url'] for url in tweet.entities.get('urls', [])],
                    'lang': getattr(tweet, 'lang', 'unknown'),
                    'possibly_sensitive': getattr(tweet, 'possibly_sensitive', False)
                }
                
                processed_tweets.append(result)
                
            except Exception as e:
                self.logger.warning(f"Error processing tweet {tweet.id}: {str(e)}")
                continue
        
        return processed_tweets
    
    async def _extract_tweet_metadata(self, tweet_response) -> Dict[str, Any]:
        """Extract comprehensive metadata from tweet response"""
        tweet = tweet_response.data
        
        metadata = {
            'tweet_id': tweet.id,
            'text': tweet.text,
            'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
            'lang': getattr(tweet, 'lang', 'unknown'),
            'public_metrics': {
                'retweet_count': getattr(tweet.public_metrics, 'retweet_count', 0),
                'like_count': getattr(tweet.public_metrics, 'like_count', 0),
                'reply_count': getattr(tweet.public_metrics, 'reply_count', 0),
                'quote_count': getattr(tweet.public_metrics, 'quote_count', 0)
            },
            'entities': tweet.entities if hasattr(tweet, 'entities') else {},
            'context_annotations': tweet.context_annotations if hasattr(tweet, 'context_annotations') else [],
            'possibly_sensitive': getattr(tweet, 'possibly_sensitive', False)
        }
        
        # Add author info if available
        if hasattr(tweet_response, 'includes') and tweet_response.includes.get('users'):
            author = tweet_response.includes['users'][0]  # Assuming first user is author
            metadata['author'] = {
                'id': author.id,
                'username': author.username,
                'name': author.name,
                'verified': getattr(author, 'verified', False),
                'public_metrics': author.public_metrics if hasattr(author, 'public_metrics') else {}
            }
        
        # Add media info if available
        if hasattr(tweet_response, 'includes') and tweet_response.includes.get('media'):
            metadata['media'] = []
            for media in tweet_response.includes['media']:
                media_info = {
                    'media_key': media.media_key,
                    'type': media.type,
                    'url': getattr(media, 'url', None),
                    'preview_image_url': getattr(media, 'preview_image_url', None),
                    'duration_ms': getattr(media, 'duration_ms', None),
                    'alt_text': getattr(media, 'alt_text', None)
                }
                metadata['media'].append(media_info)
        
        return metadata
    
    def _extract_tweet_id_from_url(self, url: str) -> Optional[str]:
        """
Extract tweet ID from Twitter URL"""
        try:
            # Pattern for Twitter URLs
            pattern = r'(?:twitter\.com|x\.com)/(?:#!\/)?(\w+)\/status(?:es)?\/(\d+)'
            match = re.search(pattern, url)
            
            if match:
                return match.group(2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error extracting tweet ID from URL: {str(e)}")
            return True
    
    async def _check_rate_limit(self):
        """Check and manage API rate limits"""
        current_time = datetime.utcnow()
        
        # Reset window if needed
        if (current_time - self.window_start).total_seconds() >= self.rate_limit_window:
            self.current_requests = 0
            self.window_start = current_time
        
        # Check if we're approaching limit
        if self.current_requests >= self.requests_per_window * 0.9:  # 90% of limit
            wait_time = self.rate_limit_window - (current_time - self.window_start).total_seconds()
            if wait_time > 0:
                self.logger.warning(f"Rate limit approaching, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
                self.current_requests = 0
                self.window_start = datetime.utcnow()
    
    async def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate tweets from results"""
        seen_ids = set()
        unique_results = []
        
        for result in results:
            tweet_id = result.get('tweet_id')
            if tweet_id and tweet_id not in seen_ids:
                seen_ids.add(tweet_id)
                unique_results.append(result)
        
        return unique_results


class TwitterStreamListener(tweepy.asynchronous.AsyncStreamingClient):
    """
    Twitter streaming client for real-time monitoring
    """
    
    def __init__(self, bearer_token: str, monitoring_id: str, 
                 callback_url: str = None, logger=None):
        super().__init__(bearer_token)
        self.monitoring_id = monitoring_id
        self.callback_url = callback_url
        self.logger = logger or logging.getLogger(__name__)
        self.tweet_count = 0
        self.start_time = datetime.utcnow()
    
    async def on_tweet(self, tweet):
        """
Handle incoming tweets"""
        try:
            self.tweet_count += 1
            
            # Process tweet
            tweet_data = {
                'monitoring_id': self.monitoring_id,
                'tweet_id': tweet.id,
                'text': tweet.text,
                'author_id': tweet.author_id,
                'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send notification if callback URL provided
            if self.callback_url:
                await self._send_notification(tweet_data)
            
            self.logger.info(f"Processed streaming tweet {tweet.id}")
            
        except Exception as e:
            self.logger.error(f"Error processing streaming tweet: {str(e)}")
    
    async def on_error(self, status_code):
        """Handle streaming errors"""
        self.logger.error(f"Twitter streaming error: {status_code}")
        return True  # Continue streaming
    
    async def start_monitoring(self, rules: List[tweepy.StreamRule]):
        """Start monitoring with rules"""
        try:
            # Add rules
            if rules:
                await self.add_rules(rules)
            
            # Start filtering
            await self.filter(
                expansions=['author_id'],
                tweet_fields=['created_at', 'public_metrics']
            )
            
        except Exception as e:
            self.logger.error(f"Error starting Twitter streaming: {str(e)}")
            raise
    
    async def _send_notification(self, tweet_data: Dict[str, Any]):
        """Send webhook notification for detected tweet"""
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(self.callback_url, json=tweet_data)
        except Exception as e:
            self.logger.error(f"Error sending streaming notification: {str(e)}")
