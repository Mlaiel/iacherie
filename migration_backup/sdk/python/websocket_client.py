"""WebSocket Real-time Client for Ainflue SDK

Enterprise-grade WebSocket client with multi-expert design:
- DevOps: Connection monitoring and automatic reconnection
- Backend Senior: Robust real-time architecture with heartbeat
- Sécurité: Secure WebSocket connections with authentication
- Lead Dev IA: Intelligent connection management and event routing

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import json
import logging
import ssl
import time
from typing import Dict, Any, Optional, Callable, List, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import websockets
import certifi

from .exceptions import (
    NetworkError, AuthenticationError, AinflueSdkException,
    ConfigurationError
)


class ConnectionState(Enum):
    """WebSocket connection states"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    message_id: Optional[str] = None
    correlation_id: Optional[str] = None


class ConnectionMetrics:
    """Connection metrics for monitoring (DevOps expertise)"""
    
    def __init__(self):
        self.connected_at: Optional[datetime] = None
        self.disconnected_at: Optional[datetime] = None
        self.total_messages_sent = 0
        self.total_messages_received = 0
        self.total_reconnections = 0
        self.last_heartbeat: Optional[datetime] = None
        self.connection_errors = 0
    
    def record_connection(self):
        """Record successful connection"""
        self.connected_at = datetime.utcnow()
        self.disconnected_at = None
    
    def record_disconnection(self):
        """Record disconnection"""
        self.disconnected_at = datetime.utcnow()
    
    def record_message_sent(self):
        """Record sent message"""
        self.total_messages_sent += 1
    
    def record_message_received(self):
        """Record received message"""
        self.total_messages_received += 1
    
    def record_reconnection(self):
        """Record reconnection attempt"""
        self.total_reconnections += 1
    
    def record_heartbeat(self):
        """Record heartbeat"""
        self.last_heartbeat = datetime.utcnow()
    
    def record_error(self):
        """Record connection error"""
        self.connection_errors += 1
    
    def get_uptime(self) -> Optional[timedelta]:
        """Get connection uptime"""
        if self.connected_at and not self.disconnected_at:
            return datetime.utcnow() - self.connected_at
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        uptime = self.get_uptime()
        
        return {
            'connected_at': self.connected_at.isoformat() if self.connected_at else None,
            'disconnected_at': self.disconnected_at.isoformat() if self.disconnected_at else None,
            'uptime_seconds': uptime.total_seconds() if uptime else None,
            'messages_sent': self.total_messages_sent,
            'messages_received': self.total_messages_received,
            'reconnections': self.total_reconnections,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'connection_errors': self.connection_errors
        }


