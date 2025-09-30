"""
🎯 Frontend Module - Ainflue Platform Enterprise
Frontend infrastructure and client-side components for IA Influencer Agent

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .infrastructure.expert_orchestrator import ExpertOrchestrator
from .infrastructure.performance_optimizer import PerformanceOptimizer
from .infrastructure.ml_audio_processor import MLAudioProcessor
from .business.analytics_orchestrator import AnalyticsOrchestrator

__version__ = "3.1.0"
__all__ = [
    "ExpertOrchestrator",
    "PerformanceOptimizer", 
    "MLAudioProcessor",
    "AnalyticsOrchestrator"
]