"""MongoDB Webhook Dispatcher
===========================

Webhook-based notifications and integrations system for MongoDB synchronization
in the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import threading
from queue import Queue
import time
import hashlib
import hmac

try:
    import aiohttp
    import requests
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False

from . import SyncEvent

logger = logging.getLogger(__name__)

class WebhookEvent(Enum):
    """Webhook event types."""
    SYNC_STARTED = "sync_started"
    SYNC_COMPLETED = "sync_completed"
    SYNC_FAILED = "sync_failed"
    DOCUMENT_SYNCED = "document_synced"
    CONFLICT_DETECTED = "conflict_detected"
    CONFLICT_RESOLVED = "conflict_resolved"
    ERROR_OCCURRED = "error_occurred"
    HEALTH_CHECK = "health_check"

class DeliveryStatus(Enum):
    """Webhook delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"

@dataclass
class WebhookConfig:
    """Webhook configuration."""
    webhook_id: str
    url: str
    events: List[WebhookEvent]
    secret: Optional[str] = None
    headers: Dict[str, str] = None
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 5
    enabled: bool = True

@dataclass
class WebhookDelivery:
    """Webhook delivery record."""
    delivery_id: str
    webhook_id: str
    event_type: WebhookEvent
    payload: Dict[str, Any]
    url: str
    status: DeliveryStatus
    attempts: int
    created_at: datetime
    delivered_at: Optional[datetime] = None
    last_attempt_at: Optional[datetime] = None
    error_message: Optional[str] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None

