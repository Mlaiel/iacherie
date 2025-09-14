"""
Model Development Module
Enterprise model development and training infrastructure

Components:
- Distributed model training orchestration
- AutoML and hyperparameter optimization
- Model validation and testing frameworks
- Specialized AI agents for content processing
- Transfer learning and few-shot learning
- Model performance optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .model_training_orchestrator import ModelTrainingOrchestrator
from .hyperparameter_tuner import HyperparameterTuner
from .automl_engine import AutoMLEngine
from .model_evaluation_framework import ModelEvaluationFramework
from .model_testing_suite import ModelTestingSuite
from .audio_engine import AudioEngine
from .prompt_optimization_template import PromptOptimizationTemplate
from .model_explainability import ModelExplainability
from .distributed_training_manager import DistributedTrainingManager
from .transfer_learning_engine import TransferLearningEngine
from .model_validation_framework import ModelValidationFramework
from .ensemble_model_manager import EnsembleModelManager
from .model_performance_optimizer import ModelPerformanceOptimizer
from .few_shot_learning_engine import FewShotLearningEngine
from .incremental_learning_manager import IncrementalLearningManager
from .model_benchmarking_suite import ModelBenchmarkingSuite

__version__ = "1.0.0"
__all__ = [
    "ModelTrainingOrchestrator",
    "HyperparameterTuner",
    "AutoMLEngine", 
    "ModelEvaluationFramework",
    "ModelTestingSuite",
    "AudioEngine",
    "PromptOptimizationTemplate",
    "ModelExplainability",
    "DistributedTrainingManager",
    "TransferLearningEngine",
    "ModelValidationFramework",
    "EnsembleModelManager",
    "ModelPerformanceOptimizer",
    "FewShotLearningEngine",
    "IncrementalLearningManager",
    "ModelBenchmarkingSuite"
]