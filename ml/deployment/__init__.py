"""🚀 ML Deployment Module - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/deployment/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODULE DE DÉPLOIEMENT ML
Système complet de déploiement de modèles ML
- Docker et Kubernetes deployment
- Strategies avancées (Blue-Green, Canary)
- Auto-scaling et load balancing
- Health monitoring et rollback
"""
from .deployment_manager import (
    ModelDeploymentManager,
    DeploymentConfig,
    DeploymentInfo,
    PerformanceMetrics,
    DeploymentType,
    DeploymentStrategy,
    DeploymentStatus,
    DeploymentManagerFactory
)

__all__ = [
    'ModelDeploymentManager',
    'DeploymentConfig',
    'DeploymentInfo',
    'PerformanceMetrics',
    'DeploymentType',
    'DeploymentStrategy',
    'DeploymentStatus',
    'DeploymentManagerFactory'
]

# Version du module
__version__ = "1.0.0"

# Metadata
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. Tous droits réservés."