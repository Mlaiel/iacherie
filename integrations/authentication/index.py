"""
Authentication Module - Ainflue Integrations
===========================================
Enterprise-grade authentication and security management providing comprehensive
OAuth 2.0/OIDC integration, multi-factor authentication, JWT token management,
and advanced security scanning across 65+ platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Import all authentication components
from .authentication_handler import *
from .oauth_manager import *
from .security_scanner_core import *
from .vulnerability_scanner import *
from .compliance_checker import *

# Re-export for convenience
from . import (
    authentication_handler,
    oauth_manager,
    security_scanner_core,
    vulnerability_scanner,
    compliance_checker
)

# Exports publics
__all__ = [
    'AuthenticationHandler',
    'OAuthManager',
    'SecurityScannerCore', 
    'VulnerabilityScanner',
    'ComplianceChecker',
]

# Metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise authentication infrastructure for multi-platform content creators"

# Configuration logique métier Ainflue
AINFLUE_INTEGRATIONS = {
    'platforms': 65,
    'ecosystems': 3,
    'workflow': 'connect→auth→transform→process→distribute→monitor',
    'auth_features': [
        'oauth2_providers',
        'jwt_management', 
        'mfa_enforcement',
        'security_scanning',
        'compliance_checking'
    ]
}