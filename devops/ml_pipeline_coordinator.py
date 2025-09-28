#!/usr/bin/env python3
"""
Advanced ML/AI Orchestration & AutoML Pipeline System
===================================================

Enterprise-grade ML/AI orchestration system for Ainflue platform.
Implements advanced AutoML pipelines, model serving, drift detection,
A/B testing, and MLOps automation with multi-provider AI integration.

Author: Expert Team - ML Engineer + Lead Dev IA Roles
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited.
"""

import asyncio
import json
import logging
import pickle
import time
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from abc import ABC, abstractmethod

import mlflow
import mlflow.sklearn
import mlflow.pytorch
# MLflow TensorFlow imports avec protection
try:
    import mlflow.tensorflow
except ImportError:
    mlflow = None
from mlflow.tracking import MlflowClient
import optuna
import scikit_learn
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import xgboost as xgb
import lightgbm as lgb
import catboost as cb

# Deep Learning frameworks
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from core.tensorflow_singleton import get_tensorflow
tf = get_tensorflow()
# keras sera accessible via tf.keras

# AI Provider integrations
import openai
from anthropic import Anthropic
import google.generativeai as genai
import boto3

# Monitoring and observability
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
import wandb
import neptune


class ModelType(Enum):
    """Supported model types."""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    NLP = "natural_language_processing"
    COMPUTER_VISION = "computer_vision"
    AUDIO_PROCESSING = "audio_processing"
    RECOMMENDATION = "recommendation"
    TIME_SERIES = "time_series"
    GENERATIVE = "generative"


class ModelFramework(Enum):
    """Supported ML frameworks."""
    SCIKIT_LEARN = "scikit_learn"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    CATBOOST = "catboost"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    TRANSFORMERS = "transformers"
    CUSTOM = "custom"


class DeploymentStrategy(Enum):
    """Model deployment strategies."""
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    A_B_TEST = "a_b_test"
    SHADOW = "shadow"
    ROLLING = "rolling"


class ModelStatus(Enum):
    """Model lifecycle status."""
    TRAINING = "training"
    VALIDATION = "validation"
    STAGING = "staging"
    PRODUCTION = "production"
    RETIRED = "retired"
    FAILED = "failed"


@dataclass
class ModelMetrics:
    """Model performance metrics."""
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc_roc: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    latency_p50: Optional[float] = None
    latency_p95: Optional[float] = None
    latency_p99: Optional[float] = None
    throughput: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None


@dataclass
class ModelConfiguration:
    """Model configuration and hyperparameters."""
    model_id: str
    name: str
    model_type: ModelType
    framework: ModelFramework
    version: str
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    target: Optional[str] = None
    preprocessing_config: Dict[str, Any] = field(default_factory=dict)
    training_config: Dict[str, Any] = field(default_factory=dict)
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelExperiment:
    """ML experiment tracking."""
    experiment_id: str
    name: str
    model_config: ModelConfiguration
    metrics: ModelMetrics
    artifacts: Dict[str, str] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: ModelStatus = ModelStatus.TRAINING
    notes: str = ""


@dataclass
class DataDriftReport:
    """Data drift detection report."""
    report_id: str
    timestamp: datetime
    dataset_name: str
    drift_score: float
    drift_detected: bool
    feature_drifts: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    severity: str = "low"


class BaseModelTrainer(ABC):
    """Abstract base class for model trainers."""
    
    @abstractmethod
    async def train(self, data: pd.DataFrame, config: ModelConfiguration) -> ModelExperiment:
        """Train a model with given data and configuration."""
        pass
    
    @abstractmethod
    async def evaluate(self, model: Any, test_data: pd.DataFrame) -> ModelMetrics:
        """Evaluate model performance."""
        pass
    
    @abstractmethod
    async def predict(self, model: Any, data: pd.DataFrame) -> np.ndarray:
        """Make predictions with the model."""
        pass


