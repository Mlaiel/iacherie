"""IA-Influencer-Agent - Event Types Definition
Module: backend/core/events/event_types.py
Architecture: Event Type System for Business Logic
Auteur: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIÉTÉ INTELLECTUELLE - AVERTISSEMENT STRICT ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.

Description:
    Définitions des types d'événements métier pour la plateforme IA-Influencer-Agent.
    Couvre tous les événements de la logique métier : contenu, protection, monétisation, 
    collaboration et système.
"""
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid

from .event_bus import Event, EventPriority


class EventType(Enum):
    """Types d'événements principaux de la plateforme"""    
    # Événements contenu
    CONTENT_UPLOADED = "content.uploaded"
    CONTENT_PROCESSED = "content.processed"
    CONTENT_ANALYZED = "content.analyzed"
    CONTENT_FINGERPRINTED = "content.fingerprinted"
    CONTENT_APPROVED = "content.approved"
    CONTENT_REJECTED = "content.rejected"
    CONTENT_DELETED = "content.deleted"
    CONTENT_MODIFIED = "content.modified"
    
    # Événements protection
    PROTECTION_ENABLED = "protection.enabled"
    PROTECTION_VIOLATION_DETECTED = "protection.violation.detected"
    PROTECTION_TAKEDOWN_REQUESTED = "protection.takedown.requested"
    PROTECTION_TAKEDOWN_COMPLETED = "protection.takedown.completed"
    PROTECTION_WHITELIST_ADDED = "protection.whitelist.added"
    PROTECTION_MONITORING_STARTED = "protection.monitoring.started"
    PROTECTION_MONITORING_STOPPED = "protection.monitoring.stopped"
    
    # Événements monétisation
    MONETIZATION_ENABLED = "monetization.enabled"
    MONETIZATION_REVENUE_DETECTED = "monetization.revenue.detected"
    MONETIZATION_PAYMENT_PROCESSED = "monetization.payment.processed"
    MONETIZATION_PAYOUT_SCHEDULED = "monetization.payout.scheduled"
    MONETIZATION_PAYOUT_COMPLETED = "monetization.payout.completed"
    MONETIZATION_CLAIM_SUBMITTED = "monetization.claim.submitted"
    MONETIZATION_CLAIM_APPROVED = "monetization.claim.approved"
    
    # Événements collaboration
    COLLABORATION_INVITE_SENT = "collaboration.invite.sent"
    COLLABORATION_INVITE_ACCEPTED = "collaboration.invite.accepted"
    COLLABORATION_INVITE_DECLINED = "collaboration.invite.declined"
    COLLABORATION_PROJECT_CREATED = "collaboration.project.created"
    COLLABORATION_PROJECT_UPDATED = "collaboration.project.updated"
    COLLABORATION_PROJECT_COMPLETED = "collaboration.project.completed"
    COLLABORATION_MATCHING_FOUND = "collaboration.matching.found"
    
    # Événements système
    SYSTEM_USER_REGISTERED = "system.user.registered"
    SYSTEM_USER_AUTHENTICATED = "system.user.authenticated"
    SYSTEM_USER_UPGRADED = "system.user.upgraded"
    SYSTEM_API_LIMIT_REACHED = "system.api.limit.reached"
    SYSTEM_MAINTENANCE_STARTED = "system.maintenance.started"
    SYSTEM_MAINTENANCE_COMPLETED = "system.maintenance.completed"
    SYSTEM_ERROR_OCCURRED = "system.error.occurred"


@dataclass
class ContentEvent(Event):
    """Événement lié au contenu"""    
    content_id: str = ""
    content_type: str = ""  # audio, video, image, text
    file_size: int = 0
    duration: Optional[float] = None
    format: str = ""
    quality: Optional[str] = None
    
    def __post_init__(self):
        if not self.type:
            self.type = EventType.CONTENT_UPLOADED.value
        if not self.source:
            self.source = "content_service"
        if not self.subject:
            self.subject = f"content/{self.content_id}"
    
    @classmethod
    def create_uploaded(
        cls,
        content_id: str,
        content_type: str,
        file_size: int,
        format: str,
        user_id: str,
        tenant_id: str,
        **kwargs
    ) -> "ContentEvent":
        """Crée un événement de contenu uploadé"""        return cls(
            type=EventType.CONTENT_UPLOADED.value,
            content_id=content_id,
            content_type=content_type,
            file_size=file_size,
            format=format,
            user_id=user_id,
            tenant_id=tenant_id,
            priority=EventPriority.HIGH,
            data={
                "action": "uploaded",
                "content_id": content_id,
                "content_type": content_type,
                "file_size": file_size,
                "format": format,
                **kwargs
            }
        )
    
    @classmethod
    def create_fingerprinted(
        cls,
        content_id: str,
        fingerprint_hash: str,
        similarity_threshold: float,
        user_id: str,
        tenant_id: str
    ) -> "ContentEvent":
        """Crée un événement de contenu fingerprinté"""        return cls(
            type=EventType.CONTENT_FINGERPRINTED.value,
            content_id=content_id,
            user_id=user_id,
            tenant_id=tenant_id,
            priority=EventPriority.HIGH,
            data={
                "action": "fingerprinted",
                "content_id": content_id,
                "fingerprint_hash": fingerprint_hash,
                "similarity_threshold": similarity_threshold
            }
        )


