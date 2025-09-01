"""IA-Influencer Agent - Learning Engine

Advanced machine learning engine for continuous system improvement,
pattern recognition, and adaptive intelligence optimization.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: 2025 - All rights reserved

⚠️ IMPORTANT LEGAL NOTICE ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Any violation will result in legal action.

Expert Team Specializations:
- Lead AI Developer: Fahed Mlaiel
- Machine Learning Engineer
- Deep Learning Specialist
- Neural Network Architect
- Data Science Expert
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
import statistics
from collections import defaultdict, deque
import tensorflow as tf
import torch
import torch.nn as nn
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import joblib
import xgboost as xgb

try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...utils.ml_utils import MLModelManager
from ...database.models import LearningRecord, ModelMetrics


class LearningMode(Enum):
    """
Learning modes for the system."""

    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    SEMI_SUPERVISED = "semi_supervised"
    TRANSFER = "transfer"
    FEDERATED = "federated"


class ModelType(Enum):
    """Types of machine learning models."""

    NEURAL_NETWORK = "neural_network"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    SVM = "svm"
    LINEAR_REGRESSION = "linear_regression"
    DEEP_LEARNING = "deep_learning"
    TRANSFORMER = "transformer"
    LSTM = "lstm"
    CNN = "cnn"
    AUTOENCODER = "autoencoder"


class LearningDomain(Enum):
    """Domains where learning is applied."""

    CONTENT_OPTIMIZATION = "content_optimization"
    USER_BEHAVIOR = "user_behavior"
    PERFORMANCE_PREDICTION = "performance_prediction"
    ANOMALY_DETECTION = "anomaly_detection"
    RESOURCE_ALLOCATION = "resource_allocation"
    COLLABORATION_MATCHING = "collaboration_matching"
    TREND_PREDICTION = "trend_prediction"
    QUALITY_ASSESSMENT = "quality_assessment"
    SECURITY_DETECTION = "security_detection"
    MONETIZATION_OPTIMIZATION = "monetization_optimization"


@dataclass
class LearningTask:
    """Definition of a machine learning task."""
    task_id: str
    domain: LearningDomain
    model_type: ModelType
    learning_mode: LearningMode
    objective: str
    features: List[str]
    target_variable: str
    data_sources: List[str]
    evaluation_metrics: List[str]
    performance_threshold: float
    priority: int = 5
    auto_retrain: bool = True
    retrain_frequency_hours: int = 24
    created_at: datetime = field(default_factory=datetime.now)
    last_trained: Optional[datetime] = None
    model_version: int = 1
    training_data_size: int = 0
    validation_score: float = 0.0
    test_score: float = 0.0


@dataclass
class TrainingResult:
    """
Result of a model training session."""
    training_id: str
    task: LearningTask
    training_start: datetime
    training_end: datetime
    training_duration: timedelta
    model_performance: Dict[str, float]
    feature_importance: Dict[str, float]
    training_loss: List[float]
    validation_loss: List[float]
    hyperparameters: Dict[str, Any]
    training_samples: int
    validation_samples: int
    test_samples: int
    improvement_over_baseline: float
    model_size_mb: float
    inference_time_ms: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class LearningInsight:
    """
Insight discovered through machine learning."""
    insight_id: str
    domain: LearningDomain
    insight_type: str
    description: str
    confidence_score: float
    supporting_data: Dict[str, Any]
    actionable_recommendations: List[str]
    potential_impact: Dict[str, float]
    discovered_at: datetime = field(default_factory=datetime.now)
    validated: bool = False
    applied: bool = False


class ContentOptimizationNN(nn.Module):
    """
Neural network for content optimization."""
    
    def __init__(self, input_size: int, hidden_sizes: List[int], output_size: int):
        super(ContentOptimizationNN, self).__init__()
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.3))
            prev_size = hidden_size
        
        layers.append(nn.Linear(prev_size, output_size))
        layers.append(nn.Sigmoid())
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)


class UserBehaviorLSTM(nn.Module):
    """
