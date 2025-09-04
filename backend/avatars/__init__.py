"""Advanced 3D Avatar System - Backend Module

Comprehensive 3D avatar generation, animation, and customization system
for the IA Influencer Agent Platform.

This module provides advanced avatar functionality including:
- MetaHuman-style realistic 3D avatars
- Animation and movement systems  
- Dynamic clothing and accessories
- Facial expressions and emotions

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

from .metahuman import MetaHumanGenerator, MetaHumanConfig
from .animation_system import AvatarAnimationSystem, AnimationConfig
from .clothing_system import AvatarClothingSystem, ClothingConfig
from .facial_expressions import FacialExpressionSystem, ExpressionConfig

__all__ = [
    'MetaHumanGenerator',
    'MetaHumanConfig',
    'AvatarAnimationSystem', 
    'AnimationConfig',
    'AvatarClothingSystem',
    'ClothingConfig',
    'FacialExpressionSystem',
    'ExpressionConfig'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"