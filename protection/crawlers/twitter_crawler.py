"""🐦 Twitter/X Content Crawler
============================

Professional Twitter/X content discovery and monitoring system.
Integrates Twitter API v2 with advanced content analysis capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT WARNING: Unauthorized use, copying, or distribution of this code 
is strictly prohibited without explicit written permission from Fahed Mlaiel.
Contact: mlaiel@live.de for licensing and authorization.
"""
import asyncio
import logging
import re
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import tweepy
import requests
from urllib.parse import urljoin, urlparse

from .base_crawler import BasePlatformCrawler, CrawlResult, CrawlerStatus

logger = logging.getLogger(__name__)

@dataclass
class TwitterTweetInfo:
    """Twitter tweet information structure."""    tweet_id: str
    url: str
    text: str
    author_id: str
    author_username: str
    author_name: str
    created_at: datetime
    public_metrics: Dict[str, int]  # retweet_count, reply_count, like_count, quote_count
    context_annotations: List[Dict[str, Any]] = None
    entities: Dict[str, Any] = None  # hashtags, mentions, urls
    referenced_tweets: List[Dict[str, Any]] = None
    in_reply_to_user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    attachments: Dict[str, Any] = None
    geo: Dict[str, Any] = None
    lang: Optional[str] = None
    possibly_sensitive: bool = False
    source: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class TwitterUserInfo:
    """Twitter user information structure."""    user_id: str
    username: str
    name: str
    description: str
    public_metrics: Dict[str, int]  # followers_count, following_count, tweet_count, listed_count
    created_at: datetime
    location: Optional[str] = None
    url: Optional[str] = None
    profile_image_url: Optional[str] = None
    verified: bool = False
    verified_type: Optional[str] = None
    protected: bool = False
    entities: Dict[str, Any] = None

@dataclass
class TwitterSpaceInfo:
    """Twitter Space information structure."""    space_id: str
    state: str
    title: str
    host_ids: List[str]
    speaker_ids: List[str]
    is_ticketed: bool
    participant_count: int
    subscriber_count: int
    topic_ids: List[str]
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

