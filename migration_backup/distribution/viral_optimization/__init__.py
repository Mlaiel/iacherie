"""Viral Optimization Engine

Advanced ML-powered viral content optimization system for the Ainflue platform.
Predicts and optimizes content virality potential across all social platforms
using cutting-edge machine learning algorithms and real-time trend analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de

TEAM SPECIALTIES:
- Lead AI Engineer: Fahed Mlaiel (mlaiel@live.de)
- ML Engineer: Fahed Mlaiel (mlaiel@live.de)
- Viral Optimization Specialist: Fahed Mlaiel (mlaiel@live.de)
- Data Science Expert: Fahed Mlaiel (mlaiel@live.de)
- Social Media Algorithm Analyst: Fahed Mlaiel (mlaiel@live.de)
"""

from .viral_predictor import (
    ViralPredictor,
    ViralityScore,
    ContentFeatures,
    PredictionModel
)
from .trend_analyzer import (
    TrendAnalyzer,
    TrendSignal,
    TrendCategory,
    TrendStrength
)
from .momentum_tracker import (
    MomentumTracker,
    MomentumScore,
    VelocityMetrics,
    AccelerationPoints
)
from .influence_mapper import (
    InfluenceMapper,
    InfluenceNetwork,
    InfluenceScore,
    NetworkTopology
)
from .cascade_optimizer import (
    CascadeOptimizer,
    CascadeStrategy,
    PropagationPath,
    OptimalSequence
)
from .timing_oracle import (
    TimingOracle,
    OptimalTimestamp,
    TimingStrategy,
    PlatformTiming
)
from .virality_amplifier import (
    ViralityAmplifier,
    AmplificationStrategy,
    BoostFactors,
    AmplificationResults
)
from .network_dynamics import (
    NetworkDynamics,
    DynamicsModel,
    NetworkState,
    PropagationMetrics
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Viral Predictor
    "ViralPredictor",
    "ViralityScore",
    "ContentFeatures",
    "PredictionModel",
    # Trend Analyzer
    "TrendAnalyzer",
    "TrendSignal",
    "TrendCategory",
    "TrendStrength",
    # Momentum Tracker
    "MomentumTracker",
    "MomentumScore",
    "VelocityMetrics",
    "AccelerationPoints",
    # Influence Mapper
    "InfluenceMapper",
    "InfluenceNetwork",
    "InfluenceScore",
    "NetworkTopology",
    # Cascade Optimizer
    "CascadeOptimizer",
    "CascadeStrategy",
    "PropagationPath",
    "OptimalSequence",
    # Timing Oracle
    "TimingOracle",
    "OptimalTimestamp",
    "TimingStrategy",
    "PlatformTiming",
    # Virality Amplifier
    "ViralityAmplifier",
    "AmplificationStrategy",
    "BoostFactors",
    "AmplificationResults",
    # Network Dynamics
    "NetworkDynamics",
    "DynamicsModel",
    "NetworkState",
    "PropagationMetrics"
]