"""
🛡️ MLOps Operations & Reliability - Enterprise Architecture
===============================================================

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

Enterprise operations reliability module for Creator Economy MLOps platform.
Combining expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel
Contact: mlaiel@live.de
"""

from .cost_optimizer import (
    CostOptimizer,
    CostOptimizationStrategy,
    ResourceType,
    CloudProvider,
    CostMetrics
)

from .feature_flag_manager import (
    FeatureFlagManager,
    FeatureFlagType,
    FeatureFlagStatus,
    TargetingRule
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel - Tous droits réservés"

__all__ = [
    # Cost Optimization
    "CostOptimizer",
    "CostOptimizationStrategy", 
    "ResourceType",
    "CloudProvider",
    "CostMetrics",
    
    # Feature Flags
    "FeatureFlagManager",
    "FeatureFlagType",
    "FeatureFlagStatus",
    "TargetingRule",
    
    # Core metadata
    "__version__",
    "__author__",
    "__email__",
    "__copyright__"
]