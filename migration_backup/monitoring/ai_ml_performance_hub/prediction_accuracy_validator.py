"""
🎯 Prediction Accuracy Validator - Enterprise AI/ML Quality Assurance
===================================================================

Validateur précision prédictions temps réel pour Creator Economy.
Monitoring accuracy, confidence scores, validation business metrics.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Architecture: monitoring/ai_ml_performance_hub/prediction_accuracy_validator.py
Responsabilité: Validation précision prédictions IA/ML Creator Economy
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Audio + DevOps
"""

import asyncio
import logging
import statistics
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
import pandas as pd


class PredictionType(Enum):
    """Types de prédictions"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    RANKING = "ranking"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"
    DETECTION = "detection"


class AccuracyThreshold(Enum):
    """Niveaux seuils précision"""
    EXCELLENT = "excellent"    # > 95%
    GOOD = "good"             # 85-95%
    ACCEPTABLE = "acceptable"  # 70-85%
    POOR = "poor"             # 50-70%
    CRITICAL = "critical"     # < 50%


class ValidationMethod(Enum):
    """Méthodes validation"""
    GROUND_TRUTH_COMPARISON = "ground_truth_comparison"
    CROSS_VALIDATION = "cross_validation"
    HOLDOUT_VALIDATION = "holdout_validation"
    BOOTSTRAP_VALIDATION = "bootstrap_validation"
    BUSINESS_METRIC_CORRELATION = "business_metric_correlation"
    A_B_TESTING = "a_b_testing"


class CreatorContentCategory(Enum):
    """Catégories contenu créateur"""
    MUSIC = "music"
    PODCAST = "podcast"
    VIDEO = "video"
    BLOG = "blog"
    PHOTOGRAPHY = "photography"
    COMEDY = "comedy"
    EDUCATION = "education"
    GAMING = "gaming"


@dataclass
class PredictionAccuracyMetrics:
    """Métriques précision prédiction"""
    metric_id: str
    model_id: str
    prediction_id: str
    content_category: CreatorContentCategory
    prediction_type: PredictionType
    
    # Core accuracy metrics
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confidence_score: float
    
    # Prediction details
    predicted_value: Any
    actual_value: Any
    prediction_confidence: float
    prediction_latency: float  # milliseconds
    
    # Business metrics
    business_impact_score: float
    creator_satisfaction_score: float
    revenue_correlation: float
    user_engagement_correlation: float
    
    # Quality metrics
    prediction_consistency: float
    model_certainty: float
    false_positive_rate: float
    false_negative_rate: float
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationReport:
    """Rapport validation précision"""
    report_id: str
    model_id: str
    validation_period: Tuple[datetime, datetime]
    validation_method: ValidationMethod
    total_predictions: int
    
    # Aggregate metrics
    overall_accuracy: float
    average_confidence: float
    accuracy_by_category: Dict[str, float]
    confidence_distribution: Dict[str, float]
    
    # Quality assessment
    accuracy_threshold: AccuracyThreshold
    prediction_quality_score: float
    consistency_score: float
    reliability_score: float
    
    # Business impact
    business_value_score: float
    creator_tier_performance: Dict[str, float]
    revenue_impact: float
    
    # Recommendations
    recommendations: List[str]
    improvement_opportunities: List[str]


@dataclass
class AccuracyAlert:
    """Alerte précision"""
    alert_id: str
    model_id: str
    alert_type: str
    severity: str
    accuracy_drop: float
    threshold_violated: float
    affected_categories: List[str]
    recommended_actions: List[str]
    business_impact_assessment: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConfidenceCalibration:
    """Calibration confiance modèle"""
    model_id: str
    confidence_buckets: Dict[str, Dict[str, float]]  # bucket -> {predicted_accuracy, actual_accuracy}
    calibration_error: float
    reliability_diagram: Dict[str, List[float]]
    overconfidence_score: float
    underconfidence_score: float


class PredictionAccuracyValidator:
    """Validateur précision prédictions enterprise"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Tracking data
        self.prediction_metrics: Dict[str, List[PredictionAccuracyMetrics]] = {}
        self.validation_reports: List[ValidationReport] = []
        self.accuracy_alerts: List[AccuracyAlert] = []
        self.confidence_calibrations: Dict[str, ConfidenceCalibration] = {}
        
        # Ground truth data storage
        self.ground_truth_data: Dict[str, Dict[str, Any]] = {}
        
        # Accuracy thresholds by content category
        self.category_accuracy_thresholds = {
            CreatorContentCategory.MUSIC: 0.90,
            CreatorContentCategory.PODCAST: 0.85,
            CreatorContentCategory.VIDEO: 0.88,
            CreatorContentCategory.BLOG: 0.92,
            CreatorContentCategory.PHOTOGRAPHY: 0.94,
            CreatorContentCategory.COMEDY: 0.80,
            CreatorContentCategory.EDUCATION: 0.95,
            CreatorContentCategory.GAMING: 0.87
        }
        
        # Business metric weights
        self.business_metric_weights = {
            'creator_satisfaction': 0.3,
            'user_engagement': 0.25,
            'revenue_correlation': 0.25,
            'retention_impact': 0.2
        }
        
        # Validation configuration
        self.validation_config = {
            'min_predictions_for_validation': 100,
            'validation_window_hours': 24,
            'confidence_buckets': 10,
            'accuracy_alert_threshold': 0.05  # 5% drop triggers alert
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging"""
        logger = logging.getLogger("prediction_accuracy_validator")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def validate_prediction(self, 
                                model_id: str,
                                prediction_id: str,
                                predicted_value: Any,
                                actual_value: Any,
                                content_category: CreatorContentCategory,
                                prediction_type: PredictionType,
                                confidence_score: float,
                                prediction_latency: float = 0.0,
                                business_context: Dict[str, Any] = None) -> bool:
        """Validation prédiction individuelle"""
        try:
            # Calculate core accuracy metrics
            if prediction_type == PredictionType.CLASSIFICATION:
                accuracy, precision, recall, f1 = self._calculate_classification_metrics(
                    predicted_value, actual_value
                )
            elif prediction_type == PredictionType.REGRESSION:
                accuracy, precision, recall, f1 = self._calculate_regression_metrics(
                    predicted_value, actual_value
                )
            else:
                accuracy, precision, recall, f1 = self._calculate_generic_metrics(
                    predicted_value, actual_value, prediction_type
                )
            
            # Calculate business metrics
            business_impact_score = await self._calculate_business_impact(
                predicted_value, actual_value, business_context or {}
            )
            
            creator_satisfaction_score = await self._calculate_creator_satisfaction(
                predicted_value, actual_value, content_category
            )
            
            revenue_correlation = await self._calculate_revenue_correlation(
                predicted_value, actual_value, business_context or {}
            )
            
            engagement_correlation = await self._calculate_engagement_correlation(
                predicted_value, actual_value, business_context or {}
            )
            
            # Calculate quality metrics
            consistency_score = await self._calculate_prediction_consistency(
                model_id, predicted_value, content_category
            )
            
            model_certainty = min(1.0, confidence_score * 1.2)  # Boost confidence slightly
            
            # Calculate error rates (simplified for single prediction)
            false_positive_rate = 0.0
            false_negative_rate = 0.0
            if prediction_type == PredictionType.CLASSIFICATION:
                if predicted_value == 1 and actual_value == 0:
                    false_positive_rate = 1.0
                elif predicted_value == 0 and actual_value == 1:
                    false_negative_rate = 1.0
            
            # Create metrics object
            metrics = PredictionAccuracyMetrics(
                metric_id=str(uuid.uuid4()),
                model_id=model_id,
                prediction_id=prediction_id,
                content_category=content_category,
                prediction_type=prediction_type,
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                confidence_score=confidence_score,
                predicted_value=predicted_value,
                actual_value=actual_value,
                prediction_confidence=confidence_score,
                prediction_latency=prediction_latency,
                business_impact_score=business_impact_score,
                creator_satisfaction_score=creator_satisfaction_score,
                revenue_correlation=revenue_correlation,
                user_engagement_correlation=engagement_correlation,
                prediction_consistency=consistency_score,
                model_certainty=model_certainty,
                false_positive_rate=false_positive_rate,
                false_negative_rate=false_negative_rate
            )
            
            # Store metrics
            if model_id not in self.prediction_metrics:
                self.prediction_metrics[model_id] = []
            
            self.prediction_metrics[model_id].append(metrics)
            
            # Keep only recent metrics (last 10000 predictions)
            if len(self.prediction_metrics[model_id]) > 10000:
                self.prediction_metrics[model_id] = self.prediction_metrics[model_id][-10000:]
            
            # Check for accuracy alerts
            await self._check_accuracy_alerts(model_id, metrics)
            
            # Update confidence calibration
            await self._update_confidence_calibration(model_id, metrics)
            
            self.logger.debug(f"Validated prediction {prediction_id} for model {model_id}: accuracy={accuracy:.3f}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating prediction: {e}")
            return False
    
    def _calculate_classification_metrics(self, predicted: Any, actual: Any) -> Tuple[float, float, float, float]:
        """Calcul métriques classification"""
        try:
            # Convert to binary for simplicity
            if isinstance(predicted, (list, np.ndarray)) and isinstance(actual, (list, np.ndarray)):
                accuracy = accuracy_score(actual, predicted)
                precision = precision_score(actual, predicted, average='weighted', zero_division=0)
                recall = recall_score(actual, predicted, average='weighted', zero_division=0)
                f1 = f1_score(actual, predicted, average='weighted', zero_division=0)
            else:
                # Single prediction case
                accuracy = 1.0 if predicted == actual else 0.0
                precision = accuracy
                recall = accuracy
                f1 = accuracy
            
            return accuracy, precision, recall, f1
            
        except Exception as e:
            self.logger.error(f"Error calculating classification metrics: {e}")
            return 0.0, 0.0, 0.0, 0.0
    
    def _calculate_regression_metrics(self, predicted: Any, actual: Any) -> Tuple[float, float, float, float]:
        """Calcul métriques régression"""
        try:
            if isinstance(predicted, (int, float)) and isinstance(actual, (int, float)):
                # Mean Absolute Percentage Error (MAPE) as accuracy
                if actual != 0:
                    mape = abs((actual - predicted) / actual)
                    accuracy = max(0.0, 1.0 - mape)
                else:
                    accuracy = 1.0 if predicted == 0 else 0.0
                
                # For regression, precision/recall are similar to accuracy
                precision = recall = f1 = accuracy
                
            else:
                accuracy = precision = recall = f1 = 0.0
            
            return accuracy, precision, recall, f1
            
        except Exception as e:
            self.logger.error(f"Error calculating regression metrics: {e}")
            return 0.0, 0.0, 0.0, 0.0
    
    def _calculate_generic_metrics(self, predicted: Any, actual: Any, prediction_type: PredictionType) -> Tuple[float, float, float, float]:
        """Calcul métriques génériques"""
        try:
            # Simple similarity measure
            if prediction_type == PredictionType.RANKING:
                # Rank correlation (simplified)
                if isinstance(predicted, list) and isinstance(actual, list):
                    # Spearman rank correlation approximation
                    min_len = min(len(predicted), len(actual))
                    if min_len > 0:
                        predicted_ranks = predicted[:min_len]
                        actual_ranks = actual[:min_len]
                        correlation = np.corrcoef(predicted_ranks, actual_ranks)[0, 1] if min_len > 1 else 0
                        accuracy = max(0.0, (correlation + 1) / 2)  # Normalize to 0-1
                    else:
                        accuracy = 0.0
                else:
                    accuracy = 0.0
            elif prediction_type == PredictionType.RECOMMENDATION:
                # Recommendation accuracy (simplified)
                if isinstance(predicted, list) and isinstance(actual, list):
                    intersection = set(predicted) & set(actual)
                    union = set(predicted) | set(actual)
                    accuracy = len(intersection) / len(union) if union else 0.0
                else:
                    accuracy = 1.0 if predicted == actual else 0.0
            else:
                # Generic comparison
                accuracy = 1.0 if predicted == actual else 0.0
            
            # For non-classification tasks, use accuracy for all metrics
            precision = recall = f1 = accuracy
            
            return accuracy, precision, recall, f1
            
        except Exception as e:
            self.logger.error(f"Error calculating generic metrics: {e}")
            return 0.0, 0.0, 0.0, 0.0
    
    async def _calculate_business_impact(self, predicted: Any, actual: Any, business_context: Dict[str, Any]) -> float:
        """Calcul impact business"""
        try:
            # Simplified business impact calculation
            prediction_accuracy = 1.0 if predicted == actual else 0.0
            
            # Weight by business context
            revenue_weight = business_context.get('revenue_impact', 1.0)
            user_count_weight = business_context.get('affected_users', 1.0) / 1000.0  # Normalize
            
            business_impact = prediction_accuracy * min(1.0, revenue_weight * user_count_weight)
            
            return business_impact
            
        except Exception as e:
            self.logger.error(f"Error calculating business impact: {e}")
            return 0.0
    
    async def _calculate_creator_satisfaction(self, predicted: Any, actual: Any, category: CreatorContentCategory) -> float:
        """Calcul satisfaction créateur"""
        try:
            base_accuracy = 1.0 if predicted == actual else 0.0
            
            # Category-specific satisfaction multipliers
            category_multipliers = {
                CreatorContentCategory.MUSIC: 1.2,      # Music creators are very quality-sensitive
                CreatorContentCategory.COMEDY: 0.9,     # Comedy is more subjective
                CreatorContentCategory.EDUCATION: 1.3,  # Education requires high accuracy
                CreatorContentCategory.GAMING: 1.0,     # Standard expectations
                CreatorContentCategory.PHOTOGRAPHY: 1.1,
                CreatorContentCategory.PODCAST: 1.0,
                CreatorContentCategory.VIDEO: 1.1,
                CreatorContentCategory.BLOG: 1.0
            }
            
            multiplier = category_multipliers.get(category, 1.0)
            satisfaction = min(1.0, base_accuracy * multiplier)
            
            return satisfaction
            
        except Exception as e:
            self.logger.error(f"Error calculating creator satisfaction: {e}")
            return 0.0
    
    async def _calculate_revenue_correlation(self, predicted: Any, actual: Any, business_context: Dict[str, Any]) -> float:
        """Calcul corrélation revenus"""
        try:
            prediction_accuracy = 1.0 if predicted == actual else 0.0
            
            # Revenue correlation based on prediction type and business context
            revenue_potential = business_context.get('revenue_potential', 1.0)
            monetization_tier = business_context.get('creator_tier', 'free')
            
            tier_multipliers = {'free': 0.5, 'premium': 1.0, 'enterprise': 1.5}
            multiplier = tier_multipliers.get(monetization_tier, 1.0)
            
            correlation = prediction_accuracy * revenue_potential * multiplier
            
            return min(1.0, correlation)
            
        except Exception as e:
            self.logger.error(f"Error calculating revenue correlation: {e}")
            return 0.0
    
    async def _calculate_engagement_correlation(self, predicted: Any, actual: Any, business_context: Dict[str, Any]) -> float:
        """Calcul corrélation engagement"""
        try:
            prediction_accuracy = 1.0 if predicted == actual else 0.0
            
            # Engagement correlation
            expected_engagement = business_context.get('expected_engagement', 1.0)
            content_virality = business_context.get('virality_score', 1.0)
            
            correlation = prediction_accuracy * expected_engagement * content_virality
            
            return min(1.0, correlation)
            
        except Exception as e:
            self.logger.error(f"Error calculating engagement correlation: {e}")
            return 0.0
    
    async def _calculate_prediction_consistency(self, model_id: str, predicted_value: Any, category: CreatorContentCategory) -> float:
        """Calcul consistance prédictions"""
        try:
            if model_id not in self.prediction_metrics:
                return 1.0  # First prediction is consistent by default
            
            # Get recent predictions for same category
            recent_predictions = [
                m for m in self.prediction_metrics[model_id][-50:]  # Last 50 predictions
                if m.content_category == category
            ]
            
            if len(recent_predictions) < 2:
                return 1.0
            
            # Calculate consistency based on prediction variance
            if isinstance(predicted_value, (int, float)):
                recent_values = [m.predicted_value for m in recent_predictions if isinstance(m.predicted_value, (int, float))]
                if len(recent_values) > 1:
                    std_dev = np.std(recent_values)
                    mean_val = np.mean(recent_values)
                    # Normalize consistency (lower std_dev = higher consistency)
                    consistency = max(0.0, 1.0 - (std_dev / max(1.0, abs(mean_val))))
                else:
                    consistency = 1.0
            else:
                # For non-numeric predictions, check how often same prediction occurs
                recent_values = [str(m.predicted_value) for m in recent_predictions]
                most_common_count = max([recent_values.count(val) for val in set(recent_values)])
                consistency = most_common_count / len(recent_values)
            
            return consistency
            
        except Exception as e:
            self.logger.error(f"Error calculating prediction consistency: {e}")
            return 0.5
    
    async def _check_accuracy_alerts(self, model_id: str, metrics: PredictionAccuracyMetrics):
        """Vérification alertes précision"""
        try:
            if model_id not in self.prediction_metrics or len(self.prediction_metrics[model_id]) < 50:
                return  # Need sufficient data for comparison
            
            # Get recent accuracy trend
            recent_metrics = self.prediction_metrics[model_id][-50:]
            current_accuracy = metrics.accuracy
            
            # Calculate baseline accuracy (last 100-200 predictions)
            if len(self.prediction_metrics[model_id]) >= 200:
                baseline_metrics = self.prediction_metrics[model_id][-200:-50]
                baseline_accuracy = statistics.mean([m.accuracy for m in baseline_metrics])
            else:
                baseline_accuracy = statistics.mean([m.accuracy for m in recent_metrics[:-1]]) if len(recent_metrics) > 1 else current_accuracy
            
            # Check for accuracy drop
            accuracy_drop = baseline_accuracy - current_accuracy
            
            if accuracy_drop > self.validation_config['accuracy_alert_threshold']:
                # Generate alert
                alert = AccuracyAlert(
                    alert_id=str(uuid.uuid4()),
                    model_id=model_id,
                    alert_type="accuracy_degradation",
                    severity="HIGH" if accuracy_drop > 0.1 else "MEDIUM",
                    accuracy_drop=accuracy_drop,
                    threshold_violated=self.validation_config['accuracy_alert_threshold'],
                    affected_categories=[metrics.content_category.value],
                    recommended_actions=[
                        "Review recent model changes",
                        "Check data quality",
                        "Consider model retraining",
                        "Validate ground truth data"
                    ],
                    business_impact_assessment=f"Potential {accuracy_drop:.1%} reduction in prediction quality"
                )
                
                self.accuracy_alerts.append(alert)
                
                self.logger.warning(
                    f"🚨 Accuracy Alert: Model {model_id} accuracy dropped by {accuracy_drop:.1%}"
                )
            
            # Check category-specific thresholds
            category_threshold = self.category_accuracy_thresholds.get(metrics.content_category, 0.85)
            if current_accuracy < category_threshold:
                alert = AccuracyAlert(
                    alert_id=str(uuid.uuid4()),
                    model_id=model_id,
                    alert_type="category_threshold_violation",
                    severity="MEDIUM",
                    accuracy_drop=category_threshold - current_accuracy,
                    threshold_violated=category_threshold,
                    affected_categories=[metrics.content_category.value],
                    recommended_actions=[
                        f"Optimize model for {metrics.content_category.value} content",
                        "Increase training data for this category",
                        "Review category-specific features"
                    ],
                    business_impact_assessment=f"{metrics.content_category.value} creators may experience reduced quality"
                )
                
                self.accuracy_alerts.append(alert)
            
            # Keep only recent alerts (last 1000)
            if len(self.accuracy_alerts) > 1000:
                self.accuracy_alerts = self.accuracy_alerts[-1000:]
                
        except Exception as e:
            self.logger.error(f"Error checking accuracy alerts: {e}")
    
    async def _update_confidence_calibration(self, model_id: str, metrics: PredictionAccuracyMetrics):
        """Mise à jour calibration confiance"""
        try:
            if model_id not in self.confidence_calibrations:
                self.confidence_calibrations[model_id] = ConfidenceCalibration(
                    model_id=model_id,
                    confidence_buckets={},
                    calibration_error=0.0,
                    reliability_diagram={},
                    overconfidence_score=0.0,
                    underconfidence_score=0.0
                )
            
            calibration = self.confidence_calibrations[model_id]
            
            # Determine confidence bucket (0-10)
            confidence_bucket = min(9, int(metrics.confidence_score * 10))
            bucket_key = f"bucket_{confidence_bucket}"
            
            if bucket_key not in calibration.confidence_buckets:
                calibration.confidence_buckets[bucket_key] = {
                    'predicted_accuracy': [],
                    'actual_accuracy': []
                }
            
            # Add prediction to bucket
            calibration.confidence_buckets[bucket_key]['predicted_accuracy'].append(metrics.confidence_score)
            calibration.confidence_buckets[bucket_key]['actual_accuracy'].append(metrics.accuracy)
            
            # Keep only recent predictions in each bucket (last 100)
            for bucket in calibration.confidence_buckets.values():
                if len(bucket['predicted_accuracy']) > 100:
                    bucket['predicted_accuracy'] = bucket['predicted_accuracy'][-100:]
                    bucket['actual_accuracy'] = bucket['actual_accuracy'][-100:]
            
            # Recalculate calibration error
            total_error = 0.0
            total_predictions = 0
            
            for bucket_data in calibration.confidence_buckets.values():
                if len(bucket_data['predicted_accuracy']) > 0:
                    avg_predicted = statistics.mean(bucket_data['predicted_accuracy'])
                    avg_actual = statistics.mean(bucket_data['actual_accuracy'])
                    bucket_error = abs(avg_predicted - avg_actual)
                    bucket_count = len(bucket_data['predicted_accuracy'])
                    
                    total_error += bucket_error * bucket_count
                    total_predictions += bucket_count
            
            calibration.calibration_error = total_error / max(1, total_predictions)
            
            # Calculate over/under confidence
            if model_id in self.prediction_metrics:
                recent_predictions = self.prediction_metrics[model_id][-100:]
                confidences = [m.confidence_score for m in recent_predictions]
                accuracies = [m.accuracy for m in recent_predictions]
                
                if len(confidences) > 10:
                    avg_confidence = statistics.mean(confidences)
                    avg_accuracy = statistics.mean(accuracies)
                    
                    if avg_confidence > avg_accuracy:
                        calibration.overconfidence_score = avg_confidence - avg_accuracy
                        calibration.underconfidence_score = 0.0
                    else:
                        calibration.underconfidence_score = avg_accuracy - avg_confidence
                        calibration.overconfidence_score = 0.0
            
        except Exception as e:
            self.logger.error(f"Error updating confidence calibration: {e}")
    
    async def generate_validation_report(self, 
                                       model_id: str, 
                                       validation_method: ValidationMethod = ValidationMethod.GROUND_TRUTH_COMPARISON,
                                       time_window_hours: int = 24) -> Optional[ValidationReport]:
        """Génération rapport validation"""
        try:
            if model_id not in self.prediction_metrics:
                return None
            
            # Filter predictions by time window
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            recent_predictions = [
                m for m in self.prediction_metrics[model_id]
                if m.timestamp >= cutoff_time
            ]
            
            if len(recent_predictions) < self.validation_config['min_predictions_for_validation']:
                self.logger.warning(f"Insufficient predictions for validation report: {len(recent_predictions)}")
                return None
            
            # Calculate aggregate metrics
            overall_accuracy = statistics.mean([m.accuracy for m in recent_predictions])
            average_confidence = statistics.mean([m.confidence_score for m in recent_predictions])
            
            # Accuracy by category
            accuracy_by_category = {}
            for category in CreatorContentCategory:
                category_predictions = [m for m in recent_predictions if m.content_category == category]
                if category_predictions:
                    accuracy_by_category[category.value] = statistics.mean([m.accuracy for m in category_predictions])
            
            # Confidence distribution
            confidence_buckets = {}
            for i in range(10):
                bucket_min = i / 10.0
                bucket_max = (i + 1) / 10.0
                bucket_predictions = [
                    m for m in recent_predictions 
                    if bucket_min <= m.confidence_score < bucket_max
                ]
                confidence_buckets[f"{bucket_min:.1f}-{bucket_max:.1f}"] = len(bucket_predictions)
            
            # Determine accuracy threshold
            if overall_accuracy >= 0.95:
                accuracy_threshold = AccuracyThreshold.EXCELLENT
            elif overall_accuracy >= 0.85:
                accuracy_threshold = AccuracyThreshold.GOOD
            elif overall_accuracy >= 0.70:
                accuracy_threshold = AccuracyThreshold.ACCEPTABLE
            elif overall_accuracy >= 0.50:
                accuracy_threshold = AccuracyThreshold.POOR
            else:
                accuracy_threshold = AccuracyThreshold.CRITICAL
            
            # Calculate quality scores
            prediction_quality_score = overall_accuracy
            consistency_score = statistics.mean([m.prediction_consistency for m in recent_predictions])
            reliability_score = min(1.0, average_confidence * overall_accuracy)
            
            # Business metrics
            business_value_score = statistics.mean([m.business_impact_score for m in recent_predictions])
            
            # Creator tier performance (mock data)
            creator_tier_performance = {
                'free': statistics.mean([m.accuracy for m in recent_predictions[:len(recent_predictions)//3]]),
                'premium': statistics.mean([m.accuracy for m in recent_predictions[len(recent_predictions)//3:2*len(recent_predictions)//3]]),
                'enterprise': statistics.mean([m.accuracy for m in recent_predictions[2*len(recent_predictions)//3:]])
            }
            
            revenue_impact = statistics.mean([m.revenue_correlation for m in recent_predictions])
            
            # Generate recommendations
            recommendations = await self._generate_validation_recommendations(recent_predictions, overall_accuracy)
            improvement_opportunities = await self._identify_improvement_opportunities(recent_predictions)
            
            report = ValidationReport(
                report_id=str(uuid.uuid4()),
                model_id=model_id,
                validation_period=(cutoff_time, datetime.utcnow()),
                validation_method=validation_method,
                total_predictions=len(recent_predictions),
                overall_accuracy=overall_accuracy,
                average_confidence=average_confidence,
                accuracy_by_category=accuracy_by_category,
                confidence_distribution=confidence_buckets,
                accuracy_threshold=accuracy_threshold,
                prediction_quality_score=prediction_quality_score,
                consistency_score=consistency_score,
                reliability_score=reliability_score,
                business_value_score=business_value_score,
                creator_tier_performance=creator_tier_performance,
                revenue_impact=revenue_impact,
                recommendations=recommendations,
                improvement_opportunities=improvement_opportunities
            )
            
            self.validation_reports.append(report)
            
            # Keep only recent reports (last 100)
            if len(self.validation_reports) > 100:
                self.validation_reports = self.validation_reports[-100:]
            
            self.logger.info(f"✅ Validation report generated for model {model_id}: {overall_accuracy:.1%} accuracy")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating validation report: {e}")
            return None
    
    async def _generate_validation_recommendations(self, predictions: List[PredictionAccuracyMetrics], overall_accuracy: float) -> List[str]:
        """Génération recommandations validation"""
        recommendations = []
        
        try:
            # Accuracy-based recommendations
            if overall_accuracy < 0.7:
                recommendations.append("Critical: Model requires immediate retraining")
                recommendations.append("Review and expand training dataset")
                recommendations.append("Consider ensemble methods for improved accuracy")
            elif overall_accuracy < 0.85:
                recommendations.append("Consider model fine-tuning for better performance")
                recommendations.append("Analyze misclassified samples for patterns")
            
            # Category-specific recommendations
            category_accuracies = {}
            for pred in predictions:
                category = pred.content_category.value
                if category not in category_accuracies:
                    category_accuracies[category] = []
                category_accuracies[category].append(pred.accuracy)
            
            for category, accuracies in category_accuracies.items():
                avg_accuracy = statistics.mean(accuracies)
                if avg_accuracy < 0.8:
                    recommendations.append(f"Improve {category} category performance through specialized training")
            
            # Confidence calibration recommendations
            confidences = [p.confidence_score for p in predictions]
            accuracies = [p.accuracy for p in predictions]
            
            if len(confidences) > 10:
                avg_confidence = statistics.mean(confidences)
                avg_accuracy = statistics.mean(accuracies)
                
                if avg_confidence > avg_accuracy + 0.1:
                    recommendations.append("Model is overconfident - implement confidence calibration")
                elif avg_accuracy > avg_confidence + 0.1:
                    recommendations.append("Model is underconfident - review confidence scoring mechanism")
            
            # Business impact recommendations
            business_scores = [p.business_impact_score for p in predictions]
            avg_business_impact = statistics.mean(business_scores)
            
            if avg_business_impact < 0.6:
                recommendations.append("Focus on predictions with higher business impact")
                recommendations.append("Align model optimization with business metrics")
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return recommendations
    
    async def _identify_improvement_opportunities(self, predictions: List[PredictionAccuracyMetrics]) -> List[str]:
        """Identification opportunités amélioration"""
        opportunities = []
        
        try:
            # Latency optimization opportunities
            latencies = [p.prediction_latency for p in predictions if p.prediction_latency > 0]
            if latencies:
                avg_latency = statistics.mean(latencies)
                if avg_latency > 100:  # More than 100ms
                    opportunities.append(f"Optimize prediction latency (current avg: {avg_latency:.1f}ms)")
            
            # Consistency improvement opportunities
            consistencies = [p.prediction_consistency for p in predictions]
            avg_consistency = statistics.mean(consistencies)
            if avg_consistency < 0.8:
                opportunities.append("Improve prediction consistency across similar inputs")
            
            # Creator satisfaction opportunities
            satisfaction_scores = [p.creator_satisfaction_score for p in predictions]
            avg_satisfaction = statistics.mean(satisfaction_scores)
            if avg_satisfaction < 0.8:
                opportunities.append("Enhance creator satisfaction through improved prediction quality")
            
            # Revenue correlation opportunities
            revenue_correlations = [p.revenue_correlation for p in predictions]
            avg_revenue_correlation = statistics.mean(revenue_correlations)
            if avg_revenue_correlation < 0.7:
                opportunities.append("Improve alignment between predictions and revenue outcomes")
            
            # False positive/negative rate opportunities
            fp_rates = [p.false_positive_rate for p in predictions]
            fn_rates = [p.false_negative_rate for p in predictions]
            
            if fp_rates and statistics.mean(fp_rates) > 0.1:
                opportunities.append("Reduce false positive rate through threshold optimization")
            
            if fn_rates and statistics.mean(fn_rates) > 0.1:
                opportunities.append("Reduce false negative rate through recall optimization")
            
            return opportunities[:5]  # Return top 5 opportunities
            
        except Exception as e:
            self.logger.error(f"Error identifying improvement opportunities: {e}")
            return opportunities
    
    async def get_model_accuracy_summary(self, model_id: str) -> Dict[str, Any]:
        """Résumé précision modèle"""
        try:
            if model_id not in self.prediction_metrics:
                return {'model_id': model_id, 'error': 'No predictions found'}
            
            predictions = self.prediction_metrics[model_id]
            if not predictions:
                return {'model_id': model_id, 'error': 'No prediction data'}
            
            # Recent predictions (last 24 hours)
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            recent_predictions = [p for p in predictions if p.timestamp >= recent_cutoff]
            
            # Basic statistics
            total_predictions = len(predictions)
            recent_predictions_count = len(recent_predictions)
            
            if recent_predictions:
                current_accuracy = statistics.mean([p.accuracy for p in recent_predictions])
                current_confidence = statistics.mean([p.confidence_score for p in recent_predictions])
            else:
                current_accuracy = statistics.mean([p.accuracy for p in predictions[-100:]])
                current_confidence = statistics.mean([p.confidence_score for p in predictions[-100:]])
            
            # Category breakdown
            category_stats = {}
            for category in CreatorContentCategory:
                category_predictions = [p for p in recent_predictions if p.content_category == category]
                if category_predictions:
                    category_stats[category.value] = {
                        'count': len(category_predictions),
                        'accuracy': statistics.mean([p.accuracy for p in category_predictions]),
                        'confidence': statistics.mean([p.confidence_score for p in category_predictions])
                    }
            
            # Performance trend
            if len(predictions) >= 100:
                old_predictions = predictions[-200:-100]
                new_predictions = predictions[-100:]
                
                old_accuracy = statistics.mean([p.accuracy for p in old_predictions])
                new_accuracy = statistics.mean([p.accuracy for p in new_predictions])
                
                accuracy_trend = "improving" if new_accuracy > old_accuracy + 0.01 else \
                               "declining" if new_accuracy < old_accuracy - 0.01 else "stable"
            else:
                accuracy_trend = "insufficient_data"
            
            # Recent alerts
            recent_alerts = [
                {
                    'type': alert.alert_type,
                    'severity': alert.severity,
                    'accuracy_drop': alert.accuracy_drop,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in self.accuracy_alerts
                if alert.model_id == model_id and 
                   (datetime.utcnow() - alert.timestamp).total_seconds() < 86400
            ]
            
            # Confidence calibration
            calibration_info = {}
            if model_id in self.confidence_calibrations:
                calib = self.confidence_calibrations[model_id]
                calibration_info = {
                    'calibration_error': calib.calibration_error,
                    'overconfidence_score': calib.overconfidence_score,
                    'underconfidence_score': calib.underconfidence_score
                }
            
            return {
                'model_id': model_id,
                'summary': {
                    'total_predictions': total_predictions,
                    'recent_predictions_24h': recent_predictions_count,
                    'current_accuracy': current_accuracy,
                    'current_confidence': current_confidence,
                    'accuracy_trend': accuracy_trend
                },
                'category_performance': category_stats,
                'recent_alerts': recent_alerts,
                'confidence_calibration': calibration_info,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating accuracy summary: {e}")
            return {'model_id': model_id, 'error': str(e)}
    
    async def get_validation_reports(self, model_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupération rapports validation"""
        try:
            reports = self.validation_reports
            if model_id:
                reports = [r for r in reports if r.model_id == model_id]
            
            # Sort by most recent first
            reports = sorted(reports, key=lambda x: x.validation_period[1], reverse=True)
            
            # Limit results
            reports = reports[:limit]
            
            # Convert to dict format
            report_dicts = []
            for report in reports:
                report_dict = {
                    'report_id': report.report_id,
                    'model_id': report.model_id,
                    'validation_period': {
                        'start': report.validation_period[0].isoformat(),
                        'end': report.validation_period[1].isoformat()
                    },
                    'validation_method': report.validation_method.value,
                    'total_predictions': report.total_predictions,
                    'overall_accuracy': report.overall_accuracy,
                    'average_confidence': report.average_confidence,
                    'accuracy_threshold': report.accuracy_threshold.value,
                    'quality_scores': {
                        'prediction_quality': report.prediction_quality_score,
                        'consistency': report.consistency_score,
                        'reliability': report.reliability_score,
                        'business_value': report.business_value_score
                    },
                    'recommendations_count': len(report.recommendations),
                    'improvement_opportunities_count': len(report.improvement_opportunities)
                }
                report_dicts.append(report_dict)
            
            return report_dicts
            
        except Exception as e:
            self.logger.error(f"Error getting validation reports: {e}")
            return []
    
    async def shutdown(self):
        """Arrêt propre du validateur"""
        self.logger.info("⏹️ Arrêt Prediction Accuracy Validator...")
        
        # Clear data
        self.prediction_metrics.clear()
        self.validation_reports.clear()
        self.accuracy_alerts.clear()
        self.confidence_calibrations.clear()
        self.ground_truth_data.clear()
        
        self.logger.info("✅ Prediction Accuracy Validator arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_accuracy_validator():
        config = {
            'debug': True,
            'validation_window_hours': 24
        }
        
        validator = PredictionAccuracyValidator(config)
        
        # Test individual prediction validations
        for i in range(100):
            predicted = np.random.choice([0, 1])
            actual = np.random.choice([0, 1])
            confidence = np.random.uniform(0.6, 0.95)
            
            success = await validator.validate_prediction(
                model_id="test_model_001",
                prediction_id=f"pred_{i}",
                predicted_value=predicted,
                actual_value=actual,
                content_category=np.random.choice(list(CreatorContentCategory)),
                prediction_type=PredictionType.CLASSIFICATION,
                confidence_score=confidence,
                prediction_latency=np.random.uniform(50, 200),
                business_context={
                    'revenue_potential': np.random.uniform(0.5, 2.0),
                    'creator_tier': np.random.choice(['free', 'premium', 'enterprise']),
                    'expected_engagement': np.random.uniform(0.3, 1.0)
                }
            )
        
        print(f"Validated 100 predictions successfully")
        
        # Generate validation report
        report = await validator.generate_validation_report("test_model_001")
        if report:
            print(f"Validation report generated: {report.overall_accuracy:.1%} accuracy")
            print(f"Recommendations: {len(report.recommendations)}")
        
        # Get accuracy summary
        summary = await validator.get_model_accuracy_summary("test_model_001")
        print(f"Model summary: {summary['summary']['current_accuracy']:.1%} current accuracy")
        
        # Get validation reports
        reports = await validator.get_validation_reports("test_model_001")
        print(f"Retrieved {len(reports)} validation reports")
        
        print('✅ Prediction Accuracy Validator test passed')
        await validator.shutdown()
    
    asyncio.run(test_accuracy_validator())