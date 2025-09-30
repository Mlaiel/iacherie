"""MongoDB Realtime Updater
=========================

Real-time UI updates and notifications system for MongoDB synchronization
in the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import threading
from queue import Queue
import time

try:
    import websockets
    import aiohttp
    from aiohttp import web
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

from . import SyncEvent

logger = logging.getLogger(__name__)

class UpdateType(Enum):
    """Real-time update types."""
    DOCUMENT_CREATED = "document_created"
    DOCUMENT_UPDATED = "document_updated"
    DOCUMENT_DELETED = "document_deleted"
    SYNC_STATUS_CHANGED = "sync_status_changed"
    CONFLICT_DETECTED = "conflict_detected"
    BATCH_COMPLETED = "batch_completed"
    ERROR_OCCURRED = "error_occurred"
    HEALTH_UPDATE = "health_update"

class ChannelType(Enum):
    """Update channel types."""
    USER_SPECIFIC = "user_specific"
    COLLECTION_SPECIFIC = "collection_specific"
    GLOBAL = "global"
    ADMIN_ONLY = "admin_only"

@dataclass
class RealtimeUpdate:
    """Real-time update message."""
    update_id: str
    update_type: UpdateType
    channel: str
    payload: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    collection: Optional[str] = None
    priority: int = 1  # 1=low, 5=high

@dataclass
class ClientConnection:
    """WebSocket client connection."""
    connection_id: str
    websocket: Any
    user_id: Optional[str]
    subscribed_channels: Set[str]
    connected_at: datetime
    last_ping: datetime
    is_admin: bool = False

class RealtimeUpdater:
    """Enterprise-grade real-time updates and notifications system."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        """Initialize realtime updater."""
        if not WEB_AVAILABLE:
            logger.warning("websockets/aiohttp not available - realtime functionality limited")
        
        self.host = host
        self.port = port
        self.server = None
        
        # Client connections
        self.connections: Dict[str, ClientConnection] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        
        # Update channels and subscriptions
        self.channels: Dict[str, Set[str]] = {}  # channel -> connection_ids
        self.update_queue = Queue(maxsize=10000)
        
        # Processing threads
        self.update_processor_thread = None
        self.ping_thread = None
        self.running = False
        self.shutdown_event = threading.Event()
        
        # Configuration
        self.ping_interval = 30  # seconds
        self.connection_timeout = 60  # seconds
        self.max_connections = 1000
        self.rate_limit_per_second = 100
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'updates_sent': 0,
            'updates_failed': 0,
            'channels_created': 0
        }
    
    async def start_server(self):
        """Start the WebSocket server."""
        if not WEB_AVAILABLE:
            raise ImportError("websockets required for realtime updates")
        
        if self.running:
            logger.warning("Realtime updater already running")
            return
        
        self.running = True
        
        # Start WebSocket server
        self.server = await websockets.serve(
            self._handle_connection,
            self.host,
            self.port,
            ping_interval=self.ping_interval,
            ping_timeout=self.connection_timeout
        )
        
        # Start background threads
        self.update_processor_thread = threading.Thread(
            target=self._update_processor_loop,
            daemon=True
        )
        self.update_processor_thread.start()
        
        self.ping_thread = threading.Thread(
            target=self._ping_loop,
            daemon=True
        )
        self.ping_thread.start()
        
        logger.info(f"Realtime updater started on {self.host}:{self.port}")
    
    async def _handle_connection(self, websocket, path):
        """Handle new WebSocket connection."""
        connection_id = self._generate_connection_id()
        
        try:
            # Create client connection
            connection = ClientConnection(
                connection_id=connection_id,
                websocket=websocket,
                user_id=None,
                subscribed_channels=set(),
                connected_at=datetime.now(),
                last_ping=datetime.now()
            )
            
            # Store connection
            self.connections[connection_id] = connection
            self.stats['total_connections'] += 1
            self.stats['active_connections'] += 1
            
            logger.info(f"New WebSocket connection: {connection_id}")
            
            # Send welcome message
            await self._send_to_connection(connection_id, {
                'type': 'welcome',
                'connection_id': connection_id,
                'server_time': datetime.now().isoformat()
            })
            
            # Handle messages
            async for message in websocket:
                await self._handle_message(connection_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed: {connection_id}")
        except Exception as e:
            logger.error(f"Error handling WebSocket connection {connection_id}: {e}")
        finally:
            # Clean up connection
            await self._cleanup_connection(connection_id)
    
    async def _handle_message(self, connection_id: str, message: str):
        """Handle message from WebSocket client."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'authenticate':
                await self._handle_authentication(connection_id, data)
            elif message_type == 'subscribe':
                await self._handle_subscription(connection_id, data)
            elif message_type == 'unsubscribe':
                await self._handle_unsubscription(connection_id, data)
            elif message_type == 'ping':
                await self._handle_ping(connection_id)
            else:
                logger.warning(f"Unknown message type from {connection_id}: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from {connection_id}")
        except Exception as e:
            logger.error(f"Error handling message from {connection_id}: {e}")
    
    async def _handle_authentication(self, connection_id: str, data: Dict[str, Any]):
        """Handle client authentication."""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        # Extract authentication data
        user_id = data.get('user_id')
        token = data.get('token')
        is_admin = data.get('is_admin', False)
        
        # Validate authentication (simplified - in production, verify token)
        if user_id and token:
            connection.user_id = user_id
            connection.is_admin = is_admin
            
            # Track user connections
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
            
            # Auto-subscribe to user-specific channel
            user_channel = f"user:{user_id}"
            await self._subscribe_to_channel(connection_id, user_channel)
            
            # Send authentication success
            await self._send_to_connection(connection_id, {
                'type': 'auth_success',
                'user_id': user_id,
                'channels': list(connection.subscribed_channels)
            })
            
            logger.info(f"Client authenticated: {connection_id} (user: {user_id})")
        else:
            await self._send_to_connection(connection_id, {
                'type': 'auth_error',
                'message': 'Invalid authentication data'
            })
    
    async def _handle_subscription(self, connection_id: str, data: Dict[str, Any]):
        """Handle channel subscription."""
        channel = data.get('channel')
        
        if channel and self._is_valid_channel(connection_id, channel):
            await self._subscribe_to_channel(connection_id, channel)
            
            await self._send_to_connection(connection_id, {
                'type': 'subscribed',
                'channel': channel
            })
        else:
            await self._send_to_connection(connection_id, {
                'type': 'subscription_error',
                'message': 'Invalid or unauthorized channel'
            })
    
    async def _handle_unsubscription(self, connection_id: str, data: Dict[str, Any]):
        """Handle channel unsubscription."""
        channel = data.get('channel')
        
        if channel:
            await self._unsubscribe_from_channel(connection_id, channel)
            
            await self._send_to_connection(connection_id, {
                'type': 'unsubscribed',
                'channel': channel
            })
    
    async def _handle_ping(self, connection_id: str):
        """Handle ping message."""
        if connection_id in self.connections:
            self.connections[connection_id].last_ping = datetime.now()
            
            await self._send_to_connection(connection_id, {
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    def _is_valid_channel(self, connection_id: str, channel: str) -> bool:
        """Check if connection can subscribe to channel."""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        
        # Admin channels require admin access
        if channel.startswith('admin:') and not connection.is_admin:
            return False
        
        # User-specific channels require matching user ID
        if channel.startswith('user:'):
            required_user_id = channel.split(':', 1)[1]
            if connection.user_id != required_user_id and not connection.is_admin:
                return False
        
        return True
    
    async def _subscribe_to_channel(self, connection_id: str, channel: str):
        """Subscribe connection to a channel."""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        connection.subscribed_channels.add(channel)
        
        # Add to channel subscribers
        if channel not in self.channels:
            self.channels[channel] = set()
            self.stats['channels_created'] += 1
        
        self.channels[channel].add(connection_id)
        logger.debug(f"Connection {connection_id} subscribed to {channel}")
    
    async def _unsubscribe_from_channel(self, connection_id: str, channel: str):
        """Unsubscribe connection from a channel."""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        connection.subscribed_channels.discard(channel)
        
        # Remove from channel subscribers
        if channel in self.channels:
            self.channels[channel].discard(connection_id)
            
            # Clean up empty channels
            if not self.channels[channel]:
                del self.channels[channel]
        
        logger.debug(f"Connection {connection_id} unsubscribed from {channel}")
    
    async def _cleanup_connection(self, connection_id: str):
        """Clean up disconnected connection."""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        # Remove from user connections
        if connection.user_id and connection.user_id in self.user_connections:
            self.user_connections[connection.user_id].discard(connection_id)
            if not self.user_connections[connection.user_id]:
                del self.user_connections[connection.user_id]
        
        # Remove from all channels
        for channel in list(connection.subscribed_channels):
            await self._unsubscribe_from_channel(connection_id, channel)
        
        # Remove connection
        del self.connections[connection_id]
        self.stats['active_connections'] -= 1
        
        logger.info(f"Cleaned up connection: {connection_id}")
    
    def _generate_connection_id(self) -> str:
        """Generate unique connection ID."""
        timestamp = int(time.time() * 1000000)
        return f"conn_{timestamp}"
    
    async def _send_to_connection(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific connection."""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        
        try:
            await connection.websocket.send(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {e}")
            # Mark connection for cleanup
            asyncio.create_task(self._cleanup_connection(connection_id))
            return False
    
    def queue_update(self, update: RealtimeUpdate):
        """Queue an update for processing."""
        try:
            self.update_queue.put(update, timeout=1)
        except:
            logger.warning("Update queue full, dropping update")
    
    def send_sync_event_update(self, sync_event: SyncEvent):
        """Send real-time update for sync event."""
        # Determine update type
        update_type_map = {
            'insert': UpdateType.DOCUMENT_CREATED,
            'update': UpdateType.DOCUMENT_UPDATED,
            'delete': UpdateType.DOCUMENT_DELETED
        }
        
        update_type = update_type_map.get(sync_event.operation_type, UpdateType.DOCUMENT_UPDATED)
        
        # Create update
        update = RealtimeUpdate(
            update_id=self._generate_update_id(),
            update_type=update_type,
            channel=f"collection:{sync_event.collection}",
            payload={
                'sync_id': sync_event.sync_id,
                'operation': sync_event.operation_type,
                'collection': sync_event.collection,
                'document_id': str(sync_event.document_id),
                'timestamp': sync_event.timestamp.isoformat(),
                'data': sync_event.data
            },
            timestamp=datetime.now(),
            collection=sync_event.collection,
            priority=3
        )
        
        self.queue_update(update)
    
    def send_sync_status_update(self, sync_id: str, status: str, details: Dict[str, Any]):
        """Send sync status update."""
        update = RealtimeUpdate(
            update_id=self._generate_update_id(),
            update_type=UpdateType.SYNC_STATUS_CHANGED,
            channel="global",
            payload={
                'sync_id': sync_id,
                'status': status,
                'details': details,
                'timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now(),
            priority=4
        )
        
        self.queue_update(update)
    
    def send_conflict_update(self, conflict_id: str, conflict_data: Dict[str, Any]):
        """Send conflict detection update."""
        update = RealtimeUpdate(
            update_id=self._generate_update_id(),
            update_type=UpdateType.CONFLICT_DETECTED,
            channel="admin:conflicts",
            payload={
                'conflict_id': conflict_id,
                'conflict_data': conflict_data,
                'timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now(),
            priority=5  # High priority
        )
        
        self.queue_update(update)
    
    def send_batch_completion_update(self, batch_id: str, stats: Dict[str, Any]):
        """Send batch completion update."""
        update = RealtimeUpdate(
            update_id=self._generate_update_id(),
            update_type=UpdateType.BATCH_COMPLETED,
            channel="global",
            payload={
                'batch_id': batch_id,
                'statistics': stats,
                'timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now(),
            priority=2
        )
        
        self.queue_update(update)
    
    def send_user_notification(self, user_id: str, message: str, data: Dict[str, Any] = None):
        """Send notification to specific user."""
        update = RealtimeUpdate(
            update_id=self._generate_update_id(),
            update_type=UpdateType.HEALTH_UPDATE,
            channel=f"user:{user_id}",
            payload={
                'message': message,
                'data': data or {},
                'timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now(),
            user_id=user_id,
            priority=4
        )
        
        self.queue_update(update)
    
    def _generate_update_id(self) -> str:
        """Generate unique update ID."""
        timestamp = int(time.time() * 1000000)
        return f"update_{timestamp}"
    
    def _update_processor_loop(self):
        """Process queued updates."""
        logger.info("Update processor started")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                # Get update from queue
                update = self.update_queue.get(timeout=1)
                
                # Process the update
                asyncio.run(self._process_update(update))
                
                # Mark task as done
                self.update_queue.task_done()
                
            except:
                # Timeout or shutdown
                continue
        
        logger.info("Update processor stopped")
    
    async def _process_update(self, update: RealtimeUpdate):
        """Process a real-time update."""
        try:
            # Get connections subscribed to the channel
            target_connections = self.channels.get(update.channel, set())
            
            if not target_connections:
                logger.debug(f"No subscribers for channel: {update.channel}")
                return
            
            # Prepare message
            message = {
                'type': 'update',
                'update_id': update.update_id,
                'update_type': update.update_type.value,
                'channel': update.channel,
                'payload': update.payload,
                'timestamp': update.timestamp.isoformat(),
                'priority': update.priority
            }
            
            # Send to all subscribed connections
            successful = 0
            failed = 0
            
            for connection_id in list(target_connections):
                if await self._send_to_connection(connection_id, message):
                    successful += 1
                else:
                    failed += 1
            
            # Update statistics
            self.stats['updates_sent'] += successful
            self.stats['updates_failed'] += failed
            
            logger.debug(f"Sent update {update.update_id} to {successful}/{len(target_connections)} connections")
            
        except Exception as e:
            logger.error(f"Error processing update {update.update_id}: {e}")
            self.stats['updates_failed'] += 1
    
    def _ping_loop(self):
        """Send periodic pings and cleanup stale connections."""
        logger.info("Ping loop started")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                current_time = datetime.now()
                stale_connections = []
                
                # Check for stale connections
                for connection_id, connection in self.connections.items():
                    time_since_ping = current_time - connection.last_ping
                    
                    if time_since_ping.total_seconds() > self.connection_timeout:
                        stale_connections.append(connection_id)
                
                # Clean up stale connections
                for connection_id in stale_connections:
                    logger.info(f"Cleaning up stale connection: {connection_id}")
                    asyncio.run(self._cleanup_connection(connection_id))
                
                # Sleep before next ping cycle
                time.sleep(self.ping_interval)
                
            except Exception as e:
                logger.error(f"Error in ping loop: {e}")
                time.sleep(self.ping_interval)
        
        logger.info("Ping loop stopped")
    
    def get_connection_statistics(self) -> Dict[str, Any]:
        """Get connection statistics."""
        # Calculate channel statistics
        channel_stats = {}
        for channel, connections in self.channels.items():
            channel_stats[channel] = len(connections)
        
        # Calculate user statistics
        authenticated_users = len(self.user_connections)
        anonymous_connections = len([c for c in self.connections.values() if not c.user_id])
        
        return {
            'total_connections_ever': self.stats['total_connections'],
            'active_connections': self.stats['active_connections'],
            'authenticated_users': authenticated_users,
            'anonymous_connections': anonymous_connections,
            'total_channels': len(self.channels),
            'updates_sent': self.stats['updates_sent'],
            'updates_failed': self.stats['updates_failed'],
            'queue_size': self.update_queue.qsize(),
            'channel_subscribers': channel_stats,
            'server_running': self.running
        }
    
    def get_active_connections(self) -> List[Dict[str, Any]]:
        """Get list of active connections."""
        return [
            {
                'connection_id': conn.connection_id,
                'user_id': conn.user_id,
                'connected_at': conn.connected_at.isoformat(),
                'last_ping': conn.last_ping.isoformat(),
                'subscribed_channels': list(conn.subscribed_channels),
                'is_admin': conn.is_admin
            }
            for conn in self.connections.values()
        ]
    
    def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """Broadcast message to all subscribers of a channel."""
        update = RealtimeUpdate(
            update_id=self._generate_update_id(),
            update_type=UpdateType.HEALTH_UPDATE,
            channel=channel,
            payload=message,
            timestamp=datetime.now(),
            priority=3
        )
        
        self.queue_update(update)
    
    def kick_connection(self, connection_id: str) -> bool:
        """Forcibly disconnect a connection."""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            
            try:
                asyncio.run(connection.websocket.close())
                logger.info(f"Kicked connection: {connection_id}")
                return True
            except Exception as e:
                logger.error(f"Error kicking connection {connection_id}: {e}")
                return False
        
        return False
    
    async def stop_server(self):
        """Stop the realtime update server."""
        if not self.running:
            return
        
        logger.info("Stopping realtime updater")
        self.running = False
        self.shutdown_event.set()
        
        # Close all connections
        for connection_id in list(self.connections.keys()):
            await self._cleanup_connection(connection_id)
        
        # Stop server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # Wait for threads
        if self.update_processor_thread:
            self.update_processor_thread.join(timeout=5)
        
        if self.ping_thread:
            self.ping_thread.join(timeout=5)
        
        logger.info("Realtime updater stopped")

# Export the main class
__all__ = ['RealtimeUpdater', 'RealtimeUpdate', 'UpdateType', 'ClientConnection']