class TwitterAPIClient:
    """Twitter API v2 client with comprehensive features."""    
    def __init__(
        self,
        bearer_token: str,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None
    ):
        """Initialize Twitter API client."""        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        
        # Initialize Tweepy client
        self.client = None
        self.api = None
        
        try:
            # Twitter API v2 client (for most operations)
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Twitter API v1.1 client (for some legacy operations)
            if all([api_key, api_secret, access_token, access_token_secret]):
                auth = tweepy.OAuth1UserHandler(
                    api_key, api_secret, access_token, access_token_secret
                )
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            logger.info("Twitter API client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            raise
        
        # Rate limiting tracking
        self.rate_limits = {}
        self.last_rate_limit_check = datetime.utcnow()
    
    async def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        tweet_fields: List[str] = None,
        user_fields: List[str] = None,
        expansions: List[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[TwitterTweetInfo]:
        """Search for tweets using Twitter API v2."""        if not tweet_fields:
            tweet_fields = [
                'id', 'text', 'author_id', 'created_at', 'public_metrics',
                'context_annotations', 'entities', 'referenced_tweets',
                'in_reply_to_user_id', 'conversation_id', 'attachments',
                'geo', 'lang', 'possibly_sensitive', 'source'
            ]
        
        if not user_fields:
            user_fields = ['id', 'name', 'username', 'verified', 'public_metrics']
        
        if not expansions:
            expansions = ['author_id', 'referenced_tweets.id', 'attachments.media_keys']
        
        try:
            # Build search parameters
            search_params = {
                'query': query,
                'max_results': min(max_results, 100),  # API limit
                'tweet_fields': tweet_fields,
                'user_fields': user_fields,
                'expansions': expansions
            }
            
            if start_time:
                search_params['start_time'] = start_time
            if end_time:
                search_params['end_time'] = end_time
            
            # Execute search
            response = self.client.search_recent_tweets(**search_params)
            
            if not response.data:
                return []
            
            # Parse results
            tweets = []
            users_dict = {}
            
            # Build users dictionary for quick lookup
            if response.includes and 'users' in response.includes:
                for user in response.includes['users']:
                    users_dict[user.id] = user
            
            # Process tweets
            for tweet in response.data:
                tweet_info = self._parse_tweet(tweet, users_dict)
                if tweet_info:
                    tweets.append(tweet_info)
            
            logger.info(f"Found {len(tweets)} tweets for query: {query}")
            return tweets
            
        except tweepy.TooManyRequests:
            logger.warning("Twitter API rate limit exceeded")
            raise Exception("Twitter API rate limit exceeded")
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
            raise
    
    def _parse_tweet(self, tweet, users_dict: Dict[str, Any]) -> Optional[TwitterTweetInfo]:
        """Parse tweet data from API response."""        try:
            # Get author info
            author = users_dict.get(tweet.author_id)
            author_username = author.username if author else 'unknown'
            author_name = author.name if author else 'Unknown'
            
            # Create tweet URL
            tweet_url = f"https://twitter.com/{author_username}/status/{tweet.id}"
            
            return TwitterTweetInfo(
                tweet_id=str(tweet.id),
                url=tweet_url,
                text=tweet.text,
                author_id=str(tweet.author_id),
                author_username=author_username,
                author_name=author_name,
                created_at=tweet.created_at,
                public_metrics=tweet.public_metrics or {},
                context_annotations=tweet.context_annotations,
                entities=tweet.entities,
                referenced_tweets=tweet.referenced_tweets,
                in_reply_to_user_id=str(tweet.in_reply_to_user_id) if tweet.in_reply_to_user_id else None,
                conversation_id=str(tweet.conversation_id) if tweet.conversation_id else None,
                attachments=tweet.attachments,
                geo=tweet.geo,
                lang=tweet.lang,
                possibly_sensitive=tweet.possibly_sensitive or False,
                source=tweet.source,
                metadata={
                    'api_version': '2.0',
                    'extracted_at': datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing tweet: {e}")
            return None
    
    async def get_user_tweets(
        self,
        user_id: str,
        max_results: int = 100,
        exclude: List[str] = None
    ) -> List[TwitterTweetInfo]:
        """Get tweets from a specific user."""        try:
            if not exclude:
                exclude = ['retweets', 'replies']
            
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                exclude=exclude,
                tweet_fields=[
                    'id', 'text', 'created_at', 'public_metrics',
                    'context_annotations', 'entities', 'attachments'
                ]
            )
            
            if not response.data:
                return []
            
            tweets = []
            for tweet in response.data:
                tweet_info = self._parse_tweet(tweet, {user_id: {'username': 'user', 'name': 'User'}})
                if tweet_info:
                    tweets.append(tweet_info)
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error getting user tweets: {e}")
            return []
    
    async def get_user_by_username(self, username: str) -> Optional[TwitterUserInfo]:
        """Get user information by username."""        try:
            response = self.client.get_user(
                username=username,
                user_fields=[
                    'id', 'name', 'username', 'description', 'public_metrics',
                    'created_at', 'location', 'url', 'profile_image_url',
                    'verified', 'verified_type', 'protected', 'entities'
                ]
            )
            
            if not response.data:
                return None
            
            user = response.data
            return TwitterUserInfo(
                user_id=str(user.id),
                username=user.username,
                name=user.name,
                description=user.description or '',
                public_metrics=user.public_metrics or {},
                created_at=user.created_at,
                location=user.location,
                url=user.url,
                profile_image_url=user.profile_image_url,
                verified=user.verified or False,
                verified_type=user.verified_type,
                protected=user.protected or False,
                entities=user.entities
            )
            
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    async def search_spaces(self, query: str, max_results: int = 10) -> List[TwitterSpaceInfo]:
        """Search for Twitter Spaces."""        try:
            response = self.client.search_spaces(
                query=query,
                max_results=min(max_results, 100),
                space_fields=[
                    'id', 'state', 'title', 'host_ids', 'speaker_ids',
                    'is_ticketed', 'participant_count', 'subscriber_count',
                    'topic_ids', 'created_at', 'started_at', 'ended_at'
                ]
            )
            
            if not response.data:
                return []
            
            spaces = []
            for space in response.data:
                space_info = TwitterSpaceInfo(
                    space_id=space.id,
                    state=space.state,
                    title=space.title,
                    host_ids=space.host_ids or [],
                    speaker_ids=space.speaker_ids or [],
                    is_ticketed=space.is_ticketed or False,
                    participant_count=space.participant_count or 0,
                    subscriber_count=space.subscriber_count or 0,
                    topic_ids=space.topic_ids or [],
                    created_at=space.created_at,
                    started_at=space.started_at,
                    ended_at=space.ended_at
                )
                spaces.append(space_info)
            
            return spaces
            
        except Exception as e:
            logger.error(f"Error searching spaces: {e}")
            return []
    
    async def get_trending_topics(self, woeid: int = 1) -> List[Dict[str, Any]]:
        """Get trending topics (requires API v1.1)."""        if not self.api:
            logger.warning("Twitter API v1.1 not available for trending topics")
            return []
        
        try:
            trends = self.api.get_place_trends(woeid)
            
            if not trends:
                return []
            
            trending_topics = []
            for trend in trends[0]['trends']:
                trending_topics.append({
                    'name': trend['name'],
                    'url': trend['url'],
                    'promoted_content': trend['promoted_content'],
                    'query': trend['query'],
                    'tweet_volume': trend['tweet_volume']
                })
            
            return trending_topics
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []

class TwitterCrawler(BasePlatformCrawler):
    """    Professional Twitter/X Content Crawler
    ======================================
    
    Advanced Twitter content discovery and monitoring system featuring:
    - Twitter API v2 integration with comprehensive tweet data
    - Real-time tweet streaming and monitoring
    - User profile and timeline analysis
    - Hashtag and keyword tracking
    - Trending topics monitoring
    - Twitter Spaces discovery
    - Advanced search and filtering capabilities
    """    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Twitter crawler."""        super().__init__("twitter", config)
        
        # API configuration
        self.bearer_token = config.get('bearer_token')
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.access_token = config.get('access_token')
        self.access_token_secret = config.get('access_token_secret')
        
        # Search configuration
        self.max_results_per_search = config.get('max_results_per_search', 100)
        self.default_tweet_fields = config.get('tweet_fields', [
            'id', 'text', 'author_id', 'created_at', 'public_metrics',
            'context_annotations', 'entities', 'lang'
        ])
        
        # Initialize API client
        self.api_client = None
        
        if self.bearer_token:
            try:
                self.api_client = TwitterAPIClient(
                    bearer_token=self.bearer_token,
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret
                )
                logger.info("Twitter API client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter API: {e}")
                raise
        else:
            raise ValueError("Twitter bearer token is required")
    
    async def search_content(
        self,
        query: str,
        content_type: str = 'tweet',
        max_results: int = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CrawlResult]:
        """Search for content on Twitter."""        if not self.api_client:
            raise Exception("Twitter API client not available")
        
        max_results = max_results or self.max_results_per_search
        
        try:
            # Apply filters to query
            enhanced_query = self._build_search_query(query, filters)
            
            # Extract time filters
            start_time = None
            end_time = None
            if filters:
                start_time = filters.get('start_time')
                end_time = filters.get('end_time')
            
            # Search tweets
            tweets = await self.api_client.search_tweets(
                query=enhanced_query,
                max_results=max_results,
                start_time=start_time,
                end_time=end_time
            )
            
            # Convert to CrawlResult format
            results = await self._convert_tweets_to_results(tweets)
            
            logger.info(f"Twitter search '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
            return []
    
    def _build_search_query(self, base_query: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """Build enhanced search query with filters."""        query_parts = [base_query]
        
        if not filters:
            return base_query
        
        # Language filter
        if 'lang' in filters:
            query_parts.append(f"lang:{filters['lang']}")
        
        # Exclude retweets
        if filters.get('exclude_retweets', False):
            query_parts.append('-is:retweet')
        
        # Include only verified users
        if filters.get('verified_only', False):
            query_parts.append('is:verified')
        
        # Minimum engagement
        if 'min_retweets' in filters:
            query_parts.append(f"min_retweets:{filters['min_retweets']}")
        
        if 'min_faves' in filters:
            query_parts.append(f"min_faves:{filters['min_faves']}")
        
        if 'min_replies' in filters:
            query_parts.append(f"min_replies:{filters['min_replies']}")
        
        # Media filters
        if filters.get('has_images', False):
            query_parts.append('has:images')
        
        if filters.get('has_videos', False):
            query_parts.append('has:videos')
        
        if filters.get('has_media', False):
            query_parts.append('has:media')
        
        # Location filter
        if 'location' in filters:
            query_parts.append(f'place:"{filters["location"]}"')
        
        return ' '.join(query_parts)
    
    async def _convert_tweets_to_results(self, tweets: List[TwitterTweetInfo]) -> List[CrawlResult]:
        """Convert Twitter tweets to CrawlResult format."""        results = []
        
        for tweet in tweets:
            try:
                # Extract hashtags and mentions
                hashtags = []
                mentions = []
                urls = []
                
                if tweet.entities:
                    hashtags = [tag['tag'] for tag in tweet.entities.get('hashtags', [])]
                    mentions = [mention['username'] for mention in tweet.entities.get('mentions', [])]
                    urls = [url['expanded_url'] for url in tweet.entities.get('urls', [])]
                
                # Determine content type
                content_type = 'text'
                file_url = None
                
                if tweet.attachments and 'media_keys' in tweet.attachments:
                    content_type = 'media'
                    # Would need to fetch media details for actual URLs
                
                result = CrawlResult(
                    platform="twitter",
                    url=tweet.url,
                    title=tweet.text[:100] + "..." if len(tweet.text) > 100 else tweet.text,
                    description=tweet.text,
                    content_type=content_type,
                    file_url=file_url,
                    metadata={
                        'tweet_id': tweet.tweet_id,
                        'author_id': tweet.author_id,
                        'author_username': tweet.author_username,
                        'author_name': tweet.author_name,
                        'created_at': tweet.created_at.isoformat(),
                        'public_metrics': tweet.public_metrics,
                        'hashtags': hashtags,
                        'mentions': mentions,
                        'urls': urls,
                        'lang': tweet.lang,
                        'possibly_sensitive': tweet.possibly_sensitive,
                        'conversation_id': tweet.conversation_id,
                        'in_reply_to_user_id': tweet.in_reply_to_user_id,
                        'context_annotations': tweet.context_annotations,
                        'source': tweet.source,
                        **(tweet.metadata or {})
                    },
                    discovered_at=datetime.utcnow(),
                    fingerprint_candidates=[
                        tweet.url,
                        tweet.text,
                        ' '.join(hashtags),
                        tweet.author_username
                    ]
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error converting tweet to result: {e}")
                continue
        
        return results
    
    async def search_hashtag(self, hashtag: str, max_results: int = 50) -> List[CrawlResult]:
        """Search for tweets by hashtag."""        if not hashtag.startswith('#'):
            hashtag = f"#{hashtag}"
        
        return await self.search_content(
            query=hashtag,
            max_results=max_results,
            filters={'exclude_retweets': True}
        )
    
    async def search_user_tweets(self, username: str, max_results: int = 50) -> List[CrawlResult]:
        """Search for tweets from a specific user."""        if not self.api_client:
            return []
        
        try:
            # Get user info first
            user_info = await self.api_client.get_user_by_username(username)
            if not user_info:
                logger.error(f"User {username} not found")
                return []
            
            # Get user tweets
            tweets = await self.api_client.get_user_tweets(user_info.user_id, max_results)
            
            # Convert to results
            results = await self._convert_tweets_to_results(tweets)
            
            logger.info(f"Found {len(results)} tweets from user {username}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching user tweets: {e}")
            return []
    
    async def monitor_keywords(
        self,
        keywords: List[str],
        callback_func: callable = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Monitor keywords for new tweets."""        try:
            query = ' OR '.join(keywords)
            monitoring_key = f"keywords_{hash(query)}"
            
            if monitoring_key in self.monitoring_tasks:
                logger.warning(f"Already monitoring keywords: {keywords}")
                return False
            
            # Create monitoring task
            task = asyncio.create_task(
                self._continuous_keyword_monitor(query, callback_func, filters)
            )
            self.monitoring_tasks[monitoring_key] = task
            
            logger.info(f"Started monitoring keywords: {keywords}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting keyword monitoring: {e}")
            return False
    
    async def _continuous_keyword_monitor(
        self,
        query: str,
        callback_func: callable,
        filters: Optional[Dict[str, Any]] = None
    ):
        """Continuous keyword monitoring loop."""        logger.info(f"Starting continuous monitoring for query: {query}")
        
        last_tweet_id = None
        
        try:
            while True:
                try:
                    # Add since_id filter to get only new tweets
                    search_filters = filters.copy() if filters else {}
                    if last_tweet_id:
                        search_filters['since_id'] = last_tweet_id
                    
                    results = await self.search_content(
                        query=query,
                        max_results=100,
                        filters=search_filters
                    )
                    
                    if results:
                        # Update last tweet ID
                        last_tweet_id = max(
                            int(result.metadata['tweet_id']) for result in results
                        )
                        
                        if callback_func:
                            await callback_func(results)
                    
                except Exception as e:
                    logger.error(f"Error in keyword monitoring: {e}")
                
                # Wait before next check (15 minutes to respect rate limits)
                await asyncio.sleep(15 * 60)
                
        except asyncio.CancelledError:
            logger.info(f"Keyword monitoring cancelled for query: {query}")
        except Exception as e:
            logger.error(f"Keyword monitoring error: {e}")
    
    async def get_trending_topics(self, location_woeid: int = 1) -> List[Dict[str, Any]]:
        """Get trending topics for a location."""        if not self.api_client:
            return []
        
        try:
            trends = await self.api_client.get_trending_topics(location_woeid)
            return trends
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []
    
    async def search_spaces(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for Twitter Spaces."""        if not self.api_client:
            return []
        
        try:
            spaces = await self.api_client.search_spaces(query, max_results)
            
            # Convert to dictionary format
            return [asdict(space) for space in spaces]
            
        except Exception as e:
            logger.error(f"Error searching spaces: {e}")
            return []
    
    async def check_rate_limits(self) -> bool:
        """Check if crawler is within rate limits."""        # Twitter API v2 has generous rate limits with automatic waiting
        return True
    
    async def get_crawler_stats(self) -> Dict[str, Any]:
        """Get crawler statistics."""        return {
            "platform": "twitter",
            "api_available": self.api_client is not None,
            "active_monitoring": len(self.monitoring_tasks),
            "max_results_per_search": self.max_results_per_search
        }
    
    def cleanup(self):
        """Cleanup crawler resources."""        # Cancel monitoring tasks
        for task in self.monitoring_tasks.values():
            task.cancel()
        self.monitoring_tasks.clear()
        
        logger.info("Twitter crawler cleanup completed")

# Export main classes
__all__ = [
    'TwitterCrawler',
    'TwitterAPIClient',
    'TwitterTweetInfo',
    'TwitterUserInfo',
    'TwitterSpaceInfo'
]
