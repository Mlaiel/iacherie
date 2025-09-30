"""
📦 CONTENT MODELS INDEX - ENTERPRISE GRADE
=========================================

Point d'entrée central pour tous les modèles Content Enterprise
Support complet: Multi-format, Metadata, Lifecycle, Performance

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Architecture: Enterprise Content Models with advanced media patterns
"""

from .base_content_model import BaseContentModel
from .audio_content_model import AudioContentModel
from .video_content_model import VideoContentModel
from .image_content_model import ImageContentModel
from .text_content_model import TextContentModel
from .document_content_model import DocumentContentModel
from .podcast_content_model import PodcastContentModel
from .social_content_model import SocialContentModel
from .content_metadata_model import ContentMetadataModel
from .content_category_model import ContentCategoryModel
from .content_relationship_model import ContentRelationshipModel
from .content_lifecycle_model import ContentLifecycleModel
from .content_targeting_model import ContentTargetingModel
from .content_performance_model import ContentPerformanceModel

# Enterprise Content Models Collection
__all__ = [
    # Core Content Models
    'BaseContentModel',
    'ContentMetadataModel',
    'ContentCategoryModel',
    'ContentRelationshipModel',
    
    # Media Format Models
    'AudioContentModel',
    'VideoContentModel',
    'ImageContentModel',
    'TextContentModel',
    'DocumentContentModel',
    
    # Specialized Content Models
    'PodcastContentModel',
    'SocialContentModel',
    
    # Content Management Models
    'ContentLifecycleModel',
    'ContentTargetingModel',
    'ContentPerformanceModel',
]

# Enterprise Content Registry
CONTENT_MODELS_REGISTRY = {
    'core': {
        'base': BaseContentModel,
        'metadata': ContentMetadataModel,
        'category': ContentCategoryModel,
        'relationship': ContentRelationshipModel,
    },
    'media': {
        'audio': AudioContentModel,
        'video': VideoContentModel,
        'image': ImageContentModel,
        'text': TextContentModel,
        'document': DocumentContentModel,
    },
    'specialized': {
        'podcast': PodcastContentModel,
        'social': SocialContentModel,
    },
    'management': {
        'lifecycle': ContentLifecycleModel,
        'targeting': ContentTargetingModel,
        'performance': ContentPerformanceModel,
    }
}

def get_content_model(category: str, model_type: str):
    """
    Récupère un modèle Content Enterprise par catégorie et type
    
    Args:
        category: core, media, specialized, management
        model_type: Type spécifique de modèle content
        
    Returns:
        Classe du modèle Content Enterprise correspondant
    """
    return CONTENT_MODELS_REGISTRY.get(category, {}).get(model_type)

def list_available_content_models():
    """Liste tous les modèles Content Enterprise disponibles"""
    return CONTENT_MODELS_REGISTRY

# Content Models Enterprise Stats
CONTENT_MODELS_STATS = {
    'total_models': 14,
    'categories': 4,
    'core_models': 4,
    'media_models': 5,
    'specialized_models': 2,
    'management_models': 3,
    'enterprise_ready': True,
    'multi_format_support': True,
    'metadata_complete': True,
    'lifecycle_managed': True
}