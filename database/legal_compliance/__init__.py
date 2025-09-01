"""Legal Compliance Database Module - IA Influencer Agent + Content Protection Platform

🚨 INTELLECTUAL PROPERTY WARNING
(c) 2025 Fahed Mlaiel. ALL RIGHTS RESERVED.
Email: mlaiel@live.de

STRICT WARNING: This software, concept and all associated code are the exclusive 
intellectual property of Fahed Mlaiel. Any unauthorized use, copying, distribution,
modification or theft of this code, concept or idea without explicit written 
permission from Fahed Mlaiel is STRICTLY PROHIBITED and will result in immediate 
legal action under German and International Copyright Law.

Comprehensive legal compliance management for multi-format content creators including
musicians, bloggers, photographers, influencers, and comedians.

Business Logic Flow:
User Upload → AI Protection → Compliance Validation → Copyright Registration → 
Surveillance Activation → Collaboration Licensing → Revenue Distribution → Multi-Platform Distribution

Expert Team:
- Lead Dev IA + Backend Senior - Enterprise AI Architecture
- ML Engineer - Advanced Machine Learning Systems  
- DBA + Security Specialist - Database Security & Compliance
- Legal Compliance Expert - Multi-jurisdictions Law Expertise
- Microservices Architect - Scalable System Design
- Audio Processing Specialist - Advanced Audio Analytics
- DevOps Engineer - Production Infrastructure
- IA Prompt Engineer - AI Integration & Optimization
"""

from typing import List, Dict, Any, Optional
import logging

# Core orchestration
from .index import (
    LegalComplianceOrchestrator,
    ContentProcessingRequest,
    ContentProcessingResult
)

# Compliance management
from .compliance_manager import (
    ComplianceManager,
    ComplianceFramework,
    CompliancePriority,
    ContentType,
    CreatorType,
    CompliancePolicy,
    ComplianceViolation,
    ComplianceReport
)

# Copyright management
from .copyright_management import (
    CopyrightManager,
    CopyrightStatus,
    RightsType,
    CopyrightRecord,
    RoyaltyDistribution,
    ContentUsageRecord,
    LicenseAgreement
)

# Collaboration licensing
from .collaboration_licensing import (
    CollaborationLicensingManager,
    CollaborationType,
    LicenseScope,
    RevenueModel,
    CollaborationStatus,
    CollaborationProposal,
    CollaborationAgreement,
    CollaborationRevenue,
    CreatorProfile
)

# Content surveillance
from .surveillance_system import (
    ContentSurveillanceManager,
    SurveillancePlatform,
    InfringementType,
    ConfidenceLevel,
    InfringementStatus,
    EnforcementAction,
    SurveillanceTarget,
    InfringementDetection,
    SurveillanceReport
)

# Data protection and privacy
from .data_protection import (
    DataProtectionManager,
    DataClassification,
    ProtectionMethod,
    ProcessingPurpose,
    DataSubjectRight,
    DataProcessingRecord,
    ProtectionConfiguration,
    DataInventoryItem
)

# GDPR compliance
from .gdpr_handler import (
    GDPRHandler,
    ConsentStatus,
    DataCategory,
    ProcessingPurpose as GDPRProcessingPurpose,
    DataSubjectRight as GDPRDataSubjectRight,
    ConsentRecord,
    DataSubjectRequest
)

# Consent management
from .consent_manager import (
    ConsentManager,
    ConsentType,
    ConsentStatus as ConsentManagerStatus,
    ConsentMethod,
    DataCategory as ConsentDataCategory,
    ConsentPurpose,
    ConsentRecord as ConsentManagerRecord,
    ConsentWithdrawal
)

# DMCA processing
from .dmca_processor import (
    DMCAProcessor,
    DMCANoticeStatus,
    NoticeType,
    InfringementType as DMCAInfringementType,
    DMCANotice,
    CounterNotification
)

# Licensing engine
from .licensing_engine import (
    LicensingEngine,
    LicenseType,
    LicenseStatus,
    UsageType,
    LicenseScope as LicenseEngineScope,
    LicenseTerms,
    PricingModel,
    License,
    LicenseUsage
)

# Regulatory monitoring
from .regulatory_monitor import (
    RegulatoryMonitor,
    Jurisdiction,
    RegulatoryFramework,
    ComplianceRequirement,
    RegulatoryRule,
    ComplianceAlert
)

# Audit logging
from .audit_logger import (
    AuditLogger,
    AuditEventType,
    AuditLevel,
    DataSensitivity,
    AuditSession,
    AuditEvent
)

logger = logging.getLogger(__name__)

# Module version and metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__description__ = "Comprehensive legal compliance system for IA Influencer Agent platform"

# Modules exportés
__all__ = [
    # Core managers
    "ComplianceManager",
    "CopyrightManager",
    "GDPRHandler",
    "DMCAProcessor",
    "LicensingEngine",
    "RegulatoryMonitor",
    "AuditLogger",
    "ConsentManager",
    "DataProtectionManager",
    "JurisdictionHandler",
    "LegalRepository",
    "LegalNotificationEngine",
    # Legacy compatibility
    "legal_documents",
    "compliance_rules",
    "regulatory_tracking",
    "gdpr_management",
    "legal_proceedings"
]

def get_module_info() -> Dict[str, Any]:
    """
    Returns comprehensive information about the Legal Compliance module.
    
    Returns:
        Dict[str, Any]: Module information including capabilities and compliance features
    """
    return {
        "name": "Legal Compliance Database",
        "version": __version__,
        "author": "Fahed Mlaiel",
        "email": "mlaiel@live.de",
        "description": "Comprehensive legal compliance management for content protection platform",
        "features": [
            "Copyright management and verification",
            "GDPR compliance and data protection",
            "DMCA automated processing",
            "Multi-jurisdictional regulatory compliance",
            "License automation and enforcement",
            "Legal audit trail maintenance",
            "Rights attribution and royalty tracking"
        ],
        "modules": __all__,
        "compliance_standards": [
            "GDPR",
            "CCPA", 
            "DMCA",
            "PIPEDA",
            "LGPD",
            "Copyright Directive EU"
        ]
    }