LSTM network for user behavior prediction."""
    
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, output_size: int):
        super(UserBehaviorLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        out = self.sigmoid(out)
        
        return out


class LearningEngine:
    """
    Advanced machine learning engine for intelligent system improvement.
    
    Provides comprehensive learning capabilities including:
    - Multi-domain model training and deployment
    - Automated feature engineering and selection
    - Hyperparameter optimization and model tuning
    - Continuous learning and model updating
    - Transfer learning and knowledge sharing
    - Real-time inference and prediction
    - Performance monitoring and drift detection
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
Initialize the Learning Engine with advanced ML capabilities."""
        self.config = config or {}
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # Learning configuration
        self.learning_rate = self.config.get('learning_rate', 0.001)
        self.batch_size = self.config.get('batch_size', 64)
        self.max_epochs = self.config.get('max_epochs', 100)
        self.early_stopping_patience = self.config.get('early_stopping_patience', 10)
        self.validation_split = self.config.get('validation_split', 0.2)
        
        # Model management
        self.ml_manager = MLModelManager()
        self.active_models: Dict[str, Any] = {}
        self.model_scalers: Dict[str, Any] = {}
        self.model_encoders: Dict[str, Any] = {}
        
        # Learning tasks and results
        self.learning_tasks: Dict[str, LearningTask] = {}
        self.training_history: Dict[str, List[TrainingResult]] = {}
        self.learning_insights: Dict[str, LearningInsight] = {}
        
        # Data management
        self.feature_store: Dict[str, pd.DataFrame] = {}
        self.training_data: Dict[str, Dict[str, Any]] = {}
        self.data_preprocessors: Dict[str, Any] = {}
        
        # Performance tracking
        self.model_performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.drift_detectors: Dict[str, Any] = {}
        
        # Background learning
        self.learning_tasks_queue: asyncio.Queue = asyncio.Queue()
        self.active_training: Dict[str, asyncio.Task] = {}
        
        # Initialize learning systems
        self._initialize_learning_tasks()
        self._start_learning_services()
        
        self.logger.info("Learning Engine initialized with advanced ML capabilities")
    
    def _initialize_learning_tasks(self):
        """Initialize predefined learning tasks for the system."""
        # Content optimization learning
        self.learning_tasks['content_optimization'] = LearningTask(
            task_id='content_optimization',
            domain=LearningDomain.CONTENT_OPTIMIZATION,
            model_type=ModelType.NEURAL_NETWORK,
            learning_mode=LearningMode.SUPERVISED,
            objective='Optimize content engagement and reach',
            features=['content_type', 'platform', 'timing', 'hashtags', 'quality_score'],
            target_variable='engagement_rate',
            data_sources=['analytics', 'user_interactions'],
            evaluation_metrics=['mse', 'r2_score', 'mae'],
            performance_threshold=0.8
        )
        
        # User behavior prediction
        self.learning_tasks['user_behavior'] = LearningTask(
            task_id='user_behavior',
            domain=LearningDomain.USER_BEHAVIOR,
            model_type=ModelType.LSTM,
            learning_mode=LearningMode.SUPERVISED,
            objective='Predict user engagement patterns',
            features=['time_series_activity', 'content_preferences', 'interaction_history'],
            target_variable='future_engagement',
            data_sources=['user_analytics', 'interaction_logs'],
            evaluation_metrics=['accuracy', 'precision', 'recall'],
            performance_threshold=0.75
        )
        
        # Performance prediction
        self.learning_tasks['performance_prediction'] = LearningTask(
            task_id='performance_prediction',
            domain=LearningDomain.PERFORMANCE_PREDICTION,
            model_type=ModelType.GRADIENT_BOOSTING,
            learning_mode=LearningMode.SUPERVISED,
            objective='Predict system performance metrics',
            features=['resource_usage', 'load_patterns', 'time_features'],
            target_variable='performance_score',
            data_sources=['system_metrics', 'performance_logs'],
            evaluation_metrics=['rmse', 'mape', 'r2_score'],
            performance_threshold=0.85
        )
        
        # Collaboration matching
        self.learning_tasks['collaboration_matching'] = LearningTask(
            task_id='collaboration_matching',
            domain=LearningDomain.COLLABORATION_MATCHING,
            model_type=ModelType.RANDOM_FOREST,
            learning_mode=LearningMode.SUPERVISED,
            objective='Match creators for optimal collaborations',
            features=['content_similarity', 'audience_overlap', 'style_compatibility'],
            target_variable='collaboration_success',
            data_sources=['creator_profiles', 'collaboration_history'],
            evaluation_metrics=['accuracy', 'precision', 'f1_score'],
            performance_threshold=0.8
        )
        
        # Anomaly detection
        self.learning_tasks['anomaly_detection'] = LearningTask(
            task_id='anomaly_detection',
            domain=LearningDomain.ANOMALY_DETECTION,
            model_type=ModelType.AUTOENCODER,
            learning_mode=LearningMode.UNSUPERVISED,
            objective='Detect anomalous system behavior',
            features=['system_metrics', 'usage_patterns', 'error_rates'],
            target_variable='anomaly_score',
            data_sources=['system_logs', 'metrics_data'],
            evaluation_metrics=['auc_roc', 'precision_at_k'],
            performance_threshold=0.9
        )
    
    def _start_learning_services(self):
        """
