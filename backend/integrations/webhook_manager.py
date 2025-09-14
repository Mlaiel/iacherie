"""Webhook Manager Integration - Centralized Webhook Processing
============================================================

Professional integration for real-time event processing from all platforms
including event routing, data synchronization, and retry logic.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, AsyncGenerator, Callable
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import json
import aiohttp
import hashlib
import hmac
import base64
import uuid
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)


class WebhookSource(str, Enum):
    """Webhook event sources."""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    SENDGRID = "sendgrid"
    TWILIO = "twilio"
    SHOPIFY = "shopify"
    CUSTOM = "custom"


class EventType(str, Enum):
    """Webhook event types."""
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"
    PAYOUT_SENT = "payout.sent"
    PAYOUT_FAILED = "payout.failed"
    CONTENT_UPLOADED = "content.uploaded"
    CONTENT_APPROVED = "content.approved"
    CONTENT_REJECTED = "content.rejected"
    CONTENT_MONETIZED = "content.monetized"
    USER_SUBSCRIBED = "user.subscribed"
    USER_UNSUBSCRIBED = "user.unsubscribed"
    ENGAGEMENT_THRESHOLD = "engagement.threshold"
    REVENUE_MILESTONE = "revenue.milestone"
    FRAUD_DETECTED = "fraud.detected"
    COPYRIGHT_CLAIM = "copyright.claim"
    SECURITY_INCIDENT = "security.incident"
    SYSTEM_ERROR = "system.error"


class EventStatus(str, Enum):
    """Event processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"
    FILTERED = "filtered"


