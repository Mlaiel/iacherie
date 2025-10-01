"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Communication Manager for IA Chéries Microservices Platform
=======================================================

Enterprise-grade inter-service communication providing patterns for:
- Synchronous and asynchronous messaging
- Message queuing and event streaming
- Circuit breaker and retry mechanisms
- Message serialization and compression
- Load balancing and failover
- Request-response and pub-sub patterns
- Message routing and transformation
- Dead letter queue handling

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior & Microservices Expert
"""

import logging
import asyncio
import json
import pickle
import gzip
from typing import Dict, Any, Optional, List, Callable, Union, Type
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import uuid
import hashlib

from pydantic import BaseModel, Field
import redis.asyncio as redis
import httpx
import aioamqp
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

from .microservice_template import ServiceMessage, MessageType, ServiceStatus
from .circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class CommunicationProtocol(Enum):
    """Communication protocol enumeration"""
    HTTP = "http"
    REDIS_STREAMS = "redis_streams"
    REDIS_PUBSUB = "redis_pubsub"
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"
    GRPC = "grpc"
    WEBSOCKET = "websocket"


class MessagePriority(Enum):
    """Message priority enumeration"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class DeliveryMode(Enum):
    """Message delivery mode"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


class CompressionType(Enum):
    """Message compression type"""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    SNAPPY = "snappy"


class CommunicationConfig(BaseModel):
    """Communication configuration"""
    default_protocol: CommunicationProtocol = Field(default=CommunicationProtocol.REDIS_STREAMS, description="Default communication protocol")
    default_timeout: int = Field(default=30, description="Default request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_backoff_factor: float = Field(default=2.0, description="Retry backoff factor")
    enable_compression: bool = Field(default=True, description="Enable message compression")
    compression_type: CompressionType = Field(default=CompressionType.GZIP, description="Message compression type")
    enable_encryption: bool = Field(default=False, description="Enable message encryption")
    default_delivery_mode: DeliveryMode = Field(default=DeliveryMode.AT_LEAST_ONCE, description="Default delivery mode")
    batch_size: int = Field(default=100, description="Batch processing size")
    max_message_size: int = Field(default=1024*1024, description="Maximum message size in bytes")
    dead_letter_queue_enabled: bool = Field(default=True, description="Enable dead letter queue")
    circuit_breaker_enabled: bool = Field(default=True, description="Enable circuit breaker")
    load_balancing_enabled: bool = Field(default=True, description="Enable load balancing")


class MessageHeader(BaseModel):
    """Message header information"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique message ID")
    correlation_id: Optional[str] = Field(default=None, description="Correlation ID for tracing")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    priority: MessagePriority = Field(default=MessagePriority.NORMAL, description="Message priority")
    ttl: Optional[int] = Field(default=None, description="Time to live in seconds")
    delivery_mode: DeliveryMode = Field(default=DeliveryMode.AT_LEAST_ONCE, description="Delivery mode")
    content_type: str = Field(default="application/json", description="Content type")
    content_encoding: Optional[str] = Field(default=None, description="Content encoding")
    reply_to: Optional[str] = Field(default=None, description="Reply queue/topic")
    source_service: str = Field(..., description="Source service name")
    target_service: Optional[str] = Field(default=None, description="Target service name")
    routing_key: Optional[str] = Field(default=None, description="Message routing key")
    tags: Dict[str, str] = Field(default_factory=dict, description="Message tags")


class EnhancedServiceMessage(BaseModel):
    """Enhanced service message with additional metadata"""
    header: MessageHeader = Field(..., description="Message header")
    type: MessageType = Field(..., description="Message type")
    operation: str = Field(..., description="Operation or event name")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message payload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    retry_count: int = Field(default=0, description="Retry attempt count")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    checksum: Optional[str] = Field(default=None, description="Message checksum")


class CommunicationError(Exception):
    """Base communication error"""
    pass


class MessageSerializationError(CommunicationError):
    """Message serialization error"""
    pass


class MessageDeliveryError(CommunicationError):
    """Message delivery error"""
    pass


