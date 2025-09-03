"""🎵 Audio Processing Pipeline

Advanced audio processing pipeline with AI-powered analysis, protection, and optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .processors.voice_analyzer import VoiceAnalyzer
from .processors.audio_fingerprint import AudioFingerprint
from .processors.noise_reduction import NoiseReduction
from .processors.mastering_engine import MasteringEngine

from .protection.watermark_engine import WatermarkEngine
from .protection.voice_protection import VoiceProtection

from .distribution.streaming_optimizer import StreamingOptimizer

__all__ = [
    # Processors
    'VoiceAnalyzer',
    'AudioFingerprint', 
    'NoiseReduction',
    'MasteringEngine',
    
    # Protection
    'WatermarkEngine',
    'VoiceProtection',
    
    # Distribution
    'StreamingOptimizer',
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"