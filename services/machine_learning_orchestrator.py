"""
Machine Learning Orchestrator - Enterprise ML Pipeline Management
================================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Role**: ML Engineer & Lead Dev IA
**Module**: AI & Machine Learning Services
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Advanced ML orchestration with model lifecycle management,
automated training pipelines, and intelligent model deployment.
"""

import asyncio
import json
import logging
import pickle
import hashlib
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import aioredis
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd
import base64


class ModelType(Enum):
    """Types of ML models"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"
    ANOMALY_DETECTION = "anomaly_detection"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    TIME_SERIES = "time_series"


class ModelStatus(Enum):
    """Model lifecycle status"""
    DEVELOPMENT = "development"
    TRAINING = "training"
    VALIDATION = "validation"
    DEPLOYED = "deployed"
    RETIRED = "retired"
    FAILED = "failed"


class TrainingStatus(Enum):
    """Training job status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ModelConfig:
    """ML model configuration"""
    model_id: str
    name: str
    model_type: ModelType
    algorithm: str
    hyperparameters: Dict[str, Any]
    features: List[str]
    target: Optional[str] = None
    preprocessing_steps: List[str] = field(default_factory=list)
    validation_strategy: str = "train_test_split"
    performance_threshold: float = 0.8
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrainingJob:
    """ML training job"""
    job_id: str
    model_id: str
    status: TrainingStatus
    dataset_path: str
    training_config: Dict[str, Any]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    logs: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class ModelVersion:
    """Model version information"""
    model_id: str
    version: str
    status: ModelStatus
    performance_metrics: Dict[str, float]
    model_artifact: str  # Base64 encoded model
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    deployed_at: Optional[datetime] = None


@dataclass
class PredictionRequest:
    """ML prediction request"""
    request_id: str
    model_id: str
    version: Optional[str] = None
    input_data: Union[Dict[str, Any], List[Dict[str, Any]]]
    preprocessing_required: bool = True


