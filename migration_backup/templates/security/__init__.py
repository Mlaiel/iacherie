"""IA Chéries Platform Security Templates Module

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel (mlaiel@live.de)
Enterprise Security Architecture Expert
"""

from typing import Dict, Any, List, Optional, Type
import logging

# Core Security Templates
from .authentication_template import (
    AuthenticationTemplate,
    AuthMethod,
    TokenType,
    SecurityLevel
)
from .authorization_template import (
    AuthorizationTemplate,
    RoleBasedAccessControl,
    AttributeBasedAccessControl,
    PolicyEngine
)
from .csrf_protection_template import (
    CSRFProtectionTemplate,
    CSRFTokenManager,
    DoubleSubmitCookiePattern
)
from .encryption_template import (
    EncryptionTemplate,
    AESEncryption,
    RSAEncryption,
    KeyDerivationEngine
)
from .input_validation_template import (
    InputValidationTemplate,
    XSSProtection,
    SQLInjectionProtection,
    FileUploadSecurity
)
from .security_middleware_template import (
    SecurityMiddlewareTemplate,
    SecurityHeadersManager,
    ThreatDetectionEngine
)

# Advanced Authentication Templates
from .biometric_authentication_template import (
    BiometricAuthenticationTemplate,
    BiometricType,
    BiometricVerifier
)
from .social_login_template import (
    SocialLoginTemplate,
    SocialProvider,
    OAuthFlowManager
)
from .sso_integration_template import (
    SSOIntegrationTemplate,
    SAMLProvider,
    OpenIDConnectProvider
)
from .passwordless_authentication_template import (
    PasswordlessAuthenticationTemplate,
    MagicLinkManager,
    WebAuthnManager
)
from .device_trust_template import (
    DeviceTrustTemplate,
    DeviceFingerprinting,
    TrustScoreCalculator
)
from .session_management_template import (
    SessionManagementTemplate,
    SessionStore,
    SessionSecurity
)
from .token_introspection_template import (
    TokenIntrospectionTemplate,
    TokenValidator,
    TokenRevocationManager
)
from .oauth2_server_template import (
    OAuth2ServerTemplate,
    AuthorizationServer,
    ResourceServer
)

# Content Protection Templates
from .content_watermarking_template import (
    ContentWatermarkingTemplate,
    WatermarkVerificationEngine,
    WatermarkType,
    ContentType as WatermarkContentType,
    WatermarkStrength,
    WatermarkConfig,
    WatermarkMetadata
)
from .digital_rights_management_template import (
    DigitalRightsManagementTemplate,
    LicenseManager,
    LicenseType,
    UsageRight,
    ProtectionLevel,
    LicenseStatus,
    DRMConfig,
    LicenseMetadata,
    AccessPolicy
)
from .content_fingerprinting_template import (
    ContentFingerprintingTemplate,
    FingerprintAnalyzer,
    FingerprintType,
    ContentType as FingerprintContentType,
    SimilarityMetric,
    FingerprintConfig,
    FingerprintData,
    SimilarityResult
)
from .plagiarism_detection_template import (
    PlagiarismDetectionTemplate,
    PlagiarismReportGenerator,
    PlagiarismType,
    ContentType as PlagiarismContentType,
    DetectionMethod,
    PlagiarismConfig,
    PlagiarismMatch,
    PlagiarismReport
)

# Security Registry
from .security_template_registry import (
    SecurityTemplateRegistry,
    TemplateMetadata,
    TemplateRegistration,
    TemplateCategory,
    TemplateStatus,
    SecurityLevel as RegistrySecurityLevel,
    get_security_registry
)

logger = logging.getLogger(__name__)

# Security Template Registry
SECURITY_TEMPLATES: Dict[str, Type] = {
    # Core Security
    'authentication': AuthenticationTemplate,
    'authorization': AuthorizationTemplate,
    'csrf_protection': CSRFProtectionTemplate,
    'encryption': EncryptionTemplate,
    'input_validation': InputValidationTemplate,
    'security_middleware': SecurityMiddlewareTemplate,
    
    # Advanced Authentication
    'biometric_authentication': BiometricAuthenticationTemplate,
    'social_login': SocialLoginTemplate,
    'sso_integration': SSOIntegrationTemplate,
    'passwordless_authentication': PasswordlessAuthenticationTemplate,
    'device_trust': DeviceTrustTemplate,
    'session_management': SessionManagementTemplate,
    'token_introspection': TokenIntrospectionTemplate,
    'oauth2_server': OAuth2ServerTemplate,
    
    # Content Protection
    'content_watermarking': ContentWatermarkingTemplate,
    'digital_rights_management': DigitalRightsManagementTemplate,
    'content_fingerprinting': ContentFingerprintingTemplate,
    'plagiarism_detection': PlagiarismDetectionTemplate,
}

