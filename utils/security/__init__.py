"""
Security Utilities Module - Enterprise Architecture Level 2
=========================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade security utilities implementing ultra-strict standards:
- AES-256-GCM + RSA-4096 encryption
- Multi-factor authentication
- Comprehensive input validation
- Security scanning automation
- Audit logging with encryption

Compliance: GDPR, SOX, ISO 27001, OWASP, NIST Framework
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .encryption_engine import EncryptionEngine
    from .authentication_utils import AuthenticationUtils
    from .validation_engine import ValidationEngine
    from .security_scanner import SecurityScanner
    from .password_manager import PasswordManager
    from .audit_logger import AuditLogger
    from .threat_detector import ThreatDetector
    from .vulnerability_scanner import VulnerabilityScanner
    from .access_control import AccessControl
    from .session_manager import SessionManager

__all__ = [
    "EncryptionEngine",
    "AuthenticationUtils",
    "ValidationEngine", 
    "SecurityScanner",
    "PasswordManager",
    "AuditLogger",
    "ThreatDetector",
    "VulnerabilityScanner",
    "AccessControl",
    "SessionManager",
    "EncryptionEngineFactory",
    "AuthenticationUtilsFactory",
    "ValidationEngineFactory",
    "SecurityScannerFactory", 
    "PasswordManagerFactory",
    "AuditLoggerFactory",
    "ThreatDetectorFactory",
    "VulnerabilityScannerFactory",
    "AccessControlFactory",
    "SessionManagerFactory"
]

# Lazy loading for enterprise performance
def __getattr__(name: str):
    if name == "EncryptionEngine":
        from .encryption_engine import EncryptionEngine
        return EncryptionEngine
    elif name == "AuthenticationUtils":
        from .authentication_utils import AuthenticationUtils
        return AuthenticationUtils
    elif name == "ValidationEngine":
        from .validation_engine import ValidationEngine
        return ValidationEngine
    elif name == "SecurityScanner":
        from .security_scanner import SecurityScanner
        return SecurityScanner
    elif name == "PasswordManager":
        from .password_manager import PasswordManager
        return PasswordManager
    elif name == "AuditLogger":
        from .audit_logger import AuditLogger
        return AuditLogger
    elif name == "ThreatDetector":
        from .threat_detector import ThreatDetector
        return ThreatDetector
    elif name == "VulnerabilityScanner":
        from .vulnerability_scanner import VulnerabilityScanner
        return VulnerabilityScanner
    elif name == "AccessControl":
        from .access_control import AccessControl
        return AccessControl
    elif name == "SessionManager":
        from .session_manager import SessionManager
        return SessionManager
    elif name == "EncryptionEngineFactory":
        from .encryption_engine import EncryptionEngineFactory
        return EncryptionEngineFactory
    elif name == "AuthenticationUtilsFactory":
        from .authentication_utils import AuthenticationUtilsFactory
        return AuthenticationUtilsFactory
    elif name == "ValidationEngineFactory":
        from .validation_engine import ValidationEngineFactory
        return ValidationEngineFactory
    elif name == "SecurityScannerFactory":
        from .security_scanner import SecurityScannerFactory
        return SecurityScannerFactory
    elif name == "PasswordManagerFactory":
        from .password_manager import PasswordManagerFactory
        return PasswordManagerFactory
    elif name == "AuditLoggerFactory":
        from .audit_logger import AuditLoggerFactory
        return AuditLoggerFactory
    elif name == "ThreatDetectorFactory":
        from .threat_detector import ThreatDetectorFactory
        return ThreatDetectorFactory
    elif name == "VulnerabilityScannerFactory":
        from .vulnerability_scanner import VulnerabilityScannerFactory
        return VulnerabilityScannerFactory
    elif name == "AccessControlFactory":
        from .access_control import AccessControlFactory
        return AccessControlFactory
    elif name == "SessionManagerFactory":
        from .session_manager import SessionManagerFactory
        return SessionManagerFactory
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")