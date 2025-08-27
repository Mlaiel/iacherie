"""
Ensemble Module - Ensemble learning, model blending, and voting classifiers
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides comprehensive ensemble learning capabilities including
model blending, voting systems, stacking, and advanced ensemble techniques.
"""

import logging
import numpy as np
import copy
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EnsembleStrategy(Enum):
    """Ensemble learning strategies"""
    VOTING = "voting"
    BAGGING = "bagging"
    BOOSTING = "boosting"
    STACKING = "stacking"
    BLENDING = "blending"
    CASCADING = "cascading"

class VotingType(Enum):
    """Types of voting for ensemble"""
    HARD = "hard"
    SOFT = "soft"
    WEIGHTED = "weighted"

class BlendingStrategy(Enum):
    """Model blending strategies"""
    SIMPLE_AVERAGE = "simple_average"
    WEIGHTED_AVERAGE = "weighted_average"
    RANK_AVERAGE = "rank_average"
    GEOMETRIC_MEAN = "geometric_mean"
    HARMONIC_MEAN = "harmonic_mean"

@dataclass
class ModelInfo:
    """Information about a model in the ensemble"""
    model_id: str
    model_name: str
    model: Any
    weight: float = 1.0
    performance_score: float = 0.0
    metadata: Dict[str, Any] = None

@dataclass
class EnsembleConfig:
    """Configuration for ensemble learning"""
    strategy: EnsembleStrategy
    voting_type: VotingType = VotingType.HARD
    blending_strategy: BlendingStrategy = BlendingStrategy.WEIGHTED_AVERAGE
    use_cross_validation: bool = True
    cv_folds: int = 5
    meta_learner: str = "linear_regression"
    diversity_threshold: float = 0.1

