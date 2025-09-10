"""
Telegram Platform Connector for Ainflue Distribution
Provides enterprise-grade integration with Telegram for content distribution

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import base64
import hashlib

import aiohttp
import numpy as np
from pydantic import BaseModel, Field, validator

# Configure logging
logger = logging.getLogger(__name__)


class TelegramMessageType(str, Enum):
    """Telegram message types"""
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    ANIMATION = "animation"
    VOICE = "voice"
    VIDEO_NOTE = "video_note"
    STICKER = "sticker"
    POLL = "poll"


class TelegramChannelType(str, Enum):
    """Telegram channel types"""
    PUBLIC = "public"
    PRIVATE = "private"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"
    BOT = "bot"


@dataclass
class TelegramCredentials:
    """Telegram API credentials"""
    bot_token: str
    api_id: str
    api_hash: str
    phone_number: Optional[str] = None
    session_string: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TelegramMessage(BaseModel):
    """Telegram message model"""
    message_id: Optional[str] = Field(None, description="Message ID after sending")
    chat_id: str = Field(..., description="Target chat/channel ID")
    text: Optional[str] = Field(None, description="Message text")
    message_type: TelegramMessageType = Field(default=TelegramMessageType.TEXT)
    media_url: Optional[str] = Field(None, description="Media file URL")
    media_caption: Optional[str] = Field(None, description="Media caption")
    parse_mode: str = Field(default="HTML", description="Text parsing mode")
    reply_markup: Optional[Dict[str, Any]] = Field(None, description="Inline keyboard")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled send time")
    disable_notification: bool = Field(default=False, description="Silent message")
    protect_content: bool = Field(default=False, description="Content protection")
    
    @validator('scheduled_time')
    def validate_scheduled_time(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class TelegramChannel(BaseModel):
    """Telegram channel/chat model"""
    chat_id: str = Field(..., description="Channel/chat identifier")
    title: str = Field(..., description="Channel/chat title")
    username: Optional[str] = Field(None, description="Channel username")
    channel_type: TelegramChannelType = Field(..., description="Channel type")
    members_count: int = Field(default=0, description="Number of members")
    description: Optional[str] = Field(None, description="Channel description")
    invite_link: Optional[str] = Field(None, description="Invite link")
    is_verified: bool = Field(default=False, description="Verification status")


class TelegramMetrics(BaseModel):
    """Telegram message/channel metrics"""
    message_id: str
    chat_id: str
    views: int = 0
    forwards: int = 0
    reactions: Dict[str, int] = Field(default_factory=dict)
    replies: int = 0
    engagement_rate: float = 0.0
    reach: int = 0
    click_through_rate: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TelegramConnector:
    """
    Advanced Telegram connector for multi-format content distribution
    Features: Bot API, User API, channels, groups, scheduling, analytics
    """
    
    def __init__(self, credentials: TelegramCredentials):
        self.credentials = credentials
        self.bot_base_url = f"https://api.telegram.org/bot{credentials.bot_token}"
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limits = {
            'messages_per_second': 30,
            'messages_per_minute': 1000,
            'bulk_messages_per_minute': 20
        }
        self.message_queue: List[TelegramMessage] = []
        self.current_requests = 0
        self.last_reset = datetime.now(timezone.utc)
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        
    async def initialize(self) -> bool:
        """Initialize Telegram connector"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Ainflue-Distribution/3.0',
                    'Content-Type': 'application/json'
                }
            )
            
            # Verify bot token
            if await self._verify_bot_token():
                logger.info("Telegram connector initialized successfully")
                # Start message queue processor
                asyncio.create_task(self._process_message_queue())
                return True
            else:
                logger.error("Telegram bot token verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Telegram connector: {e}")
            return False
            
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            
    async def _verify_bot_token(self) -> bool:
        """Verify bot token validity"""
        try:
            async with self.session.get(f"{self.bot_base_url}/getMe") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        bot_info = data.get('result', {})
                        logger.info(f"Bot verified: {bot_info.get('username', 'Unknown')}")
                        return True
                return False
        except Exception as e:
            logger.error(f"Bot token verification failed: {e}")
            return False
            
    async def _check_rate_limits(self) -> bool:
        """Check and enforce rate limits"""
        now = datetime.now(timezone.utc)
        if (now - self.last_reset).total_seconds() >= 60:
            self.current_requests = 0
            self.last_reset = now
            
        if self.current_requests >= self.rate_limits['messages_per_minute']:
            logger.warning("Rate limit exceeded, waiting...")
            await asyncio.sleep(60)
            self.current_requests = 0
            
        self.current_requests += 1
        return True
        
    async def send_message(self, message: TelegramMessage) -> Dict[str, Any]:
        """
        Send a message to Telegram chat/channel
        
        Args:
            message: Message configuration
            
        Returns:
            Send result with message ID
        """
        if message.scheduled_time and message.scheduled_time > datetime.now(timezone.utc):
            # Add to queue for scheduled sending
            self.message_queue.append(message)
            logger.info(f"Message queued for {message.scheduled_time}")
            return {
                'success': True,
                'queued': True,
                'scheduled_time': message.scheduled_time.isoformat()
            }
            
        await self._check_rate_limits()
        
        try:
            if message.message_type == TelegramMessageType.TEXT:
                return await self._send_text_message(message)
            elif message.message_type == TelegramMessageType.PHOTO:
                return await self._send_photo_message(message)
            elif message.message_type == TelegramMessageType.VIDEO:
                return await self._send_video_message(message)
            elif message.message_type == TelegramMessageType.AUDIO:
                return await self._send_audio_message(message)
            elif message.message_type == TelegramMessageType.DOCUMENT:
                return await self._send_document_message(message)
            else:
                return {'success': False, 'error': f'Unsupported message type: {message.message_type}'}
                
        except Exception as e:
            logger.error(f"Message send error: {e}")
            return {'success': False, 'error': str(e)}
            
    async def _send_text_message(self, message: TelegramMessage) -> Dict[str, Any]:
        """Send text message"""
        payload = {
            'chat_id': message.chat_id,
            'text': message.text,
            'parse_mode': message.parse_mode,
            'disable_notification': message.disable_notification,
            'protect_content': message.protect_content
        }
        
        if message.reply_markup:
            payload['reply_markup'] = json.dumps(message.reply_markup)
            
        async with self.session.post(
            f"{self.bot_base_url}/sendMessage",
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('ok'):
                    result = data.get('result', {})
                    message_id = result.get('message_id')
                    logger.info(f"Text message sent successfully: {message_id}")
                    return {
                        'success': True,
                        'message_id': message_id,
                        'chat_id': message.chat_id
                    }
            
            error_text = await response.text()
            logger.error(f"Failed to send text message: {error_text}")
            return {'success': False, 'error': error_text}
            
    async def _send_photo_message(self, message: TelegramMessage) -> Dict[str, Any]:
        """Send photo message"""
        payload = {
            'chat_id': message.chat_id,
            'photo': message.media_url,
            'caption': message.media_caption,
            'parse_mode': message.parse_mode,
            'disable_notification': message.disable_notification,
            'protect_content': message.protect_content
        }
        
        if message.reply_markup:
            payload['reply_markup'] = json.dumps(message.reply_markup)
            
        async with self.session.post(
            f"{self.bot_base_url}/sendPhoto",
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('ok'):
                    result = data.get('result', {})
                    message_id = result.get('message_id')
                    logger.info(f"Photo message sent successfully: {message_id}")
                    return {
                        'success': True,
                        'message_id': message_id,
                        'chat_id': message.chat_id
                    }
            
            error_text = await response.text()
            logger.error(f"Failed to send photo message: {error_text}")
            return {'success': False, 'error': error_text}
            
    async def _send_video_message(self, message: TelegramMessage) -> Dict[str, Any]:
        """Send video message"""
        payload = {
            'chat_id': message.chat_id,
            'video': message.media_url,
            'caption': message.media_caption,
            'parse_mode': message.parse_mode,
            'disable_notification': message.disable_notification,
            'protect_content': message.protect_content
        }
        
        if message.reply_markup:
            payload['reply_markup'] = json.dumps(message.reply_markup)
            
        async with self.session.post(
            f"{self.bot_base_url}/sendVideo",
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('ok'):
                    result = data.get('result', {})
                    message_id = result.get('message_id')
                    logger.info(f"Video message sent successfully: {message_id}")
                    return {
                        'success': True,
                        'message_id': message_id,
                        'chat_id': message.chat_id
                    }
            
            error_text = await response.text()
            logger.error(f"Failed to send video message: {error_text}")
            return {'success': False, 'error': error_text}
            
    async def _send_audio_message(self, message: TelegramMessage) -> Dict[str, Any]:
        """Send audio message"""
        payload = {
            'chat_id': message.chat_id,
            'audio': message.media_url,
            'caption': message.media_caption,
            'parse_mode': message.parse_mode,
            'disable_notification': message.disable_notification,
            'protect_content': message.protect_content
        }
        
        if message.reply_markup:
            payload['reply_markup'] = json.dumps(message.reply_markup)
            
        async with self.session.post(
            f"{self.bot_base_url}/sendAudio",
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('ok'):
                    result = data.get('result', {})
                    message_id = result.get('message_id')
                    logger.info(f"Audio message sent successfully: {message_id}")
                    return {
                        'success': True,
                        'message_id': message_id,
                        'chat_id': message.chat_id
                    }
            
            error_text = await response.text()
            logger.error(f"Failed to send audio message: {error_text}")
            return {'success': False, 'error': error_text}
            
    async def _send_document_message(self, message: TelegramMessage) -> Dict[str, Any]:
        """Send document message"""
        payload = {
            'chat_id': message.chat_id,
            'document': message.media_url,
            'caption': message.media_caption,
            'parse_mode': message.parse_mode,
            'disable_notification': message.disable_notification,
            'protect_content': message.protect_content
        }
        
        if message.reply_markup:
            payload['reply_markup'] = json.dumps(message.reply_markup)
            
        async with self.session.post(
            f"{self.bot_base_url}/sendDocument",
            json=payload
        ) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('ok'):
                    result = data.get('result', {})
                    message_id = result.get('message_id')
                    logger.info(f"Document message sent successfully: {message_id}")
                    return {
                        'success': True,
                        'message_id': message_id,
                        'chat_id': message.chat_id
                    }
            
            error_text = await response.text()
            logger.error(f"Failed to send document message: {error_text}")
            return {'success': False, 'error': error_text}
            
    async def _process_message_queue(self):
        """Background processor for scheduled messages"""
        while True:
            try:
                now = datetime.now(timezone.utc)
                messages_to_send = []
                
                # Find messages ready to send
                for i, message in enumerate(self.message_queue):
                    if message.scheduled_time and message.scheduled_time <= now:
                        messages_to_send.append((i, message))
                        
                # Send messages and remove from queue
                for i, message in reversed(messages_to_send):
                    await self.send_message(message)
                    self.message_queue.pop(i)
                    
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Message queue processing error: {e}")
                await asyncio.sleep(60)
                
    async def get_chat_info(self, chat_id: str) -> Optional[TelegramChannel]:
        """
        Get information about a chat/channel
        
        Args:
            chat_id: Chat/channel identifier
            
        Returns:
            Channel information
        """
        await self._check_rate_limits()
        
        try:
            async with self.session.get(
                f"{self.bot_base_url}/getChat",
                params={'chat_id': chat_id}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        chat_data = data.get('result', {})
                        
                        # Determine channel type
                        chat_type = chat_data.get('type', 'private')
                        if chat_type == 'channel':
                            channel_type = TelegramChannelType.CHANNEL
                        elif chat_type == 'supergroup':
                            channel_type = TelegramChannelType.SUPERGROUP
                        elif chat_type == 'private':
                            channel_type = TelegramChannelType.PRIVATE
                        else:
                            channel_type = TelegramChannelType.PUBLIC
                            
                        return TelegramChannel(
                            chat_id=str(chat_data.get('id')),
                            title=chat_data.get('title', chat_data.get('first_name', 'Unknown')),
                            username=chat_data.get('username'),
                            channel_type=channel_type,
                            members_count=chat_data.get('member_count', 0),
                            description=chat_data.get('description'),
                            invite_link=chat_data.get('invite_link'),
                            is_verified=chat_data.get('is_verified', False)
                        )
                        
                logger.error(f"Failed to get chat info for {chat_id}")
                return None
                
        except Exception as e:
            logger.error(f"Chat info retrieval error: {e}")
            return None
            
    async def get_message_metrics(self, chat_id: str, message_id: str) -> Optional[TelegramMetrics]:
        """
        Get message performance metrics (requires premium API access)
        
        Args:
            chat_id: Chat identifier
            message_id: Message identifier
            
        Returns:
            Message metrics
        """
        # Note: This requires Telegram Premium API access for detailed analytics
        # For basic bot API, we can only get limited information
        
        try:
            # Basic implementation - would need premium API for full metrics
            return TelegramMetrics(
                message_id=message_id,
                chat_id=chat_id,
                views=0,  # Not available in basic bot API
                forwards=0,  # Not available in basic bot API
                reactions={},  # Not available in basic bot API
                replies=0,  # Would need to track separately
                engagement_rate=0.0,
                reach=0  # Not available in basic bot API
            )
            
        except Exception as e:
            logger.error(f"Metrics retrieval error: {e}")
            return None
            
    async def create_invite_link(self, chat_id: str, expire_date: Optional[datetime] = None, 
                                member_limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Create invite link for a chat/channel
        
        Args:
            chat_id: Chat identifier
            expire_date: Link expiration date
            member_limit: Maximum members through this link
            
        Returns:
            Invite link creation result
        """
        await self._check_rate_limits()
        
        try:
            payload = {'chat_id': chat_id}
            
            if expire_date:
                payload['expire_date'] = int(expire_date.timestamp())
            if member_limit:
                payload['member_limit'] = member_limit
                
            async with self.session.post(
                f"{self.bot_base_url}/createChatInviteLink",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        result = data.get('result', {})
                        logger.info(f"Invite link created for chat {chat_id}")
                        return {
                            'success': True,
                            'invite_link': result.get('invite_link'),
                            'expire_date': result.get('expire_date'),
                            'member_limit': result.get('member_limit')
                        }
                        
                error_text = await response.text()
                logger.error(f"Failed to create invite link: {error_text}")
                return {'success': False, 'error': error_text}
                
        except Exception as e:
            logger.error(f"Invite link creation error: {e}")
            return {'success': False, 'error': str(e)}
            
    async def bulk_send_messages(self, messages: List[TelegramMessage]) -> List[Dict[str, Any]]:
        """
        Send multiple messages with rate limiting
        
        Args:
            messages: List of messages to send
            
        Returns:
            List of send results
        """
        results = []
        
        for i, message in enumerate(messages):
            # Rate limiting for bulk sends
            if i > 0 and i % self.rate_limits['bulk_messages_per_minute'] == 0:
                logger.info("Rate limiting bulk send, waiting 60 seconds...")
                await asyncio.sleep(60)
                
            result = await self.send_message(message)
            results.append(result)
            
            # Small delay between messages
            await asyncio.sleep(1)
            
        logger.info(f"Bulk send completed: {len(results)} messages processed")
        return results
        
    async def forward_message(self, from_chat_id: str, to_chat_id: str, 
                            message_id: str, disable_notification: bool = False) -> Dict[str, Any]:
        """
        Forward a message between chats
        
        Args:
            from_chat_id: Source chat ID
            to_chat_id: Destination chat ID
            message_id: Message to forward
            disable_notification: Silent forwarding
            
        Returns:
            Forward result
        """
        await self._check_rate_limits()
        
        try:
            payload = {
                'chat_id': to_chat_id,
                'from_chat_id': from_chat_id,
                'message_id': message_id,
                'disable_notification': disable_notification
            }
            
            async with self.session.post(
                f"{self.bot_base_url}/forwardMessage",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        result = data.get('result', {})
                        new_message_id = result.get('message_id')
                        logger.info(f"Message forwarded successfully: {new_message_id}")
                        return {
                            'success': True,
                            'message_id': new_message_id,
                            'chat_id': to_chat_id
                        }
                        
                error_text = await response.text()
                logger.error(f"Failed to forward message: {error_text}")
                return {'success': False, 'error': error_text}
                
        except Exception as e:
            logger.error(f"Message forward error: {e}")
            return {'success': False, 'error': str(e)}


class TelegramDistributionManager:
    """
    High-level manager for Telegram distribution strategies
    Handles channel management, content optimization, and audience engagement
    """
    
    def __init__(self, connector: TelegramConnector):
        self.connector = connector
        self.channels: List[TelegramChannel] = []
        self.performance_history: List[TelegramMetrics] = []
        
    async def add_distribution_channel(self, chat_id: str) -> bool:
        """
        Add a channel to distribution list
        
        Args:
            chat_id: Channel identifier
            
        Returns:
            Success status
        """
        try:
            channel_info = await self.connector.get_chat_info(chat_id)
            if channel_info:
                self.channels.append(channel_info)
                logger.info(f"Added distribution channel: {channel_info.title}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to add distribution channel: {e}")
            return False
            
    async def distribute_content(self, content: Dict[str, Any], 
                               target_channels: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Distribute content across multiple channels
        
        Args:
            content: Content to distribute
            target_channels: Specific channels (if None, uses all)
            
        Returns:
            Distribution results
        """
        if target_channels:
            channels = [c for c in self.channels if c.chat_id in target_channels]
        else:
            channels = self.channels
            
        messages = []
        for channel in channels:
            # Adapt content for each channel
            adapted_message = await self._adapt_content_for_channel(content, channel)
            messages.append(adapted_message)
            
        # Send messages
        results = await self.connector.bulk_send_messages(messages)
        
        logger.info(f"Content distributed to {len(channels)} channels")
        return results
        
    async def _adapt_content_for_channel(self, content: Dict[str, Any], 
                                       channel: TelegramChannel) -> TelegramMessage:
        """
        Adapt content format for specific channel
        
        Args:
            content: Original content
            channel: Target channel
            
        Returns:
            Adapted message
        """
        # Basic content adaptation logic
        text = content.get('text', '')
        
        # Add channel-specific formatting
        if channel.channel_type == TelegramChannelType.CHANNEL:
            # Formal formatting for channels
            text = f"📢 {content.get('title', '')}\n\n{text}"
        elif channel.channel_type == TelegramChannelType.SUPERGROUP:
            # Interactive formatting for groups
            text = f"💬 {content.get('title', '')}\n\n{text}\n\nWhat do you think? 🤔"
            
        # Create inline keyboard if appropriate
        reply_markup = None
        if content.get('call_to_action'):
            reply_markup = {
                'inline_keyboard': [[
                    {
                        'text': content['call_to_action']['text'],
                        'url': content['call_to_action']['url']
                    }
                ]]
            }
            
        return TelegramMessage(
            chat_id=channel.chat_id,
            text=text,
            message_type=TelegramMessageType(content.get('type', 'text')),
            media_url=content.get('media_url'),
            media_caption=content.get('caption'),
            reply_markup=reply_markup,
            scheduled_time=content.get('scheduled_time')
        )
        
    def analyze_channel_performance(self) -> Dict[str, Any]:
        """
        Analyze performance across all distribution channels
        
        Returns:
            Performance analysis and insights
        """
        if not self.performance_history:
            return {'message': 'No performance data available'}
            
        try:
            # Group metrics by channel
            channel_metrics = {}
            for metric in self.performance_history:
                chat_id = metric.chat_id
                if chat_id not in channel_metrics:
                    channel_metrics[chat_id] = []
                channel_metrics[chat_id].append(metric)
                
            # Calculate channel performance
            channel_performance = {}
            for chat_id, metrics in channel_metrics.items():
                avg_engagement = np.mean([m.engagement_rate for m in metrics])
                total_reach = sum([m.reach for m in metrics])
                
                channel = next((c for c in self.channels if c.chat_id == chat_id), None)
                channel_name = channel.title if channel else chat_id
                
                channel_performance[channel_name] = {
                    'average_engagement': round(avg_engagement, 2),
                    'total_reach': total_reach,
                    'messages_sent': len(metrics),
                    'best_performing_time': self._find_best_time(metrics)
                }
                
            return {
                'total_channels': len(self.channels),
                'total_messages': len(self.performance_history),
                'channel_performance': channel_performance,
                'recommendations': self._generate_distribution_recommendations(channel_performance)
            }
            
        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
            return {'error': str(e)}
            
    def _find_best_time(self, metrics: List[TelegramMetrics]) -> str:
        """Find best performing time of day"""
        if not metrics:
            return "No data"
            
        hour_performance = {}
        for metric in metrics:
            hour = metric.timestamp.hour
            if hour not in hour_performance:
                hour_performance[hour] = []
            hour_performance[hour].append(metric.engagement_rate)
            
        if not hour_performance:
            return "No data"
            
        best_hour = max(hour_performance.items(), 
                       key=lambda x: np.mean(x[1]))[0]
        return f"{best_hour:02d}:00"
        
    def _generate_distribution_recommendations(self, performance: Dict[str, Any]) -> List[str]:
        """Generate distribution recommendations"""
        recommendations = []
        
        if not performance:
            recommendations.append("Add more distribution channels for better reach")
            return recommendations
            
        # Find best and worst performing channels
        channels = list(performance.keys())
        if len(channels) > 1:
            best_channel = max(channels, key=lambda x: performance[x]['average_engagement'])
            worst_channel = min(channels, key=lambda x: performance[x]['average_engagement'])
            
            recommendations.append(f"Best performing channel: {best_channel}")
            recommendations.append(f"Consider improving content strategy for: {worst_channel}")
            
        # General recommendations
        avg_engagement = np.mean([data['average_engagement'] for data in performance.values()])
        if avg_engagement < 5:
            recommendations.append("Low engagement rates - consider more interactive content")
        elif avg_engagement > 15:
            recommendations.append("Great engagement! Consider expanding to similar channels")
            
        return recommendations


# Export main classes
__all__ = [
    'TelegramConnector',
    'TelegramDistributionManager',
    'TelegramMessage',
    'TelegramChannel', 
    'TelegramMetrics',
    'TelegramCredentials',
    'TelegramMessageType',
    'TelegramChannelType'
]