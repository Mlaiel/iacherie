"""🚀 ML Training Module - IA Influencer Agent Platform Enterprise
==============================================================
Module: backend/ml/training/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 MODULE D'ENTRAÎNEMENT ML
Composants d'entraînement et d'optimisation des modèles
- AutoML Pipeline automatisé
- Hyperparameter tuning avancé avec Optuna
- Cross-validation et validation robuste
- Gestion des expériences et métriques
"""

from .automl_pipeline import (
    AutoMLPipeline,
    AutoMLConfig,
    AutoMLPipelineFactory,
    ModelType,
    TrainingStatus,
    TrainingMetrics,
    TrainingJob
)

from .hyperparameter_tuning import (
    HyperparameterTuner,
    OptimizationConfig,
    OptimizationResult,
    HyperparameterSpace,
    OptimizationDirection,
    SamplerType,
    PrunerType,
    CommonParameterSpaces
)

from .distributed_training_manager import (
    DistributedTrainingManager,
    DistributedTrainingConfig,
    TrainingStrategy,
    NodeStatus,
    TrainingNode
)

# NEW PHASE 10 & 11 MODULES - Advanced Training Infrastructure
from .continual_learning_engine import (
    ContinualLearningEngine, 
    ContinualLearningConfig,
    TaskMetadata,
    create_continual_learning_engine
)
from .data_augmentation_engine import (
    DataAugmentationEngine,
    AugmentationConfig,
    CreatorProfile,
    create_augmentation_engine
)
from .loss_function_optimizer import (
    LossFunctionOptimizer,
    LossConfig,
    CreatorObjectives,
    CreatorSpecificLossFunction,
    create_loss_optimizer,
    create_creator_objectives
)
from .gradient_optimization_engine import (
    GradientOptimizationEngine,
    OptimizationConfig as GradOptConfig,
    CreatorOptimizationProfile,
    create_optimization_engine,
    create_creator_profile
)
from .model_compression_toolkit import (
    ModelCompressionToolkit,
    CompressionConfig,
    CompressionResults,
    create_compression_toolkit
)
from .training_metrics_collector import (
    TrainingMetricsCollector,
    MetricConfig,
    MetricData,
    create_metrics_collector
)
from .model_convergence_analyzer import (
    ModelConvergenceAnalyzer,
    ConvergenceConfig,
    ConvergenceAnalysis,
    create_convergence_analyzer
)

# NEW PHASE 15 MODULES - Advanced Training Infrastructure
from .learning_rate_scheduler import (
    LearningRateScheduler,
    SchedulerConfig,
    SchedulerType,
    CreatorType as TrainingCreatorType,
    SchedulerState,
    SchedulerMetrics,
    create_learning_rate_scheduler,
    create_creator_optimized_scheduler
)

__all__ = [
    # AutoML Pipeline
    'AutoMLPipeline',
    'AutoMLConfig', 
    'AutoMLPipelineFactory',
    'ModelType',
    'TrainingStatus',
    'TrainingMetrics',
    'TrainingJob',
    
    # Hyperparameter Tuning
    'HyperparameterTuner',
    'OptimizationConfig',
    'OptimizationResult',
    'HyperparameterSpace',
    'OptimizationDirection',
    'SamplerType',
    'PrunerType',
    'CommonParameterSpaces',
    
    # Distributed Training
    'DistributedTrainingManager',
    'DistributedTrainingConfig',
    'TrainingStrategy',
    'NodeStatus',
    'TrainingNode',
    
    # NEW PHASE 10 & 11 - Advanced Training Infrastructure
    'ContinualLearningEngine',
    'ContinualLearningConfig',
    'TaskMetadata',
    'create_continual_learning_engine',
    'DataAugmentationEngine',
    'AugmentationConfig',
    'CreatorProfile',
    'create_augmentation_engine',
    'LossFunctionOptimizer',
    'LossConfig',
    'CreatorObjectives',
    'CreatorSpecificLossFunction',
    'create_loss_optimizer',
    'create_creator_objectives',
    'GradientOptimizationEngine',
    'GradOptConfig',
    'CreatorOptimizationProfile',
    'create_optimization_engine',
    'create_creator_profile',
    'ModelCompressionToolkit',
    'CompressionConfig',
    'CompressionResults',
    'create_compression_toolkit',
    'TrainingMetricsCollector',
    'MetricConfig',
    'MetricData',
    'create_metrics_collector',
    'ModelConvergenceAnalyzer',
    'ConvergenceConfig',
    'ConvergenceAnalysis',
    'create_convergence_analyzer',
    
    # NEW PHASE 15 - Advanced Training Infrastructure
    'LearningRateScheduler',
    'SchedulerConfig',
    'SchedulerType',
    'TrainingCreatorType',
    'SchedulerState',
    'SchedulerMetrics',
    'create_learning_rate_scheduler',
    'create_creator_optimized_scheduler'
]

# Version du module
__version__ = "1.0.0"

# Metadata
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. Tous droits réservés."