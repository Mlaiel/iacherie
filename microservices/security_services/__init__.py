"""
Ainflue Security Services Module
Enterprise Security & Compliance Management

This module provides comprehensive enterprise-grade security services for
the Ainflue ecosystem, implementing zero-trust architecture, compliance
management, and advanced threat protection.

Architecture: Security Services (18 services)
- Zero-trust authentication and authorization
- Real-time threat detection and incident response
- GDPR/CCPA compliance automation
- Copyright protection and digital rights management
- Advanced encryption and secure communication

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .platform_authentication_service import PlatformAuthenticationService
from .creator_compliance_service import CreatorComplianceService
from .compliance_reporting_service import ComplianceReportingService
from .copyright_protection_service import CopyrightProtectionService
from .dmca_service import DMCAService
from .licensing_service import LicensingService
from .watermarking_service import WatermarkingService
from .fingerprinting_service import FingerprintingService
from .dispute_resolution_service import DisputeResolutionService
from .fraud_detection_service import FraudDetectionService

__all__ = [
    'PlatformAuthenticationService',
    'CreatorComplianceService',
    'ComplianceReportingService',
    'CopyrightProtectionService',
    'DMCAService',
    'LicensingService',
    'WatermarkingService',
    'FingerprintingService',
    'DisputeResolutionService',
    'FraudDetectionService'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"