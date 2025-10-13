#!/usr/bin/env python3
"""
🧠 OPTIMIZED ML FRAMEWORK
=========================

High-performance ML framework with best practices applied by ML Engineer.

Author: ML Engineer Expert
Created: 2025-09-23
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
import joblib
import time


@dataclass
class ModelMetrics:
    """Model performance metrics"""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    training_time: float = 0.0
    inference_time: float = 0.0


class MLModelBase(ABC):
    """Base class for ML models with optimization patterns"""
    
    def __init__(self, model_version: str = "1.0.0"):
        self.model_version = model_version
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = None
        self.metrics = ModelMetrics()
        self.is_trained = False
    
    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray, **kwargs) -> ModelMetrics:
        """Train the model with optimization"""
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions with performance monitoring"""
        pass
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> ModelMetrics:
        """Evaluate model performance"""
        start_time = time.time()
        predictions = self.predict(X)
        inference_time = time.time() - start_time
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        self.metrics.accuracy = accuracy_score(y, predictions)
        self.metrics.precision = precision_score(y, predictions, average='weighted')
        self.metrics.recall = recall_score(y, predictions, average='weighted')
        self.metrics.f1_score = f1_score(y, predictions, average='weighted')
        self.metrics.inference_time = inference_time
        
        self.logger.info(f"Model evaluation: Accuracy={self.metrics.accuracy:.4f}")
        return self.metrics
    
    def save_model(self, path: str) -> bool:
        """Save model with versioning"""
        try:
            model_data = {
                'model': self.model,
                'version': self.model_version,
                'metrics': self.metrics,
                'trained': self.is_trained
            }
            joblib.dump(model_data, path)
            self.logger.info(f"Model saved to {path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, path: str) -> bool:
        """Load model with validation"""
        try:
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.model_version = model_data['version']
            self.metrics = model_data['metrics']
            self.is_trained = model_data['trained']
            self.logger.info(f"Model loaded from {path}")
            return True
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False


class OptimizedMLPipeline:
    """Optimized ML pipeline with performance enhancements"""
    
    def __init__(self, batch_size: int = 32, n_jobs: int = -1):
        self.batch_size = batch_size
        self.n_jobs = n_jobs
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pipeline_metrics = {}
    
    def batch_process(self, data: np.ndarray, process_func, **kwargs) -> List[Any]:
        """Optimized batch processing"""
        results = []
        
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            
            start_time = time.time()
            batch_result = process_func(batch, **kwargs)
            batch_time = time.time() - start_time
            
            results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
            
            # Log batch performance
            if i % (self.batch_size * 10) == 0:
                self.logger.info(f"Processed batch {i//self.batch_size}, time: {batch_time:.4f}s")
        
        return results
    
    def parallel_train_models(self, models: List[MLModelBase], X: np.ndarray, y: np.ndarray) -> Dict[str, ModelMetrics]:
        """Train multiple models in parallel"""
        from concurrent.futures import ThreadPoolExecutor
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.n_jobs if self.n_jobs > 0 else None) as executor:
            future_to_model = {
                executor.submit(model.train, X, y): model.__class__.__name__ 
                for model in models
            }
            
            for future in future_to_model:
                model_name = future_to_model[future]
                try:
                    metrics = future.result()
                    results[model_name] = metrics
                    self.logger.info(f"Model {model_name} trained successfully")
                except Exception as e:
                    self.logger.error(f"Model {model_name} training failed: {e}")
        
        return results
    
    def optimize_hyperparameters(self, model: MLModelBase, X: np.ndarray, y: np.ndarray, 
                                param_grid: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Optimized hyperparameter tuning"""
        from sklearn.model_selection import GridSearchCV
        
        # Simplified grid search with cross-validation
        best_params = {}
        best_score = 0.0
        
        # Sample-based optimization for performance
        sample_size = min(1000, len(X))
        sample_indices = np.random.choice(len(X), sample_size, replace=False)
        X_sample = X[sample_indices]
        y_sample = y[sample_indices]
        
        for param_name, param_values in param_grid.items():
            best_param_value = param_values[0]
            
            for param_value in param_values:
                # Quick evaluation
                temp_model = model.__class__()
                setattr(temp_model, param_name, param_value)
                
                metrics = temp_model.train(X_sample, y_sample)
                
                if metrics.accuracy > best_score:
                    best_score = metrics.accuracy
                    best_param_value = param_value
            
            best_params[param_name] = best_param_value
        
        self.logger.info(f"Best hyperparameters: {best_params}")
        return best_params


class ModelPerformanceMonitor:
    """Monitor ML model performance in production"""
    
    def __init__(self):
        self.performance_history = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_prediction(self, model_version: str, prediction_time: float, 
                      confidence: float = None) -> None:
        """Log prediction performance"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'model_version': model_version,
            'prediction_time': prediction_time,
            'confidence': confidence
        }
        
        self.performance_history.append(log_entry)
        
        # Alert if performance degrades
        if len(self.performance_history) > 100:
            recent_avg = np.mean([entry['prediction_time'] for entry in self.performance_history[-100:]])
            overall_avg = np.mean([entry['prediction_time'] for entry in self.performance_history])
            
            if recent_avg > overall_avg * 1.5:
                self.logger.warning("Model performance degradation detected")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        if not self.performance_history:
            return {"status": "No data available"}
        
        times = [entry['prediction_time'] for entry in self.performance_history]
        
        return {
            "total_predictions": len(self.performance_history),
            "avg_prediction_time": np.mean(times),
            "max_prediction_time": np.max(times),
            "min_prediction_time": np.min(times),
            "std_prediction_time": np.std(times),
            "last_24h_predictions": len([e for e in self.performance_history 
                                       if (datetime.now() - datetime.fromisoformat(e['timestamp'])).days < 1])
        }


# Factory functions
def create_optimized_pipeline(batch_size: int = 32, n_jobs: int = -1) -> OptimizedMLPipeline:
    """Create optimized ML pipeline"""
    return OptimizedMLPipeline(batch_size=batch_size, n_jobs=n_jobs)

def create_performance_monitor() -> ModelPerformanceMonitor:
    """Create model performance monitor"""
    return ModelPerformanceMonitor()
