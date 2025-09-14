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
                 api_name -> None: str,
                 endpoint -> None: str,
                 method -> None: str,
                 request_id -> None: str,
                 correlation_id -> None: Optional[str] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 api_name -> None: str,
                 endpoint -> None: str,
                 request_id -> None: str,
                 status_code -> None: int,
                 response_time_ms -> None: float,
                 success -> None: bool,
                 error_message -> None: Optional[str] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 source -> None: str,
                 webhook_type -> None: str,
                 payload -> None: Dict[str, Any],
                 signature -> None: Optional[str] = None,
                 verified -> None: bool = False,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 target_url -> None: str,
                 webhook_type -> None: str,
                 payload -> None: Dict[str, Any],
                 attempt_number -> None: int = 1,
                 success -> None: bool = False,
                 response_code -> None: Optional[int] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 sync_id -> None: str,
                 source_system -> None: str,
                 target_system -> None: str,
                 data_type -> None: str,
                 record_count -> None: Optional[int] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 sync_id -> None: str,
                 source_system -> None: str,
                 target_system -> None: str,
                 records_processed -> None: int,
                 records_success -> None: int,
                 records_failed -> None: int,
                 duration_seconds -> None: float,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 service_name -> None: str,
                 user_id -> None: str,
                 connection_type -> None: str,
                 permissions -> None: List[str],
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 service_name -> None: str,
                 user_id -> None: str,
                 reason -> None: str,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 content_id -> None: str,
                 platform -> None: str,
                 platform_content_id -> None: str,
                 sync_type -> None: str,
                 status -> None: str,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 transaction_id -> None: str,
                 gateway -> None: str,
                 user_id -> None: str,
                 amount -> None: Decimal,
                 currency -> None: str,
                 transaction_type -> None: str,
                 status -> None: str,
                 gateway_response -> None: Optional[Dict[str, Any]] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 message_id -> None: str,
                 service_provider -> None: str,
                 recipient -> None: str,
                 email_type -> None: str,
                 delivery_status -> None: str,
                 bounce_reason -> None: Optional[str] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 message_id -> None: str,
                 service_provider -> None: str,
                 recipient -> None: str,
                 message_type -> None: str,
                 delivery_status -> None: str,
                 error_code -> None: Optional[str] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 operation_id -> None: str,
                 provider -> None: str,
                 operation_type -> None: str,
                 file_path -> None: str,
                 file_size -> None: Optional[int] = None,
                 success -> None: bool = True,
                 error_message -> None: Optional[str] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 purge_id -> None: str,
                 cdn_provider -> None: str,
                 purge_type -> None: str,
                 paths -> None: List[str],
                 status -> None: str,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 service -> None: str,
                 data_type -> None: str,
                 record_count -> None: int,
                 batch_id -> None: str,
                 success -> None: bool,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 source_service -> None: str,
                 target_service -> None: str,
                 operation -> None: str,
                 request_id -> None: str,
                 response_time_ms -> None: Optional[float] = None,
                 status_code -> None: Optional[int] = None,
                 success -> None: Optional[bool] = None,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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
                 config_source -> None: str,
                 config_key -> None: str,
                 old_value -> None: Optional[str] = None,
                 new_value -> None: Optional[str] = None,
                 applied -> None: bool = False,
                 metadata -> None: Optional[Dict[str, Any]] = None) -> None:
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