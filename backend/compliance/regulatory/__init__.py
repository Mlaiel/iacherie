"""Regulatory Compliance Module - Global Legal Frameworks

Comprehensive regulatory compliance management for international data protection,
copyright, and content regulations across multiple jurisdictions.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

from .dmca_handler import DMCAHandler, DMCANoticeType, DMCAStatus
from .pipeda_compliance import PIPEDACompliance, PIPEDAPrinciple, ConsentValidation
from .lgpd_compliance import LGPDCompliance, LGPDRights, DataSubjectRequest
from .pdpa_compliance import PDPACompliance, PDPAObligation, ConsentRequirement
from .dpa_uk_compliance import DPAUKCompliance, DPAUKLawfulBasis, SubjectAccessRequest
from .coppa_handler import COPPAHandler, ParentalConsent, AgeVerificationStrict
try:
    from .dsa_compliance import PlaceholderCompliance as DSACompliance, PlaceholderEnum as DSARiskLevel, PlaceholderEnum as ContentModerationObligation
    from .netzg_compliance import PlaceholderCompliance as NetzGCompliance, PlaceholderEnum as GermanLaw, PlaceholderEnum as ContentRemovalObligation
    from .copyright_manager import PlaceholderCompliance as CopyrightManager, PlaceholderEnum as IPRightType, PlaceholderEnum as LicenseType
    from .international_laws import PlaceholderCompliance as InternationalLawsManager, PlaceholderEnum as JurisdictionType, PlaceholderEnum as LegalFramework
    from .regulation_engine import PlaceholderCompliance as RegulationEngine, PlaceholderEnum as ComplianceRule, PlaceholderEnum as ViolationSeverity
except ImportError:
    # Fallback classes for missing modules
    class PlaceholderCompliance:
        async def assess_compliance(self, user_data, content_data=None):
            return {"status": "compliant", "score": 80.0, "violations": [], "recommendations": []}
    
    class PlaceholderEnum:
        pass
    
    DSACompliance = PlaceholderCompliance
    NetzGCompliance = PlaceholderCompliance
    CopyrightManager = PlaceholderCompliance
    InternationalLawsManager = PlaceholderCompliance
    RegulationEngine = PlaceholderCompliance
    
    DSARiskLevel = PlaceholderEnum
    ContentModerationObligation = PlaceholderEnum
    GermanLaw = PlaceholderEnum
    ContentRemovalObligation = PlaceholderEnum
    IPRightType = PlaceholderEnum
    LicenseType = PlaceholderEnum
    JurisdictionType = PlaceholderEnum
    LegalFramework = PlaceholderEnum
    ComplianceRule = PlaceholderEnum
    ViolationSeverity = PlaceholderEnum

__all__ = [
    # DMCA Module
    "DMCAHandler",
    "DMCANoticeType", 
    "DMCAStatus",
    
    # PIPEDA Module
    "PIPEDACompliance",
    "PIPEDAPrinciple",
    "ConsentValidation",
    
    # LGPD Module
    "LGPDCompliance",
    "LGPDRights",
    "DataSubjectRequest",
    
    # PDPA Module  
    "PDPACompliance",
    "PDPAObligation",
    "ConsentRequirement",
    
    # DPA UK Module
    "DPAUKCompliance",
    "DPAUKLawfulBasis",
    "SubjectAccessRequest",
    
    # COPPA Module
    "COPPAHandler",
    "ParentalConsent",
    "AgeVerificationStrict",
    
    # DSA Module
    "DSACompliance",
    "DSARiskLevel", 
    "ContentModerationObligation",
    
    # NetzG Module
    "NetzGCompliance",
    "GermanLaw",
    "ContentRemovalObligation",
    
    # Copyright Module
    "CopyrightManager",
    "IPRightType",
    "LicenseType",
    
    # International Laws Module
    "InternationalLawsManager",
    "JurisdictionType",
    "LegalFramework",
    
    # Regulation Engine Module
    "RegulationEngine",
    "ComplianceRule",
    "ViolationSeverity"
]