class WebhookDispatcher:
    """Enterprise-grade webhook dispatcher for MongoDB sync events."""
    
    def __init__(self, max_workers -> None: int = 10) -> None:
        """Initialize webhook dispatcher."""
        if not HTTP_AVAILABLE:
            logger.warning("aiohttp not available - webhook functionality limited")
        
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.delivery_queue = Queue(maxsize=10000)
        self.delivery_history: List[WebhookDelivery] = []
        self.max_workers = max_workers
        
        # Worker threads
        self.worker_threads = []
        self.running = False
        self.shutdown_event = threading.Event()
        
        # Configuration
        self.max_history_size = 10000
        self.cleanup_interval_hours = 24
        self.delivery_timeout = 30
        
        # Statistics
        self.stats = {
            'total_dispatched': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'retries': 0
        }
    
    def register_webhook(self, config -> None: WebhookConfig) -> None:
        """Register a new webhook."""
        self.webhooks[config.webhook_id] = config
        logger.info(f"Registered webhook: {config.webhook_id} -> {config.url}")
    
    def unregister_webhook(self, webhook_id -> None: str) -> None:
        """Unregister a webhook."""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            logger.info(f"Unregistered webhook: {webhook_id}")
    
    def dispatch_event(self, event_type -> None: WebhookEvent, payload -> None: Dict[str, Any]) -> None:
        """Dispatch an event to all registered webhooks."""
        for webhook_id, webhook_config in self.webhooks.items():
            if not webhook_config.enabled:
                continue
            
            if event_type in webhook_config.events:
                self._queue_delivery(webhook_config, event_type, payload)
    
    def _queue_delivery(self, webhook_config -> None: WebhookConfig, event_type -> None: WebhookEvent, payload -> None: Dict[str, Any]) -> None:
        """Queue a webhook delivery."""
        delivery = WebhookDelivery(
            delivery_id=self._generate_delivery_id(),
            webhook_id=webhook_config.webhook_id,
            event_type=event_type,
            payload=payload,
            url=webhook_config.url,
            status=DeliveryStatus.PENDING,
            attempts=0,
            created_at=datetime.now()
        )
        
        try:
            self.delivery_queue.put(delivery, timeout=1)
            self.stats['total_dispatched'] += 1
            logger.debug(f"Queued webhook delivery: {delivery.delivery_id}")
        except:
            logger.warning(f"Webhook delivery queue full, dropping delivery for {webhook_config.webhook_id}")
    
    def _generate_delivery_id(self) -> str:
        """Generate unique delivery ID."""
        timestamp = str(int(time.time() * 1000000))
        return hashlib.md5(timestamp.encode()).hexdigest()[:16]
    
    def start_workers(self) -> None:
        """Start webhook worker threads."""
        if self.running:
            logger.warning("Webhook dispatcher already running")
            return
        
        self.running = True
        
        # Start worker threads
        for i in range(self.max_workers):
            worker_thread = threading.Thread(
                target=self._worker_loop,
                args=(f"webhook_worker_{i}",),
                daemon=True
            )
            worker_thread.start()
            self.worker_threads.append(worker_thread)
        
        # Start cleanup thread
        cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True
        )
        cleanup_thread.start()
        self.worker_threads.append(cleanup_thread)
        
        logger.info(f"Started {self.max_workers} webhook workers")
    
    def _worker_loop(self, worker_name -> None: str) -> None:
        """Main worker loop for processing webhook deliveries."""
        logger.info(f"Webhook worker started: {worker_name}")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                # Get delivery from queue
                delivery = self.delivery_queue.get(timeout=1)
                
                # Process the delivery
                self._process_delivery(delivery)
                
                # Mark task as done
                self.delivery_queue.task_done()
                
            except:
                # Timeout or shutdown
                continue
        
        logger.info(f"Webhook worker stopped: {worker_name}")
    
    def _process_delivery(self, delivery -> None: WebhookDelivery) -> None:
        """Process a webhook delivery."""
        webhook_config = self.webhooks.get(delivery.webhook_id)
        
        if not webhook_config or not webhook_config.enabled:
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = "Webhook not found or disabled"
            self._record_delivery(delivery)
            return
        
        delivery.attempts += 1
        delivery.last_attempt_at = datetime.now()
        
        try:
            # Prepare payload
            webhook_payload = self._prepare_payload(delivery, webhook_config)
            
            # Send webhook
            success, response_code, response_body, error = self._send_webhook(
                webhook_config, webhook_payload
            )
            
            delivery.response_code = response_code
            delivery.response_body = response_body[:1000] if response_body else None  # Limit size
            
            if success:
                delivery.status = DeliveryStatus.DELIVERED
                delivery.delivered_at = datetime.now()
                self.stats['successful_deliveries'] += 1
                logger.debug(f"Webhook delivered successfully: {delivery.delivery_id}")
            else:
                delivery.error_message = error
                
                # Check if we should retry
                if delivery.attempts < webhook_config.max_retries:
                    delivery.status = DeliveryStatus.RETRYING
                    # Re-queue for retry after delay
                    self._schedule_retry(delivery, webhook_config.retry_delay_seconds)
                    self.stats['retries'] += 1
                else:
                    delivery.status = DeliveryStatus.FAILED
                    self.stats['failed_deliveries'] += 1
                    logger.warning(f"Webhook delivery failed after {delivery.attempts} attempts: {delivery.delivery_id}")
        
        except Exception as e:
            delivery.error_message = str(e)
            delivery.status = DeliveryStatus.FAILED
            self.stats['failed_deliveries'] += 1
            logger.error(f"Error processing webhook delivery {delivery.delivery_id}: {e}")
        
        # Record delivery
        self._record_delivery(delivery)
    
    def _prepare_payload(self, delivery: WebhookDelivery, webhook_config: WebhookConfig) -> Dict[str, Any]:
        """Prepare webhook payload."""
        webhook_payload = {
            'event_type': delivery.event_type.value,
            'webhook_id': delivery.webhook_id,
            'delivery_id': delivery.delivery_id,
            'timestamp': delivery.created_at.isoformat(),
            'data': delivery.payload
        }
        
        # Add signature if secret is configured
        if webhook_config.secret:
            signature = self._generate_signature(webhook_payload, webhook_config.secret)
            webhook_payload['signature'] = signature
        
        return webhook_payload
    
    def _generate_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Generate HMAC signature for webhook payload."""
        payload_string = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def _send_webhook(self, webhook_config: WebhookConfig, payload: Dict[str, Any]) -> tuple:
        """Send webhook HTTP request."""
        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Ainflue-Webhook-Dispatcher/1.0'
            }
            
            # Add custom headers
            if webhook_config.headers:
                headers.update(webhook_config.headers)
            
            # Send request
            response = requests.post(
                webhook_config.url,
                json=payload,
                headers=headers,
                timeout=webhook_config.timeout_seconds
            )
            
            # Check response
            if 200 <= response.status_code < 300:
                return True, response.status_code, response.text, None
            else:
                return False, response.status_code, response.text, f"HTTP {response.status_code}"
        
        except requests.exceptions.Timeout:
            return False, None, None, "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, None, None, "Connection error"
        except Exception as e:
            return False, None, None, str(e)
    
    def _schedule_retry(self, delivery -> None: WebhookDelivery, delay_seconds -> None: int) -> None:
        """Schedule a delivery for retry."""
        def retry_after_delay() -> None:
            time.sleep(delay_seconds)
            if self.running:
                try:
                    self.delivery_queue.put(delivery, timeout=1)
                except:
                    logger.warning(f"Failed to re-queue delivery for retry: {delivery.delivery_id}")
        
        retry_thread = threading.Thread(target=retry_after_delay, daemon=True)
        retry_thread.start()
    
    def _record_delivery(self, delivery -> None: WebhookDelivery) -> None:
        """Record delivery in history."""
        self.delivery_history.append(delivery)
        
        # Limit history size
        if len(self.delivery_history) > self.max_history_size:
            self.delivery_history = self.delivery_history[-self.max_history_size:]
    
    def _cleanup_loop(self) -> None:
        """Cleanup old delivery records."""
        while self.running and not self.shutdown_event.is_set():
            try:
                # Clean up old deliveries
                cutoff_time = datetime.now() - timedelta(hours=self.cleanup_interval_hours)
                
                initial_count = len(self.delivery_history)
                self.delivery_history = [
                    d for d in self.delivery_history
                    if d.created_at > cutoff_time or d.status in [DeliveryStatus.PENDING, DeliveryStatus.RETRYING]
                ]
                
                cleaned_count = initial_count - len(self.delivery_history)
                if cleaned_count > 0:
                    logger.info(f"Cleaned up {cleaned_count} old webhook delivery records")
                
                # Sleep for cleanup interval
                time.sleep(self.cleanup_interval_hours * 3600)
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                time.sleep(3600)  # Sleep 1 hour on error
    
    # Event-specific dispatch methods
    def dispatch_sync_started(self, sync_id -> None: str, config -> None: Dict[str, Any]) -> None:
        """Dispatch sync started event."""
        payload = {
            'sync_id': sync_id,
            'config': config,
            'message': 'Synchronization started'
        }
        self.dispatch_event(WebhookEvent.SYNC_STARTED, payload)
    
    def dispatch_sync_completed(self, sync_id -> None: str, stats -> None: Dict[str, Any]) -> None:
        """Dispatch sync completed event."""
        payload = {
            'sync_id': sync_id,
            'statistics': stats,
            'message': 'Synchronization completed successfully'
        }
        self.dispatch_event(WebhookEvent.SYNC_COMPLETED, payload)
    
    def dispatch_sync_failed(self, sync_id -> None: str, error -> None: str, stats -> None: Dict[str, Any]) -> None:
        """Dispatch sync failed event."""
        payload = {
            'sync_id': sync_id,
            'error': error,
            'statistics': stats,
            'message': 'Synchronization failed'
        }
        self.dispatch_event(WebhookEvent.SYNC_FAILED, payload)
    
    def dispatch_document_synced(self, sync_event -> None: SyncEvent) -> None:
        """Dispatch document synced event."""
        payload = {
            'sync_id': sync_event.sync_id,
            'operation_type': sync_event.operation_type,
            'collection': sync_event.collection,
            'document_id': str(sync_event.document_id),
            'timestamp': sync_event.timestamp.isoformat(),
            'status': sync_event.status,
            'message': f'Document {sync_event.operation_type} in {sync_event.collection}'
        }
        self.dispatch_event(WebhookEvent.DOCUMENT_SYNCED, payload)
    
    def dispatch_conflict_detected(self, conflict_id -> None: str, conflict_data -> None: Dict[str, Any]) -> None:
        """Dispatch conflict detected event."""
        payload = {
            'conflict_id': conflict_id,
            'conflict_type': conflict_data.get('type'),
            'collection': conflict_data.get('collection'),
            'document_id': str(conflict_data.get('document_id')),
            'message': 'Synchronization conflict detected'
        }
        self.dispatch_event(WebhookEvent.CONFLICT_DETECTED, payload)
    
    def dispatch_conflict_resolved(self, conflict_id -> None: str, resolution -> None: Dict[str, Any]) -> None:
        """Dispatch conflict resolved event."""
        payload = {
            'conflict_id': conflict_id,
            'resolution': resolution,
            'message': 'Synchronization conflict resolved'
        }
        self.dispatch_event(WebhookEvent.CONFLICT_RESOLVED, payload)
    
    def dispatch_error_occurred(self, error_type -> None: str, error_message -> None: str, context -> None: Dict[str, Any]) -> None:
        """Dispatch error occurred event."""
        payload = {
            'error_type': error_type,
            'error_message': error_message,
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'message': f'Error occurred: {error_type}'
        }
        self.dispatch_event(WebhookEvent.ERROR_OCCURRED, payload)
    
    def dispatch_health_check(self, health_status -> None: Dict[str, Any]) -> None:
        """Dispatch health check event."""
        payload = {
            'health_status': health_status,
            'timestamp': datetime.now().isoformat(),
            'message': 'Health check performed'
        }
        self.dispatch_event(WebhookEvent.HEALTH_CHECK, payload)
    
    def get_webhook_statistics(self) -> Dict[str, Any]:
        """Get webhook delivery statistics."""
        # Calculate recent statistics (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_deliveries = [d for d in self.delivery_history if d.created_at > recent_cutoff]
        
        recent_stats = {
            'successful': len([d for d in recent_deliveries if d.status == DeliveryStatus.DELIVERED]),
            'failed': len([d for d in recent_deliveries if d.status == DeliveryStatus.FAILED]),
            'pending': len([d for d in recent_deliveries if d.status in [DeliveryStatus.PENDING, DeliveryStatus.RETRYING]])
        }
        
        # Calculate success rate
        total_completed = self.stats['successful_deliveries'] + self.stats['failed_deliveries']
        success_rate = (self.stats['successful_deliveries'] / total_completed * 100) if total_completed > 0 else 0
        
        return {
            'total_stats': self.stats,
            'recent_24h': recent_stats,
            'success_rate_percent': round(success_rate, 2),
            'active_webhooks': len([w for w in self.webhooks.values() if w.enabled]),
            'total_webhooks': len(self.webhooks),
            'queue_size': self.delivery_queue.qsize(),
            'history_size': len(self.delivery_history)
        }
    
    def get_delivery_history(self, webhook_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get webhook delivery history."""
        deliveries = self.delivery_history
        
        if webhook_id:
            deliveries = [d for d in deliveries if d.webhook_id == webhook_id]
        
        # Sort by creation time (newest first) and limit
        deliveries = sorted(deliveries, key=lambda d: d.created_at, reverse=True)[:limit]
        
        return [asdict(delivery) for delivery in deliveries]
    
    def get_failed_deliveries(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get failed deliveries within specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        failed_deliveries = [
            d for d in self.delivery_history
            if d.status == DeliveryStatus.FAILED and d.created_at > cutoff_time
        ]
        
        return [asdict(delivery) for delivery in failed_deliveries]
    
    def retry_failed_delivery(self, delivery_id: str) -> bool:
        """Manually retry a failed delivery."""
        for delivery in self.delivery_history:
            if delivery.delivery_id == delivery_id and delivery.status == DeliveryStatus.FAILED:
                # Reset delivery for retry
                delivery.status = DeliveryStatus.PENDING
                delivery.error_message = None
                delivery.attempts = 0
                
                try:
                    self.delivery_queue.put(delivery, timeout=1)
                    logger.info(f"Manually retrying delivery: {delivery_id}")
                    return True
                except:
                    logger.warning(f"Failed to queue delivery for retry: {delivery_id}")
                    return False
        
        return False
    
    def test_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Test a webhook by sending a test event."""
        if webhook_id not in self.webhooks:
            return {'success': False, 'error': 'Webhook not found'}
        
        webhook_config = self.webhooks[webhook_id]
        
        # Create test payload
        test_payload = {
            'test': True,
            'webhook_id': webhook_id,
            'timestamp': datetime.now().isoformat(),
            'message': 'This is a test webhook delivery'
        }
        
        # Send test webhook
        webhook_payload = self._prepare_payload(
            WebhookDelivery(
                delivery_id='test',
                webhook_id=webhook_id,
                event_type=WebhookEvent.HEALTH_CHECK,
                payload=test_payload,
                url=webhook_config.url,
                status=DeliveryStatus.PENDING,
                attempts=0,
                created_at=datetime.now()
            ),
            webhook_config
        )
        
        success, response_code, response_body, error = self._send_webhook(webhook_config, webhook_payload)
        
        return {
            'success': success,
            'response_code': response_code,
            'response_body': response_body,
            'error': error
        }
    
    def stop_workers(self) -> None:
        """Stop webhook workers."""
        if not self.running:
            return
        
        logger.info("Stopping webhook dispatcher")
        self.running = False
        self.shutdown_event.set()
        
        # Wait for workers to finish
        for thread in self.worker_threads:
            thread.join(timeout=5)
        
        logger.info("Webhook dispatcher stopped")

# Export the main class
__all__ = ['WebhookDispatcher', 'WebhookConfig', 'WebhookEvent', 'WebhookDelivery']