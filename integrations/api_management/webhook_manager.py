"""Webhook Manager - Webhook Handling and Events
==============================================

Comprehensive webhook management system for handling real-time events 
from third-party integrations. Provides secure processing, validation, 
and event distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import hashlib
import hmac
import json
import logging
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import secrets
from urllib.parse import urlparse

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding


class WebhookEvent(Enum):
    """Webhook event types."""
    USER_AUTHENTICATED = "user.authenticated"
    USER_DEAUTHORIZED = "user.deauthorized"
    CONTENT_UPLOADED = "content.uploaded"
    CONTENT_PROCESSED = "content.processed"
    CONTENT_PUBLISHED = "content.published"
    CONTENT_DELETED = "content.deleted"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    COLLABORATION_REQUESTED = "collaboration.requested"
    COLLABORATION_ACCEPTED = "collaboration.accepted"
    INTEGRATION_ERROR = "integration.error"
    RATE_LIMIT_EXCEEDED = "rate_limit.exceeded"
    SECURITY_ALERT = "security.alert"
    CUSTOM_EVENT = "custom.event"


class WebhookStatus(Enum):
    """Webhook delivery status."""
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"


class SignatureAlgorithm(Enum):
    """Webhook signature algorithms."""
    HMAC_SHA256 = "hmac_sha256"
    HMAC_SHA512 = "hmac_sha512"
    RSA_SHA256 = "rsa_sha256"
    ED25519 = "ed25519"


@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration."""
    url: str
    integration_name: str
    events: Set[WebhookEvent]
    secret: str
    signature_algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256
    is_active: bool = True
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    timeout: int = 30  # seconds
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookPayload:
    """Webhook payload data."""
    event: WebhookEvent
    data: Dict[str, Any]
    timestamp: datetime
    integration_name: str
    user_id: Optional[str] = None
    request_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookDelivery:
    """Webhook delivery tracking."""
    id: str
    endpoint_url: str
    payload: WebhookPayload
    status: WebhookStatus
    attempts: int = 0
    last_attempt_at: Optional[datetime] = None
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


WebhookHandler = Callable[[WebhookPayload], None]


