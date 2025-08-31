"""
Agent Communication Hub

Central communication system for AI agents enabling secure, efficient,
and coordinated inter-agent messaging and collaboration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

  LEGAL WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages between agents"""
    # Task coordination
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    TASK_UPDATE = "task_update"
    TASK_COMPLETION = "task_completion"
    TASK_ERROR = "task_error"
    
    # Data sharing
    DATA_SHARE = "data_share"
    DATA_REQUEST = "data_request"
    DATA_UPDATE = "data_update"
    
    # Coordination
    WORKFLOW_START = "workflow_start"
    WORKFLOW_STEP = "workflow_step"
    WORKFLOW_COMPLETE = "workflow_complete"
    COORDINATION_REQUEST = "coordination_request"
    
    # Notifications
    ALERT = "alert"
    NOTIFICATION = "notification"
    STATUS_UPDATE = "status_update"
    HEARTBEAT = "heartbeat"
    
    # Collaboration
    COLLABORATION_INVITE = "collaboration_invite"
    COLLABORATION_ACCEPT = "collaboration_accept"
    COLLABORATION_REJECT = "collaboration_reject"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_GRANT = "resource_grant"
    
    # System
    SHUTDOWN = "shutdown"
    HEALTH_CHECK = "health_check"
    CAPABILITY_QUERY = "capability_query"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class MessageStatus(Enum):
    """Message delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    PROCESSED = "processed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class AgentMessage:
    """Message between agents"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = ""
    message_type: MessageType = MessageType.NOTIFICATION
    priority: MessagePriority = MessagePriority.NORMAL
    subject: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    reply_to: Optional[str] = None
    conversation_id: Optional[str] = None
    requires_response: bool = False
    delivery_confirmation: bool = False
    encryption_enabled: bool = False
    status: MessageStatus = MessageStatus.PENDING
    delivery_attempts: int = 0
    max_delivery_attempts: int = 3
    
    def __post_init__(self):
        if self.expires_at is None and self.requires_response:
            # Default expiry for messages requiring response
            self.expires_at = self.created_at + timedelta(minutes=30)
    
    @property
    def is_expired(self) -> bool:
        """Check if message has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        data = asdict(self)
        # Convert datetime objects to ISO format
        data["created_at"] = self.created_at.isoformat()
        if self.expires_at:
            data["expires_at"] = self.expires_at.isoformat()
        # Convert enums to values
        data["message_type"] = self.message_type.value
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary"""
        # Convert ISO format back to datetime
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "expires_at" in data and data["expires_at"]:
            data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        
        # Convert values back to enums
        if "message_type" in data:
            data["message_type"] = MessageType(data["message_type"])
        if "priority" in data:
            data["priority"] = MessagePriority(data["priority"])
        if "status" in data:
            data["status"] = MessageStatus(data["status"])
        
        return cls(**data)


@dataclass
class MessageHandler:
    """Handler for specific message types"""
    message_type: MessageType
    handler_func: Callable[[AgentMessage], Any]
    agent_id: str
    is_async: bool = True
    priority: int = 0  # Higher number = higher priority


