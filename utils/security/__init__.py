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

__all__ = [
    "EncryptionEngine",
    "AuthenticationUtils",
    "ValidationEngine", 
    "SecurityScanner",
    "PasswordManager",
    "AuditLogger",
    "EncryptionEngineFactory",
    "AuthenticationUtilsFactory",
    "ValidationEngineFactory",
    "SecurityScannerFactory", 
    "PasswordManagerFactory",
    "AuditLoggerFactory"
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
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")