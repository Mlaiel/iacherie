"""
WebSocket API Gateway - Real-time Communication Hub
© 2025 Fahed Mlaiel. All rights reserved.

WebSocket Gateway providing real-time communication, connection management,
authentication, and broadcasting for live creator platform features.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from dataclasses import dataclass, field
import weakref
import time
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """WebSocket connection states"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class MessageType(Enum):
    """WebSocket message types"""
    CONNECTION_INIT = "connection_init"
    CONNECTION_ACK = "connection_ack"
    CONNECTION_ERROR = "connection_error"
    AUTHENTICATION = "authentication"
    SUBSCRIPTION_START = "subscription_start"
    SUBSCRIPTION_DATA = "subscription_data"
    SUBSCRIPTION_ERROR = "subscription_error"
    SUBSCRIPTION_COMPLETE = "subscription_complete"
    KEEPALIVE = "keepalive"
    BROADCAST = "broadcast"
    DIRECT_MESSAGE = "direct_message"
    SYSTEM_MESSAGE = "system_message"


class ChannelType(Enum):
    """Broadcasting channel types"""
    CREATOR_UPDATES = "creator_updates"
    LIVE_STREAM = "live_stream"
    ANALYTICS_REAL_TIME = "analytics_real_time"
    COLLABORATION = "collaboration"
    NOTIFICATIONS = "notifications"
    PLATFORM_SYNC = "platform_sync"
    AI_PROCESSING = "ai_processing"
    REVENUE_UPDATES = "revenue_updates"
    AUDIENCE_ENGAGEMENT = "audience_engagement"
    CONTENT_MODERATION = "content_moderation"


@dataclass
class WebSocketConnection:
    """WebSocket connection representation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    state: ConnectionState = ConnectionState.CONNECTING
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    authenticated_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    subscriptions: Set[str] = field(default_factory=set)
    channels: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Connection statistics
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0


@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.DIRECT_MESSAGE
    payload: Dict[str, Any] = field(default_factory=dict)
    connection_id: str = ""
    user_id: Optional[str] = None
    channel: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class Channel:
    """Broadcasting channel"""
    name: str
    type: ChannelType
    description: str = ""
    max_connections: int = 10000
    require_auth: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    connection_count: int = 0
    message_count: int = 0
    last_activity: Optional[datetime] = None


@dataclass
class Subscription:
    """Real-time subscription"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    connection_id: str = ""
    query: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_event_at: Optional[datetime] = None
    is_active: bool = True


