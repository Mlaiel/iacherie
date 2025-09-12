"""🤖 Base Model Interface - IA Influencer Agent Platform Enterprise
==================================================================
Module: ml/models/base_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
==================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 BASE MODEL INTERFACE
Interface de base pour tous les modèles ML de la plateforme
- Interface standardisée pour tous les modèles
- Gestion du cycle de vie des modèles
- Méthodes communes pour training/inference
- Support multi-modal (audio, video, image, text)
"""

import abc
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Types de modèles supportés"""
    CONTENT_CLASSIFIER = "content_classifier"
    ENGAGEMENT_PREDICTOR = "engagement_predictor"
    AUDIO_ANALYZER = "audio_analyzer"
    VIDEO_ANALYZER = "video_analyzer"
    IMAGE_ANALYZER = "image_analyzer"
    TEXT_PROCESSOR = "text_processor"
    CREATOR_RECOMMENDER = "creator_recommender"
    TREND_PREDICTOR = "trend_predictor"
    REVENUE_FORECASTER = "revenue_forecaster"

class ModelStatus(Enum):
    """États des modèles"""
    INITIALIZED = "initialized"
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"

@dataclass
class ModelMetadata:
    """Métadonnées des modèles"""
    model_id: str
    model_type: ModelType
    version: str
    created_at: datetime
    updated_at: datetime
    creator_type: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    training_config: Dict[str, Any] = field(default_factory=dict)
    status: ModelStatus = ModelStatus.INITIALIZED
    description: str = ""
    tags: List[str] = field(default_factory=list)

class BaseModel(abc.ABC):
    """
    Interface de base pour tous les modèles ML de la plateforme.
    
    Cette classe abstraite définit l'interface standardisée que tous
    les modèles doivent implémenter pour assurer la cohérence et
    l'interopérabilité dans la plateforme.
    """
    
    def __init__(self, model_id: Optional[str] = None, **kwargs):
        """Initialise le modèle de base"""
        self.model_id = model_id or str(uuid.uuid4())
        self.metadata = ModelMetadata(
            model_id=self.model_id,
            model_type=self.get_model_type(),
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.model = None
        self.is_trained = False
        self.performance_history = []
        
        # Configuration par défaut
        self.config = {
            "batch_size": kwargs.get("batch_size", 32),
            "learning_rate": kwargs.get("learning_rate", 0.001),
            "epochs": kwargs.get("epochs", 100),
            "validation_split": kwargs.get("validation_split", 0.2),
            "random_state": kwargs.get("random_state", 42),
            "device": kwargs.get("device", "cpu")
        }
        
        logger.info(f"Initialized {self.__class__.__name__} with ID: {self.model_id}")
    
    @abc.abstractmethod
    def get_model_type(self) -> ModelType:
        """Retourne le type du modèle"""
        pass
    
    @abc.abstractmethod
    def build_model(self, input_shape: Optional[Tuple] = None, **kwargs) -> Any:
        """
        Construit l'architecture du modèle.
        
        Args:
            input_shape: Forme des données d'entrée
            **kwargs: Arguments supplémentaires
            
        Returns:
            Le modèle construit
        """
        pass
    
    @abc.abstractmethod
    def train(self, X_train: Any, y_train: Any, 
              X_val: Optional[Any] = None, y_val: Optional[Any] = None,
              **kwargs) -> Dict[str, Any]:
        """
        Entraîne le modèle sur les données fournies.
        
        Args:
            X_train: Données d'entraînement
            y_train: Labels d'entraînement
            X_val: Données de validation (optionnel)
            y_val: Labels de validation (optionnel)
            **kwargs: Arguments supplémentaires
            
        Returns:
            Historique d'entraînement et métriques
        """
        pass
    
    @abc.abstractmethod
    def predict(self, X: Any, **kwargs) -> Any:
        """
        Effectue des prédictions sur les données fournies.
        
        Args:
            X: Données pour la prédiction
            **kwargs: Arguments supplémentaires
            
        Returns:
            Prédictions du modèle
        """
        pass
    
    @abc.abstractmethod
    def evaluate(self, X_test: Any, y_test: Any, **kwargs) -> Dict[str, float]:
        """
        Évalue les performances du modèle.
        
        Args:
            X_test: Données de test
            y_test: Labels de test
            **kwargs: Arguments supplémentaires
            
        Returns:
            Métriques de performance
        """
        pass
    
    def save_model(self, filepath: str) -> bool:
        """
        Sauvegarde le modèle sur disque.
        
        Args:
            filepath: Chemin de sauvegarde
            
        Returns:
            True si succès, False sinon
        """
        try:
            model_data = {
                "metadata": self.metadata.__dict__,
                "config": self.config,
                "model_state": self._get_model_state(),
                "performance_history": self.performance_history
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved successfully to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """
        Charge un modèle depuis le disque.
        
        Args:
            filepath: Chemin du fichier
            
        Returns:
            True si succès, False sinon
        """
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            # Restaurer les métadonnées
            metadata_dict = model_data["metadata"]
            self.metadata = ModelMetadata(**metadata_dict)
            
            # Restaurer la configuration
            self.config = model_data["config"]
            
            # Restaurer l'état du modèle
            self._set_model_state(model_data["model_state"])
            
            # Restaurer l'historique
            self.performance_history = model_data["performance_history"]
            
            self.is_trained = True
            logger.info(f"Model loaded successfully from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations du modèle"""
        return {
            "model_id": self.model_id,
            "model_type": self.metadata.model_type.value,
            "version": self.metadata.version,
            "status": self.metadata.status.value,
            "created_at": self.metadata.created_at.isoformat(),
            "updated_at": self.metadata.updated_at.isoformat(),
            "is_trained": self.is_trained,
            "performance_metrics": self.metadata.performance_metrics,
            "config": self.config
        }
    
    def update_metadata(self, **kwargs) -> None:
        """Met à jour les métadonnées du modèle"""
        for key, value in kwargs.items():
            if hasattr(self.metadata, key):
                setattr(self.metadata, key, value)
        
        self.metadata.updated_at = datetime.now()
        logger.info(f"Updated metadata for model {self.model_id}")
    
    def validate_input(self, X: Any) -> bool:
        """
        Valide les données d'entrée.
        
        Args:
            X: Données à valider
            
        Returns:
            True si valide, False sinon
        """
        if X is None:
            return False
        
        # Validation générique - à surcharger dans les classes filles
        if hasattr(X, 'shape') and len(X.shape) > 0:
            return True
        
        if isinstance(X, (list, tuple)) and len(X) > 0:
            return True
        
        return False
    
    def preprocess_data(self, X: Any, **kwargs) -> Any:
        """
        Préprocesse les données d'entrée.
        
        Args:
            X: Données à préprocesser
            **kwargs: Arguments supplémentaires
            
        Returns:
            Données préprocessées
        """
        # Implémentation par défaut - à surcharger dans les classes filles
        return X
    
    def postprocess_predictions(self, predictions: Any, **kwargs) -> Any:
        """
        Post-traite les prédictions.
        
        Args:
            predictions: Prédictions brutes
            **kwargs: Arguments supplémentaires
            
        Returns:
            Prédictions post-traitées
        """
        # Implémentation par défaut - à surcharger dans les classes filles
        return predictions
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Retourne l'importance des features si disponible.
        
        Returns:
            Dictionnaire des importances ou None
        """
        # À implémenter dans les classes filles si applicable
        return None
    
    def explain_prediction(self, X: Any, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Explique une prédiction si possible.
        
        Args:
            X: Données pour l'explication
            **kwargs: Arguments supplémentaires
            
        Returns:
            Explication ou None
        """
        # À implémenter dans les classes filles si applicable
        return None
    
    def _get_model_state(self) -> Dict[str, Any]:
        """Récupère l'état interne du modèle pour la sauvegarde"""
        if hasattr(self.model, 'state_dict'):
            # PyTorch model
            return {"type": "pytorch", "state_dict": self.model.state_dict()}
        elif hasattr(self.model, 'get_params'):
            # Sklearn model
            return {"type": "sklearn", "params": self.model.get_params(), "model": self.model}
        else:
            # Modèle personnalisé
            return {"type": "custom", "model": self.model}
    
    def _set_model_state(self, model_state: Dict[str, Any]) -> None:
        """Restaure l'état interne du modèle après chargement"""
        if model_state["type"] == "pytorch":
            if self.model is not None:
                self.model.load_state_dict(model_state["state_dict"])
        elif model_state["type"] == "sklearn":
            self.model = model_state["model"]
        else:
            self.model = model_state["model"]
    
    def __str__(self) -> str:
        """Représentation string du modèle"""
        return f"{self.__class__.__name__}(id={self.model_id}, type={self.metadata.model_type.value})"
    
    def __repr__(self) -> str:
        """Représentation détaillée du modèle"""
        return (f"{self.__class__.__name__}("
                f"id={self.model_id}, "
                f"type={self.metadata.model_type.value}, "
                f"status={self.metadata.status.value}, "
                f"trained={self.is_trained})")