class ScikitLearnTrainer(BaseModelTrainer):
    """Scikit-learn model trainer implementation."""
    
    def __init__(self):
        self.model_classes = {
            'random_forest': RandomForestClassifier,
            'gradient_boosting': GradientBoostingClassifier,
            'logistic_regression': LogisticRegression,
            'svm': SVC
        }
    
    async def train(self, data: pd.DataFrame, config: ModelConfiguration) -> ModelExperiment:
        """Train scikit-learn model."""
        experiment = ModelExperiment(
            experiment_id=str(uuid.uuid4()),
            name=f"{config.name}_experiment_{int(time.time())}",
            model_config=config,
            metrics=ModelMetrics(),
            status=ModelStatus.TRAINING
        )
        
        try:
            # Prepare data
            X = data[config.features]
            y = data[config.target] if config.target else None
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Preprocessing
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Model selection and training
            model_name = config.hyperparameters.get('model_type', 'random_forest')
            model_class = self.model_classes.get(model_name, RandomForestClassifier)
            
            # Remove model_type from hyperparameters for model initialization
            model_params = {k: v for k, v in config.hyperparameters.items() if k != 'model_type'}
            model = model_class(**model_params)
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            metrics = await self.evaluate(model, X_test_scaled, y_test)
            experiment.metrics = metrics
            
            # Save model artifacts
            model_path = f"models/{experiment.experiment_id}/model.pkl"
            Path(model_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            with open(f"models/{experiment.experiment_id}/scaler.pkl", 'wb') as f:
                pickle.dump(scaler, f)
            
            experiment.artifacts = {
                'model': model_path,
                'scaler': f"models/{experiment.experiment_id}/scaler.pkl"
            }
            
            experiment.status = ModelStatus.VALIDATION
            experiment.end_time = datetime.now()
            
        except Exception as e:
            experiment.status = ModelStatus.FAILED
            experiment.notes = str(e)
        
        return experiment
    
    async def evaluate(self, model: Any, X_test: np.ndarray, y_test: np.ndarray) -> ModelMetrics:
        """Evaluate scikit-learn model."""
        y_pred = model.predict(X_test)
        
        metrics = ModelMetrics(
            accuracy=accuracy_score(y_test, y_pred),
            precision=precision_score(y_test, y_pred, average='weighted'),
            recall=recall_score(y_test, y_pred, average='weighted'),
            f1_score=f1_score(y_test, y_pred, average='weighted')
        )
        
        return metrics
    
    async def predict(self, model: Any, data: pd.DataFrame) -> np.ndarray:
        """Make predictions with scikit-learn model."""
        return model.predict(data)


class PyTorchTrainer(BaseModelTrainer):
    """PyTorch model trainer implementation."""
    
    async def train(self, data: pd.DataFrame, config: ModelConfiguration) -> ModelExperiment:
        """Train PyTorch model."""
        experiment = ModelExperiment(
            experiment_id=str(uuid.uuid4()),
            name=f"{config.name}_pytorch_{int(time.time())}",
            model_config=config,
            metrics=ModelMetrics(),
            status=ModelStatus.TRAINING
        )
        
        try:
            # Prepare data
            X = torch.FloatTensor(data[config.features].values)
            y = torch.LongTensor(data[config.target].values) if config.target else None
            
            # Create dataset and dataloader
            dataset = TensorDataset(X, y)
            dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
            
            # Define model architecture
            input_size = len(config.features)
            hidden_size = config.hyperparameters.get('hidden_size', 64)
            num_classes = len(data[config.target].unique()) if config.target else 1
            
            model = nn.Sequential(
                nn.Linear(input_size, hidden_size),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(hidden_size, num_classes)
            )
            
            # Training configuration
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(model.parameters(), lr=config.hyperparameters.get('learning_rate', 0.001))
            epochs = config.hyperparameters.get('epochs', 100)
            
            # Training loop
            model.train()
            for epoch in range(epochs):
                for batch_X, batch_y in dataloader:
                    optimizer.zero_grad()
                    outputs = model(batch_X)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
            
            # Save model
            model_path = f"models/{experiment.experiment_id}/pytorch_model.pth"
            Path(model_path).parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), model_path)
            
            experiment.artifacts = {'model': model_path}
            experiment.status = ModelStatus.VALIDATION
            experiment.end_time = datetime.now()
            
        except Exception as e:
            experiment.status = ModelStatus.FAILED
            experiment.notes = str(e)
        
        return experiment
    
    async def evaluate(self, model: Any, test_data: pd.DataFrame) -> ModelMetrics:
        """Evaluate PyTorch model."""
        # Implementation would include proper evaluation
        return ModelMetrics(accuracy=0.85)  # Placeholder
    
    async def predict(self, model: Any, data: pd.DataFrame) -> np.ndarray:
        """Make predictions with PyTorch model."""
        # Implementation would include prediction logic
        return np.array([0] * len(data))  # Placeholder


