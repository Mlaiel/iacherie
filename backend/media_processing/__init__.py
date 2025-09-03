"""Media Processing Module

Advanced multi-format media processing capabilities including audio, video, image optimization,
format conversion, and quality analysis for content creators and influencers.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

from .audio_processor import AudioProcessor
from .video_processor import VideoProcessor
from .image_optimizer import ImageOptimizer
from .format_converter import FormatConverter
from .quality_analyzer import QualityAnalyzer

__all__ = [
    'AudioProcessor',
    'VideoProcessor', 
    'ImageOptimizer',
    'FormatConverter',
    'QualityAnalyzer'
]

__version__ = "1.0.0"