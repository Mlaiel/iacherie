"""
Content Generation - Ainflue Integrations
=========================================
Point d'entrée principal pour génération de contenu IA.
Orchestration des 53 agents IA spécialisés.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations  
Version: 1.0 Production
"""

try:
    from .video_generation_engine import VideoGenerationEngine
except ImportError:
    VideoGenerationEngine = None

try:
    from .audio_generation_engine import AudioGenerationEngine
except ImportError:
    AudioGenerationEngine = None

try:
    from .image_generation_engine import ImageGenerationEngine
except ImportError:
    ImageGenerationEngine = None

try:
    from .text_generation_engine import TextGenerationEngine
except ImportError:
    TextGenerationEngine = None

try:
    from .ai_content_orchestrator import AIContentOrchestrator
except ImportError:
    AIContentOrchestrator = None

try:
    from .quality_enhancement_engine import QualityEnhancementEngine
except ImportError:
    QualityEnhancementEngine = None

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
    generators = {}
    
    if AIContentOrchestrator:
        generators['orchestrator'] = AIContentOrchestrator()
    if VideoGenerationEngine:
        generators['video'] = VideoGenerationEngine()
    if AudioGenerationEngine:
        generators['audio'] = AudioGenerationEngine()
    if ImageGenerationEngine:
        generators['image'] = ImageGenerationEngine()
    if TextGenerationEngine:
        generators['text'] = TextGenerationEngine()
    if QualityEnhancementEngine:
        generators['quality'] = QualityEnhancementEngine()
    
    return generators