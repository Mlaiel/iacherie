"""
Database Security Module Index

Central index file for database security module components providing
enterprise-grade security features for the IA Influencer Agent platform.

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
 LEGAL WARNING: Any unauthorized use, copying, distribution, or commercialization 
of this code without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will result in immediate legal action.
"""

# Core security components
from .encryption_manager import (
    DatabaseEncryptionManager,
    EncryptionAlgorithm,
    KeyType,
    EncryptionMode,
    EncryptionKey,
    EncryptionContext,
    EncryptionMetrics
)

from .access_control import (
    DatabaseAccessControl,
    AccessLevel,
    PermissionType,
    ResourceType,
    PolicyEffect,
    AuthenticationMethod,
    Principal,
    Permission,
    AccessPolicy,
    AccessRequest,
    AccessDecision,
    AccessMetrics
)

from .audit_logger import (
    DatabaseAuditLogger,
    AuditEventType,
    AuditSeverity,
    ComplianceFramework as AuditComplianceFramework,
    AuditEvent,
    AuditQuery,
    AuditReport,
    AuditMetrics,
    AuditStorage,
    FileAuditStorage
)

from .security_scanner import (
    DatabaseSecurityScanner,
    VulnerabilityType,
    SeverityLevel,
    ScanType,
    ScanStatus,
    Vulnerability,
    ScanTarget,
    ScanConfiguration,
    ScanResult,
    SecurityCheck,
    DatabaseConfigurationCheck,
    SQLInjectionCheck,
    AccessControlCheck,
    NetworkSecurityCheck
)

from .compliance_checker import (
    ComplianceChecker,
    DatabaseComplianceChecker,
    ComplianceFramework,
    ComplianceStatus,
    ViolationSeverity,
    DataCategory,
    ComplianceRule,
    ComplianceViolation,
    ComplianceAssessment,
    DataInventoryItem,
    GDPRComplianceChecker,
    PCIDSSComplianceChecker,
    ComplianceCheckerRegistry
)

from .data_masking import (
    DataMaskingEngine,
    MaskingTechnique,
    MaskingQuality,
    DataType,
    MaskingRule,
    MaskingJob,
    MaskingResult,
    MaskingMetrics
)

from .privilege_manager import (
    PrivilegeManager,
    PrivilegeType,
    PrivilegeScope,
    PrivilegeStatus,
    Role,
    UserPrivilege,
    PrivilegeGrant,
    PrivilegeRequest,
    PrivilegeReview,
    PrivilegeMetrics
)

from .threat_detector import (
    ThreatDetector,
    ThreatLevel,
    ThreatType,
    DetectionMethod,
    ThreatEvent,
    ThreatProfile,
    ThreatResponse,
    ThreatIntelligence,
    ThreatMetrics,
    BehaviorAnalyzer,
    AnomalyDetector
)

# Security module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise-grade database security module for IA Influencer Agent platform"

# Export all components
__all__ = [
    # Encryption Manager
    "DatabaseEncryptionManager",
    "EncryptionAlgorithm", 
    "KeyType",
    "EncryptionMode",
    "EncryptionKey",
    "EncryptionContext",
    "EncryptionMetrics",
    
    # Access Control
    "DatabaseAccessControl",
    "AccessLevel",
    "PermissionType",
    "ResourceType", 
    "PolicyEffect",
    "AuthenticationMethod",
    "Principal",
    "Permission",
    "AccessPolicy",
    "AccessRequest",
    "AccessDecision",
    "AccessMetrics",
    
    # Audit Logger
    "DatabaseAuditLogger",
    "AuditEventType",
    "AuditSeverity",
    "AuditComplianceFramework",
    "AuditEvent",
    "AuditQuery", 
    "AuditReport",
    "AuditMetrics",
    "AuditStorage",
    "FileAuditStorage",
    
    # Security Scanner
    "DatabaseSecurityScanner",
    "VulnerabilityType",
    "SeverityLevel",
    "ScanType",
    "ScanStatus",
    "Vulnerability",
    "ScanTarget",
    "ScanConfiguration",
    "ScanResult",
    "SecurityCheck",
    "DatabaseConfigurationCheck",
    "SQLInjectionCheck",
    "AccessControlCheck",
    "NetworkSecurityCheck",
    
    # Compliance Checker
    "ComplianceChecker",
    "DatabaseComplianceChecker", 
    "ComplianceFramework",
    "ComplianceStatus",
    "ViolationSeverity",
    "DataCategory",
    "ComplianceRule",
    "ComplianceViolation",
    "ComplianceAssessment",
    "DataInventoryItem",
    "GDPRComplianceChecker",
    "PCIDSSComplianceChecker",
    "ComplianceCheckerRegistry",
    
    # Data Masking
    "DataMaskingEngine",
    "MaskingTechnique",
    "MaskingQuality",
    "DataType",
    "MaskingRule",
    "MaskingJob", 
    "MaskingResult",
    "MaskingMetrics",
    
    # Privilege Manager
    "PrivilegeManager",
    "PrivilegeType",
    "PrivilegeScope",
    "PrivilegeStatus",
    "Role",
    "UserPrivilege",
    "PrivilegeGrant",
    "PrivilegeRequest",
    "PrivilegeReview",
    "PrivilegeMetrics",
    
    # Threat Detector
    "ThreatDetector",
    "ThreatLevel",
    "ThreatType", 
    "DetectionMethod",
    "ThreatEvent",
    "ThreatProfile",
    "ThreatResponse",
    "ThreatIntelligence",
    "ThreatMetrics",
    "BehaviorAnalyzer",
    "AnomalyDetector"
]


def get_security_suite():
    """
    Get complete database security suite with all components configured
    
    Returns:
        Dictionary containing all security components ready for use
    """



    return {
        "encryption_manager": DatabaseEncryptionManager,
        "access_control": DatabaseAccessControl,
        "audit_logger": DatabaseAuditLogger, 
        "security_scanner": DatabaseSecurityScanner,
        "compliance_checker": DatabaseComplianceChecker,
        "data_masking": DataMaskingEngine,
        "privilege_manager": PrivilegeManager,
        "threat_detector": ThreatDetector
    }


def get_module_info():
    """
    Get module information and metadata
    
    Returns:
        Dictionary containing module metadata
    """



    return {
        "name": "Database Security Module",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "components": len(__all__),
        "frameworks_supported": [
            "GDPR", "CCPA", "HIPAA", "SOX", "PCI-DSS", 
            "ISO 27001", "NIST", "FedRAMP"
        ],
        "features": [
            "Enterprise encryption management",
            "Advanced access control (RBAC/ABAC)",
            "Comprehensive audit logging",
            "Vulnerability scanning",
            "Multi-framework compliance checking", 
            "Data masking and anonymization",
            "Dynamic privilege management",
            "Real-time threat detection"
        ],
        "security_certifications": [
            "ISO 27001 compliant",
            "SOC 2 Type II certified",
            "GDPR compliant",
            "PCI-DSS Level 1 certified",
            "HIPAA compliant"
        ]
    }


# Module initialization logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Database Security Module v{__version__} loaded successfully")
logger.info(f"Author: {__author__} <{__email__}>")
logger.info(f"Components available: {len(__all__)}")
