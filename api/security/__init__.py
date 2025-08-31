"""IA Influencer Agent - Security Module
Complete security framework for content protection and platform security

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent Platform

Team Specialties:
- Lead AI Developer: Advanced machine learning and neural networks
- Senior Backend Developer: Enterprise-grade Python architecture
- ML Engineer: Deep learning and content analysis algorithms  
- Database Administrator: High-performance data management
- Security Expert: Cybersecurity and content protection
- Microservices Architect: Scalable distributed systems
- Audio Engineer: Digital signal processing and audio analysis
- DevOps Engineer: CI/CD and cloud infrastructure deployment
- AI Prompt Engineer: LLM integration and optimization

  COPYRIGHT NOTICE - STRICTLY PROTECTED 
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
ANY UNAUTHORIZED USE, REPRODUCTION, DISTRIBUTION, OR THEFT OF THIS CODE
OR CONCEPT WITHOUT EXPLICIT WRITTEN PERMISSION IS STRICTLY FORBIDDEN.

Violators will face:
- Legal action under German and international copyright laws
- Criminal charges for intellectual property theft
- Financial penalties and damages claims
- Immediate cease and desist enforcement

Contact: mlaiel@live.de for any authorization requests.
"""
from .auth import *
from .authorization import *
from .encryption import *
from .validation import *
from .audit import *
from .content_protection import *
from .blockchain_security import *
from .threat_intelligence import *
from .compliance import *
from .forensics import *

from .index import (
    initialize_security_services,
    setup_security_middleware,
    get_security_dashboard_data,
    validate_request_security,
    protect_intellectual_property
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

__all__ = [
    # Core Security Services
    'initialize_security_services',
    'setup_security_middleware',
    'get_security_dashboard_data',
    'validate_request_security',
    'protect_intellectual_property',
    
    # Authentication Module
    'AuthenticationManager',
    'JWTManager',
    'OAuth2Manager',
    'SessionManager',
    'TwoFactorAuthManager',
    'BiometricAuthManager',
    
    # Authorization Module
    'AuthorizationManager',
    'RoleBasedAccessControl',
    'PermissionManager',
    'ResourceAccessManager',
    'PolicyEngine',
    
    # Encryption Module
    'EncryptionManager',
    'AESEncryption',
    'RSAEncryption',
    'HybridEncryption',
    'KeyManagementService',
    'HashingService',
    
    # Validation Module
    'InputValidator',
    'SecurityValidator',
    'CSRFProtection',
    'XSSProtection',
    'SQLInjectionProtection',
    'RateLimiter',
    
    # Audit Module
    'AuditLogger',
    'SecurityMonitor',
    'ThreatDetection',
    'IncidentResponse',
    'ComplianceTracker',
    
    # Content Protection Module
    'ContentProtectionManager',
    'DigitalWatermarking',
    'FingerprintAnalyzer',
    'AntiPiracyService',
    'LicenseValidator',
    
    # Blockchain Security Module
    'SmartContractSecurity',
    'WalletSecurityManager',
    'TransactionValidator',
    'ConsensusValidator',
    'BlockchainAuditor',
    
    # Threat Intelligence Module
    'ThreatIntelligenceManager',
    'IOCAnalyzer',
    'AttackPatternDetector',
    'RiskAssessment',
    'SecurityAlertSystem',
    
    # Compliance Module
    'ComplianceManager',
    'GDPRCompliance',
    'SOC2Compliance',
    'ISO27001Compliance',
    'RegulationTracker',
    
    # Digital Forensics Module
    'DigitalForensicsManager',
    'EvidenceCollector',
    'ChainOfCustody',
    'ForensicAnalyzer',
    'IncidentReconstructor'
]
