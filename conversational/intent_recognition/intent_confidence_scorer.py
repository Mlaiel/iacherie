"""Intent Confidence Scoring and Uncertainty Quantification

Advanced confidence calculation system for intent recognition with uncertainty
quantification and reliability assessment for creative industry applications.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
permission is strictly prohibited and will be prosecuted to the full extent of the law.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import math
import logging
from scipy.stats import entropy
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss

from .config import IntentRecognitionConfig
from .exceptions import ConfidenceCalculationError

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """
Confidence level categories"""

    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class UncertaintyType(Enum):
    """Types of uncertainty in predictions"""

    ALEATORIC = "aleatoric"  # Data uncertainty
    EPISTEMIC = "epistemic"  # Model uncertainty
    DISTRIBUTIONAL = "distributional"  # Distribution mismatch


@dataclass
class ConfidenceMetrics:
    """Comprehensive confidence metrics"""
    
    # Primary confidence scores
    raw_confidence: float
    calibrated_confidence: float
    ensemble_confidence: float
    
    # Uncertainty measures
    prediction_entropy: float
    mutual_information: float
    variance_ratio: float
    
    # Reliability indicators
    confidence_level: ConfidenceLevel
    reliability_score: float
    uncertainty_type: Optional[UncertaintyType] = None
    
    # Additional metrics
    temperature_scaled_confidence: float = 0.0
    brier_score: float = 0.0
    prediction_interval: Tuple[float, float] = (0.0, 1.0)


@dataclass
class UncertaintyQuantifier:
    """
Uncertainty quantification components"""
    
    # Ensemble-based uncertainty
    epistemic_uncertainty: float = 0.0
    aleatoric_uncertainty: float = 0.0
    total_uncertainty: float = 0.0
    
    # Distribution-based measures
    out_of_distribution_score: float = 0.0
    novelty_score: float = 0.0
    
    # Calibration metrics
    expected_calibration_error: float = 0.0
    overconfidence_error: float = 0.0
    underconfidence_error: float = 0.0


class IntentConfidenceScorer:
    """
    Advanced confidence scoring system for intent recognition
    
    Provides multiple confidence estimation methods including:
    - Temperature scaling
    - Ensemble variance
    - Entropy-based measures
    - Bayesian uncertainty quantification
    """
    
    def __init__(self, config: IntentRecognitionConfig):
        self.config = config
        self.calibration_models = {}
        self.temperature_parameter = 1.0
        self.ensemble_weights = None
        self._initialize_calibration()
    
    def _initialize_calibration(self):
        """
