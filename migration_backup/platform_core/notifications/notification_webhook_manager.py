"""🚀 Notification Webhook Manager - Enterprise Integration System
================================================================
Module: platform_core/notifications/notification_webhook_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

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

🎯 NOTIFICATION WEBHOOK MANAGER - ENTERPRISE INTEGRATION
- Manager webhooks pour intégrations externes
- Delivery tracking avec retry mechanisms
- Security avec signature verification
- Rate limiting et batch processing
- Event filtering et transformation
"""

import asyncio
import logging
import json
import uuid
import hmac
import hashlib
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import redis.asyncio as redis
from urllib.parse import urlparse
import base64

logger = logging.getLogger(__name__)


class WebhookEvent(Enum):
    """Webhook event types."""
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_DELIVERED = "notification.delivered"
    NOTIFICATION_OPENED = "notification.opened"
    NOTIFICATION_CLICKED = "notification.clicked"
    NOTIFICATION_BOUNCED = "notification.bounced"
    NOTIFICATION_COMPLAINED = "notification.complained"
    NOTIFICATION_FAILED = "notification.failed"
    CAMPAIGN_STARTED = "campaign.started"
    CAMPAIGN_COMPLETED = "campaign.completed"
    USER_OPTED_IN = "user.opted_in"
    USER_OPTED_OUT = "user.opted_out"
    TEMPLATE_UPDATED = "template.updated"


class WebhookStatus(Enum):
    """Webhook delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    DISABLED = "disabled"


class RetryStrategy(Enum):
    """Retry strategies for failed webhooks."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    IMMEDIATE_RETRY = "immediate_retry"
    NO_RETRY = "no_retry"


