"""🛡️ Audio Protection Module - Content Protection System

Advanced audio protection components for watermarking and voice protection
against unauthorized use and cloning.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .watermark_engine import WatermarkEngine
from .voice_protection import VoiceProtector

__all__ = [
    'WatermarkEngine',
    'VoiceProtector'
]