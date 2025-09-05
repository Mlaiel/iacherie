"""Infrastructure Security Module - IA-Influencer-Agent Platform
================================================================
Security management and authentication functionality

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
License: Proprietary - All rights reserved

This module handles security and authentication:
- Authentication and authorization
- Security policies and compliance
- Access control and permissions
"""

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__status__ = "Production"

# Import security modules with error handling
import logging

logger = logging.getLogger(__name__)

# Import auth module with graceful error handling
try:
    from .auth import (
        SecurityManager, 
        AuthenticationManager,
        AuthorizationManager,
        SessionManager,
        EncryptionManager,
        SecurityValidator,
        UnifiedSecurityManager,
        AccessControlManager,
        SecurityAuditManager,
        PolicyManager,
        ComplianceManager,
        JWTManager,
        TokenManager,
        PasswordManager,
        CertificateManager,
        VaultManager
    )
except ImportError as e:
    logger.warning(f"Failed to import some auth components: {e}")
    
    # Provide placeholder classes for missing components
    class SecurityManager:
        def __init__(self, **kwargs):
            logger.warning("SecurityManager not available - using placeholder")
    
    class AuthenticationManager:
        def __init__(self, **kwargs):
            logger.warning("AuthenticationManager not available - using placeholder")
    
    class CertificateManager:
        def __init__(self, **kwargs):
            logger.warning("CertificateManager not available - using placeholder")
    
    class VaultManager:
        def __init__(self, **kwargs):
            logger.warning("VaultManager not available - using placeholder")
    
    class PolicyManager:
        def __init__(self, **kwargs):
            logger.warning("PolicyManager not available - using placeholder")
    
    class ComplianceManager:
        def __init__(self, **kwargs):
            logger.warning("ComplianceManager not available - using placeholder")

__all__ = [
    # Core security functionality
    "SecurityManager",
    "AuthenticationManager", 
    "AuthorizationManager",
    "SessionManager",
    "EncryptionManager",
    "SecurityValidator",
    "UnifiedSecurityManager",
    "AccessControlManager",
    "SecurityAuditManager",
    "PolicyManager",
    "ComplianceManager",
    "JWTManager",
    "TokenManager",
    "PasswordManager",
    "CertificateManager",
    "VaultManager",
    # Instances
    "security_manager",
    "certificate_manager",
    "vault_manager",
    "policy_manager",
    "compliance_manager"
]

# Create default instances
try:
    security_manager = SecurityManager()
    certificate_manager = CertificateManager()
    vault_manager = VaultManager()
    policy_manager = PolicyManager()
    compliance_manager = ComplianceManager()
except Exception as e:
    logger.warning(f"Failed to create some security instances: {e}")
    # Create placeholder instances
    security_manager = SecurityManager()
    certificate_manager = CertificateManager()
    vault_manager = VaultManager()
    policy_manager = PolicyManager()
    compliance_manager = ComplianceManager()