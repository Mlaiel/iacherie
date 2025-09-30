#!/usr/bin/env python3
"""
Platform Core Security Module - Enterprise Security Suite
Comprehensive security components for creator economy platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
==========================================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code of Fahed Mlaiel
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided

This module provides the complete enterprise security suite including:
- Authentication Manager: Multi-factor authentication with biometrics
- Authorization Engine: Granular RBAC/ABAC access control
- Encryption Service: Multi-algorithm encryption with HSM support
- Threat Detection Engine: ML-powered security intelligence
- Security Policy Engine: Centralized policy management
"""

# Core security components
from .authentication_manager import (
    AuthenticationManager,
    AuthenticationType,
    AuthenticationStatus,
    BiometricType,
    RiskLevel,
    BiometricData,
    BehavioralPattern,
    AuthenticationSession,
    AuthenticationAttempt,
    create_authentication_manager
)

from .authorization_engine import (
    AuthorizationEngine,
    PermissionType,
    ResourceType,
    PolicyEffect,
    AuthorizationContext,
    Permission,
    Role,
    UserRoleAssignment,
    AuthorizationPolicy,
    AuthorizationRequest,
    AuthorizationDecision,
    create_authorization_engine
)

from .encryption_service import (
    EncryptionService,
    EncryptionAlgorithm,
    KeyType,
    KeyStatus,
    WatermarkType,
    EncryptionKey,
    EncryptionOperation,
    WatermarkData,
    EncryptedData,
    create_encryption_service
)

from .threat_detection_engine import (
    ThreatDetectionEngine,
    ThreatLevel,
    ThreatType,
    ThreatStatus,
    AlertSeverity,
    BehavioralBaseline,
    ThreatIntelligence,
    SecurityEvent,
    ThreatDetection,
    SecurityAlert,
    create_threat_detection_engine
)

from .security_policy_engine import (
    SecurityPolicyEngine,
    PolicyType,
    PolicyScope,
    EnforcementAction,
    ComplianceStandard,
    SecurityPolicy,
    PolicyRule,
    PolicyViolation,
    ComplianceCheck,
    create_security_policy_engine
)

# Module version and metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Enterprise Commercial License"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

# Export all public components
__all__ = [
    # Authentication Manager
    "AuthenticationManager",
    "AuthenticationType",
    "AuthenticationStatus", 
    "BiometricType",
    "RiskLevel",
    "BiometricData",
    "BehavioralPattern",
    "AuthenticationSession",
    "AuthenticationAttempt",
    "create_authentication_manager",
    
    # Authorization Engine
    "AuthorizationEngine",
    "PermissionType",
    "ResourceType",
    "PolicyEffect",
    "AuthorizationContext",
    "Permission",
    "Role",
    "UserRoleAssignment",
    "AuthorizationPolicy",
    "AuthorizationRequest",
    "AuthorizationDecision",
    "create_authorization_engine",
    
    # Encryption Service
    "EncryptionService",
    "EncryptionAlgorithm",
    "KeyType",
    "KeyStatus",
    "WatermarkType",
    "EncryptionKey",
    "EncryptionOperation",
    "WatermarkData",
    "EncryptedData",
    "create_encryption_service",
    
    # Threat Detection Engine
    "ThreatDetectionEngine",
    "ThreatLevel",
    "ThreatType", 
    "ThreatStatus",
    "AlertSeverity",
    "BehavioralBaseline",
    "ThreatIntelligence",
    "SecurityEvent",
    "ThreatDetection",
    "SecurityAlert",
    "create_threat_detection_engine",
    
    # Security Policy Engine
    "SecurityPolicyEngine",
    "PolicyType",
    "PolicyScope",
    "EnforcementAction",
    "ComplianceStandard",
    "SecurityPolicy",
    "PolicyRule",
    "PolicyViolation",
    "ComplianceCheck",
    "create_security_policy_engine",
]


def get_security_module_info():
    """Get security module information"""
    return {
        "name": "Platform Core Security Module",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "copyright": __copyright__,
        "components": {
            "authentication_manager": "Multi-factor authentication with biometric support",
            "authorization_engine": "Granular RBAC/ABAC access control system",
            "encryption_service": "Multi-algorithm encryption with HSM integration",
            "threat_detection_engine": "ML-powered real-time threat detection",
            "security_policy_engine": "Centralized security policy management"
        },
        "features": [
            "Enterprise-grade multi-factor authentication",
            "Biometric authentication support", 
            "Hierarchical role-based access control",
            "Attribute-based access control (ABAC)",
            "AES-256/RSA-4096/ECC encryption algorithms",
            "Digital watermarking and DRM protection",
            "ML-powered behavioral anomaly detection",
            "Real-time threat intelligence correlation",
            "Automated security policy enforcement",
            "GDPR/SOC2/ISO27001 compliance monitoring"
        ],
        "creator_economy_features": [
            "Content creator IP protection",
            "Digital rights management (DRM)",
            "Forensic watermarking",
            "Content theft detection",
            "Creator collaboration security",
            "Revenue protection mechanisms"
        ]
    }