@dataclass
class ProtectionEvent(Event):
    """Événement lié à la protection du contenu"""    
    content_id: str = ""
    protection_id: str = ""
    violation_url: Optional[str] = None
    similarity_score: Optional[float] = None
    platform: Optional[str] = None
    
    def __post_init__(self):
        if not self.type:
            self.type = EventType.PROTECTION_ENABLED.value
        if not self.source:
            self.source = "protection_service"
        if not self.subject:
            self.subject = f"protection/{self.protection_id}"
    
    @classmethod
    def create_violation_detected(
        cls,
        content_id: str,
        violation_url: str,
        similarity_score: float,
        platform: str,
        user_id: str,
        tenant_id: str
    ) -> "ProtectionEvent":
        """Crée un événement de violation détectée"""        return cls(
            type=EventType.PROTECTION_VIOLATION_DETECTED.value,
            content_id=content_id,
            protection_id=str(uuid.uuid4()),
            violation_url=violation_url,
            similarity_score=similarity_score,
            platform=platform,
            user_id=user_id,
            tenant_id=tenant_id,
            priority=EventPriority.CRITICAL,
            data={
                "action": "violation_detected",
                "content_id": content_id,
                "violation_url": violation_url,
                "similarity_score": similarity_score,
                "platform": platform,
                "detected_at": datetime.now(timezone.utc).isoformat()
            }
        )
    
    @classmethod
    def create_takedown_requested(
        cls,
        content_id: str,
        violation_url: str,
        platform: str,
        user_id: str,
        tenant_id: str
    ) -> "ProtectionEvent":
        """Crée un événement de demande de takedown"""        return cls(
            type=EventType.PROTECTION_TAKEDOWN_REQUESTED.value,
            content_id=content_id,
            protection_id=str(uuid.uuid4()),
            violation_url=violation_url,
            platform=platform,
            user_id=user_id,
            tenant_id=tenant_id,
            priority=EventPriority.HIGH,
            data={
                "action": "takedown_requested",
                "content_id": content_id,
                "violation_url": violation_url,
                "platform": platform,
                "requested_at": datetime.now(timezone.utc).isoformat()
            }
        )


