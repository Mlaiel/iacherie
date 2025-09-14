"""Data Flow Manager for IA Influencer Agent Platform
=================================================

Consolidated data flow management system combining buffer, queue, and connector
functionality for enterprise-grade data orchestration and pipeline management.

CONSOLIDATED ARCHITECTURE:
- DataFlowManager: Main orchestrator for data flow operations
- StreamBuffer: Legacy compatibility for buffering
- StreamQueue: Legacy compatibility for queuing
- StreamConnector: Legacy compatibility for connections

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  LEGAL WARNING ⚠️
Unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violations will be prosecuted under German and international copyright law.

Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import gzip
import threading
from collections import deque, defaultdict
from queue import Queue, PriorityQueue, Empty, Full
import heapq
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class BufferType(str, Enum):
    """Buffer storage types"""
    MEMORY = "memory"
    DISK = "disk"
    REDIS = "redis"
    HYBRID = "hybrid"


class CompressionType(str, Enum):
    """Data compression types"""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    SNAPPY = "snappy"


class EvictionPolicy(str, Enum):
    """Buffer eviction policies"""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"
    SIZE_BASED = "size_based"


class QueuePriority(int, Enum):
    """Queue priority levels"""
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


class MessageStatus(str, Enum):
    """Message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class ConnectorType(str, Enum):
    """Connector types"""
    HTTP = "http"
    WEBSOCKET = "websocket"
    KAFKA = "kafka"
    REDIS = "redis"
    DATABASE = "database"
    FILE = "file"
    S3 = "s3"
    FTP = "ftp"
    CUSTOM = "custom"


class ConnectionStatus(str, Enum):
    """Connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class BufferConfig:
    """Buffer configuration"""
    buffer_id: str
    buffer_type: BufferType = BufferType.MEMORY
    max_size_mb: int = 100
    max_items: int = 10000
    ttl_seconds: int = 3600
    compression: CompressionType = CompressionType.NONE
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    persistence_enabled: bool = False
    persistence_path: str = "/tmp/buffer"
    batch_size: int = 100


@dataclass
class BufferItem:
    """Buffer item data structure"""
    item_id: str
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    size_bytes: int = 0
    compressed: bool = False


@dataclass
class QueueMessage:
    """Queue message data structure"""
    message_id: str
    data: Any
    priority: QueuePriority = QueuePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None


@dataclass
class ConnectionConfig:
    """Connection configuration"""
    connection_id: str
    connector_type: ConnectorType
    endpoint: str
    credentials: Dict[str, str] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30
    retry_attempts: int = 3
    heartbeat_interval: int = 60
    auto_reconnect: bool = True


@dataclass
class Connection:
    """Connection data structure"""
    connection_id: str
    config: ConnectionConfig
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    last_heartbeat: Optional[datetime] = None
    connected_at: Optional[datetime] = None
    error_count: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    messages_sent: int = 0
    messages_received: int = 0


class BaseConnector(ABC):
    """Base connector interface"""
    
    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> bool:
        """Establish connection"""
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection"""
        pass
        
    @abstractmethod
    async def send(self, data: Any) -> bool:
        """Send data"""
        pass
        
    @abstractmethod
    async def receive(self) -> Optional[Any]:
        """Receive data"""
        pass
        
    @abstractmethod
    async def health_check(self) -> bool:
        """Check connection health"""
        pass


