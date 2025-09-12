"""📡 Gateway Event Bus
=====================

Enterprise event bus for real-time payment gateway event streaming.
Handles event publication, subscription, webhook management, and
integration with external systems.

Features:
- Real-time payment event streaming
- Webhook management and routing
- Event-driven architecture support
- Integration with external systems
- Event filtering and transformation
- Reliable event delivery

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json
import uuid
import hashlib
import hmac
import aiohttp
from collections import defaultdict, deque
import aioredis
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of payment gateway events"""
    TRANSACTION_CREATED = "transaction.created"
    TRANSACTION_PROCESSING = "transaction.processing"
    TRANSACTION_COMPLETED = "transaction.completed"
    TRANSACTION_FAILED = "transaction.failed"
    TRANSACTION_REFUNDED = "transaction.refunded"
    TRANSACTION_DISPUTED = "transaction.disputed"
    
    PAYMENT_AUTHORIZED = "payment.authorized"
    PAYMENT_CAPTURED = "payment.captured"
    PAYMENT_VOIDED = "payment.voided"
    
    PROVIDER_HEALTH_CHANGED = "provider.health_changed"
    PROVIDER_MAINTENANCE = "provider.maintenance"
    PROVIDER_RESTORED = "provider.restored"
    
    FRAUD_DETECTED = "fraud.detected"
    FRAUD_CLEARED = "fraud.cleared"
    
    WEBHOOK_RECEIVED = "webhook.received"
    WEBHOOK_FAILED = "webhook.failed"
    
    SYSTEM_ALERT = "system.alert"
    SYSTEM_ERROR = "system.error"
    
    REVENUE_MILESTONE = "revenue.milestone"
    ANALYTICS_UPDATED = "analytics.updated"


