"""
🌐 PLATFORM MODELS INDEX - ENTERPRISE GRADE
==========================================

Point d'entrée central pour tous les modèles Platform Enterprise
Support complet: Multi-platform, APIs, Cross-platform Analytics

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Architecture: Enterprise Platform Models with advanced integration patterns
"""

from .base_platform_model import BasePlatformModel
from .spotify_integration_model import SpotifyIntegrationModel
from .youtube_integration_model import YouTubeIntegrationModel
from .instagram_integration_model import InstagramIntegrationModel
from .tiktok_integration_model import TikTokIntegrationModel
from .twitter_integration_model import TwitterIntegrationModel
from .soundcloud_integration_model import SoundCloudIntegrationModel
from .twitch_integration_model import TwitchIntegrationModel
from .facebook_integration_model import FacebookIntegrationModel
from .linkedin_integration_model import LinkedInIntegrationModel
from .platform_synchronization_model import PlatformSynchronizationModel
from .cross_platform_analytics_model import CrossPlatformAnalyticsModel
from .distribution_model import DistributionModel
from .platform_performance_model import PlatformPerformanceModel

# Enterprise Platform Models Collection
__all__ = [
    # Core Platform Models
    'BasePlatformModel',
    'PlatformSynchronizationModel',
    'CrossPlatformAnalyticsModel',
    'DistributionModel',
    'PlatformPerformanceModel',
    
    # Music & Audio Platforms
    'SpotifyIntegrationModel',
    'SoundCloudIntegrationModel',
    
    # Video & Streaming Platforms
    'YouTubeIntegrationModel',
    'TwitchIntegrationModel',
    
    # Social Media Platforms
    'InstagramIntegrationModel',
    'TikTokIntegrationModel',
    'TwitterIntegrationModel',
    'FacebookIntegrationModel',
    
    # Professional Platforms
    'LinkedInIntegrationModel',
]

# Enterprise Platform Registry
PLATFORM_MODELS_REGISTRY = {
    'core': {
        'base': BasePlatformModel,
        'sync': PlatformSynchronizationModel,
        'analytics': CrossPlatformAnalyticsModel,
        'distribution': DistributionModel,
        'performance': PlatformPerformanceModel,
    },
    'music_audio': {
        'spotify': SpotifyIntegrationModel,
        'soundcloud': SoundCloudIntegrationModel,
    },
    'video_streaming': {
        'youtube': YouTubeIntegrationModel,
        'twitch': TwitchIntegrationModel,
    },
    'social_media': {
        'instagram': InstagramIntegrationModel,
        'tiktok': TikTokIntegrationModel,
        'twitter': TwitterIntegrationModel,
        'facebook': FacebookIntegrationModel,
    },
    'professional': {
        'linkedin': LinkedInIntegrationModel,
    }
}

def get_platform_model(category: str, model_type: str):
    """
    Récupère un modèle Platform Enterprise par catégorie et type
    
    Args:
        category: core, music_audio, video_streaming, social_media, professional
        model_type: Type spécifique de modèle platform
        
    Returns:
        Classe du modèle Platform Enterprise correspondant
    """
    return PLATFORM_MODELS_REGISTRY.get(category, {}).get(model_type)

def list_available_platform_models():
    """Liste tous les modèles Platform Enterprise disponibles"""
    return PLATFORM_MODELS_REGISTRY

# Platform Models Enterprise Stats
PLATFORM_MODELS_STATS = {
    'total_models': 14,
    'categories': 5,
    'core_models': 5,
    'music_audio_models': 2,
    'video_streaming_models': 2,
    'social_media_models': 4,
    'professional_models': 1,
    'enterprise_ready': True,
    'api_integrated': True,
    'cross_platform_sync': True,
    'real_time_analytics': True
}