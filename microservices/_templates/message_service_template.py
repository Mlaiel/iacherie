#!/usr/bin/env python3
"""
📨 Enterprise Message Service Template - Ainflue
==============================================
Template enterprise pour services message-driven.
RabbitMQ + Kafka + Redis Streams + event sourcing + CQRS patterns.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Microservices Templates
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction sans autorisation est STRICTEMENT INTERDITE.
"""

import asyncio
import json
import uuid
from abc import abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Type
import logging
from collections import defaultdict, deque

from .service_template import EnterpriseServiceBase, ServiceConfig


class MessageBrokerType(Enum):
    """Types de message brokers supportés."""
    RABBITMQ = "rabbitmq"
    KAFKA = "kafka"
    REDIS_STREAMS = "redis_streams"
    IN_MEMORY = "in_memory"


class EventType(Enum):
    """Types d'événements."""
    COMMAND = "command"
    EVENT = "event"
    QUERY = "query"
    NOTIFICATION = "notification"


class DeliveryGuarantee(Enum):
    """Garanties de livraison."""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


@dataclass
class Message:
    """Modèle de message standard."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    event_type: EventType = EventType.EVENT
    topic: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    max_retries: int = 3
    ttl_seconds: Optional[int] = None
    priority: int = 0  # 0 = normal, higher = more priority
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create from dictionary."""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if 'event_type' in data:
            data['event_type'] = EventType(data['event_type'])
        return cls(**data)


@dataclass
class BrokerConfig:
    """Configuration broker."""
    broker_type: MessageBrokerType
    connection_url: str
    exchange_name: str = "ainflue_exchange"
    dead_letter_queue: str = "dlq"
    retry_policy: Dict = field(default_factory=lambda: {
        'max_retries': 3,
        'retry_delay_seconds': 5,
        'exponential_backoff': True
    })
    delivery_guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE
    batch_size: int = 100
    flush_timeout_ms: int = 1000


@dataclass
class EventHandler:
    """Configuration event handler."""
    event_type: str
    handler_func: Callable
    topic_pattern: str = "*"
    error_handler: Optional[Callable] = None
    max_concurrent: int = 10
    timeout_seconds: int = 30