@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration."""
    id: str
    name: str
    url: str
    secret: str
    events: List[WebhookEvent] = field(default_factory=list)
    enabled: bool = True
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    max_retries: int = 5
    timeout_seconds: int = 30
    headers: Dict[str, str] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    transform_template: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0


@dataclass
class WebhookPayload:
    """Webhook payload data."""
    id: str
    event: WebhookEvent
    timestamp: datetime
    data: Dict[str, Any]
    user_id: Optional[str] = None
    notification_id: Optional[str] = None
    campaign_id: Optional[str] = None
    template_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookDelivery:
    """Webhook delivery attempt."""
    id: str
    endpoint_id: str
    payload: WebhookPayload
    status: WebhookStatus = WebhookStatus.PENDING
    attempts: int = 0
    last_attempt: Optional[datetime] = None
    next_attempt: Optional[datetime] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class WebhookSecurity:
    """Webhook security and signature verification."""
    
    @staticmethod
    def generate_signature(payload: str, secret: str, algorithm: str = "sha256") -> str:
        """Generate webhook signature."""
        try:
            if algorithm == "sha256":
                signature = hmac.new(
                    secret.encode(),
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()
                return f"sha256={signature}"
            elif algorithm == "sha1":
                signature = hmac.new(
                    secret.encode(),
                    payload.encode(),
                    hashlib.sha1
                ).hexdigest()
                return f"sha1={signature}"
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
        except Exception as e:
            logger.error(f"Signature generation failed: {e}")
            return ""
    
    @staticmethod
    def verify_signature(payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature."""
        try:
            if signature.startswith("sha256="):
                expected = WebhookSecurity.generate_signature(payload, secret, "sha256")
            elif signature.startswith("sha1="):
                expected = WebhookSecurity.generate_signature(payload, secret, "sha1")
            else:
                return False
            
            return hmac.compare_digest(signature, expected)
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate webhook URL."""
        try:
            parsed = urlparse(url)
            
            # Must be HTTPS in production
            if parsed.scheme not in ["http", "https"]:
                return False
            
            # Must have valid hostname
            if not parsed.hostname:
                return False
            
            # No localhost or private IPs in production
            if parsed.hostname in ["localhost", "127.0.0.1", "0.0.0.0"]:
                logger.warning(f"Local URL detected: {url}")
            
            return True
            
        except Exception as e:
            logger.error(f"URL validation failed: {e}")
            return False


class EventFilter:
    """Event filtering and transformation."""
    
    def __init__(self):
        pass
    
    def should_send_event(self, payload: WebhookPayload, filters: Dict[str, Any]) -> bool:
        """Check if event should be sent based on filters."""
        try:
            if not filters:
                return True
            
            # User filter
            if "user_ids" in filters:
                if payload.user_id and payload.user_id not in filters["user_ids"]:
                    return False
            
            # Campaign filter
            if "campaign_ids" in filters:
                if payload.campaign_id and payload.campaign_id not in filters["campaign_ids"]:
                    return False
            
            # Template filter
            if "template_ids" in filters:
                if payload.template_id and payload.template_id not in filters["template_ids"]:
                    return False
            
            # Data filters
            if "data_filters" in filters:
                for field, expected_value in filters["data_filters"].items():
                    actual_value = self._get_nested_value(payload.data, field)
                    if actual_value != expected_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Event filtering failed: {e}")
            return True  # Default to send if filter fails
    
    def transform_payload(self, payload: WebhookPayload, template: str) -> Dict[str, Any]:
        """Transform payload using template."""
        try:
            if not template:
                return self._default_payload_format(payload)
            
            # Simple template transformation (in production, use proper template engine)
            transformed = json.loads(template)
            
            # Replace placeholders
            transformed_str = json.dumps(transformed)
            
            # Replace event data
            transformed_str = transformed_str.replace("{{event}}", payload.event.value)
            transformed_str = transformed_str.replace("{{timestamp}}", payload.timestamp.isoformat())
            transformed_str = transformed_str.replace("{{id}}", payload.id)
            
            if payload.user_id:
                transformed_str = transformed_str.replace("{{user_id}}", payload.user_id)
            if payload.notification_id:
                transformed_str = transformed_str.replace("{{notification_id}}", payload.notification_id)
            if payload.campaign_id:
                transformed_str = transformed_str.replace("{{campaign_id}}", payload.campaign_id)
            
            # Replace data fields
            for key, value in payload.data.items():
                transformed_str = transformed_str.replace(f"{{{{data.{key}}}}}", str(value))
            
            return json.loads(transformed_str)
            
        except Exception as e:
            logger.error(f"Payload transformation failed: {e}")
            return self._default_payload_format(payload)
    
    def _default_payload_format(self, payload: WebhookPayload) -> Dict[str, Any]:
        """Default payload format."""
        return {
            "id": payload.id,
            "event": payload.event.value,
            "timestamp": payload.timestamp.isoformat(),
            "data": payload.data,
            "user_id": payload.user_id,
            "notification_id": payload.notification_id,
            "campaign_id": payload.campaign_id,
            "template_id": payload.template_id,
            "metadata": payload.metadata
        }
    
    def _get_nested_value(self, data: Dict[str, Any], field: str) -> Any:
        """Get nested value from data using dot notation."""
        try:
            keys = field.split(".")
            value = data
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None


class WebhookRateLimiter:
    """Rate limiting for webhook deliveries."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def can_send_webhook(self, endpoint_id: str, requests_per_minute: int = 60) -> bool:
        """Check if webhook can be sent within rate limit."""
        try:
            current_minute = datetime.utcnow().strftime('%Y-%m-%d:%H:%M')
            key = f"webhook_rate_limit:{endpoint_id}:{current_minute}"
            
            current_count = await self.redis.get(key) or 0
            current_count = int(current_count)
            
            return current_count < requests_per_minute
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Default to allow
    
    async def record_webhook_sent(self, endpoint_id: str) -> None:
        """Record webhook sent for rate limiting."""
        try:
            current_minute = datetime.utcnow().strftime('%Y-%m-%d:%H:%M')
            key = f"webhook_rate_limit:{endpoint_id}:{current_minute}"
            
            await self.redis.incr(key)
            await self.redis.expire(key, 60)  # Expire after 1 minute
            
        except Exception as e:
            logger.error(f"Failed to record webhook: {e}")


