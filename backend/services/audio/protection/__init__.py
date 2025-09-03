"""Audio Protection Module

Advanced audio protection components for watermarking and voice protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .watermark_engine import WatermarkEngine
from .voice_protection import VoiceProtection

__all__ = [
    'WatermarkEngine',
    'VoiceProtection',
]