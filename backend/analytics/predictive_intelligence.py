"""
🤖 Predictive Intelligence - ML-powered Analytics and Forecasting
Enterprise-grade predictive analytics with machine learning capabilities

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class PredictionModel(Enum):
    """Types of prediction models"""
    LINEAR_REGRESSION = "linear_regression"
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    TREND_ANALYSIS = "trend_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"


class TrendDirection(Enum):
    """Trend direction indicators"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class PredictionResult:
    """Prediction result data structure"""
    model: PredictionModel
    predicted_value: float
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    is_anomaly: bool
    anomaly_score: float
    expected_value: float
    actual_value: float
    timestamp: datetime
    severity: str  # "low", "medium", "high"


@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    direction: TrendDirection
    slope: float
    confidence: float
    start_value: float
    end_value: float
    data_points: int


class PredictiveAnalytics:
    """
    Predictive analytics engine with ML capabilities
    """
    
    def __init__(self):
        """Initialize predictive analytics"""
        self.predictions_history: List[PredictionResult] = []
        self.anomalies_detected: List[AnomalyDetection] = []
        self.training_data: Dict[str, List[float]] = defaultdict(list)
        self.models_cache: Dict[str, Any] = {}
        
        logger.info("🤖 Predictive Analytics initialized")
    
    def predict(self, data: List[float], model: PredictionModel = PredictionModel.LINEAR_REGRESSION, 
                steps_ahead: int = 1) -> PredictionResult:
        """
        Make predictions based on historical data
        
        Args:
            data: Historical data points
            model: Prediction model to use
            steps_ahead: Number of steps to predict ahead
            
        Returns:
            PredictionResult: Prediction result with confidence
        """
        if not data or len(data) < 2:
            logger.warning("⚠️ Insufficient data for prediction")
            return PredictionResult(
                model=model,
                predicted_value=data[-1] if data else 0.0,
                confidence=0.0,
                timestamp=datetime.utcnow(),
                metadata={"error": "insufficient_data"}
            )
        
        if model == PredictionModel.LINEAR_REGRESSION:
            predicted_value, confidence = self._linear_regression_predict(data, steps_ahead)
        elif model == PredictionModel.MOVING_AVERAGE:
            predicted_value, confidence = self._moving_average_predict(data, steps_ahead)
        elif model == PredictionModel.EXPONENTIAL_SMOOTHING:
            predicted_value, confidence = self._exponential_smoothing_predict(data, steps_ahead)
        else:
            predicted_value, confidence = self._linear_regression_predict(data, steps_ahead)
        
        result = PredictionResult(
            model=model,
            predicted_value=predicted_value,
            confidence=confidence,
            timestamp=datetime.utcnow(),
            metadata={
                "data_points": len(data),
                "steps_ahead": steps_ahead,
                "last_value": data[-1]
            }
        )
        
        self.predictions_history.append(result)
        return result
    
    def detect_anomalies(self, data: List[float], threshold: float = 2.0) -> List[AnomalyDetection]:
        """
        Detect anomalies in data using statistical methods
        
        Args:
            data: Data points to analyze
            threshold: Standard deviation threshold for anomaly detection
            
        Returns:
            List[AnomalyDetection]: Detected anomalies
        """
        if len(data) < 5:
            return []
        
        anomalies = []
        mean = np.mean(data)
        std = np.std(data)
        
        for i, value in enumerate(data):
            z_score = abs((value - mean) / std) if std > 0 else 0
            is_anomaly = z_score > threshold
            
            if is_anomaly:
                severity = "high" if z_score > 3 else "medium" if z_score > 2.5 else "low"
                anomaly = AnomalyDetection(
                    is_anomaly=True,
                    anomaly_score=z_score,
                    expected_value=mean,
                    actual_value=value,
                    timestamp=datetime.utcnow(),
                    severity=severity
                )
                anomalies.append(anomaly)
                logger.warning(f"🚨 Anomaly detected: score={z_score:.2f}, value={value:.2f}, expected={mean:.2f}")
        
        self.anomalies_detected.extend(anomalies)
        return anomalies
    
    def analyze_trend(self, data: List[float], window_size: Optional[int] = None) -> TrendAnalysis:
        """
        Analyze trend in time series data
        
        Args:
            data: Time series data
            window_size: Optional window size for trend analysis
            
        Returns:
            TrendAnalysis: Trend analysis result
        """
        if len(data) < 2:
            return TrendAnalysis(
                direction=TrendDirection.STABLE,
                slope=0.0,
                confidence=0.0,
                start_value=data[0] if data else 0.0,
                end_value=data[-1] if data else 0.0,
                data_points=len(data)
            )
        
        # Calculate linear regression slope
        x = np.arange(len(data))
        y = np.array(data)
        
        # Linear regression: y = mx + b
        n = len(data)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x ** 2)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
        
        # Calculate R² (coefficient of determination) as confidence
        y_mean = np.mean(y)
        ss_tot = np.sum((y - y_mean) ** 2)
        y_pred = slope * x + (sum_y - slope * sum_x) / n
        ss_res = np.sum((y - y_pred) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Determine trend direction
        if abs(slope) < 0.01:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING
        
        # Check volatility
        std = np.std(data)
        mean = np.mean(data)
        cv = (std / mean) if mean != 0 else 0
        if cv > 0.5:
            direction = TrendDirection.VOLATILE
        
        return TrendAnalysis(
            direction=direction,
            slope=float(slope),
            confidence=float(r_squared),
            start_value=float(data[0]),
            end_value=float(data[-1]),
            data_points=len(data)
        )
    
    def forecast(self, metric_name: str, data: List[float], periods: int = 5) -> Dict[str, Any]:
        """
        Forecast future values for a metric
        
        Args:
            metric_name: Name of the metric
            data: Historical data
            periods: Number of periods to forecast
            
        Returns:
            Dict: Forecast results with multiple models
        """
        forecasts = {}
        
        # Linear regression forecast
        lr_result = self.predict(data, PredictionModel.LINEAR_REGRESSION, periods)
        forecasts["linear_regression"] = {
            "value": lr_result.predicted_value,
            "confidence": lr_result.confidence
        }
        
        # Moving average forecast
        ma_result = self.predict(data, PredictionModel.MOVING_AVERAGE, periods)
        forecasts["moving_average"] = {
            "value": ma_result.predicted_value,
            "confidence": ma_result.confidence
        }
        
        # Exponential smoothing forecast
        es_result = self.predict(data, PredictionModel.EXPONENTIAL_SMOOTHING, periods)
        forecasts["exponential_smoothing"] = {
            "value": es_result.predicted_value,
            "confidence": es_result.confidence
        }
        
        # Ensemble forecast (weighted average)
        weights = [lr_result.confidence, ma_result.confidence, es_result.confidence]
        total_weight = sum(weights)
        if total_weight > 0:
            ensemble_value = (
                lr_result.predicted_value * weights[0] +
                ma_result.predicted_value * weights[1] +
                es_result.predicted_value * weights[2]
            ) / total_weight
            ensemble_confidence = total_weight / 3
        else:
            ensemble_value = np.mean([lr_result.predicted_value, ma_result.predicted_value, es_result.predicted_value])
            ensemble_confidence = 0.5
        
        forecasts["ensemble"] = {
            "value": ensemble_value,
            "confidence": ensemble_confidence
        }
        
        return {
            "metric": metric_name,
            "periods_ahead": periods,
            "forecasts": forecasts,
            "recommended": "ensemble",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_insights(self, data: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        Get comprehensive insights from multiple metrics
        
        Args:
            data: Dictionary of metric names to data lists
            
        Returns:
            Dict: Comprehensive insights
        """
        insights = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_analyzed": len(data),
            "trends": {},
            "anomalies": {},
            "forecasts": {},
            "recommendations": []
        }
        
        for metric_name, values in data.items():
            if len(values) < 2:
                continue
            
            # Trend analysis
            trend = self.analyze_trend(values)
            insights["trends"][metric_name] = {
                "direction": trend.direction.value,
                "slope": trend.slope,
                "confidence": trend.confidence
            }
            
            # Anomaly detection
            anomalies = self.detect_anomalies(values)
            if anomalies:
                insights["anomalies"][metric_name] = len(anomalies)
            
            # Forecast
            forecast = self.forecast(metric_name, values, periods=3)
            insights["forecasts"][metric_name] = forecast["forecasts"]["ensemble"]
            
            # Generate recommendations
            if trend.direction == TrendDirection.INCREASING and "error" in metric_name.lower():
                insights["recommendations"].append(f"⚠️ {metric_name} is increasing - investigate error sources")
            elif trend.direction == TrendDirection.VOLATILE:
                insights["recommendations"].append(f"📊 {metric_name} is volatile - consider stabilization measures")
        
        return insights
    
    def _linear_regression_predict(self, data: List[float], steps: int) -> Tuple[float, float]:
        """Linear regression prediction"""
        x = np.arange(len(data))
        y = np.array(data)
        
        # Calculate linear regression coefficients
        n = len(data)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x ** 2)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
        intercept = (sum_y - slope * sum_x) / n
        
        # Predict
        predicted_value = slope * (len(data) + steps - 1) + intercept
        
        # Calculate R² as confidence
        y_mean = np.mean(y)
        ss_tot = np.sum((y - y_mean) ** 2)
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        confidence = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return float(predicted_value), float(max(0, min(1, confidence)))
    
    def _moving_average_predict(self, data: List[float], steps: int, window: int = 5) -> Tuple[float, float]:
        """Moving average prediction"""
        window = min(window, len(data))
        recent_data = data[-window:]
        predicted_value = np.mean(recent_data)
        
        # Confidence based on variance
        variance = np.var(recent_data)
        confidence = 1 / (1 + variance) if variance > 0 else 0.8
        
        return float(predicted_value), float(min(1, confidence))
    
    def _exponential_smoothing_predict(self, data: List[float], steps: int, alpha: float = 0.3) -> Tuple[float, float]:
        """Exponential smoothing prediction"""
        smoothed = [data[0]]
        for i in range(1, len(data)):
            smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[-1])
        
        predicted_value = smoothed[-1]
        
        # Confidence based on smoothing stability
        recent_variance = np.var(data[-5:]) if len(data) >= 5 else np.var(data)
        confidence = 1 / (1 + recent_variance) if recent_variance > 0 else 0.7
        
        return float(predicted_value), float(min(1, confidence))


# Global predictive analytics instance
_global_predictive_analytics: Optional[PredictiveAnalytics] = None


def get_predictive_analytics() -> PredictiveAnalytics:
    """
    Get global predictive analytics instance
    
    Returns:
        PredictiveAnalytics: Global predictive analytics
    """
    global _global_predictive_analytics
    if _global_predictive_analytics is None:
        _global_predictive_analytics = PredictiveAnalytics()
    return _global_predictive_analytics


# Auto-initialize
_global_predictive_analytics = PredictiveAnalytics()

logger.info("🤖 Predictive Intelligence module initialized")
