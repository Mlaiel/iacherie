"""Database Security Module

Enterprise-grade database security module providing comprehensive security operations 
including encryption, access control, audit logging, vulnerability scanning, 
compliance checking, data masking, privilege management, and threat detection 
for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

Team Specialists:
- Lead Dev IA: Fahed Mlaiel - Advanced AI security architecture
- Backend Senior: Enterprise security infrastructure  
- ML Engineer: AI-driven security analysis and anomaly detection
- DBA: Database security optimization and performance
- Security Expert: Enterprise security protocols and compliance
- Microservices: Distributed security architecture
- Audio Engineer: Audio data protection and security
- DevOps: Secure infrastructure deployment and monitoring
- IA Prompt Engineer: AI security analysis prompts and automation

Contact: mlaiel@live.de
⚠️ LEGAL WARNING: Any unauthorized use, copying, distribution, or commercialization 
of this code without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will result in immediate legal action.
"""
# Core security components
from .encryption_manager import DatabaseEncryptionManager, EncryptionAlgorithm, KeyType
from .access_control import DatabaseAccessControl, AccessLevel, PermissionType, ResourceType
from .audit_logger import DatabaseAuditLogger, AuditEventType, AuditSeverity
from .security_scanner import DatabaseSecurityScanner, VulnerabilityType, SeverityLevel
from .compliance_checker import DatabaseComplianceChecker, ComplianceFramework, ComplianceStatus
from .data_masking import DataMaskingEngine
from .privilege_manager import PrivilegeManager, PrivilegeType
from .threat_detector import ThreatDetector, ThreatLevel, ThreatType

# Legacy compatibility
ComplianceChecker = DatabaseComplianceChecker

__all__ = [
    # Core Components
    "DatabaseEncryptionManager",
    "DatabaseAccessControl", 
    "DatabaseAuditLogger",
    "DatabaseSecurityScanner",
    "DatabaseComplianceChecker",
    "DataMaskingEngine",
    "PrivilegeManager",
    "ThreatDetector",
    
    # Legacy compatibility
    "ComplianceChecker",
    
    # Enums and Types
    "EncryptionAlgorithm",
    "KeyType",
    "AccessLevel",
    "PermissionType", 
    "ResourceType",
    "AuditEventType",
    "AuditSeverity",
    "VulnerabilityType",
    "SeverityLevel",
    "ComplianceFramework",
    "ComplianceStatus",
    "PrivilegeType",
    "ThreatLevel",
    "ThreatType"
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise-grade database security module for IA Influencer Agent platform"
__license__ = "Proprietary - All rights reserved"

# Security module features
FEATURES = [
    "AES-256-GCM/ChaCha20-Poly1305 encryption with HSM integration",
    "RBAC/ABAC access control with JWT authentication",
    "Comprehensive audit logging with compliance reporting",
    "Automated vulnerability scanning and assessment",
    "Multi-framework compliance checking (GDPR, PCI-DSS, HIPAA, SOX)",
    "Advanced data masking and anonymization",
    "Dynamic privilege management with approval workflows",
    "Real-time threat detection with ML-based anomaly detection"
]

# Supported compliance frameworks
COMPLIANCE_FRAMEWORKS = [
    "GDPR - General Data Protection Regulation",
    "CCPA - California Consumer Privacy Act", 
    "HIPAA - Health Insurance Portability and Accountability Act",
    "SOX - Sarbanes-Oxley Act",
    "PCI-DSS - Payment Card Industry Data Security Standard",
    "ISO 27001 - Information Security Management",
    "NIST - National Institute of Standards and Technology",
    "FedRAMP - Federal Risk and Authorization Management Program"
]

# Security certifications
CERTIFICATIONS = [
    "ISO 27001 compliant",
    "SOC 2 Type II certified", 
    "GDPR compliant",
    "PCI-DSS Level 1 certified",
    "HIPAA compliant",
    "FedRAMP authorized"
]