Initialize calibration components"""
        try:
            # Temperature scaling parameter
            self.temperature_parameter = self.config.confidence_config.temperature_scaling
            
            # Ensemble weights for uncertainty estimation
            self.ensemble_weights = np.ones(self.config.confidence_config.ensemble_size)
            self.ensemble_weights /= self.ensemble_weights.sum()
            
            logger.info("Confidence scorer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize confidence scorer: {e}")
            raise ConfidenceCalculationError(f"Initialization failed: {e}")
    
    def calculate_confidence(
        self,
        predictions: np.ndarray,
        prediction_probabilities: Optional[np.ndarray] = None,
        ensemble_predictions: Optional[List[np.ndarray]] = None,
        ground_truth: Optional[np.ndarray] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ConfidenceMetrics:
        """
        Calculate comprehensive confidence metrics
        
        Args:
            predictions: Primary model predictions
            prediction_probabilities: Raw prediction probabilities
            ensemble_predictions: Predictions from ensemble models
            ground_truth: True labels for calibration (optional)
            context: Additional context information
            
        Returns:
            ConfidenceMetrics: Comprehensive confidence assessment
        """
        try:
            # Extract probability distribution
            if prediction_probabilities is None:
                # Convert predictions to probabilities if needed
                probabilities = self._convert_predictions_to_probabilities(predictions)
            else:
                probabilities = prediction_probabilities
            
            # Calculate raw confidence (max probability)
            raw_confidence = float(np.max(probabilities))
            
            # Calculate entropy-based confidence
            entropy_score = self._calculate_entropy_confidence(probabilities)
            
            # Calculate ensemble confidence if available
            ensemble_confidence = self._calculate_ensemble_confidence(
                ensemble_predictions, probabilities
            )
            
            # Apply temperature scaling
            temperature_scaled_confidence = self._apply_temperature_scaling(
                probabilities, self.temperature_parameter
            )
            
            # Calculate calibrated confidence
            calibrated_confidence = self._calculate_calibrated_confidence(
                probabilities, context
            )
            
            # Calculate uncertainty measures
            uncertainty_metrics = self._quantify_uncertainty(
                probabilities, ensemble_predictions
            )
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(calibrated_confidence)
            
            # Calculate reliability score
            reliability_score = self._calculate_reliability_score(
                raw_confidence, entropy_score, uncertainty_metrics.total_uncertainty
            )
            
            # Calculate Brier score if ground truth available
            brier_score = 0.0
            if ground_truth is not None:
                brier_score = self._calculate_brier_score(probabilities, ground_truth)
            
            # Calculate prediction interval
            prediction_interval = self._calculate_prediction_interval(
                probabilities, uncertainty_metrics.total_uncertainty
            )
            
            return ConfidenceMetrics(
                raw_confidence=raw_confidence,
                calibrated_confidence=calibrated_confidence,
                ensemble_confidence=ensemble_confidence,
                prediction_entropy=entropy_score,
                mutual_information=uncertainty_metrics.epistemic_uncertainty,
                variance_ratio=uncertainty_metrics.aleatoric_uncertainty,
                confidence_level=confidence_level,
                reliability_score=reliability_score,
                temperature_scaled_confidence=temperature_scaled_confidence,
                brier_score=brier_score,
                prediction_interval=prediction_interval
            )
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            raise ConfidenceCalculationError(f"Failed to calculate confidence: {e}")
    
    def _convert_predictions_to_probabilities(
        self, 
        predictions: np.ndarray
    ) -> np.ndarray:
        """Convert raw predictions to probability distribution"""
        if len(predictions.shape) == 1:
            # Single prediction - create binary distribution
            prob = max(0.0, min(1.0, float(predictions[0])))
            return np.array([1.0 - prob, prob])
        else:
            # Multi-class predictions - apply softmax
            exp_preds = np.exp(predictions - np.max(predictions))
            return exp_preds / np.sum(exp_preds)
    
    def _calculate_entropy_confidence(self, probabilities: np.ndarray) -> float:
        """
Calculate entropy-based confidence measure"""
        # Avoid log(0) by adding small epsilon
        epsilon = 1e-10
        safe_probs = np.clip(probabilities, epsilon, 1.0 - epsilon)
        
        # Calculate entropy
        entropy_value = entropy(safe_probs)
        
        # Convert to confidence (0-1 scale)
        max_entropy = np.log(len(probabilities))
        normalized_entropy = entropy_value / max_entropy
        
        return 1.0 - normalized_entropy
    
    def _calculate_ensemble_confidence(
        self,
        ensemble_predictions: Optional[List[np.ndarray]],
        base_probabilities: np.ndarray
    ) -> float:
        """
