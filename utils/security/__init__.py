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
    "AuditLogger"
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
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")