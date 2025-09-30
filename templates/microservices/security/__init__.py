"""
⚠️ AVERTISSEMENT LÉGAL OBLIGATOIRE:
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

IA Chérie Security Templates Module
Advanced security microservices templates for enterprise creator economy platform
"""

from .jwt_auth_template import JWTAuthTemplate
from .oauth2_service_template import OAuth2ServiceTemplate
from .rbac_middleware_template import RBACMiddlewareTemplate
from .encryption_service_template import EncryptionServiceTemplate
from .key_management_template import KeyManagementTemplate
from .security_gateway_template import SecurityGatewayTemplate
from .audit_service_template import AuditServiceTemplate
from .compliance_checker_template import ComplianceCheckerTemplate

__all__ = [
    "JWTAuthTemplate",
    "OAuth2ServiceTemplate", 
    "RBACMiddlewareTemplate",
    "EncryptionServiceTemplate",
    "KeyManagementTemplate",
    "SecurityGatewayTemplate",
    "AuditServiceTemplate",
    "ComplianceCheckerTemplate"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"