# Security Categories
AUTHENTICATION_TEMPLATES = [
    'authentication',
    'biometric_authentication',
    'social_login',
    'sso_integration',
    'passwordless_authentication',
    'device_trust',
    'oauth2_server'
]

AUTHORIZATION_TEMPLATES = [
    'authorization',
    'token_introspection'
]

PROTECTION_TEMPLATES = [
    'csrf_protection',
    'encryption',
    'input_validation',
    'security_middleware'
]

SESSION_TEMPLATES = [
    'session_management'
]


class SecurityTemplateManager:
    """Central manager for all security templates"""
    
    def __init__(self):
        """Initialize security template manager"""
        self.templates = SECURITY_TEMPLATES.copy()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def get_template(self, template_name: str) -> Optional[Type]:
        """Get security template by name
        
        Args:
            template_name: Name of the security template
            
        Returns:
            Security template class or None if not found
        """
        template = self.templates.get(template_name)
        if template is None:
            self.logger.warning(f"Security template '{template_name}' not found")
        return template
        
    def list_templates(self) -> List[str]:
        """List all available security templates
        
        Returns:
            List of template names
        """
        return list(self.templates.keys())
        
    def get_templates_by_category(self, category: str) -> List[str]:
        """Get templates by security category
        
        Args:
            category: Security category (authentication, authorization, protection, session)
            
        Returns:
            List of template names in the category
        """
        category_map = {
            'authentication': AUTHENTICATION_TEMPLATES,
            'authorization': AUTHORIZATION_TEMPLATES,
            'protection': PROTECTION_TEMPLATES,
            'session': SESSION_TEMPLATES,
            'content_protection': CONTENT_PROTECTION_TEMPLATES
        }
        
        return category_map.get(category, [])
        
    def register_template(self, name: str, template_class: Type) -> None:
        """Register new security template
        
        Args:
            name: Template name
            template_class: Template class
        """
        self.templates[name] = template_class
        self.logger.info(f"Registered security template: {name}")
        
    def validate_template(self, template_name: str) -> bool:
        """Validate if template exists and is properly configured
        
        Args:
            template_name: Name of the template to validate
            
        Returns:
            True if template is valid, False otherwise
        """
        template = self.get_template(template_name)
        if template is None:
            return False
            
        # Check if template has required methods
        required_methods = ['initialize', 'configure', 'validate']
        for method in required_methods:
            if not hasattr(template, method):
                self.logger.error(f"Template '{template_name}' missing required method: {method}")
                return False
                
        return True


# Global security template manager instance
security_manager = SecurityTemplateManager()

# Export main components
__all__ = [
    # Core Templates
    'AuthenticationTemplate',
    'AuthorizationTemplate', 
    'CSRFProtectionTemplate',
    'EncryptionTemplate',
    'InputValidationTemplate',
    'SecurityMiddlewareTemplate',
    
    # Advanced Templates
    'BiometricAuthenticationTemplate',
    'SocialLoginTemplate',
    'SSOIntegrationTemplate',
    'PasswordlessAuthenticationTemplate',
    'DeviceTrustTemplate',
    'SessionManagementTemplate',
    'TokenIntrospectionTemplate',
    'OAuth2ServerTemplate',
    
    # Content Protection Templates
    'ContentWatermarkingTemplate',
    'WatermarkVerificationEngine',
    'DigitalRightsManagementTemplate',
    'LicenseManager',
    'ContentFingerprintingTemplate',
    'FingerprintAnalyzer',
    'PlagiarismDetectionTemplate',
    'PlagiarismReportGenerator',
    
    # Registry and Management
    'SecurityTemplateRegistry',
    'SecurityTemplateManager',
    'security_manager',
    'get_security_registry',
    
    # Enums and Types
    'AuthMethod',
    'TokenType',
    'SecurityLevel',
    'BiometricType',
    'SocialProvider',
    'WatermarkType',
    'LicenseType',
    'UsageRight',
    'ProtectionLevel',
    'FingerprintType',
    'SimilarityMetric',
    'PlagiarismType',
    'DetectionMethod',
    'TemplateCategory',
    'TemplateStatus',
    
    # Registry
    'SECURITY_TEMPLATES',
    'AUTHENTICATION_TEMPLATES',
    'AUTHORIZATION_TEMPLATES',
    'PROTECTION_TEMPLATES',
    'SESSION_TEMPLATES',
    'CONTENT_PROTECTION_TEMPLATES'
]

# Module version
__version__ = "4.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."