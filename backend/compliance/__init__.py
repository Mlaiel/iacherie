"""Backend Compliance Module - Conformité Globale

Consolidated compliance services for global regulatory requirements including
GDPR, CCPA, content moderation, and age verification.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

from .gdpr import GDPRCompliance, GDPRRequestType, ConsentPurpose, ProcessingLawfulBasis
from .ccpa import CCPACompliance, ConsumerRight, PrivacyRequestStatus
from .content_moderation import ContentModerationCompliance, ModerationAction, ViolationType, ContentType
from .age_verification import AgeVerificationCompliance, VerificationMethod, VerificationStatus, AgeCategory

__all__ = [
    # GDPR Module
    "GDPRCompliance",
    "GDPRRequestType", 
    "ConsentPurpose",
    "ProcessingLawfulBasis",
    
    # CCPA Module
    "CCPACompliance",
    "ConsumerRight",
    "PrivacyRequestStatus",
    
    # Content Moderation Module
    "ContentModerationCompliance",
    "ModerationAction",
    "ViolationType",
    "ContentType",
    
    # Age Verification Module
    "AgeVerificationCompliance",
    "VerificationMethod",
    "VerificationStatus",
    "AgeCategory"
]