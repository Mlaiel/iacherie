"""
Security Module for Ainflue Distribution Platform

This module provides comprehensive security management for content distribution,
including API security, credential management, access control, and threat detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .api_security_manager import (
    APISecurityManager,
    SecurityPolicy,
    SecurityIncident,
    ThreatLevel
)

from .credential_vault import (
    CredentialVault,
    SecureCredential,
    CredentialType,
    EncryptionLevel
)

from .access_controller import (
    AccessController,
    AccessPolicy,
    Permission,
    AccessDecision
)

from .audit_logger import (
    AuditLogger,
    AuditEvent,
    AuditLevel,
    AuditReport
)

from .threat_detector import (
    ThreatDetector,
    ThreatAnalysis,
    ThreatPattern,
    SecurityAlert
)

__all__ = [
    # API Security
    'APISecurityManager',
    'SecurityPolicy',
    'SecurityIncident',
    'ThreatLevel',
    
    # Credential Management
    'CredentialVault',
    'SecureCredential',
    'CredentialType',
    'EncryptionLevel',
    
    # Access Control
    'AccessController',
    'AccessPolicy',
    'Permission',
    'AccessDecision',
    
    # Audit Logging
    'AuditLogger',
    'AuditEvent',
    'AuditLevel',
    'AuditReport',
    
    # Threat Detection
    'ThreatDetector',
    'ThreatAnalysis',
    'ThreatPattern',
    'SecurityAlert'
]

__version__ = "1.0.0"