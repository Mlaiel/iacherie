"""🚀 Model Registry Module - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/model_registry/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODULE MODEL REGISTRY
Gestion complète du cycle de vie des modèles ML
- MLflow registry avec versioning automatique
- Model promotion et deployment tracking
- Rollback et A/B testing support
- Metadata et lineage management
"""
from .mlflow_registry import (
    MLflowModelRegistry,
    ModelRegistryConfig,
    ModelMetadata,
    DeploymentInfo,
    ModelStage,
    RegistryStatus,
    ModelRegistryFactory
)

__all__ = [
    'MLflowModelRegistry',
    'ModelRegistryConfig',
    'ModelMetadata',
    'DeploymentInfo',
    'ModelStage',
    'RegistryStatus',
    'ModelRegistryFactory'
]

# Version du module
__version__ = "1.0.0"

# Metadata
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. Tous droits réservés."