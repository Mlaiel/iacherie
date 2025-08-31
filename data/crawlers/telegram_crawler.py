"""Telegram Crawler Implementation
==============================

Advanced Telegram content monitoring and channel analysis crawler.
Implements comprehensive message tracking and media analysis.

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
"""import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
import aiohttp
from telethon import TelegramClient, events
from telethon.tl.types import (
    Channel, Chat, User, Message, MessageMediaPhoto, 
    MessageMediaDocument, MessageMediaWebPage,
    PeerChannel, PeerChat, PeerUser
)
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
import time
import random
from urllib.parse import urljoin, urlparse, parse_qs
import re
import hashlib

from .platform_crawler import PlatformCrawler, CrawlerConfig, CrawlerResult


@dataclass
class TelegramMessage:
    """Telegram message information"""    message_id: int
    chat_id: int
    chat_username: Optional[str]
    chat_title: str
    sender_id: Optional[int]
    sender_username: Optional[str]
    sender_first_name: Optional[str]
    sender_last_name: Optional[str]
    text: str
    raw_text: str
    date: datetime
    edit_date: Optional[datetime]
    is_reply: bool
    reply_to_msg_id: Optional[int]
    forward_info: Optional[Dict[str, Any]]
    views: Optional[int]
    forwards: Optional[int]
    replies: Optional[int]
    reactions: Optional[Dict[str, Any]]
    media_type: Optional[str]  # photo, document, video, audio, voice, sticker
    media_info: Optional[Dict[str, Any]]
    file_id: Optional[str]
    file_size: Optional[int]
    file_name: Optional[str]
    mime_type: Optional[str]
    duration: Optional[int]
    width: Optional[int]
    height: Optional[int]
    has_media_spoiler: bool
    is_scheduled: bool
    is_pinned: bool
    is_silent: bool
    post_author: Optional[str]
    grouped_id: Optional[int]
    restriction_reason: Optional[str]
    ttl_period: Optional[int]
    web_preview: Optional[Dict[str, Any]]
    entities: List[Dict[str, Any]]
    message_link: str
    language: Optional[str]
    sentiment_score: Optional[float]


@dataclass
class TelegramChannel:
    """Telegram channel information"""    channel_id: int
    username: Optional[str]
    title: str
    about: Optional[str]
    chat_photo: Optional[str]
    participants_count: int
    admins_count: Optional[int]
    kicked_count: Optional[int]
    banned_count: Optional[int]
    online_count: Optional[int]
    created_date: Optional[datetime]
    is_broadcast: bool
    is_megagroup: bool
    is_verified: bool
    is_restricted: bool
    is_scam: bool
    is_fake: bool
    has_location: bool
    has_link: bool
    has_geo: bool
    can_view_participants: bool
    can_set_username: bool
    can_set_stickers: bool
    can_set_location: bool
    can_view_stats: bool
    default_banned_rights: Optional[Dict[str, Any]]
    migrated_from_chat_id: Optional[int]
    migrated_from_max_id: Optional[int]
    pinned_msg_id: Optional[int]
    stickerset: Optional[Dict[str, Any]]
    available_min_id: int
    folder_id: Optional[int]
    linked_chat_id: Optional[int]
    location: Optional[Dict[str, Any]]
    slowmode_seconds: Optional[int]
    slowmode_next_send_date: Optional[datetime]
    stats: Optional[Dict[str, Any]]
    channel_link: str
    recent_messages: List[TelegramMessage]
    growth_rate: Optional[float]
    engagement_rate: Optional[float]


@dataclass
class TelegramUser:
    """Telegram user information"""    user_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    phone: Optional[str]
    bio: Optional[str]
    profile_photo: Optional[str]
    is_self: bool
    is_contact: bool
    is_mutual_contact: bool
    is_deleted: bool
    is_bot: bool
    is_verified: bool
    is_restricted: bool
    is_scam: bool
    is_fake: bool
    is_premium: bool
    is_support: bool
    lang_code: Optional[str]
    common_chats_count: int
    blocked: bool
    restriction_reason: Optional[str]
    bot_chat_history: bool
    bot_nochats: bool
    bot_inline_geo: bool
    bot_info_version: Optional[int]
    bot_inline_placeholder: Optional[str]
    settings: Optional[Dict[str, Any]]
    personal_photo: Optional[str]
    fallback_photo: Optional[str]
    pinned_msg_id: Optional[int]
    folder_id: Optional[int]
    ttl_period: Optional[int]
    theme_emoticon: Optional[str]
    private_forward_name: Optional[str]
    bot_commands: List[Dict[str, Any]]
    status: Optional[str]
    last_seen: Optional[datetime]


