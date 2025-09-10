"""Ainflue Core AI Intelligence - Advanced AI & Machine Learning
===========================================================

Core AI intelligence providing AI models, ML pipelines, neural networks,
deep learning, natural language processing, computer vision, audio AI,
recommendation engines, predictive analytics, and advanced AI capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any

# AI core imports (existing files to be moved here)
try:
    from .ai_model_core import AIModelCore
except ImportError:
    AIModelCore = None

try:
    from .ia_processing_core import IAProcessingCore
except ImportError:
    IAProcessingCore = None

try:
    from .intelligent_analysis_core import IntelligentAnalysisCore
except ImportError:
    IntelligentAnalysisCore = None

try:
    from .ml_pipeline_core import MLPipelineCore
except ImportError:
    MLPipelineCore = None

# New AI core files (to be created)
try:
    from .neural_network_core import NeuralNetworkCore
except ImportError:
    NeuralNetworkCore = None

try:
    from .deep_learning_core import DeepLearningCore
except ImportError:
    DeepLearningCore = None

try:
    from .natural_language_core import NaturalLanguageCore
except ImportError:
    NaturalLanguageCore = None

try:
    from .computer_vision_core import ComputerVisionCore
except ImportError:
    ComputerVisionCore = None

try:
    from .audio_ai_core import AudioAICore
except ImportError:
    AudioAICore = None

try:
    from .recommendation_engine_core import RecommendationEngineCore
except ImportError:
    RecommendationEngineCore = None

try:
    from .predictive_analytics_core import PredictiveAnalyticsCore
except ImportError:
    PredictiveAnalyticsCore = None

try:
    from .anomaly_detection_core import AnomalyDetectionCore
except ImportError:
    AnomalyDetectionCore = None

try:
    from .reinforcement_learning_core import ReinforcementLearningCore
except ImportError:
    ReinforcementLearningCore = None

try:
    from .federated_learning_core import FederatedLearningCore
except ImportError:
    FederatedLearningCore = None

try:
    from .transfer_learning_core import TransferLearningCore
except ImportError:
    TransferLearningCore = None

try:
    from .model_optimization_core import ModelOptimizationCore
except ImportError:
    ModelOptimizationCore = None

try:
    from .ai_explainability_core import AIExplainabilityCore
except ImportError:
    AIExplainabilityCore = None

try:
    from .quantum_ai_core import QuantumAICore
except ImportError:
    QuantumAICore = None

try:
    from .edge_ai_core import EdgeAICore
except ImportError:
    EdgeAICore = None

__all__ = [
    "AIModelCore", "IAProcessingCore", "IntelligentAnalysisCore", "MLPipelineCore",
    "NeuralNetworkCore", "DeepLearningCore", "NaturalLanguageCore",
    "ComputerVisionCore", "AudioAICore", "RecommendationEngineCore",
    "PredictiveAnalyticsCore", "AnomalyDetectionCore", "ReinforcementLearningCore",
    "FederatedLearningCore", "TransferLearningCore", "ModelOptimizationCore",
    "AIExplainabilityCore", "QuantumAICore", "EdgeAICore"
]