class WebSocketAPIManager:
    """
    Enterprise WebSocket API Gateway Manager
    
    Provides comprehensive real-time communication, connection management,
    authentication, broadcasting, and subscription management for creator platform.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize WebSocket API Manager"""
        self.config = config or {}
        self.connections: Dict[str, WebSocketConnection] = {}
        self.channels: Dict[str, Channel] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)
        self.channel_connections: Dict[str, Set[str]] = defaultdict(set)
        self.message_queue: Dict[str, List[WebSocketMessage]] = defaultdict(list)
        self.connection_handlers: Dict[str, Callable] = {}
        self.metrics: Dict[str, Any] = {}
        
        # Configuration
        self.max_connections = self.config.get('max_connections', 10000)
        self.max_connections_per_user = self.config.get('max_connections_per_user', 10)
        self.heartbeat_interval = self.config.get('heartbeat_interval', 30)
        self.connection_timeout = self.config.get('connection_timeout', 300)
        self.authentication_timeout = self.config.get('authentication_timeout', 30)
        self.message_buffer_size = self.config.get('message_buffer_size', 1000)
        
        # Setup default channels
        self._setup_default_channels()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("WebSocket API Manager initialized")
    
    def _setup_default_channels(self):
        """Setup default broadcasting channels for creator platform"""
        default_channels = [
            Channel(
                name="creator_updates",
                type=ChannelType.CREATOR_UPDATES,
                description="Real-time creator profile and content updates",
                max_connections=5000,
                require_auth=True
            ),
            Channel(
                name="live_streams",
                type=ChannelType.LIVE_STREAM,
                description="Live streaming events and interactions",
                max_connections=10000,
                require_auth=False
            ),
            Channel(
                name="analytics_live",
                type=ChannelType.ANALYTICS_REAL_TIME,
                description="Real-time analytics and performance metrics",
                max_connections=1000,
                require_auth=True
            ),
            Channel(
                name="collaborations",
                type=ChannelType.COLLABORATION,
                description="Creator collaboration and project updates",
                max_connections=2000,
                require_auth=True
            ),
            Channel(
                name="notifications",
                type=ChannelType.NOTIFICATIONS,
                description="User notifications and alerts",
                max_connections=5000,
                require_auth=True
            ),
            Channel(
                name="platform_sync",
                type=ChannelType.PLATFORM_SYNC,
                description="Platform integration and sync updates",
                max_connections=3000,
                require_auth=True
            ),
            Channel(
                name="ai_processing",
                type=ChannelType.AI_PROCESSING,
                description="AI processing status and results",
                max_connections=2000,
                require_auth=True
            ),
            Channel(
                name="revenue_updates",
                type=ChannelType.REVENUE_UPDATES,
                description="Real-time revenue and monetization updates",
                max_connections=1000,
                require_auth=True
            ),
            Channel(
                name="audience_engagement",
                type=ChannelType.AUDIENCE_ENGAGEMENT,
                description="Live audience engagement and interactions",
                max_connections=8000,
                require_auth=False
            ),
            Channel(
                name="content_moderation",
                type=ChannelType.CONTENT_MODERATION,
                description="Content moderation and compliance alerts",
                max_connections=500,
                require_auth=True
            )
        ]
        
        for channel in default_channels:
            self.channels[channel.name] = channel
        
        logger.info(f"Setup {len(default_channels)} default channels")
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        asyncio.create_task(self._heartbeat_monitor())
        asyncio.create_task(self._connection_cleanup())
        asyncio.create_task(self._message_processor())
        asyncio.create_task(self._metrics_collector())
    
    async def create_connection(self, connection_data: Dict[str, Any]) -> WebSocketConnection:
        """Create new WebSocket connection"""
        try:
            # Check connection limits
            if len(self.connections) >= self.max_connections:
                raise Exception("Maximum connections exceeded")
            
            # Create connection
            connection = WebSocketConnection(
                ip_address=connection_data.get('ip_address'),
                user_agent=connection_data.get('user_agent'),
                metadata=connection_data.get('metadata', {})
            )
            
            # Store connection
            self.connections[connection.id] = connection
            
            # Update metrics
            await self._update_connection_metrics('created')
            
            logger.info(f"WebSocket connection created: {connection.id}")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
            raise
    
    async def authenticate_connection(self, connection_id: str, auth_data: Dict[str, Any]) -> bool:
        """Authenticate WebSocket connection"""
        try:
            if connection_id not in self.connections:
                logger.error(f"Connection not found: {connection_id}")
                return False
            
            connection = self.connections[connection_id]
            
            # Validate authentication
            if not await self._validate_authentication(auth_data):
                logger.error(f"Authentication failed for connection: {connection_id}")
                return False
            
            # Extract user information
            user_id = auth_data.get('user_id')
            session_id = auth_data.get('session_id')
            
            # Check user connection limits
            if user_id and len(self.user_connections[user_id]) >= self.max_connections_per_user:
                logger.error(f"User connection limit exceeded: {user_id}")
                return False
            
            # Update connection
            connection.user_id = user_id
            connection.session_id = session_id
            connection.state = ConnectionState.AUTHENTICATED
            connection.authenticated_at = datetime.utcnow()
            
            # Track user connections
            if user_id:
                self.user_connections[user_id].add(connection_id)
            
            # Send authentication acknowledgment
            await self._send_auth_ack(connection)
            
            logger.info(f"Connection authenticated: {connection_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Authentication error for connection {connection_id}: {e}")
            return False
    
    async def close_connection(self, connection_id: str, reason: str = "closed") -> bool:
        """Close WebSocket connection"""
        try:
            if connection_id not in self.connections:
                return False
            
            connection = self.connections[connection_id]
            
            # Update connection state
            connection.state = ConnectionState.DISCONNECTING
            
            # Remove from channels
            for channel_name in connection.channels.copy():
                await self.leave_channel(connection_id, channel_name)
            
            # Remove subscriptions
            for subscription_id in connection.subscriptions.copy():
                await self.remove_subscription(subscription_id)
            
            # Remove from user tracking
            if connection.user_id:
                self.user_connections[connection.user_id].discard(connection_id)
            
            # Update state and remove
            connection.state = ConnectionState.DISCONNECTED
            del self.connections[connection_id]
            
            # Update metrics
            await self._update_connection_metrics('closed')
            
            logger.info(f"Connection closed: {connection_id}, reason: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing connection {connection_id}: {e}")
            return False
    
    async def join_channel(self, connection_id: str, channel_name: str) -> bool:
        """Join connection to broadcasting channel"""
        try:
            if connection_id not in self.connections:
                logger.error(f"Connection not found: {connection_id}")
                return False
            
            if channel_name not in self.channels:
                logger.error(f"Channel not found: {channel_name}")
                return False
            
            connection = self.connections[connection_id]
            channel = self.channels[channel_name]
            
            # Check authentication requirement
            if channel.require_auth and connection.state != ConnectionState.AUTHENTICATED:
                logger.error(f"Authentication required for channel: {channel_name}")
                return False
            
            # Check channel capacity
            if len(self.channel_connections[channel_name]) >= channel.max_connections:
                logger.error(f"Channel capacity exceeded: {channel_name}")
                return False
            
            # Join channel
            connection.channels.add(channel_name)
            self.channel_connections[channel_name].add(connection_id)
            channel.connection_count = len(self.channel_connections[channel_name])
            channel.last_activity = datetime.utcnow()
            
            logger.info(f"Connection {connection_id} joined channel {channel_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error joining channel {channel_name}: {e}")
            return False
    
    async def leave_channel(self, connection_id: str, channel_name: str) -> bool:
        """Remove connection from broadcasting channel"""
        try:
            if connection_id not in self.connections:
                return False
            
            connection = self.connections[connection_id]
            
            # Remove from channel
            connection.channels.discard(channel_name)
            self.channel_connections[channel_name].discard(connection_id)
            
            # Update channel stats
            if channel_name in self.channels:
                self.channels[channel_name].connection_count = len(self.channel_connections[channel_name])
            
            logger.info(f"Connection {connection_id} left channel {channel_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error leaving channel {channel_name}: {e}")
            return False
    
    async def send_message(self, connection_id: str, message: WebSocketMessage) -> bool:
        """Send message to specific connection"""
        try:
            if connection_id not in self.connections:
                logger.error(f"Connection not found: {connection_id}")
                return False
            
            connection = self.connections[connection_id]
            
            # Update connection activity
            connection.last_activity = datetime.utcnow()
            connection.messages_sent += 1
            
            # Add to message queue for processing
            self.message_queue[connection_id].append(message)
            
            # Process immediately if queue is not too large
            if len(self.message_queue[connection_id]) < 10:
                await self._process_message_queue(connection_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            return False
    
    async def broadcast_to_channel(self, channel_name: str, message: WebSocketMessage) -> int:
        """Broadcast message to all connections in channel"""
        try:
            if channel_name not in self.channels:
                logger.error(f"Channel not found: {channel_name}")
                return 0
            
            channel = self.channels[channel_name]
            connections = self.channel_connections[channel_name].copy()
            
            # Send to all connections in channel
            successful_sends = 0
            for connection_id in connections:
                message_copy = WebSocketMessage(
                    type=MessageType.BROADCAST,
                    payload=message.payload,
                    connection_id=connection_id,
                    channel=channel_name,
                    timestamp=datetime.utcnow()
                )
                
                if await self.send_message(connection_id, message_copy):
                    successful_sends += 1
            
            # Update channel stats
            channel.message_count += 1
            channel.last_activity = datetime.utcnow()
            
            logger.info(f"Broadcast to channel {channel_name}: {successful_sends}/{len(connections)} successful")
            return successful_sends
            
        except Exception as e:
            logger.error(f"Error broadcasting to channel {channel_name}: {e}")
            return 0
    
    async def broadcast_to_user(self, user_id: str, message: WebSocketMessage) -> int:
        """Broadcast message to all user connections"""
        try:
            connections = self.user_connections[user_id].copy()
            
            successful_sends = 0
            for connection_id in connections:
                message_copy = WebSocketMessage(
                    type=MessageType.DIRECT_MESSAGE,
                    payload=message.payload,
                    connection_id=connection_id,
                    user_id=user_id,
                    timestamp=datetime.utcnow()
                )
                
                if await self.send_message(connection_id, message_copy):
                    successful_sends += 1
            
            logger.info(f"Broadcast to user {user_id}: {successful_sends}/{len(connections)} successful")
            return successful_sends
            
        except Exception as e:
            logger.error(f"Error broadcasting to user {user_id}: {e}")
            return 0
    
    async def create_subscription(self, connection_id: str, subscription_data: Dict[str, Any]) -> Optional[str]:
        """Create real-time subscription"""
        try:
            if connection_id not in self.connections:
                logger.error(f"Connection not found: {connection_id}")
                return None
            
            connection = self.connections[connection_id]
            
            # Create subscription
            subscription = Subscription(
                connection_id=connection_id,
                query=subscription_data.get('query', ''),
                variables=subscription_data.get('variables', {})
            )
            
            # Store subscription
            self.subscriptions[subscription.id] = subscription
            connection.subscriptions.add(subscription.id)
            
            # Setup subscription handler
            await self._setup_subscription_handler(subscription)
            
            logger.info(f"Subscription created: {subscription.id} for connection {connection_id}")
            return subscription.id
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return None
    
    async def remove_subscription(self, subscription_id: str) -> bool:
        """Remove subscription"""
        try:
            if subscription_id not in self.subscriptions:
                return False
            
            subscription = self.subscriptions[subscription_id]
            connection_id = subscription.connection_id
            
            # Remove from connection
            if connection_id in self.connections:
                self.connections[connection_id].subscriptions.discard(subscription_id)
            
            # Remove subscription
            subscription.is_active = False
            del self.subscriptions[subscription_id]
            
            logger.info(f"Subscription removed: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing subscription {subscription_id}: {e}")
            return False
    
    async def get_connection_metrics(self) -> Dict[str, Any]:
        """Get comprehensive connection metrics"""
        active_connections = len([c for c in self.connections.values() if c.state == ConnectionState.CONNECTED or c.state == ConnectionState.AUTHENTICATED])
        authenticated_connections = len([c for c in self.connections.values() if c.state == ConnectionState.AUTHENTICATED])
        
        return {
            'total_connections': len(self.connections),
            'active_connections': active_connections,
            'authenticated_connections': authenticated_connections,
            'channels': len(self.channels),
            'active_subscriptions': len([s for s in self.subscriptions.values() if s.is_active]),
            'total_users': len(self.user_connections),
            'channel_stats': {
                name: {
                    'connection_count': channel.connection_count,
                    'message_count': channel.message_count,
                    'last_activity': channel.last_activity.isoformat() if channel.last_activity else None
                }
                for name, channel in self.channels.items()
            },
            'message_queue_size': sum(len(queue) for queue in self.message_queue.values()),
            'uptime': datetime.utcnow().isoformat()
        }
    
    # Internal Implementation Methods
    
    async def _validate_authentication(self, auth_data: Dict[str, Any]) -> bool:
        """Validate authentication data"""
        # Implementation would verify JWT token or API key
        # For now, simple validation
        return 'user_id' in auth_data and 'session_id' in auth_data
    
    async def _send_auth_ack(self, connection: WebSocketConnection):
        """Send authentication acknowledgment"""
        message = WebSocketMessage(
            type=MessageType.CONNECTION_ACK,
            payload={
                'authenticated': True,
                'user_id': connection.user_id,
                'session_id': connection.session_id,
                'timestamp': datetime.utcnow().isoformat()
            },
            connection_id=connection.id
        )
        
        await self.send_message(connection.id, message)
    
    async def _setup_subscription_handler(self, subscription: Subscription):
        """Setup subscription event handler"""
        # Implementation would setup real-time data source listener
        logger.info(f"Subscription handler setup for {subscription.id}")
    
    async def _process_message_queue(self, connection_id: str):
        """Process pending messages for connection"""
        try:
            if connection_id not in self.message_queue:
                return
            
            queue = self.message_queue[connection_id]
            if not queue:
                return
            
            # Process messages (would send to actual WebSocket)
            processed_count = 0
            while queue and processed_count < 10:  # Process up to 10 messages at once
                message = queue.pop(0)
                
                # Simulate message sending
                logger.debug(f"Processing message {message.id} for connection {connection_id}")
                processed_count += 1
            
            # Update connection stats
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                connection.bytes_sent += processed_count * 100  # Estimated bytes
            
        except Exception as e:
            logger.error(f"Error processing message queue for {connection_id}: {e}")
    
    async def _heartbeat_monitor(self):
        """Monitor connection heartbeats"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                current_time = datetime.utcnow()
                timeout_threshold = current_time - timedelta(seconds=self.connection_timeout)
                
                # Check for inactive connections
                inactive_connections = []
                for connection_id, connection in self.connections.items():
                    if connection.last_activity < timeout_threshold:
                        inactive_connections.append(connection_id)
                
                # Close inactive connections
                for connection_id in inactive_connections:
                    await self.close_connection(connection_id, "timeout")
                
                # Send keepalive to active connections
                keepalive_message = WebSocketMessage(
                    type=MessageType.KEEPALIVE,
                    payload={'timestamp': current_time.isoformat()}
                )
                
                for connection_id, connection in self.connections.items():
                    if connection.state == ConnectionState.AUTHENTICATED:
                        await self.send_message(connection_id, keepalive_message)
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
    
    async def _connection_cleanup(self):
        """Cleanup disconnected connections and expired data"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                # Clean up message queues
                for connection_id in list(self.message_queue.keys()):
                    if connection_id not in self.connections:
                        del self.message_queue[connection_id]
                
                # Clean up expired subscriptions
                current_time = datetime.utcnow()
                expired_subscriptions = []
                
                for subscription_id, subscription in self.subscriptions.items():
                    if not subscription.is_active:
                        expired_subscriptions.append(subscription_id)
                    elif subscription.connection_id not in self.connections:
                        expired_subscriptions.append(subscription_id)
                
                for subscription_id in expired_subscriptions:
                    await self.remove_subscription(subscription_id)
                
            except Exception as e:
                logger.error(f"Error in connection cleanup: {e}")
    
    async def _message_processor(self):
        """Process queued messages"""
        while True:
            try:
                await asyncio.sleep(1)  # Process every second
                
                # Process message queues for all connections
                for connection_id in list(self.message_queue.keys()):
                    if self.message_queue[connection_id]:
                        await self._process_message_queue(connection_id)
                
            except Exception as e:
                logger.error(f"Error in message processor: {e}")
    
    async def _metrics_collector(self):
        """Collect and update metrics"""
        while True:
            try:
                await asyncio.sleep(30)  # Collect every 30 seconds
                
                metrics = await self.get_connection_metrics()
                self.metrics[datetime.utcnow().isoformat()] = metrics
                
                # Keep only last 24 hours of metrics
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.metrics = {
                    timestamp: data
                    for timestamp, data in self.metrics.items()
                    if datetime.fromisoformat(timestamp) > cutoff_time
                }
                
            except Exception as e:
                logger.error(f"Error in metrics collector: {e}")
    
    async def _update_connection_metrics(self, action: str):
        """Update connection metrics"""
        # Implementation would update Prometheus/monitoring metrics
        logger.debug(f"Connection metric updated: {action}")


# WebSocket API Manager Factory
def create_websocket_api_manager(config: Optional[Dict[str, Any]] = None) -> WebSocketAPIManager:
    """Factory function to create WebSocket API Manager instance"""
    return WebSocketAPIManager(config)


# Creator Platform WebSocket Events
CREATOR_PLATFORM_EVENTS = {
    'content_upload_progress': {
        'channel': 'creator_updates',
        'description': 'Real-time content upload progress',
        'payload_schema': {
            'upload_id': 'string',
            'progress': 'number',
            'status': 'string',
            'eta': 'string'
        }
    },
    'live_analytics_update': {
        'channel': 'analytics_live',
        'description': 'Live analytics data updates',
        'payload_schema': {
            'creator_id': 'string',
            'views': 'number',
            'likes': 'number',
            'shares': 'number',
            'engagement_rate': 'number'
        }
    },
    'collaboration_invite': {
        'channel': 'collaborations',
        'description': 'Collaboration invitation',
        'payload_schema': {
            'invite_id': 'string',
            'from_creator': 'string',
            'to_creator': 'string',
            'project_title': 'string'
        }
    },
    'ai_processing_complete': {
        'channel': 'ai_processing',
        'description': 'AI processing completion notification',
        'payload_schema': {
            'job_id': 'string',
            'service': 'string',
            'result_url': 'string',
            'processing_time': 'number'
        }
    },
    'revenue_milestone': {
        'channel': 'revenue_updates',
        'description': 'Revenue milestone reached',
        'payload_schema': {
            'creator_id': 'string',
            'milestone': 'number',
            'total_earnings': 'number',
            'achievement_date': 'string'
        }
    }
}


if __name__ == "__main__":
    # Example usage
    async def main():
        manager = create_websocket_api_manager({
            'max_connections': 5000,
            'heartbeat_interval': 30,
            'connection_timeout': 300
        })
        
        # Example connection flow
        connection_data = {
            'ip_address': '192.168.1.100',
            'user_agent': 'Creator Platform Client/1.0'
        }
        
        connection = await manager.create_connection(connection_data)
        print(f"Connection created: {connection.id}")
        
        # Authenticate connection
        auth_data = {
            'user_id': 'creator_123',
            'session_id': 'session_456'
        }
        
        auth_success = await manager.authenticate_connection(connection.id, auth_data)
        print(f"Authentication: {auth_success}")
        
        # Join channel
        await manager.join_channel(connection.id, "creator_updates")
        
        # Send message
        message = WebSocketMessage(
            type=MessageType.DIRECT_MESSAGE,
            payload={'message': 'Hello from WebSocket API!'}
        )
        
        await manager.send_message(connection.id, message)
        
        # Get metrics
        metrics = await manager.get_connection_metrics()
        print(f"Metrics: {metrics}")
        
        # Simulate some time passing
        await asyncio.sleep(2)
        
        # Close connection
        await manager.close_connection(connection.id, "example_complete")
    
    asyncio.run(main())