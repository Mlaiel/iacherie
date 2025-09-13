"""
Authentication Module - Ainflue Integrations
===========================================
Enterprise authentication and security management module providing
OAuth, JWT, multi-factor authentication, and advanced security scanning.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations
Version: 1.0 Production
"""

# Authentication Core Components
from .authentication_handler import AuthenticationHandler
from .oauth_manager import OAuthManager

# Security Components (decomposed from security_scanner.py)
from .security_scanner_core import SecurityScannerCore
from .vulnerability_scanner import VulnerabilityScanner
from .compliance_checker import ComplianceChecker

# Public exports
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
__description__ = "Enterprise authentication and security management for Ainflue platform"

# Configuration logique métier Ainflue
AINFLUE_AUTHENTICATION = {
    'platforms': 65,
    'auth_methods': ['oauth2', 'jwt', 'mfa', 'biometric'],
    'workflow': 'connect→auth→transform→process→distribute→monitor'
}