"""Enhanced Data Drift Monitoring

This module extends the existing drift detection capabilities with
production-grade monitoring, alerting, and continuous tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import accuracy_score
import json
import uuid

# Import existing drift detector
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from database.ai_engines.performance_metrics import ModelDriftDetector, DriftType, AlertLevel
except ImportError:
    # Fallback definitions if import fails
    class DriftType(str, Enum):
        DATA_DRIFT = "data_drift"
        CONCEPT_DRIFT = "concept_drift"
        PREDICTION_DRIFT = "prediction_drift"
    
    class AlertLevel(str, Enum):
        INFO = "info"
        WARNING = "warning"
        CRITICAL = "critical"

logger = logging.getLogger(__name__)


class MonitoringStatus(str, Enum):
    """Monitoring status enumeration"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class DriftSeverity(str, Enum):
    """Drift severity levels"""
    MINIMAL = "minimal"      # < 10% drift
    MODERATE = "moderate"    # 10-25% drift
    SIGNIFICANT = "significant"  # 25-50% drift
    SEVERE = "severe"       # > 50% drift


@dataclass
class DriftAlert:
    """Enhanced drift alert with detailed information"""
    alert_id: str
    model_id: str
    drift_type: DriftType
    severity: DriftSeverity
    drift_score: float
    threshold: float
    affected_features: List[str]
    timestamp: datetime
    description: str
    recommendations: List[str]
    auto_actions: List[str] = field(default_factory=list)
    acknowledged: bool = False


@dataclass
class MonitoringConfig:
    """Configuration for drift monitoring"""
    model_id: str
    monitoring_frequency: timedelta
    drift_thresholds: Dict[DriftType, float]
    alert_thresholds: Dict[DriftSeverity, float]
    auto_retrain_threshold: float
    notification_channels: List[str]
    historical_window: timedelta
    statistical_tests: List[str]
    feature_importance_weights: Optional[Dict[str, float]] = None


@dataclass
class DriftTrend:
    """Drift trend analysis"""
    model_id: str
    drift_type: DriftType
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float
    projected_threshold_breach: Optional[datetime]
    confidence_interval: Tuple[float, float]
    historical_data: List[Dict[str, Any]]


