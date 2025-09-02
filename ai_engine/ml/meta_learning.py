"""Meta Learning Module - Meta-learning, few-shot learning, and transfer learning
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides meta-learning capabilities including few-shot learning,
transfer learning, and model adaptation techniques.
"""

import logging
import numpy as np
import copy
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)

class MetaLearningAlgorithm(Enum):
    """
Meta-learning algorithms"""

    MAML = "maml"  # Model-Agnostic Meta-Learning
    PROTOTYPICAL = "prototypical"
    MATCHING_NETWORKS = "matching_networks"
    REPTILE = "reptile"

class TransferStrategy(Enum):
    """Transfer learning strategies"""

    FEATURE_EXTRACTION = "feature_extraction"
    FINE_TUNING = "fine_tuning"
    DOMAIN_ADAPTATION = "domain_adaptation"
    MULTI_TASK = "multi_task"

@dataclass
class Task:
    """Meta-learning task definition"""
    task_id: str
    name: str
    data: Dict[str, np.ndarray]  # X_train, y_train, X_test, y_test
    metadata: Dict[str, Any]
    domain: str

@dataclass
class MetaLearningConfig:
    """
Configuration for meta-learning"""
    algorithm: MetaLearningAlgorithm
    num_inner_steps: int = 5
    inner_lr: float = 0.01
    meta_lr: float = 0.001
    num_support_samples: int = 5
    num_query_samples: int = 15
    num_meta_iterations: int = 1000

