"""🤖 AI/ML Pipeline Module - Enterprise Implementation
==================================================

Module principal pour l'orchestration des 53 agents IA d'Ainflue
avec optimisation GPU, serving production et MLOps automation.

Author: Fahed Mlaiel (mlaiel@live.de)
Date: 14 Septembre 2025
"""

from .enterprise_ai_ml_pipeline import (
    EnterpriseAIMLPipeline,
    ModelConfiguration,
    ModelInstance,
    ModelType,
    ModelStatus,
    InferenceProvider,
    OptimizationStrategy,
    InferenceRequest,
    InferenceResponse,
    initialize_ai_ml_pipeline
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "EnterpriseAIMLPipeline",
    "ModelConfiguration", 
    "ModelInstance",
    "ModelType",
    "ModelStatus",
    "InferenceProvider",
    "OptimizationStrategy",
    "InferenceRequest",
    "InferenceResponse",
    "initialize_ai_ml_pipeline"
]