"""Messaging System - Real-Time Communication Engine
===================================================

Advanced messaging system providing:
- Real-time messaging and chat
- Multi-format message support
- Message encryption and security
- Chat rooms and conversations
- Message threading and replies
- Read receipts and presence

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    LOCATION = "location"
    SYSTEM = "system"
    REACTION = "reaction"
    THREAD_REPLY = "thread_reply"


class MessageStatus(Enum):
    """Message delivery status"""
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    ENCRYPTED = "encrypted"


class ConversationType(Enum):
    """Types of conversations"""
    DIRECT = "direct"
    GROUP = "group"
    PROJECT = "project"
    CHANNEL = "channel"
    BROADCAST = "broadcast"


class UserPresence(Enum):
    """User presence status"""
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"
    INVISIBLE = "invisible"


@dataclass
class Message:
    """Message definition"""
    message_id: str
    conversation_id: str
    sender_id: str
    content: str
    message_type: MessageType
    timestamp: datetime = field(default_factory=datetime.now)
    status: MessageStatus = MessageStatus.SENDING
    reply_to: Optional[str] = None
    thread_id: Optional[str] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    reactions: Dict[str, List[str]] = field(default_factory=dict)  # emoji -> user_ids
    mentions: List[str] = field(default_factory=list)
    edited_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.message_id:
            self.message_id = str(uuid.uuid4())


@dataclass
class Conversation:
    """Conversation definition"""
    conversation_id: str
    name: str
    conversation_type: ConversationType
    participants: List[str] = field(default_factory=list)
    admins: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_message_at: Optional[datetime] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    
    def __post_init__(self):
        if not self.conversation_id:
            self.conversation_id = str(uuid.uuid4())


@dataclass
class ChatRoom:
    """Chat room for project collaboration"""
    room_id: str
    project_id: str
    name: str
    description: str = ""
    room_type: str = "general"
    participants: List[str] = field(default_factory=list)
    moderators: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.room_id:
            self.room_id = str(uuid.uuid4())


@dataclass
class UserSession:
    """User session information"""
    user_id: str
    session_id: str
    presence: UserPresence = UserPresence.ONLINE
    last_seen: datetime = field(default_factory=datetime.now)
    device_info: Dict[str, Any] = field(default_factory=dict)
    current_conversation: Optional[str] = None


class MessagingSystem:
    """
    Real-Time Messaging System
    
    Provides comprehensive messaging capabilities for collaboration
    with real-time delivery, encryption, and rich media support.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the messaging system"""
        self.config = config or {}
        
        # System settings
        self.encryption_enabled = self.config.get('encryption_enabled', True)
        self.max_message_length = self.config.get('max_message_length', 10000)
        self.message_retention_days = self.config.get('retention_days', 365)
        self.typing_timeout_seconds = self.config.get('typing_timeout', 5)
        
        # WebSocket settings for real-time
        self.websocket_connections = {}
        self.user_sessions = {}
        
        # Data storage
        self.messages = {}
        self.conversations = {}
        self.chat_rooms = {}
        self.message_indices = defaultdict(list)  # For efficient querying
        
        # Real-time features
        self.typing_indicators = defaultdict(set)
        self.presence_status = {}
        self.read_receipts = defaultdict(dict)
        
        # Message filters and moderation
        self.content_filters = []
        self.spam_detection = True
        
        logger.info("MessagingSystem initialized with real-time capabilities")
    
    async def create_conversation(
        self,
        name: str,
        conversation_type: ConversationType,
        creator_id: str,
        participants: List[str],
        settings: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """
        Create a new conversation
        
        Args:
            name: Conversation name
            conversation_type: Type of conversation
            creator_id: Creator user ID
            participants: List of participant user IDs
            settings: Conversation settings
            
        Returns:
            Created conversation
        """
        try:
            conversation = Conversation(
                conversation_id=str(uuid.uuid4()),
                name=name,
                conversation_type=conversation_type,
                participants=participants,
                admins=[creator_id],
                created_by=creator_id,
                settings=settings or {}
            )
            
            self.conversations[conversation.conversation_id] = conversation
            
            # Send system message about conversation creation
            await self._send_system_message(
                conversation.conversation_id,
                f"Conversation '{name}' created by {creator_id}"
            )
            
            # Notify participants
            await self._notify_conversation_created(conversation)
            
            logger.info(f"Conversation '{name}' created with {len(participants)} participants")
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to create conversation: {str(e)}")
            raise
    
    async def send_message(
        self,
        conversation_id: str,
        sender_id: str,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Message:
        """
        Send a message to a conversation
        
        Args:
            conversation_id: Target conversation
            sender_id: Sender user ID
            content: Message content
            message_type: Type of message
            reply_to: Message ID being replied to
            attachments: File attachments
            
        Returns:
            Sent message
        """
        try:
            if conversation_id not in self.conversations:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            conversation = self.conversations[conversation_id]
            
            # Validate sender is participant
            if sender_id not in conversation.participants:
                raise ValueError(f"User {sender_id} not participant in conversation")
            
            # Content filtering
            filtered_content = await self._filter_content(content)
            
            # Extract mentions
            mentions = await self._extract_mentions(content)
            
            # Create message
            message = Message(
                message_id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                sender_id=sender_id,
                content=filtered_content,
                message_type=message_type,
                reply_to=reply_to,
                attachments=attachments or [],
                mentions=mentions
            )
            
            # Encrypt if enabled
            if self.encryption_enabled:
                message.content = await self._encrypt_content(message.content)
                message.status = MessageStatus.ENCRYPTED
            
            # Store message
            self.messages[message.message_id] = message
            self.message_indices[conversation_id].append(message.message_id)
            
            # Update conversation
            conversation.last_message_at = message.timestamp
            
            # Real-time delivery
            await self._deliver_message_realtime(message)
            
            # Mark as sent
            message.status = MessageStatus.SENT
            
            # Handle mentions
            if mentions:
                await self._handle_mentions(message, mentions)
            
            logger.info(f"Message sent in conversation {conversation_id}")
            return message
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            raise
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 50,
        before: Optional[str] = None,
        after: Optional[str] = None
    ) -> List[Message]:
        """
        Get messages from a conversation
        
        Args:
            conversation_id: Conversation ID
            user_id: Requesting user ID
            limit: Maximum messages to return
            before: Get messages before this message ID
            after: Get messages after this message ID
            
        Returns:
            List of messages
        """
        try:
            if conversation_id not in self.conversations:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            conversation = self.conversations[conversation_id]
            
            # Validate user access
            if user_id not in conversation.participants:
                raise ValueError(f"User {user_id} not authorized for conversation")
            
            # Get message IDs for conversation
            message_ids = self.message_indices.get(conversation_id, [])
            
            # Apply pagination filters
            if before:
                try:
                    before_index = message_ids.index(before)
                    message_ids = message_ids[:before_index]
                except ValueError:
                    pass
            
            if after:
                try:
                    after_index = message_ids.index(after)
                    message_ids = message_ids[after_index + 1:]
                except ValueError:
                    pass
            
            # Apply limit
            message_ids = message_ids[-limit:]
            
            # Get messages
            messages = []
            for msg_id in message_ids:
                if msg_id in self.messages:
                    message = self.messages[msg_id]
                    
                    # Decrypt if needed
                    if self.encryption_enabled and message.status == MessageStatus.ENCRYPTED:
                        decrypted_message = await self._decrypt_message(message)
                        messages.append(decrypted_message)
                    else:
                        messages.append(message)
            
            # Mark messages as read
            await self._mark_messages_read(user_id, [m.message_id for m in messages])
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get conversation messages: {str(e)}")
            raise
    
    async def add_reaction(
        self,
        message_id: str,
        user_id: str,
        emoji: str
    ) -> bool:
        """
        Add reaction to a message
        
        Args:
            message_id: Message to react to
            user_id: User adding reaction
            emoji: Emoji reaction
            
        Returns:
            Success status
        """
        try:
            if message_id not in self.messages:
                raise ValueError(f"Message {message_id} not found")
            
            message = self.messages[message_id]
            
            # Validate user access
            conversation = self.conversations[message.conversation_id]
            if user_id not in conversation.participants:
                raise ValueError(f"User {user_id} not authorized")
            
            # Add reaction
            if emoji not in message.reactions:
                message.reactions[emoji] = []
            
            if user_id not in message.reactions[emoji]:
                message.reactions[emoji].append(user_id)
            
            # Notify real-time
            await self._notify_reaction_added(message, user_id, emoji)
            
            logger.info(f"Reaction {emoji} added to message {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add reaction: {str(e)}")
            return False
    
    async def set_typing_indicator(
        self,
        conversation_id: str,
        user_id: str,
        is_typing: bool
    ):
        """
        Set typing indicator for user in conversation
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            is_typing: Whether user is typing
        """
        try:
            if is_typing:
                self.typing_indicators[conversation_id].add(user_id)
                
                # Auto-remove after timeout
                await asyncio.sleep(self.typing_timeout_seconds)
                self.typing_indicators[conversation_id].discard(user_id)
            else:
                self.typing_indicators[conversation_id].discard(user_id)
            
            # Notify other participants
            await self._notify_typing_indicator(conversation_id, user_id, is_typing)
            
        except Exception as e:
            logger.error(f"Failed to set typing indicator: {str(e)}")
    
    async def set_user_presence(
        self,
        user_id: str,
        presence: UserPresence,
        device_info: Optional[Dict[str, Any]] = None
    ):
        """
        Set user presence status
        
        Args:
            user_id: User ID
            presence: Presence status
            device_info: Device information
        """
        try:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = UserSession(
                    user_id=user_id,
                    session_id=str(uuid.uuid4()),
                    device_info=device_info or {}
                )
            
            session = self.user_sessions[user_id]
            session.presence = presence
            session.last_seen = datetime.now()
            
            self.presence_status[user_id] = presence
            
            # Notify contacts
            await self._notify_presence_change(user_id, presence)
            
            logger.info(f"User {user_id} presence set to {presence.value}")
            
        except Exception as e:
            logger.error(f"Failed to set user presence: {str(e)}")
    
    async def create_chat_room(
        self,
        project_id: str,
        name: str,
        creator_id: str,
        room_type: str = "general",
        description: str = ""
    ) -> ChatRoom:
        """
        Create a chat room for project collaboration
        
        Args:
            project_id: Project ID
            name: Room name
            creator_id: Creator user ID
            room_type: Type of room
            description: Room description
            
        Returns:
            Created chat room
        """
        try:
            room = ChatRoom(
                room_id=str(uuid.uuid4()),
                project_id=project_id,
                name=name,
                description=description,
                room_type=room_type,
                participants=[creator_id],
                moderators=[creator_id]
            )
            
            self.chat_rooms[room.room_id] = room
            
            # Create conversation for the room
            conversation = await self.create_conversation(
                name=f"Room: {name}",
                conversation_type=ConversationType.PROJECT,
                creator_id=creator_id,
                participants=[creator_id],
                settings={'room_id': room.room_id, 'project_id': project_id}
            )
            
            room.settings['conversation_id'] = conversation.conversation_id
            
            logger.info(f"Chat room '{name}' created for project {project_id}")
            return room
            
        except Exception as e:
            logger.error(f"Failed to create chat room: {str(e)}")
            raise
    
    async def join_chat_room(
        self,
        room_id: str,
        user_id: str
    ) -> bool:
        """
        Join a chat room
        
        Args:
            room_id: Room ID to join
            user_id: User ID
            
        Returns:
            Success status
        """
        try:
            if room_id not in self.chat_rooms:
                raise ValueError(f"Chat room {room_id} not found")
            
            room = self.chat_rooms[room_id]
            
            if user_id not in room.participants:
                room.participants.append(user_id)
                
                # Add to conversation
                conversation_id = room.settings.get('conversation_id')
                if conversation_id and conversation_id in self.conversations:
                    conversation = self.conversations[conversation_id]
                    if user_id not in conversation.participants:
                        conversation.participants.append(user_id)
                
                # Send system message
                await self._send_system_message(
                    conversation_id,
                    f"{user_id} joined the room"
                )
                
                logger.info(f"User {user_id} joined room {room_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to join chat room: {str(e)}")
            return False
    
    async def search_messages(
        self,
        user_id: str,
        query: str,
        conversation_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Message]:
        """
        Search messages with full-text search
        
        Args:
            user_id: Searching user ID
            query: Search query
            conversation_id: Optional conversation filter
            limit: Maximum results
            
        Returns:
            List of matching messages
        """
        try:
            results = []
            query_lower = query.lower()
            
            # Get accessible conversations
            accessible_conversations = []
            for conv in self.conversations.values():
                if user_id in conv.participants:
                    if not conversation_id or conv.conversation_id == conversation_id:
                        accessible_conversations.append(conv.conversation_id)
            
            # Search through messages
            for msg_id, message in self.messages.items():
                if message.conversation_id in accessible_conversations:
                    # Simple text search (in production, would use proper search engine)
                    if (query_lower in message.content.lower() or
                        any(query_lower in mention.lower() for mention in message.mentions)):
                        
                        # Decrypt if needed
                        if self.encryption_enabled and message.status == MessageStatus.ENCRYPTED:
                            decrypted_message = await self._decrypt_message(message)
                            results.append(decrypted_message)
                        else:
                            results.append(message)
                        
                        if len(results) >= limit:
                            break
            
            # Sort by relevance/timestamp
            results.sort(key=lambda m: m.timestamp, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search messages: {str(e)}")
            return []
    
    async def _filter_content(self, content: str) -> str:
        """Filter message content for spam/inappropriate content"""
        # Simple content filtering (in production, would use AI/ML)
        filtered_content = content
        
        # Remove potential spam patterns
        spam_patterns = ['buy now', 'click here', 'free money']
        for pattern in spam_patterns:
            if pattern.lower() in content.lower():
                logger.warning(f"Potential spam detected: {pattern}")
        
        return filtered_content
    
    async def _extract_mentions(self, content: str) -> List[str]:
        """Extract user mentions from message content"""
        mentions = []
        
        # Extract @username mentions
        words = content.split()
        for word in words:
            if word.startswith('@') and len(word) > 1:
                username = word[1:].rstrip('.,!?:;')
                mentions.append(username)
        
        return mentions
    
    async def _encrypt_content(self, content: str) -> str:
        """Encrypt message content"""
        # Simple encryption placeholder (in production, use proper encryption)
        import base64
        return base64.b64encode(content.encode()).decode()
    
    async def _decrypt_message(self, message: Message) -> Message:
        """Decrypt message content"""
        # Simple decryption placeholder
        import base64
        try:
            decrypted_content = base64.b64decode(message.content).decode()
            decrypted_message = Message(
                message_id=message.message_id,
                conversation_id=message.conversation_id,
                sender_id=message.sender_id,
                content=decrypted_content,
                message_type=message.message_type,
                timestamp=message.timestamp,
                status=MessageStatus.DELIVERED,
                reply_to=message.reply_to,
                thread_id=message.thread_id,
                attachments=message.attachments,
                metadata=message.metadata,
                reactions=message.reactions,
                mentions=message.mentions,
                edited_at=message.edited_at,
                deleted_at=message.deleted_at
            )
            return decrypted_message
        except Exception:
            return message
    
    async def _deliver_message_realtime(self, message: Message):
        """Deliver message to online participants in real-time"""
        conversation = self.conversations[message.conversation_id]
        
        for participant_id in conversation.participants:
            if participant_id in self.websocket_connections:
                # Send via WebSocket
                await self._send_websocket_message(participant_id, {
                    'type': 'new_message',
                    'message': {
                        'id': message.message_id,
                        'conversation_id': message.conversation_id,
                        'sender_id': message.sender_id,
                        'content': message.content if not self.encryption_enabled else '[Encrypted]',
                        'timestamp': message.timestamp.isoformat(),
                        'message_type': message.message_type.value,
                        'attachments': message.attachments,
                        'mentions': message.mentions
                    }
                })
    
    async def _send_websocket_message(self, user_id: str, data: Dict[str, Any]):
        """Send message via WebSocket to user"""
        # Placeholder for WebSocket implementation
        logger.info(f"WebSocket message sent to {user_id}: {data['type']}")
    
    async def _mark_messages_read(self, user_id: str, message_ids: List[str]):
        """Mark messages as read by user"""
        for message_id in message_ids:
            if message_id in self.messages:
                message = self.messages[message_id]
                if message.sender_id != user_id:  # Don't mark own messages as read
                    self.read_receipts[message_id][user_id] = datetime.now()
                    
                    # Update message status
                    if message.status == MessageStatus.DELIVERED:
                        message.status = MessageStatus.READ
    
    async def _handle_mentions(self, message: Message, mentions: List[str]):
        """Handle user mentions in message"""
        for mention in mentions:
            # Send notification to mentioned user
            await self._send_mention_notification(message, mention)
    
    async def _send_mention_notification(self, message: Message, mentioned_user: str):
        """Send notification for user mention"""
        # Placeholder for notification system integration
        logger.info(f"Mention notification sent to {mentioned_user} for message {message.message_id}")
    
    async def _send_system_message(self, conversation_id: str, content: str):
        """Send system message to conversation"""
        system_message = Message(
            message_id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            sender_id="system",
            content=content,
            message_type=MessageType.SYSTEM,
            status=MessageStatus.SENT
        )
        
        self.messages[system_message.message_id] = system_message
        self.message_indices[conversation_id].append(system_message.message_id)
        
        # Deliver real-time
        await self._deliver_message_realtime(system_message)
    
    async def _notify_conversation_created(self, conversation: Conversation):
        """Notify participants about new conversation"""
        for participant_id in conversation.participants:
            if participant_id in self.websocket_connections:
                await self._send_websocket_message(participant_id, {
                    'type': 'conversation_created',
                    'conversation': {
                        'id': conversation.conversation_id,
                        'name': conversation.name,
                        'type': conversation.conversation_type.value,
                        'participants': conversation.participants
                    }
                })
    
    async def _notify_reaction_added(self, message: Message, user_id: str, emoji: str):
        """Notify about reaction added to message"""
        conversation = self.conversations[message.conversation_id]
        
        for participant_id in conversation.participants:
            if participant_id in self.websocket_connections:
                await self._send_websocket_message(participant_id, {
                    'type': 'reaction_added',
                    'message_id': message.message_id,
                    'user_id': user_id,
                    'emoji': emoji
                })
    
    async def _notify_typing_indicator(self, conversation_id: str, user_id: str, is_typing: bool):
        """Notify about typing indicator"""
        conversation = self.conversations[conversation_id]
        
        for participant_id in conversation.participants:
            if participant_id != user_id and participant_id in self.websocket_connections:
                await self._send_websocket_message(participant_id, {
                    'type': 'typing_indicator',
                    'conversation_id': conversation_id,
                    'user_id': user_id,
                    'is_typing': is_typing
                })
    
    async def _notify_presence_change(self, user_id: str, presence: UserPresence):
        """Notify contacts about presence change"""
        # Find conversations where user is participant
        user_conversations = [
            conv for conv in self.conversations.values()
            if user_id in conv.participants
        ]
        
        # Notify other participants
        notified_users = set()
        for conversation in user_conversations:
            for participant_id in conversation.participants:
                if (participant_id != user_id and 
                    participant_id not in notified_users and
                    participant_id in self.websocket_connections):
                    
                    await self._send_websocket_message(participant_id, {
                        'type': 'presence_change',
                        'user_id': user_id,
                        'presence': presence.value
                    })
                    notified_users.add(participant_id)
    
    async def get_conversation_analytics(self, conversation_id: str) -> Dict[str, Any]:
        """Get analytics for a conversation"""
        if conversation_id not in self.conversations:
            return {}
        
        message_ids = self.message_indices.get(conversation_id, [])
        messages = [self.messages[mid] for mid in message_ids if mid in self.messages]
        
        if not messages:
            return {}
        
        # Calculate metrics
        total_messages = len(messages)
        participants = set(m.sender_id for m in messages if m.sender_id != "system")
        
        # Message frequency by user
        user_message_count = defaultdict(int)
        for message in messages:
            if message.sender_id != "system":
                user_message_count[message.sender_id] += 1
        
        # Most active hours
        hour_activity = defaultdict(int)
        for message in messages:
            hour_activity[message.timestamp.hour] += 1
        
        most_active_hour = max(hour_activity.items(), key=lambda x: x[1])[0] if hour_activity else 0
        
        # Response times (simplified)
        response_times = []
        for i in range(1, len(messages)):
            prev_msg = messages[i-1]
            curr_msg = messages[i]
            if prev_msg.sender_id != curr_msg.sender_id:
                time_diff = (curr_msg.timestamp - prev_msg.timestamp).total_seconds() / 60
                if time_diff < 60:  # Within 1 hour
                    response_times.append(time_diff)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'conversation_id': conversation_id,
            'total_messages': total_messages,
            'unique_participants': len(participants),
            'most_active_user': max(user_message_count.items(), key=lambda x: x[1])[0] if user_message_count else None,
            'most_active_hour': most_active_hour,
            'average_response_time_minutes': avg_response_time,
            'message_types': {
                msg_type.value: sum(1 for m in messages if m.message_type == msg_type)
                for msg_type in MessageType
            }
        }


# Export main classes
__all__ = [
    'MessagingSystem',
    'Message',
    'Conversation', 
    'ChatRoom',
    'UserSession',
    'MessageType',
    'MessageStatus',
    'ConversationType',
    'UserPresence'
]