"""SLA Predictive Analytics System
ML-powered SLA violation prediction and performance forecasting for Creator Economy Platform

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Propriété intellectuelle exclusive
"""

import asyncio
import logging
import statistics
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import deque, defaultdict
from enum import Enum
import json
import numpy as np

class PredictionModel(Enum):
    """Types of prediction models"""
    LINEAR_REGRESSION = "linear_regression"
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    ARIMA = "arima"
    LSTM = "lstm"
    ENSEMBLE = "ensemble"

class ForecastHorizon(Enum):
    """Forecast time horizons"""
    NEXT_HOUR = "1h"
    NEXT_4_HOURS = "4h"
    NEXT_24_HOURS = "24h"
    NEXT_7_DAYS = "7d"
    NEXT_30_DAYS = "30d"

class AlertSeverity(Enum):
    """Predictive alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PredictionResult:
    """Prediction result data structure"""
    metric_name: str
    current_value: float
    predicted_value: float
    confidence_score: float
    prediction_timestamp: datetime
    forecast_horizon: ForecastHorizon
    model_used: PredictionModel
    risk_level: AlertSeverity
    factors: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    metric_name: str
    current_value: float
    expected_range: Tuple[float, float]
    anomaly_score: float
    detection_timestamp: datetime
    anomaly_type: str
    severity: AlertSeverity
    contributing_factors: List[str]
    suggested_actions: List[str]

class SLAPredictiveAnalytics:
    """
    Enterprise SLA Predictive Analytics System
    ML-powered SLA violation prediction and performance optimization
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.historical_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50000))
        self.predictions: deque = deque(maxlen=10000)
        self.anomalies: deque = deque(maxlen=5000)
        self.model_performance: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.prediction_cache: Dict[str, PredictionResult] = {}
        self.monitoring_active = False
        
        # ML model parameters (simplified for this implementation)
        self.model_params = {
            "smoothing_alpha": 0.3,
            "trend_alpha": 0.1,
            "seasonal_alpha": 0.05,
            "confidence_threshold": 0.7,
            "anomaly_threshold": 2.5  # Standard deviations
        }
        
    async def record_metric_data(self, metric_name: str, value: float, 
                               timestamp: datetime, metadata: Dict[str, Any] = None):
        """Record historical metric data for analysis"""
        data_point = {
            'timestamp': timestamp,
            'value': value,
            'metadata': metadata or {}
        }
        
        self.historical_data[metric_name].append(data_point)
        
        # Trigger real-time anomaly detection
        await self._detect_anomalies(metric_name, value, timestamp)
        
        # Update predictions if enough data
        if len(self.historical_data[metric_name]) >= 24:  # Minimum 24 data points
            await self._update_predictions(metric_name)
        
    async def predict_sla_violation(self, metric_name: str, 
                                  forecast_horizon: ForecastHorizon,
                                  model_type: PredictionModel = PredictionModel.ENSEMBLE) -> PredictionResult:
        """Predict potential SLA violations"""
        
        if metric_name not in self.historical_data:
            raise ValueError(f"No historical data available for metric: {metric_name}")
        
        historical_values = [dp['value'] for dp in self.historical_data[metric_name]]
        
        if len(historical_values) < 10:
            raise ValueError(f"Insufficient data for prediction: {len(historical_values)} points")
        
        # Apply ensemble prediction if requested
        if model_type == PredictionModel.ENSEMBLE:
            predicted_value, confidence = await self._ensemble_prediction(
                historical_values, forecast_horizon
            )
        else:
            predicted_value, confidence = await self._single_model_prediction(
                historical_values, forecast_horizon, model_type
            )
        
        # Assess risk level
        risk_level = self._assess_violation_risk(metric_name, predicted_value, confidence)
        
        # Identify contributing factors
        factors = await self._identify_contributing_factors(metric_name, historical_values)
        
        # Generate recommendations
        recommendations = await self._generate_prediction_recommendations(
            metric_name, predicted_value, risk_level, factors
        )
        
        # Create prediction result
        prediction = PredictionResult(
            metric_name=metric_name,
            current_value=historical_values[-1],
            predicted_value=predicted_value,
            confidence_score=confidence,
            prediction_timestamp=datetime.now(),
            forecast_horizon=forecast_horizon,
            model_used=model_type,
            risk_level=risk_level,
            factors=factors,
            recommendations=recommendations,
            metadata={
                "data_points_used": len(historical_values),
                "prediction_accuracy": self.model_performance.get(metric_name, {}).get("accuracy", 0.0)
            }
        )
        
        # Store prediction
        self.predictions.append(prediction)
        self.prediction_cache[f"{metric_name}_{forecast_horizon.value}"] = prediction
        
        self.logger.info(
            f"SLA violation prediction: {metric_name}, risk: {risk_level.value}, "
            f"confidence: {confidence:.2f}"
        )
        
        return prediction
        
    async def _ensemble_prediction(self, values: List[float], 
                                 horizon: ForecastHorizon) -> Tuple[float, float]:
        """Ensemble prediction combining multiple models"""
        predictions = []
        confidences = []
        
        # Linear regression prediction
        linear_pred, linear_conf = await self._linear_regression_prediction(values, horizon)
        predictions.append(linear_pred)
        confidences.append(linear_conf)
        
        # Moving average prediction
        ma_pred, ma_conf = await self._moving_average_prediction(values, horizon)
        predictions.append(ma_pred)
        confidences.append(ma_conf)
        
        # Exponential smoothing prediction
        exp_pred, exp_conf = await self._exponential_smoothing_prediction(values, horizon)
        predictions.append(exp_pred)
        confidences.append(exp_conf)
        
        # Weighted average based on confidence scores
        total_weight = sum(confidences)
        if total_weight > 0:
            weighted_prediction = sum(p * c for p, c in zip(predictions, confidences)) / total_weight
            average_confidence = statistics.mean(confidences)
        else:
            weighted_prediction = statistics.mean(predictions)
            average_confidence = 0.5
        
        return weighted_prediction, average_confidence
        
    async def _single_model_prediction(self, values: List[float], 
                                     horizon: ForecastHorizon,
                                     model_type: PredictionModel) -> Tuple[float, float]:
        """Single model prediction"""
        if model_type == PredictionModel.LINEAR_REGRESSION:
            return await self._linear_regression_prediction(values, horizon)
        elif model_type == PredictionModel.MOVING_AVERAGE:
            return await self._moving_average_prediction(values, horizon)
        elif model_type == PredictionModel.EXPONENTIAL_SMOOTHING:
            return await self._exponential_smoothing_prediction(values, horizon)
        else:
            # Default to moving average for unsupported models
            return await self._moving_average_prediction(values, horizon)
        
    async def _linear_regression_prediction(self, values: List[float], 
                                          horizon: ForecastHorizon) -> Tuple[float, float]:
        """Simple linear regression prediction"""
        n = len(values)
        x = list(range(n))
        y = values
        
        # Calculate slope and intercept
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        intercept = y_mean - slope * x_mean
        
        # Predict future value
        horizon_steps = self._horizon_to_steps(horizon)
        predicted_value = slope * (n + horizon_steps) + intercept
        
        # Calculate confidence based on R-squared
        y_pred = [slope * xi + intercept for xi in x]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        confidence = max(0, min(1, r_squared))
        
        return predicted_value, confidence
        
    async def _moving_average_prediction(self, values: List[float], 
                                       horizon: ForecastHorizon) -> Tuple[float, float]:
        """Moving average prediction"""
        window_size = min(20, len(values) // 2)
        if window_size < 3:
            window_size = len(values)
        
        recent_values = values[-window_size:]
        predicted_value = statistics.mean(recent_values)
        
        # Calculate confidence based on variance
        variance = statistics.variance(recent_values) if len(recent_values) > 1 else 0
        confidence = max(0, min(1, 1 / (1 + variance / 100)))
        
        return predicted_value, confidence
        
    async def _exponential_smoothing_prediction(self, values: List[float], 
                                              horizon: ForecastHorizon) -> Tuple[float, float]:
        """Exponential smoothing prediction"""
        alpha = self.model_params["smoothing_alpha"]
        
        if len(values) < 2:
            return values[-1], 0.5
        
        # Initialize
        smooth = values[0]
        
        # Apply exponential smoothing
        for value in values[1:]:
            smooth = alpha * value + (1 - alpha) * smooth
        
        predicted_value = smooth
        
        # Calculate confidence based on forecast error
        errors = []
        test_smooth = values[0]
        
        for i in range(1, len(values)):
            test_smooth = alpha * values[i-1] + (1 - alpha) * test_smooth
            error = abs(values[i] - test_smooth)
            errors.append(error)
        
        mean_error = statistics.mean(errors) if errors else 0
        confidence = max(0, min(1, 1 / (1 + mean_error / 10)))
        
        return predicted_value, confidence
        
    def _horizon_to_steps(self, horizon: ForecastHorizon) -> int:
        """Convert forecast horizon to prediction steps"""
        horizon_map = {
            ForecastHorizon.NEXT_HOUR: 1,
            ForecastHorizon.NEXT_4_HOURS: 4,
            ForecastHorizon.NEXT_24_HOURS: 24,
            ForecastHorizon.NEXT_7_DAYS: 168,  # 7 * 24 hours
            ForecastHorizon.NEXT_30_DAYS: 720  # 30 * 24 hours
        }
        return horizon_map.get(horizon, 1)
        
    async def _detect_anomalies(self, metric_name: str, current_value: float, 
                              timestamp: datetime):
        """Real-time anomaly detection"""
        if metric_name not in self.historical_data:
            return
        
        historical_values = [dp['value'] for dp in self.historical_data[metric_name]]
        
        if len(historical_values) < 10:
            return  # Need minimum data for anomaly detection
        
        # Calculate statistical bounds
        recent_values = historical_values[-20:]  # Last 20 values
        mean_value = statistics.mean(recent_values)
        std_dev = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
        
        # Calculate anomaly score (z-score)
        anomaly_score = abs(current_value - mean_value) / std_dev if std_dev > 0 else 0
        
        # Determine if anomalous
        threshold = self.model_params["anomaly_threshold"]
        
        if anomaly_score > threshold:
            # Classify anomaly type
            anomaly_type = "spike" if current_value > mean_value else "drop"
            
            # Determine severity
            if anomaly_score > threshold * 2:
                severity = AlertSeverity.CRITICAL
            elif anomaly_score > threshold * 1.5:
                severity = AlertSeverity.HIGH
            elif anomaly_score > threshold * 1.2:
                severity = AlertSeverity.MEDIUM
            else:
                severity = AlertSeverity.LOW
            
            # Expected range
            expected_range = (
                mean_value - threshold * std_dev,
                mean_value + threshold * std_dev
            )
            
            # Identify contributing factors
            factors = await self._identify_anomaly_factors(metric_name, current_value, timestamp)
            
            # Generate suggested actions
            actions = await self._generate_anomaly_actions(metric_name, anomaly_type, severity)
            
            # Create anomaly detection result
            anomaly = AnomalyDetection(
                metric_name=metric_name,
                current_value=current_value,
                expected_range=expected_range,
                anomaly_score=anomaly_score,
                detection_timestamp=timestamp,
                anomaly_type=anomaly_type,
                severity=severity,
                contributing_factors=factors,
                suggested_actions=actions
            )
            
            self.anomalies.append(anomaly)
            
            self.logger.warning(
                f"Anomaly detected: {metric_name}, score: {anomaly_score:.2f}, "
                f"severity: {severity.value}"
            )
        
    def _assess_violation_risk(self, metric_name: str, predicted_value: float, 
                             confidence: float) -> AlertSeverity:
        """Assess SLA violation risk level"""
        # Simplified risk assessment based on metric type and predicted value
        # In production, would use more sophisticated thresholds
        
        risk_thresholds = {
            "response_time": {"warning": 200, "critical": 500},
            "uptime": {"warning": 99.0, "critical": 98.0},
            "throughput": {"warning": 8000, "critical": 5000},
            "error_rate": {"warning": 1.0, "critical": 5.0}
        }
        
        # Determine metric category
        metric_category = None
        for category in risk_thresholds.keys():
            if category in metric_name.lower():
                metric_category = category
                break
        
        if not metric_category:
            # Default assessment based on confidence
            if confidence < 0.3:
                return AlertSeverity.LOW
            elif confidence < 0.6:
                return AlertSeverity.MEDIUM
            else:
                return AlertSeverity.HIGH
        
        thresholds = risk_thresholds[metric_category]
        
        # Assess based on predicted value and thresholds
        if metric_category in ["response_time", "error_rate"]:
            # Higher values are worse
            if predicted_value > thresholds["critical"]:
                return AlertSeverity.CRITICAL
            elif predicted_value > thresholds["warning"]:
                return AlertSeverity.HIGH
            else:
                return AlertSeverity.LOW if confidence > 0.7 else AlertSeverity.MEDIUM
        else:
            # Lower values are worse (uptime, throughput)
            if predicted_value < thresholds["critical"]:
                return AlertSeverity.CRITICAL
            elif predicted_value < thresholds["warning"]:
                return AlertSeverity.HIGH
            else:
                return AlertSeverity.LOW if confidence > 0.7 else AlertSeverity.MEDIUM
        
    async def _identify_contributing_factors(self, metric_name: str, 
                                           values: List[float]) -> List[str]:
        """Identify factors contributing to prediction"""
        factors = []
        
        # Trend analysis
        if len(values) >= 5:
            recent_trend = statistics.mean(values[-5:]) - statistics.mean(values[-10:-5]) if len(values) >= 10 else 0
            
            if abs(recent_trend) > 0.1:
                direction = "increasing" if recent_trend > 0 else "decreasing"
                factors.append(f"Recent {direction} trend detected")
        
        # Volatility analysis
        if len(values) >= 10:
            recent_std = statistics.stdev(values[-10:])
            overall_std = statistics.stdev(values)
            
            if recent_std > overall_std * 1.5:
                factors.append("Increased volatility in recent measurements")
        
        # Seasonality detection (simplified)
        if len(values) >= 24:
            hourly_avg = {}
            for i, value in enumerate(values[-24:]):
                hour = i % 24
                if hour not in hourly_avg:
                    hourly_avg[hour] = []
                hourly_avg[hour].append(value)
            
            hourly_means = {h: statistics.mean(vals) for h, vals in hourly_avg.items()}
            if len(hourly_means) > 1:
                variance = statistics.variance(hourly_means.values())
                if variance > statistics.variance(values) * 0.5:
                    factors.append("Potential seasonal pattern detected")
        
        # Default factors if none identified
        if not factors:
            factors.append("Historical performance patterns")
        
        return factors
        
    async def _identify_anomaly_factors(self, metric_name: str, current_value: float, 
                                      timestamp: datetime) -> List[str]:
        """Identify factors contributing to anomaly"""
        factors = []
        
        # Time-based factors
        hour = timestamp.hour
        if hour < 6 or hour > 22:
            factors.append("Off-peak hours")
        elif 9 <= hour <= 17:
            factors.append("Peak business hours")
        
        # Day of week
        weekday = timestamp.weekday()
        if weekday >= 5:  # Weekend
            factors.append("Weekend traffic pattern")
        
        # Recent data pattern
        if metric_name in self.historical_data:
            recent_values = [dp['value'] for dp in list(self.historical_data[metric_name])[-10:]]
            if len(recent_values) >= 3:
                recent_mean = statistics.mean(recent_values[:-1])
                if abs(current_value - recent_mean) > statistics.stdev(recent_values) * 2:
                    factors.append("Sudden deviation from recent pattern")
        
        if not factors:
            factors.append("Unknown external factors")
        
        return factors
        
    async def _generate_prediction_recommendations(self, metric_name: str, 
                                                 predicted_value: float,
                                                 risk_level: AlertSeverity,
                                                 factors: List[str]) -> List[str]:
        """Generate recommendations based on prediction"""
        recommendations = []
        
        if risk_level in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            recommendations.append("Implement proactive monitoring and alerting")
            
            if "response_time" in metric_name.lower():
                recommendations.extend([
                    "Scale infrastructure resources preemptively",
                    "Optimize database queries and API endpoints",
                    "Enable performance caching mechanisms"
                ])
            
            elif "uptime" in metric_name.lower():
                recommendations.extend([
                    "Schedule maintenance window to prevent downtime",
                    "Verify backup systems and failover procedures",
                    "Monitor critical system dependencies"
                ])
            
            elif "throughput" in metric_name.lower():
                recommendations.extend([
                    "Prepare auto-scaling policies",
                    "Monitor load balancer configuration",
                    "Review rate limiting policies"
                ])
        
        elif risk_level == AlertSeverity.MEDIUM:
            recommendations.extend([
                "Monitor metric closely for trend confirmation",
                "Prepare contingency plans for potential issues",
                "Review recent system changes"
            ])
        
        # Add factor-specific recommendations
        for factor in factors:
            if "trend" in factor.lower():
                recommendations.append("Investigate root cause of trending behavior")
            elif "volatility" in factor.lower():
                recommendations.append("Implement smoothing mechanisms to reduce volatility")
            elif "seasonal" in factor.lower():
                recommendations.append("Adjust capacity planning for seasonal patterns")
        
        return recommendations
        
    async def _generate_anomaly_actions(self, metric_name: str, anomaly_type: str, 
                                      severity: AlertSeverity) -> List[str]:
        """Generate suggested actions for anomaly"""
        actions = []
        
        if severity == AlertSeverity.CRITICAL:
            actions.append("IMMEDIATE: Investigate and take corrective action")
            actions.append("Notify operations team and stakeholders")
        
        if anomaly_type == "spike":
            actions.extend([
                "Check for system overload or traffic surge",
                "Verify auto-scaling is functioning",
                "Monitor for cascading effects"
            ])
        elif anomaly_type == "drop":
            actions.extend([
                "Check for system failures or outages",
                "Verify data collection integrity",
                "Review recent deployments or changes"
            ])
        
        actions.append("Document incident for trend analysis")
        
        return actions
        
    async def get_prediction_summary(self, hours_ahead: int = 24) -> Dict[str, Any]:
        """Get summary of all current predictions"""
        cutoff_time = datetime.now() - timedelta(hours=1)  # Recent predictions only
        
        recent_predictions = [
            p for p in self.predictions
            if p.prediction_timestamp >= cutoff_time
        ]
        
        # Group by risk level
        risk_distribution = defaultdict(int)
        for pred in recent_predictions:
            risk_distribution[pred.risk_level.value] += 1
        
        # Get high-risk metrics
        high_risk_predictions = [
            p for p in recent_predictions
            if p.risk_level in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]
        ]
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "prediction_summary": {
                "total_predictions": len(recent_predictions),
                "risk_distribution": dict(risk_distribution),
                "high_risk_metrics": len(high_risk_predictions),
                "average_confidence": statistics.mean([
                    p.confidence_score for p in recent_predictions
                ]) if recent_predictions else 0
            },
            "high_risk_alerts": [
                {
                    "metric": p.metric_name,
                    "current_value": p.current_value,
                    "predicted_value": p.predicted_value,
                    "risk_level": p.risk_level.value,
                    "confidence": p.confidence_score,
                    "recommendations": p.recommendations[:3]  # Top 3
                }
                for p in high_risk_predictions[:10]  # Top 10
            ],
            "recent_anomalies": [
                {
                    "metric": a.metric_name,
                    "anomaly_score": a.anomaly_score,
                    "severity": a.severity.value,
                    "detection_time": a.detection_timestamp.isoformat()
                }
                for a in list(self.anomalies)[-10:]  # Last 10 anomalies
            ]
        }
        
        return summary
        
    async def optimize_prediction_models(self):
        """Optimize prediction model parameters based on performance"""
        # Evaluate model performance
        for metric_name in self.historical_data.keys():
            if len(self.historical_data[metric_name]) >= 50:
                accuracy = await self._evaluate_model_accuracy(metric_name)
                self.model_performance[metric_name]["accuracy"] = accuracy
                
                # Adjust parameters based on performance
                if accuracy < 0.6:
                    # Increase smoothing for poor performance
                    self.model_params["smoothing_alpha"] = min(0.5, self.model_params["smoothing_alpha"] + 0.1)
                elif accuracy > 0.8:
                    # Decrease smoothing for good performance
                    self.model_params["smoothing_alpha"] = max(0.1, self.model_params["smoothing_alpha"] - 0.05)
        
        self.logger.info("Prediction model parameters optimized")
        
    async def _evaluate_model_accuracy(self, metric_name: str) -> float:
        """Evaluate prediction model accuracy"""
        values = [dp['value'] for dp in self.historical_data[metric_name]]
        
        if len(values) < 20:
            return 0.5  # Default accuracy for insufficient data
        
        # Use last 20% of data for testing
        split_point = int(len(values) * 0.8)
        train_data = values[:split_point]
        test_data = values[split_point:]
        
        errors = []
        
        # Test predictions
        for i in range(len(test_data)):
            if i == 0:
                continue  # Skip first test point
            
            # Make prediction using training data + previous test points
            prediction_data = train_data + test_data[:i]
            predicted, _ = await self._moving_average_prediction(
                prediction_data, ForecastHorizon.NEXT_HOUR
            )
            
            actual = test_data[i]
            error = abs(predicted - actual) / max(actual, 1)  # Relative error
            errors.append(error)
        
        # Calculate accuracy (1 - mean error)
        mean_error = statistics.mean(errors) if errors else 1.0
        accuracy = max(0, 1 - mean_error)
        
        return accuracy

# Global SLA predictive analytics instance
sla_predictive_analytics = SLAPredictiveAnalytics()