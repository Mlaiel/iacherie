"""Audio Protection & Copyright Events - Industrial Grade Copyright Protection
=============================================================================

This module handles all events related to audio copyright protection, security,
and digital rights management for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use, modification, or distribution of this code is strictly prohibited.
Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from enum import Enum

from ..core.base_event import BaseEvent


class CopyrightViolationType(Enum):
    """Copyright violation types"""
    UNAUTHORIZED_COPY = "unauthorized_copy"
    PIRACY = "piracy"
    PLAGIARISM = "plagiarism"
    TRADEMARK_INFRINGEMENT = "trademark_infringement"
    LICENSE_VIOLATION = "license_violation"
    FAIR_USE_VIOLATION = "fair_use_violation"


class ProtectionLevel(Enum):
    """Audio protection levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class AudioCopyrightProtectionEvent(BaseEvent):
    """
    Event triggered when copyright protection is applied to audio content.
    
    Handles digital rights management and protection mechanisms.
    """
    user_id: UUID
    file_id: UUID
    protection_id: UUID
    filename: str
    protection_level: str
    protection_methods: List[str]
    watermark_applied: bool
    drm_enabled: bool
    access_restrictions: Dict[str, Any]
    usage_permissions: Dict[str, Any]
    expiration_date: Optional[datetime] = None
    protection_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.protection.copyright_applied",
            data={
                "file_id": str(self.file_id),
                "protection_id": str(self.protection_id),
                "protection_level": self.protection_level,
                "watermark_applied": self.watermark_applied,
                "drm_enabled": self.drm_enabled,
                "protection_methods": self.protection_methods
            }
        )


@dataclass
class AudioRightsVerificationEvent(BaseEvent):
    """
    Event triggered during audio rights verification process.
    
    Validates ownership and usage rights for audio content.
    """
    user_id: UUID
    file_id: UUID
    verification_id: UUID
    filename: str
    verification_status: str  # verified, pending, failed, disputed
    rights_holder: str
    verification_method: str
    evidence_provided: List[Dict[str, Any]]
    verification_duration: float
    confidence_score: float
    rights_database_checked: List[str]
    verification_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.protection.rights_verification",
            data={
                "file_id": str(self.file_id),
                "verification_id": str(self.verification_id),
                "verification_status": self.verification_status,
                "confidence_score": self.confidence_score,
                "rights_holder": self.rights_holder
            }
        )


@dataclass
class AudioPiracyDetectionEvent(BaseEvent):
    """
    Event triggered when potential piracy is detected.
    
    Monitors and detects unauthorized distribution of protected content.
    """
    user_id: UUID
    file_id: UUID
    detection_id: UUID
    filename: str
    piracy_type: str
    detection_method: str
    confidence_level: float
    infringing_sources: List[Dict[str, Any]]
    detection_timestamp: datetime
    evidence_collected: List[Dict[str, Any]]
    automated_response: bool
    response_actions: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.protection.piracy_detected",
            data={
                "file_id": str(self.file_id),
                "detection_id": str(self.detection_id),
                "piracy_type": self.piracy_type,
                "confidence_level": self.confidence_level,
                "sources_count": len(self.infringing_sources)
            }
        )


@dataclass
class AudioLicenseValidationEvent(BaseEvent):
    """
    Event triggered during license validation process.
    
    Validates usage licenses and permissions for audio content.
    """
    user_id: UUID
    file_id: UUID
    license_id: UUID
    filename: str
    license_type: str
    validation_status: str  # valid, expired, invalid, suspended
    license_terms: Dict[str, Any]
    usage_limitations: Dict[str, Any]
    validation_date: datetime
    expiration_date: Optional[datetime] = None
    renewal_required: bool = False
    compliance_check: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.protection.license_validation",
            data={
                "file_id": str(self.file_id),
                "license_id": str(self.license_id),
                "license_type": self.license_type,
                "validation_status": self.validation_status,
                "renewal_required": self.renewal_required
            }
        )


@dataclass
class AudioWatermarkingEvent(BaseEvent):
    """
    Event triggered when audio watermarking is applied or detected.
    
    Handles digital watermarking for content identification and protection.
    """
    user_id: UUID
    file_id: UUID
    watermark_id: UUID
    filename: str
    watermark_type: str  # digital, acoustic, steganographic
    watermark_strength: float
    watermark_data: Dict[str, Any]
    embedding_method: str
    detection_robustness: float
    imperceptibility_score: float
    watermark_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.protection.watermarking",
            data={
                "file_id": str(self.file_id),
                "watermark_id": str(self.watermark_id),
                "watermark_type": self.watermark_type,
                "watermark_strength": self.watermark_strength,
                "imperceptibility_score": self.imperceptibility_score
            }
        )


