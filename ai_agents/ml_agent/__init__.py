"""
ML Agent Module - Advanced Machine Learning & AI Operations System

Industrial-grade machine learning operations, model training, inference, and optimization system.
Handles ML pipelines, model versioning, automated training, and performance optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is STRICTLY PROHIBITED and will result in legal action.

ALL RIGHTS RESERVED - FAHED MLAIEL ©2025

🎯 BUSINESS LOGIC INTEGRATION:
Creator Upload → AI/ML Processing → Feature Extraction → Model Training
→ Model Optimization → Deployment → Performance Monitoring → Continuous Learning

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

# Core ML Agent Components
from .ml_agent import MLAgent, MLAgentManager
from .model_trainer import ModelTrainer, TrainingPipeline, TrainingStatus
from .model_inference import ModelInference, BatchProcessor, InferenceEngine
from .model_optimizer import ModelOptimizer, PerformanceTuner, OptimizationStrategy
from .feature_extractor import FeatureExtractor, DataPreprocessor, FeatureEngineer
from .model_registry import ModelRegistry, ModelVersion, ModelMetadata

# Advanced ML Components
from .pipeline_manager import (
    MLPipelineManager, PipelineDefinition, PipelineExecution,
    PipelineStep, PipelineStatus, pipeline_manager
)
from .experiment_manager import (
    MLExperimentTracker, ExperimentConfig, ExperimentResult,
    ExperimentSummary, ExperimentType, experiment_tracker
)
from .deployment_manager import (
    MLModelDeploymentManager, DeploymentConfig, ModelDeployment,
    DeploymentStatus, DeploymentEnvironment, deployment_manager
)
from .performance_monitor import (
    MLPerformanceMonitor, PerformanceThresholds, MonitoringAlert,
    DriftReport, ModelQualityReport, AlertSeverity, ml_performance_monitor
)

# Central orchestration and access
from .index import (
    MLServiceOrchestrator, MLOperationRequest, ServiceHealth,
    MLServiceType, ServiceStatus, ml_orchestrator,
    process_training_request, process_inference_request,
    process_optimization_request, extract_features,
    get_ml_health, get_ml_metrics
)

__all__ = [
    # Core Components
    'MLAgent',
    'MLAgentManager', 
    'ModelTrainer',
    'TrainingPipeline',
    'TrainingStatus',
    'ModelInference',
    'BatchProcessor',
    'InferenceEngine',
    'ModelOptimizer',
    'PerformanceTuner',
    'OptimizationStrategy',
    'FeatureExtractor',
    'DataPreprocessor',
    'FeatureEngineer',
    'ModelRegistry',
    'ModelVersion',
    'ModelMetadata',
    
    # Advanced Components
    'MLPipelineManager',
    'PipelineDefinition',
    'PipelineExecution',
    'PipelineStep',
    'PipelineStatus',
    'pipeline_manager',
    'MLExperimentTracker',
    'ExperimentConfig',
    'ExperimentResult',
    'ExperimentSummary',
    'ExperimentType',
    'experiment_tracker',
    'MLModelDeploymentManager',
    'DeploymentConfig',
    'ModelDeployment',
    'DeploymentStatus',
    'DeploymentEnvironment',
    'deployment_manager',
    'MLPerformanceMonitor',
    'PerformanceThresholds',
    'MonitoringAlert',
    'DriftReport',
    'ModelQualityReport',
    'AlertSeverity',
    'ml_performance_monitor',
    
    # Orchestration Components
    'MLServiceOrchestrator',
    'MLOperationRequest',
    'ServiceHealth',
    'MLServiceType',
    'ServiceStatus',
    'ml_orchestrator',
    'process_training_request',
    'process_inference_request',
    'process_optimization_request',
    'extract_features',
    'get_ml_health',
    'get_ml_metrics'
]