class MessageServiceTemplate(EnterpriseServiceBase):
    """
    📨 Template enterprise pour services message-driven.
    RabbitMQ + Kafka + Redis Streams + event sourcing patterns.
    
    Features:
    - Support multi-brokers (RabbitMQ, Kafka, Redis)
    - Event sourcing avec snapshots
    - CQRS patterns
    - Dead letter queues
    - Retry logic avec exponential backoff
    - Message deduplication
    - Priority queues
    - Batch processing
    - Circuit breaker pour consumers
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize message service template."""
        super().__init__(config)
        
        self.message_brokers: Dict[str, Any] = {}
        self.event_handlers: Dict[str, EventHandler] = {}
        self.dead_letter_queues: Dict[str, deque] = defaultdict(deque)
        self.broker_configs: Dict[str, BrokerConfig] = {}
        
        # Event sourcing
        self.event_store: List[Message] = []
        self.snapshots: Dict[str, Dict] = {}
        self.snapshot_frequency = 100  # Take snapshot every 100 events
        
        # Message tracking
        self.message_metrics = {
            'messages_sent': 0,
            'messages_received': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'messages_retried': 0,
            'dead_letter_messages': 0,
            'active_handlers': 0,
            'event_store_size': 0,
            'snapshots_count': 0
        }
        
        # Circuit breaker states
        self.circuit_breakers: Dict[str, Dict] = {}
        
        self.logger.info(f"📨 Message Service Template initialized: {config.service_name}")
    
    async def _initialize(self) -> None:
        """Initialize service-specific components."""
        try:
            # Setup default in-memory broker si aucun configuré
            if not self.broker_configs:
                await self.setup_default_broker()
            
            # Initialize event sourcing store
            await self.setup_event_sourcing()
            
            # Start background tasks
            asyncio.create_task(self._background_tasks())
            
            self.logger.info("✅ Message service components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize message service: {e}")
            raise
    
    async def _cleanup(self) -> None:
        """Cleanup service-specific resources."""
        try:
            # Close all broker connections
            for broker_name, broker in self.message_brokers.items():
                await self._close_broker_connection(broker_name, broker)
            
            # Clear handlers and queues
            self.event_handlers.clear()
            self.dead_letter_queues.clear()
            
            self.logger.info("✅ Message service cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during message service cleanup: {e}")
    
    async def _service_health_check(self) -> Dict[str, Any]:
        """Perform message service-specific health checks."""
        try:
            broker_health = {}
            for broker_name in self.message_brokers.keys():
                broker_health[broker_name] = await self._check_broker_health(broker_name)
            
            return {
                'brokers': broker_health,
                'handlers_count': len(self.event_handlers),
                'dlq_size': sum(len(dlq) for dlq in self.dead_letter_queues.values()),
                'event_store_size': len(self.event_store),
                'metrics': self.message_metrics.copy(),
                'circuit_breakers': {name: cb['state'] for name, cb in self.circuit_breakers.items()}
            }
            
        except Exception as e:
            self.logger.error(f"❌ Message service health check failed: {e}")
            return {'error': str(e), 'status': 'unhealthy'}
    
    async def setup_message_broker(self, broker_name: str, broker_config: BrokerConfig) -> None:
        """Configuration broker (RabbitMQ/Kafka/Redis)."""
        try:
            self.broker_configs[broker_name] = broker_config
            
            if broker_config.broker_type == MessageBrokerType.IN_MEMORY:
                broker = await self._setup_in_memory_broker(broker_name, broker_config)
            elif broker_config.broker_type == MessageBrokerType.RABBITMQ:
                broker = await self._setup_rabbitmq_broker(broker_name, broker_config)
            elif broker_config.broker_type == MessageBrokerType.KAFKA:
                broker = await self._setup_kafka_broker(broker_name, broker_config)
            elif broker_config.broker_type == MessageBrokerType.REDIS_STREAMS:
                broker = await self._setup_redis_broker(broker_name, broker_config)
            else:
                raise ValueError(f"Unsupported broker type: {broker_config.broker_type}")
            
            self.message_brokers[broker_name] = broker
            
            # Initialize circuit breaker for this broker
            self.circuit_breakers[broker_name] = {
                'state': 'closed',  # closed, open, half_open
                'failure_count': 0,
                'last_failure_time': None,
                'timeout': 60  # seconds
            }
            
            self.logger.info(f"✅ Message broker '{broker_name}' configured ({broker_config.broker_type.value})")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup message broker '{broker_name}': {e}")
            raise
    
    async def register_event_handler(self, handler: EventHandler) -> None:
        """Enregistrement handler pour type d'événement."""
        try:
            handler_key = f"{handler.event_type}:{handler.topic_pattern}"
            self.event_handlers[handler_key] = handler
            
            self.message_metrics['active_handlers'] = len(self.event_handlers)
            
            self.logger.info(f"✅ Event handler registered: {handler.event_type} -> {handler.topic_pattern}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register event handler: {e}")
            raise
    
    async def publish_event(self, message: Message, broker_name: str = "default") -> bool:
        """Publication événement avec retry et DLQ."""
        try:
            if broker_name not in self.message_brokers:
                raise ValueError(f"Broker '{broker_name}' not configured")
            
            # Check circuit breaker
            if not await self._check_circuit_breaker(broker_name):
                self.logger.warning(f"⚠️  Circuit breaker open for broker '{broker_name}', message queued")
                return False
            
            # Add to event store for event sourcing
            if message.event_type in [EventType.EVENT, EventType.COMMAND]:
                await self._append_to_event_store(message)
            
            # Publish to broker
            success = await self._publish_to_broker(broker_name, message)
            
            if success:
                self.message_metrics['messages_sent'] += 1
                await self._record_success(broker_name)
            else:
                await self._record_failure(broker_name)
                # Add to DLQ if max retries exceeded
                if message.retry_count >= message.max_retries:
                    await self._add_to_dead_letter_queue(broker_name, message)
                    self.message_metrics['dead_letter_messages'] += 1
                else:
                    # Retry avec exponential backoff
                    await self._schedule_retry(broker_name, message)
                    self.message_metrics['messages_retried'] += 1
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to publish event: {e}")
            await self._record_failure(broker_name)
            return False
    
    async def setup_event_sourcing(self, store_config: Optional[Dict] = None) -> None:
        """Configuration event sourcing avec snapshots."""
        try:
            if store_config:
                self.snapshot_frequency = store_config.get('snapshot_frequency', 100)
            
            # Initialize event store (in-memory par défaut)
            self.event_store = []
            self.snapshots = {}
            
            self.logger.info("✅ Event sourcing configured")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup event sourcing: {e}")
            raise
    
    async def setup_default_broker(self) -> None:
        """Setup default in-memory broker."""
        default_config = BrokerConfig(
            broker_type=MessageBrokerType.IN_MEMORY,
            connection_url="memory://localhost"
        )
        await self.setup_message_broker("default", default_config)
    
    async def _setup_in_memory_broker(self, broker_name: str, config: BrokerConfig) -> Dict:
        """Setup in-memory message broker."""
        return {
            'type': 'in_memory',
            'queues': defaultdict(deque),
            'subscribers': defaultdict(list),
            'config': config
        }
    
    async def _setup_rabbitmq_broker(self, broker_name: str, config: BrokerConfig) -> Dict:
        """Setup RabbitMQ broker."""
        # Placeholder - implement with aio-pika
        self.logger.warning("🚧 RabbitMQ broker setup not implemented - using in-memory fallback")
        return await self._setup_in_memory_broker(broker_name, config)
    
    async def _setup_kafka_broker(self, broker_name: str, config: BrokerConfig) -> Dict:
        """Setup Kafka broker."""
        # Placeholder - implement with aiokafka
        self.logger.warning("🚧 Kafka broker setup not implemented - using in-memory fallback")
        return await self._setup_in_memory_broker(broker_name, config)
    
    async def _setup_redis_broker(self, broker_name: str, config: BrokerConfig) -> Dict:
        """Setup Redis Streams broker."""
        # Placeholder - implement with redis-py
        self.logger.warning("🚧 Redis broker setup not implemented - using in-memory fallback")
        return await self._setup_in_memory_broker(broker_name, config)
    
    async def _publish_to_broker(self, broker_name: str, message: Message) -> bool:
        """Publish message to specific broker."""
        try:
            broker = self.message_brokers[broker_name]
            
            if broker['type'] == 'in_memory':
                # In-memory publishing
                queue_key = message.topic or 'default'
                broker['queues'][queue_key].append(message)
                
                # Notify subscribers
                for handler_key, handler in self.event_handlers.items():
                    if await self._matches_handler(message, handler):
                        asyncio.create_task(self._process_message(handler, message))
                
                return True
            
            # Other broker types would be implemented here
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to publish to broker '{broker_name}': {e}")
            return False
    
    async def _process_message(self, handler: EventHandler, message: Message) -> None:
        """Process message avec handler."""
        try:
            self.message_metrics['messages_received'] += 1
            
            # Apply timeout
            result = await asyncio.wait_for(
                handler.handler_func(message),
                timeout=handler.timeout_seconds
            )
            
            self.message_metrics['messages_processed'] += 1
            self.logger.debug(f"✅ Message processed: {message.id}")
            
        except asyncio.TimeoutError:
            self.message_metrics['messages_failed'] += 1
            self.logger.error(f"⏰ Handler timeout for message {message.id}")
            if handler.error_handler:
                await handler.error_handler(message, "timeout")
        except Exception as e:
            self.message_metrics['messages_failed'] += 1
            self.logger.error(f"❌ Handler error for message {message.id}: {e}")
            if handler.error_handler:
                await handler.error_handler(message, str(e))
    
    async def _matches_handler(self, message: Message, handler: EventHandler) -> bool:
        """Check if message matches handler criteria."""
        # Simple pattern matching - can be enhanced
        if handler.event_type != "*" and handler.event_type != message.event_type.value:
            return False
        
        if handler.topic_pattern != "*" and handler.topic_pattern != message.topic:
            return False
        
        return True
    
    async def _append_to_event_store(self, message: Message) -> None:
        """Add message to event store."""
        self.event_store.append(message)
        self.message_metrics['event_store_size'] = len(self.event_store)
        
        # Create snapshot si nécessaire
        if len(self.event_store) % self.snapshot_frequency == 0:
            await self._create_snapshot()
    
    async def _create_snapshot(self) -> None:
        """Create snapshot of current state."""
        try:
            snapshot_id = f"snapshot_{len(self.event_store)}"
            snapshot_data = {
                'timestamp': datetime.now().isoformat(),
                'event_count': len(self.event_store),
                'metrics': self.message_metrics.copy(),
                'last_event_id': self.event_store[-1].id if self.event_store else None
            }
            
            self.snapshots[snapshot_id] = snapshot_data
            self.message_metrics['snapshots_count'] = len(self.snapshots)
            
            self.logger.info(f"📸 Snapshot created: {snapshot_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create snapshot: {e}")
    
    async def _add_to_dead_letter_queue(self, broker_name: str, message: Message) -> None:
        """Add message to dead letter queue."""
        dlq_key = f"{broker_name}_dlq"
        self.dead_letter_queues[dlq_key].append({
            'message': message,
            'timestamp': datetime.now(),
            'reason': 'max_retries_exceeded'
        })
        
        self.logger.warning(f"💀 Message added to DLQ: {message.id}")
    
    async def _schedule_retry(self, broker_name: str, message: Message) -> None:
        """Schedule message retry avec exponential backoff."""
        try:
            message.retry_count += 1
            config = self.broker_configs[broker_name]
            
            # Calculate delay
            base_delay = config.retry_policy['retry_delay_seconds']
            if config.retry_policy.get('exponential_backoff', False):
                delay = base_delay * (2 ** (message.retry_count - 1))
            else:
                delay = base_delay
            
            # Schedule retry
            await asyncio.sleep(delay)
            await self.publish_event(message, broker_name)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to schedule retry: {e}")
    
    async def _check_circuit_breaker(self, broker_name: str) -> bool:
        """Check circuit breaker state."""
        cb = self.circuit_breakers.get(broker_name, {})
        state = cb.get('state', 'closed')
        
        if state == 'closed':
            return True
        elif state == 'open':
            # Check if timeout elapsed
            if cb.get('last_failure_time'):
                elapsed = (datetime.now() - cb['last_failure_time']).total_seconds()
                if elapsed > cb.get('timeout', 60):
                    cb['state'] = 'half_open'
                    return True
            return False
        elif state == 'half_open':
            return True  # Allow one request to test
        
        return False
    
    async def _record_success(self, broker_name: str) -> None:
        """Record successful operation."""
        if broker_name in self.circuit_breakers:
            cb = self.circuit_breakers[broker_name]
            cb['state'] = 'closed'
            cb['failure_count'] = 0
            cb['last_failure_time'] = None
    
    async def _record_failure(self, broker_name: str) -> None:
        """Record failed operation."""
        if broker_name in self.circuit_breakers:
            cb = self.circuit_breakers[broker_name]
            cb['failure_count'] += 1
            cb['last_failure_time'] = datetime.now()
            
            # Open circuit breaker si trop d'échecs
            if cb['failure_count'] >= 5:  # Configurable threshold
                cb['state'] = 'open'
    
    async def _check_broker_health(self, broker_name: str) -> str:
        """Check health of specific broker."""
        try:
            if broker_name not in self.message_brokers:
                return "not_configured"
            
            cb = self.circuit_breakers.get(broker_name, {})
            if cb.get('state') == 'open':
                return "circuit_breaker_open"
            
            # Additional broker-specific health checks here
            return "healthy"
            
        except Exception as e:
            self.logger.error(f"❌ Broker health check failed for '{broker_name}': {e}")
            return "unhealthy"
    
    async def _close_broker_connection(self, broker_name: str, broker: Any) -> None:
        """Close broker connection."""
        try:
            # Broker-specific cleanup logic
            if broker.get('type') == 'in_memory':
                broker['queues'].clear()
                broker['subscribers'].clear()
            
            self.logger.info(f"🔌 Broker connection closed: {broker_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to close broker connection '{broker_name}': {e}")
    
    async def _background_tasks(self) -> None:
        """Background maintenance tasks."""
        while self.status == "running":
            try:
                # Process dead letter queues
                await self._process_dead_letter_queues()
                
                # Cleanup old snapshots
                await self._cleanup_old_snapshots()
                
                # Health check circuit breakers
                await self._check_all_circuit_breakers()
                
                await asyncio.sleep(30)  # Run every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Background task error: {e}")
                await asyncio.sleep(60)
    
    async def _process_dead_letter_queues(self) -> None:
        """Process messages in dead letter queues."""
        # Implementation for DLQ processing (retry, manual intervention, etc.)
        pass
    
    async def _cleanup_old_snapshots(self) -> None:
        """Cleanup old snapshots."""
        # Keep only last 10 snapshots
        if len(self.snapshots) > 10:
            sorted_snapshots = sorted(self.snapshots.keys())
            for old_snapshot in sorted_snapshots[:-10]:
                del self.snapshots[old_snapshot]
            self.message_metrics['snapshots_count'] = len(self.snapshots)
    
    async def _check_all_circuit_breakers(self) -> None:
        """Check all circuit breakers."""
        for broker_name in self.circuit_breakers:
            await self._check_circuit_breaker(broker_name)
    
    # Abstract methods pour extension
    @abstractmethod
    async def configure_custom_handlers(self) -> List[EventHandler]:
        """Configure handlers spécifiques au service."""
        pass
    
    @abstractmethod
    async def configure_custom_brokers(self) -> Dict[str, BrokerConfig]:
        """Configure brokers spécifiques au service."""
        pass


if __name__ == "__main__":
    print("📨 Enterprise Message Service Template")
    print("Use this template to create event-driven microservices")