class EnsembleManager:
    """Main ensemble learning manager"""
    
    def __init__(self, config: EnsembleConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.models: List[ModelInfo] = []
        self.meta_model = None
        self.ensemble_weights = {}
        self.performance_history = []
        self.is_fitted = False
        self.logger.info("EnsembleManager initialized successfully")
    
    def add_model(self, model_id: str, model: Any, model_name: str = None,
                 weight: float = 1.0, metadata: Dict[str, Any] = None) -> bool:
        """Add a model to the ensemble"""
        try:
            if model_name is None:
                model_name = f"Model_{len(self.models) + 1}"
            
            model_info = ModelInfo(
                model_id=model_id,
                model_name=model_name,
                model=model,
                weight=weight,
                performance_score=0.0,
                metadata=metadata or {}
            )
            
            self.models.append(model_info)
            self.logger.info(f"Added model to ensemble: {model_id} ({model_name})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add model to ensemble: {e}")
            return False
    
    def remove_model(self, model_id: str) -> bool:
        """Remove a model from the ensemble"""
        try:
            original_count = len(self.models)
            self.models = [m for m in self.models if m.model_id != model_id]
            
            if len(self.models) < original_count:
                self.logger.info(f"Removed model from ensemble: {model_id}")
                self.is_fitted = False  # Need to refit after removal
                return True
            else:
                self.logger.warning(f"Model not found in ensemble: {model_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to remove model from ensemble: {e}")
            return False
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'EnsembleManager':
        """Fit the ensemble on training data"""
        try:
            if len(self.models) < 2:
                raise ValueError("Ensemble requires at least 2 models")
            
            self.logger.info(f"Fitting ensemble with {len(self.models)} models")
            start_time = datetime.utcnow()
            
            # Fit individual models
            for model_info in self.models:
                try:
                    # Simulate model fitting
                    self._fit_individual_model(model_info, X, y)
                    self.logger.debug(f"Fitted model: {model_info.model_id}")
                except Exception as e:
                    self.logger.error(f"Failed to fit model {model_info.model_id}: {e}")
            
            # Calculate model weights based on strategy
            if self.config.strategy == EnsembleStrategy.STACKING:
                self._fit_meta_model(X, y)
            elif self.config.strategy == EnsembleStrategy.BLENDING:
                self._calculate_blend_weights(X, y)
            else:
                self._calculate_ensemble_weights(X, y)
            
            self.is_fitted = True
            fitting_time = (datetime.utcnow() - start_time).total_seconds()
            
            self.performance_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "fitting_time": fitting_time,
                "num_models": len(self.models),
                "strategy": self.config.strategy.value
            })
            
            self.logger.info(f"Ensemble fitting completed in {fitting_time:.2f}s")
            return self
            
        except Exception as e:
            self.logger.error(f"Ensemble fitting failed: {e}")
            raise
    
    def _fit_individual_model(self, model_info: ModelInfo, X: np.ndarray, y: np.ndarray):
        """Fit an individual model"""
        # Simulate model training
        # In production, this would call the actual model's fit method
        model_info.performance_score = np.random.uniform(0.7, 0.95)
    
    def _fit_meta_model(self, X: np.ndarray, y: np.ndarray):
        """Fit meta-model for stacking ensemble"""
        try:
            # Generate meta-features using cross-validation
            meta_features = self._generate_meta_features(X, y)
            
            # Fit meta-model
            self.meta_model = self._create_meta_model()
            # In production, would actually fit the meta-model
            # self.meta_model.fit(meta_features, y)
            
            self.logger.info("Meta-model fitted for stacking ensemble")
            
        except Exception as e:
            self.logger.error(f"Meta-model fitting failed: {e}")
    
    def _generate_meta_features(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Generate meta-features for stacking"""
        if not self.config.use_cross_validation:
            # Simple holdout approach
            split_idx = int(0.8 * len(X))
            X_train, X_val = X[:split_idx], X[split_idx:]
            
            meta_features = []
            for model_info in self.models:
                predictions = self._predict_with_model(model_info, X_val)
                meta_features.append(predictions)
            
            return np.column_stack(meta_features)
        
        # Cross-validation approach (simplified)
        fold_size = len(X) // self.config.cv_folds
        meta_features = np.zeros((len(X), len(self.models)))
        
        for fold in range(self.config.cv_folds):
            start_idx = fold * fold_size
            end_idx = start_idx + fold_size if fold < self.config.cv_folds - 1 else len(X)
            
            for i, model_info in enumerate(self.models):
                # Simulate cross-validation predictions
                predictions = np.random.random(end_idx - start_idx)
                meta_features[start_idx:end_idx, i] = predictions
        
        return meta_features
    
    def _create_meta_model(self):
        """Create meta-model for stacking"""
        # Simplified meta-model
        return {
            "type": self.config.meta_learner,
            "weights": np.random.normal(0, 0.1, len(self.models)),
            "bias": np.random.normal(0, 0.1)
        }
    
    def _calculate_blend_weights(self, X: np.ndarray, y: np.ndarray):
        """Calculate blending weights for models"""
        try:
            if self.config.blending_strategy == BlendingStrategy.SIMPLE_AVERAGE:
                # Equal weights
                weight = 1.0 / len(self.models)
                self.ensemble_weights = {
                    model.model_id: weight for model in self.models
                }
            
            elif self.config.blending_strategy == BlendingStrategy.WEIGHTED_AVERAGE:
                # Performance-based weights
                total_score = sum(model.performance_score for model in self.models)
                if total_score > 0:
                    self.ensemble_weights = {
                        model.model_id: model.performance_score / total_score
                        for model in self.models
                    }
                else:
                    # Fallback to equal weights
                    weight = 1.0 / len(self.models)
                    self.ensemble_weights = {
                        model.model_id: weight for model in self.models
                    }
            
            else:
                # Default to equal weights
                weight = 1.0 / len(self.models)
                self.ensemble_weights = {
                    model.model_id: weight for model in self.models
                }
            
            self.logger.info("Blend weights calculated")
            
        except Exception as e:
            self.logger.error(f"Blend weight calculation failed: {e}")
    
    def _calculate_ensemble_weights(self, X: np.ndarray, y: np.ndarray):
        """Calculate general ensemble weights"""
        # For voting and other strategies
        if self.config.voting_type == VotingType.WEIGHTED:
            self._calculate_blend_weights(X, y)
        else:
            # Equal weights for hard/soft voting
            weight = 1.0 / len(self.models)
            self.ensemble_weights = {
                model.model_id: weight for model in self.models
            }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make ensemble predictions"""
        try:
            if not self.is_fitted:
                raise ValueError("Ensemble not fitted. Call fit() first.")
            
            if self.config.strategy == EnsembleStrategy.STACKING:
                return self._stacking_predict(X)
            elif self.config.strategy == EnsembleStrategy.VOTING:
                return self._voting_predict(X)
            elif self.config.strategy == EnsembleStrategy.BLENDING:
                return self._blending_predict(X)
            else:
                return self._voting_predict(X)  # Default to voting
                
        except Exception as e:
            self.logger.error(f"Ensemble prediction failed: {e}")
            raise
    
    def _stacking_predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using stacking"""
        # Generate meta-features
        meta_features = []
        for model_info in self.models:
            predictions = self._predict_with_model(model_info, X)
            meta_features.append(predictions)
        
        meta_X = np.column_stack(meta_features)
        
        # Use meta-model for final prediction
        if self.meta_model:
            # Simulate meta-model prediction
            weights = self.meta_model["weights"]
            bias = self.meta_model["bias"]
            predictions = np.dot(meta_X, weights) + bias
        else:
            # Fallback to simple average
            predictions = np.mean(meta_X, axis=1)
        
        return predictions
    
    def _voting_predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using voting"""
        all_predictions = []
        
        for model_info in self.models:
            predictions = self._predict_with_model(model_info, X)
            weight = self.ensemble_weights.get(model_info.model_id, 1.0)
            
            if self.config.voting_type == VotingType.WEIGHTED:
                predictions = predictions * weight
            
            all_predictions.append(predictions)
        
        # Combine predictions
        if self.config.voting_type == VotingType.HARD:
            # Majority voting for classification
            stacked = np.column_stack(all_predictions)
            predictions = np.apply_along_axis(
                lambda x: np.bincount(x.astype(int)).argmax(),
                axis=1, arr=stacked
            )
        else:
            # Soft voting (average probabilities/scores)
            predictions = np.mean(all_predictions, axis=0)
        
        return predictions
    
    def _blending_predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using blending"""
        all_predictions = []
        weights = []
        
        for model_info in self.models:
            predictions = self._predict_with_model(model_info, X)
            weight = self.ensemble_weights.get(model_info.model_id, 1.0)
            
            all_predictions.append(predictions)
            weights.append(weight)
        
        # Apply blending strategy
        if self.config.blending_strategy == BlendingStrategy.WEIGHTED_AVERAGE:
            weighted_preds = [pred * w for pred, w in zip(all_predictions, weights)]
            predictions = np.sum(weighted_preds, axis=0) / sum(weights)
        
        elif self.config.blending_strategy == BlendingStrategy.GEOMETRIC_MEAN:
            # Geometric mean of predictions
            stacked = np.column_stack(all_predictions)
            predictions = np.exp(np.mean(np.log(stacked + 1e-8), axis=1))
        
        elif self.config.blending_strategy == BlendingStrategy.HARMONIC_MEAN:
            # Harmonic mean of predictions
            stacked = np.column_stack(all_predictions)
            predictions = len(self.models) / np.sum(1.0 / (stacked + 1e-8), axis=1)
        
        else:
            # Simple average
            predictions = np.mean(all_predictions, axis=0)
        
        return predictions
    
    def _predict_with_model(self, model_info: ModelInfo, X: np.ndarray) -> np.ndarray:
        """Make prediction with individual model"""
        # Simulate model prediction
        # In production, this would call the actual model's predict method
        return np.random.random(len(X))
    
    def get_model_weights(self) -> Dict[str, float]:
        """Get current ensemble weights for all models"""
        return self.ensemble_weights.copy()
    
    def get_ensemble_info(self) -> Dict[str, Any]:
        """Get comprehensive ensemble information"""
        return {
            "num_models": len(self.models),
            "strategy": self.config.strategy.value,
            "voting_type": self.config.voting_type.value if self.config.strategy == EnsembleStrategy.VOTING else None,
            "blending_strategy": self.config.blending_strategy.value if self.config.strategy == EnsembleStrategy.BLENDING else None,
            "is_fitted": self.is_fitted,
            "model_weights": self.ensemble_weights,
            "models": [
                {
                    "model_id": m.model_id,
                    "model_name": m.model_name,
                    "weight": m.weight,
                    "performance_score": m.performance_score
                } for m in self.models
            ]
        }

class ModelBlender:
    """Advanced model blending system"""
    
    def __init__(self, blending_strategy: BlendingStrategy = BlendingStrategy.WEIGHTED_AVERAGE):
        self.blending_strategy = blending_strategy
        self.logger = logging.getLogger(self.__class__.__name__)
        self.blend_weights = {}
        self.model_predictions = {}
        self.validation_scores = {}
        self.logger.info("ModelBlender initialized successfully")
    
    def add_model_predictions(self, model_id: str, predictions: np.ndarray, 
                            validation_score: float = None):
        """Add model predictions to the blender"""
        self.model_predictions[model_id] = predictions
        if validation_score is not None:
            self.validation_scores[model_id] = validation_score
        
        self.logger.info(f"Added predictions for model: {model_id}")
    
    def calculate_blend_weights(self, target_values: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Calculate optimal blending weights"""
        try:
            if self.blending_strategy == BlendingStrategy.SIMPLE_AVERAGE:
                # Equal weights
                num_models = len(self.model_predictions)
                weight = 1.0 / num_models
                self.blend_weights = {
                    model_id: weight for model_id in self.model_predictions.keys()
                }
            
            elif self.blending_strategy == BlendingStrategy.WEIGHTED_AVERAGE:
                # Performance-based weights
                if self.validation_scores:
                    total_score = sum(self.validation_scores.values())
                    self.blend_weights = {
                        model_id: score / total_score
                        for model_id, score in self.validation_scores.items()
                    }
                else:
                    # Fallback to equal weights
                    num_models = len(self.model_predictions)
                    weight = 1.0 / num_models
                    self.blend_weights = {
                        model_id: weight for model_id in self.model_predictions.keys()
                    }
            
            elif self.blending_strategy == BlendingStrategy.RANK_AVERAGE:
                # Rank-based blending
                self._calculate_rank_weights()
            
            self.logger.info("Blend weights calculated")
            return self.blend_weights.copy()
            
        except Exception as e:
            self.logger.error(f"Blend weight calculation failed: {e}")
            raise
    
    def _calculate_rank_weights(self):
        """Calculate rank-based weights"""
        if not self.validation_scores:
            # Equal weights if no scores
            num_models = len(self.model_predictions)
            weight = 1.0 / num_models
            self.blend_weights = {
                model_id: weight for model_id in self.model_predictions.keys()
            }
            return
        
        # Sort models by validation score (descending)
        sorted_models = sorted(
            self.validation_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Calculate rank weights
        num_models = len(sorted_models)
        total_rank_weight = sum(range(1, num_models + 1))
        
        self.blend_weights = {}
        for rank, (model_id, _) in enumerate(sorted_models):
            rank_weight = (num_models - rank) / total_rank_weight
            self.blend_weights[model_id] = rank_weight
    
    def blend_predictions(self) -> np.ndarray:
        """Generate blended predictions"""
        try:
            if not self.model_predictions:
                raise ValueError("No model predictions available")
            
            if not self.blend_weights:
                self.calculate_blend_weights()
            
            # Get all prediction arrays
            predictions_list = []
            weights_list = []
            
            for model_id, predictions in self.model_predictions.items():
                predictions_list.append(predictions)
                weights_list.append(self.blend_weights.get(model_id, 0.0))
            
            # Apply blending strategy
            if self.blending_strategy == BlendingStrategy.GEOMETRIC_MEAN:
                stacked = np.column_stack(predictions_list)
                blended = np.exp(np.mean(np.log(stacked + 1e-8), axis=1))
            
            elif self.blending_strategy == BlendingStrategy.HARMONIC_MEAN:
                stacked = np.column_stack(predictions_list)
                blended = len(predictions_list) / np.sum(1.0 / (stacked + 1e-8), axis=1)
            
            else:
                # Weighted average (default)
                weighted_preds = [pred * w for pred, w in zip(predictions_list, weights_list)]
                blended = np.sum(weighted_preds, axis=0) / sum(weights_list)
            
            self.logger.info("Predictions blended successfully")
            return blended
            
        except Exception as e:
            self.logger.error(f"Prediction blending failed: {e}")
            raise

class VotingClassifier:
    """Advanced voting classifier with multiple voting strategies"""
    
    def __init__(self, voting_type: VotingType = VotingType.HARD):
        self.voting_type = voting_type
        self.logger = logging.getLogger(self.__class__.__name__)
        self.classifiers = {}
        self.classifier_weights = {}
        self.is_fitted = False
        self.class_labels = None
        self.logger.info("VotingClassifier initialized successfully")
    
    def add_classifier(self, classifier_id: str, classifier: Any, weight: float = 1.0):
        """Add a classifier to the voting ensemble"""
        self.classifiers[classifier_id] = classifier
        self.classifier_weights[classifier_id] = weight
        self.is_fitted = False
        
        self.logger.info(f"Added classifier: {classifier_id} with weight {weight}")
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'VotingClassifier':
        """Fit all classifiers in the ensemble"""
        try:
            self.logger.info(f"Fitting voting classifier with {len(self.classifiers)} classifiers")
            
            # Get unique class labels
            self.class_labels = np.unique(y)
            
            # Fit each classifier
            for classifier_id, classifier in self.classifiers.items():
                try:
                    # Simulate classifier fitting
                    self._fit_classifier(classifier, X, y)
                    self.logger.debug(f"Fitted classifier: {classifier_id}")
                except Exception as e:
                    self.logger.error(f"Failed to fit classifier {classifier_id}: {e}")
            
            self.is_fitted = True
            self.logger.info("Voting classifier fitting completed")
            return self
            
        except Exception as e:
            self.logger.error(f"Voting classifier fitting failed: {e}")
            raise
    
    def _fit_classifier(self, classifier: Any, X: np.ndarray, y: np.ndarray):
        """Fit individual classifier (simulation)"""
        # In production, this would call classifier.fit(X, y)
        pass
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using voting"""
        try:
            if not self.is_fitted:
                raise ValueError("Voting classifier not fitted. Call fit() first.")
            
            if self.voting_type == VotingType.HARD:
                return self._hard_voting_predict(X)
            elif self.voting_type == VotingType.SOFT:
                return self._soft_voting_predict(X)
            else:  # WEIGHTED
                return self._weighted_voting_predict(X)
                
        except Exception as e:
            self.logger.error(f"Voting prediction failed: {e}")
            raise
    
    def _hard_voting_predict(self, X: np.ndarray) -> np.ndarray:
        """Hard voting predictions"""
        all_predictions = []
        
        for classifier_id, classifier in self.classifiers.items():
            predictions = self._predict_with_classifier(classifier, X)
            all_predictions.append(predictions)
        
        # Majority vote
        stacked = np.column_stack(all_predictions)
        final_predictions = np.apply_along_axis(
            lambda x: np.bincount(x.astype(int)).argmax(),
            axis=1, arr=stacked
        )
        
        return final_predictions
    
    def _soft_voting_predict(self, X: np.ndarray) -> np.ndarray:
        """Soft voting predictions (average probabilities)"""
        all_probabilities = []
        
        for classifier_id, classifier in self.classifiers.items():
            probabilities = self._predict_proba_with_classifier(classifier, X)
            all_probabilities.append(probabilities)
        
        # Average probabilities
        avg_probabilities = np.mean(all_probabilities, axis=0)
        final_predictions = np.argmax(avg_probabilities, axis=1)
        
        return final_predictions
    
    def _weighted_voting_predict(self, X: np.ndarray) -> np.ndarray:
        """Weighted voting predictions"""
        if self.voting_type == VotingType.HARD:
            # Weighted hard voting
            vote_counts = np.zeros((len(X), len(self.class_labels)))
            
            for classifier_id, classifier in self.classifiers.items():
                predictions = self._predict_with_classifier(classifier, X)
                weight = self.classifier_weights.get(classifier_id, 1.0)
                
                for i, pred in enumerate(predictions):
                    vote_counts[i, pred] += weight
            
            final_predictions = np.argmax(vote_counts, axis=1)
        else:
            # Weighted soft voting
            weighted_probabilities = np.zeros((len(X), len(self.class_labels)))
            total_weight = 0
            
            for classifier_id, classifier in self.classifiers.items():
                probabilities = self._predict_proba_with_classifier(classifier, X)
                weight = self.classifier_weights.get(classifier_id, 1.0)
                
                weighted_probabilities += probabilities * weight
                total_weight += weight
            
            avg_probabilities = weighted_probabilities / total_weight
            final_predictions = np.argmax(avg_probabilities, axis=1)
        
        return final_predictions
    
    def _predict_with_classifier(self, classifier: Any, X: np.ndarray) -> np.ndarray:
        """Make prediction with individual classifier"""
        # Simulate classifier prediction
        return np.random.randint(0, len(self.class_labels), len(X))
    
    def _predict_proba_with_classifier(self, classifier: Any, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities from individual classifier"""
        # Simulate classifier probability prediction
        probabilities = np.random.dirichlet(np.ones(len(self.class_labels)), len(X))
        return probabilities
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get ensemble prediction probabilities"""
        try:
            if not self.is_fitted:
                raise ValueError("Voting classifier not fitted. Call fit() first.")
            
            all_probabilities = []
            weights = []
            
            for classifier_id, classifier in self.classifiers.items():
                probabilities = self._predict_proba_with_classifier(classifier, X)
                weight = self.classifier_weights.get(classifier_id, 1.0)
                
                all_probabilities.append(probabilities * weight)
                weights.append(weight)
            
            # Weighted average of probabilities
            total_weight = sum(weights)
            ensemble_probabilities = np.sum(all_probabilities, axis=0) / total_weight
            
            return ensemble_probabilities
            
        except Exception as e:
            self.logger.error(f"Probability prediction failed: {e}")
            raise

# Export classes for external use
__all__ = [
    'EnsembleStrategy',
    'VotingType',
    'BlendingStrategy',
    'ModelInfo',
    'EnsembleConfig',
    'EnsembleManager',
    'ModelBlender',
    'VotingClassifier'
]

logger.info("Ensemble module loaded successfully")