class CircuitBreakerOpenError(CommunicationError):
    """Circuit breaker open error"""
    pass


class MessageHandler(ABC):
    """Abstract message handler"""
    
    @abstractmethod
    async def handle(self, message: EnhancedServiceMessage) -> Optional[Any]:
        """Handle incoming message"""
        pass
    
    @abstractmethod
    async def validate_message(self, message: EnhancedServiceMessage) -> bool:
        """Validate message before processing"""
        pass


class MessageSerializer:
    """Message serialization utilities"""
    
    @staticmethod
    def serialize(message: EnhancedServiceMessage, compression: CompressionType = CompressionType.NONE) -> bytes:
        """Serialize message to bytes"""
        try:
            # Convert to JSON
            message_data = message.json()
            message_bytes = message_data.encode('utf-8')
            
            # Apply compression
            if compression == CompressionType.GZIP:
                message_bytes = gzip.compress(message_bytes)
            elif compression == CompressionType.LZ4:
                try:
                    import lz4.frame
                    message_bytes = lz4.frame.compress(message_bytes)
                except ImportError:
                    logger.warning("LZ4 not available, using no compression")
            elif compression == CompressionType.SNAPPY:
                try:
                    import snappy
                    message_bytes = snappy.compress(message_bytes)
                except ImportError:
                    logger.warning("Snappy not available, using no compression")
            
            return message_bytes
            
        except Exception as e:
            raise MessageSerializationError(f"Serialization failed: {str(e)}")
    
    @staticmethod
    def deserialize(data: bytes, compression: CompressionType = CompressionType.NONE) -> EnhancedServiceMessage:
        """Deserialize bytes to message"""
        try:
            # Apply decompression
            if compression == CompressionType.GZIP:
                data = gzip.decompress(data)
            elif compression == CompressionType.LZ4:
                try:
                    import lz4.frame
                    data = lz4.frame.decompress(data)
                except ImportError:
                    logger.warning("LZ4 not available, assuming no compression")
            elif compression == CompressionType.SNAPPY:
                try:
                    import snappy
                    data = snappy.decompress(data)
                except ImportError:
                    logger.warning("Snappy not available, assuming no compression")
            
            # Convert from JSON
            message_data = json.loads(data.decode('utf-8'))
            return EnhancedServiceMessage(**message_data)
            
        except Exception as e:
            raise MessageSerializationError(f"Deserialization failed: {str(e)}")
    
    @staticmethod
    def calculate_checksum(message: EnhancedServiceMessage) -> str:
        """Calculate message checksum"""
        message_str = f"{message.header.message_id}{message.operation}{json.dumps(message.payload, sort_keys=True)}"
        return hashlib.md5(message_str.encode()).hexdigest()


