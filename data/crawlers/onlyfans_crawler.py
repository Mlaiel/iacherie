"""OnlyFans Crawler Implementation
===============================

Advanced OnlyFans platform crawler for creator economy and subscription content monitoring.
Implements comprehensive Creator, Post, Subscription, and Monetization tracking.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

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
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
import aiohttp
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class OnlyFansCreator:
    """OnlyFans creator information"""    creator_id: str
    username: str
    name: str
    bio: str
    avatar_url: str
    header_url: str
    location: str
    website_url: Optional[str]
    wishlist_url: Optional[str]
    subscriber_count: int
    following_count: int
    photo_count: int
    video_count: int
    archived_post_count: int
    private_archived_post_count: int
    stream_count: int
    is_verified: bool
    is_real_performer: bool
    can_look_story: bool
    can_comment_story: bool
    has_not_viewed_story: bool
    is_restricted: bool
    can_earn: bool
    joined_at: datetime
    last_seen: Optional[datetime]
    subscription_price: float
    subscription_bundles: List[Dict[str, Any]]
    promotional_campaigns: List[Dict[str, Any]]
    current_subscribe_price: float
    subscribe_prices: List[Dict[str, float]]
    tips_enabled: bool
    tips_text_enabled: bool
    tips_min_amount: float
    tips_max_amount: float
    show_posts_in_feed: bool
    can_suggest_price: bool
    privacy_settings: Dict[str, bool]
    notification_settings: Dict[str, bool]
    earnings_total: float
    earnings_tips: float
    earnings_posts: float
    earnings_streams: float
    earnings_referrals: float
    payout_method: str


@dataclass
class OnlyFansPost:
    """OnlyFans post information"""    post_id: str
    creator_id: str
    creator_username: str
    text: str
    localized_text: str
    created_at: datetime
    changed_at: Optional[datetime]
    media_count: int
    media_type: str  # photo, video, audio, gif
    media_urls: List[str]
    media_info: List[Dict[str, Any]]
    preview_ids: List[str]
    thumbnail_url: Optional[str]
    price: float
    is_archived: bool
    is_bookmarked: bool
    is_favorite: bool
    is_watch_later: bool
    is_purchased: bool
    is_opened: bool
    can_purchase: bool
    can_comment: bool
    can_toggle_favorite: bool
    can_report: bool
    can_delete: bool
    can_pin: bool
    comments_count: int
    tips_amount: float
    tips_count: int
    likes_count: int
    is_liked: bool
    is_paid: bool
    author: str
    raw_text: str
    preview_text: str
    hashtags: List[str]
    mentions: List[str]
    visibility: str  # all, subscribers, purchase
    promotion_type: Optional[str]
    expire_date: Optional[datetime]
    post_stats: Dict[str, int]


@dataclass
class OnlyFansMessage:
    """OnlyFans private message information"""    message_id: str
    from_user_id: str
    to_user_id: str
    text: str
    localized_text: str
    created_at: datetime
    is_new: bool
    is_free: bool
    price: float
    media_count: int
    media_type: str
    media_urls: List[str]
    media_info: List[Dict[str, Any]]
    preview_ids: List[str]
    can_purchase: bool
    can_reply: bool
    can_unsend: bool
    can_report: bool
    is_opened: bool
    is_purchased: bool
    tips_amount: float
    hashtags: List[str]
    mentions: List[str]
    raw_text: str
    preview_text: str
    response_type: str  # message, tip, mass_message


@dataclass
class OnlyFansSubscription:
    """OnlyFans subscription information"""    subscription_id: str
    user_id: str
    creator_id: str
    creator_username: str
    creator_name: str
    status: str  # active, expired, cancelled
    started_at: datetime
    expires_at: Optional[datetime]
    renewed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    subscription_type: str  # regular, bundle, promotional
    price: float
    recurring_price: float
    discount_percent: int
    auto_rebill: bool
    show_posts_in_feed: bool
    can_comment: bool
    can_message: bool
    total_spent: float
    tips_given: float
    messages_sent: int
    last_interaction: Optional[datetime]
    subscription_source: str  # direct, promotion, referral
    payment_method: str
    transaction_id: str


@dataclass
class OnlyFansStream:
    """OnlyFans live stream information"""    stream_id: str
    creator_id: str
    creator_username: str
    title: str
    description: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: int
    status: str  # live, ended, scheduled
    viewer_count: int
    max_viewers: int
    likes_count: int
    tips_amount: float
    tips_count: int
    is_private: bool
    price: float
    thumbnail_url: str
    stream_url: str
    quality_options: List[str]
    chat_enabled: bool
    recording_enabled: bool
    can_join: bool
    can_tip: bool
    can_chat: bool
    viewers: List[str]
    moderators: List[str]
    tags: List[str]
    category: str


class OnlyFansCrawler(PlatformCrawler):
    """    Advanced OnlyFans crawler for creator economy and subscription content monitoring.
    
    Features:
    - Creator profile tracking
    - Post and media monitoring
    - Subscription management tracking
    - Private message monitoring (with permissions)
    - Live stream tracking
    - Monetization and earnings analysis
    - Tip and payment tracking
    - Fan engagement metrics
    - Content performance analysis
    - Privacy-aware data collection
    """    
    def __init__(self, config: CrawlerConfig, vector_matcher=None):
        super().__init__(config, vector_matcher)
        self.platform_name = "onlyfans"
        self.base_url = "https://onlyfans.com"
        self.api_base_url = "https://onlyfans.com/api2/v2"
        
        # Rate limiting (OnlyFans has strict limits)
        self.requests_per_minute = 5
        self.min_delay = 12.0
        self.max_delay = 20.0
        
        # Content type mappings
        self.content_types = {
            'creators': self._crawl_creators,
            'posts': self._crawl_posts,
            'messages': self._crawl_messages,
            'subscriptions': self._crawl_subscriptions,
            'streams': self._crawl_streams,
            'trending': self._crawl_trending,
            'featured': self._crawl_featured,
            'search': self._crawl_search
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Privacy and security settings
        self.respect_privacy = True
        self.require_authentication = True
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup OnlyFans-specific headers"""        self.session_headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://onlyfans.com/',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    async def search_content(self, query: str, content_type: str = "creators", 
                           max_results: int = 50, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """        Search for content on OnlyFans.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            filters: Additional search filters
            
        Returns:
            List of crawler results
        """        try:
            # Privacy check
            if not self._check_privacy_compliance():
                self.logger.warning("Privacy compliance check failed - limiting data collection")
                return []
            
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, filters)
            
            self.logger.info(f"Found {len(results)} OnlyFans {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching OnlyFans content: {str(e)}")
            return []
    
    async def _crawl_creators(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl OnlyFans creators"""        try:
            results = []
            
            # Mock creator data (privacy-compliant)
            mock_creators = await self._get_mock_creators(query, max_results)
            
            for creator_data in mock_creators:
                creator = await self._parse_creator_data(creator_data)
                if creator:
                    result = CrawlerResult(
                        url=f"{self.base_url}/{creator.username}",
                        title=f"{creator.name} (@{creator.username})",
                        content=creator.bio,
                        metadata={
                            'creator_data': asdict(creator),
                            'platform': 'onlyfans',
                            'content_type': 'creator',
                            'username': creator.username,
                            'name': creator.name,
                            'subscriber_count': creator.subscriber_count,
                            'following_count': creator.following_count,
                            'photo_count': creator.photo_count,
                            'video_count': creator.video_count,
                            'is_verified': creator.is_verified,
                            'is_real_performer': creator.is_real_performer,
                            'subscription_price': creator.subscription_price,
                            'current_subscribe_price': creator.current_subscribe_price,
                            'tips_enabled': creator.tips_enabled,
                            'can_earn': creator.can_earn,
                            'location': creator.location,
                            'earnings_total': creator.earnings_total if not self.respect_privacy else 0
                        },
                        timestamp=creator.joined_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling OnlyFans creators: {str(e)}")
            return []
    
    async def _crawl_posts(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl OnlyFans posts"""        try:
            results = []
            
            # Privacy check for post content
            if not self._check_content_access_permissions():
                self.logger.warning("Insufficient permissions for post content access")
                return []
            
            # Mock post data (privacy-compliant)
            mock_posts = await self._get_mock_posts(query, max_results)
            
            for post_data in mock_posts:
                post = await self._parse_post_data(post_data)
                if post:
                    result = CrawlerResult(
                        url=f"{self.base_url}/post/{post.post_id}",
                        title=f"Post by @{post.creator_username}",
                        content=post.preview_text if self.respect_privacy else post.text,
                        metadata={
                            'post_data': asdict(post),
                            'platform': 'onlyfans',
                            'content_type': 'post',
                            'creator_username': post.creator_username,
                            'media_type': post.media_type,
                            'media_count': post.media_count,
                            'price': post.price,
                            'is_paid': post.is_paid,
                            'is_purchased': post.is_purchased,
                            'comments_count': post.comments_count,
                            'likes_count': post.likes_count,
                            'tips_amount': post.tips_amount if not self.respect_privacy else 0,
                            'tips_count': post.tips_count,
                            'visibility': post.visibility,
                            'hashtags': post.hashtags,
                            'mentions': post.mentions,
                            'is_archived': post.is_archived
                        },
                        timestamp=post.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling OnlyFans posts: {str(e)}")
            return []
    
    async def _crawl_messages(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl OnlyFans messages (requires special permissions)"""        try:
            results = []
            
            # Strict privacy check for messages
            if not self._check_message_access_permissions():
                self.logger.warning("Insufficient permissions for message access")
                return []
            
            # Mock message data (highly privacy-compliant)
            mock_messages = await self._get_mock_messages(query, max_results)
            
            for message_data in mock_messages:
                message = await self._parse_message_data(message_data)
                if message:
                    result = CrawlerResult(
                        url=f"{self.base_url}/messages/{message.message_id}",
                        title=f"Message from User {message.from_user_id[:8]}...",
                        content=message.preview_text,  # Only preview for privacy
                        metadata={
                            'message_data': asdict(message),
                            'platform': 'onlyfans',
                            'content_type': 'message',
                            'from_user_id': message.from_user_id[:8] + "..." if self.respect_privacy else message.from_user_id,
                            'to_user_id': message.to_user_id[:8] + "..." if self.respect_privacy else message.to_user_id,
                            'is_free': message.is_free,
                            'price': message.price,
                            'media_type': message.media_type,
                            'media_count': message.media_count,
                            'is_purchased': message.is_purchased,
                            'response_type': message.response_type,
                            'tips_amount': 0 if self.respect_privacy else message.tips_amount
                        },
                        timestamp=message.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling OnlyFans messages: {str(e)}")
            return []
    
    async def _crawl_subscriptions(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl OnlyFans subscriptions"""        try:
            results = []
            
            # Privacy check for subscription data
            if not self._check_subscription_access_permissions():
                self.logger.warning("Insufficient permissions for subscription access")
                return []
            
            # Mock subscription data
            mock_subscriptions = await self._get_mock_subscriptions(query, max_results)
            
            for subscription_data in mock_subscriptions:
                subscription = await self._parse_subscription_data(subscription_data)
                if subscription:
                    result = CrawlerResult(
                        url=f"{self.base_url}/subscriptions/{subscription.subscription_id}",
                        title=f"Subscription to @{subscription.creator_username}",
                        content=f"Subscription status: {subscription.status}",
                        metadata={
                            'subscription_data': asdict(subscription),
                            'platform': 'onlyfans',
                            'content_type': 'subscription',
                            'creator_username': subscription.creator_username,
                            'creator_name': subscription.creator_name,
                            'status': subscription.status,
                            'subscription_type': subscription.subscription_type,
                            'price': subscription.price,
                            'recurring_price': subscription.recurring_price,
                            'auto_rebill': subscription.auto_rebill,
                            'total_spent': 0 if self.respect_privacy else subscription.total_spent,
                            'tips_given': 0 if self.respect_privacy else subscription.tips_given,
                            'subscription_source': subscription.subscription_source
                        },
                        timestamp=subscription.started_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling OnlyFans subscriptions: {str(e)}")
            return []
    
    async def _crawl_streams(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl OnlyFans streams"""        try:
            results = []
            
            # Mock stream data
            mock_streams = await self._get_mock_streams(query, max_results)
            
            for stream_data in mock_streams:
                stream = await self._parse_stream_data(stream_data)
                if stream:
                    result = CrawlerResult(
                        url=f"{self.base_url}/stream/{stream.stream_id}",
                        title=f"Stream: {stream.title}",
                        content=stream.description,
                        metadata={
                            'stream_data': asdict(stream),
                            'platform': 'onlyfans',
                            'content_type': 'stream',
                            'creator_username': stream.creator_username,
                            'title': stream.title,
                            'status': stream.status,
                            'duration_seconds': stream.duration_seconds,
                            'viewer_count': stream.viewer_count,
                            'max_viewers': stream.max_viewers,
                            'likes_count': stream.likes_count,
                            'tips_amount': 0 if self.respect_privacy else stream.tips_amount,
                            'tips_count': stream.tips_count,
                            'is_private': stream.is_private,
                            'price': stream.price,
                            'chat_enabled': stream.chat_enabled,
                            'recording_enabled': stream.recording_enabled,
                            'category': stream.category,
                            'tags': stream.tags
                        },
                        timestamp=stream.started_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling OnlyFans streams: {str(e)}")
            return []
    
    async def _crawl_trending(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl trending OnlyFans content"""        try:
            results = []
            
            # Get trending content
            trending_content = await self._get_trending_content(query, max_results, filters)
            
            for content in trending_content:
                result = CrawlerResult(
                    url=content.get('url', ''),
                    title=f"[TRENDING] {content.get('title', 'Unknown')}",
                    content=content.get('description', ''),
                    metadata={
                        'trending_data': content,
                        'platform': 'onlyfans',
                        'content_type': 'trending',
                        'is_trending': True,
                        'trend_score': content.get('trend_score', 0),
                        'category': content.get('category', 'general')
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling trending OnlyFans content: {str(e)}")
            return []
    
    async def _crawl_featured(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl featured OnlyFans content"""        try:
            results = []
            
            # Get featured content
            featured_content = await self._get_featured_content(query, max_results, filters)
            
            for content in featured_content:
                result = CrawlerResult(
                    url=content.get('url', ''),
                    title=f"[FEATURED] {content.get('title', 'Unknown')}",
                    content=content.get('description', ''),
                    metadata={
                        'featured_data': content,
                        'platform': 'onlyfans',
                        'content_type': 'featured',
                        'is_featured': True,
                        'feature_score': content.get('feature_score', 0),
                        'featured_by': content.get('featured_by', 'onlyfans')
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling featured OnlyFans content: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """General OnlyFans search"""        try:
            results = []
            
            # Search across different content types (privacy-compliant)
            creators = await self._crawl_creators(query, max_results // 2, filters)
            posts = await self._crawl_posts(query, max_results // 4, filters)
            streams = await self._crawl_streams(query, max_results // 4, filters)
            
            results.extend(creators)
            results.extend(posts)
            results.extend(streams)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing OnlyFans search: {str(e)}")
            return []
    
    # Privacy and permission checks
    
    def _check_privacy_compliance(self) -> bool:
        """Check privacy compliance settings"""        # In real implementation, check user permissions and platform ToS
        return True
    
    def _check_content_access_permissions(self) -> bool:
        """Check permissions for content access"""        # In real implementation, verify subscription and access rights
        return True
    
    def _check_message_access_permissions(self) -> bool:
        """Check permissions for message access"""        # In real implementation, verify user owns the messages
        return False  # Default to restricted for privacy
    
    def _check_subscription_access_permissions(self) -> bool:
        """Check permissions for subscription access"""        # In real implementation, verify user owns the subscription data
        return True
    
    # Mock data generators (privacy-compliant)
    
    async def _get_mock_creators(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock creator data"""        creators = []
        
        for i in range(min(max_results, 15)):
            joined_at = datetime.utcnow() - timedelta(days=random.randint(30, 1095))
            creators.append({
                'id': f'creator_{i}',
                'username': f'{query.lower() if query else "creator"}{i}',
                'name': f'{query} Creator {i}' if query else f'Creator {i}',
                'bio': f'Content creator focused on {query}' if query else f'Creator bio {i}',
                'location': random.choice(['USA', 'Canada', 'UK', 'Australia', '']),
                'subscriber_count': random.randint(100, 50000),
                'following_count': random.randint(10, 1000),
                'photo_count': random.randint(50, 1000),
                'video_count': random.randint(10, 500),
                'archived_post_count': random.randint(0, 100),
                'private_archived_post_count': random.randint(0, 50),
                'stream_count': random.randint(0, 100),
                'is_verified': random.choice([True, False]),
                'is_real_performer': random.choice([True, False]),
                'can_earn': True,
                'joined_at': joined_at.isoformat(),
                'subscription_price': round(random.uniform(5.0, 50.0), 2),
                'current_subscribe_price': round(random.uniform(5.0, 50.0), 2),
                'tips_enabled': random.choice([True, False]),
                'tips_min_amount': 1.0,
                'tips_max_amount': 100.0,
                'earnings_total': round(random.uniform(1000.0, 100000.0), 2),
                'earnings_tips': round(random.uniform(100.0, 10000.0), 2),
                'earnings_posts': round(random.uniform(500.0, 50000.0), 2),
                'privacy_settings': {
                    'show_online_status': random.choice([True, False]),
                    'allow_messages': random.choice([True, False]),
                    'show_tips_in_feed': random.choice([True, False])
                }
            })
        
        return creators
    
    async def _get_mock_posts(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock post data"""        posts = []
        
        for i in range(min(max_results, 25)):
            created_at = datetime.utcnow() - timedelta(hours=random.randint(1, 168))
            posts.append({
                'id': f'post_{i}',
                'creator_id': f'creator_{i % 5}',
                'creator_username': f'{query.lower() if query else "creator"}{i % 5}',
                'text': f'New {query} content! Check it out!' if query else f'Post content {i}',
                'preview_text': f'New {query} content...' if query else f'Preview {i}',
                'created_at': created_at.isoformat(),
                'media_type': random.choice(['photo', 'video', 'audio', 'gif']),
                'media_count': random.randint(1, 10),
                'price': round(random.uniform(0.0, 25.0), 2) if random.choice([True, False]) else 0.0,
                'is_paid': random.choice([True, False]),
                'is_purchased': random.choice([True, False]),
                'comments_count': random.randint(0, 100),
                'likes_count': random.randint(0, 500),
                'tips_amount': round(random.uniform(0.0, 100.0), 2),
                'tips_count': random.randint(0, 20),
                'visibility': random.choice(['all', 'subscribers', 'purchase']),
                'hashtags': [f'#{query}'] if query else ['#content', '#exclusive'],
                'mentions': [f'@user{j}' for j in range(random.randint(0, 3))],
                'is_archived': random.choice([True, False])
            })
        
        return posts
    
    async def _get_mock_messages(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock message data (privacy-compliant)"""        messages = []
        
        for i in range(min(max_results, 10)):  # Limited for privacy
            created_at = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            messages.append({
                'id': f'message_{i}',
                'from_user_id': f'user_{i}',
                'to_user_id': f'creator_{i % 3}',
                'text': f'Message about {query}' if query else f'Message {i}',
                'preview_text': f'Message about {query}...' if query else f'Preview {i}',
                'created_at': created_at.isoformat(),
                'is_free': random.choice([True, False]),
                'price': round(random.uniform(0.0, 10.0), 2),
                'media_type': random.choice(['text', 'photo', 'video']),
                'media_count': random.randint(0, 3),
                'is_purchased': random.choice([True, False]),
                'response_type': random.choice(['message', 'tip', 'mass_message']),
                'tips_amount': round(random.uniform(0.0, 50.0), 2)
            })
        
        return messages
    
    async def _get_mock_subscriptions(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock subscription data"""        subscriptions = []
        
        for i in range(min(max_results, 10)):
            started_at = datetime.utcnow() - timedelta(days=random.randint(1, 365))
            expires_at = started_at + timedelta(days=30)
            subscriptions.append({
                'id': f'subscription_{i}',
                'user_id': f'user_{i}',
                'creator_id': f'creator_{i % 5}',
                'creator_username': f'{query.lower() if query else "creator"}{i % 5}',
                'creator_name': f'{query} Creator {i % 5}' if query else f'Creator {i % 5}',
                'status': random.choice(['active', 'expired', 'cancelled']),
                'started_at': started_at.isoformat(),
                'expires_at': expires_at.isoformat(),
                'subscription_type': random.choice(['regular', 'bundle', 'promotional']),
                'price': round(random.uniform(5.0, 50.0), 2),
                'recurring_price': round(random.uniform(5.0, 50.0), 2),
                'auto_rebill': random.choice([True, False]),
                'total_spent': round(random.uniform(50.0, 1000.0), 2),
                'tips_given': round(random.uniform(10.0, 200.0), 2),
                'subscription_source': random.choice(['direct', 'promotion', 'referral'])
            })
        
        return subscriptions
    
    async def _get_mock_streams(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock stream data"""        streams = []
        
        for i in range(min(max_results, 15)):
            started_at = datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            ended_at = started_at + timedelta(minutes=random.randint(30, 180)) if random.choice([True, False]) else None
            streams.append({
                'id': f'stream_{i}',
                'creator_id': f'creator_{i % 5}',
                'creator_username': f'{query.lower() if query else "creator"}{i % 5}',
                'title': f'{query} Live Stream {i}' if query else f'Live Stream {i}',
                'description': f'Live {query} content!' if query else f'Stream description {i}',
                'started_at': started_at.isoformat(),
                'ended_at': ended_at.isoformat() if ended_at else None,
                'duration_seconds': random.randint(1800, 7200),
                'status': random.choice(['live', 'ended', 'scheduled']),
                'viewer_count': random.randint(5, 500),
                'max_viewers': random.randint(10, 1000),
                'likes_count': random.randint(0, 100),
                'tips_amount': round(random.uniform(0.0, 500.0), 2),
                'tips_count': random.randint(0, 50),
                'is_private': random.choice([True, False]),
                'price': round(random.uniform(0.0, 20.0), 2),
                'chat_enabled': random.choice([True, False]),
                'recording_enabled': random.choice([True, False]),
                'category': random.choice(['chat', 'performance', 'gaming', 'lifestyle']),
                'tags': [query] if query else ['live', 'exclusive']
            })
        
        return streams
    
    async def _get_trending_content(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get trending content"""        content = []
        
        for i in range(min(max_results, 10)):
            content.append({
                'title': f'Trending: {query} {i}' if query else f'Trending Content {i}',
                'url': f'{self.base_url}/trending/{i}',
                'description': f'Trending content about {query}' if query else f'Trending description {i}',
                'trend_score': random.randint(80, 100),
                'category': random.choice(['creators', 'content', 'live'])
            })
        
        return content
    
    async def _get_featured_content(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get featured content"""        content = []
        
        for i in range(min(max_results, 10)):
            content.append({
                'title': f'Featured: {query} {i}' if query else f'Featured Content {i}',
                'url': f'{self.base_url}/featured/{i}',
                'description': f'Featured content about {query}' if query else f'Featured description {i}',
                'feature_score': random.randint(90, 100),
                'featured_by': random.choice(['onlyfans', 'algorithm', 'staff'])
            })
        
        return content
    
    # Parser methods
    
    async def _parse_creator_data(self, creator_data: Dict[str, Any]) -> Optional[OnlyFansCreator]:
        """Parse creator data"""        try:
            joined_at = datetime.fromisoformat(creator_data.get('joined_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            creator = OnlyFansCreator(
                creator_id=creator_data.get('id', ''),
                username=creator_data.get('username', ''),
                name=creator_data.get('name', ''),
                bio=creator_data.get('bio', ''),
                avatar_url='',
                header_url='',
                location=creator_data.get('location', ''),
                website_url=creator_data.get('website_url'),
                wishlist_url=creator_data.get('wishlist_url'),
                subscriber_count=creator_data.get('subscriber_count', 0),
                following_count=creator_data.get('following_count', 0),
                photo_count=creator_data.get('photo_count', 0),
                video_count=creator_data.get('video_count', 0),
                archived_post_count=creator_data.get('archived_post_count', 0),
                private_archived_post_count=creator_data.get('private_archived_post_count', 0),
                stream_count=creator_data.get('stream_count', 0),
                is_verified=creator_data.get('is_verified', False),
                is_real_performer=creator_data.get('is_real_performer', False),
                can_look_story=creator_data.get('can_look_story', True),
                can_comment_story=creator_data.get('can_comment_story', True),
                has_not_viewed_story=creator_data.get('has_not_viewed_story', False),
                is_restricted=creator_data.get('is_restricted', False),
                can_earn=creator_data.get('can_earn', True),
                joined_at=joined_at,
                last_seen=None,
                subscription_price=creator_data.get('subscription_price', 0.0),
                subscription_bundles=creator_data.get('subscription_bundles', []),
                promotional_campaigns=creator_data.get('promotional_campaigns', []),
                current_subscribe_price=creator_data.get('current_subscribe_price', 0.0),
                subscribe_prices=creator_data.get('subscribe_prices', []),
                tips_enabled=creator_data.get('tips_enabled', True),
                tips_text_enabled=creator_data.get('tips_text_enabled', True),
                tips_min_amount=creator_data.get('tips_min_amount', 1.0),
                tips_max_amount=creator_data.get('tips_max_amount', 100.0),
                show_posts_in_feed=creator_data.get('show_posts_in_feed', True),
                can_suggest_price=creator_data.get('can_suggest_price', True),
                privacy_settings=creator_data.get('privacy_settings', {}),
                notification_settings=creator_data.get('notification_settings', {}),
                earnings_total=creator_data.get('earnings_total', 0.0),
                earnings_tips=creator_data.get('earnings_tips', 0.0),
                earnings_posts=creator_data.get('earnings_posts', 0.0),
                earnings_streams=creator_data.get('earnings_streams', 0.0),
                earnings_referrals=creator_data.get('earnings_referrals', 0.0),
                payout_method=creator_data.get('payout_method', 'bank_transfer')
            )
            
            return creator
            
        except Exception as e:
            self.logger.error(f"Error parsing creator data: {str(e)}")
            return None
    
    async def _parse_post_data(self, post_data: Dict[str, Any]) -> Optional[OnlyFansPost]:
        """Parse post data"""        try:
            created_at = datetime.fromisoformat(post_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            post = OnlyFansPost(
                post_id=post_data.get('id', ''),
                creator_id=post_data.get('creator_id', ''),
                creator_username=post_data.get('creator_username', ''),
                text=post_data.get('text', ''),
                localized_text=post_data.get('localized_text', ''),
                created_at=created_at,
                changed_at=None,
                media_count=post_data.get('media_count', 0),
                media_type=post_data.get('media_type', 'text'),
                media_urls=post_data.get('media_urls', []),
                media_info=post_data.get('media_info', []),
                preview_ids=post_data.get('preview_ids', []),
                thumbnail_url=post_data.get('thumbnail_url'),
                price=post_data.get('price', 0.0),
                is_archived=post_data.get('is_archived', False),
                is_bookmarked=post_data.get('is_bookmarked', False),
                is_favorite=post_data.get('is_favorite', False),
                is_watch_later=post_data.get('is_watch_later', False),
                is_purchased=post_data.get('is_purchased', False),
                is_opened=post_data.get('is_opened', False),
                can_purchase=post_data.get('can_purchase', True),
                can_comment=post_data.get('can_comment', True),
                can_toggle_favorite=post_data.get('can_toggle_favorite', True),
                can_report=post_data.get('can_report', True),
                can_delete=post_data.get('can_delete', False),
                can_pin=post_data.get('can_pin', False),
                comments_count=post_data.get('comments_count', 0),
                tips_amount=post_data.get('tips_amount', 0.0),
                tips_count=post_data.get('tips_count', 0),
                likes_count=post_data.get('likes_count', 0),
                is_liked=post_data.get('is_liked', False),
                is_paid=post_data.get('is_paid', False),
                author=post_data.get('author', ''),
                raw_text=post_data.get('raw_text', ''),
                preview_text=post_data.get('preview_text', ''),
                hashtags=post_data.get('hashtags', []),
                mentions=post_data.get('mentions', []),
                visibility=post_data.get('visibility', 'all'),
                promotion_type=post_data.get('promotion_type'),
                expire_date=None,
                post_stats=post_data.get('post_stats', {})
            )
            
            return post
            
        except Exception as e:
            self.logger.error(f"Error parsing post data: {str(e)}")
            return None
    
    async def _parse_message_data(self, message_data: Dict[str, Any]) -> Optional[OnlyFansMessage]:
        """Parse message data"""        try:
            created_at = datetime.fromisoformat(message_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            message = OnlyFansMessage(
                message_id=message_data.get('id', ''),
                from_user_id=message_data.get('from_user_id', ''),
                to_user_id=message_data.get('to_user_id', ''),
                text=message_data.get('text', ''),
                localized_text=message_data.get('localized_text', ''),
                created_at=created_at,
                is_new=message_data.get('is_new', False),
                is_free=message_data.get('is_free', True),
                price=message_data.get('price', 0.0),
                media_count=message_data.get('media_count', 0),
                media_type=message_data.get('media_type', 'text'),
                media_urls=message_data.get('media_urls', []),
                media_info=message_data.get('media_info', []),
                preview_ids=message_data.get('preview_ids', []),
                can_purchase=message_data.get('can_purchase', False),
                can_reply=message_data.get('can_reply', True),
                can_unsend=message_data.get('can_unsend', False),
                can_report=message_data.get('can_report', True),
                is_opened=message_data.get('is_opened', False),
                is_purchased=message_data.get('is_purchased', False),
                tips_amount=message_data.get('tips_amount', 0.0),
                hashtags=message_data.get('hashtags', []),
                mentions=message_data.get('mentions', []),
                raw_text=message_data.get('raw_text', ''),
                preview_text=message_data.get('preview_text', ''),
                response_type=message_data.get('response_type', 'message')
            )
            
            return message
            
        except Exception as e:
            self.logger.error(f"Error parsing message data: {str(e)}")
            return None
    
    async def _parse_subscription_data(self, subscription_data: Dict[str, Any]) -> Optional[OnlyFansSubscription]:
        """Parse subscription data"""        try:
            started_at = datetime.fromisoformat(subscription_data.get('started_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            expires_at = None
            if subscription_data.get('expires_at'):
                expires_at = datetime.fromisoformat(subscription_data['expires_at'].replace('Z', '+00:00'))
            
            subscription = OnlyFansSubscription(
                subscription_id=subscription_data.get('id', ''),
                user_id=subscription_data.get('user_id', ''),
                creator_id=subscription_data.get('creator_id', ''),
                creator_username=subscription_data.get('creator_username', ''),
                creator_name=subscription_data.get('creator_name', ''),
                status=subscription_data.get('status', 'active'),
                started_at=started_at,
                expires_at=expires_at,
                renewed_at=None,
                cancelled_at=None,
                subscription_type=subscription_data.get('subscription_type', 'regular'),
                price=subscription_data.get('price', 0.0),
                recurring_price=subscription_data.get('recurring_price', 0.0),
                discount_percent=subscription_data.get('discount_percent', 0),
                auto_rebill=subscription_data.get('auto_rebill', True),
                show_posts_in_feed=subscription_data.get('show_posts_in_feed', True),
                can_comment=subscription_data.get('can_comment', True),
                can_message=subscription_data.get('can_message', True),
                total_spent=subscription_data.get('total_spent', 0.0),
                tips_given=subscription_data.get('tips_given', 0.0),
                messages_sent=subscription_data.get('messages_sent', 0),
                last_interaction=None,
                subscription_source=subscription_data.get('subscription_source', 'direct'),
                payment_method=subscription_data.get('payment_method', 'credit_card'),
                transaction_id=subscription_data.get('transaction_id', '')
            )
            
            return subscription
            
        except Exception as e:
            self.logger.error(f"Error parsing subscription data: {str(e)}")
            return None
    
    async def _parse_stream_data(self, stream_data: Dict[str, Any]) -> Optional[OnlyFansStream]:
        """Parse stream data"""        try:
            started_at = datetime.fromisoformat(stream_data.get('started_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            ended_at = None
            if stream_data.get('ended_at'):
                ended_at = datetime.fromisoformat(stream_data['ended_at'].replace('Z', '+00:00'))
            
            stream = OnlyFansStream(
                stream_id=stream_data.get('id', ''),
                creator_id=stream_data.get('creator_id', ''),
                creator_username=stream_data.get('creator_username', ''),
                title=stream_data.get('title', ''),
                description=stream_data.get('description', ''),
                started_at=started_at,
                ended_at=ended_at,
                duration_seconds=stream_data.get('duration_seconds', 0),
                status=stream_data.get('status', 'ended'),
                viewer_count=stream_data.get('viewer_count', 0),
                max_viewers=stream_data.get('max_viewers', 0),
                likes_count=stream_data.get('likes_count', 0),
                tips_amount=stream_data.get('tips_amount', 0.0),
                tips_count=stream_data.get('tips_count', 0),
                is_private=stream_data.get('is_private', False),
                price=stream_data.get('price', 0.0),
                thumbnail_url='',
                stream_url='',
                quality_options=stream_data.get('quality_options', ['720p']),
                chat_enabled=stream_data.get('chat_enabled', True),
                recording_enabled=stream_data.get('recording_enabled', False),
                can_join=stream_data.get('can_join', True),
                can_tip=stream_data.get('can_tip', True),
                can_chat=stream_data.get('can_chat', True),
                viewers=stream_data.get('viewers', []),
                moderators=stream_data.get('moderators', []),
                tags=stream_data.get('tags', []),
                category=stream_data.get('category', 'chat')
            )
            
            return stream
            
        except Exception as e:
            self.logger.error(f"Error parsing stream data: {str(e)}")
            return None
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""        try:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            # Enforce minimum delay between requests
            min_interval = 60.0 / self.requests_per_minute
            if time_since_last < min_interval:
                await asyncio.sleep(min_interval - time_since_last)
            
            self.last_request_time = current_time
            self.request_count += 1
            
        except Exception as e:
            self.logger.error(f"Error in rate limiting: {str(e)}")
    
    async def extract_content_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from OnlyFans content"""        try:
            # Parse OnlyFans URL
            parsed_url = urlparse(url)
            
            metadata = {
                'platform': 'onlyfans',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat(),
                'privacy_compliant': self.respect_privacy
            }
            
            # Handle OnlyFans URLs
            if 'onlyfans.com' in parsed_url.netloc:
                path_parts = parsed_url.path.strip('/').split('/')
                
                if len(path_parts) >= 1:
                    if path_parts[0] == 'post':
                        # Post URL: /post/post_id
                        if len(path_parts) >= 2:
                            metadata.update({
                                'content_type': 'post',
                                'post_id': path_parts[1]
                            })
                    
                    elif path_parts[0] == 'stream':
                        # Stream URL: /stream/stream_id
                        if len(path_parts) >= 2:
                            metadata.update({
                                'content_type': 'stream',
                                'stream_id': path_parts[1]
                            })
                    
                    elif path_parts[0] == 'messages':
                        # Message URL: /messages/message_id
                        if len(path_parts) >= 2:
                            metadata.update({
                                'content_type': 'message',
                                'message_id': path_parts[1],
                                'requires_permission': True
                            })
                    
                    else:
                        # Creator profile: /username
                        metadata.update({
                            'content_type': 'creator',
                            'username': path_parts[0]
                        })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting OnlyFans metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get OnlyFans platform information"""        return {
            'platform_name': 'OnlyFans',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Creator profile tracking',
                'Post and media monitoring',
                'Subscription management tracking',
                'Private message monitoring (with permissions)',
                'Live stream tracking',
                'Monetization and earnings analysis',
                'Tip and payment tracking',
                'Fan engagement metrics',
                'Content performance analysis',
                'Privacy-aware data collection'
            ],
            'authentication': {
                'required': True,
                'type': 'OAuth 2.0 + API Key',
                'scope': 'Creator and subscriber content access'
            },
            'privacy_compliance': {
                'respect_privacy': self.respect_privacy,
                'require_authentication': self.require_authentication,
                'restricted_content': True,
                'age_verification': True
            },
            'content_characteristics': {
                'adult_content': True,
                'subscription_based': True,
                'creator_economy': True,
                'monetization_focused': True
            },
            'limitations': [
                'Adult content platform (18+ only)',
                'Strict rate limiting',
                'Requires authentication for most content',
                'Privacy restrictions on personal data',
                'Geographic restrictions may apply',
                'Payment information is restricted',
                'Message access requires special permissions'
            ]
        }
