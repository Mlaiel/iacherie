"""
Core AI Engine Package
Package principal du moteur d'IA
"""

from .ml_models import MLModels, MLModelManager, MLModelConfig, ml_models, get_model_config, register_model

__all__ = [
    'MLModels',
    'MLModelManager',  # Alias pour compatibilité
    'MLModelConfig', 
    'ml_models',
    'get_model_config',
    'register_model'
]