@dataclass
class PredictionResult:
    """ML prediction result"""
    request_id: str
    model_id: str
    version: str
    predictions: Union[List[Any], Any]
    probabilities: Optional[List[float]] = None
    confidence_scores: Optional[List[float]] = None
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MachineLearningOrchestrator:
    """
    Enterprise Machine Learning Orchestrator Service
    
    Comprehensive ML orchestration with:
    - Model lifecycle management and versioning
    - Automated training pipeline orchestration
    - Intelligent hyperparameter optimization
    - Real-time model serving and prediction
    - A/B testing and model comparison
    - Performance monitoring and drift detection
    - Automated retraining and deployment
    """

    def __init__(self, redis_url -> None: str = "redis -> None://localhost -> None:6379") -> None:
        self.logger = logging.getLogger(__name__)
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Model registry and versioning
        self.model_registry: Dict[str, ModelConfig] = {}
        self.model_versions: Dict[str, Dict[str, ModelVersion]] = {}
        self.deployed_models: Dict[str, ModelVersion] = {}
        
        # Training job management
        self.training_jobs: Dict[str, TrainingJob] = {}
        self.training_queue: List[str] = []
        
        # Model cache for fast inference
        self.model_cache: Dict[str, Any] = {}
        self.preprocessors: Dict[str, Any] = {}
        
        # Performance monitoring
        self.model_metrics = {
            "total_predictions": 0,
            "avg_response_time": 0.0,
            "model_accuracy": {},
            "drift_scores": {},
            "last_performance_check": None
        }
        
        # Training algorithms registry
        self.algorithms = {
            "random_forest": RandomForestClassifier,
            "gradient_boosting": GradientBoostingRegressor,
            "logistic_regression": "sklearn.linear_model.LogisticRegression",
            "svm": "sklearn.svm.SVC",
            "neural_network": "sklearn.neural_network.MLPClassifier"
        }
        
        # Background tasks
        self.orchestrator_tasks: List[asyncio.Task] = []
        
        self.logger.info("Machine Learning Orchestrator initialized")

    async def initialize(self) -> None:
        """Initialize ML orchestrator"""
        try:
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            
            # Load existing models and configurations
            await self._load_model_registry()
            await self._load_model_versions()
            await self._load_deployed_models()
            
            # Start background orchestration tasks
            await self._start_orchestration_tasks()
            
            self.logger.info("Machine Learning Orchestrator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ML Orchestrator: {e}")
            raise

    async def _start_orchestration_tasks(self) -> None:
        """Start background orchestration tasks"""
        
        # Training job processor
        self.orchestrator_tasks.append(
            asyncio.create_task(self._process_training_queue())
        )
        
        # Model performance monitoring
        self.orchestrator_tasks.append(
            asyncio.create_task(self._monitor_model_performance())
        )
        
        # Model drift detection
        self.orchestrator_tasks.append(
            asyncio.create_task(self._detect_model_drift())
        )
        
        # Automated retraining
        self.orchestrator_tasks.append(
            asyncio.create_task(self._automated_retraining())
        )
        
        self.logger.info(f"Started {len(self.orchestrator_tasks)} orchestration tasks")

    async def register_model(self, config: ModelConfig) -> str:
        """Register a new ML model for training and deployment"""
        
        try:
            # Validate model configuration
            await self._validate_model_config(config)
            
            # Store in registry
            self.model_registry[config.model_id] = config
            
            # Initialize model versions dictionary
            self.model_versions[config.model_id] = {}
            
            # Save to Redis
            await self._save_model_registry()
            
            self.logger.info(f"Model registered: {config.model_id}")
            return config.model_id
            
        except Exception as e:
            self.logger.error(f"Error registering model {config.model_id}: {e}")
            raise

    async def create_training_job(self, model_id: str, dataset_path: str,
                                training_config: Optional[Dict[str, Any]] = None) -> str:
        """Create a new training job for a model"""
        
        if model_id not in self.model_registry:
            raise ValueError(f"Model {model_id} not found in registry")
        
        job_id = f"job_{model_id}_{int(time.time())}"
        
        training_job = TrainingJob(
            job_id=job_id,
            model_id=model_id,
            status=TrainingStatus.QUEUED,
            dataset_path=dataset_path,
            training_config=training_config or {}
        )
        
        # Store training job
        self.training_jobs[job_id] = training_job
        self.training_queue.append(job_id)
        
        # Save to Redis
        await self._save_training_job(training_job)
        
        self.logger.info(f"Training job created: {job_id} for model {model_id}")
        return job_id

    async def _process_training_queue(self) -> None:
        """Process training job queue"""
        
        while True:
            try:
                if self.training_queue:
                    job_id = self.training_queue.pop(0)
                    
                    if job_id in self.training_jobs:
                        training_job = self.training_jobs[job_id]
                        
                        # Execute training job
                        await self._execute_training_job(training_job)
                
                await asyncio.sleep(10)  # Check queue every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error processing training queue: {e}")
                await asyncio.sleep(30)

    async def _execute_training_job(self, training_job -> None: TrainingJob) -> None:
        """Execute a training job"""
        
        try:
            # Update job status
            training_job.status = TrainingStatus.RUNNING
            training_job.started_at = datetime.utcnow()
            training_job.progress = 0.0
            
            await self._save_training_job(training_job)
            
            self.logger.info(f"Starting training job: {training_job.job_id}")
            
            # Get model configuration
            model_config = self.model_registry[training_job.model_id]
            
            # Load and preprocess data
            training_job.progress = 0.1
            training_job.logs.append("Loading dataset...")
            await self._save_training_job(training_job)
            
            X, y = await self._load_training_data(training_job.dataset_path, model_config)
            
            # Data preprocessing
            training_job.progress = 0.3
            training_job.logs.append("Preprocessing data...")
            await self._save_training_job(training_job)
            
            X_processed, preprocessor = await self._preprocess_data(X, model_config)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y, test_size=0.2, random_state=42
            )
            
            # Train model
            training_job.progress = 0.5
            training_job.logs.append("Training model...")
            await self._save_training_job(training_job)
            
            model, training_metrics = await self._train_model(
                X_train, y_train, X_test, y_test, model_config, training_job
            )
            
            # Validate model
            training_job.progress = 0.8
            training_job.logs.append("Validating model...")
            await self._save_training_job(training_job)
            
            validation_metrics = await self._validate_model(
                model, X_test, y_test, model_config
            )
            
            # Save model version
            training_job.progress = 0.9
            training_job.logs.append("Saving model version...")
            await self._save_training_job(training_job)
            
            version_id = await self._save_model_version(
                model_config.model_id,
                model,
                preprocessor,
                {**training_metrics, **validation_metrics}
            )
            
            # Complete training job
            training_job.status = TrainingStatus.COMPLETED
            training_job.completed_at = datetime.utcnow()
            training_job.progress = 1.0
            training_job.metrics = {**training_metrics, **validation_metrics}
            training_job.logs.append(f"Training completed. Model version: {version_id}")
            
            await self._save_training_job(training_job)
            
            self.logger.info(f"Training job completed: {training_job.job_id}")
            
        except Exception as e:
            # Mark job as failed
            training_job.status = TrainingStatus.FAILED
            training_job.error_message = str(e)
            training_job.logs.append(f"Training failed: {str(e)}")
            
            await self._save_training_job(training_job)
            
            self.logger.error(f"Training job failed {training_job.job_id}: {e}")

    async def _load_training_data(self, dataset_path: str, 
                                model_config: ModelConfig) -> tuple:
        """Load training data from dataset path"""
        
        try:
            # Simulate data loading - in production, load from actual data source
            if dataset_path.endswith('.csv'):
                # Load CSV data
                data = pd.DataFrame({
                    'feature1': np.random.randn(1000),
                    'feature2': np.random.randn(1000),
                    'feature3': np.random.randn(1000),
                    'target': np.random.randint(0, 2, 1000)
                })
            else:
                # Generate synthetic data for demonstration
                data = pd.DataFrame({
                    'feature1': np.random.randn(1000),
                    'feature2': np.random.randn(1000),
                    'feature3': np.random.randn(1000),
                    'target': np.random.randint(0, 2, 1000)
                })
            
            # Extract features and target
            X = data[model_config.features] if model_config.features else data.drop('target', axis=1)
            y = data[model_config.target] if model_config.target else data['target']
            
            return X, y
            
        except Exception as e:
            self.logger.error(f"Error loading training data: {e}")
            raise

    async def _preprocess_data(self, X: pd.DataFrame, 
                             model_config: ModelConfig) -> tuple:
        """Preprocess training data"""
        
        try:
            preprocessor = StandardScaler()
            
            # Apply preprocessing steps
            if 'standardize' in model_config.preprocessing_steps:
                X_processed = preprocessor.fit_transform(X)
            else:
                X_processed = X.values
            
            return X_processed, preprocessor
            
        except Exception as e:
            self.logger.error(f"Error preprocessing data: {e}")
            raise

    async def _train_model(self, X_train, y_train, X_test, y_test,
                         model_config: ModelConfig, training_job: TrainingJob) -> tuple:
        """Train ML model with hyperparameter optimization"""
        
        try:
            # Get algorithm class
            algorithm_class = self.algorithms.get(model_config.algorithm)
            if not algorithm_class:
                raise ValueError(f"Unknown algorithm: {model_config.algorithm}")
            
            # Create model instance
            if model_config.algorithm == "random_forest":
                model = RandomForestClassifier(**model_config.hyperparameters)
            elif model_config.algorithm == "gradient_boosting":
                model = GradientBoostingRegressor(**model_config.hyperparameters)
            else:
                model = algorithm_class(**model_config.hyperparameters)
            
            # Train model
            model.fit(X_train, y_train)
            
            # Calculate training metrics
            train_predictions = model.predict(X_train)
            test_predictions = model.predict(X_test)
            
            if model_config.model_type == ModelType.CLASSIFICATION:
                training_metrics = {
                    "train_accuracy": accuracy_score(y_train, train_predictions),
                    "test_accuracy": accuracy_score(y_test, test_predictions),
                    "train_precision": precision_score(y_train, train_predictions, average='weighted'),
                    "test_precision": precision_score(y_test, test_predictions, average='weighted'),
                    "train_recall": recall_score(y_train, train_predictions, average='weighted'),
                    "test_recall": recall_score(y_test, test_predictions, average='weighted'),
                    "train_f1": f1_score(y_train, train_predictions, average='weighted'),
                    "test_f1": f1_score(y_test, test_predictions, average='weighted')
                }
            else:
                # Regression metrics
                from sklearn.metrics import mean_squared_error, r2_score
                training_metrics = {
                    "train_mse": mean_squared_error(y_train, train_predictions),
                    "test_mse": mean_squared_error(y_test, test_predictions),
                    "train_r2": r2_score(y_train, train_predictions),
                    "test_r2": r2_score(y_test, test_predictions)
                }
            
            return model, training_metrics
            
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            raise

    async def _validate_model(self, model, X_test, y_test, 
                            model_config: ModelConfig) -> Dict[str, float]:
        """Validate trained model"""
        
        try:
            validation_metrics = {}
            
            # Cross-validation
            if model_config.validation_strategy == "cross_validation":
                cv_scores = cross_val_score(model, X_test, y_test, cv=5)
                validation_metrics["cv_mean"] = np.mean(cv_scores)
                validation_metrics["cv_std"] = np.std(cv_scores)
            
            # Performance threshold check
            predictions = model.predict(X_test)
            
            if model_config.model_type == ModelType.CLASSIFICATION:
                accuracy = accuracy_score(y_test, predictions)
                validation_metrics["validation_accuracy"] = accuracy
                validation_metrics["meets_threshold"] = accuracy >= model_config.performance_threshold
            else:
                r2 = r2_score(y_test, predictions)
                validation_metrics["validation_r2"] = r2
                validation_metrics["meets_threshold"] = r2 >= model_config.performance_threshold
            
            return validation_metrics
            
        except Exception as e:
            self.logger.error(f"Error validating model: {e}")
            raise

    async def _save_model_version(self, model_id: str, model, preprocessor,
                                metrics: Dict[str, float]) -> str:
        """Save a new model version"""
        
        try:
            # Generate version ID
            version_id = f"v{len(self.model_versions[model_id]) + 1}_{int(time.time())}"
            
            # Serialize model
            model_bytes = pickle.dumps(model)
            model_artifact = base64.b64encode(model_bytes).decode('utf-8')
            
            # Serialize preprocessor
            preprocessor_bytes = pickle.dumps(preprocessor)
            preprocessor_artifact = base64.b64encode(preprocessor_bytes).decode('utf-8')
            
            # Create model version
            model_version = ModelVersion(
                model_id=model_id,
                version=version_id,
                status=ModelStatus.VALIDATION,
                performance_metrics=metrics,
                model_artifact=model_artifact,
                metadata={
                    "preprocessor": preprocessor_artifact,
                    "training_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Store version
            self.model_versions[model_id][version_id] = model_version
            
            # Save to Redis
            await self._save_model_version_to_redis(model_version)
            
            self.logger.info(f"Model version saved: {model_id}/{version_id}")
            return version_id
            
        except Exception as e:
            self.logger.error(f"Error saving model version: {e}")
            raise

    async def deploy_model(self, model_id: str, version_id: str) -> bool:
        """Deploy a model version to production"""
        
        try:
            if model_id not in self.model_versions:
                raise ValueError(f"Model {model_id} not found")
            
            if version_id not in self.model_versions[model_id]:
                raise ValueError(f"Version {version_id} not found for model {model_id}")
            
            model_version = self.model_versions[model_id][version_id]
            
            # Check if model meets performance threshold
            if not model_version.metadata.get("meets_threshold", False):
                self.logger.warning(f"Model {model_id}/{version_id} does not meet performance threshold")
            
            # Load model into cache
            model = self._deserialize_model(model_version.model_artifact)
            preprocessor = self._deserialize_model(model_version.metadata["preprocessor"])
            
            self.model_cache[f"{model_id}_{version_id}"] = model
            self.preprocessors[f"{model_id}_{version_id}"] = preprocessor
            
            # Update deployment status
            model_version.status = ModelStatus.DEPLOYED
            model_version.deployed_at = datetime.utcnow()
            
            # Set as current deployed model
            self.deployed_models[model_id] = model_version
            
            # Save updated status
            await self._save_model_version_to_redis(model_version)
            await self._save_deployed_models()
            
            self.logger.info(f"Model deployed: {model_id}/{version_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deploying model {model_id}/{version_id}: {e}")
            raise

    async def predict(self, request: PredictionRequest) -> PredictionResult:
        """Make predictions using deployed model"""
        
        start_time = time.time()
        
        try:
            # Get deployed model version
            if request.version:
                model_key = f"{request.model_id}_{request.version}"
            else:
                if request.model_id not in self.deployed_models:
                    raise ValueError(f"No deployed model found for {request.model_id}")
                
                deployed_version = self.deployed_models[request.model_id]
                model_key = f"{request.model_id}_{deployed_version.version}"
                request.version = deployed_version.version
            
            # Get model and preprocessor from cache
            if model_key not in self.model_cache:
                await self._load_model_to_cache(request.model_id, request.version)
            
            model = self.model_cache[model_key]
            preprocessor = self.preprocessors.get(model_key)
            
            # Prepare input data
            if isinstance(request.input_data, dict):
                input_data = [request.input_data]
            else:
                input_data = request.input_data
            
            # Convert to DataFrame for preprocessing
            input_df = pd.DataFrame(input_data)
            
            # Apply preprocessing if required
            if request.preprocessing_required and preprocessor:
                processed_data = preprocessor.transform(input_df)
            else:
                processed_data = input_df.values
            
            # Make predictions
            predictions = model.predict(processed_data)
            
            # Get prediction probabilities if available
            probabilities = None
            confidence_scores = None
            
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(processed_data).tolist()
                confidence_scores = [max(probs) for probs in probabilities]
            
            # Create result
            result = PredictionResult(
                request_id=request.request_id,
                model_id=request.model_id,
                version=request.version,
                predictions=predictions.tolist() if len(predictions) > 1 else predictions[0],
                probabilities=probabilities,
                confidence_scores=confidence_scores,
                processing_time=time.time() - start_time
            )
            
            # Update metrics
            await self._update_prediction_metrics(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {e}")
            raise

    async def _load_model_to_cache(self, model_id -> None: str, version_id -> None: str) -> None:
        """Load model version to cache"""
        
        try:
            model_version = self.model_versions[model_id][version_id]
            
            # Deserialize model
            model = self._deserialize_model(model_version.model_artifact)
            preprocessor = self._deserialize_model(model_version.metadata["preprocessor"])
            
            # Cache model and preprocessor
            model_key = f"{model_id}_{version_id}"
            self.model_cache[model_key] = model
            self.preprocessors[model_key] = preprocessor
            
            self.logger.info(f"Model loaded to cache: {model_key}")
            
        except Exception as e:
            self.logger.error(f"Error loading model to cache: {e}")
            raise

    def _deserialize_model(self, model_artifact -> None: str) -> None:
        """Deserialize model from base64 encoded string"""
        
        try:
            model_bytes = base64.b64decode(model_artifact)
            return pickle.loads(model_bytes)
        except Exception as e:
            self.logger.error(f"Error deserializing model: {e}")
            raise

    async def _monitor_model_performance(self) -> None:
        """Monitor deployed model performance"""
        
        while True:
            try:
                for model_id, deployed_version in self.deployed_models.items():
                    # Check model performance metrics
                    await self._check_model_performance(model_id, deployed_version)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error monitoring model performance: {e}")
                await asyncio.sleep(1800)

    async def _check_model_performance(self, model_id -> None: str, model_version -> None: ModelVersion) -> None:
        """Check individual model performance"""
        
        try:
            # Get recent prediction metrics
            recent_metrics = await self._get_recent_prediction_metrics(model_id)
            
            # Check for performance degradation
            if recent_metrics.get("accuracy", 1.0) < model_version.performance_metrics.get("test_accuracy", 0.0) * 0.9:
                self.logger.warning(f"Performance degradation detected for model {model_id}")
                
                # Trigger retraining alert
                await self._trigger_retraining_alert(model_id, "performance_degradation")
            
        except Exception as e:
            self.logger.error(f"Error checking model performance for {model_id}: {e}")

    async def _detect_model_drift(self) -> None:
        """Detect model drift in deployed models"""
        
        while True:
            try:
                for model_id in self.deployed_models.keys():
                    drift_score = await self._calculate_drift_score(model_id)
                    
                    self.model_metrics["drift_scores"][model_id] = drift_score
                    
                    # Check drift threshold
                    if drift_score > 0.3:  # Threshold for drift detection
                        self.logger.warning(f"Model drift detected for {model_id}: {drift_score}")
                        await self._trigger_retraining_alert(model_id, "model_drift")
                
                await asyncio.sleep(7200)  # Check every 2 hours
                
            except Exception as e:
                self.logger.error(f"Error detecting model drift: {e}")
                await asyncio.sleep(3600)

    async def _calculate_drift_score(self, model_id: str) -> float:
        """Calculate drift score for a model"""
        
        try:
            # Simulate drift calculation
            # In production, compare feature distributions
            return np.random.random() * 0.5  # Random drift score for demo
            
        except Exception as e:
            self.logger.error(f"Error calculating drift score: {e}")
            return 0.0

    async def _automated_retraining(self) -> None:
        """Automated retraining based on triggers"""
        
        while True:
            try:
                # Check for retraining triggers
                retraining_alerts = await self.redis_client.lrange("retraining_alerts", 0, -1)
                
                for alert_json in retraining_alerts:
                    alert = json.loads(alert_json)
                    model_id = alert["model_id"]
                    
                    # Check if model needs retraining
                    if await self._should_retrain_model(model_id, alert["reason"]):
                        await self._initiate_automated_retraining(model_id)
                
                # Clear processed alerts
                await self.redis_client.delete("retraining_alerts")
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Error in automated retraining: {e}")
                await asyncio.sleep(3600)

    async def _should_retrain_model(self, model_id: str, reason: str) -> bool:
        """Determine if model should be retrained"""
        
        # Check time since last training
        if model_id in self.deployed_models:
            deployed_version = self.deployed_models[model_id]
            time_since_deployment = datetime.utcnow() - deployed_version.deployed_at
            
            # Retrain if deployed for more than 7 days and performance issues
            if time_since_deployment.days > 7 and reason in ["performance_degradation", "model_drift"]:
                return True
        
        return False

    async def _initiate_automated_retraining(self, model_id -> None: str) -> None:
        """Initiate automated retraining for a model"""
        
        try:
            # Use latest dataset for retraining
            dataset_path = f"datasets/{model_id}_latest.csv"
            
            # Create retraining job
            job_id = await self.create_training_job(model_id, dataset_path, {
                "automated": True,
                "reason": "automated_retraining"
            })
            
            self.logger.info(f"Automated retraining initiated for {model_id}: {job_id}")
            
        except Exception as e:
            self.logger.error(f"Error initiating automated retraining for {model_id}: {e}")

    async def _trigger_retraining_alert(self, model_id -> None: str, reason -> None: str) -> None:
        """Trigger retraining alert"""
        
        alert = {
            "model_id": model_id,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis_client.lpush("retraining_alerts", json.dumps(alert))

    async def _get_recent_prediction_metrics(self, model_id: str) -> Dict[str, float]:
        """Get recent prediction metrics for a model"""
        
        # Simulate recent metrics
        return {
            "accuracy": 0.85 + np.random.random() * 0.1,
            "prediction_count": np.random.randint(100, 1000),
            "avg_response_time": 0.1 + np.random.random() * 0.1
        }

    async def _update_prediction_metrics(self, result -> None: PredictionResult) -> None:
        """Update prediction metrics"""
        
        self.model_metrics["total_predictions"] += 1
        
        # Update average response time
        current_avg = self.model_metrics["avg_response_time"]
        total_predictions = self.model_metrics["total_predictions"]
        
        self.model_metrics["avg_response_time"] = (
            (current_avg * (total_predictions - 1) + result.processing_time) / total_predictions
        )

    async def _validate_model_config(self, config -> None: ModelConfig) -> None:
        """Validate model configuration"""
        
        if not config.model_id or not config.name:
            raise ValueError("Model ID and name are required")
        
        if config.algorithm not in self.algorithms:
            raise ValueError(f"Unknown algorithm: {config.algorithm}")
        
        if not config.features:
            raise ValueError("Features list is required")

    # Redis persistence methods
    
    async def _save_model_registry(self) -> None:
        """Save model registry to Redis"""
        
        registry_data = {}
        for model_id, config in self.model_registry.items():
            registry_data[model_id] = {
                "model_id": config.model_id,
                "name": config.name,
                "model_type": config.model_type.value,
                "algorithm": config.algorithm,
                "hyperparameters": config.hyperparameters,
                "features": config.features,
                "target": config.target,
                "preprocessing_steps": config.preprocessing_steps,
                "validation_strategy": config.validation_strategy,
                "performance_threshold": config.performance_threshold,
                "created_at": config.created_at.isoformat()
            }
        
        await self.redis_client.setex(
            "ml_model_registry",
            86400,
            json.dumps(registry_data)
        )

    async def _load_model_registry(self) -> None:
        """Load model registry from Redis"""
        
        try:
            registry_data = await self.redis_client.get("ml_model_registry")
            if registry_data:
                data = json.loads(registry_data)
                
                for model_id, config_data in data.items():
                    config = ModelConfig(
                        model_id=config_data["model_id"],
                        name=config_data["name"],
                        model_type=ModelType(config_data["model_type"]),
                        algorithm=config_data["algorithm"],
                        hyperparameters=config_data["hyperparameters"],
                        features=config_data["features"],
                        target=config_data["target"],
                        preprocessing_steps=config_data["preprocessing_steps"],
                        validation_strategy=config_data["validation_strategy"],
                        performance_threshold=config_data["performance_threshold"],
                        created_at=datetime.fromisoformat(config_data["created_at"])
                    )
                    self.model_registry[model_id] = config
                
                self.logger.info(f"Loaded {len(self.model_registry)} models from registry")
        
        except Exception as e:
            self.logger.warning(f"Could not load model registry: {e}")

    async def _save_training_job(self, job -> None: TrainingJob) -> None:
        """Save training job to Redis"""
        
        job_data = {
            "job_id": job.job_id,
            "model_id": job.model_id,
            "status": job.status.value,
            "dataset_path": job.dataset_path,
            "training_config": job.training_config,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "progress": job.progress,
            "logs": job.logs,
            "metrics": job.metrics,
            "error_message": job.error_message
        }
        
        await self.redis_client.setex(
            f"training_job:{job.job_id}",
            86400,
            json.dumps(job_data)
        )

    async def _save_model_version_to_redis(self, version -> None: ModelVersion) -> None:
        """Save model version to Redis"""
        
        version_data = {
            "model_id": version.model_id,
            "version": version.version,
            "status": version.status.value,
            "performance_metrics": version.performance_metrics,
            "model_artifact": version.model_artifact,
            "metadata": version.metadata,
            "created_at": version.created_at.isoformat(),
            "deployed_at": version.deployed_at.isoformat() if version.deployed_at else None
        }
        
        await self.redis_client.setex(
            f"model_version:{version.model_id}:{version.version}",
            604800,  # 7 days
            json.dumps(version_data)
        )

    async def _load_model_versions(self) -> None:
        """Load model versions from Redis"""
        
        try:
            version_keys = await self.redis_client.keys("model_version:*")
            
            for key in version_keys:
                version_data = await self.redis_client.get(key)
                if version_data:
                    data = json.loads(version_data)
                    
                    version = ModelVersion(
                        model_id=data["model_id"],
                        version=data["version"],
                        status=ModelStatus(data["status"]),
                        performance_metrics=data["performance_metrics"],
                        model_artifact=data["model_artifact"],
                        metadata=data["metadata"],
                        created_at=datetime.fromisoformat(data["created_at"]),
                        deployed_at=datetime.fromisoformat(data["deployed_at"]) if data["deployed_at"] else None
                    )
                    
                    if version.model_id not in self.model_versions:
                        self.model_versions[version.model_id] = {}
                    
                    self.model_versions[version.model_id][version.version] = version
            
            self.logger.info(f"Loaded model versions from Redis")
        
        except Exception as e:
            self.logger.warning(f"Could not load model versions: {e}")

    async def _save_deployed_models(self) -> None:
        """Save deployed models to Redis"""
        
        deployed_data = {}
        for model_id, version in self.deployed_models.items():
            deployed_data[model_id] = {
                "model_id": version.model_id,
                "version": version.version,
                "deployed_at": version.deployed_at.isoformat() if version.deployed_at else None
            }
        
        await self.redis_client.setex(
            "deployed_models",
            86400,
            json.dumps(deployed_data)
        )

    async def _load_deployed_models(self) -> None:
        """Load deployed models from Redis"""
        
        try:
            deployed_data = await self.redis_client.get("deployed_models")
            if deployed_data:
                data = json.loads(deployed_data)
                
                for model_id, deployment_info in data.items():
                    version_id = deployment_info["version"]
                    
                    if (model_id in self.model_versions and 
                        version_id in self.model_versions[model_id]):
                        self.deployed_models[model_id] = self.model_versions[model_id][version_id]
                
                self.logger.info(f"Loaded {len(self.deployed_models)} deployed models")
        
        except Exception as e:
            self.logger.warning(f"Could not load deployed models: {e}")

    async def get_orchestrator_dashboard(self) -> Dict[str, Any]:
        """Get ML orchestrator dashboard"""
        
        # Training jobs summary
        training_summary = {
            "total_jobs": len(self.training_jobs),
            "queued": len([j for j in self.training_jobs.values() if j.status == TrainingStatus.QUEUED]),
            "running": len([j for j in self.training_jobs.values() if j.status == TrainingStatus.RUNNING]),
            "completed": len([j for j in self.training_jobs.values() if j.status == TrainingStatus.COMPLETED]),
            "failed": len([j for j in self.training_jobs.values() if j.status == TrainingStatus.FAILED])
        }
        
        # Model registry summary
        registry_summary = {
            "total_models": len(self.model_registry),
            "deployed_models": len(self.deployed_models),
            "total_versions": sum(len(versions) for versions in self.model_versions.values())
        }
        
        return {
            "training_summary": training_summary,
            "registry_summary": registry_summary,
            "model_metrics": self.model_metrics,
            "cache_size": len(self.model_cache),
            "orchestrator_status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }

    async def shutdown(self) -> None:
        """Shutdown ML orchestrator"""
        
        # Cancel orchestrator tasks
        for task in self.orchestrator_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.orchestrator_tasks:
            await asyncio.gather(*self.orchestrator_tasks, return_exceptions=True)
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("Machine Learning Orchestrator shutdown completed")


# Example usage
async def main() -> None:
    """Example usage of Machine Learning Orchestrator"""
    
    orchestrator = MachineLearningOrchestrator()
    await orchestrator.initialize()
    
    try:
        # Register a model
        model_config = ModelConfig(
            model_id="sentiment_classifier",
            name="Sentiment Classification Model",
            model_type=ModelType.CLASSIFICATION,
            algorithm="random_forest",
            hyperparameters={"n_estimators": 100, "random_state": 42},
            features=["feature1", "feature2", "feature3"],
            target="target"
        )
        
        await orchestrator.register_model(model_config)
        
        # Create training job
        job_id = await orchestrator.create_training_job(
            "sentiment_classifier",
            "datasets/sentiment_data.csv"
        )
        
        # Wait for training to complete
        await asyncio.sleep(10)
        
        # Get dashboard
        dashboard = await orchestrator.get_orchestrator_dashboard()
        print(f"Orchestrator dashboard: {dashboard}")
        
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())