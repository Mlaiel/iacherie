"""IA Influencer Agent - Performance Analytics Engine
Enterprise-grade performance analysis with ML-powered insights and optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

⚠️  AVERTISSEMENT LÉGAL STRICT ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et fera l'objet de poursuites 
judiciaires selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de

Équipe de développement:
- Lead Developer IA & Architecte: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- DBA & Data Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- Security Specialist: Fahed Mlaiel
- Audio Processing Expert: Fahed Mlaiel

Features:
- Advanced ML-powered performance analysis and optimization
- Real-time anomaly detection with predictive capabilities
- Multi-dimensional performance profiling with correlation analysis
- Business impact assessment with ROI calculations
- Automated optimization recommendations with A/B testing
- Advanced bottleneck identification with root cause analysis
- Predictive scaling with capacity planning
- Performance forecasting with trend analysis
"""

import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.metrics import mean_squared_error, r2_score
import scipy.stats as stats
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.utils.redis_manager import RedisManager
from backend.utils.database import get_database_session
from backend.models.metrics import PerformanceModel, AnalyticsModel
from .config import get_metrics_config, MetricsConfiguration

logger = get_logger(__name__)
settings = get_settings()


class PerformanceMetricType(Enum):
    """
Performance metric categorization for advanced analysis"""

    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    RESOURCE_UTILIZATION = "resource_utilization"
    BUSINESS_KPI = "business_kpi"
    AI_MODEL_PERFORMANCE = "ai_model_performance"
    USER_EXPERIENCE = "user_experience"
    SECURITY_METRIC = "security_metric"


class PerformanceSeverity(Enum):
    """Performance issue severity levels"""

    OPTIMAL = "optimal"
    GOOD = "good"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AnalysisWindow(Enum):
    """Time window for performance analysis"""

    REALTIME = "1m"
    SHORT_TERM = "1h"
    MEDIUM_TERM = "24h"
    LONG_TERM = "7d"
    HISTORICAL = "30d"


class OptimizationStrategy(Enum):
    """Performance optimization strategies"""

    SCALE_UP = "scale_up"
    SCALE_OUT = "scale_out"
    CACHE_OPTIMIZATION = "cache_optimization"
    QUERY_OPTIMIZATION = "query_optimization"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"
    RESOURCE_REALLOCATION = "resource_reallocation"
    LOAD_BALANCING = "load_balancing"
    CONFIGURATION_TUNING = "configuration_tuning"


@dataclass
class PerformanceMetric:
    """Enhanced performance metric with metadata"""
    name: str
    value: float
    timestamp: datetime
    metric_type: PerformanceMetricType
    labels: Dict[str, str] = field(default_factory=dict)
    tenant_id: Optional[str] = None
    component: Optional[str] = None
    business_impact: float = 0.0
    confidence_score: float = 1.0


@dataclass
class PerformanceBaseline:
    """
Performance baseline with statistical analysis"""
    metric_name: str
    mean: float
    std: float
    percentiles: Dict[str, float]
    seasonal_patterns: Dict[str, Any]
    trend_coefficients: List[float]
    confidence_interval: Tuple[float, float]
    last_updated: datetime
    sample_size: int


@dataclass
class PerformanceAnomaly:
    """
Performance anomaly with detailed analysis"""
    id: str
    metric_name: str
    detected_at: datetime
    severity: PerformanceSeverity
    anomaly_score: float
    expected_value: float
    actual_value: float
    deviation_percentage: float
    potential_causes: List[str]
    business_impact_estimate: float
    recommended_actions: List[str]
    correlation_metrics: List[str]
    root_cause_confidence: float


@dataclass
class PerformanceInsight:
    """
Performance insight with actionable recommendations"""
    id: str
    title: str
    description: str
    category: str
    severity: PerformanceSeverity
    confidence: float
    business_impact: float
    estimated_improvement: Dict[str, float]
    implementation_effort: str  # low, medium, high
    timeline: str
    prerequisites: List[str]
    recommendations: List[str]
    metrics_affected: List[str]
    roi_estimate: float


@dataclass
class PerformanceForecast:
    """
Performance forecast with uncertainty bounds"""
    metric_name: str
    forecast_values: List[float]
    timestamps: List[datetime]
    confidence_intervals: List[Tuple[float, float]]
    trend_direction: str  # increasing, decreasing, stable
    seasonal_component: List[float]
    forecast_accuracy: float
    uncertainty_level: str  # low, medium, high


