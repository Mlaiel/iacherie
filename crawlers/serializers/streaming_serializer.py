"""Streaming Serializer Module
============================

Specialized serialization for real-time streaming data and WebSocket communications.
Optimized for low-latency, high-throughput data streaming and real-time updates.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel (mlaiel@live.de). 
Any unauthorized copying, distribution, modification, or commercial use is STRICTLY PROHIBITED 
and will result in immediate legal action under German and International Copyright Law.

ZERO TOLERANCE POLICY: Anyone attempting to steal, copy, or misappropriate this code or concept 
will face severe legal consequences including but not limited to criminal charges, civil litigation, 
and substantial financial damages.

AUTHORIZED USE ONLY: Contact mlaiel@live.de for official licensing agreements.

Expertise combinée:
- Lead Developer IA: Architecture de streaming intelligent en temps réel
- Backend Senior: Infrastructure haute performance pour streaming massif
- ML Engineer: Algorithmes prédictifs pour optimisation de flux
- DBA Expert: Optimisation stockage et streaming de données massives
- Sécurité: Protection et chiffrement des flux de données sensibles
- Microservices: Architecture distribuée pour streaming multi-plateformes
- Audio/Vidéo: Streaming optimisé pour contenu multimédia haute qualité
- DevOps: Monitoring et scaling automatique des flux temps réel
- IA Prompt Engineer: Streaming intelligent pour interactions IA en temps réel
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, AsyncGenerator, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import time
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class StreamType(Enum):
    """
Types of streaming data."""

    REAL_TIME = "real_time"
    BATCH = "batch"
    EVENT = "event"
    WEBSOCKET = "websocket"
    SSE = "sse"  # Server-Sent Events
    MQTT = "mqtt"
    KAFKA = "kafka"

class StreamPriority(Enum):
    """Stream message priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

class StreamFormat(Enum):
    """
Streaming data formats."""

    JSON = "json"
    MSGPACK = "msgpack"
    PROTOBUF = "protobuf"
    AVRO = "avro"
    BINARY = "binary"
    PLAIN_TEXT = "text"

class CompressionMode(Enum):
    """Compression modes for streaming."""

    NONE = "none"
    REAL_TIME = "real_time"  # Fast compression
    BALANCED = "balanced"    # Balance speed/ratio
    HIGH_RATIO = "high_ratio"  # Maximum compression

@dataclass
class StreamMetrics:
    """Streaming performance metrics."""
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    average_latency_ms: float = 0.0
    peak_latency_ms: float = 0.0
    throughput_mps: float = 0.0  # Messages per second
    bandwidth_bps: float = 0.0   # Bytes per second
    error_count: int = 0
    connection_count: int = 0
    active_streams: int = 0
    compression_ratio: float = 1.0

