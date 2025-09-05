"""Privacy Management Module - Advanced Privacy Controls

Comprehensive privacy management framework with consent management,
data minimization, anonymization, and privacy-by-design implementation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

from .consent_manager import ConsentManager, ConsentType, ConsentStatus
from .data_minimization import DataMinimizer, MinimizationLevel, DataNecessity
from .anonymization_engine import AnonymizationEngine, AnonymizationType, RiskLevel
from .retention_policy import RetentionPolicyManager, RetentionCategory, DisposalMethod
from .data_portability import DataPortabilityManager, PortabilityFormat, ExportStatus
from .right_to_erasure import ErasureManager, ErasureReason, ErasureStatus
from .privacy_impact_assessment import PIAManager, PIARisk, PIARecommendation
from .data_protection_officer import DPOManager, DPOFunction, DPOReport
from .breach_notification import BreachNotificationManager, BreachSeverity, NotificationStatus
from .cross_border_transfer import TransferManager, TransferMechanism, AdequacyLevel
from .privacy_by_design import PrivacyByDesignManager, DesignPrinciple, ImplementationLevel

__all__ = [
    # Consent Management
    "ConsentManager",
    "ConsentType",
    "ConsentStatus",
    
    # Data Minimization
    "DataMinimizer",
    "MinimizationLevel",
    "DataNecessity",
    
    # Anonymization Engine
    "AnonymizationEngine",
    "AnonymizationType", 
    "RiskLevel",
    
    # Retention Policy
    "RetentionPolicyManager",
    "RetentionCategory",
    "DisposalMethod",
    
    # Data Portability
    "DataPortabilityManager",
    "PortabilityFormat",
    "ExportStatus",
    
    # Right to Erasure
    "ErasureManager",
    "ErasureReason",
    "ErasureStatus",
    
    # Privacy Impact Assessment
    "PIAManager",
    "PIARisk",
    "PIARecommendation",
    
    # Data Protection Officer
    "DPOManager",
    "DPOFunction",
    "DPOReport",
    
    # Breach Notification
    "BreachNotificationManager",
    "BreachSeverity",
    "NotificationStatus",
    
    # Cross Border Transfer
    "TransferManager",
    "TransferMechanism",
    "AdequacyLevel",
    
    # Privacy by Design
    "PrivacyByDesignManager",
    "DesignPrinciple",
    "ImplementationLevel"
]