@dataclass
class MonetizationEvent(Event):
    """Événement lié à la monétisation"""    
    content_id: str = ""
    revenue_amount: float = 0.0
    currency: str = "EUR"
    platform: str = ""
    payment_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.type:
            self.type = EventType.MONETIZATION_ENABLED.value
        if not self.source:
            self.source = "monetization_service"
        if not self.subject:
            self.subject = f"monetization/{self.content_id}"
    
    @classmethod
    def create_revenue_detected(
        cls,
        content_id: str,
        revenue_amount: float,
        currency: str,
        platform: str,
        user_id: str,
        tenant_id: str
    ) -> "MonetizationEvent":
        """Crée un événement de revenus détectés"""        return cls(
            type=EventType.MONETIZATION_REVENUE_DETECTED.value,
            content_id=content_id,
            revenue_amount=revenue_amount,
            currency=currency,
            platform=platform,
            user_id=user_id,
            tenant_id=tenant_id,
            priority=EventPriority.HIGH,
            data={
                "action": "revenue_detected",
                "content_id": content_id,
                "revenue_amount": revenue_amount,
                "currency": currency,
                "platform": platform,
                "detected_at": datetime.now(timezone.utc).isoformat()
            }
        )
    
    @classmethod
    def create_payment_processed(
        cls,
        content_id: str,
        payment_id: str,
        amount: float,
        currency: str,
        user_id: str,
        tenant_id: str
    ) -> "MonetizationEvent":
        """Crée un événement de paiement traité"""        return cls(
            type=EventType.MONETIZATION_PAYMENT_PROCESSED.value,
            content_id=content_id,
            payment_id=payment_id,
            revenue_amount=amount,
            currency=currency,
            user_id=user_id,
            tenant_id=tenant_id,
            priority=EventPriority.HIGH,
            data={
                "action": "payment_processed",
                "content_id": content_id,
                "payment_id": payment_id,
                "amount": amount,
                "currency": currency,
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
        )


@dataclass
class CollaborationEvent(Event):
    """Événement lié à la collaboration"""    
    project_id: str = ""
    collaborator_id: Optional[str] = None
    invite_id: Optional[str] = None
    matching_score: Optional[float] = None
    
    def __post_init__(self):
        if not self.type:
            self.type = EventType.COLLABORATION_PROJECT_CREATED.value
        if not self.source:
            self.source = "collaboration_service"
        if not self.subject:
            self.subject = f"collaboration/{self.project_id}"
    
    @classmethod
    def create_invite_sent(
        cls,
        project_id: str,
        collaborator_id: str,
        invite_id: str,
        user_id: str,
        tenant_id: str
    ) -> "CollaborationEvent":
        """Crée un événement d'invitation envoyée"""        return cls(
            type=EventType.COLLABORATION_INVITE_SENT.value,
            project_id=project_id,
            collaborator_id=collaborator_id,
            invite_id=invite_id,
            user_id=user_id,
            tenant_id=tenant_id,
            priority=EventPriority.NORMAL,
            data={
                "action": "invite_sent",
                "project_id": project_id,
                "collaborator_id": collaborator_id,
                "invite_id": invite_id,
                "sent_at": datetime.now(timezone.utc).isoformat()
            }
        )
    
    @classmethod
    def create_matching_found(
        cls,
        project_id: str,
        collaborator_id: str,
        matching_score: float,
        user_id: str,
        tenant_id: str
    ) -> "CollaborationEvent":
        """Crée un événement de matching trouvé"""        return cls(
            type=EventType.COLLABORATION_MATCHING_FOUND.value,
            project_id=project_id,
            collaborator_id=collaborator_id,
            matching_score=matching_score,
            user_id=user_id,
            tenant_id=tenant_id,
            priority=EventPriority.HIGH,
            data={
                "action": "matching_found",
                "project_id": project_id,
                "collaborator_id": collaborator_id,
                "matching_score": matching_score,
                "found_at": datetime.now(timezone.utc).isoformat()
            }
        )


@dataclass
class SystemEvent(Event):
    """Événement système"""    
    severity: str = "info"  # info, warning, error, critical
    component: str = ""
    error_code: Optional[str] = None
    
    def __post_init__(self):
        if not self.type:
            self.type = EventType.SYSTEM_ERROR_OCCURRED.value
        if not self.source:
            self.source = "system"
        if not self.subject:
            self.subject = f"system/{self.component}"
    
    @classmethod
    def create_user_registered(
        cls,
        user_id: str,
        tenant_id: str,
        plan: str = "free"
    ) -> "SystemEvent":
        """Crée un événement d'utilisateur enregistré"""        return cls(
            type=EventType.SYSTEM_USER_REGISTERED.value,
            user_id=user_id,
            tenant_id=tenant_id,
            severity="info",
            component="auth_service",
            priority=EventPriority.NORMAL,
            data={
                "action": "user_registered",
                "user_id": user_id,
                "tenant_id": tenant_id,
                "plan": plan,
                "registered_at": datetime.now(timezone.utc).isoformat()
            }
        )
    
    @classmethod
    def create_error_occurred(
        cls,
        component: str,
        error_code: str,
        error_message: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> "SystemEvent":
        """Crée un événement d'erreur système"""        return cls(
            type=EventType.SYSTEM_ERROR_OCCURRED.value,
            user_id=user_id,
            tenant_id=tenant_id,
            severity="error",
            component=component,
            error_code=error_code,
            priority=EventPriority.HIGH,
            data={
                "action": "error_occurred",
                "component": component,
                "error_code": error_code,
                "error_message": error_message,
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
        )


# Helper functions pour création rapide d'événements
def create_content_event(event_type: str, content_id: str, **kwargs) -> ContentEvent:
    """Fonction helper pour créer des événements de contenu"""    return ContentEvent(type=event_type, content_id=content_id, **kwargs)


def create_protection_event(event_type: str, content_id: str, **kwargs) -> ProtectionEvent:
    """Fonction helper pour créer des événements de protection"""    return ProtectionEvent(type=event_type, content_id=content_id, **kwargs)


def create_monetization_event(event_type: str, content_id: str, **kwargs) -> MonetizationEvent:
    """Fonction helper pour créer des événements de monétisation"""    return MonetizationEvent(type=event_type, content_id=content_id, **kwargs)


def create_collaboration_event(event_type: str, project_id: str, **kwargs) -> CollaborationEvent:
    """Fonction helper pour créer des événements de collaboration"""    return CollaborationEvent(type=event_type, project_id=project_id, **kwargs)


def create_system_event(event_type: str, component: str, **kwargs) -> SystemEvent:
    """Fonction helper pour créer des événements système"""    return SystemEvent(type=event_type, component=component, **kwargs)
