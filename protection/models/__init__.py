"""
Protection Models Package
========================

Central models package for the protection system.
Contains all data models used across protection modules.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .alert_models import *
from .base_models import *
from .security_models import *
from .monitoring_models import *
from .notification_models import *

__all__ = [
    # Alert models
    "AlertRule",
    "AlertEvent", 
    "AlertNotification",
    "AlertConfiguration",
    "AlertResponse",
    "AlertEscalation",
    "AlertMetrics",
    "AlertAudit",
    "ThreatIntelligenceAlert",
    "AlertWorkflow",
    "AlertCorrelation",
    "AlertEnrichment",
    "AlertSuppression",
    "AlertTemplate",
    "AlertBatch",
    "AlertForensics",
    "AlertCompliance",
    
    # Base models
    "BaseModel",
    "TimestampedModel",
    "AuditableModel",
    
    # Security models
    "SecurityEvent",
    "ThreatIndicator",
    "VulnerabilityReport",
    
    # Monitoring models
    "MonitoringSession",
    "MonitoringMetrics",
    
    # Notification models
    "NotificationType",
    "NotificationPriority", 
    "NotificationStatus",
    "DeliveryStatus",
    "NotificationRecipient",
    "NotificationTemplate",
    "NotificationRequest",
    "NotificationResponse",
    "NotificationLog",
    "NotificationHistory",
    "NotificationPreferences",
    "NotificationChannel",
    "NotificationStats",
    "NotificationBatch",
    "NotificationRule",
    "FingerprintResult",
    "SimilarityMatch"
]

# Add missing FingerprintResult class
class FingerprintResult:
    """Result of fingerprinting operation."""
    
    def __init__(self, fingerprint_id=None, hash_value=None, metadata=None):
        self.fingerprint_id = fingerprint_id
        self.hash_value = hash_value
        self.metadata = metadata or {}

# Add missing SimilarityMatch class
class SimilarityMatch:
    """Similarity match result."""
    
    def __init__(self, match_id=None, similarity_score=0.0, metadata=None):
        self.match_id = match_id
        self.similarity_score = similarity_score
        self.metadata = metadata or {}