class CommunicationChannel(ABC):
    """Abstract communication channel"""
    
    @abstractmethod
    async def send(self, message: EnhancedServiceMessage) -> bool:
        """Send message"""
        pass
    
    @abstractmethod
    async def receive(self) -> Optional[EnhancedServiceMessage]:
        """Receive message"""
        pass
    
    @abstractmethod
    async def subscribe(self, topic: str, handler: MessageHandler):
        """Subscribe to topic with handler"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, topic: str):
        """Unsubscribe from topic"""
        pass
    
    @abstractmethod
    async def close(self):
        """Close channel"""
        pass


class RedisStreamChannel(CommunicationChannel):
    """Redis Streams communication channel"""
    
    def __init__(self, redis_client: redis.Redis, stream_name: str, consumer_group: str):
        self.redis_client = redis_client
        self.stream_name = stream_name
        self.consumer_group = consumer_group
        self.consumer_name = f"consumer_{uuid.uuid4().hex[:8]}"
        self.handlers: Dict[str, MessageHandler] = {}
        self.running = False
    
    async def send(self, message: EnhancedServiceMessage) -> bool:
        """Send message to Redis stream"""
        try:
            # Serialize message
            message_data = MessageSerializer.serialize(message)
            
            # Add to stream
            await self.redis_client.xadd(
                self.stream_name,
                {"data": message_data, "type": message.type.value}
            )
            
            logger.debug(f"Sent message to stream {self.stream_name}: {message.header.message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to Redis stream: {str(e)}")
            return False
    
    async def receive(self) -> Optional[EnhancedServiceMessage]:
        """Receive message from Redis stream"""
        try:
            # Read from stream
            messages = await self.redis_client.xreadgroup(
                self.consumer_group,
                self.consumer_name,
                {self.stream_name: ">"},
                count=1,
                block=1000
            )
            
            if messages:
                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        # Deserialize message
                        message_data = fields.get("data")
                        if message_data:
                            message = MessageSerializer.deserialize(message_data)
                            
                            # Acknowledge message
                            await self.redis_client.xack(self.stream_name, self.consumer_group, msg_id)
                            
                            return message
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to receive message from Redis stream: {str(e)}")
            return None
    
    async def subscribe(self, topic: str, handler: MessageHandler):
        """Subscribe to stream with handler"""
        self.handlers[topic] = handler
        
        if not self.running:
            asyncio.create_task(self._process_messages())
            self.running = True
    
    async def unsubscribe(self, topic: str):
        """Unsubscribe from topic"""
        if topic in self.handlers:
            del self.handlers[topic]
    
    async def _process_messages(self):
        """Process incoming messages"""
        while self.running:
            try:
                message = await self.receive()
                if message:
                    # Find appropriate handler
                    handler = self.handlers.get(message.operation)
                    if handler:
                        try:
                            await handler.handle(message)
                        except Exception as e:
                            logger.error(f"Message handler failed: {str(e)}")
                    else:
                        logger.warning(f"No handler for operation: {message.operation}")
                
            except Exception as e:
                logger.error(f"Error in message processing loop: {str(e)}")
                await asyncio.sleep(1)
    
    async def close(self):
        """Close channel"""
        self.running = False
        if self.redis_client:
            await self.redis_client.close()


class HttpChannel(CommunicationChannel):
    """HTTP communication channel"""
    
    def __init__(self, http_client: httpx.AsyncClient, base_url: str):
        self.http_client = http_client
        self.base_url = base_url
        self.handlers: Dict[str, MessageHandler] = {}
    
    async def send(self, message: EnhancedServiceMessage) -> bool:
        """Send HTTP request"""
        try:
            # Determine endpoint
            endpoint = f"{self.base_url}/api/v1/{message.operation}"
            
            # Prepare request data
            request_data = {
                "header": message.header.dict(),
                "payload": message.payload,
                "metadata": message.metadata
            }
            
            # Send request
            response = await self.http_client.post(
                endpoint,
                json=request_data,
                timeout=message.header.ttl or 30
            )
            
            response.raise_for_status()
            logger.debug(f"Sent HTTP message to {endpoint}: {message.header.message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send HTTP message: {str(e)}")
            return False
    
    async def receive(self) -> Optional[EnhancedServiceMessage]:
        """HTTP channels don't receive in traditional sense"""
        return None
    
    async def subscribe(self, topic: str, handler: MessageHandler):
        """HTTP channels don't subscribe in traditional sense"""
        self.handlers[topic] = handler
    
    async def unsubscribe(self, topic: str):
        """Unsubscribe from topic"""
        if topic in self.handlers:
            del self.handlers[topic]
    
    async def close(self):
        """Close channel"""
        if self.http_client:
            await self.http_client.aclose()


