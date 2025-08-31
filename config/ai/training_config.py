"""Model Training Configuration for IA-Influencer Agent Platform
=============================================================

Professional AI/ML Model Training and Fine-tuning configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

STRICT COPYRIGHT NOTICE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or reverse engineering
without explicit written permission is STRICTLY PROHIBITED and will be
prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseSettings, validator
from enum import Enum
from dataclasses import dataclass, field
import os


class TrainingMode(str, Enum):
    """Training modes for model development."""    
    SCRATCH = "scratch"
    FINE_TUNING = "fine_tuning"
    TRANSFER_LEARNING = "transfer_learning"
    INCREMENTAL = "incremental"
    DISTILLATION = "distillation"
    MULTI_TASK = "multi_task"
    FEW_SHOT = "few_shot"
    ZERO_SHOT = "zero_shot"


class OptimizationStrategy(str, Enum):
    """Optimization strategies for training."""    
    ADAM = "adam"
    ADAMW = "adamw"
    SGD = "sgd"
    RMSPROP = "rmsprop"
    ADAGRAD = "adagrad"
    ADADELTA = "adadelta"
    ADAMAX = "adamax"


class SchedulerType(str, Enum):
    """Learning rate scheduler types."""    
    COSINE = "cosine"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    STEP = "step"
    PLATEAU = "plateau"
    CYCLIC = "cyclic"
    ONE_CYCLE = "one_cycle"


@dataclass
class TrainingHyperparameters:
    """Hyperparameters for model training."""    
    learning_rate: float = 1e-4
    batch_size: int = 32
    epochs: int = 100
    warmup_steps: int = 1000
    weight_decay: float = 0.01
    gradient_clip_norm: float = 1.0
    dropout_rate: float = 0.1
    label_smoothing: float = 0.0
    early_stopping_patience: int = 10
    validation_split: float = 0.2
    test_split: float = 0.1
    optimizer: OptimizationStrategy = OptimizationStrategy.ADAMW
    scheduler: SchedulerType = SchedulerType.COSINE
    mixed_precision: bool = True
    gradient_accumulation_steps: int = 1
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrainingSpec:
    """Complete training specification for a model."""    
    model_name: str
    task_type: str
    training_mode: TrainingMode
    base_model: Optional[str] = None
    dataset_path: str = ""
    output_dir: str = ""
    hyperparameters: TrainingHyperparameters = field(default_factory=TrainingHyperparameters)
    hardware_requirements: Dict[str, Any] = field(default_factory=dict)
    estimated_training_time: Optional[int] = None  # hours
    data_preprocessing: List[str] = field(default_factory=list)
    evaluation_metrics: List[str] = field(default_factory=list)


class ModelTrainingConfig(BaseSettings):
    """    Professional Model Training Configuration for IA-Influencer Agent Platform.
    
    Manages all aspects of AI/ML model training including hyperparameters,
    data preprocessing, evaluation, and deployment pipelines.
    """    
    # Core Training Configuration
    TRAINING_DATA_DIR: str = "/data/training"
    MODEL_OUTPUT_DIR: str = "/models/trained"
    CHECKPOINT_DIR: str = "/models/checkpoints"
    LOGS_DIR: str = "/logs/training"
    
    # Hardware Configuration
    GPU_TRAINING_ENABLED: bool = True
    MULTI_GPU_TRAINING: bool = False
    NUM_GPUS: int = 1
    CPU_CORES: int = 8
    MEMORY_LIMIT_GB: int = 32
    DISTRIBUTED_TRAINING: bool = False
    
    # Training Performance
    MIXED_PRECISION_ENABLED: bool = True
    GRADIENT_CHECKPOINTING: bool = False
    COMPILE_MODE: bool = False  # PyTorch 2.0 compile
    
    # Default Hyperparameters
    DEFAULT_LEARNING_RATE: float = 1e-4
    DEFAULT_BATCH_SIZE: int = 32
    DEFAULT_EPOCHS: int = 100
    DEFAULT_WARMUP_STEPS: int = 1000
    DEFAULT_WEIGHT_DECAY: float = 0.01
    
    # Data Configuration
    TRAIN_VALIDATION_SPLIT: float = 0.8
    VALIDATION_TEST_SPLIT: float = 0.5  # Of the remaining 20%
    DATA_AUGMENTATION_ENABLED: bool = True
    DATA_CACHING_ENABLED: bool = True
    PREPROCESSING_WORKERS: int = 4
    
    # Model Checkpointing
    SAVE_CHECKPOINT_EVERY_N_EPOCHS: int = 5
    KEEP_TOP_K_CHECKPOINTS: int = 3
    SAVE_BEST_MODEL_ONLY: bool = True
    CHECKPOINT_METRIC: str = "validation_loss"
    
    # Early Stopping
    EARLY_STOPPING_ENABLED: bool = True
    EARLY_STOPPING_PATIENCE: int = 10
    EARLY_STOPPING_MIN_DELTA: float = 1e-4
    EARLY_STOPPING_METRIC: str = "validation_loss"
    
    # Logging and Monitoring
    LOG_EVERY_N_STEPS: int = 100
    EVAL_EVERY_N_EPOCHS: int = 1
    WANDB_ENABLED: bool = False
    TENSORBOARD_ENABLED: bool = True
    MLFLOW_ENABLED: bool = False
    
    # Model Specific Configurations
    NLP_TRAINING_CONFIG: Dict[str, Any] = {
        "max_sequence_length": 512,
        "learning_rate": 2e-5,
        "batch_size": 16,
        "epochs": 5,
        "warmup_ratio": 0.1,
        "weight_decay": 0.01,
    }
    
    VISION_TRAINING_CONFIG: Dict[str, Any] = {
        "image_size": (224, 224),
        "learning_rate": 1e-4,
        "batch_size": 32,
        "epochs": 50,
        "data_augmentation": True,
        "mixup_alpha": 0.2,
    }
    
    AUDIO_TRAINING_CONFIG: Dict[str, Any] = {
        "sample_rate": 22050,
        "n_fft": 2048,
        "hop_length": 512,
        "learning_rate": 1e-3,
        "batch_size": 64,
        "epochs": 100,
    }
    
    # Fine-tuning Configuration
    FINE_TUNING_LAYERS: int = 3  # Number of layers to unfreeze
    FINE_TUNING_LEARNING_RATE: float = 1e-5
    GRADUAL_UNFREEZING: bool = True
    DISCRIMINATIVE_LEARNING_RATES: bool = True
    
    class Config:
        env_prefix = "TRAINING_"
        case_sensitive = False
        env_file = ".env"
    
    @validator("TRAINING_DATA_DIR", "MODEL_OUTPUT_DIR", "CHECKPOINT_DIR", "LOGS_DIR")
    def create_directories(cls, v):
        """Ensure training directories exist."""        os.makedirs(v, exist_ok=True)
        return v
    
    def get_training_spec(self, model_name: str, task_type: str) -> TrainingSpec:
        """Get training specification for a specific model and task."""        
        # Base specifications for different task types
        base_specs = {
            "text_classification": TrainingSpec(
                model_name=model_name,
                task_type="text_classification",
                training_mode=TrainingMode.FINE_TUNING,
                base_model="bert-base-uncased",
                hyperparameters=TrainingHyperparameters(
                    learning_rate=self.NLP_TRAINING_CONFIG["learning_rate"],
                    batch_size=self.NLP_TRAINING_CONFIG["batch_size"],
                    epochs=self.NLP_TRAINING_CONFIG["epochs"],
                    warmup_steps=int(self.NLP_TRAINING_CONFIG["warmup_ratio"] * 1000),
                    weight_decay=self.NLP_TRAINING_CONFIG["weight_decay"],
                ),
                hardware_requirements={
                    "gpu_memory_gb": 8,
                    "cpu_cores": 4,
                    "ram_gb": 16,
                },
                estimated_training_time=2,
                data_preprocessing=["tokenization", "padding", "attention_mask"],
                evaluation_metrics=["accuracy", "f1_score", "precision", "recall"]
            ),
            
            "image_classification": TrainingSpec(
                model_name=model_name,
                task_type="image_classification",
                training_mode=TrainingMode.TRANSFER_LEARNING,
                base_model="resnet50",
                hyperparameters=TrainingHyperparameters(
                    learning_rate=self.VISION_TRAINING_CONFIG["learning_rate"],
                    batch_size=self.VISION_TRAINING_CONFIG["batch_size"],
                    epochs=self.VISION_TRAINING_CONFIG["epochs"],
                ),
                hardware_requirements={
                    "gpu_memory_gb": 12,
                    "cpu_cores": 8,
                    "ram_gb": 32,
                },
                estimated_training_time=6,
                data_preprocessing=["resize", "normalize", "augmentation"],
                evaluation_metrics=["accuracy", "top5_accuracy", "confusion_matrix"]
            ),
            
            "audio_classification": TrainingSpec(
                model_name=model_name,
                task_type="audio_classification",
                training_mode=TrainingMode.FINE_TUNING,
                base_model="wav2vec2-base",
                hyperparameters=TrainingHyperparameters(
                    learning_rate=self.AUDIO_TRAINING_CONFIG["learning_rate"],
                    batch_size=self.AUDIO_TRAINING_CONFIG["batch_size"],
                    epochs=self.AUDIO_TRAINING_CONFIG["epochs"],
                ),
                hardware_requirements={
                    "gpu_memory_gb": 16,
                    "cpu_cores": 8,
                    "ram_gb": 24,
                },
                estimated_training_time=8,
                data_preprocessing=["audio_loading", "feature_extraction", "normalization"],
                evaluation_metrics=["accuracy", "auc_score", "mse"]
            ),
            
            "similarity_learning": TrainingSpec(
                model_name=model_name,
                task_type="similarity_learning",
                training_mode=TrainingMode.FINE_TUNING,
                base_model="sentence-transformers/all-MiniLM-L6-v2",
                hyperparameters=TrainingHyperparameters(
                    learning_rate=1e-5,
                    batch_size=16,
                    epochs=10,
                    warmup_steps=500,
                ),
                hardware_requirements={
                    "gpu_memory_gb": 6,
                    "cpu_cores": 4,
                    "ram_gb": 16,
                },
                estimated_training_time=4,
                data_preprocessing=["tokenization", "pair_generation"],
                evaluation_metrics=["cosine_similarity", "euclidean_distance", "spearman_correlation"]
            ),
        }
        
        return base_specs.get(task_type, self._get_default_training_spec(model_name, task_type))
    
    def _get_default_training_spec(self, model_name: str, task_type: str) -> TrainingSpec:
        """Get default training specification."""        return TrainingSpec(
            model_name=model_name,
            task_type=task_type,
            training_mode=TrainingMode.FINE_TUNING,
            hyperparameters=TrainingHyperparameters(
                learning_rate=self.DEFAULT_LEARNING_RATE,
                batch_size=self.DEFAULT_BATCH_SIZE,
                epochs=self.DEFAULT_EPOCHS,
            ),
            hardware_requirements={
                "gpu_memory_gb": 8,
                "cpu_cores": 4,
                "ram_gb": 16,
            },
            evaluation_metrics=["accuracy", "loss"]
        )
    
    def get_hyperparameters_for_task(self, task_type: str) -> TrainingHyperparameters:
        """Get optimized hyperparameters for specific task type."""        task_configs = {
            "nlp": self.NLP_TRAINING_CONFIG,
            "vision": self.VISION_TRAINING_CONFIG,
            "audio": self.AUDIO_TRAINING_CONFIG,
        }
        
        config = task_configs.get(task_type, {})
        
        return TrainingHyperparameters(
            learning_rate=config.get("learning_rate", self.DEFAULT_LEARNING_RATE),
            batch_size=config.get("batch_size", self.DEFAULT_BATCH_SIZE),
            epochs=config.get("epochs", self.DEFAULT_EPOCHS),
            warmup_steps=config.get("warmup_steps", self.DEFAULT_WARMUP_STEPS),
            weight_decay=config.get("weight_decay", self.DEFAULT_WEIGHT_DECAY),
        )
    
    def get_data_config(self) -> Dict[str, Any]:
        """Get data processing configuration."""        return {
            "data_dir": self.TRAINING_DATA_DIR,
            "splits": {
                "train_val_split": self.TRAIN_VALIDATION_SPLIT,
                "val_test_split": self.VALIDATION_TEST_SPLIT,
            },
            "augmentation": {
                "enabled": self.DATA_AUGMENTATION_ENABLED,
                "vision": {
                    "random_rotation": 15,
                    "random_horizontal_flip": 0.5,
                    "color_jitter": 0.2,
                    "random_crop": True,
                },
                "audio": {
                    "time_stretch": 0.1,
                    "pitch_shift": 2,
                    "noise_injection": 0.05,
                    "time_shift": 0.1,
                },
                "text": {
                    "synonym_replacement": 0.1,
                    "back_translation": False,
                    "paraphrasing": False,
                }
            },
            "preprocessing": {
                "workers": self.PREPROCESSING_WORKERS,
                "caching": self.DATA_CACHING_ENABLED,
                "batch_size": self.DEFAULT_BATCH_SIZE,
            }
        }
    
    def get_training_config(self) -> Dict[str, Any]:
        """Get complete training configuration."""        return {
            "hardware": {
                "gpu_enabled": self.GPU_TRAINING_ENABLED,
                "multi_gpu": self.MULTI_GPU_TRAINING,
                "num_gpus": self.NUM_GPUS,
                "distributed": self.DISTRIBUTED_TRAINING,
                "mixed_precision": self.MIXED_PRECISION_ENABLED,
                "gradient_checkpointing": self.GRADIENT_CHECKPOINTING,
                "compile_mode": self.COMPILE_MODE,
            },
            "optimization": {
                "default_lr": self.DEFAULT_LEARNING_RATE,
                "default_batch_size": self.DEFAULT_BATCH_SIZE,
                "default_epochs": self.DEFAULT_EPOCHS,
                "warmup_steps": self.DEFAULT_WARMUP_STEPS,
                "weight_decay": self.DEFAULT_WEIGHT_DECAY,
            },
            "checkpointing": {
                "save_every_n_epochs": self.SAVE_CHECKPOINT_EVERY_N_EPOCHS,
                "keep_top_k": self.KEEP_TOP_K_CHECKPOINTS,
                "save_best_only": self.SAVE_BEST_MODEL_ONLY,
                "metric": self.CHECKPOINT_METRIC,
                "checkpoint_dir": self.CHECKPOINT_DIR,
            },
            "early_stopping": {
                "enabled": self.EARLY_STOPPING_ENABLED,
                "patience": self.EARLY_STOPPING_PATIENCE,
                "min_delta": self.EARLY_STOPPING_MIN_DELTA,
                "metric": self.EARLY_STOPPING_METRIC,
            },
            "logging": {
                "log_every_n_steps": self.LOG_EVERY_N_STEPS,
                "eval_every_n_epochs": self.EVAL_EVERY_N_EPOCHS,
                "tensorboard": self.TENSORBOARD_ENABLED,
                "wandb": self.WANDB_ENABLED,
                "mlflow": self.MLFLOW_ENABLED,
                "logs_dir": self.LOGS_DIR,
            }
        }
    
    def get_fine_tuning_config(self) -> Dict[str, Any]:
        """Get fine-tuning specific configuration."""        return {
            "layers_to_unfreeze": self.FINE_TUNING_LAYERS,
            "fine_tuning_lr": self.FINE_TUNING_LEARNING_RATE,
            "gradual_unfreezing": self.GRADUAL_UNFREEZING,
            "discriminative_lr": self.DISCRIMINATIVE_LEARNING_RATES,
            "strategies": {
                "layer_wise_decay": 0.9,
                "differential_learning_rates": True,
                "warmup_fine_tuning": True,
            }
        }
    
    def estimate_training_resources(self, spec: TrainingSpec) -> Dict[str, Any]:
        """Estimate required resources for training."""        base_memory = spec.hyperparameters.batch_size * 0.1  # GB per batch item
        
        # Task-specific memory multipliers
        memory_multipliers = {
            "text_classification": 1.0,
            "image_classification": 4.0,
            "audio_classification": 2.0,
            "object_detection": 6.0,
            "similarity_learning": 1.5,
        }
        
        multiplier = memory_multipliers.get(spec.task_type, 2.0)
        estimated_memory = base_memory * multiplier
        
        return {
            "gpu_memory_gb": max(4, int(estimated_memory)),
            "cpu_cores": max(4, spec.hyperparameters.batch_size // 8),
            "ram_gb": max(8, int(estimated_memory * 2)),
            "disk_space_gb": 50,  # For checkpoints and logs
            "estimated_time_hours": spec.estimated_training_time or 4,
        }
    
    def get_evaluation_config(self) -> Dict[str, Any]:
        """Get model evaluation configuration."""        return {
            "metrics_by_task": {
                "classification": ["accuracy", "precision", "recall", "f1_score", "auc"],
                "regression": ["mse", "mae", "r2_score", "rmse"],
                "similarity": ["cosine_similarity", "spearman_correlation", "pearson_correlation"],
                "generation": ["bleu", "rouge", "meteor", "bertscore"],
            },
            "validation": {
                "cross_validation": False,
                "k_folds": 5,
                "stratified": True,
            },
            "testing": {
                "test_size": 0.1,
                "random_state": 42,
                "bootstrap_samples": 1000,
            }
        }


# Global model training configuration instance
model_training_config = ModelTrainingConfig()
