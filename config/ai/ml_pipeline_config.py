"""
ML Pipeline Configuration - Enterprise Configuration Management
Enterprise configuration for machine learning pipeline systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)


class PipelineStage(str, Enum):
    """ML pipeline stages"""
    DATA_INGESTION = "data_ingestion"
    DATA_PREPROCESSING = "data_preprocessing"
    FEATURE_EXTRACTION = "feature_extraction"
    MODEL_TRAINING = "model_training"
    MODEL_VALIDATION = "model_validation"
    MODEL_DEPLOYMENT = "model_deployment"
    INFERENCE = "inference"
    MONITORING = "monitoring"


class ModelType(str, Enum):
    """Machine learning model types"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"
    GENERATIVE = "generative"
    REINFORCEMENT = "reinforcement"
    TRANSFORMER = "transformer"
    CNN = "cnn"
    RNN = "rnn"
    ENSEMBLE = "ensemble"


class TrainingMode(str, Enum):
    """Model training modes"""
    BATCH = "batch"
    ONLINE = "online"
    INCREMENTAL = "incremental"
    FEDERATED = "federated"
    TRANSFER = "transfer"
    MULTI_TASK = "multi_task"


class DeploymentStrategy(str, Enum):
    """Model deployment strategies"""
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    A_B_TESTING = "a_b_testing"
    SHADOW = "shadow"
    FEATURE_FLAGS = "feature_flags"


@dataclass
class TrainingConfiguration:
    """Training configuration parameters"""
    batch_size: int
    learning_rate: float
    epochs: int
    validation_split: float
    early_stopping: bool
    patience: int
    optimizer: str
    loss_function: str
    metrics: List[str]
    regularization: Dict[str, Any]


@dataclass
class ModelConfiguration:
    """Model configuration parameters"""
    model_name: str
    model_type: ModelType
    architecture: Dict[str, Any]
    hyperparameters: Dict[str, Any]
    training_config: TrainingConfiguration
    resource_requirements: Dict[str, Any]


@dataclass
class PipelineConfiguration:
    """ML pipeline configuration"""
    pipeline_name: str
    stages: List[PipelineStage]
    dependencies: Dict[str, List[str]]
    resource_allocation: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    retry_policy: Dict[str, Any]


@dataclass
class InferenceConfiguration:
    """Inference configuration parameters"""
    max_batch_size: int
    timeout_seconds: int
    retry_attempts: int
    cache_results: bool
    preprocessing_pipeline: List[str]
    postprocessing_pipeline: List[str]