class TelegramCrawler(PlatformCrawler):
    """    Advanced Telegram crawler for messaging content monitoring and analysis.
    
    Features:
    - Channel and group monitoring
    - Message content analysis
    - Media file tracking
    - User activity analysis
    - Real-time message streaming
    - Forward chain tracking
    - Reaction and engagement metrics
    - Bot interaction monitoring
    - Privacy-respecting crawling
    """    
    def __init__(self, config: CrawlerConfig, vector_matcher=None, 
                 api_id: int = None, api_hash: str = None, 
                 bot_token: str = None, session_name: str = "telegram_crawler"):
        super().__init__(config, vector_matcher)
        self.platform_name = "telegram"
        self.base_url = "https://t.me"
        
        # Telegram API credentials
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.session_name = session_name
        
        # Rate limiting (Telegram is restrictive)
        self.requests_per_minute = 20
        self.min_delay = 3.0
        self.max_delay = 5.0
        
        # Content type mappings
        self.content_types = {
            'messages': self._crawl_messages,
            'channels': self._crawl_channels,
            'users': self._crawl_users,
            'search': self._crawl_search,
            'media': self._crawl_media,
            'forwards': self._crawl_forwards,
            'reactions': self._crawl_reactions
        }
        
        # Telegram client
        self.client = None
        if self.api_id and self.api_hash:
            if self.bot_token:
                self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            else:
                self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        
        # Tracking
        self.request_count = 0
        self.last_request_time = 0
        self.monitored_channels = set()
        
        # Initialize session headers
        self._setup_session_headers()
    
    def _setup_session_headers(self):
        """Setup Telegram-specific headers"""        self.session_headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://web.telegram.org',
            'Referer': 'https://web.telegram.org/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    async def search_content(self, query: str, content_type: str = "messages", 
                           max_results: int = 50, channel_username: str = None) -> List[CrawlerResult]:
        """        Search for content on Telegram.
        
        Args:
            query: Search query
            content_type: Type of content to search for
            max_results: Maximum number of results
            channel_username: Specific channel to search in
            
        Returns:
            List of crawler results
        """        try:
            await self._check_rate_limit()
            
            if content_type not in self.content_types:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Initialize Telegram client if needed
            if not self.client:
                self.logger.error("Telegram client not configured")
                return []
            
            if not self.client.is_connected():
                await self.client.start(bot_token=self.bot_token)
            
            # Execute search based on content type
            crawler_func = self.content_types[content_type]
            results = await crawler_func(query, max_results, channel_username)
            
            self.logger.info(f"Found {len(results)} Telegram {content_type} for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching Telegram content: {str(e)}")
            return []
    
    async def _crawl_messages(self, query: str, max_results: int, channel_username: str = None) -> List[CrawlerResult]:
        """Crawl Telegram messages"""        try:
            results = []
            
            if not self.client:
                return []
            
            # Get channels to search
            channels_to_search = []
            if channel_username:
                try:
                    entity = await self.client.get_entity(channel_username)
                    channels_to_search.append(entity)
                except Exception as e:
                    self.logger.error(f"Error getting channel {channel_username}: {str(e)}")
                    return []
            else:
                # Get all dialogs/chats
                async for dialog in self.client.iter_dialogs():
                    if hasattr(dialog.entity, 'broadcast') or hasattr(dialog.entity, 'megagroup'):
                        channels_to_search.append(dialog.entity)
                        if len(channels_to_search) >= 10:  # Limit for safety
                            break
            
            # Search messages in channels
            for channel in channels_to_search:
                try:
                    message_count = 0
                    async for message in self.client.iter_messages(channel, limit=100):
                        # Filter by query
                        if query and query.lower() not in message.text.lower():
                            continue
                        
                        # Parse message data
                        telegram_message = await self._parse_message_data(message, channel)
                        if telegram_message:
                            result = CrawlerResult(
                                url=telegram_message.message_link,
                                title=f"Message from {telegram_message.chat_title}",
                                content=telegram_message.text,
                                metadata={
                                    'message_data': asdict(telegram_message),
                                    'platform': 'telegram',
                                    'content_type': 'message',
                                    'channel_title': telegram_message.chat_title,
                                    'channel_username': telegram_message.chat_username,
                                    'sender_username': telegram_message.sender_username,
                                    'views': telegram_message.views,
                                    'forwards': telegram_message.forwards,
                                    'media_type': telegram_message.media_type,
                                    'is_reply': telegram_message.is_reply
                                },
                                timestamp=telegram_message.date,
                                similarity_score=0.0
                            )
                            results.append(result)
                            message_count += 1
                            
                            if message_count >= max_results // len(channels_to_search):
                                break
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                    
                except Exception as e:
                    self.logger.error(f"Error crawling channel {channel}: {str(e)}")
                    continue
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Telegram messages: {str(e)}")
            return []
    
    async def _crawl_channels(self, query: str, max_results: int, channel_username: str = None) -> List[CrawlerResult]:
        """Crawl Telegram channels"""        try:
            results = []
            
            if not self.client:
                return []
            
            # Search for channels
            if channel_username:
                # Get specific channel
                try:
                    entity = await self.client.get_entity(channel_username)
                    if hasattr(entity, 'broadcast') or hasattr(entity, 'megagroup'):
                        channel_data = await self._get_detailed_channel_info(entity)
                        if channel_data:
                            result = CrawlerResult(
                                url=channel_data.channel_link,
                                title=channel_data.title,
                                content=f"Channel: {channel_data.title} - {channel_data.about}",
                                metadata={
                                    'channel_data': asdict(channel_data),
                                    'platform': 'telegram',
                                    'content_type': 'channel',
                                    'participants_count': channel_data.participants_count,
                                    'is_verified': channel_data.is_verified,
                                    'is_megagroup': channel_data.is_megagroup,
                                    'username': channel_data.username
                                },
                                timestamp=channel_data.created_date or datetime.utcnow(),
                                similarity_score=0.0
                            )
                            results.append(result)
                except Exception as e:
                    self.logger.error(f"Error getting channel {channel_username}: {str(e)}")
            else:
                # Get all channels from dialogs
                async for dialog in self.client.iter_dialogs():
                    entity = dialog.entity
                    if hasattr(entity, 'broadcast') or hasattr(entity, 'megagroup'):
                        # Filter by query
                        if query and query.lower() not in entity.title.lower():
                            continue
                        
                        channel_data = await self._get_detailed_channel_info(entity)
                        if channel_data:
                            result = CrawlerResult(
                                url=channel_data.channel_link,
                                title=channel_data.title,
                                content=f"Channel: {channel_data.title} - {channel_data.about}",
                                metadata={
                                    'channel_data': asdict(channel_data),
                                    'platform': 'telegram',
                                    'content_type': 'channel',
                                    'participants_count': channel_data.participants_count,
                                    'is_verified': channel_data.is_verified,
                                    'is_megagroup': channel_data.is_megagroup,
                                    'username': channel_data.username
                                },
                                timestamp=channel_data.created_date or datetime.utcnow(),
                                similarity_score=0.0
                            )
                            results.append(result)
                            
                            if len(results) >= max_results:
                                break
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Telegram channels: {str(e)}")
            return []
    
    async def _crawl_users(self, query: str, max_results: int, channel_username: str = None) -> List[CrawlerResult]:
        """Crawl Telegram users"""        try:
            results = []
            
            if not self.client:
                return []
            
            # Get users from recent messages
            seen_users = set()
            
            # Get channels to search for users
            channels_to_search = []
            if channel_username:
                try:
                    entity = await self.client.get_entity(channel_username)
                    channels_to_search.append(entity)
                except Exception as e:
                    self.logger.error(f"Error getting channel {channel_username}: {str(e)}")
                    return []
            else:
                # Get some channels from dialogs
                async for dialog in self.client.iter_dialogs():
                    if hasattr(dialog.entity, 'megagroup'):  # Only megagroups show user info
                        channels_to_search.append(dialog.entity)
                        if len(channels_to_search) >= 5:  # Limit for safety
                            break
            
            # Get users from channel messages
            for channel in channels_to_search:
                try:
                    async for message in self.client.iter_messages(channel, limit=50):
                        if message.sender_id and message.sender_id not in seen_users:
                            sender = await message.get_sender()
                            if sender and hasattr(sender, 'username'):
                                # Filter by query
                                username = getattr(sender, 'username', '') or ''
                                first_name = getattr(sender, 'first_name', '') or ''
                                if query and query.lower() not in username.lower() and query.lower() not in first_name.lower():
                                    continue
                                
                                seen_users.add(message.sender_id)
                                
                                user_data = await self._parse_user_data(sender)
                                if user_data:
                                    result = CrawlerResult(
                                        url=f"https://t.me/{user_data.username}" if user_data.username else f"tg://user?id={user_data.user_id}",
                                        title=f"Telegram User: {user_data.first_name}",
                                        content=f"User: {user_data.first_name} (@{user_data.username}) - {user_data.bio}",
                                        metadata={
                                            'user_data': asdict(user_data),
                                            'platform': 'telegram',
                                            'content_type': 'user',
                                            'username': user_data.username,
                                            'is_bot': user_data.is_bot,
                                            'is_verified': user_data.is_verified,
                                            'is_premium': user_data.is_premium,
                                            'common_chats_count': user_data.common_chats_count
                                        },
                                        timestamp=datetime.utcnow(),
                                        similarity_score=0.0
                                    )
                                    results.append(result)
                                    
                                    if len(results) >= max_results:
                                        return results
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                    
                except Exception as e:
                    self.logger.error(f"Error getting users from channel {channel}: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error crawling Telegram users: {str(e)}")
            return []
    
    async def _crawl_search(self, query: str, max_results: int, channel_username: str = None) -> List[CrawlerResult]:
        """General Telegram search across all content types"""        try:
            results = []
            
            # Search across different content types
            messages = await self._crawl_messages(query, max_results // 2, channel_username)
            channels = await self._crawl_channels(query, max_results // 4, channel_username)
            users = await self._crawl_users(query, max_results // 4, channel_username)
            
            results.extend(messages)
            results.extend(channels)
            results.extend(users)
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error performing Telegram search: {str(e)}")
            return []
    
    async def _crawl_media(self, query: str, max_results: int, channel_username: str = None) -> List[CrawlerResult]:
        """Crawl media messages on Telegram"""        try:
            results = []
            
            if not self.client:
                return []
            
            # Get channels to search
            channels_to_search = []
            if channel_username:
                try:
                    entity = await self.client.get_entity(channel_username)
                    channels_to_search.append(entity)
                except Exception as e:
                    self.logger.error(f"Error getting channel {channel_username}: {str(e)}")
                    return []
            else:
                # Get channels from dialogs
                async for dialog in self.client.iter_dialogs():
                    if hasattr(dialog.entity, 'broadcast') or hasattr(dialog.entity, 'megagroup'):
                        channels_to_search.append(dialog.entity)
                        if len(channels_to_search) >= 10:
                            break
            
            # Search for media messages
            for channel in channels_to_search:
                try:
                    media_count = 0
                    async for message in self.client.iter_messages(channel, limit=100):
                        # Only process messages with media
                        if not message.media:
                            continue
                        
                        # Filter by query in caption or filename
                        caption = message.text or ''
                        if query and query.lower() not in caption.lower():
                            continue
                        
                        telegram_message = await self._parse_message_data(message, channel)
                        if telegram_message and telegram_message.media_type:
                            result = CrawlerResult(
                                url=telegram_message.message_link,
                                title=f"[{telegram_message.media_type.upper()}] Media from {telegram_message.chat_title}",
                                content=telegram_message.text,
                                metadata={
                                    'message_data': asdict(telegram_message),
                                    'platform': 'telegram',
                                    'content_type': 'media',
                                    'media_type': telegram_message.media_type,
                                    'file_size': telegram_message.file_size,
                                    'file_name': telegram_message.file_name,
                                    'mime_type': telegram_message.mime_type,
                                    'duration': telegram_message.duration,
                                    'dimensions': f"{telegram_message.width}x{telegram_message.height}" if telegram_message.width else None
                                },
                                timestamp=telegram_message.date,
                                similarity_score=0.0
                            )
                            results.append(result)
                            media_count += 1
                            
                            if media_count >= max_results // len(channels_to_search):
                                break
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                    
                except Exception as e:
                    self.logger.error(f"Error crawling media from channel {channel}: {str(e)}")
                    continue
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Telegram media: {str(e)}")
            return []
    
    async def _crawl_forwards(self, query: str, max_results: int, channel_username: str = None) -> List[CrawlerResult]:
        """Crawl forwarded messages"""        try:
            results = []
            
            if not self.client:
                return []
            
            # Get channels to search
            channels_to_search = []
            if channel_username:
                try:
                    entity = await self.client.get_entity(channel_username)
                    channels_to_search.append(entity)
                except Exception as e:
                    self.logger.error(f"Error getting channel {channel_username}: {str(e)}")
                    return []
            else:
                # Get channels from dialogs
                async for dialog in self.client.iter_dialogs():
                    if hasattr(dialog.entity, 'broadcast') or hasattr(dialog.entity, 'megagroup'):
                        channels_to_search.append(dialog.entity)
                        if len(channels_to_search) >= 10:
                            break
            
            # Search for forwarded messages
            for channel in channels_to_search:
                try:
                    forward_count = 0
                    async for message in self.client.iter_messages(channel, limit=100):
                        # Only process forwarded messages
                        if not message.forward:
                            continue
                        
                        # Filter by query
                        if query and query.lower() not in message.text.lower():
                            continue
                        
                        telegram_message = await self._parse_message_data(message, channel)
                        if telegram_message and telegram_message.forward_info:
                            result = CrawlerResult(
                                url=telegram_message.message_link,
                                title=f"[FORWARDED] Message from {telegram_message.chat_title}",
                                content=telegram_message.text,
                                metadata={
                                    'message_data': asdict(telegram_message),
                                    'platform': 'telegram',
                                    'content_type': 'forwarded_message',
                                    'forward_info': telegram_message.forward_info,
                                    'original_source': telegram_message.forward_info.get('from_name') if telegram_message.forward_info else None
                                },
                                timestamp=telegram_message.date,
                                similarity_score=0.0
                            )
                            results.append(result)
                            forward_count += 1
                            
                            if forward_count >= max_results // len(channels_to_search):
                                break
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                    
                except Exception as e:
                    self.logger.error(f"Error crawling forwards from channel {channel}: {str(e)}")
                    continue
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Telegram forwards: {str(e)}")
            return []
    
    async def _crawl_reactions(self, query: str, max_results: int, channel_username: str = None) -> List[CrawlerResult]:
        """Crawl messages with reactions"""        try:
            results = []
            
            if not self.client:
                return []
            
            # Get channels to search
            channels_to_search = []
            if channel_username:
                try:
                    entity = await self.client.get_entity(channel_username)
                    channels_to_search.append(entity)
                except Exception as e:
                    self.logger.error(f"Error getting channel {channel_username}: {str(e)}")
                    return []
            else:
                # Get channels from dialogs
                async for dialog in self.client.iter_dialogs():
                    if hasattr(dialog.entity, 'broadcast') or hasattr(dialog.entity, 'megagroup'):
                        channels_to_search.append(dialog.entity)
                        if len(channels_to_search) >= 10:
                            break
            
            # Search for messages with reactions
            for channel in channels_to_search:
                try:
                    reaction_count = 0
                    async for message in self.client.iter_messages(channel, limit=100):
                        # Only process messages with reactions
                        if not hasattr(message, 'reactions') or not message.reactions:
                            continue
                        
                        # Filter by query
                        if query and query.lower() not in message.text.lower():
                            continue
                        
                        telegram_message = await self._parse_message_data(message, channel)
                        if telegram_message and telegram_message.reactions:
                            result = CrawlerResult(
                                url=telegram_message.message_link,
                                title=f"[REACTIONS] Message from {telegram_message.chat_title}",
                                content=telegram_message.text,
                                metadata={
                                    'message_data': asdict(telegram_message),
                                    'platform': 'telegram',
                                    'content_type': 'reaction_message',
                                    'reactions': telegram_message.reactions,
                                    'total_reactions': sum(r.get('count', 0) for r in telegram_message.reactions.get('results', []))
                                },
                                timestamp=telegram_message.date,
                                similarity_score=0.0
                            )
                            results.append(result)
                            reaction_count += 1
                            
                            if reaction_count >= max_results // len(channels_to_search):
                                break
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))
                    
                except Exception as e:
                    self.logger.error(f"Error crawling reactions from channel {channel}: {str(e)}")
                    continue
            
            return results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Error crawling Telegram reactions: {str(e)}")
            return []
    
    # Helper methods
    
    async def _parse_message_data(self, message, channel) -> Optional[TelegramMessage]:
        """Parse message data from Telegram API"""        try:
            # Get sender information
            sender = await message.get_sender() if message.sender_id else None
            
            # Parse forward information
            forward_info = None
            if message.forward:
                forward_info = {
                    'from_id': getattr(message.forward.from_id, 'user_id', None) if message.forward.from_id else None,
                    'from_name': message.forward.from_name,
                    'channel_post': message.forward.channel_post,
                    'post_author': message.forward.post_author,
                    'saved_from_peer': str(message.forward.saved_from_peer) if message.forward.saved_from_peer else None,
                    'saved_from_msg_id': message.forward.saved_from_msg_id,
                    'date': message.forward.date
                }
            
            # Parse media information
            media_type = None
            media_info = None
            file_info = {}
            
            if message.media:
                if isinstance(message.media, MessageMediaPhoto):
                    media_type = 'photo'
                    if message.photo:
                        file_info.update({
                            'file_id': str(message.photo.id),
                            'file_size': sum(size.size for size in message.photo.sizes if hasattr(size, 'size')),
                            'width': max((size.w for size in message.photo.sizes if hasattr(size, 'w')), default=0),
                            'height': max((size.h for size in message.photo.sizes if hasattr(size, 'h')), default=0)
                        })
                
                elif isinstance(message.media, MessageMediaDocument):
                    if message.document:
                        # Determine document type
                        mime_type = message.document.mime_type or ''
                        if mime_type.startswith('video/'):
                            media_type = 'video'
                        elif mime_type.startswith('audio/'):
                            media_type = 'audio'
                        elif mime_type.startswith('image/'):
                            media_type = 'image'
                        else:
                            media_type = 'document'
                        
                        file_info.update({
                            'file_id': str(message.document.id),
                            'file_size': message.document.size,
                            'mime_type': message.document.mime_type,
                            'file_name': next((attr.file_name for attr in message.document.attributes 
                                             if hasattr(attr, 'file_name')), None)
                        })
                        
                        # Get video/audio specific attributes
                        for attr in message.document.attributes:
                            if hasattr(attr, 'duration'):
                                file_info['duration'] = attr.duration
                            if hasattr(attr, 'w') and hasattr(attr, 'h'):
                                file_info['width'] = attr.w
                                file_info['height'] = attr.h
                
                elif isinstance(message.media, MessageMediaWebPage):
                    media_type = 'webpage'
                    if message.media.webpage:
                        media_info = {
                            'url': message.media.webpage.url,
                            'display_url': message.media.webpage.display_url,
                            'title': message.media.webpage.title,
                            'description': message.media.webpage.description,
                            'site_name': message.media.webpage.site_name
                        }
            
            # Parse reactions
            reactions = None
            if hasattr(message, 'reactions') and message.reactions:
                reactions = {
                    'results': [
                        {
                            'reaction': str(reaction.reaction),
                            'count': reaction.count,
                            'chosen': reaction.chosen
                        }
                        for reaction in message.reactions.results
                    ],
                    'min': message.reactions.min,
                    'can_see_list': message.reactions.can_see_list,
                    'recent_reactors': [str(peer) for peer in (message.reactions.recent_reactors or [])]
                }
            
            # Parse entities (mentions, hashtags, etc.)
            entities = []
            if message.entities:
                for entity in message.entities:
                    entities.append({
                        'type': type(entity).__name__,
                        'offset': entity.offset,
                        'length': entity.length,
                        'url': getattr(entity, 'url', None),
                        'user_id': getattr(entity, 'user_id', None)
                    })
            
            # Create message link
            channel_username = getattr(channel, 'username', None)
            if channel_username:
                message_link = f"https://t.me/{channel_username}/{message.id}"
            else:
                message_link = f"https://t.me/c/{channel.id}/{message.id}"
            
            telegram_message = TelegramMessage(
                message_id=message.id,
                chat_id=message.chat_id,
                chat_username=getattr(channel, 'username', None),
                chat_title=getattr(channel, 'title', ''),
                sender_id=message.sender_id,
                sender_username=getattr(sender, 'username', None) if sender else None,
                sender_first_name=getattr(sender, 'first_name', None) if sender else None,
                sender_last_name=getattr(sender, 'last_name', None) if sender else None,
                text=message.text or '',
                raw_text=message.raw_text or '',
                date=message.date,
                edit_date=message.edit_date,
                is_reply=message.is_reply,
                reply_to_msg_id=message.reply_to_msg_id,
                forward_info=forward_info,
                views=getattr(message, 'views', None),
                forwards=getattr(message, 'forwards', None),
                replies=getattr(message.replies, 'replies', None) if hasattr(message, 'replies') and message.replies else None,
                reactions=reactions,
                media_type=media_type,
                media_info=media_info,
                file_id=file_info.get('file_id'),
                file_size=file_info.get('file_size'),
                file_name=file_info.get('file_name'),
                mime_type=file_info.get('mime_type'),
                duration=file_info.get('duration'),
                width=file_info.get('width'),
                height=file_info.get('height'),
                has_media_spoiler=getattr(message, 'media_spoiler', False),
                is_scheduled=getattr(message, 'scheduled', False),
                is_pinned=getattr(message, 'pinned', False),
                is_silent=getattr(message, 'silent', False),
                post_author=getattr(message, 'post_author', None),
                grouped_id=getattr(message, 'grouped_id', None),
                restriction_reason=getattr(message, 'restriction_reason', None),
                ttl_period=getattr(message, 'ttl_period', None),
                web_preview=media_info if media_type == 'webpage' else None,
                entities=entities,
                message_link=message_link,
                language=None,  # Would need language detection
                sentiment_score=None  # Would need sentiment analysis
            )
            
            return telegram_message
            
        except Exception as e:
            self.logger.error(f"Error parsing message data: {str(e)}")
            return None
    
    async def _get_detailed_channel_info(self, channel) -> Optional[TelegramChannel]:
        """Get detailed channel information"""        try:
            # Get full channel information
            full_channel = await self.client(GetFullChannelRequest(channel))
            full_info = full_channel.full_chat
            
            # Get recent messages
            recent_messages = []
            async for message in self.client.iter_messages(channel, limit=10):
                telegram_message = await self._parse_message_data(message, channel)
                if telegram_message:
                    recent_messages.append(telegram_message)
            
            # Create channel link
            username = getattr(channel, 'username', None)
            if username:
                channel_link = f"https://t.me/{username}"
            else:
                channel_link = f"https://t.me/c/{channel.id}"
            
            telegram_channel = TelegramChannel(
                channel_id=channel.id,
                username=getattr(channel, 'username', None),
                title=getattr(channel, 'title', ''),
                about=getattr(full_info, 'about', None),
                chat_photo=str(channel.photo) if getattr(channel, 'photo', None) else None,
                participants_count=getattr(full_info, 'participants_count', 0),
                admins_count=getattr(full_info, 'admins_count', None),
                kicked_count=getattr(full_info, 'kicked_count', None),
                banned_count=getattr(full_info, 'banned_count', None),
                online_count=getattr(full_info, 'online_count', None),
                created_date=getattr(channel, 'date', None),
                is_broadcast=getattr(channel, 'broadcast', False),
                is_megagroup=getattr(channel, 'megagroup', False),
                is_verified=getattr(channel, 'verified', False),
                is_restricted=getattr(channel, 'restricted', False),
                is_scam=getattr(channel, 'scam', False),
                is_fake=getattr(channel, 'fake', False),
                has_location=getattr(channel, 'has_location', False),
                has_link=getattr(channel, 'has_link', False),
                has_geo=getattr(channel, 'has_geo', False),
                can_view_participants=getattr(full_info, 'can_view_participants', False),
                can_set_username=getattr(full_info, 'can_set_username', False),
                can_set_stickers=getattr(full_info, 'can_set_stickers', False),
                can_set_location=getattr(full_info, 'can_set_location', False),
                can_view_stats=getattr(full_info, 'can_view_stats', False),
                default_banned_rights=None,  # Would need detailed parsing
                migrated_from_chat_id=getattr(full_info, 'migrated_from_chat_id', None),
                migrated_from_max_id=getattr(full_info, 'migrated_from_max_id', None),
                pinned_msg_id=getattr(full_info, 'pinned_msg_id', None),
                stickerset=None,  # Would need detailed parsing
                available_min_id=getattr(full_info, 'available_min_id', 0),
                folder_id=getattr(full_info, 'folder_id', None),
                linked_chat_id=getattr(full_info, 'linked_chat_id', None),
                location=None,  # Would need detailed parsing
                slowmode_seconds=getattr(full_info, 'slowmode_seconds', None),
                slowmode_next_send_date=getattr(full_info, 'slowmode_next_send_date', None),
                stats=None,  # Would need additional API calls
                channel_link=channel_link,
                recent_messages=recent_messages,
                growth_rate=None,  # Would need calculation
                engagement_rate=None  # Would need calculation
            )
            
            return telegram_channel
            
        except Exception as e:
            self.logger.error(f"Error getting detailed channel info: {str(e)}")
            return None
    
    async def _parse_user_data(self, user) -> Optional[TelegramUser]:
        """Parse user data from Telegram API"""        try:
            # Get full user information if possible
            full_user = None
            try:
                full_user_result = await self.client(GetFullUserRequest(user))
                full_user = full_user_result.full_user
            except:
                pass
            
            telegram_user = TelegramUser(
                user_id=user.id,
                username=getattr(user, 'username', None),
                first_name=getattr(user, 'first_name', ''),
                last_name=getattr(user, 'last_name', None),
                phone=getattr(user, 'phone', None),
                bio=getattr(full_user, 'about', None) if full_user else None,
                profile_photo=str(user.photo) if getattr(user, 'photo', None) else None,
                is_self=getattr(user, 'is_self', False),
                is_contact=getattr(user, 'contact', False),
                is_mutual_contact=getattr(user, 'mutual_contact', False),
                is_deleted=getattr(user, 'deleted', False),
                is_bot=getattr(user, 'bot', False),
                is_verified=getattr(user, 'verified', False),
                is_restricted=getattr(user, 'restricted', False),
                is_scam=getattr(user, 'scam', False),
                is_fake=getattr(user, 'fake', False),
                is_premium=getattr(user, 'premium', False),
                is_support=getattr(user, 'support', False),
                lang_code=getattr(user, 'lang_code', None),
                common_chats_count=getattr(full_user, 'common_chats_count', 0) if full_user else 0,
                blocked=getattr(full_user, 'blocked', False) if full_user else False,
                restriction_reason=None,  # Would need detailed parsing
                bot_chat_history=getattr(user, 'bot_chat_history', False),
                bot_nochats=getattr(user, 'bot_nochats', False),
                bot_inline_geo=getattr(user, 'bot_inline_geo', False),
                bot_info_version=getattr(user, 'bot_info_version', None),
                bot_inline_placeholder=getattr(user, 'bot_inline_placeholder', None),
                settings=None,  # Would need additional parsing
                personal_photo=None,  # Would need additional API calls
                fallback_photo=None,  # Would need additional API calls
                pinned_msg_id=getattr(full_user, 'pinned_msg_id', None) if full_user else None,
                folder_id=getattr(full_user, 'folder_id', None) if full_user else None,
                ttl_period=getattr(full_user, 'ttl_period', None) if full_user else None,
                theme_emoticon=getattr(full_user, 'theme_emoticon', None) if full_user else None,
                private_forward_name=getattr(full_user, 'private_forward_name', None) if full_user else None,
                bot_commands=[],  # Would need additional parsing
                status=None,  # Would need status parsing
                last_seen=None  # Would need status parsing
            )
            
            return telegram_user
            
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
        """Extract metadata from Telegram content"""        try:
            # Parse Telegram URL
            parsed_url = urlparse(url)
            
            metadata = {
                'platform': 'telegram',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }
            
            # Parse t.me URLs
            if 't.me' in parsed_url.netloc:
                path_parts = parsed_url.path.strip('/').split('/')
                
                if len(path_parts) >= 1:
                    username_or_id = path_parts[0]
                    
                    if username_or_id.startswith('c'):
                        # Private channel link
                        if len(path_parts) >= 3:
                            channel_id = path_parts[1]
                            message_id = path_parts[2]
                            metadata.update({
                                'channel_id': channel_id,
                                'message_id': message_id,
                                'content_type': 'message',
                                'is_private': True
                            })
                    else:
                        # Public channel/user
                        username = username_or_id
                        metadata['username'] = username
                        
                        if len(path_parts) >= 2:
                            message_id = path_parts[1]
                            metadata.update({
                                'message_id': message_id,
                                'content_type': 'message'
                            })
                        else:
                            metadata['content_type'] = 'channel_or_user'
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting Telegram metadata: {str(e)}")
            return {'error': str(e)}
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get Telegram platform information"""        return {
            'platform_name': 'Telegram',
            'base_url': self.base_url,
            'supported_content_types': list(self.content_types.keys()),
            'rate_limits': {
                'requests_per_minute': self.requests_per_minute,
                'min_delay': self.min_delay,
                'max_delay': self.max_delay
            },
            'features': [
                'Channel and group monitoring',
                'Message content analysis',
                'Media file tracking',
                'User activity analysis',
                'Real-time message streaming',
                'Forward chain tracking',
                'Reaction and engagement metrics',
                'Bot interaction monitoring',
                'Privacy-respecting crawling'
            ],
            'authentication': {
                'required': True,
                'type': 'Telegram API credentials',
                'scope': 'Bot token or user session'
            },
            'limitations': [
                'Strict rate limiting',
                'Requires API credentials',
                'Private chats not accessible',
                'Some features require user permissions',
                'Bot limitations for certain data'
            ]
        }
