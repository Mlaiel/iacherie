"""
Security Models - Protection System
==================================

Security-specific data models for the protection system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from .base_models import AuditableModel

class ThreatLevel(Enum):
    """Threat level enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

class SecurityEventType(Enum):
    """Security event type enumeration"""
    INTRUSION_ATTEMPT = "intrusion_attempt"
    MALWARE_DETECTED = "malware_detected"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

@dataclass
class SecurityEvent(AuditableModel):
    """Security event model"""
    event_type: SecurityEventType = SecurityEventType.SUSPICIOUS_ACTIVITY
    threat_level: ThreatLevel = ThreatLevel.MEDIUM
    source_ip: str = ""
    target_ip: str = ""
    user_agent: str = ""
    description: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)
    mitigated: bool = False
    mitigation_actions: List[str] = field(default_factory=list)

@dataclass
class ThreatIndicator(AuditableModel):
    """Threat indicator model"""
    indicator_type: str = ""
    indicator_value: str = ""
    threat_level: ThreatLevel = ThreatLevel.MEDIUM
    confidence_score: float = 0.0
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    tags: List[str] = field(default_factory=list)
    active: bool = True

@dataclass
class VulnerabilityReport(AuditableModel):
    """Vulnerability report model"""
    vulnerability_id: str = ""
    title: str = ""
    description: str = ""
    severity: str = "medium"
    cvss_score: float = 0.0
    affected_systems: List[str] = field(default_factory=list)
    remediation_steps: List[str] = field(default_factory=list)
    status: str = "open"
    discovered_date: datetime = field(default_factory=datetime.utcnow)
    patched_date: Optional[datetime] = None

# Export all models
__all__ = [
    "ThreatLevel",
    "SecurityEventType",
    "SecurityEvent",
    "ThreatIndicator",
    "VulnerabilityReport"
]