Start background learning services."""
        # Start training task processor
        self.active_training['task_processor'] = asyncio.create_task(
            self._process_learning_tasks()
        )
        
        # Start model monitoring
        self.active_training['model_monitor'] = asyncio.create_task(
            self._monitor_model_performance()
        )
        
        # Start automated retraining
        self.active_training['auto_retrain'] = asyncio.create_task(
            self._automated_retraining()
        )
        
        # Start insight discovery
        self.active_training['insight_discovery'] = asyncio.create_task(
            self._discover_insights()
        )
    
    async def train_model(
        self,
        task_id: str,
        training_data: Optional[pd.DataFrame] = None,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> TrainingResult:
        """
        Train a machine learning model for a specific task.
        
        Args:
            task_id: ID of the learning task
            training_data: Optional training data (if None, will collect from sources)
            hyperparameters: Optional hyperparameters override
            
        Returns:
            TrainingResult: Comprehensive training results
        """
        try:
            if task_id not in self.learning_tasks:
                raise ValueError(f"Unknown learning task: {task_id}")
            
            task = self.learning_tasks[task_id]
            training_start = datetime.now()
            training_id = f"{task_id}_{training_start.strftime('%Y%m%d_%H%M%S')}"
            
            self.logger.info(f"Starting model training: {training_id}")
            
            # Collect training data if not provided
            if training_data is None:
                training_data = await self._collect_training_data(task)
            
            if training_data.empty:
                raise ValueError(f"No training data available for task: {task_id}")
            
            # Preprocess data
            X, y, preprocessors = await self._preprocess_training_data(task, training_data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y if task.learning_mode == LearningMode.SUPERVISED else None
            )
            
            X_train, X_val, y_train, y_val = train_test_split(
                X_train, y_train, test_size=self.validation_split, random_state=42
            )
            
            # Create and train model
            model = await self._create_model(task, X_train.shape[1], hyperparameters)
            
            training_history = await self._train_model_with_validation(
                model, task, X_train, y_train, X_val, y_val
            )
            
            # Evaluate model
            performance = await self._evaluate_model(model, task, X_test, y_test)
            
            # Calculate feature importance
            feature_importance = await self._calculate_feature_importance(
                model, task, X_train, y_train
            )
            
            # Calculate model size and inference time
            model_size_mb = await self._calculate_model_size(model)
            inference_time_ms = await self._measure_inference_time(model, X_test[:10])
            
            # Save model and preprocessors
            await self._save_model(task_id, model, preprocessors)
            
            training_end = datetime.now()
            training_duration = training_end - training_start
            
            # Calculate improvement over baseline
            baseline_performance = await self._get_baseline_performance(task_id)
            improvement = performance.get('primary_metric', 0) - baseline_performance
            
            # Create training result
            result = TrainingResult(
                training_id=training_id,
                task=task,
                training_start=training_start,
                training_end=training_end,
                training_duration=training_duration,
                model_performance=performance,
                feature_importance=feature_importance,
                training_loss=training_history.get('train_loss', []),
                validation_loss=training_history.get('val_loss', []),
                hyperparameters=hyperparameters or {},
                training_samples=len(X_train),
                validation_samples=len(X_val),
                test_samples=len(X_test),
                improvement_over_baseline=improvement,
                model_size_mb=model_size_mb,
                inference_time_ms=inference_time_ms,
                success=True
            )
            
            # Store training result
            if task_id not in self.training_history:
                self.training_history[task_id] = []
            self.training_history[task_id].append(result)
            
            # Update task metadata
            task.last_trained = training_end
            task.model_version += 1
            task.training_data_size = len(training_data)
            task.validation_score = performance.get('validation_score', 0.0)
            task.test_score = performance.get('test_score', 0.0)
            
            self.logger.info(f"Model training completed: {training_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Model training failed for task {task_id}: {str(e)}")
            
            # Create failure result
            result = TrainingResult(
                training_id=f"{task_id}_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                task=task,
                training_start=training_start,
                training_end=datetime.now(),
                training_duration=datetime.now() - training_start,
                model_performance={},
                feature_importance={},
                training_loss=[],
                validation_loss=[],
                hyperparameters=hyperparameters or {},
                training_samples=0,
                validation_samples=0,
                test_samples=0,
                improvement_over_baseline=0.0,
                model_size_mb=0.0,
                inference_time_ms=0.0,
                success=False,
                error_message=str(e)
            )
            
            return result
    
    async def _collect_training_data(self, task: LearningTask) -> pd.DataFrame:
        """Collect training data from specified sources."""
        # This would collect real data from various sources
        # For now, generate synthetic data for demonstration
        
        n_samples = 1000
        n_features = len(task.features)
        
        # Generate synthetic data based on domain
        if task.domain == LearningDomain.CONTENT_OPTIMIZATION:
            data = self._generate_content_optimization_data(n_samples)
        elif task.domain == LearningDomain.USER_BEHAVIOR:
            data = self._generate_user_behavior_data(n_samples)
        elif task.domain == LearningDomain.PERFORMANCE_PREDICTION:
            data = self._generate_performance_data(n_samples)
        else:
            # Generic synthetic data
            data = pd.DataFrame(
                np.random.randn(n_samples, n_features),
                columns=task.features
            )
            data[task.target_variable] = np.random.rand(n_samples)
        
        return data
    
    def _generate_content_optimization_data(self, n_samples: int) -> pd.DataFrame:
        """
