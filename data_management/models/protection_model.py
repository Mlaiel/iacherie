"""🛡️ Protection Models - IA Influencer Agent Platform Enterprise
=============================================================
Module: backend/data_management/models/protection_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
Type: Industrial Protection Data Models - Production-Ready
===========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
from decimal import Decimal
import uuid

class ViolationType(Enum):
    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PRIVACY = "privacy"
    DEFAMATION = "defamation"

class ViolationStatus(Enum):
    DETECTED = "detected"
    VERIFIED = "verified"
    DISPUTED = "disputed"
    RESOLVED = "resolved"

@dataclass
class ProtectionModel:
    protection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    creator_id: str = ""
    tenant_id: str = ""
    protection_level: str = "basic"
    monitoring_active: bool = True
    alert_threshold: float = 0.85
    whitelist_domains: List[str] = field(default_factory=list)
    blacklist_domains: List[str] = field(default_factory=list)
    auto_takedown: bool = False
    legal_notices_sent: int = 0
    successful_takedowns: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "protection_id": self.protection_id,
            "content_id": self.content_id,
            "creator_id": self.creator_id,
            "tenant_id": self.tenant_id,
            "protection_level": self.protection_level,
            "monitoring_active": self.monitoring_active,
            "alert_threshold": self.alert_threshold,
            "whitelist_domains": self.whitelist_domains,
            "blacklist_domains": self.blacklist_domains,
            "auto_takedown": self.auto_takedown,
            "legal_notices_sent": self.legal_notices_sent,
            "successful_takedowns": self.successful_takedowns,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class ViolationModel:
    violation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    protection_id: str = ""
    fingerprint_id: str = ""
    violation_type: ViolationType = ViolationType.COPYRIGHT
    status: ViolationStatus = ViolationStatus.DETECTED
    detected_url: str = ""
    platform: str = ""
    similarity_score: float = 0.0
    evidence_urls: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "protection_id": self.protection_id,
            "fingerprint_id": self.fingerprint_id,
            "violation_type": self.violation_type.value,
            "status": self.status.value,
            "detected_url": self.detected_url,
            "platform": self.platform,
            "similarity_score": self.similarity_score,
            "evidence_urls": self.evidence_urls,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class TakedownModel:
    takedown_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    violation_id: str = ""
    takedown_type: str = "dmca"
    platform: str = ""
    status: str = "sent"
    notice_url: str = ""
    response_received: bool = False
    successful: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "takedown_id": self.takedown_id,
            "violation_id": self.violation_id,
            "takedown_type": self.takedown_type,
            "platform": self.platform,
            "status": self.status,
            "notice_url": self.notice_url,
            "response_received": self.response_received,
            "successful": self.successful,
            "created_at": self.created_at.isoformat()
        }
