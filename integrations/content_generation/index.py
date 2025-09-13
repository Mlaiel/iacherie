"""
Content Generation - Ainflue Integrations
=========================================
Point d'entrée principal pour génération de contenu IA.
Orchestration des 53 agents IA spécialisés.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations  
Version: 1.0 Production
"""

from .video_generation_engine import VideoGenerationEngine
from .audio_generation_engine import AudioGenerationEngine
from .image_generation_engine import ImageGenerationEngine
from .text_generation_engine import TextGenerationEngine
from .ai_content_orchestrator import AIContentOrchestrator
from .quality_enhancement_engine import QualityEnhancementEngine

# Configuration logique métier Ainflue
CONTENT_GENERATION_CONFIG = {
    'total_ai_agents': 53,
    'content_types': ['video', 'audio', 'image', 'text', 'remix'],
    'platforms_supported': 65,
    'quality_levels': ['standard', 'hd', '4k', '8k'],
    'ai_providers': ['openai', 'anthropic', 'stability', 'elevenlabs', 'midjourney'],
    'languages_supported': 644,
    'generation_models': {
        'text': 12, 'audio': 8, 'video': 10, 'image': 15, 'remix': 8
    }
}

def get_content_generator():
    """Factory pour créer le gestionnaire principal de génération."""
    return {
        'orchestrator': AIContentOrchestrator(),
        'video': VideoGenerationEngine(),
        'audio': AudioGenerationEngine(),
        'image': ImageGenerationEngine(),
        'text': TextGenerationEngine(),
        'quality': QualityEnhancementEngine()
    }