class WebhookManager:
    """Comprehensive webhook management system.
    
    Handles incoming and outgoing webhooks for all platform integrations,
    ensuring secure, reliable, and scalable event processing.
    """
    
    def __init__(self) -> None:
        """Initialize webhook manager."""
        self.logger = logging.getLogger(__name__)
        
        # Webhook endpoints registry
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        
        # Event handlers registry
        self.handlers: Dict[WebhookEvent, List[WebhookHandler]] = {}
        
        # Delivery tracking
        self.deliveries: Dict[str, WebhookDelivery] = {}
        
        # Security settings
        self.allowed_ips: Set[str] = set()
        self.blocked_ips: Set[str] = set()
        
        # Processing queues
        self.incoming_queue: asyncio.Queue = asyncio.Queue()
        self.outgoing_queue: asyncio.Queue = asyncio.Queue()
        
        # Worker tasks
        self.workers: List[asyncio.Task] = []
        
        # Initialize default event handlers
        self._initialize_default_handlers()
    
    def _initialize_default_handlers(self) -> None:
        """Initialize default webhook event handlers."""
        # Business logic event handlers for Ainflue workflow
        
        async def handle_user_authenticated(payload -> None: WebhookPayload) -> None:
            """Handle user authentication event."""
            self.logger.info(f"User authenticated: {payload.user_id} on {payload.integration_name}")
            # Trigger user onboarding workflow
            await self._trigger_internal_event("user_onboarding_started", payload.data)
        
        async def handle_content_uploaded(payload -> None: WebhookPayload) -> None:
            """Handle content upload event."""
            self.logger.info(f"Content uploaded: {payload.data.get('content_id')} by {payload.user_id}")
            # Trigger AI processing workflow
            await self._trigger_internal_event("ai_processing_queued", payload.data)
        
        async def handle_content_processed(payload -> None: WebhookPayload) -> None:
            """Handle content processing completion."""
            self.logger.info(f"Content processed: {payload.data.get('content_id')}")
            # Trigger protection and SEO workflow
            await self._trigger_internal_event("protection_analysis_started", payload.data)
        
        async def handle_payment_completed(payload -> None: WebhookPayload) -> None:
            """Handle successful payment."""
            self.logger.info(f"Payment completed: {payload.data.get('payment_id')}")
            # Trigger revenue distribution workflow
            await self._trigger_internal_event("revenue_distribution_started", payload.data)
        
        async def handle_collaboration_requested(payload -> None: WebhookPayload) -> None:
            """Handle collaboration request."""
            self.logger.info(f"Collaboration requested: {payload.data.get('collaboration_id')}")
            # Trigger matching algorithm
            await self._trigger_internal_event("collaboration_matching_started", payload.data)
        
        # Register default handlers
        self.register_handler(WebhookEvent.USER_AUTHENTICATED, handle_user_authenticated)
        self.register_handler(WebhookEvent.CONTENT_UPLOADED, handle_content_uploaded)
        self.register_handler(WebhookEvent.CONTENT_PROCESSED, handle_content_processed)
        self.register_handler(WebhookEvent.PAYMENT_COMPLETED, handle_payment_completed)
        self.register_handler(WebhookEvent.COLLABORATION_REQUESTED, handle_collaboration_requested)
    
    async def register_endpoint(self, endpoint: WebhookEndpoint) -> str:
        """Register a webhook endpoint."""
        try:
            # Validate endpoint configuration
            if not self._validate_endpoint(endpoint):
                raise ValueError("Invalid endpoint configuration")
            
            # Generate endpoint ID
            endpoint_id = self._generate_endpoint_id(endpoint.url, endpoint.integration_name)
            
            # Store endpoint
            self.endpoints[endpoint_id] = endpoint
            
            self.logger.info(f"Webhook endpoint registered: {endpoint_id} for {endpoint.integration_name}")
            
            return endpoint_id
            
        except Exception as e:
            self.logger.error(f"Failed to register webhook endpoint: {str(e)}")
            raise
    
    async def unregister_endpoint(self, endpoint_id: str) -> bool:
        """Unregister a webhook endpoint."""
        try:
            if endpoint_id in self.endpoints:
                del self.endpoints[endpoint_id]
                self.logger.info(f"Webhook endpoint unregistered: {endpoint_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to unregister webhook endpoint: {str(e)}")
            return False
    
    def register_handler(self, event: WebhookEvent, handler: WebhookHandler) -> None:
        """Register event handler."""
        if event not in self.handlers:
            self.handlers[event] = []
        
        self.handlers[event].append(handler)
        self.logger.info(f"Handler registered for event: {event.value}")
    
    def unregister_handler(self, event: WebhookEvent, handler: WebhookHandler) -> bool:
        """Unregister event handler."""
        if event in self.handlers and handler in self.handlers[event]:
            self.handlers[event].remove(handler)
            self.logger.info(f"Handler unregistered for event: {event.value}")
            return True
        return False
    
    async def process_incoming_webhook(
        self,
        integration_name: str,
        headers: Dict[str, str],
        body: bytes,
        source_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process incoming webhook from third-party integration."""
        try:
            # Security validation
            if not await self._validate_incoming_security(source_ip):
                return {"error": "Access denied", "status": 403}
            
            # Parse and validate payload
            payload_data = json.loads(body.decode('utf-8'))
            
            # Find matching endpoint for validation
            endpoint = self._find_endpoint_by_integration(integration_name)
            if not endpoint:
                return {"error": "Integration not configured", "status": 404}
            
            # Verify webhook signature
            if not await self._verify_signature(endpoint, headers, body):
                return {"error": "Invalid signature", "status": 401}
            
            # Create webhook payload
            payload = self._parse_incoming_payload(integration_name, payload_data)
            
            # Queue for processing
            await self.incoming_queue.put(payload)
            
            self.logger.info(f"Incoming webhook queued: {integration_name} - {payload.event.value}")
            
            return {"message": "Webhook received", "status": 200}
            
        except json.JSONDecodeError:
            return {"error": "Invalid JSON payload", "status": 400}
        except Exception as e:
            self.logger.error(f"Error processing incoming webhook: {str(e)}")
            return {"error": "Internal server error", "status": 500}
    
    async def send_webhook(
        self,
        event: WebhookEvent,
        data: Dict[str, Any],
        integration_name: str,
        user_id: Optional[str] = None,
        target_endpoints: Optional[List[str]] = None
    ) -> List[str]:
        """Send webhook to registered endpoints."""
        try:
            # Create payload
            payload = WebhookPayload(
                event=event,
                data=data,
                timestamp=datetime.utcnow(),
                integration_name=integration_name,
                user_id=user_id,
                request_id=secrets.token_hex(16)
            )
            
            # Find target endpoints
            endpoints_to_notify = []
            
            if target_endpoints:
                endpoints_to_notify = [
                    self.endpoints[ep_id] for ep_id in target_endpoints
                    if ep_id in self.endpoints and event in self.endpoints[ep_id].events
                ]
            else:
                endpoints_to_notify = [
                    endpoint for endpoint in self.endpoints.values()
                    if event in endpoint.events and endpoint.is_active
                ]
            
            # Create deliveries
            delivery_ids = []
            
            for endpoint in endpoints_to_notify:
                delivery = WebhookDelivery(
                    id=secrets.token_hex(16),
                    endpoint_url=endpoint.url,
                    payload=payload,
                    status=WebhookStatus.PENDING
                )
                
                self.deliveries[delivery.id] = delivery
                delivery_ids.append(delivery.id)
                
                # Queue for delivery
                await self.outgoing_queue.put(delivery)
            
            self.logger.info(f"Webhook queued for delivery: {event.value} to {len(delivery_ids)} endpoints")
            
            return delivery_ids
            
        except Exception as e:
            self.logger.error(f"Error sending webhook: {str(e)}")
            return []
    
    async def process_webhook(self, integration_name: str, webhook_data: Dict[str, Any]) -> bool:
        """Process webhook data and trigger appropriate handlers."""
        try:
            # Parse webhook event
            event = self._determine_event_type(integration_name, webhook_data)
            
            # Create payload
            payload = WebhookPayload(
                event=event,
                data=webhook_data,
                timestamp=datetime.utcnow(),
                integration_name=integration_name,
                request_id=secrets.token_hex(16)
            )
            
            # Execute handlers
            await self._execute_handlers(payload)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing webhook: {str(e)}")
            return False
    
    async def retry_failed_delivery(self, delivery_id: str) -> bool:
        """Retry failed webhook delivery."""
        try:
            if delivery_id not in self.deliveries:
                return False
            
            delivery = self.deliveries[delivery_id]
            
            if delivery.status not in [WebhookStatus.FAILED, WebhookStatus.EXPIRED]:
                return False
            
            # Reset delivery status
            delivery.status = WebhookStatus.PENDING
            delivery.updated_at = datetime.utcnow()
            
            # Queue for retry
            await self.outgoing_queue.put(delivery)
            
            self.logger.info(f"Webhook delivery queued for retry: {delivery_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error retrying webhook delivery: {str(e)}")
            return False
    
    async def get_delivery_status(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        """Get webhook delivery status."""
        if delivery_id not in self.deliveries:
            return None
        
        delivery = self.deliveries[delivery_id]
        
        return {
            "id": delivery.id,
            "endpoint_url": delivery.endpoint_url,
            "event": delivery.payload.event.value,
            "status": delivery.status.value,
            "attempts": delivery.attempts,
            "last_attempt_at": delivery.last_attempt_at.isoformat() if delivery.last_attempt_at else None,
            "response_status": delivery.response_status,
            "error_message": delivery.error_message,
            "created_at": delivery.created_at.isoformat(),
            "updated_at": delivery.updated_at.isoformat()
        }
    
    async def get_endpoint_statistics(self, endpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get webhook endpoint statistics."""
        if endpoint_id not in self.endpoints:
            return None
        
        endpoint = self.endpoints[endpoint_id]
        
        # Calculate statistics
        endpoint_deliveries = [
            d for d in self.deliveries.values()
            if d.endpoint_url == endpoint.url
        ]
        
        total_deliveries = len(endpoint_deliveries)
        successful_deliveries = len([d for d in endpoint_deliveries if d.status == WebhookStatus.DELIVERED])
        failed_deliveries = len([d for d in endpoint_deliveries if d.status == WebhookStatus.FAILED])
        
        success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        
        return {
            "endpoint_id": endpoint_id,
            "url": endpoint.url,
            "integration_name": endpoint.integration_name,
            "is_active": endpoint.is_active,
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "success_rate": round(success_rate, 2),
            "events": [event.value for event in endpoint.events]
        }
    
    async def start_workers(self, num_workers: int = 3) -> None:
        """Start webhook processing workers."""
        self.logger.info(f"Starting {num_workers} webhook workers...")
        
        # Start incoming webhook processors
        for i in range(num_workers):
            task = asyncio.create_task(self._incoming_worker(f"incoming-{i}"))
            self.workers.append(task)
        
        # Start outgoing webhook processors
        for i in range(num_workers):
            task = asyncio.create_task(self._outgoing_worker(f"outgoing-{i}"))
            self.workers.append(task)
        
        self.logger.info("Webhook workers started successfully")
    
    async def stop_workers(self) -> None:
        """Stop webhook processing workers."""
        self.logger.info("Stopping webhook workers...")
        
        # Cancel all worker tasks
        for task in self.workers:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        self.workers.clear()
        self.logger.info("Webhook workers stopped successfully")
    
    async def _incoming_worker(self, worker_id: str) -> None:
        """Worker for processing incoming webhooks."""
        self.logger.info(f"Incoming webhook worker started: {worker_id}")
        
        try:
            while True:
                # Get payload from queue
                payload = await self.incoming_queue.get()
                
                try:
                    # Execute event handlers
                    await self._execute_handlers(payload)
                    
                    self.logger.debug(f"Incoming webhook processed: {payload.event.value}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing incoming webhook: {str(e)}")
                
                finally:
                    self.incoming_queue.task_done()
                    
        except asyncio.CancelledError:
            self.logger.info(f"Incoming webhook worker stopped: {worker_id}")
            raise
    
    async def _outgoing_worker(self, worker_id: str) -> None:
        """Worker for delivering outgoing webhooks."""
        self.logger.info(f"Outgoing webhook worker started: {worker_id}")
        
        try:
            while True:
                # Get delivery from queue
                delivery = await self.outgoing_queue.get()
                
                try:
                    # Attempt delivery
                    await self._attempt_delivery(delivery)
                    
                    self.logger.debug(f"Webhook delivery attempted: {delivery.id}")
                    
                except Exception as e:
                    self.logger.error(f"Error during webhook delivery: {str(e)}")
                
                finally:
                    self.outgoing_queue.task_done()
                    
        except asyncio.CancelledError:
            self.logger.info(f"Outgoing webhook worker stopped: {worker_id}")
            raise
    
    async def _execute_handlers(self, payload: WebhookPayload) -> None:
        """Execute all registered handlers for webhook event."""
        if payload.event in self.handlers:
            handlers = self.handlers[payload.event]
            
            # Execute handlers concurrently
            tasks = [handler(payload) for handler in handlers]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _attempt_delivery(self, delivery: WebhookDelivery) -> None:
        """Attempt webhook delivery to endpoint."""
        delivery.status = WebhookStatus.PROCESSING
        delivery.attempts += 1
        delivery.last_attempt_at = datetime.utcnow()
        delivery.updated_at = datetime.utcnow()
        
        try:
            # Find endpoint configuration
            endpoint = self._find_endpoint_by_url(delivery.endpoint_url)
            if not endpoint:
                delivery.status = WebhookStatus.FAILED
                delivery.error_message = "Endpoint configuration not found"
                return
            
            # Prepare payload
            payload_data = {
                "event": delivery.payload.event.value,
                "data": delivery.payload.data,
                "timestamp": delivery.payload.timestamp.isoformat(),
                "integration_name": delivery.payload.integration_name,
                "user_id": delivery.payload.user_id,
                "request_id": delivery.payload.request_id,
                "metadata": delivery.payload.metadata
            }
            
            # Generate signature
            payload_json = json.dumps(payload_data, sort_keys=True)
            signature = self._generate_signature(endpoint, payload_json.encode())
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature,
                "X-Webhook-Event": delivery.payload.event.value,
                "X-Webhook-Integration": delivery.payload.integration_name,
                "X-Webhook-Timestamp": str(int(delivery.payload.timestamp.timestamp())),
                **endpoint.headers
            }
            
            # Send webhook
            async with httpx.AsyncClient(timeout=endpoint.timeout) as client:
                response = await client.post(
                    delivery.endpoint_url,
                    json=payload_data,
                    headers=headers
                )
                
                delivery.response_status = response.status_code
                delivery.response_body = response.text[:1000]  # Limit response body storage
                
                if 200 <= response.status_code < 300:
                    delivery.status = WebhookStatus.DELIVERED
                else:
                    delivery.status = WebhookStatus.FAILED
                    delivery.error_message = f"HTTP {response.status_code}: {response.text[:200]}"
                    
                    # Schedule retry if attempts remain
                    if delivery.attempts < endpoint.max_retries:
                        await self._schedule_retry(delivery, endpoint.retry_delay)
        
        except Exception as e:
            delivery.status = WebhookStatus.FAILED
            delivery.error_message = str(e)
            
            # Find endpoint for retry configuration
            endpoint = self._find_endpoint_by_url(delivery.endpoint_url)
            if endpoint and delivery.attempts < endpoint.max_retries:
                await self._schedule_retry(delivery, endpoint.retry_delay)
        
        finally:
            delivery.updated_at = datetime.utcnow()
    
    async def _schedule_retry(self, delivery: WebhookDelivery, delay: int) -> None:
        """Schedule webhook delivery retry."""
        delivery.status = WebhookStatus.RETRYING
        
        # Schedule retry with exponential backoff
        retry_delay = delay * (2 ** (delivery.attempts - 1))
        
        async def retry_task() -> None:
            await asyncio.sleep(retry_delay)
            await self.outgoing_queue.put(delivery)
        
        asyncio.create_task(retry_task())
    
    async def _trigger_internal_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Trigger internal Ainflue workflow events."""
        # This would integrate with the main Ainflue event system
        self.logger.info(f"Internal event triggered: {event_name}")
        # Implementation would depend on the main event system
    
    def _validate_endpoint(self, endpoint: WebhookEndpoint) -> bool:
        """Validate webhook endpoint configuration."""
        # Validate URL
        try:
            parsed_url = urlparse(endpoint.url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return False
        except Exception:
            return False
        
        # Validate other fields
        if not endpoint.integration_name or not endpoint.secret:
            return False
        
        if not endpoint.events:
            return False
        
        return True
    
    def _generate_endpoint_id(self, url: str, integration_name: str) -> str:
        """Generate unique endpoint identifier."""
        data = f"{url}:{integration_name}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _find_endpoint_by_integration(self, integration_name: str) -> Optional[WebhookEndpoint]:
        """Find endpoint by integration name."""
        for endpoint in self.endpoints.values():
            if endpoint.integration_name == integration_name:
                return endpoint
        return None
    
    def _find_endpoint_by_url(self, url: str) -> Optional[WebhookEndpoint]:
        """Find endpoint by URL."""
        for endpoint in self.endpoints.values():
            if endpoint.url == url:
                return endpoint
        return None
    
    async def _validate_incoming_security(self, source_ip: Optional[str]) -> bool:
        """Validate incoming webhook security."""
        if source_ip:
            # Check blocked IPs
            if source_ip in self.blocked_ips:
                return False
            
            # Check allowed IPs (if configured)
            if self.allowed_ips and source_ip not in self.allowed_ips:
                return False
        
        return True
    
    async def _verify_signature(
        self,
        endpoint: WebhookEndpoint,
        headers: Dict[str, str],
        body: bytes
    ) -> bool:
        """Verify webhook signature."""
        signature_header = headers.get("X-Webhook-Signature") or headers.get("X-Hub-Signature-256")
        
        if not signature_header:
            return False
        
        try:
            if endpoint.signature_algorithm == SignatureAlgorithm.HMAC_SHA256:
                expected_signature = hmac.new(
                    endpoint.secret.encode(),
                    body,
                    hashlib.sha256
                ).hexdigest()
                
                # Remove algorithm prefix if present
                if signature_header.startswith("sha256="):
                    signature_header = signature_header[7:]
                
                return hmac.compare_digest(expected_signature, signature_header)
            
            # Add other signature algorithms as needed
            return False
            
        except Exception:
            return False
    
    def _generate_signature(self, endpoint: WebhookEndpoint, payload: bytes) -> str:
        """Generate webhook signature."""
        if endpoint.signature_algorithm == SignatureAlgorithm.HMAC_SHA256:
            signature = hmac.new(
                endpoint.secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            return f"sha256={signature}"
        
        # Add other signature algorithms as needed
        return ""
    
    def _parse_incoming_payload(self, integration_name: str, data: Dict[str, Any]) -> WebhookPayload:
        """Parse incoming webhook payload."""
        # Determine event type based on integration and payload
        event = self._determine_event_type(integration_name, data)
        
        return WebhookPayload(
            event=event,
            data=data,
            timestamp=datetime.utcnow(),
            integration_name=integration_name,
            request_id=secrets.token_hex(16)
        )
    
    def _determine_event_type(self, integration_name: str, data: Dict[str, Any]) -> WebhookEvent:
        """Determine webhook event type from payload."""
        # Integration-specific event mapping
        event_mappings = {
            "stripe": {
                "payment_intent.succeeded": WebhookEvent.PAYMENT_COMPLETED,
                "payment_intent.payment_failed": WebhookEvent.PAYMENT_FAILED,
                "customer.subscription.created": WebhookEvent.SUBSCRIPTION_CREATED,
                "customer.subscription.deleted": WebhookEvent.SUBSCRIPTION_CANCELLED,
            },
            "youtube": {
                "video.upload": WebhookEvent.CONTENT_UPLOADED,
                "video.processed": WebhookEvent.CONTENT_PROCESSED,
                "video.published": WebhookEvent.CONTENT_PUBLISHED,
            },
            "instagram": {
                "media.upload": WebhookEvent.CONTENT_UPLOADED,
                "media.published": WebhookEvent.CONTENT_PUBLISHED,
            },
            "spotify": {
                "track.upload": WebhookEvent.CONTENT_UPLOADED,
                "track.published": WebhookEvent.CONTENT_PUBLISHED,
            }
        }
        
        # Get event type from payload
        event_type = data.get("type") or data.get("event") or data.get("event_type")
        
        if integration_name in event_mappings and event_type in event_mappings[integration_name]:
            return event_mappings[integration_name][event_type]
        
        return WebhookEvent.CUSTOM_EVENT