class PerformanceAnalytics:
    """
    Advanced performance analytics engine with ML capabilities
    
    Features:
    - Real-time anomaly detection with adaptive thresholds
    - Multi-dimensional performance correlation analysis
    - Predictive performance forecasting with seasonality
    - Automated optimization recommendations
    - Business impact assessment and ROI analysis
    - Root cause analysis with confidence scoring
    - Advanced visualization and reporting
    - Multi-tenant performance isolation
    """
    
    def __init__(self, config: Optional[MetricsConfiguration] = None):
        self.config = config or get_metrics_config()
        self.logger = logger
        
        # Enhanced components
        self.redis_manager = RedisManager()
        
        # ML models and analyzers
        self.anomaly_detectors: Dict[str, IsolationForest] = {}
        self.forecasting_models: Dict[str, RandomForestRegressor] = {}
        self.baseline_models: Dict[str, PerformanceBaseline] = {}
        self.correlation_analyzer = self._initialize_correlation_analyzer()
        
        # Performance tracking
        self.performance_metrics: Dict[str, List[PerformanceMetric]] = {}
        self.detected_anomalies: List[PerformanceAnomaly] = []
        self.performance_insights: List[PerformanceInsight] = []
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Advanced analytics
        self.trend_analyzer = self._initialize_trend_analyzer()
        self.seasonal_analyzer = self._initialize_seasonal_analyzer()
        self.business_impact_calculator = self._initialize_business_impact_calculator()
        
        # Configuration
        self.analysis_intervals = {
            AnalysisWindow.REALTIME: 60,      # 1 minute
            AnalysisWindow.SHORT_TERM: 3600,  # 1 hour
            AnalysisWindow.MEDIUM_TERM: 86400, # 24 hours
            AnalysisWindow.LONG_TERM: 604800,  # 7 days
            AnalysisWindow.HISTORICAL: 2592000 # 30 days
        }
        
        # Performance optimization
        self._running = False
        self._analysis_tasks: Dict[str, asyncio.Task] = {}
        
        # Initialize components
        self._initialize_default_baselines()
        self._initialize_ml_models()
    
    async def start(self) -> None:
        """
Start performance analytics engine"""
        try:
            if self._running:
                self.logger.warning("Performance analytics already running")
                return
            
            self._running = True
            
            # Start analysis loops for different time windows
            for window in AnalysisWindow:
                task_name = f"analysis_{window.name.lower()}"
                self._analysis_tasks[task_name] = asyncio.create_task(
                    self._analysis_loop(window)
                )
            
            # Start specialized analysis tasks
            self._analysis_tasks["anomaly_detection"] = asyncio.create_task(
                self._anomaly_detection_loop()
            )
            
            self._analysis_tasks["forecasting"] = asyncio.create_task(
                self._forecasting_loop()
            )
            
            self._analysis_tasks["optimization"] = asyncio.create_task(
                self._optimization_loop()
            )
            
            self._analysis_tasks["business_intelligence"] = asyncio.create_task(
                self._business_intelligence_loop()
            )
            
            self.logger.info("Advanced Performance Analytics Engine started")
            
        except Exception as e:
            self.logger.error(f"Error starting performance analytics: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop performance analytics engine"""
        try:
            self._running = False
            
            # Stop all analysis tasks
            for task_name, task in self._analysis_tasks.items():
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Save ML models and insights
            await self._save_ml_models()
            await self._save_performance_insights()
            
            self.logger.info("Performance Analytics Engine stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping performance analytics: {e}")
    
    async def analyze_performance(
        self,
        metric_name: str,
        time_window: AnalysisWindow = AnalysisWindow.SHORT_TERM,
        tenant_id: Optional[str] = None,
        include_forecast: bool = True,
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """Comprehensive performance analysis with ML insights"""
        try:
            # Get performance data
            metrics_data = await self._get_metrics_data(
                metric_name, time_window, tenant_id
            )
            
            if not metrics_data:
                return {"error": "No data available for analysis"}
            
            # Perform comprehensive analysis
            analysis_result = {
                "metric_name": metric_name,
                "time_window": time_window.value,
                "tenant_id": tenant_id,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "data_points": len(metrics_data),
                "statistical_analysis": {},
                "anomaly_detection": {},
                "trend_analysis": {},
                "seasonality_analysis": {},
                "performance_score": 0.0,
                "business_impact": {},
                "optimization_opportunities": []
            }
            
            # Statistical analysis
            analysis_result["statistical_analysis"] = await self._perform_statistical_analysis(
                metrics_data
            )
            
            # Anomaly detection
            analysis_result["anomaly_detection"] = await self._detect_anomalies(
                metric_name, metrics_data
            )
            
            # Trend analysis
            analysis_result["trend_analysis"] = await self._analyze_trends(
                metrics_data
            )
            
            # Seasonality analysis
            analysis_result["seasonality_analysis"] = await self._analyze_seasonality(
                metrics_data
            )
            
            # Calculate performance score
            analysis_result["performance_score"] = await self._calculate_performance_score(
                metric_name, metrics_data
            )
            
            # Business impact assessment
            analysis_result["business_impact"] = await self._assess_business_impact(
                metric_name, metrics_data, tenant_id
            )
            
            # Forecasting
            if include_forecast:
                analysis_result["forecast"] = await self._generate_forecast(
                    metric_name, metrics_data
                )
            
            # Optimization recommendations
            if include_recommendations:
                analysis_result["optimization_opportunities"] = await self._generate_optimization_recommendations(
                    metric_name, analysis_result
                )
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance: {e}")
            return {"error": str(e)}
    
    async def detect_performance_anomalies(
        self,
        metric_names: Optional[List[str]] = None,
        tenant_id: Optional[str] = None,
        sensitivity: float = 0.8,
        lookback_hours: int = 24
    ) -> List[PerformanceAnomaly]:
        """Advanced anomaly detection with ML and statistical methods"""
        try:
            detected_anomalies = []
            
            # Get metric names to analyze
            if not metric_names:
                metric_names = await self._get_available_metrics(tenant_id)
            
            for metric_name in metric_names:
                try:
                    # Get recent data
                    end_time = datetime.utcnow()
                    start_time = end_time - timedelta(hours=lookback_hours)
                    
                    metrics_data = await self._get_metrics_data_timerange(
                        metric_name, start_time, end_time, tenant_id
                    )
                    
                    if len(metrics_data) < 10:  # Need minimum data points
                        continue
                    
                    # Multiple anomaly detection methods
                    anomalies = []
                    
                    # 1. Statistical anomaly detection
                    statistical_anomalies = await self._detect_statistical_anomalies(
                        metric_name, metrics_data, sensitivity
                    )
                    anomalies.extend(statistical_anomalies)
                    
                    # 2. ML-based anomaly detection
                    ml_anomalies = await self._detect_ml_anomalies(
                        metric_name, metrics_data, sensitivity
                    )
                    anomalies.extend(ml_anomalies)
                    
                    # 3. Contextual anomaly detection
                    contextual_anomalies = await self._detect_contextual_anomalies(
                        metric_name, metrics_data
                    )
                    anomalies.extend(contextual_anomalies)
                    
                    # Merge and deduplicate anomalies
                    merged_anomalies = await self._merge_anomalies(anomalies)
                    detected_anomalies.extend(merged_anomalies)
                    
                except Exception as e:
                    self.logger.error(f"Error detecting anomalies for {metric_name}: {e}")
            
            # Sort by severity and business impact
            detected_anomalies.sort(
                key=lambda x: (x.severity.value, x.business_impact_estimate),
                reverse=True
            )
            
            return detected_anomalies
            
        except Exception as e:
            self.logger.error(f"Error in anomaly detection: {e}")
            return []
    
    async def generate_performance_forecast(
        self,
        metric_name: str,
        forecast_hours: int = 24,
        tenant_id: Optional[str] = None,
        include_scenarios: bool = True
    ) -> PerformanceForecast:
        """Advanced performance forecasting with uncertainty quantification"""
        try:
            # Get historical data for training
            training_data = await self._get_training_data(metric_name, tenant_id)
            
            if not training_data or len(training_data) < 50:
                raise ValueError("Insufficient data for forecasting")
            
            # Prepare data for forecasting
            X, y = await self._prepare_forecasting_data(training_data)
            
            # Train or update forecasting model
            model = await self._get_or_create_forecasting_model(metric_name)
            model.fit(X, y)
            
            # Generate forecast
            forecast_timestamps = [
                datetime.utcnow() + timedelta(hours=i)
                for i in range(1, forecast_hours + 1)
            ]
            
            # Prepare forecast features
            forecast_X = await self._prepare_forecast_features(
                forecast_timestamps, training_data
            )
            
            # Generate predictions with uncertainty
            predictions = model.predict(forecast_X)
            
            # Calculate confidence intervals
            confidence_intervals = await self._calculate_forecast_confidence_intervals(
                model, forecast_X, predictions
            )
            
            # Analyze seasonal patterns
            seasonal_component = await self._extract_seasonal_component(
                training_data, forecast_hours
            )
            
            # Calculate forecast accuracy from historical validation
            forecast_accuracy = await self._calculate_forecast_accuracy(
                metric_name, model
            )
            
            # Determine trend direction
            trend_direction = await self._determine_trend_direction(predictions)
            
            # Create forecast object
            forecast = PerformanceForecast(
                metric_name=metric_name,
                forecast_values=predictions.tolist(),
                timestamps=forecast_timestamps,
                confidence_intervals=confidence_intervals,
                trend_direction=trend_direction,
                seasonal_component=seasonal_component,
                forecast_accuracy=forecast_accuracy,
                uncertainty_level=self._determine_uncertainty_level(confidence_intervals)
            )
            
            # Generate scenario forecasts if requested
            if include_scenarios:
                forecast.scenarios = await self._generate_scenario_forecasts(
                    metric_name, model, forecast_X, predictions
                )
            
            return forecast
            
        except Exception as e:
            self.logger.error(f"Error generating forecast: {e}")
            raise
    
    async def get_optimization_recommendations(
        self,
        tenant_id: Optional[str] = None,
        priority_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        max_recommendations: int = 10
    ) -> List[PerformanceInsight]:
        """Generate advanced optimization recommendations with ROI analysis"""
        try:
            recommendations = []
            
            # Analyze current performance state
            performance_state = await self._analyze_current_performance_state(tenant_id)
            
            # Generate recommendations based on different analysis methods
            
            # 1. Bottleneck analysis recommendations
            bottleneck_recommendations = await self._generate_bottleneck_recommendations(
                performance_state, tenant_id
            )
            recommendations.extend(bottleneck_recommendations)
            
            # 2. Resource optimization recommendations
            resource_recommendations = await self._generate_resource_optimization_recommendations(
                performance_state, tenant_id
            )
            recommendations.extend(resource_recommendations)
            
            # 3. Algorithm optimization recommendations
            algorithm_recommendations = await self._generate_algorithm_optimization_recommendations(
                performance_state, tenant_id
            )
            recommendations.extend(algorithm_recommendations)
            
            # 4. Configuration tuning recommendations
            config_recommendations = await self._generate_configuration_recommendations(
                performance_state, tenant_id
            )
            recommendations.extend(config_recommendations)
            
            # 5. Business process optimization recommendations
            business_recommendations = await self._generate_business_optimization_recommendations(
                performance_state, tenant_id
            )
            recommendations.extend(business_recommendations)
            
            # Apply filters
            if priority_filter:
                recommendations = [
                    r for r in recommendations
                    if r.severity.value == priority_filter
                ]
            
            if category_filter:
                recommendations = [
                    r for r in recommendations
                    if r.category == category_filter
                ]
            
            # Sort by ROI and business impact
            recommendations.sort(
                key=lambda x: (x.roi_estimate, x.business_impact),
                reverse=True
            )
            
            # Limit results
            return recommendations[:max_recommendations]
            
        except Exception as e:
            self.logger.error(f"Error generating optimization recommendations: {e}")
            return []
    
    async def calculate_performance_score(
        self,
        tenant_id: Optional[str] = None,
        metric_categories: Optional[List[PerformanceMetricType]] = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive performance score with breakdown"""
        try:
            if not metric_categories:
                metric_categories = list(PerformanceMetricType)
            
            score_breakdown = {}
            weighted_scores = []
            weights = []
            
            for category in metric_categories:
                category_score = await self._calculate_category_performance_score(
                    category, tenant_id
                )
                
                if category_score is not None:
                    score_breakdown[category.value] = category_score
                    
                    # Apply category weights
                    weight = self._get_category_weight(category)
                    weighted_scores.append(category_score["score"] * weight)
                    weights.append(weight)
            
            # Calculate overall score
            if weights:
                overall_score = sum(weighted_scores) / sum(weights)
            else:
                overall_score = 0.0
            
            # Determine performance level
            performance_level = self._determine_performance_level(overall_score)
            
            # Calculate trend
            historical_scores = await self._get_historical_performance_scores(tenant_id)
            trend = self._calculate_score_trend(historical_scores, overall_score)
            
            return {
                "overall_score": round(overall_score, 2),
                "performance_level": performance_level,
                "trend": trend,
                "score_breakdown": score_breakdown,
                "calculation_timestamp": datetime.utcnow().isoformat(),
                "recommendations": await self._get_score_improvement_recommendations(
                    overall_score, score_breakdown
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating performance score: {e}")
            return {"error": str(e)}
    
    # Private implementation methods
    
    async def _get_metrics_data(
        self,
        metric_name: str,
        time_window: AnalysisWindow,
        tenant_id: Optional[str]
    ) -> List[PerformanceMetric]:
        """Get metrics data for analysis"""
        # Implementation would query from Redis/database
        return []
    
    async def _perform_statistical_analysis(
        self,
        metrics_data: List[PerformanceMetric]
    ) -> Dict[str, Any]:
        """
Perform comprehensive statistical analysis"""
        values = [m.value for m in metrics_data]
        
        if not values:
            return {}
        
        values_array = np.array(values)
        
        return {
            "count": len(values),
            "mean": float(np.mean(values_array)),
            "median": float(np.median(values_array)),
            "std": float(np.std(values_array)),
            "min": float(np.min(values_array)),
            "max": float(np.max(values_array)),
            "percentiles": {
                "p25": float(np.percentile(values_array, 25)),
                "p50": float(np.percentile(values_array, 50)),
                "p75": float(np.percentile(values_array, 75)),
                "p90": float(np.percentile(values_array, 90)),
                "p95": float(np.percentile(values_array, 95)),
                "p99": float(np.percentile(values_array, 99))
            },
            "variance": float(np.var(values_array)),
            "skewness": float(stats.skew(values_array)),
            "kurtosis": float(stats.kurtosis(values_array)),
            "coefficient_of_variation": float(np.std(values_array) / np.mean(values_array)) if np.mean(values_array) != 0 else 0
        }
    
    async def _detect_anomalies(
        self,
        metric_name: str,
        metrics_data: List[PerformanceMetric]
    ) -> Dict[str, Any]:
        """Detect anomalies in metrics data"""
        # Placeholder implementation
        return {
            "anomalies_detected": 0,
            "anomaly_scores": [],
            "anomaly_threshold": 0.8,
            "detection_method": "isolation_forest"
        }
    
    async def _analyze_trends(
        self,
        metrics_data: List[PerformanceMetric]
    ) -> Dict[str, Any]:
        """Analyze performance trends"""
        # Placeholder implementation
        return {
            "trend_direction": "stable",
            "trend_strength": 0.0,
            "linear_regression": {
                "slope": 0.0,
                "intercept": 0.0,
                "r_squared": 0.0
            }
        }
    
    async def _analyze_seasonality(
        self,
        metrics_data: List[PerformanceMetric]
    ) -> Dict[str, Any]:
        """Analyze seasonal patterns"""
        # Placeholder implementation
        return {
            "seasonal_patterns_detected": False,
            "dominant_frequency": None,
            "seasonal_strength": 0.0
        }
    
    async def _calculate_performance_score(
        self,
        metric_name: str,
        metrics_data: List[PerformanceMetric]
    ) -> float:
        """Calculate performance score for metric"""
        # Placeholder implementation
        return 85.0
    
    async def _assess_business_impact(
        self,
        metric_name: str,
        metrics_data: List[PerformanceMetric],
        tenant_id: Optional[str]
    ) -> Dict[str, Any]:
        """
Assess business impact of performance"""
        # Placeholder implementation
        return {
            "impact_score": 7.5,
            "revenue_impact_estimate": 0.0,
            "user_experience_impact": "medium",
            "business_criticality": "high"
        }
    
    async def _generate_forecast(
        self,
        metric_name: str,
        metrics_data: List[PerformanceMetric]
    ) -> Dict[str, Any]:
        """Generate performance forecast"""
        # Placeholder implementation
        return {
            "forecast_horizon": "24h",
            "predicted_values": [],
            "confidence_intervals": [],
            "accuracy_estimate": 0.85
        }
    
    async def _generate_optimization_recommendations(
        self,
        metric_name: str,
        analysis_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        # Placeholder implementation
        return []
    
    # Additional helper methods would be implemented here...
    
    def _initialize_correlation_analyzer(self):
        """
Initialize correlation analyzer"""
        return None
    
    def _initialize_trend_analyzer(self):
        """
Initialize trend analyzer"""
        return None
    
    def _initialize_seasonal_analyzer(self):
        """
Initialize seasonal analyzer"""
        return None
    
    def _initialize_business_impact_calculator(self):
        """
Initialize business impact calculator"""
        return None
    
    def _initialize_default_baselines(self) -> None:
        try:
            logger.info(f"Executing _initialize_default_baselines")
            
            # Implementation for _initialize_default_baselines
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _initialize_ml_models")
            
            # Implementation for _initialize_ml_models
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _analysis_loop")
            
            # Implementation for _analysis_loop
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _anomaly_detection_loop")
            
            # Implementation for _anomaly_detection_loop
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _forecasting_loop")
            
            # Implementation for _forecasting_loop
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _optimization_loop")
            
            # Implementation for _optimization_loop
            # TODO: Add specific business logic here
        try:
            logger.info(f"Executing _business_intelligence_loop")
            
            # Implementation for _business_intelligence_loop
            # TODO: Add specific business logic here
        try:
                    async with self.db_session() as session:
                        # Database operation
                
                        await session.commit()
                        logger.info(f"Database operation _save_ml_models completed")
                        return True
                
                except Exception as e:
        try:
                    async with self.db_session() as session:
                        # Database operation
                
                        await session.commit()
                        logger.info(f"Database operation _save_performance_insights completed")
                        return True
                
                except Exception as e:
                    logger.error(f"Database operation _save_performance_insights failed: {e}")
                    raise
                except Exception as e:
                    logger.error(f"Database operation _save_ml_models failed: {e}")
                    raise
            logger.info(f"_business_intelligence_loop completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_business_intelligence_loop failed: {e}")
            raise
            logger.info(f"_optimization_loop completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_optimization_loop failed: {e}")
            raise
            logger.info(f"_forecasting_loop completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_forecasting_loop failed: {e}")
            raise
            logger.info(f"_anomaly_detection_loop completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_anomaly_detection_loop failed: {e}")
            raise
            logger.info(f"_analysis_loop completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_analysis_loop failed: {e}")
            raise
            logger.info(f"_initialize_ml_models completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_initialize_ml_models failed: {e}")
            raise
            logger.info(f"_initialize_default_baselines completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_initialize_default_baselines failed: {e}")
            raise
    def _initialize_ml_models(self) -> None:
        """
Initialize ML models"""
        pass
    
    async def _analysis_loop(self, window: AnalysisWindow) -> None:
        """
Analysis loop for specific time window"""
        pass
    
    async def _anomaly_detection_loop(self) -> None:
        """
Anomaly detection loop"""
        pass
    
    async def _forecasting_loop(self) -> None:
        """
Forecasting loop"""
        pass
    
    async def _optimization_loop(self) -> None:
        """
Optimization loop"""
        pass
    
    async def _business_intelligence_loop(self) -> None:
        """
Business intelligence loop"""
        pass
    
    async def _save_ml_models(self) -> None:
        """
Save ML models"""
        pass
    
    async def _save_performance_insights(self) -> None:
        """
Save performance insights"""
        pass
    
    # Additional implementation methods would go here...

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import statistics
import numpy as np
from scipy import stats
import pandas as pd

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.models.analytics import PerformanceReport, PerformanceTrend
from backend.utils.redis_manager import RedisManager
from backend.utils.database import get_database_session

logger = get_logger(__name__)
settings = get_settings()


class PerformanceMetricType(Enum):
    """
Performance metric types"""

    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"
    RESOURCE_UTILIZATION = "resource_utilization"
    USER_SATISFACTION = "user_satisfaction"


class TimeWindow(Enum):
    """Time window for analysis"""

    REALTIME = "realtime"  # Last 5 minutes
    HOURLY = "hourly"      # Last hour
    DAILY = "daily"        # Last 24 hours
    WEEKLY = "weekly"      # Last 7 days
    MONTHLY = "monthly"    # Last 30 days


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceAnalysis:
    """
Performance analysis result"""
    metric_name: str
    time_window: TimeWindow
    tenant_id: Optional[str]
    
    # Statistical measures
    mean: float
    median: float
    std_deviation: float
    min_value: float
    max_value: float
    percentile_95: float
    percentile_99: float
    
    # Trend analysis
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0-1
    
    # Performance assessment
    performance_score: float  # 0-100
    health_status: str  # "excellent", "good", "warning", "critical"
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Additional metadata
    sample_count: int = 0
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)


class PerformanceAnalytics:
    """
    Enterprise performance analytics engine
    
    Handles:
    - Real-time performance monitoring and analysis
    - Statistical analysis and trend detection
    - Performance scoring and health assessment
    - Automated optimization recommendations
    - Comparative analysis across tenants
    - Performance forecasting and capacity planning
    """
    
    def __init__(self):
        self.redis_manager = RedisManager()
        self.logger = logger
        self.settings = settings
        
        # Analysis state
        self.metric_cache: Dict[str, List[PerformanceMetric]] = {}
        self.analysis_cache: Dict[str, PerformanceAnalysis] = {}
        
        # Analysis configuration
        self.analysis_intervals = {
            TimeWindow.REALTIME: 5,    # 5 minutes
            TimeWindow.HOURLY: 60,     # 1 hour
            TimeWindow.DAILY: 1440,    # 24 hours
            TimeWindow.WEEKLY: 10080,  # 7 days
            TimeWindow.MONTHLY: 43200  # 30 days
        }
        
        # Performance thresholds
        self.performance_thresholds = self._initialize_thresholds()
    
    async def analyze_performance(
        self,
        metric_name: str,
        time_window: TimeWindow,
        tenant_id: Optional[str] = None
    ) -> PerformanceAnalysis:
        """
Analyze performance for specific metric and time window"""
        try:
            # Get metric data
            metrics = await self._get_metrics_data(metric_name, time_window, tenant_id)
            
            if not metrics:
                return self._create_empty_analysis(metric_name, time_window, tenant_id)
            
            # Extract values and timestamps
            values = [m.value for m in metrics]
            timestamps = [m.timestamp for m in metrics]
            
            # Statistical analysis
            analysis = PerformanceAnalysis(
                metric_name=metric_name,
                time_window=time_window,
                tenant_id=tenant_id,
                mean=statistics.mean(values),
                median=statistics.median(values),
                std_deviation=statistics.stdev(values) if len(values) > 1 else 0,
                min_value=min(values),
                max_value=max(values),
                percentile_95=np.percentile(values, 95),
                percentile_99=np.percentile(values, 99),
                sample_count=len(values)
            )
            
            # Trend analysis
            trend_direction, trend_strength = self._analyze_trend(values, timestamps)
            analysis.trend_direction = trend_direction
            analysis.trend_strength = trend_strength
            
            # Performance scoring
            analysis.performance_score = self._calculate_performance_score(analysis)
            analysis.health_status = self._determine_health_status(analysis.performance_score)
            
            # Generate recommendations
            analysis.recommendations = self._generate_recommendations(analysis)
            
            # Cache result
            cache_key = f"{metric_name}_{time_window.value}_{tenant_id or 'global'}"
            self.analysis_cache[cache_key] = analysis
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance: {e}")
            return self._create_empty_analysis(metric_name, time_window, tenant_id)
    
    async def analyze_ai_model_performance(
        self,
        model_name: str,
        time_window: TimeWindow,
        tenant_id: Optional[str] = None
    ) -> Dict[str, PerformanceAnalysis]:
        """Analyze AI model performance across multiple metrics"""
        try:
            model_metrics = [
                f"ai_inference_duration_{model_name}",
                f"ai_model_accuracy_{model_name}",
                f"ai_predictions_total_{model_name}"
            ]
            
            analysis_results = {}
            
            for metric in model_metrics:
                analysis = await self.analyze_performance(metric, time_window, tenant_id)
                analysis_results[metric] = analysis
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error analyzing AI model performance: {e}")
            return {}
    
    async def analyze_content_protection_performance(
        self,
        time_window: TimeWindow,
        tenant_id: Optional[str] = None
    ) -> Dict[str, PerformanceAnalysis]:
        """Analyze content protection performance"""
        try:
            protection_metrics = [
                "fingerprint_processing_duration_seconds",
                "content_matches_detected_total",
                "fingerprints_created_total"
            ]
            
            analysis_results = {}
            
            for metric in protection_metrics:
                analysis = await self.analyze_performance(metric, time_window, tenant_id)
                analysis_results[metric] = analysis
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error analyzing content protection performance: {e}")
            return {}
    
    async def analyze_infrastructure_performance(
        self,
        time_window: TimeWindow
    ) -> Dict[str, PerformanceAnalysis]:
        """Analyze infrastructure performance"""
        try:
            infrastructure_metrics = [
                "system_cpu_percent",
                "system_memory_bytes",
                "database_connections_active",
                "cache_hit_rate"
            ]
            
            analysis_results = {}
            
            for metric in infrastructure_metrics:
                analysis = await self.analyze_performance(metric, time_window)
                analysis_results[metric] = analysis
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error analyzing infrastructure performance: {e}")
            return {}
    
    async def generate_performance_report(
        self,
        tenant_id: Optional[str] = None,
        time_window: TimeWindow = TimeWindow.DAILY
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            report = {
                "tenant_id": tenant_id,
                "time_window": time_window.value,
                "generated_at": datetime.utcnow().isoformat(),
                "sections": {}
            }
            
            # Application performance
            app_metrics = await self._analyze_application_performance(time_window, tenant_id)
            report["sections"]["application"] = app_metrics
            
            # AI model performance
            ai_metrics = await self.analyze_ai_model_performance("all", time_window, tenant_id)
            report["sections"]["ai_models"] = ai_metrics
            
            # Content protection
            protection_metrics = await self.analyze_content_protection_performance(time_window, tenant_id)
            report["sections"]["content_protection"] = protection_metrics
            
            # Infrastructure (global only)
            if not tenant_id:
                infra_metrics = await self.analyze_infrastructure_performance(time_window)
                report["sections"]["infrastructure"] = infra_metrics
            
            # Overall performance score
            report["overall_score"] = self._calculate_overall_score(report["sections"])
            
            # Summary and recommendations
            report["summary"] = self._generate_performance_summary(report)
            report["recommendations"] = self._generate_report_recommendations(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {}
    
    async def compare_tenant_performance(
        self,
        tenant_ids: List[str],
        metric_name: str,
        time_window: TimeWindow
    ) -> Dict[str, Any]:
        """Compare performance across multiple tenants"""
        try:
            comparison = {
                "metric_name": metric_name,
                "time_window": time_window.value,
                "tenant_comparisons": {},
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            tenant_analyses = {}
            
            # Analyze each tenant
            for tenant_id in tenant_ids:
                analysis = await self.analyze_performance(metric_name, time_window, tenant_id)
                tenant_analyses[tenant_id] = analysis
            
            comparison["tenant_comparisons"] = tenant_analyses
            
            # Comparative analysis
            comparison["rankings"] = self._rank_tenants_by_performance(tenant_analyses)
            comparison["performance_gaps"] = self._identify_performance_gaps(tenant_analyses)
            comparison["best_practices"] = self._identify_best_practices(tenant_analyses)
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Error comparing tenant performance: {e}")
            return {}
    
    async def forecast_performance(
        self,
        metric_name: str,
        tenant_id: Optional[str] = None,
        forecast_days: int = 7
    ) -> Dict[str, Any]:
        """Forecast future performance trends"""
        try:
            # Get historical data
            metrics = await self._get_metrics_data(
                metric_name,
                TimeWindow.MONTHLY,
                tenant_id
            )
            
            if len(metrics) < 10:  # Need minimum data points
                return {"error": "Insufficient data for forecasting"}
            
            # Prepare time series data
            timestamps = [m.timestamp for m in metrics]
            values = [m.value for m in metrics]
            
            # Convert to numerical timestamps
            time_numeric = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
            
            # Linear regression for trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(time_numeric, values)
            
            # Generate forecast
            last_timestamp = timestamps[-1]
            forecast_points = []
            
            for i in range(1, forecast_days + 1):
                future_timestamp = last_timestamp + timedelta(days=i)
                future_time_numeric = (future_timestamp - timestamps[0]).total_seconds()
                predicted_value = slope * future_time_numeric + intercept
                
                forecast_points.append({
                    "timestamp": future_timestamp.isoformat(),
                    "predicted_value": predicted_value,
                    "confidence_interval": {
                        "lower": predicted_value - (2 * std_err),
                        "upper": predicted_value + (2 * std_err)
                    }
                })
            
            return {
                "metric_name": metric_name,
                "tenant_id": tenant_id,
                "forecast_days": forecast_days,
                "forecast_points": forecast_points,
                "model_accuracy": {
                    "r_squared": r_value ** 2,
                    "p_value": p_value,
                    "standard_error": std_err
                },
                "trend_analysis": {
                    "slope": slope,
                    "direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error forecasting performance: {e}")
            return {}
    
    async def identify_performance_anomalies(
        self,
        metric_name: str,
        time_window: TimeWindow,
        tenant_id: Optional[str] = None,
        sensitivity: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Identify performance anomalies using statistical methods"""
        try:
            metrics = await self._get_metrics_data(metric_name, time_window, tenant_id)
            
            if len(metrics) < 30:  # Need sufficient data
                return []
            
            values = [m.value for m in metrics]
            timestamps = [m.timestamp for m in metrics]
            
            # Calculate statistical bounds
            mean_value = statistics.mean(values)
            std_value = statistics.stdev(values)
            
            upper_bound = mean_value + (sensitivity * std_value)
            lower_bound = mean_value - (sensitivity * std_value)
            
            anomalies = []
            
            for i, (value, timestamp) in enumerate(zip(values, timestamps)):
                if value > upper_bound or value < lower_bound:
                    anomaly_type = "spike" if value > upper_bound else "dip"
                    severity = abs(value - mean_value) / std_value
                    
                    anomalies.append({
                        "timestamp": timestamp.isoformat(),
                        "value": value,
                        "expected_value": mean_value,
                        "deviation": abs(value - mean_value),
                        "type": anomaly_type,
                        "severity": severity,
                        "context": {
                            "preceding_values": values[max(0, i-5):i],
                            "following_values": values[i+1:min(len(values), i+6)]
                        }
                    })
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error identifying anomalies: {e}")
            return []
    
    async def _get_metrics_data(
        self,
        metric_name: str,
        time_window: TimeWindow,
        tenant_id: Optional[str] = None
    ) -> List[PerformanceMetric]:
        """Get metrics data from storage"""
        try:
            # Check cache first
            cache_key = f"{metric_name}_{time_window.value}_{tenant_id or 'global'}"
            if cache_key in self.metric_cache:
                return self.metric_cache[cache_key]
            
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=self.analysis_intervals[time_window])
            
            metrics = []
            
            # Get data from Redis
            current_time = start_time
            while current_time <= end_time:
                timestamp_key = current_time.strftime("%Y%m%d%H%M")
                
                if tenant_id:
                    key = f"metrics:tenant:{tenant_id}:{metric_name}:{timestamp_key}"
                else:
                    key = f"metrics:global:{metric_name}:{timestamp_key}"
                
                data = await self.redis_manager.lrange(key, 0, -1)
                
                for item in data:
                    try:
                        metric_data = json.loads(item)
                        
                        metric = PerformanceMetric(
                            name=metric_data["name"],
                            value=metric_data["value"],
                            timestamp=datetime.fromisoformat(metric_data["timestamp"]),
                            labels=metric_data.get("labels", {}),
                            tenant_id=metric_data.get("tenant_id"),
                            metadata=metric_data.get("metadata", {})
                        )
                        
                        if start_time <= metric.timestamp <= end_time:
                            metrics.append(metric)
                            
                    except Exception as e:
                        self.logger.error(f"Error parsing metric data: {e}")
                
                current_time += timedelta(minutes=1)
            
            # Cache results
            self.metric_cache[cache_key] = metrics
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting metrics data: {e}")
            return []
    
    def _analyze_trend(
        self,
        values: List[float],
        timestamps: List[datetime]
    ) -> Tuple[str, float]:
        """Analyze trend direction and strength"""
        try:
            if len(values) < 3:
                return "stable", 0.0
            
            # Convert timestamps to numeric
            time_numeric = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
            
            # Linear regression
            slope, _, r_value, _, _ = stats.linregress(time_numeric, values)
            
            # Determine direction
            if abs(slope) < 0.001:  # Very small slope
                direction = "stable"
            elif slope > 0:
                direction = "increasing"
            else:
                direction = "decreasing"
            
            # Strength is absolute correlation coefficient
            strength = abs(r_value)
            
            return direction, strength
            
        except Exception as e:
            self.logger.error(f"Error analyzing trend: {e}")
            return "stable", 0.0
    
    def _calculate_performance_score(self, analysis: PerformanceAnalysis) -> float:
        """Calculate performance score (0-100)"""
        try:
            metric_thresholds = self.performance_thresholds.get(analysis.metric_name, {})
            
            if not metric_thresholds:
                return 50.0  # Default neutral score
            
            # Get thresholds
            excellent_threshold = metric_thresholds.get("excellent", 0)
            good_threshold = metric_thresholds.get("good", 0)
            warning_threshold = metric_thresholds.get("warning", 0)
            critical_threshold = metric_thresholds.get("critical", 0)
            
            # Use appropriate metric value (mean for most cases)
            value = analysis.mean
            
            # Calculate score based on thresholds
            if "latency" in analysis.metric_name or "duration" in analysis.metric_name:
                # Lower is better for latency metrics
                if value <= excellent_threshold:
                    return 95.0
                elif value <= good_threshold:
                    return 80.0
                elif value <= warning_threshold:
                    return 60.0
                elif value <= critical_threshold:
                    return 30.0
                else:
                    return 10.0
            else:
                # Higher is better for most other metrics
                if value >= excellent_threshold:
                    return 95.0
                elif value >= good_threshold:
                    return 80.0
                elif value >= warning_threshold:
                    return 60.0
                elif value >= critical_threshold:
                    return 30.0
                else:
                    return 10.0
                    
        except Exception as e:
            self.logger.error(f"Error calculating performance score: {e}")
            return 50.0
    
    def _determine_health_status(self, score: float) -> str:
        """Determine health status from performance score"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 50:
            return "warning"
        else:
            return "critical"
    
    def _generate_recommendations(self, analysis: PerformanceAnalysis) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        try:
            # Trend-based recommendations
            if analysis.trend_direction == "decreasing" and analysis.trend_strength > 0.7:
                recommendations.append(f"Performance is declining for {analysis.metric_name}. Consider investigating root causes.")
            
            # Statistical recommendations
            if analysis.std_deviation > (analysis.mean * 0.5):
                recommendations.append(f"High variability detected in {analysis.metric_name}. Consider stabilizing the system.")
            
            # Performance score recommendations
            if analysis.performance_score < 50:
                recommendations.append(f"Critical performance issue with {analysis.metric_name}. Immediate attention required.")
            elif analysis.performance_score < 75:
                recommendations.append(f"Performance degradation detected in {analysis.metric_name}. Optimization recommended.")
            
            # Metric-specific recommendations
            if "latency" in analysis.metric_name or "duration" in analysis.metric_name:
                if analysis.percentile_95 > analysis.mean * 2:
                    recommendations.append("High tail latency detected. Consider optimizing slow requests.")
            
            if "error" in analysis.metric_name and analysis.mean > 0.05:
                recommendations.append("High error rate detected. Check application logs and fix issues.")
            
            if "cpu" in analysis.metric_name and analysis.mean > 80:
                recommendations.append("High CPU usage detected. Consider scaling or optimization.")
            
            if "memory" in analysis.metric_name and analysis.mean > 80:
                recommendations.append("High memory usage detected. Check for memory leaks or consider scaling.")
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
        
        return recommendations or ["Performance appears normal."]
    
    def _create_empty_analysis(
        self,
        metric_name: str,
        time_window: TimeWindow,
        tenant_id: Optional[str]
    ) -> PerformanceAnalysis:
        """Create empty analysis for missing data"""
        return PerformanceAnalysis(
            metric_name=metric_name,
            time_window=time_window,
            tenant_id=tenant_id,
            mean=0.0,
            median=0.0,
            std_deviation=0.0,
            min_value=0.0,
            max_value=0.0,
            percentile_95=0.0,
            percentile_99=0.0,
            trend_direction="stable",
            trend_strength=0.0,
            performance_score=0.0,
            health_status="unknown",
            recommendations=["No data available for analysis."],
            sample_count=0
        )
    
    async def _analyze_application_performance(
        self,
        time_window: TimeWindow,
        tenant_id: Optional[str]
    ) -> Dict[str, PerformanceAnalysis]:
        """Analyze application-level performance"""
        app_metrics = [
            "http_request_duration_seconds",
            "http_requests_total",
            "http_errors_total"
        ]
        
        results = {}
        for metric in app_metrics:
            analysis = await self.analyze_performance(metric, time_window, tenant_id)
            results[metric] = analysis
        
        return results
    
    def _calculate_overall_score(self, sections: Dict[str, Any]) -> float:
        """Calculate overall performance score from all sections"""
        try:
            all_scores = []
            
            for section_name, section_data in sections.items():
                if isinstance(section_data, dict):
                    for metric_name, analysis in section_data.items():
                        if hasattr(analysis, 'performance_score'):
                            all_scores.append(analysis.performance_score)
            
            return statistics.mean(all_scores) if all_scores else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating overall score: {e}")
            return 0.0
    
    def _generate_performance_summary(self, report: Dict[str, Any]) -> str:
        """Generate performance summary text"""
        try:
            overall_score = report.get("overall_score", 0)
            health_status = self._determine_health_status(overall_score)
            
            summary = f"Overall system performance is {health_status} with a score of {overall_score:.1f}/100. "
            
            # Add specific insights
            if overall_score >= 90:
                summary += "All systems are performing excellently."
            elif overall_score >= 75:
                summary += "Most systems are performing well with minor optimization opportunities."
            elif overall_score >= 50:
                summary += "Performance degradation detected in several areas requiring attention."
            else:
                summary += "Critical performance issues detected requiring immediate action."
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return "Performance analysis completed."
    
    def _generate_report_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations from full report"""
        try:
            all_recommendations = []
            
            for section_name, section_data in report.get("sections", {}).items():
                if isinstance(section_data, dict):
                    for metric_name, analysis in section_data.items():
                        if hasattr(analysis, 'recommendations'):
                            all_recommendations.extend(analysis.recommendations)
            
            # Deduplicate and prioritize
            unique_recommendations = list(set(all_recommendations))
            
            # Sort by priority (critical issues first)
            critical_recommendations = [r for r in unique_recommendations if "critical" in r.lower()]
            warning_recommendations = [r for r in unique_recommendations if "warning" in r.lower() or "degradation" in r.lower()]
            other_recommendations = [r for r in unique_recommendations if r not in critical_recommendations + warning_recommendations]
            
            return critical_recommendations + warning_recommendations + other_recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating report recommendations: {e}")
            return []
    
    def _rank_tenants_by_performance(
        self,
        tenant_analyses: Dict[str, PerformanceAnalysis]
    ) -> List[Dict[str, Any]]:
        """Rank tenants by performance score"""
        try:
            rankings = []
            
            for tenant_id, analysis in tenant_analyses.items():
                rankings.append({
                    "tenant_id": tenant_id,
                    "performance_score": analysis.performance_score,
                    "health_status": analysis.health_status
                })
            
            # Sort by performance score (descending)
            rankings.sort(key=lambda x: x["performance_score"], reverse=True)
            
            # Add rank numbers
            for i, ranking in enumerate(rankings):
                ranking["rank"] = i + 1
            
            return rankings
            
        except Exception as e:
            self.logger.error(f"Error ranking tenants: {e}")
            return []
    
    def _identify_performance_gaps(
        self,
        tenant_analyses: Dict[str, PerformanceAnalysis]
    ) -> Dict[str, Any]:
        """Identify performance gaps between tenants"""
        try:
            scores = [analysis.performance_score for analysis in tenant_analyses.values()]
            
            if not scores:
                return {}
            
            return {
                "performance_range": {
                    "min": min(scores),
                    "max": max(scores),
                    "gap": max(scores) - min(scores)
                },
                "performance_variance": statistics.variance(scores) if len(scores) > 1 else 0,
                "underperforming_tenants": [
                    tenant_id for tenant_id, analysis in tenant_analyses.items()
                    if analysis.performance_score < statistics.mean(scores) - statistics.stdev(scores)
                ] if len(scores) > 1 else []
            }
            
        except Exception as e:
            self.logger.error(f"Error identifying performance gaps: {e}")
            return {}
    
    def _identify_best_practices(
        self,
        tenant_analyses: Dict[str, PerformanceAnalysis]
    ) -> List[str]:
        """Identify best practices from top-performing tenants"""
        try:
            # Find top performing tenant
            best_tenant = max(
                tenant_analyses.items(),
                key=lambda x: x[1].performance_score,
                default=(None, None)
            )
            
            if not best_tenant[0]:
                return []
            
            best_practices = [
                f"Top performing tenant ({best_tenant[0]}) demonstrates excellent performance patterns.",
                "Consider analyzing configuration and usage patterns of high-performing tenants.",
                "Implement performance monitoring and alerting based on top performer benchmarks."
            ]
            
            return best_practices
            
        except Exception as e:
            self.logger.error(f"Error identifying best practices: {e}")
            return []
    
    def _initialize_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize performance thresholds for different metrics"""
        return {
            "http_request_duration_seconds": {
                "excellent": 0.1,   # 100ms
                "good": 0.25,       # 250ms
                "warning": 0.5,     # 500ms
                "critical": 1.0     # 1s
            },
            "http_errors_total": {
                "excellent": 0.01,  # 1%
                "good": 0.02,       # 2%
                "warning": 0.05,    # 5%
                "critical": 0.1     # 10%
            },
            "system_cpu_percent": {
                "excellent": 50,    # 50%
                "good": 70,         # 70%
                "warning": 80,      # 80%
                "critical": 90      # 90%
            },
            "ai_inference_duration_seconds": {
                "excellent": 0.05,  # 50ms
                "good": 0.1,        # 100ms
                "warning": 0.25,    # 250ms
                "critical": 0.5     # 500ms
            },
            "fingerprint_processing_duration_seconds": {
                "excellent": 1.0,   # 1s
                "good": 3.0,        # 3s
                "warning": 5.0,     # 5s
                "critical": 10.0    # 10s
            }
        }