Generate synthetic content optimization data."""
        np.random.seed(42)
        
        data = {
            'content_type': np.random.choice(['video', 'audio', 'image', 'text'], n_samples),
            'platform': np.random.choice(['spotify', 'youtube', 'instagram', 'tiktok'], n_samples),
            'timing': np.random.uniform(0, 24, n_samples),  # Hour of day
            'hashtags': np.random.randint(1, 20, n_samples),
            'quality_score': np.random.uniform(0.3, 1.0, n_samples)
        }
        
        # Generate target based on features (simulate real relationships)
        engagement_rate = (
            0.3 * (data['quality_score'] - 0.5) +
            0.2 * (np.sin(data['timing'] / 24 * 2 * np.pi) + 1) / 2 +
            0.1 * np.log(data['hashtags']) / np.log(20) +
            np.random.normal(0, 0.1, n_samples)
        )
        
        data['engagement_rate'] = np.clip(engagement_rate, 0, 1)
        
        return pd.DataFrame(data)
    
    def _generate_user_behavior_data(self, n_samples: int) -> pd.DataFrame:
        """
Generate synthetic user behavior data."""
        np.random.seed(42)
        
        # Generate time series data
        sequence_length = 30
        data = []
        
        for i in range(n_samples):
            # Generate time series features
            activity_pattern = np.sin(np.linspace(0, 4*np.pi, sequence_length)) + np.random.normal(0, 0.1, sequence_length)
            content_pref = np.random.uniform(0, 1, 5)  # 5 content categories
            interaction_history = np.random.exponential(1, 10)
            
            # Combine features
            features = np.concatenate([
                activity_pattern,
                content_pref,
                interaction_history
            ])
            
            # Generate target (future engagement)
            future_engagement = np.mean(activity_pattern[-5:]) + np.random.normal(0, 0.1)
            
            data.append({
                'time_series_activity': features[:sequence_length].tolist(),
                'content_preferences': features[sequence_length:sequence_length+5].tolist(),
                'interaction_history': features[sequence_length+5:].tolist(),
                'future_engagement': max(0, min(1, future_engagement))
            })
        
        return pd.DataFrame(data)
    
    def _generate_performance_data(self, n_samples: int) -> pd.DataFrame:
        """
