"""
Mastodon Crawling Engine
========================

Advanced Mastodon crawler for decentralized social content discovery and analytics.
Handles toot metadata extraction, instance analysis, and federation monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import hashlib
import json
from urllib.parse import urljoin, urlparse, parse_qs

import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..models.content_models import SocialContent, UserContent
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class MastodonToot:
    """Mastodon toot data structure"""
    id: str
    uri: str
    url: str
    account_id: str
    account_username: str
    account_display_name: str
    content: str
    created_at: datetime
    edited_at: Optional[datetime]
    in_reply_to_id: Optional[str]
    in_reply_to_account_id: Optional[str]
    reblog: Optional[str]
    sensitive: bool
    spoiler_text: str
    visibility: str  # public, unlisted, private, direct
    language: Optional[str]
    replies_count: int
    reblogs_count: int
    favourites_count: int
    media_attachments: List[Dict[str, Any]]
    mentions: List[Dict[str, str]]
    tags: List[str]
    poll: Optional[Dict[str, Any]]
    instance_url: str


@dataclass
class MastodonAccount:
    """Mastodon account data structure"""
    id: str
    username: str
    acct: str
    display_name: str
    note: str
    url: str
    avatar: str
    avatar_static: str
    header: str
    header_static: str
    locked: bool
    bot: bool
    discoverable: bool
    group: bool
    created_at: datetime
    last_status_at: Optional[datetime]
    statuses_count: int
    followers_count: int
    following_count: int
    fields: List[Dict[str, str]]
    emojis: List[Dict[str, Any]]
    instance_url: str


@dataclass
class MastodonInstance:
    """Mastodon instance data structure"""
    uri: str
    title: str
    short_description: str
    description: str
    email: str
    version: str
    languages: List[str]
    registrations: bool
    approval_required: bool
    invite_required: bool
    configuration: Dict[str, Any]
    contact_account: Optional[Dict[str, Any]]
    rules: List[Dict[str, str]]
    stats: Dict[str, int]


class MastodonCrawlerEngine(BaseCrawlerEngine):
    """
    Professional Mastodon crawler engine for decentralized social content analysis.
    
    Features:
    - Multi-instance federation support
    - Toot discovery and analytics
    - Account relationship mapping
    - Instance health monitoring
    - Content moderation tracking
    - Cross-instance trend analysis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Mastodon crawler engine"""
        super().__init__(platform="mastodon", config=config)
        
        # Rate limiting (varies by instance)
        self.rate_limiter = RateLimiter(
            requests_per_minute=60,
            requests_per_hour=3600
        )
        
        # Cache configuration
        self.cache_manager = CacheManager(
            cache_ttl=timedelta(minutes=10),
            max_cache_size=10000
        )
        
        # Default instances to monitor
        self.default_instances = [
            "mastodon.social",
            "mastodon.world",
            "fosstodon.org",
            "mas.to",
            "mstdn.social"
        ]
        
        # Configure instances
        self.instances = self.config.get("instances", self.default_instances)
        
        # Session management per instance
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        self.access_tokens: Dict[str, str] = {}
        
        logger.info(f"Mastodon crawler engine initialized for {len(self.instances)} instances")
    
    async def initialize(self) -> None:
        """Initialize the crawler engine"""
        try:
            await self._create_sessions()
            logger.info("Mastodon engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Mastodon engine: {e}")
            raise CrawlerError(f"Initialization failed: {e}")
    
    async def _create_sessions(self) -> None:
        """Create HTTP sessions for each instance"""
        for instance in self.instances:
            headers = {
                'User-Agent': 'IA-Influencer-Agent/1.0 (Mastodon Bot)',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Add authorization header if token available
            if instance in self.access_tokens:
                headers['Authorization'] = f'Bearer {self.access_tokens[instance]}'
            
            timeout = aiohttp.ClientTimeout(total=30)
            self.sessions[instance] = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=aiohttp.TCPConnector(limit=50)
            )
    
    async def get_instance_info(self, instance_url: str) -> Optional[MastodonInstance]:
        """
        Get information about a Mastodon instance
        
        Args:
            instance_url: Instance URL (e.g., "mastodon.social")
            
        Returns:
            Instance information or None if not accessible
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"instance_info:{instance_url}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get or create session for this instance
            if instance_url not in self.sessions:
                await self._create_session_for_instance(instance_url)
            
            session = self.sessions[instance_url]
            api_url = f"https://{instance_url}/api/v1/instance"
            
            async with session.get(api_url) as response:
                if response.status == 429:
                    raise RateLimitError(f"Rate limit exceeded for {instance_url}")
                elif response.status != 200:
                    logger.warning(f"Failed to get instance info for {instance_url}: {response.status}")
                    return None
                
                data = await response.json()
                instance = self._parse_instance_data(data, instance_url)
                
                # Cache result
                await self.cache_manager.set(cache_key, instance)
                
                return instance
                
        except Exception as e:
            logger.error(f"Error getting instance info for {instance_url}: {e}")
            return None
    
    async def _create_session_for_instance(self, instance_url: str) -> None:
        """Create session for a specific instance"""
        headers = {
            'User-Agent': 'IA-Influencer-Agent/1.0 (Mastodon Bot)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.sessions[instance_url] = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=50)
        )
    
    async def get_public_timeline(
        self,
        instance_url: str,
        local: bool = False,
        only_media: bool = False,
        limit: int = 40
    ) -> List[MastodonToot]:
        """
        Get public timeline from an instance
        
        Args:
            instance_url: Instance to query
            local: Only local toots
            only_media: Only toots with media
            limit: Number of toots to return
            
        Returns:
            List of public toots
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"public_timeline:{instance_url}:{local}:{only_media}:{limit}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get or create session
            if instance_url not in self.sessions:
                await self._create_session_for_instance(instance_url)
            
            session = self.sessions[instance_url]
            api_url = f"https://{instance_url}/api/v1/timelines/public"
            
            params = {
                'limit': min(limit, 80),
                'local': str(local).lower(),
                'only_media': str(only_media).lower()
            }
            
            async with session.get(api_url, params=params) as response:
                if response.status == 429:
                    raise RateLimitError(f"Rate limit exceeded for {instance_url}")
                elif response.status != 200:
                    raise CrawlerError(f"Timeline request failed: {response.status}")
                
                data = await response.json()
                toots = []
                
                for toot_data in data:
                    toot = self._parse_toot_data(toot_data, instance_url)
                    toots.append(toot)
                
                # Cache results
                await self.cache_manager.set(cache_key, toots)
                
                logger.info(f"Retrieved {len(toots)} toots from {instance_url} public timeline")
                return toots
                
        except Exception as e:
            logger.error(f"Error getting public timeline from {instance_url}: {e}")
            raise CrawlerError(f"Public timeline retrieval failed: {e}")
    
    async def get_hashtag_timeline(
        self,
        instance_url: str,
        hashtag: str,
        local: bool = False,
        limit: int = 40
    ) -> List[MastodonToot]:
        """
        Get timeline for a specific hashtag
        
        Args:
            instance_url: Instance to query
            hashtag: Hashtag to search (without #)
            local: Only local toots
            limit: Number of toots to return
            
        Returns:
            List of toots with the hashtag
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"hashtag_timeline:{instance_url}:{hashtag}:{local}:{limit}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get or create session
            if instance_url not in self.sessions:
                await self._create_session_for_instance(instance_url)
            
            session = self.sessions[instance_url]
            api_url = f"https://{instance_url}/api/v1/timelines/tag/{hashtag}"
            
            params = {
                'limit': min(limit, 80),
                'local': str(local).lower()
            }
            
            async with session.get(api_url, params=params) as response:
                if response.status == 429:
                    raise RateLimitError(f"Rate limit exceeded for {instance_url}")
                elif response.status != 200:
                    raise CrawlerError(f"Hashtag timeline request failed: {response.status}")
                
                data = await response.json()
                toots = []
                
                for toot_data in data:
                    toot = self._parse_toot_data(toot_data, instance_url)
                    toots.append(toot)
                
                # Cache results
                await self.cache_manager.set(cache_key, toots)
                
                logger.info(f"Retrieved {len(toots)} toots for hashtag #{hashtag} from {instance_url}")
                return toots
                
        except Exception as e:
            logger.error(f"Error getting hashtag timeline: {e}")
            raise CrawlerError(f"Hashtag timeline retrieval failed: {e}")
    
    async def get_account_info(
        self,
        instance_url: str,
        account_id: str
    ) -> Optional[MastodonAccount]:
        """
        Get account information
        
        Args:
            instance_url: Instance where account exists
            account_id: Account ID
            
        Returns:
            Account information or None if not found
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"account_info:{instance_url}:{account_id}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get or create session
            if instance_url not in self.sessions:
                await self._create_session_for_instance(instance_url)
            
            session = self.sessions[instance_url]
            api_url = f"https://{instance_url}/api/v1/accounts/{account_id}"
            
            async with session.get(api_url) as response:
                if response.status == 404:
                    raise ContentNotFoundError(f"Account not found: {account_id}")
                elif response.status == 429:
                    raise RateLimitError(f"Rate limit exceeded for {instance_url}")
                elif response.status != 200:
                    raise CrawlerError(f"Account request failed: {response.status}")
                
                data = await response.json()
                account = self._parse_account_data(data, instance_url)
                
                # Cache result
                await self.cache_manager.set(cache_key, account)
                
                return account
                
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise CrawlerError(f"Account info retrieval failed: {e}")
    
    async def search_content(
        self,
        instance_url: str,
        query: str,
        type_filter: str = "statuses",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for content across Mastodon
        
        Args:
            instance_url: Instance to search on
            query: Search query
            type_filter: Type to search (accounts, hashtags, statuses)
            limit: Number of results
            
        Returns:
            List of search results
        """
        try:
            await self.rate_limiter.acquire()
            
            # Check cache
            cache_key = f"search:{instance_url}:{hashlib.md5(f'{query}:{type_filter}:{limit}'.encode()).hexdigest()}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get or create session
            if instance_url not in self.sessions:
                await self._create_session_for_instance(instance_url)
            
            session = self.sessions[instance_url]
            api_url = f"https://{instance_url}/api/v2/search"
            
            params = {
                'q': query,
                'type': type_filter,
                'limit': min(limit, 40),
                'resolve': 'true'
            }
            
            async with session.get(api_url, params=params) as response:
                if response.status == 429:
                    raise RateLimitError(f"Rate limit exceeded for {instance_url}")
                elif response.status != 200:
                    raise CrawlerError(f"Search request failed: {response.status}")
                
                data = await response.json()
                results = []
                
                # Parse results based on type
                if type_filter == "statuses" and "statuses" in data:
                    for toot_data in data["statuses"]:
                        toot = self._parse_toot_data(toot_data, instance_url)
                        results.append({"type": "toot", "data": toot})
                
                elif type_filter == "accounts" and "accounts" in data:
                    for account_data in data["accounts"]:
                        account = self._parse_account_data(account_data, instance_url)
                        results.append({"type": "account", "data": account})
                
                elif type_filter == "hashtags" and "hashtags" in data:
                    for hashtag_data in data["hashtags"]:
                        results.append({"type": "hashtag", "data": hashtag_data})
                
                # Cache results
                await self.cache_manager.set(cache_key, results)
                
                logger.info(f"Found {len(results)} search results for '{query}' on {instance_url}")
                return results
                
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            raise CrawlerError(f"Content search failed: {e}")
    
    def _parse_toot_data(self, toot_data: Dict[str, Any], instance_url: str) -> MastodonToot:
        """Parse toot data from API response"""
        try:
            # Parse media attachments
            media_attachments = []
            for media in toot_data.get("media_attachments", []):
                media_attachments.append({
                    "id": media.get("id"),
                    "type": media.get("type"),
                    "url": media.get("url"),
                    "preview_url": media.get("preview_url"),
                    "description": media.get("description")
                })
            
            # Parse mentions
            mentions = []
            for mention in toot_data.get("mentions", []):
                mentions.append({
                    "id": mention.get("id"),
                    "username": mention.get("username"),
                    "acct": mention.get("acct"),
                    "url": mention.get("url")
                })
            
            # Parse tags
            tags = [tag.get("name", "") for tag in toot_data.get("tags", [])]
            
            return MastodonToot(
                id=toot_data.get("id", ""),
                uri=toot_data.get("uri", ""),
                url=toot_data.get("url", ""),
                account_id=toot_data.get("account", {}).get("id", ""),
                account_username=toot_data.get("account", {}).get("username", ""),
                account_display_name=toot_data.get("account", {}).get("display_name", ""),
                content=toot_data.get("content", ""),
                created_at=datetime.fromisoformat(toot_data.get("created_at", "").replace("Z", "+00:00")),
                edited_at=datetime.fromisoformat(toot_data.get("edited_at", "").replace("Z", "+00:00")) if toot_data.get("edited_at") else None,
                in_reply_to_id=toot_data.get("in_reply_to_id"),
                in_reply_to_account_id=toot_data.get("in_reply_to_account_id"),
                reblog=toot_data.get("reblog", {}).get("id") if toot_data.get("reblog") else None,
                sensitive=toot_data.get("sensitive", False),
                spoiler_text=toot_data.get("spoiler_text", ""),
                visibility=toot_data.get("visibility", "public"),
                language=toot_data.get("language"),
                replies_count=toot_data.get("replies_count", 0),
                reblogs_count=toot_data.get("reblogs_count", 0),
                favourites_count=toot_data.get("favourites_count", 0),
                media_attachments=media_attachments,
                mentions=mentions,
                tags=tags,
                poll=toot_data.get("poll"),
                instance_url=instance_url
            )
        except Exception as e:
            logger.error(f"Error parsing toot data: {e}")
            raise CrawlerError(f"Toot data parsing failed: {e}")
    
    def _parse_account_data(self, account_data: Dict[str, Any], instance_url: str) -> MastodonAccount:
        """Parse account data from API response"""
        try:
            # Parse custom fields
            fields = []
            for field in account_data.get("fields", []):
                fields.append({
                    "name": field.get("name", ""),
                    "value": field.get("value", ""),
                    "verified_at": field.get("verified_at")
                })
            
            return MastodonAccount(
                id=account_data.get("id", ""),
                username=account_data.get("username", ""),
                acct=account_data.get("acct", ""),
                display_name=account_data.get("display_name", ""),
                note=account_data.get("note", ""),
                url=account_data.get("url", ""),
                avatar=account_data.get("avatar", ""),
                avatar_static=account_data.get("avatar_static", ""),
                header=account_data.get("header", ""),
                header_static=account_data.get("header_static", ""),
                locked=account_data.get("locked", False),
                bot=account_data.get("bot", False),
                discoverable=account_data.get("discoverable", True),
                group=account_data.get("group", False),
                created_at=datetime.fromisoformat(account_data.get("created_at", "").replace("Z", "+00:00")),
                last_status_at=datetime.fromisoformat(account_data.get("last_status_at", "").replace("Z", "+00:00")) if account_data.get("last_status_at") else None,
                statuses_count=account_data.get("statuses_count", 0),
                followers_count=account_data.get("followers_count", 0),
                following_count=account_data.get("following_count", 0),
                fields=fields,
                emojis=account_data.get("emojis", []),
                instance_url=instance_url
            )
        except Exception as e:
            logger.error(f"Error parsing account data: {e}")
            raise CrawlerError(f"Account data parsing failed: {e}")
    
    def _parse_instance_data(self, instance_data: Dict[str, Any], instance_url: str) -> MastodonInstance:
        """Parse instance data from API response"""
        try:
            return MastodonInstance(
                uri=instance_data.get("uri", instance_url),
                title=instance_data.get("title", ""),
                short_description=instance_data.get("short_description", ""),
                description=instance_data.get("description", ""),
                email=instance_data.get("email", ""),
                version=instance_data.get("version", ""),
                languages=instance_data.get("languages", []),
                registrations=instance_data.get("registrations", False),
                approval_required=instance_data.get("approval_required", True),
                invite_required=instance_data.get("invite_required", False),
                configuration=instance_data.get("configuration", {}),
                contact_account=instance_data.get("contact_account"),
                rules=instance_data.get("rules", []),
                stats=instance_data.get("stats", {})
            )
        except Exception as e:
            logger.error(f"Error parsing instance data: {e}")
            raise CrawlerError(f"Instance data parsing failed: {e}")
    
    async def analyze_federation_network(self) -> Dict[str, Any]:
        """
        Analyze the federation network and instance relationships
        
        Returns:
            Federation network analysis
        """
        try:
            network_analysis = {
                'instances_analyzed': len(self.instances),
                'total_users': 0,
                'total_statuses': 0,
                'instance_details': [],
                'federation_health': {},
                'analysis_date': datetime.utcnow().isoformat()
            }
            
            for instance_url in self.instances:
                instance_info = await self.get_instance_info(instance_url)
                if instance_info:
                    instance_stats = {
                        'url': instance_url,
                        'title': instance_info.title,
                        'version': instance_info.version,
                        'registrations_open': instance_info.registrations,
                        'user_count': instance_info.stats.get('user_count', 0),
                        'status_count': instance_info.stats.get('status_count', 0),
                        'domain_count': instance_info.stats.get('domain_count', 0)
                    }
                    
                    network_analysis['instance_details'].append(instance_stats)
                    network_analysis['total_users'] += instance_stats['user_count']
                    network_analysis['total_statuses'] += instance_stats['status_count']
            
            logger.info(f"Federation network analysis completed for {len(self.instances)} instances")
            return network_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing federation network: {e}")
            raise CrawlerError(f"Federation network analysis failed: {e}")
    
    async def monitor_trending_hashtags(self) -> Dict[str, List[str]]:
        """
        Monitor trending hashtags across instances
        
        Returns:
            Trending hashtags by instance
        """
        try:
            trending_data = {}
            
            for instance_url in self.instances:
                try:
                    # Get or create session
                    if instance_url not in self.sessions:
                        await self._create_session_for_instance(instance_url)
                    
                    session = self.sessions[instance_url]
                    api_url = f"https://{instance_url}/api/v1/trends/tags"
                    
                    async with session.get(api_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            trending_tags = [tag.get("name", "") for tag in data]
                            trending_data[instance_url] = trending_tags[:10]  # Top 10
                        else:
                            trending_data[instance_url] = []
                            
                except Exception as e:
                    logger.warning(f"Failed to get trending hashtags for {instance_url}: {e}")
                    trending_data[instance_url] = []
            
            logger.info(f"Trending hashtags monitoring completed for {len(self.instances)} instances")
            return trending_data
            
        except Exception as e:
            logger.error(f"Error monitoring trending hashtags: {e}")
            raise CrawlerError(f"Trending hashtags monitoring failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up resources"""
        try:
            for session in self.sessions.values():
                await session.close()
            await super().cleanup()
            logger.info("Mastodon engine cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __str__(self) -> str:
        return f"MastodonCrawlerEngine(platform=mastodon, instances={len(self.instances)})"