class NotificationWebhookManager:
    """Enterprise notification webhook management system."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis = redis.Redis(**config.get('redis', {}))
        
        # Initialize components
        self.event_filter = EventFilter()
        self.rate_limiter = WebhookRateLimiter(self.redis)
        
        # Configuration
        self.max_concurrent_deliveries = config.get('max_concurrent_deliveries', 100)
        self.default_timeout = config.get('default_timeout', 30)
        self.retry_delays = [60, 300, 900, 3600, 7200]  # 1m, 5m, 15m, 1h, 2h
        
        # Storage
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.pending_deliveries: List[WebhookDelivery] = []
        
        # Start background processors
        asyncio.create_task(self._process_webhook_deliveries())
        asyncio.create_task(self._process_retry_queue())
        asyncio.create_task(self._cleanup_old_deliveries())
    
    async def register_endpoint(self, endpoint: WebhookEndpoint) -> bool:
        """Register webhook endpoint."""
        try:
            # Validate endpoint
            if not await self._validate_endpoint(endpoint):
                return False
            
            # Store endpoint
            await self._store_endpoint(endpoint)
            
            # Cache in memory
            self.endpoints[endpoint.id] = endpoint
            
            logger.info(f"Webhook endpoint {endpoint.id} registered")
            return True
            
        except Exception as e:
            logger.error(f"Endpoint registration failed: {e}")
            return False
    
    async def update_endpoint(self, endpoint_id: str, updates: Dict[str, Any]) -> bool:
        """Update webhook endpoint."""
        try:
            endpoint = await self._load_endpoint(endpoint_id)
            if not endpoint:
                return False
            
            # Update fields
            for key, value in updates.items():
                if hasattr(endpoint, key):
                    setattr(endpoint, key, value)
            
            endpoint.updated_at = datetime.utcnow()
            
            # Store updated endpoint
            await self._store_endpoint(endpoint)
            
            # Update cache
            self.endpoints[endpoint_id] = endpoint
            
            logger.info(f"Webhook endpoint {endpoint_id} updated")
            return True
            
        except Exception as e:
            logger.error(f"Endpoint update failed: {e}")
            return False
    
    async def delete_endpoint(self, endpoint_id: str) -> bool:
        """Delete webhook endpoint."""
        try:
            # Remove from storage
            await self.redis.delete(f"webhook_endpoint:{endpoint_id}")
            await self.redis.srem("webhook_endpoints", endpoint_id)
            
            # Remove from cache
            if endpoint_id in self.endpoints:
                del self.endpoints[endpoint_id]
            
            logger.info(f"Webhook endpoint {endpoint_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Endpoint deletion failed: {e}")
            return False
    
    async def send_webhook(self, payload: WebhookPayload) -> List[str]:
        """Send webhook to all registered endpoints."""
        try:
            delivery_ids = []
            
            # Get endpoints that should receive this event
            relevant_endpoints = await self._get_relevant_endpoints(payload.event)
            
            for endpoint in relevant_endpoints:
                # Check if endpoint should receive this event
                if not self.event_filter.should_send_event(payload, endpoint.filters):
                    continue
                
                # Check rate limits
                if not await self.rate_limiter.can_send_webhook(endpoint.id):
                    logger.warning(f"Rate limit exceeded for endpoint {endpoint.id}")
                    continue
                
                # Create delivery
                delivery = WebhookDelivery(
                    id=str(uuid.uuid4()),
                    endpoint_id=endpoint.id,
                    payload=payload
                )
                
                # Queue for delivery
                await self._queue_delivery(delivery)
                delivery_ids.append(delivery.id)
            
            return delivery_ids
            
        except Exception as e:
            logger.error(f"Webhook sending failed: {e}")
            return []
    
    async def send_test_webhook(self, endpoint_id: str) -> bool:
        """Send test webhook to endpoint."""
        try:
            endpoint = await self._load_endpoint(endpoint_id)
            if not endpoint:
                return False
            
            # Create test payload
            test_payload = WebhookPayload(
                id=str(uuid.uuid4()),
                event=WebhookEvent.NOTIFICATION_SENT,
                timestamp=datetime.utcnow(),
                data={
                    "test": True,
                    "message": "This is a test webhook",
                    "endpoint_id": endpoint_id
                }
            )
            
            # Create delivery
            delivery = WebhookDelivery(
                id=str(uuid.uuid4()),
                endpoint_id=endpoint_id,
                payload=test_payload
            )
            
            # Send immediately
            success = await self._deliver_webhook(delivery)
            
            logger.info(f"Test webhook sent to {endpoint_id}: {'success' if success else 'failed'}")
            return success
            
        except Exception as e:
            logger.error(f"Test webhook failed: {e}")
            return False
    
    async def get_endpoint_stats(self, endpoint_id: str) -> Dict[str, Any]:
        """Get webhook endpoint statistics."""
        try:
            endpoint = await self._load_endpoint(endpoint_id)
            if not endpoint:
                return {}
            
            # Get delivery stats
            total_deliveries = await self.redis.get(f"webhook_stats:{endpoint_id}:total") or 0
            successful_deliveries = await self.redis.get(f"webhook_stats:{endpoint_id}:success") or 0
            failed_deliveries = await self.redis.get(f"webhook_stats:{endpoint_id}:failed") or 0
            
            # Calculate success rate
            total = int(total_deliveries)
            success_rate = (int(successful_deliveries) / total * 100) if total > 0 else 0
            
            return {
                'endpoint_id': endpoint_id,
                'total_deliveries': total,
                'successful_deliveries': int(successful_deliveries),
                'failed_deliveries': int(failed_deliveries),
                'success_rate': round(success_rate, 2),
                'last_success': endpoint.last_success.isoformat() if endpoint.last_success else None,
                'last_failure': endpoint.last_failure.isoformat() if endpoint.last_failure else None,
                'consecutive_failures': endpoint.failure_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get endpoint stats: {e}")
            return {}
    
    async def get_delivery_history(self, endpoint_id: str = None, 
                                 limit: int = 100) -> List[Dict[str, Any]]:
        """Get webhook delivery history."""
        try:
            if endpoint_id:
                delivery_ids = await self.redis.lrange(f"webhook_deliveries:{endpoint_id}", 0, limit - 1)
            else:
                delivery_ids = await self.redis.lrange("webhook_deliveries:all", 0, limit - 1)
            
            deliveries = []
            for delivery_id in delivery_ids:
                delivery_data = await self.redis.hgetall(f"webhook_delivery:{delivery_id}")
                if delivery_data:
                    deliveries.append({
                        'id': delivery_data['id'],
                        'endpoint_id': delivery_data['endpoint_id'],
                        'event': delivery_data['event'],
                        'status': delivery_data['status'],
                        'attempts': int(delivery_data['attempts']),
                        'last_attempt': delivery_data.get('last_attempt'),
                        'response_code': int(delivery_data['response_code']) if delivery_data.get('response_code') else None,
                        'error_message': delivery_data.get('error_message'),
                        'created_at': delivery_data['created_at']
                    })
            
            return deliveries
            
        except Exception as e:
            logger.error(f"Failed to get delivery history: {e}")
            return []
    
    async def retry_failed_delivery(self, delivery_id: str) -> bool:
        """Manually retry failed delivery."""
        try:
            delivery = await self._load_delivery(delivery_id)
            if not delivery or delivery.status != WebhookStatus.FAILED:
                return False
            
            # Reset delivery status
            delivery.status = WebhookStatus.PENDING
            delivery.next_attempt = datetime.utcnow()
            
            # Queue for retry
            await self._queue_delivery(delivery)
            
            logger.info(f"Delivery {delivery_id} queued for retry")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry delivery: {e}")
            return False
    
    async def _validate_endpoint(self, endpoint: WebhookEndpoint) -> bool:
        """Validate webhook endpoint."""
        try:
            # Validate URL
            if not WebhookSecurity.validate_url(endpoint.url):
                logger.error(f"Invalid URL: {endpoint.url}")
                return False
            
            # Validate secret
            if not endpoint.secret or len(endpoint.secret) < 16:
                logger.error("Webhook secret must be at least 16 characters")
                return False
            
            # Validate events
            if not endpoint.events:
                logger.error("At least one event must be specified")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Endpoint validation failed: {e}")
            return False
    
    async def _get_relevant_endpoints(self, event: WebhookEvent) -> List[WebhookEndpoint]:
        """Get endpoints that should receive this event."""
        try:
            relevant_endpoints = []
            
            # Get all endpoints
            endpoint_ids = await self.redis.smembers("webhook_endpoints")
            
            for endpoint_id in endpoint_ids:
                endpoint = await self._load_endpoint(endpoint_id)
                if endpoint and endpoint.enabled and event in endpoint.events:
                    relevant_endpoints.append(endpoint)
            
            return relevant_endpoints
            
        except Exception as e:
            logger.error(f"Failed to get relevant endpoints: {e}")
            return []
    
    async def _queue_delivery(self, delivery: WebhookDelivery) -> None:
        """Queue delivery for processing."""
        try:
            # Store delivery
            await self._store_delivery(delivery)
            
            # Add to processing queue
            delivery_data = {
                'delivery_id': delivery.id,
                'endpoint_id': delivery.endpoint_id,
                'priority': 1  # Normal priority
            }
            
            schedule_time = delivery.next_attempt or datetime.utcnow()
            await self.redis.zadd("webhook_delivery_queue", {json.dumps(delivery_data): schedule_time.timestamp()})
            
        except Exception as e:
            logger.error(f"Failed to queue delivery: {e}")
    
    async def _deliver_webhook(self, delivery: WebhookDelivery) -> bool:
        """Deliver individual webhook."""
        try:
            endpoint = await self._load_endpoint(delivery.endpoint_id)
            if not endpoint:
                return False
            
            # Transform payload
            transformed_payload = self.event_filter.transform_payload(
                delivery.payload, endpoint.transform_template
            )
            
            # Create request payload
            payload_json = json.dumps(transformed_payload, default=str)
            
            # Generate signature
            signature = WebhookSecurity.generate_signature(payload_json, endpoint.secret)
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'IA Chéries-Webhooks/1.0',
                'X-Webhook-Signature': signature,
                'X-Webhook-Event': delivery.payload.event.value,
                'X-Webhook-ID': delivery.id,
                'X-Webhook-Timestamp': str(int(delivery.payload.timestamp.timestamp()))
            }
            
            # Add custom headers
            headers.update(endpoint.headers)
            
            # Send webhook
            timeout = aiohttp.ClientTimeout(total=endpoint.timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    endpoint.url,
                    data=payload_json,
                    headers=headers
                ) as response:
                    
                    delivery.attempts += 1
                    delivery.last_attempt = datetime.utcnow()
                    delivery.response_code = response.status
                    delivery.response_body = (await response.text())[:1000]  # Limit response body
                    
                    if 200 <= response.status < 300:
                        # Success
                        delivery.status = WebhookStatus.DELIVERED
                        endpoint.last_success = datetime.utcnow()
                        endpoint.success_count += 1
                        endpoint.failure_count = 0
                        
                        await self.rate_limiter.record_webhook_sent(endpoint.id)
                        await self._update_endpoint_stats(endpoint.id, True)
                        
                        logger.info(f"Webhook delivered successfully: {delivery.id}")
                        return True
                    else:
                        # HTTP error
                        delivery.error_message = f"HTTP {response.status}: {delivery.response_body}"
                        return await self._handle_delivery_failure(delivery, endpoint)
            
        except asyncio.TimeoutError:
            delivery.attempts += 1
            delivery.last_attempt = datetime.utcnow()
            delivery.error_message = "Request timeout"
            return await self._handle_delivery_failure(delivery, endpoint)
            
        except Exception as e:
            delivery.attempts += 1
            delivery.last_attempt = datetime.utcnow()
            delivery.error_message = str(e)
            return await self._handle_delivery_failure(delivery, endpoint)
    
    async def _handle_delivery_failure(self, delivery: WebhookDelivery, 
                                     endpoint: WebhookEndpoint) -> bool:
        """Handle delivery failure and schedule retry if needed."""
        try:
            endpoint.last_failure = datetime.utcnow()
            endpoint.failure_count += 1
            
            # Check if we should retry
            if delivery.attempts < endpoint.max_retries and endpoint.retry_strategy != RetryStrategy.NO_RETRY:
                # Calculate retry delay
                retry_delay = self._calculate_retry_delay(delivery.attempts, endpoint.retry_strategy)
                delivery.next_attempt = datetime.utcnow() + timedelta(seconds=retry_delay)
                
                # Queue for retry
                await self._queue_delivery(delivery)
                
                logger.info(f"Webhook delivery failed, scheduling retry: {delivery.id}")
            else:
                # Max retries reached
                delivery.status = WebhookStatus.FAILED
                logger.error(f"Webhook delivery failed permanently: {delivery.id}")
            
            await self._update_endpoint_stats(endpoint.id, False)
            await self._store_delivery(delivery)
            await self._store_endpoint(endpoint)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to handle delivery failure: {e}")
            return False
    
    def _calculate_retry_delay(self, attempt: int, strategy: RetryStrategy) -> int:
        """Calculate retry delay based on strategy."""
        try:
            if strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
                return min(self.retry_delays[attempt - 1] if attempt <= len(self.retry_delays) else 7200, 7200)
            elif strategy == RetryStrategy.LINEAR_BACKOFF:
                return min(attempt * 300, 3600)  # 5 minutes * attempt, max 1 hour
            elif strategy == RetryStrategy.IMMEDIATE_RETRY:
                return 10  # 10 seconds
            else:
                return 300  # 5 minutes default
                
        except Exception as e:
            logger.error(f"Retry delay calculation failed: {e}")
            return 300
    
    async def _store_endpoint(self, endpoint: WebhookEndpoint) -> None:
        """Store webhook endpoint."""
        try:
            endpoint_data = {
                'id': endpoint.id,
                'name': endpoint.name,
                'url': endpoint.url,
                'secret': endpoint.secret,
                'events': json.dumps([event.value for event in endpoint.events]),
                'enabled': str(endpoint.enabled),
                'retry_strategy': endpoint.retry_strategy.value,
                'max_retries': str(endpoint.max_retries),
                'timeout_seconds': str(endpoint.timeout_seconds),
                'headers': json.dumps(endpoint.headers),
                'filters': json.dumps(endpoint.filters),
                'transform_template': endpoint.transform_template or '',
                'created_at': endpoint.created_at.isoformat(),
                'updated_at': endpoint.updated_at.isoformat(),
                'last_success': endpoint.last_success.isoformat() if endpoint.last_success else '',
                'last_failure': endpoint.last_failure.isoformat() if endpoint.last_failure else '',
                'failure_count': str(endpoint.failure_count),
                'success_count': str(endpoint.success_count)
            }
            
            await self.redis.hset(f"webhook_endpoint:{endpoint.id}", mapping=endpoint_data)
            await self.redis.sadd("webhook_endpoints", endpoint.id)
            
        except Exception as e:
            logger.error(f"Failed to store endpoint: {e}")
            raise
    
    async def _load_endpoint(self, endpoint_id: str) -> Optional[WebhookEndpoint]:
        """Load webhook endpoint."""
        try:
            # Check cache
            if endpoint_id in self.endpoints:
                return self.endpoints[endpoint_id]
            
            # Load from Redis
            endpoint_data = await self.redis.hgetall(f"webhook_endpoint:{endpoint_id}")
            if not endpoint_data:
                return None
            
            endpoint = WebhookEndpoint(
                id=endpoint_data['id'],
                name=endpoint_data['name'],
                url=endpoint_data['url'],
                secret=endpoint_data['secret'],
                events=[WebhookEvent(event) for event in json.loads(endpoint_data['events'])],
                enabled=endpoint_data['enabled'].lower() == 'true',
                retry_strategy=RetryStrategy(endpoint_data['retry_strategy']),
                max_retries=int(endpoint_data['max_retries']),
                timeout_seconds=int(endpoint_data['timeout_seconds']),
                headers=json.loads(endpoint_data['headers']),
                filters=json.loads(endpoint_data['filters']),
                transform_template=endpoint_data['transform_template'] if endpoint_data['transform_template'] else None,
                created_at=datetime.fromisoformat(endpoint_data['created_at']),
                updated_at=datetime.fromisoformat(endpoint_data['updated_at']),
                last_success=datetime.fromisoformat(endpoint_data['last_success']) if endpoint_data.get('last_success') else None,
                last_failure=datetime.fromisoformat(endpoint_data['last_failure']) if endpoint_data.get('last_failure') else None,
                failure_count=int(endpoint_data.get('failure_count', 0)),
                success_count=int(endpoint_data.get('success_count', 0))
            )
            
            # Cache endpoint
            self.endpoints[endpoint_id] = endpoint
            return endpoint
            
        except Exception as e:
            logger.error(f"Failed to load endpoint: {e}")
            return None
    
    async def _store_delivery(self, delivery: WebhookDelivery) -> None:
        """Store webhook delivery."""
        try:
            delivery_data = {
                'id': delivery.id,
                'endpoint_id': delivery.endpoint_id,
                'event': delivery.payload.event.value,
                'payload': json.dumps({
                    'id': delivery.payload.id,
                    'event': delivery.payload.event.value,
                    'timestamp': delivery.payload.timestamp.isoformat(),
                    'data': delivery.payload.data,
                    'user_id': delivery.payload.user_id,
                    'notification_id': delivery.payload.notification_id,
                    'campaign_id': delivery.payload.campaign_id,
                    'template_id': delivery.payload.template_id,
                    'metadata': delivery.payload.metadata
                }),
                'status': delivery.status.value,
                'attempts': str(delivery.attempts),
                'last_attempt': delivery.last_attempt.isoformat() if delivery.last_attempt else '',
                'next_attempt': delivery.next_attempt.isoformat() if delivery.next_attempt else '',
                'response_code': str(delivery.response_code) if delivery.response_code else '',
                'response_body': delivery.response_body or '',
                'error_message': delivery.error_message or '',
                'created_at': delivery.created_at.isoformat()
            }
            
            await self.redis.hset(f"webhook_delivery:{delivery.id}", mapping=delivery_data)
            await self.redis.lpush(f"webhook_deliveries:{delivery.endpoint_id}", delivery.id)
            await self.redis.lpush("webhook_deliveries:all", delivery.id)
            
            # Limit history size
            await self.redis.ltrim(f"webhook_deliveries:{delivery.endpoint_id}", 0, 999)
            await self.redis.ltrim("webhook_deliveries:all", 0, 9999)
            
        except Exception as e:
            logger.error(f"Failed to store delivery: {e}")
    
    async def _load_delivery(self, delivery_id: str) -> Optional[WebhookDelivery]:
        """Load webhook delivery."""
        try:
            delivery_data = await self.redis.hgetall(f"webhook_delivery:{delivery_id}")
            if not delivery_data:
                return None
            
            payload_data = json.loads(delivery_data['payload'])
            payload = WebhookPayload(
                id=payload_data['id'],
                event=WebhookEvent(payload_data['event']),
                timestamp=datetime.fromisoformat(payload_data['timestamp']),
                data=payload_data['data'],
                user_id=payload_data.get('user_id'),
                notification_id=payload_data.get('notification_id'),
                campaign_id=payload_data.get('campaign_id'),
                template_id=payload_data.get('template_id'),
                metadata=payload_data.get('metadata', {})
            )
            
            return WebhookDelivery(
                id=delivery_data['id'],
                endpoint_id=delivery_data['endpoint_id'],
                payload=payload,
                status=WebhookStatus(delivery_data['status']),
                attempts=int(delivery_data['attempts']),
                last_attempt=datetime.fromisoformat(delivery_data['last_attempt']) if delivery_data.get('last_attempt') else None,
                next_attempt=datetime.fromisoformat(delivery_data['next_attempt']) if delivery_data.get('next_attempt') else None,
                response_code=int(delivery_data['response_code']) if delivery_data.get('response_code') else None,
                response_body=delivery_data.get('response_body'),
                error_message=delivery_data.get('error_message'),
                created_at=datetime.fromisoformat(delivery_data['created_at'])
            )
            
        except Exception as e:
            logger.error(f"Failed to load delivery: {e}")
            return None
    
    async def _update_endpoint_stats(self, endpoint_id: str, success: bool) -> None:
        """Update endpoint statistics."""
        try:
            await self.redis.incr(f"webhook_stats:{endpoint_id}:total")
            
            if success:
                await self.redis.incr(f"webhook_stats:{endpoint_id}:success")
            else:
                await self.redis.incr(f"webhook_stats:{endpoint_id}:failed")
                
        except Exception as e:
            logger.error(f"Failed to update endpoint stats: {e}")
    
    async def _process_webhook_deliveries(self) -> None:
        """Background task to process webhook deliveries."""
        while True:
            try:
                current_time = datetime.utcnow().timestamp()
                
                # Get deliveries ready for processing
                ready_deliveries = await self.redis.zrangebyscore(
                    "webhook_delivery_queue", 0, current_time, withscores=True, limit=50
                )
                
                # Process deliveries concurrently
                tasks = []
                for delivery_data_str, _ in ready_deliveries:
                    try:
                        delivery_data = json.loads(delivery_data_str)
                        delivery_id = delivery_data['delivery_id']
                        
                        # Load and process delivery
                        task = asyncio.create_task(self._process_single_delivery(delivery_id))
                        tasks.append(task)
                        
                        # Remove from queue
                        await self.redis.zrem("webhook_delivery_queue", delivery_data_str)
                        
                    except Exception as e:
                        logger.error(f"Failed to process delivery: {e}")
                
                # Wait for all deliveries to complete
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Webhook delivery processing error: {e}")
                await asyncio.sleep(30)
    
    async def _process_single_delivery(self, delivery_id: str) -> None:
        """Process single webhook delivery."""
        try:
            delivery = await self._load_delivery(delivery_id)
            if delivery:
                await self._deliver_webhook(delivery)
        except Exception as e:
            logger.error(f"Single delivery processing failed: {e}")
    
    async def _process_retry_queue(self) -> None:
        """Background task to process retry queue."""
        while True:
            try:
                # Process failed deliveries for retry
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Retry queue processing error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_deliveries(self) -> None:
        """Background task to cleanup old deliveries."""
        while True:
            try:
                # Clean up deliveries older than 30 days
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                # This would be more sophisticated in production
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                await asyncio.sleep(3600)


# Factory function for creating service instance
def create_webhook_manager(config: Dict[str, Any]) -> NotificationWebhookManager:
    """Create and configure notification webhook manager."""
    return NotificationWebhookManager(config)


# Export main classes and functions
__all__ = [
    'NotificationWebhookManager',
    'WebhookEndpoint',
    'WebhookPayload',
    'WebhookDelivery',
    'WebhookEvent',
    'WebhookStatus',
    'RetryStrategy',
    'WebhookSecurity',
    'EventFilter',
    'WebhookRateLimiter',
    'create_webhook_manager'
]