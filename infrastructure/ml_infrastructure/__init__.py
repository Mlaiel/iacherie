"""
ML Infrastructure Module - Enterprise Machine Learning Infrastructure
================================================================================

Expert Team: ML Engineer + Lead Dev IA + DevOps + Backend Senior
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🤖 ML Engineer: Model deployment, training infrastructure, MLOps pipelines
🧠 Lead Dev IA: AI model orchestration, performance optimization
⚙️ DevOps: Infrastructure automation, monitoring, scaling
🏗️ Backend Senior: Microservices integration, API management

Production-ready ML infrastructure for Ainflue creator platform supporting:
- Model serving and deployment automation
- GPU cluster management for training and inference
- MLOps pipelines for continuous model improvement
- Model monitoring and performance tracking
- Feature store and data pipeline management
- A/B testing and model versioning
- Distributed training across multiple clusters
"""

from .model_serving_infrastructure import ModelServingInfrastructure
from .gpu_cluster_manager import MLGPUClusterManager
from .mlops_pipeline import MLOpsPipeline
from .model_monitoring import ModelMonitoring
from .model_deployment_manager import ModelDeploymentManager
from .model_performance_tracker import ModelPerformanceTracker
from .model_versioning import ModelVersioning
from .model_registry import ModelRegistry
from .feature_store import FeatureStore
from .training_infrastructure import TrainingInfrastructure
from .automated_retraining import AutomatedRetraining
from .distributed_ml import DistributedML

__all__ = [
    'ModelServingInfrastructure',
    'MLGPUClusterManager',
    'MLOpsPipeline',
    'ModelMonitoring',
    'ModelDeploymentManager',
    'ModelPerformanceTracker',
    'ModelVersioning',
    'ModelRegistry',
    'FeatureStore',
    'TrainingInfrastructure',
    'AutomatedRetraining',
    'DistributedML'
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__description__ = "Enterprise ML infrastructure for production model deployment and management"