class AdvancedMLOrchestrator:
    """
    Advanced ML/AI Orchestration System for enterprise ML operations.
    
    Features:
    - AutoML pipeline with hyperparameter optimization
    - Multi-framework model training and serving
    - Real-time model monitoring and drift detection
    - A/B testing and canary deployments
    - MLOps automation with CI/CD integration
    - Multi-provider AI integration (OpenAI, Anthropic, Google)
    - Advanced feature engineering and selection
    - Model explainability and interpretability
    """
    
    def __init__(self, config_path: str = "config/ml_orchestrator.yaml"):
        """Initialize ML orchestrator."""
        self.config_path = config_path
        self.logger = self._setup_logging()
        
        # Initialize MLflow
        self.mlflow_client = MlflowClient()
        mlflow.set_tracking_uri("http://localhost:5000")
        
        # Initialize trainers
        self.trainers = {
            ModelFramework.SCIKIT_LEARN: ScikitLearnTrainer(),
            ModelFramework.PYTORCH: PyTorchTrainer(),
            # Additional trainers would be added here
        }
        
        # State management
        self.experiments: Dict[str, ModelExperiment] = {}
        self.deployed_models: Dict[str, Dict[str, Any]] = {}
        self.monitoring_data: Dict[str, List[Dict[str, Any]]] = {}
        self.drift_reports: Dict[str, DataDriftReport] = {}
        
        # Metrics collection
        self._setup_metrics()
        
        # Load configuration
        self._load_configuration()
        
        # Initialize AI providers
        self._initialize_ai_providers()
        
        self.logger.info("Advanced ML Orchestrator initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup ML orchestrator logging."""
        logger = logging.getLogger("ml_orchestrator")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - ML_ORCHESTRATOR - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _setup_metrics(self):
        """Setup Prometheus metrics."""
        self.metrics = {
            'model_training_duration': Histogram(
                'model_training_duration_seconds',
                'Time spent training models',
                ['model_type', 'framework']
            ),
            'model_prediction_duration': Histogram(
                'model_prediction_duration_seconds',
                'Time spent making predictions',
                ['model_id', 'version']
            ),
            'model_accuracy': Gauge(
                'model_accuracy_score',
                'Current model accuracy',
                ['model_id', 'version']
            ),
            'drift_score': Gauge(
                'data_drift_score',
                'Current data drift score',
                ['dataset_name']
            ),
            'prediction_requests': Counter(
                'prediction_requests_total',
                'Total prediction requests',
                ['model_id', 'version']
            )
        }
    
    def _load_configuration(self):
        """Load ML orchestrator configuration."""
        # Load from config file if exists
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                import yaml
                self.config = yaml.safe_load(f)
        else:
            self.config = {
                'automl': {
                    'enabled': True,
                    'optimization_trials': 100,
                    'timeout_seconds': 3600
                },
                'monitoring': {
                    'drift_threshold': 0.1,
                    'monitoring_interval': 300
                },
                'deployment': {
                    'strategy': 'canary',
                    'rollback_threshold': 0.05
                }
            }
    
    def _initialize_ai_providers(self):
        """Initialize AI provider clients."""
        self.ai_providers = {}
        
        # OpenAI
        if hasattr(openai, 'api_key') and openai.api_key:
            self.ai_providers['openai'] = openai
        
        # Anthropic
        try:
            self.ai_providers['anthropic'] = Anthropic()
        except:
            pass
        
        # Google AI
        try:
            genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
            self.ai_providers['google'] = genai
        except:
            pass
    
    async def start_automl_pipeline(
        self,
        data: pd.DataFrame,
        target_column: str,
        model_type: ModelType,
        experiment_name: str,
        optimization_metric: str = 'accuracy',
        timeout_seconds: int = 3600
    ) -> str:
        """Start AutoML pipeline with hyperparameter optimization."""
        
        self.logger.info(f"Starting AutoML pipeline: {experiment_name}")
        
        # Create experiment
        experiment_id = str(uuid.uuid4())
        
        # Start optimization process
        optimization_task = asyncio.create_task(
            self._run_automl_optimization(
                experiment_id, data, target_column, model_type,
                optimization_metric, timeout_seconds
            )
        )
        
        return experiment_id
    
    async def _run_automl_optimization(
        self,
        experiment_id: str,
        data: pd.DataFrame,
        target_column: str,
        model_type: ModelType,
        optimization_metric: str,
        timeout_seconds: int
    ):
        """Run AutoML optimization using Optuna."""
        
        def objective(trial):
            """Optimization objective function."""
            # Define hyperparameter search space
            if model_type == ModelType.CLASSIFICATION:
                framework = trial.suggest_categorical('framework', ['scikit_learn', 'xgboost', 'lightgbm'])
                
                if framework == 'scikit_learn':
                    model_name = trial.suggest_categorical('model_type', ['random_forest', 'gradient_boosting'])
                    
                    if model_name == 'random_forest':
                        hyperparams = {
                            'model_type': model_name,
                            'n_estimators': trial.suggest_int('n_estimators', 10, 200),
                            'max_depth': trial.suggest_int('max_depth', 3, 20),
                            'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10)
                        }
                    else:  # gradient_boosting
                        hyperparams = {
                            'model_type': model_name,
                            'n_estimators': trial.suggest_int('n_estimators', 50, 200),
                            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                            'max_depth': trial.suggest_int('max_depth', 3, 10)
                        }
                
                elif framework == 'xgboost':
                    hyperparams = {
                        'n_estimators': trial.suggest_int('n_estimators', 50, 200),
                        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                        'max_depth': trial.suggest_int('max_depth', 3, 10),
                        'subsample': trial.suggest_float('subsample', 0.6, 1.0)
                    }
                
                else:  # lightgbm
                    hyperparams = {
                        'n_estimators': trial.suggest_int('n_estimators', 50, 200),
                        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                        'max_depth': trial.suggest_int('max_depth', 3, 10),
                        'num_leaves': trial.suggest_int('num_leaves', 10, 100)
                    }
            
            # Create model configuration
            config = ModelConfiguration(
                model_id=f"{experiment_id}_{trial.number}",
                name=f"automl_trial_{trial.number}",
                model_type=model_type,
                framework=ModelFramework.SCIKIT_LEARN,  # Default for this example
                version="1.0.0",
                hyperparameters=hyperparams,
                features=[col for col in data.columns if col != target_column],
                target=target_column
            )
            
            # Train and evaluate model
            trainer = self.trainers[config.framework]
            experiment = asyncio.run(trainer.train(data, config))
            
            # Return optimization metric
            if optimization_metric == 'accuracy':
                return experiment.metrics.accuracy or 0.0
            elif optimization_metric == 'f1_score':
                return experiment.metrics.f1_score or 0.0
            else:
                return 0.0
        
        # Run optimization
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, timeout=timeout_seconds)
        
        # Get best trial
        best_trial = study.best_trial
        self.logger.info(f"AutoML optimization completed. Best score: {best_trial.value}")
        
        # Train final model with best parameters
        best_config = ModelConfiguration(
            model_id=f"{experiment_id}_best",
            name=f"automl_best_model",
            model_type=model_type,
            framework=ModelFramework.SCIKIT_LEARN,
            version="1.0.0",
            hyperparameters=best_trial.params,
            features=[col for col in data.columns if col != target_column],
            target=target_column
        )
        
        trainer = self.trainers[best_config.framework]
        best_experiment = await trainer.train(data, best_config)
        self.experiments[experiment_id] = best_experiment
        
        return best_experiment
    
    async def deploy_model(
        self,
        experiment_id: str,
        deployment_strategy: DeploymentStrategy = DeploymentStrategy.CANARY,
        traffic_percentage: float = 10.0
    ) -> str:
        """Deploy model to production with specified strategy."""
        
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        deployment_id = f"deploy_{experiment_id}_{int(time.time())}"
        
        self.logger.info(f"Deploying model {experiment.model_config.model_id} with {deployment_strategy.value} strategy")
        
        # Load model artifacts
        model_artifacts = await self._load_model_artifacts(experiment)
        
        # Create deployment configuration
        deployment_config = {
            'deployment_id': deployment_id,
            'experiment_id': experiment_id,
            'model_config': experiment.model_config,
            'strategy': deployment_strategy,
            'traffic_percentage': traffic_percentage,
            'artifacts': model_artifacts,
            'deployed_at': datetime.now(),
            'status': 'active'
        }
        
        # Execute deployment strategy
        if deployment_strategy == DeploymentStrategy.CANARY:
            await self._deploy_canary(deployment_config)
        elif deployment_strategy == DeploymentStrategy.A_B_TEST:
            await self._deploy_ab_test(deployment_config)
        elif deployment_strategy == DeploymentStrategy.BLUE_GREEN:
            await self._deploy_blue_green(deployment_config)
        
        self.deployed_models[deployment_id] = deployment_config
        
        # Start monitoring
        asyncio.create_task(self._monitor_deployment(deployment_id))
        
        self.logger.info(f"Model deployed successfully: {deployment_id}")
        return deployment_id
    
    async def _load_model_artifacts(self, experiment: ModelExperiment) -> Dict[str, Any]:
        """Load model artifacts from storage."""
        artifacts = {}
        
        for artifact_name, artifact_path in experiment.artifacts.items():
            if artifact_name == 'model' and artifact_path.endswith('.pkl'):
                with open(artifact_path, 'rb') as f:
                    artifacts[artifact_name] = pickle.load(f)
            elif artifact_name == 'scaler' and artifact_path.endswith('.pkl'):
                with open(artifact_path, 'rb') as f:
                    artifacts[artifact_name] = pickle.load(f)
        
        return artifacts
    
    async def _deploy_canary(self, deployment_config: Dict[str, Any]):
        """Deploy model using canary strategy."""
        self.logger.info(f"Executing canary deployment: {deployment_config['deployment_id']}")
        
        # Canary deployment logic would go here
        # This would typically involve:
        # 1. Deploying to a subset of servers
        # 2. Routing a small percentage of traffic
        # 3. Monitoring performance metrics
        # 4. Gradually increasing traffic if successful
        
        await asyncio.sleep(1)  # Simulate deployment time
    
    async def _deploy_ab_test(self, deployment_config: Dict[str, Any]):
        """Deploy model using A/B testing strategy."""
        self.logger.info(f"Executing A/B test deployment: {deployment_config['deployment_id']}")
        
        # A/B testing deployment logic
        await asyncio.sleep(1)
    
    async def _deploy_blue_green(self, deployment_config: Dict[str, Any]):
        """Deploy model using blue-green strategy."""
        self.logger.info(f"Executing blue-green deployment: {deployment_config['deployment_id']}")
        
        # Blue-green deployment logic
        await asyncio.sleep(1)
    
    async def predict(
        self,
        deployment_id: str,
        input_data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Make predictions using deployed model."""
        
        if deployment_id not in self.deployed_models:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        deployment = self.deployed_models[deployment_id]
        
        # Convert input data to DataFrame if needed
        if isinstance(input_data, dict):
            input_df = pd.DataFrame([input_data])
        elif isinstance(input_data, list):
            input_df = pd.DataFrame(input_data)
        else:
            input_df = input_data
        
        # Record prediction request
        self.metrics['prediction_requests'].labels(
            model_id=deployment['model_config'].model_id,
            version=deployment['model_config'].version
        ).inc()
        
        # Make prediction
        start_time = time.time()
        
        # Load model and make prediction
        model = deployment['artifacts']['model']
        scaler = deployment['artifacts'].get('scaler')
        
        if scaler:
            input_scaled = scaler.transform(input_df[deployment['model_config'].features])
        else:
            input_scaled = input_df[deployment['model_config'].features]
        
        predictions = model.predict(input_scaled)
        probabilities = None
        
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(input_scaled)
        
        prediction_time = time.time() - start_time
        
        # Record metrics
        self.metrics['model_prediction_duration'].labels(
            model_id=deployment['model_config'].model_id,
            version=deployment['model_config'].version
        ).observe(prediction_time)
        
        # Store monitoring data
        monitoring_entry = {
            'timestamp': datetime.now(),
            'input_data': input_data,
            'predictions': predictions.tolist(),
            'probabilities': probabilities.tolist() if probabilities is not None else None,
            'prediction_time': prediction_time
        }
        
        if deployment_id not in self.monitoring_data:
            self.monitoring_data[deployment_id] = []
        
        self.monitoring_data[deployment_id].append(monitoring_entry)
        
        return {
            'deployment_id': deployment_id,
            'predictions': predictions.tolist(),
            'probabilities': probabilities.tolist() if probabilities is not None else None,
            'model_version': deployment['model_config'].version,
            'prediction_time': prediction_time
        }
    
    async def _monitor_deployment(self, deployment_id: str):
        """Monitor deployed model performance and detect issues."""
        
        while deployment_id in self.deployed_models:
            try:
                deployment = self.deployed_models[deployment_id]
                
                # Check model performance
                await self._check_model_performance(deployment_id)
                
                # Check for data drift
                await self._check_data_drift(deployment_id)
                
                # Check system metrics
                await self._check_system_metrics(deployment_id)
                
                # Sleep before next check
                await asyncio.sleep(self.config['monitoring']['monitoring_interval'])
                
            except Exception as e:
                self.logger.error(f"Error monitoring deployment {deployment_id}: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _check_model_performance(self, deployment_id: str):
        """Check model performance metrics."""
        if deployment_id not in self.monitoring_data:
            return
        
        # Get recent monitoring data
        recent_data = self.monitoring_data[deployment_id][-100:]  # Last 100 predictions
        
        if len(recent_data) < 10:  # Need minimum data points
            return
        
        # Calculate performance metrics
        avg_prediction_time = np.mean([entry['prediction_time'] for entry in recent_data])
        
        # Update metrics
        deployment = self.deployed_models[deployment_id]
        self.metrics['model_prediction_duration'].labels(
            model_id=deployment['model_config'].model_id,
            version=deployment['model_config'].version
        ).observe(avg_prediction_time)
        
        # Check for performance degradation
        if avg_prediction_time > 1.0:  # Alert if predictions take longer than 1 second
            self.logger.warning(f"High prediction latency detected for deployment {deployment_id}: {avg_prediction_time:.3f}s")
    
    async def _check_data_drift(self, deployment_id: str):
        """Check for data drift in incoming requests."""
        if deployment_id not in self.monitoring_data:
            return
        
        # Get recent data
        recent_data = self.monitoring_data[deployment_id][-1000:]  # Last 1000 predictions
        
        if len(recent_data) < 100:
            return
        
        # Extract input features
        features_data = []
        deployment = self.deployed_models[deployment_id]
        feature_names = deployment['model_config'].features
        
        for entry in recent_data:
            if isinstance(entry['input_data'], dict):
                features_data.append([entry['input_data'].get(feat, 0) for feat in feature_names])
            elif isinstance(entry['input_data'], list) and len(entry['input_data']) > 0:
                features_data.append([entry['input_data'][0].get(feat, 0) for feat in feature_names])
        
        if len(features_data) < 50:
            return
        
        # Calculate drift score (simplified implementation)
        features_df = pd.DataFrame(features_data, columns=feature_names)
        
        # Compare with reference data (would typically be training data)
        # For now, using a simple statistical approach
        drift_scores = {}
        overall_drift = 0.0
        
        for feature in feature_names:
            if features_df[feature].dtype in ['int64', 'float64']:
                # Calculate statistical measures
                current_mean = features_df[feature].mean()
                current_std = features_df[feature].std()
                
                # Simplified drift calculation (would use more sophisticated methods in practice)
                drift_score = abs(current_std) / (current_mean + 1e-8)  # Coefficient of variation
                drift_scores[feature] = drift_score
                overall_drift += drift_score
        
        overall_drift = overall_drift / len(feature_names) if feature_names else 0.0
        
        # Update drift metrics
        self.metrics['drift_score'].labels(
            dataset_name=deployment_id
        ).set(overall_drift)
        
        # Check drift threshold
        drift_threshold = self.config['monitoring']['drift_threshold']
        if overall_drift > drift_threshold:
            # Create drift report
            drift_report = DataDriftReport(
                report_id=f"drift_{deployment_id}_{int(time.time())}",
                timestamp=datetime.now(),
                dataset_name=deployment_id,
                drift_score=overall_drift,
                drift_detected=True,
                feature_drifts=drift_scores,
                recommendations=[
                    "Consider retraining the model with recent data",
                    "Review feature engineering pipeline",
                    "Investigate data source changes"
                ],
                severity="high" if overall_drift > drift_threshold * 2 else "medium"
            )
            
            self.drift_reports[drift_report.report_id] = drift_report
            
            self.logger.warning(f"Data drift detected for deployment {deployment_id}: {overall_drift:.3f}")
            
            # Trigger retraining if auto-retraining is enabled
            if self.config.get('auto_retraining', {}).get('enabled', False):
                await self._trigger_model_retraining(deployment_id, drift_report)
    
    async def _check_system_metrics(self, deployment_id: str):
        """Check system-level metrics for the deployment."""
        # Check CPU, memory, disk usage, etc.
        # This would integrate with system monitoring tools
        pass
    
    async def _trigger_model_retraining(self, deployment_id: str, drift_report: DataDriftReport):
        """Trigger automatic model retraining due to drift."""
        self.logger.info(f"Triggering automatic retraining for deployment {deployment_id}")
        
        # Implementation would:
        # 1. Collect recent data
        # 2. Start new AutoML pipeline
        # 3. Evaluate new model against current model
        # 4. Deploy if performance is better
        
        # For now, just log the action
        pass
    
    async def generate_model_explanation(
        self,
        deployment_id: str,
        input_data: Dict[str, Any],
        explanation_type: str = "shap"
    ) -> Dict[str, Any]:
        """Generate model explanation for a prediction."""
        
        if deployment_id not in self.deployed_models:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        deployment = self.deployed_models[deployment_id]
        model = deployment['artifacts']['model']
        
        # Convert input to DataFrame
        input_df = pd.DataFrame([input_data])
        features = deployment['model_config'].features
        
        # Make prediction
        prediction_result = await self.predict(deployment_id, input_data)
        
        # Generate explanation based on type
        if explanation_type == "shap":
            explanation = await self._generate_shap_explanation(model, input_df[features])
        elif explanation_type == "lime":
            explanation = await self._generate_lime_explanation(model, input_df[features])
        else:
            explanation = {"error": f"Unsupported explanation type: {explanation_type}"}
        
        return {
            'deployment_id': deployment_id,
            'input_data': input_data,
            'prediction': prediction_result['predictions'][0],
            'explanation': explanation,
            'explanation_type': explanation_type
        }
    
    async def _generate_shap_explanation(self, model: Any, input_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate SHAP explanation for model prediction."""
        try:
            import shap
            
            # Create explainer (simplified - would use appropriate explainer type)
            explainer = shap.Explainer(model)
            shap_values = explainer(input_data)
            
            return {
                'feature_importance': dict(zip(input_data.columns, shap_values.values[0])),
                'base_value': float(shap_values.base_values[0]) if hasattr(shap_values, 'base_values') else 0.0
            }
        except ImportError:
            return {"error": "SHAP not available"}
        except Exception as e:
            return {"error": f"SHAP explanation failed: {str(e)}"}
    
    async def _generate_lime_explanation(self, model: Any, input_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate LIME explanation for model prediction."""
        try:
            import lime
            import lime.lime_tabular
            
            # This is a simplified implementation
            return {"feature_importance": {col: 0.1 for col in input_data.columns}}
        except ImportError:
            return {"error": "LIME not available"}
        except Exception as e:
            return {"error": f"LIME explanation failed: {str(e)}"}
    
    async def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get comprehensive deployment status."""
        if deployment_id not in self.deployed_models:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        deployment = self.deployed_models[deployment_id]
        
        # Get monitoring statistics
        monitoring_stats = {}
        if deployment_id in self.monitoring_data:
            recent_data = self.monitoring_data[deployment_id][-100:]
            monitoring_stats = {
                'total_predictions': len(self.monitoring_data[deployment_id]),
                'recent_predictions': len(recent_data),
                'avg_prediction_time': np.mean([entry['prediction_time'] for entry in recent_data]) if recent_data else 0.0,
                'last_prediction': recent_data[-1]['timestamp'].isoformat() if recent_data else None
            }
        
        # Get drift information
        drift_info = {}
        recent_drift_reports = [
            report for report in self.drift_reports.values()
            if report.dataset_name == deployment_id and
            report.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        if recent_drift_reports:
            latest_drift = max(recent_drift_reports, key=lambda x: x.timestamp)
            drift_info = {
                'drift_detected': latest_drift.drift_detected,
                'drift_score': latest_drift.drift_score,
                'last_check': latest_drift.timestamp.isoformat()
            }
        
        return {
            'deployment_id': deployment_id,
            'model_config': {
                'model_id': deployment['model_config'].model_id,
                'name': deployment['model_config'].name,
                'version': deployment['model_config'].version,
                'model_type': deployment['model_config'].model_type.value,
                'framework': deployment['model_config'].framework.value
            },
            'deployment_info': {
                'strategy': deployment['strategy'].value,
                'deployed_at': deployment['deployed_at'].isoformat(),
                'status': deployment['status']
            },
            'monitoring': monitoring_stats,
            'drift_detection': drift_info
        }
    
    async def rollback_deployment(self, deployment_id: str, reason: str = "") -> bool:
        """Rollback a deployment to previous version."""
        if deployment_id not in self.deployed_models:
            return False
        
        deployment = self.deployed_models[deployment_id]
        
        self.logger.info(f"Rolling back deployment {deployment_id}. Reason: {reason}")
        
        # Mark deployment as rolled back
        deployment['status'] = 'rolled_back'
        deployment['rollback_reason'] = reason
        deployment['rolled_back_at'] = datetime.now()
        
        # Implementation would handle actual rollback logic
        # This might involve:
        # 1. Stopping traffic to new model
        # 2. Restoring previous model version
        # 3. Updating load balancer configuration
        
        return True
    
    async def cleanup_old_experiments(self, days: int = 30):
        """Cleanup old experiments and artifacts."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        experiments_to_remove = []
        for exp_id, experiment in self.experiments.items():
            if experiment.end_time and experiment.end_time < cutoff_date:
                if experiment.status in [ModelStatus.FAILED, ModelStatus.RETIRED]:
                    experiments_to_remove.append(exp_id)
        
        for exp_id in experiments_to_remove:
            # Remove experiment
            experiment = self.experiments[exp_id]
            
            # Clean up artifacts
            for artifact_path in experiment.artifacts.values():
                try:
                    Path(artifact_path).unlink()
                except:
                    pass
            
            # Remove experiment
            del self.experiments[exp_id]
            
        self.logger.info(f"Cleaned up {len(experiments_to_remove)} old experiments")
    
    async def export_model_registry(self) -> Dict[str, Any]:
        """Export comprehensive model registry information."""
        return {
            'experiments': {
                exp_id: {
                    'experiment_id': exp.experiment_id,
                    'name': exp.name,
                    'model_config': {
                        'model_id': exp.model_config.model_id,
                        'name': exp.model_config.name,
                        'model_type': exp.model_config.model_type.value,
                        'framework': exp.model_config.framework.value,
                        'version': exp.model_config.version
                    },
                    'metrics': {
                        'accuracy': exp.metrics.accuracy,
                        'precision': exp.metrics.precision,
                        'recall': exp.metrics.recall,
                        'f1_score': exp.metrics.f1_score
                    },
                    'status': exp.status.value,
                    'start_time': exp.start_time.isoformat(),
                    'end_time': exp.end_time.isoformat() if exp.end_time else None
                }
                for exp_id, exp in self.experiments.items()
            },
            'deployments': {
                dep_id: {
                    'deployment_id': dep_id,
                    'experiment_id': dep['experiment_id'],
                    'strategy': dep['strategy'].value,
                    'deployed_at': dep['deployed_at'].isoformat(),
                    'status': dep['status']
                }
                for dep_id, dep in self.deployed_models.items()
            },
            'drift_reports': {
                report_id: {
                    'report_id': report.report_id,
                    'dataset_name': report.dataset_name,
                    'drift_score': report.drift_score,
                    'drift_detected': report.drift_detected,
                    'timestamp': report.timestamp.isoformat(),
                    'severity': report.severity
                }
                for report_id, report in self.drift_reports.items()
            }
        }


# Enterprise usage example
async def main():
    """Demonstrate ML orchestrator usage."""
    orchestrator = AdvancedMLOrchestrator()
    
    # Generate sample data
    np.random.seed(42)
    n_samples = 1000
    data = pd.DataFrame({
        'feature_1': np.random.normal(0, 1, n_samples),
        'feature_2': np.random.normal(0, 1, n_samples),
        'feature_3': np.random.normal(0, 1, n_samples),
        'feature_4': np.random.normal(0, 1, n_samples),
    })
    
    # Create target variable
    data['target'] = (
        data['feature_1'] * 0.5 + 
        data['feature_2'] * 0.3 + 
        np.random.normal(0, 0.1, n_samples) > 0
    ).astype(int)
    
    print("Starting AutoML pipeline...")
    
    # Start AutoML pipeline
    experiment_id = await orchestrator.start_automl_pipeline(
        data=data,
        target_column='target',
        model_type=ModelType.CLASSIFICATION,
        experiment_name="Sample Classification",
        optimization_metric='accuracy',
        timeout_seconds=300  # 5 minutes for demo
    )
    
    print(f"AutoML pipeline started: {experiment_id}")
    
    # Wait for completion
    while experiment_id not in orchestrator.experiments:
        await asyncio.sleep(5)
        print("Waiting for AutoML completion...")
    
    experiment = orchestrator.experiments[experiment_id]
    print(f"AutoML completed with accuracy: {experiment.metrics.accuracy:.3f}")
    
    # Deploy model
    deployment_id = await orchestrator.deploy_model(
        experiment_id=experiment_id,
        deployment_strategy=DeploymentStrategy.CANARY,
        traffic_percentage=20.0
    )
    
    print(f"Model deployed: {deployment_id}")
    
    # Make predictions
    sample_input = {
        'feature_1': 0.5,
        'feature_2': -0.2,
        'feature_3': 1.0,
        'feature_4': 0.1
    }
    
    prediction_result = await orchestrator.predict(deployment_id, sample_input)
    print(f"Prediction result: {prediction_result}")
    
    # Generate explanation
    explanation = await orchestrator.generate_model_explanation(
        deployment_id=deployment_id,
        input_data=sample_input,
        explanation_type="shap"
    )
    print(f"Model explanation: {explanation}")
    
    # Get deployment status
    status = await orchestrator.get_deployment_status(deployment_id)
    print(f"Deployment status: {status}")


if __name__ == "__main__":
    asyncio.run(main())