class EventPriority(str, Enum):
    """Event processing priority."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class WebhookEvent:
    """Webhook event data."""
    event_id: str
    source: WebhookSource
    event_type: EventType
    priority: EventPriority
    payload: Dict[str, Any]
    headers: Dict[str, str]
    signature: Optional[str]
    received_at: datetime
    processed_at: Optional[datetime]
    status: EventStatus
    retry_count: int
    next_retry_at: Optional[datetime]
    error_message: Optional[str]
    processing_time_ms: Optional[int]
    metadata: Dict[str, Any]


@dataclass
class WebhookEndpoint:
    """Webhook endpoint configuration."""
    endpoint_id: str
    url: str
    source: WebhookSource
    secret: str
    is_active: bool
    event_types: List[EventType]
    signature_algorithm: str  # hmac-sha256, hmac-sha1, etc.
    retry_config: Dict[str, Any]
    rate_limit: Dict[str, int]
    metadata: Dict[str, Any]


@dataclass
class EventHandler:
    """Event handler configuration."""
    handler_id: str
    event_types: List[EventType]
    handler_function: Callable[[WebhookEvent], Any]
    priority: EventPriority
    is_async: bool
    timeout_seconds: int
    retry_on_failure: bool
    metadata: Dict[str, Any]


@dataclass
class EventMetrics:
    """Event processing metrics."""
    source: WebhookSource
    event_type: EventType
    period_start: datetime
    period_end: datetime
    total_events: int
    successful_events: int
    failed_events: int
    average_processing_time_ms: float
    retry_rate: float
    error_rate: float
    throughput_per_minute: float
    metadata: Dict[str, Any]


class WebhookManagerIntegration:
    """Professional webhook manager integration."""
    
    def __init__(
        self,
        # Redis configuration for event queuing
        redis_host -> None: str = "localhost",
        redis_port -> None: int = 6379,
        redis_password -> None: Optional[str] = None,
        redis_db -> None: int = 0,
        # Processing configuration
        max_workers -> None: int = 10,
        max_retry_attempts -> None: int = 3,
        retry_base_delay -> None: int = 5,  # seconds
        max_retry_delay -> None: int = 300,  # seconds
        dead_letter_threshold -> None: int = 5,
        # Rate limiting
        global_rate_limit -> None: int = 1000,  # events per minute
        # General settings
        timeout -> None: int = 30
    ) -> None:
        # Configuration
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_db = redis_db
        self.max_workers = max_workers
        self.max_retry_attempts = max_retry_attempts
        self.retry_base_delay = retry_base_delay
        self.max_retry_delay = max_retry_delay
        self.dead_letter_threshold = dead_letter_threshold
        self.global_rate_limit = global_rate_limit
        self.timeout = timeout
        
        # Session and worker pool
        self.session: Optional[aiohttp.ClientSession] = None
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Storage
        self.webhook_endpoints: Dict[str, WebhookEndpoint] = {}
        self.event_handlers: Dict[str, EventHandler] = {}
        self.pending_events: Dict[str, WebhookEvent] = {}
        self.processed_events: Dict[str, WebhookEvent] = {}
        
        # Metrics and tracking
        self.total_events_received = 0
        self.total_events_processed = 0
        self.total_events_failed = 0
        self.total_retries = 0
        self.average_processing_time = 0.0
        self.request_count = 0
        
        # Event queues by priority
        self.event_queues = {
            EventPriority.CRITICAL: asyncio.Queue(),
            EventPriority.HIGH: asyncio.Queue(),
            EventPriority.NORMAL: asyncio.Queue(),
            EventPriority.LOW: asyncio.Queue()
        }
        
        # Processing control
        self.is_processing = False
        self.processing_tasks: List[asyncio.Task] = []
        
        logger.info("Webhook Manager integration initialized")
    
    async def __aenter__(self) -> None:
        """Async context manager entry."""
        await self._ensure_session()
        await self.start_processing()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.stop_processing()
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure HTTP session is available."""
        if self.session is None or self.session.closed:
            headers = {
                "User-Agent": "Ainflue/1.0 Webhook Manager",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def close(self) -> None:
        """Close HTTP session and executor."""
        if self.session and not self.session.closed:
            await self.session.close()
        
        self.executor.shutdown(wait=True)
    
    async def register_webhook_endpoint(
        self,
        url: str,
        source: WebhookSource,
        secret: str,
        event_types: List[EventType],
        signature_algorithm: str = "hmac-sha256",
        retry_config: Optional[Dict[str, Any]] = None,
        rate_limit: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WebhookEndpoint:
        """Register a webhook endpoint."""
        
        endpoint_id = str(uuid.uuid4())
        
        endpoint = WebhookEndpoint(
            endpoint_id=endpoint_id,
            url=url,
            source=source,
            secret=secret,
            is_active=True,
            event_types=event_types,
            signature_algorithm=signature_algorithm,
            retry_config=retry_config or {
                "max_attempts": self.max_retry_attempts,
                "base_delay": self.retry_base_delay,
                "max_delay": self.max_retry_delay,
                "exponential_backoff": True
            },
            rate_limit=rate_limit or {"per_minute": 60, "burst": 10},
            metadata=metadata or {}
        )
        
        self.webhook_endpoints[endpoint_id] = endpoint
        
        logger.info(f"Webhook endpoint registered: {source} - {url}")
        return endpoint
    
    async def register_event_handler(
        self,
        event_types: List[EventType],
        handler_function: Callable[[WebhookEvent], Any],
        priority: EventPriority = EventPriority.NORMAL,
        is_async: bool = True,
        timeout_seconds: int = 30,
        retry_on_failure: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EventHandler:
        """Register an event handler."""
        
        handler_id = str(uuid.uuid4())
        
        handler = EventHandler(
            handler_id=handler_id,
            event_types=event_types,
            handler_function=handler_function,
            priority=priority,
            is_async=is_async,
            timeout_seconds=timeout_seconds,
            retry_on_failure=retry_on_failure,
            metadata=metadata or {}
        )
        
        self.event_handlers[handler_id] = handler
        
        logger.info(f"Event handler registered: {handler_id} for {len(event_types)} event types")
        return handler
    
    async def receive_webhook(
        self,
        source: WebhookSource,
        event_type: EventType,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        signature: Optional[str] = None
    ) -> WebhookEvent:
        """Receive and process incoming webhook."""
        
        event_id = str(uuid.uuid4())
        
        # Determine event priority
        priority = self._determine_event_priority(event_type, payload)
        
        # Create webhook event
        event = WebhookEvent(
            event_id=event_id,
            source=source,
            event_type=event_type,
            priority=priority,
            payload=payload,
            headers=headers,
            signature=signature,
            received_at=datetime.now(),
            processed_at=None,
            status=EventStatus.PENDING,
            retry_count=0,
            next_retry_at=None,
            error_message=None,
            processing_time_ms=None,
            metadata={}
        )
        
        # Verify webhook signature if provided
        if signature and not await self._verify_webhook_signature(event):
            event.status = EventStatus.FAILED
            event.error_message = "Invalid webhook signature"
            logger.warning(f"Webhook signature verification failed: {event_id}")
            return event
        
        # Add to appropriate queue
        await self.event_queues[priority].put(event)
        self.pending_events[event_id] = event
        self.total_events_received += 1
        
        logger.info(f"Webhook received: {source} - {event_type} ({priority})")
        return event
    
    async def _verify_webhook_signature(self, event: WebhookEvent) -> bool:
        """Verify webhook signature."""
        try:
            # Find matching endpoint
            matching_endpoint = None
            for endpoint in self.webhook_endpoints.values():
                if (endpoint.source == event.source and 
                    event.event_type in endpoint.event_types):
                    matching_endpoint = endpoint
                    break
            
            if not matching_endpoint:
                logger.warning(f"No matching endpoint found for {event.source} - {event.event_type}")
                return True  # Allow if no endpoint configured
            
            # Calculate expected signature
            secret = matching_endpoint.secret.encode()
            payload_bytes = json.dumps(event.payload, sort_keys=True).encode()
            
            if matching_endpoint.signature_algorithm == "hmac-sha256":
                expected_signature = hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()
                signature_prefix = "sha256="
            elif matching_endpoint.signature_algorithm == "hmac-sha1":
                expected_signature = hmac.new(secret, payload_bytes, hashlib.sha1).hexdigest()
                signature_prefix = "sha1="
            else:
                logger.error(f"Unsupported signature algorithm: {matching_endpoint.signature_algorithm}")
                return False
            
            # Compare signatures
            provided_signature = event.signature
            if provided_signature and provided_signature.startswith(signature_prefix):
                provided_signature = provided_signature[len(signature_prefix):]
            
            return hmac.compare_digest(expected_signature, provided_signature or "")
        
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    def _determine_event_priority(self, event_type: EventType, payload: Dict[str, Any]) -> EventPriority:
        """Determine event processing priority."""
        
        # Critical events
        if event_type in [EventType.FRAUD_DETECTED, EventType.SECURITY_INCIDENT, EventType.SYSTEM_ERROR]:
            return EventPriority.CRITICAL
        
        # High priority events
        if event_type in [EventType.PAYMENT_FAILED, EventType.PAYOUT_FAILED, EventType.COPYRIGHT_CLAIM]:
            return EventPriority.HIGH
        
        # Payment events are generally high priority
        if event_type.value.startswith("payment.") or event_type.value.startswith("payout."):
            return EventPriority.HIGH
        
        # Content events are normal priority
        if event_type.value.startswith("content."):
            return EventPriority.NORMAL
        
        # User events are typically low priority
        if event_type.value.startswith("user."):
            return EventPriority.LOW
        
        # Default to normal priority
        return EventPriority.NORMAL
    
    async def start_processing(self) -> None:
        """Start webhook event processing."""
        if self.is_processing:
            logger.warning("Event processing already started")
            return
        
        self.is_processing = True
        
        # Start processing tasks for each priority level
        for priority in EventPriority:
            task = asyncio.create_task(
                self._process_events_queue(priority),
                name=f"webhook_processor_{priority.value}"
            )
            self.processing_tasks.append(task)
        
        # Start retry processor
        retry_task = asyncio.create_task(
            self._process_retry_queue(),
            name="webhook_retry_processor"
        )
        self.processing_tasks.append(retry_task)
        
        logger.info(f"Webhook processing started with {len(self.processing_tasks)} tasks")
    
    async def stop_processing(self) -> None:
        """Stop webhook event processing."""
        if not self.is_processing:
            return
        
        self.is_processing = False
        
        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.processing_tasks:
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        self.processing_tasks.clear()
        
        logger.info("Webhook processing stopped")
    
    async def _process_events_queue(self, priority -> None: EventPriority) -> None:
        """Process events from a specific priority queue."""
        queue = self.event_queues[priority]
        
        while self.is_processing:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                # Process the event
                await self._process_single_event(event)
                
                # Mark task as done
                queue.task_done()
            
            except asyncio.TimeoutError:
                # No events in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error in {priority} queue processor: {e}")
                await asyncio.sleep(1)
    
    async def _process_single_event(self, event -> None: WebhookEvent) -> None:
        """Process a single webhook event."""
        start_time = time.time()
        event.status = EventStatus.PROCESSING
        
        try:
            # Find matching handlers
            matching_handlers = [
                handler for handler in self.event_handlers.values()
                if event.event_type in handler.event_types
            ]
            
            if not matching_handlers:
                logger.warning(f"No handlers found for event type: {event.event_type}")
                event.status = EventStatus.COMPLETED
                event.error_message = "No handlers configured"
                return
            
            # Execute handlers
            handler_results = []
            for handler in matching_handlers:
                try:
                    if handler.is_async:
                        result = await asyncio.wait_for(
                            handler.handler_function(event),
                            timeout=handler.timeout_seconds
                        )
                    else:
                        # Run sync handler in executor
                        result = await asyncio.get_event_loop().run_in_executor(
                            self.executor,
                            handler.handler_function,
                            event
                        )
                    
                    handler_results.append({
                        "handler_id": handler.handler_id,
                        "result": result,
                        "success": True
                    })
                
                except Exception as e:
                    logger.error(f"Handler {handler.handler_id} failed: {e}")
                    handler_results.append({
                        "handler_id": handler.handler_id,
                        "error": str(e),
                        "success": False
                    })
            
            # Check if all handlers succeeded
            all_succeeded = all(result["success"] for result in handler_results)
            
            if all_succeeded:
                event.status = EventStatus.COMPLETED
                self.total_events_processed += 1
            else:
                event.status = EventStatus.FAILED
                event.error_message = f"Handler failures: {[r for r in handler_results if not r['success']]}"
                self.total_events_failed += 1
                
                # Schedule retry if configured
                if event.retry_count < self.max_retry_attempts:
                    await self._schedule_retry(event)
                else:
                    await self._send_to_dead_letter(event)
        
        except Exception as e:
            logger.error(f"Event processing error: {e}")
            event.status = EventStatus.FAILED
            event.error_message = str(e)
            self.total_events_failed += 1
            
            # Schedule retry
            if event.retry_count < self.max_retry_attempts:
                await self._schedule_retry(event)
            else:
                await self._send_to_dead_letter(event)
        
        finally:
            # Update processing metrics
            processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            event.processing_time_ms = int(processing_time)
            event.processed_at = datetime.now()
            
            # Update average processing time
            self._update_processing_time_average(processing_time)
            
            # Move to processed events
            if event.event_id in self.pending_events:
                del self.pending_events[event.event_id]
            self.processed_events[event.event_id] = event
            
            logger.info(f"Event processed: {event.event_id} - {event.status} ({processing_time:.1f}ms)")
    
    async def _schedule_retry(self, event -> None: WebhookEvent) -> None:
        """Schedule event for retry."""
        event.retry_count += 1
        event.status = EventStatus.RETRY
        
        # Calculate retry delay with exponential backoff
        delay = min(
            self.retry_base_delay * (2 ** (event.retry_count - 1)),
            self.max_retry_delay
        )
        
        event.next_retry_at = datetime.now() + timedelta(seconds=delay)
        self.total_retries += 1
        
        logger.info(f"Event scheduled for retry: {event.event_id} (attempt {event.retry_count}/{self.max_retry_attempts})")
    
    async def _process_retry_queue(self) -> None:
        """Process events scheduled for retry."""
        while self.is_processing:
            try:
                current_time = datetime.now()
                
                # Find events ready for retry
                retry_events = [
                    event for event in self.processed_events.values()
                    if (event.status == EventStatus.RETRY and 
                        event.next_retry_at and 
                        event.next_retry_at <= current_time)
                ]
                
                for event in retry_events:
                    # Reset event status and re-queue
                    event.status = EventStatus.PENDING
                    event.next_retry_at = None
                    
                    # Add back to appropriate queue
                    await self.event_queues[event.priority].put(event)
                    
                    # Move back to pending
                    self.pending_events[event.event_id] = event
                    if event.event_id in self.processed_events:
                        del self.processed_events[event.event_id]
                
                # Sleep before next check
                await asyncio.sleep(5)
            
            except Exception as e:
                logger.error(f"Retry queue processor error: {e}")
                await asyncio.sleep(5)
    
    async def _send_to_dead_letter(self, event -> None: WebhookEvent) -> None:
        """Send event to dead letter queue."""
        event.status = EventStatus.DEAD_LETTER
        
        # In a real implementation, this would persist to a dead letter queue
        # For now, we'll just log and keep in memory
        
        logger.error(f"Event sent to dead letter queue: {event.event_id} after {event.retry_count} retries")
        
        # Could trigger alerts or notifications here
        await self._trigger_dead_letter_alert(event)
    
    async def _trigger_dead_letter_alert(self, event -> None: WebhookEvent) -> None:
        """Trigger alert for dead letter events."""
        alert_data = {
            "event_id": event.event_id,
            "source": event.source.value,
            "event_type": event.event_type.value,
            "retry_count": event.retry_count,
            "error_message": event.error_message,
            "received_at": event.received_at.isoformat(),
            "last_processed_at": event.processed_at.isoformat() if event.processed_at else None
        }
        
        # Send alert to monitoring system
        logger.critical(f"Dead letter alert: {json.dumps(alert_data)}")
    
    def _update_processing_time_average(self, processing_time -> None: float) -> None:
        """Update average processing time."""
        if self.total_events_processed == 0:
            self.average_processing_time = processing_time
        else:
            # Simple moving average
            self.average_processing_time = (
                (self.average_processing_time * (self.total_events_processed - 1) + processing_time) /
                self.total_events_processed
            )
    
    async def get_event_metrics(
        self,
        source: Optional[WebhookSource] = None,
        event_type: Optional[EventType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> EventMetrics:
        """Get event processing metrics."""
        
        # Filter events based on criteria
        filtered_events = []
        for event in self.processed_events.values():
            if source and event.source != source:
                continue
            if event_type and event.event_type != event_type:
                continue
            if start_date and event.received_at < start_date:
                continue
            if end_date and event.received_at > end_date:
                continue
            
            filtered_events.append(event)
        
        if not filtered_events:
            return EventMetrics(
                source=source or WebhookSource.CUSTOM,
                event_type=event_type or EventType.SYSTEM_ERROR,
                period_start=start_date or datetime.now(),
                period_end=end_date or datetime.now(),
                total_events=0,
                successful_events=0,
                failed_events=0,
                average_processing_time_ms=0.0,
                retry_rate=0.0,
                error_rate=0.0,
                throughput_per_minute=0.0,
                metadata={}
            )
        
        # Calculate metrics
        total_events = len(filtered_events)
        successful_events = len([e for e in filtered_events if e.status == EventStatus.COMPLETED])
        failed_events = len([e for e in filtered_events if e.status in [EventStatus.FAILED, EventStatus.DEAD_LETTER]])
        
        # Calculate average processing time
        processing_times = [e.processing_time_ms for e in filtered_events if e.processing_time_ms]
        average_processing_time_ms = sum(processing_times) / len(processing_times) if processing_times else 0.0
        
        # Calculate retry rate
        events_with_retries = len([e for e in filtered_events if e.retry_count > 0])
        retry_rate = (events_with_retries / total_events) * 100 if total_events > 0 else 0.0
        
        # Calculate error rate
        error_rate = (failed_events / total_events) * 100 if total_events > 0 else 0.0
        
        # Calculate throughput
        period_start = start_date or min(e.received_at for e in filtered_events)
        period_end = end_date or max(e.received_at for e in filtered_events)
        period_minutes = (period_end - period_start).total_seconds() / 60
        throughput_per_minute = total_events / period_minutes if period_minutes > 0 else 0.0
        
        return EventMetrics(
            source=source or WebhookSource.CUSTOM,
            event_type=event_type or EventType.SYSTEM_ERROR,
            period_start=period_start,
            period_end=period_end,
            total_events=total_events,
            successful_events=successful_events,
            failed_events=failed_events,
            average_processing_time_ms=average_processing_time_ms,
            retry_rate=retry_rate,
            error_rate=error_rate,
            throughput_per_minute=throughput_per_minute,
            metadata={
                "events_with_retries": events_with_retries,
                "max_retry_count": max((e.retry_count for e in filtered_events), default=0),
                "dead_letter_events": len([e for e in filtered_events if e.status == EventStatus.DEAD_LETTER])
            }
        )
    
    async def replay_events(
        self,
        event_ids: List[str],
        reset_retry_count: bool = True
    ) -> Dict[str, bool]:
        """Replay specific events."""
        results = {}
        
        for event_id in event_ids:
            if event_id in self.processed_events:
                event = self.processed_events[event_id]
                
                # Reset event state
                if reset_retry_count:
                    event.retry_count = 0
                
                event.status = EventStatus.PENDING
                event.next_retry_at = None
                event.error_message = None
                
                # Re-queue event
                await self.event_queues[event.priority].put(event)
                
                # Move back to pending
                self.pending_events[event_id] = event
                del self.processed_events[event_id]
                
                results[event_id] = True
                logger.info(f"Event replayed: {event_id}")
            else:
                results[event_id] = False
                logger.warning(f"Event not found for replay: {event_id}")
        
        return results
    
    async def get_webhook_status(self) -> Dict[str, Any]:
        """Get webhook manager status."""
        
        # Calculate queue sizes
        queue_sizes = {}
        for priority, queue in self.event_queues.items():
            queue_sizes[priority.value] = queue.qsize()
        
        # Calculate status by source
        source_stats = {}
        for event in list(self.processed_events.values()) + list(self.pending_events.values()):
            source = event.source.value
            if source not in source_stats:
                source_stats[source] = {"total": 0, "successful": 0, "failed": 0, "pending": 0}
            
            source_stats[source]["total"] += 1
            
            if event.status == EventStatus.COMPLETED:
                source_stats[source]["successful"] += 1
            elif event.status in [EventStatus.FAILED, EventStatus.DEAD_LETTER]:
                source_stats[source]["failed"] += 1
            elif event.status in [EventStatus.PENDING, EventStatus.PROCESSING, EventStatus.RETRY]:
                source_stats[source]["pending"] += 1
        
        status = {
            "is_processing": self.is_processing,
            "processing_tasks": len(self.processing_tasks),
            "queue_sizes": queue_sizes,
            "total_pending_events": len(self.pending_events),
            "total_processed_events": len(self.processed_events),
            "metrics": {
                "total_events_received": self.total_events_received,
                "total_events_processed": self.total_events_processed,
                "total_events_failed": self.total_events_failed,
                "total_retries": self.total_retries,
                "average_processing_time_ms": self.average_processing_time,
                "success_rate": (self.total_events_processed / max(self.total_events_received, 1)) * 100,
                "error_rate": (self.total_events_failed / max(self.total_events_received, 1)) * 100
            },
            "source_statistics": source_stats,
            "registered_endpoints": len(self.webhook_endpoints),
            "registered_handlers": len(self.event_handlers),
            "uptime": "N/A"  # Would calculate from start time
        }
        
        return status
    
    async def pause_processing(self) -> None:
        """Pause event processing without stopping completely."""
        logger.info("Webhook processing paused")
        self.is_processing = False
    
    async def resume_processing(self) -> None:
        """Resume event processing."""
        if not self.is_processing:
            self.is_processing = True
            logger.info("Webhook processing resumed")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get webhook manager usage statistics."""
        return {
            "total_requests": self.request_count,
            "total_events_received": self.total_events_received,
            "total_events_processed": self.total_events_processed,
            "total_events_failed": self.total_events_failed,
            "total_retries": self.total_retries,
            "average_processing_time_ms": self.average_processing_time,
            "success_rate": (self.total_events_processed / max(self.total_events_received, 1)) * 100,
            "error_rate": (self.total_events_failed / max(self.total_events_received, 1)) * 100,
            "retry_rate": (self.total_retries / max(self.total_events_received, 1)) * 100,
            "registered_endpoints": len(self.webhook_endpoints),
            "registered_handlers": len(self.event_handlers),
            "pending_events": len(self.pending_events),
            "processed_events": len(self.processed_events)
        }


# Utility functions
async def create_webhook_manager(
    redis_host: str = "localhost",
    redis_port: int = 6379,
    max_workers: int = 10
) -> WebhookManagerIntegration:
    """Create and initialize webhook manager integration."""
    manager = WebhookManagerIntegration(
        redis_host=redis_host,
        redis_port=redis_port,
        max_workers=max_workers
    )
    await manager._ensure_session()
    return manager


# Example event handlers
async def payment_completed_handler(event -> None: WebhookEvent) -> None:
    """Handle payment completed events."""
    payment_data = event.payload
    
    logger.info(f"Payment completed: {payment_data.get('payment_id')} - ${payment_data.get('amount')}")
    
    # Update user account balance
    # Send confirmation email
    # Update analytics
    
    return {"status": "processed", "action": "payment_confirmed"}


async def content_uploaded_handler(event -> None: WebhookEvent) -> None:
    """Handle content upload events."""
    content_data = event.payload
    
    logger.info(f"Content uploaded: {content_data.get('content_id')} by {content_data.get('user_id')}")
    
    # Start content processing pipeline
    # Run copyright scan
    # Generate thumbnails
    # Update content database
    
    return {"status": "processed", "action": "content_processing_started"}


async def fraud_detected_handler(event -> None: WebhookEvent) -> None:
    """Handle fraud detection events."""
    fraud_data = event.payload
    
    logger.critical(f"Fraud detected: {fraud_data.get('user_id')} - Risk score: {fraud_data.get('risk_score')}")
    
    # Freeze account
    # Send security alert
    # Escalate to fraud team
    # Log security incident
    
    return {"status": "processed", "action": "fraud_response_initiated"}


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        async with WebhookManagerIntegration(max_workers=5) as webhook_manager:
            # Register webhook endpoints
            stripe_endpoint = await webhook_manager.register_webhook_endpoint(
                url="https://api.ainflue.com/webhooks/stripe",
                source=WebhookSource.STRIPE,
                secret="whsec_test_secret",
                event_types=[EventType.PAYMENT_COMPLETED, EventType.PAYMENT_FAILED]
            )
            print(f"Stripe endpoint registered: {stripe_endpoint.endpoint_id}")
            
            # Register event handlers
            payment_handler = await webhook_manager.register_event_handler(
                event_types=[EventType.PAYMENT_COMPLETED],
                handler_function=payment_completed_handler,
                priority=EventPriority.HIGH
            )
            print(f"Payment handler registered: {payment_handler.handler_id}")
            
            content_handler = await webhook_manager.register_event_handler(
                event_types=[EventType.CONTENT_UPLOADED],
                handler_function=content_uploaded_handler,
                priority=EventPriority.NORMAL
            )
            print(f"Content handler registered: {content_handler.handler_id}")
            
            fraud_handler = await webhook_manager.register_event_handler(
                event_types=[EventType.FRAUD_DETECTED],
                handler_function=fraud_detected_handler,
                priority=EventPriority.CRITICAL
            )
            print(f"Fraud handler registered: {fraud_handler.handler_id}")
            
            # Simulate webhook events
            payment_event = await webhook_manager.receive_webhook(
                source=WebhookSource.STRIPE,
                event_type=EventType.PAYMENT_COMPLETED,
                payload={
                    "payment_id": "pi_test_123",
                    "amount": 99.99,
                    "currency": "USD",
                    "user_id": "user_456"
                },
                headers={"Content-Type": "application/json"},
                signature="sha256=test_signature"
            )
            print(f"Payment event received: {payment_event.event_id}")
            
            # Wait for processing
            await asyncio.sleep(2)
            
            # Get status
            status = await webhook_manager.get_webhook_status()
            print(f"Webhook manager status: {status['metrics']}")
            
            # Get usage stats
            stats = webhook_manager.get_usage_stats()
            print(f"Usage stats: {stats}")
    
    asyncio.run(main())