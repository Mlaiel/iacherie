"""Backend Media Generation & IA Processing Module

Enterprise-grade media processing system including:

MEDIA GENERATION:
- Avatar generation (8 types)
- Voice synthesis (6 types) 
- Image generation (10 types)
- Video generation (7 types)
- Audio generation (8 types)
- Text generation (4 types)
- Media orchestration

IA PROCESSING & INTELLIGENCE (NEW):
- AI-powered content processing and analysis
- Intelligent media analysis with ML models
- Semantic content understanding engine
- Media quality optimization with IA enhancement

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

# IA Processing & Intelligence Components (NEW - Phase 1 Critical)
try:
    from .ai_content_processor import (
        AIContentProcessor, 
        ContentProcessingJob, 
        IAProcessingResult, 
        ProcessingStage
    )
    _ai_content_processor_available = True
except ImportError as e:
    print(f"Warning: AI Content Processor not available: {e}")
    AIContentProcessor = None
    ContentProcessingJob = None
    IAProcessingResult = None
    ProcessingStage = None
    _ai_content_processor_available = False

try:
    from .intelligent_media_analyzer import (
        IntelligentMediaAnalyzer,
        AnalysisResult,
        MediaFeatures,
        AnalysisType,
        ContentCategory
    )
    _intelligent_media_analyzer_available = True
except ImportError as e:
    print(f"Warning: Intelligent Media Analyzer not available: {e}")
    IntelligentMediaAnalyzer = None
    AnalysisResult = None
    MediaFeatures = None
    AnalysisType = None
    ContentCategory = None
    _intelligent_media_analyzer_available = False

try:
    from .content_understanding_engine import (
        ContentUnderstandingEngine,
        SemanticUnderstanding,
        SemanticEntity,
        ContentContext,
        SemanticDepth,
        ContentTheme
    )
    _content_understanding_engine_available = True
except ImportError as e:
    print(f"Warning: Content Understanding Engine not available: {e}")
    ContentUnderstandingEngine = None
    SemanticUnderstanding = None
    SemanticEntity = None
    ContentContext = None
    SemanticDepth = None
    ContentTheme = None
    _content_understanding_engine_available = False

try:
    from .media_quality_optimizer import (
        MediaQualityOptimizer,
        OptimizationResult,
        OptimizationParams,
        QualityMetrics,
        OptimizationType,
        QualityLevel,
        OptimizationStrategy
    )
    _media_quality_optimizer_available = True
except ImportError as e:
    print(f"Warning: Media Quality Optimizer not available: {e}")
    MediaQualityOptimizer = None
    OptimizationResult = None
    OptimizationParams = None
    QualityMetrics = None
    OptimizationType = None
    QualityLevel = None
    OptimizationStrategy = None
    _media_quality_optimizer_available = False

# Media Generation Components (existing - with graceful fallbacks)
AvatarGenerator = None
VoiceGenerator = None
MediaImageGenerator = None
MediaVideoGenerator = None
MediaTextGenerator = None
MediaAudioGenerator = None
MediaGeneratorOrchestrator = None

# Try to import existing components
try:
    from .avatars import AvatarGenerator
except ImportError:
    pass

try:
    from .voice import VoiceGenerator
except ImportError:
    pass

try:
    from .images import MediaImageGenerator
except ImportError:
    pass

try:
    from .videos import MediaVideoGenerator
except ImportError:
    pass

try:
    from .text import MediaTextGenerator
except ImportError:
    pass

try:
    from .audio import MediaAudioGenerator
except ImportError:
    pass

try:
    from .media_generator import MediaGeneratorOrchestrator
except ImportError:
    pass

# Backward compatibility imports (graceful fallbacks)
AvatarGeneratorCompat = None
VoiceGeneratorCompat = None
MediaImageGeneratorCompat = None
MediaVideoGeneratorCompat = None
MediaTextGeneratorCompat = None

try:
    from .avatar_generator import AvatarGenerator as AvatarGeneratorCompat
except ImportError:
    pass

try:
    from .voice_generator import VoiceGenerator as VoiceGeneratorCompat
except ImportError:
    pass

try:
    from .image_generator import MediaImageGenerator as MediaImageGeneratorCompat
except ImportError:
    pass

try:
    from .video_generator import MediaVideoGenerator as MediaVideoGeneratorCompat
except ImportError:
    pass

try:
    from .text_generator import MediaTextGenerator as MediaTextGeneratorCompat
except ImportError:
    pass

__all__ = [
    # IA Processing & Intelligence (NEW - Phase 1 Critical)
    "AIContentProcessor",
    "ContentProcessingJob", 
    "IAProcessingResult", 
    "ProcessingStage",
    "IntelligentMediaAnalyzer",
    "AnalysisResult",
    "MediaFeatures",
    "AnalysisType",
    "ContentCategory",
    "ContentUnderstandingEngine",
    "SemanticUnderstanding",
    "SemanticEntity",
    "ContentContext",
    "SemanticDepth",
    "ContentTheme",
    "MediaQualityOptimizer",
    "OptimizationResult",
    "OptimizationParams",
    "QualityMetrics",
    "OptimizationType",
    "QualityLevel",
    "OptimizationStrategy",
    
    # Media Generation (existing - if available)
    "AvatarGenerator",
    "VoiceGenerator", 
    "MediaImageGenerator",
    "MediaVideoGenerator", 
    "MediaTextGenerator",
    "MediaAudioGenerator",
    "MediaGeneratorOrchestrator",
    
    # Backward compatibility (if available)
    "AvatarGeneratorCompat",
    "VoiceGeneratorCompat",
    "MediaImageGeneratorCompat",
    "MediaVideoGeneratorCompat",
    "MediaTextGeneratorCompat"
]

# Module availability status
def get_module_status():
    """Get availability status of all media module components"""
    return {
        'ia_processing': {
            'ai_content_processor': _ai_content_processor_available,
            'intelligent_media_analyzer': _intelligent_media_analyzer_available,
            'content_understanding_engine': _content_understanding_engine_available,
            'media_quality_optimizer': _media_quality_optimizer_available
        },
        'media_generation': {
            'avatar_generator': AvatarGenerator is not None,
            'voice_generator': VoiceGenerator is not None,
            'image_generator': MediaImageGenerator is not None,
            'video_generator': MediaVideoGenerator is not None,
            'text_generator': MediaTextGenerator is not None,
            'audio_generator': MediaAudioGenerator is not None,
            'orchestrator': MediaGeneratorOrchestrator is not None
        },
        'backward_compatibility': {
            'avatar_generator_compat': AvatarGeneratorCompat is not None,
            'voice_generator_compat': VoiceGeneratorCompat is not None,
            'image_generator_compat': MediaImageGeneratorCompat is not None,
            'video_generator_compat': MediaVideoGeneratorCompat is not None,
            'text_generator_compat': MediaTextGeneratorCompat is not None
        }
    }