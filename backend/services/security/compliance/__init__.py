"""Compliance Module - Conformité GDPR et légale

Consolidated compliance services for GDPR, DMCA and legal validation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

from .gdpr_manager import GDPRComplianceManager, GDPRRequestType, ConsentPurpose, ProcessingLawfulBasis
from .dmca_handler import DMCAHandler, NoticeType, NoticeStatus
from .legal_validator import LegalValidator, ValidationLevel, ComplianceStatus

__all__ = [
    "GDPRComplianceManager",
    "DMCAHandler", 
    "LegalValidator",
    "GDPRRequestType",
    "ConsentPurpose",
    "ProcessingLawfulBasis",
    "NoticeType",
    "NoticeStatus",
    "ValidationLevel",
    "ComplianceStatus"
]