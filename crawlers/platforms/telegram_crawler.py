"""Telegram Platform Crawler
=========================

Enterprise-grade Telegram content crawler with ultra-advanced monitoring capabilities.
Implements Telegram Bot API and MTProto integration, intelligent channel and group monitoring, 
and real-time message content protection with AI-powered analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Features:
- Telegram Bot API and MTProto integration
- Real-time channel and group message monitoring
- AI-powered content classification and moderation
- Automated spam and violation detection
- Multi-channel content discovery and tracking
- Media file analysis and fingerprinting
- Comprehensive chat analytics and member behavior analysis
- Content fingerprinting for copyright protection
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, AsyncGenerator, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import re
import base64
import hashlib
from urllib.parse import urljoin

import aiohttp
from telethon import TelegramClient, events
from telethon.tl.types import (
    Channel, Chat, User, Message, MessageMediaPhoto, 
    MessageMediaDocument, MessageMediaVideo, MessageMediaAudio
)
from telethon.errors import SessionPasswordNeededError, FloodWaitError
import requests

from ..utils.rate_limiter import TelegramRateLimiter
from ..utils.proxy_manager import ProxyManager
from ..utils.user_agent_rotator import UserAgentRotator
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, RateLimitError, AuthenticationError
from ...database.models import CrawlResult, ContentMatch
from ...ai.content_protection.fingerprinting.text_fingerprint import TextFingerprinter
from ...ai.content_protection.fingerprinting.image_fingerprint import ImageFingerprinter
from ...ai.content_protection.fingerprinting.video_fingerprint import VideoFingerprinter
from ...ai.content_protection.fingerprinting.audio_fingerprint import AudioFingerprinter

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class TelegramMessage:
    """Telegram message data structure with enhanced analysis."""
    message_id: int
    text: Optional[str]
    date: datetime
    from_id: Optional[int]
    from_username: Optional[str]
    from_first_name: Optional[str]
    from_last_name: Optional[str]
    chat_id: int
    chat_title: Optional[str]
    chat_username: Optional[str]
    chat_type: str  # channel, group, supergroup, private
    # Message content analysis
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    media_file_id: Optional[str] = None
    forward_from: Optional[Dict] = None
    reply_to_message_id: Optional[int] = None
    views: Optional[int] = None
    forwards: Optional[int] = None
    replies: Optional[int] = None
    # Advanced analysis
    content_fingerprint: Optional[str] = None
    media_fingerprint: Optional[str] = None
    sentiment_score: Optional[float] = None
    toxicity_score: Optional[float] = None
    spam_probability: Optional[float] = None
    language: Optional[str] = None
    # Copyright protection
    copyright_matches: List[Dict] = None
    violation_flags: List[str] = None
    protection_status: Optional[str] = None
    # Engagement metrics
    engagement_rate: Optional[float] = None
    viral_score: Optional[float] = None

@dataclass
class TelegramChat:
    """Telegram chat (channel/group) data structure."""
    chat_id: int
    title: str
    username: Optional[str]
    description: Optional[str]
    chat_type: str  # channel, group, supergroup
    member_count: Optional[int]
    created_date: Optional[datetime]
    # Channel/Group features
    is_verified: bool = False
    is_scam: bool = False
    is_fake: bool = False
    is_restricted: bool = False
    is_megagroup: bool = False
    is_broadcast: bool = False
    # Analytics
    activity_score: Optional[float] = None
    growth_rate: Optional[float] = None
    engagement_metrics: Optional[Dict] = None
    # Content analysis
    primary_language: Optional[str] = None
    content_categories: List[str] = None
    # Moderation
    has_admin_rights: bool = False
    content_policy: Optional[Dict] = None
    monitoring_enabled: bool = False

@dataclass
class TelegramUser:
    """Telegram user data structure."""
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    is_bot: bool
    is_verified: bool
    is_premium: bool
    is_scam: bool
    is_fake: bool
    # Status and activity
    status: Optional[str] = None
    last_seen: Optional[datetime] = None
    # Analytics
    message_count: Optional[int] = None
    activity_score: Optional[float] = None
    # Behavior analysis
    toxicity_score: Optional[float] = None
    spam_reports: Optional[int] = None
    violation_history: List[Dict] = None

class TelegramCrawler:
    """
    Enterprise Telegram content crawler with advanced monitoring capabilities.
    
    Provides comprehensive Telegram content discovery, monitoring, and analysis
    with focus on channel management and content protection.
    """
    
    def __init__(self, 
                 api_id: int,
                 api_hash: str,
                 bot_token: str = None,
                 proxy_manager: ProxyManager = None,
                 rate_limiter: TelegramRateLimiter = None,
                 session_name: str = "telegram_crawler"):
        """
        Initialize Telegram crawler.
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API hash
            bot_token: Bot token for Bot API (optional)
            proxy_manager: Proxy manager instance
            rate_limiter: Rate limiter instance
            session_name: Session file name
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.proxy_manager = proxy_manager or ProxyManager()
        self.rate_limiter = rate_limiter or TelegramRateLimiter()
        self.session_name = session_name
        
        # Initialize fingerprinters
        self.text_fingerprinter = TextFingerprinter()
        self.image_fingerprinter = ImageFingerprinter()
        self.video_fingerprinter = VideoFingerprinter()
        self.audio_fingerprinter = AudioFingerprinter()
        
        # Telegram client setup
        self.client = TelegramClient(
            session_name,
            api_id,
            api_hash,
            proxy=self._get_proxy_config()
        )
        
        self.session = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Monitoring state
        self.monitored_chats = set()
        self.content_violations = []
        self.message_handlers = []
        
        # Setup event handlers
        self._setup_event_handlers()
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def initialize(self):
        """Initialize the crawler and Telegram client."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Start Telegram client
        await self.client.start(bot_token=self.bot_token)
        
        self.logger.info("Telegram crawler initialized")
        
    async def close(self):
        """Close the crawler and client connection."""
        if self.session:
            await self.session.close()
        
        if self.client:
            await self.client.disconnect()
            
        self.logger.info("Telegram crawler closed")
        
    def _get_proxy_config(self):
        """Get proxy configuration for Telegram client."""
        if self.proxy_manager:
            proxy_url = self.proxy_manager.get_proxy_sync()
            if proxy_url:
                # Parse proxy URL and return config
                # This would need to be implemented based on proxy format
                pass
        return None
        
    def _setup_event_handlers(self):
        """Setup Telegram event handlers."""
        
        @self.client.on(events.NewMessage)
        async def handle_new_message(event):
            if str(event.chat_id) in self.monitored_chats:
                await self._process_message(event.message)
        
        @self.client.on(events.MessageEdited)
        async def handle_message_edit(event):
            if str(event.chat_id) in self.monitored_chats:
                await self._process_message_edit(event.message)
        
        @self.client.on(events.ChatAction)
        async def handle_chat_action(event):
            if str(event.chat_id) in self.monitored_chats:
                await self._process_chat_action(event)
    
    async def search_channels(self, query: str, limit: int = 50) -> List[TelegramChat]:
        """
        Search for Telegram channels.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of channels matching criteria
        """
        try:
            await self.rate_limiter.acquire()
            
            # Search for channels using Telegram's search
            result = await self.client.get_dialogs(limit=limit)
            
            channels = []
            for dialog in result:
                if dialog.is_channel and query.lower() in dialog.title.lower():
                    chat_data = await self._parse_chat_data(dialog.entity)
                    channels.append(chat_data)
            
            self.logger.info(f"Found {len(channels)} channels matching query: {query}")
            return channels
            
        except FloodWaitError as e:
            self.logger.warning(f"Flood wait error: {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            raise RateLimitError(f"Telegram rate limit: wait {e.seconds} seconds")
        except Exception as e:
            self.logger.error(f"Channel search failed: {str(e)}")
            raise CrawlerError(f"Channel search error: {str(e)}")
    
    async def monitor_chat(self, chat_identifier: Union[str, int]) -> Dict:
        """
        Start monitoring a specific chat/channel.
        
        Args:
            chat_identifier: Chat username, ID, or invite link
            
        Returns:
            Monitoring configuration and status
        """
        try:
            # Get chat entity
            chat = await self.client.get_entity(chat_identifier)
            chat_id = str(chat.id)
            
            self.monitored_chats.add(chat_id)
            
            # Perform initial analysis
            chat_data = await self._analyze_chat(chat)
            
            monitoring_config = {
                'chat_id': chat_id,
                'chat_title': chat.title,
                'chat_type': self._get_chat_type(chat),
                'monitoring_started': datetime.utcnow(),
                'initial_analysis': asdict(chat_data)
            }
            
            self.logger.info(f"Started monitoring chat: {chat.title}")
            return monitoring_config
            
        except Exception as e:
            self.logger.error(f"Failed to start chat monitoring: {str(e)}")
            raise CrawlerError(f"Chat monitoring error: {str(e)}")
    
    async def get_chat_messages(self, 
                               chat_identifier: Union[str, int],
                               limit: int = 100,
                               min_id: int = 0,
                               max_id: int = 0,
                               from_user: Union[str, int] = None,
                               search: str = None) -> List[TelegramMessage]:
        """
        Get messages from a specific chat.
        
        Args:
            chat_identifier: Chat username, ID, or invite link
            limit: Maximum messages to return
            min_id: Get messages with ID greater than this
            max_id: Get messages with ID less than this
            from_user: Filter messages from specific user
            search: Text search query
            
        Returns:
            List of messages
        """
        try:
            await self.rate_limiter.acquire()
            
            chat = await self.client.get_entity(chat_identifier)
            
            messages = []
            async for message in self.client.iter_messages(
                chat,
                limit=limit,
                min_id=min_id,
                max_id=max_id,
                from_user=from_user,
                search=search
            ):
                message_data = await self._parse_message_data(message)
                messages.append(message_data)
            
            self.logger.info(f"Retrieved {len(messages)} messages from {chat.title}")
            return messages
            
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
            raise RateLimitError(f"Telegram rate limit: wait {e.seconds} seconds")
        except Exception as e:
            self.logger.error(f"Message retrieval failed: {str(e)}")
            raise CrawlerError(f"Message retrieval error: {str(e)}")
    
    async def detect_content_violations(self, 
                                       protected_content: List[str],
                                       similarity_threshold: float = 0.8) -> List[Dict]:
        """
        Detect potential content violations across monitored chats.
        
        Args:
            protected_content: List of protected content fingerprints
            similarity_threshold: Minimum similarity for violation
            
        Returns:
            List of potential violations
        """
        try:
            violations = []
            
            for chat_id in self.monitored_chats:
                try:
                    chat = await self.client.get_entity(int(chat_id))
                    
                    # Get recent messages
                    recent_messages = await self.get_chat_messages(
                        chat,
                        limit=100
                    )
                    
                    for message in recent_messages:
                        if not message.content_fingerprint:
                            continue
                        
                        # Check against protected content
                        for protected_fp in protected_content:
                            similarity = await self._calculate_content_similarity(
                                message.content_fingerprint,
                                protected_fp
                            )
                            
                            if similarity >= similarity_threshold:
                                violation = {
                                    'message_id': message.message_id,
                                    'chat_id': message.chat_id,
                                    'from_id': message.from_id,
                                    'content_similarity': similarity,
                                    'detected_at': datetime.utcnow(),
                                    'violation_type': 'content_similarity',
                                    'protected_content_id': protected_fp
                                }
                                violations.append(violation)
                                
                except Exception as e:
                    self.logger.warning(f"Failed to check chat {chat_id}: {str(e)}")
                    continue
            
            self.logger.info(f"Detected {len(violations)} potential violations")
            return violations
            
        except Exception as e:
            self.logger.error(f"Violation detection failed: {str(e)}")
            raise CrawlerError(f"Violation detection error: {str(e)}")
    
    async def get_chat_analytics(self, chat_identifier: Union[str, int]) -> Dict:
        """
        Get comprehensive analytics for a chat.
        
        Args:
            chat_identifier: Chat username, ID, or invite link
            
        Returns:
            Chat analytics data
        """
        try:
            chat = await self.client.get_entity(chat_identifier)
            
            # Get recent messages for analysis
            messages = await self.get_chat_messages(chat, limit=1000)
            
            if not messages:
                return {'error': 'No messages found'}
            
            # Calculate analytics
            total_messages = len(messages)
            total_views = sum(msg.views or 0 for msg in messages)
            total_forwards = sum(msg.forwards or 0 for msg in messages)
            
            # Activity analysis
            now = datetime.utcnow()
            last_24h = sum(1 for msg in messages if (now - msg.date).days < 1)
            last_7d = sum(1 for msg in messages if (now - msg.date).days < 7)
            
            # Engagement analysis
            avg_views = total_views / total_messages if total_messages > 0 else 0
            avg_forwards = total_forwards / total_messages if total_messages > 0 else 0
            
            # Content analysis
            media_count = sum(1 for msg in messages if msg.media_type)
            text_count = sum(1 for msg in messages if msg.text)
            
            analytics = {
                'chat_info': {
                    'id': chat.id,
                    'title': chat.title,
                    'username': getattr(chat, 'username', None),
                    'type': self._get_chat_type(chat),
                    'member_count': getattr(chat, 'participants_count', None)
                },
                'message_stats': {
                    'total_messages': total_messages,
                    'text_messages': text_count,
                    'media_messages': media_count,
                    'last_24h': last_24h,
                    'last_7d': last_7d
                },
                'engagement_stats': {
                    'total_views': total_views,
                    'total_forwards': total_forwards,
                    'avg_views_per_message': avg_views,
                    'avg_forwards_per_message': avg_forwards
                },
                'activity_score': (last_24h * 10 + last_7d) / max(total_messages, 1) * 100,
                'analysis_period': {
                    'start_date': min(msg.date for msg in messages),
                    'end_date': max(msg.date for msg in messages),
                    'analyzed_at': datetime.utcnow()
                }
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Analytics generation failed: {str(e)}")
            raise CrawlerError(f"Analytics error: {str(e)}")
    
    async def _process_message(self, message):
        """Process incoming message for analysis."""
        try:
            # Parse message data
            message_data = await self._parse_message_data(message)
            
            # Generate content fingerprint
            if message_data.text:
                message_data.content_fingerprint = await self.text_fingerprinter.generate_fingerprint(
                    message_data.text
                )
            
            # Analyze media if present
            if message_data.media_type:
                await self._analyze_message_media(message_data, message)
            
            # Check for violations
            await self._check_message_violations(message_data)
            
        except Exception as e:
            self.logger.error(f"Message processing failed: {str(e)}")
    
    async def _parse_message_data(self, message) -> TelegramMessage:
        """Parse Telegram message into structured data."""
        chat = await message.get_chat()
        sender = await message.get_sender()
        
        return TelegramMessage(
            message_id=message.id,
            text=message.text,
            date=message.date,
            from_id=sender.id if sender else None,
            from_username=getattr(sender, 'username', None),
            from_first_name=getattr(sender, 'first_name', None),
            from_last_name=getattr(sender, 'last_name', None),
            chat_id=chat.id,
            chat_title=getattr(chat, 'title', None),
            chat_username=getattr(chat, 'username', None),
            chat_type=self._get_chat_type(chat),
            media_type=self._get_media_type(message),
            forward_from=self._get_forward_info(message),
            reply_to_message_id=getattr(message.reply_to, 'reply_to_msg_id', None) if message.reply_to else None,
            views=getattr(message, 'views', None),
            forwards=getattr(message, 'forwards', None)
        )
    
    async def _parse_chat_data(self, chat) -> TelegramChat:
        """Parse Telegram chat into structured data."""
        return TelegramChat(
            chat_id=chat.id,
            title=getattr(chat, 'title', ''),
            username=getattr(chat, 'username', None),
            description=getattr(chat, 'about', None),
            chat_type=self._get_chat_type(chat),
            member_count=getattr(chat, 'participants_count', None),
            created_date=getattr(chat, 'date', None),
            is_verified=getattr(chat, 'verified', False),
            is_scam=getattr(chat, 'scam', False),
            is_fake=getattr(chat, 'fake', False),
            is_restricted=getattr(chat, 'restricted', False),
            is_megagroup=getattr(chat, 'megagroup', False),
            is_broadcast=getattr(chat, 'broadcast', False)
        )
    
    async def _analyze_chat(self, chat) -> TelegramChat:
        """Perform comprehensive chat analysis."""
        chat_data = await self._parse_chat_data(chat)
        
        # Calculate activity score based on recent messages
        try:
            recent_messages = await self.get_chat_messages(chat, limit=50)
            if recent_messages:
                recent_activity = len([
                    msg for msg in recent_messages 
                    if (datetime.utcnow() - msg.date).days < 7
                ])
                chat_data.activity_score = recent_activity / len(recent_messages) * 100
        except:
            chat_data.activity_score = 0
        
        return chat_data
    
    def _get_chat_type(self, chat) -> str:
        """Determine chat type."""
        if hasattr(chat, 'broadcast') and chat.broadcast:
            return 'channel'
        elif hasattr(chat, 'megagroup') and chat.megagroup:
            return 'supergroup'
        elif isinstance(chat, Channel):
            return 'channel'
        elif isinstance(chat, Chat):
            return 'group'
        else:
            return 'private'
    
    def _get_media_type(self, message) -> Optional[str]:
        """Get media type from message."""
        if message.photo:
            return 'photo'
        elif message.video:
            return 'video'
        elif message.audio:
            return 'audio'
        elif message.voice:
            return 'voice'
        elif message.document:
            return 'document'
        elif message.sticker:
            return 'sticker'
        elif message.gif:
            return 'gif'
        return None
    
    def _get_forward_info(self, message) -> Optional[Dict]:
        """Extract forward information from message."""
        if message.forward:
            return {
                'from_id': getattr(message.forward.from_id, 'user_id', None),
                'from_name': message.forward.from_name,
                'channel_id': getattr(message.forward.channel_id, 'channel_id', None),
                'date': message.forward.date
            }
        return None
    
    async def _calculate_content_similarity(self, fingerprint1: str, fingerprint2: str) -> float:
        """Calculate similarity between content fingerprints."""
        return await self.text_fingerprinter.calculate_similarity(fingerprint1, fingerprint2)
    
    def get_crawler_stats(self) -> Dict[str, any]:
        """Get crawler statistics and status."""
        return {
            'platform': 'telegram',
            'client_connected': self.client.is_connected(),
            'monitored_chats': len(self.monitored_chats),
            'content_violations': len(self.content_violations),
            'rate_limiter_status': self.rate_limiter.get_status() if self.rate_limiter else None
        }

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_telegram_crawler():
        api_id = 12345  # Your API ID
        api_hash = "your_api_hash"  # Your API hash
        
        async with TelegramCrawler(api_id, api_hash) as crawler:
            # Search channels
            channels = await crawler.search_channels("news", limit=10)
            print(f"Found {len(channels)} channels")
            
            # Monitor a channel
            if channels:
                monitoring_config = await crawler.monitor_chat(channels[0].username)
                print(f"Monitoring config: {monitoring_config}")
    
    # asyncio.run(test_telegram_crawler())

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from urllib.parse import urljoin, urlparse

import aiohttp
from telethon import TelegramClient, events
from telethon.tl.types import User, Chat, Channel, Message, MessageMediaPhoto, MessageMediaDocument
import pandas as pd
from pydantic import BaseModel, Field

from ..base_crawler import BaseCrawler
from ....core.config import get_settings
from ....core.logging import get_logger
from ....models.content import ContentMatch, PlatformContent
from ....utils.rate_limiter import RateLimiter
from ....security.encryption import encrypt_sensitive_data

logger = get_logger(__name__)
settings = get_settings()


class TelegramMessage(BaseModel):
    """Telegram Message data model"""
    message_id: int
    content: str
    sender_id: Optional[int] = None
    sender_username: Optional[str] = None
    sender_first_name: Optional[str] = None
    sender_last_name: Optional[str] = None
    chat_id: int
    chat_title: Optional[str] = None
    chat_username: Optional[str] = None
    chat_type: str = "private"  # private, group, supergroup, channel
    date: datetime
    edit_date: Optional[datetime] = None
    reply_to_message_id: Optional[int] = None
    forward_from_chat_id: Optional[int] = None
    forward_from_message_id: Optional[int] = None
    forward_date: Optional[datetime] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    media_file_name: Optional[str] = None
    media_file_size: Optional[int] = None
    media_mime_type: Optional[str] = None
    photo_sizes: List[Dict[str, Any]] = Field(default_factory=list)
    document_attributes: List[Dict[str, Any]] = Field(default_factory=list)
    views: Optional[int] = None
    reactions: List[Dict[str, Any]] = Field(default_factory=list)
    replies_count: Optional[int] = None
    mentions: List[Dict[str, Any]] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    is_pinned: bool = False
    is_silent: bool = False
    is_scheduled: bool = False
    via_bot_id: Optional[int] = None
    grouped_id: Optional[int] = None
    restriction_reason: Optional[str] = None


class TelegramChat(BaseModel):
    """Telegram Chat data model"""
    chat_id: int
    title: str
    username: Optional[str] = None
    chat_type: str = "private"  # private, group, supergroup, channel
    description: Optional[str] = None
    photo_url: Optional[str] = None
    member_count: Optional[int] = None
    admin_count: Optional[int] = None
    creator_id: Optional[int] = None
    created_date: Optional[datetime] = None
    is_verified: bool = False
    is_scam: bool = False
    is_fake: bool = False
    is_restricted: bool = False
    restriction_reason: Optional[str] = None
    has_geo: bool = False
    has_link: bool = False
    has_username: bool = False
    is_broadcast: bool = False
    is_gigagroup: bool = False
    is_forum: bool = False
    join_to_send: bool = False
    join_request: bool = False
    linked_chat_id: Optional[int] = None
    location: Optional[Dict[str, Any]] = None
    slowmode_delay: Optional[int] = None
    message_ttl: Optional[int] = None
    available_reactions: List[str] = Field(default_factory=list)
    default_banned_rights: Optional[Dict[str, Any]] = None
    admin_rights: Optional[Dict[str, Any]] = None


class TelegramUser(BaseModel):
    """Telegram User data model"""
    user_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    is_bot: bool = False
    is_verified: bool = False
    is_premium: bool = False
    is_restricted: bool = False
    is_scam: bool = False
    is_fake: bool = False
    is_support: bool = False
    restriction_reason: Optional[str] = None
    language_code: Optional[str] = None
    status: str = "offline"  # online, offline, recently, within_week, within_month, long_time_ago
    last_online: Optional[datetime] = None
    common_chats_count: int = 0
    mutual_contact: bool = False
    deleted: bool = False
    bot_info_version: Optional[int] = None
    bot_inline_geo: bool = False
    bot_attach_menu: bool = False
    stories_max_id: Optional[int] = None


class TelegramChannel(BaseModel):
    """Telegram Channel data model"""
    channel_id: int
    title: str
    username: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None
    subscriber_count: Optional[int] = None
    created_date: Optional[datetime] = None
    creator_id: Optional[int] = None
    is_verified: bool = False
    is_scam: bool = False
    is_fake: bool = False
    is_restricted: bool = False
    is_broadcast: bool = True
    is_megagroup: bool = False
    restriction_reason: Optional[str] = None
    has_geo: bool = False
    has_link: bool = False
    join_to_send: bool = False
    join_request: bool = False
    linked_discussion_group_id: Optional[int] = None
    location: Optional[Dict[str, Any]] = None
    slowmode_delay: Optional[int] = None
    message_ttl: Optional[int] = None
    available_reactions: List[str] = Field(default_factory=list)
    default_banned_rights: Optional[Dict[str, Any]] = None
    admin_rights: Optional[Dict[str, Any]] = None
    post_frequency: float = 0.0  # posts per day
    engagement_rate: float = 0.0
    growth_rate: float = 0.0


class TelegramCrawler(BaseCrawler):
    """
    Advanced Telegram crawler for comprehensive messaging content monitoring
    
    Features:
    - Message content analysis across chats and channels
    - User behavior analytics and profiling
    - Channel and group monitoring with engagement metrics
    - Media content extraction and analysis
    - Copyright infringement detection in messages and media
    - Spam and scam detection algorithms
    - Sentiment analysis and content categorization
    - Forward tracking and viral content analysis
    - Bot detection and automation monitoring
    - Geolocation and temporal analysis
    - Privacy-compliant data collection
    - Real-time monitoring and alerting
    """
    
    def __init__(self):
        super().__init__()
        self.platform = "telegram"
        self.api_base = "https://api.telegram.org"
        self.rate_limiter = RateLimiter(
            requests_per_minute=300,  # Telegram API rate limits
            requests_per_hour=3000
        )
        self.client = None
        self.session = None
        self.api_id = None
        self.api_hash = None
        self.bot_token = None
        self.monitored_chats = set()
        self.monitored_channels = set()
        
    async def authenticate(
        self,
        api_id: int,
        api_hash: str,
        bot_token: str = None,
        phone: str = None,
        password: str = None
    ) -> bool:
        """
        Authenticate with Telegram API
        
        Args:
            api_id: Telegram API ID
            api_hash: Telegram API hash
            bot_token: Bot token (for bot authentication)
            phone: Phone number (for user authentication)
            password: 2FA password if required
            
        Returns:
            Authentication success status
        """
        try:
            self.api_id = api_id
            self.api_hash = api_hash
            self.bot_token = bot_token
            
            # Initialize Telegram client
            if bot_token:
                # Bot authentication
                self.client = TelegramClient('bot_session', api_id, api_hash)
                await self.client.start(bot_token=bot_token)
                logger.info("Successfully authenticated Telegram bot")
            elif phone:
                # User authentication
                self.client = TelegramClient('user_session', api_id, api_hash)
                await self.client.start(phone=phone, password=password)
                logger.info("Successfully authenticated Telegram user")
            else:
                logger.error("Either bot_token or phone must be provided")
                return False
            
            # Set up event handlers
            @self.client.on(events.NewMessage)
            async def new_message_handler(event):
                await self._process_new_message(event)
            
            @self.client.on(events.MessageEdited)
            async def edited_message_handler(event):
                await self._process_edited_message(event)
            
            return True
            
        except Exception as e:
            logger.error(f"Telegram authentication error: {str(e)}")
            return False
    
    async def start_monitoring(self):
        """Start real-time monitoring"""
        if self.client:
            try:
                await self.client.run_until_disconnected()
            except Exception as e:
                logger.error(f"Error during Telegram monitoring: {str(e)}")
    
    async def stop_monitoring(self):
        """Stop monitoring and disconnect"""
        if self.client and self.client.is_connected():
            await self.client.disconnect()
    
    async def get_chat_details(self, chat_identifier: str) -> Optional[TelegramChat]:
        """Get detailed information about a chat/group/channel"""
        await self.rate_limiter.wait()
        
        try:
            chat = await self.client.get_entity(chat_identifier)
            return await self._create_chat_model(chat)
            
        except Exception as e:
            logger.error(f"Error getting chat details: {str(e)}")
            return None
    
    async def get_user_details(self, user_identifier: str) -> Optional[TelegramUser]:
        """Get detailed information about a user"""
        await self.rate_limiter.wait()
        
        try:
            user = await self.client.get_entity(user_identifier)
            return await self._create_user_model(user)
            
        except Exception as e:
            logger.error(f"Error getting user details: {str(e)}")
            return None
    
    async def get_chat_messages(
        self,
        chat_identifier: str,
        limit: int = 100,
        offset_date: datetime = None,
        offset_id: int = 0,
        min_id: int = 0,
        max_id: int = 0,
        search: str = None
    ) -> List[TelegramMessage]:
        """
        Get messages from a chat/channel
        
        Args:
            chat_identifier: Chat username, ID, or invite link
            limit: Maximum number of messages
            offset_date: Offset date for pagination
            offset_id: Offset message ID
            min_id: Minimum message ID
            max_id: Maximum message ID
            search: Search query within messages
            
        Returns:
            List of messages
        """
        await self.rate_limiter.wait()
        
        try:
            messages = []
            async for message in self.client.iter_messages(
                chat_identifier,
                limit=limit,
                offset_date=offset_date,
                offset_id=offset_id,
                min_id=min_id,
                max_id=max_id,
                search=search
            ):
                telegram_message = await self._create_message_model(message)
                if telegram_message:
                    messages.append(telegram_message)
            
            logger.info(f"Retrieved {len(messages)} messages from {chat_identifier}")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting chat messages: {str(e)}")
            return []
    
    async def search_messages(
        self,
        query: str,
        chat_identifier: str = None,
        from_user: str = None,
        media_type: str = None,
        limit: int = 100
    ) -> List[TelegramMessage]:
        """
        Search messages across chats or within specific chat
        
        Args:
            query: Search query
            chat_identifier: Specific chat to search in
            from_user: Filter by sender
            media_type: Filter by media type (photo, video, document, etc.)
            limit: Maximum results
            
        Returns:
            List of matching messages
        """
        await self.rate_limiter.wait()
        
        try:
            if chat_identifier:
                # Search within specific chat
                messages = await self.get_chat_messages(
                    chat_identifier=chat_identifier,
                    search=query,
                    limit=limit
                )
                
                # Apply additional filters
                if from_user:
                    messages = [msg for msg in messages if msg.sender_username == from_user]
                
                if media_type:
                    messages = [msg for msg in messages if msg.media_type == media_type]
                
                return messages
            else:
                # Global search across monitored chats
                all_messages = []
                
                for chat_id in self.monitored_chats.union(self.monitored_channels):
                    try:
                        chat_messages = await self.get_chat_messages(
                            chat_identifier=str(chat_id),
                            search=query,
                            limit=min(limit // len(self.monitored_chats.union(self.monitored_channels)) + 1, 50)
                        )
                        all_messages.extend(chat_messages)
                    except Exception as e:
                        logger.debug(f"Error searching in chat {chat_id}: {str(e)}")
                        continue
                
                return all_messages[:limit]
                
        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            return []
    
    async def get_channel_statistics(self, channel_identifier: str) -> Dict[str, Any]:
        """
        Get comprehensive channel statistics and analytics
        
        Args:
            channel_identifier: Channel username or ID
            
        Returns:
            Channel statistics and metrics
        """
        await self.rate_limiter.wait()
        
        try:
            channel = await self.get_chat_details(channel_identifier)
            if not channel:
                return {}
            
            # Get recent messages for analysis
            recent_messages = await self.get_chat_messages(channel_identifier, limit=100)
            
            # Calculate statistics
            total_messages = len(recent_messages)
            if total_messages == 0:
                return {'channel_id': channel.chat_id, 'error': 'No messages found'}
            
            # Time-based analysis
            now = datetime.utcnow()
            messages_last_24h = len([msg for msg in recent_messages if (now - msg.date).days < 1])
            messages_last_week = len([msg for msg in recent_messages if (now - msg.date).days < 7])
            
            # Content analysis
            total_views = sum(msg.views or 0 for msg in recent_messages)
            avg_views = total_views / total_messages if total_messages > 0 else 0
            
            media_messages = len([msg for msg in recent_messages if msg.media_type])
            text_only_messages = total_messages - media_messages
            
            # Engagement analysis
            total_reactions = sum(len(msg.reactions) for msg in recent_messages)
            avg_reactions = total_reactions / total_messages if total_messages > 0 else 0
            
            # Forward analysis
            forwarded_messages = len([msg for msg in recent_messages if msg.forward_from_chat_id])
            original_content_ratio = (total_messages - forwarded_messages) / total_messages if total_messages > 0 else 0
            
            statistics = {
                'channel_info': {
                    'channel_id': channel.chat_id,
                    'title': channel.title,
                    'username': channel.username,
                    'subscriber_count': channel.member_count,
                    'verified': channel.is_verified,
                    'description': channel.description
                },
                'activity_metrics': {
                    'total_messages_analyzed': total_messages,
                    'messages_last_24h': messages_last_24h,
                    'messages_last_week': messages_last_week,
                    'posting_frequency_per_day': messages_last_week / 7 if messages_last_week > 0 else 0,
                    'activity_score': self._calculate_activity_score(messages_last_24h, messages_last_week)
                },
                'engagement_metrics': {
                    'total_views': total_views,
                    'average_views_per_post': avg_views,
                    'total_reactions': total_reactions,
                    'average_reactions_per_post': avg_reactions,
                    'engagement_rate': avg_reactions / max(avg_views, 1) * 100,
                    'view_to_subscriber_ratio': avg_views / max(channel.member_count or 1, 1)
                },
                'content_analysis': {
                    'media_message_percentage': (media_messages / total_messages) * 100,
                    'text_only_percentage': (text_only_messages / total_messages) * 100,
                    'original_content_ratio': original_content_ratio * 100,
                    'forwarded_content_ratio': (1 - original_content_ratio) * 100,
                    'content_diversity_score': self._calculate_content_diversity(recent_messages)
                },
                'growth_indicators': {
                    'recent_activity_trend': self._analyze_activity_trend(recent_messages),
                    'engagement_trend': self._analyze_engagement_trend(recent_messages),
                    'content_quality_score': self._calculate_content_quality_score(recent_messages)
                },
                'audience_insights': {
                    'peak_posting_hours': self._analyze_posting_hours(recent_messages),
                    'content_language_distribution': await self._analyze_content_languages(recent_messages),
                    'hashtag_analysis': self._analyze_hashtags(recent_messages)
                }
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting channel statistics: {str(e)}")
            return {}
    
    async def monitor_content_infringement(
        self,
        protected_content: Dict,
        similarity_threshold: float = 0.8,
        chat_identifiers: List[str] = None
    ) -> List[ContentMatch]:
        """
        Monitor Telegram for potential copyright infringement
        
        Args:
            protected_content: Content to protect
            similarity_threshold: Minimum similarity for match detection
            chat_identifiers: Specific chats/channels to monitor
            
        Returns:
            List of potential copyright matches
        """
        matches = []
        
        try:
            # Generate search queries from protected content
            search_queries = self._generate_search_queries(protected_content)
            
            target_chats = chat_identifiers or list(self.monitored_chats.union(self.monitored_channels))
            
            for query in search_queries:
                for chat_id in target_chats:
                    try:
                        results = await self.search_messages(
                            query=query,
                            chat_identifier=str(chat_id),
                            limit=25
                        )
                        
                        for message in results:
                            similarity_score = await self._calculate_content_similarity(
                                protected_content, message
                            )
                            
                            if similarity_score >= similarity_threshold:
                                match = ContentMatch(
                                    platform="telegram",
                                    content_id=str(message.message_id),
                                    url=f"https://t.me/{message.chat_username}/{message.message_id}" if message.chat_username else f"tg://msg?chat_id={message.chat_id}&message_id={message.message_id}",
                                    title=f"Message in {message.chat_title or 'Private Chat'}",
                                    description=message.content[:200] + "..." if len(message.content) > 200 else message.content,
                                    creator=message.sender_username or f"User_{message.sender_id}",
                                    similarity_score=similarity_score,
                                    detection_date=datetime.utcnow(),
                                    content_type="message",
                                    metadata={
                                        'chat_id': message.chat_id,
                                        'chat_title': message.chat_title,
                                        'chat_type': message.chat_type,
                                        'sender_id': message.sender_id,
                                        'message_date': message.date.isoformat(),
                                        'media_type': message.media_type,
                                        'views': message.views,
                                        'is_forwarded': message.forward_from_chat_id is not None
                                    }
                                )
                                matches.append(match)
                                
                    except Exception as e:
                        logger.debug(f"Error monitoring chat {chat_id}: {str(e)}")
                        continue
            
            logger.info(f"Found {len(matches)} potential copyright matches on Telegram")
            return matches
            
        except Exception as e:
            logger.error(f"Error monitoring Telegram content infringement: {str(e)}")
            return []
    
    async def analyze_user_behavior(self, user_identifier: str, chat_context: str = None) -> Dict[str, Any]:
        """
        Analyze user behavior and activity patterns
        
        Args:
            user_identifier: User ID or username
            chat_context: Optional chat context for analysis
            
        Returns:
            Comprehensive user behavior analysis
        """
        try:
            user = await self.get_user_details(user_identifier)
            if not user:
                return {}
            
            # Get user's recent messages
            user_messages = []
            if chat_context:
                messages = await self.get_chat_messages(chat_context, limit=200)
                user_messages = [msg for msg in messages if msg.sender_id == user.user_id]
            
            behavior_analysis = {
                'user_profile': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_bot': user.is_bot,
                    'is_verified': user.is_verified,
                    'is_premium': user.is_premium,
                    'status': user.status
                },
                'activity_patterns': {
                    'total_messages': len(user_messages),
                    'average_message_length': sum(len(msg.content) for msg in user_messages) / len(user_messages) if user_messages else 0,
                    'posting_frequency': self._calculate_user_posting_frequency(user_messages),
                    'active_hours': self._analyze_user_active_hours(user_messages),
                    'message_types': self._analyze_user_message_types(user_messages)
                },
                'communication_analysis': {
                    'media_sharing_frequency': len([msg for msg in user_messages if msg.media_type]) / len(user_messages) if user_messages else 0,
                    'forward_frequency': len([msg for msg in user_messages if msg.forward_from_chat_id]) / len(user_messages) if user_messages else 0,
                    'reply_frequency': len([msg for msg in user_messages if msg.reply_to_message_id]) / len(user_messages) if user_messages else 0,
                    'hashtag_usage': self._analyze_user_hashtag_usage(user_messages),
                    'url_sharing_frequency': len([msg for msg in user_messages if msg.urls]) / len(user_messages) if user_messages else 0
                },
                'engagement_metrics': {
                    'average_views_per_message': sum(msg.views or 0 for msg in user_messages) / len(user_messages) if user_messages else 0,
                    'average_reactions_per_message': sum(len(msg.reactions) for msg in user_messages) / len(user_messages) if user_messages else 0,
                    'message_impact_score': self._calculate_message_impact_score(user_messages),
                    'influence_level': self._assess_user_influence_level(user, user_messages)
                },
                'behavioral_indicators': {
                    'bot_probability': await self._calculate_bot_probability(user, user_messages),
                    'spam_likelihood': await self._calculate_spam_likelihood(user_messages),
                    'authenticity_score': await self._calculate_authenticity_score(user, user_messages),
                    'engagement_quality': await self._assess_engagement_quality(user_messages)
                },
                'risk_assessment': {
                    'scam_risk_score': await self._assess_scam_risk(user, user_messages),
                    'content_violation_risk': await self._assess_content_violation_risk(user_messages),
                    'suspicious_activity_indicators': await self._identify_suspicious_indicators(user, user_messages)
                },
                'network_analysis': {
                    'common_chats_participation': user.common_chats_count,
                    'social_connectivity_score': await self._calculate_social_connectivity(user),
                    'influence_network_size': await self._estimate_influence_network_size(user)
                }
            }
            
            return behavior_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {str(e)}")
            return {}
    
    async def track_content_virality(
        self,
        content_identifier: str,
        tracking_period_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Track content virality and spread across Telegram
        
        Args:
            content_identifier: Message ID or content hash to track
            tracking_period_hours: Period to track virality
            
        Returns:
            Virality analysis and metrics
        """
        try:
            # This would require complex message tracking across channels
            # Implementation would depend on specific tracking requirements
            
            virality_analysis = {
                'content_id': content_identifier,
                'tracking_period': tracking_period_hours,
                'spread_metrics': {
                    'total_forwards': 0,
                    'unique_channels': 0,
                    'reach_estimate': 0,
                    'viral_coefficient': 0.0
                },
                'temporal_analysis': {
                    'peak_spread_hour': None,
                    'spread_velocity': 0.0,
                    'decay_rate': 0.0
                },
                'geographic_spread': {
                    'countries_reached': [],
                    'language_variants': []
                },
                'modification_tracking': {
                    'content_variations': [],
                    'authenticity_preserved': True
                }
            }
            
            return virality_analysis
            
        except Exception as e:
            logger.error(f"Error tracking content virality: {str(e)}")
            return {}
    
    # Model creation methods
    async def _create_message_model(self, message) -> Optional[TelegramMessage]:
        """Create TelegramMessage model from Telegram API message"""
        try:
            if not message:
                return None
            
            # Extract sender information
            sender_id = None
            sender_username = None
            sender_first_name = None
            sender_last_name = None
            
            if hasattr(message, 'sender') and message.sender:
                sender_id = message.sender.id
                if hasattr(message.sender, 'username'):
                    sender_username = message.sender.username
                if hasattr(message.sender, 'first_name'):
                    sender_first_name = message.sender.first_name
                if hasattr(message.sender, 'last_name'):
                    sender_last_name = message.sender.last_name
            elif hasattr(message, 'from_id') and message.from_id:
                sender_id = message.from_id.user_id if hasattr(message.from_id, 'user_id') else message.from_id
            
            # Extract chat information
            chat_id = message.peer_id.channel_id if hasattr(message.peer_id, 'channel_id') else message.peer_id.chat_id if hasattr(message.peer_id, 'chat_id') else message.peer_id.user_id
            chat_title = None
            chat_username = None
            chat_type = "private"
            
            if hasattr(message, 'chat') and message.chat:
                chat_title = message.chat.title if hasattr(message.chat, 'title') else None
                chat_username = message.chat.username if hasattr(message.chat, 'username') else None
                if hasattr(message.chat, 'broadcast'):
                    chat_type = "channel" if message.chat.broadcast else "supergroup"
                elif hasattr(message.chat, 'megagroup'):
                    chat_type = "supergroup" if message.chat.megagroup else "group"
            
            # Extract media information
            media_type = None
            media_url = None
            media_file_name = None
            media_file_size = None
            media_mime_type = None
            photo_sizes = []
            document_attributes = []
            
            if hasattr(message, 'media') and message.media:
                if isinstance(message.media, MessageMediaPhoto):
                    media_type = "photo"
                    if hasattr(message.media.photo, 'sizes'):
                        photo_sizes = [{'type': size.type, 'width': getattr(size, 'w', 0), 'height': getattr(size, 'h', 0)} for size in message.media.photo.sizes]
                elif isinstance(message.media, MessageMediaDocument):
                    media_type = "document"
                    if hasattr(message.media.document, 'mime_type'):
                        media_mime_type = message.media.document.mime_type
                    if hasattr(message.media.document, 'size'):
                        media_file_size = message.media.document.size
                    if hasattr(message.media.document, 'attributes'):
                        for attr in message.media.document.attributes:
                            if hasattr(attr, 'file_name'):
                                media_file_name = attr.file_name
                            document_attributes.append({
                                'type': type(attr).__name__,
                                'data': str(attr)
                            })
            
            # Extract text content
            content = message.message if hasattr(message, 'message') else ""
            
            # Extract hashtags and URLs
            hashtags = re.findall(r'#\w+', content)
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
            
            # Extract forward information
            forward_from_chat_id = None
            forward_from_message_id = None
            forward_date = None
            
            if hasattr(message, 'fwd_from') and message.fwd_from:
                if hasattr(message.fwd_from, 'from_id'):
                    forward_from_chat_id = message.fwd_from.from_id
                if hasattr(message.fwd_from, 'channel_post'):
                    forward_from_message_id = message.fwd_from.channel_post
                if hasattr(message.fwd_from, 'date'):
                    forward_date = message.fwd_from.date
            
            telegram_message = TelegramMessage(
                message_id=message.id,
                content=content,
                sender_id=sender_id,
                sender_username=sender_username,
                sender_first_name=sender_first_name,
                sender_last_name=sender_last_name,
                chat_id=chat_id,
                chat_title=chat_title,
                chat_username=chat_username,
                chat_type=chat_type,
                date=message.date,
                edit_date=message.edit_date if hasattr(message, 'edit_date') else None,
                reply_to_message_id=message.reply_to.reply_to_msg_id if hasattr(message, 'reply_to') and message.reply_to else None,
                forward_from_chat_id=forward_from_chat_id,
                forward_from_message_id=forward_from_message_id,
                forward_date=forward_date,
                media_type=media_type,
                media_url=media_url,
                media_file_name=media_file_name,
                media_file_size=media_file_size,
                media_mime_type=media_mime_type,
                photo_sizes=photo_sizes,
                document_attributes=document_attributes,
                views=message.views if hasattr(message, 'views') else None,
                hashtags=hashtags,
                urls=urls,
                is_pinned=message.pinned if hasattr(message, 'pinned') else False,
                is_silent=message.silent if hasattr(message, 'silent') else False,
                via_bot_id=message.via_bot_id if hasattr(message, 'via_bot_id') else None,
                grouped_id=message.grouped_id if hasattr(message, 'grouped_id') else None
            )
            
            return telegram_message
            
        except Exception as e:
            logger.error(f"Error creating message model: {str(e)}")
            return None
    
    async def _create_chat_model(self, chat) -> Optional[TelegramChat]:
        """Create TelegramChat model from Telegram API chat"""
        try:
            if not chat:
                return None
            
            chat_type = "private"
            if hasattr(chat, 'broadcast') and chat.broadcast:
                chat_type = "channel"
            elif hasattr(chat, 'megagroup') and chat.megagroup:
                chat_type = "supergroup"
            elif hasattr(chat, 'gigagroup') and chat.gigagroup:
                chat_type = "gigagroup"
            elif hasattr(chat, 'participants_count'):
                chat_type = "group"
            
            telegram_chat = TelegramChat(
                chat_id=chat.id,
                title=chat.title if hasattr(chat, 'title') else "",
                username=chat.username if hasattr(chat, 'username') else None,
                chat_type=chat_type,
                description=chat.about if hasattr(chat, 'about') else None,
                member_count=chat.participants_count if hasattr(chat, 'participants_count') else None,
                is_verified=chat.verified if hasattr(chat, 'verified') else False,
                is_scam=chat.scam if hasattr(chat, 'scam') else False,
                is_fake=chat.fake if hasattr(chat, 'fake') else False,
                is_restricted=chat.restricted if hasattr(chat, 'restricted') else False,
                restriction_reason=chat.restriction_reason[0].text if hasattr(chat, 'restriction_reason') and chat.restriction_reason else None,
                has_geo=chat.geo if hasattr(chat, 'geo') else False,
                has_link=chat.has_link if hasattr(chat, 'has_link') else False,
                is_broadcast=chat.broadcast if hasattr(chat, 'broadcast') else False,
                is_gigagroup=chat.gigagroup if hasattr(chat, 'gigagroup') else False,
                join_to_send=chat.join_to_send if hasattr(chat, 'join_to_send') else False,
                join_request=chat.join_request if hasattr(chat, 'join_request') else False,
                linked_chat_id=chat.linked_chat_id if hasattr(chat, 'linked_chat_id') else None,
                slowmode_delay=chat.slowmode_seconds if hasattr(chat, 'slowmode_seconds') else None
            )
            
            return telegram_chat
            
        except Exception as e:
            logger.error(f"Error creating chat model: {str(e)}")
            return None
    
    async def _create_user_model(self, user) -> Optional[TelegramUser]:
        """Create TelegramUser model from Telegram API user"""
        try:
            if not user:
                return None
            
            telegram_user = TelegramUser(
                user_id=user.id,
                username=user.username if hasattr(user, 'username') else None,
                first_name=user.first_name if hasattr(user, 'first_name') else "",
                last_name=user.last_name if hasattr(user, 'last_name') else None,
                phone=user.phone if hasattr(user, 'phone') else None,
                is_bot=user.bot if hasattr(user, 'bot') else False,
                is_verified=user.verified if hasattr(user, 'verified') else False,
                is_premium=user.premium if hasattr(user, 'premium') else False,
                is_restricted=user.restricted if hasattr(user, 'restricted') else False,
                is_scam=user.scam if hasattr(user, 'scam') else False,
                is_fake=user.fake if hasattr(user, 'fake') else False,
                is_support=user.support if hasattr(user, 'support') else False,
                restriction_reason=user.restriction_reason[0].text if hasattr(user, 'restriction_reason') and user.restriction_reason else None,
                language_code=user.lang_code if hasattr(user, 'lang_code') else None,
                deleted=user.deleted if hasattr(user, 'deleted') else False
            )
            
            return telegram_user
            
        except Exception as e:
            logger.error(f"Error creating user model: {str(e)}")
            return None
    
    # Event handlers
    async def _process_new_message(self, event):
        """Process new message event"""
        try:
            message = await self._create_message_model(event.message)
            if message:
                logger.debug(f"Processed new message {message.message_id} in chat {message.chat_id}")
                # Add custom processing logic here
                
        except Exception as e:
            logger.error(f"Error processing new message: {str(e)}")
    
    async def _process_edited_message(self, event):
        """Process edited message event"""
        try:
            message = await self._create_message_model(event.message)
            if message:
                logger.debug(f"Processed edited message {message.message_id} in chat {message.chat_id}")
                # Add custom processing logic here
                
        except Exception as e:
            logger.error(f"Error processing edited message: {str(e)}")
    
    # Helper methods
    def _generate_search_queries(self, protected_content: Dict) -> List[str]:
        """Generate search queries for content protection"""
        queries = []
        
        if 'content' in protected_content:
            # Extract key phrases
            content = protected_content['content']
            words = content.split()
            if len(words) > 3:
                queries.append(' '.join(words[:8]))
            if len(words) > 8:
                queries.append(' '.join(words[4:12]))
        
        if 'title' in protected_content:
            queries.append(protected_content['title'])
        
        if 'keywords' in protected_content:
            queries.extend(protected_content['keywords'][:2])
        
        return queries[:4]  # Limit to avoid rate limits
    
    async def _calculate_content_similarity(
        self,
        protected_content: Dict,
        message: TelegramMessage
    ) -> float:
        """Calculate similarity between protected content and Telegram message"""
        from difflib import SequenceMatcher
        
        similarity_scores = []
        
        # Text content similarity
        if 'content' in protected_content and message.content:
            content_similarity = SequenceMatcher(
                None,
                protected_content['content'].lower(),
                message.content.lower()
            ).ratio()
            similarity_scores.append(content_similarity)
        
        # Media similarity (placeholder - would need actual media comparison)
        if 'media_hash' in protected_content and message.media_type:
            # This would require downloading and comparing media files
            similarity_scores.append(0.0)
        
        return max(similarity_scores) if similarity_scores else 0.0
    
    # Analysis helper methods
    def _calculate_activity_score(self, messages_24h: int, messages_week: int) -> float:
        """Calculate activity score based on message frequency"""
        daily_average = messages_week / 7
        if daily_average == 0:
            return 0.0
        
        activity_ratio = messages_24h / daily_average
        return min(activity_ratio, 2.0) / 2.0  # Normalize to 0-1
    
    def _calculate_content_diversity(self, messages: List[TelegramMessage]) -> float:
        """Calculate content diversity score"""
        if not messages:
            return 0.0
        
        text_messages = len([msg for msg in messages if not msg.media_type])
        media_messages = len([msg for msg in messages if msg.media_type])
        forwarded_messages = len([msg for msg in messages if msg.forward_from_chat_id])
        
        total_messages = len(messages)
        
        # Calculate diversity based on content types
        diversity_score = 0.0
        if text_messages > 0:
            diversity_score += 0.4
        if media_messages > 0:
            diversity_score += 0.4
        if forwarded_messages > 0:
            diversity_score += 0.2
        
        return diversity_score
    
    def _analyze_activity_trend(self, messages: List[TelegramMessage]) -> str:
        """Analyze activity trend from recent messages"""
        if len(messages) < 10:
            return "insufficient_data"
        
        # Split messages into two halves by time
        sorted_messages = sorted(messages, key=lambda x: x.date)
        mid_point = len(sorted_messages) // 2
        
        recent_half = sorted_messages[mid_point:]
        older_half = sorted_messages[:mid_point]
        
        recent_count = len(recent_half)
        older_count = len(older_half)
        
        if recent_count > older_count * 1.2:
            return "increasing"
        elif recent_count < older_count * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_engagement_trend(self, messages: List[TelegramMessage]) -> str:
        """Analyze engagement trend from recent messages"""
        if not messages:
            return "no_data"
        
        messages_with_engagement = [msg for msg in messages if (msg.views or 0) > 0 or msg.reactions]
        
        if not messages_with_engagement:
            return "no_engagement"
        
        # Calculate average engagement
        avg_views = sum(msg.views or 0 for msg in messages_with_engagement) / len(messages_with_engagement)
        avg_reactions = sum(len(msg.reactions) for msg in messages_with_engagement) / len(messages_with_engagement)
        
        # This is a simplified trend analysis
        if avg_views > 1000 or avg_reactions > 10:
            return "high_engagement"
        elif avg_views > 100 or avg_reactions > 2:
            return "moderate_engagement"
        else:
            return "low_engagement"
    
    def _calculate_content_quality_score(self, messages: List[TelegramMessage]) -> float:
        """Calculate content quality score"""
        if not messages:
            return 0.0
        
        # Factors for quality assessment
        avg_length = sum(len(msg.content) for msg in messages) / len(messages)
        media_ratio = len([msg for msg in messages if msg.media_type]) / len(messages)
        engagement_ratio = len([msg for msg in messages if (msg.views or 0) > 0]) / len(messages)
        
        # Normalize and combine factors
        length_score = min(avg_length / 100, 1.0) * 0.3  # Longer messages often higher quality
        media_score = media_ratio * 0.3  # Media content often more engaging
        engagement_score = engagement_ratio * 0.4  # Engagement indicates quality
        
        return length_score + media_score + engagement_score
    
    def _analyze_posting_hours(self, messages: List[TelegramMessage]) -> Dict[str, Any]:
        """Analyze posting hours distribution"""
        if not messages:
            return {}
        
        hour_counts = {}
        for message in messages:
            hour = message.date.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hour = max(hour_counts.keys(), key=lambda x: hour_counts[x]) if hour_counts else 0
        
        return {
            'peak_hour': peak_hour,
            'distribution': hour_counts,
            'total_posts': len(messages)
        }
    
    async def _analyze_content_languages(self, messages: List[TelegramMessage]) -> Dict[str, int]:
        """Analyze content language distribution"""
        # This would require language detection
        # Placeholder implementation
        return {'en': len(messages)}
    
    def _analyze_hashtags(self, messages: List[TelegramMessage]) -> Dict[str, Any]:
        """Analyze hashtag usage"""
        all_hashtags = []
        for message in messages:
            all_hashtags.extend(message.hashtags)
        
        hashtag_counts = {}
        for hashtag in all_hashtags:
            hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        
        return {
            'total_hashtags': len(all_hashtags),
            'unique_hashtags': len(hashtag_counts),
            'most_popular': sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    # Additional placeholder methods for comprehensive analysis
    def _calculate_user_posting_frequency(self, messages: List[TelegramMessage]) -> float:
        """Calculate user posting frequency"""
        if len(messages) < 2:
            return 0.0
        
        time_span = (messages[0].date - messages[-1].date).total_seconds() / 3600  # hours
        return len(messages) / max(time_span, 1)
    
    def _analyze_user_active_hours(self, messages: List[TelegramMessage]) -> Dict:
        """Analyze user's active hours"""
        return self._analyze_posting_hours(messages)
    
    def _analyze_user_message_types(self, messages: List[TelegramMessage]) -> Dict:
        """Analyze user's message types"""
        text_only = len([msg for msg in messages if not msg.media_type])
        with_media = len([msg for msg in messages if msg.media_type])
        forwarded = len([msg for msg in messages if msg.forward_from_chat_id])
        
        return {
            'text_only': text_only,
            'with_media': with_media,
            'forwarded': forwarded,
            'original_content_ratio': (text_only + with_media - forwarded) / len(messages) if messages else 0
        }
    
    def _analyze_user_hashtag_usage(self, messages: List[TelegramMessage]) -> Dict:
        """Analyze user's hashtag usage patterns"""
        messages_with_hashtags = [msg for msg in messages if msg.hashtags]
        
        return {
            'hashtag_frequency': len(messages_with_hashtags) / len(messages) if messages else 0,
            'avg_hashtags_per_message': sum(len(msg.hashtags) for msg in messages) / len(messages) if messages else 0
        }
