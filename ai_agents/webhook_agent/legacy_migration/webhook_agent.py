"""Webhook Agent - Main Processing Engine

Industrial-grade webhook agent for enterprise-level real-time event processing,
platform integrations, and automated notification management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written 
permission from Fahed Mlaiel <mlaiel@live.de> is strictly prohibited.
"""
import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum

import aiohttp
import aioredis
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..base import BaseAgent, AgentStatus
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import WebhookError, ValidationError, SecurityError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    WebhookError, ValidationError, SecurityError = globals().get('WebhookError, ValidationError, SecurityError', Exception)
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.rate_limiter import RateLimiter

from .webhook_manager import WebhookManager
from .event_processor import EventProcessor
from .signature_validator import SignatureValidator
from .notification_dispatcher import NotificationDispatcher
from .webhook_registry import WebhookRegistry
from .payload_transformer import PayloadTransformer
from .webhook_analytics import WebhookAnalytics
from .retry_handler import RetryHandler
from .webhook_security import WebhookSecurity

logger = logging.getLogger(__name__)

class WebhookEventType(Enum):
    """Webhook event types for platform integrations"""    CONTENT_PROTECTION_ALERT = "content_protection_alert"
    COPYRIGHT_MATCH_FOUND = "copyright_match_found" 
    TAKEDOWN_REQUEST_SUBMITTED = "takedown_request_submitted"
    TAKEDOWN_COMPLETED = "takedown_completed"
    CONTENT_REMOVED = "content_removed"
    APPEAL_SUBMITTED = "appeal_submitted"
    LICENSING_REQUEST = "licensing_request"
    REVENUE_NOTIFICATION = "revenue_notification"
    PLATFORM_STATUS_CHANGE = "platform_status_change"
    USER_ACTION_REQUIRED = "user_action_required"
    MONITORING_ALERT = "monitoring_alert"
    SYSTEM_NOTIFICATION = "system_notification"

class WebhookDirection(Enum):
    """Webhook direction types"""    INCOMING = "incoming"
    OUTGOING = "outgoing"
    BIDIRECTIONAL = "bidirectional"

@dataclass
class WebhookEvent:
    """Webhook event data structure"""    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: WebhookEventType = None
    platform: str = None
    direction: WebhookDirection = None
    payload: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None
    content_id: Optional[str] = None
    signature: Optional[str] = None
    verified: bool = False
    processed: bool = False
    retry_count: int = 0
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None

@dataclass 
class WebhookEndpoint:
    """Webhook endpoint configuration"""    endpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    url: str = None
    platform: str = None
    event_types: List[WebhookEventType] = field(default_factory=list)
    secret: str = None
    signature_method: str = "hmac_sha256"
    max_retries: int = 3
    timeout_seconds: int = 30
    active: bool = True
    headers: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: Optional[datetime] = None

@dataclass
class WebhookMetrics:
    """Webhook processing metrics"""    total_events: int = 0
    successful_events: int = 0
    failed_events: int = 0
    average_processing_time: float = 0.0
    events_per_minute: float = 0.0
    last_event_timestamp: Optional[datetime] = None

