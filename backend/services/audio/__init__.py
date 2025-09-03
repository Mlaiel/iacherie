"""🎵 Audio Processing Pipeline - Professional Audio Services

Advanced audio processing services for the IA Influencer Agent platform.
Comprehensive pipeline for audio analysis, protection, and distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .processors import (
    VoiceAnalyzer,
    AudioFingerprinter,
    NoiseReducer,
    MasteringEngine
)

from .protection import (
    WatermarkEngine,
    VoiceProtector
)

from .distribution import (
    StreamingOptimizer
)

# Module version
__version__ = "1.0.0"

# Module description
__description__ = "Audio Processing Pipeline for comprehensive audio services"

# Export all main classes
__all__ = [
    # Processors Module
    'VoiceAnalyzer',
    'AudioFingerprinter',
    'NoiseReducer',
    'MasteringEngine',
    
    # Protection Module
    'WatermarkEngine',
    'VoiceProtector',
    
    # Distribution Module
    'StreamingOptimizer'
]