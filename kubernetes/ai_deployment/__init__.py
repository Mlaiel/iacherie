"""
AI Deployment Module
Enterprise AI model deployment and management system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

from .model_serving import (
    ModelServer,
    ModelConfig,
    ModelDeployment,
    DeploymentStrategy,
    ScalingPolicy,
    HealthCheck
)

from .training_pipeline import (
    TrainingPipeline,
    TrainingConfig,
    DatasetConfig,
    ModelConfig as TrainingModelConfig,
    OptimizationConfig,
    ValidationConfig,
    ExperimentConfig,
    TrainingStatus,
    DataProcessingStep,
    ModelValidationStep,
    ExperimentTracking,
    HyperparameterOptimization
)

from .edge_computing_deployment import (
    EdgeComputingDeployment,
    EdgeDeviceConfig,
    EdgeDeploymentConfig,
    EdgeDevice,
    EdgeCluster
)

from .federated_learning_deployment import (
    FederatedLearningDeployment,
    FederatedConfig,
    ClientConfig,
    FederatedRound,
    AggregationStrategy,
    PrivacyMechanism
)

from .mlops_pipeline_deployment import (
    MLOpsPipelineDeployment,
    MLOpsPipelineConfig,
    PipelineStage,
    ModelRegistry,
    FeatureStore,
    ExperimentTracking as MLOpsExperimentTracking
)

from .creative_ai_deployment import (
    CreativeAIDeployment,
    CreativeAIConfig,
    CreativeAIType,
    CreativeModality,
    CreativeQuality,
    CreativeStyle
)

from .conversational_ai_deployment import (
    ConversationalAIDeployment,
    ConversationalAIConfig,
    ConversationalAIType,
    ConversationMode,
    DialogueStrategy,
    PersonalityType,
    ContextAwareness
)

from .computer_vision_ai_deployment import (
    ComputerVisionAIDeployment,
    ComputerVisionAIConfig,
    ComputerVisionAIType,
    VisualModality,
    ProcessingMode,
    QualityLevel,
    OutputFormat
)

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."

# AI deployment components
from .model_serving import ModelServingDeployment
from .training_pipeline import TrainingPipelineDeployment
from .inference_engine import InferenceEngineDeployment
from .ml_orchestrator import MLOrchestrator
from .model_registry_deployment import ModelRegistryDeployment
from .feature_store_deployment import FeatureStoreDeployment
from .ai_model_optimizer import AIModelOptimizer
from .distributed_training_manager import DistributedTrainingManager
from .content_analysis_deployment import ContentAnalysisDeployment
from .fingerprinting_deployment import FingerprintingDeployment
from .recommendation_engine_deployment import RecommendationEngineDeployment
from .auto_scaling_manager import AutoScalingManager
from .edge_computing_deployment import EdgeComputingDeployment
from .federated_learning_deployment import FederatedLearningDeployment
from .mlops_pipeline_deployment import MLOpsPipelineDeployment
from .creative_ai_deployment import CreativeAIDeployment
from .conversational_ai_deployment import ConversationalAIDeployment
from .computer_vision_ai_deployment import ComputerVisionAIDeployment
from .index import AIDeploymentManager

__all__ = [
    "ModelServingDeployment",
    "TrainingPipelineDeployment", 
    "InferenceEngineDeployment",
    "MLOrchestrator",
    "ModelRegistryDeployment",
    "FeatureStoreDeployment",
    "AIModelOptimizer",
    "DistributedTrainingManager",
    "ContentAnalysisDeployment",
    "FingerprintingDeployment",
    "RecommendationEngineDeployment",
    "AutoScalingManager",
    "EdgeComputingDeployment",
    "FederatedLearningDeployment",
    "MLOpsPipelineDeployment",
    "CreativeAIDeployment",
    "ConversationalAIDeployment", 
    "ComputerVisionAIDeployment",
    "AIDeploymentManager"
]
