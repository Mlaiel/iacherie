"""
Legal Module - Enterprise Legal Compliance Framework
=======================================================

Comprehensive legal compliance system providing automated legal protection,
copyright enforcement, data protection, contract management, and regulatory compliance.

This module integrates with the backend compliance infrastructure to provide
a complete legal framework for the IA Influencer Agent platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

# Import backend compliance systems for integration
try:
    from backend.compliance import (
        LegalFrameworkEngine, GDPRCompliance, CCPACompliance,
        ContentModerationCompliance, FinancialCompliance,
        CreatorCompliance, AccessibilityCompliance,
        ComplianceOrchestrator, RegulatoryComplianceHub
    )
except ImportError:
    # Fallback imports for development environment
    pass

# Core legal framework classes
from .core import (
    LegalComplianceFramework,
    CopyrightProtectionEngine,
    DataProtectionManager,
    ContractManagementSystem,
    LegalEnforcementEngine
)

# Copyright and IP protection
from .copyright import (
    CopyrightRegistrationManager,
    DMCANoticeGenerator,
    CopyrightInfringementDetector,
    IntellectualPropertyProtection,
    InternationalCopyrightCompliance,
    CopyrightEnforcementEngine,
    CopyrightRenewalManager,
    CopyrightLicensingFramework,
    CopyrightAuditTrail,
    CopyrightDisputeResolver,
    CopyrightComplianceReporter,
    PatentComplianceMonitor,
    TradeSecretProtection,
    IPViolationDetector,
    IPLegalDocumentGenerator,
    IPEnforcementOrchestrator,
    IPComplianceValidator,
    IPLegalAnalytics,
    IPInternationalFramework
)

# Data protection and privacy
from .privacy import (
    GDPRComplianceManager,
    PrivacyPolicyManager,
    ConsentManagementSystem,
    DataMinimizationEngine,
    RightToErasureProcessor,
    DataPortabilityManager,
    ConsentWithdrawalProcessor,
    DataProcessingLegalBasis,
    PrivacyImpactAssessment,
    CCPAComplianceEngine,
    LGPDComplianceFramework,
    PIPEDAComplianceSystem,
    PDPAComplianceEngine,
    COPPAChildProtection,
    PrivacyComplianceReporter
)

# Content regulation and safety
from .content_regulation import (
    ContentModerationLegalFramework,
    PlatformSafetyCompliance,
    ContentLiabilityAssessment
)

# Contract and licensing
from .contracts import (
    LegalContractGenerator,
    DigitalSignatureManager,
    ContractComplianceMonitor,
    AudioContractSpecialist,
    ContractType,
    ContractStatus,
    EnterpriseContract
)

# Financial and regulatory compliance
from .financial import (
    AntiMoneyLaunderingCompliance,
    KYCProcessor,
    SanctionsScreener,
    MLFinancialRiskAnalyzer,
    AudioFinancialSpecialist,
    RegulatoryReporter
)

# International compliance
from .international import (
    InternationalLegalCompliance,
    CrossBorderOperationOrchestrator,
    InternationalTreatyCompliance,
    GlobalLegalUpdateMonitor,
    get_supported_jurisdictions
)

# Integration and orchestration
from .integration import (
    LegalBackendBridge,
    assess_comprehensive_legal_compliance,
    unified_content_protection
)

__all__ = [
    # Core framework
    "LegalComplianceFramework",
    "CopyrightProtectionEngine", 
    "DataProtectionManager",
    "ContractManagementSystem",
    "LegalEnforcementEngine",
    
    # Copyright & IP
    "CopyrightRegistrationManager",
    "DMCANoticeGenerator", 
    "CopyrightInfringementDetector",
    "IntellectualPropertyProtection",
    
    # Privacy & Data Protection
    "GDPRComplianceManager",
    "PrivacyPolicyManager",
    "ConsentManagementSystem", 
    "DataMinimizationEngine",
    
    # Content Regulation
    "ContentModerationLegalFramework",
    "PlatformSafetyCompliance",
    "ContentLiabilityAssessment",
    
    # Contracts & Licensing
    "LegalContractGenerator",
    "DigitalSignatureLegal",
    "LicensingAgreementEngine",
    "ContractEnforcementEngine",
    
    # Financial Compliance
    "AntiMoneyLaunderingCompliance",
    "KnowYourCustomerLegal", 
    "TaxComplianceLegal",
    "FinancialAuditLegal",
    
    # International Compliance
    "InternationalLegalCompliance",
    "CrossBorderLegalFramework",
    "LegalJurisdictionEngine",
    
    # Enforcement & Disputes
    "LegalEnforcementOrchestrator",
    "DisputeResolutionFramework",
    "LegalNotificationSystem",
    
    # Integration & Orchestration
    "LegalBackendBridge",
    "assess_comprehensive_legal_compliance",
    "unified_content_protection"
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"

# Logging setup
import logging
logger = logging.getLogger(__name__)
logger.info("🏛️ Legal Module loaded - Enterprise Legal Compliance Framework")
logger.info("⚖️ Copyright protection, data privacy, contract management enabled")
logger.info("🛡️ Multi-jurisdiction legal compliance ready")
logger.info("⚠️ Protected by copyright - Unauthorized use prohibited")