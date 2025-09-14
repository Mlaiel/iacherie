"""
🤖 BASE AI MODEL - ENTERPRISE GRADE
==================================

Modèle de base pour tous les modèles IA Enterprise
Architecture: SQLAlchemy + Advanced ML patterns

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

Base = declarative_base()

class BaseAIModel(Base):
    """
    Modèle de base pour tous les modèles IA Enterprise
    Support: TensorFlow, PyTorch, embeddings, versioning
    """
    __tablename__ = 'ai_models_base'
    
    # Core Identity
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Model Metadata
    model_name = Column(String(255), nullable=False, index=True)
    model_type = Column(String(100), nullable=False, index=True)  # fingerprint, embedding, classification, etc.
    model_version = Column(String(50), nullable=False, default="1.0.0")
    model_framework = Column(String(50), nullable=False)  # tensorflow, pytorch, sklearn, etc.
    
    # Model Configuration
    config = Column(JSON, nullable=True)  # Model-specific configuration
    parameters = Column(JSON, nullable=True)  # Model parameters
    hyperparameters = Column(JSON, nullable=True)  # Training hyperparameters
    
    # Model Status
    status = Column(String(50), nullable=False, default="training")  # training, ready, deployed, deprecated
    is_active = Column(Boolean, default=True, nullable=False)
    is_production_ready = Column(Boolean, default=False, nullable=False)
    
    # Performance Metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Training Information
    training_dataset_size = Column(Integer, nullable=True)
    training_duration_seconds = Column(Integer, nullable=True)
    training_started_at = Column(DateTime, nullable=True)
    training_completed_at = Column(DateTime, nullable=True)
    
    # Model Storage
    model_path = Column(String(500), nullable=True)  # Path to saved model
    model_size_bytes = Column(Integer, nullable=True)
    checksum = Column(String(64), nullable=True)  # Model file checksum
    
    # Metadata
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags for categorization
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deployed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<BaseAIModel(name='{self.model_name}', type='{self.model_type}', version='{self.model_version}')>"
    
    @property
    def is_trained(self) -> bool:
        """Vérifie si le modèle est entraîné"""
        return self.status in ['ready', 'deployed'] and self.training_completed_at is not None
    
    @property
    def training_duration(self) -> Optional[int]:
        """Durée d'entraînement en secondes"""
        if self.training_started_at and self.training_completed_at:
            return int((self.training_completed_at - self.training_started_at).total_seconds())
        return self.training_duration_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'model_name': self.model_name,
            'model_type': self.model_type,
            'model_version': self.model_version,
            'model_framework': self.model_framework,
            'status': self.status,
            'is_active': self.is_active,
            'is_production_ready': self.is_production_ready,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deployed_at': self.deployed_at.isoformat() if self.deployed_at else None
        }
    
    def update_metrics(self, metrics: Dict[str, float]):
        """Met à jour les métriques de performance"""
        if 'accuracy' in metrics:
            self.accuracy = metrics['accuracy']
        if 'precision' in metrics:
            self.precision = metrics['precision']
        if 'recall' in metrics:
            self.recall = metrics['recall']
        if 'f1_score' in metrics:
            self.f1_score = metrics['f1_score']
        self.updated_at = datetime.utcnow()
    
    def mark_as_production_ready(self):
        """Marque le modèle comme prêt pour la production"""
        self.is_production_ready = True
        self.status = 'ready'
        self.updated_at = datetime.utcnow()
    
    def deploy(self):
        """Déploie le modèle en production"""
        if not self.is_production_ready:
            raise ValueError("Model must be production ready before deployment")
        self.status = 'deployed'
        self.deployed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class AIModelRegistry:
    """Registry pour gérer les modèles IA Enterprise"""
    
    @staticmethod
    def create_model(model_name: str, model_type: str, framework: str, **kwargs) -> BaseAIModel:
        """Crée un nouveau modèle IA"""
        return BaseAIModel(
            model_name=model_name,
            model_type=model_type,
            model_framework=framework,
            **kwargs
        )
    
    @staticmethod
    def get_active_models(model_type: Optional[str] = None) -> List[BaseAIModel]:
        """Récupère les modèles actifs, optionnellement filtrés par type"""
        # This would typically use a database session
        # For now, return empty list as placeholder
        return []
    
    @staticmethod
    def get_production_models() -> List[BaseAIModel]:
        """Récupère tous les modèles prêts pour la production"""
        # This would typically use a database session
        # For now, return empty list as placeholder
        return []