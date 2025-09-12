"""{{agent_name}} Classification Agent for Ainflue Platform
{{agent_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder, StandardScaler
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from pydantic import BaseModel, Field, validator

from ai.base_agent import BaseAIAgent
from ai.models import ClassificationModelManager
from ml.preprocessing import TextPreprocessor, DataPreprocessor
from ml.feature_engineering import FeatureEngineer
from ml.model_selection import ModelSelector
from core.config import get_settings
from utils.exceptions import ClassificationException
from monitoring.ml_metrics import MLMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class ClassificationType(Enum):
    """Classification task types"""
    BINARY = "binary"
    MULTICLASS = "multiclass"
    MULTILABEL = "multilabel"
    HIERARCHICAL = "hierarchical"


class ModelType(Enum):
    """Classification model types"""
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST = "random_forest"
    SVM = "svm"
    NAIVE_BAYES = "naive_bayes"
    GRADIENT_BOOSTING = "gradient_boosting"
    NEURAL_NETWORK = "neural_network"
    TRANSFORMER = "transformer"
    ENSEMBLE = "ensemble"


class DataType(Enum):
    """Data types for classification"""
    TEXT = "text"
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    MIXED = "mixed"
    IMAGE = "image"
    AUDIO = "audio"


class ClassificationConfig(BaseModel):
    """Classification model configuration"""
    model_type: ModelType = Field(..., description="Type of classification model")
    classification_type: ClassificationType = Field(..., description="Type of classification task")
    data_type: DataType = Field(..., description="Type of input data")
    target_labels: List[str] = Field(..., description="Target class labels")
    feature_columns: Optional[List[str]] = Field(None, description="Feature columns")
    text_columns: Optional[List[str]] = Field(None, description="Text columns for NLP")
    max_features: int = Field(default=10000, description="Maximum number of features")
    test_size: float = Field(default=0.2, description="Test set size")
    validation_size: float = Field(default=0.1, description="Validation set size")
    cross_validation_folds: int = Field(default=5, description="Number of CV folds")
    random_state: int = Field(default=42, description="Random state for reproducibility")
    
    @validator('test_size', 'validation_size')
    def validate_splits(cls, v):
        if not 0 < v < 1:
            raise ValueError('Split sizes must be between 0 and 1')
        return v
    
    @validator('cross_validation_folds')
    def validate_cv_folds(cls, v):
        if v < 2:
            raise ValueError('CV folds must be at least 2')
        return v


class ClassificationTask(BaseModel):
    """Classification task specification"""
    id: str = Field(..., description="Unique task identifier")
    name: str = Field(..., description="Task name")
    config: ClassificationConfig = Field(..., description="Classification configuration")
    training_data: Union[str, Dict[str, Any]] = Field(..., description="Training data path or data")
    validation_data: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Validation data")
    enable_hyperparameter_tuning: bool = Field(default=True, description="Enable hyperparameter tuning")
    enable_feature_selection: bool = Field(default=True, description="Enable automatic feature selection")
    enable_ensemble: bool = Field(default=False, description="Enable ensemble methods")
    performance_threshold: float = Field(default=0.85, description="Minimum performance threshold")
    priority: int = Field(default=1, description="Task priority")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ClassificationPrediction(BaseModel):
    """Classification prediction result"""
    predicted_class: str = Field(..., description="Predicted class label")
    confidence: float = Field(..., description="Prediction confidence")
    probabilities: Dict[str, float] = Field(..., description="Class probabilities")
    features_used: List[str] = Field(default_factory=list, description="Features used for prediction")
    model_version: Optional[str] = Field(None, description="Model version used")


class ClassificationInferenceTask(BaseModel):
    """Classification inference task"""
    id: str = Field(..., description="Unique task identifier")
    model_id: str = Field(..., description="Model identifier")
    input_data: Union[str, Dict[str, Any], List[Dict[str, Any]]] = Field(..., description="Input data for classification")
    return_probabilities: bool = Field(default=True, description="Return class probabilities")
    return_features: bool = Field(default=False, description="Return features used")
    batch_mode: bool = Field(default=False, description="Batch inference mode")
    confidence_threshold: Optional[float] = Field(None, description="Minimum confidence threshold")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ClassificationResult(BaseModel):
    """Classification training/inference result"""
    task_id: str = Field(..., description="Task identifier")
    success: bool = Field(..., description="Whether operation succeeded")
    model_id: Optional[str] = Field(None, description="Model identifier")
    predictions: Optional[List[ClassificationPrediction]] = Field(None, description="Predictions (for inference)")
    
    # Training metrics
    accuracy: Optional[float] = Field(None, description="Model accuracy")
    precision: Optional[Dict[str, float]] = Field(None, description="Precision per class")
    recall: Optional[Dict[str, float]] = Field(None, description="Recall per class")
    f1_score: Optional[Dict[str, float]] = Field(None, description="F1 score per class")
    confusion_matrix: Optional[List[List[int]]] = Field(None, description="Confusion matrix")
    
    # Feature importance
    feature_importance: Optional[Dict[str, float]] = Field(None, description="Feature importance scores")
    selected_features: Optional[List[str]] = Field(None, description="Selected features")
    
    # Model details
    model_type: Optional[str] = Field(None, description="Model type used")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Final hyperparameters")
    cross_validation_scores: Optional[List[float]] = Field(None, description="CV scores")
    
    # Performance
    processing_time: float = Field(..., description="Processing time in seconds")
    training_samples: Optional[int] = Field(None, description="Number of training samples")
    test_samples: Optional[int] = Field(None, description="Number of test samples")
    
    # Error details
    error_message: Optional[str] = Field(None, description="Error message if failed")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class {{agent_name}}Agent(BaseAIAgent):
    """{{agent_description}} with comprehensive classification capabilities"""
    
    def __init__(
        self,
        agent_id: str,
        model_configs: Dict[str, Dict[str, Any]],
        enable_gpu: bool = True,
        cache_size: int = 1000,
        **kwargs
    ):
        super().__init__(agent_id=agent_id, **kwargs)
        self.model_configs = model_configs
        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.cache_size = cache_size
        self.device = torch.device("cuda" if self.enable_gpu else "cpu")
        
        # Initialize components
        self.model_manager = ClassificationModelManager()
        self.text_preprocessor = TextPreprocessor()
        self.data_preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer()
        self.model_selector = ModelSelector()
        self.metrics_collector = MLMetricsCollector()
        
        # Initialize vectorizers and encoders
        self.vectorizers: Dict[str, Any] = {}
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Store trained models
        self.trained_models: Dict[str, Any] = {}
        
        logger.info(f"ClassificationAgent {agent_id} initialized")
    
    async def train_classifier(self, task: ClassificationTask) -> ClassificationResult:
        """Train a classification model"""
        start_time = datetime.utcnow()
        
        try:
            # Load and preprocess data
            X_train, X_test, y_train, y_test = await self._prepare_training_data(task)
            
            # Feature engineering
            if task.enable_feature_selection:
                X_train, X_test, selected_features = await self._perform_feature_selection(
                    X_train, X_test, y_train, task
                )
            else:
                selected_features = None
            
            # Model selection and training
            best_model, best_params, cv_scores = await self._train_and_select_model(
                X_train, y_train, task
            )
            
            # Evaluate model
            evaluation_results = await self._evaluate_model(
                best_model, X_test, y_test, task
            )
            
            # Store model
            model_id = f"{task.id}_{task.config.model_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            await self._store_model(model_id, best_model, task)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create result
            result = ClassificationResult(
                task_id=task.id,
                success=True,
                model_id=model_id,
                accuracy=evaluation_results['accuracy'],
                precision=evaluation_results['precision'],
                recall=evaluation_results['recall'],
                f1_score=evaluation_results['f1_score'],
                confusion_matrix=evaluation_results['confusion_matrix'],
                feature_importance=evaluation_results.get('feature_importance'),
                selected_features=selected_features,
                model_type=task.config.model_type.value,
                hyperparameters=best_params,
                cross_validation_scores=cv_scores,
                processing_time=processing_time,
                training_samples=len(X_train),
                test_samples=len(X_test)
            )
            
            # Record metrics
            await self.metrics_collector.record_training_completion(
                task_id=task.id,
                model_type=task.config.model_type.value,
                accuracy=evaluation_results['accuracy'],
                processing_time=processing_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Classification training failed for task {task.id}: {e}")
            
            # Record error metrics
            await self.metrics_collector.record_training_completion(
                task_id=task.id,
                model_type=task.config.model_type.value,
                accuracy=0.0,
                processing_time=processing_time,
                success=False
            )
            
            return ClassificationResult(
                task_id=task.id,
                success=False,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def predict(self, task: ClassificationInferenceTask) -> ClassificationResult:
        """Perform classification inference"""
        start_time = datetime.utcnow()
        
        try:
            # Load model
            model = await self._load_model(task.model_id)
            if not model:
                raise ClassificationException(f"Model {task.model_id} not found")
            
            # Prepare input data
            X = await self._prepare_inference_data(task.input_data, task.model_id)
            
            # Make predictions
            predictions = await self._make_predictions(model, X, task)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create result
            result = ClassificationResult(
                task_id=task.id,
                success=True,
                model_id=task.model_id,
                predictions=predictions,
                processing_time=processing_time
            )
            
            # Record metrics
            await self.metrics_collector.record_inference_completion(
                task_id=task.id,
                model_id=task.model_id,
                num_predictions=len(predictions),
                processing_time=processing_time,
                success=True
            )
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Classification inference failed for task {task.id}: {e}")
            
            return ClassificationResult(
                task_id=task.id,
                success=False,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _prepare_training_data(self, task: ClassificationTask) -> Tuple[Any, Any, Any, Any]:
        """Prepare training data for classification"""
        
        # Load data
        if isinstance(task.training_data, str):
            # Load from file
            if task.training_data.endswith('.csv'):
                data = pd.read_csv(task.training_data)
            elif task.training_data.endswith('.json'):
                data = pd.read_json(task.training_data)
            else:
                raise ClassificationException(f"Unsupported file format: {task.training_data}")
        else:
            # Use provided data
            data = pd.DataFrame(task.training_data)
        
        # Extract features and labels
        if task.config.data_type == DataType.TEXT:
            X = await self._prepare_text_features(data, task)
        elif task.config.data_type == DataType.NUMERICAL:
            X = await self._prepare_numerical_features(data, task)
        elif task.config.data_type == DataType.CATEGORICAL:
            X = await self._prepare_categorical_features(data, task)
        elif task.config.data_type == DataType.MIXED:
            X = await self._prepare_mixed_features(data, task)
        else:
            raise ClassificationException(f"Unsupported data type: {task.config.data_type}")
        
        # Prepare labels
        y = self._prepare_labels(data, task)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=task.config.test_size,
            random_state=task.config.random_state,
            stratify=y if task.config.classification_type == ClassificationType.BINARY or task.config.classification_type == ClassificationType.MULTICLASS else None
        )
        
        return X_train, X_test, y_train, y_test
    
    async def _prepare_text_features(self, data: pd.DataFrame, task: ClassificationTask) -> np.ndarray:
        """Prepare text features using TF-IDF or other methods"""
        
        # Combine text columns
        text_columns = task.config.text_columns or [col for col in data.columns if data[col].dtype == 'object']
        text_data = data[text_columns].fillna('').apply(lambda x: ' '.join(x.astype(str)), axis=1)
        
        # Preprocess text
        processed_text = await self.text_preprocessor.preprocess_batch(text_data.tolist())
        
        # Vectorize text
        vectorizer_id = f"{task.id}_tfidf"
        if vectorizer_id not in self.vectorizers:
            self.vectorizers[vectorizer_id] = TfidfVectorizer(
                max_features=task.config.max_features,
                stop_words='english',
                ngram_range=(1, 2)
            )
            X = self.vectorizers[vectorizer_id].fit_transform(processed_text)
        else:
            X = self.vectorizers[vectorizer_id].transform(processed_text)
        
        return X.toarray()
    
    async def _prepare_numerical_features(self, data: pd.DataFrame, task: ClassificationTask) -> np.ndarray:
        """Prepare numerical features with scaling"""
        
        feature_columns = task.config.feature_columns or data.select_dtypes(include=[np.number]).columns.tolist()
        X = data[feature_columns].fillna(data[feature_columns].mean())
        
        # Scale features
        scaler_id = f"{task.id}_scaler"
        if scaler_id not in self.scalers:
            self.scalers[scaler_id] = StandardScaler()
            X_scaled = self.scalers[scaler_id].fit_transform(X)
        else:
            X_scaled = self.scalers[scaler_id].transform(X)
        
        return X_scaled
    
    async def _prepare_categorical_features(self, data: pd.DataFrame, task: ClassificationTask) -> np.ndarray:
        """Prepare categorical features with encoding"""
        
        feature_columns = task.config.feature_columns or data.select_dtypes(include=['object']).columns.tolist()
        X = data[feature_columns].fillna('unknown')
        
        # One-hot encode categorical features
        X_encoded = pd.get_dummies(X, drop_first=True)
        
        return X_encoded.values
    
    async def _prepare_mixed_features(self, data: pd.DataFrame, task: ClassificationTask) -> np.ndarray:
        """Prepare mixed features (numerical + categorical + text)"""
        
        features = []
        
        # Numerical features
        num_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            num_features = await self._prepare_numerical_features(data[num_cols], task)
            features.append(num_features)
        
        # Categorical features
        cat_cols = data.select_dtypes(include=['object']).columns.tolist()
        if task.config.text_columns:
            cat_cols = [col for col in cat_cols if col not in task.config.text_columns]
        
        if cat_cols:
            cat_features = await self._prepare_categorical_features(data[cat_cols], task)
            features.append(cat_features)
        
        # Text features
        if task.config.text_columns:
            text_features = await self._prepare_text_features(data, task)
            features.append(text_features)
        
        # Combine all features
        if features:
            return np.hstack(features)
        else:
            raise ClassificationException("No valid features found in data")
    
    def _prepare_labels(self, data: pd.DataFrame, task: ClassificationTask) -> np.ndarray:
        """Prepare target labels"""
        
        # Assuming the last column or a column named 'target' contains labels
        if 'target' in data.columns:
            y = data['target']
        elif 'label' in data.columns:
            y = data['label']
        else:
            y = data.iloc[:, -1]  # Last column
        
        # Encode labels
        encoder_id = f"{task.id}_label_encoder"
        if encoder_id not in self.label_encoders:
            self.label_encoders[encoder_id] = LabelEncoder()
            y_encoded = self.label_encoders[encoder_id].fit_transform(y)
        else:
            y_encoded = self.label_encoders[encoder_id].transform(y)
        
        return y_encoded
    
    async def _perform_feature_selection(
        self, 
        X_train: np.ndarray, 
        X_test: np.ndarray, 
        y_train: np.ndarray, 
        task: ClassificationTask
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Perform automatic feature selection"""
        
        selected_features, X_train_selected, X_test_selected = await self.feature_engineer.select_features(
            X_train, X_test, y_train,
            method='mutual_info',
            k_best=min(1000, X_train.shape[1] // 2)
        )
        
        return X_train_selected, X_test_selected, selected_features
    
    async def _train_and_select_model(
        self, 
        X_train: np.ndarray, 
        y_train: np.ndarray, 
        task: ClassificationTask
    ) -> Tuple[Any, Dict[str, Any], List[float]]:
        """Train and select the best model"""
        
        if task.config.model_type == ModelType.ENSEMBLE or task.enable_ensemble:
            # Train multiple models and create ensemble
            return await self._train_ensemble(X_train, y_train, task)
        else:
            # Train single model
            return await self._train_single_model(X_train, y_train, task)
    
    async def _train_single_model(
        self, 
        X_train: np.ndarray, 
        y_train: np.ndarray, 
        task: ClassificationTask
    ) -> Tuple[Any, Dict[str, Any], List[float]]:
        """Train a single classification model"""
        
        # Select model based on configuration
        if task.config.model_type == ModelType.LOGISTIC_REGRESSION:
            model = LogisticRegression(random_state=task.config.random_state, max_iter=1000)
            param_grid = {
                'C': [0.1, 1.0, 10.0],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear']
            }
        elif task.config.model_type == ModelType.RANDOM_FOREST:
            model = RandomForestClassifier(random_state=task.config.random_state)
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5, 10]
            }
        elif task.config.model_type == ModelType.SVM:
            model = SVC(random_state=task.config.random_state, probability=True)
            param_grid = {
                'C': [0.1, 1.0, 10.0],
                'kernel': ['rbf', 'linear'],
                'gamma': ['scale', 'auto']
            }
        elif task.config.model_type == ModelType.NAIVE_BAYES:
            model = MultinomialNB()
            param_grid = {
                'alpha': [0.1, 1.0, 10.0]
            }
        elif task.config.model_type == ModelType.GRADIENT_BOOSTING:
            model = GradientBoostingClassifier(random_state=task.config.random_state)
            param_grid = {
                'n_estimators': [100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            }
        else:
            raise ClassificationException(f"Unsupported model type: {task.config.model_type}")
        
        # Hyperparameter tuning
        if task.enable_hyperparameter_tuning:
            best_model, best_params = await self.model_selector.grid_search_cv(
                model, param_grid, X_train, y_train,
                cv=task.config.cross_validation_folds,
                scoring='accuracy'
            )
        else:
            best_model = model
            best_params = model.get_params()
            best_model.fit(X_train, y_train)
        
        # Cross-validation scores
        cv_scores = cross_val_score(
            best_model, X_train, y_train,
            cv=task.config.cross_validation_folds,
            scoring='accuracy'
        ).tolist()
        
        return best_model, best_params, cv_scores
    
    async def _train_ensemble(
        self, 
        X_train: np.ndarray, 
        y_train: np.ndarray, 
        task: ClassificationTask
    ) -> Tuple[Any, Dict[str, Any], List[float]]:
        """Train an ensemble of models"""
        
        # Define base models
        base_models = [
            ('rf', RandomForestClassifier(random_state=task.config.random_state)),
            ('lr', LogisticRegression(random_state=task.config.random_state, max_iter=1000)),
            ('svm', SVC(random_state=task.config.random_state, probability=True))
        ]
        
        # Train ensemble
        ensemble_model = await self.model_selector.create_voting_ensemble(
            base_models, X_train, y_train, voting='soft'
        )
        
        # Cross-validation scores
        cv_scores = cross_val_score(
            ensemble_model, X_train, y_train,
            cv=task.config.cross_validation_folds,
            scoring='accuracy'
        ).tolist()
        
        return ensemble_model, ensemble_model.get_params(), cv_scores
    
    async def _evaluate_model(
        self, 
        model: Any, 
        X_test: np.ndarray, 
        y_test: np.ndarray, 
        task: ClassificationTask
    ) -> Dict[str, Any]:
        """Evaluate trained model"""
        
        # Make predictions
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # Classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Extract per-class metrics
        precision = {str(i): report[str(i)]['precision'] for i in range(len(task.config.target_labels))}
        recall = {str(i): report[str(i)]['recall'] for i in range(len(task.config.target_labels))}
        f1_score = {str(i): report[str(i)]['f1-score'] for i in range(len(task.config.target_labels))}
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        # Feature importance (if available)
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            feature_importance = {
                f"feature_{i}": importance 
                for i, importance in enumerate(model.feature_importances_)
            }
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'confusion_matrix': cm,
            'feature_importance': feature_importance
        }
    
    async def _store_model(self, model_id: str, model: Any, task: ClassificationTask):
        """Store trained model"""
        self.trained_models[model_id] = {
            'model': model,
            'task': task,
            'created_at': datetime.utcnow()
        }
        
        # Store associated preprocessors
        vectorizer_id = f"{task.id}_tfidf"
        if vectorizer_id in self.vectorizers:
            self.trained_models[model_id]['vectorizer'] = self.vectorizers[vectorizer_id]
        
        scaler_id = f"{task.id}_scaler"
        if scaler_id in self.scalers:
            self.trained_models[model_id]['scaler'] = self.scalers[scaler_id]
        
        encoder_id = f"{task.id}_label_encoder"
        if encoder_id in self.label_encoders:
            self.trained_models[model_id]['label_encoder'] = self.label_encoders[encoder_id]
    
    async def _load_model(self, model_id: str) -> Optional[Any]:
        """Load trained model"""
        if model_id in self.trained_models:
            return self.trained_models[model_id]['model']
        return None
    
    async def _prepare_inference_data(self, input_data: Any, model_id: str) -> np.ndarray:
        """Prepare data for inference"""
        
        # Get model info
        model_info = self.trained_models.get(model_id)
        if not model_info:
            raise ClassificationException(f"Model {model_id} not found")
        
        task = model_info['task']
        
        # Convert input to DataFrame
        if isinstance(input_data, str):
            # Single text input
            data = pd.DataFrame({'text': [input_data]})
        elif isinstance(input_data, dict):
            # Single record
            data = pd.DataFrame([input_data])
        elif isinstance(input_data, list):
            # Multiple records
            data = pd.DataFrame(input_data)
        else:
            raise ClassificationException("Invalid input data format")
        
        # Prepare features using the same method as training
        if task.config.data_type == DataType.TEXT:
            vectorizer = model_info.get('vectorizer')
            if vectorizer:
                text_columns = task.config.text_columns or [col for col in data.columns if data[col].dtype == 'object']
                text_data = data[text_columns].fillna('').apply(lambda x: ' '.join(x.astype(str)), axis=1)
                processed_text = await self.text_preprocessor.preprocess_batch(text_data.tolist())
                X = vectorizer.transform(processed_text).toarray()
            else:
                raise ClassificationException("Text vectorizer not found")
        
        elif task.config.data_type == DataType.NUMERICAL:
            scaler = model_info.get('scaler')
            feature_columns = task.config.feature_columns or data.select_dtypes(include=[np.number]).columns.tolist()
            X = data[feature_columns].fillna(data[feature_columns].mean())
            if scaler:
                X = scaler.transform(X)
        
        else:
            # For other data types, implement similar logic
            raise ClassificationException(f"Inference for {task.config.data_type} not implemented")
        
        return X
    
    async def _make_predictions(
        self, 
        model: Any, 
        X: np.ndarray, 
        task: ClassificationInferenceTask
    ) -> List[ClassificationPrediction]:
        """Make predictions using trained model"""
        
        predictions = []
        
        # Get model info
        model_info = self.trained_models.get(task.model_id)
        label_encoder = model_info.get('label_encoder') if model_info else None
        
        # Make predictions
        y_pred = model.predict(X)
        y_prob = model.predict_proba(X) if hasattr(model, 'predict_proba') else None
        
        for i in range(len(y_pred)):
            # Get predicted class
            predicted_class_encoded = y_pred[i]
            if label_encoder:
                predicted_class = label_encoder.inverse_transform([predicted_class_encoded])[0]
            else:
                predicted_class = str(predicted_class_encoded)
            
            # Get probabilities
            if y_prob is not None:
                probs = y_prob[i]
                confidence = float(np.max(probs))
                if label_encoder:
                    class_names = label_encoder.classes_
                    probabilities = {str(class_names[j]): float(probs[j]) for j in range(len(probs))}
                else:
                    probabilities = {str(j): float(probs[j]) for j in range(len(probs))}
            else:
                confidence = 1.0
                probabilities = {predicted_class: 1.0}
            
            # Apply confidence threshold
            if task.confidence_threshold and confidence < task.confidence_threshold:
                predicted_class = "low_confidence"
                confidence = 0.0
            
            prediction = ClassificationPrediction(
                predicted_class=predicted_class,
                confidence=confidence,
                probabilities=probabilities,
                model_version=task.model_id
            )
            
            predictions.append(prediction)
        
        return predictions
    
    async def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a trained model"""
        if model_id in self.trained_models:
            model_info = self.trained_models[model_id]
            return {
                'model_id': model_id,
                'task_name': model_info['task'].name,
                'model_type': model_info['task'].config.model_type.value,
                'classification_type': model_info['task'].config.classification_type.value,
                'data_type': model_info['task'].config.data_type.value,
                'target_labels': model_info['task'].config.target_labels,
                'created_at': model_info['created_at'].isoformat()
            }
        return None
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List all trained models"""
        models = []
        for model_id in self.trained_models:
            model_info = await self.get_model_info(model_id)
            if model_info:
                models.append(model_info)
        return models
    
    async def delete_model(self, model_id: str) -> bool:
        """Delete a trained model"""
        if model_id in self.trained_models:
            del self.trained_models[model_id]
            return True
        return False
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the classification agent"""
        return await self.metrics_collector.get_metrics_summary()


# Template usage example
def create_classification_agent_example():
    """Example of how to create and use a classification agent"""
    
    # Define model configurations
    model_configs = {
        "text_classifier": {
            "model_type": "random_forest",
            "max_features": 5000
        },
        "numerical_classifier": {
            "model_type": "gradient_boosting",
            "n_estimators": 200
        }
    }
    
    # Create agent
    classifier_agent = ClassificationAgent(
        agent_id="classification_001",
        model_configs=model_configs,
        enable_gpu=True
    )
    
    return classifier_agent


# Template configuration for code generation
TEMPLATE_CONFIG = {
    "template_name": "classification_agent_template",
    "template_version": "1.0.0",
    "template_description": "Comprehensive classification agent with multiple algorithms and data types",
    "required_parameters": [
        "agent_name",
        "agent_description",
        "author_name",
        "author_email",
        "created_date"
    ],
    "optional_parameters": [
        "custom_models",
        "feature_engineering_options",
        "evaluation_metrics"
    ],
    "dependencies": [
        "scikit-learn>=1.3.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "torch>=2.0.0",
        "transformers>=4.35.0"
    ],
    "features": [
        "Multiple classification algorithms",
        "Multi-data type support (text, numerical, categorical, mixed)",
        "Automatic feature selection",
        "Hyperparameter tuning",
        "Ensemble methods",
        "Cross-validation",
        "Model evaluation metrics",
        "Batch inference",
        "Model persistence",
        "Performance monitoring"
    ]
}