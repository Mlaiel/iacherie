# Ainflue Infrastructure Module
# =============================
# 
# Enterprise-grade infrastructure management for Ainflue platform
# Supports multi-cloud deployment and enterprise security
#
# Author: Fahed Mlaiel <mlaiel@live.de>
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
#
# ⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️

"""
Security Infrastructure Module

Enterprise security infrastructure for Ainflue platform.
Provides comprehensive security, compliance, and threat protection capabilities.
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary"

# Security infrastructure components
from .certificate_manager import CertificateManager
from .network_security_policies import NetworkSecurityPolicies
from .rbac_configuration import RBACConfiguration
from .encryption_management import EncryptionManagement
from .compliance_monitoring import ComplianceMonitoring
from .intrusion_detection_system import IntrusionDetectionSystem
from .vulnerability_scanner import VulnerabilityScanner
from .security_audit_engine import SecurityAuditEngine
from .threat_intelligence import ThreatIntelligence
from .incident_response_automation import IncidentResponseAutomation

__all__ = [
    # Security Components
    "CertificateManager",
    "NetworkSecurityPolicies",
    "RBACConfiguration",
    "EncryptionManagement",
    "ComplianceMonitoring",
    
    # Threat Protection
    "IntrusionDetectionSystem",
    "VulnerabilityScanner",
    "SecurityAuditEngine",
    "ThreatIntelligence",
    "IncidentResponseAutomation",
]

# Security configuration constants
SECURITY_LEVELS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4
}

COMPLIANCE_FRAMEWORKS = [
    "SOC2",
    "GDPR",
    "HIPAA",
    "PCI-DSS",
    "ISO27001",
    "NIST"
]

def get_security_info():
    """Get security module information."""
    return {
        "version": __version__,
        "author": __author__,
        "security_levels": SECURITY_LEVELS,
        "compliance_frameworks": COMPLIANCE_FRAMEWORKS
    }