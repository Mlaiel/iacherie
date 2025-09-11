"""
Model Utilities - ML Engineer Expert Implementation
=================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise ML model management, evaluation, and optimization utilities.
"""

import logging
import pickle
import joblib
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime
import hashlib
import time
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import cross_val_score
import warnings

logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    """Model performance metrics"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_time: float
    inference_time: float
    model_size: int  # in bytes
    timestamp: datetime


@dataclass
class ModelVersion:
    """Model version information"""
    version: str
    model_hash: str
    created_at: datetime
    metrics: ModelMetrics
    metadata: Dict[str, Any]
    file_path: str


class ModelUtilities:
    """
    Enterprise ML model management system implementing:
    - Model serialization and versioning
    - Performance evaluation and monitoring
    - Model optimization and compression
    - Feature engineering utilities
    - Cross-validation and hyperparameter tuning
    - Model deployment preparation
    """
    
    def __init__(self):
        """Initialize model utilities"""
        self.models_registry: Dict[str, List[ModelVersion]] = {}
        self.active_models: Dict[str, Any] = {}
        self.feature_scalers: Dict[str, Any] = {}
        self.evaluation_history: List[Dict[str, Any]] = []
        
        # Performance thresholds
        self.performance_thresholds = {
            'accuracy_min': 0.85,
            'precision_min': 0.80,
            'recall_min': 0.80,
            'f1_score_min': 0.80,
            'inference_time_max': 0.1,  # seconds
            'model_size_max': 100 * 1024 * 1024  # 100MB
        }
        
        logger.info("ModelUtilities initialized with enterprise ML capabilities")
    
    def save_model(self, model: Any, model_name: str, version: str = None,
                   metadata: Dict[str, Any] = None) -> str:
        """Save model with versioning and metadata"""
        try:
            if version is None:
                version = f"v{int(time.time())}"
            
            # Create model hash for integrity checking
            model_data = pickle.dumps(model)
            model_hash = hashlib.sha256(model_data).hexdigest()
            
            # Save model file
            file_path = f"/tmp/models/{model_name}_{version}.pkl"
            
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb') as f:
                pickle.dump(model, f)
            
            # Calculate model size
            model_size = len(model_data)
            
            # Create version record
            model_version = ModelVersion(
                version=version,
                model_hash=model_hash,
                created_at=datetime.now(),
                metrics=ModelMetrics(
                    accuracy=0.0, precision=0.0, recall=0.0, f1_score=0.0,
                    training_time=0.0, inference_time=0.0, model_size=model_size,
                    timestamp=datetime.now()
                ),
                metadata=metadata or {},
                file_path=file_path
            )
            
            # Add to registry
            if model_name not in self.models_registry:
                self.models_registry[model_name] = []
            
            self.models_registry[model_name].append(model_version)
            
            logger.info(f"Model saved: {model_name} v{version}")
            return version
            
        except Exception as e:
            logger.error(f"Model saving failed: {e}")
            raise
    
    def load_model(self, model_name: str, version: str = None) -> Any:
        """Load model by name and version"""
        try:
            if model_name not in self.models_registry:
                raise ValueError(f"Model '{model_name}' not found in registry")
            
            versions = self.models_registry[model_name]
            
            if version is None:
                # Load latest version
                if not versions:
                    raise ValueError(f"No versions found for model '{model_name}'")
                model_version = max(versions, key=lambda v: v.created_at)
            else:
                # Load specific version
                model_version = next((v for v in versions if v.version == version), None)
                if model_version is None:
                    raise ValueError(f"Version '{version}' not found for model '{model_name}'")
            
            # Load model from file
            with open(model_version.file_path, 'rb') as f:
                model = pickle.load(f)
            
            # Verify model integrity
            model_data = pickle.dumps(model)
            current_hash = hashlib.sha256(model_data).hexdigest()
            
            if current_hash != model_version.model_hash:
                logger.warning(f"Model integrity check failed for {model_name} v{model_version.version}")
            
            # Cache active model
            self.active_models[f"{model_name}_{model_version.version}"] = model
            
            logger.info(f"Model loaded: {model_name} v{model_version.version}")
            return model
            
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise
    
    def evaluate_model(self, model: Any, X_test: np.ndarray, y_test: np.ndarray,
                      model_name: str = "unknown") -> ModelMetrics:
        """Comprehensive model evaluation"""
        try:
            start_time = time.time()
            
            # Make predictions
            y_pred = model.predict(X_test)
            inference_time = (time.time() - start_time) / len(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            
            # Handle binary vs multiclass classification
            average_method = 'binary' if len(np.unique(y_test)) == 2 else 'weighted'
            
            precision = precision_score(y_test, y_pred, average=average_method, zero_division=0)
            recall = recall_score(y_test, y_pred, average=average_method, zero_division=0)
            f1 = f1_score(y_test, y_pred, average=average_method, zero_division=0)
            
            # Model size
            model_size = len(pickle.dumps(model))
            
            metrics = ModelMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                training_time=0.0,  # Would be set during training
                inference_time=inference_time,
                model_size=model_size,
                timestamp=datetime.now()
            )
            
            # Check performance thresholds
            self._check_performance_thresholds(metrics, model_name)
            
            # Log evaluation
            self.evaluation_history.append({
                'model_name': model_name,
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1,
                    'inference_time': inference_time
                }
            })
            
            logger.info(f"Model evaluated: {model_name} - Accuracy: {accuracy:.4f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            raise
    
    def cross_validate_model(self, model: Any, X: np.ndarray, y: np.ndarray,
                           cv_folds: int = 5, scoring: str = 'accuracy') -> Dict[str, Any]:
        """Perform cross-validation on model"""
        try:
            start_time = time.time()
            
            # Perform cross-validation
            cv_scores = cross_val_score(model, X, y, cv=cv_folds, scoring=scoring)
            
            cv_time = time.time() - start_time
            
            results = {
                'mean_score': np.mean(cv_scores),
                'std_score': np.std(cv_scores),
                'scores': cv_scores.tolist(),
                'cv_folds': cv_folds,
                'scoring_metric': scoring,
                'cv_time': cv_time
            }
            
            logger.info(f"Cross-validation completed: {scoring} = {results['mean_score']:.4f} (+/- {results['std_score']:.4f})")
            return results
            
        except Exception as e:
            logger.error(f"Cross-validation failed: {e}")
            raise
    
    def optimize_hyperparameters(self, model_class: type, param_grid: Dict[str, List],
                                X: np.ndarray, y: np.ndarray, cv_folds: int = 5) -> Dict[str, Any]:
        """Hyperparameter optimization using grid search"""
        try:
            from sklearn.model_selection import GridSearchCV
            
            start_time = time.time()
            
            # Create base model
            base_model = model_class()
            
            # Perform grid search
            grid_search = GridSearchCV(
                base_model, param_grid, cv=cv_folds, 
                scoring='accuracy', n_jobs=-1, verbose=1
            )
            
            grid_search.fit(X, y)
            
            optimization_time = time.time() - start_time
            
            results = {
                'best_params': grid_search.best_params_,
                'best_score': grid_search.best_score_,
                'best_model': grid_search.best_estimator_,
                'cv_results': grid_search.cv_results_,
                'optimization_time': optimization_time,
                'total_fits': len(grid_search.cv_results_['params'])
            }
            
            logger.info(f"Hyperparameter optimization completed: Best score = {results['best_score']:.4f}")
            return results
            
        except Exception as e:
            logger.error(f"Hyperparameter optimization failed: {e}")
            raise
    
    def feature_importance_analysis(self, model: Any, feature_names: List[str] = None) -> Dict[str, Any]:
        """Analyze feature importance"""
        try:
            importance_data = {}
            
            # Try to get feature importance from model
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                importance_data['type'] = 'tree_based'
            elif hasattr(model, 'coef_'):
                importances = np.abs(model.coef_).flatten()
                importance_data['type'] = 'linear'
            else:
                logger.warning("Model does not support feature importance analysis")
                return {}
            
            # Create feature names if not provided
            if feature_names is None:
                feature_names = [f"feature_{i}" for i in range(len(importances))]
            
            # Sort features by importance
            feature_importance_pairs = list(zip(feature_names, importances))
            feature_importance_pairs.sort(key=lambda x: x[1], reverse=True)
            
            importance_data.update({
                'features': [pair[0] for pair in feature_importance_pairs],
                'importances': [float(pair[1]) for pair in feature_importance_pairs],
                'top_features': feature_importance_pairs[:10],  # Top 10 features
                'total_features': len(feature_names)
            })
            
            logger.info(f"Feature importance analysis completed: {len(feature_names)} features analyzed")
            return importance_data
            
        except Exception as e:
            logger.error(f"Feature importance analysis failed: {e}")
            raise
    
    def prepare_features(self, data: pd.DataFrame, target_column: str = None,
                        scaling_method: str = 'standard') -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for model training"""
        try:
            # Separate features and target
            if target_column:
                X = data.drop(columns=[target_column])
                y = data[target_column].values
            else:
                X = data
                y = None
            
            # Handle categorical variables
            X_processed = pd.get_dummies(X, drop_first=True)
            
            # Handle missing values
            X_processed = X_processed.fillna(X_processed.mean())
            
            # Feature scaling
            if scaling_method == 'standard':
                from sklearn.preprocessing import StandardScaler
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_processed)
                self.feature_scalers[f'scaler_{int(time.time())}'] = scaler
            elif scaling_method == 'minmax':
                from sklearn.preprocessing import MinMaxScaler
                scaler = MinMaxScaler()
                X_scaled = scaler.fit_transform(X_processed)
                self.feature_scalers[f'scaler_{int(time.time())}'] = scaler
            else:
                X_scaled = X_processed.values
            
            logger.info(f"Features prepared: {X_scaled.shape[1]} features, {X_scaled.shape[0]} samples")
            return X_scaled, y
            
        except Exception as e:
            logger.error(f"Feature preparation failed: {e}")
            raise
    
    def model_comparison(self, models: Dict[str, Any], X_test: np.ndarray, 
                        y_test: np.ndarray) -> Dict[str, Any]:
        """Compare multiple models performance"""
        try:
            comparison_results = {}
            
            for model_name, model in models.items():
                metrics = self.evaluate_model(model, X_test, y_test, model_name)
                
                comparison_results[model_name] = {
                    'accuracy': metrics.accuracy,
                    'precision': metrics.precision,
                    'recall': metrics.recall,
                    'f1_score': metrics.f1_score,
                    'inference_time': metrics.inference_time,
                    'model_size': metrics.model_size
                }
            
            # Find best model for each metric
            best_models = {}
            for metric in ['accuracy', 'precision', 'recall', 'f1_score']:
                best_models[f'best_{metric}'] = max(
                    comparison_results.items(),
                    key=lambda x: x[1][metric]
                )[0]
            
            best_models['fastest_inference'] = min(
                comparison_results.items(),
                key=lambda x: x[1]['inference_time']
            )[0]
            
            best_models['smallest_size'] = min(
                comparison_results.items(),
                key=lambda x: x[1]['model_size']
            )[0]
            
            results = {
                'model_metrics': comparison_results,
                'best_models': best_models,
                'comparison_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Model comparison completed: {len(models)} models compared")
            return results
            
        except Exception as e:
            logger.error(f"Model comparison failed: {e}")
            raise
    
    def model_deployment_check(self, model: Any, model_name: str) -> Dict[str, Any]:
        """Check if model is ready for deployment"""
        try:
            deployment_checks = {
                'serializable': False,
                'size_acceptable': False,
                'performance_acceptable': False,
                'inference_speed_acceptable': False,
                'ready_for_deployment': False,
                'issues': []
            }
            
            # Check serializability
            try:
                pickle.dumps(model)
                deployment_checks['serializable'] = True
            except Exception as e:
                deployment_checks['issues'].append(f"Serialization failed: {e}")
            
            # Check model size
            model_size = len(pickle.dumps(model))
            if model_size <= self.performance_thresholds['model_size_max']:
                deployment_checks['size_acceptable'] = True
            else:
                deployment_checks['issues'].append(f"Model too large: {model_size} bytes")
            
            # Check if we have performance metrics
            if model_name in self.models_registry:
                latest_version = max(self.models_registry[model_name], key=lambda v: v.created_at)
                metrics = latest_version.metrics
                
                # Check performance thresholds
                if metrics.accuracy >= self.performance_thresholds['accuracy_min']:
                    deployment_checks['performance_acceptable'] = True
                else:
                    deployment_checks['issues'].append(f"Accuracy too low: {metrics.accuracy}")
                
                # Check inference speed
                if metrics.inference_time <= self.performance_thresholds['inference_time_max']:
                    deployment_checks['inference_speed_acceptable'] = True
                else:
                    deployment_checks['issues'].append(f"Inference too slow: {metrics.inference_time}s")
            
            # Overall deployment readiness
            deployment_checks['ready_for_deployment'] = (
                deployment_checks['serializable'] and
                deployment_checks['size_acceptable'] and
                deployment_checks['performance_acceptable'] and
                deployment_checks['inference_speed_acceptable']
            )
            
            logger.info(f"Deployment check completed for {model_name}: Ready = {deployment_checks['ready_for_deployment']}")
            return deployment_checks
            
        except Exception as e:
            logger.error(f"Deployment check failed: {e}")
            raise
    
    def get_model_registry_summary(self) -> Dict[str, Any]:
        """Get summary of model registry"""
        try:
            summary = {
                'total_models': len(self.models_registry),
                'total_versions': sum(len(versions) for versions in self.models_registry.values()),
                'active_models': len(self.active_models),
                'models': {}
            }
            
            for model_name, versions in self.models_registry.items():
                latest_version = max(versions, key=lambda v: v.created_at)
                summary['models'][model_name] = {
                    'total_versions': len(versions),
                    'latest_version': latest_version.version,
                    'created_at': latest_version.created_at.isoformat(),
                    'latest_metrics': {
                        'accuracy': latest_version.metrics.accuracy,
                        'f1_score': latest_version.metrics.f1_score,
                        'model_size': latest_version.metrics.model_size
                    }
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get model registry summary: {e}")
            return {}
    
    def _check_performance_thresholds(self, metrics: ModelMetrics, model_name: str):
        """Check if model meets performance thresholds"""
        warnings_list = []
        
        if metrics.accuracy < self.performance_thresholds['accuracy_min']:
            warnings_list.append(f"Low accuracy: {metrics.accuracy:.4f}")
        
        if metrics.precision < self.performance_thresholds['precision_min']:
            warnings_list.append(f"Low precision: {metrics.precision:.4f}")
        
        if metrics.recall < self.performance_thresholds['recall_min']:
            warnings_list.append(f"Low recall: {metrics.recall:.4f}")
        
        if metrics.f1_score < self.performance_thresholds['f1_score_min']:
            warnings_list.append(f"Low F1-score: {metrics.f1_score:.4f}")
        
        if metrics.inference_time > self.performance_thresholds['inference_time_max']:
            warnings_list.append(f"Slow inference: {metrics.inference_time:.4f}s")
        
        if metrics.model_size > self.performance_thresholds['model_size_max']:
            warnings_list.append(f"Large model size: {metrics.model_size} bytes")
        
        if warnings_list:
            logger.warning(f"Model {model_name} performance issues: {'; '.join(warnings_list)}")


# Global instance for easy access
model_utils = ModelUtilities()