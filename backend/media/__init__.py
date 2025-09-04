"""Backend Media Generation Module

Consolidated media generators for all content types including:
- Avatar generation (8 types)
- Voice synthesis (6 types) 
- Image generation (10 types)
- Video generation (7 types)
- Audio generation (8 types)
- Text generation (4 types)
- Media orchestration

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

# New consolidated imports (target files)
from .avatars import AvatarGenerator
from .voice import VoiceGenerator  
from .images import MediaImageGenerator
from .videos import MediaVideoGenerator
from .text import MediaTextGenerator
from .audio import MediaAudioGenerator
from .media_generator import MediaGeneratorOrchestrator

# Backward compatibility imports (original files)
from .avatar_generator import AvatarGenerator as AvatarGeneratorCompat
from .voice_generator import VoiceGenerator as VoiceGeneratorCompat
from .image_generator import MediaImageGenerator as MediaImageGeneratorCompat
from .video_generator import MediaVideoGenerator as MediaVideoGeneratorCompat
from .text_generator import MediaTextGenerator as MediaTextGeneratorCompat

__all__ = [
    # New consolidated exports (6 generators + orchestrator)
    "AvatarGenerator",
    "VoiceGenerator", 
    "MediaImageGenerator",
    "MediaVideoGenerator", 
    "MediaTextGenerator",
    "MediaAudioGenerator",
    "MediaGeneratorOrchestrator",
    
    # Backward compatibility
    "AvatarGeneratorCompat",
    "VoiceGeneratorCompat",
    "MediaImageGeneratorCompat",
    "MediaVideoGeneratorCompat",
    "MediaTextGeneratorCompat"
]