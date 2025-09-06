"""🚀 Integration Events System - IA Influencer Agent Platform
==============================================================
Module: events/integration_events.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 INTEGRATION EVENTS
Cross-service integration events for distributed systems
- External API integration events
- Microservice communication events
- Third-party platform events
- Webhook and callback events
- Data synchronization events
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal

from .core.base_event import BaseEvent
from .core.event_priority import EventPriority


@dataclass
class ExternalAPICallStartedEvent(BaseEvent):
    """External API call started event"""
    
    def __init__(self,
                 api_name: str,
                 endpoint: str,
                 method: str,
                 request_id: str,
                 correlation_id: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.api.call.started",
            data={
                "api_name": api_name,
                "endpoint": endpoint,
                "method": method,
                "request_id": request_id,
                "correlation_id": correlation_id
            },
            metadata=metadata or {},
            priority=EventPriority.LOW
        )


@dataclass
class ExternalAPICallCompletedEvent(BaseEvent):
    """External API call completed event"""
    
    def __init__(self,
                 api_name: str,
                 endpoint: str,
                 request_id: str,
                 status_code: int,
                 response_time_ms: float,
                 success: bool,
                 error_message: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.api.call.completed",
            data={
                "api_name": api_name,
                "endpoint": endpoint,
                "request_id": request_id,
                "status_code": status_code,
                "response_time_ms": response_time_ms,
                "success": success,
                "error_message": error_message
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM if success else EventPriority.HIGH
        )


@dataclass
class WebhookReceivedEvent(BaseEvent):
    """Webhook received from external service"""
    
    def __init__(self,
                 source: str,
                 webhook_type: str,
                 payload: Dict[str, Any],
                 signature: Optional[str] = None,
                 verified: bool = False,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.webhook.received",
            data={
                "source": source,
                "webhook_type": webhook_type,
                "payload": payload,
                "signature": signature,
                "verified": verified
            },
            metadata=metadata or {},
            priority=EventPriority.HIGH
        )


@dataclass
class WebhookSentEvent(BaseEvent):
    """Webhook sent to external service"""
    
    def __init__(self,
                 target_url: str,
                 webhook_type: str,
                 payload: Dict[str, Any],
                 attempt_number: int = 1,
                 success: bool = False,
                 response_code: Optional[int] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.webhook.sent",
            data={
                "target_url": target_url,
                "webhook_type": webhook_type,
                "payload": payload,
                "attempt_number": attempt_number,
                "success": success,
                "response_code": response_code
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class DataSyncStartedEvent(BaseEvent):
    """Data synchronization started"""
    
    def __init__(self,
                 sync_id: str,
                 source_system: str,
                 target_system: str,
                 data_type: str,
                 record_count: Optional[int] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.data.sync.started",
            data={
                "sync_id": sync_id,
                "source_system": source_system,
                "target_system": target_system,
                "data_type": data_type,
                "record_count": record_count
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class DataSyncCompletedEvent(BaseEvent):
    """Data synchronization completed"""
    
    def __init__(self,
                 sync_id: str,
                 source_system: str,
                 target_system: str,
                 records_processed: int,
                 records_success: int,
                 records_failed: int,
                 duration_seconds: float,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.data.sync.completed",
            data={
                "sync_id": sync_id,
                "source_system": source_system,
                "target_system": target_system,
                "records_processed": records_processed,
                "records_success": records_success,
                "records_failed": records_failed,
                "duration_seconds": duration_seconds
            },
            metadata=metadata or {},
            priority=EventPriority.HIGH
        )


@dataclass
class ThirdPartyServiceConnectedEvent(BaseEvent):
    """Third-party service connection established"""
    
    def __init__(self,
                 service_name: str,
                 user_id: str,
                 connection_type: str,
                 permissions: List[str],
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.thirdparty.connected",
            data={
                "service_name": service_name,
                "user_id": user_id,
                "connection_type": connection_type,
                "permissions": permissions
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class ThirdPartyServiceDisconnectedEvent(BaseEvent):
    """Third-party service disconnected"""
    
    def __init__(self,
                 service_name: str,
                 user_id: str,
                 reason: str,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.thirdparty.disconnected",
            data={
                "service_name": service_name,
                "user_id": user_id,
                "reason": reason
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class PlatformContentSyncEvent(BaseEvent):
    """Content synchronized with external platform"""
    
    def __init__(self,
                 content_id: str,
                 platform: str,
                 platform_content_id: str,
                 sync_type: str,
                 status: str,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.platform.content.sync",
            data={
                "content_id": content_id,
                "platform": platform,
                "platform_content_id": platform_content_id,
                "sync_type": sync_type,
                "status": status
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class PaymentGatewayTransactionEvent(BaseEvent):
    """Payment gateway transaction event"""
    
    def __init__(self,
                 transaction_id: str,
                 gateway: str,
                 user_id: str,
                 amount: Decimal,
                 currency: str,
                 transaction_type: str,
                 status: str,
                 gateway_response: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.payment.transaction",
            data={
                "transaction_id": transaction_id,
                "gateway": gateway,
                "user_id": user_id,
                "amount": str(amount),
                "currency": currency,
                "transaction_type": transaction_type,
                "status": status,
                "gateway_response": gateway_response or {}
            },
            metadata=metadata or {},
            priority=EventPriority.HIGH
        )


@dataclass
class EmailServiceDeliveryEvent(BaseEvent):
    """Email service delivery event"""
    
    def __init__(self,
                 message_id: str,
                 service_provider: str,
                 recipient: str,
                 email_type: str,
                 delivery_status: str,
                 bounce_reason: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.email.delivery",
            data={
                "message_id": message_id,
                "service_provider": service_provider,
                "recipient": recipient,
                "email_type": email_type,
                "delivery_status": delivery_status,
                "bounce_reason": bounce_reason
            },
            metadata=metadata or {},
            priority=EventPriority.LOW
        )


@dataclass
class SMSServiceDeliveryEvent(BaseEvent):
    """SMS service delivery event"""
    
    def __init__(self,
                 message_id: str,
                 service_provider: str,
                 recipient: str,
                 message_type: str,
                 delivery_status: str,
                 error_code: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.sms.delivery",
            data={
                "message_id": message_id,
                "service_provider": service_provider,
                "recipient": recipient,
                "message_type": message_type,
                "delivery_status": delivery_status,
                "error_code": error_code
            },
            metadata=metadata or {},
            priority=EventPriority.LOW
        )


@dataclass
class CloudStorageOperationEvent(BaseEvent):
    """Cloud storage operation event"""
    
    def __init__(self,
                 operation_id: str,
                 provider: str,
                 operation_type: str,
                 file_path: str,
                 file_size: Optional[int] = None,
                 success: bool = True,
                 error_message: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.storage.operation",
            data={
                "operation_id": operation_id,
                "provider": provider,
                "operation_type": operation_type,
                "file_path": file_path,
                "file_size": file_size,
                "success": success,
                "error_message": error_message
            },
            metadata=metadata or {},
            priority=EventPriority.LOW
        )


@dataclass
class CDNPurgeEvent(BaseEvent):
    """CDN cache purge event"""
    
    def __init__(self,
                 purge_id: str,
                 cdn_provider: str,
                 purge_type: str,
                 paths: List[str],
                 status: str,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.cdn.purge",
            data={
                "purge_id": purge_id,
                "cdn_provider": cdn_provider,
                "purge_type": purge_type,
                "paths": paths,
                "status": status
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class AnalyticsServiceDataSentEvent(BaseEvent):
    """Analytics data sent to external service"""
    
    def __init__(self,
                 service: str,
                 data_type: str,
                 record_count: int,
                 batch_id: str,
                 success: bool,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.analytics.data.sent",
            data={
                "service": service,
                "data_type": data_type,
                "record_count": record_count,
                "batch_id": batch_id,
                "success": success
            },
            metadata=metadata or {},
            priority=EventPriority.LOW
        )


@dataclass
class MicroserviceCallEvent(BaseEvent):
    """Microservice to microservice call event"""
    
    def __init__(self,
                 source_service: str,
                 target_service: str,
                 operation: str,
                 request_id: str,
                 response_time_ms: Optional[float] = None,
                 status_code: Optional[int] = None,
                 success: Optional[bool] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.microservice.call",
            data={
                "source_service": source_service,
                "target_service": target_service,
                "operation": operation,
                "request_id": request_id,
                "response_time_ms": response_time_ms,
                "status_code": status_code,
                "success": success
            },
            metadata=metadata or {},
            priority=EventPriority.LOW
        )


@dataclass
class ConfigurationUpdatedEvent(BaseEvent):
    """Configuration updated from external source"""
    
    def __init__(self,
                 config_source: str,
                 config_key: str,
                 old_value: Optional[str] = None,
                 new_value: Optional[str] = None,
                 applied: bool = False,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="integration.config.updated",
            data={
                "config_source": config_source,
                "config_key": config_key,
                "old_value": old_value,
                "new_value": new_value,
                "applied": applied
            },
            metadata=metadata or {},
            priority=EventPriority.HIGH
        )


# Factory functions for integration events
def create_api_event(event_type: str, api_name: str, **kwargs) -> BaseEvent:
    """Create an API integration event"""
    return BaseEvent(
        event_type=f"integration.api.{event_type}",
        data={"api_name": api_name, **kwargs},
        priority=EventPriority.MEDIUM
    )


def create_webhook_event(event_type: str, source: str, **kwargs) -> BaseEvent:
    """Create a webhook integration event"""
    return BaseEvent(
        event_type=f"integration.webhook.{event_type}",
        data={"source": source, **kwargs},
        priority=EventPriority.HIGH
    )


def create_sync_event(event_type: str, sync_id: str, **kwargs) -> BaseEvent:
    """Create a data sync event"""
    return BaseEvent(
        event_type=f"integration.sync.{event_type}",
        data={"sync_id": sync_id, **kwargs},
        priority=EventPriority.MEDIUM
    )


def create_platform_event(event_type: str, platform: str, **kwargs) -> BaseEvent:
    """Create a platform integration event"""
    return BaseEvent(
        event_type=f"integration.platform.{event_type}",
        data={"platform": platform, **kwargs},
        priority=EventPriority.MEDIUM
    )


def create_service_event(event_type: str, service: str, **kwargs) -> BaseEvent:
    """Create a service integration event"""
    return BaseEvent(
        event_type=f"integration.service.{event_type}",
        data={"service": service, **kwargs},
        priority=EventPriority.MEDIUM
    )


# Integration event types registry
INTEGRATION_EVENT_TYPES = {
    # API events
    "integration.api.call.started",
    "integration.api.call.completed",
    "integration.api.call.failed",
    "integration.api.rate.limited",
    
    # Webhook events
    "integration.webhook.received",
    "integration.webhook.sent",
    "integration.webhook.failed",
    "integration.webhook.verified",
    
    # Data sync events
    "integration.data.sync.started",
    "integration.data.sync.completed",
    "integration.data.sync.failed",
    "integration.data.conflict.detected",
    
    # Third-party service events
    "integration.thirdparty.connected",
    "integration.thirdparty.disconnected",
    "integration.thirdparty.error",
    "integration.thirdparty.rate.limited",
    
    # Platform sync events
    "integration.platform.content.sync",
    "integration.platform.user.sync",
    "integration.platform.analytics.sync",
    
    # Payment gateway events
    "integration.payment.transaction",
    "integration.payment.webhook",
    "integration.payment.failed",
    
    # Communication service events
    "integration.email.sent",
    "integration.email.delivery",
    "integration.email.bounce",
    "integration.sms.sent",
    "integration.sms.delivery",
    "integration.sms.failed",
    
    # Storage events
    "integration.storage.operation",
    "integration.storage.sync",
    "integration.storage.error",
    
    # CDN events
    "integration.cdn.purge",
    "integration.cdn.invalidation",
    "integration.cdn.error",
    
    # Analytics events
    "integration.analytics.data.sent",
    "integration.analytics.report.generated",
    
    # Microservice events
    "integration.microservice.call",
    "integration.microservice.timeout",
    "integration.microservice.error",
    
    # Configuration events
    "integration.config.updated",
    "integration.config.sync",
    "integration.config.error"
}


def is_integration_event(event_type: str) -> bool:
    """Check if event type is a valid integration event"""
    return event_type in INTEGRATION_EVENT_TYPES