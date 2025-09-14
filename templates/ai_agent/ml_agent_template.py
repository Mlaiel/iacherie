"""{{agent_name}} Machine Learning Agent for Ainflue Platform
import asyncio

{{agent_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from pydantic import BaseModel, Field, validator

from ai.base_agent import BaseAIAgent
from ai.models import MLModelManager
from ml.preprocessing import DataPreprocessor
from ml.feature_engineering import FeatureEngineer
from ml.model_registry import ModelRegistry
from core.config import get_settings
from utils.exceptions import MLException
from monitoring.ml_metrics import MLMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class MLTaskType(Enum):
    """ML task types"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    RECOMMENDATION = "recommendation"
    TIME_SERIES = "time_series"


class MLModelState(Enum):
    """ML model states"""
    UNTRAINED = "untrained"
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    ERROR = "error"


class MLModelConfig(BaseModel):
    """ML model configuration"""
    model_type: str = Field(..., description="Type of ML model")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="Model hyperparameters")
    feature_columns: List[str] = Field(default_factory=list, description="Feature columns")
    target_column: Optional[str] = Field(default=None, description="Target column")
    validation_split: float = Field(default=0.2, description="Validation split ratio")
    random_state: Optional[int] = Field(default=42, description="Random state for reproducibility")
    
    @validator('validation_split')
    def validate_split(cls, v) -> None:
        if not 0 < v < 1:
            raise ValueError('Validation split must be between 0 and 1')
        return v


class MLTrainingTask(BaseModel):
    """ML training task"""
    id: str = Field(..., description="Unique task identifier")
    dataset_path: str = Field(..., description="Path to training dataset")
    model_config: MLModelConfig = Field(..., description="Model configuration")
    task_type: MLTaskType = Field(..., description="Type of ML task")
    priority: int = Field(default=1, description="Task priority (1-10)")
    auto_feature_engineering: bool = Field(default=True, description="Enable automatic feature engineering")
    hyperparameter_tuning: bool = Field(default=False, description="Enable hyperparameter tuning")
    cross_validation: bool = Field(default=True, description="Enable cross-validation")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MLInferenceTask(BaseModel):
    """ML inference task"""
    id: str = Field(..., description="Unique task identifier")
    model_id: str = Field(..., description="Model identifier for inference")
    input_data: Dict[str, Any] = Field(..., description="Input data for prediction")
    batch_mode: bool = Field(default=False, description="Batch inference mode")
    explain_predictions: bool = Field(default=False, description="Generate prediction explanations")
    confidence_threshold: Optional[float] = Field(default=None, description="Minimum confidence threshold")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MLResult(BaseModel):
    """ML operation result"""
    task_id: str = Field(..., description="Task identifier")
    success: bool = Field(..., description="Whether the operation succeeded")
    model_id: Optional[str] = Field(default=None, description="Model identifier")
    predictions: Optional[Union[List, np.ndarray]] = Field(default=None, description="Model predictions")
    probabilities: Optional[Union[List, np.ndarray]] = Field(default=None, description="Prediction probabilities")
    confidence_scores: Optional[Union[List, np.ndarray]] = Field(default=None, description="Confidence scores")
    metrics: Optional[Dict[str, float]] = Field(default=None, description="Model performance metrics")
    feature_importance: Optional[Dict[str, float]] = Field(default=None, description="Feature importance scores")
    explanations: Optional[List[Dict[str, Any]]] = Field(default=None, description="Prediction explanations")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
    """Config: class implementation"""
        arbitrary_types_allowed = True


