"""Discord Crawler Implementation
==============================

Advanced Discord server and community content monitoring crawler.
Implements comprehensive community analysis and user engagement tracking.

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
import discord
from discord.ext import commands
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class DiscordUser:
    """Discord user information"""    user_id: str
    username: str
    discriminator: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    banner_url: Optional[str]
    accent_color: Optional[int]
    bot: bool
    system: bool
    verified: bool
    email: Optional[str]
    locale: Optional[str]
    mfa_enabled: bool
    premium_type: Optional[int]
    public_flags: int
    flags: int
    created_at: datetime
    joined_at: Optional[datetime]
    bio: Optional[str]
    pronouns: Optional[str]
    status: str  # online, idle, dnd, offline
    activity: Optional[Dict[str, Any]]
    roles: List[str]
    permissions: List[str]
    badges: List[str]
    nitro_since: Optional[datetime]
    mutual_guilds: List[str]
    is_friend: bool
    is_blocked: bool
    message_count: int
    reaction_count: int
    voice_time_minutes: int


@dataclass
class DiscordMessage:
    """Discord message information"""    message_id: str
    channel_id: str
    guild_id: Optional[str]
    author_id: str
    author_username: str
    author_display_name: str
    content: str
    clean_content: str
    created_at: datetime
    edited_at: Optional[datetime]
    tts: bool
    mention_everyone: bool
    mentions: List[Dict[str, Any]]
    mention_roles: List[str]
    mention_channels: List[str]
    attachments: List[Dict[str, Any]]
    embeds: List[Dict[str, Any]]
    reactions: List[Dict[str, Any]]
    pinned: bool
    webhook_id: Optional[str]
    message_type: str
    activity: Optional[Dict[str, Any]]
    application: Optional[Dict[str, Any]]
    message_reference: Optional[Dict[str, Any]]
    flags: int
    stickers: List[Dict[str, Any]]
    referenced_message: Optional[str]
    interaction: Optional[Dict[str, Any]]
    thread: Optional[Dict[str, Any]]
    components: List[Dict[str, Any]]
    sentiment_score: Optional[float]
    toxicity_score: Optional[float]
    language: Optional[str]


@dataclass
class DiscordChannel:
    """Discord channel information"""    channel_id: str
    guild_id: Optional[str]
    name: str
    topic: Optional[str]
    position: int
    type: int  # 0=text, 1=dm, 2=voice, etc.
    nsfw: bool
    last_message_id: Optional[str]
    bitrate: Optional[int]
    user_limit: Optional[int]
    rate_limit_per_user: int
    recipients: List[Dict[str, Any]]
    icon: Optional[str]
    owner_id: Optional[str]
    application_id: Optional[str]
    parent_id: Optional[str]
    last_pin_timestamp: Optional[datetime]
    rtc_region: Optional[str]
    video_quality_mode: Optional[int]
    message_count: Optional[int]
    member_count: Optional[int]
    thread_metadata: Optional[Dict[str, Any]]
    member: Optional[Dict[str, Any]]
    default_auto_archive_duration: Optional[int]
    permissions: Optional[str]
    flags: int
    created_at: datetime
    category_name: Optional[str]
    overwrites: List[Dict[str, Any]]
    message_history: List[DiscordMessage]
    active_threads: List[str]
    archived_threads: List[str]


@dataclass
class DiscordGuild:
    """Discord guild/server information"""    guild_id: str
    name: str
    icon: Optional[str]
    icon_hash: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    owner: bool
    owner_id: str
    permissions: Optional[str]
    region: Optional[str]
    afk_channel_id: Optional[str]
    afk_timeout: int
    widget_enabled: Optional[bool]
    widget_channel_id: Optional[str]
    verification_level: int
    default_message_notifications: int
    explicit_content_filter: int
    roles: List[Dict[str, Any]]
    emojis: List[Dict[str, Any]]
    features: List[str]
    mfa_level: int
    application_id: Optional[str]
    system_channel_id: Optional[str]
    system_channel_flags: int
    rules_channel_id: Optional[str]
    max_presences: Optional[int]
    max_members: Optional[int]
    vanity_url_code: Optional[str]
    description: Optional[str]
    banner: Optional[str]
    premium_tier: int
    premium_subscription_count: Optional[int]
    preferred_locale: str
    public_updates_channel_id: Optional[str]
    max_video_channel_users: Optional[int]
    approximate_member_count: Optional[int]
    approximate_presence_count: Optional[int]
    welcome_screen: Optional[Dict[str, Any]]
    nsfw_level: int
    stickers: List[Dict[str, Any]]
    premium_progress_bar_enabled: bool
    created_at: datetime
    member_count: int
    online_count: int
    boost_count: int
    boost_level: int
    channels: List[DiscordChannel]
    categories: List[Dict[str, Any]]
    voice_channels: List[Dict[str, Any]]
    threads: List[Dict[str, Any]]
    scheduled_events: List[Dict[str, Any]]


@dataclass
class DiscordRole:
    """Discord role information"""    role_id: str
    guild_id: str
    name: str
    color: int
    hoist: bool
    icon: Optional[str]
    unicode_emoji: Optional[str]
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: Optional[Dict[str, Any]]
    flags: int
    created_at: datetime
    member_count: int
    members: List[str]


class DiscordCrawler(PlatformCrawler):
    """    Advanced Discord crawler for community content monitoring and analysis.
    
    Features:
    - Server/guild discovery and analysis
    - Channel content monitoring
    - User activity tracking
    - Message sentiment analysis
    - Community engagement metrics
    - Moderation log tracking
    - Voice channel activity monitoring
    - Event and announcement tracking
    - Bot interaction analysis
    - Thread and forum monitoring
    """    
    def __init__(self, config: CrawlerConfig, vector_matcher=None, bot_token: str = None):
        super().__init__(config, vector_matcher)
        self.platform_name = "discord"
        self.base_url = "https://discord.com"
        self.api_base_url = "https://discord.com/api/v10"
        
        # Discord bot token for API access
        self.bot_token = bot_token
        
        # Rate limiting (Discord is strict)
        self.requests_per_minute = 50
        self.min_delay = 1.2
        self.max_delay = 3.0
        
        # Content type mappings
        self.content_types = {
            'guilds': self._crawl_guilds,
            'channels': self._crawl_channels,
            'messages': self._crawl_messages,
            'users': self._crawl_users,
            'search': self._crawl_search,
            'announcements': self._crawl_announcements,
            'events': self._crawl_events,
            'threads': self._crawl_threads
        }
        
        # Discord bot client (if token provided)
        self.bot_client = None
        if self.bot_token:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            intents.guilds = True
            self.bot_client = discord.Client(intents=intents)
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        self.monitored_guilds = set()
        self.monitored_channels = set()
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Discord-specific headers"""        self.session_headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://discord.com',
            'Referer': 'https://discord.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Debug-Options': 'bugReporterEnabled',
            'X-Discord-Locale': 'en-US'
        })
        
        if self.bot_token:
            self.session_headers['Authorization'] = f'Bot {self.bot_token}'
    
    async def search_content(self, query: str, content_type: str = "messages", 
                           max_results: int = 50, guild_id: str = None) -> List[CrawlerResult]:
        """        Search for content on Discord.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            guild_id: Specific guild to search in
            
        Returns:
            List of crawler results
        """        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, guild_id)
            
            self.logger.info(f"Found {len(results)} Discord {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Discord content: {str(e)}")
            return []
    
    async def _crawl_guilds(self, query: str, max_results: int, guild_id: str = None) -> List[CrawlerResult]:
        """Crawl Discord guilds/servers"""        try:
            results = []
            
            if not self.bot_client:
                self.logger.error("Bot client not available for guild crawling")
                return []
            
            # Get guilds the bot is in
            if not self.bot_client.is_ready():
                await self.bot_client.wait_until_ready()
            
            guilds = self.bot_client.guilds
            
            for guild in guilds:
                # Filter by query if provided
                if query and query.lower() not in guild.name.lower():
                    continue
                
                # Get detailed guild information
                detailed_guild = await self._get_detailed_guild_info(guild)
                if detailed_guild:
                    result = CrawlerResult(
                        url=f"https://discord.com/channels/{guild.id}",
                        title=f"Discord Server: {guild.name}",
                        content=f"Server: {guild.name} - {detailed_guild.description or 'No description'}",
                        metadata={
                            'guild_data': asdict(detailed_guild),
                            'platform': 'discord',
                            'content_type': 'guild',
                            'member_count': detailed_guild.member_count,
                            'channel_count': len(detailed_guild.channels),
                            'boost_level': detailed_guild.boost_level,
                            'verification_level': detailed_guild.verification_level,
                            'features': detailed_guild.features
                        },
                        timestamp=detailed_guild.created_at,
                        similarity_score=0.0
                    )
                    results.append(result)
                    
                    if len(results) >= max_results:
                        break
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Discord guilds: {str(e)}")
            return []
    
    async def _crawl_channels(self, query: str, max_results: int, guild_id: str = None) -> List[CrawlerResult]:
        """Crawl Discord channels"""        try:
            results = []
            
            if not self.bot_client:
                self.logger.error("Bot client not available for channel crawling")
                return []
            
            # Get channels
            guilds_to_search = []
            if guild_id:
                guild = self.bot_client.get_guild(int(guild_id))
                if guild:
                    guilds_to_search.append(guild)
            else:
                guilds_to_search = self.bot_client.guilds
            
            for guild in guilds_to_search:
                for channel in guild.channels:
                    # Filter by query and type
                    if query and query.lower() not in channel.name.lower():
                        continue
                    
                    # Only process text channels for content
                    if isinstance(channel, discord.TextChannel):
                        detailed_channel = await self._get_detailed_channel_info(channel)
                        if detailed_channel:
                            result = CrawlerResult(
                                url=f"https://discord.com/channels/{guild.id}/{channel.id}",
                                title=f"#{channel.name} ({guild.name})",
                                content=f"Channel: #{channel.name} in {guild.name} - {channel.topic or 'No topic'}",
                                metadata={
                                    'channel_data': asdict(detailed_channel),
                                    'platform': 'discord',
                                    'content_type': 'channel',
                                    'guild_name': guild.name,
                                    'channel_type': 'text',
                                    'member_count': len(channel.members) if hasattr(channel, 'members') else 0,
                                    'nsfw': channel.nsfw,
                                    'category': channel.category.name if channel.category else None
                                },
                                timestamp=detailed_channel.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            if len(results) >= max_results:
                                return results
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Discord channels: {str(e)}")
            return []
    
    async def _crawl_messages(self, query: str, max_results: int, guild_id: str = None) -> List[CrawlerResult]:
        """Crawl Discord messages"""        try:
            results = []
            
            if not self.bot_client:
                self.logger.error("Bot client not available for message crawling")
                return []
            
            # Get channels to search
            channels_to_search = []
            if guild_id:
                guild = self.bot_client.get_guild(int(guild_id))
                if guild:
                    channels_to_search.extend([ch for ch in guild.text_channels])
            else:
                for guild in self.bot_client.guilds:
                    channels_to_search.extend([ch for ch in guild.text_channels])
            
            # Search messages in channels
            for channel in channels_to_search:
                try:
                    # Check permissions
                    if not channel.permissions_for(channel.guild.me).read_message_history:
                        continue
                    
                    # Search recent messages
                    async for message in channel.history(limit=100):
                        # Filter by query
                        if query and query.lower() not in message.content.lower():
                            continue
                        
                        # Parse message data
                        discord_message = await self._parse_message_data(message)
                        if discord_message:
                            result = CrawlerResult(
                                url=f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}",
                                title=f"Message by {message.author.display_name}",
                                content=message.content,
                                metadata={
                                    'message_data': asdict(discord_message),
                                    'platform': 'discord',
                                    'content_type': 'message',
                                    'guild_name': message.guild.name,
                                    'channel_name': message.channel.name,
                                    'author_name': message.author.display_name,
                                    'reaction_count': len(message.reactions),
                                    'attachment_count': len(message.attachments),
                                    'embed_count': len(message.embeds)
                                },
                                timestamp=discord_message.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            if len(results) >= max_results:
                                return results
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                    
                except discord.Forbidden:
                    continue
                except Exception as e:
                    self.logger.error(f"Error searching channel {channel.name}: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Discord messages: {str(e)}")
            return []
    
    async def _crawl_users(self, query: str, max_results: int, guild_id: str = None) -> List[CrawlerResult]:
        """Crawl Discord users"""        try:
            results = []
            
            if not self.bot_client:
                self.logger.error("Bot client not available for user crawling")
                return []
            
            # Get users from guilds
            guilds_to_search = []
            if guild_id:
                guild = self.bot_client.get_guild(int(guild_id))
                if guild:
                    guilds_to_search.append(guild)
            else:
                guilds_to_search = self.bot_client.guilds
            
            seen_users = set()
            
            for guild in guilds_to_search:
                for member in guild.members:
                    # Avoid duplicates
                    if member.id in seen_users:
                        continue
                    seen_users.add(member.id)
                    
                    # Filter by query
                    if query and query.lower() not in member.display_name.lower() and query.lower() not in member.name.lower():
                        continue
                    
                    # Parse user data
                    discord_user = await self._parse_user_data(member, guild)
                    if discord_user:
                        result = CrawlerResult(
                            url=f"https://discord.com/users/{member.id}",
                            title=f"User: {member.display_name}",
                            content=f"User: {member.display_name} ({member.name}) in {guild.name}",
                            metadata={
                                'user_data': asdict(discord_user),
                                'platform': 'discord',
                                'content_type': 'user',
                                'guild_name': guild.name,
                                'role_count': len(member.roles),
                                'highest_role': member.top_role.name,
                                'is_bot': member.bot,
                                'status': str(member.status),
                                'premium': member.premium_since is not None
                            },
                            timestamp=discord_user.created_at,
                            similarity_score=0.0
                        )
                        results.append(result)
                        
                        if len(results) >= max_results:
                            return results
                
                # Rate limiting
                await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Discord users: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, guild_id: str = None) -> List[CrawlerResult]:
        """General Discord search across all content types"""        try:
            results = []
            
            # Search across different content types
            messages = await self._crawl_messages(query, max_results // 2, guild_id)
            channels = await self._crawl_channels(query, max_results // 4, guild_id)
            users = await self._crawl_users(query, max_results // 4, guild_id)
            
            results.extend(messages)
            results.extend(channels)
            results.extend(users)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Discord search: {str(e)}")
            return []
    
    async def _crawl_announcements(self, query: str, max_results: int, guild_id: str = None) -> List[CrawlerResult]:
        """Crawl Discord announcements"""        try:
            results = []
            
            if not self.bot_client:
                return []
            
            # Look for announcement channels
            guilds_to_search = []
            if guild_id:
                guild = self.bot_client.get_guild(int(guild_id))
                if guild:
                    guilds_to_search.append(guild)
            else:
                guilds_to_search = self.bot_client.guilds
            
            for guild in guilds_to_search:
                announcement_channels = [
                    ch for ch in guild.text_channels 
                    if 'announcement' in ch.name.lower() or 
                       'news' in ch.name.lower() or
                       ch.type == discord.ChannelType.news
                ]
                
                for channel in announcement_channels:
                    try:
                        async for message in channel.history(limit=50):
                            # Filter by query if provided
                            if query and query.lower() not in message.content.lower():
                                continue
                            
                            discord_message = await self._parse_message_data(message)
                            if discord_message:
                                result = CrawlerResult(
                                    url=f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}",
                                    title=f"[ANNOUNCEMENT] {message.author.display_name}",
                                    content=message.content,
                                    metadata={
                                        'message_data': asdict(discord_message),
                                        'platform': 'discord',
                                        'content_type': 'announcement',
                                        'channel_type': 'announcement',
                                        'is_published': message.flags.crossposted if message.flags else False
                                    },
                                    timestamp=discord_message.created_at,
                                    similarity_score=0.0
                                )
                                results.append(result)
                                
                                if len(results) >= max_results:
                                    return results
                        
                        await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                        
                    except discord.Forbidden:
                        continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Discord announcements: {str(e)}")
            return []
    
    async def _crawl_events(self, query: str, max_results: int, guild_id: str = None) -> List[CrawlerResult]:
        """Crawl Discord scheduled events"""        try:
            results = []
            
            if not self.bot_client:
                return []
            
            # Get scheduled events
            guilds_to_search = []
            if guild_id:
                guild = self.bot_client.get_guild(int(guild_id))
                if guild:
                    guilds_to_search.append(guild)
            else:
                guilds_to_search = self.bot_client.guilds
            
            for guild in guilds_to_search:
                try:
                    events = guild.scheduled_events
                    
                    for event in events:
                        # Filter by query if provided
                        if query and query.lower() not in event.name.lower():
                            continue
                        
                        result = CrawlerResult(
                            url=f"https://discord.com/events/{guild.id}/{event.id}",
                            title=f"[EVENT] {event.name}",
                            content=f"Event: {event.name} - {event.description or 'No description'}",
                            metadata={
                                'platform': 'discord',
                                'content_type': 'event',
                                'event_id': str(event.id),
                                'guild_name': guild.name,
                                'start_time': event.start_time.isoformat(),
                                'end_time': event.end_time.isoformat() if event.end_time else None,
                                'location': event.location,
                                'user_count': event.user_count,
                                'status': str(event.status),
                                'entity_type': str(event.entity_type),
                                'privacy_level': str(event.privacy_level)
                            },
                            timestamp=event.created_at,
                            similarity_score=0.0
                        )
                        results.append(result)
                        
                        if len(results) >= max_results:
                            return results
                    
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                    
                except Exception as e:
                    self.logger.error(f"Error getting events for guild {guild.name}: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Discord events: {str(e)}")
            return []
    
    async def _crawl_threads(self, query: str, max_results: int, guild_id: str = None) -> List[CrawlerResult]:
        """Crawl Discord threads"""        try:
            results = []
            
            if not self.bot_client:
                return []
            
            # Get threads
            guilds_to_search = []
            if guild_id:
                guild = self.bot_client.get_guild(int(guild_id))
                if guild:
                    guilds_to_search.append(guild)
            else:
                guilds_to_search = self.bot_client.guilds
            
            for guild in guilds_to_search:
                for channel in guild.text_channels:
                    try:
                        # Get active threads
                        active_threads = await channel.active_threads()
                        
                        for thread in active_threads.threads:
                            # Filter by query if provided
                            if query and query.lower() not in thread.name.lower():
                                continue
                            
                            result = CrawlerResult(
                                url=f"https://discord.com/channels/{guild.id}/{thread.id}",
                                title=f"[THREAD] {thread.name}",
                                content=f"Thread: {thread.name} in #{channel.name}",
                                metadata={
                                    'platform': 'discord',
                                    'content_type': 'thread',
                                    'thread_id': str(thread.id),
                                    'parent_channel': channel.name,
                                    'guild_name': guild.name,
                                    'member_count': thread.member_count,
                                    'message_count': thread.message_count,
                                    'archived': thread.archived,
                                    'auto_archive_duration': thread.auto_archive_duration,
                                    'archive_timestamp': thread.archive_timestamp.isoformat() if thread.archive_timestamp else None
                                },
                                timestamp=thread.created_at,
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            if len(results) >= max_results:
                                return results
                        
                        await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                        
                    except discord.Forbidden:
                        continue
                    except Exception as e:
                        self.logger.error(f"Error getting threads for channel {channel.name}: {str(e)}")
                        continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Discord threads: {str(e)}")
            return []
    
    # Helper methods
    
    async def _get_detailed_guild_info(self, guild: discord.Guild) -> Optional[DiscordGuild]:
        """Get detailed guild information"""        try:
            # Get channels
            channels = []
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    detailed_channel = await self._get_detailed_channel_info(channel)
                    if detailed_channel:
                        channels.append(detailed_channel)
            
            discord_guild = DiscordGuild(
                guild_id=str(guild.id),
                name=guild.name,
                icon=guild.icon.url if guild.icon else None,
                icon_hash=str(guild.icon) if guild.icon else None,
                splash=guild.splash.url if guild.splash else None,
                discovery_splash=guild.discovery_splash.url if guild.discovery_splash else None,
                owner=guild.owner_id == self.bot_client.user.id,
                owner_id=str(guild.owner_id),
                permissions=None,  # Would need to calculate
                region=str(guild.region) if hasattr(guild, 'region') else None,
                afk_channel_id=str(guild.afk_channel.id) if guild.afk_channel else None,
                afk_timeout=guild.afk_timeout,
                widget_enabled=guild.widget_enabled,
                widget_channel_id=str(guild.widget_channel.id) if guild.widget_channel else None,
                verification_level=guild.verification_level.value,
                default_message_notifications=guild.default_notifications.value,
                explicit_content_filter=guild.explicit_content_filter.value,
                roles=[{'id': str(role.id), 'name': role.name, 'color': role.color.value} for role in guild.roles],
                emojis=[{'id': str(emoji.id), 'name': emoji.name, 'animated': emoji.animated} for emoji in guild.emojis],
                features=guild.features,
                mfa_level=guild.mfa_level.value,
                application_id=str(guild.application_id) if guild.application_id else None,
                system_channel_id=str(guild.system_channel.id) if guild.system_channel else None,
                system_channel_flags=guild.system_channel_flags.value,
                rules_channel_id=str(guild.rules_channel.id) if guild.rules_channel else None,
                max_presences=guild.max_presences,
                max_members=guild.max_members,
                vanity_url_code=guild.vanity_url,
                description=guild.description,
                banner=guild.banner.url if guild.banner else None,
                premium_tier=guild.premium_tier,
                premium_subscription_count=guild.premium_subscription_count,
                preferred_locale=str(guild.preferred_locale),
                public_updates_channel_id=str(guild.public_updates_channel.id) if guild.public_updates_channel else None,
                max_video_channel_users=guild.max_video_channel_users,
                approximate_member_count=guild.approximate_member_count,
                approximate_presence_count=guild.approximate_presence_count,
                welcome_screen=None,  # Would need additional parsing
                nsfw_level=guild.nsfw_level.value,
                stickers=[{'id': str(sticker.id), 'name': sticker.name} for sticker in guild.stickers],
                premium_progress_bar_enabled=guild.premium_progress_bar_enabled,
                created_at=guild.created_at,
                member_count=guild.member_count,
                online_count=sum(1 for member in guild.members if member.status != discord.Status.offline),
                boost_count=guild.premium_subscription_count or 0,
                boost_level=guild.premium_tier,
                channels=channels,
                categories=[{'id': str(cat.id), 'name': cat.name} for cat in guild.categories],
                voice_channels=[{'id': str(vc.id), 'name': vc.name} for vc in guild.voice_channels],
                threads=[],  # Would need additional API calls
                scheduled_events=[{'id': str(event.id), 'name': event.name} for event in guild.scheduled_events]
            )
            
            return discord_guild
            
        except Exception as e:
            self.logger.error(f"Error getting detailed guild info: {str(e)}")
            return None
    
    async def _get_detailed_channel_info(self, channel: discord.TextChannel) -> Optional[DiscordChannel]:
        """Get detailed channel information"""        try:
            discord_channel = DiscordChannel(
                channel_id=str(channel.id),
                guild_id=str(channel.guild.id),
                name=channel.name,
                topic=channel.topic,
                position=channel.position,
                type=channel.type.value,
                nsfw=channel.nsfw,
                last_message_id=str(channel.last_message_id) if channel.last_message_id else None,
                bitrate=None,  # Voice channel only
                user_limit=None,  # Voice channel only
                rate_limit_per_user=channel.slowmode_delay,
                recipients=[],  # DM only
                icon=None,  # Group DM only
                owner_id=None,  # Group DM only
                application_id=None,
                parent_id=str(channel.category.id) if channel.category else None,
                last_pin_timestamp=None,  # Would need additional API call
                rtc_region=None,  # Voice channel only
                video_quality_mode=None,  # Voice channel only
                message_count=None,  # Would need calculation
                member_count=len(channel.members) if hasattr(channel, 'members') else None,
                thread_metadata=None,  # Thread only
                member=None,  # Thread only
                default_auto_archive_duration=channel.default_auto_archive_duration,
                permissions=None,  # Would need calculation
                flags=0,  # Would need to get from API
                created_at=channel.created_at,
                category_name=channel.category.name if channel.category else None,
                overwrites=[],  # Would need parsing
                message_history=[],  # Would need separate API calls
                active_threads=[],  # Would need separate API calls
                archived_threads=[]  # Would need separate API calls
            )
            
            return discord_channel
            
        except Exception as e:
            self.logger.error(f"Error getting detailed channel info: {str(e)}")
            return None
    
    async def _parse_message_data(self, message: discord.Message) -> Optional[DiscordMessage]:
        """Parse message data"""        try:
            discord_message = DiscordMessage(
                message_id=str(message.id),
                channel_id=str(message.channel.id),
                guild_id=str(message.guild.id) if message.guild else None,
                author_id=str(message.author.id),
                author_username=message.author.name,
                author_display_name=message.author.display_name,
                content=message.content,
                clean_content=message.clean_content,
                created_at=message.created_at,
                edited_at=message.edited_at,
                tts=message.tts,
                mention_everyone=message.mention_everyone,
                mentions=[{'id': str(user.id), 'username': user.name} for user in message.mentions],
                mention_roles=[str(role.id) for role in message.role_mentions],
                mention_channels=[str(channel.id) for channel in message.channel_mentions],
                attachments=[{
                    'id': str(att.id),
                    'filename': att.filename,
                    'size': att.size,
                    'url': att.url,
                    'content_type': att.content_type
                } for att in message.attachments],
                embeds=[embed.to_dict() for embed in message.embeds],
                reactions=[{
                    'emoji': str(reaction.emoji),
                    'count': reaction.count,
                    'me': reaction.me
                } for reaction in message.reactions],
                pinned=message.pinned,
                webhook_id=str(message.webhook_id) if message.webhook_id else None,
                message_type=str(message.type),
                activity=None,  # Would need additional parsing
                application=None,  # Would need additional parsing
                message_reference={
                    'message_id': str(message.reference.message_id),
                    'channel_id': str(message.reference.channel_id),
                    'guild_id': str(message.reference.guild_id)
                } if message.reference else None,
                flags=message.flags.value if message.flags else 0,
                stickers=[{
                    'id': str(sticker.id),
                    'name': sticker.name,
                    'format': str(sticker.format)
                } for sticker in message.stickers],
                referenced_message=str(message.reference.message_id) if message.reference else None,
                interaction=None,  # Would need additional parsing
                thread=None,  # Would need additional parsing
                components=[],  # Would need additional parsing
                sentiment_score=None,  # Would need sentiment analysis
                toxicity_score=None,  # Would need toxicity analysis
                language=None  # Would need language detection
            )
            
            return discord_message
            
        except Exception as e:
            self.logger.error(f"Error parsing message data: {str(e)}")
            return None
    
    async def _parse_user_data(self, member: discord.Member, guild: discord.Guild) -> Optional[DiscordUser]:
        """Parse user data"""        try:
            discord_user = DiscordUser(
                user_id=str(member.id),
                username=member.name,
                discriminator=member.discriminator,
                display_name=member.display_name,
                avatar_url=member.avatar.url if member.avatar else None,
                banner_url=member.banner.url if member.banner else None,
                accent_color=member.accent_color.value if member.accent_color else None,
                bot=member.bot,
                system=member.system,
                verified=getattr(member, 'verified', False),
                email=None,  # Not accessible
                locale=None,  # Not accessible
                mfa_enabled=False,  # Not accessible
                premium_type=None,  # Not accessible
                public_flags=member.public_flags.value,
                flags=0,  # Would need additional API call
                created_at=member.created_at,
                joined_at=member.joined_at,
                bio=None,  # Would need additional API call
                pronouns=None,  # Would need additional API call
                status=str(member.status),
                activity=member.activity.to_dict() if member.activity else None,
                roles=[role.name for role in member.roles],
                permissions=[],  # Would need calculation
                badges=[],  # Would need additional API call
                nitro_since=member.premium_since,
                mutual_guilds=[],  # Would need additional API calls
                is_friend=False,  # Would need additional API call
                is_blocked=False,  # Would need additional API call
                message_count=0,  # Would need calculation
                reaction_count=0,  # Would need calculation
                voice_time_minutes=0  # Would need calculation
            )
            
            return discord_user
            
        except Exception as e:
            self.logger.error(f"Error parsing user data: {str(e)}")
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
        """Extract metadata from Discord content"""        try:
            # Parse Discord URL
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            metadata = {
                'platform': 'discord',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            if 'channels' in path_parts:
                idx = path_parts.index('channels')
                if len(path_parts) > idx + 1:
                    guild_id = path_parts[idx + 1]
                    metadata['guild_id'] = guild_id
                    
                    if len(path_parts) > idx + 2:
                        channel_id = path_parts[idx + 2]
                        metadata['channel_id'] = channel_id
                        
                        if len(path_parts) > idx + 3:
                            message_id = path_parts[idx + 3]
                            metadata['message_id'] = message_id
                            metadata['content_type'] = 'message'
                        else:
                            metadata['content_type'] = 'channel'
                    else:
                        metadata['content_type'] = 'guild'
            
            elif 'events' in path_parts:
                idx = path_parts.index('events')
                if len(path_parts) > idx + 2:
                    guild_id = path_parts[idx + 1]
                    event_id = path_parts[idx + 2]
                    metadata.update({
                        'guild_id': guild_id,
                        'event_id': event_id,
                        'content_type': 'event'
                    })
            
            elif 'users' in path_parts:
                idx = path_parts.index('users')
                if len(path_parts) > idx + 1:
                    user_id = path_parts[idx + 1]
                    metadata.update({
                        'user_id': user_id,
                        'content_type': 'user'
                    })
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Discord metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Discord platform information"""        return {
            'platform_name': 'Discord',
            'base_url': self.base_url,
            'api_base_url': self.api_base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Server/guild discovery and analysis',
                'Channel content monitoring',
                'User activity tracking',
                'Message sentiment analysis',
                'Community engagement metrics',
                'Moderation log tracking',
                'Voice channel activity monitoring',
                'Event and announcement tracking',
                'Bot interaction analysis',
                'Thread and forum monitoring'
            ],
            'authentication': {
                'required': True,
                'type': 'Bot Token',
                'scope': 'Bot permissions required'
            },
            'limitations': [
                'Requires bot to be in servers to access content',
                'Limited by Discord API rate limits',
                'Requires appropriate permissions for each action',
                'Some user data not accessible without additional permissions'
            ]
        }
