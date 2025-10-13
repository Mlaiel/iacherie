"""Advanced Enhancement IA Module
AI-powered multimedia enhancement with upscaling, restoration, and quality improvement.

Project Team: Lead AI Developer + Backend Senior Engineer + ML Engineer + 
              Database Administrator + Security Expert + Microservices Architect +
              Multimedia Processing Specialist + DevOps Engineer + AI Prompt Engineer

Created by: Fahed Mlaiel <mlaiel@live.de>

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Any unauthorized use, reproduction, 
distribution, or modification without written permission from Fahed Mlaiel 
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full 
extent of the law. All rights reserved.

Contact: mlaiel@live.de for licensing and authorization inquiries.
"""

from .audio_enhancement import AudioEnhancementEngine
from .video_enhancement import VideoEnhancementEngine
from .image_enhancement import ImageEnhancementEngine
from .ai_upscaling import AIUpscalingEngine
from .color_enhancement import ColorEnhancementEngine
from .noise_reduction import NoiseReductionEngine
from .sharpness_enhancement import SharpnessEnhancementEngine
from .contrast_optimization import ContrastOptimizationEngine
from .frame_interpolation import FrameInterpolationEngine
from .audio_restoration import AudioRestorationEngine
from .dynamic_range_enhancement import DynamicRangeEnhancementEngine
from .ai_filter_engine import AIFilterEngine
from .enhancement_pipeline import EnhancementPipeline

__version__ = "3.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "AudioEnhancementEngine",
    "VideoEnhancementEngine", 
    "ImageEnhancementEngine",
    "AIUpscalingEngine",
    "ColorEnhancementEngine",
    "NoiseReductionEngine",
    "SharpnessEnhancementEngine",
    "ContrastOptimizationEngine",
    "FrameInterpolationEngine",
    "AudioRestorationEngine",
    "DynamicRangeEnhancementEngine",
    "AIFilterEngine",
    "EnhancementPipeline"
]