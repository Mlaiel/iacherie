"""
🎯 Message Broker Microservice
Event-driven messaging and communication service with multiple brokers, message routing, and reliable delivery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import time
import logging
import uuid
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
import weakref
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MessageStatus(str, Enum):
    """Message status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    EXPIRED = "expired"


class BrokerType(str, Enum):
    """Message broker types"""
    MEMORY = "memory"
    REDIS = "redis"
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    AWS_SQS = "aws_sqs"
    AZURE_SERVICE_BUS = "azure_service_bus"


class DeliveryGuarantee(str, Enum):
    """Message delivery guarantees"""
    AT_MOST_ONCE = "at_most_once"  # Fire and forget
    AT_LEAST_ONCE = "at_least_once"  # May deliver duplicates
    EXACTLY_ONCE = "exactly_once"  # Exactly one delivery


@dataclass
class Message:
    """Message structure"""
    id: str
    topic: str
    payload: Any
    headers: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    content_type: str = "application/json"
    compression: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if message is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat() if self.expires_at else None
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        return data
        
    def serialize_payload(self) -> bytes:
        """Serialize payload for transmission"""
        if isinstance(self.payload, bytes):
            return self.payload
        elif isinstance(self.payload, str):
            return self.payload.encode('utf-8')
        else:
            return json.dumps(self.payload, default=str).encode('utf-8')


@dataclass
class TopicConfiguration:
    """Topic configuration"""
    name: str
    partitions: int = 1
    replication_factor: int = 1
    retention_period: timedelta = timedelta(hours=24)
    max_message_size: int = 1024 * 1024  # 1MB
    delivery_guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE
    dead_letter_topic: Optional[str] = None
    compression_enabled: bool = False
    encryption_enabled: bool = False


@dataclass
class ConsumerGroup:
    """Consumer group configuration"""
    name: str
    topics: List[str]
    max_parallel_consumers: int = 5
    auto_commit: bool = True
    commit_interval: int = 5000  # milliseconds
    session_timeout: int = 30000  # milliseconds
    heartbeat_interval: int = 3000  # milliseconds


class MessageHandler(ABC):
    """Abstract message handler"""
    
    @abstractmethod
    async def handle_message(self, message: Message) -> bool:
        """Handle a message"""
        pass
        
    @abstractmethod
    async def handle_error(self, message: Message, error: Exception) -> bool:
        """Handle message processing error"""
        pass


class MessageBrokerInterface(ABC):
    """Abstract message broker interface"""
    
    @abstractmethod
    async def publish(self, message: Message) -> bool:
        """Publish message"""
        pass
        
    @abstractmethod
    async def subscribe(self, topic: str, handler: MessageHandler, 
                       consumer_group: str = None) -> str:
        """Subscribe to topic"""
        pass
        
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from topic"""
        pass
        
    @abstractmethod
    async def create_topic(self, config: TopicConfiguration) -> bool:
        """Create topic"""
        pass
        
    @abstractmethod
    async def delete_topic(self, topic: str) -> bool:
        """Delete topic"""
        pass
        
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get broker statistics"""
        pass
        
    @abstractmethod
    async def close(self) -> None:
        """Close broker connection"""
        pass