@dataclass
class StreamMessage:
    """
Individual streaming message."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    stream_id: str = ""
    sequence_number: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    priority: StreamPriority = StreamPriority.NORMAL
    message_type: str = "data"
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    compressed: bool = False
    size_bytes: int = 0
    delivery_attempts: int = 0
    max_delivery_attempts: int = 3
    expires_at: Optional[datetime] = None

class StreamData(BaseModel):
    """
    Comprehensive streaming data model.
    
    Represents streaming configuration, messages, and performance metrics
    for the IA-Influencer-Agent real-time data streaming system.
    """
    
    # Stream identification
    stream_id: str = Field(..., description="Unique stream identifier")
    stream_name: str = Field(..., description="Stream name/topic")
    stream_type: StreamType = Field(default=StreamType.REAL_TIME)
    stream_format: StreamFormat = Field(default=StreamFormat.JSON)
    
    # Stream configuration
    max_message_size: int = Field(default=1024 * 1024)  # 1MB
    buffer_size: int = Field(default=10000)
    compression_mode: CompressionMode = Field(default=CompressionMode.REAL_TIME)
    enable_ordering: bool = Field(default=True)
    enable_acknowledgments: bool = Field(default=True)
    heartbeat_interval_seconds: int = Field(default=30)
    max_reconnect_attempts: int = Field(default=5)
    
    # Message management
    message_buffer: List[StreamMessage] = Field(default_factory=list)
    pending_acknowledgments: Dict[str, StreamMessage] = Field(default_factory=dict)
    failed_messages: List[StreamMessage] = Field(default_factory=list)
    
    # Performance metrics
    metrics: StreamMetrics = Field(default_factory=StreamMetrics)
    
    # Connection management
    connection_id: Optional[str] = None
    connection_state: str = Field(default="disconnected")
    last_heartbeat: Optional[datetime] = None
    connection_established_at: Optional[datetime] = None
    
    # Quality of Service
    delivery_guarantee: str = Field(default="at_least_once")  # at_most_once, at_least_once, exactly_once
    ordering_guarantee: str = Field(default="per_partition")  # none, per_partition, global
    durability_level: str = Field(default="memory")  # memory, disk, replicated
    
    # Filtering and routing
    content_filters: List[str] = Field(default_factory=list)
    routing_key: Optional[str] = None
    target_consumers: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_activity_at: datetime = Field(default_factory=datetime.now)
    
    @validator('stream_type', pre=True)
    def validate_stream_type(cls, v):
        if isinstance(v, str):
            return StreamType(v.lower())
        return v
    
    @validator('stream_format', pre=True)
    def validate_stream_format(cls, v):
        if isinstance(v, str):
            return StreamFormat(v.lower())
        return v
    
    @validator('compression_mode', pre=True)
    def validate_compression_mode(cls, v):
        if isinstance(v, str):
            return CompressionMode(v.lower())
        return v

class StreamingSerializer:
    """
    Advanced streaming data serialization system.
    
    Handles efficient serialization and deserialization of streaming
    messages with optimization for real-time performance, low latency,
    and high throughput requirements.
    """
    
    def __init__(self):
        """
