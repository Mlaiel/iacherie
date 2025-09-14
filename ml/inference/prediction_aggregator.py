"""🎯 Prediction Aggregator - Enterprise ML Infrastructure
=======================================================
Module: ml/inference/prediction_aggregator.py
Author: Fahed Mlaiel (mlaiel@live.de)
=======================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 PREDICTION AGGREGATION & ENSEMBLE SYSTEM
Enterprise ensemble prediction aggregation with confidence scoring and voting mechanisms
- Multi-model ensemble predictions
- Weighted voting and confidence scoring
- Creator-specific model combinations
- Performance-based model selection
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from statistics import mean, median, mode
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class AggregationMethod(Enum):
    """Prediction aggregation methods"""
    SIMPLE_AVERAGE = "simple_average"
    WEIGHTED_AVERAGE = "weighted_average"
    MAJORITY_VOTING = "majority_voting"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    RANK_FUSION = "rank_fusion"
    STACKING = "stacking"
    DYNAMIC_SELECTION = "dynamic_selection"
    CREATOR_SPECIFIC = "creator_specific"


class PredictionType(Enum):
    """Types of predictions"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    RANKING = "ranking"
    PROBABILITY = "probability"
    MULTI_OUTPUT = "multi_output"


class ModelPerformance(Enum):
    """Model performance levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    DISABLED = "disabled"


@dataclass
class ModelPrediction:
    """Individual model prediction"""
    model_id: str
    model_version: str
    prediction: Any
    confidence: float
    latency: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnsemblePrediction:
    """Ensemble prediction result"""
    final_prediction: Any
    confidence: float
    contributing_models: List[str]
    aggregation_method: AggregationMethod
    individual_predictions: List[ModelPrediction]
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelWeight:
    """Model weight configuration"""
    model_id: str
    weight: float
    performance_score: float
    creator_specific_weight: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class PredictionAggregator:
    """Enterprise Prediction Aggregation System"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        
        # Model management
        self.model_weights: Dict[str, ModelWeight] = {}
        self.model_performance: Dict[str, ModelPerformance] = {}
        self.prediction_history: List[EnsemblePrediction] = []
        
        # Configuration
        self.default_aggregation = AggregationMethod(
            self.config.get('default_aggregation', 'weighted_average')
        )
        self.min_models_required = self.config.get('min_models_required', 2)
        self.max_models_per_ensemble = self.config.get('max_models_per_ensemble', 10)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.timeout_seconds = self.config.get('timeout_seconds', 30)
        
        # Creator-specific configurations
        self.creator_aggregation_methods: Dict[str, AggregationMethod] = {}
        self.creator_model_preferences: Dict[str, List[str]] = {}
        
        # Performance tracking
        self.aggregation_metrics = {
            'total_predictions': 0,
            'successful_aggregations': 0,
            'failed_aggregations': 0,
            'average_confidence': 0.0,
            'average_processing_time': 0.0,
            'model_usage_count': {}
        }
        
        # Thread pool for parallel predictions
        self.executor = ThreadPoolExecutor(max_workers=self.config.get('max_workers', 8))
        
        logger.info("🎯 Prediction Aggregator initialized")
    
    async def aggregate_predictions(
        self,
        model_predictions: List[ModelPrediction],
        aggregation_method: Optional[AggregationMethod] = None,
        creator_type: Optional[str] = None,
        prediction_type: PredictionType = PredictionType.CLASSIFICATION
    ) -> EnsemblePrediction:
        """Aggregate predictions from multiple models"""
        try:
            start_time = time.time()
            
            # Filter valid predictions
            valid_predictions = [
                pred for pred in model_predictions
                if self._is_valid_prediction(pred)
            ]
            
            if len(valid_predictions) < self.min_models_required:
                raise ValueError(f"Insufficient valid predictions: {len(valid_predictions)}")
            
            # Select aggregation method
            method = (aggregation_method or 
                     self.creator_aggregation_methods.get(creator_type) or 
                     self.default_aggregation)
            
            # Filter models by performance and creator preferences
            filtered_predictions = await self._filter_predictions(
                valid_predictions, creator_type
            )
            
            # Aggregate based on method
            if method == AggregationMethod.SIMPLE_AVERAGE:
                result = await self._simple_average(filtered_predictions, prediction_type)
            elif method == AggregationMethod.WEIGHTED_AVERAGE:
                result = await self._weighted_average(filtered_predictions, prediction_type)
            elif method == AggregationMethod.MAJORITY_VOTING:
                result = await self._majority_voting(filtered_predictions)
            elif method == AggregationMethod.CONFIDENCE_WEIGHTED:
                result = await self._confidence_weighted(filtered_predictions, prediction_type)
            elif method == AggregationMethod.RANK_FUSION:
                result = await self._rank_fusion(filtered_predictions)
            elif method == AggregationMethod.STACKING:
                result = await self._stacking_aggregation(filtered_predictions, prediction_type)
            elif method == AggregationMethod.DYNAMIC_SELECTION:
                result = await self._dynamic_selection(filtered_predictions, creator_type)
            elif method == AggregationMethod.CREATOR_SPECIFIC:
                result = await self._creator_specific_aggregation(
                    filtered_predictions, creator_type, prediction_type
                )
            else:
                result = await self._weighted_average(filtered_predictions, prediction_type)
            
            processing_time = time.time() - start_time
            
            # Create ensemble prediction
            ensemble_prediction = EnsemblePrediction(
                final_prediction=result['prediction'],
                confidence=result['confidence'],
                contributing_models=[pred.model_id for pred in filtered_predictions],
                aggregation_method=method,
                individual_predictions=filtered_predictions,
                processing_time=processing_time,
                metadata={
                    'creator_type': creator_type,
                    'prediction_type': prediction_type.value,
                    'models_used': len(filtered_predictions),
                    'aggregation_details': result.get('details', {})
                }
            )
            
            # Update metrics and history
            await self._update_metrics(ensemble_prediction)
            self.prediction_history.append(ensemble_prediction)
            
            # Keep only recent history
            if len(self.prediction_history) > 1000:
                self.prediction_history = self.prediction_history[-1000:]
            
            logger.info(f"✅ Aggregated predictions: {method.value} - Confidence: {result['confidence']:.3f}")
            return ensemble_prediction
            
        except Exception as e:
            logger.error(f"❌ Error aggregating predictions: {e}")
            self.aggregation_metrics['failed_aggregations'] += 1
            raise
    
    async def predict_ensemble(
        self,
        model_ids: List[str],
        input_data: Any,
        creator_type: Optional[str] = None,
        aggregation_method: Optional[AggregationMethod] = None,
        prediction_type: PredictionType = PredictionType.CLASSIFICATION
    ) -> EnsemblePrediction:
        """Get predictions from multiple models and aggregate"""
        try:
            # Get predictions from all models in parallel
            prediction_tasks = []
            
            for model_id in model_ids:
                if self._is_model_available(model_id):
                    task = asyncio.create_task(
                        self._get_model_prediction(model_id, input_data)
                    )
                    prediction_tasks.append(task)
            
            # Wait for all predictions with timeout
            try:
                predictions = await asyncio.wait_for(
                    asyncio.gather(*prediction_tasks, return_exceptions=True),
                    timeout=self.timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.warning("Prediction timeout - using partial results")
                predictions = [
                    task.result() if task.done() else None
                    for task in prediction_tasks
                ]
            
            # Filter successful predictions
            valid_predictions = [
                pred for pred in predictions
                if isinstance(pred, ModelPrediction)
            ]
            
            if not valid_predictions:
                raise ValueError("No valid predictions received")
            
            # Aggregate predictions
            return await self.aggregate_predictions(
                valid_predictions,
                aggregation_method,
                creator_type,
                prediction_type
            )
            
        except Exception as e:
            logger.error(f"❌ Error in ensemble prediction: {e}")
            raise
    
    async def update_model_weights(
        self,
        model_id: str,
        performance_score: float,
        weight: Optional[float] = None,
        creator_specific_weights: Optional[Dict[str, float]] = None
    ) -> bool:
        """Update model weights based on performance"""
        try:
            if weight is None:
                weight = self._calculate_weight_from_performance(performance_score)
            
            # Update or create model weight
            if model_id in self.model_weights:
                model_weight = self.model_weights[model_id]
                model_weight.weight = weight
                model_weight.performance_score = performance_score
                model_weight.last_updated = datetime.utcnow()
            else:
                model_weight = ModelWeight(
                    model_id=model_id,
                    weight=weight,
                    performance_score=performance_score
                )
                self.model_weights[model_id] = model_weight
            
            # Update creator-specific weights
            if creator_specific_weights:
                model_weight.creator_specific_weight.update(creator_specific_weights)
            
            # Update performance classification
            self.model_performance[model_id] = self._classify_performance(performance_score)
            
            logger.info(f"✅ Updated weights for model {model_id}: {weight:.3f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating model weights: {e}")
            return False
    
    async def configure_creator_preferences(
        self,
        creator_type: str,
        preferred_models: List[str],
        aggregation_method: AggregationMethod
    ) -> bool:
        """Configure creator-specific preferences"""
        try:
            self.creator_model_preferences[creator_type] = preferred_models
            self.creator_aggregation_methods[creator_type] = aggregation_method
            
            logger.info(f"✅ Configured preferences for {creator_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configuring creator preferences: {e}")
            return False
    
    async def _simple_average(
        self,
        predictions: List[ModelPrediction],
        prediction_type: PredictionType
    ) -> Dict[str, Any]:
        """Simple average aggregation"""
        try:
            if prediction_type == PredictionType.CLASSIFICATION:
                # For classification, average probabilities if available
                if isinstance(predictions[0].prediction, dict):
                    # Assume class probabilities
                    classes = set()
                    for pred in predictions:
                        classes.update(pred.prediction.keys())
                    
                    averaged_probs = {}
                    for cls in classes:
                        probs = [pred.prediction.get(cls, 0.0) for pred in predictions]
                        averaged_probs[cls] = mean(probs)
                    
                    final_prediction = max(averaged_probs, key=averaged_probs.get)
                    confidence = averaged_probs[final_prediction]
                else:
                    # Simple majority vote for discrete classes
                    class_votes = [pred.prediction for pred in predictions]
                    final_prediction = mode(class_votes)
                    confidence = class_votes.count(final_prediction) / len(class_votes)
            
            elif prediction_type == PredictionType.REGRESSION:
                values = [pred.prediction for pred in predictions]
                final_prediction = mean(values)
                # Confidence based on agreement (inverse of std dev)
                std_dev = np.std(values) if len(values) > 1 else 0
                confidence = max(0.1, 1.0 / (1.0 + std_dev))
            
            else:
                # Default behavior
                values = [pred.prediction for pred in predictions]
                final_prediction = mean(values) if all(isinstance(v, (int, float)) for v in values) else values[0]
                confidence = mean([pred.confidence for pred in predictions])
            
            return {
                'prediction': final_prediction,
                'confidence': confidence,
                'details': {'method': 'simple_average', 'num_models': len(predictions)}
            }
            
        except Exception as e:
            logger.error(f"❌ Error in simple average: {e}")
            raise
    
    async def _weighted_average(
        self,
        predictions: List[ModelPrediction],
        prediction_type: PredictionType
    ) -> Dict[str, Any]:
        """Weighted average based on model weights"""
        try:
            weights = []
            values = []
            
            for pred in predictions:
                model_weight = self.model_weights.get(pred.model_id)
                weight = model_weight.weight if model_weight else 1.0
                weights.append(weight)
                values.append(pred.prediction)
            
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            if prediction_type == PredictionType.CLASSIFICATION:
                if isinstance(predictions[0].prediction, dict):
                    # Weighted average of probabilities
                    classes = set()
                    for pred in predictions:
                        classes.update(pred.prediction.keys())
                    
                    weighted_probs = {}
                    for cls in classes:
                        weighted_sum = sum(
                            pred.prediction.get(cls, 0.0) * weight
                            for pred, weight in zip(predictions, normalized_weights)
                        )
                        weighted_probs[cls] = weighted_sum
                    
                    final_prediction = max(weighted_probs, key=weighted_probs.get)
                    confidence = weighted_probs[final_prediction]
                else:
                    # Weighted voting for discrete classes
                    class_weights = {}
                    for pred, weight in zip(predictions, normalized_weights):
                        class_weights[pred.prediction] = class_weights.get(pred.prediction, 0) + weight
                    
                    final_prediction = max(class_weights, key=class_weights.get)
                    confidence = class_weights[final_prediction]
            
            elif prediction_type == PredictionType.REGRESSION:
                final_prediction = sum(
                    val * weight for val, weight in zip(values, normalized_weights)
                )
                # Weighted confidence
                confidence = sum(
                    pred.confidence * weight
                    for pred, weight in zip(predictions, normalized_weights)
                )
            
            else:
                # Default weighted average
                if all(isinstance(v, (int, float)) for v in values):
                    final_prediction = sum(val * weight for val, weight in zip(values, normalized_weights))
                else:
                    final_prediction = values[0]  # Fallback
                
                confidence = sum(
                    pred.confidence * weight
                    for pred, weight in zip(predictions, normalized_weights)
                )
            
            return {
                'prediction': final_prediction,
                'confidence': confidence,
                'details': {
                    'method': 'weighted_average',
                    'weights': dict(zip([p.model_id for p in predictions], normalized_weights))
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in weighted average: {e}")
            raise
    
    async def _majority_voting(self, predictions: List[ModelPrediction]) -> Dict[str, Any]:
        """Majority voting aggregation"""
        try:
            votes = [pred.prediction for pred in predictions]
            vote_counts = {}
            
            for vote in votes:
                vote_counts[vote] = vote_counts.get(vote, 0) + 1
            
            final_prediction = max(vote_counts, key=vote_counts.get)
            confidence = vote_counts[final_prediction] / len(votes)
            
            return {
                'prediction': final_prediction,
                'confidence': confidence,
                'details': {
                    'method': 'majority_voting',
                    'vote_counts': vote_counts
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in majority voting: {e}")
            raise
    
    async def _confidence_weighted(
        self,
        predictions: List[ModelPrediction],
        prediction_type: PredictionType
    ) -> Dict[str, Any]:
        """Confidence-weighted aggregation"""
        try:
            weights = [pred.confidence for pred in predictions]
            return await self._weighted_average_with_weights(predictions, weights, prediction_type)
            
        except Exception as e:
            logger.error(f"❌ Error in confidence weighted: {e}")
            raise
    
    async def _rank_fusion(self, predictions: List[ModelPrediction]) -> Dict[str, Any]:
        """Rank fusion aggregation for ranking problems"""
        try:
            # Assume predictions are rankings/scores
            if not all(isinstance(pred.prediction, (list, dict)) for pred in predictions):
                raise ValueError("Rank fusion requires list or dict predictions")
            
            # Simple Borda count for now
            item_scores = {}
            
            for pred in predictions:
                if isinstance(pred.prediction, list):
                    # List of items in rank order
                    for i, item in enumerate(pred.prediction):
                        score = len(pred.prediction) - i
                        item_scores[item] = item_scores.get(item, 0) + score
                elif isinstance(pred.prediction, dict):
                    # Dict of item -> score
                    for item, score in pred.prediction.items():
                        item_scores[item] = item_scores.get(item, 0) + score
            
            # Sort by score
            ranked_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)
            final_prediction = [item for item, score in ranked_items]
            
            # Confidence based on agreement
            confidence = min(1.0, len(item_scores) / (len(predictions) * 10))  # Normalize
            
            return {
                'prediction': final_prediction,
                'confidence': confidence,
                'details': {
                    'method': 'rank_fusion',
                    'item_scores': item_scores
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in rank fusion: {e}")
            raise
    
    async def _stacking_aggregation(
        self,
        predictions: List[ModelPrediction],
        prediction_type: PredictionType
    ) -> Dict[str, Any]:
        """Stacking aggregation using a meta-learner"""
        try:
            # For now, implement as weighted average based on historical performance
            # In practice, this would use a trained meta-model
            
            performance_weights = []
            for pred in predictions:
                model_weight = self.model_weights.get(pred.model_id)
                if model_weight:
                    weight = model_weight.performance_score
                else:
                    weight = pred.confidence
                performance_weights.append(weight)
            
            return await self._weighted_average_with_weights(
                predictions, performance_weights, prediction_type
            )
            
        except Exception as e:
            logger.error(f"❌ Error in stacking aggregation: {e}")
            raise
    
    async def _dynamic_selection(
        self,
        predictions: List[ModelPrediction],
        creator_type: Optional[str]
    ) -> Dict[str, Any]:
        """Dynamic model selection based on context"""
        try:
            # Select best model based on creator type and recent performance
            best_model = None
            best_score = -1
            
            for pred in predictions:
                score = pred.confidence
                
                # Boost score for creator-specific preferences
                if creator_type and creator_type in self.creator_model_preferences:
                    if pred.model_id in self.creator_model_preferences[creator_type]:
                        score *= 1.2
                
                # Boost score for good performance models
                model_weight = self.model_weights.get(pred.model_id)
                if model_weight:
                    score *= model_weight.performance_score
                
                if score > best_score:
                    best_score = score
                    best_model = pred
            
            if best_model:
                return {
                    'prediction': best_model.prediction,
                    'confidence': best_model.confidence,
                    'details': {
                        'method': 'dynamic_selection',
                        'selected_model': best_model.model_id,
                        'selection_score': best_score
                    }
                }
            else:
                # Fallback to simple average
                return await self._simple_average(predictions, PredictionType.CLASSIFICATION)
                
        except Exception as e:
            logger.error(f"❌ Error in dynamic selection: {e}")
            raise
    
    async def _creator_specific_aggregation(
        self,
        predictions: List[ModelPrediction],
        creator_type: Optional[str],
        prediction_type: PredictionType
    ) -> Dict[str, Any]:
        """Creator-specific aggregation strategy"""
        try:
            if not creator_type:
                return await self._weighted_average(predictions, prediction_type)
            
            # Apply creator-specific weights
            creator_weights = []
            for pred in predictions:
                model_weight = self.model_weights.get(pred.model_id)
                if model_weight and creator_type in model_weight.creator_specific_weight:
                    weight = model_weight.creator_specific_weight[creator_type]
                else:
                    weight = model_weight.weight if model_weight else 1.0
                creator_weights.append(weight)
            
            return await self._weighted_average_with_weights(
                predictions, creator_weights, prediction_type
            )
            
        except Exception as e:
            logger.error(f"❌ Error in creator-specific aggregation: {e}")
            raise
    
    async def _weighted_average_with_weights(
        self,
        predictions: List[ModelPrediction],
        weights: List[float],
        prediction_type: PredictionType
    ) -> Dict[str, Any]:
        """Helper for weighted average with custom weights"""
        try:
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            # Create temporary model weights
            temp_weights = {}
            for pred, weight in zip(predictions, normalized_weights):
                temp_weights[pred.model_id] = ModelWeight(
                    model_id=pred.model_id,
                    weight=weight,
                    performance_score=1.0
                )
            
            # Store original weights
            original_weights = self.model_weights.copy()
            self.model_weights.update(temp_weights)
            
            try:
                result = await self._weighted_average(predictions, prediction_type)
                return result
            finally:
                # Restore original weights
                self.model_weights = original_weights
                
        except Exception as e:
            logger.error(f"❌ Error in weighted average with weights: {e}")
            raise
    
    async def _filter_predictions(
        self,
        predictions: List[ModelPrediction],
        creator_type: Optional[str]
    ) -> List[ModelPrediction]:
        """Filter predictions based on performance and preferences"""
        try:
            filtered = []
            
            for pred in predictions:
                # Check performance
                performance = self.model_performance.get(pred.model_id, ModelPerformance.AVERAGE)
                if performance == ModelPerformance.DISABLED:
                    continue
                
                # Check confidence threshold
                if pred.confidence < self.confidence_threshold:
                    continue
                
                filtered.append(pred)
            
            # Apply creator preferences if available
            if creator_type and creator_type in self.creator_model_preferences:
                preferred_models = self.creator_model_preferences[creator_type]
                preferred_predictions = [
                    pred for pred in filtered
                    if pred.model_id in preferred_models
                ]
                if len(preferred_predictions) >= self.min_models_required:
                    filtered = preferred_predictions
            
            # Limit to max models
            if len(filtered) > self.max_models_per_ensemble:
                # Sort by confidence and take top models
                filtered.sort(key=lambda p: p.confidence, reverse=True)
                filtered = filtered[:self.max_models_per_ensemble]
            
            return filtered
            
        except Exception as e:
            logger.error(f"❌ Error filtering predictions: {e}")
            return predictions
    
    def _is_valid_prediction(self, prediction: ModelPrediction) -> bool:
        """Check if prediction is valid"""
        try:
            return (
                prediction.prediction is not None and
                0.0 <= prediction.confidence <= 1.0 and
                prediction.latency >= 0
            )
        except:
            return False
    
    def _is_model_available(self, model_id: str) -> bool:
        """Check if model is available for prediction"""
        performance = self.model_performance.get(model_id, ModelPerformance.AVERAGE)
        return performance != ModelPerformance.DISABLED
    
    async def _get_model_prediction(
        self,
        model_id: str,
        input_data: Any
    ) -> ModelPrediction:
        """Get prediction from a single model"""
        try:
            start_time = time.time()
            
            # Simulate model prediction
            # In practice, this would call the actual model
            await asyncio.sleep(0.05)  # Simulate prediction time
            
            # Mock prediction based on model_id
            if "classifier" in model_id.lower():
                prediction = {"positive": 0.7, "negative": 0.3}
                confidence = 0.7
            elif "regression" in model_id.lower():
                prediction = 42.5
                confidence = 0.8
            else:
                prediction = "result"
                confidence = 0.6
            
            latency = time.time() - start_time
            
            return ModelPrediction(
                model_id=model_id,
                model_version="1.0.0",
                prediction=prediction,
                confidence=confidence,
                latency=latency
            )
            
        except Exception as e:
            logger.error(f"❌ Error getting prediction from {model_id}: {e}")
            raise
    
    def _calculate_weight_from_performance(self, performance_score: float) -> float:
        """Calculate model weight from performance score"""
        # Simple linear mapping
        return max(0.1, min(1.0, performance_score))
    
    def _classify_performance(self, performance_score: float) -> ModelPerformance:
        """Classify performance level"""
        if performance_score >= 0.9:
            return ModelPerformance.EXCELLENT
        elif performance_score >= 0.8:
            return ModelPerformance.GOOD
        elif performance_score >= 0.6:
            return ModelPerformance.AVERAGE
        elif performance_score >= 0.3:
            return ModelPerformance.POOR
        else:
            return ModelPerformance.DISABLED
    
    async def _update_metrics(self, ensemble_prediction -> None: EnsemblePrediction) -> None:
        """Update aggregation metrics"""
        try:
            self.aggregation_metrics['total_predictions'] += 1
            self.aggregation_metrics['successful_aggregations'] += 1
            
            # Update average confidence
            total = self.aggregation_metrics['total_predictions']
            current_avg = self.aggregation_metrics['average_confidence']
            new_avg = (current_avg * (total - 1) + ensemble_prediction.confidence) / total
            self.aggregation_metrics['average_confidence'] = new_avg
            
            # Update average processing time
            current_time_avg = self.aggregation_metrics['average_processing_time']
            new_time_avg = (current_time_avg * (total - 1) + ensemble_prediction.processing_time) / total
            self.aggregation_metrics['average_processing_time'] = new_time_avg
            
            # Update model usage counts
            for model_id in ensemble_prediction.contributing_models:
                count = self.aggregation_metrics['model_usage_count'].get(model_id, 0)
                self.aggregation_metrics['model_usage_count'][model_id] = count + 1
                
        except Exception as e:
            logger.error(f"❌ Error updating metrics: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get aggregation metrics"""
        return {
            **self.aggregation_metrics,
            'active_models': len(self.model_weights),
            'creator_configurations': len(self.creator_aggregation_methods),
            'prediction_history_size': len(self.prediction_history)
        }


# Global instance
prediction_aggregator = PredictionAggregator()


async def main() -> None:
    """Test the Prediction Aggregator"""
    aggregator = PredictionAggregator()
    
    print("🎯 Testing Prediction Aggregator...")
    
    # Configure model weights
    await aggregator.update_model_weights("model_a", 0.85, creator_specific_weights={"musician": 0.9})
    await aggregator.update_model_weights("model_b", 0.75)
    await aggregator.update_model_weights("model_c", 0.95)
    
    # Configure creator preferences
    await aggregator.configure_creator_preferences(
        "musician", ["model_a", "model_c"], AggregationMethod.CONFIDENCE_WEIGHTED
    )
    
    # Test ensemble prediction
    result = await aggregator.predict_ensemble(
        ["model_a", "model_b", "model_c"],
        {"content": "test music content"},
        creator_type="musician",
        prediction_type=PredictionType.CLASSIFICATION
    )
    
    print(f"Ensemble prediction: {result.final_prediction}")
    print(f"Confidence: {result.confidence:.3f}")
    print(f"Contributing models: {result.contributing_models}")
    print(f"Processing time: {result.processing_time:.3f}s")
    
    # Get metrics
    metrics = await aggregator.get_metrics()
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())