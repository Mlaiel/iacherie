"""Webhook Management System
===========================

Centralized webhook handling and event processing for all platform integrations.
Supports webhook registration, validation, routing, and real-time event processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import hmac
import hashlib
import time
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
from aiohttp import web
import ssl
import traceback


class WebhookStatus(Enum):
    """Webhook status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    PENDING = "pending"


class EventType(Enum):
    """Common webhook event types"""
    USER_AUTHORIZED = "user.authorized"
    USER_DEAUTHORIZED = "user.deauthorized"
    CONTENT_UPLOADED = "content.uploaded"
    CONTENT_DELETED = "content.deleted"
    CONTENT_UPDATED = "content.updated"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    API_LIMIT_REACHED = "api.limit_reached"
    ERROR_OCCURRED = "error.occurred"


@dataclass
class WebhookEvent:
    """Webhook event data structure"""
    id: str
    event_type: str
    provider: str
    timestamp: datetime
    data: Dict[str, Any]
    signature: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    user_id: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration"""
    id: str
    provider: str
    url: str
    secret: str
    events: List[str]
    status: WebhookStatus = WebhookStatus.ACTIVE
    retry_attempts: int = 3
    retry_delay: int = 60
    signature_header: str = "X-Hub-Signature-256"
    signature_method: str = "sha256"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class WebhookManager:
    """Centralized webhook management system"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        """Initialize webhook manager
        
        Args:
            host: Server host
            port: Server port
        """
        self.logger = logging.getLogger(__name__)
        self.host = host
        self.port = port
        
        # Webhook storage
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.event_queue = asyncio.Queue()
        
        # Web server
        self.app = web.Application()
        self.runner = None
        self.site = None
        
        # Statistics
        self.stats = {
            "events_received": 0,
            "events_processed": 0,
            "events_failed": 0,
            "provider_stats": {}
        }
        
        # Processing tasks
        self.processor_tasks = []
        self.is_running = False
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup webhook routes"""
        self.app.router.add_post('/webhook/{provider}', self._handle_webhook)
        self.app.router.add_get('/webhook/health', self._health_check)
        self.app.router.add_get('/webhook/stats', self._get_stats)
    
    async def start(self, ssl_context: Optional[ssl.SSLContext] = None):
        """Start webhook server
        
        Args:
            ssl_context: SSL context for HTTPS
        """
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(
                self.runner, 
                self.host, 
                self.port,
                ssl_context=ssl_context
            )
            await self.site.start()
            
            # Start event processors
            self.is_running = True
            for i in range(3):  # Start 3 processor workers
                task = asyncio.create_task(self._process_events())
                self.processor_tasks.append(task)
            
            self.logger.info(f"Webhook server started on {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start webhook server: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown webhook server"""
        try:
            self.is_running = False
            
            # Cancel processor tasks
            for task in self.processor_tasks:
                task.cancel()
            
            await asyncio.gather(*self.processor_tasks, return_exceptions=True)
            
            # Shutdown server
            if self.site:
                await self.site.stop()
            
            if self.runner:
                await self.runner.cleanup()
            
            self.logger.info("Webhook server shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during webhook server shutdown: {e}")
    
    def register_endpoint(self, endpoint: WebhookEndpoint):
        """Register webhook endpoint
        
        Args:
            endpoint: Webhook endpoint configuration
        """
        self.endpoints[endpoint.id] = endpoint
        
        # Initialize provider stats
        if endpoint.provider not in self.stats["provider_stats"]:
            self.stats["provider_stats"][endpoint.provider] = {
                "events_received": 0,
                "events_processed": 0,
                "events_failed": 0
            }
        
        self.logger.info(f"Registered webhook endpoint: {endpoint.id} for {endpoint.provider}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler
        
        Args:
            event_type: Event type to handle
            handler: Handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        self.logger.info(f"Registered handler for event type: {event_type}")
    
    def unregister_event_handler(self, event_type: str, handler: Callable):
        """Unregister event handler
        
        Args:
            event_type: Event type
            handler: Handler function to remove
        """
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                self.logger.info(f"Unregistered handler for event type: {event_type}")
            except ValueError:
                self.logger.warning(f"Handler not found for event type: {event_type}")
    
    async def _handle_webhook(self, request: web.Request) -> web.Response:
        """Handle incoming webhook request
        
        Args:
            request: HTTP request
            
        Returns:
            web.Response: HTTP response
        """
        provider = request.match_info['provider']
        
        try:
            # Get request data
            body = await request.read()
            headers = dict(request.headers)
            
            # Find matching endpoint
            endpoint = self._find_endpoint(provider, headers)
            if not endpoint:
                self.logger.warning(f"No endpoint found for provider: {provider}")
                return web.Response(status=404, text="Endpoint not found")
            
            # Verify signature
            if not await self._verify_signature(endpoint, body, headers):
                self.logger.warning(f"Invalid signature for webhook: {provider}")
                return web.Response(status=401, text="Invalid signature")
            
            # Parse event data
            try:
                event_data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                self.logger.error(f"Invalid JSON in webhook: {provider}")
                return web.Response(status=400, text="Invalid JSON")
            
            # Create webhook event
            event = WebhookEvent(
                id=self._generate_event_id(),
                event_type=self._extract_event_type(provider, event_data),
                provider=provider,
                timestamp=datetime.utcnow(),
                data=event_data,
                headers=headers,
                signature=headers.get(endpoint.signature_header),
                user_id=self._extract_user_id(provider, event_data)
            )
            
            # Queue event for processing
            await self.event_queue.put(event)
            
            # Update statistics
            self.stats["events_received"] += 1
            self.stats["provider_stats"][provider]["events_received"] += 1
            
            self.logger.info(f"Received webhook event: {event.id} from {provider}")
            return web.Response(status=200, text="OK")
            
        except Exception as e:
            self.logger.error(f"Error handling webhook from {provider}: {e}")
            return web.Response(status=500, text="Internal server error")
    
    async def _health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint
        
        Args:
            request: HTTP request
            
        Returns:
            web.Response: Health status
        """
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": len(self.endpoints),
            "queue_size": self.event_queue.qsize(),
            "is_running": self.is_running
        }
        
        return web.json_response(health_data)
    
    async def _get_stats(self, request: web.Request) -> web.Response:
        """Get webhook statistics
        
        Args:
            request: HTTP request
            
        Returns:
            web.Response: Statistics data
        """
        return web.json_response(self.stats)
    
    def _find_endpoint(self, provider: str, headers: Dict[str, str]) -> Optional[WebhookEndpoint]:
        """Find matching webhook endpoint
        
        Args:
            provider: Provider name
            headers: Request headers
            
        Returns:
            Optional[WebhookEndpoint]: Matching endpoint
        """
        for endpoint in self.endpoints.values():
            if endpoint.provider == provider and endpoint.status == WebhookStatus.ACTIVE:
                return endpoint
        return None
    
    async def _verify_signature(self, endpoint: WebhookEndpoint, body: bytes, 
                              headers: Dict[str, str]) -> bool:
        """Verify webhook signature
        
        Args:
            endpoint: Webhook endpoint
            body: Request body
            headers: Request headers
            
        Returns:
            bool: Signature is valid
        """
        signature_header = endpoint.signature_header
        received_signature = headers.get(signature_header)
        
        if not received_signature:
            return False
        
        # Generate expected signature
        if endpoint.signature_method == "sha256":
            expected_signature = hmac.new(
                endpoint.secret.encode('utf-8'),
                body,
                hashlib.sha256
            ).hexdigest()
            
            # Different providers use different formats
            if endpoint.provider == "github":
                expected_signature = f"sha256={expected_signature}"
            elif endpoint.provider == "facebook":
                expected_signature = f"sha256={expected_signature}"
            elif endpoint.provider == "shopify":
                expected_signature = expected_signature
        
        else:
            # MD5 or other methods
            expected_signature = hmac.new(
                endpoint.secret.encode('utf-8'),
                body,
                getattr(hashlib, endpoint.signature_method)
            ).hexdigest()
        
        # Secure comparison
        return hmac.compare_digest(received_signature, expected_signature)
    
    def _extract_event_type(self, provider: str, data: Dict[str, Any]) -> str:
        """Extract event type from webhook data
        
        Args:
            provider: Provider name
            data: Webhook data
            
        Returns:
            str: Event type
        """
        # Provider-specific event type extraction
        if provider == "stripe":
            return data.get("type", "unknown")
        elif provider == "github":
            return data.get("action", "unknown")
        elif provider == "facebook":
            return data.get("object", {}).get("entry", [{}])[0].get("messaging", [{}])[0].get("type", "unknown")
        elif provider == "twitter":
            return data.get("tweet_create_events", "unknown")
        elif provider == "youtube":
            return data.get("kind", "unknown")
        elif provider == "instagram":
            return data.get("object", "unknown")
        else:
            return data.get("event_type", data.get("type", "unknown"))
    
    def _extract_user_id(self, provider: str, data: Dict[str, Any]) -> Optional[str]:
        """Extract user ID from webhook data
        
        Args:
            provider: Provider name
            data: Webhook data
            
        Returns:
            Optional[str]: User ID
        """
        # Provider-specific user ID extraction
        if provider == "stripe":
            return data.get("data", {}).get("object", {}).get("customer")
        elif provider == "github":
            return str(data.get("sender", {}).get("id"))
        elif provider == "facebook":
            return data.get("object", {}).get("entry", [{}])[0].get("id")
        elif provider == "twitter":
            return data.get("for_user_id")
        elif provider == "youtube":
            return data.get("snippet", {}).get("channelId")
        elif provider == "instagram":
            return data.get("object", {}).get("entry", [{}])[0].get("id")
        else:
            return data.get("user_id")
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID
        
        Returns:
            str: Unique event ID
        """
        timestamp = int(time.time() * 1000)
        return f"evt_{timestamp}_{hash(time.time()) % 10000:04d}"
    
    async def _process_events(self):
        """Process events from queue"""
        while self.is_running:
            try:
                # Get event from queue (with timeout)
                event = await asyncio.wait_for(
                    self.event_queue.get(), 
                    timeout=1.0
                )
                
                await self._handle_event(event)
                
            except asyncio.TimeoutError:
                # No events to process, continue
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
    
    async def _handle_event(self, event: WebhookEvent):
        """Handle individual webhook event
        
        Args:
            event: Webhook event to handle
        """
        try:
            # Get handlers for this event type
            handlers = self.event_handlers.get(event.event_type, [])
            generic_handlers = self.event_handlers.get("*", [])  # Wildcard handlers
            
            all_handlers = handlers + generic_handlers
            
            if not all_handlers:
                self.logger.warning(f"No handlers for event type: {event.event_type}")
                return
            
            # Process with all handlers
            for handler in all_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                        
                except Exception as e:
                    self.logger.error(f"Handler error for event {event.id}: {e}")
                    self.logger.error(traceback.format_exc())
            
            # Update statistics
            self.stats["events_processed"] += 1
            self.stats["provider_stats"][event.provider]["events_processed"] += 1
            
            self.logger.debug(f"Successfully processed event: {event.id}")
            
        except Exception as e:
            # Update failure statistics
            self.stats["events_failed"] += 1
            self.stats["provider_stats"][event.provider]["events_failed"] += 1
            
            self.logger.error(f"Failed to process event {event.id}: {e}")
            
            # Retry logic could be added here
            if event.retry_count < 3:
                event.retry_count += 1
                # Re-queue for retry after delay
                await asyncio.sleep(event.retry_count * 60)  # Exponential backoff
                await self.event_queue.put(event)
    
    async def send_webhook(self, url: str, data: Dict[str, Any], 
                         secret: Optional[str] = None, headers: Optional[Dict[str, str]] = None) -> bool:
        """Send webhook to external URL
        
        Args:
            url: Target URL
            data: Webhook data
            secret: Secret for signature
            headers: Additional headers
            
        Returns:
            bool: Success status
        """
        try:
            payload = json.dumps(data)
            request_headers = {
                "Content-Type": "application/json",
                "User-Agent": "Ainflue-Webhook/1.0"
            }
            
            if headers:
                request_headers.update(headers)
            
            # Add signature if secret provided
            if secret:
                signature = hmac.new(
                    secret.encode('utf-8'),
                    payload.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                request_headers["X-Ainflue-Signature"] = f"sha256={signature}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    data=payload, 
                    headers=request_headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        self.logger.info(f"Successfully sent webhook to {url}")
                        return True
                    else:
                        self.logger.warning(f"Webhook failed: {response.status} for {url}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Error sending webhook to {url}: {e}")
            return False
    
    async def get_endpoint_status(self, endpoint_id: str) -> Optional[Dict[str, Any]]:
        """Get webhook endpoint status
        
        Args:
            endpoint_id: Endpoint ID
            
        Returns:
            Optional[Dict[str, Any]]: Endpoint status
        """
        if endpoint_id not in self.endpoints:
            return None
        
        endpoint = self.endpoints[endpoint_id]
        provider_stats = self.stats["provider_stats"].get(endpoint.provider, {})
        
        return {
            "id": endpoint.id,
            "provider": endpoint.provider,
            "status": endpoint.status.value,
            "events": endpoint.events,
            "created_at": endpoint.created_at.isoformat(),
            "statistics": provider_stats
        }
    
    async def update_endpoint_status(self, endpoint_id: str, status: WebhookStatus):
        """Update webhook endpoint status
        
        Args:
            endpoint_id: Endpoint ID
            status: New status
        """
        if endpoint_id in self.endpoints:
            self.endpoints[endpoint_id].status = status
            self.logger.info(f"Updated endpoint {endpoint_id} status to {status.value}")
    
    async def list_endpoints(self) -> List[Dict[str, Any]]:
        """List all webhook endpoints
        
        Returns:
            List[Dict[str, Any]]: Endpoint information
        """
        endpoints = []
        
        for endpoint in self.endpoints.values():
            endpoints.append({
                "id": endpoint.id,
                "provider": endpoint.provider,
                "url": endpoint.url,
                "events": endpoint.events,
                "status": endpoint.status.value,
                "created_at": endpoint.created_at.isoformat()
            })
        
        return endpoints
    
    async def get_event_history(self, limit: int = 100, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get webhook event history (would need persistent storage in production)
        
        Args:
            limit: Number of events to return
            provider: Filter by provider
            
        Returns:
            List[Dict[str, Any]]: Event history
        """
        # This would typically query a database
        # For now, return empty list as events are processed in real-time
        return []


# Global webhook manager instance
webhook_manager = WebhookManager()


async def get_webhook_manager() -> WebhookManager:
    """Get global webhook manager instance
    
    Returns:
        WebhookManager: Global instance
    """
    return webhook_manager