class MemoryMessageBroker(MessageBrokerInterface):
    """In-memory message broker implementation"""
    
    def __init__(self) -> None:
        self.topics: Dict[str, TopicConfiguration] = {}
        self.messages: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.subscribers: Dict[str, List[Tuple[MessageHandler, str]]] = defaultdict(list)
        self.subscription_counter = 0
        self.subscriptions: Dict[str, Tuple[str, MessageHandler, str]] = {}
        self.stats = {
            'messages_published': 0,
            'messages_delivered': 0,
            'messages_failed': 0,
            'active_subscriptions': 0
        }
        self._lock = threading.RLock()
        self.running = False
        self.delivery_task = None
        
    async def start(self) -> None:
        """Start the broker"""
        self.running = True
        self.delivery_task = asyncio.create_task(self._delivery_loop())
        
    async def stop(self) -> None:
        """Stop the broker"""
        self.running = False
        if self.delivery_task:
            self.delivery_task.cancel()
            try:
                await self.delivery_task
            except asyncio.CancelledError:
                pass
                
    async def publish(self, message: Message) -> bool:
        """Publish message to topic"""
        try:
            with self._lock:
                if message.topic not in self.topics:
                    # Auto-create topic with default config
                    await self.create_topic(TopicConfiguration(name=message.topic))
                    
                # Check message size
                topic_config = self.topics[message.topic]
                payload_size = len(message.serialize_payload())
                if payload_size > topic_config.max_message_size:
                    logger.error(f"Message too large: {payload_size} > {topic_config.max_message_size}")
                    return False
                    
                # Add to topic queue
                self.messages[message.topic].append(message)
                message.status = MessageStatus.SENT
                self.stats['messages_published'] += 1
                
                logger.debug(f"Published message {message.id} to topic {message.topic}")
                return True
                
        except Exception as e:
            logger.error(f"Error publishing message: {str(e)}")
            return False
            
    async def subscribe(self, topic: str, handler: MessageHandler, 
                       consumer_group: str = None) -> str:
        """Subscribe to topic"""
        try:
            with self._lock:
                subscription_id = f"sub_{self.subscription_counter}"
                self.subscription_counter += 1
                
                self.subscribers[topic].append((handler, consumer_group or "default"))
                self.subscriptions[subscription_id] = (topic, handler, consumer_group or "default")
                self.stats['active_subscriptions'] += 1
                
                logger.info(f"Subscribed to topic {topic} with ID {subscription_id}")
                return subscription_id
                
        except Exception as e:
            logger.error(f"Error subscribing to topic: {str(e)}")
            return ""
            
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from topic"""
        try:
            with self._lock:
                if subscription_id in self.subscriptions:
                    topic, handler, consumer_group = self.subscriptions[subscription_id]
                    self.subscribers[topic] = [
                        (h, cg) for h, cg in self.subscribers[topic]
                        if not (h == handler and cg == consumer_group)
                    ]
                    del self.subscriptions[subscription_id]
                    self.stats['active_subscriptions'] -= 1
                    
                    logger.info(f"Unsubscribed from topic {topic} with ID {subscription_id}")
                    return True
                    
                return False
                
        except Exception as e:
            logger.error(f"Error unsubscribing: {str(e)}")
            return False
            
    async def create_topic(self, config: TopicConfiguration) -> bool:
        """Create topic"""
        try:
            with self._lock:
                self.topics[config.name] = config
                if config.name not in self.messages:
                    self.messages[config.name] = deque(maxlen=10000)
                    
                logger.info(f"Created topic: {config.name}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating topic: {str(e)}")
            return False
            
    async def delete_topic(self, topic: str) -> bool:
        """Delete topic"""
        try:
            with self._lock:
                if topic in self.topics:
                    del self.topics[topic]
                    del self.messages[topic]
                    # Remove all subscriptions for this topic
                    self.subscribers[topic].clear()
                    
                    logger.info(f"Deleted topic: {topic}")
                    return True
                    
                return False
                
        except Exception as e:
            logger.error(f"Error deleting topic: {str(e)}")
            return False
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get broker statistics"""
        with self._lock:
            stats = self.stats.copy()
            stats['topics_count'] = len(self.topics)
            stats['total_messages'] = sum(len(queue) for queue in self.messages.values())
            return stats
            
    async def close(self) -> None:
        """Close memory broker"""
        await self.stop()
        
    async def _delivery_loop(self) -> None:
        """Message delivery loop"""
        while self.running:
            try:
                await self._deliver_messages()
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in delivery loop: {str(e)}")
                
    async def _deliver_messages(self) -> None:
        """Deliver messages to subscribers"""
        with self._lock:
            topics_to_process = list(self.messages.keys())
            
        for topic in topics_to_process:
            try:
                with self._lock:
                    if not self.messages[topic] or topic not in self.subscribers:
                        continue
                        
                    message = self.messages[topic].popleft()
                    handlers = self.subscribers[topic].copy()
                    
                if message.is_expired():
                    message.status = MessageStatus.EXPIRED
                    continue
                    
                # Deliver to all subscribers
                delivered = False
                for handler, consumer_group in handlers:
                    try:
                        success = await handler.handle_message(message)
                        if success:
                            delivered = True
                            self.stats['messages_delivered'] += 1
                            message.status = MessageStatus.DELIVERED
                        else:
                            await handler.handle_error(message, Exception("Handler returned False"))
                            
                    except Exception as e:
                        logger.error(f"Error delivering message {message.id}: {str(e)}")
                        await handler.handle_error(message, e)
                        self.stats['messages_failed'] += 1
                        
                if not delivered and message.retry_count < message.max_retries:
                    # Retry message
                    message.retry_count += 1
                    with self._lock:
                        self.messages[topic].append(message)
                        
            except Exception as e:
                logger.error(f"Error processing topic {topic}: {str(e)}")


