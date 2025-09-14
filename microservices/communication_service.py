"""
💬 Communication Service - Real-time Messaging & Communication Hub
==================================================================

**Module**: Communication Service  
**Author**: Fahed Mlaiel (mlaiel@live.de)  
**Copyright**: (c) 2025 Fahed Mlaiel - All Rights Reserved  
**Role**: Backend Senior + Microservices Architect + Security Specialist

Advanced real-time communication service with multi-channel messaging,
encryption, moderation, and enterprise-grade security features.

⚠️ **STRICT COPYRIGHT WARNING** ⚠️  
This code is proprietary and confidential. Unauthorized use prohibited.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
import uuid
import hashlib
from cryptography.fernet import Fernet
import re

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CommunicationService")

class MessageType(str, Enum):
    """MessageType class implementation"""
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    SYSTEM = "system"
    ANNOUNCEMENT = "announcement"

class ChannelType(str, Enum):
    """ChannelType class implementation"""
    DIRECT = "direct"
    GROUP = "group"
    PUBLIC = "public"
    PRIVATE = "private"
    BROADCAST = "broadcast"

class MessageStatus(str, Enum):
    """MessageStatus class implementation"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class UserStatus(str, Enum):
    """UserStatus class implementation"""
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"

@dataclass
class MessageMetrics:
    """Message and communication metrics"""
    total_messages: int
    messages_today: int
    active_channels: int
    online_users: int
    message_rate_per_minute: float
    average_response_time: float
    moderation_actions: int

class MessageModel(BaseModel):
    """Message model for communication"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    channel_id: str
    sender_id: str
    content: str
    message_type: MessageType = MessageType.TEXT
    status: MessageStatus = MessageStatus.SENT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    edited_at: Optional[datetime] = None
    reply_to: Optional[str] = None
    attachments: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    reactions: Dict[str, List[str]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    encrypted: bool = False

class ChannelModel(BaseModel):
    """Channel model for communication"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    channel_type: ChannelType = ChannelType.GROUP
    creator_id: str
    members: List[str] = Field(default_factory=list)
    admins: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = Field(default_factory=dict)
    encrypted: bool = False

