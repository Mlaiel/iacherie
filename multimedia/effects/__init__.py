"""Advanced Creative Effects Module
Professional creative effects and filters for multimedia content.

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

from .audio_effects import AudioEffectsEngine
from .video_effects import VideoEffectsEngine
from .image_effects import ImageEffectsEngine
from .ai_style_transfer import AIStyleTransferEngine
from .color_grading import ColorGradingEngine
from .motion_effects import MotionEffectsEngine
from .particle_effects import ParticleEffectsEngine
from .lighting_effects import LightingEffectsEngine
from .blur_effects import BlurEffectsEngine
from .vintage_effects import VintageEffectsEngine
from .artistic_filters import ArtisticFiltersEngine
from .instagram_filters import InstagramFiltersEngine
from .custom_effect_engine import CustomEffectEngine

__version__ = "3.1.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "AudioEffectsEngine",
    "VideoEffectsEngine", 
    "ImageEffectsEngine",
    "AIStyleTransferEngine",
    "ColorGradingEngine",
    "MotionEffectsEngine",
    "ParticleEffectsEngine",
    "LightingEffectsEngine",
    "BlurEffectsEngine",
    "VintageEffectsEngine",
    "ArtisticFiltersEngine",
    "InstagramFiltersEngine",
    "CustomEffectEngine"
]