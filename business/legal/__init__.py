"""Legal and Compliance Management Module

Comprehensive legal framework implementation for GDPR compliance,
data subject rights, legal holds, breach notifications, and more.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
"""

from .consent_management import ConsentManager, ConsentType, ConsentStatus
from .data_subject_rights import DataSubjectRightsManager, DataSubjectRight
from .legal_hold import LegalHoldManager, LegalHold
from .breach_notification import BreachNotificationManager, DataBreach
from .vendor_risk import VendorRiskManager, VendorAssessment
from .privacy_by_design import PrivacyByDesignFramework, PrivacyImpactLevel

__all__ = [
    'ConsentManager', 'ConsentType', 'ConsentStatus',
    'DataSubjectRightsManager', 'DataSubjectRight',
    'LegalHoldManager', 'LegalHold',
    'BreachNotificationManager', 'DataBreach',
    'VendorRiskManager', 'VendorAssessment',
    'PrivacyByDesignFramework', 'PrivacyImpactLevel'
]