@dataclass
class AudioCopyrightClaimEvent(BaseEvent):
    """
    Event triggered when a copyright claim is made against audio content.
    
    Handles copyright infringement claims and dispute resolution.
    """
    user_id: UUID
    file_id: UUID
    claim_id: UUID
    filename: str
    claimant_id: UUID
    claim_type: str
    claim_basis: str
    evidence_provided: List[Dict[str, Any]]
    claim_timestamp: datetime
    dispute_status: str  # pending, accepted, rejected, disputed
    resolution_deadline: Optional[datetime] = None
    claim_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.protection.copyright_claim",
            data={
                "file_id": str(self.file_id),
                "claim_id": str(self.claim_id),
                "claimant_id": str(self.claimant_id),
                "claim_type": self.claim_type,
                "dispute_status": self.dispute_status
            }
        )


@dataclass
class AudioDMCARequestEvent(BaseEvent):
    """
    Event triggered for DMCA takedown requests.
    
    Handles Digital Millennium Copyright Act takedown procedures.
    """
    user_id: UUID
    file_id: UUID
    dmca_id: UUID
    filename: str
    requestor_id: UUID
    request_type: str  # takedown, counter_notice
    copyright_work: Dict[str, Any]
    infringing_material: Dict[str, Any]
    contact_information: Dict[str, Any]
    sworn_statement: str
    request_timestamp: datetime
    response_deadline: datetime
    status: str  # received, processing, complied, disputed
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.protection.dmca_request",
            data={
                "file_id": str(self.file_id),
                "dmca_id": str(self.dmca_id),
                "requestor_id": str(self.requestor_id),
                "request_type": self.request_type,
                "status": self.status
            }
        )


@dataclass
class AudioRightsTransferEvent(BaseEvent):
    """
    Event triggered when audio rights are transferred between parties.
    
    Manages ownership transfers and rights assignments.
    """
    user_id: UUID
    file_id: UUID
    transfer_id: UUID
    filename: str
    from_user_id: UUID
    to_user_id: UUID
    rights_transferred: List[str]
    transfer_type: str  # sale, license, assignment, inheritance
    transfer_terms: Dict[str, Any]
    transfer_date: datetime
    effective_date: datetime
    compensation: Optional[Dict[str, Any]] = None
    legal_documentation: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.protection.rights_transfer",
            data={
                "file_id": str(self.file_id),
                "transfer_id": str(self.transfer_id),
                "from_user_id": str(self.from_user_id),
                "to_user_id": str(self.to_user_id),
                "transfer_type": self.transfer_type,
                "rights_count": len(self.rights_transferred)
            }
        )


@dataclass
class AudioUsageAuthorizationEvent(BaseEvent):
    """
    Event triggered when usage authorization is granted or revoked.
    
    Manages authorized usage permissions for audio content.
    """
    user_id: UUID
    file_id: UUID
    authorization_id: UUID
    filename: str
    authorized_user_id: UUID
    authorization_type: str  # view, stream, download, remix, commercial
    permissions_granted: List[str]
    authorization_scope: Dict[str, Any]
    grant_date: datetime
    expiration_date: Optional[datetime] = None
    usage_limitations: Dict[str, Any] = field(default_factory=dict)
    revoked: bool = False
    revocation_reason: Optional[str] = None
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.protection.usage_authorization",
            data={
                "file_id": str(self.file_id),
                "authorization_id": str(self.authorization_id),
                "authorized_user_id": str(self.authorized_user_id),
                "authorization_type": self.authorization_type,
                "revoked": self.revoked,
                "permissions_count": len(self.permissions_granted)
            }
        )


@dataclass
class AudioCopyrightViolationReportedEvent(BaseEvent):
    """
    Event triggered when a copyright violation is reported.
    
    Handles user-reported copyright infringement incidents.
    """
    user_id: UUID
    file_id: UUID
    report_id: UUID
    filename: str
    reporter_id: UUID
    violation_type: str
    reported_content: Dict[str, Any]
    evidence_submitted: List[Dict[str, Any]]
    report_timestamp: datetime
    severity_level: str  # low, medium, high, critical
    automated_analysis: Dict[str, Any]
    investigation_status: str  # pending, investigating, resolved, dismissed
    resolution_actions: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        super().__init__(
            event_type="audio.protection.violation_reported",
            data={
                "file_id": str(self.file_id),
                "report_id": str(self.report_id),
                "reporter_id": str(self.reporter_id),
                "violation_type": self.violation_type,
                "severity_level": self.severity_level,
                "investigation_status": self.investigation_status
            }
        )