Initialize streaming serializer."""
        self.active_streams: Dict[str, StreamData] = {}
        self.serialization_cache = {}
        self.compression_cache = {}
        self.performance_counters = {
            'serializations': 0,
            'deserializations': 0,
            'compressions': 0,
            'decompressions': 0,
            'total_bytes_processed': 0,
            'average_processing_time': 0.0
        }
        
        logger.info("Streaming serializer initialized")
    
    def serialize_stream_data(
        self,
        stream_data: StreamData,
        include_buffer: bool = False,
        max_buffer_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Serialize streaming data to dictionary format.
        
        Args:
            stream_data: Stream data to serialize
            include_buffer: Whether to include message buffer
            max_buffer_size: Maximum buffer size to include
            
        Returns:
            Serialized stream dictionary
        """
        start_time = time.time()
        
        try:
            # Convert to dictionary
            data = stream_data.dict(exclude={'message_buffer', 'pending_acknowledgments', 'failed_messages'})
            
            # Handle datetime conversions
            datetime_fields = [
                'created_at', 'updated_at', 'last_activity_at', 
                'last_heartbeat', 'connection_established_at'
            ]
            for field in datetime_fields:
                if data.get(field):
                    data[field] = getattr(stream_data, field).isoformat()
            
            # Serialize metrics
            data['metrics'] = self._serialize_stream_metrics(stream_data.metrics)
            
            # Handle message buffer
            if include_buffer and stream_data.message_buffer:
                buffer_to_serialize = stream_data.message_buffer
                
                # Limit buffer size if specified
                if max_buffer_size and len(buffer_to_serialize) > max_buffer_size:
                    # Keep most recent messages
                    buffer_to_serialize = buffer_to_serialize[-max_buffer_size:]
                    data['_buffer_truncated'] = True
                    data['_total_buffer_size'] = len(stream_data.message_buffer)
                
                data['message_buffer'] = [
                    self._serialize_stream_message(msg)
                    for msg in buffer_to_serialize
                ]
            else:
                data['message_buffer'] = []
            
            # Handle pending acknowledgments
            data['pending_acknowledgments'] = {
                msg_id: self._serialize_stream_message(msg)
                for msg_id, msg in stream_data.pending_acknowledgments.items()
            }
            
            # Handle failed messages
            data['failed_messages'] = [
                self._serialize_stream_message(msg)
                for msg in stream_data.failed_messages
            ]
            
            # Convert enums
            data['stream_type'] = stream_data.stream_type.value
            data['stream_format'] = stream_data.stream_format.value
            data['compression_mode'] = stream_data.compression_mode.value
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'includes_buffer': include_buffer,
                'max_buffer_size': max_buffer_size,
                'stream_type': stream_data.stream_type.value
            }
            
            # Update performance counters
            processing_time = time.time() - start_time
            self._update_performance_counters('serialization', processing_time, len(json.dumps(data)))
            
            logger.debug(f"Serialized stream data {stream_data.stream_id}")
            return data
            
        except Exception as e:
            logger.error(f"Stream data serialization failed: {e}")
            raise
    
    def deserialize_stream_data(
        self,
        data: Dict[str, Any]
    ) -> StreamData:
        """
        Deserialize streaming data from dictionary format.
        
        Args:
            data: Serialized stream dictionary
            
        Returns:
            Deserialized StreamData object
        """
        start_time = time.time()
        
        try:
            # Handle datetime conversions
            datetime_fields = [
                'created_at', 'updated_at', 'last_activity_at',
                'last_heartbeat', 'connection_established_at'
            ]
            for field in datetime_fields:
                if isinstance(data.get(field), str):
                    data[field] = datetime.fromisoformat(data[field])
            
            # Deserialize metrics
            if 'metrics' in data and data['metrics']:
                data['metrics'] = self._deserialize_stream_metrics(data['metrics'])
            
            # Deserialize message buffer
            if 'message_buffer' in data and data['message_buffer']:
                data['message_buffer'] = [
                    self._deserialize_stream_message(msg_data)
                    for msg_data in data['message_buffer']
                ]
            
            # Deserialize pending acknowledgments
            if 'pending_acknowledgments' in data and data['pending_acknowledgments']:
                data['pending_acknowledgments'] = {
                    msg_id: self._deserialize_stream_message(msg_data)
                    for msg_id, msg_data in data['pending_acknowledgments'].items()
                }
            
            # Deserialize failed messages
            if 'failed_messages' in data and data['failed_messages']:
                data['failed_messages'] = [
                    self._deserialize_stream_message(msg_data)
                    for msg_data in data['failed_messages']
                ]
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            data.pop('_buffer_truncated', None)
            data.pop('_total_buffer_size', None)
            
            # Create StreamData object
            stream_data = StreamData(**data)
            
            # Update performance counters
            processing_time = time.time() - start_time
            self._update_performance_counters('deserialization', processing_time, 0)
            
            logger.debug(f"Deserialized stream data {stream_data.stream_id}")
            return stream_data
            
        except Exception as e:
            logger.error(f"Stream data deserialization failed: {e}")
            raise
    
    def serialize_stream_message(
        self,
        message: StreamMessage,
        compress: bool = False
    ) -> Dict[str, Any]:
        """
        Serialize individual stream message.
        
        Args:
            message: Stream message to serialize
            compress: Whether to compress message content
            
        Returns:
            Serialized message dictionary
        """
        try:
            return self._serialize_stream_message(message, compress)
            
        except Exception as e:
            logger.error(f"Stream message serialization failed: {e}")
            raise
    
    def deserialize_stream_message(
        self,
        data: Dict[str, Any]
    ) -> StreamMessage:
        """
        Deserialize individual stream message.
        
        Args:
            data: Serialized message dictionary
            
        Returns:
            Deserialized StreamMessage object
        """
        try:
            return self._deserialize_stream_message(data)
            
        except Exception as e:
            logger.error(f"Stream message deserialization failed: {e}")
            raise
    
    def _serialize_stream_message(
        self,
        message: StreamMessage,
        compress: bool = False
    ) -> Dict[str, Any]:
        """Internal stream message serialization."""
        data = {
            'message_id': message.message_id,
            'stream_id': message.stream_id,
            'sequence_number': message.sequence_number,
            'timestamp': message.timestamp.isoformat(),
            'priority': message.priority.value,
            'message_type': message.message_type,
            'metadata': message.metadata,
            'compressed': message.compressed,
            'size_bytes': message.size_bytes,
            'delivery_attempts': message.delivery_attempts,
            'max_delivery_attempts': message.max_delivery_attempts
        }
        
        if message.expires_at:
            data['expires_at'] = message.expires_at.isoformat()
        
        # Handle content serialization
        try:
            if compress and not message.compressed:
                compressed_content = self._compress_message_content(message.content)
                data['content'] = compressed_content
                data['_content_compressed'] = True
            else:
                data['content'] = message.content
                data['_content_compressed'] = False
                
        except Exception as e:
            logger.warning(f"Message content serialization failed: {e}")
            data['content'] = str(message.content)  # Fallback
            data['_content_compressed'] = False
        
        return data
    
    def _deserialize_stream_message(self, data: Dict[str, Any]) -> StreamMessage:
        """Internal stream message deserialization."""
        # Handle datetime conversions
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        if isinstance(data.get('expires_at'), str):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        
        # Handle priority enum
        if isinstance(data.get('priority'), int):
            data['priority'] = StreamPriority(data['priority'])
        
        # Handle content decompression
        if data.get('_content_compressed', False):
            data['content'] = self._decompress_message_content(data['content'])
        
        # Remove compression metadata
        data.pop('_content_compressed', None)
        
        return StreamMessage(**data)
    
    def _serialize_stream_metrics(self, metrics: StreamMetrics) -> Dict[str, Any]:
        """
Serialize stream metrics."""
        return {
            'messages_sent': metrics.messages_sent,
            'messages_received': metrics.messages_received,
            'bytes_sent': metrics.bytes_sent,
            'bytes_received': metrics.bytes_received,
            'average_latency_ms': metrics.average_latency_ms,
            'peak_latency_ms': metrics.peak_latency_ms,
            'throughput_mps': metrics.throughput_mps,
            'bandwidth_bps': metrics.bandwidth_bps,
            'error_count': metrics.error_count,
            'connection_count': metrics.connection_count,
            'active_streams': metrics.active_streams,
            'compression_ratio': metrics.compression_ratio
        }
    
    def _deserialize_stream_metrics(self, data: Dict[str, Any]) -> StreamMetrics:
        """
Deserialize stream metrics."""
        return StreamMetrics(**data)
    
    def _compress_message_content(self, content: Any) -> str:
        """
Compress message content for streaming."""
        try:
            import gzip
            import pickle
            
            # Serialize content
            serialized = pickle.dumps(content, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Compress with fast algorithm for real-time
            compressed = gzip.compress(serialized, compresslevel=1)  # Fast compression
            
            # Encode to base64
            import base64
            encoded = base64.b64encode(compressed).decode('utf-8')
            
            # Update performance counters
            self._update_performance_counters('compression', 0, len(compressed))
            
            return f"gzip_pickle_fast:{encoded}"
            
        except Exception as e:
            logger.error(f"Message content compression failed: {e}")
            # Fallback to JSON
            return json.dumps(content, default=str)
    
    def _decompress_message_content(self, compressed_content: str) -> Any:
        """Decompress message content."""
        try:
            if compressed_content.startswith('gzip_pickle_fast:'):
                import gzip
                import pickle
                import base64
                
                # Remove prefix and decode
                encoded = compressed_content[17:]  # len('gzip_pickle_fast:')
                compressed = base64.b64decode(encoded)
                
                # Decompress
                serialized = gzip.decompress(compressed)
                
                # Deserialize
                content = pickle.loads(serialized)
                
                # Update performance counters
                self._update_performance_counters('decompression', 0, len(compressed))
                
                return content
            else:
                # JSON fallback
                return json.loads(compressed_content)
                
        except Exception as e:
            logger.error(f"Message content decompression failed: {e}")
            return compressed_content
    
    def _update_performance_counters(
        self,
        operation: str,
        processing_time: float,
        bytes_processed: int
    ):
        """Update performance counters."""
        try:
            if operation in ['serialization', 'deserialization']:
                self.performance_counters[f'{operation}s'] += 1
            elif operation in ['compression', 'decompression']:
                self.performance_counters[f'{operation}s'] += 1
            
            self.performance_counters['total_bytes_processed'] += bytes_processed
            
            # Update average processing time
            current_avg = self.performance_counters['average_processing_time']
            total_operations = sum([
                self.performance_counters['serializations'],
                self.performance_counters['deserializations'],
                self.performance_counters['compressions'],
                self.performance_counters['decompressions']
            ])
            
            if total_operations > 0:
                self.performance_counters['average_processing_time'] = (
                    (current_avg * (total_operations - 1) + processing_time) / total_operations
                )
                
        except Exception as e:
            logger.error(f"Performance counter update failed: {e}")
    
    async def stream_messages_async(
        self,
        stream_data: StreamData,
        message_generator: AsyncGenerator[StreamMessage, None],
        compression_enabled: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Asynchronously stream and serialize messages.
        
        Args:
            stream_data: Stream configuration
            message_generator: Async generator of messages
            compression_enabled: Whether to compress messages
            
        Yields:
            Serialized message dictionaries
        """
        try:
            async for message in message_generator:
                # Update stream metrics
                stream_data.metrics.messages_sent += 1
                stream_data.last_activity_at = datetime.now()
                
                # Serialize message
                serialized_message = self._serialize_stream_message(
                    message, 
                    compress=compression_enabled
                )
                
                # Add streaming metadata
                serialized_message['_stream_metadata'] = {
                    'stream_id': stream_data.stream_id,
                    'serialized_at': datetime.now().isoformat(),
                    'sequence': message.sequence_number,
                    'compressed': compression_enabled
                }
                
                yield serialized_message
                
        except Exception as e:
            logger.error(f"Async message streaming failed: {e}")
            stream_data.metrics.error_count += 1
            raise
    
    def create_stream_batch(
        self,
        messages: List[StreamMessage],
        batch_size: int = 100,
        compression_enabled: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Create serialized batch of stream messages.
        
        Args:
            messages: List of messages to batch
            batch_size: Maximum batch size
            compression_enabled: Whether to compress messages
            
        Returns:
            List of serialized message batches
        """
        try:
            batches = []
            
            for i in range(0, len(messages), batch_size):
                batch_messages = messages[i:i + batch_size]
                
                serialized_batch = {
                    'batch_id': str(uuid.uuid4()),
                    'batch_size': len(batch_messages),
                    'created_at': datetime.now().isoformat(),
                    'compressed': compression_enabled,
                    'messages': [
                        self._serialize_stream_message(msg, compress=compression_enabled)
                        for msg in batch_messages
                    ]
                }
                
                batches.append(serialized_batch)
            
            logger.info(f"Created {len(batches)} message batches")
            return batches
            
        except Exception as e:
            logger.error(f"Stream batch creation failed: {e}")
            raise
    
    def get_streaming_statistics(self) -> Dict[str, Any]:
        """Get comprehensive streaming statistics."""
        try:
            total_streams = len(self.active_streams)
            total_messages = sum(
                len(stream.message_buffer) for stream in self.active_streams.values()
            )
            
            return {
                'active_streams': total_streams,
                'total_buffered_messages': total_messages,
                'performance_counters': self.performance_counters.copy(),
                'cache_size': len(self.serialization_cache),
                'compression_cache_size': len(self.compression_cache),
                'streams_by_type': {
                    stream_type.value: sum(
                        1 for stream in self.active_streams.values()
                        if stream.stream_type == stream_type
                    )
                    for stream_type in StreamType
                },
                'average_buffer_size': total_messages / max(total_streams, 1),
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Streaming statistics calculation failed: {e}")
            return {'error': str(e)}


# Export main classes
__all__ = [
    'StreamingSerializer',
    'StreamData',
    'StreamMessage',
    'StreamMetrics',
    'StreamType',
    'StreamPriority',
    'StreamFormat',
    'CompressionMode'
]
