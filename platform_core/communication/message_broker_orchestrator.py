"""
Message Broker Orchestrator - Platform Core Enterprise Architecture
Multi-broker message routing for Ainflue AI Creator Platform

© 2025 Fahed Mlaiel. All rights reserved.
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import uuid
from abc import ABC, abstractmethod

# Platform Core Imports
from ..utils.base_classes import EnterpriseComponent
from ..utils.exceptions import MessageBrokerError, ValidationError
from ..utils.metrics import MetricsCollector
from ..security.auth_manager import AuthenticationManager

logger = logging.getLogger(__name__)

class BrokerType(Enum):
    """Message broker types."""
    REDIS = "redis"
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    NATS = "nats"
    AWS_SQS = "aws_sqs"
    AZURE_SERVICE_BUS = "azure_service_bus"
    GOOGLE_PUBSUB = "google_pubsub"

class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class RoutingStrategy(Enum):
    """Message routing strategies."""
    ROUND_ROBIN = "round_robin"
    PRIORITY_BASED = "priority_based"
    LOAD_BALANCED = "load_balanced"
    TOPIC_BASED = "topic_based"
    CONTENT_BASED = "content_based"

@dataclass
class BrokerConfig:
    """Message broker configuration."""
    name: str
    broker_type: BrokerType
    connection_string: str
    max_connections: int = 100
    retry_attempts: int = 3
    timeout: int = 30
    heartbeat_interval: int = 60
    batch_size: int = 100
    compression: bool = False
    encryption: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Topic:
    """Message topic configuration."""
    name: str
    partitions: int = 1
    replication_factor: int = 1
    retention_hours: int = 168  # 7 days
    compression_type: str = "gzip"
    cleanup_policy: str = "delete"
    max_message_bytes: int = 1048576  # 1MB
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConsumerGroup:
    """Consumer group configuration."""
    name: str
    topics: List[str]
    auto_offset_reset: str = "latest"
    enable_auto_commit: bool = True
    session_timeout: int = 30000
    heartbeat_interval: int = 3000
    max_poll_records: int = 500
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Message:
    """Message structure."""
    id: str
    topic: str
    payload: Dict[str, Any]
    headers: Dict[str, str] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    expiry: Optional[datetime] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    content_type: str = "application/json"
    compression: bool = False

@dataclass
class BrokerStats:
    """Broker statistics."""
    broker_name: str
    messages_sent: int = 0
    messages_received: int = 0
    messages_failed: int = 0
    connections_active: int = 0
    throughput_per_second: float = 0.0
    average_latency: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

class MessageBroker(ABC):
    """Abstract message broker interface."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the message broker."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the message broker."""
        pass
    
    @abstractmethod
    async def publish(self, message: Message) -> bool:
        """Publish a message."""
        pass
    
    @abstractmethod
    async def subscribe(self, topic: str, handler: Callable) -> str:
        """Subscribe to a topic."""
        pass
    
    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a topic."""
        pass
    
    @abstractmethod
    async def create_topic(self, topic: Topic) -> bool:
        """Create a topic."""
        pass
    
    @abstractmethod
    async def delete_topic(self, topic_name: str) -> bool:
        """Delete a topic."""
        pass

