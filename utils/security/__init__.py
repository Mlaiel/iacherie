"""
🔒 AINFLUE PLATFORM - SECURITY UTILITIES MODULE
Enterprise-grade security utilities with quantum-safe encryption and advanced threat protection

Author: Fahed Mlaiel (Security Expert + Backend Senior)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Classification: CONFIDENTIAL ENTERPRISE

This module provides ultra-secure utilities following strict enterprise standards:
- AES-256-GCM + RSA-4096 encryption
- Multi-factor authentication support
- Advanced input validation and sanitization
- GDPR/SOX/PCI compliance
- Real-time security scanning
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

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__security_level__ = "QUANTUM-SAFE"
__compliance__ = ["GDPR", "SOX", "PCI", "ISO27001", "OWASP"]