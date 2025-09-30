"""🔒 Security Integration Module - Enterprise Security Centralized
=================================================================

Module __init__.py pour centraliser tous les services de sécurité enterprise
dans le module integrations/security.

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Production Enterprise

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
"""

# Import avec gestion d'erreur pour éviter les dépendances circulaires
try:
    from .enterprise_security_integration import (
        EnterpriseSecurityIntegration,
        SecurityConfiguration,
        SecurityLevel,
        ComplianceStandard,
        AuthenticationMethod,
        ThreatLevel,
        SecurityEvent,
        ComplianceReport,
        initialize_enterprise_security
    )
except ImportError as e:
    print(f"⚠️ Enterprise security integration import failed: {e}")
    # Définition des classes de base pour éviter les erreurs
    EnterpriseSecurityIntegration = None
    SecurityConfiguration = None
    SecurityLevel = None
    ComplianceStandard = None
    AuthenticationMethod = None
    ThreatLevel = None
    SecurityEvent = None
    ComplianceReport = None
    initialize_enterprise_security = None

# Import direct et sécurisé de SecurityScannerCore
try:
    from .security_scanner import SecurityScannerCore
except ImportError as e:
    print(f"⚠️ SecurityScannerCore import failed: {e}")
    SecurityScannerCore = None

# Import du SecurityScannerCore nouvellement créé
try:
    from .security_scanner import SecurityScannerCore
except ImportError as e:
    print(f"⚠️ SecurityScannerCore import failed: {e}")
    SecurityScannerCore = None

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "EnterpriseSecurityIntegration",
    "SecurityConfiguration", 
    "SecurityLevel",
    "ComplianceStandard",
    "AuthenticationMethod",
    "ThreatLevel",
    "SecurityEvent",
    "ComplianceReport",
    "initialize_enterprise_security",
    "SecurityScannerCore"
]