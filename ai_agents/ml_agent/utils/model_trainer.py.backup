"""Model Trainer - Advanced ML Model Training & Pipeline Management System

Industrial-grade model training orchestrator providing automated training workflows,
hyperparameter optimization, cross-validation, and comprehensive model evaluation
for the IA-Influencer-Agent ML platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This training system and methodologies are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission
is strictly PROHIBITED and will result in legal action.

ALL RIGHTS RESERVED - FAHED MLAIEL ©2025
"""
import asyncio
import logging
import time
import uuid
import json
import pickle
import joblib
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from pathlib import Path
import numpy as np
import pandas as pd
import hashlib
import traceback
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Core ML frameworks
import tensorflow as tf
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import sklearn
from sklearn.model_selection import (
    train_test_split, GridSearchCV, RandomizedSearchCV, 
    cross_val_score, StratifiedKFold, TimeSeriesSplit
)
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, classification_report,
    confusion_matrix, roc_auc_score, mean_squared_error, r2_score
)
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor

# AutoML and optimization
try:
    from optuna import create_study, Trial
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

# MLOps integration
import mlflow
import mlflow.tensorflow
import mlflow.pytorch
import mlflow.sklearn
from prometheus_client import Counter, Histogram, Gauge

# Platform imports
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import TrainingError, ValidationError, ModelError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    TrainingError, ValidationError, ModelError = globals().get('TrainingError, ValidationError, ModelError', Exception)
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.cache import CacheManager

logger = logging.getLogger(__name__)

class TrainingStatus(Enum):
    """Training job status enumeration"""
    QUEUED = "queued"
    PREPARING = "preparing"
    TRAINING = "training"
    VALIDATING = "validating"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class OptimizationMethod(Enum):
    """Hyperparameter optimization methods"""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN = "bayesian"
    OPTUNA = "optuna"
    GENETIC = "genetic"

class ValidationStrategy(Enum):
    """Model validation strategies"""
    TRAIN_TEST_SPLIT = "train_test_split"
    K_FOLD_CV = "k_fold_cv"
    STRATIFIED_K_FOLD = "stratified_k_fold"
    TIME_SERIES_SPLIT = "time_series_split"
    LEAVE_ONE_OUT = "leave_one_out"

@dataclass
class TrainingConfig:
    """Comprehensive training configuration"""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str = ""
    model_type: str = "classifier"
    framework: str = "sklearn"
    algorithm: str = "random_forest"
    
    # Data configuration
    feature_columns: List[str] = field(default_factory=list)
    target_column: str = ""
    data_preprocessing: Dict[str, Any] = field(default_factory=dict)
    feature_engineering: Dict[str, Any] = field(default_factory=dict)
    data_validation: Dict[str, Any] = field(default_factory=dict)
    
    # Training parameters
    validation_strategy: ValidationStrategy = ValidationStrategy.TRAIN_TEST_SPLIT
    test_size: float = 0.2
    validation_size: float = 0.2
    cv_folds: int = 5
    random_state: int = 42
    stratify: bool = True
    
    # Optimization configuration
    optimization_method: OptimizationMethod = OptimizationMethod.RANDOM_SEARCH
    hyperparameter_space: Dict[str, Any] = field(default_factory=dict)
    optimization_iterations: int = 100
    optimization_timeout_minutes: int = 60
    early_stopping: bool = True
    early_stopping_patience: int = 10
    
    # Training limits
    max_training_time_hours: float = 24.0
    max_memory_gb: float = 8.0
    use_gpu: bool = True
    distributed_training: bool = False
    parallel_jobs: int = -1
    
    # Evaluation metrics
    primary_metric: str = "accuracy"
    evaluation_metrics: List[str] = field(default_factory=lambda: ["accuracy", "precision", "recall", "f1"])
    metric_greater_is_better: bool = True
    
    # Model persistence
    save_model: bool = True
    save_intermediate_models: bool = False
    model_versioning: bool = True
    model_compression: bool = False
    
    # Monitoring and logging
    log_level: str = "INFO"
    log_training_progress: bool = True
    mlflow_tracking: bool = True
    prometheus_metrics: bool = True
    
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrainingMetrics:
    """Training performance and evaluation metrics"""
    training_accuracy: float = 0.0
    validation_accuracy: float = 0.0
    test_accuracy: float = 0.0
    training_loss: float = 0.0
    validation_loss: float = 0.0
    test_loss: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    roc_auc: float = 0.0
    
    # Training progress metrics
    epochs_completed: int = 0
    total_epochs: int = 0
    training_time_seconds: float = 0.0
    convergence_epoch: Optional[int] = None
    best_score: float = 0.0
    best_epoch: int = 0
    
    # Resource utilization
    peak_memory_mb: float = 0.0
    average_cpu_percent: float = 0.0
    gpu_utilization_percent: float = 0.0
    disk_usage_mb: float = 0.0
    
    # Cross-validation metrics
    cv_scores: List[float] = field(default_factory=list)
    cv_mean: float = 0.0
    cv_std: float = 0.0
    
    # Model characteristics
    model_parameters: int = 0
    model_size_mb: float = 0.0
    inference_time_ms: float = 0.0
    
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TrainingResult:
    """Complete training job result"""
    job_id: str
    status: TrainingStatus
    model_name: str
    model_version: str
    
    # Results
    trained_model: Optional[Any] = None
    model_path: Optional[str] = None
    feature_pipeline: Optional[Any] = None
    preprocessing_pipeline: Optional[Any] = None
    
    # Performance
    metrics: Optional[TrainingMetrics] = None
    evaluation_report: Dict[str, Any] = field(default_factory=dict)
    feature_importance: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    training_config: Optional[TrainingConfig] = None
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    data_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Execution details
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    # MLflow tracking
    mlflow_run_id: Optional[str] = None
    mlflow_experiment_id: Optional[str] = None

