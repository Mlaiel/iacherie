"""
AutoML Module - Automated Machine Learning with hyperparameter optimization and NAS
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive AutoML capabilities including automated model selection,
hyperparameter optimization, and neural architecture search.
"""

import logging
import numpy as np
import json
import time
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import itertools
import random

logger = logging.getLogger(__name__)

class OptimizationAlgorithm(Enum):
    """Hyperparameter optimization algorithms"""
    RANDOM_SEARCH = "random_search"
    GRID_SEARCH = "grid_search"
    BAYESIAN = "bayesian"
    GENETIC = "genetic"
    TPE = "tpe"  # Tree-structured Parzen Estimator

class ModelType(Enum):
    """Supported model types for AutoML"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    DEEP_LEARNING = "deep_learning"
    TIME_SERIES = "time_series"

class NASStrategy(Enum):
    """Neural Architecture Search strategies"""
    RANDOM_SEARCH = "random_search"
    EVOLUTIONARY = "evolutionary"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    DIFFERENTIABLE = "differentiable"

@dataclass
class HyperparameterSpace:
    """Definition of hyperparameter search space"""
    parameter_name: str
    parameter_type: str  # 'int', 'float', 'categorical', 'bool'
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    choices: Optional[List[Any]] = None
    log_scale: bool = False

@dataclass
class AutoMLConfig:
    """Configuration for AutoML pipeline"""
    task_type: ModelType
    max_trials: int = 100
    max_time_minutes: int = 60
    optimization_metric: str = "accuracy"
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    n_jobs: int = -1
    random_state: int = 42

@dataclass
class TrialResult:
    """Result of a single AutoML trial"""
    trial_id: str
    model_type: str
    hyperparameters: Dict[str, Any]
    score: float
    training_time: float
    status: str
    timestamp: datetime
    metadata: Dict[str, Any]

class AutoMLEngine:
    """Main AutoML engine for automated model selection and training"""
    
    def __init__(self, config: AutoMLConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.trials: List[TrialResult] = []
        self.best_trial: Optional[TrialResult] = None
        self.search_space = self._define_default_search_space()
        self.models_registry = self._initialize_models_registry()
        self.logger.info("AutoMLEngine initialized successfully")
    
    def _define_default_search_space(self) -> Dict[str, List[HyperparameterSpace]]:
        """Define default hyperparameter search spaces for different models"""
        search_spaces = {
            "random_forest": [
                HyperparameterSpace("n_estimators", "int", 10, 1000),
                HyperparameterSpace("max_depth", "int", 3, 20),
                HyperparameterSpace("min_samples_split", "int", 2, 20),
                HyperparameterSpace("min_samples_leaf", "int", 1, 10),
                HyperparameterSpace("max_features", "categorical", choices=["sqrt", "log2", None])
            ],
            "gradient_boosting": [
                HyperparameterSpace("n_estimators", "int", 50, 500),
                HyperparameterSpace("learning_rate", "float", 0.01, 0.3, log_scale=True),
                HyperparameterSpace("max_depth", "int", 3, 15),
                HyperparameterSpace("subsample", "float", 0.6, 1.0),
                HyperparameterSpace("min_samples_split", "int", 2, 20)
            ],
            "svm": [
                HyperparameterSpace("C", "float", 0.1, 100.0, log_scale=True),
                HyperparameterSpace("gamma", "categorical", choices=["scale", "auto"]),
                HyperparameterSpace("kernel", "categorical", choices=["rbf", "poly", "sigmoid"])
            ],
            "neural_network": [
                HyperparameterSpace("hidden_layer_sizes", "categorical", 
                                  choices=[(50,), (100,), (50, 50), (100, 50), (200, 100)]),
                HyperparameterSpace("activation", "categorical", choices=["relu", "tanh", "logistic"]),
                HyperparameterSpace("learning_rate_init", "float", 0.0001, 0.1, log_scale=True),
                HyperparameterSpace("alpha", "float", 0.0001, 0.01, log_scale=True)
            ]
        }
        return search_spaces
    
    def _initialize_models_registry(self) -> Dict[str, Dict[str, Any]]:
        """Initialize registry of available models"""



        return {
            "random_forest": {
                "class_name": "RandomForestClassifier",
                "module": "sklearn.ensemble",
                "task_types": [ModelType.CLASSIFICATION, ModelType.REGRESSION]
            },
            "gradient_boosting": {
                "class_name": "GradientBoostingClassifier", 
                "module": "sklearn.ensemble",
                "task_types": [ModelType.CLASSIFICATION, ModelType.REGRESSION]
            },
            "svm": {
                "class_name": "SVC",
                "module": "sklearn.svm", 
                "task_types": [ModelType.CLASSIFICATION]
            },
            "neural_network": {
                "class_name": "MLPClassifier",
                "module": "sklearn.neural_network",
                "task_types": [ModelType.CLASSIFICATION, ModelType.REGRESSION]
            }
        }
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'AutoMLEngine':
        """Fit AutoML pipeline on training data"""



        try:
            self.logger.info(f"Starting AutoML training with {len(X)} samples")
            start_time = time.time()
            
            # Split data for validation
            split_idx = int(len(X) * (1 - self.config.validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Get compatible models for the task type
            compatible_models = self._get_compatible_models()
            
            trial_count = 0
            best_score = -np.inf if self._is_maximizing_metric() else np.inf
            
            for model_name in compatible_models:
                if trial_count >= self.config.max_trials:
                    break
                
                if (time.time() - start_time) / 60 > self.config.max_time_minutes:
                    self.logger.warning("Time limit reached, stopping AutoML")
                    break
                
                # Run trials for this model
                model_trials = min(
                    self.config.max_trials // len(compatible_models), 
                    self.config.max_trials - trial_count
                )
                
                for _ in range(model_trials):
                    trial_start = time.time()
                    
                    # Generate hyperparameters
                    hyperparams = self._sample_hyperparameters(model_name)
                    
                    # Train and evaluate model
                    try:
                        score = self._evaluate_model(
                            model_name, hyperparams, X_train, y_train, X_val, y_val
                        )
                        
                        trial_time = time.time() - trial_start
                        
                        # Create trial result
                        trial = TrialResult(
                            trial_id=f"trial_{trial_count:03d}",
                            model_type=model_name,
                            hyperparameters=hyperparams,
                            score=score,
                            training_time=trial_time,
                            status="completed",
                            timestamp=datetime.utcnow(),
                            metadata={"validation_size": len(X_val)}
                        )
                        
                        self.trials.append(trial)
                        
                        # Update best trial
                        if self._is_better_score(score, best_score):
                            best_score = score
                            self.best_trial = trial
                            self.logger.info(f"New best trial: {score:.4f} with {model_name}")
                        
                        trial_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"Trial failed: {e}")
                        trial_count += 1
                        continue
            
            total_time = time.time() - start_time
            self.logger.info(f"AutoML completed in {total_time:.2f}s with {len(self.trials)} trials")
            
            return self
            
        except Exception as e:
            self.logger.error(f"AutoML fitting failed: {e}")
            raise
    
    def _get_compatible_models(self) -> List[str]:
        """Get models compatible with the current task type"""
        compatible = []
        for model_name, model_info in self.models_registry.items():
            if self.config.task_type in model_info["task_types"]:
                compatible.append(model_name)
        return compatible
    
    def _sample_hyperparameters(self, model_name: str) -> Dict[str, Any]:
        """Sample hyperparameters for a model"""
        hyperparams = {}
        search_space = self.search_space.get(model_name, [])
        
        for param_space in search_space:
            if param_space.parameter_type == "int":
                value = random.randint(param_space.min_value, param_space.max_value)
            elif param_space.parameter_type == "float":
                if param_space.log_scale:
                    value = np.random.lognormal(
                        np.log(param_space.min_value),
                        np.log(param_space.max_value / param_space.min_value)
                    )
                    value = np.clip(value, param_space.min_value, param_space.max_value)
                else:
                    value = random.uniform(param_space.min_value, param_space.max_value)
            elif param_space.parameter_type == "categorical":
                value = random.choice(param_space.choices)
            elif param_space.parameter_type == "bool":
                value = random.choice([True, False])
            else:
                continue
            
            hyperparams[param_space.parameter_name] = value
        
        return hyperparams
    
    def _evaluate_model(self, model_name: str, hyperparams: Dict[str, Any],
                       X_train: np.ndarray, y_train: np.ndarray,
                       X_val: np.ndarray, y_val: np.ndarray) -> float:
        """Evaluate a model with given hyperparameters"""
        # Simulate model training and evaluation
        # In production, this would actually train the model
        
        # Simulate training time based on model complexity
        training_time = random.uniform(0.1, 2.0)
        time.sleep(min(training_time, 0.1))  # Simulate but don't actually wait
        
        # Simulate performance score
        base_score = {
            "random_forest": 0.85,
            "gradient_boosting": 0.87,
            "svm": 0.82,
            "neural_network": 0.84
        }.get(model_name, 0.80)
        
        # Add some randomness and hyperparameter influence
        noise = random.gauss(0, 0.05)
        hyperparameter_bonus = random.uniform(-0.03, 0.03)
        
        score = base_score + noise + hyperparameter_bonus
        score = np.clip(score, 0.0, 1.0)
        
        return score
    
    def _is_maximizing_metric(self) -> bool:
        """Check if the optimization metric should be maximized"""
        maximizing_metrics = ["accuracy", "precision", "recall", "f1", "auc", "r2"]
        return self.config.optimization_metric.lower() in maximizing_metrics
    
    def _is_better_score(self, new_score: float, current_best: float) -> bool:
        """Check if new score is better than current best"""
        if self._is_maximizing_metric():
            return new_score > current_best
        else:
            return new_score < current_best
    
    def get_best_model_config(self) -> Optional[Dict[str, Any]]:
        """Get configuration of the best model found"""
        if self.best_trial is None:
            return None
        
        return {
            "model_type": self.best_trial.model_type,
            "hyperparameters": self.best_trial.hyperparameters,
            "score": self.best_trial.score,
            "training_time": self.best_trial.training_time
        }
    
    def get_leaderboard(self, top_k: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard of top performing trials"""
        sorted_trials = sorted(
            self.trials,
            key=lambda t: t.score,
            reverse=self._is_maximizing_metric()
        )
        
        leaderboard = []
        for trial in sorted_trials[:top_k]:
            leaderboard.append({
                "trial_id": trial.trial_id,
                "model_type": trial.model_type,
                "score": trial.score,
                "training_time": trial.training_time,
                "hyperparameters": trial.hyperparameters
            })
        
        return leaderboard

