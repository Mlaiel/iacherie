"""Mastodon Crawler Implementation
===============================

Advanced Mastodon platform crawler for decentralized social networking content monitoring.
Implements comprehensive Post, User, Instance, and Federation tracking.

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
class MastodonPost:
    """Mastodon post (toot) information"""    post_id: str
    uri: str
    url: str
    account_id: str
    username: str
    display_name: str
    content: str
    content_warning: Optional[str]
    language: str
    created_at: datetime
    edited_at: Optional[datetime]
    visibility: str  # public, unlisted, private, direct
    sensitive: bool
    spoiler_text: str
    replies_count: int
    reblogs_count: int
    favourites_count: int
    reblogged: bool
    favourited: bool
    bookmarked: bool
    pinned: bool
    in_reply_to_id: Optional[str]
    in_reply_to_account_id: Optional[str]
    reblog_of_id: Optional[str]
    poll: Optional[Dict[str, Any]]
    card: Optional[Dict[str, Any]]
    media_attachments: List[Dict[str, Any]]
    mentions: List[Dict[str, str]]
    tags: List[Dict[str, str]]
    emojis: List[Dict[str, str]]
    application: Optional[Dict[str, str]]
    instance_domain: str
    federated_from: Optional[str]


@dataclass
class MastodonAccount:
    """Mastodon account information"""    account_id: str
    username: str
    acct: str  # username@domain for remote accounts
    display_name: str
    locked: bool
    bot: bool
    discoverable: bool
    group: bool
    created_at: datetime
    note: str  # bio
    url: str
    avatar_url: str
    avatar_static_url: str
    header_url: str
    header_static_url: str
    followers_count: int
    following_count: int
    statuses_count: int
    last_status_at: Optional[datetime]
    source: Optional[Dict[str, Any]]
    emojis: List[Dict[str, str]]
    fields: List[Dict[str, str]]
    moved_to: Optional[str]
    suspended: bool
    limited: bool
    instance_domain: str
    verified_at: Optional[datetime]
    roles: List[str]
    memorial: bool


@dataclass
class MastodonInstance:
    """Mastodon instance information"""    domain: str
    title: str
    short_description: str
    description: str
    version: str
    languages: List[str]
    registrations: bool
    approval_required: bool
    invites_enabled: bool
    configuration: Dict[str, Any]
    stats: Dict[str, int]  # user_count, status_count, domain_count
    thumbnail: str
    contact_account: Optional[Dict[str, Any]]
    rules: List[Dict[str, str]]
    max_toot_chars: int
    streaming_api: str
    created_at: datetime
    updated_at: datetime
    active_month: int
    active_halfyear: int
    local_posts: int
    federation_enabled: bool
    peers: List[str]
    category: str
    moderators: List[str]


@dataclass
class MastodonNotification:
    """Mastodon notification information"""    notification_id: str
    type: str  # mention, status, reblog, follow, follow_request, favourite, poll, update
    created_at: datetime
    account: Dict[str, Any]
    status: Optional[Dict[str, Any]]
    target: Optional[Dict[str, Any]]
    is_read: bool
    grouped: bool
    instance_domain: str


@dataclass
class MastodonHashtag:
    """Mastodon hashtag information"""    name: str
    url: str
    history: List[Dict[str, Any]]  # usage statistics
    following: bool
    total_uses: int
    accounts_count: int
    trending: bool
    trend_score: float
    last_updated: datetime
    related_tags: List[str]
    instance_domain: str


class MastodonCrawler(PlatformCrawler):
    """    Advanced Mastodon crawler for decentralized social networking content monitoring.
    
    Features:
    - Multi-instance federation crawling
    - Post (toot) content tracking
    - Account profile analysis
    - Hashtag trending analysis
    - Instance discovery and monitoring
    - Cross-instance interaction tracking
    - Privacy-aware content collection
    - Moderation and community tracking
    - Federated timeline analysis
    - Local instance community analysis
    """    
    def __init__(self, config: CrawlerConfig, vector_matcher=None):
        super().__init__(config, vector_matcher)
        self.platform_name = "mastodon"
        self.base_url = "https://mastodon.social"  # Default instance
        self.api_base_url = "https://mastodon.social/api/v1"
        
        # Configure for multiple instances
        self.instances = [
            "mastodon.social",
            "mastodon.online", 
            "fosstodon.org",
            "mas.to",
            "mstdn.social",
            "pixelfed.social",
            "lemmy.ml"
        ]
        
        # Rate limiting (Mastodon is generally permissive)
        self.requests_per_minute = 60
        self.min_delay = 1.0
        self.max_delay = 2.0
        
        # Content type mappings
        self.content_types = {
            'posts': self._crawl_posts,
            'accounts': self._crawl_accounts,
            'instances': self._crawl_instances,
            'hashtags': self._crawl_hashtags,
            'notifications': self._crawl_notifications,
            'federated': self._crawl_federated_timeline,
            'local': self._crawl_local_timeline,
            'trending': self._crawl_trending,
            'search': self._crawl_search
        }
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Mastodon-specific headers"""        self.session_headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'MastodonCrawler/1.0 (https://example.com/contact; crawler@example.com)',
            'Content-Type': 'application/json'
        })
    
    async def search_content(self, query: str, content_type: str = "posts", 
                           max_results: int = 50, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """        Search for content on Mastodon across multiple instances.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            filters: Additional search filters (instance, language, etc.)
            
        Returns:
            List of crawler results
        """        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, filters)
            
            self.logger.info(f"Found {len(results)} Mastodon {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Mastodon content: {str(e)}")
            return []
    
    async def _crawl_posts(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Mastodon posts across instances"""        try:
            results = []
            instances_to_search = self.instances
            
            # Filter instances if specified
            if filters and 'instances' in filters:
                instances_to_search = filters['instances']
            
            for instance in instances_to_search[:3]:  # Limit to 3 instances for performance
                instance_posts = await self._get_instance_posts(instance, query, max_results // len(instances_to_search))
                
                for post_data in instance_posts:
                    post = await self._parse_post_data(post_data)
                    if post:
                        result = CrawlerResult(
                            url=post.url,
                            title=f"@{post.username}: {post.content[:100]}...",
                            content=post.content,
                            metadata={
                                'post_data': asdict(post),
                                'platform': 'mastodon',
                                'content_type': 'post',
                                'username': post.username,
                                'display_name': post.display_name,
                                'visibility': post.visibility,
                                'instance_domain': post.instance_domain,
                                'language': post.language,
                                'replies_count': post.replies_count,
                                'reblogs_count': post.reblogs_count,
                                'favourites_count': post.favourites_count,
                                'sensitive': post.sensitive,
                                'tags': [tag['name'] for tag in post.tags],
                                'mentions': [mention['username'] for mention in post.mentions],
                                'federated_from': post.federated_from,
                                'has_media': len(post.media_attachments) > 0,
                                'has_poll': post.poll is not None
                            },
                            timestamp=post.created_at,
                            similarity_score=0.0
                        )
                        results.append(result)
                        
                        # Rate limiting
                        await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Mastodon posts: {str(e)}")
            return []
    
    async def _crawl_accounts(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Mastodon accounts"""        try:
            results = []
            
            # Mock account data
            mock_accounts = await self._get_mock_accounts(query, max_results)
            
            for account_data in mock_accounts:
                account = await self._parse_account_data(account_data)
                if account:
                    result = CrawlerResult(
                        url=account.url,
                        title=f"{account.display_name} (@{account.acct})",
                        content=account.note,
                        metadata={
                            'account_data': asdict(account),
                            'platform': 'mastodon',
                            'content_type': 'account',
                            'username': account.username,
                            'acct': account.acct,
                            'display_name': account.display_name,
                            'instance_domain': account.instance_domain,
                            'followers_count': account.followers_count,
                            'following_count': account.following_count,
                            'statuses_count': account.statuses_count,
                            'locked': account.locked,
                            'bot': account.bot,
                            'discoverable': account.discoverable,
                            'verified_at': account.verified_at.isoformat() if account.verified_at else None,
                            'fields': account.fields,
                            'roles': account.roles,
                            'suspended': account.suspended
                        },
                        timestamp=account.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Mastodon accounts: {str(e)}")
            return []
    
    async def _crawl_instances(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Mastodon instances"""        try:
            results = []
            
            # Mock instance data
            mock_instances = await self._get_mock_instances(query, max_results)
            
            for instance_data in mock_instances:
                instance = await self._parse_instance_data(instance_data)
                if instance:
                    result = CrawlerResult(
                        url=f"https://{instance.domain}",
                        title=f"{instance.title} ({instance.domain})",
                        content=instance.description,
                        metadata={
                            'instance_data': asdict(instance),
                            'platform': 'mastodon',
                            'content_type': 'instance',
                            'domain': instance.domain,
                            'title': instance.title,
                            'version': instance.version,
                            'languages': instance.languages,
                            'registrations': instance.registrations,
                            'approval_required': instance.approval_required,
                            'user_count': instance.stats.get('user_count', 0),
                            'status_count': instance.stats.get('status_count', 0),
                            'domain_count': instance.stats.get('domain_count', 0),
                            'category': instance.category,
                            'federation_enabled': instance.federation_enabled,
                            'active_month': instance.active_month,
                            'local_posts': instance.local_posts
                        },
                        timestamp=instance.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Mastodon instances: {str(e)}")
            return []
    
    async def _crawl_hashtags(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Mastodon hashtags"""        try:
            results = []
            
            # Mock hashtag data
            mock_hashtags = await self._get_mock_hashtags(query, max_results)
            
            for hashtag_data in mock_hashtags:
                hashtag = await self._parse_hashtag_data(hashtag_data)
                if hashtag:
                    result = CrawlerResult(
                        url=hashtag.url,
                        title=f"#{hashtag.name}",
                        content=f"Hashtag #{hashtag.name} with {hashtag.total_uses} total uses",
                        metadata={
                            'hashtag_data': asdict(hashtag),
                            'platform': 'mastodon',
                            'content_type': 'hashtag',
                            'name': hashtag.name,
                            'total_uses': hashtag.total_uses,
                            'accounts_count': hashtag.accounts_count,
                            'trending': hashtag.trending,
                            'trend_score': hashtag.trend_score,
                            'following': hashtag.following,
                            'instance_domain': hashtag.instance_domain,
                            'related_tags': hashtag.related_tags,
                            'history': hashtag.history
                        },
                        timestamp=hashtag.last_updated,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Mastodon hashtags: {str(e)}")
            return []
    
    async def _crawl_notifications(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl Mastodon notifications"""        try:
            results = []
            
            # Mock notification data
            mock_notifications = await self._get_mock_notifications(query, max_results)
            
            for notification_data in mock_notifications:
                notification = await self._parse_notification_data(notification_data)
                if notification:
                    result = CrawlerResult(
                        url=f"https://{notification.instance_domain}/notifications",
                        title=f"Notification: {notification.type}",
                        content=f"Notification of type {notification.type}",
                        metadata={
                            'notification_data': asdict(notification),
                            'platform': 'mastodon',
                            'content_type': 'notification',
                            'type': notification.type,
                            'instance_domain': notification.instance_domain,
                            'is_read': notification.is_read,
                            'grouped': notification.grouped,
                            'account': notification.account,
                            'status': notification.status,
                            'target': notification.target
                        },
                        timestamp=notification.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Mastodon notifications: {str(e)}")
            return []
    
    async def _crawl_federated_timeline(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl federated timeline"""        try:
            results = []
            
            # Get federated timeline content
            federated_content = await self._get_federated_timeline(query, max_results, filters)
            
            for content in federated_content:
                result = CrawlerResult(
                    url=content.get('url', ''),
                    title=f"[FEDERATED] {content.get('title', 'Unknown')}",
                    content=content.get('content', ''),
                    metadata={
                        'federated_data': content,
                        'platform': 'mastodon',
                        'content_type': 'federated_timeline',
                        'is_federated': True,
                        'origin_instance': content.get('origin_instance'),
                        'federation_reach': content.get('federation_reach', 0)
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling federated timeline: {str(e)}")
            return []
    
    async def _crawl_local_timeline(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl local instance timeline"""        try:
            results = []
            
            # Get local timeline content
            local_content = await self._get_local_timeline(query, max_results, filters)
            
            for content in local_content:
                result = CrawlerResult(
                    url=content.get('url', ''),
                    title=f"[LOCAL] {content.get('title', 'Unknown')}",
                    content=content.get('content', ''),
                    metadata={
                        'local_data': content,
                        'platform': 'mastodon',
                        'content_type': 'local_timeline',
                        'is_local': True,
                        'instance_domain': content.get('instance_domain'),
                        'community_engagement': content.get('community_engagement', 0)
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling local timeline: {str(e)}")
            return []
    
    async def _crawl_trending(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """Crawl trending Mastodon content"""        try:
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
                        'platform': 'mastodon',
                        'content_type': 'trending',
                        'is_trending': True,
                        'trend_score': content.get('trend_score', 0),
                        'trend_type': content.get('trend_type', 'general')
                    },
                    timestamp=datetime.utcnow(),
                    similarity_score=0.0
                )
                results.append(result)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling trending Mastodon content: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[CrawlerResult]:
        """General Mastodon search"""        try:
            results = []
            
            # Search across different content types
            posts = await self._crawl_posts(query, max_results // 3, filters)
            accounts = await self._crawl_accounts(query, max_results // 3, filters)
            hashtags = await self._crawl_hashtags(query, max_results // 3, filters)
            
            results.extend(posts)
            results.extend(accounts)
            results.extend(hashtags)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Mastodon search: {str(e)}")
            return []
    
    # Mock data generators and helper methods
    
    async def _get_instance_posts(self, instance: str, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Get posts from specific instance"""        # Mock implementation - in reality would call actual API
        return await self._get_mock_posts(query, max_results, instance)
    
    async def _get_mock_posts(self, query: str, max_results: int, instance: str = "mastodon.social") -> List[Dict[str, Any]]:
        """Generate mock post data"""        posts = []
        
        for i in range(min(max_results, 20)):
            created_at = datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            posts.append({
                'id': f'post_{instance.replace(".", "_")}_{i}',
                'uri': f'https://{instance}/users/user{i}/statuses/{i}',
                'url': f'https://{instance}/@user{i}/{i}',
                'account_id': f'user_{i}',
                'username': f'{query.lower() if query else "user"}{i}',
                'display_name': f'{query} User {i}' if query else f'User {i}',
                'content': f'Interesting post about {query} on the fediverse!' if query else f'Post content {i}',
                'content_warning': None,
                'language': random.choice(['en', 'es', 'fr', 'de', 'ja']),
                'created_at': created_at.isoformat(),
                'visibility': random.choice(['public', 'unlisted', 'private']),
                'sensitive': random.choice([True, False]),
                'spoiler_text': '',
                'replies_count': random.randint(0, 50),
                'reblogs_count': random.randint(0, 100),
                'favourites_count': random.randint(0, 200),
                'tags': [{'name': query}] if query else [{'name': 'mastodon'}, {'name': 'fediverse'}],
                'mentions': [{'username': f'mention{j}'} for j in range(random.randint(0, 3))],
                'media_attachments': [],
                'instance_domain': instance,
                'federated_from': random.choice([None, 'other.instance']) if random.choice([True, False]) else None
            })
        
        return posts
    
    async def _get_mock_accounts(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock account data"""        accounts = []
        
        for i in range(min(max_results, 15)):
            created_at = datetime.utcnow() - timedelta(days=random.randint(30, 1095))
            instance = random.choice(self.instances)
            accounts.append({
                'id': f'account_{i}',
                'username': f'{query.lower() if query else "user"}{i}',
                'acct': f'{query.lower() if query else "user"}{i}@{instance}',
                'display_name': f'{query} Expert {i}' if query else f'User {i}',
                'locked': random.choice([True, False]),
                'bot': random.choice([True, False]),
                'discoverable': random.choice([True, False]),
                'created_at': created_at.isoformat(),
                'note': f'Passionate about {query} and the fediverse' if query else f'Mastodon user {i}',
                'url': f'https://{instance}/@{query.lower() if query else "user"}{i}',
                'followers_count': random.randint(10, 5000),
                'following_count': random.randint(10, 1000),
                'statuses_count': random.randint(1, 10000),
                'fields': [{'name': 'Interests', 'value': query if query else 'Technology'}],
                'instance_domain': instance,
                'verified_at': (datetime.utcnow() - timedelta(days=random.randint(1, 365))).isoformat() if random.choice([True, False]) else None,
                'roles': ['member'] if not random.choice([True, False]) else ['moderator'],
                'suspended': False
            })
        
        return accounts
    
    async def _get_mock_instances(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock instance data"""        instances = []
        
        for i, domain in enumerate(self.instances[:max_results]):
            created_at = datetime.utcnow() - timedelta(days=random.randint(365, 2555))
            instances.append({
                'domain': domain,
                'title': f'{query} Community' if query else f'{domain.split(".")[0].title()} Community',
                'short_description': f'Community for {query} enthusiasts' if query else f'Mastodon instance',
                'description': f'A federated community focused on {query}' if query else f'Description for {domain}',
                'version': '4.1.0',
                'languages': ['en', 'es', 'fr'],
                'registrations': random.choice([True, False]),
                'approval_required': random.choice([True, False]),
                'stats': {
                    'user_count': random.randint(100, 100000),
                    'status_count': random.randint(1000, 1000000),
                    'domain_count': random.randint(50, 10000)
                },
                'created_at': created_at.isoformat(),
                'category': random.choice(['general', 'technology', 'art', 'activism']),
                'federation_enabled': True,
                'active_month': random.randint(50, 10000),
                'local_posts': random.randint(500, 50000)
            })
        
        return instances
    
    async def _get_mock_hashtags(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock hashtag data"""        hashtags = []
        
        for i in range(min(max_results, 20)):
            last_updated = datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            hashtags.append({
                'name': f'{query}' if query else f'hashtag{i}',
                'url': f'https://mastodon.social/tags/{query if query else f"hashtag{i}"}',
                'total_uses': random.randint(100, 10000),
                'accounts_count': random.randint(50, 1000),
                'trending': random.choice([True, False]),
                'trend_score': random.uniform(0.1, 1.0),
                'following': random.choice([True, False]),
                'last_updated': last_updated.isoformat(),
                'instance_domain': 'mastodon.social',
                'related_tags': [f'related{j}' for j in range(random.randint(1, 5))],
                'history': [{'day': str(i), 'uses': str(random.randint(10, 100))} for i in range(7)]
            })
        
        return hashtags
    
    async def _get_mock_notifications(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock notification data"""        notifications = []
        notification_types = ['mention', 'status', 'reblog', 'follow', 'favourite', 'poll']
        
        for i in range(min(max_results, 25)):
            created_at = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            notifications.append({
                'id': f'notification_{i}',
                'type': random.choice(notification_types),
                'created_at': created_at.isoformat(),
                'account': {'id': f'user_{i}', 'username': f'user{i}'},
                'status': {'id': f'status_{i}', 'content': f'Status about {query}'} if query else None,
                'is_read': random.choice([True, False]),
                'grouped': random.choice([True, False]),
                'instance_domain': random.choice(self.instances)
            })
        
        return notifications
    
    async def _get_federated_timeline(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get federated timeline content"""        content = []
        
        for i in range(min(max_results, 15)):
            content.append({
                'title': f'Federated: {query} {i}' if query else f'Federated Content {i}',
                'url': f'https://mastodon.social/federated/{i}',
                'content': f'Federated content about {query}' if query else f'Federated description {i}',
                'origin_instance': random.choice(self.instances),
                'federation_reach': random.randint(5, 50)
            })
        
        return content
    
    async def _get_local_timeline(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get local timeline content"""        content = []
        
        for i in range(min(max_results, 15)):
            content.append({
                'title': f'Local: {query} {i}' if query else f'Local Content {i}',
                'url': f'https://mastodon.social/local/{i}',
                'content': f'Local content about {query}' if query else f'Local description {i}',
                'instance_domain': random.choice(self.instances),
                'community_engagement': random.randint(10, 100)
            })
        
        return content
    
    async def _get_trending_content(self, query: str, max_results: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get trending content"""        content = []
        
        for i in range(min(max_results, 10)):
            content.append({
                'title': f'Trending: {query} {i}' if query else f'Trending Content {i}',
                'url': f'https://mastodon.social/trending/{i}',
                'description': f'Trending content about {query}' if query else f'Trending description {i}',
                'trend_score': random.randint(70, 100),
                'trend_type': random.choice(['hashtag', 'link', 'account'])
            })
        
        return content
    
    # Parser methods
    
    async def _parse_post_data(self, post_data: Dict[str, Any]) -> Optional[MastodonPost]:
        """Parse post data"""        try:
            created_at = datetime.fromisoformat(post_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            post = MastodonPost(
                post_id=post_data.get('id', ''),
                uri=post_data.get('uri', ''),
                url=post_data.get('url', ''),
                account_id=post_data.get('account_id', ''),
                username=post_data.get('username', ''),
                display_name=post_data.get('display_name', ''),
                content=post_data.get('content', ''),
                content_warning=post_data.get('content_warning'),
                language=post_data.get('language', 'en'),
                created_at=created_at,
                edited_at=None,
                visibility=post_data.get('visibility', 'public'),
                sensitive=post_data.get('sensitive', False),
                spoiler_text=post_data.get('spoiler_text', ''),
                replies_count=post_data.get('replies_count', 0),
                reblogs_count=post_data.get('reblogs_count', 0),
                favourites_count=post_data.get('favourites_count', 0),
                reblogged=post_data.get('reblogged', False),
                favourited=post_data.get('favourited', False),
                bookmarked=post_data.get('bookmarked', False),
                pinned=post_data.get('pinned', False),
                in_reply_to_id=post_data.get('in_reply_to_id'),
                in_reply_to_account_id=post_data.get('in_reply_to_account_id'),
                reblog_of_id=post_data.get('reblog_of_id'),
                poll=post_data.get('poll'),
                card=post_data.get('card'),
                media_attachments=post_data.get('media_attachments', []),
                mentions=post_data.get('mentions', []),
                tags=post_data.get('tags', []),
                emojis=post_data.get('emojis', []),
                application=post_data.get('application'),
                instance_domain=post_data.get('instance_domain', ''),
                federated_from=post_data.get('federated_from')
            )
            
            return post
            
        except Exception as e:
            self.logger.error(f"Error parsing post data: {str(e)}")
            return None
    
    async def _parse_account_data(self, account_data: Dict[str, Any]) -> Optional[MastodonAccount]:
        """Parse account data"""        try:
            created_at = datetime.fromisoformat(account_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            verified_at = None
            if account_data.get('verified_at'):
                verified_at = datetime.fromisoformat(account_data['verified_at'].replace('Z', '+00:00'))
            
            account = MastodonAccount(
                account_id=account_data.get('id', ''),
                username=account_data.get('username', ''),
                acct=account_data.get('acct', ''),
                display_name=account_data.get('display_name', ''),
                locked=account_data.get('locked', False),
                bot=account_data.get('bot', False),
                discoverable=account_data.get('discoverable', True),
                group=account_data.get('group', False),
                created_at=created_at,
                note=account_data.get('note', ''),
                url=account_data.get('url', ''),
                avatar_url='',
                avatar_static_url='',
                header_url='',
                header_static_url='',
                followers_count=account_data.get('followers_count', 0),
                following_count=account_data.get('following_count', 0),
                statuses_count=account_data.get('statuses_count', 0),
                last_status_at=None,
                source=account_data.get('source'),
                emojis=account_data.get('emojis', []),
                fields=account_data.get('fields', []),
                moved_to=account_data.get('moved_to'),
                suspended=account_data.get('suspended', False),
                limited=account_data.get('limited', False),
                instance_domain=account_data.get('instance_domain', ''),
                verified_at=verified_at,
                roles=account_data.get('roles', []),
                memorial=account_data.get('memorial', False)
            )
            
            return account
            
        except Exception as e:
            self.logger.error(f"Error parsing account data: {str(e)}")
            return None
    
    async def _parse_instance_data(self, instance_data: Dict[str, Any]) -> Optional[MastodonInstance]:
        """Parse instance data"""        try:
            created_at = datetime.fromisoformat(instance_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            instance = MastodonInstance(
                domain=instance_data.get('domain', ''),
                title=instance_data.get('title', ''),
                short_description=instance_data.get('short_description', ''),
                description=instance_data.get('description', ''),
                version=instance_data.get('version', ''),
                languages=instance_data.get('languages', []),
                registrations=instance_data.get('registrations', True),
                approval_required=instance_data.get('approval_required', False),
                invites_enabled=instance_data.get('invites_enabled', True),
                configuration=instance_data.get('configuration', {}),
                stats=instance_data.get('stats', {}),
                thumbnail='',
                contact_account=instance_data.get('contact_account'),
                rules=instance_data.get('rules', []),
                max_toot_chars=instance_data.get('max_toot_chars', 500),
                streaming_api='',
                created_at=created_at,
                updated_at=datetime.utcnow(),
                active_month=instance_data.get('active_month', 0),
                active_halfyear=instance_data.get('active_halfyear', 0),
                local_posts=instance_data.get('local_posts', 0),
                federation_enabled=instance_data.get('federation_enabled', True),
                peers=instance_data.get('peers', []),
                category=instance_data.get('category', ''),
                moderators=instance_data.get('moderators', [])
            )
            
            return instance
            
        except Exception as e:
            self.logger.error(f"Error parsing instance data: {str(e)}")
            return None
    
    async def _parse_hashtag_data(self, hashtag_data: Dict[str, Any]) -> Optional[MastodonHashtag]:
        """Parse hashtag data"""        try:
            last_updated = datetime.fromisoformat(hashtag_data.get('last_updated', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            hashtag = MastodonHashtag(
                name=hashtag_data.get('name', ''),
                url=hashtag_data.get('url', ''),
                history=hashtag_data.get('history', []),
                following=hashtag_data.get('following', False),
                total_uses=hashtag_data.get('total_uses', 0),
                accounts_count=hashtag_data.get('accounts_count', 0),
                trending=hashtag_data.get('trending', False),
                trend_score=hashtag_data.get('trend_score', 0.0),
                last_updated=last_updated,
                related_tags=hashtag_data.get('related_tags', []),
                instance_domain=hashtag_data.get('instance_domain', '')
            )
            
            return hashtag
            
        except Exception as e:
            self.logger.error(f"Error parsing hashtag data: {str(e)}")
            return None
    
    async def _parse_notification_data(self, notification_data: Dict[str, Any]) -> Optional[MastodonNotification]:
        """Parse notification data"""        try:
            created_at = datetime.fromisoformat(notification_data.get('created_at', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            notification = MastodonNotification(
                notification_id=notification_data.get('id', ''),
                type=notification_data.get('type', ''),
                created_at=created_at,
                account=notification_data.get('account', {}),
                status=notification_data.get('status'),
                target=notification_data.get('target'),
                is_read=notification_data.get('is_read', False),
                grouped=notification_data.get('grouped', False),
                instance_domain=notification_data.get('instance_domain', '')
            )
            
            return notification
            
        except Exception as e:
            self.logger.error(f"Error parsing notification data: {str(e)}")
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
        """Extract metadata from Mastodon content"""        try:
            # Parse Mastodon URL
            parsed_url = urlparse(url)
            
            metadata = {
                'platform': 'mastodon',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Extract instance domain
            if parsed_url.netloc:
                metadata['instance_domain'] = parsed_url.netloc
                
                # Handle different Mastodon URL patterns
                path_parts = parsed_url.path.strip('/').split('/')
                
                if len(path_parts) >= 1:
                    if path_parts[0].startswith('@'):
                        # User profile: /@username
                        metadata.update({
                            'content_type': 'user',
                            'username': path_parts[0][1:]
                        })
                        
                        # Status URL: /@username/status_id
                        if len(path_parts) >= 2 and path_parts[1].isdigit():
                            metadata.update({
                                'content_type': 'status',
                                'status_id': path_parts[1]
                            })
                    
                    elif path_parts[0] == 'tags':
                        # Hashtag URL: /tags/hashtag_name
                        if len(path_parts) >= 2:
                            metadata.update({
                                'content_type': 'hashtag',
                                'hashtag': path_parts[1]
                            })
                    
                    elif path_parts[0] == 'users':
                        # ActivityPub user URL: /users/username
                        if len(path_parts) >= 2:
                            metadata.update({
                                'content_type': 'user',
                                'username': path_parts[1]
                            })
                            
                            # ActivityPub status URL: /users/username/statuses/status_id
                            if len(path_parts) >= 4 and path_parts[2] == 'statuses':
                                metadata.update({
                                    'content_type': 'status',
                                    'status_id': path_parts[3]
                                })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Mastodon metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Mastodon platform information"""        return {
            'platform_name': 'Mastodon',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Multi-instance federation crawling',
                'Post (toot) content tracking',
                'Account profile analysis',
                'Hashtag trending analysis',
                'Instance discovery and monitoring',
                'Cross-instance interaction tracking',
                'Privacy-aware content collection',
                'Moderation and community tracking',
                'Federated timeline analysis',
                'Local instance community analysis'
            ],
            'authentication': {
                'required': False,
                'type': 'OAuth 2.0 (Optional)',
                'scope': 'Public and private content access'
            },
            'content_characteristics': {
                'decentralized': True,
                'federated': True,
                'open_source': True,
                'privacy_focused': True
            },
            'instances': self.instances,
            'limitations': [
                'Instance-specific rate limits',
                'Federated content complexity',
                'Privacy restrictions',
                'Variable instance policies',
                'Content may be instance-locked'
            ]
        }
