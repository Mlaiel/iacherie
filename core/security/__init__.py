"""Ainflue Core Security - Enterprise Security & Protection
=======================================================

Core security providing authentication, authorization, protection systems,
copyright fingerprinting, rights management, violation detection,
encryption, threat detection, compliance, and zero-trust security.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any

# Security core imports (existing files to be moved here)
try:
    from .auth import AuthCore
except ImportError:
    AuthCore = None

try:
    from .security import SecurityCore
except ImportError:
    SecurityCore = None

try:
    from .protection_business_core import ProtectionBusinessCore
except ImportError:
    ProtectionBusinessCore = None

try:
    from .copyright_fingerprinting_core import CopyrightFingerprintingCore
except ImportError:
    CopyrightFingerprintingCore = None

try:
    from .rights_management_core import RightsManagementCore
except ImportError:
    RightsManagementCore = None

try:
    from .violation_detection_core import ViolationDetectionCore
except ImportError:
    ViolationDetectionCore = None

# New security core files (to be created)
try:
    from .encryption_core import EncryptionCore
except ImportError:
    EncryptionCore = None

try:
    from .oauth_core import OAuthCore
except ImportError:
    OAuthCore = None

try:
    from .jwt_manager_core import JWTManagerCore
except ImportError:
    JWTManagerCore = None

try:
    from .session_management_core import SessionManagementCore
except ImportError:
    SessionManagementCore = None

try:
    from .role_based_access_core import RoleBasedAccessCore
except ImportError:
    RoleBasedAccessCore = None

try:
    from .audit_trail_core import AuditTrailCore
except ImportError:
    AuditTrailCore = None

try:
    from .threat_detection_core import ThreatDetectionCore
except ImportError:
    ThreatDetectionCore = None

try:
    from .vulnerability_scanner_core import VulnerabilityScannerCore
except ImportError:
    VulnerabilityScannerCore = None

try:
    from .penetration_testing_core import PenetrationTestingCore
except ImportError:
    PenetrationTestingCore = None

try:
    from .compliance_checker_core import ComplianceCheckerCore
except ImportError:
    ComplianceCheckerCore = None

try:
    from .data_loss_prevention_core import DataLossPreventionCore
except ImportError:
    DataLossPreventionCore = None

try:
    from .privacy_protection_core import PrivacyProtectionCore
except ImportError:
    PrivacyProtectionCore = None

try:
    from .zero_trust_core import ZeroTrustCore
except ImportError:
    ZeroTrustCore = None

__all__ = [
    "AuthCore", "SecurityCore", "ProtectionBusinessCore", "CopyrightFingerprintingCore",
    "RightsManagementCore", "ViolationDetectionCore", "EncryptionCore", "OAuthCore",
    "JWTManagerCore", "SessionManagementCore", "RoleBasedAccessCore", "AuditTrailCore",
    "ThreatDetectionCore", "VulnerabilityScannerCore", "PenetrationTestingCore",
    "ComplianceCheckerCore", "DataLossPreventionCore", "PrivacyProtectionCore",
    "ZeroTrustCore"
]