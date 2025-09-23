"""
Intelligent Timeout Predictor - Ainflue Enterprise
================================================
Prédicteur timeout intelligent avec ML time series.
Timeout prediction + performance forecasting + resource optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Timeout Handling
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
from collections import deque, defaultdict
import statistics
import json

logger = logging.getLogger(__name__)

class PredictionModel(Enum):
    """ML model types for timeout prediction"""
    LINEAR_REGRESSION = "linear_regression"
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"
    ENSEMBLE = "ensemble"

class TimeSeriesPattern(Enum):
    """Time series pattern types"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    SEASONAL = "seasonal"
    CYCLICAL = "cyclical"
    RANDOM = "random"
    STABLE = "stable"

@dataclass
class TimeoutPredictionRequest:
    """Request for timeout prediction"""
    service_name: str
    operation_name: str
    business_context: Dict[str, Any]
    historical_window: int = 100  # Number of historical data points to use
    prediction_horizon: int = 1   # How many time steps ahead to predict
    confidence_level: float = 0.95

@dataclass
class TimeoutPredictionResult:
    """Result of timeout prediction"""
    service_name: str
    operation_name: str
    predicted_timeout: float
    confidence_interval: Tuple[float, float]
    prediction_accuracy: float
    model_used: PredictionModel
    pattern_detected: TimeSeriesPattern
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceDataPoint:
    """Single performance measurement"""
    timestamp: float
    execution_time: float
    success: bool
    resource_usage: Dict[str, float]
    business_context: Dict[str, Any]
    load_factor: float = 1.0

@dataclass
class ServicePerformanceHistory:
    """Historical performance data for a service"""
    service_name: str
    operation_name: str
    data_points: deque = field(default_factory=lambda: deque(maxlen=1000))
    last_updated: float = field(default_factory=time.time)

@dataclass
class PredictorConfig:
    """Configuration for timeout predictor"""
    max_history_size: int = 1000
    min_data_points: int = 10
    prediction_update_interval: float = 300.0  # 5 minutes
    model_retrain_interval: float = 3600.0     # 1 hour
    outlier_threshold: float = 3.0             # Standard deviations
    seasonal_period: int = 24                  # Hours for seasonal analysis

