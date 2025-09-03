"""🔧 IP Protection Service Models - Data Structures and Enums
===========================================================

Professional data models and enumerations for the IP Protection Service
providing comprehensive type safety and validation for content protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + ML Engineer + Security Architect + Legal Tech + DevOps + DBA
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

class ContentType(Enum):
    """Types of content that can be protected"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MULTIMEDIA = "multimedia"

class ProtectionLevel(Enum):
    """Levels of content protection"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    MAXIMUM = "maximum"

class ViolationType(Enum):
    """Types of content violations"""
    UNAUTHORIZED_COPY = "unauthorized_copy"
    PARTIAL_COPY = "partial_copy"
    DERIVATIVE_WORK = "derivative_work"
    COMMERCIAL_INFRINGEMENT = "commercial_infringement"
    PLAGIARISM = "plagiarism"
    FAIR_USE_VIOLATION = "fair_use_violation"
    ATTRIBUTION_MISSING = "attribution_missing"
    LICENSING_VIOLATION = "licensing_violation"

class EnforcementType(Enum):
    """Types of enforcement actions"""
    STANDARD = "standard"
    URGENT = "urgent"
    IMMEDIATE = "immediate"
    LEGAL_ACTION = "legal_action"
    CEASE_DESIST = "cease_desist"
    COURT_ORDER = "court_order"

class MonitoringFrequency(Enum):
    """Monitoring frequency options"""
    REAL_TIME = "real_time"
    EVERY_MINUTE = "every_minute"
    EVERY_5_MINUTES = "every_5_minutes"
    EVERY_15_MINUTES = "every_15_minutes"
    EVERY_30_MINUTES = "every_30_minutes"
    HOURLY = "hourly"
    DAILY = "daily"

@dataclass
class ContentAnalysis:
    """Content analysis result"""
    content_id: str
    content_type: ContentType
    features: List[float]
    metadata: Dict[str, Any]
    fingerprint_hash: str
    analysis_timestamp: datetime
    quality_score: float
    uniqueness_score: float

@dataclass
class SimilarityScore:
    """Similarity analysis result"""
    score: float
    algorithm_used: str
    confidence: float
    analysis_details: Dict[str, Any]
    comparison_timestamp: datetime

@dataclass
class EnforcementAction:
    """Enforcement action details"""
    action_id: str
    action_type: EnforcementType
    target_platform: str
    target_url: str
    status: str
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LegalNotice:
    """Legal notice details"""
    notice_id: str
    notice_type: str
    recipient: str
    content: str
    sent_at: datetime
    response_received: bool = False
    response_at: Optional[datetime] = None
    response_content: Optional[str] = None
    legal_status: str = "pending"

@dataclass
class RevenueImpact:
    """Revenue impact analysis"""
    estimated_value: float
    currency: str
    impact_period: str
    protection_score: float
    risk_level: str
    estimated_losses: float
    recovery_potential: float

@dataclass
class ProtectionMetrics:
    """Protection performance metrics"""
    total_content_protected: int
    violations_detected: int
    violations_resolved: int
    takedowns_successful: int
    average_resolution_time: float
    protection_effectiveness: float
    false_positive_rate: float
    revenue_protected: float

# Export all models and enums
__all__ = [
    # Enums
    "ContentType",
    "ProtectionLevel", 
    "ViolationType",
    "EnforcementType",
    "MonitoringFrequency",
    
    # Data classes
    "ContentAnalysis",
    "SimilarityScore",
    "EnforcementAction",
    "LegalNotice",
    "RevenueImpact",
    "ProtectionMetrics"
]