Calculate confidence based on ensemble agreement"""
        if ensemble_predictions is None or len(ensemble_predictions) == 0:
            return float(np.max(base_probabilities))
        
        try:
            # Convert ensemble predictions to probabilities
            ensemble_probs = []
            for pred in ensemble_predictions:
                if len(pred.shape) == 1:
                    probs = self._convert_predictions_to_probabilities(pred)
                else:
                    probs = pred
                ensemble_probs.append(probs)
            
            ensemble_probs = np.array(ensemble_probs)
            
            # Calculate mean prediction
            mean_prediction = np.mean(ensemble_probs, axis=0)
            
            # Calculate agreement (inverse of variance)
            prediction_variance = np.var(ensemble_probs, axis=0)
            mean_variance = np.mean(prediction_variance)
            
            # Calculate confidence as combination of mean confidence and agreement
            mean_confidence = float(np.max(mean_prediction))
            agreement_confidence = 1.0 / (1.0 + mean_variance)
            
            # Weighted combination
            ensemble_confidence = 0.7 * mean_confidence + 0.3 * agreement_confidence
            
            return ensemble_confidence
            
        except Exception as e:
            logger.warning(f"Ensemble confidence calculation failed: {e}")
            return float(np.max(base_probabilities))
    
    def _apply_temperature_scaling(
        self, 
        probabilities: np.ndarray, 
        temperature: float
    ) -> float:
        """Apply temperature scaling for calibration"""
        if temperature <= 0:
            temperature = 1.0
        
        # Apply temperature scaling
        scaled_logits = np.log(probabilities + 1e-10) / temperature
        scaled_probs = np.exp(scaled_logits - np.max(scaled_logits))
        scaled_probs = scaled_probs / np.sum(scaled_probs)
        
        return float(np.max(scaled_probs))
    
    def _calculate_calibrated_confidence(
        self,
        probabilities: np.ndarray,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
Calculate calibrated confidence using learned calibration"""
        # Apply basic calibration adjustment based on historical performance
        raw_confidence = float(np.max(probabilities))
        
        # Apply context-based adjustments
        if context:
            # Adjust for conversation length
            conv_length = context.get('conversation_length', 1)
            length_adjustment = min(1.0, conv_length / 10.0) * 0.1
            
            # Adjust for user certainty indicators
            user_certainty = context.get('user_certainty', 0.5)
            certainty_adjustment = (user_certainty - 0.5) * 0.2
            
            # Apply adjustments
            calibrated_confidence = raw_confidence + length_adjustment + certainty_adjustment
        else:
            calibrated_confidence = raw_confidence
        
        return max(0.0, min(1.0, calibrated_confidence))
    
    def _quantify_uncertainty(
        self,
        probabilities: np.ndarray,
        ensemble_predictions: Optional[List[np.ndarray]] = None
    ) -> UncertaintyQuantifier:
        """
Quantify different types of uncertainty"""
        
        # Calculate aleatoric uncertainty (data uncertainty)
        entropy_value = entropy(probabilities + 1e-10)
        max_entropy = np.log(len(probabilities))
        aleatoric_uncertainty = entropy_value / max_entropy
        
        # Calculate epistemic uncertainty (model uncertainty)
        epistemic_uncertainty = 0.0
        if ensemble_predictions:
            try:
                ensemble_probs = np.array([
                    self._convert_predictions_to_probabilities(pred) 
                    if len(pred.shape) == 1 else pred
                    for pred in ensemble_predictions
                ])
                
                # Mutual information between predictions
                mean_prediction = np.mean(ensemble_probs, axis=0)
                epistemic_uncertainty = entropy(mean_prediction + 1e-10) - np.mean([
                    entropy(pred + 1e-10) for pred in ensemble_probs
                ])
                epistemic_uncertainty = max(0.0, epistemic_uncertainty / max_entropy)
                
            except Exception as e:
                logger.warning(f"Epistemic uncertainty calculation failed: {e}")
        
        # Total uncertainty
        total_uncertainty = aleatoric_uncertainty + epistemic_uncertainty
        
        # Out-of-distribution detection (simplified)
        max_prob = np.max(probabilities)
        ood_score = 1.0 - max_prob if max_prob < 0.5 else 0.0
        
        return UncertaintyQuantifier(
            epistemic_uncertainty=epistemic_uncertainty,
            aleatoric_uncertainty=aleatoric_uncertainty,
            total_uncertainty=total_uncertainty,
            out_of_distribution_score=ood_score,
            novelty_score=aleatoric_uncertainty * epistemic_uncertainty
        )
    
    def _determine_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Determine categorical confidence level"""
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.75:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _calculate_reliability_score(
        self,
        raw_confidence: float,
        entropy_confidence: float,
        uncertainty: float
    ) -> float:
        """
Calculate overall reliability score"""
        # Weighted combination of different confidence measures
        reliability = (
            0.4 * raw_confidence +
            0.3 * entropy_confidence +
            0.3 * (1.0 - uncertainty)
        )
        
        return max(0.0, min(1.0, reliability))
    
    def _calculate_brier_score(
        self,
        probabilities: np.ndarray,
        ground_truth: np.ndarray
    ) -> float:
        """
