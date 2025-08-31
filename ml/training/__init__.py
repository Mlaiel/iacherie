"""🚀 ML Training Module - IA Influencer Agent Platform Enterprise
==============================================================
Module: backend/ml/training/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODULE D'ENTRAÎNEMENT ML
Composants d'entraînement et d'optimisation des modèles
- AutoML Pipeline automatisé
- Hyperparameter tuning avancé avec Optuna
- Cross-validation et validation robuste
- Gestion des expériences et métriques
"""

from .automl_pipeline import (
    AutoMLPipeline,
    AutoMLConfig,
    AutoMLPipelineFactory,
    ModelType,
    TrainingStatus,
    TrainingMetrics,
    TrainingJob
)

from .hyperparameter_tuning import (
    HyperparameterTuner,
    OptimizationConfig,
    OptimizationResult,
    HyperparameterSpace,
    OptimizationDirection,
    SamplerType,
    PrunerType,
    CommonParameterSpaces
)

__all__ = [
    # AutoML Pipeline
    'AutoMLPipeline',
    'AutoMLConfig', 
    'AutoMLPipelineFactory',
    'ModelType',
    'TrainingStatus',
    'TrainingMetrics',
    'TrainingJob',
    
    # Hyperparameter Tuning
    'HyperparameterTuner',
    'OptimizationConfig',
    'OptimizationResult',
    'HyperparameterSpace',
    'OptimizationDirection',
    'SamplerType',
    'PrunerType',
    'CommonParameterSpaces'
]

# Version du module
__version__ = "1.0.0"

# Metadata
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. Tous droits réservés."