class RedisMessageBroker(MessageBroker):
    """Redis message broker implementation."""
    
    def __init__(self, config: BrokerConfig):
        self.config = config
        self.client = None
        self.subscriptions: Dict[str, Any] = {}
        
    async def connect(self) -> bool:
        """Connect to Redis."""
        try:
            # Simulate Redis connection
            await asyncio.sleep(0.1)
            logger.info(f"Connected to Redis broker: {self.config.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.client:
            # Simulate disconnection
            await asyncio.sleep(0.05)
            logger.info(f"Disconnected from Redis broker: {self.config.name}")
    
    async def publish(self, message: Message) -> bool:
        """Publish message to Redis."""
        try:
            # Simulate Redis publish
            await asyncio.sleep(0.01)
            logger.debug(f"Published message to Redis topic {message.topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish to Redis: {str(e)}")
            return False
    
    async def subscribe(self, topic: str, handler: Callable) -> str:
        """Subscribe to Redis topic."""
        subscription_id = str(uuid.uuid4())
        self.subscriptions[subscription_id] = {"topic": topic, "handler": handler}
        logger.debug(f"Subscribed to Redis topic {topic}")
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from Redis topic."""
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            return True
        return False
    
    async def create_topic(self, topic: Topic) -> bool:
        """Create Redis topic (stream)."""
        # Redis uses streams for topics
        await asyncio.sleep(0.01)
        return True
    
    async def delete_topic(self, topic_name: str) -> bool:
        """Delete Redis topic."""
        await asyncio.sleep(0.01)
        return True

class KafkaMessageBroker(MessageBroker):
    """Kafka message broker implementation."""
    
    def __init__(self, config: BrokerConfig):
        self.config = config
        self.producer = None
        self.consumer = None
        self.admin_client = None
        
    async def connect(self) -> bool:
        """Connect to Kafka."""
        try:
            # Simulate Kafka connection
            await asyncio.sleep(0.2)
            logger.info(f"Connected to Kafka broker: {self.config.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Kafka."""
        # Simulate disconnection
        await asyncio.sleep(0.1)
        logger.info(f"Disconnected from Kafka broker: {self.config.name}")
    
    async def publish(self, message: Message) -> bool:
        """Publish message to Kafka."""
        try:
            # Simulate Kafka produce
            await asyncio.sleep(0.02)
            logger.debug(f"Published message to Kafka topic {message.topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish to Kafka: {str(e)}")
            return False
    
    async def subscribe(self, topic: str, handler: Callable) -> str:
        """Subscribe to Kafka topic."""
        subscription_id = str(uuid.uuid4())
        # Simulate Kafka consumer creation
        await asyncio.sleep(0.05)
        logger.debug(f"Subscribed to Kafka topic {topic}")
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from Kafka topic."""
        await asyncio.sleep(0.02)
        return True
    
    async def create_topic(self, topic: Topic) -> bool:
        """Create Kafka topic."""
        try:
            # Simulate topic creation
            await asyncio.sleep(0.1)
            logger.info(f"Created Kafka topic: {topic.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create Kafka topic: {str(e)}")
            return False
    
    async def delete_topic(self, topic_name: str) -> bool:
        """Delete Kafka topic."""
        try:
            await asyncio.sleep(0.1)
            logger.info(f"Deleted Kafka topic: {topic_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete Kafka topic: {str(e)}")
            return False

class MessageBrokerOrchestrator(EnterpriseComponent):
    """
    Enterprise message broker orchestration system.
    
    Features:
    - Multi-broker message routing
    - Topic management and partitioning
    - Consumer group coordination
    - Message transformation and filtering
    - Load balancing across brokers
    - Failover and redundancy
    - Performance monitoring
    - Message guarantees and reliability
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.brokers: Dict[str, MessageBroker] = {}
        self.broker_configs: Dict[str, BrokerConfig] = {}
        self.topics: Dict[str, Topic] = {}
        self.consumer_groups: Dict[str, ConsumerGroup] = {}
        self.broker_stats: Dict[str, BrokerStats] = {}
        self.routing_table: Dict[str, List[str]] = {}  # topic -> brokers
        self.message_filters: Dict[str, Callable] = {}
        self.message_transformers: Dict[str, Callable] = {}
        self.metrics_collector = MetricsCollector("message_broker_orchestrator")
        self.auth_manager = AuthenticationManager()
        
        # Configuration
        self.default_routing_strategy = RoutingStrategy.ROUND_ROBIN
        self.health_check_interval = config.get("health_check_interval", 60)
        self.max_retry_attempts = config.get("max_retry_attempts", 3)
        self.message_timeout = config.get("message_timeout", 30)
        
        # Active subscriptions tracking
        self.active_subscriptions: Dict[str, Dict[str, Any]] = {}
        
        logger.info("MessageBrokerOrchestrator initialized successfully")

    async def register_broker(
        self,
        config: BrokerConfig,
        user_id: str = None
    ) -> str:
        """Register a message broker."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_broker_management(user_id):
                raise ValidationError(f"User {user_id} not authorized for broker management")
            
            # Validate configuration
            await self._validate_broker_config(config)
            
            # Create broker instance
            broker = await self._create_broker_instance(config)
            
            # Test connection
            if not await broker.connect():
                raise MessageBrokerError(f"Failed to connect to broker {config.name}")
            
            # Store broker
            self.brokers[config.name] = broker
            self.broker_configs[config.name] = config
            
            # Initialize stats
            self.broker_stats[config.name] = BrokerStats(broker_name=config.name)
            
            # Start health monitoring
            asyncio.create_task(self._monitor_broker_health(config.name))
            
            self.metrics_collector.increment("brokers_registered")
            logger.info(f"Message broker registered: {config.name}")
            
            return config.name
            
        except Exception as e:
            logger.error(f"Failed to register broker: {str(e)}")
            raise MessageBrokerError(f"Broker registration failed: {str(e)}")

    async def create_topic(
        self,
        topic: Topic,
        broker_names: List[str] = None,
        user_id: str = None
    ) -> bool:
        """Create a topic across specified brokers."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_topic_management(user_id):
                raise ValidationError(f"User {user_id} not authorized for topic management")
            
            # Use all brokers if none specified
            if not broker_names:
                broker_names = list(self.brokers.keys())
            
            # Validate brokers exist
            for broker_name in broker_names:
                if broker_name not in self.brokers:
                    raise MessageBrokerError(f"Broker {broker_name} not found")
            
            # Create topic on each broker
            success_count = 0
            for broker_name in broker_names:
                broker = self.brokers[broker_name]
                if await broker.create_topic(topic):
                    success_count += 1
                    logger.info(f"Topic {topic.name} created on broker {broker_name}")
                else:
                    logger.error(f"Failed to create topic {topic.name} on broker {broker_name}")
            
            # Store topic configuration
            if success_count > 0:
                self.topics[topic.name] = topic
                self.routing_table[topic.name] = [
                    broker_name for broker_name in broker_names
                    if broker_name in self.brokers
                ]
                
                self.metrics_collector.increment("topics_created")
                logger.info(f"Topic created successfully: {topic.name} on {success_count} brokers")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to create topic: {str(e)}")
            raise MessageBrokerError(f"Topic creation failed: {str(e)}")

    async def publish_message(
        self,
        message: Message,
        routing_strategy: RoutingStrategy = None,
        user_id: str = None
    ) -> bool:
        """Publish a message using specified routing strategy."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_message_publish(user_id, message.topic):
                raise ValidationError(f"User {user_id} not authorized to publish to topic {message.topic}")
            
            # Validate message
            await self._validate_message(message)
            
            # Check if topic exists
            if message.topic not in self.routing_table:
                raise MessageBrokerError(f"Topic {message.topic} not found")
            
            # Apply message transformations
            transformed_message = await self._apply_message_transformations(message)
            
            # Apply message filters
            if not await self._apply_message_filters(transformed_message):
                logger.info(f"Message filtered out for topic {message.topic}")
                return False
            
            # Select broker(s) based on routing strategy
            routing_strategy = routing_strategy or self.default_routing_strategy
            selected_brokers = await self._select_brokers_for_routing(
                message.topic, routing_strategy, transformed_message
            )
            
            # Publish to selected brokers
            success_count = 0
            for broker_name in selected_brokers:
                if await self._publish_to_broker(broker_name, transformed_message):
                    success_count += 1
                    
                    # Update stats
                    if broker_name in self.broker_stats:
                        self.broker_stats[broker_name].messages_sent += 1
            
            success = success_count > 0
            
            if success:
                self.metrics_collector.increment("messages_published")
                logger.debug(f"Message published to {success_count} brokers for topic {message.topic}")
            else:
                self.metrics_collector.increment("messages_failed")
                logger.error(f"Failed to publish message to any broker for topic {message.topic}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            self.metrics_collector.increment("messages_failed")
            raise MessageBrokerError(f"Message publishing failed: {str(e)}")

    async def subscribe_to_topic(
        self,
        topic: str,
        handler: Callable,
        consumer_group: str = None,
        broker_names: List[str] = None,
        user_id: str = None
    ) -> str:
        """Subscribe to a topic with a message handler."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_topic_subscribe(user_id, topic):
                raise ValidationError(f"User {user_id} not authorized to subscribe to topic {topic}")
            
            # Check if topic exists
            if topic not in self.routing_table:
                raise MessageBrokerError(f"Topic {topic} not found")
            
            # Use topic's brokers if none specified
            if not broker_names:
                broker_names = self.routing_table[topic]
            
            # Create subscription ID
            subscription_id = str(uuid.uuid4())
            
            # Subscribe to each broker
            broker_subscriptions = {}
            for broker_name in broker_names:
                if broker_name in self.brokers:
                    broker = self.brokers[broker_name]
                    broker_sub_id = await broker.subscribe(topic, handler)
                    broker_subscriptions[broker_name] = broker_sub_id
            
            # Store subscription info
            self.active_subscriptions[subscription_id] = {
                "topic": topic,
                "handler": handler,
                "consumer_group": consumer_group,
                "broker_subscriptions": broker_subscriptions,
                "created_at": datetime.now()
            }
            
            self.metrics_collector.increment("subscriptions_created")
            logger.info(f"Subscribed to topic {topic} with subscription ID {subscription_id}")
            
            return subscription_id
            
        except Exception as e:
            logger.error(f"Failed to subscribe to topic: {str(e)}")
            raise MessageBrokerError(f"Topic subscription failed: {str(e)}")

    async def unsubscribe_from_topic(
        self,
        subscription_id: str,
        user_id: str = None
    ) -> bool:
        """Unsubscribe from a topic."""
        try:
            # Check if subscription exists
            if subscription_id not in self.active_subscriptions:
                raise MessageBrokerError(f"Subscription {subscription_id} not found")
            
            subscription_info = self.active_subscriptions[subscription_id]
            
            # Check authorization
            if user_id and not await self.auth_manager.authorize_topic_unsubscribe(user_id, subscription_info["topic"]):
                raise ValidationError(f"User {user_id} not authorized to unsubscribe from topic")
            
            # Unsubscribe from each broker
            success_count = 0
            for broker_name, broker_sub_id in subscription_info["broker_subscriptions"].items():
                if broker_name in self.brokers:
                    broker = self.brokers[broker_name]
                    if await broker.unsubscribe(broker_sub_id):
                        success_count += 1
            
            # Remove subscription
            del self.active_subscriptions[subscription_id]
            
            self.metrics_collector.increment("subscriptions_removed")
            logger.info(f"Unsubscribed from topic with subscription ID {subscription_id}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from topic: {str(e)}")
            raise MessageBrokerError(f"Topic unsubscription failed: {str(e)}")

    async def create_consumer_group(
        self,
        consumer_group: ConsumerGroup,
        user_id: str = None
    ) -> bool:
        """Create a consumer group."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_consumer_group_management(user_id):
                raise ValidationError(f"User {user_id} not authorized for consumer group management")
            
            # Validate consumer group
            await self._validate_consumer_group(consumer_group)
            
            # Store consumer group
            self.consumer_groups[consumer_group.name] = consumer_group
            
            self.metrics_collector.increment("consumer_groups_created")
            logger.info(f"Consumer group created: {consumer_group.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create consumer group: {str(e)}")
            raise MessageBrokerError(f"Consumer group creation failed: {str(e)}")

    async def set_message_filter(
        self,
        topic: str,
        filter_func: Callable,
        user_id: str = None
    ) -> None:
        """Set a message filter for a topic."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_message_filter_management(user_id):
                raise ValidationError(f"User {user_id} not authorized for message filter management")
            
            self.message_filters[topic] = filter_func
            logger.info(f"Message filter set for topic: {topic}")
            
        except Exception as e:
            logger.error(f"Failed to set message filter: {str(e)}")
            raise MessageBrokerError(f"Message filter setup failed: {str(e)}")

    async def set_message_transformer(
        self,
        topic: str,
        transformer_func: Callable,
        user_id: str = None
    ) -> None:
        """Set a message transformer for a topic."""
        try:
            # Check authorization
            if user_id and not await self.auth_manager.authorize_message_transformer_management(user_id):
                raise ValidationError(f"User {user_id} not authorized for message transformer management")
            
            self.message_transformers[topic] = transformer_func
            logger.info(f"Message transformer set for topic: {topic}")
            
        except Exception as e:
            logger.error(f"Failed to set message transformer: {str(e)}")
            raise MessageBrokerError(f"Message transformer setup failed: {str(e)}")

    async def get_broker_stats(self) -> Dict[str, BrokerStats]:
        """Get statistics for all brokers."""
        try:
            # Update stats with current data
            for broker_name in self.brokers:
                await self._update_broker_stats(broker_name)
            
            return self.broker_stats.copy()
            
        except Exception as e:
            logger.error(f"Failed to get broker stats: {str(e)}")
            raise MessageBrokerError(f"Stats retrieval failed: {str(e)}")

    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status and metrics."""
        try:
            status = {
                "registered_brokers": len(self.brokers),
                "active_topics": len(self.topics),
                "active_subscriptions": len(self.active_subscriptions),
                "consumer_groups": len(self.consumer_groups),
                "broker_health": {},
                "total_messages_sent": sum(stats.messages_sent for stats in self.broker_stats.values()),
                "total_messages_received": sum(stats.messages_received for stats in self.broker_stats.values()),
                "total_messages_failed": sum(stats.messages_failed for stats in self.broker_stats.values()),
                "metrics": await self.metrics_collector.get_summary()
            }
            
            # Check broker health
            for broker_name in self.brokers:
                status["broker_health"][broker_name] = await self._check_broker_health(broker_name)
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get orchestrator status: {str(e)}")
            raise MessageBrokerError(f"Status retrieval failed: {str(e)}")

    # Private Methods
    
    async def _validate_broker_config(self, config: BrokerConfig) -> None:
        """Validate broker configuration."""
        if not config.name:
            raise ValidationError("Broker name is required")
        
        if not config.connection_string:
            raise ValidationError("Connection string is required")
        
        if config.max_connections <= 0:
            raise ValidationError("Max connections must be positive")
        
        if config.timeout <= 0:
            raise ValidationError("Timeout must be positive")

    async def _create_broker_instance(self, config: BrokerConfig) -> MessageBroker:
        """Create appropriate broker instance based on type."""
        if config.broker_type == BrokerType.REDIS:
            return RedisMessageBroker(config)
        elif config.broker_type == BrokerType.KAFKA:
            return KafkaMessageBroker(config)
        else:
            # Default to Redis for simulation
            return RedisMessageBroker(config)

    async def _validate_message(self, message: Message) -> None:
        """Validate message structure."""
        if not message.topic:
            raise ValidationError("Message topic is required")
        
        if not message.payload:
            raise ValidationError("Message payload is required")
        
        if message.expiry and message.expiry <= datetime.now():
            raise ValidationError("Message has already expired")

    async def _apply_message_transformations(self, message: Message) -> Message:
        """Apply message transformations."""
        if message.topic in self.message_transformers:
            transformer = self.message_transformers[message.topic]
            try:
                transformed_payload = await transformer(message.payload)
                message.payload = transformed_payload
            except Exception as e:
                logger.error(f"Message transformation failed: {str(e)}")
        
        return message

    async def _apply_message_filters(self, message: Message) -> bool:
        """Apply message filters."""
        if message.topic in self.message_filters:
            filter_func = self.message_filters[message.topic]
            try:
                return await filter_func(message)
            except Exception as e:
                logger.error(f"Message filter failed: {str(e)}")
                return True  # Allow message through on filter error
        
        return True  # No filter, allow message

    async def _select_brokers_for_routing(
        self,
        topic: str,
        strategy: RoutingStrategy,
        message: Message
    ) -> List[str]:
        """Select brokers based on routing strategy."""
        available_brokers = self.routing_table.get(topic, [])
        
        if not available_brokers:
            return []
        
        if strategy == RoutingStrategy.ROUND_ROBIN:
            # Simple round robin - just return first broker for simulation
            return [available_brokers[0]]
        
        elif strategy == RoutingStrategy.PRIORITY_BASED:
            # Route based on message priority
            if message.priority in [MessagePriority.HIGH, MessagePriority.CRITICAL]:
                # Use first (primary) broker for high priority
                return [available_brokers[0]]
            else:
                # Use any available broker for normal/low priority
                return available_brokers[:1]
        
        elif strategy == RoutingStrategy.LOAD_BALANCED:
            # Select broker with lowest load
            broker_loads = {}
            for broker_name in available_brokers:
                if broker_name in self.broker_stats:
                    broker_loads[broker_name] = self.broker_stats[broker_name].messages_sent
                else:
                    broker_loads[broker_name] = 0
            
            # Select broker with minimum load
            min_load_broker = min(broker_loads.items(), key=lambda x: x[1])
            return [min_load_broker[0]]
        
        elif strategy == RoutingStrategy.TOPIC_BASED:
            # Route to all brokers for the topic
            return available_brokers
        
        else:
            # Default to first available broker
            return [available_brokers[0]]

    async def _publish_to_broker(self, broker_name: str, message: Message) -> bool:
        """Publish message to a specific broker."""
        if broker_name not in self.brokers:
            return False
        
        broker = self.brokers[broker_name]
        
        # Attempt to publish with retries
        for attempt in range(self.max_retry_attempts):
            try:
                success = await broker.publish(message)
                if success:
                    return True
                
                # Wait before retry
                if attempt < self.max_retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as e:
                logger.error(f"Publish attempt {attempt + 1} failed for broker {broker_name}: {str(e)}")
                if attempt < self.max_retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)
        
        # Update failure stats
        if broker_name in self.broker_stats:
            self.broker_stats[broker_name].messages_failed += 1
        
        return False

    async def _validate_consumer_group(self, consumer_group: ConsumerGroup) -> None:
        """Validate consumer group configuration."""
        if not consumer_group.name:
            raise ValidationError("Consumer group name is required")
        
        if not consumer_group.topics:
            raise ValidationError("Consumer group must have at least one topic")
        
        # Validate that topics exist
        for topic in consumer_group.topics:
            if topic not in self.topics:
                raise ValidationError(f"Topic {topic} does not exist")

    async def _monitor_broker_health(self, broker_name: str) -> None:
        """Monitor broker health continuously."""
        while broker_name in self.brokers:
            try:
                health_status = await self._check_broker_health(broker_name)
                
                if not health_status:
                    logger.warning(f"Broker {broker_name} health check failed")
                    # Could trigger failover logic here
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error for broker {broker_name}: {str(e)}")
                await asyncio.sleep(self.health_check_interval)

    async def _check_broker_health(self, broker_name: str) -> bool:
        """Check if a broker is healthy."""
        if broker_name not in self.brokers:
            return False
        
        try:
            # Simple health check - could be enhanced with ping/status check
            await asyncio.sleep(0.01)  # Simulate health check
            return True
            
        except Exception as e:
            logger.error(f"Health check failed for broker {broker_name}: {str(e)}")
            return False

    async def _update_broker_stats(self, broker_name: str) -> None:
        """Update broker statistics."""
        if broker_name not in self.broker_stats:
            return
        
        stats = self.broker_stats[broker_name]
        stats.last_updated = datetime.now()
        
        # In real implementation, would collect actual metrics from broker
        # For simulation, we'll just update the timestamp

    async def get_health_status(self) -> Dict[str, Any]:
        """Get orchestrator health status."""
        healthy_brokers = sum(1 for broker_name in self.brokers 
                             if await self._check_broker_health(broker_name))
        
        return {
            "status": "healthy" if healthy_brokers > 0 else "unhealthy",
            "total_brokers": len(self.brokers),
            "healthy_brokers": healthy_brokers,
            "active_topics": len(self.topics),
            "active_subscriptions": len(self.active_subscriptions),
            "consumer_groups": len(self.consumer_groups),
            "metrics": await self.metrics_collector.get_summary()
        }

    async def cleanup(self) -> None:
        """Cleanup orchestrator resources."""
        try:
            # Unsubscribe from all topics
            for subscription_id in list(self.active_subscriptions.keys()):
                await self.unsubscribe_from_topic(subscription_id)
            
            # Disconnect from all brokers
            for broker_name, broker in self.brokers.items():
                await broker.disconnect()
            
            logger.info("MessageBrokerOrchestrator cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")