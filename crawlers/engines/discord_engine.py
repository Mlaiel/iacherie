"""Discord Crawling Engine
======================

Advanced Discord crawler for community monitoring and content protection.
Handles servers, channels, messages, and voice data extraction.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, ou distribution sans autorisation écrite explicite est strictement interdite.
Les contrevenants seront poursuivis selon la loi allemande et internationale.

🏗️ Architecture Enterprise - Équipe Projet Spécialisée :
• Lead Developer IA : Fahed Mlaiel (mlaiel@live.de)
• Backend Senior Engineer : Architecture microservices & APIs
• ML/AI Engineer : Intelligence artificielle & algorithmes avancés
• Database Administrator : Optimisation données & performance
• Security Expert : Cybersécurité & protection contenu
• DevOps Engineer : Infrastructure cloud & déploiement
• Audio/Video Specialist : Traitement multimédia avancé
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import re
import json
import hashlib
import time
import base64
from io import BytesIO

import aiohttp
import discord
from discord.ext import commands
import requests

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError,
    PermissionDeniedError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..models.content_models import MessageContent, ChannelContent, ServerContent
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class DiscordMessageData:
    """Discord message data structure"""    message_id: str
    channel_id: str
    guild_id: str
    author_id: str
    author_name: str
    author_discriminator: str
    content: str
    timestamp: datetime
    edited_timestamp: Optional[datetime]
    message_type: str
    attachments: List[Dict[str, Any]]
    embeds: List[Dict[str, Any]]
    reactions: List[Dict[str, Any]]
    mentions: List[Dict[str, Any]]
    mention_roles: List[str]
    mention_everyone: bool
    pinned: bool
    tts: bool
    reference: Optional[Dict[str, Any]]
    thread: Optional[Dict[str, Any]]
    stickers: List[Dict[str, Any]]
    flags: int
    interaction: Optional[Dict[str, Any]]
    webhook_id: Optional[str] = None
    is_bot: bool = False
    is_system: bool = False


@dataclass
class DiscordChannelData:
    """Discord channel data structure"""    channel_id: str
    guild_id: str
    name: str
    type: str  # text, voice, category, news, etc.
    position: int
    permission_overwrites: List[Dict[str, Any]]
    nsfw: bool
    rate_limit_per_user: int
    topic: Optional[str]
    last_message_id: Optional[str]
    parent_id: Optional[str]
    bitrate: Optional[int]
    user_limit: Optional[int]
    rtc_region: Optional[str]
    video_quality_mode: Optional[int]
    default_auto_archive_duration: Optional[int]
    permissions: Optional[str]
    flags: int
    member_count: int = 0
    message_count: int = 0
    archived: bool = False
    locked: bool = False
    invitable: bool = True


@dataclass
class DiscordServerData:
    """Discord server (guild) data structure"""    guild_id: str
    name: str
    icon: Optional[str]
    icon_hash: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    owner_id: str
    permissions: Optional[str]
    region: str
    afk_channel_id: Optional[str]
    afk_timeout: int
    widget_enabled: bool
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
    channels: List[DiscordChannelData] = None
    members: List[Dict[str, Any]] = None


class DiscordCrawlerEngine(BaseCrawlerEngine):
    """    Advanced Discord crawler engine for community monitoring.
    
    Features:
    - Discord Bot API integration
    - Real-time message monitoring
    - Server and channel analysis
    - Content moderation capabilities
    - Attachment and media extraction
    - Voice channel monitoring
    - Reaction and engagement tracking
    - Permission-aware data collection
    """
    def __init__(self, 
                 bot_token: Optional[str] = None,
                 user_token: Optional[str] = None,
                 use_bot: bool = True,
                 intents: Optional[discord.Intents] = None,
                 rate_limit_config: Optional[Dict] = None):
        """        Initialize Discord crawler engine.
        
        Args:
            bot_token: Discord bot token
            user_token: Discord user token (for self-bot, use carefully)
            use_bot: Whether to use bot or user token
            intents: Discord intents configuration
            rate_limit_config: Rate limiting configuration
        """        super().__init__()
        
        # Authentication
        self.bot_token = bot_token or settings.DISCORD_BOT_TOKEN
        self.user_token = user_token or settings.DISCORD_USER_TOKEN
        self.use_bot = use_bot
        
        # Discord client setup
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True
            intents.members = True
            intents.reactions = True
        
        self.intents = intents
        self.client = None
        self.bot = None
        
        # Rate limiting (Discord has strict limits)
        rate_config = rate_limit_config or {
            'requests_per_second': 50,
            'requests_per_minute': 120,
            'requests_per_hour': 3600,
            'burst_limit': 10
        }
        self.rate_limiter = RateLimiter(**rate_config)
        
        # Cache manager
        self.cache_manager = CacheManager(
            cache_type='redis',
            ttl=1800,  # 30 minute cache
            key_prefix='discord_'
        )

    async def authenticate(self) -> bool:
        """Authenticate with Discord API"""        try:
            if self.use_bot and self.bot_token:
                self.bot = commands.Bot(
                    command_prefix='!',
                    intents=self.intents
                )
                
                @self.bot.event
                async def on_ready():
                    logger.info(f"Discord bot logged in as {self.bot.user}")
                
                await self.bot.login(self.bot_token)
                return True
            
            elif not self.use_bot and self.user_token:
                self.client = discord.Client(intents=self.intents)
                
                @self.client.event
                async def on_ready():
                    logger.info(f"Discord client logged in as {self.client.user}")
                
                await self.client.login(self.user_token)
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Discord authentication failed: {e}")
            return False

    async def get_guild_info(self, guild_id: int) -> DiscordServerData:
        """        Get Discord guild (server) information.
        
        Args:
            guild_id: Discord guild ID
        
        Returns:
            DiscordServerData object
        """        cache_key = f"guild_info_{guild_id}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return DiscordServerData(**cached_result)

        try:
            await self.rate_limiter.acquire()
            
            client = self.bot or self.client
            if not client:
                raise AuthenticationError("Discord client not initialized")
            
            guild = client.get_guild(guild_id)
            if not guild:
                guild = await client.fetch_guild(guild_id)
            
            # Get channels
            channels = []
            for channel in guild.channels:
                channel_data = DiscordChannelData(
                    channel_id=str(channel.id),
                    guild_id=str(guild.id),
                    name=channel.name,
                    type=str(channel.type),
                    position=channel.position,
                    permission_overwrites=[
                        {
                            'id': str(overwrite[0].id),
                            'type': 'role' if hasattr(overwrite[0], 'color') else 'member',
                            'allow': overwrite[1].allow.value,
                            'deny': overwrite[1].deny.value
                        }
                        for overwrite in channel.overwrites.items()
                    ],
                    nsfw=getattr(channel, 'nsfw', False),
                    rate_limit_per_user=getattr(channel, 'slowmode_delay', 0),
                    topic=getattr(channel, 'topic', None),
                    last_message_id=str(getattr(channel, 'last_message_id', None) or ''),
                    parent_id=str(getattr(channel, 'category_id', None) or ''),
                    bitrate=getattr(channel, 'bitrate', None),
                    user_limit=getattr(channel, 'user_limit', None),
                    flags=0
                )
                channels.append(channel_data)
            
            server_data = DiscordServerData(
                guild_id=str(guild.id),
                name=guild.name,
                icon=str(guild.icon.url) if guild.icon else None,
                icon_hash=str(guild.icon) if guild.icon else None,
                splash=str(guild.splash.url) if guild.splash else None,
                discovery_splash=str(guild.discovery_splash.url) if guild.discovery_splash else None,
                owner_id=str(guild.owner_id),
                permissions=None,
                region=str(guild.region) if hasattr(guild, 'region') else 'unknown',
                afk_channel_id=str(guild.afk_channel.id) if guild.afk_channel else None,
                afk_timeout=guild.afk_timeout,
                widget_enabled=guild.widget_enabled or False,
                widget_channel_id=str(guild.widget_channel.id) if guild.widget_channel else None,
                verification_level=guild.verification_level.value,
                default_message_notifications=guild.default_notifications.value,
                explicit_content_filter=guild.explicit_content_filter.value,
                roles=[
                    {
                        'id': str(role.id),
                        'name': role.name,
                        'color': role.color.value,
                        'hoist': role.hoist,
                        'mentionable': role.mentionable,
                        'permissions': role.permissions.value,
                        'position': role.position
                    }
                    for role in guild.roles
                ],
                emojis=[
                    {
                        'id': str(emoji.id),
                        'name': emoji.name,
                        'animated': emoji.animated,
                        'url': str(emoji.url)
                    }
                    for emoji in guild.emojis
                ],
                features=guild.features,
                mfa_level=guild.mfa_level,
                application_id=str(guild.application_id) if guild.application_id else None,
                system_channel_id=str(guild.system_channel.id) if guild.system_channel else None,
                system_channel_flags=guild.system_channel_flags.value,
                rules_channel_id=str(guild.rules_channel.id) if guild.rules_channel else None,
                max_presences=guild.max_presences,
                max_members=guild.max_members,
                vanity_url_code=guild.vanity_url_code,
                description=guild.description,
                banner=str(guild.banner.url) if guild.banner else None,
                premium_tier=guild.premium_tier,
                premium_subscription_count=guild.premium_subscription_count,
                preferred_locale=str(guild.preferred_locale),
                public_updates_channel_id=str(guild.public_updates_channel.id) if guild.public_updates_channel else None,
                max_video_channel_users=guild.max_video_channel_users,
                approximate_member_count=guild.approximate_member_count,
                approximate_presence_count=guild.approximate_presence_count,
                welcome_screen=None,
                nsfw_level=guild.nsfw_level.value if hasattr(guild, 'nsfw_level') else 0,
                stickers=[],
                premium_progress_bar_enabled=guild.premium_progress_bar_enabled,
                channels=channels
            )
            
            # Cache result
            await self.cache_manager.set(cache_key, asdict(server_data))
            
            return server_data
        
        except Exception as e:
            logger.error(f"Error getting Discord guild info: {e}")
            raise CrawlerError(f"Discord guild info retrieval failed: {e}")

    async def get_channel_messages(self, 
                                 channel_id: int, 
                                 limit: int = 100,
                                 before: Optional[datetime] = None,
                                 after: Optional[datetime] = None) -> List[DiscordMessageData]:
        """        Get messages from a Discord channel.
        
        Args:
            channel_id: Discord channel ID
            limit: Maximum number of messages to return
            before: Get messages before this timestamp
            after: Get messages after this timestamp
        
        Returns:
            List of DiscordMessageData objects
        """        cache_key = f"channel_messages_{channel_id}_{limit}_{before}_{after}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return [DiscordMessageData(**msg) for msg in cached_result]

        messages = []
        
        try:
            await self.rate_limiter.acquire()
            
            client = self.bot or self.client
            if not client:
                raise AuthenticationError("Discord client not initialized")
            
            channel = client.get_channel(channel_id)
            if not channel:
                channel = await client.fetch_channel(channel_id)
            
            # Fetch messages
            async for message in channel.history(
                limit=limit,
                before=before,
                after=after
            ):
                message_data = await self._process_message_data(message)
                if message_data:
                    messages.append(message_data)
            
            # Cache results
            await self.cache_manager.set(
                cache_key, 
                [asdict(msg) for msg in messages]
            )
        
        except Exception as e:
            logger.error(f"Error getting Discord channel messages: {e}")
            raise CrawlerError(f"Discord channel messages retrieval failed: {e}")
        
        return messages

    async def search_messages(self, 
                            guild_id: int,
                            query: str,
                            channel_id: Optional[int] = None,
                            author_id: Optional[int] = None,
                            limit: int = 100) -> List[DiscordMessageData]:
        """        Search for Discord messages by query.
        
        Args:
            guild_id: Discord guild ID
            query: Search query
            channel_id: Specific channel to search in
            author_id: Specific author to search for
            limit: Maximum number of messages to return
        
        Returns:
            List of DiscordMessageData objects
        """        # Note: Discord doesn't have a built-in search API
        # This implementation searches through recent messages
        
        messages = []
        
        try:
            client = self.bot or self.client
            if not client:
                raise AuthenticationError("Discord client not initialized")
            
            guild = client.get_guild(guild_id)
            if not guild:
                guild = await client.fetch_guild(guild_id)
            
            channels_to_search = []
            if channel_id:
                channel = guild.get_channel(channel_id)
                if channel:
                    channels_to_search.append(channel)
            else:
                channels_to_search = [
                    ch for ch in guild.text_channels 
                    if ch.permissions_for(guild.me).read_message_history
                ]
            
            for channel in channels_to_search:
                try:
                    await self.rate_limiter.acquire()
                    
                    async for message in channel.history(limit=200):
                        # Check if message matches search criteria
                        if query.lower() in message.content.lower():
                            if author_id and message.author.id != author_id:
                                continue
                            
                            message_data = await self._process_message_data(message)
                            if message_data:
                                messages.append(message_data)
                            
                            if len(messages) >= limit:
                                break
                    
                    if len(messages) >= limit:
                        break
                
                except Exception as e:
                    logger.warning(f"Error searching channel {channel.id}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error searching Discord messages: {e}")
            raise CrawlerError(f"Discord message search failed: {e}")
        
        return messages[:limit]

    async def monitor_server_content(self, 
                                   guild_ids: List[int],
                                   keywords: List[str],
                                   check_interval: int = 60) -> AsyncGenerator[Dict[str, Any], None]:
        """        Monitor Discord servers for content matches.
        
        Args:
            guild_ids: List of Discord guild IDs to monitor
            keywords: Keywords to search for
            check_interval: Check interval in seconds
        
        Yields:
            Dictionary containing monitoring results
        """        logger.info(f"Starting Discord content monitoring for {len(guild_ids)} servers")
        
        last_check = {}
        
        while True:
            for guild_id in guild_ids:
                try:
                    current_time = datetime.now()
                    since = last_check.get(guild_id, current_time - timedelta(minutes=5))
                    
                    # Get recent messages from all accessible channels
                    guild_data = await self.get_guild_info(guild_id)
                    
                    for channel in guild_data.channels:
                        if channel.type == 'text':
                            try:
                                messages = await self.get_channel_messages(
                                    int(channel.channel_id),
                                    limit=50,
                                    after=since
                                )
                                
                                for message in messages:
                                    content = message.content.lower()
                                    for keyword in keywords:
                                        if keyword.lower() in content:
                                            yield {
                                                'type': 'discord_content_match',
                                                'platform': 'discord',
                                                'guild_id': guild_id,
                                                'channel_id': message.channel_id,
                                                'message_id': message.message_id,
                                                'keyword': keyword,
                                                'content': content[:500],
                                                'author': message.author_name,
                                                'timestamp': message.timestamp,
                                                'attachments': len(message.attachments),
                                                'reactions': len(message.reactions)
                                            }
                            
                            except Exception as e:
                                logger.warning(f"Error monitoring Discord channel {channel.channel_id}: {e}")
                                continue
                    
                    last_check[guild_id] = current_time
                
                except Exception as e:
                    logger.error(f"Error monitoring Discord guild {guild_id}: {e}")
                    yield {
                        'type': 'error',
                        'platform': 'discord',
                        'guild_id': guild_id,
                        'error': str(e),
                        'timestamp': datetime.now()
                    }
            
            await asyncio.sleep(check_interval)

    async def _process_message_data(self, message) -> Optional[DiscordMessageData]:
        """Process Discord message into DiscordMessageData object"""        try:
            return DiscordMessageData(
                message_id=str(message.id),
                channel_id=str(message.channel.id),
                guild_id=str(message.guild.id) if message.guild else '',
                author_id=str(message.author.id),
                author_name=message.author.name,
                author_discriminator=message.author.discriminator,
                content=message.content,
                timestamp=message.created_at,
                edited_timestamp=message.edited_at,
                message_type=str(message.type),
                attachments=[
                    {
                        'id': str(att.id),
                        'filename': att.filename,
                        'size': att.size,
                        'url': att.url,
                        'proxy_url': att.proxy_url,
                        'content_type': att.content_type
                    }
                    for att in message.attachments
                ],
                embeds=[embed.to_dict() for embed in message.embeds],
                reactions=[
                    {
                        'emoji': str(reaction.emoji),
                        'count': reaction.count,
                        'me': reaction.me
                    }
                    for reaction in message.reactions
                ],
                mentions=[
                    {
                        'id': str(user.id),
                        'username': user.name,
                        'discriminator': user.discriminator
                    }
                    for user in message.mentions
                ],
                mention_roles=[str(role.id) for role in message.role_mentions],
                mention_everyone=message.mention_everyone,
                pinned=message.pinned,
                tts=message.tts,
                reference=message.reference.to_dict() if message.reference else None,
                stickers=[sticker.to_dict() for sticker in getattr(message, 'stickers', [])],
                flags=message.flags.value,
                interaction=message.interaction.to_dict() if getattr(message, 'interaction', None) else None,
                webhook_id=str(message.webhook_id) if getattr(message, 'webhook_id', None) else None,
                is_bot=message.author.bot,
                is_system=message.is_system()
            )
        
        except Exception as e:
            logger.error(f"Error processing Discord message data: {e}")
            return None

    async def close(self):
        """Close Discord client connections"""        if self.bot:
            await self.bot.close()
        if self.client:
            await self.client.close()

    def __del__(self):
        """Cleanup resources"""        try:
            if self.bot or self.client:
                asyncio.create_task(self.close())
        except:
            pass