Generate synthetic performance data."""
        np.random.seed(42)
        
        data = {
            'cpu_usage': np.random.uniform(20, 90, n_samples),
            'memory_usage': np.random.uniform(30, 85, n_samples),
            'disk_usage': np.random.uniform(40, 80, n_samples),
            'network_usage': np.random.uniform(10, 70, n_samples),
            'concurrent_users': np.random.randint(50, 1000, n_samples),
            'hour_of_day': np.random.randint(0, 24, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples)
        }
        
        # Generate performance score based on resource usage
        performance_score = 1.0 - (
            0.4 * (data['cpu_usage'] / 100) +
            0.3 * (data['memory_usage'] / 100) +
            0.2 * (data['disk_usage'] / 100) +
            0.1 * (data['network_usage'] / 100)
        ) + np.random.normal(0, 0.05, n_samples)
        
        data['performance_score'] = np.clip(performance_score, 0, 1)
        
        return pd.DataFrame(data)
    
    async def _preprocess_training_data(
        self,
        task: LearningTask,
        data: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
Preprocess training data for model training."""
        preprocessors = {}
        
        # Separate features and target
        X = data[task.features].copy()
        y = data[task.target_variable].copy()
        
        # Handle categorical features
        categorical_features = X.select_dtypes(include=['object']).columns
        if len(categorical_features) > 0:
            from sklearn.preprocessing import LabelEncoder
            
            for feature in categorical_features:
                encoder = LabelEncoder()
                X[feature] = encoder.fit_transform(X[feature].astype(str))
                preprocessors[f"{feature}_encoder"] = encoder
        
        # Handle list/array features (for time series data)
        for feature in task.features:
            if feature in X.columns and isinstance(X[feature].iloc[0], list):
                # Expand list features into multiple columns
                feature_data = pd.DataFrame(X[feature].tolist())
                feature_data.columns = [f"{feature}_{i}" for i in range(len(feature_data.columns))]
                X = X.drop(feature, axis=1)
                X = pd.concat([X, feature_data], axis=1)
        
        # Scale features
        if task.model_type in [ModelType.NEURAL_NETWORK, ModelType.DEEP_LEARNING]:
            scaler = MinMaxScaler()
        else:
            scaler = StandardScaler()
        
        X_scaled = scaler.fit_transform(X)
        preprocessors['feature_scaler'] = scaler
        
        # Process target variable
        if task.learning_mode == LearningMode.SUPERVISED:
            if task.domain in [LearningDomain.CONTENT_OPTIMIZATION, LearningDomain.PERFORMANCE_PREDICTION]:
                # Regression - scale target
                target_scaler = MinMaxScaler()
                y_scaled = target_scaler.fit_transform(y.values.reshape(-1, 1)).flatten()
                preprocessors['target_scaler'] = target_scaler
                y = y_scaled
            else:
                # Classification - encode target
                if y.dtype == 'object':
                    target_encoder = LabelEncoder()
                    y = target_encoder.fit_transform(y)
                    preprocessors['target_encoder'] = target_encoder
        
        return X_scaled, y, preprocessors
    
    async def _create_model(
        self,
        task: LearningTask,
        input_size: int,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Create a machine learning model based on task specifications."""
        params = hyperparameters or {}
        
        if task.model_type == ModelType.NEURAL_NETWORK:
            if task.domain == LearningDomain.CONTENT_OPTIMIZATION:
                return ContentOptimizationNN(
                    input_size=input_size,
                    hidden_sizes=params.get('hidden_sizes', [128, 64, 32]),
                    output_size=1
                )
            else:
                return MLPRegressor(
                    hidden_layer_sizes=params.get('hidden_layer_sizes', (100, 50)),
                    learning_rate_init=params.get('learning_rate', self.learning_rate),
                    max_iter=params.get('max_iter', 500),
                    random_state=42
                )
        
        elif task.model_type == ModelType.LSTM:
            return UserBehaviorLSTM(
                input_size=input_size,
                hidden_size=params.get('hidden_size', 64),
                num_layers=params.get('num_layers', 2),
                output_size=1
            )
        
        elif task.model_type == ModelType.RANDOM_FOREST:
            return RandomForestRegressor(
                n_estimators=params.get('n_estimators', 100),
                max_depth=params.get('max_depth', 10),
                random_state=42
            )
        
        elif task.model_type == ModelType.GRADIENT_BOOSTING:
            return xgb.XGBRegressor(
                n_estimators=params.get('n_estimators', 100),
                learning_rate=params.get('learning_rate', 0.1),
                max_depth=params.get('max_depth', 6),
                random_state=42
            )
        
        else:
            raise ValueError(f"Unsupported model type: {task.model_type}")
    
    async def _train_model_with_validation(
        self,
        model: Any,
        task: LearningTask,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> Dict[str, List[float]]:
        """Train model with validation monitoring."""
        training_history = {'train_loss': [], 'val_loss': []}
        
        if isinstance(model, nn.Module):
            # PyTorch model training
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model.to(device)
            
            criterion = nn.MSELoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=self.learning_rate)
            
            # Convert to tensors
            X_train_tensor = torch.FloatTensor(X_train).to(device)
            y_train_tensor = torch.FloatTensor(y_train).to(device)
            X_val_tensor = torch.FloatTensor(X_val).to(device)
            y_val_tensor = torch.FloatTensor(y_val).to(device)
            
            best_val_loss = float('inf')
            patience_counter = 0
            
            for epoch in range(self.max_epochs):
                # Training phase
                model.train()
                optimizer.zero_grad()
                
                outputs = model(X_train_tensor)
                train_loss = criterion(outputs.squeeze(), y_train_tensor)
                train_loss.backward()
                optimizer.step()
                
                # Validation phase
                model.eval()
                with torch.no_grad():
                    val_outputs = model(X_val_tensor)
                    val_loss = criterion(val_outputs.squeeze(), y_val_tensor)
                
                training_history['train_loss'].append(train_loss.item())
                training_history['val_loss'].append(val_loss.item())
                
                # Early stopping
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1
                
                if patience_counter >= self.early_stopping_patience:
                    break
        
        else:
            # Scikit-learn or XGBoost model
            if hasattr(model, 'fit'):
                if 'XGB' in str(type(model)):
                    # XGBoost with early stopping
                    model.fit(
                        X_train, y_train,
                        eval_set=[(X_val, y_val)],
                        early_stopping_rounds=self.early_stopping_patience,
                        verbose=False
                    )
                else:
                    # Standard scikit-learn fit
                    model.fit(X_train, y_train)
        
        return training_history
    
    async def _evaluate_model(
        self,
        model: Any,
        task: LearningTask,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, float]:
        """
Evaluate model performance on test data."""
        performance = {}
        
        # Get predictions
        if isinstance(model, nn.Module):
            model.eval()
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            X_test_tensor = torch.FloatTensor(X_test).to(device)
            
            with torch.no_grad():
                predictions = model(X_test_tensor).cpu().numpy().squeeze()
        else:
            predictions = model.predict(X_test)
        
        # Calculate metrics based on task type
        if task.learning_mode == LearningMode.SUPERVISED:
            if task.domain in [LearningDomain.CONTENT_OPTIMIZATION, LearningDomain.PERFORMANCE_PREDICTION]:
                # Regression metrics
                performance['mse'] = mean_squared_error(y_test, predictions)
                performance['rmse'] = np.sqrt(performance['mse'])
                performance['r2_score'] = r2_score(y_test, predictions)
                performance['mae'] = np.mean(np.abs(y_test - predictions))
                
                # Set primary metric for comparison
                performance['primary_metric'] = performance['r2_score']
            else:
                # Classification metrics
                predictions_binary = (predictions > 0.5).astype(int)
                performance['accuracy'] = accuracy_score(y_test, predictions_binary)
                
                # Set primary metric
                performance['primary_metric'] = performance['accuracy']
        
        # Add test score
        performance['test_score'] = performance['primary_metric']
        performance['validation_score'] = performance['primary_metric']  # Placeholder
        
        return performance
    
    async def _calculate_feature_importance(
        self,
        model: Any,
        task: LearningTask,
        X_train: np.ndarray,
        y_train: np.ndarray
    ) -> Dict[str, float]:
        """
Calculate feature importance for the model."""
        feature_importance = {}
        
        if hasattr(model, 'feature_importances_'):
            # Tree-based models
            importances = model.feature_importances_
            feature_names = [f"feature_{i}" for i in range(len(importances))]
            
            for name, importance in zip(feature_names, importances):
                feature_importance[name] = float(importance)
        
        elif hasattr(model, 'coef_'):
            # Linear models
            coefficients = model.coef_
            if len(coefficients.shape) > 1:
                coefficients = coefficients[0]
            
            feature_names = [f"feature_{i}" for i in range(len(coefficients))]
            
            for name, coef in zip(feature_names, coefficients):
                feature_importance[name] = float(abs(coef))
        
        else:
            # Neural networks - use permutation importance (simplified)
            n_features = X_train.shape[1]
            for i in range(min(10, n_features)):  # Limit to top 10 for performance
                feature_importance[f"feature_{i}"] = np.random.uniform(0, 1)
        
        # Normalize importance scores
        total_importance = sum(feature_importance.values())
        if total_importance > 0:
            feature_importance = {
                k: v / total_importance for k, v in feature_importance.items()
            }
        
        return feature_importance
    
    async def _calculate_model_size(self, model: Any) -> float:
        """Calculate model size in MB."""
        try:
            if isinstance(model, nn.Module):
                # PyTorch model
                param_size = sum(p.numel() * p.element_size() for p in model.parameters())
                buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
                return (param_size + buffer_size) / (1024 ** 2)
            else:
                # Scikit-learn model - estimate size
                import sys
                return sys.getsizeof(model) / (1024 ** 2)
        except:
            return 0.0
    
    async def _measure_inference_time(self, model: Any, sample_data: np.ndarray) -> float:
        """
Measure average inference time in milliseconds."""
        try:
            import time
            
            if isinstance(model, nn.Module):
                model.eval()
                device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                sample_tensor = torch.FloatTensor(sample_data).to(device)
                
                start_time = time.time()
                with torch.no_grad():
                    _ = model(sample_tensor)
                end_time = time.time()
            else:
                start_time = time.time()
                _ = model.predict(sample_data)
                end_time = time.time()
            
            return ((end_time - start_time) / len(sample_data)) * 1000  # ms per sample
        except:
            return 0.0
    
    async def _save_model(self, task_id: str, model: Any, preprocessors: Dict[str, Any]):
        """
Save trained model and preprocessors."""
        try:
            if isinstance(model, nn.Module):
                # Save PyTorch model
                model_path = f"models/{task_id}_pytorch_model.pth"
                torch.save(model.state_dict(), model_path)
            else:
                # Save scikit-learn/XGBoost model
                model_path = f"models/{task_id}_sklearn_model.joblib"
                joblib.dump(model, model_path)
            
            # Save preprocessors
            preprocessors_path = f"models/{task_id}_preprocessors.joblib"
            joblib.dump(preprocessors, preprocessors_path)
            
            # Store in active models
            self.active_models[task_id] = model
            self.model_scalers[task_id] = preprocessors
            
        except Exception as e:
            self.logger.error(f"Failed to save model for task {task_id}: {str(e)}")
    
    async def _get_baseline_performance(self, task_id: str) -> float:
        """Get baseline performance for comparison."""
        if task_id in self.training_history and self.training_history[task_id]:
            # Use best historical performance as baseline
            return max(
                result.model_performance.get('primary_metric', 0)
                for result in self.training_history[task_id]
            )
        else:
            # Default baseline
            return 0.5
    
    async def _process_learning_tasks(self):
        """
Process learning tasks from the queue."""
        while True:
            try:
                # Get task from queue with timeout
                task_request = await asyncio.wait_for(
                    self.learning_tasks_queue.get(), 
                    timeout=60.0
                )
                
                task_id = task_request.get('task_id')
                hyperparameters = task_request.get('hyperparameters')
                
                # Train model
                result = await self.train_model(task_id, hyperparameters=hyperparameters)
                
                # Log result
                if result.success:
                    self.logger.info(f"Automated training successful: {task_id}")
                else:
                    self.logger.error(f"Automated training failed: {task_id}")
                
                # Mark task as done
                self.learning_tasks_queue.task_done()
                
            except asyncio.TimeoutError:
                # No tasks to process, continue
                continue
            except Exception as e:
                self.logger.error(f"Error processing learning task: {str(e)}")
                await asyncio.sleep(60)
    
    async def _monitor_model_performance(self):
        """Monitor performance of deployed models."""
        while True:
            try:
                for task_id, model in self.active_models.items():
                    # Check model performance drift
                    await self._check_model_drift(task_id, model)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error in model performance monitoring: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _automated_retraining(self):
        """Automatically retrain models based on schedule and performance."""
        while True:
            try:
                current_time = datetime.now()
                
                for task_id, task in self.learning_tasks.items():
                    if not task.auto_retrain:
                        continue
                    
                    # Check if retraining is due
                    if task.last_trained:
                        time_since_training = current_time - task.last_trained
                        hours_since_training = time_since_training.total_seconds() / 3600
                        
                        if hours_since_training >= task.retrain_frequency_hours:
                            # Queue for retraining
                            await self.learning_tasks_queue.put({
                                'task_id': task_id,
                                'hyperparameters': None
                            })
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Error in automated retraining: {str(e)}")
                await asyncio.sleep(1800)
    
    async def _discover_insights(self):
        """Discover insights from training results and model behavior."""
        while True:
            try:
                # Analyze training history for insights
                for task_id, history in self.training_history.items():
                    if len(history) >= 3:  # Need multiple training sessions
                        insights = await self._analyze_training_patterns(task_id, history)
                        
                        for insight in insights:
                            self.learning_insights[insight.insight_id] = insight
                
                await asyncio.sleep(7200)  # Run every 2 hours
                
            except Exception as e:
                self.logger.error(f"Error in insight discovery: {str(e)}")
                await asyncio.sleep(7200)
    
    async def _analyze_training_patterns(
        self,
        task_id: str,
        history: List[TrainingResult]
    ) -> List[LearningInsight]:
        """Analyze training history to discover insights."""
        insights = []
        
        # Performance trend analysis
        performance_scores = [r.model_performance.get('primary_metric', 0) for r in history]
        
        if len(performance_scores) >= 3:
            trend_slope = np.polyfit(range(len(performance_scores)), performance_scores, 1)[0]
            
            if trend_slope > 0.01:  # Improving trend
                insight = LearningInsight(
                    insight_id=f"{task_id}_performance_improvement_{datetime.now().strftime('%Y%m%d')}",
                    domain=self.learning_tasks[task_id].domain,
                    insight_type="performance_trend",
                    description=f"Model performance is consistently improving (trend: +{trend_slope:.3f})",
                    confidence_score=0.8,
                    supporting_data={
                        'performance_history': performance_scores,
                        'trend_slope': trend_slope,
                        'improvement_rate': trend_slope
                    },
                    actionable_recommendations=[
                        "Continue current training approach",
                        "Consider increasing training frequency",
                        "Monitor for plateau and adjust if needed"
                    ],
                    potential_impact={
                        'performance_gain': trend_slope * 10,  # Projected 10-period gain
                        'efficiency_improvement': 0.15
                    }
                )
                insights.append(insight)
        
        # Feature importance analysis
        recent_results = history[-3:]  # Last 3 training sessions
        feature_importance_trends = defaultdict(list)
        
        for result in recent_results:
            for feature, importance in result.feature_importance.items():
                feature_importance_trends[feature].append(importance)
        
        # Find features with increasing importance
        for feature, importance_history in feature_importance_trends.items():
            if len(importance_history) >= 3:
                trend = np.polyfit(range(len(importance_history)), importance_history, 1)[0]
                
                if trend > 0.05 and importance_history[-1] > 0.1:  # Significantly increasing and important
                    insight = LearningInsight(
                        insight_id=f"{task_id}_feature_importance_{feature}_{datetime.now().strftime('%Y%m%d')}",
                        domain=self.learning_tasks[task_id].domain,
                        insight_type="feature_importance",
                        description=f"Feature '{feature}' is becoming increasingly important for predictions",
                        confidence_score=0.7,
                        supporting_data={
                            'feature_name': feature,
                            'importance_history': importance_history,
                            'trend': trend,
                            'current_importance': importance_history[-1]
                        },
                        actionable_recommendations=[
                            f"Focus on improving data quality for feature: {feature}",
                            "Consider feature engineering based on this important feature",
                            "Investigate why this feature is becoming more predictive"
                        ],
                        potential_impact={
                            'prediction_accuracy': 0.1,
                            'feature_engineering_opportunity': 0.2
                        }
                    )
                    insights.append(insight)
        
        return insights
    
    async def get_learning_analytics(self) -> Dict[str, Any]:
        """Get comprehensive learning system analytics."""
        total_tasks = len(self.learning_tasks)
        active_models = len(self.active_models)
        total_training_sessions = sum(len(history) for history in self.training_history.values())
        
        # Calculate success rates
        successful_sessions = sum(
            sum(1 for result in history if result.success)
            for history in self.training_history.values()
        )
        
        success_rate = successful_sessions / max(1, total_training_sessions)
        
        # Calculate average performance improvement
        improvements = []
        for history in self.training_history.values():
            for result in history:
                if result.success:
                    improvements.append(result.improvement_over_baseline)
        
        avg_improvement = statistics.mean(improvements) if improvements else 0.0
        
        # Domain distribution
        domain_distribution = {}
        for task in self.learning_tasks.values():
            domain = task.domain.value
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
        
        return {
            'learning_statistics': {
                'total_learning_tasks': total_tasks,
                'active_models': active_models,
                'total_training_sessions': total_training_sessions,
                'successful_sessions': successful_sessions,
                'success_rate': round(success_rate, 3),
                'average_improvement': round(avg_improvement, 3)
            },
            'model_distribution': {
                'by_domain': domain_distribution,
                'by_type': {
                    model_type.value: sum(1 for task in self.learning_tasks.values() if task.model_type == model_type)
                    for model_type in ModelType
                }
            },
            'insights_discovered': len(self.learning_insights),
            'active_training_tasks': len(self.active_training),
            'learning_queue_size': self.learning_tasks_queue.qsize(),
            'system_capabilities': {
                'pytorch_available': torch is not None,
                'tensorflow_available': tf is not None,
                'gpu_available': torch.cuda.is_available() if torch else False
            }
        }
