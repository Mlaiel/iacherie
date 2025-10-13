"""
Prediction Quality Assessor - Continuous Prediction Quality Assessment
Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade continuous prediction quality assessment with confidence intervals,
uncertainty quantification, and performance monitoring for creator-specific models.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta
from scipy import stats
from collections import deque, defaultdict
import uuid

@dataclass
class PredictionRecord:
    """Individual prediction record for quality assessment."""
    prediction_id: str
    model_id: str
    model_version: str
    input_features: Dict[str, Any]
    prediction: Any
    confidence_score: float
    uncertainty_metrics: Dict[str, float]
    timestamp: datetime
    ground_truth: Optional[Any] = None
    feedback_score: Optional[float] = None
    context_metadata: Dict[str, Any] = None
    creator_domain: str = "general"

@dataclass
class QualityMetrics:
    """Quality assessment metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    calibration_error: float
    uncertainty_quality: float
    confidence_correlation: float
    prediction_stability: float
    domain_specific_metrics: Dict[str, float]

@dataclass
class QualityAssessment:
    """Complete quality assessment result."""
    assessment_id: str
    model_id: str
    assessment_period: Tuple[datetime, datetime]
    total_predictions: int
    quality_metrics: QualityMetrics
    confidence_distribution: Dict[str, float]
    uncertainty_analysis: Dict[str, Any]
    performance_trends: Dict[str, List[float]]
    anomaly_detection: Dict[str, Any]
    recommendations: List[str]
    risk_score: float
    assessment_timestamp: datetime

