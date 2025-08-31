"""Neural Networks Module for IA-Influencer-Agent

Advanced neural network architectures for content processing, analysis, and generation.
Supports multi-modal content understanding and creator assistance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING / AVERTISSEMENT LÉGAL ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
Toute utilisation non autorisée est strictement interdite.
"""from .transformer_models import (
    ContentTransformer,
    MultiModalTransformer,
    AudioTransformer,
    VideoTransformer,
    TextTransformer,
    CreatorPersonalityTransformer
)

from .content_understanding import (
    ContentUnderstandingNetwork,
    SemanticAnalysisNetwork,
    EmotionRecognitionNetwork,
    StyleAnalysisNetwork,
    QualityAssessmentNetwork
)

from .generative_models import (
    ContentGeneratorNetwork,
    AudioGeneratorNetwork,
    TextGeneratorNetwork,
    CoverArtGeneratorNetwork,
    ThumbnailGeneratorNetwork
)

from .recommendation_networks import (
    CollaborationRecommendationNetwork,
    ContentRecommendationNetwork,
    AudienceTargetingNetwork,
    TrendPredictionNetwork
)

from .protection_networks import (
    ContentFingerprintingNetwork,
    PlagiarismDetectionNetwork,
    DeepfakeDetectionNetwork,
    CopyrightProtectionNetwork
)

from .optimization_networks import (
    SEOOptimizationNetwork,
    MonetizationOptimizationNetwork,
    EngagementOptimizationNetwork,
    PerformancePredictionNetwork
)

from .base_networks import (
    BaseNeuralNetwork,
    NetworkConfig,
    TrainingConfig,
    InferenceEngine,
    ModelRegistry
)

from .config import (
    NeuralNetworkConfig,
    TransformerNetworkConfig,
    ContentProtectionConfig,
    OptimizationNetworkConfig,
    ConfigFactory,
    PRODUCTION_CONFIG,
    DEVELOPMENT_CONFIG,
    ENTERPRISE_CONFIG
)

from .utils import (
    ModelMetrics,
    DeviceManager,
    DataPreprocessor,
    ModelOptimizer,
    PerformanceProfiler,
    ContentAnalyzer,
    device_manager,
    profiler
)

from .deployment import (
    ProductionDeploymentManager,
    DeploymentStatus,
    ServiceTier,
    DeploymentMetrics,
    initialize_production_deployment,
    deployment_manager
)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    # Transformer Models
    "ContentTransformer",
    "MultiModalTransformer", 
    "AudioTransformer",
    "VideoTransformer",
    "TextTransformer",
    "CreatorPersonalityTransformer",
    
    # Content Understanding
    "ContentUnderstandingNetwork",
    "SemanticAnalysisNetwork",
    "EmotionRecognitionNetwork", 
    "StyleAnalysisNetwork",
    "QualityAssessmentNetwork",
    
    # Generative Models
    "ContentGeneratorNetwork",
    "AudioGeneratorNetwork",
    "TextGeneratorNetwork",
    "CoverArtGeneratorNetwork",
    "ThumbnailGeneratorNetwork",
    
    # Recommendation Systems
    "CollaborationRecommendationNetwork",
    "ContentRecommendationNetwork",
    "AudienceTargetingNetwork", 
    "TrendPredictionNetwork",
    
    # Protection Networks
    "ContentFingerprintingNetwork",
    "PlagiarismDetectionNetwork",
    "DeepfakeDetectionNetwork",
    "CopyrightProtectionNetwork",
    
    # Optimization Networks  
    "SEOOptimizationNetwork",
    "MonetizationOptimizationNetwork",
    "EngagementOptimizationNetwork",
    "PerformancePredictionNetwork",
    
    # Base Infrastructure
    "BaseNeuralNetwork",
    "NetworkConfig",
    "TrainingConfig", 
    "InferenceEngine",
    "ModelRegistry",
    
    # Configuration Management
    "NeuralNetworkConfig",
    "TransformerNetworkConfig",
    "ContentProtectionConfig",
    "OptimizationNetworkConfig",
    "ConfigFactory",
    "PRODUCTION_CONFIG",
    "DEVELOPMENT_CONFIG",
    "ENTERPRISE_CONFIG",
    
    # Utilities & Tools
    "ModelMetrics",
    "DeviceManager",
    "DataPreprocessor", 
    "ModelOptimizer",
    "PerformanceProfiler",
    "ContentAnalyzer",
    "device_manager",
    "profiler",
    
    # Production Deployment
    "ProductionDeploymentManager",
    "DeploymentStatus",
    "ServiceTier",
    "DeploymentMetrics", 
    "initialize_production_deployment",
    "deployment_manager"
]

# Module configuration
NEURAL_NETWORKS_CONFIG = {
    "supported_frameworks": ["PyTorch", "TensorFlow", "Transformers"],
    "device_support": ["CPU", "CUDA", "MPS"],
    "model_formats": ["ONNX", "TorchScript", "SavedModel"],
    "optimization_levels": ["O1", "O2", "O3"],
    "precision_modes": ["FP32", "FP16", "INT8"]
}