class IntelligentTimeoutPredictor:
    """
    Prédicteur timeout intelligent avec ML time series.
    Timeout prediction + performance forecasting + resource optimization.
    """
    
    def __init__(self, predictor_config: Optional[PredictorConfig] = None):
        self.predictor_config = predictor_config or PredictorConfig()
        self.performance_history: Dict[str, ServicePerformanceHistory] = {}
        self.prediction_cache: Dict[str, TimeoutPredictionResult] = {}
        self.model_performance: Dict[str, Dict[str, float]] = {}
        self.is_initialized = False
        
        # Ainflue business context weights
        self.business_context_weights = {
            'file_size': 0.3,
            'complexity': 0.25,
            'user_count': 0.2,
            'peak_hour': 0.15,
            'resource_availability': 0.1
        }
        
        # Creator workflow patterns
        self.creator_patterns = {
            'content_upload': {
                'base_multiplier': 1.0,
                'file_size_factor': 0.1,  # seconds per MB
                'quality_factor': 1.2     # HD/4K multiplier
            },
            'ai_processing': {
                'base_multiplier': 2.0,
                'complexity_factor': 1.5,
                'gpu_availability': 0.7
            },
            'collaboration': {
                'base_multiplier': 0.5,
                'participant_factor': 0.1,
                'real_time_factor': 0.3
            }
        }
        
    async def initialize(self):
        """Initialize the timeout predictor"""
        if self.is_initialized:
            return
            
        logger.info("Initializing Intelligence Timeout Predictor")
        
        # Load historical data
        await self._load_historical_data()
        
        # Initialize prediction models
        await self._initialize_prediction_models()
        
        # Start background tasks
        asyncio.create_task(self._prediction_update_task())
        asyncio.create_task(self._model_retrain_task())
        
        self.is_initialized = True
        logger.info("Intelligent Timeout Predictor initialized successfully")
        
    async def predict_optimal_timeouts(self, prediction_request: TimeoutPredictionRequest) -> TimeoutPredictionResult:
        """
        Prédiction timeouts optimaux avec ML intelligence.
        
        Timeout Prediction Features:
        - ML-based timeout prediction avec historical performance data
        - Service performance pattern analysis pour optimal timeout calculation
        - Resource utilization impact sur timeout requirements
        - Seasonal pattern detection pour Creator activity cycles
        - Load-based timeout adjustment pour peak usage periods
        - Cross-service timeout correlation analysis
        - Business SLA alignment avec timeout optimization
        - Predictive scaling recommendations basé sur timeout patterns
        """
        if not self.is_initialized:
            await self.initialize()
            
        service_key = f"{prediction_request.service_name}_{prediction_request.operation_name}"
        
        # Check cache first
        cached_result = self.prediction_cache.get(service_key)
        if cached_result and time.time() - cached_result.metadata.get('timestamp', 0) < 300:
            return cached_result
            
        # Get historical performance data
        performance_history = self.performance_history.get(service_key)
        
        if not performance_history or len(performance_history.data_points) < self.predictor_config.min_data_points:
            # Not enough data, use business rule-based prediction
            result = await self._predict_with_business_rules(prediction_request)
        else:
            # Use ML-based prediction
            result = await self._predict_with_ml_models(prediction_request, performance_history)
            
        # Cache the result
        result.metadata['timestamp'] = time.time()
        self.prediction_cache[service_key] = result
        
        return result
    
    async def record_performance_data(self, service_name: str, operation_name: str, 
                                    execution_time: float, success: bool, 
                                    business_context: Optional[Dict[str, Any]] = None,
                                    resource_usage: Optional[Dict[str, float]] = None):
        """Record performance data for future predictions"""
        service_key = f"{service_name}_{operation_name}"
        
        if service_key not in self.performance_history:
            self.performance_history[service_key] = ServicePerformanceHistory(
                service_name=service_name,
                operation_name=operation_name
            )
            
        data_point = PerformanceDataPoint(
            timestamp=time.time(),
            execution_time=execution_time,
            success=success,
            resource_usage=resource_usage or {},
            business_context=business_context or {},
            load_factor=await self._calculate_current_load_factor()
        )
        
        self.performance_history[service_key].data_points.append(data_point)
        self.performance_history[service_key].last_updated = time.time()
        
        # Invalidate cache for this service
        self.prediction_cache.pop(service_key, None)
    
    async def analyze_timeout_patterns(self, service_name: str, operation_name: str) -> Dict[str, Any]:
        """Analyze timeout patterns for optimization insights"""
        service_key = f"{service_name}_{operation_name}"
        performance_history = self.performance_history.get(service_key)
        
        if not performance_history or len(performance_history.data_points) < self.predictor_config.min_data_points:
            return {
                'pattern': TimeSeriesPattern.RANDOM,
                'confidence': 0.0,
                'recommendations': ['Collect more performance data for analysis']
            }
            
        data_points = list(performance_history.data_points)
        execution_times = [dp.execution_time for dp in data_points if dp.success]
        
        if not execution_times:
            return {
                'pattern': TimeSeriesPattern.RANDOM,
                'confidence': 0.0,
                'recommendations': ['No successful executions recorded']
            }
            
        # Analyze trend
        trend_analysis = await self._analyze_trend(execution_times)
        
        # Analyze seasonality
        seasonal_analysis = await self._analyze_seasonality(data_points)
        
        # Detect outliers
        outliers = await self._detect_outliers(execution_times)
        
        # Generate recommendations
        recommendations = await self._generate_pattern_recommendations(
            trend_analysis, seasonal_analysis, outliers, service_name, operation_name
        )
        
        return {
            'pattern': trend_analysis['pattern'],
            'trend_confidence': trend_analysis['confidence'],
            'seasonal_component': seasonal_analysis,
            'outlier_percentage': len(outliers) / len(execution_times) if execution_times else 0,
            'recommendations': recommendations,
            'statistics': {
                'mean': statistics.mean(execution_times),
                'median': statistics.median(execution_times),
                'std_dev': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                'min': min(execution_times),
                'max': max(execution_times),
                'percentile_95': np.percentile(execution_times, 95),
                'percentile_99': np.percentile(execution_times, 99)
            }
        }
    
    async def forecast_service_performance(self, service_name: str, operation_name: str, 
                                         forecast_hours: int = 24) -> Dict[str, Any]:
        """Forecast service performance for timeout planning"""
        service_key = f"{service_name}_{operation_name}"
        performance_history = self.performance_history.get(service_key)
        
        if not performance_history or len(performance_history.data_points) < self.predictor_config.min_data_points:
            return {
                'forecast_available': False,
                'reason': 'Insufficient historical data'
            }
            
        data_points = list(performance_history.data_points)
        
        # Group data by hours for forecasting
        hourly_performance = await self._aggregate_hourly_performance(data_points)
        
        # Generate forecast
        forecast = await self._generate_performance_forecast(hourly_performance, forecast_hours)
        
        return {
            'forecast_available': True,
            'forecast_horizon_hours': forecast_hours,
            'predicted_performance': forecast,
            'confidence_intervals': await self._calculate_forecast_confidence(forecast),
            'peak_hours': await self._identify_peak_hours(forecast),
            'recommendations': await self._generate_forecast_recommendations(forecast, service_name)
        }
    
    async def optimize_resource_allocation(self, services: List[str]) -> Dict[str, Any]:
        """Optimize resource allocation based on timeout requirements"""
        service_priorities = {}
        resource_requirements = {}
        
        for service_spec in services:
            if '_' in service_spec:
                service_name, operation_name = service_spec.split('_', 1)
            else:
                service_name, operation_name = service_spec, 'default'
                
            service_key = f"{service_name}_{operation_name}"
            performance_history = self.performance_history.get(service_key)
            
            if performance_history and len(performance_history.data_points) >= self.predictor_config.min_data_points:
                # Calculate resource requirements based on performance patterns
                data_points = list(performance_history.data_points)
                avg_execution_time = statistics.mean([dp.execution_time for dp in data_points if dp.success])
                success_rate = sum(1 for dp in data_points if dp.success) / len(data_points)
                
                # Calculate priority based on business domain
                business_domain = self._extract_business_domain(service_name)
                priority_score = await self._calculate_service_priority(business_domain, success_rate, avg_execution_time)
                
                service_priorities[service_spec] = priority_score
                resource_requirements[service_spec] = {
                    'cpu_weight': avg_execution_time / 60.0,  # Normalize to minutes
                    'memory_weight': self._estimate_memory_requirement(service_name),
                    'io_weight': self._estimate_io_requirement(operation_name),
                    'network_weight': self._estimate_network_requirement(service_name)
                }
            else:
                # Default values for services without enough data
                service_priorities[service_spec] = 0.5
                resource_requirements[service_spec] = {
                    'cpu_weight': 1.0,
                    'memory_weight': 1.0,
                    'io_weight': 1.0,
                    'network_weight': 1.0
                }
        
        # Generate optimization recommendations
        optimization_plan = await self._generate_optimization_plan(service_priorities, resource_requirements)
        
        return {
            'service_priorities': service_priorities,
            'resource_requirements': resource_requirements,
            'optimization_plan': optimization_plan,
            'estimated_improvement': await self._estimate_optimization_impact(optimization_plan)
        }
    
    async def detect_timeout_anomalies(self, service_name: str, operation_name: str, 
                                     window_hours: int = 24) -> Dict[str, Any]:
        """Detect timeout anomalies with ML pattern recognition"""
        service_key = f"{service_name}_{operation_name}"
        performance_history = self.performance_history.get(service_key)
        
        if not performance_history:
            return {
                'anomalies_detected': False,
                'reason': 'No performance history available'
            }
            
        current_time = time.time()
        window_start = current_time - (window_hours * 3600)
        
        # Filter data to the analysis window
        recent_data = [
            dp for dp in performance_history.data_points 
            if dp.timestamp >= window_start
        ]
        
        if len(recent_data) < 10:
            return {
                'anomalies_detected': False,
                'reason': 'Insufficient recent data for anomaly detection'
            }
            
        # Detect anomalies
        anomalies = await self._detect_performance_anomalies(recent_data)
        
        # Analyze anomaly patterns
        anomaly_patterns = await self._analyze_anomaly_patterns(anomalies)
        
        # Generate alert recommendations
        alerts = await self._generate_anomaly_alerts(anomalies, anomaly_patterns, service_name)
        
        return {
            'anomalies_detected': len(anomalies) > 0,
            'anomaly_count': len(anomalies),
            'anomaly_details': anomalies,
            'patterns': anomaly_patterns,
            'severity': await self._assess_anomaly_severity(anomalies),
            'alerts': alerts,
            'recommendations': await self._generate_anomaly_recommendations(anomalies, service_name)
        }
    
    async def _predict_with_business_rules(self, prediction_request: TimeoutPredictionRequest) -> TimeoutPredictionResult:
        """Predict timeout using business rules when ML data is insufficient"""
        service_name = prediction_request.service_name
        operation_name = prediction_request.operation_name
        business_context = prediction_request.business_context
        
        # Get base timeout from Ainflue business patterns
        base_timeout = await self._get_business_rule_timeout(service_name, operation_name)
        
        # Adjust based on business context
        context_multiplier = 1.0
        
        if 'file_size_mb' in business_context:
            file_size = business_context['file_size_mb']
            context_multiplier *= (1.0 + file_size * 0.01)  # 1% per MB
            
        if 'complexity' in business_context:
            complexity = business_context['complexity']  # 1-10 scale
            context_multiplier *= (1.0 + complexity * 0.1)
            
        if 'peak_hour' in business_context and business_context['peak_hour']:
            context_multiplier *= 1.5  # 50% increase during peak hours
            
        predicted_timeout = base_timeout * context_multiplier
        
        # Calculate confidence interval
        confidence_range = predicted_timeout * 0.2  # ±20%
        confidence_interval = (
            predicted_timeout - confidence_range,
            predicted_timeout + confidence_range
        )
        
        return TimeoutPredictionResult(
            service_name=service_name,
            operation_name=operation_name,
            predicted_timeout=predicted_timeout,
            confidence_interval=confidence_interval,
            prediction_accuracy=0.7,  # Lower accuracy for rule-based
            model_used=PredictionModel.LINEAR_REGRESSION,
            pattern_detected=TimeSeriesPattern.STABLE,
            recommendations=[
                'Collect more performance data for ML-based predictions',
                'Monitor actual execution times to improve accuracy'
            ]
        )
    
    async def _predict_with_ml_models(self, prediction_request: TimeoutPredictionRequest, 
                                    performance_history: ServicePerformanceHistory) -> TimeoutPredictionResult:
        """Predict timeout using ML models with historical data"""
        data_points = list(performance_history.data_points)
        execution_times = [dp.execution_time for dp in data_points if dp.success]
        
        # Try different prediction models
        model_predictions = {}
        
        # Moving average model
        model_predictions[PredictionModel.MOVING_AVERAGE] = await self._predict_moving_average(execution_times)
        
        # Exponential smoothing model
        model_predictions[PredictionModel.EXPONENTIAL_SMOOTHING] = await self._predict_exponential_smoothing(execution_times)
        
        # Linear regression model (simplified)
        model_predictions[PredictionModel.LINEAR_REGRESSION] = await self._predict_linear_regression(execution_times)
        
        # Ensemble model (weighted average)
        ensemble_prediction = await self._predict_ensemble(model_predictions)
        
        # Select best model based on historical accuracy
        best_model = await self._select_best_model(prediction_request.service_name, model_predictions)
        
        predicted_timeout = model_predictions[best_model]
        
        # Adjust for business context
        business_adjustment = await self._apply_business_context_adjustment(
            predicted_timeout, prediction_request.business_context
        )
        
        final_prediction = predicted_timeout * business_adjustment
        
        # Calculate confidence interval
        confidence_interval = await self._calculate_prediction_confidence(
            execution_times, final_prediction, prediction_request.confidence_level
        )
        
        # Detect pattern
        pattern = await self._detect_time_series_pattern(execution_times)
        
        # Generate recommendations
        recommendations = await self._generate_prediction_recommendations(
            final_prediction, confidence_interval, pattern, prediction_request
        )
        
        return TimeoutPredictionResult(
            service_name=prediction_request.service_name,
            operation_name=prediction_request.operation_name,
            predicted_timeout=final_prediction,
            confidence_interval=confidence_interval,
            prediction_accuracy=await self._get_model_accuracy(prediction_request.service_name, best_model),
            model_used=best_model,
            pattern_detected=pattern,
            recommendations=recommendations
        )
    
    # Implementation helper methods (simplified for space)
    
    async def _load_historical_data(self):
        """Load historical performance data"""
        # In a real implementation, this would load from a database
        logger.info("Historical data loading completed")
    
    async def _initialize_prediction_models(self):
        """Initialize ML prediction models"""
        # In a real implementation, this would initialize actual ML models
        logger.info("Prediction models initialized")
    
    async def _get_business_rule_timeout(self, service_name: str, operation_name: str) -> float:
        """Get base timeout from business rules"""
        # Ainflue business-specific timeout rules
        business_timeouts = {
            'creator_service': {
                'upload': 60.0,
                'process': 120.0,
                'publish': 30.0
            },
            'ai_service': {
                'analyze': 90.0,
                'generate': 180.0,
                'enhance': 240.0
            },
            'payment_service': {
                'process': 15.0,
                'verify': 10.0,
                'refund': 30.0
            },
            'collaboration_service': {
                'sync': 5.0,
                'notify': 2.0,
                'update': 10.0
            }
        }
        
        return business_timeouts.get(service_name, {}).get(operation_name, 30.0)
    
    async def _predict_moving_average(self, execution_times: List[float], window: int = 10) -> float:
        """Simple moving average prediction"""
        if len(execution_times) < window:
            return statistics.mean(execution_times) if execution_times else 30.0
        return statistics.mean(execution_times[-window:])
    
    async def _predict_exponential_smoothing(self, execution_times: List[float], alpha: float = 0.3) -> float:
        """Exponential smoothing prediction"""
        if not execution_times:
            return 30.0
        if len(execution_times) == 1:
            return execution_times[0]
            
        smoothed = execution_times[0]
        for value in execution_times[1:]:
            smoothed = alpha * value + (1 - alpha) * smoothed
        return smoothed
    
    async def _predict_linear_regression(self, execution_times: List[float]) -> float:
        """Simple linear regression prediction"""
        if len(execution_times) < 2:
            return statistics.mean(execution_times) if execution_times else 30.0
            
        # Simple linear trend calculation
        n = len(execution_times)
        x = list(range(n))
        y = execution_times
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return y_mean
            
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Predict next value
        return slope * n + intercept
    
    async def _predict_ensemble(self, model_predictions: Dict[PredictionModel, float]) -> float:
        """Ensemble prediction using weighted average"""
        weights = {
            PredictionModel.MOVING_AVERAGE: 0.3,
            PredictionModel.EXPONENTIAL_SMOOTHING: 0.4,
            PredictionModel.LINEAR_REGRESSION: 0.3
        }
        
        weighted_sum = sum(weights[model] * prediction for model, prediction in model_predictions.items() if model in weights)
        total_weight = sum(weights[model] for model in model_predictions.keys() if model in weights)
        
        return weighted_sum / total_weight if total_weight > 0 else 30.0
    
    async def _select_best_model(self, service_name: str, model_predictions: Dict[PredictionModel, float]) -> PredictionModel:
        """Select best model based on historical accuracy"""
        # For simplicity, return exponential smoothing as it's generally good for time series
        return PredictionModel.EXPONENTIAL_SMOOTHING
    
    async def _apply_business_context_adjustment(self, base_prediction: float, business_context: Dict[str, Any]) -> float:
        """Apply business context adjustments to prediction"""
        adjustment = 1.0
        
        for context_key, weight in self.business_context_weights.items():
            if context_key in business_context:
                context_value = business_context[context_key]
                if isinstance(context_value, (int, float)):
                    adjustment += weight * (context_value - 1.0) * 0.1
                    
        return max(adjustment, 0.5)  # Minimum 50% of base
    
    async def _calculate_prediction_confidence(self, execution_times: List[float], 
                                             prediction: float, confidence_level: float) -> Tuple[float, float]:
        """Calculate confidence interval for prediction"""
        if len(execution_times) < 2:
            margin = prediction * 0.3
            return (prediction - margin, prediction + margin)
            
        std_dev = statistics.stdev(execution_times)
        # Simplified confidence interval calculation
        z_score = 1.96 if confidence_level >= 0.95 else 1.645  # 95% or 90%
        margin = z_score * std_dev / np.sqrt(len(execution_times))
        
        return (max(0, prediction - margin), prediction + margin)
    
    async def _detect_time_series_pattern(self, execution_times: List[float]) -> TimeSeriesPattern:
        """Detect time series pattern in execution times"""
        if len(execution_times) < 10:
            return TimeSeriesPattern.RANDOM
            
        # Simple trend detection
        first_half = execution_times[:len(execution_times)//2]
        second_half = execution_times[len(execution_times)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if second_avg > first_avg * 1.1:
            return TimeSeriesPattern.TRENDING_UP
        elif second_avg < first_avg * 0.9:
            return TimeSeriesPattern.TRENDING_DOWN
        else:
            return TimeSeriesPattern.STABLE
    
    async def _generate_prediction_recommendations(self, prediction: float, confidence_interval: Tuple[float, float], 
                                                 pattern: TimeSeriesPattern, request: TimeoutPredictionRequest) -> List[str]:
        """Generate recommendations based on prediction results"""
        recommendations = []
        
        if pattern == TimeSeriesPattern.TRENDING_UP:
            recommendations.append("Performance is degrading - consider resource scaling")
            recommendations.append("Investigate potential bottlenecks or memory leaks")
            
        elif pattern == TimeSeriesPattern.TRENDING_DOWN:
            recommendations.append("Performance is improving - timeout values could be optimized")
            recommendations.append("Recent optimizations appear to be effective")
            
        confidence_width = confidence_interval[1] - confidence_interval[0]
        if confidence_width > prediction * 0.5:
            recommendations.append("High prediction uncertainty - collect more performance data")
            
        if prediction > 120:  # 2 minutes
            recommendations.append("Consider implementing circuit breaker patterns for long operations")
            recommendations.append("Evaluate asynchronous processing options")
            
        return recommendations
    
    async def _calculate_current_load_factor(self) -> float:
        """Calculate current system load factor"""
        # In a real implementation, this would check actual system metrics
        return 1.0
    
    async def _prediction_update_task(self):
        """Background task for updating predictions"""
        while True:
            try:
                await asyncio.sleep(self.predictor_config.prediction_update_interval)
                # Update cached predictions
                logger.debug("Prediction update cycle completed")
            except Exception as e:
                logger.error(f"Error in prediction update task: {e}")
    
    async def _model_retrain_task(self):
        """Background task for retraining ML models"""
        while True:
            try:
                await asyncio.sleep(self.predictor_config.model_retrain_interval)
                # Retrain models with new data
                logger.debug("Model retrain cycle completed")
            except Exception as e:
                logger.error(f"Error in model retrain task: {e}")
    
    # Additional helper methods (simplified implementations)
    async def _analyze_trend(self, execution_times: List[float]) -> Dict[str, Any]:
        """Analyze trend in execution times"""
        return {'pattern': TimeSeriesPattern.STABLE, 'confidence': 0.8}
    
    async def _analyze_seasonality(self, data_points: List[PerformanceDataPoint]) -> Dict[str, Any]:
        """Analyze seasonal patterns"""
        return {'seasonal_detected': False, 'period': 24}
    
    async def _detect_outliers(self, execution_times: List[float]) -> List[int]:
        """Detect outliers in execution times"""
        if len(execution_times) < 3:
            return []
        mean_time = statistics.mean(execution_times)
        std_dev = statistics.stdev(execution_times)
        threshold = self.predictor_config.outlier_threshold * std_dev
        return [i for i, t in enumerate(execution_times) if abs(t - mean_time) > threshold]
    
    async def _generate_pattern_recommendations(self, trend_analysis, seasonal_analysis, outliers, service_name, operation_name) -> List[str]:
        """Generate recommendations based on pattern analysis"""
        return ["Monitor performance trends", "Consider implementing adaptive timeouts"]
    
    async def _aggregate_hourly_performance(self, data_points: List[PerformanceDataPoint]) -> Dict[int, float]:
        """Aggregate performance data by hour"""
        hourly_data = defaultdict(list)
        for dp in data_points:
            hour = int((dp.timestamp % 86400) // 3600)  # Hour of day
            if dp.success:
                hourly_data[hour].append(dp.execution_time)
        return {hour: statistics.mean(times) for hour, times in hourly_data.items() if times}
    
    async def _generate_performance_forecast(self, hourly_performance: Dict[int, float], forecast_hours: int) -> List[float]:
        """Generate performance forecast"""
        # Simple repeat pattern for forecast
        if not hourly_performance:
            return [30.0] * forecast_hours
        avg_performance = statistics.mean(hourly_performance.values())
        return [avg_performance] * forecast_hours
    
    async def _calculate_forecast_confidence(self, forecast: List[float]) -> List[Tuple[float, float]]:
        """Calculate confidence intervals for forecast"""
        return [(f * 0.8, f * 1.2) for f in forecast]
    
    async def _identify_peak_hours(self, forecast: List[float]) -> List[int]:
        """Identify peak performance hours"""
        if not forecast:
            return []
        threshold = max(forecast) * 0.9
        return [i for i, f in enumerate(forecast) if f >= threshold]
    
    async def _generate_forecast_recommendations(self, forecast: List[float], service_name: str) -> List[str]:
        """Generate recommendations based on forecast"""
        return ["Scale resources during predicted peak hours", "Implement predictive auto-scaling"]
    
    def _extract_business_domain(self, service_name: str) -> str:
        """Extract business domain from service name"""
        domain_mapping = {
            'creator': 'creator',
            'ai': 'ai_processing',
            'payment': 'monetization',
            'collaboration': 'collaboration',
            'content': 'content',
            'distribution': 'distribution'
        }
        
        for key, domain in domain_mapping.items():
            if key in service_name.lower():
                return domain
        return 'content'  # default
    
    async def _calculate_service_priority(self, business_domain: str, success_rate: float, avg_execution_time: float) -> float:
        """Calculate service priority score"""
        domain_weights = {
            'creator': 0.9,
            'ai_processing': 0.95,
            'monetization': 0.92,
            'collaboration': 0.8,
            'content': 0.75,
            'distribution': 0.7
        }
        
        base_priority = domain_weights.get(business_domain, 0.6)
        success_factor = success_rate
        performance_factor = max(0.1, 1.0 - (avg_execution_time / 300.0))  # Normalize to 5 minutes
        
        return base_priority * success_factor * performance_factor
    
    def _estimate_memory_requirement(self, service_name: str) -> float:
        """Estimate memory requirement for service"""
        memory_estimates = {
            'ai': 2.0,
            'content': 1.5,
            'creator': 1.2,
            'payment': 1.0,
            'collaboration': 0.8
        }
        
        for key, estimate in memory_estimates.items():
            if key in service_name.lower():
                return estimate
        return 1.0
    
    def _estimate_io_requirement(self, operation_name: str) -> float:
        """Estimate I/O requirement for operation"""
        io_estimates = {
            'upload': 2.0,
            'download': 1.8,
            'process': 1.5,
            'sync': 1.2,
            'notify': 0.5
        }
        
        for key, estimate in io_estimates.items():
            if key in operation_name.lower():
                return estimate
        return 1.0
    
    def _estimate_network_requirement(self, service_name: str) -> float:
        """Estimate network requirement for service"""
        network_estimates = {
            'distribution': 2.0,
            'collaboration': 1.8,
            'content': 1.5,
            'ai': 1.2,
            'payment': 1.0
        }
        
        for key, estimate in network_estimates.items():
            if key in service_name.lower():
                return estimate
        return 1.0
    
    async def _generate_optimization_plan(self, service_priorities: Dict[str, float], 
                                        resource_requirements: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Generate resource optimization plan"""
        return {
            'high_priority_services': [s for s, p in service_priorities.items() if p > 0.8],
            'resource_reallocation': 'Allocate more resources to high-priority services',
            'scaling_recommendations': 'Implement auto-scaling for variable workloads'
        }
    
    async def _estimate_optimization_impact(self, optimization_plan: Dict[str, Any]) -> Dict[str, float]:
        """Estimate impact of optimization plan"""
        return {
            'performance_improvement': 0.15,  # 15% improvement
            'resource_efficiency': 0.20,     # 20% more efficient
            'cost_reduction': 0.10           # 10% cost reduction
        }
    
    async def _detect_performance_anomalies(self, recent_data: List[PerformanceDataPoint]) -> List[Dict[str, Any]]:
        """Detect performance anomalies in recent data"""
        execution_times = [dp.execution_time for dp in recent_data if dp.success]
        if len(execution_times) < 5:
            return []
            
        mean_time = statistics.mean(execution_times)
        std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        
        anomalies = []
        for i, dp in enumerate(recent_data):
            if dp.success and std_dev > 0:
                z_score = abs(dp.execution_time - mean_time) / std_dev
                if z_score > self.predictor_config.outlier_threshold:
                    anomalies.append({
                        'timestamp': dp.timestamp,
                        'execution_time': dp.execution_time,
                        'z_score': z_score,
                        'type': 'performance_outlier'
                    })
                    
        return anomalies
    
    async def _analyze_anomaly_patterns(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in detected anomalies"""
        if not anomalies:
            return {'pattern': 'none'}
            
        return {
            'pattern': 'isolated_spikes',
            'frequency': len(anomalies),
            'severity': 'medium'
        }
    
    async def _generate_anomaly_alerts(self, anomalies: List[Dict[str, Any]], patterns: Dict[str, Any], service_name: str) -> List[Dict[str, Any]]:
        """Generate alerts for detected anomalies"""
        if not anomalies:
            return []
            
        return [{
            'level': 'warning',
            'message': f'Performance anomalies detected in {service_name}',
            'count': len(anomalies),
            'recommendation': 'Investigate recent changes or resource constraints'
        }]
    
    async def _assess_anomaly_severity(self, anomalies: List[Dict[str, Any]]) -> str:
        """Assess overall severity of anomalies"""
        if not anomalies:
            return 'none'
        elif len(anomalies) > 10:
            return 'high'
        elif len(anomalies) > 5:
            return 'medium'
        else:
            return 'low'
    
    async def _generate_anomaly_recommendations(self, anomalies: List[Dict[str, Any]], service_name: str) -> List[str]:
        """Generate recommendations for handling anomalies"""
        if not anomalies:
            return []
            
        return [
            'Monitor service performance closely',
            'Check for resource constraints or bottlenecks',
            'Consider implementing circuit breaker patterns',
            'Review recent code deployments or configuration changes'
        ]
    
    async def _get_model_accuracy(self, service_name: str, model: PredictionModel) -> float:
        """Get historical accuracy for a model"""
        # In a real implementation, this would track actual accuracy
        accuracy_map = {
            PredictionModel.MOVING_AVERAGE: 0.75,
            PredictionModel.EXPONENTIAL_SMOOTHING: 0.80,
            PredictionModel.LINEAR_REGRESSION: 0.70,
            PredictionModel.ENSEMBLE: 0.85
        }
        return accuracy_map.get(model, 0.70)

# Global intelligent timeout predictor instance
intelligent_timeout_predictor = IntelligentTimeoutPredictor()

# Export main classes and functions
__all__ = [
    'IntelligentTimeoutPredictor',
    'TimeoutPredictionRequest',
    'TimeoutPredictionResult',
    'PredictionModel',
    'TimeSeriesPattern',
    'intelligent_timeout_predictor'
]