class MLPipelineSettings:
    """ML pipeline configuration settings"""
    
    def __init__(self):
        # Model Configurations
        self.model_configurations = {
            "content_classifier": ModelConfiguration(
                model_name="content_classifier",
                model_type=ModelType.CLASSIFICATION,
                architecture={
                    "type": "transformer",
                    "layers": 12,
                    "hidden_size": 768,
                    "attention_heads": 12,
                    "dropout": 0.1
                },
                hyperparameters={
                    "max_length": 512,
                    "num_classes": 10,
                    "pretrained_model": "bert-base-uncased"
                },
                training_config=TrainingConfiguration(
                    batch_size=32,
                    learning_rate=2e-5,
                    epochs=10,
                    validation_split=0.2,
                    early_stopping=True,
                    patience=3,
                    optimizer="AdamW",
                    loss_function="CrossEntropyLoss",
                    metrics=["accuracy", "f1_score", "precision", "recall"],
                    regularization={"weight_decay": 0.01, "dropout": 0.1}
                ),
                resource_requirements={
                    "gpu_memory_gb": 8,
                    "cpu_cores": 4,
                    "ram_gb": 16,
                    "storage_gb": 50
                }
            ),
            
            "quality_predictor": ModelConfiguration(
                model_name="quality_predictor",
                model_type=ModelType.REGRESSION,
                architecture={
                    "type": "cnn",
                    "conv_layers": 5,
                    "filters": [64, 128, 256, 512, 1024],
                    "kernel_size": 3,
                    "pooling": "max"
                },
                hyperparameters={
                    "input_size": [224, 224, 3],
                    "output_size": 1,
                    "activation": "relu"
                },
                training_config=TrainingConfiguration(
                    batch_size=64,
                    learning_rate=0.001,
                    epochs=50,
                    validation_split=0.15,
                    early_stopping=True,
                    patience=5,
                    optimizer="Adam",
                    loss_function="MSELoss",
                    metrics=["mae", "rmse", "r2"],
                    regularization={"l2": 0.0001, "dropout": 0.5}
                ),
                resource_requirements={
                    "gpu_memory_gb": 12,
                    "cpu_cores": 8,
                    "ram_gb": 32,
                    "storage_gb": 100
                }
            ),
            
            "recommendation_engine": ModelConfiguration(
                model_name="recommendation_engine",
                model_type=ModelType.RECOMMENDATION,
                architecture={
                    "type": "collaborative_filtering",
                    "embedding_dim": 128,
                    "hidden_layers": [256, 128, 64],
                    "activation": "relu"
                },
                hyperparameters={
                    "num_users": 1000000,
                    "num_items": 100000,
                    "negative_sampling_ratio": 0.1
                },
                training_config=TrainingConfiguration(
                    batch_size=1024,
                    learning_rate=0.01,
                    epochs=20,
                    validation_split=0.1,
                    early_stopping=True,
                    patience=3,
                    optimizer="SGD",
                    loss_function="BPRLoss",
                    metrics=["ndcg", "recall", "precision"],
                    regularization={"l2": 0.001}
                ),
                resource_requirements={
                    "gpu_memory_gb": 16,
                    "cpu_cores": 16,
                    "ram_gb": 64,
                    "storage_gb": 200
                }
            ),
            
            "content_generator": ModelConfiguration(
                model_name="content_generator",
                model_type=ModelType.GENERATIVE,
                architecture={
                    "type": "transformer",
                    "layers": 24,
                    "hidden_size": 1024,
                    "attention_heads": 16,
                    "context_length": 2048
                },
                hyperparameters={
                    "vocab_size": 50000,
                    "temperature": 0.8,
                    "top_k": 50,
                    "top_p": 0.9
                },
                training_config=TrainingConfiguration(
                    batch_size=16,
                    learning_rate=1e-4,
                    epochs=100,
                    validation_split=0.05,
                    early_stopping=False,
                    patience=10,
                    optimizer="AdamW",
                    loss_function="CrossEntropyLoss",
                    metrics=["perplexity", "bleu"],
                    regularization={"weight_decay": 0.01}
                ),
                resource_requirements={
                    "gpu_memory_gb": 32,
                    "cpu_cores": 8,
                    "ram_gb": 128,
                    "storage_gb": 500
                }
            )
        }
        
        # Pipeline Configurations
        self.pipeline_configurations = {
            "training_pipeline": PipelineConfiguration(
                pipeline_name="training_pipeline",
                stages=[
                    PipelineStage.DATA_INGESTION,
                    PipelineStage.DATA_PREPROCESSING,
                    PipelineStage.FEATURE_EXTRACTION,
                    PipelineStage.MODEL_TRAINING,
                    PipelineStage.MODEL_VALIDATION
                ],
                dependencies={
                    "data_preprocessing": ["data_ingestion"],
                    "feature_extraction": ["data_preprocessing"],
                    "model_training": ["feature_extraction"],
                    "model_validation": ["model_training"]
                },
                resource_allocation={
                    "max_concurrent_jobs": 5,
                    "priority_queue": True,
                    "resource_pool": "training_cluster"
                },
                monitoring_config={
                    "metrics_collection": True,
                    "logging_level": "INFO",
                    "alert_thresholds": {
                        "failure_rate": 0.05,
                        "execution_time": 3600
                    }
                },
                retry_policy={
                    "max_retries": 3,
                    "backoff_strategy": "exponential",
                    "retry_delay": 300
                }
            ),
            
            "inference_pipeline": PipelineConfiguration(
                pipeline_name="inference_pipeline",
                stages=[
                    PipelineStage.DATA_PREPROCESSING,
                    PipelineStage.INFERENCE,
                    PipelineStage.MONITORING
                ],
                dependencies={
                    "inference": ["data_preprocessing"],
                    "monitoring": ["inference"]
                },
                resource_allocation={
                    "max_concurrent_requests": 1000,
                    "auto_scaling": True,
                    "resource_pool": "inference_cluster"
                },
                monitoring_config={
                    "real_time_metrics": True,
                    "latency_tracking": True,
                    "throughput_monitoring": True
                },
                retry_policy={
                    "max_retries": 2,
                    "backoff_strategy": "linear",
                    "retry_delay": 100
                }
            )
        }
        
        # Inference Settings
        self.inference_settings = {
            "content_classifier": InferenceConfiguration(
                max_batch_size=64,
                timeout_seconds=30,
                retry_attempts=3,
                cache_results=True,
                preprocessing_pipeline=["tokenization", "normalization"],
                postprocessing_pipeline=["confidence_scoring", "threshold_filtering"]
            ),
            "quality_predictor": InferenceConfiguration(
                max_batch_size=32,
                timeout_seconds=45,
                retry_attempts=2,
                cache_results=True,
                preprocessing_pipeline=["image_resize", "normalization", "augmentation"],
                postprocessing_pipeline=["score_normalization", "confidence_interval"]
            ),
            "recommendation_engine": InferenceConfiguration(
                max_batch_size=128,
                timeout_seconds=10,
                retry_attempts=3,
                cache_results=True,
                preprocessing_pipeline=["user_embedding", "item_embedding"],
                postprocessing_pipeline=["ranking", "diversity_filtering", "explanation_generation"]
            )
        }
        
        # Training Settings
        self.training_settings = {
            "distributed_training": True,
            "mixed_precision": True,
            "gradient_checkpointing": True,
            "data_parallel": True,
            "model_parallel": False,
            "automatic_mixed_precision": True
        }
        
        # Model Management Settings
        self.model_management = {
            "version_control_enabled": True,
            "model_registry": "mlflow",
            "automated_testing": True,
            "performance_monitoring": True,
            "automatic_rollback": True,
            "champion_challenger": True
        }
        
        # Data Pipeline Settings
        self.data_pipeline = {
            "data_validation_enabled": True,
            "schema_evolution": True,
            "data_lineage_tracking": True,
            "feature_store_enabled": True,
            "data_versioning": True,
            "quality_monitoring": True
        }
        
        # Deployment Settings
        self.deployment_settings = {
            "default_strategy": DeploymentStrategy.BLUE_GREEN,
            "health_check_enabled": True,
            "rollback_threshold": 0.95,
            "traffic_splitting": True,
            "canary_percentage": 10,
            "deployment_timeout": 1800
        }
        
        # Monitoring and Observability
        self.monitoring_settings = {
            "model_drift_detection": True,
            "data_drift_detection": True,
            "performance_degradation_alerts": True,
            "bias_monitoring": True,
            "explainability_tracking": True,
            "audit_logging": True
        }
        
        # Resource Management
        self.resource_management = {
            "auto_scaling_enabled": True,
            "resource_quotas": {
                "cpu_cores": 100,
                "gpu_count": 20,
                "memory_gb": 1000,
                "storage_tb": 10
            },
            "cost_optimization": True,
            "spot_instance_usage": True
        }
        
        # Security Settings
        self.security_settings = {
            "model_encryption": True,
            "data_encryption": True,
            "access_control": True,
            "audit_trail": True,
            "vulnerability_scanning": True,
            "secure_inference": True
        }
        
        # Performance Settings
        self.performance_settings = {
            "model_optimization": True,
            "quantization_enabled": True,
            "pruning_enabled": True,
            "knowledge_distillation": True,
            "tensorrt_optimization": True,
            "onnx_conversion": True
        }
    
    def get_model_config(self, model_name: str) -> Optional[ModelConfiguration]:
        """Get model configuration by name"""
        return self.model_configurations.get(model_name)
    
    def get_pipeline_config(self, pipeline_name: str) -> Optional[PipelineConfiguration]:
        """Get pipeline configuration by name"""
        return self.pipeline_configurations.get(pipeline_name)
    
    def get_inference_config(self, model_name: str) -> Optional[InferenceConfiguration]:
        """Get inference configuration for model"""
        return self.inference_settings.get(model_name)
    
    def add_model_config(self, model_name: str, config: ModelConfiguration):
        """Add new model configuration"""
        self.model_configurations[model_name] = config
    
    def get_resource_requirements(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get resource requirements for model"""
        config = self.get_model_config(model_name)
        return config.resource_requirements if config else None
    
    def validate_model_config(self, model_name: str) -> List[str]:
        """Validate model configuration"""
        errors = []
        config = self.get_model_config(model_name)
        
        if not config:
            errors.append(f"Model configuration '{model_name}' not found")
            return errors
        
        # Validate training configuration
        if config.training_config.batch_size <= 0:
            errors.append(f"Invalid batch size for model '{model_name}'")
        if config.training_config.learning_rate <= 0:
            errors.append(f"Invalid learning rate for model '{model_name}'")
        if config.training_config.epochs <= 0:
            errors.append(f"Invalid epochs for model '{model_name}'")
        
        # Validate resource requirements
        if config.resource_requirements.get("gpu_memory_gb", 0) <= 0:
            errors.append(f"Invalid GPU memory requirement for model '{model_name}'")
        
        return errors
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete ML pipeline configuration"""
        errors = []
        
        # Validate all model configurations
        for model_name in self.model_configurations:
            model_errors = self.validate_model_config(model_name)
            errors.extend(model_errors)
        
        # Validate pipeline configurations
        for pipeline_name, config in self.pipeline_configurations.items():
            if not config.stages:
                errors.append(f"Pipeline '{pipeline_name}' has no stages defined")
            
            # Check dependency validity
            for stage, deps in config.dependencies.items():
                if stage not in config.stages:
                    errors.append(f"Pipeline '{pipeline_name}' dependency '{stage}' not in stages")
                for dep in deps:
                    if dep not in config.stages:
                        errors.append(f"Pipeline '{pipeline_name}' dependency '{dep}' not in stages")
        
        return errors


# Global ML pipeline settings instance
ml_pipeline_settings = MLPipelineSettings()

__all__ = [
    "MLPipelineSettings",
    "ml_pipeline_settings",
    "PipelineStage",
    "ModelType",
    "TrainingMode",
    "DeploymentStrategy",
    "TrainingConfiguration",
    "ModelConfiguration",
    "PipelineConfiguration",
    "InferenceConfiguration"
]