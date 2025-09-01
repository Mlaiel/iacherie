"""IA Influencer Agent - Core Security Module
Advanced Enterprise Security Suite for Multi-Content Protection Platform

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use strictly prohibited.
License: Proprietary - Contact author for licensing terms

This module provides comprehensive security infrastructure for:
- Multi-tenant authentication and authorization with advanced features
- Content protection and fingerprinting security with AI-powered detection
- API security and rate limiting with intelligent threat detection
- Cryptographic operations and key management with quantum-resistance
- Security monitoring and threat detection with machine learning
- Compliance and audit trails with automated reporting
- Advanced input validation and malware scanning
- Real-time threat intelligence and incident response
"""# Core Authentication Components
from .authentication import (
    AuthenticationManager,
    JWTManager,
    OAuth2Manager,
    MultiTenantAuth,
    TokenManager,
    TwoFactorAuth,
    AuthToken,
    AuthUser,
    AuthenticationError
)

# Advanced Authorization Components
from .authorization import (
    AuthorizationManager,
    RoleBasedAccess,
    PermissionManager,
    ResourceAccess,
    ContentAccessControl,
    PermissionLevel,
    ResourceType,
    ContentType,
    PermissionScope
)

# Enterprise Encryption Components
from .encryption import (
    EncryptionManager,
    KeyManager,
    CryptoService,
    ContentEncryption,
    DatabaseEncryption,
    EncryptionAlgorithm,
    KeyType
)

# Advanced Monitoring Components
from .monitoring import (
    SecurityMonitor,
    ThreatDetector,
    AuditLogger,
    SecurityMetrics,
    IntrusionDetection,
    BehaviorAnalyzer,
    ThreatLevel,
    EventType
)

# Content Protection Components
from .protection import (
    ContentProtection,
    FingerprintSecurity,
    AntiTamper,
    CopyrightProtection,
    WatermarkingSecurity,
    ContentFingerprint,
    ContentWatermark,
    ContentVerification,
    ProtectionLevel,
    WatermarkType
)

# Advanced Validation Components
from .validation import (
    InputValidator,
    ContentValidator,
    SecurityValidator,
    MalwareScanner,
    VirusScanner,
    ValidationResult,
    ThreatCategory,
    ContentCategory
)

# API Firewall Components
from .firewall import (
    APIFirewall,
    RateLimiter,
    DDoSProtection,
    RequestFilter,
    SecurityGateway,
    RateLimitType,
    BlockAction
)

# Compliance Components
from .compliance import (
    GDPRCompliance,
    CCPACompliance,
    DMCACompliance,
    AuditCompliance,
    ComplianceManager,
    PrivacyRight,
    DataCategory,
    ComplianceFramework
)

# Security Service Registry and Facade
from .index import (
    SecurityServiceRegistry,
    SecurityFacade,
    get_security_registry,
    get_security_facade,
    quick_authenticate,
    quick_authorize,
    quick_encrypt,
    quick_scan,
    quick_protect,
    quick_log_event
)

# Export all components
__all__ = [
    # Authentication
    'AuthenticationManager',
    'JWTManager', 
    'OAuth2Manager',
    'MultiTenantAuth',
    'TokenManager',
    'TwoFactorAuth',
    'AuthToken',
    'AuthUser',
    'AuthenticationError',
    
    # Authorization
    'AuthorizationManager',
    'RoleBasedAccess',
    'PermissionManager',
    'ResourceAccess',
    'ContentAccessControl',
    'PermissionLevel',
    'ResourceType',
    'ContentType',
    'PermissionScope',
    
    # Encryption
    'EncryptionManager',
    'KeyManager',
    'CryptoService',
    'ContentEncryption',
    'DatabaseEncryption',
    'EncryptionAlgorithm',
    'KeyType',
    
    # Monitoring
    'SecurityMonitor',
    'ThreatDetector',
    'AuditLogger',
    'SecurityMetrics',
    'IntrusionDetection',
    'BehaviorAnalyzer',
    'ThreatLevel',
    'EventType',
    
    # Protection
    'ContentProtection',
    'FingerprintSecurity',
    'AntiTamper',
    'CopyrightProtection',
    'WatermarkingSecurity',
    'ContentFingerprint',
    'ContentWatermark',
    'ContentVerification',
    'ProtectionLevel',
    'WatermarkType',
    
    # Validation
    'InputValidator',
    'ContentValidator',
    'SecurityValidator',
    'MalwareScanner',
    'VirusScanner',
    'ValidationResult',
    'ThreatCategory',
    'ContentCategory',
    
    # Firewall
    'APIFirewall',
    'RateLimiter',
    'DDoSProtection',
    'RequestFilter',
    'SecurityGateway',
    'RateLimitType',
    'BlockAction',
    
    # Compliance
    'GDPRCompliance',
    'CCPACompliance', 
    'DMCACompliance',
    'AuditCompliance',
    'ComplianceManager',
    'PrivacyRight',
    'DataCategory',
    'ComplianceFramework',
    
    # Service Registry and Facade
    'SecurityServiceRegistry',
    'SecurityFacade',
    'get_security_registry',
    'get_security_facade',
    'quick_authenticate',
    'quick_authorize',
    'quick_encrypt',
    'quick_scan',
    'quick_protect',
    'quick_log_event'
]

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise Security Suite for IA Influencer Agent"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Contact author for licensing terms"

# Security Module Status
SECURITY_FEATURES = {
    "multi_tenant_auth": True,
    "oauth2_integration": True,
    "two_factor_auth": True,
    "content_protection": True,
    "ai_fingerprinting": True,
    "anti_tamper": True,
    "watermarking": True,
    "threat_detection": True,
    "malware_scanning": True,
    "ddos_protection": True,
    "rate_limiting": True,
    "gdpr_compliance": True,
    "ccpa_compliance": True,
    "dmca_compliance": True,
    "audit_logging": True,
    "encryption_aes256": True,
    "encryption_rsa4096": True,
    "quantum_resistance": True,
    "real_time_monitoring": True,
    "incident_response": True
}

# Module Health Check
def get_security_status():
    """Get security module status and feature availability"""
    return {
        "module": "backend.core.security",
        "version": __version__,
        "author": __author__,
        "features": SECURITY_FEATURES,
        "status": "operational",
        "last_updated": "2025-08-20"
    }

# Security Configuration Validation
def validate_security_config():
    """Validate security configuration"""
    from backend.core.config import get_settings
    
    settings = get_settings()
    required_settings = [
        'SECRET_KEY',
        'ENCRYPTION_KEY',
        'FINGERPRINT_SIGNING_KEY'
    ]
    
    missing_settings = []
    for setting in required_settings:
        if not hasattr(settings, setting) or not getattr(settings, setting):
            missing_settings.append(setting)
    
    if missing_settings:
        raise ValueError(f"Missing required security settings: {missing_settings}")
    
    return True

# Module Initialization Hook
async def initialize_security():
    """Initialize the security module"""
    try:
        # Validate configuration
        validate_security_config()
        
        # Initialize security registry
        registry = await get_security_registry()
        
        return {
            "status": "initialized",
            "registry": registry,
            "features": SECURITY_FEATURES
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to initialize security module: {str(e)}")

