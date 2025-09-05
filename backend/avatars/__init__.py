"""Advanced 3D Avatar System - Backend Module

Comprehensive 3D avatar generation, animation, and customization system
for the IA Influencer Agent Platform.

This module provides advanced avatar functionality including:
- MetaHuman-style realistic 3D avatars
- AI-driven personality and behavior systems
- High-performance rendering engine
- Animation and movement systems  
- Dynamic clothing and accessories
- Facial expressions and emotions
- Monetization and social features
- Multi-platform distribution

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

STRICT COPYRIGHT NOTICE:
This code belongs exclusively to Fahed Mlaiel. Unauthorized use prohibited.
"""

# Core avatar generation and management
from .metahuman import MetaHumanGenerator, MetaHumanConfig
from .animation_system import AvatarAnimationSystem, AnimationConfig
from .clothing_system import AvatarClothingSystem, ClothingConfig
from .facial_expressions import FacialExpressionSystem, ExpressionConfig

# Advanced avatar systems
from .avatar_factory import AvatarFactory, AvatarBuilder, AvatarTemplate, AvatarSpec, avatar_factory
from .avatar_intelligence import AvatarPersonality, EmotionalIntelligence, BehaviorEngine, InteractionManager
from .avatar_rendering import RenderingEngine, MaterialManager, LightingSystem, PerformanceOptimizer
from .avatar_monetization import AvatarCommerce, DigitalAssetManager, NFTIntegration, RevenueTracker
from .avatar_social import AvatarSocialNetwork, CollaborationEngine, AvatarMatching, CommunityManager
from .avatar_performance import PerformanceAnalytics, EngagementTracker, ViralPredictor, OptimizationSuggester
from .avatar_multiplatform import PlatformAdapter, FormatConverter, QualityScaler, PlatformOptimizer

__all__ = [
    # Core systems
    'MetaHumanGenerator',
    'MetaHumanConfig',
    'AvatarAnimationSystem', 
    'AnimationConfig',
    'AvatarClothingSystem',
    'ClothingConfig',
    'FacialExpressionSystem',
    'ExpressionConfig',
    # Advanced systems
    'AvatarFactory',
    'AvatarBuilder',
    'AvatarTemplate',
    'AvatarSpec',
    'avatar_factory',
    'AvatarPersonality',
    'EmotionalIntelligence',
    'BehaviorEngine',
    'InteractionManager',
    'RenderingEngine',
    'MaterialManager',
    'LightingSystem',
    'PerformanceOptimizer',
    # Monetization and business
    'AvatarCommerce',
    'DigitalAssetManager',
    'NFTIntegration',
    'RevenueTracker',
    # Social and collaboration
    'AvatarSocialNetwork',
    'CollaborationEngine',
    'AvatarMatching',
    'CommunityManager',
    # Performance and analytics
    'PerformanceAnalytics',
    'EngagementTracker',
    'ViralPredictor',
    'OptimizationSuggester',
    # Multi-platform distribution
    'PlatformAdapter',
    'FormatConverter',
    'QualityScaler',
    'PlatformOptimizer'
]

__version__ = "2.2.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Global configuration for avatar module
AVATAR_CONFIG = {
    'quality_presets': {
        'preview': {'quality': 'low', 'fps_target': 30},
        'standard': {'quality': 'medium', 'fps_target': 60},
        'premium': {'quality': 'high', 'fps_target': 60},
        'enterprise': {'quality': 'ultra', 'fps_target': 60}
    },
    'default_templates': [
        'influencer', 'musician', 'photographer', 'fashion_model',
        'fitness_coach', 'chef', 'artist', 'business_professional'
    ],
    'supported_formats': ['fbx', 'gltf', 'vrm', 'obj', 'dae'],
    'max_concurrent_avatars': 10,
    'cache_enabled': True,
    'performance_monitoring': True
}