class EventPriority(Enum):
    """Event priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class DeliveryMethod(Enum):
    """Event delivery methods"""
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    REDIS_PUB_SUB = "redis_pub_sub"
    MESSAGE_QUEUE = "message_queue"
    INTERNAL = "internal"


@dataclass
class PaymentEvent:
    """Payment gateway event"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    source: str
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'source': self.source,
            'priority': self.priority.value,
            'correlation_id': self.correlation_id,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaymentEvent':
        """Create event from dictionary"""
        return cls(
            event_id=data['event_id'],
            event_type=EventType(data['event_type']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            data=data['data'],
            source=data['source'],
            priority=EventPriority(data.get('priority', 'normal')),
            correlation_id=data.get('correlation_id'),
            metadata=data.get('metadata', {})
        )


@dataclass
class EventSubscription:
    """Event subscription configuration"""
    subscription_id: str
    event_types: List[EventType]
    delivery_method: DeliveryMethod
    endpoint_url: Optional[str] = None
    callback_function: Optional[Callable] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_delivery: Optional[datetime] = None
    delivery_count: int = 0
    failure_count: int = 0


@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration"""
    endpoint_id: str
    url: str
    secret: str
    event_types: List[EventType]
    is_active: bool = True
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 60
    timeout_seconds: int = 30
    created_at: datetime = field(default_factory=datetime.now)
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0


@dataclass
class EventDeliveryAttempt:
    """Event delivery attempt record"""
    attempt_id: str
    event_id: str
    subscription_id: str
    delivery_method: DeliveryMethod
    attempted_at: datetime
    succeeded: bool
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0


class GatewayEventBus:
    """Enterprise event bus for payment gateway"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = None
        self.http_session = None
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.webhook_endpoints: Dict[str, WebhookEndpoint] = {}
        self.event_history: deque = deque(maxlen=10000)
        self.delivery_attempts: deque = deque(maxlen=5000)
        self.is_initialized = False
        
        # Event bus configuration
        self.max_retry_attempts = config.get('max_retry_attempts', 3)
        self.retry_delay_seconds = config.get('retry_delay_seconds', 60)
        self.event_retention_hours = config.get('event_retention_hours', 24)
        self.webhook_timeout = config.get('webhook_timeout', 30)
        
        # Performance settings
        self.batch_size = config.get('batch_size', 100)
        self.delivery_interval = config.get('delivery_interval', 5)  # seconds
        
        # Event filters and transformations
        self.event_filters: Dict[str, Callable] = {}
        self.event_transformers: Dict[EventType, Callable] = {}
        
    async def initialize(self):
        """Initialize the event bus"""
        try:
            # Initialize Redis connection for pub/sub
            redis_config = self.config.get('redis', {})
            self.redis_client = aioredis.from_url(
                f"redis://{redis_config.get('host', 'localhost')}:"
                f"{redis_config.get('port', 6379)}"
            )
            
            # Initialize HTTP session for webhooks
            self.http_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.webhook_timeout)
            )
            
            # Load existing subscriptions and webhooks
            await self._load_configuration()
            
            # Start background tasks
            asyncio.create_task(self._process_event_queue())
            asyncio.create_task(self._retry_failed_deliveries())
            asyncio.create_task(self._cleanup_old_events())
            
            self.is_initialized = True
            logger.info("Gateway Event Bus initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gateway Event Bus: {e}")
            raise
    
    async def _load_configuration(self):
        """Load existing configuration from storage"""
        try:
            # Load subscriptions
            subscriptions_data = await self.redis_client.get("eventbus:subscriptions")
            if subscriptions_data:
                subs_dict = json.loads(subscriptions_data.decode())
                for sub_id, sub_info in subs_dict.items():
                    self.subscriptions[sub_id] = EventSubscription(
                        subscription_id=sub_info['subscription_id'],
                        event_types=[EventType(et) for et in sub_info['event_types']],
                        delivery_method=DeliveryMethod(sub_info['delivery_method']),
                        endpoint_url=sub_info.get('endpoint_url'),
                        filters=sub_info.get('filters', {}),
                        is_active=sub_info['is_active'],
                        created_at=datetime.fromisoformat(sub_info['created_at']),
                        last_delivery=datetime.fromisoformat(sub_info['last_delivery']) if sub_info.get('last_delivery') else None,
                        delivery_count=sub_info.get('delivery_count', 0),
                        failure_count=sub_info.get('failure_count', 0)
                    )
            
            # Load webhook endpoints
            webhooks_data = await self.redis_client.get("eventbus:webhooks")
            if webhooks_data:
                webhooks_dict = json.loads(webhooks_data.decode())
                for endpoint_id, endpoint_info in webhooks_dict.items():
                    self.webhook_endpoints[endpoint_id] = WebhookEndpoint(
                        endpoint_id=endpoint_info['endpoint_id'],
                        url=endpoint_info['url'],
                        secret=endpoint_info['secret'],
                        event_types=[EventType(et) for et in endpoint_info['event_types']],
                        is_active=endpoint_info['is_active'],
                        max_retry_attempts=endpoint_info.get('max_retry_attempts', 3),
                        retry_delay_seconds=endpoint_info.get('retry_delay_seconds', 60),
                        timeout_seconds=endpoint_info.get('timeout_seconds', 30),
                        created_at=datetime.fromisoformat(endpoint_info['created_at']),
                        last_success=datetime.fromisoformat(endpoint_info['last_success']) if endpoint_info.get('last_success') else None,
                        last_failure=datetime.fromisoformat(endpoint_info['last_failure']) if endpoint_info.get('last_failure') else None,
                        success_count=endpoint_info.get('success_count', 0),
                        failure_count=endpoint_info.get('failure_count', 0)
                    )
                    
            logger.info("Event bus configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load event bus configuration: {e}")
    
    async def publish_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source: str,
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: Optional[str] = None
    ) -> str:
        """Publish an event to the bus"""
        try:
            # Create event
            event = PaymentEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                timestamp=datetime.now(),
                data=data,
                source=source,
                priority=priority,
                correlation_id=correlation_id
            )
            
            # Apply transformations if configured
            if event_type in self.event_transformers:
                event = await self.event_transformers[event_type](event)
            
            # Store event
            self.event_history.append(event)
            
            # Publish to Redis pub/sub
            await self.redis_client.publish(
                f"payment_events:{event_type.value}",
                json.dumps(event.to_dict())
            )
            
            # Queue for webhook and other deliveries
            await self._queue_event_for_delivery(event)
            
            logger.debug(f"Published event: {event_type.value} ({event.event_id})")
            return event.event_id
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise
    
    async def _queue_event_for_delivery(self, event: PaymentEvent):
        """Queue event for delivery to subscribers"""
        try:
            # Find matching subscriptions
            matching_subscriptions = []
            
            for subscription in self.subscriptions.values():
                if not subscription.is_active:
                    continue
                
                # Check if event type matches
                if event.event_type in subscription.event_types:
                    # Apply filters
                    if await self._apply_event_filters(event, subscription.filters):
                        matching_subscriptions.append(subscription)
            
            # Queue delivery for each matching subscription
            for subscription in matching_subscriptions:
                await self._schedule_event_delivery(event, subscription)
                
        except Exception as e:
            logger.error(f"Failed to queue event for delivery: {e}")
    
    async def _apply_event_filters(
        self,
        event: PaymentEvent,
        filters: Dict[str, Any]
    ) -> bool:
        """Apply filters to determine if event should be delivered"""
        try:
            if not filters:
                return True
            
            # Apply source filter
            if 'sources' in filters:
                if event.source not in filters['sources']:
                    return False
            
            # Apply priority filter
            if 'min_priority' in filters:
                priority_order = {
                    EventPriority.LOW: 0,
                    EventPriority.NORMAL: 1,
                    EventPriority.HIGH: 2,
                    EventPriority.CRITICAL: 3
                }
                min_priority = EventPriority(filters['min_priority'])
                if priority_order[event.priority] < priority_order[min_priority]:
                    return False
            
            # Apply data filters
            if 'data_filters' in filters:
                for key, expected_value in filters['data_filters'].items():
                    if key not in event.data or event.data[key] != expected_value:
                        return False
            
            # Apply custom filter functions
            if 'custom_filter' in filters:
                filter_name = filters['custom_filter']
                if filter_name in self.event_filters:
                    if not await self.event_filters[filter_name](event):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply event filters: {e}")
            return False
    
    async def _schedule_event_delivery(
        self,
        event: PaymentEvent,
        subscription: EventSubscription
    ):
        """Schedule event delivery for a subscription"""
        try:
            delivery_data = {
                'event': event.to_dict(),
                'subscription_id': subscription.subscription_id,
                'delivery_method': subscription.delivery_method.value,
                'endpoint_url': subscription.endpoint_url,
                'scheduled_at': datetime.now().isoformat()
            }
            
            # Add to delivery queue
            await self.redis_client.lpush(
                "eventbus:delivery_queue",
                json.dumps(delivery_data)
            )
            
        except Exception as e:
            logger.error(f"Failed to schedule event delivery: {e}")
    
    async def _process_event_queue(self):
        """Process queued events for delivery"""
        while True:
            try:
                # Get batch of events from queue
                batch = []
                for _ in range(self.batch_size):
                    item = await self.redis_client.brpop("eventbus:delivery_queue", timeout=1)
                    if item:
                        batch.append(json.loads(item[1].decode()))
                    else:
                        break
                
                # Process batch
                for delivery_data in batch:
                    await self._deliver_event(delivery_data)
                
                # Small delay if no events to process
                if not batch:
                    await asyncio.sleep(self.delivery_interval)
                    
            except Exception as e:
                logger.error(f"Error in event queue processing: {e}")
                await asyncio.sleep(10)
    
    async def _deliver_event(self, delivery_data: Dict[str, Any]):
        """Deliver event using specified method"""
        try:
            event = PaymentEvent.from_dict(delivery_data['event'])
            subscription_id = delivery_data['subscription_id']
            delivery_method = DeliveryMethod(delivery_data['delivery_method'])
            
            # Create delivery attempt record
            attempt = EventDeliveryAttempt(
                attempt_id=str(uuid.uuid4()),
                event_id=event.event_id,
                subscription_id=subscription_id,
                delivery_method=delivery_method,
                attempted_at=datetime.now(),
                succeeded=False
            )
            
            try:
                if delivery_method == DeliveryMethod.WEBHOOK:
                    await self._deliver_webhook(event, delivery_data, attempt)
                elif delivery_method == DeliveryMethod.WEBSOCKET:
                    await self._deliver_websocket(event, delivery_data, attempt)
                elif delivery_method == DeliveryMethod.REDIS_PUB_SUB:
                    await self._deliver_redis_pubsub(event, delivery_data, attempt)
                elif delivery_method == DeliveryMethod.INTERNAL:
                    await self._deliver_internal(event, delivery_data, attempt)
                
                # Update subscription statistics
                if subscription_id in self.subscriptions:
                    subscription = self.subscriptions[subscription_id]
                    subscription.delivery_count += 1
                    subscription.last_delivery = datetime.now()
                    
            except Exception as e:
                attempt.error_message = str(e)
                attempt.succeeded = False
                
                # Update failure count
                if subscription_id in self.subscriptions:
                    self.subscriptions[subscription_id].failure_count += 1
                
                # Schedule retry if not exceeded max attempts
                retry_count = attempt.retry_count + 1
                if retry_count <= self.max_retry_attempts:
                    await self._schedule_retry(delivery_data, retry_count)
                
                logger.error(f"Failed to deliver event {event.event_id}: {e}")
            
            # Store delivery attempt
            self.delivery_attempts.append(attempt)
            
        except Exception as e:
            logger.error(f"Failed to process event delivery: {e}")
    
    async def _deliver_webhook(
        self,
        event: PaymentEvent,
        delivery_data: Dict[str, Any],
        attempt: EventDeliveryAttempt
    ):
        """Deliver event via webhook"""
        endpoint_url = delivery_data['endpoint_url']
        if not endpoint_url:
            raise ValueError("Webhook endpoint URL not provided")
        
        # Find webhook endpoint configuration
        webhook_endpoint = None
        for endpoint in self.webhook_endpoints.values():
            if endpoint.url == endpoint_url and endpoint.is_active:
                webhook_endpoint = endpoint
                break
        
        if not webhook_endpoint:
            raise ValueError(f"Webhook endpoint not found or inactive: {endpoint_url}")
        
        # Prepare webhook payload
        payload = {
            'event_id': event.event_id,
            'event_type': event.event_type.value,
            'timestamp': event.timestamp.isoformat(),
            'data': event.data
        }
        
        # Generate signature
        signature = await self._generate_webhook_signature(
            json.dumps(payload, sort_keys=True),
            webhook_endpoint.secret
        )
        
        # Send webhook
        headers = {
            'Content-Type': 'application/json',
            'X-Signature': signature,
            'X-Event-ID': event.event_id,
            'X-Event-Type': event.event_type.value
        }
        
        async with self.http_session.post(
            endpoint_url,
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=webhook_endpoint.timeout_seconds)
        ) as response:
            attempt.response_code = response.status
            attempt.response_body = await response.text()
            
            if response.status == 200:
                attempt.succeeded = True
                webhook_endpoint.success_count += 1
                webhook_endpoint.last_success = datetime.now()
            else:
                webhook_endpoint.failure_count += 1
                webhook_endpoint.last_failure = datetime.now()
                raise Exception(f"Webhook returned status {response.status}")
    
    async def _deliver_websocket(
        self,
        event: PaymentEvent,
        delivery_data: Dict[str, Any],
        attempt: EventDeliveryAttempt
    ):
        """Deliver event via WebSocket"""
        # This would implement WebSocket delivery
        # For now, mark as successful (placeholder implementation)
        attempt.succeeded = True
        logger.debug(f"WebSocket delivery (placeholder): {event.event_id}")
    
    async def _deliver_redis_pubsub(
        self,
        event: PaymentEvent,
        delivery_data: Dict[str, Any],
        attempt: EventDeliveryAttempt
    ):
        """Deliver event via Redis pub/sub"""
        channel = f"subscription:{delivery_data['subscription_id']}"
        await self.redis_client.publish(channel, json.dumps(event.to_dict()))
        attempt.succeeded = True
    
    async def _deliver_internal(
        self,
        event: PaymentEvent,
        delivery_data: Dict[str, Any],
        attempt: EventDeliveryAttempt
    ):
        """Deliver event to internal callback function"""
        subscription_id = delivery_data['subscription_id']
        
        if subscription_id in self.subscriptions:
            subscription = self.subscriptions[subscription_id]
            if subscription.callback_function:
                await subscription.callback_function(event)
                attempt.succeeded = True
            else:
                raise ValueError("No callback function configured for internal delivery")
    
    async def _generate_webhook_signature(self, payload: str, secret: str) -> str:
        """Generate webhook signature for verification"""
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    async def _schedule_retry(self, delivery_data: Dict[str, Any], retry_count: int):
        """Schedule event delivery retry"""
        try:
            delivery_data['retry_count'] = retry_count
            delay = self.retry_delay_seconds * (2 ** (retry_count - 1))  # Exponential backoff
            
            # Schedule retry
            retry_time = datetime.now() + timedelta(seconds=delay)
            retry_data = {
                'delivery_data': delivery_data,
                'retry_at': retry_time.isoformat()
            }
            
            await self.redis_client.lpush(
                "eventbus:retry_queue",
                json.dumps(retry_data)
            )
            
            logger.debug(f"Scheduled retry {retry_count} for event in {delay} seconds")
            
        except Exception as e:
            logger.error(f"Failed to schedule retry: {e}")
    
    async def _retry_failed_deliveries(self):
        """Process retry queue for failed deliveries"""
        while True:
            try:
                # Check retry queue
                retry_item = await self.redis_client.brpop("eventbus:retry_queue", timeout=10)
                
                if retry_item:
                    retry_data = json.loads(retry_item[1].decode())
                    retry_time = datetime.fromisoformat(retry_data['retry_at'])
                    
                    # Check if it's time to retry
                    if datetime.now() >= retry_time:
                        await self._deliver_event(retry_data['delivery_data'])
                    else:
                        # Put back in queue if not time yet
                        await self.redis_client.lpush(
                            "eventbus:retry_queue",
                            retry_item[1]
                        )
                        await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in retry processing: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_events(self):
        """Clean up old events from history"""
        while True:
            try:
                cutoff_time = datetime.now() - timedelta(hours=self.event_retention_hours)
                
                # Clean event history
                while self.event_history and self.event_history[0].timestamp < cutoff_time:
                    self.event_history.popleft()
                
                # Clean delivery attempts
                while (self.delivery_attempts and 
                       self.delivery_attempts[0].attempted_at < cutoff_time):
                    self.delivery_attempts.popleft()
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in event cleanup: {e}")
                await asyncio.sleep(3600)
    
    async def subscribe(
        self,
        event_types: List[EventType],
        delivery_method: DeliveryMethod,
        endpoint_url: Optional[str] = None,
        callback_function: Optional[Callable] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Subscribe to events"""
        try:
            subscription_id = str(uuid.uuid4())
            
            subscription = EventSubscription(
                subscription_id=subscription_id,
                event_types=event_types,
                delivery_method=delivery_method,
                endpoint_url=endpoint_url,
                callback_function=callback_function,
                filters=filters or {}
            )
            
            self.subscriptions[subscription_id] = subscription
            await self._save_subscriptions()
            
            logger.info(f"Created subscription: {subscription_id}")
            return subscription_id
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            raise
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events"""
        try:
            if subscription_id in self.subscriptions:
                del self.subscriptions[subscription_id]
                await self._save_subscriptions()
                logger.info(f"Removed subscription: {subscription_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe: {e}")
            return False
    
    async def add_webhook_endpoint(
        self,
        url: str,
        secret: str,
        event_types: List[EventType],
        max_retry_attempts: int = 3,
        timeout_seconds: int = 30
    ) -> str:
        """Add webhook endpoint"""
        try:
            endpoint_id = str(uuid.uuid4())
            
            endpoint = WebhookEndpoint(
                endpoint_id=endpoint_id,
                url=url,
                secret=secret,
                event_types=event_types,
                max_retry_attempts=max_retry_attempts,
                timeout_seconds=timeout_seconds
            )
            
            self.webhook_endpoints[endpoint_id] = endpoint
            await self._save_webhook_endpoints()
            
            logger.info(f"Added webhook endpoint: {endpoint_id}")
            return endpoint_id
            
        except Exception as e:
            logger.error(f"Failed to add webhook endpoint: {e}")
            raise
    
    async def remove_webhook_endpoint(self, endpoint_id: str) -> bool:
        """Remove webhook endpoint"""
        try:
            if endpoint_id in self.webhook_endpoints:
                del self.webhook_endpoints[endpoint_id]
                await self._save_webhook_endpoints()
                logger.info(f"Removed webhook endpoint: {endpoint_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove webhook endpoint: {e}")
            return False
    
    async def get_event_bus_status(self) -> Dict[str, Any]:
        """Get event bus status and metrics"""
        try:
            # Calculate statistics
            total_events = len(self.event_history)
            recent_events = len([
                e for e in self.event_history
                if (datetime.now() - e.timestamp).total_seconds() < 3600
            ])
            
            total_deliveries = len(self.delivery_attempts)
            successful_deliveries = len([
                a for a in self.delivery_attempts if a.succeeded
            ])
            
            delivery_success_rate = (
                (successful_deliveries / total_deliveries * 100)
                if total_deliveries > 0 else 0
            )
            
            # Active subscriptions by delivery method
            delivery_method_counts = {}
            for subscription in self.subscriptions.values():
                if subscription.is_active:
                    method = subscription.delivery_method.value
                    delivery_method_counts[method] = delivery_method_counts.get(method, 0) + 1
            
            return {
                'is_initialized': self.is_initialized,
                'total_subscriptions': len(self.subscriptions),
                'active_subscriptions': len([s for s in self.subscriptions.values() if s.is_active]),
                'webhook_endpoints': len(self.webhook_endpoints),
                'active_webhooks': len([w for w in self.webhook_endpoints.values() if w.is_active]),
                'total_events': total_events,
                'recent_events_1h': recent_events,
                'total_deliveries': total_deliveries,
                'successful_deliveries': successful_deliveries,
                'delivery_success_rate': delivery_success_rate,
                'delivery_method_distribution': delivery_method_counts,
                'queue_sizes': {
                    'delivery_queue': await self.redis_client.llen("eventbus:delivery_queue"),
                    'retry_queue': await self.redis_client.llen("eventbus:retry_queue")
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get event bus status: {e}")
            return {'error': str(e)}
    
    async def _save_subscriptions(self):
        """Save subscriptions to storage"""
        try:
            subs_dict = {}
            for sub_id, subscription in self.subscriptions.items():
                subs_dict[sub_id] = {
                    'subscription_id': subscription.subscription_id,
                    'event_types': [et.value for et in subscription.event_types],
                    'delivery_method': subscription.delivery_method.value,
                    'endpoint_url': subscription.endpoint_url,
                    'filters': subscription.filters,
                    'is_active': subscription.is_active,
                    'created_at': subscription.created_at.isoformat(),
                    'last_delivery': subscription.last_delivery.isoformat() if subscription.last_delivery else None,
                    'delivery_count': subscription.delivery_count,
                    'failure_count': subscription.failure_count
                }
            
            await self.redis_client.set(
                "eventbus:subscriptions",
                json.dumps(subs_dict),
                ex=86400 * 7  # 1 week expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to save subscriptions: {e}")
    
    async def _save_webhook_endpoints(self):
        """Save webhook endpoints to storage"""
        try:
            webhooks_dict = {}
            for endpoint_id, endpoint in self.webhook_endpoints.items():
                webhooks_dict[endpoint_id] = {
                    'endpoint_id': endpoint.endpoint_id,
                    'url': endpoint.url,
                    'secret': endpoint.secret,
                    'event_types': [et.value for et in endpoint.event_types],
                    'is_active': endpoint.is_active,
                    'max_retry_attempts': endpoint.max_retry_attempts,
                    'retry_delay_seconds': endpoint.retry_delay_seconds,
                    'timeout_seconds': endpoint.timeout_seconds,
                    'created_at': endpoint.created_at.isoformat(),
                    'last_success': endpoint.last_success.isoformat() if endpoint.last_success else None,
                    'last_failure': endpoint.last_failure.isoformat() if endpoint.last_failure else None,
                    'success_count': endpoint.success_count,
                    'failure_count': endpoint.failure_count
                }
            
            await self.redis_client.set(
                "eventbus:webhooks",
                json.dumps(webhooks_dict),
                ex=86400 * 7  # 1 week expiry
            )
            
        except Exception as e:
            logger.error(f"Failed to save webhook endpoints: {e}")
    
    async def close(self):
        """Close the event bus and cleanup resources"""
        try:
            if self.http_session:
                await self.http_session.close()
            
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Gateway Event Bus closed successfully")
            
        except Exception as e:
            logger.error(f"Failed to close Gateway Event Bus: {e}")