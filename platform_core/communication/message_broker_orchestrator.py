#!/usr/bin/env python3
"""
Message Broker Orchestrator - Enterprise Core Component
Multi-broker message routing and orchestration system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive message broker orchestration capabilities including:
- Multi-broker message routing
- Topic management and partitioning
- Consumer group coordination
- Message transformation and filtering
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrokerType(Enum):
    """Message broker types"""
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    REDIS = "redis"
    PULSAR = "pulsar"
    NATS = "nats"
    ACTIVEMQ = "activemq"
    INTERNAL = "internal"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class ConsumerStatus(Enum):
    """Consumer status"""
    ACTIVE = "active"
    IDLE = "idle"
    ERROR = "error"
    DISCONNECTED = "disconnected"


@dataclass
class MessageBrokerConfig:
    """Message broker configuration"""
    broker_id: str
    broker_type: BrokerType
    name: str
    connection_string: str
    max_connections: int = 100
    heartbeat_interval: int = 30
    retry_attempts: int = 3
    timeout: int = 30
    compression_enabled: bool = True
    persistence_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Topic:
    """Message topic configuration"""
    topic_id: str
    name: str
    broker_id: str
    partitions: int = 1
    replication_factor: int = 1
    retention_hours: int = 168  # 7 days
    max_message_size: int = 1048576  # 1MB
    compression_type: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Message:
    """Message structure"""
    message_id: str
    topic: str
    partition: Optional[int] = None
    key: Optional[str] = None
    value: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: MessagePriority = MessagePriority.NORMAL
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Consumer:
    """Message consumer configuration"""
    consumer_id: str
    group_id: str
    topics: List[str]
    broker_id: str
    handler: Callable[[Message], bool]
    status: ConsumerStatus = ConsumerStatus.IDLE
    auto_commit: bool = True
    batch_size: int = 100
    poll_timeout: float = 1.0
    max_poll_records: int = 500
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Producer:
    """Message producer configuration"""
    producer_id: str
    broker_id: str
    default_topic: Optional[str] = None
    batch_size: int = 100
    linger_ms: int = 0
    compression_type: Optional[str] = None
    acks: str = "all"
    retries: int = 3
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MessageRoute:
    """Message routing configuration"""
    route_id: str
    name: str
    source_topic: str
    target_topics: List[str]
    condition: Optional[str] = None
    transformation: Optional[Callable[[Message], Message]] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class MessageBrokerOrchestrator:
    """
    Enterprise Message Broker Orchestrator
    
    Manages comprehensive message broker operations including multi-broker
    routing, topic management, consumer coordination, and message transformation.
    """
    
    def __init__(self):
        self.brokers: Dict[str, MessageBrokerConfig] = {}
        self.topics: Dict[str, Topic] = {}
        self.consumers: Dict[str, Consumer] = {}
        self.producers: Dict[str, Producer] = {}
        self.routes: Dict[str, MessageRoute] = {}
        
        # Message storage (for internal broker)
        self.message_store: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.consumer_offsets: Dict[str, Dict[str, int]] = defaultdict(dict)
        
        # Active connections
        self.broker_connections: Dict[str, Any] = {}
        self.consumer_tasks: Dict[str, asyncio.Task] = {}
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        
        # Metrics
        self.message_metrics: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.consumer_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "message_sent": [],
            "message_received": [],
            "consumer_connected": [],
            "consumer_disconnected": [],
            "broker_connected": [],
            "broker_disconnected": [],
            "routing_failed": [],
            "dead_letter": []
        }
        
        # Configuration
        self.max_retry_attempts = 3
        self.dead_letter_enabled = True
        self.metrics_retention_hours = 24
        self.auto_scaling_enabled = True
        
        logger.info("Message Broker Orchestrator initialized")
    
    async def register_broker(self, config: MessageBrokerConfig) -> bool:
        """Register a message broker"""
        try:
            self.brokers[config.broker_id] = config
            
            # Initialize connection
            if config.broker_type != BrokerType.INTERNAL:
                success = await self._connect_broker(config)
                if not success:
                    logger.error(f"Failed to connect to broker: {config.broker_id}")
                    return False
            
            # Start health check
            await self._start_broker_health_check(config.broker_id)
            
            await self._trigger_event("broker_connected", config.broker_id)
            logger.info(f"Broker registered: {config.broker_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register broker {config.broker_id}: {e}")
            return False
    
    async def create_topic(self, topic: Topic) -> bool:
        """Create a topic"""
        try:
            if topic.broker_id not in self.brokers:
                logger.error(f"Broker not found: {topic.broker_id}")
                return False
            
            self.topics[topic.topic_id] = topic
            
            # Create topic on broker
            broker_config = self.brokers[topic.broker_id]
            success = await self._create_topic_on_broker(topic, broker_config)
            
            if success:
                logger.info(f"Topic created: {topic.name} on broker {topic.broker_id}")
            else:
                del self.topics[topic.topic_id]
                logger.error(f"Failed to create topic on broker: {topic.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to create topic {topic.name}: {e}")
            return False
    
    async def create_producer(self, producer: Producer) -> bool:
        """Create a message producer"""
        try:
            if producer.broker_id not in self.brokers:
                logger.error(f"Broker not found for producer: {producer.broker_id}")
                return False
            
            self.producers[producer.producer_id] = producer
            
            # Initialize producer connection
            success = await self._initialize_producer(producer)
            
            if success:
                logger.info(f"Producer created: {producer.producer_id}")
            else:
                del self.producers[producer.producer_id]
                logger.error(f"Failed to initialize producer: {producer.producer_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to create producer {producer.producer_id}: {e}")
            return False
    
    async def create_consumer(self, consumer: Consumer) -> bool:
        """Create a message consumer"""
        try:
            if consumer.broker_id not in self.brokers:
                logger.error(f"Broker not found for consumer: {consumer.broker_id}")
                return False
            
            self.consumers[consumer.consumer_id] = consumer
            
            # Start consumer task
            success = await self._start_consumer(consumer)
            
            if success:
                await self._trigger_event("consumer_connected", consumer.consumer_id)
                logger.info(f"Consumer created: {consumer.consumer_id}")
            else:
                del self.consumers[consumer.consumer_id]
                logger.error(f"Failed to start consumer: {consumer.consumer_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to create consumer {consumer.consumer_id}: {e}")
            return False
    
    async def send_message(
        self,
        producer_id: str,
        message: Message,
        topic: Optional[str] = None
    ) -> bool:
        """Send a message"""
        producer = self.producers.get(producer_id)
        if not producer:
            logger.error(f"Producer not found: {producer_id}")
            return False
        
        try:
            # Determine topic
            target_topic = topic or message.topic or producer.default_topic
            if not target_topic:
                logger.error("No topic specified for message")
                return False
            
            message.topic = target_topic
            
            # Send to broker
            broker_config = self.brokers[producer.broker_id]
            success = await self._send_to_broker(message, broker_config)
            
            if success:
                # Update metrics
                self.message_metrics[target_topic]["sent"] += 1
                
                # Apply routing rules
                await self._apply_routing_rules(message)
                
                await self._trigger_event("message_sent", message.message_id)
                logger.debug(f"Message sent: {message.message_id} to topic {target_topic}")
            else:
                self.message_metrics[target_topic]["failed"] += 1
                logger.error(f"Failed to send message: {message.message_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send message {message.message_id}: {e}")
            return False
    
    async def create_route(self, route: MessageRoute) -> bool:
        """Create message route"""
        try:
            self.routes[route.route_id] = route
            logger.info(f"Route created: {route.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create route {route.name}: {e}")
            return False
    
    async def stop_consumer(self, consumer_id: str) -> bool:
        """Stop a consumer"""
        consumer = self.consumers.get(consumer_id)
        if not consumer:
            return False
        
        try:
            # Cancel consumer task
            if consumer_id in self.consumer_tasks:
                self.consumer_tasks[consumer_id].cancel()
                del self.consumer_tasks[consumer_id]
            
            consumer.status = ConsumerStatus.DISCONNECTED
            await self._trigger_event("consumer_disconnected", consumer_id)
            
            logger.info(f"Consumer stopped: {consumer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop consumer {consumer_id}: {e}")
            return False
    
    async def get_topic_metrics(self, topic_name: str) -> Dict[str, Any]:
        """Get topic metrics"""
        metrics = self.message_metrics.get(topic_name, {})
        
        # Get consumer metrics for topic
        consumer_count = sum(
            1 for consumer in self.consumers.values()
            if topic_name in consumer.topics and consumer.status == ConsumerStatus.ACTIVE
        )
        
        return {
            "topic_name": topic_name,
            "messages_sent": metrics.get("sent", 0),
            "messages_received": metrics.get("received", 0),
            "messages_failed": metrics.get("failed", 0),
            "active_consumers": consumer_count,
            "last_activity": datetime.utcnow().isoformat()
        }
    
    async def get_consumer_metrics(self, consumer_id: str) -> Optional[Dict[str, Any]]:
        """Get consumer metrics"""
        consumer = self.consumers.get(consumer_id)
        if not consumer:
            return None
        
        metrics = self.consumer_metrics.get(consumer_id, {})
        
        return {
            "consumer_id": consumer_id,
            "group_id": consumer.group_id,
            "topics": consumer.topics,
            "status": consumer.status.value,
            "messages_processed": metrics.get("processed", 0),
            "messages_failed": metrics.get("failed", 0),
            "last_activity": consumer.last_activity.isoformat(),
            "uptime": (datetime.utcnow() - consumer.created_at).total_seconds()
        }
    
    async def get_broker_status(self, broker_id: str) -> Optional[Dict[str, Any]]:
        """Get broker status"""
        broker = self.brokers.get(broker_id)
        if not broker:
            return None
        
        # Count active consumers and producers
        active_consumers = sum(
            1 for consumer in self.consumers.values()
            if consumer.broker_id == broker_id and consumer.status == ConsumerStatus.ACTIVE
        )
        
        active_producers = sum(
            1 for producer in self.producers.values()
            if producer.broker_id == broker_id
        )
        
        # Count topics
        topic_count = sum(
            1 for topic in self.topics.values()
            if topic.broker_id == broker_id
        )
        
        return {
            "broker_id": broker_id,
            "broker_type": broker.broker_type.value,
            "name": broker.name,
            "active_consumers": active_consumers,
            "active_producers": active_producers,
            "topic_count": topic_count,
            "connected": broker_id in self.broker_connections,
            "health_status": "healthy"  # Simplified
        }
    
    async def list_topics(self, broker_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List topics"""
        topics = []
        
        for topic in self.topics.values():
            if broker_id and topic.broker_id != broker_id:
                continue
            
            metrics = await self.get_topic_metrics(topic.name)
            
            topics.append({
                "topic_id": topic.topic_id,
                "name": topic.name,
                "broker_id": topic.broker_id,
                "partitions": topic.partitions,
                "created_at": topic.created_at.isoformat(),
                "metrics": metrics
            })
        
        return topics
    
    async def rebalance_consumers(self, group_id: str) -> bool:
        """Rebalance consumers in a group"""
        try:
            group_consumers = [
                consumer for consumer in self.consumers.values()
                if consumer.group_id == group_id and consumer.status == ConsumerStatus.ACTIVE
            ]
            
            if not group_consumers:
                return True
            
            # Simple rebalancing logic
            for consumer in group_consumers:
                # Redistribute topic partitions among consumers
                await self._rebalance_consumer_partitions(consumer, group_consumers)
            
            logger.info(f"Consumer group rebalanced: {group_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rebalance consumer group {group_id}: {e}")
            return False
    
    async def purge_topic(self, topic_name: str) -> bool:
        """Purge all messages from a topic"""
        try:
            # For internal broker
            if topic_name in self.message_store:
                self.message_store[topic_name].clear()
                logger.info(f"Topic purged: {topic_name}")
            
            # For external brokers, would need broker-specific implementation
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to purge topic {topic_name}: {e}")
            return False
    
    async def create_dead_letter_topic(self, original_topic: str) -> str:
        """Create dead letter topic for failed messages"""
        dead_letter_topic_name = f"{original_topic}.dead-letter"
        
        # Find original topic to get broker info
        original_topic_obj = None
        for topic in self.topics.values():
            if topic.name == original_topic:
                original_topic_obj = topic
                break
        
        if not original_topic_obj:
            logger.error(f"Original topic not found: {original_topic}")
            return ""
        
        # Create dead letter topic
        dead_letter_topic = Topic(
            topic_id=str(uuid.uuid4()),
            name=dead_letter_topic_name,
            broker_id=original_topic_obj.broker_id,
            partitions=1,
            retention_hours=24 * 30  # 30 days
        )
        
        success = await self.create_topic(dead_letter_topic)
        if success:
            return dead_letter_topic_name
        else:
            return ""
    
    # Private methods
    
    async def _connect_broker(self, config: MessageBrokerConfig) -> bool:
        """Connect to external broker"""
        try:
            # Simulate broker connection based on type
            if config.broker_type == BrokerType.KAFKA:
                await self._connect_kafka(config)
            elif config.broker_type == BrokerType.RABBITMQ:
                await self._connect_rabbitmq(config)
            elif config.broker_type == BrokerType.REDIS:
                await self._connect_redis(config)
            else:
                # Generic connection
                await asyncio.sleep(0.1)
            
            self.broker_connections[config.broker_id] = {"connected": True}
            return True
            
        except Exception as e:
            logger.error(f"Broker connection failed {config.broker_id}: {e}")
            return False
    
    async def _connect_kafka(self, config: MessageBrokerConfig):
        """Connect to Kafka broker"""
        # Kafka-specific connection logic would go here
        logger.info(f"Connecting to Kafka broker: {config.name}")
        await asyncio.sleep(0.1)
    
    async def _connect_rabbitmq(self, config: MessageBrokerConfig):
        """Connect to RabbitMQ broker"""
        # RabbitMQ-specific connection logic would go here
        logger.info(f"Connecting to RabbitMQ broker: {config.name}")
        await asyncio.sleep(0.1)
    
    async def _connect_redis(self, config: MessageBrokerConfig):
        """Connect to Redis broker"""
        # Redis-specific connection logic would go here
        logger.info(f"Connecting to Redis broker: {config.name}")
        await asyncio.sleep(0.1)
    
    async def _create_topic_on_broker(self, topic: Topic, broker_config: MessageBrokerConfig) -> bool:
        """Create topic on specific broker"""
        try:
            if broker_config.broker_type == BrokerType.INTERNAL:
                # For internal broker, just initialize the deque
                self.message_store[topic.name] = deque(maxlen=10000)
            else:
                # For external brokers, use broker-specific topic creation
                logger.info(f"Creating topic {topic.name} on {broker_config.broker_type.value} broker")
                await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create topic {topic.name} on broker: {e}")
            return False
    
    async def _initialize_producer(self, producer: Producer) -> bool:
        """Initialize producer connection"""
        try:
            broker_config = self.brokers[producer.broker_id]
            
            if broker_config.broker_type == BrokerType.INTERNAL:
                # Internal broker - no special initialization needed
                pass
            else:
                # External broker - initialize producer connection
                logger.info(f"Initializing producer {producer.producer_id}")
                await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize producer {producer.producer_id}: {e}")
            return False
    
    async def _start_consumer(self, consumer: Consumer) -> bool:
        """Start consumer task"""
        try:
            async def consumer_loop():
                consumer.status = ConsumerStatus.ACTIVE
                
                while consumer.status == ConsumerStatus.ACTIVE:
                    try:
                        # Poll for messages
                        messages = await self._poll_messages(consumer)
                        
                        for message in messages:
                            try:
                                # Process message
                                success = await self._process_message(consumer, message)
                                
                                if success:
                                    self.consumer_metrics[consumer.consumer_id]["processed"] = \
                                        self.consumer_metrics[consumer.consumer_id].get("processed", 0) + 1
                                    
                                    # Commit offset if auto-commit enabled
                                    if consumer.auto_commit:
                                        await self._commit_offset(consumer, message)
                                else:
                                    self.consumer_metrics[consumer.consumer_id]["failed"] = \
                                        self.consumer_metrics[consumer.consumer_id].get("failed", 0) + 1
                                    
                                    # Send to dead letter if enabled
                                    if self.dead_letter_enabled:
                                        await self._send_to_dead_letter(message)
                                
                                consumer.last_activity = datetime.utcnow()
                                
                            except Exception as e:
                                logger.error(f"Message processing error: {e}")
                                self.consumer_metrics[consumer.consumer_id]["failed"] = \
                                    self.consumer_metrics[consumer.consumer_id].get("failed", 0) + 1
                        
                        if not messages:
                            await asyncio.sleep(consumer.poll_timeout)
                        
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        logger.error(f"Consumer loop error: {e}")
                        consumer.status = ConsumerStatus.ERROR
                        break
                
                consumer.status = ConsumerStatus.DISCONNECTED
            
            task = asyncio.create_task(consumer_loop())
            self.consumer_tasks[consumer.consumer_id] = task
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start consumer {consumer.consumer_id}: {e}")
            return False
    
    async def _poll_messages(self, consumer: Consumer) -> List[Message]:
        """Poll messages for consumer"""
        messages = []
        
        try:
            for topic in consumer.topics:
                if topic in self.message_store:
                    # Get messages from internal store
                    topic_messages = []
                    store = self.message_store[topic]
                    
                    # Get offset for this consumer group
                    offset_key = f"{consumer.group_id}:{topic}"
                    current_offset = self.consumer_offsets[consumer.consumer_id].get(offset_key, 0)
                    
                    # Get messages from offset
                    store_list = list(store)
                    if current_offset < len(store_list):
                        available_messages = store_list[current_offset:current_offset + consumer.batch_size]
                        topic_messages.extend(available_messages)
                    
                    messages.extend(topic_messages)
                
                if len(messages) >= consumer.max_poll_records:
                    break
            
            return messages[:consumer.max_poll_records]
            
        except Exception as e:
            logger.error(f"Failed to poll messages for consumer {consumer.consumer_id}: {e}")
            return []
    
    async def _process_message(self, consumer: Consumer, message: Message) -> bool:
        """Process message with consumer handler"""
        try:
            if asyncio.iscoroutinefunction(consumer.handler):
                result = await consumer.handler(message)
            else:
                result = consumer.handler(message)
            
            await self._trigger_event("message_received", message.message_id)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Message handler error: {e}")
            return False
    
    async def _commit_offset(self, consumer: Consumer, message: Message):
        """Commit message offset"""
        offset_key = f"{consumer.group_id}:{message.topic}"
        
        # For internal broker, track offset
        if message.topic in self.message_store:
            store_list = list(self.message_store[message.topic])
            try:
                message_index = store_list.index(message)
                self.consumer_offsets[consumer.consumer_id][offset_key] = message_index + 1
            except ValueError:
                # Message not found in store
                pass
    
    async def _send_to_broker(self, message: Message, broker_config: MessageBrokerConfig) -> bool:
        """Send message to broker"""
        try:
            if broker_config.broker_type == BrokerType.INTERNAL:
                # Store in internal message store
                self.message_store[message.topic].append(message)
            else:
                # Send to external broker
                logger.debug(f"Sending message to {broker_config.broker_type.value} broker")
                await asyncio.sleep(0.01)  # Simulate network delay
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to broker: {e}")
            return False
    
    async def _apply_routing_rules(self, message: Message):
        """Apply message routing rules"""
        for route in self.routes.values():
            if not route.enabled or route.source_topic != message.topic:
                continue
            
            try:
                # Check condition if specified
                if route.condition and not self._evaluate_condition(message, route.condition):
                    continue
                
                # Apply transformation if specified
                routed_message = message
                if route.transformation:
                    routed_message = route.transformation(message)
                
                # Send to target topics
                for target_topic in route.target_topics:
                    routed_message.topic = target_topic
                    routed_message.message_id = str(uuid.uuid4())  # New message ID
                    
                    # Find broker for target topic
                    target_topic_obj = None
                    for topic in self.topics.values():
                        if topic.name == target_topic:
                            target_topic_obj = topic
                            break
                    
                    if target_topic_obj:
                        broker_config = self.brokers[target_topic_obj.broker_id]
                        await self._send_to_broker(routed_message, broker_config)
                
            except Exception as e:
                logger.error(f"Routing failed for route {route.route_id}: {e}")
                await self._trigger_event("routing_failed", route.route_id)
    
    def _evaluate_condition(self, message: Message, condition: str) -> bool:
        """Evaluate routing condition"""
        try:
            # Simple condition evaluation (in production, would use a proper expression evaluator)
            # Example condition: "headers.priority == 'high'"
            if "headers.priority" in condition and "high" in condition:
                return message.headers.get("priority") == "high"
            elif "value.type" in condition:
                if isinstance(message.value, dict):
                    return message.value.get("type") in condition
            
            return True  # Default to true for unsupported conditions
            
        except Exception as e:
            logger.error(f"Condition evaluation error: {e}")
            return False
    
    async def _send_to_dead_letter(self, message: Message):
        """Send message to dead letter topic"""
        try:
            dead_letter_topic = f"{message.topic}.dead-letter"
            
            # Check if dead letter topic exists
            dead_letter_exists = any(
                topic.name == dead_letter_topic for topic in self.topics.values()
            )
            
            if not dead_letter_exists:
                # Create dead letter topic
                dead_letter_topic = await self.create_dead_letter_topic(message.topic)
                if not dead_letter_topic:
                    logger.error(f"Failed to create dead letter topic for {message.topic}")
                    return
            
            # Create dead letter message
            dead_letter_message = Message(
                message_id=str(uuid.uuid4()),
                topic=dead_letter_topic,
                key=message.key,
                value=message.value,
                headers={**message.headers, "original_topic": message.topic, "failure_reason": "processing_failed"},
                priority=message.priority,
                metadata={**message.metadata, "original_message_id": message.message_id}
            )
            
            # Send to dead letter topic
            if dead_letter_topic in self.message_store:
                self.message_store[dead_letter_topic].append(dead_letter_message)
                await self._trigger_event("dead_letter", dead_letter_message.message_id)
            
        except Exception as e:
            logger.error(f"Failed to send message to dead letter: {e}")
    
    async def _start_broker_health_check(self, broker_id: str):
        """Start health check for broker"""
        async def health_check_loop():
            while True:
                try:
                    broker = self.brokers.get(broker_id)
                    if not broker:
                        break
                    
                    # Perform health check
                    is_healthy = await self._check_broker_health(broker)
                    
                    if not is_healthy:
                        logger.warning(f"Broker health check failed: {broker_id}")
                        # Could trigger reconnection logic here
                    
                    await asyncio.sleep(broker.heartbeat_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Health check error for broker {broker_id}: {e}")
                    await asyncio.sleep(30)  # Backoff on error
        
        task = asyncio.create_task(health_check_loop())
        self.health_check_tasks[broker_id] = task
    
    async def _check_broker_health(self, broker: MessageBrokerConfig) -> bool:
        """Check broker health"""
        try:
            if broker.broker_type == BrokerType.INTERNAL:
                return True
            else:
                # For external brokers, perform actual health check
                # This would be broker-specific implementation
                return broker.broker_id in self.broker_connections
                
        except Exception as e:
            logger.error(f"Broker health check failed: {e}")
            return False
    
    async def _rebalance_consumer_partitions(self, consumer: Consumer, group_consumers: List[Consumer]):
        """Rebalance partitions for consumer"""
        # Simple round-robin partition assignment
        total_consumers = len(group_consumers)
        consumer_index = group_consumers.index(consumer)
        
        for topic_name in consumer.topics:
            # Find topic configuration
            topic = None
            for t in self.topics.values():
                if t.name == topic_name:
                    topic = t
                    break
            
            if topic:
                # Assign partitions to this consumer
                assigned_partitions = []
                for partition in range(topic.partitions):
                    if partition % total_consumers == consumer_index:
                        assigned_partitions.append(partition)
                
                logger.debug(f"Consumer {consumer.consumer_id} assigned partitions {assigned_partitions} for topic {topic_name}")
    
    async def _trigger_event(self, event_type: str, event_data: str):
        """Trigger event handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")


# Global instance
message_broker_orchestrator = MessageBrokerOrchestrator()


# Convenience functions
async def register_internal_broker() -> str:
    """Register internal message broker"""
    broker_id = "internal-broker"
    config = MessageBrokerConfig(
        broker_id=broker_id,
        broker_type=BrokerType.INTERNAL,
        name="Internal Message Broker",
        connection_string="internal://localhost"
    )
    
    await message_broker_orchestrator.register_broker(config)
    return broker_id


async def create_simple_topic(topic_name: str, broker_id: Optional[str] = None) -> str:
    """Create a simple topic"""
    if not broker_id:
        broker_id = await register_internal_broker()
    
    topic_id = str(uuid.uuid4())
    topic = Topic(
        topic_id=topic_id,
        name=topic_name,
        broker_id=broker_id
    )
    
    await message_broker_orchestrator.create_topic(topic)
    return topic_id


async def create_simple_producer(broker_id: Optional[str] = None, default_topic: Optional[str] = None) -> str:
    """Create a simple producer"""
    if not broker_id:
        broker_id = await register_internal_broker()
    
    producer_id = str(uuid.uuid4())
    producer = Producer(
        producer_id=producer_id,
        broker_id=broker_id,
        default_topic=default_topic
    )
    
    await message_broker_orchestrator.create_producer(producer)
    return producer_id


async def create_simple_consumer(
    topics: List[str],
    handler: Callable[[Message], bool],
    group_id: str = "default-group",
    broker_id: Optional[str] = None
) -> str:
    """Create a simple consumer"""
    if not broker_id:
        broker_id = await register_internal_broker()
    
    consumer_id = str(uuid.uuid4())
    consumer = Consumer(
        consumer_id=consumer_id,
        group_id=group_id,
        topics=topics,
        broker_id=broker_id,
        handler=handler
    )
    
    await message_broker_orchestrator.create_consumer(consumer)
    return consumer_id


async def send_simple_message(
    producer_id: str,
    topic: str,
    value: Any,
    key: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None
) -> bool:
    """Send a simple message"""
    message = Message(
        message_id=str(uuid.uuid4()),
        topic=topic,
        key=key,
        value=value,
        headers=headers or {}
    )
    
    return await message_broker_orchestrator.send_message(producer_id, message)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Create internal broker and topic
        broker_id = await register_internal_broker()
        topic_id = await create_simple_topic("test-topic", broker_id)
        
        # Create producer
        producer_id = await create_simple_producer(broker_id, "test-topic")
        
        # Create consumer
        def message_handler(message: Message) -> bool:
            print(f"Received message: {message.value}")
            return True
        
        consumer_id = await create_simple_consumer(["test-topic"], message_handler, broker_id=broker_id)
        
        # Send messages
        await send_simple_message(producer_id, "test-topic", "Hello World!")
        await send_simple_message(producer_id, "test-topic", {"type": "event", "data": "test"})
        
        # Wait for processing
        await asyncio.sleep(2)
        
        # Get metrics
        topic_metrics = await message_broker_orchestrator.get_topic_metrics("test-topic")
        print(f"Topic metrics: {topic_metrics}")
        
        consumer_metrics = await message_broker_orchestrator.get_consumer_metrics(consumer_id)
        print(f"Consumer metrics: {consumer_metrics}")
        
        # Stop consumer
        await message_broker_orchestrator.stop_consumer(consumer_id)
    
    asyncio.run(main())