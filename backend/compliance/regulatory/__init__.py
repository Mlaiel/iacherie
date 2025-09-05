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
from .dsa_compliance import DSACompliance, DSARiskLevel, ContentModerationObligation
from .netzg_compliance import NetzGCompliance, GermanLaw, ContentRemovalObligation
from .copyright_manager import CopyrightManager, IPRightType, LicenseType
from .international_laws import InternationalLawsManager, JurisdictionType, LegalFramework
from .regulation_engine import RegulationEngine, ComplianceRule, ViolationSeverity

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