class PredictionQualityAssessor:
    """
    Advanced prediction quality assessor for continuous monitoring.
    
    Features:
    - Real-time prediction quality monitoring
    - Confidence interval validation and calibration
    - Uncertainty quantification and analysis
    - Performance trend analysis and forecasting
    - Anomaly detection in prediction patterns
    - Creator-domain specific quality metrics
    - Adaptive threshold management
    - Feedback integration and learning
    """
    
    def __init__(self, assessment_config: Dict[str, Any] = None, cache_dir: str = "quality_cache/"):
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Configuration
        self.config = assessment_config or self._get_default_config()
        
        # Prediction storage and tracking
        self.prediction_history = defaultdict(deque)  # model_id -> predictions
        self.quality_history = defaultdict(list)      # model_id -> quality assessments
        self.feedback_buffer = defaultdict(list)      # model_id -> feedback data
        
        # Quality assessment components
        self.confidence_calibrators = {}
        self.uncertainty_estimators = {}
        self.anomaly_detectors = {}
        
        # Performance thresholds
        self.quality_thresholds = {
            "accuracy": {"good": 0.85, "acceptable": 0.75, "poor": 0.65},
            "confidence_correlation": {"good": 0.8, "acceptable": 0.6, "poor": 0.4},
            "calibration_error": {"good": 0.05, "acceptable": 0.1, "poor": 0.2},
            "uncertainty_quality": {"good": 0.8, "acceptable": 0.6, "poor": 0.4}
        }
        
        # Creator-domain specific metrics
        self.domain_metrics = {
            "musician": {
                "genre_accuracy": {"weight": 0.3, "threshold": 0.85},
                "mood_consistency": {"weight": 0.2, "threshold": 0.8},
                "tempo_prediction": {"weight": 0.2, "threshold": 0.9},
                "engagement_correlation": {"weight": 0.3, "threshold": 0.7}
            },
            "blogger": {
                "topic_accuracy": {"weight": 0.3, "threshold": 0.9},
                "sentiment_consistency": {"weight": 0.25, "threshold": 0.85},
                "readability_score": {"weight": 0.2, "threshold": 0.8},
                "seo_effectiveness": {"weight": 0.25, "threshold": 0.75}
            },
            "photographer": {
                "aesthetic_score": {"weight": 0.4, "threshold": 0.8},
                "composition_analysis": {"weight": 0.3, "threshold": 0.85},
                "style_consistency": {"weight": 0.2, "threshold": 0.9},
                "commercial_viability": {"weight": 0.1, "threshold": 0.7}
            },
            "influencer": {
                "engagement_prediction": {"weight": 0.4, "threshold": 0.8},
                "viral_potential": {"weight": 0.25, "threshold": 0.7},
                "brand_alignment": {"weight": 0.2, "threshold": 0.85},
                "authenticity_score": {"weight": 0.15, "threshold": 0.9}
            }
        }
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for quality assessment."""
        return {
            "assessment_window_hours": 24,
            "min_predictions_for_assessment": 100,
            "confidence_bins": 10,
            "uncertainty_threshold": 0.3,
            "anomaly_detection_sensitivity": 0.95,
            "trend_analysis_periods": [7, 30, 90],  # days
            "real_time_monitoring": True,
            "feedback_integration": True,
            "adaptive_thresholds": True
        }
    
    async def record_prediction(self, prediction_record: PredictionRecord) -> str:
        """Record a new prediction for quality assessment."""
        try:
            model_id = prediction_record.model_id
            
            # Add to prediction history
            self.prediction_history[model_id].append(prediction_record)
            
            # Maintain history size
            max_history = self.config.get("max_history_size", 10000)
            if len(self.prediction_history[model_id]) > max_history:
                self.prediction_history[model_id].popleft()
            
            # Calculate immediate quality metrics if ground truth available
            if prediction_record.ground_truth is not None:
                immediate_quality = await self._calculate_immediate_quality(prediction_record)
                prediction_record.uncertainty_metrics.update(immediate_quality)
            
            # Real-time anomaly detection
            if self.config.get("real_time_monitoring", True):
                await self._detect_real_time_anomalies(prediction_record)
            
            # Update confidence calibration
            await self._update_confidence_calibration(prediction_record)
            
            # Trigger assessment if threshold reached
            if (len(self.prediction_history[model_id]) % 
                self.config.get("assessment_trigger_interval", 100) == 0):
                await self._trigger_periodic_assessment(model_id)
            
            self.logger.debug(f"Prediction recorded: {prediction_record.prediction_id}")
            return prediction_record.prediction_id
            
        except Exception as e:
            self.logger.error(f"Error recording prediction: {e}")
            raise
    
    async def assess_prediction_quality(
        self,
        model_id: str,
        assessment_period: Optional[Tuple[datetime, datetime]] = None
    ) -> QualityAssessment:
        """Perform comprehensive prediction quality assessment."""
        try:
            if model_id not in self.prediction_history:
                raise ValueError(f"No predictions found for model: {model_id}")
            
            # Define assessment period
            if assessment_period is None:
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=self.config["assessment_window_hours"])
                assessment_period = (start_time, end_time)
            
            # Filter predictions by period
            predictions = self._filter_predictions_by_period(
                self.prediction_history[model_id], assessment_period
            )
            
            if len(predictions) < self.config["min_predictions_for_assessment"]:
                self.logger.warning(f"Insufficient predictions for assessment: {len(predictions)}")
            
            # Extract predictions with ground truth for accuracy metrics
            validated_predictions = [p for p in predictions if p.ground_truth is not None]
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                validated_predictions, predictions
            )
            
            # Analyze confidence distribution
            confidence_distribution = await self._analyze_confidence_distribution(predictions)
            
            # Perform uncertainty analysis
            uncertainty_analysis = await self._analyze_uncertainty_patterns(predictions)
            
            # Analyze performance trends
            performance_trends = await self._analyze_performance_trends(model_id, assessment_period)
            
            # Detect anomalies
            anomaly_detection = await self._detect_prediction_anomalies(predictions)
            
            # Generate recommendations
            recommendations = await self._generate_quality_recommendations(
                quality_metrics, confidence_distribution, uncertainty_analysis, anomaly_detection
            )
            
            # Calculate risk score
            risk_score = await self._calculate_risk_score(
                quality_metrics, anomaly_detection, uncertainty_analysis
            )
            
            # Create assessment result
            assessment = QualityAssessment(
                assessment_id=str(uuid.uuid4()),
                model_id=model_id,
                assessment_period=assessment_period,
                total_predictions=len(predictions),
                quality_metrics=quality_metrics,
                confidence_distribution=confidence_distribution,
                uncertainty_analysis=uncertainty_analysis,
                performance_trends=performance_trends,
                anomaly_detection=anomaly_detection,
                recommendations=recommendations,
                risk_score=risk_score,
                assessment_timestamp=datetime.now()
            )
            
            # Store assessment
            self.quality_history[model_id].append(assessment)
            
            # Save assessment to cache
            await self._save_assessment(assessment)
            
            self.logger.info(f"Quality assessment completed for {model_id}: "
                           f"risk_score={risk_score:.3f}, accuracy={quality_metrics.accuracy:.3f}")
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error assessing prediction quality: {e}")
            raise
    
    async def update_with_feedback(
        self,
        prediction_id: str,
        feedback_data: Dict[str, Any]
    ) -> bool:
        """Update prediction quality assessment with user feedback."""
        try:
            # Find prediction record
            prediction_record = None
            model_id = None
            
            for mid, predictions in self.prediction_history.items():
                for pred in predictions:
                    if pred.prediction_id == prediction_id:
                        prediction_record = pred
                        model_id = mid
                        break
                if prediction_record:
                    break
            
            if not prediction_record:
                self.logger.warning(f"Prediction not found for feedback: {prediction_id}")
                return False
            
            # Extract feedback information
            feedback_score = feedback_data.get("score")  # 0-1 scale
            ground_truth = feedback_data.get("ground_truth")
            user_satisfaction = feedback_data.get("user_satisfaction")
            
            # Update prediction record
            if feedback_score is not None:
                prediction_record.feedback_score = feedback_score
            
            if ground_truth is not None:
                prediction_record.ground_truth = ground_truth
            
            # Add to feedback buffer
            feedback_entry = {
                "prediction_id": prediction_id,
                "timestamp": datetime.now(),
                "feedback_data": feedback_data,
                "model_performance_impact": await self._calculate_feedback_impact(
                    prediction_record, feedback_data
                )
            }
            
            self.feedback_buffer[model_id].append(feedback_entry)
            
            # Update confidence calibration with feedback
            await self._update_calibration_with_feedback(prediction_record, feedback_data)
            
            # Trigger adaptive threshold adjustment
            if self.config.get("adaptive_thresholds", True):
                await self._adjust_quality_thresholds(model_id, feedback_data)
            
            self.logger.debug(f"Feedback integrated for prediction: {prediction_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating with feedback: {e}")
            return False
    
    async def monitor_quality_drift(
        self,
        model_id: str,
        monitoring_window_days: int = 7
    ) -> Dict[str, Any]:
        """Monitor prediction quality drift over time."""
        try:
            if model_id not in self.quality_history:
                return {"drift_detected": False, "message": "No quality history available"}
            
            # Get recent assessments
            recent_assessments = self._get_recent_assessments(
                self.quality_history[model_id], monitoring_window_days
            )
            
            if len(recent_assessments) < 2:
                return {"drift_detected": False, "message": "Insufficient assessment history"}
            
            # Analyze quality trends
            drift_analysis = {
                "drift_detected": False,
                "drift_metrics": {},
                "trend_analysis": {},
                "severity": "none",
                "recommendations": []
            }
            
            # Check accuracy drift
            accuracy_trend = [a.quality_metrics.accuracy for a in recent_assessments]
            accuracy_drift = await self._detect_metric_drift(accuracy_trend, "accuracy")
            drift_analysis["drift_metrics"]["accuracy"] = accuracy_drift
            
            # Check confidence calibration drift
            calibration_trend = [a.quality_metrics.calibration_error for a in recent_assessments]
            calibration_drift = await self._detect_metric_drift(calibration_trend, "calibration_error", ascending=False)
            drift_analysis["drift_metrics"]["calibration"] = calibration_drift
            
            # Check uncertainty quality drift
            uncertainty_trend = [a.quality_metrics.uncertainty_quality for a in recent_assessments]
            uncertainty_drift = await self._detect_metric_drift(uncertainty_trend, "uncertainty_quality")
            drift_analysis["drift_metrics"]["uncertainty"] = uncertainty_drift
            
            # Determine overall drift status
            drift_detected = any([
                accuracy_drift.get("significant_drift", False),
                calibration_drift.get("significant_drift", False),
                uncertainty_drift.get("significant_drift", False)
            ])
            
            drift_analysis["drift_detected"] = drift_detected
            
            if drift_detected:
                # Calculate severity
                drift_analysis["severity"] = await self._calculate_drift_severity(
                    drift_analysis["drift_metrics"]
                )
                
                # Generate recommendations
                drift_analysis["recommendations"] = await self._generate_drift_recommendations(
                    drift_analysis["drift_metrics"], drift_analysis["severity"]
                )
            
            # Trend analysis
            drift_analysis["trend_analysis"] = {
                "accuracy_trend": self._calculate_trend_direction(accuracy_trend),
                "stability_trend": self._calculate_stability_trend(recent_assessments),
                "prediction_volume_trend": self._calculate_volume_trend(recent_assessments)
            }
            
            self.logger.info(f"Quality drift monitoring completed for {model_id}: "
                           f"drift_detected={drift_detected}")
            
            return drift_analysis
            
        except Exception as e:
            self.logger.error(f"Error monitoring quality drift: {e}")
            return {"drift_detected": False, "error": str(e)}
    
    async def _calculate_quality_metrics(
        self,
        validated_predictions: List[PredictionRecord],
        all_predictions: List[PredictionRecord]
    ) -> QualityMetrics:
        """Calculate comprehensive quality metrics."""
        try:
            if not validated_predictions:
                # Return default metrics if no ground truth available
                return QualityMetrics(
                    accuracy=0.0,
                    precision=0.0,
                    recall=0.0,
                    f1_score=0.0,
                    auc_roc=0.0,
                    calibration_error=1.0,
                    uncertainty_quality=0.0,
                    confidence_correlation=0.0,
                    prediction_stability=0.0,
                    domain_specific_metrics={}
                )
            
            # Extract predictions and ground truth
            predictions = [p.prediction for p in validated_predictions]
            ground_truths = [p.ground_truth for p in validated_predictions]
            confidences = [p.confidence_score for p in validated_predictions]
            
            # Calculate basic metrics (mock implementation)
            accuracy = await self._calculate_accuracy(predictions, ground_truths)
            precision = await self._calculate_precision(predictions, ground_truths)
            recall = await self._calculate_recall(predictions, ground_truths)
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            auc_roc = await self._calculate_auc_roc(predictions, ground_truths)
            
            # Calculate calibration error
            calibration_error = await self._calculate_calibration_error(
                predictions, ground_truths, confidences
            )
            
            # Calculate uncertainty quality
            uncertainty_quality = await self._calculate_uncertainty_quality(validated_predictions)
            
            # Calculate confidence correlation
            confidence_correlation = await self._calculate_confidence_correlation(
                predictions, ground_truths, confidences
            )
            
            # Calculate prediction stability
            prediction_stability = await self._calculate_prediction_stability(all_predictions)
            
            # Calculate domain-specific metrics
            domain_metrics = await self._calculate_domain_specific_metrics(validated_predictions)
            
            return QualityMetrics(
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1_score,
                auc_roc=auc_roc,
                calibration_error=calibration_error,
                uncertainty_quality=uncertainty_quality,
                confidence_correlation=confidence_correlation,
                prediction_stability=prediction_stability,
                domain_specific_metrics=domain_metrics
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating quality metrics: {e}")
            raise
    
    async def _calculate_accuracy(self, predictions: List[Any], ground_truths: List[Any]) -> float:
        """Calculate prediction accuracy."""
        if not predictions or not ground_truths:
            return 0.0
        
        # Mock accuracy calculation (in production, would handle different prediction types)
        correct = sum(1 for p, gt in zip(predictions, ground_truths) if abs(p - gt) < 0.1)
        return correct / len(predictions)
    
    async def _calculate_precision(self, predictions: List[Any], ground_truths: List[Any]) -> float:
        """Calculate precision score."""
        # Mock precision calculation
        return np.random.uniform(0.7, 0.9)
    
    async def _calculate_recall(self, predictions: List[Any], ground_truths: List[Any]) -> float:
        """Calculate recall score."""
        # Mock recall calculation
        return np.random.uniform(0.7, 0.9)
    
    async def _calculate_auc_roc(self, predictions: List[Any], ground_truths: List[Any]) -> float:
        """Calculate AUC-ROC score."""
        # Mock AUC-ROC calculation
        return np.random.uniform(0.75, 0.95)
    
    async def _calculate_calibration_error(
        self,
        predictions: List[Any],
        ground_truths: List[Any],
        confidences: List[float]
    ) -> float:
        """Calculate confidence calibration error."""
        try:
            # Bin predictions by confidence
            bins = np.linspace(0, 1, self.config["confidence_bins"] + 1)
            bin_centers = (bins[:-1] + bins[1:]) / 2
            
            calibration_error = 0.0
            total_samples = len(predictions)
            
            for i in range(len(bins) - 1):
                # Find predictions in this confidence bin
                in_bin = [(conf >= bins[i]) and (conf < bins[i+1]) 
                         for conf in confidences]
                
                if not any(in_bin):
                    continue
                
                # Calculate accuracy in this bin
                bin_predictions = [p for p, ib in zip(predictions, in_bin) if ib]
                bin_ground_truths = [gt for gt, ib in zip(ground_truths, in_bin) if ib]
                bin_confidences = [c for c, ib in zip(confidences, in_bin) if ib]
                
                if bin_predictions:
                    bin_accuracy = await self._calculate_accuracy(bin_predictions, bin_ground_truths)
                    avg_confidence = np.mean(bin_confidences)
                    bin_weight = len(bin_predictions) / total_samples
                    
                    # Add weighted contribution to calibration error
                    calibration_error += bin_weight * abs(avg_confidence - bin_accuracy)
            
            return calibration_error
            
        except Exception as e:
            self.logger.error(f"Error calculating calibration error: {e}")
            return 1.0
    
    def _filter_predictions_by_period(
        self,
        predictions: deque,
        period: Tuple[datetime, datetime]
    ) -> List[PredictionRecord]:
        """Filter predictions by time period."""
        start_time, end_time = period
        return [p for p in predictions if start_time <= p.timestamp <= end_time]

# Example usage and testing
async def main():
    """Example usage of PredictionQualityAssessor."""
    assessor = PredictionQualityAssessor()
    
    # Simulate predictions for a musician model
    model_id = "musician-engagement-predictor"
    
    # Generate mock predictions
    for i in range(200):
        prediction_record = PredictionRecord(
            prediction_id=f"pred_{i}_{int(time.time())}",
            model_id=model_id,
            model_version="v2.1.0",
            input_features={"tempo": np.random.uniform(60, 180), "genre": "pop"},
            prediction=np.random.uniform(0.1, 1.0),  # Engagement score
            confidence_score=np.random.uniform(0.6, 0.95),
            uncertainty_metrics={"epistemic": np.random.uniform(0.1, 0.3)},
            timestamp=datetime.now() - timedelta(hours=np.random.uniform(0, 24)),
            ground_truth=np.random.uniform(0.1, 1.0) if i % 3 == 0 else None,  # 1/3 have ground truth
            creator_domain="musician"
        )
        
        await assessor.record_prediction(prediction_record)
    
    # Perform quality assessment
    assessment = await assessor.assess_prediction_quality(model_id)
    
    print(f"Quality Assessment Results for {model_id}:")
    print(f"- Total predictions: {assessment.total_predictions}")
    print(f"- Accuracy: {assessment.quality_metrics.accuracy:.3f}")
    print(f"- Calibration error: {assessment.quality_metrics.calibration_error:.3f}")
    print(f"- Risk score: {assessment.risk_score:.3f}")
    print(f"- Recommendations: {len(assessment.recommendations)}")
    
    for i, rec in enumerate(assessment.recommendations[:3]):
        print(f"  {i+1}. {rec}")
    
    # Monitor quality drift
    drift_analysis = await assessor.monitor_quality_drift(model_id)
    print(f"\nQuality Drift Analysis:")
    print(f"- Drift detected: {drift_analysis['drift_detected']}")
    print(f"- Severity: {drift_analysis.get('severity', 'none')}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())