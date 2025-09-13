"""
Content Generation Module - Ainflue Integrations
===============================================
Module de génération de contenu IA enterprise avec 53 agents
spécialisés pour création multi-format et multi-plateforme.

Support pour:
- Génération vidéo, audio, image, texte IA
- 53 agents IA spécialisés par domaine
- Optimisation qualité et performance
- Pipeline automatisé de création

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

__all__ = [
    'VideoGenerationEngine',
    'AudioGenerationEngine',
    'ImageGenerationEngine',
    'TextGenerationEngine',
    'AIContentOrchestrator',
    'QualityEnhancementEngine'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Content Generation IA enterprise - 53 agents spécialisés"