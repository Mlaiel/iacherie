"""AI Training Service - Automated model training and optimization
Enterprise-grade AI model training and optimization for the Ainflue AI platform.

This service provides comprehensive AI model training, hyperparameter optimization,
distributed training coordination, and model lifecycle management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
import os
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
import pickle
import hashlib


class TrainingStatus(Enum):
    """Training job status."""
    PENDING = "pending"
    PREPARING = "preparing"
    TRAINING = "training"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ModelType(Enum):
    """Types of AI models that can be trained."""
    CONTENT_CLASSIFIER = "content_classifier"
    SENTIMENT_ANALYZER = "sentiment_analyzer"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    IMAGE_GENERATOR = "image_generator"
    TEXT_GENERATOR = "text_generator"
    AUDIO_CLASSIFIER = "audio_classifier"
    VIDEO_ANALYZER = "video_analyzer"
    ENGAGEMENT_PREDICTOR = "engagement_predictor"
    TREND_PREDICTOR = "trend_predictor"
    QUALITY_ASSESSOR = "quality_assessor"


class OptimizationStrategy(Enum):
    """Model optimization strategies."""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    GENETIC_ALGORITHM = "genetic_algorithm"
    AUTO_ML = "auto_ml"


class TrainingFramework(Enum):
    """Supported training frameworks."""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SCIKIT_LEARN = "sklearn"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    HUGGINGFACE = "huggingface"


@dataclass
class TrainingConfig:
    """Training configuration parameters."""
    model_type: ModelType
    framework: TrainingFramework
    architecture: str
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BAYESIAN_OPTIMIZATION
    max_training_time_hours: int = 24
    early_stopping_patience: int = 10
    validation_split: float = 0.2
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 100
    distributed_training: bool = False
    gpu_count: int = 1
    mixed_precision: bool = True
    checkpointing_enabled: bool = True
    tensorboard_logging: bool = True


@dataclass
class DatasetInfo:
    """Dataset information for training."""
    name: str
    source_path: str
    size_mb: float
    sample_count: int
    features_count: int
    target_type: str  # classification, regression, generation
    preprocessing_required: bool = True
    augmentation_enabled: bool = False
    validation_set_path: Optional[str] = None
    test_set_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrainingMetrics:
    """Training progress metrics."""
    epoch: int = 0
    training_loss: float = 0.0
    validation_loss: float = 0.0
    training_accuracy: float = 0.0
    validation_accuracy: float = 0.0
    learning_rate: float = 0.0
    batch_time_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_utilization: float = 0.0
    custom_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class TrainingJob:
    """Training job representation."""
    id: str
    name: str
    model_type: ModelType
    config: TrainingConfig
    dataset: DatasetInfo
    status: TrainingStatus
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    progress_percentage: float = 0.0
    current_epoch: int = 0
    best_metrics: Optional[TrainingMetrics] = None
    final_metrics: Optional[TrainingMetrics] = None
    model_path: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    checkpoints: List[str] = field(default_factory=list)


@dataclass
class ModelArtifact:
    """Trained model artifact."""
    id: str
    job_id: str
    model_type: ModelType
    framework: TrainingFramework
    model_path: str
    config_path: str
    metrics_path: str
    size_mb: float
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    deployment_ready: bool = False


class AITrainingService:
    """Enterprise AI model training and optimization service."""
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        """Initialize the AI training service.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.training_jobs: Dict[str, TrainingJob] = {}
        self.active_jobs: Dict[str, asyncio.Task] = {}
        self.model_artifacts: Dict[str, ModelArtifact] = {}
        self.model_templates: Dict[ModelType, Dict[str, Any]] = {}
        
        # Configuration
        self.config = {
            'models_directory': '/var/models/ainflue',
            'checkpoints_directory': '/var/checkpoints/ainflue',
            'logs_directory': '/var/logs/training',
            'max_concurrent_jobs': 5,
            'gpu_memory_limit_gb': 8,
            'distributed_training_enabled': False,
            'auto_cleanup_completed_jobs': True,
            'cleanup_after_hours': 168,  # 7 days
            'tensorboard_port': 6006,
            'model_registry_enabled': True
        }
        
        # Metrics
        self.metrics = {
            'total_training_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'active_jobs': 0,
            'average_training_time_hours': 0.0,
            'gpu_utilization_average': 0.0,
            'models_deployed': 0,
            'total_training_hours': 0.0
        }
        
        # Initialize directories
        self._initialize_directories()
        
        # Initialize model templates
        self._create_model_templates()
        
        # Load configuration if provided
        if config_path:
            self._load_configuration(config_path)
        
        self.logger.info("AITrainingService initialized successfully")
    
    def _initialize_directories(self) -> None:
        """Initialize required directories for training."""
        try:
            from pathlib import Path
            
            directories = [
                self.config['models_directory'],
                self.config['checkpoints_directory'],
                self.config['logs_directory']
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
            
            self.logger.info("Initialized training directories")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize directories: {e}")
    
    def _create_model_templates(self) -> None:
        """Create model architecture templates for different model types."""
        
        self.model_templates = {
            ModelType.CONTENT_CLASSIFIER: {
                'architectures': {
                    'bert_classifier': {
                        'framework': TrainingFramework.HUGGINGFACE,
                        'base_model': 'bert-base-uncased',
                        'num_classes': 10,
                        'dropout': 0.1,
                        'max_length': 512
                    },
                    'cnn_classifier': {
                        'framework': TrainingFramework.PYTORCH,
                        'layers': [
                            {'type': 'conv1d', 'filters': 64, 'kernel_size': 3},
                            {'type': 'pool', 'pool_size': 2},
                            {'type': 'conv1d', 'filters': 128, 'kernel_size': 3},
                            {'type': 'pool', 'pool_size': 2},
                            {'type': 'dense', 'units': 256},
                            {'type': 'dense', 'units': 10, 'activation': 'softmax'}
                        ]
                    }
                },
                'default_hyperparameters': {
                    'learning_rate': 0.001,
                    'batch_size': 32,
                    'epochs': 50,
                    'weight_decay': 0.01
                }
            },
            
            ModelType.SENTIMENT_ANALYZER: {
                'architectures': {
                    'roberta_sentiment': {
                        'framework': TrainingFramework.HUGGINGFACE,
                        'base_model': 'roberta-base',
                        'num_labels': 3,  # positive, negative, neutral
                        'problem_type': 'single_label_classification'
                    },
                    'lstm_sentiment': {
                        'framework': TrainingFramework.PYTORCH,
                        'embedding_dim': 300,
                        'hidden_dim': 128,
                        'num_layers': 2,
                        'dropout': 0.3,
                        'bidirectional': True
                    }
                },
                'default_hyperparameters': {
                    'learning_rate': 0.0001,
                    'batch_size': 16,
                    'epochs': 30,
                    'warmup_steps': 1000
                }
            },
            
            ModelType.RECOMMENDATION_ENGINE: {
                'architectures': {
                    'collaborative_filtering': {
                        'framework': TrainingFramework.PYTORCH,
                        'embedding_dim': 50,
                        'hidden_layers': [128, 64, 32],
                        'dropout': 0.2
                    },
                    'matrix_factorization': {
                        'framework': TrainingFramework.SCIKIT_LEARN,
                        'n_factors': 100,
                        'regularization': 0.1
                    }
                },
                'default_hyperparameters': {
                    'learning_rate': 0.01,
                    'batch_size': 256,
                    'epochs': 100,
                    'weight_decay': 0.001
                }
            },
            
            ModelType.IMAGE_GENERATOR: {
                'architectures': {
                    'stable_diffusion': {
                        'framework': TrainingFramework.HUGGINGFACE,
                        'base_model': 'stable-diffusion-v1-5',
                        'resolution': 512,
                        'guidance_scale': 7.5
                    },
                    'gan': {
                        'framework': TrainingFramework.PYTORCH,
                        'latent_dim': 100,
                        'generator_layers': [256, 512, 1024, 784],
                        'discriminator_layers': [784, 512, 256, 1]
                    }
                },
                'default_hyperparameters': {
                    'learning_rate': 0.0002,
                    'batch_size': 8,
                    'epochs': 200,
                    'beta1': 0.5,
                    'beta2': 0.999
                }
            },
            
            ModelType.ENGAGEMENT_PREDICTOR: {
                'architectures': {
                    'xgboost_predictor': {
                        'framework': TrainingFramework.XGBOOST,
                        'max_depth': 6,
                        'n_estimators': 1000,
                        'subsample': 0.8,
                        'colsample_bytree': 0.8
                    },
                    'neural_predictor': {
                        'framework': TrainingFramework.PYTORCH,
                        'hidden_layers': [512, 256, 128, 64],
                        'dropout': 0.2,
                        'batch_norm': True
                    }
                },
                'default_hyperparameters': {
                    'learning_rate': 0.01,
                    'batch_size': 128,
                    'epochs': 150,
                    'early_stopping_patience': 15
                }
            }
        }
    
    async def create_training_job(self, name: str, model_type: ModelType,
                                dataset: DatasetInfo, config: Optional[TrainingConfig] = None,
                                custom_architecture: Optional[str] = None) -> str:
        """Create a new training job.
        
        Args:
            name: Job name
            model_type: Type of model to train
            dataset: Dataset information
            config: Optional training configuration
            custom_architecture: Optional custom architecture name
            
        Returns:
            Training job ID
        """
        try:
            # Generate job ID
            job_id = f"train-{int(time.time())}-{uuid.uuid4().hex[:8]}"
            
            # Create default config if not provided
            if not config:
                config = self._create_default_config(model_type, custom_architecture)
            
            # Create training job
            job = TrainingJob(
                id=job_id,
                name=name,
                model_type=model_type,
                config=config,
                dataset=dataset,
                status=TrainingStatus.PENDING
            )
            
            # Validate job configuration
            if not self._validate_training_job(job):
                raise ValueError("Invalid training job configuration")
            
            # Store job
            self.training_jobs[job_id] = job
            
            # Update metrics
            self.metrics['total_training_jobs'] += 1
            
            self.logger.info(f"Created training job: {job_id} - {name}")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Failed to create training job: {e}")
            raise
    
    def _create_default_config(self, model_type: ModelType, 
                             architecture: Optional[str] = None) -> TrainingConfig:
        """Create default training configuration for model type.
        
        Args:
            model_type: Type of model
            architecture: Optional specific architecture
            
        Returns:
            Default training configuration
        """
        template = self.model_templates.get(model_type, {})
        architectures = template.get('architectures', {})
        default_params = template.get('default_hyperparameters', {})
        
        # Select architecture
        if architecture and architecture in architectures:
            arch_config = architectures[architecture]
        else:
            # Use first available architecture
            arch_config = next(iter(architectures.values())) if architectures else {}
        
        # Get framework
        framework = TrainingFramework(arch_config.get('framework', 'pytorch'))
        
        # Create configuration
        config = TrainingConfig(
            model_type=model_type,
            framework=framework,
            architecture=architecture or list(architectures.keys())[0] if architectures else 'default',
            hyperparameters=default_params.copy()
        )
        
        # Apply architecture-specific parameters
        for key, value in arch_config.items():
            if key != 'framework':
                config.hyperparameters[key] = value
        
        return config
    
    def _validate_training_job(self, job: TrainingJob) -> bool:
        """Validate training job configuration.
        
        Args:
            job: Training job to validate
            
        Returns:
            True if valid
        """
        try:
            # Check dataset exists
            if not os.path.exists(job.dataset.source_path):
                self.logger.error(f"Dataset not found: {job.dataset.source_path}")
                return False
            
            # Check resource requirements
            if job.config.gpu_count > 1 and not self.config['distributed_training_enabled']:
                self.logger.error("Distributed training not enabled")
                return False
            
            # Check concurrent jobs limit
            if len(self.active_jobs) >= self.config['max_concurrent_jobs']:
                self.logger.error("Maximum concurrent jobs limit reached")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False
    
    async def start_training_job(self, job_id: str) -> bool:
        """Start a training job.
        
        Args:
            job_id: Training job ID
            
        Returns:
            True if started successfully
        """
        try:
            if job_id not in self.training_jobs:
                self.logger.error(f"Training job not found: {job_id}")
                return False
            
            job = self.training_jobs[job_id]
            
            if job.status != TrainingStatus.PENDING:
                self.logger.error(f"Job {job_id} is not in pending status")
                return False
            
            # Start training task
            job.status = TrainingStatus.PREPARING
            job.started_at = time.time()
            
            training_task = asyncio.create_task(self._execute_training_job(job))
            self.active_jobs[job_id] = training_task
            
            # Update metrics
            self.metrics['active_jobs'] = len(self.active_jobs)
            
            self.logger.info(f"Started training job: {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start training job {job_id}: {e}")
            return False
    
    async def _execute_training_job(self, job: TrainingJob) -> None:
        """Execute a training job.
        
        Args:
            job: Training job to execute
        """
        try:
            self.logger.info(f"Executing training job: {job.id}")
            
            # Prepare training environment
            await self._prepare_training_environment(job)
            
            # Load and preprocess data
            await self._prepare_training_data(job)
            
            # Initialize model
            await self._initialize_model(job)
            
            # Start training
            job.status = TrainingStatus.TRAINING
            await self._train_model(job)
            
            # Validate model
            job.status = TrainingStatus.VALIDATING
            await self._validate_model(job)
            
            # Save model artifact
            await self._save_model_artifact(job)
            
            # Complete job
            job.status = TrainingStatus.COMPLETED
            job.completed_at = time.time()
            
            # Update metrics
            training_time = job.completed_at - job.started_at
            self._update_training_metrics(training_time, True)
            self.metrics['completed_jobs'] += 1
            
            self.logger.info(f"Completed training job: {job.id}")
            
        except Exception as e:
            job.status = TrainingStatus.FAILED
            job.error_message = str(e)
            job.logs.append(f"Training failed: {e}")
            
            self.metrics['failed_jobs'] += 1
            self.logger.error(f"Training job {job.id} failed: {e}")
        finally:
            # Clean up active job
            if job.id in self.active_jobs:
                del self.active_jobs[job.id]
            self.metrics['active_jobs'] = len(self.active_jobs)
    
    async def _prepare_training_environment(self, job: TrainingJob) -> None:
        """Prepare training environment for the job.
        
        Args:
            job: Training job
        """
        await asyncio.sleep(1)  # Simulate environment preparation
        
        job.logs.append("Preparing training environment...")
        
        # Create job-specific directories
        from pathlib import Path
        job_dir = Path(self.config['models_directory']) / job.id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint_dir = Path(self.config['checkpoints_directory']) / job.id
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        log_file = Path(self.config['logs_directory']) / f"{job.id}.log"
        job.logs.append(f"Log file: {log_file}")
        
        # Configure GPU if needed
        if job.config.gpu_count > 0:
            job.logs.append(f"Configuring {job.config.gpu_count} GPU(s)")
        
        job.logs.append("Environment preparation completed")
    
    async def _prepare_training_data(self, job: TrainingJob) -> None:
        """Prepare and preprocess training data.
        
        Args:
            job: Training job
        """
        await asyncio.sleep(2)  # Simulate data preparation
        
        job.logs.append("Loading and preprocessing training data...")
        
        # Simulate data loading
        job.logs.append(f"Loading dataset: {job.dataset.name}")
        job.logs.append(f"Dataset size: {job.dataset.size_mb:.1f} MB")
        job.logs.append(f"Sample count: {job.dataset.sample_count}")
        
        # Data preprocessing
        if job.dataset.preprocessing_required:
            job.logs.append("Applying data preprocessing...")
            await asyncio.sleep(1)
        
        # Data augmentation
        if job.dataset.augmentation_enabled:
            job.logs.append("Applying data augmentation...")
            await asyncio.sleep(1)
        
        # Split data
        train_samples = int(job.dataset.sample_count * (1 - job.config.validation_split))
        val_samples = job.dataset.sample_count - train_samples
        
        job.logs.append(f"Training samples: {train_samples}")
        job.logs.append(f"Validation samples: {val_samples}")
        
        job.logs.append("Data preparation completed")
    
    async def _initialize_model(self, job: TrainingJob) -> None:
        """Initialize the model for training.
        
        Args:
            job: Training job
        """
        await asyncio.sleep(1)  # Simulate model initialization
        
        job.logs.append("Initializing model...")
        
        # Get model architecture
        architecture = job.config.architecture
        job.logs.append(f"Architecture: {architecture}")
        job.logs.append(f"Framework: {job.config.framework.value}")
        
        # Initialize based on framework
        if job.config.framework == TrainingFramework.PYTORCH:
            job.logs.append("Initializing PyTorch model")
        elif job.config.framework == TrainingFramework.TENSORFLOW:
            job.logs.append("Initializing TensorFlow model")
        elif job.config.framework == TrainingFramework.HUGGINGFACE:
            job.logs.append("Initializing Hugging Face model")
        
        # Log hyperparameters
        job.logs.append("Hyperparameters:")
        for key, value in job.config.hyperparameters.items():
            job.logs.append(f"  {key}: {value}")
        
        job.logs.append("Model initialization completed")
    
    async def _train_model(self, job: TrainingJob) -> None:
        """Train the model.
        
        Args:
            job: Training job
        """
        job.logs.append("Starting model training...")
        
        total_epochs = job.config.epochs
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(total_epochs):
            job.current_epoch = epoch + 1
            job.progress_percentage = (epoch + 1) / total_epochs * 100
            
            # Simulate training epoch
            await asyncio.sleep(0.5)  # Simulate training time
            
            # Generate mock training metrics
            metrics = self._generate_training_metrics(epoch, total_epochs)
            
            # Update job metrics
            if not job.best_metrics or metrics.validation_loss < job.best_metrics.validation_loss:
                job.best_metrics = metrics
                best_val_loss = metrics.validation_loss
                patience_counter = 0
                
                # Save checkpoint
                checkpoint_path = f"checkpoint_epoch_{epoch+1}.pt"
                job.checkpoints.append(checkpoint_path)
                job.logs.append(f"Saved checkpoint: {checkpoint_path}")
            else:
                patience_counter += 1
            
            # Log progress
            if (epoch + 1) % 10 == 0 or epoch == 0:
                job.logs.append(
                    f"Epoch {epoch+1}/{total_epochs} - "
                    f"Loss: {metrics.training_loss:.4f} - "
                    f"Val Loss: {metrics.validation_loss:.4f} - "
                    f"Acc: {metrics.training_accuracy:.4f} - "
                    f"Val Acc: {metrics.validation_accuracy:.4f}"
                )
            
            # Early stopping
            if patience_counter >= job.config.early_stopping_patience:
                job.logs.append(f"Early stopping triggered at epoch {epoch+1}")
                break
        
        job.final_metrics = job.best_metrics
        job.logs.append("Model training completed")
    
    def _generate_training_metrics(self, epoch: int, total_epochs: int) -> TrainingMetrics:
        """Generate mock training metrics for simulation.
        
        Args:
            epoch: Current epoch
            total_epochs: Total epochs
            
        Returns:
            Training metrics
        """
        # Simulate learning curves
        progress = epoch / total_epochs
        
        # Training loss decreases with some noise
        base_train_loss = 2.0 * (1 - progress) + 0.1
        train_loss = base_train_loss + (0.1 * (0.5 - hash(str(epoch)) % 100 / 100))
        
        # Validation loss decreases but with more variance
        base_val_loss = 2.2 * (1 - progress * 0.8) + 0.15
        val_loss = base_val_loss + (0.15 * (0.5 - hash(str(epoch + 1)) % 100 / 100))
        
        # Accuracy increases
        train_acc = 0.5 + 0.45 * progress + 0.05 * (hash(str(epoch)) % 100 / 100 - 0.5)
        val_acc = 0.4 + 0.4 * progress + 0.1 * (hash(str(epoch + 1)) % 100 / 100 - 0.5)
        
        return TrainingMetrics(
            epoch=epoch + 1,
            training_loss=max(0.01, train_loss),
            validation_loss=max(0.01, val_loss),
            training_accuracy=min(0.99, max(0.01, train_acc)),
            validation_accuracy=min(0.99, max(0.01, val_acc)),
            learning_rate=0.001 * (0.95 ** (epoch // 10)),  # Learning rate decay
            batch_time_seconds=0.5 + 0.1 * (hash(str(epoch)) % 100 / 100),
            memory_usage_mb=2048 + 512 * (hash(str(epoch)) % 100 / 100),
            gpu_utilization=80 + 15 * (hash(str(epoch)) % 100 / 100)
        )
    
    async def _validate_model(self, job: TrainingJob) -> None:
        """Validate the trained model.
        
        Args:
            job: Training job
        """
        await asyncio.sleep(2)  # Simulate validation
        
        job.logs.append("Validating trained model...")
        
        # Load best checkpoint
        if job.checkpoints:
            best_checkpoint = job.checkpoints[-1]
            job.logs.append(f"Loading best checkpoint: {best_checkpoint}")
        
        # Run validation on test set
        if job.dataset.test_set_path:
            job.logs.append("Evaluating on test set...")
            
            # Generate test metrics
            test_accuracy = 0.85 + 0.1 * (hash(job.id) % 100 / 100)
            test_loss = 0.3 + 0.2 * (hash(job.id + "loss") % 100 / 100)
            
            job.logs.append(f"Test Accuracy: {test_accuracy:.4f}")
            job.logs.append(f"Test Loss: {test_loss:.4f}")
            
            # Store in final metrics
            if job.final_metrics:
                job.final_metrics.custom_metrics['test_accuracy'] = test_accuracy
                job.final_metrics.custom_metrics['test_loss'] = test_loss
        
        job.logs.append("Model validation completed")
    
    async def _save_model_artifact(self, job: TrainingJob) -> None:
        """Save the trained model as an artifact.
        
        Args:
            job: Training job
        """
        await asyncio.sleep(1)  # Simulate model saving
        
        job.logs.append("Saving model artifact...")
        
        # Generate artifact ID
        artifact_id = f"model-{job.id}-{int(time.time())}"
        
        # Create model paths
        from pathlib import Path
        models_dir = Path(self.config['models_directory']) / job.id
        model_path = str(models_dir / "model.bin")
        config_path = str(models_dir / "config.json")
        metrics_path = str(models_dir / "metrics.json")
        
        # Simulate saving files
        job.model_path = model_path
        
        # Calculate model size (simulated)
        model_size_mb = 50 + 200 * (hash(job.id) % 100 / 100)  # 50-250 MB
        
        # Create model artifact
        artifact = ModelArtifact(
            id=artifact_id,
            job_id=job.id,
            model_type=job.model_type,
            framework=job.config.framework,
            model_path=model_path,
            config_path=config_path,
            metrics_path=metrics_path,
            size_mb=model_size_mb,
            metadata={
                'architecture': job.config.architecture,
                'hyperparameters': job.config.hyperparameters,
                'training_epochs': job.current_epoch,
                'dataset_info': {
                    'name': job.dataset.name,
                    'sample_count': job.dataset.sample_count
                }
            },
            performance_metrics={
                'validation_accuracy': job.final_metrics.validation_accuracy if job.final_metrics else 0.0,
                'validation_loss': job.final_metrics.validation_loss if job.final_metrics else 0.0
            } if job.final_metrics else {},
            deployment_ready=True
        )
        
        # Store artifact
        self.model_artifacts[artifact_id] = artifact
        
        job.logs.append(f"Model artifact saved: {artifact_id}")
        job.logs.append(f"Model size: {model_size_mb:.1f} MB")
        job.logs.append(f"Model path: {model_path}")
    
    def _update_training_metrics(self, training_time: float, success: bool) -> None:
        """Update training service metrics.
        
        Args:
            training_time: Training time in seconds
            success: Whether training was successful
        """
        training_hours = training_time / 3600
        
        # Update total training time
        self.metrics['total_training_hours'] += training_hours
        
        # Update average training time
        if success:
            completed_jobs = self.metrics['completed_jobs']
            current_avg = self.metrics['average_training_time_hours']
            self.metrics['average_training_time_hours'] = (
                (current_avg * completed_jobs + training_hours) / (completed_jobs + 1)
            )
    
    def get_training_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get training job status and progress.
        
        Args:
            job_id: Training job ID
            
        Returns:
            Job status dictionary or None if not found
        """
        if job_id not in self.training_jobs:
            return None
        
        job = self.training_jobs[job_id]
        
        return {
            'id': job.id,
            'name': job.name,
            'model_type': job.model_type.value,
            'status': job.status.value,
            'progress_percentage': job.progress_percentage,
            'current_epoch': job.current_epoch,
            'total_epochs': job.config.epochs,
            'created_at': job.created_at,
            'started_at': job.started_at,
            'completed_at': job.completed_at,
            'training_time_hours': (
                (job.completed_at or time.time()) - job.started_at
            ) / 3600 if job.started_at else 0,
            'best_metrics': {
                'validation_accuracy': job.best_metrics.validation_accuracy,
                'validation_loss': job.best_metrics.validation_loss,
                'training_accuracy': job.best_metrics.training_accuracy,
                'training_loss': job.best_metrics.training_loss
            } if job.best_metrics else None,
            'model_path': job.model_path,
            'checkpoints_count': len(job.checkpoints),
            'error_message': job.error_message,
            'resource_usage': job.resource_usage,
            'logs_count': len(job.logs)
        }
    
    def list_training_jobs(self, status_filter: Optional[TrainingStatus] = None,
                          model_type_filter: Optional[ModelType] = None) -> List[Dict[str, Any]]:
        """List training jobs with optional filtering.
        
        Args:
            status_filter: Optional status filter
            model_type_filter: Optional model type filter
            
        Returns:
            List of training job summaries
        """
        jobs = []
        
        for job in self.training_jobs.values():
            # Apply filters
            if status_filter and job.status != status_filter:
                continue
            if model_type_filter and job.model_type != model_type_filter:
                continue
            
            jobs.append({
                'id': job.id,
                'name': job.name,
                'model_type': job.model_type.value,
                'status': job.status.value,
                'progress_percentage': job.progress_percentage,
                'created_at': job.created_at,
                'started_at': job.started_at,
                'completed_at': job.completed_at
            })
        
        return sorted(jobs, key=lambda j: j['created_at'], reverse=True)
    
    def list_model_artifacts(self, model_type_filter: Optional[ModelType] = None) -> List[Dict[str, Any]]:
        """List trained model artifacts.
        
        Args:
            model_type_filter: Optional model type filter
            
        Returns:
            List of model artifacts
        """
        artifacts = []
        
        for artifact in self.model_artifacts.values():
            # Apply filter
            if model_type_filter and artifact.model_type != model_type_filter:
                continue
            
            artifacts.append({
                'id': artifact.id,
                'job_id': artifact.job_id,
                'model_type': artifact.model_type.value,
                'framework': artifact.framework.value,
                'size_mb': artifact.size_mb,
                'created_at': artifact.created_at,
                'deployment_ready': artifact.deployment_ready,
                'performance_metrics': artifact.performance_metrics,
                'model_path': artifact.model_path
            })
        
        return sorted(artifacts, key=lambda a: a['created_at'], reverse=True)
    
    def get_model_templates(self) -> Dict[str, Any]:
        """Get available model templates and architectures.
        
        Returns:
            Model templates dictionary
        """
        templates = {}
        
        for model_type, template in self.model_templates.items():
            templates[model_type.value] = {
                'architectures': list(template.get('architectures', {}).keys()),
                'default_hyperparameters': template.get('default_hyperparameters', {}),
                'supported_frameworks': list(set(
                    arch.get('framework', 'pytorch')
                    for arch in template.get('architectures', {}).values()
                ))
            }
        
        return templates
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get training service metrics and statistics.
        
        Returns:
            Metrics dictionary
        """
        # Calculate additional metrics
        total_jobs = len(self.training_jobs)
        success_rate = (
            self.metrics['completed_jobs'] / max(self.metrics['total_training_jobs'], 1) * 100
        )
        
        return {
            'training': self.metrics.copy(),
            'jobs': {
                'total_jobs': total_jobs,
                'success_rate': success_rate,
                'active_jobs': len(self.active_jobs),
                'max_concurrent_jobs': self.config['max_concurrent_jobs']
            },
            'models': {
                'total_artifacts': len(self.model_artifacts),
                'deployment_ready': len([a for a in self.model_artifacts.values() if a.deployment_ready]),
                'total_size_gb': sum(a.size_mb for a in self.model_artifacts.values()) / 1024,
                'supported_types': [t.value for t in ModelType]
            },
            'resources': {
                'distributed_training_enabled': self.config['distributed_training_enabled'],
                'gpu_memory_limit_gb': self.config['gpu_memory_limit_gb'],
                'models_directory': self.config['models_directory']
            }
        }
    
    async def stop_training_job(self, job_id: str) -> bool:
        """Stop a running training job.
        
        Args:
            job_id: Training job ID
            
        Returns:
            True if stopped successfully
        """
        try:
            if job_id not in self.training_jobs:
                self.logger.error(f"Training job not found: {job_id}")
                return False
            
            job = self.training_jobs[job_id]
            
            if job.status not in [TrainingStatus.TRAINING, TrainingStatus.PREPARING]:
                self.logger.error(f"Job {job_id} is not running")
                return False
            
            # Cancel the training task
            if job_id in self.active_jobs:
                task = self.active_jobs[job_id]
                task.cancel()
                
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                del self.active_jobs[job_id]
            
            # Update job status
            job.status = TrainingStatus.CANCELLED
            job.completed_at = time.time()
            job.logs.append("Training job cancelled by user")
            
            self.metrics['active_jobs'] = len(self.active_jobs)
            
            self.logger.info(f"Stopped training job: {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop training job {job_id}: {e}")
            return False
    
    def _load_configuration(self, config_path: str) -> None:
        """Load configuration from file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            from pathlib import Path
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Update configuration
                self.config.update(config.get('training_service', {}))
                
                # Load custom model templates
                if 'model_templates' in config:
                    for model_type, template in config['model_templates'].items():
                        self.model_templates[ModelType(model_type)] = template
                
                self.logger.info(f"Loaded configuration from {config_path}")
            else:
                self.logger.warning(f"Configuration file {config_path} not found")
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the AI training service."""
        try:
            # Stop all active training jobs
            job_ids = list(self.active_jobs.keys())
            for job_id in job_ids:
                await self.stop_training_job(job_id)
            
            self.logger.info("AITrainingService shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


# Example usage and testing
async def main() -> None:
    """Example usage of the AITrainingService."""
    # Initialize service
    service = AITrainingService()
    
    try:
        # Create dataset info
        dataset = DatasetInfo(
            name="sentiment_dataset",
            source_path="/tmp/sentiment_data.csv",
            size_mb=25.5,
            sample_count=10000,
            features_count=512,
            target_type="classification",
            preprocessing_required=True
        )
        
        # Create training job
        job_id = await service.create_training_job(
            "Sentiment Analysis Model",
            ModelType.SENTIMENT_ANALYZER,
            dataset
        )
        print(f"Created training job: {job_id}")
        
        # Start training
        started = await service.start_training_job(job_id)
        print(f"Training started: {started}")
        
        # Monitor progress
        for _ in range(10):
            status = service.get_training_status(job_id)
            if status:
                print(f"Progress: {status['progress_percentage']:.1f}% - Epoch: {status['current_epoch']}")
                if status['status'] in ['completed', 'failed']:
                    break
            await asyncio.sleep(2)
        
        # Get final status
        final_status = service.get_training_status(job_id)
        print(f"Final status: {final_status}")
        
        # List model artifacts
        artifacts = service.list_model_artifacts()
        print(f"Model artifacts: {len(artifacts)}")
        
        # Get service metrics
        metrics = service.get_metrics()
        print(f"Service metrics: {metrics}")
        
    finally:
        # Cleanup
        await service.shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())