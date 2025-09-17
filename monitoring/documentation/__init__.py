"""Documentation Module - Enterprise Creator Economy Documentation System
Complete documentation system for Ainflue Creator Economy platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

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
"""

# API validator (existing)
from .api_validator import (
    APIDocumentationValidator,
    APIEndpoint,  
    DocumentationReport
)

# Version information
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

# Module metadata
__all__ = [
    # API validation
    'APIDocumentationValidator',
    'APIEndpoint',
    'DocumentationReport',
    
    # Module metadata
    '__version__',
    '__author__',
    '__email__',
    '__copyright__'
]

# Quick access functions
def create_api_validator(project_root: str = None):
    """Create a new API documentation validator"""
    if project_root is None:
        project_root = "/home/runner/work/Ainflue/Ainflue"
    return APIDocumentationValidator(project_root)

# Module initialization message
import logging
logger = logging.getLogger(__name__)
logger.info("Ainflue Documentation Module initialized - Enterprise Creator Economy Documentation System v1.0.0")
logger.info("© 2025 Fahed Mlaiel <mlaiel@live.de> - All rights reserved")