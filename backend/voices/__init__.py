"""AI Voice System - Backend Voice Generation Modules

Comprehensive voice generation system with:
- Voice bank with 1000+ voices
- Accent generation and synthesis
- Emotional voice modulation
- Age-specific voice synthesis
- Celebrity voice cloning
- Enterprise Voice Business Logic System

Enterprise Voice Business Logic Components:
- Creator Voice Content Intelligence Engine
- Voice Content Business Logic Orchestrator
- Creator Voice Performance Analytics
- Voice Content Monetization Engine

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Core voice generation modules
from .voice_bank import VoiceBank, VoiceBankManager
from .accent_generator import AccentGenerator
from .emotion_voice import EmotionVoiceGenerator
from .age_voice import AgeVoiceGenerator
from .celebrity_cloner import CelebrityVoiceCloner

# Enterprise Voice Business Logic modules
from .creator_voice_intelligence import (
    CreatorVoiceIntelligenceEngine,
    CreatorType,
    VoiceContentType,
    VoiceAnalysisResult,
    CreatorVoiceProfile
)
from .voice_content_orchestrator import (
    VoiceContentOrchestrator,
    WorkflowStage,
    BusinessLogicTier,
    VoiceContentWorkflow
)
from .creator_voice_analytics import (
    CreatorVoiceAnalytics,
    AnalyticsMetric,
    PerformanceMetric,
    AnalyticsSnapshot,
    ContentPerformanceAnalysis
)
from .voice_monetization_engine import (
    VoiceContentMonetizationEngine,
    RevenueStream,
    MonetizationStrategy,
    RevenueOpportunity,
    PricingOptimization
)

__all__ = [
    # Core voice modules
    'VoiceBank',
    'VoiceBankManager',
    'AccentGenerator',
    'EmotionVoiceGenerator',
    'AgeVoiceGenerator',
    'CelebrityVoiceCloner',
    
    # Enterprise voice business logic
    'CreatorVoiceIntelligenceEngine',
    'CreatorType',
    'VoiceContentType',
    'VoiceAnalysisResult',
    'CreatorVoiceProfile',
    'VoiceContentOrchestrator',
    'WorkflowStage',
    'BusinessLogicTier',
    'VoiceContentWorkflow',
    'CreatorVoiceAnalytics',
    'AnalyticsMetric',
    'PerformanceMetric',
    'AnalyticsSnapshot',
    'ContentPerformanceAnalysis',
    'VoiceContentMonetizationEngine',
    'RevenueStream',
    'MonetizationStrategy',
    'RevenueOpportunity',
    'PricingOptimization'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"