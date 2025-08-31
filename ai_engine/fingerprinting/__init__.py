"""AI Engine Fingerprinting Module
Advanced multi-modal content fingerprinting with ML-powered similarity matching.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .audio_fingerprint_engine import AudioFingerprintEngine

from .video_fingerprint_engine import VideoFingerprintEngine  
from .image_fingerprint_engine import ImageFingerprintEngine

from .text_fingerprint_engine import TextFingerprintEngine

from .vector_matching_engine import VectorMatchingEngine

__all__ = [
    'AudioFingerprintEngine',
    'VideoFingerprintEngine',
    'ImageFingerprintEngine', 
    'TextFingerprintEngine',
    'VectorMatchingEngine'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"