class WebhookAgent(BaseAgent):
    """    Industrial-grade webhook agent for enterprise-level event processing
    
    Manages incoming and outgoing webhooks across all platform integrations,
    with advanced security, retry mechanisms, and real-time analytics.
    """    
    def __init__(
        self,
        agent_id: str = None,
        config: Dict[str, Any] = None,
        db_session: Session = None
    ):
        super().__init__(
            agent_id=agent_id or f"webhook_agent_{uuid.uuid4().hex[:8]}",
            agent_type="WebhookAgent",
            config=config or {}
        )
        
        self.db_session = db_session or get_db_session()
        
        # Initialize core components
        self.webhook_manager = WebhookManager(config=self.config)
        self.event_processor = EventProcessor(config=self.config)
        self.signature_validator = SignatureValidator(config=self.config)
        self.notification_dispatcher = NotificationDispatcher(config=self.config)
        self.webhook_registry = WebhookRegistry(config=self.config)
        self.payload_transformer = PayloadTransformer(config=self.config)
        self.webhook_analytics = WebhookAnalytics(config=self.config)
        self.retry_handler = RetryHandler(config=self.config)
        self.webhook_security = WebhookSecurity(config=self.config)
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor("webhook_agent")
        self.rate_limiter = RateLimiter(
            max_requests=self.config.get('max_webhooks_per_minute', 1000),
            time_window=60
        )
        
        # Internal state
        self._event_queue = asyncio.Queue(maxsize=10000)
        self._processing_tasks: Set[asyncio.Task] = set()
        self._metrics = WebhookMetrics()
        self._redis_client = None
        self._websocket_connections: Set[Any] = set()
        
        # Event handlers registry
        self._event_handlers: Dict[WebhookEventType, List[Callable]] = {}
        
        logger.info(f"WebhookAgent initialized: {self.agent_id}")

    async def initialize(self) -> None:
        """Initialize webhook agent with all required services"""        try:
            await super().initialize()
            
            # Initialize Redis connection
            self._redis_client = await aioredis.from_url(
                self.config.get('redis_url', 'redis://localhost:6379'),
                decode_responses=True
            )
            
            # Initialize all components
            await self.webhook_manager.initialize()
            await self.event_processor.initialize()
            await self.signature_validator.initialize()
            await self.notification_dispatcher.initialize()
            await self.webhook_registry.initialize()
            await self.payload_transformer.initialize()
            await self.webhook_analytics.initialize()
            await self.retry_handler.initialize()
            await self.webhook_security.initialize()
            
            # Start background processing tasks
            await self._start_background_tasks()
            
            # Register default event handlers
            await self._register_default_handlers()
            
            self.status = AgentStatus.ACTIVE
            logger.info(f"WebhookAgent fully initialized: {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebhookAgent: {e}")
            self.status = AgentStatus.ERROR
            raise WebhookError(f"Initialization failed: {str(e)}")

    async def process_incoming_webhook(
        self,
        platform: str,
        event_data: Dict[str, Any],
        headers: Dict[str, str],
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """        Process incoming webhook from external platform
        
        Args:
            platform: Source platform name
            event_data: Webhook payload data
            headers: HTTP headers from webhook request
            signature: Webhook signature for verification
            
        Returns:
            Processing result dictionary
        """        start_time = time.time()
        
        try:
            # Rate limiting check
            if not await self.rate_limiter.is_allowed():
                raise WebhookError("Rate limit exceeded")
            
            # Create webhook event
            webhook_event = WebhookEvent(
                event_type=self._determine_event_type(event_data),
                platform=platform,
                direction=WebhookDirection.INCOMING,
                payload=event_data,
                headers=headers,
                signature=signature,
                user_id=event_data.get('user_id'),
                content_id=event_data.get('content_id')
            )
            
            # Security validation
            security_result = await self.webhook_security.validate_webhook(
                webhook_event, headers
            )
            if not security_result['valid']:
                raise SecurityError(f"Security validation failed: {security_result['reason']}")
            
            # Signature verification
            if signature:
                verification_result = await self.signature_validator.verify_signature(
                    payload=event_data,
                    signature=signature,
                    platform=platform,
                    headers=headers
                )
                if not verification_result['valid']:
                    raise SecurityError(f"Invalid webhook signature: {verification_result['reason']}")
                webhook_event.verified = True
            
            # Transform payload if needed
            transformed_payload = await self.payload_transformer.transform_payload(
                webhook_event.payload,
                platform,
                webhook_event.event_type
            )
            webhook_event.payload = transformed_payload
            
            # Queue for processing
            await self._event_queue.put(webhook_event)
            
            # Update metrics
            processing_time = (time.time() - start_time) * 1000
            webhook_event.processing_time_ms = processing_time
            await self._update_metrics(webhook_event, success=True)
            
            # Record analytics
            await self.webhook_analytics.record_event(webhook_event)
            
            # Send real-time notification
            await self._notify_websocket_clients(webhook_event)
            
            logger.info(f"Incoming webhook processed successfully: {webhook_event.event_id}")
            
            return {
                'success': True,
                'event_id': webhook_event.event_id,
                'processing_time_ms': processing_time,
                'verified': webhook_event.verified
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            await self._update_metrics(None, success=False)
            logger.error(f"Failed to process incoming webhook: {e}")
            raise WebhookError(f"Processing failed: {str(e)}")

    async def send_outgoing_webhook(
        self,
        endpoint_url: str,
        event_type: WebhookEventType,
        payload: Dict[str, Any],
        platform: str = None,
        user_id: str = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """        Send outgoing webhook to external endpoint
        
        Args:
            endpoint_url: Target webhook URL
            event_type: Type of webhook event
            payload: Data payload to send
            platform: Target platform name
            user_id: Associated user ID
            headers: Additional HTTP headers
            
        Returns:
            Send result dictionary
        """        start_time = time.time()
        
        try:
            # Create webhook event
            webhook_event = WebhookEvent(
                event_type=event_type,
                platform=platform,
                direction=WebhookDirection.OUTGOING,
                payload=payload,
                headers=headers or {},
                user_id=user_id
            )
            
            # Get endpoint configuration
            endpoint_config = await self.webhook_registry.get_endpoint_config(
                endpoint_url, platform
            )
            
            # Transform payload for target platform
            transformed_payload = await self.payload_transformer.transform_outgoing_payload(
                payload, platform, event_type
            )
            
            # Generate signature if required
            if endpoint_config and endpoint_config.secret:
                signature = await self.signature_validator.generate_signature(
                    payload=transformed_payload,
                    secret=endpoint_config.secret,
                    method=endpoint_config.signature_method
                )
                webhook_event.headers['X-Webhook-Signature'] = signature
                webhook_event.signature = signature
            
            # Send webhook with retry mechanism
            send_result = await self.retry_handler.execute_with_retry(
                self._send_webhook_request,
                endpoint_url,
                transformed_payload,
                webhook_event.headers,
                timeout=endpoint_config.timeout_seconds if endpoint_config else 30
            )
            
            # Update event status
            webhook_event.processed = send_result['success']
            processing_time = (time.time() - start_time) * 1000
            webhook_event.processing_time_ms = processing_time
            
            # Update metrics
            await self._update_metrics(webhook_event, success=send_result['success'])
            
            # Record analytics
            await self.webhook_analytics.record_event(webhook_event)
            
            logger.info(f"Outgoing webhook sent: {webhook_event.event_id}")
            
            return {
                'success': send_result['success'],
                'event_id': webhook_event.event_id,
                'response_status': send_result.get('status_code'),
                'processing_time_ms': processing_time,
                'error': send_result.get('error')
            }
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            await self._update_metrics(None, success=False)
            logger.error(f"Failed to send outgoing webhook: {e}")
            raise WebhookError(f"Send failed: {str(e)}")

    async def register_webhook_endpoint(
        self,
        url: str,
        platform: str,
        event_types: List[WebhookEventType],
        secret: str = None,
        signature_method: str = "hmac_sha256",
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Register new webhook endpoint for platform"""        try:
            endpoint = WebhookEndpoint(
                url=url,
                platform=platform,
                event_types=event_types,
                secret=secret,
                signature_method=signature_method,
                headers=headers or {}
            )
            
            # Validate endpoint
            validation_result = await self.webhook_security.validate_endpoint(endpoint)
            if not validation_result['valid']:
                raise ValidationError(f"Invalid endpoint: {validation_result['reason']}")
            
            # Register endpoint
            registration_result = await self.webhook_registry.register_endpoint(endpoint)
            
            logger.info(f"Webhook endpoint registered: {endpoint.endpoint_id}")
            
            return {
                'success': True,
                'endpoint_id': endpoint.endpoint_id,
                'url': url,
                'platform': platform
            }
            
        except Exception as e:
            logger.error(f"Failed to register webhook endpoint: {e}")
            raise WebhookError(f"Registration failed: {str(e)}")

    async def register_event_handler(
        self,
        event_type: WebhookEventType,
        handler: Callable[[WebhookEvent], Any]
    ) -> None:
        """Register custom event handler for specific event type"""        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        
        self._event_handlers[event_type].append(handler)
        logger.info(f"Event handler registered for: {event_type.value}")

    async def get_webhook_metrics(
        self,
        platform: str = None,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Get webhook processing metrics and analytics"""        try:
            metrics = await self.webhook_analytics.get_metrics(platform, time_range)
            
            # Add current runtime metrics
            metrics.update({
                'current_queue_size': self._event_queue.qsize(),
                'active_processing_tasks': len(self._processing_tasks),
                'websocket_connections': len(self._websocket_connections),
                'total_events': self._metrics.total_events,
                'successful_events': self._metrics.successful_events,
                'failed_events': self._metrics.failed_events,
                'average_processing_time': self._metrics.average_processing_time,
                'events_per_minute': self._metrics.events_per_minute
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get webhook metrics: {e}")
            raise WebhookError(f"Metrics retrieval failed: {str(e)}")

    async def add_websocket_connection(self, websocket) -> None:
        """Add WebSocket connection for real-time notifications"""        self._websocket_connections.add(websocket)
        logger.info(f"WebSocket connection added. Total: {len(self._websocket_connections)}")

    async def remove_websocket_connection(self, websocket) -> None:
        """Remove WebSocket connection"""        self._websocket_connections.discard(websocket)
        logger.info(f"WebSocket connection removed. Total: {len(self._websocket_connections)}")

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for webhook agent"""        health_data = {
            'agent_id': self.agent_id,
            'status': self.status.value,
            'uptime_seconds': time.time() - self._start_time,
            'queue_size': self._event_queue.qsize(),
            'active_tasks': len(self._processing_tasks),
            'websocket_connections': len(self._websocket_connections),
            'redis_connected': self._redis_client is not None,
            'components': {}
        }
        
        # Check component health
        components = [
            self.webhook_manager,
            self.event_processor,
            self.signature_validator,
            self.notification_dispatcher,
            self.webhook_registry,
            self.payload_transformer,
            self.webhook_analytics,
            self.retry_handler,
            self.webhook_security
        ]
        
        for component in components:
            component_name = component.__class__.__name__
            try:
                component_health = await component.health_check()
                health_data['components'][component_name] = component_health
            except Exception as e:
                health_data['components'][component_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return health_data

    async def shutdown(self) -> None:
        """Graceful shutdown of webhook agent"""        try:
            logger.info(f"Shutting down WebhookAgent: {self.agent_id}")
            
            # Cancel processing tasks
            for task in self._processing_tasks:
                task.cancel()
            
            # Close WebSocket connections
            for websocket in self._websocket_connections:
                try:
                    await websocket.close()
                except:
                    pass
            
            # Shutdown components
            components = [
                self.webhook_manager,
                self.event_processor,
                self.signature_validator,
                self.notification_dispatcher,
                self.webhook_registry,
                self.payload_transformer,
                self.webhook_analytics,
                self.retry_handler,
                self.webhook_security
            ]
            
            for component in components:
                try:
                    await component.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down {component.__class__.__name__}: {e}")
            
            # Close Redis connection
            if self._redis_client:
                await self._redis_client.close()
            
            self.status = AgentStatus.INACTIVE
            await super().shutdown()
            
            logger.info(f"WebhookAgent shutdown complete: {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Error during WebhookAgent shutdown: {e}")

    # Private methods
    
    async def _start_background_tasks(self) -> None:
        """Start background processing tasks"""        # Event processing task
        task = asyncio.create_task(self._process_event_queue())
        self._processing_tasks.add(task)
        
        # Metrics collection task
        task = asyncio.create_task(self._collect_metrics())
        self._processing_tasks.add(task)
        
        # Health monitoring task
        task = asyncio.create_task(self._health_monitor())
        self._processing_tasks.add(task)

    async def _process_event_queue(self) -> None:
        """Background task to process webhook events from queue"""        while self.status == AgentStatus.ACTIVE:
            try:
                # Get event from queue with timeout
                webhook_event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0
                )
                
                # Process event
                await self._process_webhook_event(webhook_event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in event queue processing: {e}")

    async def _process_webhook_event(self, webhook_event: WebhookEvent) -> None:
        """Process individual webhook event"""        try:
            # Process with event processor
            processing_result = await self.event_processor.process_event(webhook_event)
            
            # Execute registered handlers
            if webhook_event.event_type in self._event_handlers:
                for handler in self._event_handlers[webhook_event.event_type]:
                    try:
                        await handler(webhook_event)
                    except Exception as e:
                        logger.error(f"Event handler failed: {e}")
            
            # Send notifications
            await self.notification_dispatcher.dispatch_notifications(
                webhook_event, processing_result
            )
            
            webhook_event.processed = True
            logger.debug(f"Webhook event processed: {webhook_event.event_id}")
            
        except Exception as e:
            webhook_event.error_message = str(e)
            logger.error(f"Failed to process webhook event {webhook_event.event_id}: {e}")

    async def _send_webhook_request(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Send HTTP request for outgoing webhook"""        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    return {
                        'success': response.status in [200, 201, 202],
                        'status_code': response.status,
                        'response_text': await response.text()
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _determine_event_type(self, event_data: Dict[str, Any]) -> WebhookEventType:
        """Determine webhook event type from payload"""        event_type = event_data.get('event_type', '').lower()
        
        event_type_mapping = {
            'copyright_match_found': WebhookEventType.COPYRIGHT_MATCH_FOUND,
            'takedown_request': WebhookEventType.TAKEDOWN_REQUEST_SUBMITTED,
            'takedown_completed': WebhookEventType.TAKEDOWN_COMPLETED,
            'content_removed': WebhookEventType.CONTENT_REMOVED,
            'appeal_submitted': WebhookEventType.APPEAL_SUBMITTED,
            'licensing_request': WebhookEventType.LICENSING_REQUEST,
            'revenue_notification': WebhookEventType.REVENUE_NOTIFICATION,
            'platform_status': WebhookEventType.PLATFORM_STATUS_CHANGE,
            'monitoring_alert': WebhookEventType.MONITORING_ALERT
        }
        
        return event_type_mapping.get(event_type, WebhookEventType.SYSTEM_NOTIFICATION)

    async def _update_metrics(self, webhook_event: Optional[WebhookEvent], success: bool) -> None:
        """Update internal metrics"""        self._metrics.total_events += 1
        
        if success:
            self._metrics.successful_events += 1
        else:
            self._metrics.failed_events += 1
        
        if webhook_event and webhook_event.processing_time_ms:
            # Update average processing time
            total_time = (self._metrics.average_processing_time * 
                         (self._metrics.total_events - 1) + 
                         webhook_event.processing_time_ms)
            self._metrics.average_processing_time = total_time / self._metrics.total_events
        
        self._metrics.last_event_timestamp = datetime.now(timezone.utc)

    async def _collect_metrics(self) -> None:
        """Background task for metrics collection"""        while self.status == AgentStatus.ACTIVE:
            try:
                # Calculate events per minute
                current_time = datetime.now(timezone.utc)
                time_window = 60  # seconds
                
                # This would integrate with proper metrics storage
                self._metrics.events_per_minute = self._metrics.total_events / time_window
                
                await asyncio.sleep(60)  # Collect metrics every minute
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")

    async def _health_monitor(self) -> None:
        """Background health monitoring task"""        while self.status == AgentStatus.ACTIVE:
            try:
                # Monitor queue size
                if self._event_queue.qsize() > 5000:
                    logger.warning("Webhook event queue size high")
                
                # Monitor processing tasks
                active_tasks = len([t for t in self._processing_tasks if not t.done()])
                if active_tasks == 0:
                    logger.warning("No active processing tasks")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")

    async def _notify_websocket_clients(self, webhook_event: WebhookEvent) -> None:
        """Send real-time notifications to WebSocket clients"""        if not self._websocket_connections:
            return
        
        notification = {
            'type': 'webhook_event',
            'event_id': webhook_event.event_id,
            'event_type': webhook_event.event_type.value,
            'platform': webhook_event.platform,
            'direction': webhook_event.direction.value,
            'timestamp': webhook_event.timestamp.isoformat(),
            'verified': webhook_event.verified,
            'processed': webhook_event.processed
        }
        
        # Send to all connected clients
        disconnected = set()
        for websocket in self._websocket_connections:
            try:
                await websocket.send(json.dumps(notification))
            except:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        self._websocket_connections -= disconnected

    async def _register_default_handlers(self) -> None:
        """Register default event handlers"""        # Copyright match handler
        await self.register_event_handler(
            WebhookEventType.COPYRIGHT_MATCH_FOUND,
            self._handle_copyright_match
        )
        
        # Content protection alert handler
        await self.register_event_handler(
            WebhookEventType.CONTENT_PROTECTION_ALERT,
            self._handle_content_protection_alert
        )
        
        # Revenue notification handler
        await self.register_event_handler(
            WebhookEventType.REVENUE_NOTIFICATION,
            self._handle_revenue_notification
        )

    async def _handle_copyright_match(self, webhook_event: WebhookEvent) -> None:
        """Handle copyright match events"""        logger.info(f"Processing copyright match: {webhook_event.event_id}")
        # Implementation would trigger protection workflows

    async def _handle_content_protection_alert(self, webhook_event: WebhookEvent) -> None:
        """Handle content protection alerts"""        logger.info(f"Processing content protection alert: {webhook_event.event_id}")
        # Implementation would trigger alert processing

    async def _handle_revenue_notification(self, webhook_event: WebhookEvent) -> None:
        """Handle revenue notifications"""        logger.info(f"Processing revenue notification: {webhook_event.event_id}")
        # Implementation would update revenue tracking
