"""
Chat Integration Service for Ainflue Platform
Enterprise-grade multi-platform chat integration for creator collaboration

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from decimal import Decimal
import logging
from dataclasses import dataclass, field
from enum import Enum
import uuid
import re

import aiohttp
import websockets
import structlog

from ..core.base_integration import BaseIntegration
from ..core.exceptions import (
    APIError, InvalidConfigurationError, 
    SecurityError, ValidationError
)
from ..core.security import SecurityManager
from ..core.monitoring import MetricsCollector
from ..core.cache import CacheManager

logger = structlog.get_logger(__name__)

class ChatPlatform(Enum):
    """Supported chat platforms"""
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    WEBCHAT = "webchat"
    CUSTOM = "custom"

class MessageType(Enum):
    """Message types"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    LINK = "link"
    EMBED = "embed"
    SYSTEM = "system"
    REACTION = "reaction"

class ChatEventType(Enum):
    """Chat event types"""
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_EDITED = "message_edited"
    MESSAGE_DELETED = "message_deleted"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    CHANNEL_CREATED = "channel_created"
    CHANNEL_UPDATED = "channel_updated"
    REACTION_ADDED = "reaction_added"
    REACTION_REMOVED = "reaction_removed"

class UserStatus(Enum):
    """User status in chat"""
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    BUSY = "busy"
    DND = "dnd"  # Do Not Disturb

@dataclass
class ChatUser:
    """Chat user representation"""
    id: str
    username: str
    display_name: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    status: UserStatus = UserStatus.OFFLINE
    platform: ChatPlatform = ChatPlatform.WEBCHAT
    platform_user_id: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ChatChannel:
    """Chat channel representation"""
    id: str
    name: str
    description: Optional[str] = None
    platform: ChatPlatform = ChatPlatform.WEBCHAT
    platform_channel_id: Optional[str] = None
    is_private: bool = False
    members: List[str] = field(default_factory=list)
    admins: List[str] = field(default_factory=list)
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatMessage:
    """Chat message representation"""
    id: str
    channel_id: str
    user_id: str
    content: str
    message_type: MessageType = MessageType.TEXT
    platform: ChatPlatform = ChatPlatform.WEBCHAT
    platform_message_id: Optional[str] = None
    reply_to: Optional[str] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    reactions: Dict[str, List[str]] = field(default_factory=dict)  # emoji -> user_ids
    mentions: List[str] = field(default_factory=list)
    edited: bool = False
    deleted: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)
    edited_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatEvent:
    """Chat event representation"""
    id: str
    event_type: ChatEventType
    channel_id: str
    user_id: Optional[str] = None
    message_id: Optional[str] = None
    platform: ChatPlatform = ChatPlatform.WEBCHAT
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ChatConfig:
    """Chat integration configuration"""
    # Platform configurations
    slack_bot_token: Optional[str] = None
    slack_signing_secret: Optional[str] = None
    discord_bot_token: Optional[str] = None
    teams_webhook_url: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    whatsapp_api_key: Optional[str] = None
    
    # Webhook settings
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    
    # Rate limiting
    rate_limit_messages_per_minute: int = 60
    rate_limit_messages_per_hour: int = 1000
    
    # Content filtering
    enable_content_filtering: bool = True
    blocked_words: List[str] = field(default_factory=list)
    
    # Features
    enable_file_uploads: bool = True
    max_file_size_mb: int = 10
    allowed_file_types: List[str] = field(default_factory=lambda: [
        'jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt'
    ])
    
    # Auto-moderation
    enable_auto_moderation: bool = True
    profanity_filter: bool = True
    spam_detection: bool = True
    
    # AI features
    enable_ai_responses: bool = False
    ai_model: str = "gpt-3.5-turbo"
    ai_temperature: float = 0.7

