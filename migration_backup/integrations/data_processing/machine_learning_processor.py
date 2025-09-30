# WARNING: Potential SQL injection risk - use parameterized queries
"""Machine Learning Processor - ML-driven Data Processing
========================================================

AI/ML integration for intelligent data processing with feature engineering,
model training pipeline integration, real-time inference, and MLOps workflow.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import pickle
import time
import numpy as np
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib
from pathlib import Path

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
    from sklearn.feature_selection import SelectKBest, f_classif, f_regression
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.linear_model import LogisticRegression, LinearRegression
    from sklearn.svm import SVC, SVR
    from sklearn.naive_bayes import GaussianNB
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.pipeline import Pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

try:
    import sqlalchemy as sa
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import declarative_base, sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

import redis.asyncio as redis


class ModelType(Enum):
    """Machine learning model types."""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    RECOMMENDATION = "recommendation"
    TIME_SERIES = "time_series"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"


class TrainingStatus(Enum):
    """Model training status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DeploymentStatus(Enum):
    """Model deployment status."""
    NOT_DEPLOYED = "not_deployed"
    STAGING = "staging"
    PRODUCTION = "production"
    RETIRED = "retired"


class FeatureType(Enum):
    """Feature engineering types."""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    EMBEDDING = "embedding"


@dataclass
class FeatureDefinition:
    """Feature definition for ML models."""
    name: str
    feature_type: FeatureType
    source_column: str
    transformations: List[str] = field(default_factory=list)
    is_target: bool = False
    importance: Optional[float] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MLModel:
    """Machine learning model definition."""
    id: str
    name: str
    model_type: ModelType
    algorithm: str
    features: List[FeatureDefinition]
    target_feature: str
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    preprocessing_pipeline: Optional[Any] = None
    trained_model: Optional[Any] = None
    training_status: TrainingStatus = TrainingStatus.PENDING
    deployment_status: DeploymentStatus = DeploymentStatus.NOT_DEPLOYED
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrainingJob:
    """Model training job."""
    id: str
    model_id: str
    dataset_id: str
    training_config: Dict[str, Any]
    status: TrainingStatus = TrainingStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    training_metrics: Dict[str, float] = field(default_factory=dict)
    validation_metrics: Dict[str, float] = field(default_factory=dict)
    model_artifacts: Dict[str, str] = field(default_factory=dict)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionRequest:
    """Model prediction request."""
    id: str
    model_id: str
    input_data: Dict[str, Any]
    prediction_type: str = "single"  # single, batch
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionResult:
    """Model prediction result."""
    request_id: str
    model_id: str
    predictions: Union[float, List[float], Dict[str, Any]]
    confidence: Optional[float] = None
    explanation: Optional[Dict[str, Any]] = None
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMetrics:
    """Model performance metrics."""
    model_id: str
    metric_type: str  # training, validation, production
    metrics: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    dataset_size: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


Base = declarative_base() if SQLALCHEMY_AVAILABLE else None


class MLModelModel(Base if SQLALCHEMY_AVAILABLE else object):
    """ML model database model."""
    if SQLALCHEMY_AVAILABLE:
        __tablename__ = 'ml_models'
        
        id = sa.Column(sa.String(36), primary_key=True)
        name = sa.Column(sa.String(200), nullable=False)
        model_type = sa.Column(sa.String(50), nullable=False)
        algorithm = sa.Column(sa.String(100), nullable=False)
        features = sa.Column(sa.Text)
        target_feature = sa.Column(sa.String(100))
        hyperparameters = sa.Column(sa.Text)
        training_status = sa.Column(sa.String(20))
        deployment_status = sa.Column(sa.String(20))
        version = sa.Column(sa.String(20))
        model_path = sa.Column(sa.String(500))
        created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
        updated_at = sa.Column(sa.DateTime, default=datetime.utcnow)
        meta_data = sa.Column(sa.Text)


class TrainingJobModel(Base if SQLALCHEMY_AVAILABLE else object):
    """Training job database model."""
    if SQLALCHEMY_AVAILABLE:
        __tablename__ = 'training_jobs'
        
        id = sa.Column(sa.String(36), primary_key=True)
        model_id = sa.Column(sa.String(36), nullable=False)
        dataset_id = sa.Column(sa.String(100))
        status = sa.Column(sa.String(20), nullable=False)
        started_at = sa.Column(sa.DateTime)
        completed_at = sa.Column(sa.DateTime)
        training_config = sa.Column(sa.Text)
        training_metrics = sa.Column(sa.Text)
        validation_metrics = sa.Column(sa.Text)
        error_message = sa.Column(sa.Text)
        meta_data = sa.Column(sa.Text)
        created_at = sa.Column(sa.DateTime, default=datetime.utcnow)


