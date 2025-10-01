#!/usr/bin/env python3
"""
⚡ gRPC Streaming Template - Enterprise Real-time Communication
🏗️ Architecture: IA Chéries Creator Economy Platform
🔒 Protection IP: © 2025 Fahed Mlaiel <mlaiel@live.de>

🚨 AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import grpc
from grpc import aio
import asyncio
import time
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncIterator, Iterator, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import contextlib
from collections import defaultdict, deque
import threading
import weakref
import signal

# Expert Team: Lead Dev IA + Backend Senior + Microservices Architect + Real-time Systems Expert
__author__ = "Fahed Mlaiel"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Commercial license required"
__version__ = "1.0.0"
__email__ = "mlaiel@live.de"


class StreamType(str, Enum):
    """gRPC streaming types"""
    SERVER_STREAMING = "server_streaming"
    CLIENT_STREAMING = "client_streaming"
    BIDIRECTIONAL = "bidirectional"


class StreamState(str, Enum):
    """Stream connection states"""
    INITIALIZING = "initializing"
    CONNECTED = "connected"
    STREAMING = "streaming"
    PAUSED = "paused"
    ERROR = "error"
    DISCONNECTED = "disconnected"
    TERMINATED = "terminated"


class BackpressureStrategy(str, Enum):
    """Backpressure handling strategies"""
    DROP_OLDEST = "drop_oldest"
    DROP_NEWEST = "drop_newest"
    BLOCK = "block"
    THROTTLE = "throttle"


@dataclass
class StreamMetrics:
    """Streaming metrics collection"""
    connection_count: int = 0
    active_streams: int = 0
    total_messages_sent: int = 0
    total_messages_received: int = 0
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    connection_errors: int = 0
    stream_errors: int = 0
    reconnections: int = 0
    
    # Performance metrics
    average_latency: float = 0.0
    peak_concurrent_streams: int = 0
    throughput_per_second: float = 0.0
    
    # Per-stream metrics
    stream_durations: List[float] = field(default_factory=list)
    message_rates: List[float] = field(default_factory=list)
    
    def add_stream_duration(self, duration: float):
        """Add stream duration"""
        self.stream_durations.append(duration)
        if len(self.stream_durations) > 1000:  # Keep last 1000
            self.stream_durations.pop(0)
    
    def add_message_rate(self, rate: float):
        """Add message rate"""
        self.message_rates.append(rate)
        if len(self.message_rates) > 1000:  # Keep last 1000
            self.message_rates.pop(0)


@dataclass
class StreamConfig:
    """Enterprise streaming configuration"""
    # Connection settings
    max_concurrent_streams: int = 1000
    max_message_size: int = 4 * 1024 * 1024  # 4MB
    keepalive_time: int = 30  # seconds
    keepalive_timeout: int = 5  # seconds
    max_connection_idle: int = 300  # 5 minutes
    
    # Backpressure handling
    enable_backpressure: bool = True
    backpressure_strategy: BackpressureStrategy = BackpressureStrategy.THROTTLE
    buffer_size: int = 10000
    high_water_mark: int = 8000
    low_water_mark: int = 2000
    
    # Streaming features
    enable_compression: bool = True
    enable_flow_control: bool = True
    enable_heartbeat: bool = True
    heartbeat_interval: float = 30.0
    
    # Reconnection settings
    enable_auto_reconnect: bool = True
    max_reconnect_attempts: int = 10
    initial_reconnect_delay: float = 1.0
    max_reconnect_delay: float = 60.0
    reconnect_backoff_multiplier: float = 1.5
    
    # Monitoring
    enable_metrics: bool = True
    enable_stream_logging: bool = True
    log_message_content: bool = False
    
    # Security
    enable_stream_auth: bool = True
    auth_token_refresh_interval: int = 3600  # 1 hour
    
    # Creator-specific settings
    enable_creator_streams: bool = True
    creator_upload_stream_limit: int = 5  # concurrent uploads per creator
    creator_processing_stream_limit: int = 3  # concurrent processing per creator
    
    # Quality of Service
    enable_qos: bool = True
    priority_levels: int = 3
    high_priority_methods: List[str] = field(default_factory=lambda: [
        'StreamVideoUpload', 'StreamLiveContent', 'StreamAnalytics'
    ])


@dataclass
class StreamConnection:
    """Stream connection tracking"""
    connection_id: str
    client_id: str
    creator_id: Optional[str]
    method_name: str
    stream_type: StreamType
    state: StreamState
    created_at: datetime
    last_activity: datetime
    
    # Stream statistics
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    errors: int = 0
    
    # Context
    metadata: Dict[str, str] = field(default_factory=dict)
    context: Optional[Any] = None
    
    # Backpressure management
    buffer: deque = field(default_factory=deque)
    is_throttled: bool = False
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    @property
    def duration(self) -> timedelta:
        """Get connection duration"""
        return datetime.utcnow() - self.created_at
    
    @property
    def is_active(self) -> bool:
        """Check if connection is active"""
        return self.state in [StreamState.CONNECTED, StreamState.STREAMING]


class StreamManager:
    """
    🌊 Enterprise Stream Manager
    
    Features:
    - Connection lifecycle management
    - Backpressure handling
    - Stream quality monitoring
    - Automatic reconnection
    - Creator stream optimization
    """
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.logger = self._setup_logger()
        self.metrics = StreamMetrics()
        
        # Connection tracking
        self.connections: Dict[str, StreamConnection] = {}
        self.creator_streams: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.RLock()
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        
        # Start background tasks
        self._start_background_tasks()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup stream manager logger"""
        logger = logging.getLogger("grpc_stream_manager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        if asyncio.get_event_loop().is_running():
            self._cleanup_task = asyncio.create_task(self._cleanup_worker())
            self._metrics_task = asyncio.create_task(self._metrics_worker())
            
            if self.config.enable_heartbeat:
                self._heartbeat_task = asyncio.create_task(self._heartbeat_worker())
    
    async def register_stream(
        self,
        method_name: str,
        stream_type: StreamType,
        context,
        metadata: Dict[str, str]
    ) -> str:
        """Register new stream connection"""
        connection_id = str(uuid.uuid4())
        client_id = metadata.get('x-client-id', 'unknown')
        creator_id = metadata.get('x-creator-id')
        
        # Check concurrent stream limits
        if not await self._check_stream_limits(creator_id, method_name):
            raise grpc.RpcError("Stream limit exceeded")
        
        # Create connection record
        connection = StreamConnection(
            connection_id=connection_id,
            client_id=client_id,
            creator_id=creator_id,
            method_name=method_name,
            stream_type=stream_type,
            state=StreamState.INITIALIZING,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            metadata=metadata,
            context=context
        )
        
        with self._lock:
            self.connections[connection_id] = connection
            self.metrics.connection_count += 1
            self.metrics.active_streams += 1
            self.metrics.peak_concurrent_streams = max(
                self.metrics.peak_concurrent_streams,
                self.metrics.active_streams
            )
            
            # Track creator streams
            if creator_id:
                self.creator_streams[creator_id].append(connection_id)
        
        connection.state = StreamState.CONNECTED
        
        self.logger.info(
            f"Stream registered: {connection_id} - {method_name} "
            f"({stream_type.value}) for {client_id}"
        )
        
        return connection_id
    
    async def unregister_stream(self, connection_id: str):
        """Unregister stream connection"""
        with self._lock:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                
                # Update metrics
                self.metrics.active_streams -= 1
                self.metrics.add_stream_duration(connection.duration.total_seconds())
                
                # Remove from creator tracking
                if connection.creator_id:
                    creator_streams = self.creator_streams[connection.creator_id]
                    if connection_id in creator_streams:
                        creator_streams.remove(connection_id)
                
                connection.state = StreamState.TERMINATED
                del self.connections[connection_id]
                
                self.logger.info(f"Stream unregistered: {connection_id}")
    
    async def _check_stream_limits(self, creator_id: Optional[str], method_name: str) -> bool:
        """Check if stream can be created within limits"""
        # Global limit
        if self.metrics.active_streams >= self.config.max_concurrent_streams:
            return False
        
        # Creator-specific limits
        if creator_id and self.config.enable_creator_streams:
            creator_stream_count = len(self.creator_streams.get(creator_id, []))
            
            if 'upload' in method_name.lower():
                if creator_stream_count >= self.config.creator_upload_stream_limit:
                    return False
            
            elif 'process' in method_name.lower():
                if creator_stream_count >= self.config.creator_processing_stream_limit:
                    return False
        
        return True
    
    async def send_message(self, connection_id: str, message: Any) -> bool:
        """Send message through stream with backpressure handling"""
        with self._lock:
            if connection_id not in self.connections:
                return False
            
            connection = self.connections[connection_id]
            
            # Check backpressure
            if self.config.enable_backpressure:
                if not await self._handle_backpressure(connection, message):
                    return False
            
            try:
                # Update metrics
                connection.messages_sent += 1
                connection.bytes_sent += len(str(message))
                connection.update_activity()
                
                self.metrics.total_messages_sent += 1
                self.metrics.total_bytes_sent += connection.bytes_sent
                
                # Log if enabled
                if self.config.enable_stream_logging:
                    self.logger.debug(
                        f"Message sent: {connection_id} - {connection.method_name}"
                    )
                
                return True
                
            except Exception as e:
                connection.errors += 1
                self.metrics.stream_errors += 1
                self.logger.error(f"Error sending message: {connection_id} - {e}")
                return False
    
    async def receive_message(self, connection_id: str, message: Any) -> bool:
        """Receive message from stream"""
        with self._lock:
            if connection_id not in self.connections:
                return False
            
            connection = self.connections[connection_id]
            
            try:
                # Update metrics
                connection.messages_received += 1
                connection.bytes_received += len(str(message))
                connection.update_activity()
                
                self.metrics.total_messages_received += 1
                self.metrics.total_bytes_received += connection.bytes_received
                
                # Update state
                if connection.state == StreamState.CONNECTED:
                    connection.state = StreamState.STREAMING
                
                # Log if enabled
                if self.config.enable_stream_logging:
                    self.logger.debug(
                        f"Message received: {connection_id} - {connection.method_name}"
                    )
                
                return True
                
            except Exception as e:
                connection.errors += 1
                self.metrics.stream_errors += 1
                self.logger.error(f"Error receiving message: {connection_id} - {e}")
                return False
    
    async def _handle_backpressure(self, connection: StreamConnection, message: Any) -> bool:
        """Handle backpressure for stream"""
        buffer_size = len(connection.buffer)
        
        # Check if buffer is full
        if buffer_size >= self.config.buffer_size:
            if self.config.backpressure_strategy == BackpressureStrategy.DROP_OLDEST:
                connection.buffer.popleft()
                connection.buffer.append(message)
                return True
            
            elif self.config.backpressure_strategy == BackpressureStrategy.DROP_NEWEST:
                # Drop the new message
                return False
            
            elif self.config.backpressure_strategy == BackpressureStrategy.BLOCK:
                # This would block in a real implementation
                return False
            
            elif self.config.backpressure_strategy == BackpressureStrategy.THROTTLE:
                # Throttle the stream
                if not connection.is_throttled:
                    connection.is_throttled = True
                    self.logger.warning(f"Stream throttled: {connection.connection_id}")
                return False
        
        # Check throttling state
        if connection.is_throttled and buffer_size < self.config.low_water_mark:
            connection.is_throttled = False
            self.logger.info(f"Stream unthrottled: {connection.connection_id}")
        
        # Add message to buffer
        connection.buffer.append(message)
        return True
    
    async def handle_stream_error(self, connection_id: str, error: Exception):
        """Handle stream error"""
        with self._lock:
            if connection_id not in self.connections:
                return
            
            connection = self.connections[connection_id]
            connection.state = StreamState.ERROR
            connection.errors += 1
            self.metrics.stream_errors += 1
            
            self.logger.error(
                f"Stream error: {connection_id} - {connection.method_name} - {error}"
            )
            
            # Attempt recovery if configured
            if self.config.enable_auto_reconnect:
                await self._attempt_reconnection(connection)
    
    async def _attempt_reconnection(self, connection: StreamConnection):
        """Attempt to reconnect failed stream"""
        if connection.errors >= self.config.max_reconnect_attempts:
            self.logger.error(f"Max reconnection attempts reached: {connection.connection_id}")
            connection.state = StreamState.TERMINATED
            return
        
        # Calculate backoff delay
        delay = min(
            self.config.initial_reconnect_delay * (
                self.config.reconnect_backoff_multiplier ** connection.errors
            ),
            self.config.max_reconnect_delay
        )
        
        self.logger.info(
            f"Attempting reconnection: {connection.connection_id} "
            f"in {delay:.1f}s (attempt {connection.errors + 1})"
        )
        
        await asyncio.sleep(delay)
        
        # Reset connection state
        connection.state = StreamState.CONNECTED
        self.metrics.reconnections += 1
    
    async def _cleanup_worker(self):
        """Background task for cleaning up inactive connections"""
        while True:
            try:
                current_time = datetime.utcnow()
                inactive_connections = []
                
                with self._lock:
                    for connection_id, connection in self.connections.items():
                        # Check for inactive connections
                        inactive_duration = current_time - connection.last_activity
                        
                        if inactive_duration.total_seconds() > self.config.max_connection_idle:
                            inactive_connections.append(connection_id)
                
                # Clean up inactive connections
                for connection_id in inactive_connections:
                    await self.unregister_stream(connection_id)
                    self.logger.info(f"Cleaned up inactive stream: {connection_id}")
                
                # Sleep before next cleanup
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                self.logger.error(f"Cleanup worker error: {e}")
                await asyncio.sleep(60)
    
    async def _metrics_worker(self):
        """Background task for metrics collection"""
        last_message_count = 0
        last_time = time.time()
        
        while True:
            try:
                current_time = time.time()
                current_message_count = self.metrics.total_messages_sent + self.metrics.total_messages_received
                
                # Calculate throughput
                if current_time > last_time:
                    throughput = (current_message_count - last_message_count) / (current_time - last_time)
                    self.metrics.throughput_per_second = throughput
                    self.metrics.add_message_rate(throughput)
                
                last_message_count = current_message_count
                last_time = current_time
                
                # Log metrics periodically
                if self.config.enable_metrics:
                    self.logger.info(
                        f"Stream metrics: Active={self.metrics.active_streams}, "
                        f"Throughput={self.metrics.throughput_per_second:.1f}/s, "
                        f"Errors={self.metrics.stream_errors}"
                    )
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Metrics worker error: {e}")
                await asyncio.sleep(30)
    
    async def _heartbeat_worker(self):
        """Background task for stream heartbeats"""
        while True:
            try:
                if not self.config.enable_heartbeat:
                    break
                
                current_time = datetime.utcnow()
                
                with self._lock:
                    for connection in self.connections.values():
                        if connection.is_active:
                            # Check if heartbeat is needed
                            time_since_activity = (current_time - connection.last_activity).total_seconds()
                            
                            if time_since_activity > self.config.heartbeat_interval:
                                # Send heartbeat (implementation depends on your protocol)
                                await self._send_heartbeat(connection)
                
                await asyncio.sleep(self.config.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Heartbeat worker error: {e}")
                await asyncio.sleep(self.config.heartbeat_interval)
    
    async def _send_heartbeat(self, connection: StreamConnection):
        """Send heartbeat to maintain connection"""
        try:
            # Implementation would depend on your specific protocol
            # This is a placeholder
            heartbeat_message = {
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat(),
                "connection_id": connection.connection_id
            }
            
            # Update activity
            connection.update_activity()
            
            self.logger.debug(f"Heartbeat sent: {connection.connection_id}")
            
        except Exception as e:
            self.logger.error(f"Heartbeat failed: {connection.connection_id} - {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current streaming metrics"""
        with self._lock:
            return {
                "connection_count": self.metrics.connection_count,
                "active_streams": self.metrics.active_streams,
                "total_messages_sent": self.metrics.total_messages_sent,
                "total_messages_received": self.metrics.total_messages_received,
                "total_bytes_sent": self.metrics.total_bytes_sent,
                "total_bytes_received": self.metrics.total_bytes_received,
                "connection_errors": self.metrics.connection_errors,
                "stream_errors": self.metrics.stream_errors,
                "reconnections": self.metrics.reconnections,
                "average_latency": self.metrics.average_latency,
                "peak_concurrent_streams": self.metrics.peak_concurrent_streams,
                "throughput_per_second": self.metrics.throughput_per_second,
                "creator_streams": {
                    creator_id: len(streams) 
                    for creator_id, streams in self.creator_streams.items()
                }
            }
    
    def get_connection_details(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a connection"""
        with self._lock:
            if connection_id not in self.connections:
                return None
            
            connection = self.connections[connection_id]
            return {
                "connection_id": connection.connection_id,
                "client_id": connection.client_id,
                "creator_id": connection.creator_id,
                "method_name": connection.method_name,
                "stream_type": connection.stream_type.value,
                "state": connection.state.value,
                "created_at": connection.created_at.isoformat(),
                "last_activity": connection.last_activity.isoformat(),
                "duration": connection.duration.total_seconds(),
                "messages_sent": connection.messages_sent,
                "messages_received": connection.messages_received,
                "bytes_sent": connection.bytes_sent,
                "bytes_received": connection.bytes_received,
                "errors": connection.errors,
                "buffer_size": len(connection.buffer),
                "is_throttled": connection.is_throttled
            }
    
    async def shutdown(self):
        """Graceful shutdown of stream manager"""
        self.logger.info("Shutting down stream manager...")
        
        # Cancel background tasks
        tasks = [self._cleanup_task, self._metrics_task, self._heartbeat_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Close all active connections
        with self._lock:
            connection_ids = list(self.connections.keys())
        
        for connection_id in connection_ids:
            await self.unregister_stream(connection_id)
        
        self.logger.info("Stream manager shutdown complete")


class ServerStreamingService:
    """
    🌊📤 Enterprise Server Streaming Service
    
    Features:
    - High-throughput streaming
    - Real-time data delivery
    - Stream multiplexing
    - Quality of Service
    """
    
    def __init__(self, stream_manager: StreamManager):
        self.stream_manager = stream_manager
        self.logger = logging.getLogger("grpc_server_streaming")
    
    async def stream_content_updates(self, request, context) -> AsyncIterator[Any]:
        """Stream content updates to creators"""
        connection_id = await self.stream_manager.register_stream(
            method_name="StreamContentUpdates",
            stream_type=StreamType.SERVER_STREAMING,
            context=context,
            metadata=dict(context.invocation_metadata())
        )
        
        try:
            self.logger.info(f"Starting content updates stream: {connection_id}")
            
            # Mock streaming data - in reality this would come from your data sources
            update_count = 0
            while not context.cancelled():
                # Create mock update
                update = {
                    "update_id": update_count,
                    "timestamp": datetime.utcnow().isoformat(),
                    "content_id": request.content_id if hasattr(request, 'content_id') else "sample",
                    "update_type": "analytics_update",
                    "data": {
                        "views": update_count * 100,
                        "likes": update_count * 10,
                        "shares": update_count * 2
                    }
                }
                
                # Send message through stream manager
                if await self.stream_manager.send_message(connection_id, update):
                    yield update  # This would be your actual protobuf message
                    update_count += 1
                
                # Wait before next update
                await asyncio.sleep(1.0)
                
                # Check for stream limits
                if update_count >= 1000:  # Limit for demo
                    break
            
            self.logger.info(f"Content updates stream completed: {connection_id}")
            
        except Exception as e:
            await self.stream_manager.handle_stream_error(connection_id, e)
            self.logger.error(f"Stream error: {connection_id} - {e}")
        
        finally:
            await self.stream_manager.unregister_stream(connection_id)
    
    async def stream_live_analytics(self, request, context) -> AsyncIterator[Any]:
        """Stream real-time analytics to creators"""
        connection_id = await self.stream_manager.register_stream(
            method_name="StreamLiveAnalytics",
            stream_type=StreamType.SERVER_STREAMING,
            context=context,
            metadata=dict(context.invocation_metadata())
        )
        
        try:
            self.logger.info(f"Starting live analytics stream: {connection_id}")
            
            while not context.cancelled():
                # Generate mock analytics data
                analytics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "real_time_viewers": 1500 + (update_count % 100),
                    "engagement_rate": 0.15 + (update_count % 10) * 0.01,
                    "revenue_current": 245.67 + update_count * 0.1,
                    "top_countries": ["US", "UK", "DE", "FR"],
                    "trending_content": ["video_123", "audio_456", "image_789"]
                }
                
                if await self.stream_manager.send_message(connection_id, analytics):
                    yield analytics  # Actual protobuf message
                
                await asyncio.sleep(5.0)  # Update every 5 seconds
            
        except Exception as e:
            await self.stream_manager.handle_stream_error(connection_id, e)
        finally:
            await self.stream_manager.unregister_stream(connection_id)


class ClientStreamingService:
    """
    📤🌊 Enterprise Client Streaming Service
    
    Features:
    - Large file uploads
    - Chunked data transfer
    - Progress tracking
    - Resume capability
    """
    
    def __init__(self, stream_manager: StreamManager):
        self.stream_manager = stream_manager
        self.logger = logging.getLogger("grpc_client_streaming")
    
    async def upload_content(self, request_iterator, context) -> Any:
        """Handle client streaming uploads"""
        connection_id = await self.stream_manager.register_stream(
            method_name="UploadContent",
            stream_type=StreamType.CLIENT_STREAMING,
            context=context,
            metadata=dict(context.invocation_metadata())
        )
        
        try:
            self.logger.info(f"Starting content upload stream: {connection_id}")
            
            total_size = 0
            chunk_count = 0
            
            async for chunk in request_iterator:
                if not await self.stream_manager.receive_message(connection_id, chunk):
                    break
                
                # Process chunk
                chunk_size = len(chunk.data) if hasattr(chunk, 'data') else 0
                total_size += chunk_size
                chunk_count += 1
                
                # Log progress
                if chunk_count % 100 == 0:
                    self.logger.info(
                        f"Upload progress: {connection_id} - "
                        f"Chunks: {chunk_count}, Size: {total_size} bytes"
                    )
                
                # Check for completion
                if hasattr(chunk, 'is_last') and chunk.is_last:
                    break
            
            # Return upload result
            result = {
                "upload_id": str(uuid.uuid4()),
                "total_chunks": chunk_count,
                "total_size": total_size,
                "status": "completed",
                "message": "Upload successful"
            }
            
            self.logger.info(f"Upload completed: {connection_id} - {total_size} bytes")
            return result  # Actual protobuf response
            
        except Exception as e:
            await self.stream_manager.handle_stream_error(connection_id, e)
            raise
        finally:
            await self.stream_manager.unregister_stream(connection_id)


class BidirectionalStreamingService:
    """
    🔄🌊 Enterprise Bidirectional Streaming Service
    
    Features:
    - Real-time communication
    - Live collaboration
    - Interactive streams
    - Synchronized updates
    """
    
    def __init__(self, stream_manager: StreamManager):
        self.stream_manager = stream_manager
        self.logger = logging.getLogger("grpc_bidirectional_streaming")
    
    async def live_collaboration(self, request_iterator, context) -> AsyncIterator[Any]:
        """Handle bidirectional streaming for live collaboration"""
        connection_id = await self.stream_manager.register_stream(
            method_name="LiveCollaboration",
            stream_type=StreamType.BIDIRECTIONAL,
            context=context,
            metadata=dict(context.invocation_metadata())
        )
        
        try:
            self.logger.info(f"Starting live collaboration stream: {connection_id}")
            
            # Start receiving messages in background
            receive_task = asyncio.create_task(
                self._handle_incoming_messages(request_iterator, connection_id)
            )
            
            # Start sending messages
            message_count = 0
            while not context.cancelled():
                # Generate collaboration updates
                update = {
                    "message_id": message_count,
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "collaboration_update",
                    "data": {
                        "cursor_position": {"x": 100 + message_count, "y": 200},
                        "active_users": ["user1", "user2", "user3"],
                        "recent_changes": [
                            {"type": "text_insert", "position": 150, "content": "Hello"}
                        ]
                    }
                }
                
                if await self.stream_manager.send_message(connection_id, update):
                    yield update  # Actual protobuf message
                    message_count += 1
                
                await asyncio.sleep(0.1)  # High frequency updates
            
            # Wait for receive task to complete
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
            
        except Exception as e:
            await self.stream_manager.handle_stream_error(connection_id, e)
        finally:
            await self.stream_manager.unregister_stream(connection_id)
    
    async def _handle_incoming_messages(self, request_iterator, connection_id: str):
        """Handle incoming messages in bidirectional stream"""
        try:
            async for message in request_iterator:
                if not await self.stream_manager.receive_message(connection_id, message):
                    break
                
                # Process incoming message
                self.logger.debug(f"Received message: {connection_id}")
                
                # Handle specific message types
                if hasattr(message, 'type'):
                    if message.type == "cursor_move":
                        # Handle cursor movement
                        pass
                    elif message.type == "text_change":
                        # Handle text changes
                        pass
                    elif message.type == "user_join":
                        # Handle user joining
                        pass
        
        except Exception as e:
            self.logger.error(f"Error handling incoming messages: {connection_id} - {e}")


# Factory functions for easy integration
def create_stream_manager(config: Optional[StreamConfig] = None) -> StreamManager:
    """
    🏭 Factory function to create stream manager
    
    Args:
        config: Stream configuration
    
    Returns:
        Configured stream manager instance
    """
    if config is None:
        config = StreamConfig()
    
    return StreamManager(config)


def setup_creator_streaming() -> StreamManager:
    """
    🎯 Creator-specific streaming setup
    Optimized for content creation platforms
    """
    config = StreamConfig(
        # Enhanced limits for creator content
        max_concurrent_streams=2000,
        max_message_size=50 * 1024 * 1024,  # 50MB for large media
        
        # Creator-specific settings
        enable_creator_streams=True,
        creator_upload_stream_limit=10,     # More concurrent uploads
        creator_processing_stream_limit=5,   # More processing streams
        
        # Enhanced backpressure for large files
        enable_backpressure=True,
        backpressure_strategy=BackpressureStrategy.THROTTLE,
        buffer_size=50000,  # Larger buffer
        high_water_mark=40000,
        low_water_mark=10000,
        
        # Optimized for content delivery
        enable_compression=True,
        enable_flow_control=True,
        enable_heartbeat=True,
        heartbeat_interval=15.0,  # More frequent heartbeats
        
        # Enhanced reconnection for mobile creators
        enable_auto_reconnect=True,
        max_reconnect_attempts=20,
        initial_reconnect_delay=0.5,
        max_reconnect_delay=30.0,
        
        # Quality of Service for creator priorities
        enable_qos=True,
        priority_levels=5,
        high_priority_methods=[
            'StreamVideoUpload', 'StreamLiveContent', 'StreamAnalytics',
            'LiveCollaboration', 'StreamProcessingUpdates'
        ],
        
        # Enhanced monitoring
        enable_metrics=True,
        enable_stream_logging=True,
        log_message_content=False,  # Privacy for creator content
        
        # Security for creator accounts
        enable_stream_auth=True,
        auth_token_refresh_interval=1800  # 30 minutes
    )
    
    return StreamManager(config)


if __name__ == "__main__":
    # Example usage
    async def example_streaming_server():
        """Example streaming server setup"""
        # Create stream manager
        stream_manager = setup_creator_streaming()
        
        # Create services
        server_streaming = ServerStreamingService(stream_manager)
        client_streaming = ClientStreamingService(stream_manager)
        bidirectional_streaming = BidirectionalStreamingService(stream_manager)
        
        print("Streaming services initialized")
        print("Stream manager metrics:")
        print(json.dumps(stream_manager.get_metrics(), indent=2))
        
        # Simulate running for a while
        await asyncio.sleep(1)
        
        # Shutdown
        await stream_manager.shutdown()
    
    # Run example
    print("gRPC Streaming Template Example")
    print("This demonstrates enterprise streaming for the IA Chéries creator platform")
    
    # Show configuration example
    creator_config = StreamConfig(
        enable_creator_streams=True,
        max_concurrent_streams=1000,
        enable_backpressure=True
    )
    
    print(f"\nCreator streaming configuration:")
    print(f"- Max concurrent streams: {creator_config.max_concurrent_streams}")
    print(f"- Creator streams enabled: {creator_config.enable_creator_streams}")
    print(f"- Backpressure enabled: {creator_config.enable_backpressure}")
    
    # Run async example
    asyncio.run(example_streaming_server())