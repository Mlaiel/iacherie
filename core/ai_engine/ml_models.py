"""
ML Models sub-module for Core AI Engine
Sous-module des modèles ML pour le moteur d'IA central

Ce module fournit les modèles de machine learning pour l'IA.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Configuration du logger
logger = logging.getLogger(__name__)

@dataclass
class MLModelConfig:
    """
Configuration d'un modèle ML"""
    name: str
    model_type: str
    parameters: Dict[str, Any]
    version: str = "1.0"

class MLModels:
    """
Gestionnaire des modèles ML"""
    
    def __init__(self):
        """
Initialise le gestionnaire de modèles ML"""
        self.models: Dict[str, MLModelConfig] = {}
        self._initialize_default_models()
        logger.info("ML Models initialized")
    
    def _initialize_default_models(self):
        """
Initialise les modèles par défaut"""
        
        # Modèles par défaut
        default_models = [
            MLModelConfig(
                name="content_classifier",
                model_type="classification",
                parameters={"accuracy": 0.95, "categories": 50}
            ),
            MLModelConfig(
                name="sentiment_analyzer", 
                model_type="nlp",
                parameters={"languages": ["en", "fr", "de"], "accuracy": 0.92}
            ),
            MLModelConfig(
                name="recommendation_engine",
                model_type="recommendation",
                parameters={"algorithm": "collaborative_filtering", "factors": 100}
            )
        ]
        
        for model in default_models:
            self.models[model.name] = model
    
    def get_model(self, name: str) -> Optional[MLModelConfig]:
        """
Récupère un modèle par son nom"""
        return self.models.get(name)
    
    def add_model(self, model: MLModelConfig):
        """
Ajoute un nouveau modèle"""
        self.models[model.name] = model
        logger.info(f"ML model added: {model.name}")
    
    def list_models(self) -> List[str]:
        """
Liste tous les modèles disponibles"""
        return list(self.models.keys())

# Instance globale
ml_models = MLModels()

# Alias pour compatibilité
MLModelManager = MLModels  # Alias pour compatibilité

# Fonctions utilitaires
def get_model_config(name: str) -> Optional[MLModelConfig]:
    """
Récupère la configuration d'un modèle"""
    return ml_models.get_model(name)

def register_model(name: str, model_type: str, parameters: Dict[str, Any]):
    """
Enregistre un nouveau modèle"""
    config = MLModelConfig(
        name=name,
        model_type=model_type,
        parameters=parameters
    )
    ml_models.add_model(config)

# Exports principaux
__all__ = [
    'MLModels',
    'MLModelManager',  # Alias pour compatibilité
    'MLModelConfig',
    'ml_models',
    'get_model_config',
    'register_model'
]

logger.info("ML Models sub-module initialized successfully")