class KafkaMessageBroker(MessageBrokerInterface):
    """Kafka message broker implementation"""
    
    def __init__(self, brokers -> None: List[str], client_id -> None: str = "ainflue") -> None:
        self.brokers = brokers
        self.client_id = client_id
        self.producer = None
        self.consumers: Dict[str, Any] = {}
        self.topics: Dict[str, TopicConfiguration] = {}
        self.stats = {
            'messages_published': 0,
            'messages_delivered': 0,
            'messages_failed': 0,
            'active_subscriptions': 0
        }
        
    async def _ensure_producer(self) -> None:
        """Ensure Kafka producer is initialized"""
        if self.producer is None:
            try:
                from aiokafka import AIOKafkaProducer
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=self.brokers,
                    client_id=self.client_id,
                    value_serializer=lambda x: x if isinstance(x, bytes) else json.dumps(x).encode('utf-8')
                )
                await self.producer.start()
            except ImportError:
                logger.error("aiokafka library not available")
                raise
                
    async def publish(self, message: Message) -> bool:
        """Publish message to Kafka"""
        try:
            await self._ensure_producer()
            
            # Prepare message data
            message_data = {
                'id': message.id,
                'payload': message.payload,
                'headers': message.headers,
                'created_at': message.created_at.isoformat(),
                'correlation_id': message.correlation_id
            }
            
            # Send to Kafka
            await self.producer.send(
                message.topic,
                value=message_data,
                headers={
                    'message_id': message.id.encode(),
                    'priority': message.priority.value.encode(),
                    'content_type': message.content_type.encode()
                }
            )
            
            message.status = MessageStatus.SENT
            self.stats['messages_published'] += 1
            
            logger.debug(f"Published message {message.id} to Kafka topic {message.topic}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing to Kafka: {str(e)}")
            return False
            
    async def subscribe(self, topic: str, handler: MessageHandler, 
                       consumer_group: str = None) -> str:
        """Subscribe to Kafka topic"""
        try:
            from aiokafka import AIOKafkaConsumer
            
            consumer_group = consumer_group or "default"
            subscription_id = f"kafka_{topic}_{consumer_group}_{uuid.uuid4().hex[:8]}"
            
            consumer = AIOKafkaConsumer(
                topic,
                bootstrap_servers=self.brokers,
                group_id=consumer_group,
                client_id=f"{self.client_id}_{subscription_id}",
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            
            await consumer.start()
            self.consumers[subscription_id] = consumer
            self.stats['active_subscriptions'] += 1
            
            # Start consumer task
            asyncio.create_task(self._consume_messages(subscription_id, consumer, handler))
            
            logger.info(f"Subscribed to Kafka topic {topic} with ID {subscription_id}")
            return subscription_id
            
        except ImportError:
            logger.error("aiokafka library not available")
            return ""
        except Exception as e:
            logger.error(f"Error subscribing to Kafka topic: {str(e)}")
            return ""
            
    async def _consume_messages(self, subscription_id -> None: str, consumer, handler -> None: MessageHandler) -> None:
        """Consume messages from Kafka"""
        try:
            async for msg in consumer:
                try:
                    # Convert Kafka message to our Message format
                    message_data = msg.value
                    message = Message(
                        id=message_data.get('id', str(uuid.uuid4())),
                        topic=msg.topic,
                        payload=message_data.get('payload'),
                        headers=message_data.get('headers', {}),
                        created_at=datetime.fromisoformat(message_data.get('created_at', datetime.utcnow().isoformat())),
                        correlation_id=message_data.get('correlation_id')
                    )
                    
                    # Handle message
                    success = await handler.handle_message(message)
                    if success:
                        self.stats['messages_delivered'] += 1
                        message.status = MessageStatus.DELIVERED
                    else:
                        await handler.handle_error(message, Exception("Handler returned False"))
                        self.stats['messages_failed'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing Kafka message: {str(e)}")
                    self.stats['messages_failed'] += 1
                    
        except Exception as e:
            logger.error(f"Error in Kafka consumer {subscription_id}: {str(e)}")
            
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from Kafka topic"""
        try:
            if subscription_id in self.consumers:
                consumer = self.consumers[subscription_id]
                await consumer.stop()
                del self.consumers[subscription_id]
                self.stats['active_subscriptions'] -= 1
                
                logger.info(f"Unsubscribed from Kafka with ID {subscription_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error unsubscribing from Kafka: {str(e)}")
            return False
            
    async def create_topic(self, config: TopicConfiguration) -> bool:
        """Create Kafka topic"""
        try:
            # In a real implementation, you'd use Kafka admin client
            self.topics[config.name] = config
            logger.info(f"Created Kafka topic: {config.name}")
            return True
        except Exception as e:
            logger.error(f"Error creating Kafka topic: {str(e)}")
            return False
            
    async def delete_topic(self, topic: str) -> bool:
        """Delete Kafka topic"""
        try:
            # In a real implementation, you'd use Kafka admin client
            if topic in self.topics:
                del self.topics[topic]
                logger.info(f"Deleted Kafka topic: {topic}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting Kafka topic: {str(e)}")
            return False
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get Kafka broker statistics"""
        stats = self.stats.copy()
        stats['topics_count'] = len(self.topics)
        stats['active_consumers'] = len(self.consumers)
        return stats
        
    async def close(self) -> None:
        """Close Kafka connections"""
        if self.producer:
            await self.producer.stop()
            
        for consumer in self.consumers.values():
            await consumer.stop()
        self.consumers.clear()


class MessageRouter:
    """Message routing and filtering"""
    
    def __init__(self) -> None:
        self.routes: List[Tuple[Callable[[Message], bool], str]] = []
        
    def add_route(self, condition -> None: Callable[[Message], bool], target_topic -> None: str) -> None:
        """Add routing rule"""
        self.routes.append((condition, target_topic))
        
    def route_message(self, message: Message) -> List[str]:
        """Route message to appropriate topics"""
        topics = [message.topic]  # Always include original topic
        
        for condition, target_topic in self.routes:
            try:
                if condition(message):
                    topics.append(target_topic)
            except Exception as e:
                logger.error(f"Error in routing condition: {str(e)}")
                
        return list(set(topics))  # Remove duplicates


class MessageBrokerService:
    """Event-driven Messaging and Communication Service"""
    
    def __init__(self, name -> None: str = "message_broker_service") -> None:
        self.name = name
        self.brokers: Dict[str, MessageBrokerInterface] = {}
        self.default_broker: Optional[str] = None
        self.router = MessageRouter()
        self.running = False
        self.global_stats = {
            'total_messages_published': 0,
            'total_messages_delivered': 0,
            'total_messages_failed': 0,
            'total_subscriptions': 0
        }
        
    async def start(self) -> None:
        """Start message broker service"""
        self.running = True
        
        # Start all brokers
        for broker in self.brokers.values():
            if hasattr(broker, 'start'):
                await broker.start()
                
        logger.info(f"Started message broker service: {self.name}")
        
    async def stop(self) -> None:
        """Stop message broker service"""
        self.running = False
        
        # Stop all brokers
        for broker in self.brokers.values():
            await broker.close()
            
        logger.info(f"Stopped message broker service: {self.name}")
        
    def add_broker(self, name -> None: str, broker -> None: MessageBrokerInterface, is_default -> None: bool = False) -> None:
        """Add message broker"""
        self.brokers[name] = broker
        if is_default or not self.default_broker:
            self.default_broker = name
        logger.info(f"Added message broker: {name}")
        
    def get_broker(self, name: str = None) -> Optional[MessageBrokerInterface]:
        """Get message broker"""
        broker_name = name or self.default_broker
        return self.brokers.get(broker_name)
        
    async def publish(self, topic: str, payload: Any, 
                     headers: Dict[str, Any] = None,
                     priority: MessagePriority = MessagePriority.NORMAL,
                     ttl: int = None,
                     correlation_id: str = None,
                     broker_name: str = None) -> bool:
        """Publish message"""
        try:
            broker = self.get_broker(broker_name)
            if not broker:
                logger.error(f"No broker available for publishing")
                return False
                
            # Create message
            message = Message(
                id=str(uuid.uuid4()),
                topic=topic,
                payload=payload,
                headers=headers or {},
                priority=priority,
                correlation_id=correlation_id,
                expires_at=datetime.utcnow() + timedelta(seconds=ttl) if ttl else None
            )
            
            # Route message
            topics = self.router.route_message(message)
            
            # Publish to all routed topics
            success = True
            for routed_topic in topics:
                routed_message = Message(
                    id=message.id,
                    topic=routed_topic,
                    payload=message.payload,
                    headers=message.headers,
                    priority=message.priority,
                    correlation_id=message.correlation_id,
                    expires_at=message.expires_at
                )
                
                if not await broker.publish(routed_message):
                    success = False
                    
            if success:
                self.global_stats['total_messages_published'] += 1
                
            return success
            
        except Exception as e:
            logger.error(f"Error publishing message: {str(e)}")
            return False
            
    async def subscribe(self, topic: str, handler: MessageHandler,
                       consumer_group: str = None, broker_name: str = None) -> str:
        """Subscribe to topic"""
        try:
            broker = self.get_broker(broker_name)
            if not broker:
                logger.error(f"No broker available for subscription")
                return ""
                
            subscription_id = await broker.subscribe(topic, handler, consumer_group)
            if subscription_id:
                self.global_stats['total_subscriptions'] += 1
                
            return subscription_id
            
        except Exception as e:
            logger.error(f"Error subscribing to topic: {str(e)}")
            return ""
            
    async def unsubscribe(self, subscription_id: str, broker_name: str = None) -> bool:
        """Unsubscribe from topic"""
        try:
            broker = self.get_broker(broker_name)
            if not broker:
                return False
                
            success = await broker.unsubscribe(subscription_id)
            if success:
                self.global_stats['total_subscriptions'] -= 1
                
            return success
            
        except Exception as e:
            logger.error(f"Error unsubscribing: {str(e)}")
            return False
            
    async def create_topic(self, config: TopicConfiguration, broker_name: str = None) -> bool:
        """Create topic"""
        broker = self.get_broker(broker_name)
        if not broker:
            return False
        return await broker.create_topic(config)
        
    async def delete_topic(self, topic: str, broker_name: str = None) -> bool:
        """Delete topic"""
        broker = self.get_broker(broker_name)
        if not broker:
            return False
        return await broker.delete_topic(topic)
        
    def add_route(self, condition -> None: Callable[[Message], bool], target_topic -> None: str) -> None:
        """Add message routing rule"""
        self.router.add_route(condition, target_topic)
        
    async def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        broker_stats = {}
        for name, broker in self.brokers.items():
            try:
                broker_stats[name] = await broker.get_stats()
            except Exception as e:
                logger.error(f"Error getting stats from broker {name}: {str(e)}")
                
        return {
            "name": self.name,
            "status": "running" if self.running else "stopped",
            "brokers_count": len(self.brokers),
            "default_broker": self.default_broker,
            "global_stats": self.global_stats,
            "broker_stats": broker_stats,
            "timestamp": datetime.utcnow().isoformat()
        }


def create_message_broker_service(config: Dict[str, Any] = None) -> MessageBrokerService:
    """Factory function to create Message Broker service"""
    config = config or {}
    service_name = config.get('name', 'message_broker_service')
    
    service = MessageBrokerService(service_name)
    
    # Add brokers
    if 'brokers' in config:
        for broker_config in config['brokers']:
            broker_type = broker_config.get('type')
            name = broker_config.get('name', broker_type)
            is_default = broker_config.get('is_default', False)
            
            if broker_type == 'memory':
                broker = MemoryMessageBroker()
                service.add_broker(name, broker, is_default)
                
            elif broker_type == 'kafka':
                broker = KafkaMessageBroker(
                    brokers=broker_config.get('brokers', ['localhost:9092']),
                    client_id=broker_config.get('client_id', 'ainflue')
                )
                service.add_broker(name, broker, is_default)
                
    # Add default memory broker if no brokers configured
    if not service.brokers:
        memory_broker = MemoryMessageBroker()
        service.add_broker('memory', memory_broker, True)
        
    # Add routing rules
    if 'routing_rules' in config:
        for rule_config in config['routing_rules']:
            # This would need more sophisticated rule parsing
            pass
            
    return service


__all__ = [
    'MessageBrokerService', 'Message', 'MessageHandler', 'TopicConfiguration',
    'MessagePriority', 'MessageStatus', 'BrokerType', 'DeliveryGuarantee',
    'MemoryMessageBroker', 'KafkaMessageBroker', 'MessageRouter',
    'create_message_broker_service'
]