class {{agent_name}}MLAgent(BaseAIAgent):
    """{{agent_description}}
    
    This ML agent provides comprehensive machine learning capabilities including:
    - Model training and validation
    - Automated feature engineering
    - Hyperparameter optimization
    - Model deployment and inference
    - Performance monitoring
    - Model explainability
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.model_registry = ModelRegistry()
        self.data_preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer()
        self.metrics_collector = MLMetricsCollector()
        self.trained_models: Dict[str, BaseEstimator] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        
    async def train_model(self, task: MLTrainingTask) -> MLResult:
        """Train ML model with given configuration"""
        try:
            logger.info(f"Starting ML training task: {task.id}")
            start_time = datetime.utcnow()
            
            # Load and validate dataset
            data = await self._load_dataset(task.dataset_path)
            
            # Preprocess data
            processed_data = await self._preprocess_data(data, task.model_config)
            
            # Feature engineering
            if task.auto_feature_engineering:
                processed_data = await self._engineer_features(processed_data, task.task_type)
            
            # Split data
            X_train, X_val, y_train, y_val = self._split_data(
                processed_data, task.model_config
            )
            
            # Initialize model
            model = await self._initialize_model(task.model_config, task.task_type)
            
            # Hyperparameter tuning
            if task.hyperparameter_tuning:
                model = await self._tune_hyperparameters(model, X_train, y_train, task.task_type)
            
            # Train model
            trained_model = await self._train_model(model, X_train, y_train)
            
            # Validate model
            metrics = await self._validate_model(trained_model, X_val, y_val, task.task_type)
            
            # Cross-validation
            if task.cross_validation:
                cv_metrics = await self._cross_validate(model, processed_data, task.model_config)
                metrics.update({f"cv_{k}": v for k, v in cv_metrics.items()})
            
            # Register model
            model_id = await self._register_model(trained_model, task, metrics)
            
            # Store model
            self.trained_models[model_id] = trained_model
            self.model_metadata[model_id] = {
                "task_type": task.task_type,
                "config": task.model_config.dict(),
                "metrics": metrics,
                "trained_at": datetime.utcnow()
            }
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Collect metrics
            await self.metrics_collector.record_training_metrics(
                model_id=model_id,
                task_type=task.task_type.value,
                metrics=metrics,
                execution_time=execution_time
            )
            
            return MLResult(
                task_id=task.id,
                success=True,
                model_id=model_id,
                metrics=metrics,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"ML training failed for task {task.id}: {str(e)}")
            return MLResult(
                task_id=task.id,
                success=False,
                error_message=str(e)
            )
    
    async def predict(self, task: MLInferenceTask) -> MLResult:
        """Perform ML inference"""
        try:
            logger.info(f"Starting ML inference task: {task.id}")
            start_time = datetime.utcnow()
            
            # Get model
            model = self.trained_models.get(task.model_id)
            if not model:
                model = await self.model_registry.load_model(task.model_id)
                self.trained_models[task.model_id] = model
            
            # Prepare input data
            input_data = await self._prepare_inference_data(task.input_data, task.model_id)
            
            # Make predictions
            predictions = model.predict(input_data)
            
            # Get probabilities if available
            probabilities = None
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(input_data)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence(predictions, probabilities)
            
            # Apply confidence threshold
            if task.confidence_threshold:
                predictions, confidence_scores = self._apply_confidence_threshold(
                    predictions, confidence_scores, task.confidence_threshold
                )
            
            # Generate explanations
            explanations = None
            if task.explain_predictions:
                explanations = await self._explain_predictions(
                    model, input_data, predictions, task.model_id
                )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Collect metrics
            await self.metrics_collector.record_inference_metrics(
                model_id=task.model_id,
                num_predictions=len(predictions),
                execution_time=execution_time
            )
            
            return MLResult(
                task_id=task.id,
                success=True,
                model_id=task.model_id,
                predictions=predictions.tolist() if isinstance(predictions, np.ndarray) else predictions,
                probabilities=probabilities.tolist() if probabilities is not None else None,
                confidence_scores=confidence_scores.tolist() if isinstance(confidence_scores, np.ndarray) else confidence_scores,
                explanations=explanations,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"ML inference failed for task {task.id}: {str(e)}")
            return MLResult(
                task_id=task.id,
                success=False,
                error_message=str(e)
            )
    
    async def _load_dataset(self, dataset_path: str) -> pd.DataFrame:
        """Load dataset from file"""
        path = Path(dataset_path)
        if not path.exists():
            raise MLException(f"Dataset not found: {dataset_path}")
        
        if path.suffix == '.csv':
            return pd.read_csv(dataset_path)
        elif path.suffix in ['.json', '.jsonl']:
            return pd.read_json(dataset_path)
        elif path.suffix in ['.xlsx', '.xls']:
            return pd.read_excel(dataset_path)
        else:
            raise MLException(f"Unsupported file format: {path.suffix}")
    
    async def _preprocess_data(self, data: pd.DataFrame, config: MLModelConfig) -> pd.DataFrame:
        """Preprocess data"""
        return await self.data_preprocessor.process(data, config.dict())
    
    async def _engineer_features(self, data: pd.DataFrame, task_type: MLTaskType) -> pd.DataFrame:
        """Perform automatic feature engineering"""
        return await self.feature_engineer.engineer_features(data, task_type.value)
    
    def _split_data(self, data: pd.DataFrame, config: MLModelConfig) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Split data into training and validation sets"""
        X = data[config.feature_columns]
        y = data[config.target_column] if config.target_column else None
        
        if y is not None:
            return train_test_split(
                X, y, 
                test_size=config.validation_split,
                random_state=config.random_state
            )
        else:
            # For unsupervised learning
            split_idx = int(len(X) * (1 - config.validation_split))
            return X.iloc[:split_idx], X.iloc[split_idx:], None, None
    
    async def _initialize_model(self, config: MLModelConfig, task_type: MLTaskType) -> BaseEstimator:
        """Initialize ML model based on configuration"""
        # This would be implemented based on the specific model types
        # For now, return a placeholder
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        from sklearn.cluster import KMeans
        
        if task_type == MLTaskType.CLASSIFICATION:
            return RandomForestClassifier(**config.hyperparameters)
        elif task_type == MLTaskType.REGRESSION:
            return RandomForestRegressor(**config.hyperparameters)
        elif task_type == MLTaskType.CLUSTERING:
            return KMeans(**config.hyperparameters)
        else:
            raise MLException(f"Unsupported task type: {task_type}")
    
    async def _train_model(self, model: BaseEstimator, X_train: pd.DataFrame, y_train: pd.Series) -> BaseEstimator:
        """Train the model"""
        if y_train is not None:
            model.fit(X_train, y_train)
        else:
            model.fit(X_train)
        return model
    
    async def _validate_model(self, model: BaseEstimator, X_val: pd.DataFrame, y_val: pd.Series, task_type: MLTaskType) -> Dict[str, float]:
        """Validate model performance"""
        metrics = {}
        
        if y_val is not None:
            predictions = model.predict(X_val)
            
            if task_type == MLTaskType.CLASSIFICATION:
                metrics.update({
                    'accuracy': accuracy_score(y_val, predictions),
                    'precision': precision_score(y_val, predictions, average='weighted'),
                    'recall': recall_score(y_val, predictions, average='weighted'),
                    'f1_score': f1_score(y_val, predictions, average='weighted')
                })
            elif task_type == MLTaskType.REGRESSION:
                from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
                metrics.update({
                    'mse': mean_squared_error(y_val, predictions),
                    'mae': mean_absolute_error(y_val, predictions),
                    'r2_score': r2_score(y_val, predictions)
                })
        
        return metrics
    
    async def _cross_validate(self, model: BaseEstimator, data: pd.DataFrame, config: MLModelConfig) -> Dict[str, float]:
        """Perform cross-validation"""
        from sklearn.model_selection import cross_val_score
        
        X = data[config.feature_columns]
        y = data[config.target_column] if config.target_column else None
        
        if y is not None:
            scores = cross_val_score(model, X, y, cv=5)
            return {
                'cv_mean': scores.mean(),
                'cv_std': scores.std()
            }
        
        return {}
    
    async def _register_model(self, model: BaseEstimator, task: MLTrainingTask, metrics: Dict[str, float]) -> str:
        """Register model in model registry"""
        model_metadata = {
            'task_type': task.task_type.value,
            'config': task.model_config.dict(),
            'metrics': metrics,
            'trained_at': datetime.utcnow().isoformat()
        }
        
        return await self.model_registry.register_model(
            model=model,
            metadata=model_metadata
        )
    
    async def _prepare_inference_data(self, input_data: Dict[str, Any], model_id: str) -> pd.DataFrame:
        """Prepare input data for inference"""
        # Convert input data to DataFrame and apply same preprocessing
        df = pd.DataFrame([input_data])
        
        # Apply same preprocessing as training
        model_metadata = self.model_metadata.get(model_id, {})
        config = model_metadata.get('config', {})
        
        if config:
            df = await self.data_preprocessor.process(df, config)
        
        return df
    
    def _calculate_confidence(self, predictions: np.ndarray, probabilities: Optional[np.ndarray]) -> np.ndarray:
        """Calculate confidence scores"""
        if probabilities is not None:
            return np.max(probabilities, axis=1)
        else:
            # For regression or other tasks, use a simple heuristic
            return np.ones(len(predictions))
    
    def _apply_confidence_threshold(self, predictions: np.ndarray, confidence_scores: np.ndarray, threshold: float) -> Tuple[np.ndarray, np.ndarray]:
        """Apply confidence threshold to predictions"""
        mask = confidence_scores >= threshold
        return predictions[mask], confidence_scores[mask]
    
    async def _explain_predictions(self, model: BaseEstimator, input_data: pd.DataFrame, predictions: np.ndarray, model_id: str) -> List[Dict[str, Any]]:
        """Generate prediction explanations"""
        explanations = []
        
        # Simple feature importance explanation
        if hasattr(model, 'feature_importances_'):
            feature_names = input_data.columns.tolist()
            importance = model.feature_importances_
            
            for i, pred in enumerate(predictions):
                explanations.append({
                    'prediction': pred,
                    'feature_importance': dict(zip(feature_names, importance)),
                    'top_features': sorted(
                        zip(feature_names, importance),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5]
                })
        
        return explanations
    
    async def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get model information"""
        if model_id not in self.model_metadata:
            model_info = await self.model_registry.get_model_metadata(model_id)
        else:
            model_info = self.model_metadata[model_id]
        
        return model_info
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all available models"""
        return await self.model_registry.list_models()
    
    async def delete_model(self, model_id: str) -> bool:
        """Delete a model"""
        try:
            await self.model_registry.delete_model(model_id)
            if model_id in self.trained_models:
                del self.trained_models[model_id]
            if model_id in self.model_metadata:
                del self.model_metadata[model_id]
            return True
        except Exception as e:
            logger.error(f"Failed to delete model {model_id}: {str(e)}")
            return False

# File has syntax issues - needs manual review