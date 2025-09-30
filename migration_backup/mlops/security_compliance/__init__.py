"""
Security & Compliance Module for MLOps Enterprise
Comprehensive security and compliance framework for ML models and data

Components:
- Model Security Management
- Adversarial Defense Systems
- Data Encryption & Privacy
- Compliance Framework (GDPR, Industry Standards)
- Audit Trail Management
- Security Scanning & Vulnerability Assessment
- Privacy-Preserving ML Techniques
- Threat Modeling for ML Systems

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .model_security_manager import ModelSecurityManager
from .adversarial_defense import AdversarialDefenseEngine
from .data_encryption_manager import DataEncryptionManager
from .compliance_framework import ComplianceFramework
from .audit_trail_manager import AuditTrailManager
from .security_scanning_suite import SecurityScanningSuite
from .privacy_preserving_ml import PrivacyPreservingML
from .secure_communication import SecureCommunication
from .security_analytics import SecurityAnalytics
from .threat_modeling_engine import ThreatModelingEngine
from .identity_access_manager import IdentityAccessManager
from .security_compliance_reporter import SecurityComplianceReporter

__version__ = "1.0.0"
__all__ = [
    "ModelSecurityManager",
    "AdversarialDefenseEngine", 
    "DataEncryptionManager",
    "ComplianceFramework",
    "AuditTrailManager",
    "SecurityScanningSuite",
    "PrivacyPreservingML",
    "SecureCommunication",
    "SecurityAnalytics",
    "ThreatModelingEngine",
    "IdentityAccessManager",
    "SecurityComplianceReporter"
]