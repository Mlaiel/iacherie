"""
🤖 AI MODELS INDEX - ENTERPRISE GRADE
==================================

Point d'entrée central pour tous les modèles IA Enterprise
Support complet: TensorFlow, PyTorch, embeddings, fingerprinting

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Architecture: Enterprise AI Models with advanced ML patterns
"""

from .base_ai_model import BaseAIModel
from .audio_fingerprint_model import AudioFingerprintModel
from .image_fingerprint_model import ImageFingerprintModel
from .text_embedding_model import TextEmbeddingModel
from .video_fingerprint_model import VideoFingerprintModel
from .similarity_detection_model import SimilarityDetectionModel
from .content_protection_model import ContentProtectionModel
from .ai_analytics_model import AIAnalyticsModel
from .recommendation_model import RecommendationModel
from .prediction_model import PredictionModel
from .neural_network_model import NeuralNetworkModel
from .inference_model import InferenceModel
from .creative_ai_model import CreativeAIModel
from .model_training_tracker import ModelTrainingTracker

# Enterprise AI Models Collection
__all__ = [
    # Core AI Models
    'BaseAIModel',
    'NeuralNetworkModel',
    'InferenceModel',
    'ModelTrainingTracker',
    
    # Content Fingerprinting Models
    'AudioFingerprintModel',
    'ImageFingerprintModel',
    'VideoFingerprintModel',
    'TextEmbeddingModel',
    
    # AI Analytics & Intelligence
    'SimilarityDetectionModel',
    'ContentProtectionModel',
    'AIAnalyticsModel',
    'RecommendationModel',
    'PredictionModel',
    'CreativeAIModel',
]

# Enterprise AI Models Registry
AI_MODELS_REGISTRY = {
    'fingerprinting': {
        'audio': AudioFingerprintModel,
        'image': ImageFingerprintModel,
        'video': VideoFingerprintModel,
        'text': TextEmbeddingModel,
    },
    'intelligence': {
        'similarity': SimilarityDetectionModel,
        'protection': ContentProtectionModel,
        'analytics': AIAnalyticsModel,
        'recommendations': RecommendationModel,
        'predictions': PredictionModel,
        'creative': CreativeAIModel,
    },
    'infrastructure': {
        'base': BaseAIModel,
        'neural': NeuralNetworkModel,
        'inference': InferenceModel,
        'training': ModelTrainingTracker,
    }
}

def get_ai_model(category: str, model_type: str):
    """
    Récupère un modèle IA Enterprise par catégorie et type
    
    Args:
        category: fingerprinting, intelligence, infrastructure
        model_type: Type spécifique de modèle
        
    Returns:
        Classe du modèle IA Enterprise correspondant
    """
    return AI_MODELS_REGISTRY.get(category, {}).get(model_type)

def list_available_ai_models():
    """Liste tous les modèles IA Enterprise disponibles"""
    return AI_MODELS_REGISTRY

# AI Models Enterprise Stats
AI_MODELS_STATS = {
    'total_models': 14,
    'categories': 3,
    'fingerprinting_models': 4,
    'intelligence_models': 6,
    'infrastructure_models': 4,
    'enterprise_ready': True,
    'production_validated': True
}