class CreatorSpecificModel(BaseModel):
    """
    Modèle spécialisé pour un type de créateur spécifique.
    
    Cette classe étend BaseModel pour ajouter des fonctionnalités
    spécifiques aux différents types de créateurs (musiciens, bloggers, etc.)
    """
    
    def __init__(self, creator_type: str, **kwargs):
        """
        Initialise un modèle spécifique à un créateur.
        
        Args:
            creator_type: Type de créateur (musician, blogger, photographer, etc.)
            **kwargs: Arguments supplémentaires
        """
        super().__init__(**kwargs)
        self.creator_type = creator_type
        self.metadata.creator_type = creator_type
        
        # Configuration spécifique au créateur
        self.creator_config = self._get_creator_config(creator_type)
        
        logger.info(f"Initialized creator-specific model for {creator_type}")
    
    def _get_creator_config(self, creator_type: str) -> Dict[str, Any]:
        """
        Retourne la configuration spécifique au type de créateur.
        
        Args:
            creator_type: Type de créateur
            
        Returns:
            Configuration spécifique
        """
        creator_configs = {
            "musician": {
                "content_types": ["audio", "video"],
                "metrics_focus": ["engagement", "streams", "downloads"],
                "features": ["tempo", "key", "energy", "valence", "danceability"]
            },
            "blogger": {
                "content_types": ["text", "image"],
                "metrics_focus": ["views", "shares", "comments"],
                "features": ["readability", "sentiment", "topic", "length", "seo_score"]
            },
            "photographer": {
                "content_types": ["image", "video"],
                "metrics_focus": ["likes", "shares", "portfolio_views"],
                "features": ["composition", "color_harmony", "lighting", "style", "aesthetics"]
            },
            "influencer": {
                "content_types": ["video", "image", "text"],
                "metrics_focus": ["engagement", "reach", "conversions"],
                "features": ["trend_alignment", "audience_fit", "authenticity", "virality"]
            },
            "comedian": {
                "content_types": ["video", "audio", "text"],
                "metrics_focus": ["laughs", "shares", "engagement"],
                "features": ["timing", "delivery", "content_humor", "audience_reaction"]
            }
        }
        
        return creator_configs.get(creator_type, {
            "content_types": ["text", "image", "video", "audio"],
            "metrics_focus": ["engagement"],
            "features": ["general_appeal"]
        })
    
    def get_creator_features(self, content: Any) -> Dict[str, float]:
        """
        Extrait les features spécifiques au créateur depuis le contenu.
        
        Args:
            content: Contenu à analyser
            
        Returns:
            Features extraites
        """
        # Implémentation par défaut - à surcharger dans les classes filles
        return {}
    
    def optimize_for_creator(self, content_history: List[Any]) -> Dict[str, Any]:
        """
        Optimise le modèle basé sur l'historique du créateur.
        
        Args:
            content_history: Historique du contenu du créateur
            
        Returns:
            Recommandations d'optimisation
        """
        # Implémentation par défaut - à surcharger dans les classes filles
        return {"status": "optimization_not_implemented"}

# Export des classes principales
__all__ = [
    "BaseModel",
    "CreatorSpecificModel", 
    "ModelType",
    "ModelStatus",
    "ModelMetadata"
]