class EnhancedDriftMonitor:
    """Enhanced drift monitoring with production-grade capabilities"""
    
    def __init__(self, base_drift_detector: Optional[object] = None):
        """
        Initialize enhanced drift monitor.
        
        Args:
            base_drift_detector: Existing ModelDriftDetector instance
        """
        self.base_detector = base_drift_detector or self._create_base_detector()
        self.monitoring_configs = {}
        self.drift_history = {}
        self.active_alerts = {}
        self.trend_analyses = {}
        self.logger = logging.getLogger(__name__)
        
    def _create_base_detector(self):
        """Create base drift detector if not provided"""
        try:
            from database.ai_engines.performance_metrics import ModelDriftDetector
            return ModelDriftDetector()
        except ImportError:
            # Return mock detector for testing
            return None
    
    async def setup_monitoring(
        self,
        model_id: str,
        config: MonitoringConfig
    ) -> Dict[str, Any]:
        """
        Setup continuous drift monitoring for a model.
        
        Args:
            model_id: Model to monitor
            config: Monitoring configuration
            
        Returns:
            Setup confirmation with monitoring details
        """
        try:
            self.monitoring_configs[model_id] = config
            
            # Initialize drift history
            if model_id not in self.drift_history:
                self.drift_history[model_id] = []
            
            # Initialize alert tracking
            if model_id not in self.active_alerts:
                self.active_alerts[model_id] = []
            
            setup_result = {
                "model_id": model_id,
                "status": MonitoringStatus.ACTIVE,
                "monitoring_frequency": config.monitoring_frequency.total_seconds(),
                "drift_thresholds": config.drift_thresholds,
                "next_check": (datetime.utcnow() + config.monitoring_frequency).isoformat(),
                "setup_timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Drift monitoring setup completed for model {model_id}")
            return setup_result
            
        except Exception as e:
            self.logger.error(f"Failed to setup monitoring for model {model_id}: {str(e)}")
            raise
    
    async def check_drift(
        self,
        model_id: str,
        new_data: np.ndarray,
        predictions: Optional[np.ndarray] = None,
        ground_truth: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Enhanced drift check with comprehensive analysis.
        
        Args:
            model_id: Model identifier
            new_data: New data batch to check
            predictions: Model predictions on new data
            ground_truth: Ground truth labels (if available)
            
        Returns:
            Comprehensive drift analysis result
        """
        try:
            if model_id not in self.monitoring_configs:
                raise ValueError(f"No monitoring configuration found for model {model_id}")
            
            config = self.monitoring_configs[model_id]
            
            # Run multiple drift detection types
            drift_results = {}
            
            # Data drift detection
            if self.base_detector:
                data_drift = await self.base_detector.detect_drift(
                    model_id, new_data, DriftType.DATA_DRIFT
                )
                drift_results["data_drift"] = data_drift
            else:
                # Fallback drift detection
                data_drift = await self._fallback_drift_detection(
                    model_id, new_data, DriftType.DATA_DRIFT
                )
                drift_results["data_drift"] = data_drift
            
            # Prediction drift (if predictions available)
            if predictions is not None:
                pred_drift = await self._detect_prediction_drift(
                    model_id, predictions
                )
                drift_results["prediction_drift"] = pred_drift
            
            # Concept drift (if ground truth available)
            if ground_truth is not None and predictions is not None:
                concept_drift = await self._detect_concept_drift(
                    model_id, predictions, ground_truth
                )
                drift_results["concept_drift"] = concept_drift
            
            # Comprehensive analysis
            analysis_result = await self._analyze_drift_results(
                model_id, drift_results, new_data
            )
            
            # Update drift history
            drift_record = {
                "timestamp": datetime.utcnow(),
                "drift_results": drift_results,
                "analysis": analysis_result,
                "data_batch_size": len(new_data)
            }
            self.drift_history[model_id].append(drift_record)
            
            # Check for alerts
            alerts = await self._check_alert_conditions(model_id, analysis_result)
            
            # Update trend analysis
            await self._update_trend_analysis(model_id)
            
            return {
                "model_id": model_id,
                "drift_results": drift_results,
                "analysis": analysis_result,
                "alerts": alerts,
                "timestamp": datetime.utcnow().isoformat(),
                "monitoring_status": MonitoringStatus.ACTIVE
            }
            
        except Exception as e:
            self.logger.error(f"Drift check failed for model {model_id}: {str(e)}")
            raise
    
    async def _fallback_drift_detection(
        self,
        model_id: str,
        new_data: np.ndarray,
        drift_type: DriftType
    ) -> Dict[str, Any]:
        """Fallback drift detection when base detector is unavailable"""
        
        # Simple statistical drift detection
        if model_id in self.drift_history and self.drift_history[model_id]:
            # Use previous data as reference
            last_record = self.drift_history[model_id][-1]
            if "reference_stats" in last_record:
                ref_stats = last_record["reference_stats"]
            else:
                # Calculate reference stats from current data
                ref_stats = {
                    "mean": np.mean(new_data, axis=0),
                    "std": np.std(new_data, axis=0)
                }
        else:
            # First run - establish baseline
            ref_stats = {
                "mean": np.mean(new_data, axis=0),
                "std": np.std(new_data, axis=0)
            }
        
        # Calculate drift score using statistical distance
        current_mean = np.mean(new_data, axis=0)
        current_std = np.std(new_data, axis=0)
        
        # Normalized difference
        mean_diff = np.abs(current_mean - ref_stats["mean"]) / (ref_stats["std"] + 1e-8)
        drift_score = np.mean(mean_diff)
        
        drift_detected = drift_score > 1.0  # 1 standard deviation threshold
        
        return {
            "status": "success",
            "drift_score": float(drift_score),
            "drift_detected": drift_detected,
            "threshold": 1.0,
            "metadata": {
                "reference_mean": ref_stats["mean"].tolist() if hasattr(ref_stats["mean"], 'tolist') else ref_stats["mean"],
                "current_mean": current_mean.tolist(),
                "drift_type": drift_type
            },
            "reference_stats": ref_stats
        }
    
    async def _detect_prediction_drift(
        self,
        model_id: str,
        predictions: np.ndarray
    ) -> Dict[str, Any]:
        """Detect drift in model predictions"""
        
        # Get historical prediction statistics
        historical_preds = self._get_historical_predictions(model_id)
        
        if not historical_preds:
            # Establish baseline
            return {
                "status": "baseline_established",
                "drift_score": 0.0,
                "drift_detected": False,
                "metadata": {
                    "prediction_mean": float(np.mean(predictions)),
                    "prediction_std": float(np.std(predictions)),
                    "prediction_distribution": np.histogram(predictions, bins=10)[0].tolist()
                }
            }
        
        # Compare current predictions with historical
        hist_mean = np.mean(historical_preds)
        hist_std = np.std(historical_preds)
        current_mean = np.mean(predictions)
        current_std = np.std(predictions)
        
        # Calculate drift using statistical tests
        try:
            # Kolmogorov-Smirnov test
            ks_statistic, ks_p_value = stats.ks_2samp(historical_preds[-1000:], predictions[:1000])
            
            # Drift score based on distribution difference
            drift_score = ks_statistic
            drift_detected = ks_p_value < 0.05  # 5% significance level
            
        except Exception:
            # Fallback to simple statistical comparison
            mean_change = abs(current_mean - hist_mean) / (hist_std + 1e-8)
            drift_score = mean_change
            drift_detected = mean_change > 2.0  # 2 standard deviations
        
        return {
            "status": "success",
            "drift_score": float(drift_score),
            "drift_detected": drift_detected,
            "threshold": 0.05,
            "metadata": {
                "historical_mean": float(hist_mean),
                "current_mean": float(current_mean),
                "distribution_change": float(drift_score)
            }
        }
    
    async def _detect_concept_drift(
        self,
        model_id: str,
        predictions: np.ndarray,
        ground_truth: np.ndarray
    ) -> Dict[str, Any]:
        """Detect concept drift using prediction accuracy changes"""
        
        current_accuracy = accuracy_score(ground_truth, predictions)
        
        # Get historical accuracy
        historical_accuracy = self._get_historical_accuracy(model_id)
        
        if not historical_accuracy:
            return {
                "status": "baseline_established",
                "drift_score": 0.0,
                "drift_detected": False,
                "metadata": {
                    "current_accuracy": float(current_accuracy)
                }
            }
        
        # Calculate accuracy drift
        recent_accuracy = np.mean(historical_accuracy[-10:])  # Last 10 measurements
        accuracy_change = abs(current_accuracy - recent_accuracy)
        
        # Concept drift if significant accuracy drop
        drift_detected = accuracy_change > 0.05  # 5% accuracy drop
        drift_score = accuracy_change
        
        return {
            "status": "success",
            "drift_score": float(drift_score),
            "drift_detected": drift_detected,
            "threshold": 0.05,
            "metadata": {
                "current_accuracy": float(current_accuracy),
                "historical_accuracy": float(recent_accuracy),
                "accuracy_change": float(accuracy_change)
            }
        }
    
    def _get_historical_predictions(self, model_id: str) -> List[float]:
        """Get historical predictions for comparison"""
        if model_id not in self.drift_history:
            return []
        
        predictions = []
        for record in self.drift_history[model_id]:
            if "predictions" in record.get("metadata", {}):
                predictions.extend(record["metadata"]["predictions"])
        
        return predictions
    
    def _get_historical_accuracy(self, model_id: str) -> List[float]:
        """Get historical accuracy measurements"""
        if model_id not in self.drift_history:
            return []
        
        accuracies = []
        for record in self.drift_history[model_id]:
            concept_drift = record.get("drift_results", {}).get("concept_drift", {})
            if "metadata" in concept_drift and "current_accuracy" in concept_drift["metadata"]:
                accuracies.append(concept_drift["metadata"]["current_accuracy"])
        
        return accuracies
    
    async def _analyze_drift_results(
        self,
        model_id: str,
        drift_results: Dict[str, Any],
        new_data: np.ndarray
    ) -> Dict[str, Any]:
        """Analyze drift results comprehensively"""
        
        analysis = {
            "overall_drift_detected": False,
            "drift_severity": DriftSeverity.MINIMAL,
            "affected_drift_types": [],
            "max_drift_score": 0.0,
            "feature_impact_analysis": {},
            "trend_indicators": {},
            "risk_assessment": "low"
        }
        
        # Analyze each drift type
        max_score = 0.0
        detected_drifts = []
        
        for drift_type, result in drift_results.items():
            if result.get("drift_detected", False):
                detected_drifts.append(drift_type)
                analysis["overall_drift_detected"] = True
            
            drift_score = result.get("drift_score", 0.0)
            if drift_score > max_score:
                max_score = drift_score
        
        analysis["max_drift_score"] = max_score
        analysis["affected_drift_types"] = detected_drifts
        
        # Determine drift severity
        if max_score > 2.0:
            analysis["drift_severity"] = DriftSeverity.SEVERE
            analysis["risk_assessment"] = "critical"
        elif max_score > 1.0:
            analysis["drift_severity"] = DriftSeverity.SIGNIFICANT
            analysis["risk_assessment"] = "high"
        elif max_score > 0.5:
            analysis["drift_severity"] = DriftSeverity.MODERATE
            analysis["risk_assessment"] = "medium"
        else:
            analysis["drift_severity"] = DriftSeverity.MINIMAL
            analysis["risk_assessment"] = "low"
        
        # Feature impact analysis (simplified)
        if len(new_data.shape) > 1:
            feature_impacts = {}
            for i in range(min(new_data.shape[1], 10)):  # Analyze up to 10 features
                feature_variance = np.var(new_data[:, i])
                feature_impacts[f"feature_{i}"] = float(feature_variance)
            analysis["feature_impact_analysis"] = feature_impacts
        
        return analysis
    
    async def _check_alert_conditions(
        self,
        model_id: str,
        analysis: Dict[str, Any]
    ) -> List[DriftAlert]:
        """Check if alert conditions are met"""
        alerts = []
        
        config = self.monitoring_configs.get(model_id)
        if not config:
            return alerts
        
        # Check severity-based alerts
        severity = DriftSeverity(analysis["drift_severity"])
        
        if severity in [DriftSeverity.SIGNIFICANT, DriftSeverity.SEVERE]:
            alert = DriftAlert(
                alert_id=str(uuid.uuid4()),
                model_id=model_id,
                drift_type=DriftType.DATA_DRIFT,  # Primary drift type
                severity=severity,
                drift_score=analysis["max_drift_score"],
                threshold=1.0,  # Default threshold
                affected_features=list(analysis.get("feature_impact_analysis", {}).keys()),
                timestamp=datetime.utcnow(),
                description=f"{severity} drift detected with score {analysis['max_drift_score']:.3f}",
                recommendations=self._generate_drift_recommendations(analysis)
            )
            alerts.append(alert)
            
            # Store active alert
            if model_id not in self.active_alerts:
                self.active_alerts[model_id] = []
            self.active_alerts[model_id].append(alert)
        
        return alerts
    
    def _generate_drift_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on drift analysis"""
        recommendations = []
        
        severity = analysis["drift_severity"]
        risk = analysis["risk_assessment"]
        
        if severity == DriftSeverity.SEVERE:
            recommendations.extend([
                "Immediate model retraining recommended",
                "Review data quality and preprocessing pipeline",
                "Consider temporary model rollback if available"
            ])
        elif severity == DriftSeverity.SIGNIFICANT:
            recommendations.extend([
                "Schedule model retraining within 24-48 hours",
                "Investigate root cause of drift",
                "Monitor performance metrics closely"
            ])
        elif severity == DriftSeverity.MODERATE:
            recommendations.extend([
                "Plan model retraining for next maintenance window",
                "Collect additional data for analysis",
                "Review feature engineering pipeline"
            ])
        
        if "data_drift" in analysis.get("affected_drift_types", []):
            recommendations.append("Analyze data distribution changes")
        
        if "concept_drift" in analysis.get("affected_drift_types", []):
            recommendations.append("Review target variable relationships")
        
        return recommendations
    
    async def _update_trend_analysis(self, model_id: str):
        """Update trend analysis for long-term monitoring"""
        if model_id not in self.drift_history or len(self.drift_history[model_id]) < 5:
            return  # Need minimum history for trend analysis
        
        recent_history = self.drift_history[model_id][-20:]  # Last 20 measurements
        
        # Extract drift scores over time
        data_drift_scores = []
        timestamps = []
        
        for record in recent_history:
            timestamps.append(record["timestamp"])
            data_drift = record.get("drift_results", {}).get("data_drift", {})
            score = data_drift.get("drift_score", 0.0)
            data_drift_scores.append(score)
        
        if len(data_drift_scores) < 3:
            return
        
        # Simple trend analysis
        x = np.arange(len(data_drift_scores))
        slope, _, _, _, _ = stats.linregress(x, data_drift_scores)
        
        # Determine trend direction
        if slope > 0.01:
            trend_direction = "increasing"
        elif slope < -0.01:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        trend_strength = abs(slope)
        
        # Project threshold breach (simplified)
        current_score = data_drift_scores[-1]
        threshold = 1.0
        projected_breach = None
        
        if trend_direction == "increasing" and slope > 0:
            time_to_breach = (threshold - current_score) / slope
            if time_to_breach > 0 and time_to_breach < 100:  # Within 100 time periods
                projected_breach = datetime.utcnow() + timedelta(days=time_to_breach)
        
        trend = DriftTrend(
            model_id=model_id,
            drift_type=DriftType.DATA_DRIFT,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            projected_threshold_breach=projected_breach,
            confidence_interval=(min(data_drift_scores), max(data_drift_scores)),
            historical_data=[
                {"timestamp": ts.isoformat(), "score": score}
                for ts, score in zip(timestamps, data_drift_scores)
            ]
        )
        
        self.trend_analyses[model_id] = trend
    
    def get_monitoring_status(self, model_id: str) -> Dict[str, Any]:
        """Get current monitoring status for a model"""
        if model_id not in self.monitoring_configs:
            return {"error": "Model not monitored"}
        
        config = self.monitoring_configs[model_id]
        recent_history = self.drift_history.get(model_id, [])[-10:]
        active_alerts = self.active_alerts.get(model_id, [])
        trend = self.trend_analyses.get(model_id)
        
        return {
            "model_id": model_id,
            "monitoring_status": MonitoringStatus.ACTIVE,
            "last_check": recent_history[-1]["timestamp"].isoformat() if recent_history else None,
            "drift_trend": trend.trend_direction if trend else "unknown",
            "active_alerts": len(active_alerts),
            "historical_checks": len(self.drift_history.get(model_id, [])),
            "next_scheduled_check": (datetime.utcnow() + config.monitoring_frequency).isoformat()
        }
    
    def get_drift_history(
        self,
        model_id: str,
        limit: Optional[int] = None,
        start_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get drift monitoring history"""
        if model_id not in self.drift_history:
            return []
        
        history = self.drift_history[model_id]
        
        # Filter by date if specified
        if start_date:
            history = [h for h in history if h["timestamp"] >= start_date]
        
        # Limit results if specified
        if limit:
            history = history[-limit:]
        
        return [
            {
                "timestamp": h["timestamp"].isoformat(),
                "drift_detected": any(
                    result.get("drift_detected", False)
                    for result in h["drift_results"].values()
                ),
                "max_drift_score": h["analysis"]["max_drift_score"],
                "severity": h["analysis"]["drift_severity"],
                "affected_types": h["analysis"]["affected_drift_types"]
            }
            for h in history
        ]