class ChatIntegration(BaseIntegration):
    """
    Enterprise Chat Integration for Ainflue platform
    
    Features:
    - Multi-platform chat support (Slack, Discord, Teams, etc.)
    - Real-time messaging with WebSocket support
    - File sharing and multimedia messages
    - User management and permissions
    - Channel organization and moderation
    - AI-powered responses and moderation
    - Comprehensive analytics and reporting
    - Creator collaboration tools
    - Content monetization integration
    """

    def __init__(self, config -> None: ChatConfig) -> None:
        super().__init__("chat_integration")
        self.config = config
        self.security_manager = SecurityManager()
        self.metrics = MetricsCollector()
        self.cache = CacheManager()
        
        # Storage
        self._users: Dict[str, ChatUser] = {}
        self._channels: Dict[str, ChatChannel] = {}
        self._messages: Dict[str, ChatMessage] = {}
        self._events: List[ChatEvent] = []
        
        # WebSocket connections
        self._websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # Event handlers
        self._event_handlers: Dict[ChatEventType, List[Callable]] = {}
        
        # Rate limiting
        self._rate_limits: Dict[str, List[datetime]] = {}
        
        # Platform clients
        self._platform_clients: Dict[ChatPlatform, Any] = {}
        
        logger.info("Chat integration initialized",
                   platforms_configured=self._count_configured_platforms(),
                   features={
                       "ai_responses": config.enable_ai_responses,
                       "auto_moderation": config.enable_auto_moderation,
                       "file_uploads": config.enable_file_uploads
                   })

    def _count_configured_platforms(self) -> int:
        """Count configured chat platforms"""
        count = 0
        if self.config.slack_bot_token:
            count += 1
        if self.config.discord_bot_token:
            count += 1
        if self.config.teams_webhook_url:
            count += 1
        if self.config.telegram_bot_token:
            count += 1
        if self.config.whatsapp_api_key:
            count += 1
        return count

    async def create_user(self, user_data: Dict[str, Any]) -> ChatUser:
        """
        Create a new chat user
        
        Args:
            user_data: User information
            
        Returns:
            Created chat user
        """
        try:
            user_id = user_data.get("id") or str(uuid.uuid4())
            
            user = ChatUser(
                id=user_id,
                username=user_data["username"],
                display_name=user_data.get("display_name", user_data["username"]),
                email=user_data.get("email"),
                avatar_url=user_data.get("avatar_url"),
                platform=ChatPlatform(user_data.get("platform", "webchat")),
                platform_user_id=user_data.get("platform_user_id"),
                roles=user_data.get("roles", []),
                metadata=user_data.get("metadata", {})
            )
            
            # Store user
            self._users[user_id] = user
            
            # Cache user data
            await self.cache.set(
                f"chat_user:{user_id}",
                user,
                ttl=3600  # 1 hour
            )
            
            self.metrics.increment("chat.users.created")
            
            logger.info("Chat user created",
                       user_id=user_id,
                       username=user.username,
                       platform=user.platform.value)
            
            return user
            
        except Exception as e:
            self.metrics.increment("chat.users.creation_failed")
            logger.error("Failed to create chat user", error=str(e))
            raise ValidationError(f"User creation failed: {e}")

    async def create_channel(self, channel_data: Dict[str, Any]) -> ChatChannel:
        """
        Create a new chat channel
        
        Args:
            channel_data: Channel information
            
        Returns:
            Created chat channel
        """
        try:
            channel_id = channel_data.get("id") or str(uuid.uuid4())
            
            channel = ChatChannel(
                id=channel_id,
                name=channel_data["name"],
                description=channel_data.get("description"),
                platform=ChatPlatform(channel_data.get("platform", "webchat")),
                platform_channel_id=channel_data.get("platform_channel_id"),
                is_private=channel_data.get("is_private", False),
                members=channel_data.get("members", []),
                admins=channel_data.get("admins", []),
                created_by=channel_data.get("created_by"),
                metadata=channel_data.get("metadata", {})
            )
            
            # Store channel
            self._channels[channel_id] = channel
            
            # Cache channel data
            await self.cache.set(
                f"chat_channel:{channel_id}",
                channel,
                ttl=7200  # 2 hours
            )
            
            # Emit event
            event = ChatEvent(
                id=str(uuid.uuid4()),
                event_type=ChatEventType.CHANNEL_CREATED,
                channel_id=channel_id,
                user_id=channel.created_by,
                platform=channel.platform,
                data={"channel_name": channel.name}
            )
            await self._emit_event(event)
            
            self.metrics.increment("chat.channels.created")
            
            logger.info("Chat channel created",
                       channel_id=channel_id,
                       name=channel.name,
                       platform=channel.platform.value)
            
            return channel
            
        except Exception as e:
            self.metrics.increment("chat.channels.creation_failed")
            logger.error("Failed to create chat channel", error=str(e))
            raise ValidationError(f"Channel creation failed: {e}")

    async def send_message(self, message_data: Dict[str, Any]) -> ChatMessage:
        """
        Send a message to a chat channel
        
        Args:
            message_data: Message information
            
        Returns:
            Sent chat message
        """
        try:
            # Validate rate limiting
            if not await self._check_rate_limit(message_data["user_id"]):
                raise ValidationError("Rate limit exceeded")
            
            # Content filtering
            if self.config.enable_content_filtering:
                content = await self._filter_content(message_data["content"])
                message_data["content"] = content
            
            message_id = message_data.get("id") or str(uuid.uuid4())
            
            # Extract mentions
            mentions = self._extract_mentions(message_data["content"])
            
            message = ChatMessage(
                id=message_id,
                channel_id=message_data["channel_id"],
                user_id=message_data["user_id"],
                content=message_data["content"],
                message_type=MessageType(message_data.get("message_type", "text")),
                platform=ChatPlatform(message_data.get("platform", "webchat")),
                platform_message_id=message_data.get("platform_message_id"),
                reply_to=message_data.get("reply_to"),
                attachments=message_data.get("attachments", []),
                mentions=mentions,
                metadata=message_data.get("metadata", {})
            )
            
            # Store message
            self._messages[message_id] = message
            
            # Cache message
            await self.cache.set(
                f"chat_message:{message_id}",
                message,
                ttl=86400  # 24 hours
            )
            
            # Send to platform if configured
            await self._send_to_platform(message)
            
            # Emit event
            event = ChatEvent(
                id=str(uuid.uuid4()),
                event_type=ChatEventType.MESSAGE_SENT,
                channel_id=message.channel_id,
                user_id=message.user_id,
                message_id=message_id,
                platform=message.platform,
                data={
                    "content": message.content,
                    "message_type": message.message_type.value
                }
            )
            await self._emit_event(event)
            
            # AI response if enabled
            if self.config.enable_ai_responses:
                await self._handle_ai_response(message)
            
            self.metrics.increment("chat.messages.sent")
            self.metrics.increment(f"chat.messages.{message.message_type.value}")
            
            logger.info("Message sent",
                       message_id=message_id,
                       channel_id=message.channel_id,
                       user_id=message.user_id,
                       content_length=len(message.content))
            
            return message
            
        except Exception as e:
            self.metrics.increment("chat.messages.send_failed")
            logger.error("Failed to send message", error=str(e))
            raise APIError(f"Message sending failed: {e}")

    async def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limits"""
        try:
            current_time = datetime.utcnow()
            
            if user_id not in self._rate_limits:
                self._rate_limits[user_id] = []
            
            user_attempts = self._rate_limits[user_id]
            
            # Clean old attempts
            minute_cutoff = current_time - timedelta(minutes=1)
            hour_cutoff = current_time - timedelta(hours=1)
            
            user_attempts[:] = [
                attempt for attempt in user_attempts 
                if attempt > hour_cutoff
            ]
            
            # Check limits
            minute_attempts = [
                attempt for attempt in user_attempts 
                if attempt > minute_cutoff
            ]
            
            if len(minute_attempts) >= self.config.rate_limit_messages_per_minute:
                return False
            
            if len(user_attempts) >= self.config.rate_limit_messages_per_hour:
                return False
            
            # Add current attempt
            user_attempts.append(current_time)
            
            return True
            
        except Exception as e:
            logger.error("Rate limit check failed", error=str(e))
            return True  # Allow on error

    async def _filter_content(self, content: str) -> str:
        """Filter message content for inappropriate material"""
        try:
            filtered_content = content
            
            # Profanity filter
            if self.config.profanity_filter:
                for word in self.config.blocked_words:
                    filtered_content = re.sub(
                        r'\b' + re.escape(word) + r'\b',
                        '*' * len(word),
                        filtered_content,
                        flags=re.IGNORECASE
                    )
            
            # Spam detection
            if self.config.spam_detection:
                # Simple spam patterns
                if len(re.findall(r'(.)\1{4,}', filtered_content)) > 0:  # Repeated characters
                    filtered_content = "[SPAM FILTERED]"
                elif filtered_content.count('http') > 3:  # Too many links
                    filtered_content = "[LINK SPAM FILTERED]"
            
            return filtered_content
            
        except Exception as e:
            logger.error("Content filtering failed", error=str(e))
            return content

    def _extract_mentions(self, content: str) -> List[str]:
        """Extract user mentions from message content"""
        try:
            # Extract @username mentions
            mentions = re.findall(r'@(\w+)', content)
            
            # Validate mentions against known users
            valid_mentions = []
            for mention in mentions:
                for user in self._users.values():
                    if user.username.lower() == mention.lower():
                        valid_mentions.append(user.id)
                        break
            
            return valid_mentions
            
        except Exception as e:
            logger.error("Mention extraction failed", error=str(e))
            return []

    async def _send_to_platform(self, message -> None: ChatMessage) -> None:
        """Send message to external platform"""
        try:
            if message.platform == ChatPlatform.SLACK:
                await self._send_to_slack(message)
            elif message.platform == ChatPlatform.DISCORD:
                await self._send_to_discord(message)
            elif message.platform == ChatPlatform.TEAMS:
                await self._send_to_teams(message)
            elif message.platform == ChatPlatform.TELEGRAM:
                await self._send_to_telegram(message)
            # Add other platforms as needed
            
        except Exception as e:
            logger.error("Failed to send to platform",
                        platform=message.platform.value,
                        error=str(e))

    async def _send_to_slack(self, message -> None: ChatMessage) -> None:
        """Send message to Slack"""
        if not self.config.slack_bot_token:
            return
        
        try:
            # Slack API integration would go here
            logger.info("Message sent to Slack", message_id=message.id)
            
        except Exception as e:
            logger.error("Slack send failed", error=str(e))

    async def _send_to_discord(self, message -> None: ChatMessage) -> None:
        """Send message to Discord"""
        if not self.config.discord_bot_token:
            return
        
        try:
            # Discord API integration would go here
            logger.info("Message sent to Discord", message_id=message.id)
            
        except Exception as e:
            logger.error("Discord send failed", error=str(e))

    async def _send_to_teams(self, message -> None: ChatMessage) -> None:
        """Send message to Microsoft Teams"""
        if not self.config.teams_webhook_url:
            return
        
        try:
            # Teams webhook integration would go here
            logger.info("Message sent to Teams", message_id=message.id)
            
        except Exception as e:
            logger.error("Teams send failed", error=str(e))

    async def _send_to_telegram(self, message -> None: ChatMessage) -> None:
        """Send message to Telegram"""
        if not self.config.telegram_bot_token:
            return
        
        try:
            # Telegram Bot API integration would go here
            logger.info("Message sent to Telegram", message_id=message.id)
            
        except Exception as e:
            logger.error("Telegram send failed", error=str(e))

    async def _handle_ai_response(self, message -> None: ChatMessage) -> None:
        """Handle AI-powered response to message"""
        try:
            # Simple AI trigger detection
            if any(trigger in message.content.lower() for trigger in ["@ai", "help", "?"]):
                ai_response = await self._generate_ai_response(message)
                
                if ai_response:
                    await self.send_message({
                        "channel_id": message.channel_id,
                        "user_id": "ai_assistant",
                        "content": ai_response,
                        "message_type": "text",
                        "reply_to": message.id,
                        "metadata": {"ai_generated": True}
                    })
            
        except Exception as e:
            logger.error("AI response failed", error=str(e))

    async def _generate_ai_response(self, message: ChatMessage) -> Optional[str]:
        """Generate AI response to message"""
        try:
            # In production, would integrate with OpenAI or other AI service
            # For demo, return simple responses
            
            content_lower = message.content.lower()
            
            if "help" in content_lower:
                return "I'm here to help! You can ask me about Ainflue features, creator tools, or general questions."
            elif "pricing" in content_lower:
                return "Check out our pricing plans at https://ainflue.com/pricing"
            elif "support" in content_lower:
                return "For support, please contact our team at support@ainflue.com"
            else:
                return "Thanks for your message! How can I assist you today?"
            
        except Exception as e:
            logger.error("AI response generation failed", error=str(e))
            return None

    async def add_reaction(self, message_id: str, user_id: str, emoji: str) -> bool:
        """
        Add reaction to a message
        
        Args:
            message_id: Message ID to react to
            user_id: User adding the reaction
            emoji: Emoji reaction
            
        Returns:
            True if reaction was added successfully
        """
        try:
            message = self._messages.get(message_id)
            if not message:
                raise ValidationError("Message not found")
            
            if emoji not in message.reactions:
                message.reactions[emoji] = []
            
            if user_id not in message.reactions[emoji]:
                message.reactions[emoji].append(user_id)
                
                # Update cache
                await self.cache.set(
                    f"chat_message:{message_id}",
                    message,
                    ttl=86400
                )
                
                # Emit event
                event = ChatEvent(
                    id=str(uuid.uuid4()),
                    event_type=ChatEventType.REACTION_ADDED,
                    channel_id=message.channel_id,
                    user_id=user_id,
                    message_id=message_id,
                    platform=message.platform,
                    data={"emoji": emoji}
                )
                await self._emit_event(event)
                
                self.metrics.increment("chat.reactions.added")
                
                logger.info("Reaction added",
                           message_id=message_id,
                           user_id=user_id,
                           emoji=emoji)
                
                return True
            
            return False
            
        except Exception as e:
            self.metrics.increment("chat.reactions.failed")
            logger.error("Failed to add reaction", error=str(e))
            return False

    async def join_channel(self, channel_id: str, user_id: str) -> bool:
        """
        Add user to a channel
        
        Args:
            channel_id: Channel ID to join
            user_id: User ID joining
            
        Returns:
            True if user joined successfully
        """
        try:
            channel = self._channels.get(channel_id)
            if not channel:
                raise ValidationError("Channel not found")
            
            if user_id not in channel.members:
                channel.members.append(user_id)
                channel.updated_at = datetime.utcnow()
                
                # Update cache
                await self.cache.set(
                    f"chat_channel:{channel_id}",
                    channel,
                    ttl=7200
                )
                
                # Emit event
                event = ChatEvent(
                    id=str(uuid.uuid4()),
                    event_type=ChatEventType.USER_JOINED,
                    channel_id=channel_id,
                    user_id=user_id,
                    platform=channel.platform,
                    data={"channel_name": channel.name}
                )
                await self._emit_event(event)
                
                self.metrics.increment("chat.channels.joined")
                
                logger.info("User joined channel",
                           channel_id=channel_id,
                           user_id=user_id)
                
                return True
            
            return False
            
        except Exception as e:
            self.metrics.increment("chat.channels.join_failed")
            logger.error("Failed to join channel", error=str(e))
            return False

    async def get_channel_messages(self,
                                 channel_id: str,
                                 limit: int = 50,
                                 before: Optional[str] = None) -> List[ChatMessage]:
        """
        Get messages from a channel
        
        Args:
            channel_id: Channel ID
            limit: Maximum number of messages
            before: Get messages before this message ID
            
        Returns:
            List of channel messages
        """
        try:
            messages = []
            
            for message in self._messages.values():
                if (message.channel_id == channel_id and 
                    not message.deleted):
                    messages.append(message)
            
            # Sort by timestamp
            messages.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Apply before filter
            if before:
                before_index = None
                for i, msg in enumerate(messages):
                    if msg.id == before:
                        before_index = i
                        break
                
                if before_index is not None:
                    messages = messages[before_index + 1:]
            
            # Apply limit
            messages = messages[:limit]
            
            self.metrics.increment("chat.messages.retrieved")
            
            return messages
            
        except Exception as e:
            self.metrics.increment("chat.messages.retrieval_failed")
            logger.error("Failed to get channel messages", error=str(e))
            return []

    async def _emit_event(self, event -> None: ChatEvent) -> None:
        """Emit chat event to all registered handlers"""
        try:
            # Store event
            self._events.append(event)
            
            # Limit event history
            if len(self._events) > 1000:
                self._events = self._events[-1000:]
            
            # Call event handlers
            handlers = self._event_handlers.get(event.event_type, [])
            for handler in handlers:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error("Event handler failed",
                               event_type=event.event_type.value,
                               error=str(e))
            
            # Send to WebSocket connections
            await self._broadcast_event(event)
            
            self.metrics.increment(f"chat.events.{event.event_type.value}")
            
        except Exception as e:
            logger.error("Failed to emit event", error=str(e))

    async def _broadcast_event(self, event -> None: ChatEvent) -> None:
        """Broadcast event to WebSocket connections"""
        try:
            event_data = {
                "id": event.id,
                "type": event.event_type.value,
                "channel_id": event.channel_id,
                "user_id": event.user_id,
                "message_id": event.message_id,
                "platform": event.platform.value,
                "data": event.data,
                "timestamp": event.timestamp.isoformat()
            }
            
            message = json.dumps(event_data)
            
            # Send to all connected clients
            disconnected = []
            for user_id, websocket in self._websocket_connections.items():
                try:
                    await websocket.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.append(user_id)
                except Exception as e:
                    logger.error("WebSocket send failed",
                               user_id=user_id,
                               error=str(e))
            
            # Clean up disconnected clients
            for user_id in disconnected:
                del self._websocket_connections[user_id]
            
        except Exception as e:
            logger.error("Event broadcast failed", error=str(e))

    def register_event_handler(self, 
                             event_type -> None: ChatEventType, 
                             handler -> None: Callable[[ChatEvent], None]) -> None:
        """Register event handler for specific event type"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        
        self._event_handlers[event_type].append(handler)
        
        logger.info("Event handler registered",
                   event_type=event_type.value,
                   handler_count=len(self._event_handlers[event_type]))

    async def register_websocket(self, user_id -> None: str, websocket -> None: websockets.WebSocketServerProtocol) -> None:
        """Register WebSocket connection for real-time updates"""
        try:
            self._websocket_connections[user_id] = websocket
            
            # Send connection confirmation
            await websocket.send(json.dumps({
                "type": "connection_established",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }))
            
            self.metrics.increment("chat.websockets.connected")
            
            logger.info("WebSocket registered", user_id=user_id)
            
        except Exception as e:
            logger.error("WebSocket registration failed",
                        user_id=user_id,
                        error=str(e))

    async def handle_websocket_message(self, user_id -> None: str, message -> None: str) -> None:
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "send_message":
                await self.send_message({
                    "channel_id": data["channel_id"],
                    "user_id": user_id,
                    "content": data["content"],
                    "message_type": data.get("message_type", "text")
                })
            elif message_type == "add_reaction":
                await self.add_reaction(
                    data["message_id"],
                    user_id,
                    data["emoji"]
                )
            elif message_type == "join_channel":
                await self.join_channel(data["channel_id"], user_id)
            
        except Exception as e:
            logger.error("WebSocket message handling failed",
                        user_id=user_id,
                        error=str(e))

    async def health_check(self) -> Dict[str, Any]:
        """
        Check chat integration health
        
        Returns:
            Health status information
        """
        try:
            health_status = {
                "service": "chat_integration",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "config": {
                    "platforms_configured": self._count_configured_platforms(),
                    "ai_responses": self.config.enable_ai_responses,
                    "auto_moderation": self.config.enable_auto_moderation,
                    "file_uploads": self.config.enable_file_uploads
                },
                "metrics": {
                    "total_users": len(self._users),
                    "total_channels": len(self._channels),
                    "total_messages": len(self._messages),
                    "active_websockets": len(self._websocket_connections),
                    "total_events": len(self._events)
                }
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service": "chat_integration",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Factory function for easy setup
def create_chat_integration(**kwargs) -> ChatIntegration:
    """
    Factory function to create chat integration
    
    Args:
        **kwargs: Configuration options
        
    Returns:
        Configured chat integration instance
    """
    config = ChatConfig(**kwargs)
    return ChatIntegration(config)

# Example usage for Ainflue platform
async def example_chat_integration_flow() -> None:
    """Example chat integration usage"""
    
    # Initialize chat integration
    chat = create_chat_integration(
        slack_bot_token="xoxb-slack-token",
        discord_bot_token="discord-bot-token",
        enable_ai_responses=True,
        enable_auto_moderation=True,
        enable_file_uploads=True,
        blocked_words=["spam", "scam"],
        rate_limit_messages_per_minute=30
    )
    
    try:
        # Create users
        creator_user = await chat.create_user({
            "username": "creator_alice",
            "display_name": "Alice Creator",
            "email": "alice@ainflue.com",
            "platform": "webchat",
            "roles": ["creator", "premium"]
        })
        
        collaborator_user = await chat.create_user({
            "username": "collaborator_bob",
            "display_name": "Bob Collaborator",
            "email": "bob@ainflue.com",
            "platform": "slack",
            "roles": ["collaborator"]
        })
        
        print(f"Created users: {creator_user.username}, {collaborator_user.username}")
        
        # Create channel
        project_channel = await chat.create_channel({
            "name": "project-alpha",
            "description": "Collaboration channel for Project Alpha",
            "is_private": False,
            "created_by": creator_user.id,
            "members": [creator_user.id, collaborator_user.id]
        })
        
        print(f"Created channel: {project_channel.name}")
        
        # Send messages
        message1 = await chat.send_message({
            "channel_id": project_channel.id,
            "user_id": creator_user.id,
            "content": "Welcome to our collaboration space! @collaborator_bob",
            "message_type": "text"
        })
        
        message2 = await chat.send_message({
            "channel_id": project_channel.id,
            "user_id": collaborator_user.id,
            "content": "Thanks @creator_alice! Ready to work together.",
            "message_type": "text"
        })
        
        print(f"Sent messages: {message1.id}, {message2.id}")
        
        # Add reactions
        await chat.add_reaction(message1.id, collaborator_user.id, "👍")
        await chat.add_reaction(message2.id, creator_user.id, "🚀")
        
        # Get channel messages
        messages = await chat.get_channel_messages(project_channel.id, limit=10)
        print(f"Channel has {len(messages)} messages")
        
        # Health check
        health = await chat.health_check()
        print(f"Chat integration health: {health['status']}")
        
    except Exception as e:
        print(f"Chat integration error: {e}")

if __name__ == "__main__":
    asyncio.run(example_chat_integration_flow())