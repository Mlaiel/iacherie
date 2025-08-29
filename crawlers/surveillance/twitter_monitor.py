"""
Twitter Monitor - Surveillance Twitter/X
========================================

⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED

© 2024 IA Influencer Agent Development Team. All rights reserved.
This software is proprietary and confidential. Unauthorized reproduction,
distribution, or reverse engineering is strictly prohibited by law.

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

Advanced Twitter/X monitoring system for real-time surveillance and content analysis.
Provides comprehensive monitoring of tweets, users, trends, and engagement patterns.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class Tweet:
    """Twitter/X tweet data."""
    tweet_id: str
    user_id: str
    username: str
    display_name: str
    text: str
    created_at: datetime
    lang: str = "en"
    source: str = ""
    reply_to_tweet_id: Optional[str] = None
    reply_to_user_id: Optional[str] = None
    quoted_tweet_id: Optional[str] = None
    retweeted_tweet_id: Optional[str] = None
    retweet_count: int = 0
    like_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    media_urls: List[str] = field(default_factory=list)
    media_types: List[str] = field(default_factory=list)
    possibly_sensitive: bool = False
    verified: bool = False
    location: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class TwitterUser:
    """Twitter/X user data."""
    user_id: str
    username: str
    display_name: str
    bio: str = ""
    location: Optional[str] = None
    website: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    tweet_count: int = 0
    listed_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    verified: bool = False
    protected: bool = False
    profile_image_url: str = ""
    profile_banner_url: str = ""
    pinned_tweet_id: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class TwitterTrend:
    """Twitter/X trending topic data."""
    trend_name: str
    trend_rank: int
    tweet_volume: Optional[int] = None
    location: str = "worldwide"
    url: str = ""
    promoted_content: bool = False
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class TwitterSpace:
    """Twitter/X Spaces data."""
    space_id: str
    title: str
    description: str = ""
    host_id: str = ""
    host_username: str = ""
    state: str = "live"  # live, ended, scheduled
    participant_count: int = 0
    speaker_count: int = 0
    listener_count: int = 0
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None
    topic_ids: List[str] = field(default_factory=list)
    is_ticketed: bool = False
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class TwitterViolation:
    """Twitter/X content violation detection result."""
    violation_id: str
    content_type: str  # tweet, user, space, trend
    content_id: str
    user_id: str
    username: str
    violation_type: str
    confidence_score: float
    detected_at: datetime
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"  # low, medium, high, critical
    reported: bool = False


@dataclass
class TwitterMonitoringMetrics:
    """Twitter monitoring system metrics."""
    tweets_monitored: int = 0
    users_monitored: int = 0
    trends_monitored: int = 0
    spaces_monitored: int = 0
    violations_detected: int = 0
    api_calls_made: int = 0
    rate_limit_hits: int = 0
    monitoring_duration_seconds: float = 0.0
    last_monitoring_cycle: datetime = field(default_factory=datetime.now)


class TwitterMonitor:
    """
    Advanced Twitter/X monitoring and surveillance system.
    
    Features:
    - Real-time tweet monitoring and analysis
    - User behavior tracking and profiling
    - Trend analysis and tracking
    - Twitter Spaces monitoring
    - Advanced violation detection
    - Sentiment analysis integration
    - Network analysis capabilities
    - Rate limit management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Twitter monitor."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configuration
        self.config = config or {}
        self.bearer_token = self.config.get('twitter_bearer_token', '')
        self.api_key = self.config.get('twitter_api_key', '')
        self.api_secret = self.config.get('twitter_api_secret', '')
        self.access_token = self.config.get('twitter_access_token', '')
        self.access_token_secret = self.config.get('twitter_access_token_secret', '')
        self.max_concurrent_requests = self.config.get('max_concurrent_requests', 5)
        self.monitoring_interval_seconds = self.config.get('monitoring_interval_seconds', 60)
        
        # Monitor state
        self.metrics = TwitterMonitoringMetrics()
        self.violations: List[TwitterViolation] = []
        self._monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Content storage
        self.tweets: Dict[str, Tweet] = {}
        self.users: Dict[str, TwitterUser] = {}
        self.trends: Dict[str, TwitterTrend] = {}
        self.spaces: Dict[str, TwitterSpace] = {}
        
        # Monitoring targets
        self.monitored_keywords: Set[str] = set()
        self.monitored_hashtags: Set[str] = set()
        self.monitored_users: Set[str] = set()
        self.monitored_locations: Set[str] = set()
        
        # Violation detection patterns
        self.violation_patterns = {
            'copyright': [
                r'(?i)(pirated|stolen|leaked|unauthorized|copyright\s+violation)',
                r'(?i)(download\s+free|torrent|bootleg|cracked\s+version)',
                r'(?i)(replica|fake|counterfeit|knockoff|imitation)'
            ],
            'spam': [
                r'(?i)(follow\s+for\s+follow|f4f|followback|follow\s+me)',
                r'(?i)(like\s+for\s+like|l4l|rt\s+for\s+rt|retweet)',
                r'(?i)(buy\s+followers|increase\s+followers|get\s+followers)'
            ],
            'misinformation': [
                r'(?i)(fake\s+news|conspiracy|hoax|false\s+flag)',
                r'(?i)(debunked|false\s+information|misleading|propaganda)',
                r'(?i)(unverified|rumor|not\s+confirmed|alleged)'
            ],
            'harassment': [
                r'(?i)(harassment|bullying|trolling|cyberbullying)',
                r'(?i)(kill\s+yourself|kys|die|suicide|harm\s+yourself)',
                r'(?i)(hate\s+speech|racist|sexist|homophobic)'
            ],
            'violence': [
                r'(?i)(violence|violent|harm|dangerous|weapon)',
                r'(?i)(kill|murder|assault|attack|threat|bomb)',
                r'(?i)(terrorism|extremist|radical|militia)'
            ],
            'adult_content': [
                r'(?i)(nsfw|adult\s+content|18\+|explicit)',
                r'(?i)(porn|sexual|nude|naked|xxx)',
                r'(?i)(onlyfans|adult\s+site|premium\s+content)'
            ]
        }
        
        # Rate limiting
        self._last_request_time = 0.0
        self._request_delay = 1.0
        self._rate_limit_remaining = 300  # Twitter API rate limit
        self._rate_limit_reset_time = datetime.now()
        
        self._logger.info("Twitter Monitor initialized")
    
    async def initialize(self) -> None:
        """Initialize the Twitter monitor."""
        try:
            self._logger.info("Initializing Twitter monitor...")
            
            # Validate configuration
            if not self.bearer_token and not (self.api_key and self.api_secret):
                self._logger.warning("No Twitter API credentials configured - limited functionality")
            
            # Initialize Twitter API client
            await self._initialize_twitter_client()
            
            # Setup violation detection
            await self._setup_violation_detection()
            
            self._logger.info("Twitter monitor initialization complete")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize Twitter monitor: {e}")
            raise
    
    async def _initialize_twitter_client(self) -> None:
        """Initialize Twitter API client."""
        try:
            # This would initialize the actual Twitter API client
            # For now, implement placeholder
            self._logger.debug("Twitter API client initialized")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize Twitter API client: {e}")
            raise
    
    async def _setup_violation_detection(self) -> None:
        """Setup violation detection systems."""
        try:
            # This would setup actual ML models for violation detection
            # For now, implement placeholder
            self._logger.debug("Violation detection setup complete")
            
        except Exception as e:
            self._logger.error(f"Failed to setup violation detection: {e}")
            raise
    
    async def start_monitoring(self) -> None:
        """Start Twitter monitoring operations."""
        try:
            if self._monitoring_active:
                self._logger.warning("Twitter monitoring is already active")
                return
            
            self._logger.info("Starting Twitter monitoring...")
            
            self._monitoring_active = True
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            self._logger.info("Twitter monitoring started successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to start Twitter monitoring: {e}")
            self._monitoring_active = False
            raise
    
    async def stop_monitoring(self) -> None:
        """Stop Twitter monitoring operations."""
        try:
            if not self._monitoring_active:
                self._logger.warning("Twitter monitoring is not active")
                return
            
            self._logger.info("Stopping Twitter monitoring...")
            
            self._monitoring_active = False
            
            if self._monitoring_task and not self._monitoring_task.done():
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
            
            self._logger.info("Twitter monitoring stopped successfully")
            
        except Exception as e:
            self._logger.error(f"Error stopping Twitter monitoring: {e}")
            raise
    
    async def add_keyword_monitoring(self, keyword: str) -> bool:
        """Add keyword to monitoring."""
        try:
            self.monitored_keywords.add(keyword)
            self._logger.info(f"Added keyword monitoring: {keyword}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to add keyword monitoring for {keyword}: {e}")
            return False
    
    async def add_hashtag_monitoring(self, hashtag: str) -> bool:
        """Add hashtag to monitoring."""
        try:
            # Remove # if present
            hashtag = hashtag.lstrip('#')
            self.monitored_hashtags.add(hashtag)
            self._logger.info(f"Added hashtag monitoring: #{hashtag}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to add hashtag monitoring for #{hashtag}: {e}")
            return False
    
    async def add_user_monitoring(self, username: str) -> bool:
        """Add user to monitoring."""
        try:
            # Remove @ if present
            username = username.lstrip('@')
            self.monitored_users.add(username)
            self._logger.info(f"Added user monitoring: @{username}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to add user monitoring for @{username}: {e}")
            return False
    
    async def monitor_trending_topics(self, location: str = "1") -> List[TwitterTrend]:
        """Monitor trending topics for a location."""
        try:
            self._logger.debug(f"Monitoring trending topics for location: {location}")
            
            # Rate limiting
            await self._enforce_rate_limit()
            
            # Fetch trending topics
            trends = await self._fetch_trending_topics(location)
            
            # Store trends
            for trend in trends:
                self.trends[f"{trend.trend_name}_{location}"] = trend
            
            self.metrics.trends_monitored += len(trends)
            
            # Analyze trends for violations
            for trend in trends:
                violations = await self._analyze_trend_for_violations(trend)
                
                for violation in violations:
                    self.violations.append(violation)
                    self.metrics.violations_detected += 1
            
            return trends
            
        except Exception as e:
            self._logger.error(f"Error monitoring trending topics: {e}")
            return []
    
    async def monitor_user_timeline(self, username: str, max_tweets: int = 100) -> List[Tweet]:
        """Monitor user timeline."""
        try:
            self._logger.debug(f"Monitoring timeline for user: @{username}")
            
            # Rate limiting
            await self._enforce_rate_limit()
            
            # Fetch user timeline
            tweets = await self._fetch_user_timeline(username, max_tweets)
            
            # Store tweets and analyze
            for tweet in tweets:
                self.tweets[tweet.tweet_id] = tweet
                
                # Analyze tweet for violations
                violations = await self._analyze_tweet_for_violations(tweet)
                
                for violation in violations:
                    self.violations.append(violation)
                    self.metrics.violations_detected += 1
            
            self.metrics.tweets_monitored += len(tweets)
            
            return tweets
            
        except Exception as e:
            self._logger.error(f"Error monitoring user timeline for @{username}: {e}")
            return []
    
    async def search_tweets(
        self,
        query: str,
        max_tweets: int = 100,
        result_type: str = "recent"
    ) -> List[Tweet]:
        """Search for tweets."""
        try:
            self._logger.debug(f"Searching tweets: {query}")
            
            # Rate limiting
            await self._enforce_rate_limit()
            
            # Search tweets
            tweets = await self._fetch_tweet_search(query, max_tweets, result_type)
            
            # Store tweets and analyze
            for tweet in tweets:
                self.tweets[tweet.tweet_id] = tweet
                
                # Analyze tweet for violations
                violations = await self._analyze_tweet_for_violations(tweet)
                
                for violation in violations:
                    self.violations.append(violation)
                    self.metrics.violations_detected += 1
            
            self.metrics.tweets_monitored += len(tweets)
            
            return tweets
            
        except Exception as e:
            self._logger.error(f"Error searching tweets for '{query}': {e}")
            return []
    
    async def monitor_spaces(self) -> List[TwitterSpace]:
        """Monitor active Twitter Spaces."""
        try:
            self._logger.debug("Monitoring Twitter Spaces")
            
            # Rate limiting
            await self._enforce_rate_limit()
            
            # Fetch active spaces
            spaces = await self._fetch_active_spaces()
            
            # Store spaces and analyze
            for space in spaces:
                self.spaces[space.space_id] = space
                
                # Analyze space for violations
                violations = await self._analyze_space_for_violations(space)
                
                for violation in violations:
                    self.violations.append(violation)
                    self.metrics.violations_detected += 1
            
            self.metrics.spaces_monitored += len(spaces)
            
            return spaces
            
        except Exception as e:
            self._logger.error(f"Error monitoring Twitter Spaces: {e}")
            return []
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        self._logger.info("Twitter monitoring loop started")
        
        try:
            while self._monitoring_active:
                try:
                    monitoring_start_time = datetime.now()
                    
                    # Monitor keywords
                    for keyword in self.monitored_keywords:
                        if not self._monitoring_active:
                            break
                        await self.search_tweets(keyword, max_tweets=50)
                    
                    # Monitor hashtags
                    for hashtag in self.monitored_hashtags:
                        if not self._monitoring_active:
                            break
                        await self.search_tweets(f"#{hashtag}", max_tweets=50)
                    
                    # Monitor users
                    for username in self.monitored_users:
                        if not self._monitoring_active:
                            break
                        await self.monitor_user_timeline(username, max_tweets=20)
                    
                    # Monitor trending topics
                    await self.monitor_trending_topics()
                    
                    # Monitor Twitter Spaces
                    await self.monitor_spaces()
                    
                    # Update metrics
                    monitoring_duration = (datetime.now() - monitoring_start_time).total_seconds()
                    self.metrics.monitoring_duration_seconds += monitoring_duration
                    self.metrics.last_monitoring_cycle = datetime.now()
                    
                    # Wait before next monitoring cycle
                    await asyncio.sleep(self.monitoring_interval_seconds)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self._logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes before retrying
        
        except asyncio.CancelledError:
            pass
        
        self._logger.info("Twitter monitoring loop stopped")
    
    async def _fetch_trending_topics(self, location: str) -> List[TwitterTrend]:
        """Fetch trending topics."""
        try:
            # Simulate Twitter API call
            await asyncio.sleep(0.3)
            
            trends = []
            
            # In real implementation, this would use Twitter API v2
            for i in range(10):  # Simulate 10 trending topics
                trend = TwitterTrend(
                    trend_name=f"TrendingTopic{i}",
                    trend_rank=i + 1,
                    tweet_volume=1000 * (10 - i),
                    location=location,
                    url=f"https://twitter.com/search?q=TrendingTopic{i}"
                )
                trends.append(trend)
            
            self.metrics.api_calls_made += 1
            return trends
            
        except Exception as e:
            self._logger.error(f"Error fetching trending topics: {e}")
            return []
    
    async def _fetch_user_timeline(self, username: str, max_tweets: int) -> List[Tweet]:
        """Fetch user timeline."""
        try:
            # Simulate Twitter API call
            await asyncio.sleep(0.4)
            
            tweets = []
            
            # In real implementation, this would use Twitter API v2
            for i in range(min(max_tweets, 20)):  # Simulate tweets
                tweet = Tweet(
                    tweet_id=f"tweet_{username}_{i}_{datetime.now().timestamp()}",
                    user_id=f"user_{username}",
                    username=username,
                    display_name=username.title(),
                    text=f"Tweet {i} by @{username} about something interesting",
                    created_at=datetime.now() - timedelta(hours=i),
                    retweet_count=10 * (i + 1),
                    like_count=50 * (i + 1),
                    reply_count=5 * (i + 1),
                    quote_count=2 * (i + 1),
                    hashtags=[f"hashtag{i}", "content"],
                    mentions=[f"user{i}"] if i % 2 == 0 else [],
                    urls=[f"https://example.com/{i}"] if i % 3 == 0 else []
                )
                tweets.append(tweet)
            
            self.metrics.api_calls_made += 1
            return tweets
            
        except Exception as e:
            self._logger.error(f"Error fetching timeline for @{username}: {e}")
            return []
    
    async def _fetch_tweet_search(
        self,
        query: str,
        max_tweets: int,
        result_type: str
    ) -> List[Tweet]:
        """Search for tweets."""
        try:
            # Simulate Twitter API call
            await asyncio.sleep(0.5)
            
            tweets = []
            
            # In real implementation, this would use Twitter API v2 search
            for i in range(min(max_tweets, 25)):  # Simulate search results
                tweet = Tweet(
                    tweet_id=f"search_{query}_{i}_{datetime.now().timestamp()}",
                    user_id=f"search_user_{i}",
                    username=f"searchuser{i}",
                    display_name=f"Search User {i}",
                    text=f"Tweet about {query} - result {i}",
                    created_at=datetime.now() - timedelta(minutes=i * 10),
                    retweet_count=5 * (i + 1),
                    like_count=25 * (i + 1),
                    reply_count=3 * (i + 1),
                    quote_count=1 * i,
                    hashtags=[query.replace(' ', '')] if '#' not in query else [],
                    mentions=[]
                )
                tweets.append(tweet)
            
            self.metrics.api_calls_made += 1
            return tweets
            
        except Exception as e:
            self._logger.error(f"Error searching tweets for '{query}': {e}")
            return []
    
    async def _fetch_active_spaces(self) -> List[TwitterSpace]:
        """Fetch active Twitter Spaces."""
        try:
            # Simulate Twitter API call
            await asyncio.sleep(0.3)
            
            spaces = []
            
            # In real implementation, this would use Twitter API v2 Spaces endpoints
            for i in range(5):  # Simulate 5 active spaces
                space = TwitterSpace(
                    space_id=f"space_{i}_{datetime.now().timestamp()}",
                    title=f"Space About Topic {i}",
                    description=f"Discussion about topic {i}",
                    host_id=f"host_{i}",
                    host_username=f"host{i}",
                    state="live",
                    participant_count=50 + i * 10,
                    speaker_count=3 + i,
                    listener_count=47 + i * 10,
                    started_at=datetime.now() - timedelta(minutes=i * 15),
                    topic_ids=[f"topic_{i}"]
                )
                spaces.append(space)
            
            self.metrics.api_calls_made += 1
            return spaces
            
        except Exception as e:
            self._logger.error(f"Error fetching active spaces: {e}")
            return []
    
    async def _analyze_tweet_for_violations(self, tweet: Tweet) -> List[TwitterViolation]:
        """Analyze tweet for violations."""
        violations = []
        
        try:
            # Analyze tweet text
            tweet_text = tweet.text.lower()
            
            # Check for violation patterns
            for violation_type, patterns in self.violation_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, tweet_text)
                    
                    if matches:
                        confidence = min(len(matches) * 0.3 + 0.5, 1.0)
                        
                        violation = TwitterViolation(
                            violation_id=f"twitter_tweet_{tweet.tweet_id}_{violation_type}_{datetime.now().timestamp()}",
                            content_type="tweet",
                            content_id=tweet.tweet_id,
                            user_id=tweet.user_id,
                            username=tweet.username,
                            violation_type=f"tweet_{violation_type}",
                            confidence_score=confidence,
                            detected_at=datetime.now(),
                            description=f"Tweet violation detected: {violation_type}",
                            evidence={
                                'pattern_matched': pattern,
                                'matches': matches,
                                'tweet_text_preview': tweet.text[:200],
                                'hashtags': tweet.hashtags,
                                'mentions': tweet.mentions
                            },
                            severity=self._calculate_severity(violation_type, confidence)
                        )
                        violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing tweet for violations: {e}")
        
        return violations
    
    async def _analyze_trend_for_violations(self, trend: TwitterTrend) -> List[TwitterViolation]:
        """Analyze trending topic for violations."""
        violations = []
        
        try:
            # Analyze trend name
            trend_text = trend.trend_name.lower()
            
            # Check for violation patterns
            for violation_type, patterns in self.violation_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, trend_text)
                    
                    if matches:
                        confidence = min(len(matches) * 0.4 + 0.6, 1.0)
                        
                        violation = TwitterViolation(
                            violation_id=f"twitter_trend_{trend.trend_name}_{violation_type}_{datetime.now().timestamp()}",
                            content_type="trend",
                            content_id=trend.trend_name,
                            user_id="",
                            username="",
                            violation_type=f"trend_{violation_type}",
                            confidence_score=confidence,
                            detected_at=datetime.now(),
                            description=f"Trending topic violation detected: {violation_type}",
                            evidence={
                                'pattern_matched': pattern,
                                'matches': matches,
                                'trend_name': trend.trend_name,
                                'trend_rank': trend.trend_rank,
                                'tweet_volume': trend.tweet_volume
                            },
                            severity=self._calculate_severity(violation_type, confidence)
                        )
                        violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing trend for violations: {e}")
        
        return violations
    
    async def _analyze_space_for_violations(self, space: TwitterSpace) -> List[TwitterViolation]:
        """Analyze Twitter Space for violations."""
        violations = []
        
        try:
            # Analyze space content
            space_text = f"{space.title} {space.description}".lower()
            
            # Check for violation patterns
            for violation_type, patterns in self.violation_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, space_text)
                    
                    if matches:
                        confidence = min(len(matches) * 0.3 + 0.5, 1.0)
                        
                        violation = TwitterViolation(
                            violation_id=f"twitter_space_{space.space_id}_{violation_type}_{datetime.now().timestamp()}",
                            content_type="space",
                            content_id=space.space_id,
                            user_id=space.host_id,
                            username=space.host_username,
                            violation_type=f"space_{violation_type}",
                            confidence_score=confidence,
                            detected_at=datetime.now(),
                            description=f"Twitter Space violation detected: {violation_type}",
                            evidence={
                                'pattern_matched': pattern,
                                'matches': matches,
                                'space_title': space.title,
                                'host_username': space.host_username,
                                'participant_count': space.participant_count
                            },
                            severity=self._calculate_severity(violation_type, confidence)
                        )
                        violations.append(violation)
            
        except Exception as e:
            self._logger.error(f"Error analyzing space for violations: {e}")
        
        return violations
    
    def _calculate_severity(self, violation_type: str, confidence: float) -> str:
        """Calculate violation severity."""
        high_risk_types = ['violence', 'harassment', 'misinformation']
        
        if violation_type in high_risk_types:
            if confidence >= 0.8:
                return "critical"
            elif confidence >= 0.6:
                return "high"
            else:
                return "medium"
        else:
            if confidence >= 0.9:
                return "high"
            elif confidence >= 0.7:
                return "medium"
            else:
                return "low"
    
    async def _enforce_rate_limit(self) -> None:
        """Enforce Twitter API rate limiting."""
        current_time = asyncio.get_event_loop().time()
        time_since_last_request = current_time - self._last_request_time
        
        # Check if we need to wait for rate limit reset
        if self._rate_limit_remaining <= 0:
            if datetime.now() < self._rate_limit_reset_time:
                wait_time = (self._rate_limit_reset_time - datetime.now()).total_seconds()
                self._logger.warning(f"Rate limit exceeded, waiting {wait_time:.1f} seconds")
                await asyncio.sleep(wait_time)
                self._rate_limit_remaining = 300  # Reset limit
                self.metrics.rate_limit_hits += 1
        
        # Standard rate limiting
        if time_since_last_request < self._request_delay:
            sleep_time = self._request_delay - time_since_last_request
            await asyncio.sleep(sleep_time)
        
        self._last_request_time = asyncio.get_event_loop().time()
        self._rate_limit_remaining = max(0, self._rate_limit_remaining - 1)
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            'monitoring_active': self._monitoring_active,
            'monitored_targets': {
                'keywords': len(self.monitored_keywords),
                'hashtags': len(self.monitored_hashtags),
                'users': len(self.monitored_users),
                'locations': len(self.monitored_locations)
            },
            'content_counts': {
                'tweets': len(self.tweets),
                'users': len(self.users),
                'trends': len(self.trends),
                'spaces': len(self.spaces)
            },
            'violations_detected': len(self.violations),
            'metrics': {
                'tweets_monitored': self.metrics.tweets_monitored,
                'users_monitored': self.metrics.users_monitored,
                'trends_monitored': self.metrics.trends_monitored,
                'spaces_monitored': self.metrics.spaces_monitored,
                'violations_detected': self.metrics.violations_detected,
                'api_calls_made': self.metrics.api_calls_made,
                'rate_limit_hits': self.metrics.rate_limit_hits,
                'monitoring_duration_seconds': self.metrics.monitoring_duration_seconds,
                'last_monitoring_cycle': self.metrics.last_monitoring_cycle.isoformat()
            },
            'rate_limit_status': {
                'remaining': self._rate_limit_remaining,
                'reset_time': self._rate_limit_reset_time.isoformat()
            }
        }
    
    def get_recent_violations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent violations."""
        recent_violations = sorted(
            self.violations,
            key=lambda v: v.detected_at,
            reverse=True
        )[:limit]
        
        return [
            {
                'violation_id': v.violation_id,
                'content_type': v.content_type,
                'content_id': v.content_id,
                'user_id': v.user_id,
                'username': v.username,
                'violation_type': v.violation_type,
                'confidence_score': v.confidence_score,
                'detected_at': v.detected_at.isoformat(),
                'description': v.description,
                'evidence': v.evidence,
                'severity': v.severity,
                'reported': v.reported
            }
            for v in recent_violations
        ]
    
    async def shutdown(self) -> None:
        """Shutdown the Twitter monitor."""
        try:
            self._logger.info("Shutting down Twitter monitor...")
            
            await self.stop_monitoring()
            
            # Clear data
            self.tweets.clear()
            self.users.clear()
            self.trends.clear()
            self.spaces.clear()
            self.violations.clear()
            
            self._logger.info("Twitter monitor shutdown complete")
            
        except Exception as e:
            self._logger.error(f"Error during Twitter monitor shutdown: {e}")
            raise


# Export main class
__all__ = [
    'TwitterMonitor', 'Tweet', 'TwitterUser', 'TwitterTrend', 'TwitterSpace',
    'TwitterViolation', 'TwitterMonitoringMetrics'
]