class ModelTrainer:
    """
    Ultra-Advanced Model Training Orchestrator
    
    Comprehensive training system providing:
    - Multi-framework model training (TensorFlow, PyTorch, scikit-learn)
    - Automated hyperparameter optimization with multiple algorithms
    - Advanced cross-validation and model evaluation
    - Real-time training monitoring and resource management
    - MLOps integration with experiment tracking
    - Production-ready model pipelines and versioning
    """
    
    # Prometheus metrics
    TRAINING_JOBS_TOTAL = Counter('model_trainer_jobs_total', 'Total training jobs', ['status', 'framework'])
    TRAINING_DURATION = Histogram('model_trainer_duration_seconds', 'Training duration', ['framework', 'algorithm'])
    ACTIVE_TRAINING_JOBS = Gauge('model_trainer_active_jobs', 'Active training jobs')
    MODEL_ACCURACY = Gauge('model_trainer_best_accuracy', 'Best model accuracy', ['model_name'])
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.trainer_id = f"trainer_{uuid.uuid4().hex[:8]}"
        
        # Training job management
        self.active_jobs: Dict[str, TrainingConfig] = {}
        self.completed_jobs: Dict[str, TrainingResult] = {}
        self.job_queue = asyncio.Queue()
        
        # Resource management
        self.max_concurrent_jobs = self.config.get('max_concurrent_jobs', 3)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_concurrent_jobs)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_concurrent_jobs)
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(f"trainer_{self.trainer_id}")
        
        # MLflow integration
        self.mlflow_enabled = self.config.get('mlflow_enabled', True)
        self.mlflow_tracking_uri = self.config.get('mlflow_tracking_uri', 'http://localhost:5000')
        self.mlflow_experiment_name = self.config.get('mlflow_experiment_name', 'model_training')
        
        # Caching
        self.cache_manager = CacheManager(
            max_size=self.config.get('cache_size', 500),
            ttl_seconds=self.config.get('cache_ttl', 3600)
        )
        
        # Algorithm registry
        self.algorithm_registry = self._initialize_algorithm_registry()
        
        # Background task management
        self.background_tasks = set()
        
        logger.info(f"ModelTrainer initialized: {self.trainer_id}")
        
    async def initialize(self) -> bool:
        """Initialize the model trainer"""
        try:
            # Setup MLflow if enabled
            if self.mlflow_enabled:
                await self._setup_mlflow()
            
            # Start background job processor
            task = asyncio.create_task(self._process_training_queue())
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
            
            # Start monitoring task
            monitor_task = asyncio.create_task(self._monitor_training_jobs())
            self.background_tasks.add(monitor_task)
            monitor_task.add_done_callback(self.background_tasks.discard)
            
            logger.info("ModelTrainer successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"ModelTrainer initialization failed: {str(e)}")
            return False

    async def train_model(self, 
                         training_data: pd.DataFrame,
                         config: TrainingConfig,
                         async_execution: bool = False) -> Union[TrainingResult, str]:
        """
        Train a machine learning model with comprehensive pipeline
        
        Args:
            training_data: Input training dataset
            config: Training configuration parameters
            async_execution: Whether to execute training asynchronously
            
        Returns:
            TrainingResult: Complete training results or job_id if async
        """
        job_id = config.job_id
        
        try:
            logger.info(f"Starting training job: {job_id} ({config.model_name})")
            
            # Validate configuration
            validation_result = await self._validate_training_config(config, training_data)
            if not validation_result["valid"]:
                raise ValidationError(f"Configuration validation failed: {validation_result['errors']}")
            
            # Register job
            config.created_at = datetime.utcnow()
            self.active_jobs[job_id] = config
            
            # Update metrics
            self.TRAINING_JOBS_TOTAL.labels(status="started", framework=config.framework).inc()
            self.ACTIVE_TRAINING_JOBS.inc()
            
            if async_execution:
                # Queue for background processing
                await self.job_queue.put({
                    "job_id": job_id,
                    "training_data": training_data,
                    "config": config
                })
                return job_id
            else:
                # Execute synchronously
                result = await self._execute_training_job(training_data, config)
                
                # Clean up
                if job_id in self.active_jobs:
                    del self.active_jobs[job_id]
                self.completed_jobs[job_id] = result
                self.ACTIVE_TRAINING_JOBS.dec()
                
                return result
                
        except Exception as e:
            # Handle training failure
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
            
            self.TRAINING_JOBS_TOTAL.labels(status="failed", framework=config.framework).inc()
            self.ACTIVE_TRAINING_JOBS.dec()
            
            error_result = TrainingResult(
                job_id=job_id,
                status=TrainingStatus.FAILED,
                model_name=config.model_name,
                model_version="failed",
                error_message=str(e),
                start_time=config.created_at,
                end_time=datetime.utcnow()
            )
            
            self.completed_jobs[job_id] = error_result
            logger.error(f"Training job {job_id} failed: {str(e)}")
            
            if not async_execution:
                raise TrainingError(f"Training failed: {str(e)}")
            
            return error_result

    async def optimize_hyperparameters(self,
                                     training_data: pd.DataFrame,
                                     config: TrainingConfig,
                                     optimization_trials: int = 100) -> Dict[str, Any]:
        """
        Advanced hyperparameter optimization using multiple algorithms
        
        Supports:
        - Grid Search for exhaustive parameter exploration
        - Random Search for efficient parameter sampling
        - Bayesian Optimization for intelligent parameter selection
        - Optuna for advanced optimization algorithms
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting hyperparameter optimization: {config.optimization_method.value}")
            
            # Prepare data for optimization
            X, y = self._prepare_data_for_training(training_data, config)
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=config.validation_size, 
                random_state=config.random_state,
                stratify=y if config.stratify and len(np.unique(y)) > 1 else None
            )
            
            # Execute optimization based on method
            if config.optimization_method == OptimizationMethod.GRID_SEARCH:
                best_params = await self._grid_search_optimization(
                    X_train, X_val, y_train, y_val, config
                )
            elif config.optimization_method == OptimizationMethod.RANDOM_SEARCH:
                best_params = await self._random_search_optimization(
                    X_train, X_val, y_train, y_val, config, optimization_trials
                )
            elif config.optimization_method == OptimizationMethod.BAYESIAN:
                best_params = await self._bayesian_optimization(
                    X_train, X_val, y_train, y_val, config, optimization_trials
                )
            elif config.optimization_method == OptimizationMethod.OPTUNA and OPTUNA_AVAILABLE:
                best_params = await self._optuna_optimization(
                    X_train, X_val, y_train, y_val, config, optimization_trials
                )
            else:
                # Fallback to random search
                best_params = await self._random_search_optimization(
                    X_train, X_val, y_train, y_val, config, optimization_trials
                )
            
            optimization_time = time.time() - start_time
            
            logger.info(f"Hyperparameter optimization completed in {optimization_time:.2f}s")
            logger.info(f"Best parameters: {best_params}")
            
            return {
                "best_parameters": best_params,
                "optimization_method": config.optimization_method.value,
                "optimization_time_seconds": optimization_time,
                "trials_completed": optimization_trials
            }
            
        except Exception as e:
            logger.error(f"Hyperparameter optimization failed: {str(e)}")
            raise TrainingError(f"Hyperparameter optimization failed: {str(e)}")

    async def cross_validate_model(self,
                                 training_data: pd.DataFrame,
                                 config: TrainingConfig,
                                 cv_folds: int = 5) -> Dict[str, Any]:
        """
        Comprehensive cross-validation with multiple strategies
        """
        try:
            logger.info(f"Starting cross-validation: {config.validation_strategy.value}")
            
            # Prepare data
            X, y = self._prepare_data_for_training(training_data, config)
            
            # Get algorithm instance
            algorithm = self._get_algorithm_instance(config)
            
            # Choose cross-validation strategy
            if config.validation_strategy == ValidationStrategy.K_FOLD_CV:
                cv_splitter = KFold(n_splits=cv_folds, shuffle=True, random_state=config.random_state)
            elif config.validation_strategy == ValidationStrategy.STRATIFIED_K_FOLD:
                cv_splitter = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=config.random_state)
            elif config.validation_strategy == ValidationStrategy.TIME_SERIES_SPLIT:
                cv_splitter = TimeSeriesSplit(n_splits=cv_folds)
            else:
                cv_splitter = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=config.random_state)
            
            # Perform cross-validation
            cv_scores = cross_val_score(
                algorithm, X, y, cv=cv_splitter, 
                scoring=config.primary_metric,
                n_jobs=config.parallel_jobs
            )
            
            cv_results = {
                "cv_scores": cv_scores.tolist(),
                "cv_mean": np.mean(cv_scores),
                "cv_std": np.std(cv_scores),
                "cv_min": np.min(cv_scores),
                "cv_max": np.max(cv_scores),
                "validation_strategy": config.validation_strategy.value,
                "cv_folds": cv_folds
            }
            
            logger.info(f"Cross-validation results: {cv_results['cv_mean']:.4f} (+/- {cv_results['cv_std'] * 2:.4f})")
            
            return cv_results
            
        except Exception as e:
            logger.error(f"Cross-validation failed: {str(e)}")
            raise TrainingError(f"Cross-validation failed: {str(e)}")

    async def evaluate_model(self,
                           model: Any,
                           test_data: pd.DataFrame,
                           config: TrainingConfig) -> Dict[str, Any]:
        """
        Comprehensive model evaluation with multiple metrics
        """
        try:
            logger.info("Starting comprehensive model evaluation")
            
            # Prepare test data
            X_test, y_test = self._prepare_data_for_training(test_data, config)
            
            # Make predictions
            y_pred = model.predict(X_test)
            y_pred_proba = None
            
            if hasattr(model, 'predict_proba'):
                y_pred_proba = model.predict_proba(X_test)
            
            # Calculate evaluation metrics
            evaluation_metrics = {}
            
            if config.model_type == "classifier":
                evaluation_metrics.update({
                    "accuracy": accuracy_score(y_test, y_pred),
                    "classification_report": classification_report(y_test, y_pred, output_dict=True),
                    "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
                })
                
                # Precision, Recall, F1
                precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
                evaluation_metrics.update({
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1
                })
                
                # ROC-AUC for binary classification
                if len(np.unique(y_test)) == 2 and y_pred_proba is not None:
                    evaluation_metrics["roc_auc"] = roc_auc_score(y_test, y_pred_proba[:, 1])
                    
            elif config.model_type == "regressor":
                evaluation_metrics.update({
                    "mse": mean_squared_error(y_test, y_pred),
                    "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
                    "r2_score": r2_score(y_test, y_pred),
                    "mae": np.mean(np.abs(y_test - y_pred))
                })
            
            # Feature importance (if available)
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                feature_names = config.feature_columns
                importances = model.feature_importances_
                feature_importance = dict(zip(feature_names, importances.tolist()))
            
            evaluation_results = {
                "metrics": evaluation_metrics,
                "feature_importance": feature_importance,
                "predictions_sample": y_pred[:10].tolist(),
                "model_type": config.model_type,
                "test_samples": len(y_test)
            }
            
            logger.info(f"Model evaluation completed: {evaluation_metrics}")
            
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Model evaluation failed: {str(e)}")
            raise TrainingError(f"Model evaluation failed: {str(e)}")

    async def get_training_status(self, job_id: str) -> Dict[str, Any]:
        """Get comprehensive training job status"""
        if job_id in self.active_jobs:
            config = self.active_jobs[job_id]
            return {
                "job_id": job_id,
                "status": "active",
                "model_name": config.model_name,
                "created_at": config.created_at.isoformat(),
                "framework": config.framework,
                "algorithm": config.algorithm
            }
        elif job_id in self.completed_jobs:
            result = self.completed_jobs[job_id]
            return {
                "job_id": job_id,
                "status": result.status.value,
                "model_name": result.model_name,
                "model_version": result.model_version,
                "start_time": result.start_time.isoformat() if result.start_time else None,
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "duration_seconds": result.total_duration_seconds,
                "error_message": result.error_message
            }
        else:
            return {"job_id": job_id, "status": "not_found"}

    async def cancel_training_job(self, job_id: str) -> bool:
        """Cancel an active training job"""
        if job_id in self.active_jobs:
            # Mark for cancellation - actual cancellation depends on training stage
            config = self.active_jobs[job_id]
            logger.info(f"Cancellation requested for training job: {job_id}")
            
            # Create cancelled result
            cancelled_result = TrainingResult(
                job_id=job_id,
                status=TrainingStatus.CANCELLED,
                model_name=config.model_name,
                model_version="cancelled",
                start_time=config.created_at,
                end_time=datetime.utcnow()
            )
            
            # Clean up
            del self.active_jobs[job_id]
            self.completed_jobs[job_id] = cancelled_result
            self.ACTIVE_TRAINING_JOBS.dec()
            
            return True
        
        return False

    # Private helper methods
    async def _execute_training_job(self, 
                                  training_data: pd.DataFrame, 
                                  config: TrainingConfig) -> TrainingResult:
        """Execute complete training pipeline"""
        start_time = datetime.utcnow()
        job_id = config.job_id
        
        try:
            logger.info(f"Executing training job: {job_id}")
            
            # Initialize result
            result = TrainingResult(
                job_id=job_id,
                status=TrainingStatus.TRAINING,
                model_name=config.model_name,
                model_version=f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                start_time=start_time,
                training_config=config
            )
            
            # Start MLflow run if enabled
            mlflow_run = None
            if self.mlflow_enabled:
                mlflow_run = mlflow.start_run(run_name=f"training_{config.model_name}_{job_id[:8]}")
                result.mlflow_run_id = mlflow_run.info.run_id
                
                # Log training parameters
                mlflow.log_params({
                    "model_name": config.model_name,
                    "framework": config.framework,
                    "algorithm": config.algorithm,
                    "optimization_method": config.optimization_method.value
                })
            
            with self.performance_monitor.monitor_context():
                # Data preparation and validation
                result.status = TrainingStatus.PREPARING
                X, y = self._prepare_data_for_training(training_data, config)
                
                # Data summary
                result.data_summary = {
                    "samples": len(X),
                    "features": len(config.feature_columns),
                    "target_classes": len(np.unique(y)) if config.model_type == "classifier" else None,
                    "missing_values": X.isnull().sum().sum(),
                    "data_types": X.dtypes.value_counts().to_dict()
                }
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=config.test_size,
                    random_state=config.random_state,
                    stratify=y if config.stratify and config.model_type == "classifier" else None
                )
                
                # Hyperparameter optimization
                best_params = {}
                if config.hyperparameter_space:
                    optimization_result = await self.optimize_hyperparameters(
                        pd.concat([X_train, y_train], axis=1), config, config.optimization_iterations
                    )
                    best_params = optimization_result["best_parameters"]
                    
                    if self.mlflow_enabled:
                        mlflow.log_params(best_params)
                
                # Model training
                result.status = TrainingStatus.TRAINING
                algorithm = self._get_algorithm_instance(config, best_params)
                trained_model = algorithm.fit(X_train, y_train)
                
                result.trained_model = trained_model
                result.hyperparameters = best_params
                
                # Model evaluation
                result.status = TrainingStatus.EVALUATING
                evaluation_result = await self.evaluate_model(
                    trained_model, pd.concat([X_test, y_test], axis=1), config
                )
                result.evaluation_report = evaluation_result
                result.feature_importance = evaluation_result["feature_importance"]
                
                # Cross-validation
                if config.cv_folds > 1:
                    cv_result = await self.cross_validate_model(training_data, config, config.cv_folds)
                    result.evaluation_report["cross_validation"] = cv_result
                
                # Create training metrics
                metrics = TrainingMetrics()
                if config.model_type == "classifier":
                    metrics.test_accuracy = evaluation_result["metrics"]["accuracy"]
                    metrics.precision = evaluation_result["metrics"]["precision"]
                    metrics.recall = evaluation_result["metrics"]["recall"]
                    metrics.f1_score = evaluation_result["metrics"]["f1_score"]
                    if "roc_auc" in evaluation_result["metrics"]:
                        metrics.roc_auc = evaluation_result["metrics"]["roc_auc"]
                
                metrics.training_time_seconds = (datetime.utcnow() - start_time).total_seconds()
                result.metrics = metrics
                
                # Log metrics to MLflow
                if self.mlflow_enabled:
                    for metric_name, metric_value in evaluation_result["metrics"].items():
                        if isinstance(metric_value, (int, float)):
                            mlflow.log_metric(metric_name, metric_value)
                
                # Model persistence
                if config.save_model:
                    model_path = await self._save_trained_model(trained_model, config, result)
                    result.model_path = model_path
                    
                    if self.mlflow_enabled and model_path:
                        mlflow.log_artifact(model_path)
                
                # Update Prometheus metrics
                self.MODEL_ACCURACY.labels(model_name=config.model_name).set(
                    metrics.test_accuracy if config.model_type == "classifier" else 0.0
                )
                
                # Complete training
                result.status = TrainingStatus.COMPLETED
                result.end_time = datetime.utcnow()
                result.total_duration_seconds = (result.end_time - result.start_time).total_seconds()
                
                # Record training duration
                self.TRAINING_DURATION.labels(
                    framework=config.framework, 
                    algorithm=config.algorithm
                ).observe(result.total_duration_seconds)
                
                self.TRAINING_JOBS_TOTAL.labels(status="completed", framework=config.framework).inc()
                
                logger.info(f"Training job {job_id} completed successfully")
                
                return result
                
        except Exception as e:
            result.status = TrainingStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.utcnow()
            
            self.TRAINING_JOBS_TOTAL.labels(status="failed", framework=config.framework).inc()
            
            logger.error(f"Training job {job_id} failed: {str(e)}")
            raise
            
        finally:
            if self.mlflow_enabled and mlflow_run:
                mlflow.end_run()

    def _initialize_algorithm_registry(self) -> Dict[str, Dict[str, Any]]:
        """Initialize algorithm registry with supported algorithms"""
        return {
            "random_forest": {
                "class": RandomForestClassifier,
                "regressor_class": RandomForestRegressor,
                "hyperparameter_space": {
                    "n_estimators": [50, 100, 200, 500],
                    "max_depth": [None, 10, 20, 30],
                    "min_samples_split": [2, 5, 10],
                    "min_samples_leaf": [1, 2, 4]
                }
            },
            "gradient_boosting": {
                "class": GradientBoostingClassifier,
                "regressor_class": GradientBoostingRegressor,
                "hyperparameter_space": {
                    "n_estimators": [50, 100, 200],
                    "learning_rate": [0.01, 0.1, 0.2],
                    "max_depth": [3, 5, 7],
                    "subsample": [0.8, 0.9, 1.0]
                }
            },
            "logistic_regression": {
                "class": LogisticRegression,
                "regressor_class": Ridge,
                "hyperparameter_space": {
                    "C": [0.01, 0.1, 1.0, 10.0, 100.0],
                    "penalty": ["l1", "l2", "elasticnet"],
                    "solver": ["liblinear", "saga"]
                }
            },
            "svm": {
                "class": SVC,
                "regressor_class": SVR,
                "hyperparameter_space": {
                    "C": [0.1, 1.0, 10.0, 100.0],
                    "kernel": ["linear", "rbf", "poly"],
                    "gamma": ["scale", "auto", 0.001, 0.01, 0.1, 1.0]
                }
            },
            "neural_network": {
                "class": MLPClassifier,
                "regressor_class": MLPRegressor,
                "hyperparameter_space": {
                    "hidden_layer_sizes": [(50,), (100,), (100, 50), (200, 100, 50)],
                    "activation": ["relu", "tanh", "logistic"],
                    "learning_rate": ["constant", "adaptive"],
                    "alpha": [0.0001, 0.001, 0.01]
                }
            }
        }

    def _get_algorithm_instance(self, config: TrainingConfig, params: Dict[str, Any] = None):
        """Get algorithm instance with parameters"""
        algorithm_info = self.algorithm_registry.get(config.algorithm)
        if not algorithm_info:
            raise ValueError(f"Unsupported algorithm: {config.algorithm}")
        
        # Choose classifier or regressor
        if config.model_type == "regressor" and "regressor_class" in algorithm_info:
            algorithm_class = algorithm_info["regressor_class"]
        else:
            algorithm_class = algorithm_info["class"]
        
        # Merge default hyperparameters with provided parameters
        final_params = {**config.hyperparameter_space}
        if params:
            final_params.update(params)
        
        # Add common parameters
        if hasattr(algorithm_class, 'random_state'):
            final_params['random_state'] = config.random_state
        if hasattr(algorithm_class, 'n_jobs') and config.parallel_jobs != 1:
            final_params['n_jobs'] = config.parallel_jobs
        
        return algorithm_class(**final_params)

    def _prepare_data_for_training(self, data: pd.DataFrame, config: TrainingConfig) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for training with preprocessing"""
        # Extract features and target
        X = data[config.feature_columns].copy()
        y = data[config.target_column].copy()
        
        # Handle missing values
        X = X.fillna(X.mean() if X.select_dtypes(include=[np.number]).shape[1] > 0 else X.mode().iloc[0])
        
        # Encode categorical features
        for col in X.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
        
        # Scale features if needed
        if config.data_preprocessing.get('scale_features', False):
            scaler = StandardScaler()
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            X[numeric_cols] = scaler.fit_transform(X[numeric_cols])
        
        return X, y

    async def _validate_training_config(self, config: TrainingConfig, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate training configuration"""
        errors = []
        
        if not config.model_name:
            errors.append("Model name is required")
        
        if not config.feature_columns:
            errors.append("Feature columns must be specified")
        
        if not config.target_column:
            errors.append("Target column must be specified")
        
        if config.target_column not in data.columns:
            errors.append(f"Target column '{config.target_column}' not found in data")
        
        missing_features = [col for col in config.feature_columns if col not in data.columns]
        if missing_features:
            errors.append(f"Missing feature columns: {missing_features}")
        
        if config.algorithm not in self.algorithm_registry:
            errors.append(f"Unsupported algorithm: {config.algorithm}")
        
        return {"valid": len(errors) == 0, "errors": errors}

    async def _setup_mlflow(self):
        """Setup MLflow tracking"""
        try:
            mlflow.set_tracking_uri(self.mlflow_tracking_uri)
            mlflow.set_experiment(self.mlflow_experiment_name)
            logger.info(f"MLflow tracking setup: {self.mlflow_tracking_uri}")
        except Exception as e:
            logger.warning(f"MLflow setup failed: {str(e)}")
            self.mlflow_enabled = False

    async def _grid_search_optimization(self, X_train, X_val, y_train, y_val, config: TrainingConfig) -> Dict[str, Any]:
        """Grid search hyperparameter optimization"""
        algorithm = self._get_algorithm_instance(config)
        
        grid_search = GridSearchCV(
            algorithm,
            param_grid=config.hyperparameter_space,
            cv=config.cv_folds,
            scoring=config.primary_metric,
            n_jobs=config.parallel_jobs,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        return grid_search.best_params_

    async def _random_search_optimization(self, X_train, X_val, y_train, y_val, config: TrainingConfig, n_iterations: int) -> Dict[str, Any]:
        """Random search hyperparameter optimization"""
        algorithm = self._get_algorithm_instance(config)
        
        random_search = RandomizedSearchCV(
            algorithm,
            param_distributions=config.hyperparameter_space,
            n_iter=n_iterations,
            cv=config.cv_folds,
            scoring=config.primary_metric,
            n_jobs=config.parallel_jobs,
            random_state=config.random_state,
            verbose=1
        )
        
        random_search.fit(X_train, y_train)
        return random_search.best_params_

    async def _optuna_optimization(self, X_train, X_val, y_train, y_val, config: TrainingConfig, n_trials: int) -> Dict[str, Any]:
        """Optuna-based hyperparameter optimization"""
        def objective(trial: Trial) -> float:
            # Define hyperparameter suggestions based on algorithm
            params = {}
            algorithm_info = self.algorithm_registry[config.algorithm]
            
            for param_name, param_values in algorithm_info["hyperparameter_space"].items():
                if isinstance(param_values, list):
                    if all(isinstance(v, (int, float)) for v in param_values):
                        params[param_name] = trial.suggest_uniform(param_name, min(param_values), max(param_values))
                    else:
                        params[param_name] = trial.suggest_categorical(param_name, param_values)
            
            # Train model with suggested parameters
            algorithm = self._get_algorithm_instance(config, params)
            algorithm.fit(X_train, y_train)
            
            # Evaluate on validation set
            y_pred = algorithm.predict(X_val)
            
            if config.model_type == "classifier":
                score = accuracy_score(y_val, y_pred)
            else:
                score = -mean_squared_error(y_val, y_pred)  # Negative because Optuna maximizes
            
            return score
        
        study = create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials, timeout=config.optimization_timeout_minutes * 60)
        
        return study.best_params

    async def _save_trained_model(self, model: Any, config: TrainingConfig, result: TrainingResult) -> Optional[str]:
        """Save trained model to disk"""
        try:
            models_dir = Path(self.config.get('models_directory', 'models'))
            models_dir.mkdir(exist_ok=True)
            
            model_filename = f"{config.model_name}_{result.model_version}.pkl"
            model_path = models_dir / model_filename
            
            joblib.dump(model, model_path)
            
            logger.info(f"Model saved: {model_path}")
            return str(model_path)
            
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            return None

    async def _process_training_queue(self):
        """Background training job processor"""
        while True:
            try:
                job_data = await self.job_queue.get()
                
                job_id = job_data["job_id"]
                training_data = job_data["training_data"]
                config = job_data["config"]
                
                logger.info(f"Processing queued training job: {job_id}")
                
                try:
                    result = await self._execute_training_job(training_data, config)
                    
                    # Clean up
                    if job_id in self.active_jobs:
                        del self.active_jobs[job_id]
                    self.completed_jobs[job_id] = result
                    self.ACTIVE_TRAINING_JOBS.dec()
                    
                    logger.info(f"Queued training job completed: {job_id}")
                    
                except Exception as e:
                    # Handle training failure
                    if job_id in self.active_jobs:
                        del self.active_jobs[job_id]
                    
                    error_result = TrainingResult(
                        job_id=job_id,
                        status=TrainingStatus.FAILED,
                        model_name=config.model_name,
                        model_version="failed",
                        error_message=str(e),
                        start_time=config.created_at,
                        end_time=datetime.utcnow()
                    )
                    
                    self.completed_jobs[job_id] = error_result
                    self.ACTIVE_TRAINING_JOBS.dec()
                    
                    logger.error(f"Queued training job failed: {job_id} - {str(e)}")
                
                self.job_queue.task_done()
                
            except Exception as e:
                logger.error(f"Training queue processor error: {str(e)}")
                await asyncio.sleep(5)

    async def _monitor_training_jobs(self):
        """Background training job monitoring"""
        while True:
            try:
                # Update active jobs count
                self.ACTIVE_TRAINING_JOBS.set(len(self.active_jobs))
                
                # Check for long-running jobs
                current_time = datetime.utcnow()
                for job_id, config in list(self.active_jobs.items()):
                    job_duration = (current_time - config.created_at).total_seconds() / 3600
                    
                    if job_duration > config.max_training_time_hours:
                        logger.warning(f"Training job {job_id} exceeded maximum time limit")
                        await self.cancel_training_job(job_id)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Training job monitoring error: {str(e)}")
                await asyncio.sleep(300)


class TrainingPipeline:
    """
    Advanced Training Pipeline for End-to-End ML Workflows
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.model_trainer = ModelTrainer(config)
        self.pipeline_id = f"pipeline_{uuid.uuid4().hex[:8]}"
        
        # Pipeline components
        self.data_validators = []
        self.preprocessors = []
        self.feature_engineers = []
        self.model_trainers = []
        self.evaluators = []
        
        logger.info(f"TrainingPipeline initialized: {self.pipeline_id}")
    
    async def initialize(self) -> bool:
        """Initialize training pipeline"""
        return await self.model_trainer.initialize()
    
    async def run_pipeline(self, 
                         data_source: Union[str, pd.DataFrame],
                         pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete training pipeline"""
        try:
            logger.info(f"Starting training pipeline: {self.pipeline_id}")
            
            # Load data
            if isinstance(data_source, str):
                training_data = pd.read_csv(data_source)
            else:
                training_data = data_source
            
            # Create training configuration
            training_config = TrainingConfig(**pipeline_config)
            
            # Execute training
            result = await self.model_trainer.train_model(training_data, training_config)
            
            return {
                "pipeline_id": self.pipeline_id,
                "training_result": result,
                "pipeline_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Training pipeline failed: {str(e)}")
            return {
                "pipeline_id": self.pipeline_id,
                "error": str(e),
                "pipeline_status": "failed"
            }