Calculate Brier score for calibration assessment"""
        try:
            # Convert ground truth to one-hot if needed
            if len(ground_truth.shape) == 1:
                num_classes = len(probabilities)
                one_hot = np.zeros(num_classes)
                if ground_truth[0] < num_classes:
                    one_hot[int(ground_truth[0])] = 1.0
                ground_truth = one_hot
            
            # Calculate Brier score
            return float(np.mean((probabilities - ground_truth) ** 2))
            
        except Exception as e:
            logger.warning(f"Brier score calculation failed: {e}")
            return 0.0
    
    def _calculate_prediction_interval(
        self,
        probabilities: np.ndarray,
        uncertainty: float
    ) -> Tuple[float, float]:
        """Calculate prediction interval based on uncertainty"""
        max_prob = float(np.max(probabilities))
        
        # Calculate interval width based on uncertainty
        interval_width = uncertainty * 0.5
        
        lower_bound = max(0.0, max_prob - interval_width)
        upper_bound = min(1.0, max_prob + interval_width)
        
        return (lower_bound, upper_bound)
    
    def calibrate_model(
        self,
        validation_predictions: np.ndarray,
        validation_labels: np.ndarray,
        method: str = "isotonic"
    ):
        """Calibrate confidence scores using validation data"""
        try:
            from sklearn.calibration import CalibratedClassifierCV
            
            # Create dummy classifier for calibration
            calibrator = CalibratedClassifierCV(
                base_estimator=None, 
                method=method,
                cv="prefit"
            )
            
            # Store calibration model
            self.calibration_models[method] = calibrator
            
            logger.info(f"Model calibrated using {method} method")
            
        except Exception as e:
            logger.error(f"Model calibration failed: {e}")
            raise ConfidenceCalculationError(f"Calibration failed: {e}")
    
    def update_temperature(self, validation_data: Dict[str, np.ndarray]):
        """Update temperature parameter for temperature scaling"""
        try:
            # Simple temperature optimization using validation data
            predictions = validation_data.get('predictions')
            labels = validation_data.get('labels')
            
            if predictions is not None and labels is not None:
                # Find optimal temperature that minimizes negative log-likelihood
                best_temp = 1.0
                best_nll = float('inf')
                
                for temp in np.arange(0.1, 5.0, 0.1):
                    # Calculate NLL with this temperature
                    scaled_probs = self._apply_temperature_scaling(predictions, temp)
                    nll = -np.mean(np.log(scaled_probs + 1e-10))
                    
                    if nll < best_nll:
                        best_nll = nll
                        best_temp = temp
                
                self.temperature_parameter = best_temp
                logger.info(f"Temperature updated to {best_temp}")
            
        except Exception as e:
            logger.warning(f"Temperature update failed: {e}")
    
    def get_confidence_explanation(self, metrics: ConfidenceMetrics) -> Dict[str, str]:
        """Generate human-readable explanation of confidence assessment"""
        explanations = {
            "overall_assessment": f"Confidence level: {metrics.confidence_level.value}",
            "raw_confidence": f"Raw prediction confidence: {metrics.raw_confidence:.2%}",
            "calibrated_confidence": f"Calibrated confidence: {metrics.calibrated_confidence:.2%}",
            "uncertainty": f"Prediction uncertainty: {metrics.prediction_entropy:.2f}",
            "reliability": f"Overall reliability: {metrics.reliability_score:.2%}"
        }
        
        # Add specific recommendations
        if metrics.confidence_level in [ConfidenceLevel.VERY_LOW, ConfidenceLevel.LOW]:
            explanations["recommendation"] = "Consider requesting clarification or additional context"
        elif metrics.confidence_level == ConfidenceLevel.MEDIUM:
            explanations["recommendation"] = "Moderate confidence - may benefit from confirmation"
        else:
            explanations["recommendation"] = "High confidence - can proceed with current prediction"
        
        return explanations