class WebSocketClient:
    """Enterprise WebSocket client for Ainflue real-time communication
    
    Features:
    - Automatic reconnection with exponential backoff
    - Heartbeat monitoring
    - Message queuing during disconnection
    - Event-driven architecture
    - Connection metrics and monitoring
    - Secure authentication
    """
    
    def __init__(
        self,
        url: str,
        api_key: Optional[str] = None,
        protocols: Optional[List[str]] = None,
        heartbeat_interval: int = 30,
        reconnect_interval: float = 1.0,
        max_reconnect_attempts: int = 10,
        message_queue_size: int = 1000,
        ping_timeout: int = 10,
        close_timeout: int = 10
    ):
        self.url = url
        self.api_key = api_key
        self.protocols = protocols or []
        self.heartbeat_interval = heartbeat_interval
        self.reconnect_interval = reconnect_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        self.message_queue_size = message_queue_size
        self.ping_timeout = ping_timeout
        self.close_timeout = close_timeout
        
        # Connection state
        self.state = ConnectionState.DISCONNECTED
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._reconnect_attempts = 0
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._message_handlers: Dict[str, Callable] = {}
        
        # Message queue for offline messages
        self._message_queue: List[WebSocketMessage] = []
        
        # Tasks
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._reconnect_task: Optional[asyncio.Task] = None
        self._receive_task: Optional[asyncio.Task] = None
        
        # Metrics and logging
        self.metrics = ConnectionMetrics()
        self.logger = logging.getLogger(__name__)
        
        # Authentication headers
        self._auth_headers = self._build_auth_headers()
    
    def _build_auth_headers(self) -> Dict[str, str]:
        """Build authentication headers (Sécurité expertise)"""
        headers = {
            'User-Agent': 'Ainflue-WebSocket-Client/1.0.0'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        return headers
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create secure SSL context"""
        context = ssl.create_default_context(cafile=certifi.where())
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        return context
    
    async def connect(self) -> bool:
        """Connect to WebSocket server"""
        if self.state in [ConnectionState.CONNECTED, ConnectionState.CONNECTING]:
            return True
        
        self.state = ConnectionState.CONNECTING
        self.logger.info(f"Connecting to WebSocket: {self.url}")
        
        try:
            # Create SSL context for secure connections
            ssl_context = self._create_ssl_context() if self.url.startswith('wss://') else None
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                self.url,
                extra_headers=self._auth_headers,
                subprotocols=self.protocols,
                ssl=ssl_context,
                ping_timeout=self.ping_timeout,
                close_timeout=self.close_timeout
            )
            
            self.state = ConnectionState.CONNECTED
            self._reconnect_attempts = 0
            self.metrics.record_connection()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Send queued messages
            await self._send_queued_messages()
            
            # Emit connection event
            await self._emit_event('connected', {})
            
            self.logger.info("WebSocket connected successfully")
            return True
            
        except Exception as e:
            self.state = ConnectionState.FAILED
            self.metrics.record_error()
            self.logger.error(f"WebSocket connection failed: {str(e)}")
            
            # Emit error event
            await self._emit_event('error', {'error': str(e)})
            
            # Schedule reconnection
            if self._should_reconnect():
                await self._schedule_reconnect()
            
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        if self.state == ConnectionState.DISCONNECTED:
            return
        
        self.logger.info("Disconnecting WebSocket")
        
        # Stop background tasks
        await self._stop_background_tasks()
        
        # Close WebSocket connection
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        self.state = ConnectionState.DISCONNECTED
        self.metrics.record_disconnection()
        
        # Emit disconnection event
        await self._emit_event('disconnected', {})
        
        self.logger.info("WebSocket disconnected")
    
    async def send_message(self, message_type: str, data: Dict[str, Any]) -> bool:
        """Send message to WebSocket server"""
        message = WebSocketMessage(
            type=message_type,
            data=data,
            timestamp=datetime.utcnow(),
            message_id=f"msg_{int(time.time() * 1000)}"
        )
        
        if self.state == ConnectionState.CONNECTED and self.websocket:
            try:
                # Send message
                message_json = json.dumps({
                    'type': message.type,
                    'data': message.data,
                    'timestamp': message.timestamp.isoformat(),
                    'message_id': message.message_id
                })
                
                await self.websocket.send(message_json)
                self.metrics.record_message_sent()
                
                self.logger.debug(f"Sent message: {message.type}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to send message: {str(e)}")
                await self._handle_connection_error(e)
                
                # Queue message for later
                await self._queue_message(message)
                return False
        else:
            # Queue message for when connected
            await self._queue_message(message)
            return False
    
    async def _queue_message(self, message: WebSocketMessage):
        """Queue message for later delivery"""
        if len(self._message_queue) >= self.message_queue_size:
            # Remove oldest message
            self._message_queue.pop(0)
        
        self._message_queue.append(message)
        self.logger.debug(f"Queued message: {message.type}")
    
    async def _send_queued_messages(self):
        """Send all queued messages"""
        if not self._message_queue:
            return
        
        self.logger.info(f"Sending {len(self._message_queue)} queued messages")
        
        messages_to_send = self._message_queue.copy()
        self._message_queue.clear()
        
        for message in messages_to_send:
            success = await self.send_message(message.type, message.data)
            if not success:
                # Re-queue if failed
                await self._queue_message(message)
    
    def on(self, event: str, handler: Callable):
        """Register event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        
        self._event_handlers[event].append(handler)
    
    def on_message(self, message_type: str, handler: Callable):
        """Register message handler"""
        self._message_handlers[message_type] = handler
    
    async def _emit_event(self, event: str, data: Dict[str, Any]):
        """Emit event to registered handlers"""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    self.logger.error(f"Event handler error for {event}: {str(e)}")
    
    async def _start_background_tasks(self):
        """Start background tasks"""
        # Start message receiving task
        self._receive_task = asyncio.create_task(self._receive_loop())
        
        # Start heartbeat task
        if self.heartbeat_interval > 0:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
    
    async def _stop_background_tasks(self):
        """Stop background tasks"""
        tasks = [self._receive_task, self._heartbeat_task, self._reconnect_task]
        
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self._receive_task = None
        self._heartbeat_task = None
        self._reconnect_task = None
    
    async def _receive_loop(self):
        """Message receiving loop"""
        try:
            while self.websocket and self.state == ConnectionState.CONNECTED:
                try:
                    # Receive message
                    message_raw = await self.websocket.recv()
                    self.metrics.record_message_received()
                    
                    # Parse message
                    try:
                        message_data = json.loads(message_raw)
                        message_type = message_data.get('type')
                        
                        if message_type:
                            # Handle specific message types
                            if message_type == 'pong':
                                self.metrics.record_heartbeat()
                            elif message_type in self._message_handlers:
                                handler = self._message_handlers[message_type]
                                if asyncio.iscoroutinefunction(handler):
                                    await handler(message_data)
                                else:
                                    handler(message_data)
                            
                            # Emit message event
                            await self._emit_event('message', message_data)
                        
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Invalid JSON message: {str(e)}")
                    
                except websockets.exceptions.ConnectionClosed:
                    self.logger.info("WebSocket connection closed")
                    break
                except Exception as e:
                    self.logger.error(f"Error receiving message: {str(e)}")
                    await self._handle_connection_error(e)
                    break
        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Receive loop error: {str(e)}")
            await self._handle_connection_error(e)
    
    async def _heartbeat_loop(self):
        """Heartbeat loop"""
        try:
            while self.state == ConnectionState.CONNECTED:
                await asyncio.sleep(self.heartbeat_interval)
                
                if self.websocket and self.state == ConnectionState.CONNECTED:
                    try:
                        # Send ping
                        await self.websocket.ping()
                        await self.send_message('ping', {'timestamp': datetime.utcnow().isoformat()})
                        
                    except Exception as e:
                        self.logger.error(f"Heartbeat failed: {str(e)}")
                        await self._handle_connection_error(e)
                        break
        
        except asyncio.CancelledError:
            pass
    
    async def _handle_connection_error(self, error: Exception):
        """Handle connection errors"""
        self.state = ConnectionState.FAILED
        self.metrics.record_error()
        
        # Emit error event
        await self._emit_event('error', {'error': str(error)})
        
        # Schedule reconnection
        if self._should_reconnect():
            await self._schedule_reconnect()
    
    def _should_reconnect(self) -> bool:
        """Check if should attempt reconnection"""
        return (self._reconnect_attempts < self.max_reconnect_attempts and 
                self.state != ConnectionState.DISCONNECTED)
    
    async def _schedule_reconnect(self):
        """Schedule reconnection attempt"""
        if self._reconnect_task and not self._reconnect_task.done():
            return
        
        self._reconnect_task = asyncio.create_task(self._reconnect_loop())
    
    async def _reconnect_loop(self):
        """Reconnection loop with exponential backoff"""
        try:
            while self._should_reconnect():
                self._reconnect_attempts += 1
                self.metrics.record_reconnection()
                
                # Calculate backoff delay
                delay = min(self.reconnect_interval * (2 ** (self._reconnect_attempts - 1)), 60)
                
                self.logger.info(f"Reconnecting in {delay:.1f}s (attempt {self._reconnect_attempts})")
                self.state = ConnectionState.RECONNECTING
                
                await asyncio.sleep(delay)
                
                # Attempt reconnection
                if await self.connect():
                    self.logger.info("Reconnection successful")
                    break
                else:
                    self.logger.warning(f"Reconnection attempt {self._reconnect_attempts} failed")
            
            if not self._should_reconnect():
                self.logger.error("Max reconnection attempts exceeded")
                self.state = ConnectionState.FAILED
                await self._emit_event('max_reconnects_exceeded', {})
        
        except asyncio.CancelledError:
            pass
    
    def get_state(self) -> ConnectionState:
        """Get current connection state"""
        return self.state
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get connection metrics"""
        return self.metrics.get_stats()
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self.state == ConnectionState.CONNECTED and self.websocket is not None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


# Export WebSocket client
__all__ = ['WebSocketClient', 'ConnectionState', 'WebSocketMessage', 'ConnectionMetrics']