@dataclass
class Conversation:
    """Conversation thread between agents"""
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    participants: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    subject: str = ""
    messages: List[str] = field(default_factory=list)  # Message IDs
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentCommunicationHub:
    """
    Central communication hub for AI agents
    
    Features:
    - Message routing and delivery
    - Priority-based message queues
    - Conversation threading
    - Message persistence and replay
    - Delivery confirmation and retry
    - Security and encryption
    - Performance monitoring
    """
    
    def __init__(self):
        # Message storage and routing
        self.messages: Dict[str, AgentMessage] = {}
        self.agent_queues: Dict[str, asyncio.Queue] = {}
        self.message_handlers: Dict[str, List[MessageHandler]] = {}
        self.conversations: Dict[str, Conversation] = {}
        
        # Delivery tracking
        self.delivery_tracking: Dict[str, Dict[str, Any]] = {}
        self.failed_deliveries: Dict[str, List[AgentMessage]] = {}
        
        # Security and monitoring
        self.encryption_keys: Dict[str, str] = {}
        self.message_stats: Dict[str, int] = {
            "total_sent": 0,
            "total_delivered": 0,
            "total_failed": 0,
            "total_expired": 0
        }
        
        # Configuration
        self.max_queue_size = 1000
        self.message_retention_hours = 24
        self.cleanup_interval_minutes = 30
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Start background tasks
        self._shutdown_event = asyncio.Event()
        self._background_tasks: List[asyncio.Task] = []
    
    async def initialize(self) -> None:
        """Initialize the communication hub"""



        try:
            # Start background tasks
            self._background_tasks.extend([
                asyncio.create_task(self._message_processor()),
                asyncio.create_task(self._cleanup_expired_messages()),
                asyncio.create_task(self._retry_failed_deliveries()),
                asyncio.create_task(self._update_statistics())
            ])
            
            logger.info("Agent Communication Hub initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize communication hub: {str(e)}")
            raise
    
    async def register_agent(self, agent_id: str) -> None:
        """Register an agent with the communication hub"""
        if agent_id not in self.agent_queues:
            self.agent_queues[agent_id] = asyncio.PriorityQueue(maxsize=self.max_queue_size)
            self.message_handlers[agent_id] = []
            logger.info(f"Agent {agent_id} registered with communication hub")
    
    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the communication hub"""
        if agent_id in self.agent_queues:
            # Clear remaining messages
            queue = self.agent_queues[agent_id]
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            del self.agent_queues[agent_id]
            del self.message_handlers[agent_id]
            logger.info(f"Agent {agent_id} unregistered from communication hub")
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message to an agent"""



        try:
            # Validate message
            if not self._validate_message(message):
                logger.error(f"Invalid message: {message.message_id}")
                return False
            
            # Check if recipient exists
            if message.recipient_id not in self.agent_queues:
                logger.error(f"Recipient agent {message.recipient_id} not registered")
                message.status = MessageStatus.FAILED
                return False
            
            # Store message
            self.messages[message.message_id] = message
            
            # Add to conversation if specified
            if message.conversation_id:
                await self._add_to_conversation(message)
            
            # Encrypt if needed
            if message.encryption_enabled:
                await self._encrypt_message(message)
            
            # Add to recipient's queue with priority
            priority = 10 - message.priority.value  # Lower number = higher priority in PriorityQueue
            queue_item = (priority, message.created_at.timestamp(), message.message_id)
            
            await self.agent_queues[message.recipient_id].put(queue_item)
            
            # Update tracking
            self.delivery_tracking[message.message_id] = {
                "status": MessageStatus.PENDING,
                "sent_at": datetime.utcnow(),
                "attempts": 1
            }
            
            # Update statistics
            self.message_stats["total_sent"] += 1
            
            # Trigger events
            await self._trigger_event("message_sent", {"message": message})
            
            logger.debug(f"Message {message.message_id} queued for {message.recipient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message {message.message_id}: {str(e)}")
            message.status = MessageStatus.FAILED
            return False
    
    async def receive_message(self, agent_id: str, timeout: float = 1.0) -> Optional[AgentMessage]:
        """Receive a message for an agent"""
        if agent_id not in self.agent_queues:
            return None
        
        try:
            queue = self.agent_queues[agent_id]
            priority, timestamp, message_id = await asyncio.wait_for(
                queue.get(), timeout=timeout
            )
            
            message = self.messages.get(message_id)
            if not message:
                logger.error(f"Message {message_id} not found in storage")
                return None
            
            # Check if message expired
            if message.is_expired:
                message.status = MessageStatus.EXPIRED
                self.message_stats["total_expired"] += 1
                logger.warning(f"Message {message_id} expired")
                return None
            
            # Decrypt if needed
            if message.encryption_enabled:
                await self._decrypt_message(message)
            
            # Mark as delivered
            message.status = MessageStatus.DELIVERED
            self.delivery_tracking[message_id]["status"] = MessageStatus.DELIVERED
            self.delivery_tracking[message_id]["delivered_at"] = datetime.utcnow()
            self.message_stats["total_delivered"] += 1
            
            # Send delivery confirmation if requested
            if message.delivery_confirmation:
                await self._send_delivery_confirmation(message)
            
            # Trigger events
            await self._trigger_event("message_delivered", {"message": message})
            
            logger.debug(f"Message {message_id} delivered to {agent_id}")
            return message
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Failed to receive message for {agent_id}: {str(e)}")
            return None
    
    async def register_handler(self, agent_id: str, handler: MessageHandler) -> None:
        """Register a message handler for an agent"""
        if agent_id not in self.message_handlers:
            await self.register_agent(agent_id)
        
        # Insert handler in priority order
        handlers = self.message_handlers[agent_id]
        inserted = False
        
        for i, existing_handler in enumerate(handlers):
            if handler.priority > existing_handler.priority:
                handlers.insert(i, handler)
                inserted = True
                break
        
        if not inserted:
            handlers.append(handler)
        
        logger.debug(f"Handler for {handler.message_type.value} registered for agent {agent_id}")
    
    async def reply_to_message(self, original_message: AgentMessage, reply_content: Dict[str, Any], 
                              message_type: MessageType = MessageType.TASK_RESPONSE) -> bool:
        """Reply to a message"""
        reply = AgentMessage(
            sender_id=original_message.recipient_id,
            recipient_id=original_message.sender_id,
            message_type=message_type,
            subject=f"Re: {original_message.subject}",
            content=reply_content,
            reply_to=original_message.message_id,
            conversation_id=original_message.conversation_id,
            priority=original_message.priority
        )
        
        return await self.send_message(reply)
    
    async def broadcast_message(self, sender_id: str, message_type: MessageType, 
                               content: Dict[str, Any], exclude_agents: List[str] = None) -> List[str]:
        """Broadcast a message to all registered agents"""
        exclude_agents = exclude_agents or []
        exclude_agents.append(sender_id)  # Don't send to sender
        
        successful_sends = []
        
        for agent_id in self.agent_queues.keys():
            if agent_id not in exclude_agents:
                message = AgentMessage(
                    sender_id=sender_id,
                    recipient_id=agent_id,
                    message_type=message_type,
                    subject="Broadcast Message",
                    content=content
                )
                
                if await self.send_message(message):
                    successful_sends.append(agent_id)
        
        return successful_sends
    
    async def create_conversation(self, subject: str, participants: List[str]) -> str:
        """Create a new conversation thread"""
        conversation = Conversation(
            participants=set(participants),
            subject=subject
        )
        
        self.conversations[conversation.conversation_id] = conversation
        
        # Notify participants
        for participant in participants:
            notification = AgentMessage(
                sender_id="system",
                recipient_id=participant,
                message_type=MessageType.NOTIFICATION,
                subject=f"Invited to conversation: {subject}",
                content={
                    "conversation_id": conversation.conversation_id,
                    "participants": list(participants),
                    "subject": subject
                },
                conversation_id=conversation.conversation_id
            )
            await self.send_message(notification)
        
        logger.info(f"Conversation {conversation.conversation_id} created with {len(participants)} participants")
        return conversation.conversation_id
    
    async def get_conversation_history(self, conversation_id: str) -> List[AgentMessage]:
        """Get message history for a conversation"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return []
        
        messages = []
        for message_id in conversation.messages:
            message = self.messages.get(message_id)
            if message:
                messages.append(message)
        
        # Sort by creation time
        messages.sort(key=lambda m: m.created_at)
        return messages
    
    async def get_agent_statistics(self, agent_id: str) -> Dict[str, Any]:
        """Get communication statistics for an agent"""
        sent_count = len([m for m in self.messages.values() if m.sender_id == agent_id])
        received_count = len([m for m in self.messages.values() if m.recipient_id == agent_id])
        
        return {
            "agent_id": agent_id,
            "messages_sent": sent_count,
            "messages_received": received_count,
            "queue_size": self.agent_queues[agent_id].qsize() if agent_id in self.agent_queues else 0,
            "active_conversations": len([
                c for c in self.conversations.values() 
                if agent_id in c.participants and c.is_active
            ])
        }
    
    async def shutdown(self) -> None:
        """Shutdown the communication hub"""
        logger.info("Shutting down Agent Communication Hub")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # Clear all data
        self.messages.clear()
        self.agent_queues.clear()
        self.conversations.clear()
        self.delivery_tracking.clear()
        
        logger.info("Agent Communication Hub shutdown complete")
    
    # Background task methods
    async def _message_processor(self) -> None:
        """Background task to process messages"""
        while not self._shutdown_event.is_set():
            try:
                # Process message handlers for each agent
                for agent_id in list(self.agent_queues.keys()):
                    await self._process_agent_handlers(agent_id)
                
            except Exception as e:
                logger.error(f"Error in message processor: {str(e)}")
            
            await asyncio.sleep(0.1)  # Process every 100ms
    
    async def _process_agent_handlers(self, agent_id: str) -> None:
        """Process message handlers for a specific agent"""



        try:
            # Get message without blocking
            message = await self.receive_message(agent_id, timeout=0.01)
            if not message:
                return
            
            # Find appropriate handler
            handlers = self.message_handlers.get(agent_id, [])
            for handler in handlers:
                if handler.message_type == message.message_type:
                    try:
                        if handler.is_async:
                            await handler.handler_func(message)
                        else:
                            handler.handler_func(message)
                        
                        message.status = MessageStatus.PROCESSED
                        break
                        
                    except Exception as e:
                        logger.error(f"Handler error for message {message.message_id}: {str(e)}")
                        message.status = MessageStatus.FAILED
            
        except Exception as e:
            logger.error(f"Error processing handlers for {agent_id}: {str(e)}")
    
    # Additional helper methods would be implemented here for:
    # - Message cleanup and retention
    # - Failed delivery retry logic
    # - Statistics updates
    # - Event system
    # - Encryption/decryption
    # - Message validation
