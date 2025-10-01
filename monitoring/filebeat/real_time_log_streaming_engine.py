#!/usr/bin/env python3
"""
Real-Time Log Streaming Engine - Creator Economy Enterprise
=========================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
# import websockets  # Not available in environment
# # Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")  # Not available in environment
from collections import deque, defaultdict
import uuid


class StreamingChannel(Enum):
    """Streaming channels for different log types"""
    CREATOR_ACTIVITY = "creator_activity"
    CONTENT_PROCESSING = "content_processing"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    PERFORMANCE_METRICS = "performance_metrics"
    ANOMALIES = "anomalies"
    REAL_TIME_ANALYTICS = "real_time_analytics"


@dataclass
class StreamingConnection:
    """Represents a streaming connection"""
    connection_id: str
    websocket: Any
    subscribed_channels: Set[StreamingChannel] = field(default_factory=set)
    creator_filters: Set[str] = field(default_factory=set)
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    connection_type: str = "websocket"
    metadata: Dict[str, Any] = field(default_factory=dict)


class RealTimeLogStreamingEngine:
    """
    Moteur streaming logs temps réel enterprise
    
    Real-time log streaming Creator Economy processing
    Creator log events streaming intelligent
    Real-time Creator analytics log processing
    Creator log streaming performance optimization
    Real-time Creator log aggregation engine
    Creator log streaming scalability optimization
    """
    
    def __init__(self, config, orchestrator=None):
        self.config = config
        self.orchestrator = orchestrator
        self.logger = self._setup_logging()
        
        # Streaming infrastructure
        self._connections: Dict[str, StreamingConnection] = {}
        self._channel_subscribers: Dict[StreamingChannel, Set[str]] = defaultdict(set)
        self._stream_buffers: Dict[StreamingChannel, deque] = {}
        self._websocket_server = None
        
        # Redis for distributed streaming
        self._redis_client: Optional[aioredis.Redis] = None
        
        # State management
        self._initialized = False
        self._running = False
        self._streaming_workers: List[asyncio.Task] = []
        
        # Performance metrics
        self._streaming_metrics = {
            "active_connections": 0,
            "messages_streamed": 0,
            "channels_active": 0,
            "throughput_msg_per_sec": 0.0,
            "latency_ms": 0.0,
            "buffer_sizes": {},
            "connection_types": defaultdict(int),
            "errors_count": 0,
            "uptime_seconds": 0
        }
        
        # Streaming configuration
        self._streaming_config = self._initialize_streaming_config()
        
        # Message processors for each channel
        self._channel_processors: Dict[StreamingChannel, Callable] = {}
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for streaming engine"""
        logger = logging.getLogger("filebeat.streaming_engine")
        logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [STREAMING] %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_streaming_config(self) -> Dict[str, Any]:
        """Initialize streaming configuration"""
        return {
            "websocket": {
                "host": "0.0.0.0",
                "port": 8765,
                "max_connections": 1000,
                "ping_interval": 30,
                "ping_timeout": 10,
                "close_timeout": 10
            },
            "buffering": {
                "max_buffer_size": 10000,
                "flush_interval_seconds": 1.0,
                "compression_enabled": True,
                "batch_size": 100
            },
            "redis": {
                "host": "redis.iacherie-monitoring.svc.cluster.local",
                "port": 6379,
                "db": 0,
                "channel_prefix": "filebeat_stream"
            },
            "performance": {
                "max_throughput_msg_per_sec": 10000,
                "latency_threshold_ms": 100.0,
                "connection_timeout_seconds": 300,
                "heartbeat_interval_seconds": 30
            },
            "channels": {
                StreamingChannel.CREATOR_ACTIVITY: {
                    "priority": "high",
                    "buffer_size": 5000,
                    "compression": True
                },
                StreamingChannel.CONTENT_PROCESSING: {
                    "priority": "medium",
                    "buffer_size": 3000,
                    "compression": True
                },
                StreamingChannel.MONETIZATION: {
                    "priority": "high",
                    "buffer_size": 2000,
                    "compression": False
                },
                StreamingChannel.COLLABORATION: {
                    "priority": "medium",
                    "buffer_size": 2000,
                    "compression": True
                },
                StreamingChannel.PERFORMANCE_METRICS: {
                    "priority": "low",
                    "buffer_size": 10000,
                    "compression": True
                },
                StreamingChannel.ANOMALIES: {
                    "priority": "critical",
                    "buffer_size": 1000,
                    "compression": False
                },
                StreamingChannel.REAL_TIME_ANALYTICS: {
                    "priority": "high",
                    "buffer_size": 5000,
                    "compression": True
                }
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize real-time streaming engine"""
        try:
            self.logger.info("Initializing Real-Time Log Streaming Engine...")
            
            # Initialize stream buffers
            await self._initialize_stream_buffers()
            
            # Initialize Redis client
            await self._initialize_redis_client()
            
            # Setup channel processors
            await self._setup_channel_processors()
            
            # Initialize websocket server
            await self._initialize_websocket_server()
            
            self._initialized = True
            self.logger.info("Real-Time Log Streaming Engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize streaming engine: {e}")
            return False
    
    async def _initialize_stream_buffers(self):
        """Initialize streaming buffers for each channel"""
        for channel in StreamingChannel:
            channel_config = self._streaming_config["channels"][channel]
            buffer_size = channel_config["buffer_size"]
            self._stream_buffers[channel] = deque(maxlen=buffer_size)
    
    async def _initialize_redis_client(self):
        """Initialize Redis client for distributed streaming"""
        try:
            # Redis not available in this environment
            self.logger.warning("Redis client not available in this environment")
            self._redis_client = None
        except Exception as e:
            self.logger.warning(f"Redis client initialization failed: {e}")
            self._redis_client = None
    
    async def _setup_channel_processors(self):
        """Setup message processors for each streaming channel"""
        self._channel_processors = {
            StreamingChannel.CREATOR_ACTIVITY: self._process_creator_activity_message,
            StreamingChannel.CONTENT_PROCESSING: self._process_content_processing_message,
            StreamingChannel.MONETIZATION: self._process_monetization_message,
            StreamingChannel.COLLABORATION: self._process_collaboration_message,
            StreamingChannel.PERFORMANCE_METRICS: self._process_performance_metrics_message,
            StreamingChannel.ANOMALIES: self._process_anomaly_message,
            StreamingChannel.REAL_TIME_ANALYTICS: self._process_analytics_message
        }
    
    async def _initialize_websocket_server(self):
        """Initialize WebSocket server for real-time streaming"""
        try:
            # WebSocket server not available in this environment
            self.logger.warning("WebSocket server not available in this environment")
            self._websocket_server = None
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebSocket server: {e}")
            raise
    
    async def start(self) -> bool:
        """Start real-time streaming services"""
        if not self._initialized:
            if not await self.initialize():
                return False
        
        try:
            self.logger.info("Starting Real-Time Log Streaming Engine...")
            
            # Start streaming workers
            streaming_workers = [
                asyncio.create_task(self._buffer_flusher_worker()),
                asyncio.create_task(self._connection_monitor_worker()),
                asyncio.create_task(self._performance_monitor_worker()),
                asyncio.create_task(self._redis_subscriber_worker()) if self._redis_client else None,
                asyncio.create_task(self._heartbeat_worker())
            ]
            
            # Filter out None workers
            self._streaming_workers = [worker for worker in streaming_workers if worker is not None]
            
            self._running = True
            self.logger.info("Real-Time Log Streaming Engine started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start streaming engine: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop streaming services gracefully"""
        try:
            self.logger.info("Stopping Real-Time Log Streaming Engine...")
            
            self._running = False
            
            # Close WebSocket server
            if self._websocket_server:
                self._websocket_server.close()
                await self._websocket_server.wait_closed()
            
            # Close all connections
            await self._close_all_connections()
            
            # Cancel streaming workers
            for worker in self._streaming_workers:
                if not worker.done():
                    worker.cancel()
            
            # Wait for workers to complete
            if self._streaming_workers:
                await asyncio.gather(*self._streaming_workers, return_exceptions=True)
            
            # Close Redis client
            if self._redis_client:
                await self._redis_client.close()
            
            self._streaming_workers.clear()
            
            self.logger.info("Real-Time Log Streaming Engine stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping streaming engine: {e}")
            return False
    
    async def _handle_websocket_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        # WebSocket functionality not available in this environment
        self.logger.warning("WebSocket functionality not available")
        return
    
    async def _handle_client_message(self, connection_id: str, message: str):
        """Handle message from client"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                await self._handle_subscribe_message(connection_id, data)
            elif message_type == "unsubscribe":
                await self._handle_unsubscribe_message(connection_id, data)
            elif message_type == "filter":
                await self._handle_filter_message(connection_id, data)
            elif message_type == "ping":
                await self._handle_ping_message(connection_id, data)
            else:
                self.logger.warning(f"Unknown message type from {connection_id}: {message_type}")
                
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON from connection {connection_id}")
        except Exception as e:
            self.logger.error(f"Error handling client message from {connection_id}: {e}")
    
    async def _handle_subscribe_message(self, connection_id: str, data: Dict[str, Any]):
        """Handle channel subscription"""
        try:
            channels = data.get("channels", [])
            connection = self._connections.get(connection_id)
            
            if not connection:
                return
            
            for channel_name in channels:
                try:
                    channel = StreamingChannel(channel_name)
                    connection.subscribed_channels.add(channel)
                    self._channel_subscribers[channel].add(connection_id)
                    
                    await self._send_message_to_connection(
                        connection_id,
                        {
                            "type": "subscribed",
                            "channel": channel.value,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    )
                    
                except ValueError:
                    self.logger.warning(f"Invalid channel name: {channel_name}")
            
        except Exception as e:
            self.logger.error(f"Error handling subscribe message: {e}")
    
    async def _handle_unsubscribe_message(self, connection_id: str, data: Dict[str, Any]):
        """Handle channel unsubscription"""
        try:
            channels = data.get("channels", [])
            connection = self._connections.get(connection_id)
            
            if not connection:
                return
            
            for channel_name in channels:
                try:
                    channel = StreamingChannel(channel_name)
                    connection.subscribed_channels.discard(channel)
                    self._channel_subscribers[channel].discard(connection_id)
                    
                    await self._send_message_to_connection(
                        connection_id,
                        {
                            "type": "unsubscribed",
                            "channel": channel.value,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    )
                    
                except ValueError:
                    self.logger.warning(f"Invalid channel name: {channel_name}")
            
        except Exception as e:
            self.logger.error(f"Error handling unsubscribe message: {e}")
    
    async def _handle_filter_message(self, connection_id: str, data: Dict[str, Any]):
        """Handle creator filter setup"""
        try:
            creator_ids = data.get("creator_ids", [])
            connection = self._connections.get(connection_id)
            
            if not connection:
                return
            
            connection.creator_filters = set(creator_ids)
            
            await self._send_message_to_connection(
                connection_id,
                {
                    "type": "filters_updated",
                    "creator_filters": list(connection.creator_filters),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error handling filter message: {e}")
    
    async def _handle_ping_message(self, connection_id: str, data: Dict[str, Any]):
        """Handle ping message"""
        try:
            await self._send_message_to_connection(
                connection_id,
                {
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error handling ping message: {e}")
    
    async def stream_log_event(self, channel: StreamingChannel, event_data: Dict[str, Any]) -> bool:
        """
        Stream a log event to subscribers
        
        Args:
            channel: Streaming channel
            event_data: Event data to stream
            
        Returns:
            True if streamed successfully, False otherwise
        """
        try:
            if not self._running:
                return False
            
            # Process message through channel processor
            processor = self._channel_processors.get(channel)
            if processor:
                processed_data = await processor(event_data)
            else:
                processed_data = event_data
            
            # Add to buffer
            buffer = self._stream_buffers.get(channel)
            if buffer is not None:
                buffer.append({
                    "channel": channel.value,
                    "data": processed_data,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message_id": str(uuid.uuid4())
                })
                
                # Update metrics
                self._streaming_metrics["messages_streamed"] += 1
                self._streaming_metrics["buffer_sizes"][channel.value] = len(buffer)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error streaming log event to {channel.value}: {e}")
            self._streaming_metrics["errors_count"] += 1
            return False
    
    async def _send_message_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific connection"""
        try:
            connection = self._connections.get(connection_id)
            if not connection:
                return
            
            message_json = json.dumps(message)
            await connection.websocket.send(message_json)
            connection.last_activity = datetime.now(timezone.utc)
            
        except Exception as e:
            self.logger.error(f"Error sending message to connection {connection_id}: {e}")
            await self._cleanup_connection(connection_id)
    
    async def _broadcast_to_channel(self, channel: StreamingChannel, message: Dict[str, Any]):
        """Broadcast message to all subscribers of a channel"""
        try:
            subscribers = self._channel_subscribers.get(channel, set())
            
            for connection_id in subscribers.copy():  # Copy to avoid modification during iteration
                connection = self._connections.get(connection_id)
                if not connection:
                    continue
                
                # Apply creator filters if set
                if connection.creator_filters:
                    creator_id = message.get("data", {}).get("creator_id")
                    if creator_id and creator_id not in connection.creator_filters:
                        continue
                
                await self._send_message_to_connection(connection_id, message)
            
        except Exception as e:
            self.logger.error(f"Error broadcasting to channel {channel.value}: {e}")
    
    async def _cleanup_connection(self, connection_id: str):
        """Clean up connection and remove from all subscriptions"""
        try:
            connection = self._connections.get(connection_id)
            if not connection:
                return
            
            # Remove from all channel subscriptions
            for channel in connection.subscribed_channels:
                self._channel_subscribers[channel].discard(connection_id)
            
            # Remove from connections
            del self._connections[connection_id]
            
            # Update metrics
            self._streaming_metrics["active_connections"] -= 1
            self._streaming_metrics["connection_types"][connection.connection_type] -= 1
            
            self.logger.info(f"Connection cleaned up: {connection_id}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up connection {connection_id}: {e}")
    
    async def _close_all_connections(self):
        """Close all active connections"""
        try:
            for connection_id in list(self._connections.keys()):
                await self._cleanup_connection(connection_id)
                
        except Exception as e:
            self.logger.error(f"Error closing all connections: {e}")
    
    # Worker methods
    async def _buffer_flusher_worker(self):
        """Worker to flush buffered messages to subscribers"""
        self.logger.info("Started buffer flusher worker")
        
        flush_interval = self._streaming_config["buffering"]["flush_interval_seconds"]
        
        while self._running:
            try:
                for channel, buffer in self._stream_buffers.items():
                    if buffer:
                        # Flush messages from buffer
                        messages_to_send = []
                        while buffer and len(messages_to_send) < self._streaming_config["buffering"]["batch_size"]:
                            messages_to_send.append(buffer.popleft())
                        
                        # Broadcast messages
                        for message in messages_to_send:
                            await self._broadcast_to_channel(channel, message)
                
                await asyncio.sleep(flush_interval)
                
            except Exception as e:
                self.logger.error(f"Buffer flusher worker error: {e}")
    
    async def _connection_monitor_worker(self):
        """Worker to monitor connection health"""
        self.logger.info("Started connection monitor worker")
        
        while self._running:
            try:
                current_time = datetime.now(timezone.utc)
                timeout_threshold = self._streaming_config["performance"]["connection_timeout_seconds"]
                
                # Check for inactive connections
                inactive_connections = []
                for connection_id, connection in self._connections.items():
                    if (current_time - connection.last_activity).total_seconds() > timeout_threshold:
                        inactive_connections.append(connection_id)
                
                # Clean up inactive connections
                for connection_id in inactive_connections:
                    await self._cleanup_connection(connection_id)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Connection monitor worker error: {e}")
    
    async def _performance_monitor_worker(self):
        """Worker to monitor streaming performance"""
        self.logger.info("Started performance monitor worker")
        
        last_message_count = 0
        last_time = time.time()
        
        while self._running:
            try:
                current_time = time.time()
                current_message_count = self._streaming_metrics["messages_streamed"]
                
                # Calculate throughput
                time_diff = current_time - last_time
                if time_diff > 0:
                    throughput = (current_message_count - last_message_count) / time_diff
                    self._streaming_metrics["throughput_msg_per_sec"] = throughput
                
                last_message_count = current_message_count
                last_time = current_time
                
                # Update active channels count
                self._streaming_metrics["channels_active"] = sum(
                    1 for subscribers in self._channel_subscribers.values() if subscribers
                )
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                self.logger.error(f"Performance monitor worker error: {e}")
    
    async def _redis_subscriber_worker(self):
        """Worker to handle Redis pub/sub for distributed streaming"""
        if not self._redis_client:
            return
        
        self.logger.info("Started Redis subscriber worker")
        
        try:
            pubsub = self._redis_client.pubsub()
            
            # Subscribe to all streaming channels
            for channel in StreamingChannel:
                redis_channel = f"{self._streaming_config['redis']['channel_prefix']}:{channel.value}"
                await pubsub.subscribe(redis_channel)
            
            while self._running:
                try:
                    message = await pubsub.get_message(timeout=1.0)
                    if message and message['type'] == 'message':
                        # Process Redis message
                        channel_name = message['channel'].decode().split(':')[-1]
                        data = json.loads(message['data'])
                        
                        try:
                            channel = StreamingChannel(channel_name)
                            await self._broadcast_to_channel(channel, data)
                        except ValueError:
                            self.logger.warning(f"Unknown channel from Redis: {channel_name}")
                            
                except asyncio.TimeoutError:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Redis subscriber worker error: {e}")
        finally:
            if pubsub:
                await pubsub.unsubscribe()
                await pubsub.close()
    
    async def _heartbeat_worker(self):
        """Worker to send heartbeat messages to connections"""
        self.logger.info("Started heartbeat worker")
        
        heartbeat_interval = self._streaming_config["performance"]["heartbeat_interval_seconds"]
        
        while self._running:
            try:
                heartbeat_message = {
                    "type": "heartbeat",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "active_connections": self._streaming_metrics["active_connections"],
                    "throughput": self._streaming_metrics["throughput_msg_per_sec"]
                }
                
                # Send heartbeat to all connections
                for connection_id in list(self._connections.keys()):
                    await self._send_message_to_connection(connection_id, heartbeat_message)
                
                await asyncio.sleep(heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Heartbeat worker error: {e}")
    
    # Message processors for each channel
    async def _process_creator_activity_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process creator activity message"""
        return {
            "creator_id": data.get("creator_id"),
            "activity_type": data.get("activity_type"),
            "metrics": data.get("metrics", {}),
            "timestamp": data.get("timestamp")
        }
    
    async def _process_content_processing_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process content processing message"""
        return {
            "content_id": data.get("content_id"),
            "creator_id": data.get("creator_id"),
            "processing_stage": data.get("processing_stage"),
            "format_type": data.get("format_type"),
            "metrics": data.get("metrics", {}),
            "timestamp": data.get("timestamp")
        }
    
    async def _process_monetization_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process monetization message"""
        return {
            "creator_id": data.get("creator_id"),
            "revenue_event": data.get("revenue_event"),
            "amount": data.get("amount"),
            "currency": data.get("currency", "USD"),
            "timestamp": data.get("timestamp")
        }
    
    async def _process_collaboration_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process collaboration message"""
        return {
            "collaboration_id": data.get("collaboration_id"),
            "participants": data.get("participants", []),
            "collaboration_type": data.get("collaboration_type"),
            "status": data.get("status"),
            "timestamp": data.get("timestamp")
        }
    
    async def _process_performance_metrics_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process performance metrics message"""
        return {
            "metric_type": data.get("metric_type"),
            "value": data.get("value"),
            "creator_id": data.get("creator_id"),
            "service": data.get("service"),
            "timestamp": data.get("timestamp")
        }
    
    async def _process_anomaly_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process anomaly message"""
        return {
            "anomaly_type": data.get("anomaly_type"),
            "severity": data.get("severity", "medium"),
            "creator_id": data.get("creator_id"),
            "description": data.get("description"),
            "confidence": data.get("confidence", 0.0),
            "timestamp": data.get("timestamp")
        }
    
    async def _process_analytics_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process real-time analytics message"""
        return {
            "analytics_type": data.get("analytics_type"),
            "creator_id": data.get("creator_id"),
            "metrics": data.get("metrics", {}),
            "insights": data.get("insights", []),
            "timestamp": data.get("timestamp")
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of streaming engine"""
        return {
            "status": "healthy" if self._running else "stopped",
            "initialized": self._initialized,
            "running": self._running,
            "worker_count": len(self._streaming_workers),
            "active_connections": self._streaming_metrics["active_connections"],
            "channels_active": self._streaming_metrics["channels_active"],
            "throughput_msg_per_sec": self._streaming_metrics["throughput_msg_per_sec"],
            "metrics": self._streaming_metrics
        }
    
    def get_streaming_statistics(self) -> Dict[str, Any]:
        """Get detailed streaming statistics"""
        return {
            "connections": {
                "total_active": self._streaming_metrics["active_connections"],
                "by_type": dict(self._streaming_metrics["connection_types"]),
                "channels_active": self._streaming_metrics["channels_active"]
            },
            "performance": {
                "messages_streamed": self._streaming_metrics["messages_streamed"],
                "throughput_msg_per_sec": self._streaming_metrics["throughput_msg_per_sec"],
                "latency_ms": self._streaming_metrics["latency_ms"],
                "errors_count": self._streaming_metrics["errors_count"]
            },
            "buffers": {
                "buffer_sizes": self._streaming_metrics["buffer_sizes"],
                "total_buffered": sum(len(buffer) for buffer in self._stream_buffers.values())
            },
            "channels": {
                channel.value: {
                    "subscribers": len(self._channel_subscribers[channel]),
                    "buffer_size": len(self._stream_buffers[channel])
                }
                for channel in StreamingChannel
            }
        }