class DataFlowManager:
    """
    Consolidated data flow management system combining buffer, queue, and connector
    functionality for enterprise-grade data orchestration and pipeline management.
    
    Features:
    - High-performance buffering with multiple storage backends
    - Priority-based message queuing with retry mechanisms
    - Universal connector framework for various data sources/sinks
    - Intelligent data flow optimization and load balancing
    - Real-time monitoring and metrics collection
    """
    
    def __init__(
        self,
        max_buffers -> None: int = 50,
        max_queues -> None: int = 20,
        max_connections -> None: int = 100,
        enable_monitoring -> None: bool = True
    ) -> None:
        # Configuration
        self.max_buffers = max_buffers
        self.max_queues = max_queues
        self.max_connections = max_connections
        self.enable_monitoring = enable_monitoring
        
        # Buffer management
        self.buffers: Dict[str, 'StreamBuffer'] = {}
        self.buffer_stats: Dict[str, Dict[str, Any]] = {}
        
        # Queue management
        self.queues: Dict[str, 'StreamQueue'] = {}
        self.message_processors: Dict[str, asyncio.Task] = {}
        self.dead_letter_queues: Dict[str, 'StreamQueue'] = {}
        
        # Connector management
        self.connectors: Dict[str, BaseConnector] = {}
        self.connections: Dict[str, Connection] = {}
        self.connector_registry: Dict[ConnectorType, type] = {}
        
        # Data pipeline management
        self.pipelines: Dict[str, Dict[str, Any]] = {}
        self.pipeline_tasks: Dict[str, asyncio.Task] = {}
        
        # Performance metrics
        self.flow_metrics = {
            "total_data_processed": 0,
            "average_processing_time": 0.0,
            "peak_processing_time": 0.0,
            "buffer_hit_rate": 0.0,
            "queue_throughput": 0.0,
            "connection_uptime": 0.0
        }
        
        # Background tasks
        self.buffer_maintenance_task: Optional[asyncio.Task] = None
        self.queue_monitor_task: Optional[asyncio.Task] = None
        self.connection_monitor_task: Optional[asyncio.Task] = None
        self.flow_optimizer_task: Optional[asyncio.Task] = None
        
        # State management
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()
        
        # Register default connectors
        self._register_default_connectors()
        
        logger.info("DataFlowManager initialized")
        
    async def initialize(self) -> None:
        """Initialize the data flow manager"""
        try:
            async with self._lock:
                if self._running:
                    return
                    
                # Start background tasks
                if self.enable_monitoring:
                    self.buffer_maintenance_task = asyncio.create_task(self._buffer_maintenance())
                    self.queue_monitor_task = asyncio.create_task(self._queue_monitor())
                    self.connection_monitor_task = asyncio.create_task(self._connection_monitor())
                    self.flow_optimizer_task = asyncio.create_task(self._flow_optimizer())
                    
                self._running = True
                logger.info("DataFlowManager initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize DataFlowManager: {e}")
            raise
            
    async def create_buffer(
        self,
        buffer_id: str,
        config: Optional[BufferConfig] = None
    ) -> bool:
        """
        Create a new buffer
        
        Args:
            buffer_id: Unique buffer identifier
            config: Optional buffer configuration
            
        Returns:
            Success status
        """
        try:
            if len(self.buffers) >= self.max_buffers:
                logger.error("Maximum buffers limit reached")
                return False
                
            if buffer_id in self.buffers:
                logger.warning(f"Buffer {buffer_id} already exists")
                return False
                
            if config is None:
                config = BufferConfig(buffer_id=buffer_id)
                
            buffer = StreamBuffer(config)
            await buffer.initialize()
            
            async with self._lock:
                self.buffers[buffer_id] = buffer
                self.buffer_stats[buffer_id] = {
                    "created_at": datetime.now(timezone.utc),
                    "hits": 0,
                    "misses": 0,
                    "evictions": 0,
                    "size_bytes": 0
                }
                
            logger.info(f"Buffer {buffer_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create buffer {buffer_id}: {e}")
            return False
            
    async def create_queue(
        self,
        queue_id: str,
        max_size: int = 10000,
        enable_dead_letter: bool = True
    ) -> bool:
        """
        Create a new message queue
        
        Args:
            queue_id: Unique queue identifier
            max_size: Maximum queue size
            enable_dead_letter: Enable dead letter queue
            
        Returns:
            Success status
        """
        try:
            if len(self.queues) >= self.max_queues:
                logger.error("Maximum queues limit reached")
                return False
                
            if queue_id in self.queues:
                logger.warning(f"Queue {queue_id} already exists")
                return False
                
            queue = StreamQueue(queue_id, max_size)
            await queue.initialize()
            
            async with self._lock:
                self.queues[queue_id] = queue
                
                # Create dead letter queue if enabled
                if enable_dead_letter:
                    dlq_id = f"{queue_id}_dlq"
                    dlq = StreamQueue(dlq_id, max_size // 10)
                    await dlq.initialize()
                    self.dead_letter_queues[queue_id] = dlq
                    
                # Start message processor
                processor_task = asyncio.create_task(self._message_processor(queue_id))
                self.message_processors[queue_id] = processor_task
                
            logger.info(f"Queue {queue_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create queue {queue_id}: {e}")
            return False
            
    async def create_connection(
        self,
        connection_id: str,
        connector_type: ConnectorType,
        endpoint: str,
        credentials: Optional[Dict[str, str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a new connection
        
        Args:
            connection_id: Unique connection identifier
            connector_type: Type of connector
            endpoint: Connection endpoint
            credentials: Optional credentials
            config: Optional connection configuration
            
        Returns:
            Success status
        """
        try:
            if len(self.connections) >= self.max_connections:
                logger.error("Maximum connections limit reached")
                return False
                
            if connection_id in self.connections:
                logger.warning(f"Connection {connection_id} already exists")
                return False
                
            # Create connection config
            connection_config = ConnectionConfig(
                connection_id=connection_id,
                connector_type=connector_type,
                endpoint=endpoint,
                credentials=credentials or {},
                config=config or {}
            )
            
            # Create connector instance
            if connector_type not in self.connector_registry:
                logger.error(f"Connector type {connector_type} not registered")
                return False
                
            connector_class = self.connector_registry[connector_type]
            connector = connector_class()
            
            # Establish connection
            if await connector.connect(connection_config):
                connection = Connection(
                    connection_id=connection_id,
                    config=connection_config,
                    status=ConnectionStatus.CONNECTED,
                    connected_at=datetime.now(timezone.utc)
                )
                
                async with self._lock:
                    self.connectors[connection_id] = connector
                    self.connections[connection_id] = connection
                    
                logger.info(f"Connection {connection_id} created successfully")
                return True
            else:
                logger.error(f"Failed to establish connection {connection_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create connection {connection_id}: {e}")
            return False
            
    async def put_data(
        self,
        buffer_id: str,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Put data into buffer
        
        Args:
            buffer_id: Buffer identifier
            data: Data to store
            metadata: Optional metadata
            
        Returns:
            Item ID if successful, None otherwise
        """
        try:
            if buffer_id not in self.buffers:
                logger.error(f"Buffer {buffer_id} not found")
                return None
                
            buffer = self.buffers[buffer_id]
            item_id = await buffer.put(data, metadata)
            
            if item_id and self.enable_monitoring:
                self.buffer_stats[buffer_id]["size_bytes"] = await buffer.get_size_bytes()
                
            return item_id
            
        except Exception as e:
            logger.error(f"Failed to put data in buffer {buffer_id}: {e}")
            return None
            
    async def get_data(
        self,
        buffer_id: str,
        item_id: str
    ) -> Optional[Any]:
        """
        Get data from buffer
        
        Args:
            buffer_id: Buffer identifier
            item_id: Item identifier
            
        Returns:
            Data if found, None otherwise
        """
        try:
            if buffer_id not in self.buffers:
                logger.error(f"Buffer {buffer_id} not found")
                return None
                
            buffer = self.buffers[buffer_id]
            data = await buffer.get(item_id)
            
            if self.enable_monitoring:
                if data is not None:
                    self.buffer_stats[buffer_id]["hits"] += 1
                else:
                    self.buffer_stats[buffer_id]["misses"] += 1
                    
            return data
            
        except Exception as e:
            logger.error(f"Failed to get data from buffer {buffer_id}: {e}")
            return None
            
    async def enqueue_message(
        self,
        queue_id: str,
        data: Any,
        priority: QueuePriority = QueuePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Enqueue a message
        
        Args:
            queue_id: Queue identifier
            data: Message data
            priority: Message priority
            metadata: Optional metadata
            
        Returns:
            Message ID if successful, None otherwise
        """
        try:
            if queue_id not in self.queues:
                logger.error(f"Queue {queue_id} not found")
                return None
                
            queue = self.queues[queue_id]
            message_id = await queue.enqueue(data, priority, metadata)
            
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to enqueue message in queue {queue_id}: {e}")
            return None
            
    async def send_data(
        self,
        connection_id: str,
        data: Any
    ) -> bool:
        """
        Send data through connection
        
        Args:
            connection_id: Connection identifier
            data: Data to send
            
        Returns:
            Success status
        """
        try:
            if connection_id not in self.connectors:
                logger.error(f"Connector {connection_id} not found")
                return False
                
            connector = self.connectors[connection_id]
            success = await connector.send(data)
            
            if success and connection_id in self.connections:
                connection = self.connections[connection_id]
                connection.messages_sent += 1
                connection.bytes_sent += len(str(data).encode('utf-8'))
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to send data through connection {connection_id}: {e}")
            return False
            
    async def receive_data(
        self,
        connection_id: str
    ) -> Optional[Any]:
        """
        Receive data from connection
        
        Args:
            connection_id: Connection identifier
            
        Returns:
            Received data or None
        """
        try:
            if connection_id not in self.connectors:
                logger.error(f"Connector {connection_id} not found")
                return None
                
            connector = self.connectors[connection_id]
            data = await connector.receive()
            
            if data and connection_id in self.connections:
                connection = self.connections[connection_id]
                connection.messages_received += 1
                connection.bytes_received += len(str(data).encode('utf-8'))
                
            return data
            
        except Exception as e:
            logger.error(f"Failed to receive data from connection {connection_id}: {e}")
            return None
            
    async def create_pipeline(
        self,
        pipeline_id: str,
        source_connection_id: str,
        target_buffer_id: str,
        processors: Optional[List[Callable]] = None
    ) -> bool:
        """
        Create a data pipeline
        
        Args:
            pipeline_id: Pipeline identifier
            source_connection_id: Source connection ID
            target_buffer_id: Target buffer ID
            processors: Optional data processors
            
        Returns:
            Success status
        """
        try:
            if pipeline_id in self.pipelines:
                logger.warning(f"Pipeline {pipeline_id} already exists")
                return False
                
            if source_connection_id not in self.connectors:
                logger.error(f"Source connection {source_connection_id} not found")
                return False
                
            if target_buffer_id not in self.buffers:
                logger.error(f"Target buffer {target_buffer_id} not found")
                return False
                
            pipeline_config = {
                "pipeline_id": pipeline_id,
                "source_connection_id": source_connection_id,
                "target_buffer_id": target_buffer_id,
                "processors": processors or [],
                "created_at": datetime.now(timezone.utc),
                "messages_processed": 0
            }
            
            async with self._lock:
                self.pipelines[pipeline_id] = pipeline_config
                
                # Start pipeline task
                pipeline_task = asyncio.create_task(self._pipeline_worker(pipeline_id))
                self.pipeline_tasks[pipeline_id] = pipeline_task
                
            logger.info(f"Pipeline {pipeline_id} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create pipeline {pipeline_id}: {e}")
            return False
            
    async def get_flow_metrics(self) -> Dict[str, Any]:
        """Get data flow metrics"""
        try:
            # Calculate buffer hit rate
            total_hits = sum(stats["hits"] for stats in self.buffer_stats.values())
            total_requests = sum(stats["hits"] + stats["misses"] for stats in self.buffer_stats.values())
            buffer_hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
            
            # Calculate connection uptime
            active_connections = sum(1 for conn in self.connections.values() if conn.status == ConnectionStatus.CONNECTED)
            connection_uptime = (active_connections / len(self.connections) * 100) if self.connections else 100
            
            # Calculate queue throughput
            total_messages = sum(queue.messages_processed for queue in self.queues.values())
            queue_throughput = total_messages / max(1, (datetime.now(timezone.utc) - self._start_time).total_seconds())
            
            metrics = {
                "total_buffers": len(self.buffers),
                "total_queues": len(self.queues),
                "total_connections": len(self.connections),
                "active_connections": active_connections,
                "total_pipelines": len(self.pipelines),
                "buffer_hit_rate": buffer_hit_rate,
                "connection_uptime": connection_uptime,
                "queue_throughput": queue_throughput,
                "buffer_stats": dict(self.buffer_stats),
                "flow_metrics": dict(self.flow_metrics)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get flow metrics: {e}")
            return {}
            
    def _register_default_connectors(self) -> None:
        """Register default connector types"""
        try:
            # Register built-in connector types
            self.connector_registry[ConnectorType.HTTP] = HTTPConnector
            self.connector_registry[ConnectorType.WEBSOCKET] = WebSocketConnector
            self.connector_registry[ConnectorType.KAFKA] = KafkaConnector
            self.connector_registry[ConnectorType.REDIS] = RedisConnector
            self.connector_registry[ConnectorType.FILE] = FileConnector
            self.connector_registry[ConnectorType.CUSTOM] = CustomConnector
            
        except Exception as e:
            logger.error(f"Failed to register default connectors: {e}")
            
    async def _message_processor(self, queue_id: str) -> None:
        """Message processor for queue"""
        logger.info(f"Message processor started for queue {queue_id}")
        
        while not self._shutdown_event.is_set():
            try:
                if queue_id not in self.queues:
                    break
                    
                queue = self.queues[queue_id]
                message = await queue.dequeue()
                
                if message:
                    # Process message
                    success = await self._process_message(message)
                    
                    if success:
                        message.status = MessageStatus.PROCESSED
                        message.processed_at = datetime.now(timezone.utc)
                    else:
                        message.status = MessageStatus.FAILED
                        message.retry_count += 1
                        
                        # Move to dead letter queue if max retries exceeded
                        if message.retry_count >= message.max_retries:
                            if queue_id in self.dead_letter_queues:
                                dlq = self.dead_letter_queues[queue_id]
                                await dlq.enqueue(message.data, QueuePriority.LOW, message.metadata)
                                message.status = MessageStatus.DEAD_LETTER
                        else:
                            # Re-queue for retry
                            await queue.enqueue(message.data, message.priority, message.metadata)
                else:
                    await asyncio.sleep(0.1)  # No messages, short delay
                    
            except Exception as e:
                logger.error(f"Message processor error for queue {queue_id}: {e}")
                await asyncio.sleep(1)  # Error backoff
                
        logger.info(f"Message processor stopped for queue {queue_id}")
        
    async def _process_message(self, message: QueueMessage) -> bool:
        """Process a single message"""
        try:
            start_time = time.time()
            
            # Simulate message processing
            await asyncio.sleep(0.01)  # Simulate processing time
            
            processing_time = time.time() - start_time
            
            # Update metrics
            self.flow_metrics["total_data_processed"] += 1
            
            total_processed = self.flow_metrics["total_data_processed"]
            avg_time = self.flow_metrics["average_processing_time"]
            self.flow_metrics["average_processing_time"] = (avg_time * (total_processed - 1) + processing_time) / total_processed
            self.flow_metrics["peak_processing_time"] = max(self.flow_metrics["peak_processing_time"], processing_time)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to process message {message.message_id}: {e}")
            return False
            
    async def _pipeline_worker(self, pipeline_id: str) -> None:
        """Pipeline worker for data flow"""
        logger.info(f"Pipeline worker started for {pipeline_id}")
        
        while not self._shutdown_event.is_set():
            try:
                if pipeline_id not in self.pipelines:
                    break
                    
                pipeline = self.pipelines[pipeline_id]
                source_connection_id = pipeline["source_connection_id"]
                target_buffer_id = pipeline["target_buffer_id"]
                processors = pipeline["processors"]
                
                # Receive data from source
                data = await self.receive_data(source_connection_id)
                
                if data:
                    # Apply processors
                    processed_data = data
                    for processor in processors:
                        try:
                            if asyncio.iscoroutinefunction(processor):
                                processed_data = await processor(processed_data)
                            else:
                                processed_data = processor(processed_data)
                        except Exception as e:
                            logger.error(f"Processor error in pipeline {pipeline_id}: {e}")
                            break
                            
                    # Store in target buffer
                    await self.put_data(target_buffer_id, processed_data)
                    
                    pipeline["messages_processed"] += 1
                else:
                    await asyncio.sleep(0.1)  # No data, short delay
                    
            except Exception as e:
                logger.error(f"Pipeline worker error for {pipeline_id}: {e}")
                await asyncio.sleep(1)  # Error backoff
                
        logger.info(f"Pipeline worker stopped for {pipeline_id}")
        
    async def _buffer_maintenance(self) -> None:
        """Background buffer maintenance task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60)  # Maintenance every minute
                
                for buffer_id, buffer in self.buffers.items():
                    await buffer.maintenance()
                    
                    # Update buffer stats
                    if self.enable_monitoring:
                        stats = self.buffer_stats[buffer_id]
                        stats["size_bytes"] = await buffer.get_size_bytes()
                        stats["evictions"] = buffer.eviction_count
                        
            except Exception as e:
                logger.error(f"Buffer maintenance error: {e}")
                
    async def _queue_monitor(self) -> None:
        """Background queue monitoring task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
                for queue_id, queue in self.queues.items():
                    queue_size = await queue.size()
                    
                    # Alert on high queue size
                    if queue_size > queue.max_size * 0.8:
                        logger.warning(f"Queue {queue_id} is {queue_size/queue.max_size*100:.1f}% full")
                        
            except Exception as e:
                logger.error(f"Queue monitor error: {e}")
                
    async def _connection_monitor(self) -> None:
        """Background connection monitoring task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
                for connection_id, connector in self.connectors.items():
                    health = await connector.health_check()
                    
                    if connection_id in self.connections:
                        connection = self.connections[connection_id]
                        
                        if health:
                            connection.status = ConnectionStatus.CONNECTED
                            connection.last_heartbeat = datetime.now(timezone.utc)
                        else:
                            connection.status = ConnectionStatus.ERROR
                            connection.error_count += 1
                            
                            # Try to reconnect if auto-reconnect is enabled
                            if connection.config.auto_reconnect:
                                logger.info(f"Attempting to reconnect {connection_id}")
                                await connector.connect(connection.config)
                                
            except Exception as e:
                logger.error(f"Connection monitor error: {e}")
                
    async def _flow_optimizer(self) -> None:
        """Background flow optimization task"""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # Optimize every 5 minutes
                
                # Optimize buffer sizes based on usage patterns
                for buffer_id, buffer in self.buffers.items():
                    stats = self.buffer_stats[buffer_id]
                    hit_rate = stats["hits"] / max(1, stats["hits"] + stats["misses"])
                    
                    # Adjust buffer size based on hit rate
                    if hit_rate > 0.9 and buffer.config.max_items < 50000:
                        # High hit rate, increase buffer size
                        buffer.config.max_items = min(50000, int(buffer.config.max_items * 1.2))
                        logger.info(f"Increased buffer {buffer_id} size to {buffer.config.max_items}")
                        
                    elif hit_rate < 0.5 and buffer.config.max_items > 1000:
                        # Low hit rate, decrease buffer size
                        buffer.config.max_items = max(1000, int(buffer.config.max_items * 0.8))
                        logger.info(f"Decreased buffer {buffer_id} size to {buffer.config.max_items}")
                        
            except Exception as e:
                logger.error(f"Flow optimizer error: {e}")
                
    async def shutdown(self) -> None:
        """Gracefully shutdown the data flow manager"""
        try:
            logger.info("Shutting down DataFlowManager...")
            
            self._shutdown_event.set()
            
            # Cancel background tasks
            tasks_to_cancel = [
                self.buffer_maintenance_task,
                self.queue_monitor_task,
                self.connection_monitor_task,
                self.flow_optimizer_task
            ]
            
            for task in tasks_to_cancel:
                if task:
                    task.cancel()
                    
            # Cancel pipeline tasks
            for task in self.pipeline_tasks.values():
                task.cancel()
                
            # Cancel message processors
            for task in self.message_processors.values():
                task.cancel()
                
            # Close all connections
            for connector in self.connectors.values():
                await connector.disconnect()
                
            # Shutdown buffers
            for buffer in self.buffers.values():
                await buffer.shutdown()
                
            # Shutdown queues
            for queue in self.queues.values():
                await queue.shutdown()
                
            self._running = False
            logger.info("DataFlowManager shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Buffer implementation
class StreamBuffer:
    """High-performance streaming buffer with multiple storage backends"""
    
    def __init__(self, config -> None: BufferConfig) -> None:
        self.config = config
        self.items: Dict[str, BufferItem] = {}
        self.access_order: deque = deque()  # For LRU
        self.access_frequency: Dict[str, int] = defaultdict(int)  # For LFU
        self.size_bytes = 0
        self.eviction_count = 0
        self._lock = asyncio.Lock()
        
    async def initialize(self) -> None:
        """Initialize the buffer"""
        if self.config.persistence_enabled:
            await self._load_from_disk()
            
    async def put(self, data: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Put data into buffer"""
        async with self._lock:
            item_id = str(uuid.uuid4())
            
            # Compress data if configured
            if self.config.compression != CompressionType.NONE:
                data = await self._compress_data(data)
                compressed = True
            else:
                compressed = False
                
            # Calculate size
            size_bytes = len(pickle.dumps(data))
            
            # Check if eviction is needed
            if len(self.items) >= self.config.max_items or (self.size_bytes + size_bytes) > (self.config.max_size_mb * 1024 * 1024):
                await self._evict_items()
                
            item = BufferItem(
                item_id=item_id,
                data=data,
                metadata=metadata or {},
                size_bytes=size_bytes,
                compressed=compressed
            )
            
            self.items[item_id] = item
            self.size_bytes += size_bytes
            
            # Update access tracking
            self.access_order.append(item_id)
            
            return item_id
            
    async def get(self, item_id: str) -> Optional[Any]:
        """Get data from buffer"""
        async with self._lock:
            if item_id not in self.items:
                return None
                
            item = self.items[item_id]
            
            # Update access tracking
            item.access_count += 1
            item.last_accessed = datetime.now(timezone.utc)
            self.access_frequency[item_id] += 1
            
            # Move to end for LRU
            if item_id in self.access_order:
                self.access_order.remove(item_id)
            self.access_order.append(item_id)
            
            # Decompress if needed
            data = item.data
            if item.compressed:
                data = await self._decompress_data(data)
                
            return data
            
    async def remove(self, item_id: str) -> bool:
        """Remove item from buffer"""
        async with self._lock:
            if item_id not in self.items:
                return False
                
            item = self.items[item_id]
            self.size_bytes -= item.size_bytes
            
            del self.items[item_id]
            
            if item_id in self.access_order:
                self.access_order.remove(item_id)
                
            if item_id in self.access_frequency:
                del self.access_frequency[item_id]
                
            return True
            
    async def get_size_bytes(self) -> int:
        """Get buffer size in bytes"""
        return self.size_bytes
        
    async def maintenance(self) -> None:
        """Perform buffer maintenance"""
        async with self._lock:
            # Remove expired items
            current_time = datetime.now(timezone.utc)
            expired_items = []
            
            for item_id, item in self.items.items():
                if (current_time - item.timestamp).total_seconds() > self.config.ttl_seconds:
                    expired_items.append(item_id)
                    
            for item_id in expired_items:
                await self.remove(item_id)
                
            # Persist to disk if enabled
            if self.config.persistence_enabled:
                await self._persist_to_disk()
                
    async def _evict_items(self) -> None:
        """Evict items based on configured policy"""
        items_to_evict = min(self.config.max_items // 10, len(self.items))
        
        if self.config.eviction_policy == EvictionPolicy.LRU:
            # Evict least recently used
            for _ in range(items_to_evict):
                if self.access_order:
                    item_id = self.access_order.popleft()
                    if item_id in self.items:
                        await self.remove(item_id)
                        self.eviction_count += 1
                        
        elif self.config.eviction_policy == EvictionPolicy.LFU:
            # Evict least frequently used
            sorted_items = sorted(self.access_frequency.items(), key=lambda x: x[1])
            for item_id, _ in sorted_items[:items_to_evict]:
                await self.remove(item_id)
                self.eviction_count += 1
                
        elif self.config.eviction_policy == EvictionPolicy.FIFO:
            # Evict oldest items
            oldest_items = sorted(self.items.items(), key=lambda x: x[1].timestamp)
            for item_id, _ in oldest_items[:items_to_evict]:
                await self.remove(item_id)
                self.eviction_count += 1
                
    async def _compress_data(self, data: Any) -> bytes:
        """Compress data using configured compression"""
        serialized = pickle.dumps(data)
        
        if self.config.compression == CompressionType.GZIP:
            return gzip.compress(serialized)
        # Add other compression types as needed
        return serialized
        
    async def _decompress_data(self, data: bytes) -> Any:
        """Decompress data"""
        if self.config.compression == CompressionType.GZIP:
            decompressed = gzip.decompress(data)
        else:
            decompressed = data
            
        return pickle.loads(decompressed)
        
    async def _persist_to_disk(self) -> None:
        """Persist buffer to disk"""
        # Implementation would save buffer state to disk
        pass
        
    async def _load_from_disk(self) -> None:
        """Load buffer from disk"""
        # Implementation would load buffer state from disk
        pass
        
    async def shutdown(self) -> None:
        """Shutdown the buffer"""
        if self.config.persistence_enabled:
            await self._persist_to_disk()


# Queue implementation
class StreamQueue:
    """Priority-based message queue with retry mechanisms"""
    
    def __init__(self, queue_id -> None: str, max_size -> None: int = 10000) -> None:
        self.queue_id = queue_id
        self.max_size = max_size
        self.queue = PriorityQueue(maxsize=max_size)
        self.messages_processed = 0
        self._lock = asyncio.Lock()
        
    async def initialize(self) -> None:
        """Initialize the queue"""
        pass
        
    async def enqueue(
        self,
        data: Any,
        priority: QueuePriority = QueuePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Enqueue a message"""
        message_id = str(uuid.uuid4())
        
        message = QueueMessage(
            message_id=message_id,
            data=data,
            priority=priority,
            metadata=metadata or {}
        )
        
        try:
            # Use negative priority for max-heap behavior (higher priority first)
            priority_score = (-priority.value, time.time(), message_id)
            await asyncio.get_event_loop().run_in_executor(
                None, self.queue.put, (priority_score, message)
            )
            return message_id
        except Full:
            logger.error(f"Queue {self.queue_id} is full")
            return ""
            
    async def dequeue(self) -> Optional[QueueMessage]:
        """Dequeue a message"""
        try:
            priority_score, message = await asyncio.get_event_loop().run_in_executor(
                None, self.queue.get_nowait
            )
            return message
        except Empty:
            return None
            
    async def size(self) -> int:
        """Get queue size"""
        return self.queue.qsize()
        
    async def shutdown(self) -> None:
        """Shutdown the queue"""
        pass


# Connector implementations
class HTTPConnector(BaseConnector):
    """HTTP connector implementation"""
    
    def __init__(self) -> None:
        self.session = None
        
    async def connect(self, config: ConnectionConfig) -> bool:
        import aiohttp
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=config.timeout_seconds))
        return True
        
    async def disconnect(self) -> None:
        if self.session:
            await self.session.close()
            
    async def send(self, data: Any) -> bool:
        # HTTP send implementation
        return True
        
    async def receive(self) -> Optional[Any]:
        # HTTP receive implementation
        return None
        
    async def health_check(self) -> bool:
        return self.session is not None and not self.session.closed


class WebSocketConnector(BaseConnector):
    """WebSocket connector implementation"""
    
    def __init__(self) -> None:
        self.websocket = None
        
    async def connect(self, config: ConnectionConfig) -> bool:
        # WebSocket connect implementation
        return True
        
    async def disconnect(self) -> None:
        if self.websocket:
            await self.websocket.close()
            
    async def send(self, data: Any) -> bool:
        # WebSocket send implementation
        return True
        
    async def receive(self) -> Optional[Any]:
        # WebSocket receive implementation
        return None
        
    async def health_check(self) -> bool:
        return self.websocket is not None


class KafkaConnector(BaseConnector):
    """Kafka connector implementation"""
    
    async def connect(self, config: ConnectionConfig) -> bool:
        # Kafka connect implementation
        return True
        
    async def disconnect(self) -> None:
        # Kafka disconnect implementation
        pass
        
    async def send(self, data: Any) -> bool:
        # Kafka send implementation
        return True
        
    async def receive(self) -> Optional[Any]:
        # Kafka receive implementation
        return None
        
    async def health_check(self) -> bool:
        return True


class RedisConnector(BaseConnector):
    """Redis connector implementation"""
    
    async def connect(self, config: ConnectionConfig) -> bool:
        # Redis connect implementation
        return True
        
    async def disconnect(self) -> None:
        # Redis disconnect implementation
        pass
        
    async def send(self, data: Any) -> bool:
        # Redis send implementation
        return True
        
    async def receive(self) -> Optional[Any]:
        # Redis receive implementation
        return None
        
    async def health_check(self) -> bool:
        return True


class FileConnector(BaseConnector):
    """File connector implementation"""
    
    async def connect(self, config: ConnectionConfig) -> bool:
        # File connect implementation
        return True
        
    async def disconnect(self) -> None:
        # File disconnect implementation
        pass
        
    async def send(self, data: Any) -> bool:
        # File send implementation
        return True
        
    async def receive(self) -> Optional[Any]:
        # File receive implementation
        return None
        
    async def health_check(self) -> bool:
        return True


class CustomConnector(BaseConnector):
    """Custom connector implementation"""
    
    async def connect(self, config: ConnectionConfig) -> bool:
        # Custom connect implementation
        return True
        
    async def disconnect(self) -> None:
        # Custom disconnect implementation
        pass
        
    async def send(self, data: Any) -> bool:
        # Custom send implementation
        return True
        
    async def receive(self) -> Optional[Any]:
        # Custom receive implementation
        return None
        
    async def health_check(self) -> bool:
        return True


# Legacy compatibility classes
class StreamBuffer:
    """Legacy compatibility wrapper for DataFlowManager buffer functionality"""
    
    def __init__(self, config -> None: BufferConfig, manager -> None: Optional[DataFlowManager] = None) -> None:
        self.config = config
        self.manager = manager or DataFlowManager()
        
    async def initialize(self) -> None:
        """Initialize the buffer"""
        await self.manager.initialize()
        await self.manager.create_buffer(self.config.buffer_id, self.config)
        
    async def put(self, data: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Put data into buffer"""
        return await self.manager.put_data(self.config.buffer_id, data, metadata)
        
    async def get(self, item_id: str) -> Optional[Any]:
        """Get data from buffer"""
        return await self.manager.get_data(self.config.buffer_id, item_id)


class StreamQueue:
    """Legacy compatibility wrapper for DataFlowManager queue functionality"""
    
    def __init__(self, queue_id -> None: str = None, max_size -> None: int = 10000, manager -> None: Optional[DataFlowManager] = None) -> None:
        self.queue_id = queue_id or str(uuid.uuid4())
        self.max_size = max_size
        self.manager = manager or DataFlowManager()
        self.messages_processed = 0
        
    async def initialize(self) -> None:
        """Initialize the queue"""
        await self.manager.initialize()
        await self.manager.create_queue(self.queue_id, self.max_size)
        
    async def enqueue(self, data: Any, priority: QueuePriority = QueuePriority.NORMAL, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Enqueue a message"""
        return await self.manager.enqueue_message(self.queue_id, data, priority, metadata)


class StreamConnector:
    """Legacy compatibility wrapper for DataFlowManager connector functionality"""
    
    def __init__(self, manager -> None: Optional[DataFlowManager] = None) -> None:
        self.manager = manager or DataFlowManager()
        
    async def initialize(self) -> None:
        """Initialize the connector"""
        await self.manager.initialize()
        
    async def create_connection(self, connection_id: str, connector_type: ConnectorType, endpoint: str, credentials: Dict[str, str] = None) -> bool:
        """Create a connection"""
        return await self.manager.create_connection(connection_id, connector_type, endpoint, credentials)
        
    async def send_data(self, connection_id: str, data: Any) -> bool:
        """Send data through connection"""
        return await self.manager.send_data(connection_id, data)