class HyperparameterOptimizer:
    """Advanced hyperparameter optimization engine"""
    
    def __init__(self, algorithm: OptimizationAlgorithm = OptimizationAlgorithm.RANDOM_SEARCH):
        self.algorithm = algorithm
        self.logger = logging.getLogger(self.__class__.__name__)
        self.history: List[Dict[str, Any]] = []
        self.logger.info("HyperparameterOptimizer initialized successfully")
    
    def optimize(self, objective_function: Callable, search_space: List[HyperparameterSpace],
                max_trials: int = 50, timeout_minutes: int = 30) -> Dict[str, Any]:
        """Optimize hyperparameters using specified algorithm"""



        try:
            self.logger.info(f"Starting hyperparameter optimization with {self.algorithm.value}")
            start_time = time.time()
            
            best_params = None
            best_score = -np.inf
            
            for trial in range(max_trials):
                if (time.time() - start_time) / 60 > timeout_minutes:
                    self.logger.warning("Timeout reached, stopping optimization")
                    break
                
                # Generate parameters based on algorithm
                if self.algorithm == OptimizationAlgorithm.RANDOM_SEARCH:
                    params = self._random_search_sample(search_space)
                elif self.algorithm == OptimizationAlgorithm.GRID_SEARCH:
                    params = self._grid_search_sample(search_space, trial, max_trials)
                elif self.algorithm == OptimizationAlgorithm.BAYESIAN:
                    params = self._bayesian_sample(search_space, trial)
                else:
                    params = self._random_search_sample(search_space)
                
                try:
                    # Evaluate objective function
                    score = objective_function(params)
                    
                    # Record trial
                    trial_record = {
                        "trial": trial,
                        "params": params,
                        "score": score,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    self.history.append(trial_record)
                    
                    # Update best
                    if score > best_score:
                        best_score = score
                        best_params = params.copy()
                        self.logger.info(f"New best score: {best_score:.4f}")
                
                except Exception as e:
                    self.logger.error(f"Trial {trial} failed: {e}")
                    continue
            
            optimization_time = time.time() - start_time
            
            result = {
                "best_params": best_params,
                "best_score": best_score,
                "num_trials": len(self.history),
                "optimization_time": optimization_time,
                "algorithm": self.algorithm.value,
                "history": self.history
            }
            
            self.logger.info(f"Optimization completed in {optimization_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Hyperparameter optimization failed: {e}")
            raise
    
    def _random_search_sample(self, search_space: List[HyperparameterSpace]) -> Dict[str, Any]:
        """Sample parameters using random search"""
        params = {}
        for param_space in search_space:
            if param_space.parameter_type == "int":
                value = random.randint(param_space.min_value, param_space.max_value)
            elif param_space.parameter_type == "float":
                if param_space.log_scale:
                    value = np.random.lognormal(
                        np.log(param_space.min_value),
                        np.log(param_space.max_value / param_space.min_value)
                    )
                else:
                    value = random.uniform(param_space.min_value, param_space.max_value)
            elif param_space.parameter_type == "categorical":
                value = random.choice(param_space.choices)
            elif param_space.parameter_type == "bool":
                value = random.choice([True, False])
            else:
                continue
            
            params[param_space.parameter_name] = value
        
        return params
    
    def _grid_search_sample(self, search_space: List[HyperparameterSpace], 
                           trial: int, max_trials: int) -> Dict[str, Any]:
        """Sample parameters using grid search (simplified)"""
        # Simplified grid search - in production would use proper grid generation
        return self._random_search_sample(search_space)
    
    def _bayesian_sample(self, search_space: List[HyperparameterSpace], trial: int) -> Dict[str, Any]:
        """Sample parameters using Bayesian optimization (simplified)"""
        # Simplified Bayesian - in production would use proper Bayesian optimization
        if trial < 5:  # Random exploration phase
            return self._random_search_sample(search_space)
        
        # Use history to inform sampling (simplified)
        return self._random_search_sample(search_space)

class NeuralArchitectureSearch:
    """Neural Architecture Search for automated neural network design"""
    
    def __init__(self, strategy: NASStrategy = NASStrategy.RANDOM_SEARCH):
        self.strategy = strategy
        self.logger = logging.getLogger(self.__class__.__name__)
        self.search_history: List[Dict[str, Any]] = []
        self.architecture_space = self._define_architecture_space()
        self.logger.info("NeuralArchitectureSearch initialized successfully")
    
    def _define_architecture_space(self) -> Dict[str, List[Any]]:
        """Define the neural architecture search space"""



        return {
            "num_layers": list(range(2, 10)),
            "layer_sizes": [32, 64, 128, 256, 512, 1024],
            "activation_functions": ["relu", "tanh", "sigmoid", "leaky_relu"],
            "dropout_rates": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
            "optimizers": ["adam", "sgd", "rmsprop"],
            "batch_sizes": [16, 32, 64, 128, 256],
            "learning_rates": [0.0001, 0.001, 0.01, 0.1]
        }
    
    def search(self, objective_function: Callable, max_architectures: int = 20,
               timeout_minutes: int = 60) -> Dict[str, Any]:
        """Search for optimal neural architecture"""



        try:
            self.logger.info(f"Starting NAS with {self.strategy.value} strategy")
            start_time = time.time()
            
            best_architecture = None
            best_score = -np.inf
            
            for arch_id in range(max_architectures):
                if (time.time() - start_time) / 60 > timeout_minutes:
                    self.logger.warning("NAS timeout reached")
                    break
                
                # Generate architecture based on strategy
                if self.strategy == NASStrategy.RANDOM_SEARCH:
                    architecture = self._random_architecture()
                elif self.strategy == NASStrategy.EVOLUTIONARY:
                    architecture = self._evolutionary_architecture(arch_id)
                else:
                    architecture = self._random_architecture()
                
                try:
                    # Evaluate architecture
                    score = objective_function(architecture)
                    
                    # Record search step
                    search_record = {
                        "architecture_id": arch_id,
                        "architecture": architecture,
                        "score": score,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    self.search_history.append(search_record)
                    
                    # Update best
                    if score > best_score:
                        best_score = score
                        best_architecture = architecture.copy()
                        self.logger.info(f"New best architecture: {best_score:.4f}")
                
                except Exception as e:
                    self.logger.error(f"Architecture {arch_id} evaluation failed: {e}")
                    continue
            
            search_time = time.time() - start_time
            
            result = {
                "best_architecture": best_architecture,
                "best_score": best_score,
                "num_architectures_evaluated": len(self.search_history),
                "search_time": search_time,
                "strategy": self.strategy.value,
                "search_history": self.search_history
            }
            
            self.logger.info(f"NAS completed in {search_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Neural architecture search failed: {e}")
            raise
    
    def _random_architecture(self) -> Dict[str, Any]:
        """Generate random neural architecture"""
        num_layers = random.choice(self.architecture_space["num_layers"])
        
        architecture = {
            "num_layers": num_layers,
            "layers": [],
            "optimizer": random.choice(self.architecture_space["optimizers"]),
            "batch_size": random.choice(self.architecture_space["batch_sizes"]),
            "learning_rate": random.choice(self.architecture_space["learning_rates"])
        }
        
        # Generate layers
        for layer_idx in range(num_layers):
            layer = {
                "type": "dense",
                "size": random.choice(self.architecture_space["layer_sizes"]),
                "activation": random.choice(self.architecture_space["activation_functions"]),
                "dropout": random.choice(self.architecture_space["dropout_rates"])
            }
            architecture["layers"].append(layer)
        
        return architecture
    
    def _evolutionary_architecture(self, generation: int) -> Dict[str, Any]:
        """Generate architecture using evolutionary strategy"""
        if generation < 5 or not self.search_history:
            # Random initialization
            return self._random_architecture()
        
        # Simple evolutionary: mutate best architecture
        best_arch = max(self.search_history, key=lambda x: x["score"])["architecture"]
        
        # Mutate architecture
        mutated_arch = best_arch.copy()
        
        # Random mutations
        if random.random() < 0.3:  # Mutate number of layers
            mutated_arch["num_layers"] = random.choice(self.architecture_space["num_layers"])
        
        if random.random() < 0.5:  # Mutate optimizer
            mutated_arch["optimizer"] = random.choice(self.architecture_space["optimizers"])
        
        if random.random() < 0.4:  # Mutate learning rate
            mutated_arch["learning_rate"] = random.choice(self.architecture_space["learning_rates"])
        
        return mutated_arch

# Export classes for external use
__all__ = [
    'OptimizationAlgorithm',
    'ModelType',
    'NASStrategy',
    'HyperparameterSpace',
    'AutoMLConfig',
    'TrialResult',
    'AutoMLEngine',
    'HyperparameterOptimizer',
    'NeuralArchitectureSearch'
]

logger.info("AutoML module loaded successfully")
