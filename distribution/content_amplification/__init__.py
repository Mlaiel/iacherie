"""Content Amplification Engine

Advanced content amplification and reach maximization system for the Ainflue platform.
Optimizes organic reach, manages paid boosts, and implements cross-promotion strategies
using AI-powered amplification techniques.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

# Import newly implemented modules
from .amplification_engine import (
    IntelligentAmplificationEngine,
    AmplificationPlan,
    AmplificationResult,
    AmplificationStrategy,
    AmplificationPhase
)

from .boost_optimizer import (
    AdvancedBoostOptimizer,
    BoostCampaign,
    BoostType
)

# Import main engine
from .index import ContentAmplificationEngine

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"

__all__ = [
    # Main Engine
    "ContentAmplificationEngine",
    
    # Amplification Engine
    "IntelligentAmplificationEngine", "AmplificationPlan", "AmplificationResult",
    "AmplificationStrategy", "AmplificationPhase",
    
    # Boost Optimizer
    "AdvancedBoostOptimizer", "BoostCampaign", "BoostType"
]