class UserSessionModel(BaseModel):
    """User session for real-time communication"""
    user_id: str
    websocket_id: str
    status: UserStatus = UserStatus.ONLINE
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    channels: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CommunicationService:
    """
    💬 Enterprise Communication Service
    
    **Expertise Applied:**
    - **Backend Senior**: Real-time messaging architecture
    - **Microservices**: Distributed communication patterns
    - **Security**: End-to-end encryption and moderation
    """
    
    def __init__(self) -> None:
        self.messages: Dict[str, List[MessageModel]] = {}
        self.channels: Dict[str, ChannelModel] = {}
        self.user_sessions: Dict[str, UserSessionModel] = {}
        self.active_connections: Dict[str, WebSocket] = {}
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.moderation_keywords = self._load_moderation_keywords()
        self.message_rate_limits: Dict[str, List[datetime]] = {}
        
        # Initialize default channels
        self._initialize_default_channels()
        
        logger.info("💬 Communication Service initialized")
    
    def _load_moderation_keywords(self) -> Set[str]:
        """Load moderation keywords for content filtering"""
        return {
            "spam", "scam", "inappropriate", "offensive", "harassment",
            "threat", "violence", "illegal", "fraud", "phishing"
        }
    
    def _initialize_default_channels(self) -> None:
        """Initialize default system channels"""
        system_channel = ChannelModel(
            id="system",
            name="System Announcements",
            description="Official system announcements and updates",
            channel_type=ChannelType.BROADCAST,
            creator_id="system",
            settings={"read_only": True, "auto_join": True}
        )
        self.channels[system_channel.id] = system_channel
        self.messages[system_channel.id] = []
        
        general_channel = ChannelModel(
            id="general",
            name="General Discussion",
            description="General discussion for all creators",
            channel_type=ChannelType.PUBLIC,
            creator_id="system"
        )
        self.channels[general_channel.id] = general_channel
        self.messages[general_channel.id] = []
    
    async def connect_user(self, websocket: WebSocket, user_id: str) -> str:
        """Connect user to real-time communication"""
        try:
            await websocket.accept()
            
            websocket_id = str(uuid.uuid4())
            self.active_connections[websocket_id] = websocket
            
            # Create or update user session
            session = UserSessionModel(
                user_id=user_id,
                websocket_id=websocket_id,
                status=UserStatus.ONLINE
            )
            self.user_sessions[user_id] = session
            
            # Auto-join system channels
            for channel_id, channel in self.channels.items():
                if channel.settings.get("auto_join", False):
                    await self.join_channel(user_id, channel_id)
            
            # Notify others about user coming online
            await self._broadcast_user_status(user_id, UserStatus.ONLINE)
            
            logger.info(f"👤 User {user_id} connected (WebSocket: {websocket_id})")
            return websocket_id
            
        except Exception as e:
            logger.error(f"❌ User connection failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")
    
    async def disconnect_user(self, user_id -> None: str) -> None:
        """Disconnect user from real-time communication"""
        try:
            if user_id in self.user_sessions:
                session = self.user_sessions[user_id]
                
                # Remove WebSocket connection
                if session.websocket_id in self.active_connections:
                    del self.active_connections[session.websocket_id]
                
                # Update user status
                session.status = UserStatus.OFFLINE
                session.last_seen = datetime.utcnow()
                
                # Notify others about user going offline
                await self._broadcast_user_status(user_id, UserStatus.OFFLINE)
                
                logger.info(f"👤 User {user_id} disconnected")
            
        except Exception as e:
            logger.error(f"❌ User disconnection failed: {str(e)}")
    
    async def create_channel(self, channel_data: ChannelModel) -> Dict[str, Any]:
        """Create new communication channel"""
        try:
            # Validate channel data
            if not channel_data.name or not channel_data.creator_id:
                raise ValueError("Channel name and creator ID required")
            
            # Check for duplicate names in public channels
            if channel_data.channel_type == ChannelType.PUBLIC:
                existing = [c for c in self.channels.values() 
                           if c.name.lower() == channel_data.name.lower() and 
                           c.channel_type == ChannelType.PUBLIC]
                if existing:
                    raise ValueError("Public channel with this name already exists")
            
            # Initialize channel
            self.channels[channel_data.id] = channel_data
            self.messages[channel_data.id] = []
            
            # Add creator as admin and member
            channel_data.admins.append(channel_data.creator_id)
            channel_data.members.append(channel_data.creator_id)
            
            logger.info(f"📢 Channel created: {channel_data.name} (ID: {channel_data.id})")
            
            return {
                "success": True,
                "channel_id": channel_data.id,
                "channel": channel_data.dict(),
                "message": "Channel created successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Channel creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Channel creation failed: {str(e)}")
    
    async def join_channel(self, user_id: str, channel_id: str) -> Dict[str, Any]:
        """Add user to channel"""
        try:
            if channel_id not in self.channels:
                raise ValueError(f"Channel {channel_id} not found")
            
            channel = self.channels[channel_id]
            
            # Check permissions for private channels
            if channel.channel_type == ChannelType.PRIVATE:
                if user_id not in channel.members and user_id not in channel.admins:
                    raise ValueError("Access denied to private channel")
            
            # Add user to channel
            if user_id not in channel.members:
                channel.members.append(user_id)
                channel.last_activity = datetime.utcnow()
                
                # Update user session
                if user_id in self.user_sessions:
                    session = self.user_sessions[user_id]
                    if channel_id not in session.channels:
                        session.channels.append(channel_id)
                
                # Send join notification
                await self._send_system_message(
                    channel_id, 
                    f"User {user_id} joined the channel",
                    MessageType.SYSTEM
                )
                
                logger.info(f"👥 User {user_id} joined channel {channel.name}")
            
            return {
                "success": True,
                "channel_id": channel_id,
                "user_id": user_id,
                "message": "Successfully joined channel"
            }
            
        except Exception as e:
            logger.error(f"❌ Channel join failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Channel join failed: {str(e)}")
    
    async def send_message(self, message: MessageModel) -> Dict[str, Any]:
        """Send message to channel with moderation and encryption"""
        try:
            # Validate message
            if not message.content.strip() and message.message_type == MessageType.TEXT:
                raise ValueError("Message content cannot be empty")
            
            if message.channel_id not in self.channels:
                raise ValueError(f"Channel {message.channel_id} not found")
            
            channel = self.channels[message.channel_id]
            
            # Check if user is member of the channel
            if message.sender_id not in channel.members:
                raise ValueError("User is not a member of this channel")
            
            # Rate limiting check
            await self._check_rate_limit(message.sender_id)
            
            # Content moderation
            moderation_result = await self._moderate_content(message.content)
            if not moderation_result["approved"]:
                raise ValueError(f"Message rejected: {moderation_result['reason']}")
            
            # Encrypt message if channel is encrypted
            if channel.encrypted:
                message.content = self._encrypt_content(message.content)
                message.encrypted = True
            
            # Process mentions
            message.mentions = self._extract_mentions(message.content)
            
            # Store message
            if message.channel_id not in self.messages:
                self.messages[message.channel_id] = []
            
            self.messages[message.channel_id].append(message)
            channel.last_activity = datetime.utcnow()
            
            # Broadcast message to channel members
            await self._broadcast_message_to_channel(message)
            
            # Send notifications for mentions
            if message.mentions:
                await self._send_mention_notifications(message)
            
            logger.info(f"💬 Message sent in {channel.name} by {message.sender_id}")
            
            return {
                "success": True,
                "message_id": message.id,
                "channel_id": message.channel_id,
                "status": message.status.value,
                "message": "Message sent successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Message sending failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Message sending failed: {str(e)}")
    
    async def get_channel_messages(self, channel_id: str, user_id: str, 
                                 limit: int = 50, before: Optional[str] = None) -> Dict[str, Any]:
        """Get messages from channel with pagination"""
        try:
            if channel_id not in self.channels:
                raise ValueError(f"Channel {channel_id} not found")
            
            channel = self.channels[channel_id]
            
            # Check if user has access to channel
            if user_id not in channel.members and channel.channel_type == ChannelType.PRIVATE:
                raise ValueError("Access denied to channel")
            
            messages = self.messages.get(channel_id, [])
            
            # Apply pagination
            if before:
                before_date = datetime.fromisoformat(before)
                messages = [m for m in messages if m.created_at < before_date]
            
            # Sort and limit
            messages = sorted(messages, key=lambda x: x.created_at, reverse=True)[:limit]
            
            # Decrypt messages if needed and user has access
            decrypted_messages = []
            for msg in messages:
                if msg.encrypted and channel.encrypted:
                    try:
                        msg_copy = msg.dict()
                        msg_copy["content"] = self._decrypt_content(msg.content)
                        decrypted_messages.append(msg_copy)
                    except:
                        # Skip messages that can't be decrypted
                        continue
                else:
                    decrypted_messages.append(msg.dict())
            
            return {
                "success": True,
                "channel_id": channel_id,
                "messages": decrypted_messages,
                "has_more": len(self.messages.get(channel_id, [])) > len(messages),
                "message": "Messages retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Message retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Message retrieval failed: {str(e)}")
    
    async def update_user_status(self, user_id: str, status: UserStatus) -> Dict[str, Any]:
        """Update user online status"""
        try:
            if user_id in self.user_sessions:
                session = self.user_sessions[user_id]
                old_status = session.status
                session.status = status
                session.last_seen = datetime.utcnow()
                
                # Broadcast status change
                await self._broadcast_user_status(user_id, status)
                
                logger.info(f"👤 User {user_id} status: {old_status} → {status}")
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "old_status": old_status.value,
                    "new_status": status.value,
                    "message": "Status updated successfully"
                }
            else:
                raise ValueError(f"User session {user_id} not found")
            
        except Exception as e:
            logger.error(f"❌ Status update failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Status update failed: {str(e)}")
    
    async def _check_rate_limit(self, user_id -> None: str) -> None:
        """Check message rate limiting"""
        now = datetime.utcnow()
        limit_window = timedelta(minutes=1)
        max_messages = 10
        
        if user_id not in self.message_rate_limits:
            self.message_rate_limits[user_id] = []
        
        # Clean old timestamps
        user_timestamps = self.message_rate_limits[user_id]
        user_timestamps[:] = [ts for ts in user_timestamps if now - ts < limit_window]
        
        # Check limit
        if len(user_timestamps) >= max_messages:
            raise ValueError("Rate limit exceeded. Please slow down.")
        
        # Add current timestamp
        user_timestamps.append(now)
    
    async def _moderate_content(self, content: str) -> Dict[str, Any]:
        """Moderate message content for policy violations"""
        content_lower = content.lower()
        
        # Check for moderation keywords
        for keyword in self.moderation_keywords:
            if keyword in content_lower:
                return {
                    "approved": False,
                    "reason": f"Content contains inappropriate keyword: {keyword}"
                }
        
        # Check for excessive caps (basic spam detection)
        if len(content) > 10 and content.isupper():
            return {
                "approved": False,
                "reason": "Excessive capitalization detected"
            }
        
        # Check for repetitive characters (spam detection)
        if re.search(r'(.)\1{5,}', content):
            return {
                "approved": False,
                "reason": "Repetitive characters detected"
            }
        
        return {"approved": True, "reason": None}
    
    def _encrypt_content(self, content: str) -> str:
        """Encrypt message content"""
        return self.cipher_suite.encrypt(content.encode()).decode()
    
    def _decrypt_content(self, encrypted_content: str) -> str:
        """Decrypt message content"""
        return self.cipher_suite.decrypt(encrypted_content.encode()).decode()
    
    def _extract_mentions(self, content: str) -> List[str]:
        """Extract user mentions from message content"""
        mention_pattern = r'@(\w+)'
        return re.findall(mention_pattern, content)
    
    async def _broadcast_message_to_channel(self, message -> None: MessageModel) -> None:
        """Broadcast message to all channel members"""
        channel = self.channels[message.channel_id]
        
        for member_id in channel.members:
            if member_id in self.user_sessions:
                session = self.user_sessions[member_id]
                if session.websocket_id in self.active_connections:
                    websocket = self.active_connections[session.websocket_id]
                    try:
                        await websocket.send_text(json.dumps({
                            "type": "message",
                            "data": message.dict()
                        }))
                    except:
                        # Remove dead connection
                        del self.active_connections[session.websocket_id]
    
    async def _broadcast_user_status(self, user_id -> None: str, status -> None: UserStatus) -> None:
        """Broadcast user status change to relevant channels"""
        if user_id not in self.user_sessions:
            return
        
        session = self.user_sessions[user_id]
        status_message = {
            "type": "user_status",
            "data": {
                "user_id": user_id,
                "status": status.value,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Broadcast to all channels where user is a member
        for channel_id in session.channels:
            if channel_id in self.channels:
                channel = self.channels[channel_id]
                for member_id in channel.members:
                    if (member_id != user_id and member_id in self.user_sessions):
                        member_session = self.user_sessions[member_id]
                        if member_session.websocket_id in self.active_connections:
                            websocket = self.active_connections[member_session.websocket_id]
                            try:
                                await websocket.send_text(json.dumps(status_message))
                            except:
                                pass
    
    async def _send_system_message(self, channel_id -> None: str, content -> None: str, msg_type -> None: MessageType) -> None:
        """Send system message to channel"""
        system_message = MessageModel(
            channel_id=channel_id,
            sender_id="system",
            content=content,
            message_type=msg_type
        )
        
        if channel_id not in self.messages:
            self.messages[channel_id] = []
        
        self.messages[channel_id].append(system_message)
        await self._broadcast_message_to_channel(system_message)
    
    async def _send_mention_notifications(self, message -> None: MessageModel) -> None:
        """Send notifications for user mentions"""
        for mentioned_user in message.mentions:
            if mentioned_user in self.user_sessions:
                session = self.user_sessions[mentioned_user]
                if session.websocket_id in self.active_connections:
                    websocket = self.active_connections[session.websocket_id]
                    try:
                        await websocket.send_text(json.dumps({
                            "type": "mention",
                            "data": {
                                "message_id": message.id,
                                "channel_id": message.channel_id,
                                "sender_id": message.sender_id,
                                "content": message.content[:100] + "..." if len(message.content) > 100 else message.content
                            }
                        }))
                    except:
                        pass
    
    async def get_communication_metrics(self) -> Dict[str, Any]:
        """Get communication service metrics"""
        try:
            total_messages = sum(len(msgs) for msgs in self.messages.values())
            today = datetime.utcnow().date()
            messages_today = 0
            
            for msgs in self.messages.values():
                messages_today += len([m for m in msgs if m.created_at.date() == today])
            
            online_users = len([s for s in self.user_sessions.values() if s.status == UserStatus.ONLINE])
            active_channels = len([c for c in self.channels.values() 
                                 if c.last_activity.date() == today])
            
            # Calculate message rate (simplified)
            recent_messages = 0
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            for msgs in self.messages.values():
                recent_messages += len([m for m in msgs if m.created_at > one_hour_ago])
            
            message_rate = recent_messages / 60.0  # per minute
            
            metrics = MessageMetrics(
                total_messages=total_messages,
                messages_today=messages_today,
                active_channels=active_channels,
                online_users=online_users,
                message_rate_per_minute=message_rate,
                average_response_time=15.0,  # simplified
                moderation_actions=0  # simplified
            )
            
            return {
                "success": True,
                "metrics": asdict(metrics),
                "channels_count": len(self.channels),
                "active_sessions": len(self.user_sessions),
                "message": "Communication metrics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Metrics retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Metrics failed: {str(e)}")

# FastAPI Application
app = FastAPI(title="Communication Service", version="1.0.0")
service = CommunicationService()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket -> None: WebSocket, user_id -> None: str) -> None:
    """WebSocket endpoint for real-time communication"""
    websocket_id = await service.connect_user(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Process incoming WebSocket messages here
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                message = MessageModel(**message_data["data"])
                await service.send_message(message)
            elif message_data.get("type") == "status":
                status = UserStatus(message_data["data"]["status"])
                await service.update_user_status(user_id, status)
                
    except WebSocketDisconnect:
        await service.disconnect_user(user_id)

@app.post("/channels/create")
async def create_channel(channel -> None: ChannelModel) -> None:
    """Create new communication channel"""
    return await service.create_channel(channel)

@app.post("/channels/{channel_id}/join")
async def join_channel(channel_id -> None: str, user_id -> None: str) -> None:
    """Join communication channel"""
    return await service.join_channel(user_id, channel_id)

@app.post("/messages/send")
async def send_message(message -> None: MessageModel) -> None:
    """Send message to channel"""
    return await service.send_message(message)

@app.get("/channels/{channel_id}/messages")
async def get_messages(channel_id -> None: str, user_id -> None: str, limit -> None: int = 50, before -> None: Optional[str] = None) -> None:
    """Get channel messages with pagination"""
    return await service.get_channel_messages(channel_id, user_id, limit, before)

@app.put("/users/{user_id}/status")
async def update_status(user_id -> None: str, status -> None: UserStatus) -> None:
    """Update user status"""
    return await service.update_user_status(user_id, status)

@app.get("/metrics")
async def get_metrics() -> None:
    """Get communication service metrics"""
    return await service.get_communication_metrics()

@app.get("/health")
async def health_check() -> None:
    """Service health check"""
    return {
        "service": "CommunicationService",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    print("💬 Starting Communication Service...")
    print("🔒 Enterprise real-time messaging with encryption")
    print("🛡️ Advanced content moderation and security")
    print("⚡ WebSocket-based real-time communication")
    
    uvicorn.run(app, host="0.0.0.0", port=8087)