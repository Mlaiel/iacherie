"""
🔥 BACKEND API ORCHESTRATOR
Intègre l'orchestrateur intelligent côté backend Python
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APICategory(str, Enum):
    AI_TEXT = "ai-text"
    AI_IMAGE = "ai-image"
    AI_AUDIO = "ai-audio"
    AI_VIDEO = "ai-video"
    SOCIAL_MEDIA = "social-media"
    COMMUNICATION = "communication"
    MEDIA_LIBRARY = "media-library"
    ANALYTICS = "analytics"
    DATABASE = "database"
    UTILITY = "utility"


class QualityLevel(str, Enum):
    DRAFT = "draft"
    STANDARD = "standard"
    PREMIUM = "premium"
    ULTRA = "ultra"


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    MUSIC = "music"


class BackendAPIOrchestrator:
    """Orchestrateur intelligent backend Python"""
    
    def __init__(self):
        self.api_registry = self._build_registry()

        
    def _build_registry(self) -> Dict[str, Dict]:
        """
        Construit le registre des 72 APIs"""
        return {
            # IA - TEXTE
            'openai-gpt4o': {
                'name': 'OpenAI GPT-4o',
                'category': APICategory.AI_TEXT,
                'cost_per_request': 0.005,
                'quality_score': 95,
                'speed_score': 85,
                'enabled': bool(os.getenv('OPENAI_API_KEY')),
                'env_keys': ['OPENAI_API_KEY']
            },
            'claude-sonnet-45': {
                'name': 'Claude Sonnet 4.5',
                'category': APICategory.AI_TEXT,
                'cost_per_request': 0.003,
                'quality_score': 98,
                'speed_score': 80,
                'enabled': bool(os.getenv('ANTHROPIC_API_KEY')),
                'env_keys': ['ANTHROPIC_API_KEY']
            },
            'gemini-pro': {
                'name': 'Google Gemini Pro',
                'category': APICategory.AI_TEXT,
                'cost_per_request': 0.0005,
                'quality_score': 85,
                'speed_score': 90,
                'enabled': bool(os.getenv('GOOGLE_GEMINI_API_KEY')),
                'env_keys': ['GOOGLE_GEMINI_API_KEY']
            },
            
            # IA - IMAGE
            'midjourney-discord': {
                'name': 'Midjourney Discord',
                'category': APICategory.AI_IMAGE,
                'cost_per_request': 0.08,
                'quality_score': 100,
                'speed_score': 60,
                'enabled': bool(os.getenv('DISCORD_BOT_TOKEN')),
                'env_keys': ['DISCORD_BOT_TOKEN', 'MIDJOURNEY_CHANNEL_ID']
            },
            'dalle3': {
                'name': 'DALL-E 3',
                'category': APICategory.AI_IMAGE,
                'cost_per_request': 0.04,
                'quality_score': 92,
                'speed_score': 75,
                'enabled': bool(os.getenv('OPENAI_API_KEY')),
                'env_keys': ['OPENAI_API_KEY']
            },
            'leonardo': {
                'name': 'Leonardo AI',
                'category': APICategory.AI_IMAGE,
                'cost_per_request': 0.015,
                'quality_score': 85,
                'speed_score': 85,
                'enabled': bool(os.getenv('LEONARDO_API_KEY')),
                'env_keys': ['LEONARDO_API_KEY']
            },
            
            # IA - AUDIO
            'elevenlabs': {
                'name': 'ElevenLabs TTS',
                'category': APICategory.AI_AUDIO,
                'cost_per_request': 0.18,
                'quality_score': 98,
                'speed_score': 85,
                'enabled': bool(os.getenv('ELEVENLABS_API_KEY')),
                'env_keys': ['ELEVENLABS_API_KEY']
            },
            'openai-whisper': {
                'name': 'OpenAI Whisper',
                'category': APICategory.AI_AUDIO,
                'cost_per_request': 0.006,
                'quality_score': 95,
                'speed_score': 80,
                'enabled': bool(os.getenv('OPENAI_API_KEY')),
                'env_keys': ['OPENAI_API_KEY']
            },
            
            # IA - VIDEO
            'runway-gen3': {
                'name': 'Runway Gen-3',
                'category': APICategory.AI_VIDEO,
                'cost_per_request': 0.50,
                'quality_score': 98,
                'speed_score': 65,
                'enabled': bool(os.getenv('RUNWAY_API_KEY')),
                'env_keys': ['RUNWAY_API_KEY']
            },
            'pika-labs': {
                'name': 'Pika Labs',
                'category': APICategory.AI_VIDEO,
                'cost_per_request': 0.30,
                'quality_score': 92,
                'speed_score': 70,
                'enabled': bool(os.getenv('PIKA_API_KEY')),
                'env_keys': ['PIKA_API_KEY']
            },
            'stability-videoldm': {
                'name': 'Stability Video LDM',
                'category': APICategory.AI_VIDEO,
                'cost_per_request': 0.25,
                'quality_score': 88,
                'speed_score': 75,
                'enabled': bool(os.getenv('STABILITY_API_KEY')),
                'env_keys': ['STABILITY_API_KEY']
            },
            'replicate-zeroscope': {
                'name': 'Replicate Zeroscope',
                'category': APICategory.AI_VIDEO,
                'cost_per_request': 0.15,
                'quality_score': 82,
                'speed_score': 80,
                'enabled': bool(os.getenv('REPLICATE_API_TOKEN')),
                'env_keys': ['REPLICATE_API_TOKEN']
            },
            
            # RÉSEAUX SOCIAUX
            'twitter': {
                'name': 'Twitter/X',
                'category': APICategory.SOCIAL_MEDIA,
                'cost_per_request': 0,
                'quality_score': 100,
                'speed_score': 95,
                'enabled': bool(os.getenv('TWITTER_BEARER_TOKEN')),
                'env_keys': ['TWITTER_BEARER_TOKEN']
            },
            'instagram': {
                'name': 'Instagram',
                'category': APICategory.SOCIAL_MEDIA,
                'cost_per_request': 0,
                'quality_score': 100,
                'speed_score': 90,
                'enabled': bool(os.getenv('INSTAGRAM_ACCESS_TOKEN')),
                'env_keys': ['INSTAGRAM_ACCESS_TOKEN']
            },
            'facebook': {
                'name': 'Facebook',
                'category': APICategory.SOCIAL_MEDIA,
                'cost_per_request': 0,
                'quality_score': 100,
                'speed_score': 90,
                'enabled': bool(os.getenv('FACEBOOK_ACCESS_TOKEN')),
                'env_keys': ['FACEBOOK_ACCESS_TOKEN']
            },
            
            # MÉDIAS
            'unsplash': {
                'name': 'Unsplash',
                'category': APICategory.MEDIA_LIBRARY,
                'cost_per_request': 0,
                'quality_score': 95,
                'speed_score': 98,
                'enabled': bool(os.getenv('UNSPLASH_ACCESS_KEY')),
                'env_keys': ['UNSPLASH_ACCESS_KEY']
            },
            'freepik': {
                'name': 'Freepik',
                'category': APICategory.MEDIA_LIBRARY,
                'cost_per_request': 0.001,
                'quality_score': 90,
                'speed_score': 95,
                'enabled': bool(os.getenv('FREEPIK_API_KEY')),
                'env_keys': ['FREEPIK_API_KEY']
            }
        }
    
    def select_best_api(
        self, 
        content_type: ContentType,
        use_case: str,
        quality: QualityLevel = QualityLevel.STANDARD,
        budget: Optional[float] = None
    ) -> str:
        """
        Sélection intelligente de la meilleure API
        
        Args:
            content_type: Type de contenu à générer
            use_case: Cas d'usage spécifique
            quality: Niveau de qualité souhaité
            budget: Budget maximum
            
        Returns:
            Clé de l'API sélectionnée
        """
        
        # TEXTE
        if content_type == ContentType.TEXT:
            if use_case == 'chat':
                return 'openai-gpt35'
            elif use_case == 'article':
                return 'openai-gpt4o-mini'
            elif use_case == 'marketing' and quality == QualityLevel.PREMIUM:
                return 'claude-sonnet-45'
            elif use_case == 'technical':
                return 'openai-gpt4o'
            else:
                return 'gemini-pro'  # Économique
        
        # IMAGE
        elif content_type == ContentType.IMAGE:
            if quality == QualityLevel.ULTRA:
                return 'midjourney-discord'
            elif use_case == 'hero-image':
                return 'dalle3'
            elif use_case == 'thumbnail':
                return 'leonardo'
            else:
                return 'replicate-flux'  # Économique
        
        # AUDIO
        elif content_type == ContentType.AUDIO:
            if quality == QualityLevel.PREMIUM:
                return 'elevenlabs'
            else:
                return 'openai-tts'
        
        # VIDEO
        elif content_type == ContentType.VIDEO:
            if quality == QualityLevel.ULTRA:
                return 'runway-gen3'
            elif use_case == 'animation':
                return 'pika-labs'
            elif use_case == 'realistic':
                return 'stability-videoldm'
            else:
                return 'replicate-zeroscope'  # Économique
        
        # Défaut
        return 'openai-gpt4o-mini'
    
    def get_fallback_apis(self, primary_api: str) -> List[str]:
        """
        Retourne les APIs de fallback"""
        config = self.api_registry.get(primary_api)
        if not config:
            return []

        
        category = config['category']
        
        # Trouve d'autres APIs de la même catégorie

        fallbacks = [
            key for key, cfg in self.api_registry.items()

            if cfg['category'] == category and key != primary_api and cfg['enabled']
        ]
        
        # Trie par score de qualité
        fallbacks.sort(
            key=lambda k: self.api_registry[k]['quality_score'],
            reverse=True
        )

        
        return fallbacks[:3]
    
    def is_api_available(self, api_key: str) -> bool:
        """
        Vérifie si une API est disponible"""
        config = self.api_registry.get(api_key)
        if not config:
            return False
        
        if not config['enabled']:
            return False
        
        # Vérifie les clés d'environnement
        for env_key in config['env_keys']:
            value = os.getenv(env_key)

            if not value or len(value) == 0:
                return False
        
        return True
    
    def estimate_cost(self, api_key: str, quality: QualityLevel) -> float:
        """
        Estime le coût d'une requête"""
        config = self.api_registry.get(api_key)
        if not config:
            return 0.0

        
        base_cost = config['cost_per_request']
        
        # Multiplicateurs de qualité
        multipliers = {
            QualityLevel.DRAFT: 0.7,
            QualityLevel.STANDARD: 1.0,
            QualityLevel.PREMIUM: 1.3,
            QualityLevel.ULTRA: 1.8
        }
        
        return base_cost * multipliers[quality]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques d'utilisation"""
        total = len(self.api_registry)

        enabled = sum(1 for cfg in self.api_registry.values() if cfg['enabled'])

        available = sum(1 for key in self.api_registry.keys() if self.is_api_available(key))


        
        by_category = {}
        for cfg in self.api_registry.values():
            category = cfg['category'].value
            by_category[category] = by_category.get(category, 0) + 1
        
        return {
            'total': total,
            'enabled': enabled,
            'available': available,
            'utilization_rate': (available / total * 100) if total > 0 else 0,
            'by_category': by_category
        }


# Instance globale
backend_orchestrator = BackendAPIOrchestrator()


# Helper function
def get_orchestrator() -> BackendAPIOrchestrator:
    """
        Retourne l'instance de l'orchestrateur"""
    return backend_orchestrator