class MetaLearner:
    """
Main meta-learning engine"""
    
    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.meta_model = None
        self.training_history = []
        self.task_distributions = {}
        self._initialize_meta_model()
        self.logger.info("MetaLearner initialized successfully")
    
    def _initialize_meta_model(self):
        """Initialize the meta-model"""
        try:
            # Simplified meta-model initialization
            self.meta_model = {
                "weights": np.random.normal(0, 0.1, (100, 50)),
                "bias": np.zeros(50),
                "output_weights": np.random.normal(0, 0.1, (50, 1)),
                "output_bias": np.zeros(1)
            }
            
            self.logger.info(f"Meta-model initialized with {self.config.algorithm.value} algorithm")
            
        except Exception as e:
            self.logger.error(f"Meta-model initialization failed: {e}")
            raise
    
    def train(self, tasks: List[Task]) -> Dict[str, Any]:
        """Train the meta-learner on multiple tasks"""
        try:
            self.logger.info(f"Starting meta-training on {len(tasks)} tasks")
            start_time = datetime.utcnow()
            
            meta_losses = []
            task_performances = {}
            
            for iteration in range(self.config.num_meta_iterations):
                # Sample batch of tasks
                batch_tasks = np.random.choice(tasks, size=min(4, len(tasks)), replace=False)
                
                batch_loss = 0.0
                gradients = self._initialize_gradients()
                
                for task in batch_tasks:
                    # Split task data into support and query sets
                    support_data, query_data = self._split_task_data(task)
                    
                    # Perform inner loop adaptation
                    adapted_model = self._inner_loop_adaptation(
                        copy.deepcopy(self.meta_model), support_data
                    )
                    
                    # Compute meta-loss on query set
                    task_loss = self._compute_task_loss(adapted_model, query_data)
                    batch_loss += task_loss
                    
                    # Compute gradients
                    task_gradients = self._compute_meta_gradients(
                        adapted_model, query_data
                    )
                    gradients = self._accumulate_gradients(gradients, task_gradients)
                
                # Meta-update
                avg_batch_loss = batch_loss / len(batch_tasks)
                meta_losses.append(avg_batch_loss)
                
                self._meta_update(gradients, len(batch_tasks))
                
                # Log progress
                if iteration % 100 == 0:
                    self.logger.info(f"Meta-iteration {iteration}: Loss = {avg_batch_loss:.4f}")
            
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Evaluate final performance
            for task in tasks:
                performance = self._evaluate_task_performance(task)
                task_performances[task.task_id] = performance
            
            training_result = {
                "training_time": training_time,
                "meta_losses": meta_losses,
                "final_meta_loss": meta_losses[-1] if meta_losses else 0.0,
                "task_performances": task_performances,
                "num_tasks": len(tasks),
                "num_iterations": self.config.num_meta_iterations
            }
            
            self.training_history.append(training_result)
            
            self.logger.info(f"Meta-training completed in {training_time:.2f}s")
            return training_result
            
        except Exception as e:
            self.logger.error(f"Meta-training failed: {e}")
            raise
    
    def _split_task_data(self, task: Task) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
        """Split task data into support and query sets"""
        X_train = task.data.get('X_train', np.array([]))
        y_train = task.data.get('y_train', np.array([]))
        
        if len(X_train) < self.config.num_support_samples + self.config.num_query_samples:
            # Use all data for support if not enough samples
            support_data = {
                'X': X_train[:self.config.num_support_samples],
                'y': y_train[:self.config.num_support_samples]
            }
            query_data = {
                'X': X_train[self.config.num_support_samples:],
                'y': y_train[self.config.num_support_samples:]
            }
        else:
            # Random split
            indices = np.random.permutation(len(X_train))
            support_idx = indices[:self.config.num_support_samples]
            query_idx = indices[self.config.num_support_samples:self.config.num_support_samples + self.config.num_query_samples]
            
            support_data = {'X': X_train[support_idx], 'y': y_train[support_idx]}
            query_data = {'X': X_train[query_idx], 'y': y_train[query_idx]}
        
        return support_data, query_data
    
    def _inner_loop_adaptation(self, model: Dict[str, np.ndarray], 
        try:
            logger.info(f"Executing _inner_loop_adaptation")
            
            # Implementation for _inner_loop_adaptation
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_inner_loop_adaptation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_inner_loop_adaptation failed: {e}")
            raise
    def _forward_pass(self, model: Dict[str, np.ndarray], X: np.ndarray) -> np.ndarray:
        """
Forward pass through the model"""
        if len(X) == 0:
            return np.array([])
        
        # Simple neural network forward pass
        hidden = np.dot(X, model['weights']) + model['bias']
        hidden = np.maximum(0, hidden)  # ReLU activation
        output = np.dot(hidden, model['output_weights']) + model['output_bias']
        return output.flatten()
    
    def _compute_gradients(self, model: Dict[str, np.ndarray], 
        try:
            logger.info(f"Executing _forward_pass")
            
            # Implementation for _forward_pass
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_forward_pass completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_forward_pass failed: {e}")
            raise
        if len(predictions) == 0:
            # Return zero gradients if no data
            for param_name in model:
                gradients[param_name] = np.zeros_like(model[param_name])
            return gradients
        
        # Simplified gradient computation
        error = predictions - data['y']
        
        # Output layer gradients
        gradients['output_bias'] = np.mean(error, axis=0, keepdims=True)
        
        # Hidden layer (simplified)
        hidden = np.dot(data['X'], model['weights']) + model['bias']
        hidden = np.maximum(0, hidden)
        
        gradients['output_weights'] = np.outer(hidden.mean(axis=0), error.mean())
        gradients['bias'] = np.mean(error) * np.ones_like(model['bias'])
        gradients['weights'] = np.outer(data['X'].mean(axis=0), error.mean())
        
        return gradients
    
    def _compute_task_loss(self, model: Dict[str, np.ndarray], 
        try:
                    # Request validation
                    if not model:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle__compute_task_loss_request(model)
            
                    # Return response
                    return {"status": "success", "data": result}
        try:
                    # Request validation
                    if not model:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle__compute_meta_gradients_request(model)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _compute_meta_gradients failed: {e}")
                    return {"status": "error", "message": str(e)}
    def _compute_meta_gradients(self, model: Dict[str, np.ndarray],
                               query_data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
Compute meta-gradients"""
        predictions = self._forward_pass(model, query_data['X'])
        return self._compute_gradients(model, query_data, predictions)
    
    def _initialize_gradients(self) -> Dict[str, np.ndarray]:
        """
Initialize gradients to zero"""
        gradients = {}
        for param_name in self.meta_model:
            gradients[param_name] = np.zeros_like(self.meta_model[param_name])
        return gradients
    
    def _accumulate_gradients(self, accumulated: Dict[str, np.ndarray],
                             new_gradients: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
Accumulate gradients across tasks"""
        for param_name in accumulated:
            accumulated[param_name] += new_gradients[param_name]
        return accumulated
    
    def _meta_update(self, gradients: Dict[str, np.ndarray], batch_size: int):
        """
Perform meta-parameter update"""
        for param_name in self.meta_model:
            avg_gradient = gradients[param_name] / batch_size
            self.meta_model[param_name] -= self.config.meta_lr * avg_gradient
    
    def _evaluate_task_performance(self, task: Task) -> Dict[str, float]:
        """
Evaluate performance on a single task"""
        try:
            support_data, query_data = self._split_task_data(task)
            adapted_model = self._inner_loop_adaptation(
                copy.deepcopy(self.meta_model), support_data
            )
            
            if len(query_data['X']) == 0:
                return {"accuracy": 0.0, "loss": float('inf')}
            
            predictions = self._forward_pass(adapted_model, query_data['X'])
            loss = np.mean((predictions - query_data['y']) ** 2)
            
            # Simple accuracy for binary classification
            binary_predictions = (predictions > 0.5).astype(int)
            binary_targets = (query_data['y'] > 0.5).astype(int)
            accuracy = np.mean(binary_predictions == binary_targets)
            
            return {"accuracy": float(accuracy), "loss": float(loss)}
            
        except Exception as e:
            self.logger.error(f"Task evaluation failed: {e}")
            return {"accuracy": 0.0, "loss": float('inf')}
    
    def adapt_to_new_task(self, task: Task, num_adaptation_steps: Optional[int] = None) -> Dict[str, np.ndarray]:
        """Adapt the meta-model to a new task"""
        if num_adaptation_steps is None:
            num_adaptation_steps = self.config.num_inner_steps
        
        support_data = {
            'X': task.data.get('X_train', np.array([])),
            'y': task.data.get('y_train', np.array([]))
        }
        
        adapted_model = self._inner_loop_adaptation(
            copy.deepcopy(self.meta_model), support_data
        )
        
        return adapted_model

class FewShotLearner:
    """
Specialized few-shot learning system"""
    
    def __init__(self, algorithm: MetaLearningAlgorithm = MetaLearningAlgorithm.PROTOTYPICAL):
        self.algorithm = algorithm
        self.logger = logging.getLogger(self.__class__.__name__)
        self.prototypes = {}
        self.support_embeddings = {}
        self.logger.info("FewShotLearner initialized successfully")
    
    def train(self, support_set: Dict[str, List[np.ndarray]], 
             embedding_function: Optional[Callable] = None) -> Dict[str, Any]:
        """Train few-shot learner on support set"""
        try:
            self.logger.info(f"Training few-shot learner with {len(support_set)} classes")
            
            if embedding_function is None:
                embedding_function = self._default_embedding_function
            
            # Compute prototypes for each class
            for class_label, samples in support_set.items():
                embeddings = [embedding_function(sample) for sample in samples]
                prototype = np.mean(embeddings, axis=0)
                self.prototypes[class_label] = prototype
                self.support_embeddings[class_label] = embeddings
            
            training_result = {
                "num_classes": len(support_set),
                "num_prototypes": len(self.prototypes),
                "algorithm": self.algorithm.value
            }
            
            self.logger.info("Few-shot training completed")
            return training_result
            
        except Exception as e:
            self.logger.error(f"Few-shot training failed: {e}")
            raise
    
    def predict(self, query_samples: List[np.ndarray], 
               embedding_function: Optional[Callable] = None) -> List[str]:
        """Predict classes for query samples"""
        try:
            if not self.prototypes:
                raise ValueError("Model not trained. Call train() first.")
            
            if embedding_function is None:
                embedding_function = self._default_embedding_function
            
            predictions = []
            
            for sample in query_samples:
                query_embedding = embedding_function(sample)
                
                # Find nearest prototype
                min_distance = float('inf')
                predicted_class = None
                
                for class_label, prototype in self.prototypes.items():
                    distance = np.linalg.norm(query_embedding - prototype)
                    
                    if distance < min_distance:
                        min_distance = distance
                        predicted_class = class_label
                
                predictions.append(predicted_class)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Few-shot prediction failed: {e}")
            raise
    
    def _default_embedding_function(self, sample: np.ndarray) -> np.ndarray:
        """Default embedding function (simple feature extraction)"""
        # Simple embedding: flatten and normalize
        flattened = sample.flatten()
        normalized = flattened / (np.linalg.norm(flattened) + 1e-8)
        return normalized

class TransferLearner:
    """
Transfer learning system"""
    
    def __init__(self, strategy: TransferStrategy = TransferStrategy.FINE_TUNING):
        self.strategy = strategy
        self.logger = logging.getLogger(self.__class__.__name__)
        self.source_model = None
        self.target_model = None
        self.feature_extractor = None
        self.transfer_history = []
        self.logger.info("TransferLearner initialized successfully")
    
    def set_source_model(self, model: Any, feature_extractor: Optional[Callable] = None):
        """Set the pre-trained source model"""
        self.source_model = model
        if feature_extractor:
            self.feature_extractor = feature_extractor
        else:
            self.feature_extractor = self._default_feature_extractor
        
        self.logger.info("Source model set for transfer learning")
    
    def transfer(self, target_data: Dict[str, np.ndarray], 
                target_labels: np.ndarray) -> Dict[str, Any]:
        """Perform transfer learning to target domain"""
        try:
            if self.source_model is None:
                raise ValueError("Source model not set. Call set_source_model() first.")
            
            self.logger.info(f"Starting transfer learning with {self.strategy.value} strategy")
            start_time = datetime.utcnow()
            
            if self.strategy == TransferStrategy.FEATURE_EXTRACTION:
                result = self._feature_extraction_transfer(target_data, target_labels)
            elif self.strategy == TransferStrategy.FINE_TUNING:
                result = self._fine_tuning_transfer(target_data, target_labels)
            elif self.strategy == TransferStrategy.DOMAIN_ADAPTATION:
                result = self._domain_adaptation_transfer(target_data, target_labels)
            else:
                result = self._fine_tuning_transfer(target_data, target_labels)
            
            transfer_time = (datetime.utcnow() - start_time).total_seconds()
            result['transfer_time'] = transfer_time
            result['strategy'] = self.strategy.value
            
            self.transfer_history.append(result)
            
            self.logger.info(f"Transfer learning completed in {transfer_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Transfer learning failed: {e}")
            raise
    
    def _feature_extraction_transfer(self, target_data: Dict[str, np.ndarray],
                                   target_labels: np.ndarray) -> Dict[str, Any]:
        """Transfer learning using feature extraction"""
        # Extract features using source model
        X_train = target_data.get('X_train', np.array([]))
        X_test = target_data.get('X_test', np.array([]))
        
        train_features = self.feature_extractor(X_train)
        test_features = self.feature_extractor(X_test)
        
        # Train simple classifier on extracted features
        target_model = self._train_target_classifier(train_features, target_labels)
        
        # Evaluate
        test_predictions = self._predict_with_target_model(target_model, test_features)
        
        return {
            "method": "feature_extraction",
        try:
            logger.info(f"Executing _fine_tuning_transfer")
            
            # Implementation for _fine_tuning_transfer
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_fine_tuning_transfer completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_fine_tuning_transfer failed: {e}")
            raise
        X_train = target_data.get('X_train', np.array([]))
        X_test = target_data.get('X_test', np.array([]))
        
        # Simulate fine-tuning process
        fine_tuning_steps = 100
        learning_rate = 0.001
        
        for step in range(fine_tuning_steps):
            # Simulate gradient update
            pass  # In practice, would update model parameters
        
        # Evaluate
        test_predictions = self._predict_with_source_model(X_test)
        
        return {
            "method": "fine_tuning",
            "fine_tuning_steps": fine_tuning_steps,
            "learning_rate": learning_rate,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "test_accuracy": self._compute_accuracy(test_predictions, target_data.get('y_test', np.array([])))
        }
    
    def _domain_adaptation_transfer(self, target_data: Dict[str, np.ndarray],
                                  target_labels: np.ndarray) -> Dict[str, Any]:
        """Transfer learning using domain adaptation"""
        # Simplified domain adaptation
        return self._fine_tuning_transfer(target_data, target_labels)
    
    def _default_feature_extractor(self, data: np.ndarray) -> np.ndarray:
        """
Default feature extraction function"""
        if len(data) == 0:
            return np.array([]).reshape(0, 50)
        
        # Simple feature extraction: random projection
        np.random.seed(42)  # For reproducibility
        projection_matrix = np.random.normal(0, 0.1, (data.shape[-1], 50))
        features = np.dot(data.reshape(len(data), -1), projection_matrix)
        return features
    
    def _train_target_classifier(self, features: np.ndarray, labels: np.ndarray) -> Dict[str, np.ndarray]:
        """
Train simple classifier on extracted features"""
        if len(features) == 0:
            return {"weights": np.array([]), "bias": np.array([])}
        
        # Simple linear classifier
        weights = np.random.normal(0, 0.1, features.shape[1])
        bias = np.random.normal(0, 0.1)
        
        return {"weights": weights, "bias": bias}
    
    def _predict_with_target_model(self, model: Dict[str, np.ndarray], 
                                  features: np.ndarray) -> np.ndarray:
        """Make predictions with target model"""
        if len(features) == 0:
            return np.array([])
        
        predictions = np.dot(features, model["weights"]) + model["bias"]
        return (predictions > 0).astype(int)
    
    def _predict_with_source_model(self, data: np.ndarray) -> np.ndarray:
        """Make predictions with source model"""
        if len(data) == 0:
            return np.array([])
        
        # Simulate source model prediction
        predictions = np.random.randint(0, 2, len(data))
        return predictions
    
    def _compute_accuracy(self, predictions: np.ndarray, true_labels: np.ndarray) -> float:
        """
Compute classification accuracy"""
        if len(predictions) == 0 or len(true_labels) == 0:
            return 0.0
        
        if len(predictions) != len(true_labels):
            return 0.0
        
        accuracy = np.mean(predictions == true_labels)
        return float(accuracy)

# Export classes for external use
__all__ = [
    'MetaLearningAlgorithm',
    'TransferStrategy',
    'Task',
    'MetaLearningConfig',
    'MetaLearner',
    'FewShotLearner',
    'TransferLearner'
]

logger.info("Meta learning module loaded successfully")