class CommunicationManager:
    """
    Enterprise communication manager for microservices
    
    Provides comprehensive inter-service communication including:
    - Multiple protocol support (HTTP, Redis, RabbitMQ, Kafka)
    - Circuit breaker integration
    - Message retry and dead letter queue
    - Load balancing and failover
    - Message compression and encryption
    - Request-response and pub-sub patterns
    - Message routing and transformation
    - Monitoring and metrics collection
    """
    
    def __init__(self, config: CommunicationConfig, service_name: str):
        """Initialize communication manager"""
        self.config = config
        self.service_name = service_name
        
        # Communication channels
        self.channels: Dict[CommunicationProtocol, CommunicationChannel] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Message handlers
        self.message_handlers: Dict[str, MessageHandler] = {}
        self.middleware: List[Callable] = []
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_failed": 0,
            "circuit_breaker_trips": 0
        }
        
        logger.info(f"Communication manager initialized for service: {service_name}")
    
    async def initialize(self, connections: Dict[str, Any]):
        """Initialize communication channels"""
        try:
            # Initialize Redis channel
            if "redis" in connections:
                redis_client = connections["redis"]
                redis_channel = RedisStreamChannel(
                    redis_client, 
                    f"service:{self.service_name}:messages",
                    f"{self.service_name}_group"
                )
                self.channels[CommunicationProtocol.REDIS_STREAMS] = redis_channel
            
            # Initialize HTTP channel
            if "http" in connections:
                http_client = connections["http"]
                http_channel = HttpChannel(http_client, "")
                self.channels[CommunicationProtocol.HTTP] = http_channel
            
            logger.info(f"Initialized {len(self.channels)} communication channels")
            
        except Exception as e:
            logger.error(f"Failed to initialize communication channels: {str(e)}")
            raise CommunicationError(f"Channel initialization failed: {str(e)}")
    
    async def send_message(
        self,
        target_service: str,
        operation: str,
        payload: Dict[str, Any],
        message_type: MessageType = MessageType.COMMAND,
        protocol: Optional[CommunicationProtocol] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        ttl: Optional[int] = None
    ) -> bool:
        """Send message to target service"""
        
        # Use circuit breaker
        if self.config.circuit_breaker_enabled:
            circuit_breaker = self._get_circuit_breaker(target_service)
            if not await circuit_breaker.can_execute():
                raise CircuitBreakerOpenError(f"Circuit breaker open for {target_service}")
        
        try:
            # Create message
            message = await self._create_message(
                target_service, operation, payload, message_type, priority, ttl
            )
            
            # Select communication protocol
            comm_protocol = protocol or self.config.default_protocol
            channel = self.channels.get(comm_protocol)
            
            if not channel:
                raise CommunicationError(f"Channel not available for protocol: {comm_protocol}")
            
            # Apply middleware
            for middleware in self.middleware:
                message = await middleware(message)
            
            # Send message with retry
            success = await self._send_with_retry(channel, message)
            
            if success:
                self.stats["messages_sent"] += 1
                if self.config.circuit_breaker_enabled:
                    await circuit_breaker.record_success()
            else:
                self.stats["messages_failed"] += 1
                if self.config.circuit_breaker_enabled:
                    await circuit_breaker.record_failure()
            
            return success
            
        except Exception as e:
            self.stats["messages_failed"] += 1
            if self.config.circuit_breaker_enabled:
                circuit_breaker = self._get_circuit_breaker(target_service)
                await circuit_breaker.record_failure()
            
            logger.error(f"Failed to send message to {target_service}: {str(e)}")
            return False
    
    async def _create_message(
        self,
        target_service: str,
        operation: str,
        payload: Dict[str, Any],
        message_type: MessageType,
        priority: MessagePriority,
        ttl: Optional[int]
    ) -> EnhancedServiceMessage:
        """Create enhanced service message"""
        
        header = MessageHeader(
            source_service=self.service_name,
            target_service=target_service,
            priority=priority,
            ttl=ttl or self.config.default_timeout,
            delivery_mode=self.config.default_delivery_mode
        )
        
        message = EnhancedServiceMessage(
            header=header,
            type=message_type,
            operation=operation,
            payload=payload,
            max_retries=self.config.max_retries
        )
        
        # Calculate checksum
        message.checksum = MessageSerializer.calculate_checksum(message)
        
        return message
    
    async def _send_with_retry(self, channel: CommunicationChannel, message: EnhancedServiceMessage) -> bool:
        """Send message with retry logic"""
        for attempt in range(self.config.max_retries + 1):
            try:
                success = await channel.send(message)
                if success:
                    return True
                
            except Exception as e:
                logger.warning(f"Send attempt {attempt + 1} failed: {str(e)}")
            
            # Update retry count
            message.retry_count = attempt + 1
            
            # Wait before retry (exponential backoff)
            if attempt < self.config.max_retries:
                wait_time = self.config.retry_backoff_factor ** attempt
                await asyncio.sleep(wait_time)
        
        # Send to dead letter queue if configured
        if self.config.dead_letter_queue_enabled:
            await self._send_to_dead_letter_queue(message)
        
        return False
    
    async def _send_to_dead_letter_queue(self, message: EnhancedServiceMessage):
        """Send failed message to dead letter queue"""
        try:
            # Add failure metadata
            message.metadata["failed_at"] = datetime.utcnow().isoformat()
            message.metadata["failure_reason"] = "max_retries_exceeded"
            
            # Send to DLQ (using Redis as default)
            dlq_channel = self.channels.get(CommunicationProtocol.REDIS_STREAMS)
            if dlq_channel:
                dlq_stream = RedisStreamChannel(
                    dlq_channel.redis_client,
                    f"dlq:{self.service_name}",
                    f"{self.service_name}_dlq_group"
                )
                await dlq_stream.send(message)
                logger.info(f"Sent message to dead letter queue: {message.header.message_id}")
        
        except Exception as e:
            logger.error(f"Failed to send to dead letter queue: {str(e)}")
    
    def _get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=5,
                timeout=60,
                expected_exception=CommunicationError
            )
        return self.circuit_breakers[service_name]
    
    async def subscribe(self, operation: str, handler: MessageHandler, protocol: Optional[CommunicationProtocol] = None):
        """Subscribe to operation with handler"""
        self.message_handlers[operation] = handler
        
        # Subscribe on all relevant channels
        comm_protocol = protocol or self.config.default_protocol
        channel = self.channels.get(comm_protocol)
        
        if channel:
            await channel.subscribe(operation, handler)
            logger.info(f"Subscribed to operation '{operation}' on {comm_protocol}")
    
    def add_middleware(self, middleware: Callable):
        """Add message processing middleware"""
        self.middleware.append(middleware)
        logger.info(f"Added middleware: {middleware.__name__}")
    
    async def request_response(
        self,
        target_service: str,
        operation: str,
        payload: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Send request and wait for response"""
        # Create correlation ID for tracking
        correlation_id = str(uuid.uuid4())
        response_queue = f"response:{self.service_name}:{correlation_id}"
        
        # Set up response handler
        response_future = asyncio.Future()
        
        async def response_handler(message: EnhancedServiceMessage):
            if message.header.correlation_id == correlation_id:
                response_future.set_result(message.payload)
        
        # Subscribe to response queue
        await self.subscribe(response_queue, type('ResponseHandler', (MessageHandler,), {
            'handle': response_handler,
            'validate_message': lambda self, msg: True
        })())
        
        # Send request
        message = await self._create_message(
            target_service, operation, payload, MessageType.QUERY, MessagePriority.NORMAL, timeout
        )
        message.header.correlation_id = correlation_id
        message.header.reply_to = response_queue
        
        success = await self.send_message(
            target_service, operation, payload, MessageType.QUERY, ttl=timeout
        )
        
        if not success:
            return None
        
        # Wait for response
        try:
            response = await asyncio.wait_for(
                response_future, 
                timeout=timeout or self.config.default_timeout
            )
            return response
        except asyncio.TimeoutError:
            logger.warning(f"Request timeout for operation '{operation}' on {target_service}")
            return None
    
    async def cleanup(self):
        """Cleanup communication manager"""
        try:
            # Close all channels
            for channel in self.channels.values():
                await channel.close()
            
            logger.info("Communication manager cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during communication cleanup: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get communication statistics"""
        return {
            **self.stats,
            "active_channels": list(self.channels.keys()),
            "circuit_breakers": {
                name: {
                    "state": cb.state.value,
                    "failure_count": cb.failure_count
                }
                for name, cb in self.circuit_breakers.items()
            },
            "message_handlers": list(self.message_handlers.keys())
        }