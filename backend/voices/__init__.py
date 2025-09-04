"""AI Voice System - Backend Voice Generation Modules

Comprehensive voice generation system with:
- Voice bank with 1000+ voices
- Accent generation and synthesis
- Emotional voice modulation
- Age-specific voice synthesis
- Celebrity voice cloning

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .voice_bank import VoiceBank, VoiceBankManager
from .accent_generator import AccentGenerator
from .emotion_voice import EmotionVoiceGenerator
from .age_voice import AgeVoiceGenerator
from .celebrity_cloner import CelebrityVoiceCloner

__all__ = [
    'VoiceBank',
    'VoiceBankManager',
    'AccentGenerator',
    'EmotionVoiceGenerator',
    'AgeVoiceGenerator',
    'CelebrityVoiceCloner'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"