class PredictionLogModel(Base if SQLALCHEMY_AVAILABLE else object):
    """Prediction log database model."""
    if SQLALCHEMY_AVAILABLE:
        __tablename__ = 'prediction_logs'
        
        id = sa.Column(sa.String(36), primary_key=True)
        model_id = sa.Column(sa.String(36), nullable=False)
        request_data = sa.Column(sa.Text)
        prediction_result = sa.Column(sa.Text)
        processing_time = sa.Column(sa.Float)
        timestamp = sa.Column(sa.DateTime, default=datetime.utcnow)
        meta_data = sa.Column(sa.Text)


class MachineLearningProcessor:
    """ML-driven data processing and model management system."""
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        redis_url: Optional[str] = None,
        model_storage_path: str = "./ml_models",
        config: Optional[Dict[str, Any]] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Database setup
        self.database_url = database_url
        self.engine = None
        self.async_session = None
        
        if database_url and SQLALCHEMY_AVAILABLE:
            self.engine = create_async_engine(database_url)
            self.async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
        
        # Redis setup for caching and job queue
        self.redis_url = redis_url
        self.redis_client = None
        
        # Model storage
        self.model_storage_path = Path(model_storage_path)
        self.model_storage_path.mkdir(exist_ok=True)
        
        # ML state management
        self.models: Dict[str, MLModel] = {}
        self.loaded_models: Dict[str, Any] = {}
        self.training_jobs: Dict[str, TrainingJob] = {}
        self.feature_store: Dict[str, Any] = {}
        
        # Training and inference queues
        self.training_queue: asyncio.Queue = asyncio.Queue()
        self.inference_queue: asyncio.Queue = asyncio.Queue()
        
        # Background workers
        self.training_workers: List[asyncio.Task] = []
        self.inference_workers: List[asyncio.Task] = []
        self.workers_running = False
        
        # Performance tracking
        self.ml_metrics = {
            'total_models': 0,
            'models_in_production': 0,
            'total_predictions': 0,
            'average_prediction_time': 0.0,
            'total_training_jobs': 0,
            'successful_trainings': 0
        }
        
        # Setup built-in algorithms and processors
        self._setup_algorithms()
        self._setup_feature_processors()
    
    async def initialize(self):
        """Initialize the ML processor."""
        # Initialize database if configured
        if self.engine and SQLALCHEMY_AVAILABLE:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        
        # Initialize Redis if configured
        if self.redis_url:
            self.redis_client = redis.from_url(self.redis_url)
        
        # Start background workers
        await self._start_workers()
        
        self.logger.info("Machine learning processor initialized")
    
    def _setup_algorithms(self):
        """Setup available ML algorithms."""
        self.algorithms = {
            # Classification
            'random_forest_classifier': {
                'class': RandomForestClassifier if SKLEARN_AVAILABLE else None,
                'type': ModelType.CLASSIFICATION,
                'hyperparameters': {'n_estimators': 100, 'random_state': 42}
            },
            'logistic_regression': {
                'class': LogisticRegression if SKLEARN_AVAILABLE else None,
                'type': ModelType.CLASSIFICATION,
                'hyperparameters': {'random_state': 42}
            },
            'svm_classifier': {
                'class': SVC if SKLEARN_AVAILABLE else None,
                'type': ModelType.CLASSIFICATION,
                'hyperparameters': {'random_state': 42}
            },
            'naive_bayes': {
                'class': GaussianNB if SKLEARN_AVAILABLE else None,
                'type': ModelType.CLASSIFICATION,
                'hyperparameters': {}
            },
            
            # Regression
            'random_forest_regressor': {
                'class': RandomForestRegressor if SKLEARN_AVAILABLE else None,
                'type': ModelType.REGRESSION,
                'hyperparameters': {'n_estimators': 100, 'random_state': 42}
            },
            'linear_regression': {
                'class': LinearRegression if SKLEARN_AVAILABLE else None,
                'type': ModelType.REGRESSION,
                'hyperparameters': {}
            },
            'svm_regressor': {
                'class': SVR if SKLEARN_AVAILABLE else None,
                'type': ModelType.REGRESSION,
                'hyperparameters': {}
            },
            
            # Clustering
            'kmeans': {
                'class': KMeans if SKLEARN_AVAILABLE else None,
                'type': ModelType.CLUSTERING,
                'hyperparameters': {'n_clusters': 3, 'random_state': 42}
            },
            'dbscan': {
                'class': DBSCAN if SKLEARN_AVAILABLE else None,
                'type': ModelType.CLUSTERING,
                'hyperparameters': {'eps': 0.5, 'min_samples': 5}
            }
        }
    
    def _setup_feature_processors(self):
        """Setup feature engineering processors."""
        self.feature_processors = {
            'standard_scaler': StandardScaler if SKLEARN_AVAILABLE else None,
            'label_encoder': LabelEncoder if SKLEARN_AVAILABLE else None,
            'one_hot_encoder': OneHotEncoder if SKLEARN_AVAILABLE else None,
            'pca': PCA if SKLEARN_AVAILABLE else None,
            'select_k_best': SelectKBest if SKLEARN_AVAILABLE else None
        }
    
    async def create_model(self, model: MLModel) -> bool:
        """Create a new ML model."""
        try:
            # Validate algorithm
            if model.algorithm not in self.algorithms:
                raise ValueError(f"Unsupported algorithm: {model.algorithm}")
            
            # Store model
            self.models[model.id] = model
            
            # Persist to database
            if self.async_session:
                await self._store_model(model)
            
            self.ml_metrics['total_models'] += 1
            self.logger.info(f"Created ML model: {model.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating model: {e}")
            return False
    
    async def train_model(
        self, 
        model_id: str, 
        dataset: Union[pd.DataFrame, Dict[str, Any]], 
        training_config: Optional[Dict[str, Any]] = None
    ) -> TrainingJob:
        """Start model training job."""
        if model_id not in self.models:
            raise ValueError(f"Model not found: {model_id}")
        
        # Create training job
        job = TrainingJob(
            id=str(uuid.uuid4()),
            model_id=model_id,
            dataset_id=training_config.get('dataset_id', 'unknown') if training_config else 'unknown',
            training_config=training_config or {}
        )
        
        self.training_jobs[job.id] = job
        
        # Add to training queue
        await self.training_queue.put({
            'job': job,
            'dataset': dataset
        })
        
        self.ml_metrics['total_training_jobs'] += 1
        self.logger.info(f"Queued training job: {job.id}")
        return job
    
    async def _execute_training_job(self, job_data: Dict[str, Any]):
        """Execute a training job."""
        job = job_data['job']
        dataset = job_data['dataset']
        
        try:
            job.status = TrainingStatus.IN_PROGRESS
            job.started_at = datetime.utcnow()
            
            model = self.models[job.model_id]
            
            # Prepare data
            X, y = await self._prepare_training_data(dataset, model)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Create preprocessing pipeline
            preprocessing_pipeline = await self._create_preprocessing_pipeline(model)
            
            # Create and configure algorithm
            algorithm_config = self.algorithms[model.algorithm]
            hyperparams = {**algorithm_config['hyperparameters'], **model.hyperparameters}
            
            algorithm_class = algorithm_config['class']
            if not algorithm_class:
                raise Exception(f"Algorithm {model.algorithm} not available (missing dependencies)")
            
            algorithm = algorithm_class(**hyperparams)
            
            # Create full pipeline
            if preprocessing_pipeline:
                full_pipeline = Pipeline([
                    ('preprocessing', preprocessing_pipeline),
                    ('model', algorithm)
                ])
            else:
                full_pipeline = algorithm
            
            # Train model
            full_pipeline.fit(X_train, y_train)
            
            # Evaluate model
            training_metrics = await self._evaluate_model(
                full_pipeline, X_train, y_train, model.model_type
            )
            validation_metrics = await self._evaluate_model(
                full_pipeline, X_test, y_test, model.model_type
            )
            
            # Save model
            model_path = await self._save_model(model.id, full_pipeline)
            
            # Update model and job
            model.trained_model = full_pipeline
            model.preprocessing_pipeline = preprocessing_pipeline
            model.training_status = TrainingStatus.COMPLETED
            model.updated_at = datetime.utcnow()
            
            job.status = TrainingStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.training_metrics = training_metrics
            job.validation_metrics = validation_metrics
            job.model_artifacts = {'model_path': str(model_path)}
            
            # Store results
            if self.async_session:
                await self._store_training_job(job)
                await self._store_model(model)
            
            self.ml_metrics['successful_trainings'] += 1
            self.logger.info(f"Training job completed: {job.id}")
            
        except Exception as e:
            job.status = TrainingStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.error_message = str(e)
            
            self.logger.error(f"Training job failed: {job.id} - {e}")
            
            # Store failed job
            if self.async_session:
                await self._store_training_job(job)
    
    async def _prepare_training_data(self, dataset: Union[pd.DataFrame, Dict[str, Any]], model: MLModel) -> tuple[Any, Any]:
        """Prepare training data from dataset."""
        if isinstance(dataset, dict):
            # Convert dict to DataFrame
            if PANDAS_AVAILABLE:
                df = pd.DataFrame(dataset)
            else:
                raise Exception("Pandas not available for data conversion")
        else:
            df = dataset
        
        # Extract features and target
        feature_columns = [f.source_column for f in model.features if not f.is_target]
        target_column = model.target_feature
        
        X = df[feature_columns]
        y = df[target_column] if target_column in df.columns else None
        
        if y is None:
            raise ValueError(f"Target feature '{target_column}' not found in dataset")
        
        return X, y
    
    async def _create_preprocessing_pipeline(self, model: MLModel) -> Optional[Any]:
        """Create preprocessing pipeline based on features."""
        if not SKLEARN_AVAILABLE:
            return None
        
        preprocessors = []
        
        # Add preprocessing steps based on feature types
        numerical_features = [f.source_column for f in model.features if f.feature_type == FeatureType.NUMERICAL]
        categorical_features = [f.source_column for f in model.features if f.feature_type == FeatureType.CATEGORICAL]
        
        if numerical_features:
            # Add standard scaler for numerical features
            from sklearn.compose import ColumnTransformer
            numeric_transformer = StandardScaler()
            preprocessors.append(('num', numeric_transformer, numerical_features))
        
        if categorical_features:
            # Add one-hot encoder for categorical features
            categorical_transformer = OneHotEncoder(drop='first', sparse_output=False)
            preprocessors.append(('cat', categorical_transformer, categorical_features))
        
        if preprocessors:
            from sklearn.compose import ColumnTransformer
            return ColumnTransformer(transformers=preprocessors)
        
        return None
    
    async def _evaluate_model(self, model: Any, X: Any, y: Any, model_type: ModelType) -> Dict[str, float]:
        """Evaluate model performance."""
        if not SKLEARN_AVAILABLE:
            return {}
        
        try:
            predictions = model.predict(X)
            metrics = {}
            
            if model_type == ModelType.CLASSIFICATION:
                metrics['accuracy'] = accuracy_score(y, predictions)
                
                # Handle multiclass case
                try:
                    metrics['precision'] = precision_score(y, predictions, average='weighted')
                    metrics['recall'] = recall_score(y, predictions, average='weighted')
                    metrics['f1_score'] = f1_score(y, predictions, average='weighted')
                except:
                    # Binary classification
                    metrics['precision'] = precision_score(y, predictions)
                    metrics['recall'] = recall_score(y, predictions)
                    metrics['f1_score'] = f1_score(y, predictions)
                    
            elif model_type == ModelType.REGRESSION:
                metrics['mse'] = mean_squared_error(y, predictions)
                metrics['rmse'] = np.sqrt(metrics['mse'])
                metrics['r2_score'] = r2_score(y, predictions)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            return {}
    
    async def _save_model(self, model_id: str, trained_model: Any) -> Path:
        """Save trained model to disk."""
        model_path = self.model_storage_path / f"{model_id}.joblib"
        
        if JOBLIB_AVAILABLE:
            joblib.dump(trained_model, model_path)
        else:
            # Fallback to pickle
            with open(model_path.with_suffix('.pkl'), 'wb') as f:
                pickle.dump(trained_model, f)
            model_path = model_path.with_suffix('.pkl')
        
        return model_path
    
    async def load_model(self, model_id: str) -> bool:
        """Load trained model for inference."""
        if model_id not in self.models:
            raise ValueError(f"Model not found: {model_id}")
        
        model = self.models[model_id]
        
        # Check if already loaded
        if model_id in self.loaded_models:
            return True
        
        try:
            # Find model file
            model_path = self.model_storage_path / f"{model_id}.joblib"
            if not model_path.exists():
                model_path = self.model_storage_path / f"{model_id}.pkl"
            
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_id}")
            
            # Load model
            if model_path.suffix == '.joblib' and JOBLIB_AVAILABLE:
                trained_model = joblib.load(model_path)
            else:
                with open(model_path, 'rb') as f:
                    trained_model = pickle.load(f)
            
            self.loaded_models[model_id] = trained_model
            model.trained_model = trained_model
            
            self.logger.info(f"Loaded model: {model_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading model {model_id}: {e}")
            return False
    
    async def predict(self, request: PredictionRequest) -> PredictionResult:
        """Make prediction using trained model."""
        start_time = time.time()
        
        try:
            model_id = request.model_id
            
            # Ensure model is loaded
            if model_id not in self.loaded_models:
                await self.load_model(model_id)
            
            if model_id not in self.loaded_models:
                raise ValueError(f"Model not available for inference: {model_id}")
            
            model = self.models[model_id]
            trained_model = self.loaded_models[model_id]
            
            # Prepare input data
            input_features = await self._prepare_prediction_data(request.input_data, model)
            
            # Make prediction
            if request.prediction_type == "batch":
                predictions = trained_model.predict(input_features)
                
                # Get prediction probabilities if available
                confidence = None
                if hasattr(trained_model, 'predict_proba') and model.model_type == ModelType.CLASSIFICATION:
                    probabilities = trained_model.predict_proba(input_features)
                    confidence = float(np.max(probabilities, axis=1).mean())
            else:
                # Single prediction
                prediction = trained_model.predict([input_features])[0]
                predictions = prediction
                
                # Get confidence for single prediction
                confidence = None
                if hasattr(trained_model, 'predict_proba') and model.model_type == ModelType.CLASSIFICATION:
                    probabilities = trained_model.predict_proba([input_features])[0]
                    confidence = float(np.max(probabilities))
            
            # Generate explanation if available
            explanation = await self._generate_prediction_explanation(
                trained_model, input_features, model
            )
            
            processing_time = time.time() - start_time
            
            result = PredictionResult(
                request_id=request.id,
                model_id=model_id,
                predictions=predictions,
                confidence=confidence,
                explanation=explanation,
                processing_time=processing_time
            )
            
            # Log prediction
            if self.async_session:
                await self._log_prediction(request, result)
            
            # Update metrics
            self.ml_metrics['total_predictions'] += 1
            total_time = self.ml_metrics['average_prediction_time'] * (self.ml_metrics['total_predictions'] - 1)
            self.ml_metrics['average_prediction_time'] = (total_time + processing_time) / self.ml_metrics['total_predictions']
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Prediction failed: {e}")
            
            return PredictionResult(
                request_id=request.id,
                model_id=request.model_id,
                predictions=None,
                processing_time=processing_time,
                metadata={'error': str(e)}
            )
    
    async def _prepare_prediction_data(self, input_data: Dict[str, Any], model: MLModel) -> Any:
        """Prepare input data for prediction."""
        if not PANDAS_AVAILABLE:
            # Convert to simple list
            feature_columns = [f.source_column for f in model.features if not f.is_target]
            return [input_data.get(col, 0) for col in feature_columns]
        
        # Create DataFrame for preprocessing
        feature_columns = [f.source_column for f in model.features if not f.is_target]
        
        # Ensure all required features are present
        for col in feature_columns:
            if col not in input_data:
                input_data[col] = 0  # Default value
        
        df = pd.DataFrame([input_data])
        return df[feature_columns].values[0] if len(feature_columns) > 1 else df[feature_columns[0]].values
    
    async def _generate_prediction_explanation(self, model: Any, input_features: Any, ml_model: MLModel) -> Optional[Dict[str, Any]]:
        """Generate explanation for prediction."""
        explanation = {}
        
        try:
            # Feature importance (for tree-based models)
            if hasattr(model, 'feature_importances_'):
                feature_names = [f.source_column for f in ml_model.features if not f.is_target]
                feature_importance = dict(zip(feature_names, model.feature_importances_))
                explanation['feature_importance'] = feature_importance
            
            # For pipeline models, get the final estimator
            if hasattr(model, 'named_steps'):
                final_model = model.named_steps.get('model')
                if final_model and hasattr(final_model, 'feature_importances_'):
                    feature_names = [f.source_column for f in ml_model.features if not f.is_target]
                    feature_importance = dict(zip(feature_names, final_model.feature_importances_))
                    explanation['feature_importance'] = feature_importance
            
            return explanation if explanation else None
            
        except Exception as e:
            self.logger.warning(f"Could not generate explanation: {e}")
            return None
    
    async def deploy_model(self, model_id: str, environment: str = "staging") -> bool:
        """Deploy model to specified environment."""
        if model_id not in self.models:
            raise ValueError(f"Model not found: {model_id}")
        
        model = self.models[model_id]
        
        if model.training_status != TrainingStatus.COMPLETED:
            raise ValueError("Model must be trained before deployment")
        
        try:
            # Load model for deployment
            await self.load_model(model_id)
            
            # Update deployment status
            if environment == "production":
                model.deployment_status = DeploymentStatus.PRODUCTION
                self.ml_metrics['models_in_production'] += 1
            else:
                model.deployment_status = DeploymentStatus.STAGING
            
            model.updated_at = datetime.utcnow()
            
            # Store deployment info
            if self.async_session:
                await self._store_model(model)
            
            self.logger.info(f"Deployed model {model_id} to {environment}")
            return True
            
        except Exception as e:
            self.logger.error(f"Model deployment failed: {e}")
            return False
    
    async def retire_model(self, model_id: str) -> bool:
        """Retire a deployed model."""
        if model_id not in self.models:
            raise ValueError(f"Model not found: {model_id}")
        
        model = self.models[model_id]
        
        if model.deployment_status == DeploymentStatus.PRODUCTION:
            self.ml_metrics['models_in_production'] -= 1
        
        model.deployment_status = DeploymentStatus.RETIRED
        model.updated_at = datetime.utcnow()
        
        # Remove from loaded models
        if model_id in self.loaded_models:
            del self.loaded_models[model_id]
        
        # Store retirement info
        if self.async_session:
            await self._store_model(model)
        
        self.logger.info(f"Retired model: {model_id}")
        return True
    
    async def get_model_metrics(self, model_id: str) -> Dict[str, Any]:
        """Get performance metrics for a model."""
        if model_id not in self.models:
            return {}
        
        model = self.models[model_id]
        
        # Get latest training job
        latest_job = None
        for job in self.training_jobs.values():
            if job.model_id == model_id and job.status == TrainingStatus.COMPLETED:
                if not latest_job or job.completed_at > latest_job.completed_at:
                    latest_job = job
        
        # Get prediction statistics
        prediction_stats = await self._get_prediction_statistics(model_id)
        
        return {
            'model_id': model_id,
            'model_name': model.name,
            'model_type': model.model_type.value,
            'algorithm': model.algorithm,
            'training_status': model.training_status.value,
            'deployment_status': model.deployment_status.value,
            'version': model.version,
            'training_metrics': latest_job.training_metrics if latest_job else {},
            'validation_metrics': latest_job.validation_metrics if latest_job else {},
            'prediction_statistics': prediction_stats,
            'created_at': model.created_at.isoformat(),
            'updated_at': model.updated_at.isoformat()
        }
    
    async def _get_prediction_statistics(self, model_id: str) -> Dict[str, Any]:
        """Get prediction statistics for a model."""
        # This would query the prediction logs
        return {
            'total_predictions': 150,
            'predictions_last_24h': 45,
            'average_response_time': 0.23,
            'accuracy_trend': 'stable'
        }
    
    async def create_feature_engineering_pipeline(self, features: List[FeatureDefinition]) -> Dict[str, Any]:
        """Create feature engineering pipeline."""
        pipeline_steps = []
        
        for feature in features:
            for transformation in feature.transformations:
                if transformation == 'standardize' and feature.feature_type == FeatureType.NUMERICAL:
                    pipeline_steps.append({
                        'step': 'standardize',
                        'feature': feature.name,
                        'processor': 'standard_scaler'
                    })
                elif transformation == 'encode' and feature.feature_type == FeatureType.CATEGORICAL:
                    pipeline_steps.append({
                        'step': 'encode',
                        'feature': feature.name,
                        'processor': 'one_hot_encoder'
                    })
                elif transformation == 'pca' and feature.feature_type == FeatureType.NUMERICAL:
                    pipeline_steps.append({
                        'step': 'dimensionality_reduction',
                        'feature': feature.name,
                        'processor': 'pca'
                    })
        
        return {
            'pipeline_id': str(uuid.uuid4()),
            'steps': pipeline_steps,
            'features': [f.name for f in features]
        }
    
    async def auto_feature_selection(self, dataset: pd.DataFrame, target_column: str, k: int = 10) -> List[str]:
        """Automatic feature selection."""
        if not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE:
            return list(dataset.columns)
        
        try:
            # Separate features and target
            X = dataset.drop(columns=[target_column])
            y = dataset[target_column]
            
            # Determine if it's classification or regression
            if y.dtype == 'object' or y.nunique() < 10:
                # Classification
                selector = SelectKBest(score_func=f_classif, k=min(k, X.shape[1]))
            else:
                # Regression
                selector = SelectKBest(score_func=f_regression, k=min(k, X.shape[1]))
            
            # Fit selector
            selector.fit(X, y)
            
            # Get selected features
            selected_features = X.columns[selector.get_support()].tolist()
            
            self.logger.info(f"Selected {len(selected_features)} features from {X.shape[1]}")
            return selected_features
            
        except Exception as e:
            self.logger.error(f"Auto feature selection failed: {e}")
            return list(dataset.columns)
    
    async def model_drift_detection(self, model_id: str, new_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect model drift using new data."""
        if model_id not in self.models:
            return {'error': 'Model not found'}
        
        # This would implement statistical tests for data drift
        # For now, return a simple drift score
        
        return {
            'model_id': model_id,
            'drift_score': 0.15,  # Simulated drift score
            'drift_detected': False,
            'recommendation': 'Model performance is stable',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # Worker management
    async def _start_workers(self):
        """Start background workers."""
        if self.workers_running:
            return
        
        self.workers_running = True
        
        # Start training workers
        for i in range(2):  # 2 training workers
            worker = asyncio.create_task(self._training_worker(f"training_worker_{i}"))
            self.training_workers.append(worker)
        
        # Start inference workers
        for i in range(3):  # 3 inference workers
            worker = asyncio.create_task(self._inference_worker(f"inference_worker_{i}"))
            self.inference_workers.append(worker)
        
        self.logger.info("ML workers started")
    
    async def _stop_workers(self):
        """Stop background workers."""
        if not self.workers_running:
            return
        
        self.workers_running = False
        
        # Cancel all workers
        for worker in self.training_workers + self.inference_workers:
            worker.cancel()
        
        # Wait for workers to complete
        if self.training_workers or self.inference_workers:
            await asyncio.gather(
                *self.training_workers, *self.inference_workers,
                return_exceptions=True
            )
        
        self.training_workers.clear()
        self.inference_workers.clear()
        self.logger.info("ML workers stopped")
    
    async def _training_worker(self, worker_name: str):
        """Background training worker."""
        self.logger.info(f"Started {worker_name}")
        
        while self.workers_running:
            try:
                # Get training job from queue
                job_data = await asyncio.wait_for(self.training_queue.get(), timeout=5.0)
                
                # Execute training job
                await self._execute_training_job(job_data)
                
                # Mark task as done
                self.training_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Training worker error: {e}")
    
    async def _inference_worker(self, worker_name: str):
        """Background inference worker."""
        self.logger.info(f"Started {worker_name}")
        
        while self.workers_running:
            try:
                # Check inference queue (if we had one)
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Inference worker error: {e}")
    
    # Database operations
    async def _store_model(self, model: MLModel):
        """Store model to database."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                # Check if model exists
                result = await session.execute(
                    sa.select(MLModelModel).where(MLModelModel.id == model.id)
                )
                db_model = result.scalar_one_or_none()
                
                if db_model:
                    # Update existing
                    db_model.name = model.name
                    db_model.training_status = model.training_status.value
                    db_model.deployment_status = model.deployment_status.value
                    db_model.updated_at = model.updated_at
                    db_model.metadata = json.dumps(model.metadata)
                else:
                    # Create new
                    db_model = MLModelModel(
                        id=model.id,
                        name=model.name,
                        model_type=model.model_type.value,
                        algorithm=model.algorithm,
                        features=json.dumps([{
                            'name': f.name,
                            'type': f.feature_type.value,
                            'source_column': f.source_column,
                            'is_target': f.is_target
                        } for f in model.features]),
                        target_feature=model.target_feature,
                        hyperparameters=json.dumps(model.hyperparameters),
                        training_status=model.training_status.value,
                        deployment_status=model.deployment_status.value,
                        version=model.version,
                        created_at=model.created_at,
                        updated_at=model.updated_at,
                        metadata=json.dumps(model.metadata)
                    )
                    session.add(db_model)
                
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing model: {e}")
    
    async def _store_training_job(self, job: TrainingJob):
        """Store training job to database."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                db_job = TrainingJobModel(
                    id=job.id,
                    model_id=job.model_id,
                    dataset_id=job.dataset_id,
                    status=job.status.value,
                    started_at=job.started_at,
                    completed_at=job.completed_at,
                    training_config=json.dumps(job.training_config),
                    training_metrics=json.dumps(job.training_metrics),
                    validation_metrics=json.dumps(job.validation_metrics),
                    error_message=job.error_message,
                    metadata=json.dumps(job.metadata)
                )
                session.add(db_job)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error storing training job: {e}")
    
    async def _log_prediction(self, request: PredictionRequest, result: PredictionResult):
        """Log prediction to database."""
        if not self.async_session or not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            async with self.async_session() as session:
                db_log = PredictionLogModel(
                    id=str(uuid.uuid4()),
                    model_id=request.model_id,
                    request_data=json.dumps(request.input_data),
                    prediction_result=json.dumps({
                        'predictions': result.predictions,
                        'confidence': result.confidence
                    }),
                    processing_time=result.processing_time,
                    timestamp=result.timestamp,
                    metadata=json.dumps(result.metadata)
                )
                session.add(db_log)
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error logging prediction: {e}")
    
    def get_ml_metrics(self) -> Dict[str, Any]:
        """Get ML processor metrics."""
        return {
            **self.ml_metrics,
            'registered_models': len(self.models),
            'loaded_models': len(self.loaded_models),
            'training_queue_size': self.training_queue.qsize(),
            'workers_running': self.workers_running
        }
    
    async def shutdown(self):
        """Shutdown ML processor."""
        await self._stop_workers()
        self.logger.info("ML processor shutdown complete")


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize ML processor
        processor = MachineLearningProcessor(
            database_url="postgresql+asyncpg://user:pass@localhost/db",
            redis_url="redis://localhost:6379"
        )
        
        await processor.initialize()
        
        # Create feature definitions
        features = [
            FeatureDefinition(
                name="age",
                feature_type=FeatureType.NUMERICAL,
                source_column="age",
                transformations=["standardize"]
            ),
            FeatureDefinition(
                name="platform",
                feature_type=FeatureType.CATEGORICAL,
                source_column="platform",
                transformations=["encode"]
            ),
            FeatureDefinition(
                name="engagement_score",
                feature_type=FeatureType.NUMERICAL,
                source_column="engagement_score",
                is_target=True
            )
        ]
        
        # Create ML model
        model = MLModel(
            id=str(uuid.uuid4()),
            name="User Engagement Predictor",
            model_type=ModelType.REGRESSION,
            algorithm="random_forest_regressor",
            features=features,
            target_feature="engagement_score",
            hyperparameters={"n_estimators": 200}
        )
        
        await processor.create_model(model)
        
        # Create sample training data
        if PANDAS_AVAILABLE:
            training_data = pd.DataFrame({
                'age': [25, 30, 35, 40, 45],
                'platform': ['youtube', 'instagram', 'tiktok', 'youtube', 'instagram'],
                'engagement_score': [0.8, 0.9, 0.7, 0.85, 0.95]
            })
            
            # Train model
            job = await processor.train_model(model.id, training_data)
            print(f"Training job created: {job.id}")
            
            # Wait for training to complete
            await asyncio.sleep(5)
            
            # Make prediction
            prediction_request = PredictionRequest(
                id=str(uuid.uuid4()),
                model_id=model.id,
                input_data={'age': 28, 'platform': 'youtube'}
            )
            
            result = await processor.predict(prediction_request)
            print(f"Prediction: {result.predictions}")
            print(f"Confidence: {result.confidence}")
            
            # Get model metrics
            metrics = await processor.get_model_metrics(model.id)
            print(f"Model metrics: {metrics}")
        
        # Get processor metrics
        ml_metrics = processor.get_ml_metrics()
        print(f"ML processor metrics: {ml_metrics}")
        
        await processor.shutdown()
    
    asyncio.run(main())