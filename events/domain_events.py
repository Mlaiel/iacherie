"""🚀 Domain Events System - IA Influencer Agent Platform
=========================================================
Module: events/domain_events.py
Author: Fahed Mlaiel (mlaiel@live.de)
=========================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 BUSINESS DOMAIN EVENTS
Core business domain events for the IA Influencer platform
- User lifecycle events
- Content management events
- AI processing events
- Collaboration events
- Monetization events
- Analytics and tracking events
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from decimal import Decimal

from .core.base_event import BaseEvent
from .core.event_priority import EventPriority


@dataclass
class UserCreatedEvent(BaseEvent):
    """User account created event"""
    
    def __init__(self,
                 user_id: str,
                 email: str,
                 username: str,
                 creator_type: str,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="user.created",
            data={
                "user_id": user_id,
                "email": email,
                "username": username,
                "creator_type": creator_type
            },
            metadata=metadata or {},
            priority=EventPriority.HIGH
        )


@dataclass
class UserVerifiedEvent(BaseEvent):
    """User verification completed event"""
    
    def __init__(self,
                 user_id: str,
                 verification_type: str,
                 verification_level: str,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="user.verified",
            data={
                "user_id": user_id,
                "verification_type": verification_type,
                "verification_level": verification_level
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class ContentUploadedEvent(BaseEvent):
    """Content uploaded to platform event"""
    
    def __init__(self,
                 content_id: str,
                 user_id: str,
                 content_type: str,
                 file_size: int,
                 duration: Optional[float] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="content.uploaded",
            data={
                "content_id": content_id,
                "user_id": user_id,
                "content_type": content_type,
                "file_size": file_size,
                "duration": duration
            },
            metadata=metadata or {},
            priority=EventPriority.HIGH
        )


@dataclass
class ContentProcessingStartedEvent(BaseEvent):
    """Content processing started event"""
    
    def __init__(self,
                 content_id: str,
                 processing_type: str,
                 ai_model: str,
                 estimated_duration: Optional[int] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="content.processing.started",
            data={
                "content_id": content_id,
                "processing_type": processing_type,
                "ai_model": ai_model,
                "estimated_duration": estimated_duration
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class ContentProcessingCompletedEvent(BaseEvent):
    """Content processing completed event"""
    
    def __init__(self,
                 content_id: str,
                 processing_type: str,
                 results: Dict[str, Any],
                 processing_time: float,
                 success: bool = True,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="content.processing.completed",
            data={
                "content_id": content_id,
                "processing_type": processing_type,
                "results": results,
                "processing_time": processing_time,
                "success": success
            },
            metadata=metadata or {},
            priority=EventPriority.HIGH
        )


@dataclass
class AIAnalysisStartedEvent(BaseEvent):
    """AI analysis started event"""
    
    def __init__(self,
                 content_id: str,
                 analysis_type: str,
                 ai_model: str,
                 parameters: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="ai.analysis.started",
            data={
                "content_id": content_id,
                "analysis_type": analysis_type,
                "ai_model": ai_model,
                "parameters": parameters or {}
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class AIAnalysisCompletedEvent(BaseEvent):
    """AI analysis completed event"""
    
    def __init__(self,
                 content_id: str,
                 analysis_type: str,
                 results: Dict[str, Any],
                 confidence_score: float,
                 processing_time: float,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="ai.analysis.completed",
            data={
                "content_id": content_id,
                "analysis_type": analysis_type,
                "results": results,
                "confidence_score": confidence_score,
                "processing_time": processing_time
            },
            metadata=metadata or {},
            priority=EventPriority.HIGH
        )


@dataclass
class CopyrightDetectedEvent(BaseEvent):
    """Copyright detection event"""
    
    def __init__(self,
                 content_id: str,
                 detection_type: str,
                 matches: List[Dict[str, Any]],
                 confidence_score: float,
                 action_required: bool,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="copyright.detected",
            data={
                "content_id": content_id,
                "detection_type": detection_type,
                "matches": matches,
                "confidence_score": confidence_score,
                "action_required": action_required
            },
            metadata=metadata or {},
            priority=EventPriority.CRITICAL
        )


@dataclass
class CollaborationRequestedEvent(BaseEvent):
    """Collaboration request event"""
    
    def __init__(self,
                 collaboration_id: str,
                 requester_id: str,
                 target_user_id: str,
                 collaboration_type: str,
                 message: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="collaboration.requested",
            data={
                "collaboration_id": collaboration_id,
                "requester_id": requester_id,
                "target_user_id": target_user_id,
                "collaboration_type": collaboration_type,
                "message": message
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class CollaborationAcceptedEvent(BaseEvent):
    """Collaboration accepted event"""
    
    def __init__(self,
                 collaboration_id: str,
                 acceptor_id: str,
                 terms: Dict[str, Any],
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="collaboration.accepted",
            data={
                "collaboration_id": collaboration_id,
                "acceptor_id": acceptor_id,
                "terms": terms
            },
            metadata=metadata or {},
            priority=EventPriority.HIGH
        )


@dataclass
class RevenueGeneratedEvent(BaseEvent):
    """Revenue generated event"""
    
    def __init__(self,
                 content_id: str,
                 user_id: str,
                 revenue_amount: Decimal,
                 currency: str,
                 source: str,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="revenue.generated",
            data={
                "content_id": content_id,
                "user_id": user_id,
                "revenue_amount": str(revenue_amount),
                "currency": currency,
                "source": source
            },
            metadata=metadata or {},
            priority=EventPriority.HIGH
        )


@dataclass
class PayoutProcessedEvent(BaseEvent):
    """Payout processed event"""
    
    def __init__(self,
                 payout_id: str,
                 user_id: str,
                 amount: Decimal,
                 currency: str,
                 payment_method: str,
                 status: str,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="payout.processed",
            data={
                "payout_id": payout_id,
                "user_id": user_id,
                "amount": str(amount),
                "currency": currency,
                "payment_method": payment_method,
                "status": status
            },
            metadata=metadata or {},
            priority=EventPriority.HIGH
        )


@dataclass
class ContentViewedEvent(BaseEvent):
    """Content viewed event"""
    
    def __init__(self,
                 content_id: str,
                 viewer_id: Optional[str],
                 session_id: str,
                 view_duration: Optional[float] = None,
                 platform: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="content.viewed",
            data={
                "content_id": content_id,
                "viewer_id": viewer_id,
                "session_id": session_id,
                "view_duration": view_duration,
                "platform": platform
            },
            metadata=metadata or {},
            priority=EventPriority.LOW
        )


@dataclass
class ContentSharedEvent(BaseEvent):
    """Content shared event"""
    
    def __init__(self,
                 content_id: str,
                 sharer_id: str,
                 platform: str,
                 share_type: str,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="content.shared",
            data={
                "content_id": content_id,
                "sharer_id": sharer_id,
                "platform": platform,
                "share_type": share_type
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class SEOOptimizationCompletedEvent(BaseEvent):
    """SEO optimization completed event"""
    
    def __init__(self,
                 content_id: str,
                 optimization_type: str,
                 improvements: Dict[str, Any],
                 seo_score: float,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="seo.optimization.completed",
            data={
                "content_id": content_id,
                "optimization_type": optimization_type,
                "improvements": improvements,
                "seo_score": seo_score
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class SecurityThreatDetectedEvent(BaseEvent):
    """Security threat detected event"""
    
    def __init__(self,
                 threat_id: str,
                 threat_type: str,
                 severity: str,
                 source_ip: Optional[str] = None,
                 user_id: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="security.threat.detected",
            data={
                "threat_id": threat_id,
                "threat_type": threat_type,
                "severity": severity,
                "source_ip": source_ip,
                "user_id": user_id,
                "details": details or {}
            },
            metadata=metadata or {},
            priority=EventPriority.CRITICAL
        )


@dataclass
class SystemHealthCheckEvent(BaseEvent):
    """System health check event"""
    
    def __init__(self,
                 component: str,
                 status: str,
                 metrics: Dict[str, Any],
                 issues: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="system.health.check",
            data={
                "component": component,
                "status": status,
                "metrics": metrics,
                "issues": issues or []
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class BackupCompletedEvent(BaseEvent):
    """Backup completed event"""
    
    def __init__(self,
                 backup_id: str,
                 backup_type: str,
                 size_bytes: int,
                 duration_seconds: float,
                 success: bool,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="backup.completed",
            data={
                "backup_id": backup_id,
                "backup_type": backup_type,
                "size_bytes": size_bytes,
                "duration_seconds": duration_seconds,
                "success": success
            },
            metadata=metadata or {},
            priority=EventPriority.MEDIUM
        )


@dataclass
class NotificationSentEvent(BaseEvent):
    """Notification sent event"""
    
    def __init__(self,
                 notification_id: str,
                 user_id: str,
                 notification_type: str,
                 channel: str,
                 delivered: bool,
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            event_type="notification.sent",
            data={
                "notification_id": notification_id,
                "user_id": user_id,
                "notification_type": notification_type,
                "channel": channel,
                "delivered": delivered
            },
            metadata=metadata or {},
            priority=EventPriority.LOW
        )


# Factory functions for common event creation patterns
def create_user_event(event_type: str, user_id: str, **kwargs) -> BaseEvent:
    """Create a user-related event"""
    return BaseEvent(
        event_type=f"user.{event_type}",
        data={"user_id": user_id, **kwargs},
        priority=EventPriority.MEDIUM
    )


def create_content_event(event_type: str, content_id: str, user_id: str, **kwargs) -> BaseEvent:
    """Create a content-related event"""
    return BaseEvent(
        event_type=f"content.{event_type}",
        data={"content_id": content_id, "user_id": user_id, **kwargs},
        priority=EventPriority.MEDIUM
    )


def create_ai_event(event_type: str, content_id: str, **kwargs) -> BaseEvent:
    """Create an AI processing event"""
    return BaseEvent(
        event_type=f"ai.{event_type}",
        data={"content_id": content_id, **kwargs},
        priority=EventPriority.MEDIUM
    )


def create_collaboration_event(event_type: str, collaboration_id: str, **kwargs) -> BaseEvent:
    """Create a collaboration event"""
    return BaseEvent(
        event_type=f"collaboration.{event_type}",
        data={"collaboration_id": collaboration_id, **kwargs},
        priority=EventPriority.MEDIUM
    )


def create_revenue_event(event_type: str, user_id: str, amount: Decimal, currency: str, **kwargs) -> BaseEvent:
    """Create a revenue-related event"""
    return BaseEvent(
        event_type=f"revenue.{event_type}",
        data={
            "user_id": user_id,
            "amount": str(amount),
            "currency": currency,
            **kwargs
        },
        priority=EventPriority.HIGH
    )


def create_security_event(event_type: str, severity: str, **kwargs) -> BaseEvent:
    """Create a security event"""
    priority = EventPriority.CRITICAL if severity in ["high", "critical"] else EventPriority.HIGH
    return BaseEvent(
        event_type=f"security.{event_type}",
        data={"severity": severity, **kwargs},
        priority=priority
    )


def create_system_event(event_type: str, component: str, **kwargs) -> BaseEvent:
    """Create a system event"""
    return BaseEvent(
        event_type=f"system.{event_type}",
        data={"component": component, **kwargs},
        priority=EventPriority.MEDIUM
    )


# Event type registry for validation
DOMAIN_EVENT_TYPES = {
    # User events
    "user.created",
    "user.verified",
    "user.updated",
    "user.deleted",
    "user.suspended",
    "user.reactivated",
    
    # Content events
    "content.uploaded",
    "content.processing.started",
    "content.processing.completed",
    "content.processing.failed",
    "content.published",
    "content.updated",
    "content.deleted",
    "content.viewed",
    "content.liked",
    "content.shared",
    "content.commented",
    
    # AI events
    "ai.analysis.started",
    "ai.analysis.completed",
    "ai.analysis.failed",
    "ai.enhancement.started",
    "ai.enhancement.completed",
    "ai.recommendation.generated",
    
    # Copyright events
    "copyright.detected",
    "copyright.resolved",
    "copyright.disputed",
    
    # Collaboration events
    "collaboration.requested",
    "collaboration.accepted",
    "collaboration.rejected",
    "collaboration.completed",
    "collaboration.cancelled",
    
    # Revenue events
    "revenue.generated",
    "revenue.calculated",
    "payout.requested",
    "payout.processed",
    "payout.failed",
    
    # SEO events
    "seo.optimization.started",
    "seo.optimization.completed",
    "seo.ranking.updated",
    
    # Security events
    "security.threat.detected",
    "security.incident.created",
    "security.incident.resolved",
    
    # System events
    "system.health.check",
    "system.error",
    "system.warning",
    "backup.started",
    "backup.completed",
    "backup.failed",
    
    # Notification events
    "notification.sent",
    "notification.delivered",
    "notification.failed"
}


def is_domain_event(event_type: str) -> bool:
    """Check if event type is a valid domain event"""
    return event_type in DOMAIN_EVENT_TYPES