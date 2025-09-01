"""Mastodon Platform Crawler - Ultra-Advanced Implementation
Federated Social Network Content Monitoring System

This module provides comprehensive crawling capabilities for Mastodon platform,
focusing on federated content, decentralized monitoring, and multi-instance analysis.

PROPRIETARY SOFTWARE - CONFIDENTIAL AND PROTECTED
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Created by: Fahed Mlaiel <mlaiel@live.de>

WARNING: This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import hashlib
import base64
from urllib.parse import urljoin, urlparse
from pydantic import BaseModel, Field, validator
from difflib import SequenceMatcher
import re

from ..base import BaseCrawler
from ...utils.rate_limiter import RateLimiter
from ...utils.cache import CacheManager
from ...utils.encryption import ContentEncryption
from ...utils.fingerprinting import ContentFingerprinter

logger = logging.getLogger(__name__)


class MastodonVisibility(str, Enum):
    """Mastodon post visibility levels"""
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"
    DIRECT = "direct"


class MastodonContentType(str, Enum):
    """Mastodon content types"""
    STATUS = "status"
    BOOST = "boost"
    REPLY = "reply"
    POLL = "poll"
    MEDIA = "media"
    ARTICLE = "article"


class MastodonNotificationType(str, Enum):
    """Mastodon notification types"""
    MENTION = "mention"
    STATUS = "status"
    REBLOG = "reblog"
    FOLLOW = "follow"
    FOLLOW_REQUEST = "follow_request"
    FAVOURITE = "favourite"
    POLL = "poll"
    UPDATE = "update"
    ADMIN_SIGN_UP = "admin.sign_up"
    ADMIN_REPORT = "admin.report"


class MastodonAttachment(BaseModel):
    """Mastodon media attachment data model"""
    attachment_id: str
    type: str  # image, video, gifv, audio, unknown
    url: str
    preview_url: Optional[str] = None
    remote_url: Optional[str] = None
    preview_remote_url: Optional[str] = None
    text_url: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None
    blurhash: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class MastodonEmoji(BaseModel):
    """Mastodon custom emoji data model"""
    shortcode: str
    url: str
    static_url: str
    visible_in_picker: bool = True
    category: Optional[str] = None


class MastodonMention(BaseModel):
    """Mastodon mention data model"""
    mention_id: str
    username: str
    url: str
    acct: str  # username@domain for remote users


class MastodonTag(BaseModel):
    """Mastodon hashtag data model"""
    name: str
    url: str
    history: List[Dict[str, Any]] = Field(default_factory=list)


class MastodonPoll(BaseModel):
    """Mastodon poll data model"""
    poll_id: str
    expires_at: Optional[datetime] = None
    expired: bool = False
    multiple: bool = False
    votes_count: int = 0
    voters_count: Optional[int] = None
    voted: Optional[bool] = None
    own_votes: List[int] = Field(default_factory=list)
    options: List[Dict[str, Any]] = Field(default_factory=list)
    emojis: List[MastodonEmoji] = Field(default_factory=list)


class MastodonCard(BaseModel):
    """Mastodon preview card data model"""
    url: str
    title: str
    description: str
    type: str  # link, photo, video, rich
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    provider_name: Optional[str] = None
    provider_url: Optional[str] = None
    html: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    image: Optional[str] = None
    embed_url: Optional[str] = None
    blurhash: Optional[str] = None


class MastodonApplication(BaseModel):
    """Mastodon application data model"""
    name: str
    website: Optional[str] = None
    vapid_key: Optional[str] = None


class MastodonAccount(BaseModel):
    """Mastodon account data model"""
    account_id: str
    username: str
    acct: str  # username@domain for remote accounts
    display_name: str
    locked: bool = False
    bot: bool = False
    discoverable: Optional[bool] = None
    group: bool = False
    created_at: datetime
    note: str = ""
    url: str
    avatar: str
    avatar_static: str
    header: str
    header_static: str
    followers_count: int = 0
    following_count: int = 0
    statuses_count: int = 0
    last_status_at: Optional[datetime] = None
    source: Dict[str, Any] = Field(default_factory=dict)
    emojis: List[MastodonEmoji] = Field(default_factory=list)
    fields: List[Dict[str, Any]] = Field(default_factory=list)
    moved: Optional['MastodonAccount'] = None
    suspended: bool = False
    limited: bool = False
    instance_url: str = ""
    local: bool = True


class MastodonStatus(BaseModel):
    """Mastodon status data model"""
    status_id: str
    uri: str
    created_at: datetime
    account: MastodonAccount
    content: str
    visibility: MastodonVisibility
    sensitive: bool = False
    spoiler_text: str = ""
    media_attachments: List[MastodonAttachment] = Field(default_factory=list)
    application: Optional[MastodonApplication] = None
    mentions: List[MastodonMention] = Field(default_factory=list)
    tags: List[MastodonTag] = Field(default_factory=list)
    emojis: List[MastodonEmoji] = Field(default_factory=list)
    reblogs_count: int = 0
    favourites_count: int = 0
    replies_count: int = 0
    url: Optional[str] = None
    in_reply_to_id: Optional[str] = None
    in_reply_to_account_id: Optional[str] = None
    reblog: Optional['MastodonStatus'] = None
    poll: Optional[MastodonPoll] = None
    card: Optional[MastodonCard] = None
    language: Optional[str] = None
    text: Optional[str] = None
    edited_at: Optional[datetime] = None
    favourited: Optional[bool] = None
    reblogged: Optional[bool] = None
    muted: Optional[bool] = None
    bookmarked: Optional[bool] = None
    pinned: Optional[bool] = None
    filtered: List[Dict[str, Any]] = Field(default_factory=list)
    instance_url: str = ""
    similarity_score: Optional[float] = None
    protection_status: str = "unprotected"


class MastodonInstance(BaseModel):
    """Mastodon instance data model"""
    uri: str
    title: str
    short_description: str
    description: str
    email: str
    version: str
    urls: Dict[str, str] = Field(default_factory=dict)
    stats: Dict[str, int] = Field(default_factory=dict)
    thumbnail: Optional[str] = None
    languages: List[str] = Field(default_factory=list)
    registrations: bool = True
    approval_required: bool = False
    invites_enabled: bool = True
    configuration: Dict[str, Any] = Field(default_factory=dict)
    contact_account: Optional[MastodonAccount] = None
    rules: List[Dict[str, Any]] = Field(default_factory=list)
    max_toot_chars: int = 500
    max_media_attachments: int = 4
    poll_limits: Dict[str, int] = Field(default_factory=dict)
    is_active: bool = True
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class MastodonSearchResults(BaseModel):
    """Mastodon search results data model"""
    query: str
    total_results: int
    accounts: List[MastodonAccount] = Field(default_factory=list)
    statuses: List[MastodonStatus] = Field(default_factory=list)
    hashtags: List[MastodonTag] = Field(default_factory=list)
    instances: List[MastodonInstance] = Field(default_factory=list)
    search_type: str
    filters_applied: Dict[str, Any]
    search_timestamp: datetime
    has_more: bool = False
    next_cursor: Optional[str] = None


class MastodonAnalytics(BaseModel):
    """Mastodon analytics data model"""
    account_id: str
    analysis_period: Tuple[datetime, datetime]
    total_statuses: int
    total_replies: int
    total_boosts: int
    total_favourites_received: int
    total_boosts_received: int
    average_favourites_per_status: float
    average_boosts_per_status: float
    most_active_hours: List[int]
    most_used_hashtags: List[str]
    most_mentioned_accounts: List[str]
    language_distribution: Dict[str, int]
    visibility_distribution: Dict[str, int]
    media_usage_stats: Dict[str, int]
    engagement_rate: float
    reach_estimate: int
    federation_reach: int
    instances_reached: Set[str]
    content_warnings_used: int
    sensitive_content_count: int
    similarity_violations: int
    protection_violations: int


class MastodonCrawler(BaseCrawler):
    """
    Ultra-Advanced Mastodon Platform Crawler
    
    Provides comprehensive crawling and monitoring capabilities for Mastodon federated network,
    specializing in multi-instance monitoring, federated content analysis, and decentralized protection.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Default instance configuration
        self.primary_instance = config.get('primary_instance', 'mastodon.social')
        self.base_url = f"https://{self.primary_instance}"
        self.api_base = f"{self.base_url}/api/v1"
        self.api_v2_base = f"{self.base_url}/api/v2"
        
        # Authentication
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.client_id: Optional[str] = None
        self.client_secret: Optional[str] = None
        
        # Multi-instance management
        self.monitored_instances: Set[str] = set([self.primary_instance])
        self.instance_tokens: Dict[str, str] = {}
        self.instance_stats: Dict[str, MastodonInstance] = {}
        
        # Rate limiting - Mastodon has generous limits
        self.rate_limiter = RateLimiter(
            requests_per_minute=300,
            requests_per_hour=3000,
            burst_limit=50
        )
        
        # Cache management
        self.cache_manager = CacheManager(
            cache_ttl=300,  # 5 minutes for federated content
            max_cache_size=5000
        )
        
        # Content protection
        self.content_encryption = ContentEncryption()
        self.content_fingerprinter = ContentFingerprinter()
        
        # Monitoring configuration
        self.monitored_accounts: Set[str] = set()
        self.monitored_hashtags: Set[str] = set()
        self.protected_content: Set[str] = set()
        self.similarity_threshold = config.get('similarity_threshold', 0.85)
        
        # Federation settings
        self.enable_federation_monitoring = config.get('enable_federation_monitoring', True)
        self.max_federation_depth = config.get('max_federation_depth', 3)
        self.auto_discover_instances = config.get('auto_discover_instances', True)
        
        # Content analysis
        self.enable_content_warnings = config.get('enable_content_warnings', True)
        self.monitor_sensitive_content = config.get('monitor_sensitive_content', True)
        self.track_federation_spread = config.get('track_federation_spread', True)
        
        logger.info("Mastodon crawler initialized with ultra-advanced federation monitoring")

    async def authenticate(
        self,
        instance_url: str = None,
        access_token: str = None,
        client_id: str = None,
        client_secret: str = None
    ) -> bool:
        """
        Authenticate with Mastodon instance
        
        Args:
            instance_url: Mastodon instance URL
            access_token: OAuth access token
            client_id: Application client ID
            client_secret: Application client secret
            
        Returns:
            bool: Authentication success status
        """
        try:
            instance_url = instance_url or self.primary_instance
            
            if not instance_url.startswith('http'):
                instance_url = f"https://{instance_url}"
            
            self.base_url = instance_url
            self.api_base = f"{instance_url}/api/v1"
            self.api_v2_base = f"{instance_url}/api/v2"
            
            if access_token:
                # Direct token authentication
                self.access_token = access_token
                self.session.headers.update({
                    "Authorization": f"Bearer {access_token}"
                })
                
                # Verify token
                async with self.session.get(f"{self.api_base}/accounts/verify_credentials") as response:
                    if response.status == 200:
                        user_data = await response.json()
                        logger.info(f"Authenticated as {user_data.get('username')} on {instance_url}")
                        return True
                    else:
                        logger.error(f"Token verification failed: {response.status}")
                        return False
            
            elif client_id and client_secret:
                # OAuth flow authentication
                self.client_id = client_id
                self.client_secret = client_secret
                
                # This would require implementing full OAuth flow
                # For now, return False to indicate need for manual token
                logger.info("OAuth flow not implemented. Please provide access_token directly.")
                return False
            
            else:
                logger.error("No authentication credentials provided")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def register_application(self, instance_url: str, app_name: str = "IA-Influencer-Agent") -> Dict[str, str]:
        """
        Register application with Mastodon instance
        
        Args:
            instance_url: Mastodon instance URL
            app_name: Application name
            
        Returns:
            Dict[str, str]: Application credentials
        """
        try:
            if not instance_url.startswith('http'):
                instance_url = f"https://{instance_url}"
            
            app_data = {
                "client_name": app_name,
                "redirect_uris": "urn:ietf:wg:oauth:2.0:oob",
                "scopes": "read write follow push",
                "website": "https://github.com/IA-Influencer-Agent"
            }
            
            async with self.session.post(
                f"{instance_url}/api/v1/apps",
                json=app_data
            ) as response:
                if response.status == 200:
                    credentials = await response.json()
                    logger.info(f"Application registered on {instance_url}")
                    return {
                        "client_id": credentials.get("client_id"),
                        "client_secret": credentials.get("client_secret"),
                        "vapid_key": credentials.get("vapid_key")
                    }
                else:
                    logger.error(f"Application registration failed: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Application registration error: {str(e)}")
            return {}

    async def search_content(
        self,
        query: str = "",
        content_type: Optional[MastodonContentType] = None,
        instance_filter: Optional[List[str]] = None,
        language: Optional[str] = None,
        limit: int = 50,
        resolve: bool = False
    ) -> MastodonSearchResults:
        """
        Search Mastodon content across federated network
        
        Args:
            query: Search query
            content_type: Type of content to search
            instance_filter: Specific instances to search
            language: Language filter
            limit: Maximum results
            resolve: Whether to resolve remote content
            
        Returns:
            MastodonSearchResults: Comprehensive search results
        """
        await self.rate_limiter.acquire()
        
        try:
            # Check cache first
            cache_key = f"search_{hashlib.md5(f'{query}_{content_type}_{instance_filter}_{language}'.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return MastodonSearchResults(**cached_result)
            
            results = MastodonSearchResults(
                query=query,
                total_results=0,
                search_type="federated",
                filters_applied={
                    "content_type": content_type.value if content_type else None,
                    "instance_filter": instance_filter,
                    "language": language,
                    "resolve": resolve
                },
                search_timestamp=datetime.utcnow()
            )
            
            # Search primary instance
            primary_results = await self._search_instance(
                self.primary_instance, query, content_type, language, limit, resolve
            )
            
            results.accounts.extend(primary_results.get("accounts", []))
            results.statuses.extend(primary_results.get("statuses", []))
            results.hashtags.extend(primary_results.get("hashtags", []))
            
            # Search additional instances if federation monitoring is enabled
            if self.enable_federation_monitoring:
                instances_to_search = instance_filter or list(self.monitored_instances)
                
                for instance in instances_to_search:
                    if instance != self.primary_instance:
                        try:
                            instance_results = await self._search_instance(
                                instance, query, content_type, language, limit // len(instances_to_search), resolve
                            )
                            
                            results.accounts.extend(instance_results.get("accounts", []))
                            results.statuses.extend(instance_results.get("statuses", []))
                            results.hashtags.extend(instance_results.get("hashtags", []))
                            
                        except Exception as e:
                            logger.warning(f"Search failed on instance {instance}: {str(e)}")
                            continue
            
            # Process content for protection
            for status in results.statuses:
                status.similarity_score = await self._calculate_similarity(status)
                status.protection_status = await self._check_protection_status(status)
            
            results.total_results = len(results.accounts) + len(results.statuses) + len(results.hashtags)
            
            # Cache results
            await self.cache_manager.set(cache_key, results.dict())
            
            logger.info(f"Mastodon search completed: {results.total_results} total results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return MastodonSearchResults(
                query=query,
                total_results=0,
                search_type="error",
                filters_applied={},
                search_timestamp=datetime.utcnow()
            )

    async def _search_instance(
        self,
        instance_url: str,
        query: str,
        content_type: Optional[MastodonContentType],
        language: Optional[str],
        limit: int,
        resolve: bool
    ) -> Dict[str, List[Any]]:
        """Search specific Mastodon instance"""
        try:
            if not instance_url.startswith('http'):
                instance_url = f"https://{instance_url}"
            
            params = {
                "q": query,
                "limit": limit,
                "resolve": resolve
            }
            
            if content_type:
                params["type"] = content_type.value
            
            # Use v2 search API for better results
            search_url = f"{instance_url}/api/v2/search"
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse accounts
                    accounts = []
                    for account_data in data.get("accounts", []):
                        account = await self._parse_account_data(account_data, instance_url)
                        accounts.append(account)
                    
                    # Parse statuses
                    statuses = []
                    for status_data in data.get("statuses", []):
                        status = await self._parse_status_data(status_data, instance_url)
                        if not language or status.language == language:
                            statuses.append(status)
                    
                    # Parse hashtags
                    hashtags = []
                    for tag_data in data.get("hashtags", []):
                        tag = MastodonTag(
                            name=tag_data.get("name", ""),
                            url=tag_data.get("url", ""),
                            history=tag_data.get("history", [])
                        )
                        hashtags.append(tag)
                    
                    return {
                        "accounts": accounts,
                        "statuses": statuses,
                        "hashtags": hashtags
                    }
                else:
                    logger.warning(f"Search failed on {instance_url}: {response.status}")
                    return {"accounts": [], "statuses": [], "hashtags": []}
                    
        except Exception as e:
            logger.error(f"Instance search error on {instance_url}: {str(e)}")
            return {"accounts": [], "statuses": [], "hashtags": []}

    async def get_content_details(self, status_id: str, instance_url: str = None) -> Optional[MastodonStatus]:
        """
        Get detailed information about specific Mastodon status
        
        Args:
            status_id: Status ID
            instance_url: Instance URL (uses primary if not specified)
            
        Returns:
            Optional[MastodonStatus]: Detailed status information
        """
        await self.rate_limiter.acquire()
        
        try:
            instance_url = instance_url or self.primary_instance
            if not instance_url.startswith('http'):
                instance_url = f"https://{instance_url}"
            
            # Check cache first
            cache_key = f"status_{instance_url}_{status_id}"
            cached_content = await self.cache_manager.get(cache_key)
            if cached_content:
                return MastodonStatus(**cached_content)
            
            async with self.session.get(
                f"{instance_url}/api/v1/statuses/{status_id}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status = await self._parse_status_data(data, instance_url)
                    
                    # Enhanced analysis
                    status.similarity_score = await self._calculate_similarity(status)
                    status.protection_status = await self._check_protection_status(status)
                    
                    # Cache the result
                    await self.cache_manager.set(cache_key, status.dict())
                    
                    logger.info(f"Retrieved Mastodon status details: {status_id}")
                    return status
                else:
                    logger.warning(f"Status not found: {status_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting status details: {str(e)}")
            return None

    async def monitor_content(
        self,
        account_ids: List[str] = None,
        hashtags: List[str] = None,
        keywords: List[str] = None,
        instances: List[str] = None,
        check_interval: int = 300
    ) -> AsyncGenerator[MastodonStatus, None]:
        """
        Real-time content monitoring for Mastodon
        
        Args:
            account_ids: Account IDs to monitor
            hashtags: Hashtags to monitor
            keywords: Keywords to monitor
            instances: Instances to monitor
            check_interval: Check interval in seconds
            
        Yields:
            MastodonStatus: New statuses detected
        """
        account_ids = account_ids or []
        hashtags = hashtags or []
        keywords = keywords or []
        instances = instances or [self.primary_instance]
        
        self.monitored_accounts.update(account_ids)
        self.monitored_hashtags.update(hashtags)
        self.monitored_instances.update(instances)
        
        logger.info(f"Starting Mastodon monitoring for {len(account_ids)} accounts, {len(hashtags)} hashtags")
        
        last_check = datetime.utcnow()
        seen_statuses = set()
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                
                for instance in instances:
                    try:
                        # Monitor federated timeline
                        new_statuses = await self._get_federated_timeline(instance, last_check)
                        
                        for status in new_statuses:
                            if status.status_id not in seen_statuses:
                                # Apply monitoring filters
                                should_yield = False
                                
                                # Check accounts
                                if status.account.account_id in self.monitored_accounts:
                                    should_yield = True
                                
                                # Check hashtags
                                status_hashtags = {tag.name.lower() for tag in status.tags}
                                if any(hashtag.lower() in status_hashtags for hashtag in hashtags):
                                    should_yield = True
                                
                                # Check keywords
                                if any(keyword.lower() in status.content.lower() for keyword in keywords):
                                    should_yield = True
                                
                                if should_yield:
                                    # Enhanced monitoring analysis
                                    status.similarity_score = await self._calculate_similarity(status)
                                    status.protection_status = await self._check_protection_status(status)
                                    
                                    seen_statuses.add(status.status_id)
                                    
                                    logger.info(f"New monitored status: {status.status_id}")
                                    yield status
                        
                        # Monitor specific hashtags
                        for hashtag in hashtags:
                            hashtag_statuses = await self._get_hashtag_timeline(instance, hashtag, last_check)
                            
                            for status in hashtag_statuses:
                                if status.status_id not in seen_statuses:
                                    status.similarity_score = await self._calculate_similarity(status)
                                    status.protection_status = await self._check_protection_status(status)
                                    
                                    seen_statuses.add(status.status_id)
                                    yield status
                    
                    except Exception as e:
                        logger.error(f"Monitoring error on instance {instance}: {str(e)}")
                        continue
                
                last_check = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)

    async def _get_federated_timeline(
        self,
        instance_url: str,
        since: datetime,
        limit: int = 40
    ) -> List[MastodonStatus]:
        """Get federated timeline from instance"""
        try:
            if not instance_url.startswith('http'):
                instance_url = f"https://{instance_url}"
            
            params = {
                "limit": limit,
                "since_id": None  # Would need to track last seen ID
            }
            
            async with self.session.get(
                f"{instance_url}/api/v1/timelines/public",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    statuses = []
                    
                    for status_data in data:
                        status = await self._parse_status_data(status_data, instance_url)
                        if status.created_at >= since:
                            statuses.append(status)
                    
                    return statuses
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting federated timeline: {str(e)}")
            return []

    async def _get_hashtag_timeline(
        self,
        instance_url: str,
        hashtag: str,
        since: datetime,
        limit: int = 20
    ) -> List[MastodonStatus]:
        """Get hashtag timeline from instance"""
        try:
            if not instance_url.startswith('http'):
                instance_url = f"https://{instance_url}"
            
            params = {
                "limit": limit
            }
            
            async with self.session.get(
                f"{instance_url}/api/v1/timelines/tag/{hashtag}",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    statuses = []
                    
                    for status_data in data:
                        status = await self._parse_status_data(status_data, instance_url)
                        if status.created_at >= since:
                            statuses.append(status)
                    
                    return statuses
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting hashtag timeline: {str(e)}")
            return []

    async def detect_similarity(
        self,
        target_status: MastodonStatus,
        comparison_set: List[MastodonStatus],
        threshold: float = None
    ) -> List[Tuple[MastodonStatus, float]]:
        """
        Detect status similarity across federated network
        
        Args:
            target_status: Status to compare
            comparison_set: Statuses to compare against
            threshold: Similarity threshold
            
        Returns:
            List[Tuple[MastodonStatus, float]]: Similar statuses with scores
        """
        threshold = threshold or self.similarity_threshold
        similar_statuses = []
        
        try:
            target_features = await self._extract_status_features(target_status)
            
            for status in comparison_set:
                if status.status_id == target_status.status_id:
                    continue
                
                comp_features = await self._extract_status_features(status)
                similarity_score = await self._calculate_feature_similarity(
                    target_features, comp_features
                )
                
                if similarity_score >= threshold:
                    similar_statuses.append((status, similarity_score))
            
            similar_statuses.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Similarity detection: {len(similar_statuses)} matches found")
            return similar_statuses
            
        except Exception as e:
            logger.error(f"Similarity detection error: {str(e)}")
            return []

    async def _extract_status_features(self, status: MastodonStatus) -> Dict[str, Any]:
        """Extract features for similarity comparison"""
        features = {
            "content": status.content.lower(),
            "hashtags": set(tag.name.lower() for tag in status.tags),
            "mentions": set(mention.acct.lower() for mention in status.mentions),
            "media_count": len(status.media_attachments),
            "media_types": set(att.type for att in status.media_attachments),
            "language": status.language or "unknown",
            "visibility": status.visibility.value,
            "sensitive": status.sensitive,
            "has_spoiler": bool(status.spoiler_text),
            "has_poll": status.poll is not None,
            "is_reply": status.in_reply_to_id is not None,
            "is_boost": status.reblog is not None,
            "instance": status.instance_url,
            "local": status.account.local
        }
        return features

    async def _calculate_feature_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between status features"""
        try:
            scores = []
            
            # Content similarity
            content_sim = SequenceMatcher(
                None, features1.get("content", ""), features2.get("content", "")
            ).ratio()
            scores.append(content_sim * 0.4)  # 40% weight
            
            # Hashtags overlap
            hashtags1 = features1.get("hashtags", set())
            hashtags2 = features2.get("hashtags", set())
            if hashtags1 and hashtags2:
                hashtag_overlap = len(hashtags1.intersection(hashtags2)) / len(hashtags1.union(hashtags2))
                scores.append(hashtag_overlap * 0.25)  # 25% weight
            
            # Media similarity
            media_sim = 1.0 if features1.get("media_types") == features2.get("media_types") else 0.0
            scores.append(media_sim * 0.15)  # 15% weight
            
            # Structural similarity
            structure_features = ["visibility", "sensitive", "has_spoiler", "has_poll", "is_reply", "is_boost"]
            structure_matches = sum(1 for feat in structure_features if features1.get(feat) == features2.get(feat))
            structure_sim = structure_matches / len(structure_features)
            scores.append(structure_sim * 0.2)  # 20% weight
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Feature similarity calculation error: {str(e)}")
            return 0.0

    async def get_analytics(
        self,
        account_id: str,
        analysis_period: Tuple[datetime, datetime],
        instance_url: str = None
    ) -> MastodonAnalytics:
        """
        Generate comprehensive analytics for Mastodon account
        
        Args:
            account_id: Account ID to analyze
            analysis_period: Analysis time period
            instance_url: Instance URL
            
        Returns:
            MastodonAnalytics: Comprehensive analytics data
        """
        try:
            start_time, end_time = analysis_period
            instance_url = instance_url or self.primary_instance
            
            # Get account's statuses in the period
            account_statuses = await self._get_account_statuses_in_period(
                account_id, start_time, end_time, instance_url
            )
            
            if not account_statuses:
                return MastodonAnalytics(
                    account_id=account_id,
                    analysis_period=analysis_period,
                    total_statuses=0,
                    total_replies=0,
                    total_boosts=0,
                    total_favourites_received=0,
                    total_boosts_received=0,
                    average_favourites_per_status=0.0,
                    average_boosts_per_status=0.0,
                    most_active_hours=[],
                    most_used_hashtags=[],
                    most_mentioned_accounts=[],
                    language_distribution={},
                    visibility_distribution={},
                    media_usage_stats={},
                    engagement_rate=0.0,
                    reach_estimate=0,
                    federation_reach=0,
                    instances_reached=set(),
                    content_warnings_used=0,
                    sensitive_content_count=0,
                    similarity_violations=0,
                    protection_violations=0
                )
            
            # Calculate analytics
            total_statuses = len(account_statuses)
            total_replies = sum(1 for status in account_statuses if status.in_reply_to_id)
            total_boosts = sum(1 for status in account_statuses if status.reblog)
            
            total_favourites_received = sum(status.favourites_count for status in account_statuses)
            total_boosts_received = sum(status.reblogs_count for status in account_statuses)
            
            average_favourites_per_status = total_favourites_received / total_statuses if total_statuses > 0 else 0.0
            average_boosts_per_status = total_boosts_received / total_statuses if total_statuses > 0 else 0.0
            
            # Activity patterns
            activity_hours = [status.created_at.hour for status in account_statuses]
            hour_counts = {}
            for hour in activity_hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            most_active_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            most_active_hours = [hour[0] for hour in most_active_hours]
            
            # Hashtag analysis
            hashtag_counts = {}
            for status in account_statuses:
                for tag in status.tags:
                    hashtag_counts[tag.name] = hashtag_counts.get(tag.name, 0) + 1
            most_used_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            most_used_hashtags = [tag[0] for tag in most_used_hashtags]
            
            # Mention analysis
            mention_counts = {}
            for status in account_statuses:
                for mention in status.mentions:
                    mention_counts[mention.acct] = mention_counts.get(mention.acct, 0) + 1
            most_mentioned_accounts = sorted(mention_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            most_mentioned_accounts = [acct[0] for acct in most_mentioned_accounts]
            
            # Language distribution
            language_distribution = {}
            for status in account_statuses:
                lang = status.language or "unknown"
                language_distribution[lang] = language_distribution.get(lang, 0) + 1
            
            # Visibility distribution
            visibility_distribution = {}
            for status in account_statuses:
                vis = status.visibility.value
                visibility_distribution[vis] = visibility_distribution.get(vis, 0) + 1
            
            # Media usage
            media_usage_stats = {}
            for status in account_statuses:
                for attachment in status.media_attachments:
                    media_type = attachment.type
                    media_usage_stats[media_type] = media_usage_stats.get(media_type, 0) + 1
            
            # Federation analysis
            instances_reached = set()
            for status in account_statuses:
                for mention in status.mentions:
                    if "@" in mention.acct:
                        instance = mention.acct.split("@")[1]
                        instances_reached.add(instance)
            
            federation_reach = len(instances_reached)
            
            # Content warnings and sensitive content
            content_warnings_used = sum(1 for status in account_statuses if status.spoiler_text)
            sensitive_content_count = sum(1 for status in account_statuses if status.sensitive)
            
            # Protection metrics
            similarity_violations = sum(1 for status in account_statuses if (status.similarity_score or 0) > self.similarity_threshold)
            protection_violations = sum(1 for status in account_statuses if status.protection_status == "violation")
            
            # Engagement rate
            total_engagement = total_favourites_received + total_boosts_received
            engagement_rate = total_engagement / total_statuses if total_statuses > 0 else 0.0
            
            # Reach estimate (simplified)
            reach_estimate = total_engagement * 3  # Rough estimate
            
            analytics = MastodonAnalytics(
                account_id=account_id,
                analysis_period=analysis_period,
                total_statuses=total_statuses,
                total_replies=total_replies,
                total_boosts=total_boosts,
                total_favourites_received=total_favourites_received,
                total_boosts_received=total_boosts_received,
                average_favourites_per_status=average_favourites_per_status,
                average_boosts_per_status=average_boosts_per_status,
                most_active_hours=most_active_hours,
                most_used_hashtags=most_used_hashtags,
                most_mentioned_accounts=most_mentioned_accounts,
                language_distribution=language_distribution,
                visibility_distribution=visibility_distribution,
                media_usage_stats=media_usage_stats,
                engagement_rate=engagement_rate,
                reach_estimate=reach_estimate,
                federation_reach=federation_reach,
                instances_reached=instances_reached,
                content_warnings_used=content_warnings_used,
                sensitive_content_count=sensitive_content_count,
                similarity_violations=similarity_violations,
                protection_violations=protection_violations
            )
            
            logger.info(f"Analytics generated for account {account_id}: {total_statuses} statuses analyzed")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics generation error: {str(e)}")
            return MastodonAnalytics(
                account_id=account_id,
                analysis_period=analysis_period,
                total_statuses=0,
                total_replies=0,
                total_boosts=0,
                total_favourites_received=0,
                total_boosts_received=0,
                average_favourites_per_status=0.0,
                average_boosts_per_status=0.0,
                most_active_hours=[],
                most_used_hashtags=[],
                most_mentioned_accounts=[],
                language_distribution={},
                visibility_distribution={},
                media_usage_stats={},
                engagement_rate=0.0,
                reach_estimate=0,
                federation_reach=0,
                instances_reached=set(),
                content_warnings_used=0,
                sensitive_content_count=0,
                similarity_violations=0,
                protection_violations=0
            )

    async def _parse_account_data(self, data: Dict[str, Any], instance_url: str) -> MastodonAccount:
        """Parse account data from API response"""
        try:
            # Parse custom emojis
            emojis = []
            for emoji_data in data.get("emojis", []):
                emoji = MastodonEmoji(
                    shortcode=emoji_data.get("shortcode", ""),
                    url=emoji_data.get("url", ""),
                    static_url=emoji_data.get("static_url", ""),
                    visible_in_picker=emoji_data.get("visible_in_picker", True),
                    category=emoji_data.get("category")
                )
                emojis.append(emoji)
            
            account = MastodonAccount(
                account_id=str(data.get("id", "")),
                username=data.get("username", ""),
                acct=data.get("acct", ""),
                display_name=data.get("display_name", ""),
                locked=data.get("locked", False),
                bot=data.get("bot", False),
                discoverable=data.get("discoverable"),
                group=data.get("group", False),
                created_at=datetime.fromisoformat(
                    data.get("created_at", datetime.utcnow().isoformat())
                ),
                note=data.get("note", ""),
                url=data.get("url", ""),
                avatar=data.get("avatar", ""),
                avatar_static=data.get("avatar_static", ""),
                header=data.get("header", ""),
                header_static=data.get("header_static", ""),
                followers_count=data.get("followers_count", 0),
                following_count=data.get("following_count", 0),
                statuses_count=data.get("statuses_count", 0),
                last_status_at=datetime.fromisoformat(
                    data.get("last_status_at", datetime.utcnow().isoformat())
                ) if data.get("last_status_at") else None,
                emojis=emojis,
                fields=data.get("fields", []),
                suspended=data.get("suspended", False),
                limited=data.get("limited", False),
                instance_url=instance_url,
                local="@" not in data.get("acct", "")
            )
            
            return account
            
        except Exception as e:
            logger.error(f"Error parsing account data: {str(e)}")
            raise

    async def _parse_status_data(self, data: Dict[str, Any], instance_url: str) -> MastodonStatus:
        """Parse status data from API response"""
        try:
            # Parse account
            account = await self._parse_account_data(data.get("account", {}), instance_url)
            
            # Parse media attachments
            media_attachments = []
            for media_data in data.get("media_attachments", []):
                attachment = MastodonAttachment(
                    attachment_id=str(media_data.get("id", "")),
                    type=media_data.get("type", "unknown"),
                    url=media_data.get("url", ""),
                    preview_url=media_data.get("preview_url"),
                    remote_url=media_data.get("remote_url"),
                    text_url=media_data.get("text_url"),
                    meta=media_data.get("meta", {}),
                    description=media_data.get("description"),
                    blurhash=media_data.get("blurhash")
                )
                media_attachments.append(attachment)
            
            # Parse mentions
            mentions = []
            for mention_data in data.get("mentions", []):
                mention = MastodonMention(
                    mention_id=str(mention_data.get("id", "")),
                    username=mention_data.get("username", ""),
                    url=mention_data.get("url", ""),
                    acct=mention_data.get("acct", "")
                )
                mentions.append(mention)
            
            # Parse tags
            tags = []
            for tag_data in data.get("tags", []):
                tag = MastodonTag(
                    name=tag_data.get("name", ""),
                    url=tag_data.get("url", ""),
                    history=tag_data.get("history", [])
                )
                tags.append(tag)
            
            # Parse emojis
            emojis = []
            for emoji_data in data.get("emojis", []):
                emoji = MastodonEmoji(
                    shortcode=emoji_data.get("shortcode", ""),
                    url=emoji_data.get("url", ""),
                    static_url=emoji_data.get("static_url", ""),
                    visible_in_picker=emoji_data.get("visible_in_picker", True)
                )
                emojis.append(emoji)
            
            # Parse poll if present
            poll = None
            poll_data = data.get("poll")
            if poll_data:
                poll = MastodonPoll(
                    poll_id=str(poll_data.get("id", "")),
                    expires_at=datetime.fromisoformat(
                        poll_data.get("expires_at", datetime.utcnow().isoformat())
                    ) if poll_data.get("expires_at") else None,
                    expired=poll_data.get("expired", False),
                    multiple=poll_data.get("multiple", False),
                    votes_count=poll_data.get("votes_count", 0),
                    voters_count=poll_data.get("voters_count"),
                    options=poll_data.get("options", []),
                    emojis=emojis
                )
            
            # Parse reblog if present
            reblog = None
            reblog_data = data.get("reblog")
            if reblog_data:
                reblog = await self._parse_status_data(reblog_data, instance_url)
            
            # Create status object
            status = MastodonStatus(
                status_id=str(data.get("id", "")),
                uri=data.get("uri", ""),
                created_at=datetime.fromisoformat(
                    data.get("created_at", datetime.utcnow().isoformat())
                ),
                account=account,
                content=data.get("content", ""),
                visibility=MastodonVisibility(data.get("visibility", "public")),
                sensitive=data.get("sensitive", False),
                spoiler_text=data.get("spoiler_text", ""),
                media_attachments=media_attachments,
                mentions=mentions,
                tags=tags,
                emojis=emojis,
                reblogs_count=data.get("reblogs_count", 0),
                favourites_count=data.get("favourites_count", 0),
                replies_count=data.get("replies_count", 0),
                url=data.get("url"),
                in_reply_to_id=data.get("in_reply_to_id"),
                in_reply_to_account_id=data.get("in_reply_to_account_id"),
                reblog=reblog,
                poll=poll,
                language=data.get("language"),
                text=data.get("text"),
                edited_at=datetime.fromisoformat(
                    data.get("edited_at", datetime.utcnow().isoformat())
                ) if data.get("edited_at") else None,
                instance_url=instance_url
            )
            
            return status
            
        except Exception as e:
            logger.error(f"Error parsing status data: {str(e)}")
            raise

    async def _calculate_similarity(self, status: MastodonStatus) -> float:
        """Calculate similarity score against protected content"""
        # Simplified similarity calculation
        return 0.0

    async def _check_protection_status(self, status: MastodonStatus) -> str:
        """Check protection status of status"""
        if status.status_id in self.protected_content:
            return "protected"
        return "unprotected"

    async def _get_account_statuses_in_period(
        self,
        account_id: str,
        start_time: datetime,
        end_time: datetime,
        instance_url: str
    ) -> List[MastodonStatus]:
        """Get account's statuses in a specific time period"""
        try:
            if not instance_url.startswith('http'):
                instance_url = f"https://{instance_url}"
            
            params = {
                "limit": 40,
                "exclude_replies": False,
                "exclude_reblogs": False
            }
            
            async with self.session.get(
                f"{instance_url}/api/v1/accounts/{account_id}/statuses",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    statuses = []
                    
                    for status_data in data:
                        status = await self._parse_status_data(status_data, instance_url)
                        if start_time <= status.created_at <= end_time:
                            statuses.append(status)
                    
                    return statuses
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting account statuses: {str(e)}")
            return []

    async def _handle_rate_limit(self, response: aiohttp.ClientResponse) -> bool:
        """Handle rate limiting responses"""
        if response.status == 429:
            retry_after = int(response.headers.get('X-RateLimit-Reset', 60))
            logger.warning(f"Rate limited. Waiting {retry_after} seconds")
            await asyncio.sleep(retry_after)
            return True
        return False

    async def discover_instances(self, limit: int = 100) -> List[MastodonInstance]:
        """Discover active Mastodon instances"""
        try:
            # Use instance directory services
            directory_urls = [
                "https://instances.social/api/1.0/instances/list",
                "https://mastodon.help/instances.json"
            ]
            
            discovered_instances = []
            
            for directory_url in directory_urls:
                try:
                    async with self.session.get(directory_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            instances_data = data.get("instances", data)
                            for instance_data in instances_data[:limit]:
                                instance = await self._parse_instance_data(instance_data)
                                discovered_instances.append(instance)
                                
                except Exception as e:
                    logger.warning(f"Error fetching from directory {directory_url}: {str(e)}")
                    continue
            
            return discovered_instances[:limit]
            
        except Exception as e:
            logger.error(f"Instance discovery error: {str(e)}")
            return []

    async def _parse_instance_data(self, data: Dict[str, Any]) -> MastodonInstance:
        """Parse instance data"""
        return MastodonInstance(
            uri=data.get("name", ""),
            title=data.get("title", ""),
            short_description=data.get("short_description", ""),
            description=data.get("description", ""),
            email=data.get("email", ""),
            version=data.get("version", ""),
            stats=data.get("stats", {}),
            thumbnail=data.get("thumbnail"),
            languages=data.get("languages", []),
            registrations=data.get("registrations", True),
            approval_required=data.get("approval_required", False),
            max_toot_chars=data.get("max_toot_chars", 500)
        )

    async def close(self):
        """Close crawler and cleanup resources"""
        try:
            await self.cache_manager.close()
            await super().close()
            logger.info("Mastodon crawler closed successfully")
        except Exception as e:
            logger.error(f"Error closing crawler: {str(e)}")
