"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Module IA processing Ainflue propriétaire
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

AI Processing Module for Ainflue Platform
========================================

Production-ready AI processing module with 53+ specialized agents:
- Computer Vision: Object detection, face recognition, scene analysis
- Natural Language Processing: Sentiment, translation, generation
- Audio Processing: Speech recognition, music analysis, enhancement
- Content Optimization: SEO, engagement prediction, viral analysis
- Multi-modal AI: Cross-domain processing and fusion

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Dev IA + ML Engineer + AI Specialist
"""

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"

# Import main components
from .computer_vision_agents import (
    ObjectDetectionAgent,
    FaceRecognitionAgent,
    SceneAnalysisAgent,
    StyleTransferAgent,
    ImageEnhancementAgent,
    ComputerVisionOrchestrator,
    CVProcessingRequest,
    CVProcessingResult,
    create_computer_vision_app
)

from .nlp_agents import (
    SentimentAnalysisAgent,
    LanguageDetectionAgent,
    ContentGenerationAgent,
    NLPOrchestrator,
    NLPProcessingRequest,
    NLPProcessingResult,
    create_nlp_app
)

from .audio_agents import (
    SpeechRecognitionAgent,
    MusicAnalysisAgent,
    AudioEnhancementAgent,
    AudioOrchestrator,
    AudioProcessingRequest,
    AudioProcessingResult,
    create_audio_app
)

from .service_registry import (
    ServiceRegistryOrchestrator,
    ServiceInstance,
    ServiceRegistrationRequest,
    ServiceDiscoveryRequest,
    ServiceStatus,
    ServiceType,
    create_service_registry_app
)

# Module exports
__all__ = [
    # Computer Vision
    "ObjectDetectionAgent",
    "FaceRecognitionAgent", 
    "SceneAnalysisAgent",
    "StyleTransferAgent",
    "ImageEnhancementAgent",
    "ComputerVisionOrchestrator",
    "CVProcessingRequest",
    "CVProcessingResult",
    "create_computer_vision_app",
    
    # Natural Language Processing
    "SentimentAnalysisAgent",
    "LanguageDetectionAgent",
    "ContentGenerationAgent",
    "NLPOrchestrator",
    "NLPProcessingRequest",
    "NLPProcessingResult",
    "create_nlp_app",
    
    # Audio Processing
    "SpeechRecognitionAgent",
    "MusicAnalysisAgent",
    "AudioEnhancementAgent",
    "AudioOrchestrator",
    "AudioProcessingRequest",
    "AudioProcessingResult",
    "create_audio_app",
    
    # Service Registry
    "ServiceRegistryOrchestrator",
    "ServiceInstance",
    "ServiceRegistrationRequest",
    "ServiceDiscoveryRequest",
    "ServiceStatus",
    "ServiceType",
    "create_service_registry_app",
    
    # Module info
    "__version__",
    "__author__",
    "__email__",
    "__license__"
]

# Module configuration
SUPPORTED_AI_AGENTS = {
    "computer_vision": {
        "object_detection": "YOLO v8 optimized object detection",
        "face_recognition": "ArcFace enterprise face recognition", 
        "scene_analysis": "ResNet advanced scene understanding",
        "style_transfer": "Neural style transfer proprietary",
        "image_enhancement": "ESRGAN super-resolution"
    },
    "nlp": {
        "sentiment_analysis": "BERT-based sentiment analysis",
        "language_detection": "Multi-language detection",
        "content_generation": "GPT-4 content generation"
    },
    "audio": {
        "speech_recognition": "Whisper speech-to-text",
        "music_analysis": "librosa music processing",
        "audio_enhancement": "AI audio enhancement"
    },
    "service_registry": {
        "service_discovery": "Consul-based service discovery",
        "load_balancing": "Intelligent load balancing",
        "health_monitoring": "Real-time health checks"
    }
}

PERFORMANCE_TARGETS = {
    "computer_vision": {
        "object_detection": "<5s",
        "face_recognition": "<3s", 
        "scene_analysis": "<8s",
        "style_transfer": "<20s",
        "image_enhancement": "<15s"
    },
    "processing_limits": {
        "max_image_size": "50MB",
        "max_video_duration": "600s",
        "max_audio_duration": "1800s",
        "concurrent_requests": 1000
    }
}

# Legal notice
LEGAL_NOTICE = """
⚠️  AVERTISSEMENT LÉGAL STRICT:
==============================
Ce module AI Processing est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation commerciale, reproduction ou distribution sans autorisation 
écrite explicite est strictement interdite et entraînera des poursuites légales.

Pour toute demande d'autorisation: mlaiel@live.de
© 2025 Fahed Mlaiel - Tous droits réservés
"""

print(LEGAL_NOTICE)