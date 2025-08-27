"""
Telegram Crawling Engine
=======================

Advanced Telegram crawler for content monitoring and channel analysis.
Handles channels, groups, messages, and media extraction.

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
from pathlib import Path

import aiohttp
from telethon import TelegramClient, events
from telethon.tl.types import (
    Channel, Chat, User, MessageMediaPhoto, MessageMediaDocument,
    MessageMediaVideo, MessageMediaAudio, MessageMediaContact,
    MessageMediaGeo, MessageMediaVenue, MessageMediaPoll
)
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import SessionPasswordNeededError, FloodWaitError
import requests

from ..core.base_engine import BaseCrawlerEngine
from ..core.exceptions import (
    CrawlerError, 
    RateLimitError, 
    AuthenticationError,
    ContentNotFoundError,
    ChannelPrivateError
)
from ..utils.rate_limiter import RateLimiter
from ..utils.cache_manager import CacheManager
from ..models.content_models import MessageContent, ChannelContent, MediaContent
from ...core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class TelegramMessageData:
    """Telegram message data structure"""
    message_id: int
    channel_id: int
    channel_username: str
    sender_id: int
    sender_username: str
    sender_first_name: str
    sender_last_name: str
    date: datetime
    message: str
    raw_text: str
    media_type: Optional[str]
    media_caption: Optional[str]
    media_url: Optional[str]
    media_file_name: Optional[str]
    media_file_size: Optional[int]
    media_duration: Optional[int]
    views: Optional[int]
    forwards: Optional[int]
    replies: Optional[int]
    reactions: List[Dict[str, Any]]
    mentioned_users: List[str]
    hashtags: List[str]
    urls: List[str]
    is_outgoing: bool
    is_channel_post: bool
    is_group_message: bool
    is_private_message: bool
    is_reply: bool
    reply_to_msg_id: Optional[int]
    is_forwarded: bool
    forward_from_channel: Optional[str]
    forward_from_user: Optional[str]
    edit_date: Optional[datetime] = None
    edit_hide: bool = False
    grouped_id: Optional[int] = None
    restriction_reason: Optional[str] = None


@dataclass
class TelegramChannelData:
    """Telegram channel data structure"""
    channel_id: int
    username: str
    title: str
    about: str
    participants_count: int
    admins_count: int
    kicked_count: int
    banned_count: int
    online_count: int
    read_inbox_max_id: int
    read_outbox_max_id: int
    unread_count: int
    chat_photo: Optional[str]
    notify_settings: Dict[str, Any]
    exported_invite: Optional[str]
    bot_info: List[Dict[str, Any]]
    pinned_msg_id: Optional[int]
    folder_id: Optional[int]
    call: Optional[Dict[str, Any]]
    ttl_period: Optional[int]
    pending_suggestions: List[str]
    groupcall_default_join_as: Optional[str]
    theme_emoticon: Optional[str]
    requests_pending: Optional[int]
    recent_requesters: List[int]
    default_send_as: Optional[str]
    available_reactions: List[str]
    created_date: Optional[datetime] = None
    restriction_reason: Optional[str] = None
    is_broadcast: bool = False
    is_megagroup: bool = False
    is_verified: bool = False
    is_restricted: bool = False
    is_scam: bool = False
    is_fake: bool = False
    has_geo: bool = False
    has_link: bool = False
    slowmode_enabled: bool = False


@dataclass
class TelegramChatData:
    """Telegram chat/group data structure"""
    chat_id: int
    title: str
    participants_count: int
    date: datetime
    version: int
    migrated_to: Optional[int]
    admin_rights: Optional[Dict[str, Any]]
    default_banned_rights: Optional[Dict[str, Any]]
    participants: List[Dict[str, Any]]
    chat_photo: Optional[str]
    invite_link: Optional[str]
    pinned_msg_id: Optional[int]
    is_creator: bool = False
    is_left: bool = False
    is_deactivated: bool = False
    is_call_active: bool = False
    is_call_not_empty: bool = False
    is_forbidden: bool = False


class TelegramCrawlerEngine(BaseCrawlerEngine):
    """
    Advanced Telegram crawler engine with comprehensive API integration.
    
    Features:
    - Telethon library integration
    - Channel and group monitoring
    - Message history extraction
    - Media content download
    - Real-time message monitoring
    - User and admin analysis
    - Forward tracking
    - Reaction monitoring
    """

    def __init__(self, 
                 api_id: Optional[int] = None,
                 api_hash: Optional[str] = None,
                 session_name: str = 'telegram_crawler',
                 phone_number: Optional[str] = None,
                 password: Optional[str] = None,
                 proxy_config: Optional[Dict] = None,
                 rate_limit_config: Optional[Dict] = None):
        """
        Initialize Telegram crawler engine.
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API hash
            session_name: Session file name
            phone_number: Phone number for authentication
            password: 2FA password if enabled
            proxy_config: Proxy configuration
            rate_limit_config: Rate limiting configuration
        """
        super().__init__()
        
        # API Configuration
        self.api_id = api_id or settings.TELEGRAM_API_ID
        self.api_hash = api_hash or settings.TELEGRAM_API_HASH
        self.session_name = session_name
        self.phone_number = phone_number or settings.TELEGRAM_PHONE_NUMBER
        self.password = password or settings.TELEGRAM_PASSWORD
        
        # Telegram client
        self.client = None
        self.is_authenticated = False
        
        # Rate limiting (Telegram has strict limits)
        rate_config = rate_limit_config or {
            'requests_per_second': 1,  # Very conservative for Telegram
            'requests_per_minute': 20,
            'requests_per_hour': 1200,
            'burst_limit': 5
        }
        self.rate_limiter = RateLimiter(**rate_config)
        
        # Cache manager
        self.cache_manager = CacheManager(
            cache_type='redis',
            ttl=1800,  # 30 minute cache
            key_prefix='telegram_'
        )
        
        # Proxy configuration
        self.proxy_config = proxy_config

    async def authenticate(self) -> bool:
        """Authenticate with Telegram API"""
        try:
            # Initialize client
            if self.proxy_config:
                import socks
                self.client = TelegramClient(
                    self.session_name,
                    self.api_id,
                    self.api_hash,
                    proxy=(
                        socks.SOCKS5,
                        self.proxy_config.get('host'),
                        self.proxy_config.get('port'),
                        True,
                        self.proxy_config.get('username'),
                        self.proxy_config.get('password')
                    )
                )
            else:
                self.client = TelegramClient(
                    self.session_name,
                    self.api_id,
                    self.api_hash
                )
            
            # Connect to Telegram
            await self.client.connect()
            
            # Check if already authenticated
            if await self.client.is_user_authorized():
                self.is_authenticated = True
                me = await self.client.get_me()
                logger.info(f"Authenticated Telegram user: {me.first_name} {me.last_name}")
                return True
            
            # Send code request
            if self.phone_number:
                await self.client.send_code_request(self.phone_number)
                logger.info("Telegram authentication code sent. Manual intervention required.")
                return False  # Manual code input required
            
            return False
        
        except Exception as e:
            logger.error(f"Telegram authentication failed: {e}")
            return False

    async def complete_authentication(self, code: str) -> bool:
        """Complete authentication with received code"""
        try:
            await self.client.sign_in(self.phone_number, code)
            self.is_authenticated = True
            me = await self.client.get_me()
            logger.info(f"Telegram authentication completed: {me.first_name} {me.last_name}")
            return True
        
        except SessionPasswordNeededError:
            if self.password:
                await self.client.sign_in(password=self.password)
                self.is_authenticated = True
                return True
            else:
                logger.error("2FA password required but not provided")
                return False
        
        except Exception as e:
            logger.error(f"Telegram authentication completion failed: {e}")
            return False

    async def get_channel_info(self, channel_username: str) -> TelegramChannelData:
        """
        Get Telegram channel information.
        
        Args:
            channel_username: Channel username (with or without @)
        
        Returns:
            TelegramChannelData object
        """
        if not self.is_authenticated:
            raise AuthenticationError("Telegram client not authenticated")

        cache_key = f"channel_info_{channel_username}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return TelegramChannelData(**cached_result)

        try:
            await self.rate_limiter.acquire()
            
            # Remove @ if present
            username = channel_username.lstrip('@')
            
            # Get channel entity
            channel = await self.client.get_entity(username)
            
            # Get full channel info
            full_channel = await self.client(GetFullChannelRequest(channel))
            
            channel_data = TelegramChannelData(
                channel_id=channel.id,
                username=getattr(channel, 'username', ''),
                title=channel.title,
                about=full_channel.full_chat.about,
                participants_count=full_channel.full_chat.participants_count,
                admins_count=full_channel.full_chat.admins_count,
                kicked_count=full_channel.full_chat.kicked_count,
                banned_count=full_channel.full_chat.banned_count,
                online_count=getattr(full_channel.full_chat, 'online_count', 0),
                read_inbox_max_id=full_channel.full_chat.read_inbox_max_id,
                read_outbox_max_id=full_channel.full_chat.read_outbox_max_id,
                unread_count=full_channel.full_chat.unread_count,
                chat_photo=str(full_channel.full_chat.chat_photo) if full_channel.full_chat.chat_photo else None,
                notify_settings=full_channel.full_chat.notify_settings.to_dict(),
                exported_invite=getattr(full_channel.full_chat, 'exported_invite', None),
                bot_info=[bot.to_dict() for bot in full_channel.full_chat.bot_info],
                pinned_msg_id=getattr(full_channel.full_chat, 'pinned_msg_id', None),
                folder_id=getattr(full_channel.full_chat, 'folder_id', None),
                call=getattr(full_channel.full_chat, 'call', None),
                ttl_period=getattr(full_channel.full_chat, 'ttl_period', None),
                pending_suggestions=getattr(full_channel.full_chat, 'pending_suggestions', []),
                groupcall_default_join_as=getattr(full_channel.full_chat, 'groupcall_default_join_as', None),
                theme_emoticon=getattr(full_channel.full_chat, 'theme_emoticon', None),
                requests_pending=getattr(full_channel.full_chat, 'requests_pending', None),
                recent_requesters=getattr(full_channel.full_chat, 'recent_requesters', []),
                default_send_as=getattr(full_channel.full_chat, 'default_send_as', None),
                available_reactions=getattr(full_channel.full_chat, 'available_reactions', []),
                created_date=getattr(channel, 'date', None),
                restriction_reason=getattr(channel, 'restriction_reason', None),
                is_broadcast=getattr(channel, 'broadcast', False),
                is_megagroup=getattr(channel, 'megagroup', False),
                is_verified=getattr(channel, 'verified', False),
                is_restricted=getattr(channel, 'restricted', False),
                is_scam=getattr(channel, 'scam', False),
                is_fake=getattr(channel, 'fake', False),
                has_geo=getattr(channel, 'has_geo', False),
                has_link=getattr(channel, 'has_link', False),
                slowmode_enabled=getattr(channel, 'slowmode_enabled', False)
            )
            
            # Cache result
            await self.cache_manager.set(cache_key, asdict(channel_data))
            
            return channel_data
        
        except Exception as e:
            logger.error(f"Error getting Telegram channel info: {e}")
            raise CrawlerError(f"Telegram channel info retrieval failed: {e}")

    async def get_channel_messages(self, 
                                 channel_username: str,
                                 limit: int = 100,
                                 offset_date: Optional[datetime] = None,
                                 offset_id: int = 0,
                                 min_id: int = 0,
                                 max_id: int = 0) -> List[TelegramMessageData]:
        """
        Get messages from a Telegram channel.
        
        Args:
            channel_username: Channel username
            limit: Maximum number of messages to return
            offset_date: Offset date for pagination
            offset_id: Offset message ID
            min_id: Minimum message ID
            max_id: Maximum message ID
        
        Returns:
            List of TelegramMessageData objects
        """
        if not self.is_authenticated:
            raise AuthenticationError("Telegram client not authenticated")

        cache_key = f"channel_messages_{channel_username}_{limit}_{offset_date}_{offset_id}"
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return [TelegramMessageData(**msg) for msg in cached_result]

        messages = []
        
        try:
            await self.rate_limiter.acquire()
            
            # Get channel entity
            username = channel_username.lstrip('@')
            channel = await self.client.get_entity(username)
            
            # Get messages
            async for message in self.client.iter_messages(
                channel,
                limit=limit,
                offset_date=offset_date,
                offset_id=offset_id,
                min_id=min_id,
                max_id=max_id
            ):
                message_data = await self._process_message_data(message, channel)
                if message_data:
                    messages.append(message_data)
            
            # Cache results
            await self.cache_manager.set(
                cache_key, 
                [asdict(msg) for msg in messages]
            )
        
        except FloodWaitError as e:
            logger.warning(f"Telegram flood wait: {e.seconds} seconds")
            raise RateLimitError(f"Rate limited for {e.seconds} seconds")
        
        except Exception as e:
            logger.error(f"Error getting Telegram channel messages: {e}")
            raise CrawlerError(f"Telegram channel messages retrieval failed: {e}")
        
        return messages

    async def search_messages(self, 
                            channel_username: str,
                            query: str,
                            limit: int = 100) -> List[TelegramMessageData]:
        """
        Search for messages in a Telegram channel.
        
        Args:
            channel_username: Channel username
            query: Search query
            limit: Maximum number of messages to return
        
        Returns:
            List of TelegramMessageData objects
        """
        if not self.is_authenticated:
            raise AuthenticationError("Telegram client not authenticated")

        messages = []
        
        try:
            await self.rate_limiter.acquire()
            
            # Get channel entity
            username = channel_username.lstrip('@')
            channel = await self.client.get_entity(username)
            
            # Search messages
            async for message in self.client.iter_messages(
                channel,
                search=query,
                limit=limit
            ):
                message_data = await self._process_message_data(message, channel)
                if message_data:
                    messages.append(message_data)
        
        except FloodWaitError as e:
            logger.warning(f"Telegram flood wait: {e.seconds} seconds")
            raise RateLimitError(f"Rate limited for {e.seconds} seconds")
        
        except Exception as e:
            logger.error(f"Error searching Telegram messages: {e}")
            raise CrawlerError(f"Telegram message search failed: {e}")
        
        return messages

    async def monitor_channels(self, 
                             channel_usernames: List[str],
                             keywords: List[str],
                             check_interval: int = 300) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Monitor Telegram channels for content matches.
        
        Args:
            channel_usernames: List of channel usernames to monitor
            keywords: Keywords to search for
            check_interval: Check interval in seconds
        
        Yields:
            Dictionary containing monitoring results
        """
        if not self.is_authenticated:
            raise AuthenticationError("Telegram client not authenticated")

        logger.info(f"Starting Telegram content monitoring for {len(channel_usernames)} channels")
        
        last_message_ids = {}
        
        while True:
            for channel_username in channel_usernames:
                try:
                    # Get recent messages
                    messages = await self.get_channel_messages(
                        channel_username,
                        limit=50
                    )
                    
                    # Track last seen message ID
                    last_seen = last_message_ids.get(channel_username, 0)
                    new_messages = [msg for msg in messages if msg.message_id > last_seen]
                    
                    if new_messages:
                        last_message_ids[channel_username] = max(msg.message_id for msg in new_messages)
                    
                    # Check for keyword matches
                    for message in new_messages:
                        content = f"{message.message} {message.media_caption or ''}".lower()
                        for keyword in keywords:
                            if keyword.lower() in content:
                                yield {
                                    'type': 'telegram_content_match',
                                    'platform': 'telegram',
                                    'channel': channel_username,
                                    'message_id': message.message_id,
                                    'keyword': keyword,
                                    'content': content[:500],
                                    'sender': message.sender_username,
                                    'date': message.date,
                                    'media_type': message.media_type,
                                    'views': message.views,
                                    'forwards': message.forwards,
                                    'hashtags': message.hashtags,
                                    'urls': message.urls
                                }
                
                except Exception as e:
                    logger.error(f"Error monitoring Telegram channel {channel_username}: {e}")
                    yield {
                        'type': 'error',
                        'platform': 'telegram',
                        'channel': channel_username,
                        'error': str(e),
                        'timestamp': datetime.now()
                    }
            
            await asyncio.sleep(check_interval)

    async def download_media(self, 
                           message: TelegramMessageData,
                           download_path: str = './downloads/') -> Optional[str]:
        """
        Download media from a Telegram message.
        
        Args:
            message: TelegramMessageData object
            download_path: Path to download directory
        
        Returns:
            Path to downloaded file or None if no media
        """
        if not self.is_authenticated:
            raise AuthenticationError("Telegram client not authenticated")

        try:
            if message.media_type and message.media_file_name:
                # Create download directory
                Path(download_path).mkdir(parents=True, exist_ok=True)
                
                # Get the actual message object
                channel = await self.client.get_entity(message.channel_username)
                msg = await self.client.get_messages(channel, ids=message.message_id)
                
                if msg and msg.media:
                    file_path = await self.client.download_media(
                        msg.media,
                        file=download_path
                    )
                    return file_path
            
            return None
        
        except Exception as e:
            logger.error(f"Error downloading Telegram media: {e}")
            return None

    async def _process_message_data(self, message, channel) -> Optional[TelegramMessageData]:
        """Process Telegram message into TelegramMessageData object"""
        try:
            # Extract sender information
            sender_id = getattr(message.sender, 'id', 0) if message.sender else 0
            sender_username = getattr(message.sender, 'username', '') if message.sender else ''
            sender_first_name = getattr(message.sender, 'first_name', '') if message.sender else ''
            sender_last_name = getattr(message.sender, 'last_name', '') if message.sender else ''
            
            # Extract media information
            media_type = None
            media_caption = None
            media_url = None
            media_file_name = None
            media_file_size = None
            media_duration = None
            
            if message.media:
                if isinstance(message.media, MessageMediaPhoto):
                    media_type = 'photo'
                elif isinstance(message.media, MessageMediaDocument):
                    media_type = 'document'
                    if message.media.document:
                        media_file_name = getattr(message.media.document, 'file_name', None)
                        media_file_size = getattr(message.media.document, 'size', None)
                elif isinstance(message.media, MessageMediaVideo):
                    media_type = 'video'
                    media_duration = getattr(message.media, 'duration', None)
                elif isinstance(message.media, MessageMediaAudio):
                    media_type = 'audio'
                    media_duration = getattr(message.media, 'duration', None)
                elif isinstance(message.media, MessageMediaContact):
                    media_type = 'contact'
                elif isinstance(message.media, MessageMediaGeo):
                    media_type = 'geo'
                elif isinstance(message.media, MessageMediaVenue):
                    media_type = 'venue'
                elif isinstance(message.media, MessageMediaPoll):
                    media_type = 'poll'
                
                # Get media caption
                if hasattr(message, 'caption') and message.caption:
                    media_caption = message.caption
            
            # Extract text content
            message_text = message.message or ''
            raw_text = message.raw_text or ''
            
            # Extract hashtags, mentions, and URLs
            hashtags = re.findall(r'#(\w+)', message_text)
            mentioned_users = re.findall(r'@(\w+)', message_text)
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_text)
            
            # Get reactions if available
            reactions = []
            if hasattr(message, 'reactions') and message.reactions:
                for reaction in message.reactions.results:
                    reactions.append({
                        'emoticon': reaction.reaction.emoticon if hasattr(reaction.reaction, 'emoticon') else '',
                        'count': reaction.count,
                        'chosen': reaction.chosen
                    })
            
            # Forward information
            forward_from_channel = None
            forward_from_user = None
            if message.forward:
                if hasattr(message.forward, 'from_id'):
                    if hasattr(message.forward.from_id, 'channel_id'):
                        forward_from_channel = str(message.forward.from_id.channel_id)
                    elif hasattr(message.forward.from_id, 'user_id'):
                        forward_from_user = str(message.forward.from_id.user_id)
            
            return TelegramMessageData(
                message_id=message.id,
                channel_id=channel.id,
                channel_username=getattr(channel, 'username', ''),
                sender_id=sender_id,
                sender_username=sender_username,
                sender_first_name=sender_first_name,
                sender_last_name=sender_last_name,
                date=message.date,
                message=message_text,
                raw_text=raw_text,
                media_type=media_type,
                media_caption=media_caption,
                media_url=media_url,
                media_file_name=media_file_name,
                media_file_size=media_file_size,
                media_duration=media_duration,
                views=getattr(message, 'views', None),
                forwards=getattr(message, 'forwards', None),
                replies=getattr(message, 'replies', {}).get('replies', None) if hasattr(message, 'replies') else None,
                reactions=reactions,
                mentioned_users=mentioned_users,
                hashtags=hashtags,
                urls=urls,
                is_outgoing=message.out,
                is_channel_post=hasattr(channel, 'broadcast') and channel.broadcast,
                is_group_message=hasattr(channel, 'megagroup') and channel.megagroup,
                is_private_message=isinstance(channel, User),
                is_reply=message.reply_to is not None,
                reply_to_msg_id=getattr(message.reply_to, 'reply_to_msg_id', None) if message.reply_to else None,
                is_forwarded=message.forward is not None,
                forward_from_channel=forward_from_channel,
                forward_from_user=forward_from_user,
                edit_date=getattr(message, 'edit_date', None),
                edit_hide=getattr(message, 'edit_hide', False),
                grouped_id=getattr(message, 'grouped_id', None),
                restriction_reason=getattr(message, 'restriction_reason', None)
            )
        
        except Exception as e:
            logger.error(f"Error processing Telegram message data: {e}")
            return None

    async def close(self):
        """Close Telegram client connection"""
        if self.client:
            await self.client.disconnect()

    def __del__(self):
        """Cleanup resources"""
        try:
            if self.client:
                asyncio.create_task(self.close())
        except:
            pass
