"""
📊 Business Intelligence Service
Enterprise business intelligence platform with real-time analytics and ML-powered insights

Demonstrates: DBA + ML Engineer + DevOps + Backend Senior expertise
Features: Real-time data processing, predictive analytics, automated reporting, dashboards

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import uuid
import json
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
import structlog
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import statistics
import hashlib
import pickle
import gzip
import base64

logger = structlog.get_logger(__name__)

class MetricType(str, Enum):
    """Types of business metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    RATIO = "ratio"
    PERCENTAGE = "percentage"

class DataSource(str, Enum):
    """Data source types"""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"
    WEBHOOK = "webhook"
    MANUAL = "manual"

class ReportFormat(str, Enum):
    """Report output formats"""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    HTML = "html"
    EXCEL = "excel"
    DASHBOARD = "dashboard"

class AggregationMethod(str, Enum):
    """Data aggregation methods"""
    SUM = "sum"
    COUNT = "count"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    DISTINCT_COUNT = "distinct_count"
    STANDARD_DEVIATION = "standard_deviation"

class TimeGranularity(str, Enum):
    """Time granularity for analytics"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class DataPoint:
    """Individual data point"""
    timestamp: datetime
    value: Union[float, int, str]
    dimensions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MetricDefinition(BaseModel):
    """Definition of a business metric"""
    metric_id: str = Field(..., description="Unique metric identifier")
    name: str = Field(..., description="Human-readable metric name")
    description: str = Field(..., description="Metric description")
    metric_type: MetricType
    unit: str = Field(..., description="Unit of measurement")
    data_source: DataSource
    query: str = Field(..., description="Query or calculation formula")
    dimensions: List[str] = Field(default_factory=list)
    aggregation_method: AggregationMethod = AggregationMethod.SUM
    is_real_time: bool = False
    refresh_interval_minutes: int = Field(default=60, ge=1)
    retention_days: int = Field(default=365, ge=1)
    alert_thresholds: Dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)

class KPITarget(BaseModel):
    """KPI target definition"""
    kpi_id: str
    target_value: float
    target_date: datetime
    target_type: str = "absolute"  # absolute, percentage, growth
    description: str
    owner: str
    created_at: datetime = Field(default_factory=datetime.now)

class AnalyticsQuery(BaseModel):
    """Analytics query request"""
    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metrics: List[str] = Field(..., description="Metric IDs to analyze")
    dimensions: List[str] = Field(default_factory=list)
    filters: Dict[str, Any] = Field(default_factory=dict)
    time_range: Tuple[datetime, datetime]
    granularity: TimeGranularity = TimeGranularity.DAY
    aggregation: AggregationMethod = AggregationMethod.SUM
    limit: Optional[int] = None
    format: ReportFormat = ReportFormat.JSON
    include_predictions: bool = False
    include_comparisons: bool = False

class AnalyticsResult(BaseModel):
    """Analytics query result"""
    query_id: str
    metrics: List[str]
    data: List[Dict[str, Any]]
    summary: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.now)
    execution_time_ms: float
    row_count: int
    predictions: Optional[List[Dict[str, Any]]] = None
    comparisons: Optional[Dict[str, Any]] = None

class Dashboard(BaseModel):
    """Dashboard configuration"""
    dashboard_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    widgets: List[Dict[str, Any]] = Field(default_factory=list)
    layout: Dict[str, Any] = Field(default_factory=dict)
    refresh_interval_minutes: int = Field(default=15, ge=1)
    is_public: bool = False
    owner: str
    viewers: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class MLModel(ABC):
    """Abstract base class for ML models"""
    
    def __init__(self, model_id: str, name: str):
        self.model_id = model_id
        self.name = name
        self.is_trained = False
        self.last_training = None
        self.accuracy_metrics = {}
    
    @abstractmethod
    async def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train the model"""
        pass
    
    @abstractmethod
    async def predict(self, data: pd.DataFrame) -> List[float]:
        """Make predictions"""
        pass
    
    @abstractmethod
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance"""
        pass

class TimeSeriesForecaster(MLModel):
    """Time series forecasting model for business metrics"""
    
    def __init__(self, model_id: str, name: str = "Time Series Forecaster"):
        super().__init__(model_id, name)
        self.seasonal_periods = 7  # Weekly seasonality
        self.trend_components = None
        self.seasonal_components = None
        self.residuals = None
        
    async def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train time series forecasting model"""
        try:
            # Simple decomposition and trend analysis
            if len(data) < self.seasonal_periods * 2:
                raise ValueError("Insufficient data for training")
            
            # Extract time series
            values = data['value'].values
            
            # Simple trend calculation (linear regression)
            x = np.arange(len(values))
            trend_coeff = np.polyfit(x, values, 1)
            self.trend_components = trend_coeff
            
            # Simple seasonal decomposition
            if len(values) >= self.seasonal_periods:
                seasonal_avg = []
                for i in range(self.seasonal_periods):
                    season_values = values[i::self.seasonal_periods]
                    seasonal_avg.append(np.mean(season_values))
                
                # Normalize seasonal components
                seasonal_avg = np.array(seasonal_avg)
                self.seasonal_components = seasonal_avg - np.mean(seasonal_avg)
            
            # Calculate residuals
            trend_values = np.polyval(self.trend_components, x)
            if self.seasonal_components is not None:
                seasonal_values = np.tile(self.seasonal_components, len(values) // self.seasonal_periods + 1)[:len(values)]
                predicted = trend_values + seasonal_values
            else:
                predicted = trend_values
            
            self.residuals = values - predicted
            
            # Calculate accuracy metrics
            mse = np.mean((values - predicted) ** 2)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(values - predicted))
            
            self.accuracy_metrics = {
                'mse': float(mse),
                'rmse': float(rmse),
                'mae': float(mae),
                'r2': float(1 - (np.sum((values - predicted) ** 2) / np.sum((values - np.mean(values)) ** 2)))
            }
            
            self.is_trained = True
            self.last_training = datetime.now()
            
            logger.info("Time series model trained successfully",
                       model_id=self.model_id,
                       data_points=len(data),
                       accuracy_metrics=self.accuracy_metrics)
            
            return self.accuracy_metrics
            
        except Exception as e:
            logger.error("Model training failed",
                        model_id=self.model_id,
                        error=str(e))
            raise
    
    async def predict(self, periods: int = 30) -> List[Dict[str, Any]]:
        """Generate forecasts for future periods"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            predictions = []
            base_time = datetime.now()
            
            for i in range(periods):
                # Trend component
                trend_value = np.polyval(self.trend_components, i)
                
                # Seasonal component
                if self.seasonal_components is not None:
                    seasonal_value = self.seasonal_components[i % self.seasonal_periods]
                else:
                    seasonal_value = 0
                
                # Add some noise based on residuals
                if self.residuals is not None and len(self.residuals) > 0:
                    noise = np.random.normal(0, np.std(self.residuals) * 0.5)
                else:
                    noise = 0
                
                predicted_value = trend_value + seasonal_value + noise
                
                # Confidence intervals (simplified)
                std_residual = np.std(self.residuals) if self.residuals is not None else predicted_value * 0.1
                confidence_lower = predicted_value - 1.96 * std_residual
                confidence_upper = predicted_value + 1.96 * std_residual
                
                predictions.append({
                    'timestamp': base_time + timedelta(days=i),
                    'predicted_value': float(predicted_value),
                    'confidence_lower': float(confidence_lower),
                    'confidence_upper': float(confidence_upper),
                    'trend_component': float(trend_value),
                    'seasonal_component': float(seasonal_value)
                })
            
            return predictions
            
        except Exception as e:
            logger.error("Prediction failed",
                        model_id=self.model_id,
                        error=str(e))
            raise
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance for time series components"""
        if not self.is_trained:
            return {}
        
        total_variance = np.var(self.trend_components) if self.trend_components is not None else 0
        seasonal_variance = np.var(self.seasonal_components) if self.seasonal_components is not None else 0
        residual_variance = np.var(self.residuals) if self.residuals is not None else 0
        
        total = total_variance + seasonal_variance + residual_variance
        
        if total == 0:
            return {'trend': 0.0, 'seasonal': 0.0, 'residual': 0.0}
        
        return {
            'trend': float(total_variance / total),
            'seasonal': float(seasonal_variance / total),
            'residual': float(residual_variance / total)
        }

class AnomalyDetector(MLModel):
    """Anomaly detection model for business metrics"""
    
    def __init__(self, model_id: str, name: str = "Anomaly Detector"):
        super().__init__(model_id, name)
        self.threshold_factor = 2.5  # Standard deviations for anomaly threshold
        self.historical_stats = None
        self.rolling_window = 30  # Days for rolling statistics
        
    async def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train anomaly detection model"""
        try:
            if len(data) < self.rolling_window:
                raise ValueError(f"Insufficient data for training (need at least {self.rolling_window} points)")
            
            # Calculate historical statistics
            values = data['value'].values
            
            self.historical_stats = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'median': float(np.median(values)),
                'q25': float(np.percentile(values, 25)),
                'q75': float(np.percentile(values, 75)),
                'min': float(np.min(values)),
                'max': float(np.max(values))
            }
            
            # Calculate IQR-based thresholds
            iqr = self.historical_stats['q75'] - self.historical_stats['q25']
            self.historical_stats['anomaly_threshold_lower'] = self.historical_stats['q25'] - 1.5 * iqr
            self.historical_stats['anomaly_threshold_upper'] = self.historical_stats['q75'] + 1.5 * iqr
            
            # Calculate Z-score based thresholds
            self.historical_stats['zscore_threshold_lower'] = self.historical_stats['mean'] - self.threshold_factor * self.historical_stats['std']
            self.historical_stats['zscore_threshold_upper'] = self.historical_stats['mean'] + self.threshold_factor * self.historical_stats['std']
            
            # Test accuracy on training data
            anomalies_detected = 0
            for value in values:
                if self._is_anomaly(value):
                    anomalies_detected += 1
            
            anomaly_rate = anomalies_detected / len(values)
            
            self.accuracy_metrics = {
                'anomaly_rate': float(anomaly_rate),
                'total_points': len(values),
                'anomalies_detected': anomalies_detected,
                'threshold_factor': self.threshold_factor
            }
            
            self.is_trained = True
            self.last_training = datetime.now()
            
            logger.info("Anomaly detection model trained successfully",
                       model_id=self.model_id,
                       data_points=len(data),
                       anomaly_rate=anomaly_rate)
            
            return self.accuracy_metrics
            
        except Exception as e:
            logger.error("Anomaly detection training failed",
                        model_id=self.model_id,
                        error=str(e))
            raise
    
    async def predict(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in data"""
        if not self.is_trained:
            raise ValueError("Model must be trained before detecting anomalies")
        
        try:
            results = []
            
            for _, row in data.iterrows():
                value = row['value']
                timestamp = row.get('timestamp', datetime.now())
                
                is_anomaly = self._is_anomaly(value)
                anomaly_score = self._calculate_anomaly_score(value)
                
                results.append({
                    'timestamp': timestamp,
                    'value': float(value),
                    'is_anomaly': is_anomaly,
                    'anomaly_score': float(anomaly_score),
                    'expected_range': {
                        'lower': self.historical_stats['anomaly_threshold_lower'],
                        'upper': self.historical_stats['anomaly_threshold_upper']
                    }
                })
            
            return results
            
        except Exception as e:
            logger.error("Anomaly detection failed",
                        model_id=self.model_id,
                        error=str(e))
            raise
    
    def _is_anomaly(self, value: float) -> bool:
        """Check if value is an anomaly"""
        if self.historical_stats is None:
            return False
        
        # Use IQR method
        return (value < self.historical_stats['anomaly_threshold_lower'] or 
                value > self.historical_stats['anomaly_threshold_upper'])
    
    def _calculate_anomaly_score(self, value: float) -> float:
        """Calculate anomaly score (0-1, higher = more anomalous)"""
        if self.historical_stats is None:
            return 0.0
        
        # Calculate Z-score
        if self.historical_stats['std'] == 0:
            return 0.0
        
        z_score = abs(value - self.historical_stats['mean']) / self.historical_stats['std']
        
        # Convert to 0-1 scale
        return min(z_score / self.threshold_factor, 1.0)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance for anomaly detection"""
        if not self.is_trained:
            return {}
        
        return {
            'statistical_deviation': 0.8,
            'historical_patterns': 0.2
        }

class BusinessIntelligenceService:
    """
    Enterprise Business Intelligence Service
    
    Demonstrates expertise in:
    - DBA: Advanced data modeling, query optimization, data warehouse management
    - ML Engineer: Predictive analytics, anomaly detection, automated insights
    - DevOps: Real-time processing, automated reporting, performance monitoring
    - Backend Senior: Complex data processing, async operations, caching strategies
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics_registry: Dict[str, MetricDefinition] = {}
        self.kpi_targets: Dict[str, KPITarget] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.ml_models: Dict[str, MLModel] = {}
        
        # Data storage (in production, would use proper data warehouse)
        self.metric_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100000))
        self.query_cache: Dict[str, Tuple[AnalyticsResult, datetime]] = {}
        
        self.metrics = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'ml_predictions_made': 0,
            'anomalies_detected': 0,
            'average_query_time': 0.0
        }
        
        # Initialize default ML models
        self._initialize_ml_models()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Business Intelligence Service initialized",
                   config=self.config)
    
    def _initialize_ml_models(self):
        """Initialize default ML models"""
        self.ml_models['revenue_forecaster'] = TimeSeriesForecaster(
            'revenue_forecaster', 'Revenue Forecasting Model'
        )
        self.ml_models['user_growth_forecaster'] = TimeSeriesForecaster(
            'user_growth_forecaster', 'User Growth Forecasting Model'
        )
        self.ml_models['anomaly_detector'] = AnomalyDetector(
            'anomaly_detector', 'General Anomaly Detection Model'
        )
    
    def _start_background_tasks(self):
        """Start background processing tasks"""
        # In production, would start proper background tasks
        pass
    
    async def register_metric(self, metric_def: MetricDefinition) -> bool:
        """
        Register a new business metric
        
        DBA: Data modeling, metric definition storage
        Backend Senior: Validation, error handling
        """
        try:
            # Validate metric definition
            if metric_def.metric_id in self.metrics_registry:
                logger.warning("Metric already exists", metric_id=metric_def.metric_id)
                return False
            
            # Store metric definition
            self.metrics_registry[metric_def.metric_id] = metric_def
            
            # Initialize data storage for metric
            if metric_def.metric_id not in self.metric_data:
                self.metric_data[metric_def.metric_id] = deque(maxlen=100000)
            
            logger.info("Metric registered successfully",
                       metric_id=metric_def.metric_id,
                       name=metric_def.name,
                       type=metric_def.metric_type)
            
            return True
            
        except Exception as e:
            logger.error("Metric registration failed",
                        metric_id=metric_def.metric_id,
                        error=str(e))
            return False
    
    async def ingest_data(self, metric_id: str, data_points: List[DataPoint]) -> bool:
        """
        Ingest data points for a metric
        
        DBA: Data ingestion, storage optimization
        DevOps: Real-time processing, performance monitoring
        """
        try:
            if metric_id not in self.metrics_registry:
                logger.error("Metric not found", metric_id=metric_id)
                return False
            
            metric_def = self.metrics_registry[metric_id]
            
            # Validate and store data points
            for data_point in data_points:
                # Basic validation
                if not isinstance(data_point.value, (int, float, str)):
                    logger.warning("Invalid data point value", 
                                 metric_id=metric_id,
                                 value=data_point.value)
                    continue
                
                # Store data point
                self.metric_data[metric_id].append({
                    'timestamp': data_point.timestamp,
                    'value': data_point.value,
                    'dimensions': data_point.dimensions,
                    'metadata': data_point.metadata
                })
            
            # Trigger anomaly detection if real-time
            if metric_def.is_real_time and 'anomaly_detector' in self.ml_models:
                await self._check_for_anomalies(metric_id, data_points)
            
            logger.info("Data ingested successfully",
                       metric_id=metric_id,
                       data_points_count=len(data_points))
            
            return True
            
        except Exception as e:
            logger.error("Data ingestion failed",
                        metric_id=metric_id,
                        error=str(e))
            return False
    
    async def execute_analytics_query(self, query: AnalyticsQuery) -> AnalyticsResult:
        """
        Execute analytics query with ML predictions
        
        DBA: Query optimization, data aggregation
        ML Engineer: Predictive analytics integration
        Backend Senior: Performance optimization, caching
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                self.metrics['cache_hits'] += 1
                logger.info("Query served from cache", query_id=query.query_id)
                return cached_result
            
            self.metrics['cache_misses'] += 1
            
            # Execute query
            result_data = []
            summary = {}
            
            for metric_id in query.metrics:
                if metric_id not in self.metrics_registry:
                    logger.warning("Metric not found in query", metric_id=metric_id)
                    continue
                
                metric_data = await self._get_metric_data(
                    metric_id, query.time_range, query.filters, query.granularity
                )
                
                # Aggregate data
                aggregated_data = await self._aggregate_data(
                    metric_data, query.aggregation, query.granularity
                )
                
                result_data.extend(aggregated_data)
                
                # Calculate summary statistics
                if aggregated_data:
                    values = [d['value'] for d in aggregated_data if isinstance(d['value'], (int, float))]
                    if values:
                        summary[metric_id] = {
                            'count': len(values),
                            'sum': sum(values),
                            'average': statistics.mean(values),
                            'min': min(values),
                            'max': max(values),
                            'median': statistics.median(values)
                        }
            
            # Apply limit if specified
            if query.limit:
                result_data = result_data[:query.limit]
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Create result
            result = AnalyticsResult(
                query_id=query.query_id,
                metrics=query.metrics,
                data=result_data,
                summary=summary,
                execution_time_ms=execution_time,
                row_count=len(result_data)
            )
            
            # Add predictions if requested
            if query.include_predictions and result_data:
                predictions = await self._generate_predictions(query.metrics, result_data)
                result.predictions = predictions
            
            # Add comparisons if requested
            if query.include_comparisons:
                comparisons = await self._generate_comparisons(query.metrics, query.time_range)
                result.comparisons = comparisons
            
            # Cache result
            self._cache_result(cache_key, result)
            
            # Update metrics
            self.metrics['total_queries'] += 1
            self._update_average_query_time(execution_time)
            
            logger.info("Analytics query executed successfully",
                       query_id=query.query_id,
                       execution_time_ms=execution_time,
                       row_count=len(result_data))
            
            return result
            
        except Exception as e:
            logger.error("Analytics query execution failed",
                        query_id=query.query_id,
                        error=str(e))
            raise
    
    async def _get_metric_data(self, metric_id: str, time_range: Tuple[datetime, datetime],
                              filters: Dict[str, Any], granularity: TimeGranularity) -> List[Dict[str, Any]]:
        """Get metric data for specified time range and filters"""
        start_time, end_time = time_range
        data = self.metric_data.get(metric_id, [])
        
        # Filter by time range
        filtered_data = [
            d for d in data
            if start_time <= d['timestamp'] <= end_time
        ]
        
        # Apply additional filters
        for filter_key, filter_value in filters.items():
            if filter_key in ['dimensions', 'metadata']:
                filtered_data = [
                    d for d in filtered_data
                    if filter_value in d.get(filter_key, {}).values()
                ]
            else:
                filtered_data = [
                    d for d in filtered_data
                    if d.get(filter_key) == filter_value
                ]
        
        return filtered_data
    
    async def _aggregate_data(self, data: List[Dict[str, Any]], 
                            aggregation: AggregationMethod,
                            granularity: TimeGranularity) -> List[Dict[str, Any]]:
        """Aggregate data by time granularity and method"""
        if not data:
            return []
        
        # Group by time granularity
        time_groups = defaultdict(list)
        
        for item in data:
            timestamp = item['timestamp']
            
            # Round timestamp to granularity
            if granularity == TimeGranularity.MINUTE:
                key = timestamp.replace(second=0, microsecond=0)
            elif granularity == TimeGranularity.HOUR:
                key = timestamp.replace(minute=0, second=0, microsecond=0)
            elif granularity == TimeGranularity.DAY:
                key = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            elif granularity == TimeGranularity.WEEK:
                days_since_monday = timestamp.weekday()
                key = (timestamp - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif granularity == TimeGranularity.MONTH:
                key = timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                key = timestamp  # Default to original timestamp
            
            time_groups[key].append(item)
        
        # Aggregate each group
        aggregated_data = []
        
        for timestamp, group_data in time_groups.items():
            values = []
            for item in group_data:
                if isinstance(item['value'], (int, float)):
                    values.append(item['value'])
            
            if not values:
                continue
            
            # Apply aggregation method
            if aggregation == AggregationMethod.SUM:
                agg_value = sum(values)
            elif aggregation == AggregationMethod.COUNT:
                agg_value = len(values)
            elif aggregation == AggregationMethod.AVERAGE:
                agg_value = statistics.mean(values)
            elif aggregation == AggregationMethod.MIN:
                agg_value = min(values)
            elif aggregation == AggregationMethod.MAX:
                agg_value = max(values)
            elif aggregation == AggregationMethod.MEDIAN:
                agg_value = statistics.median(values)
            elif aggregation == AggregationMethod.STANDARD_DEVIATION:
                agg_value = statistics.stdev(values) if len(values) > 1 else 0
            else:
                agg_value = sum(values)  # Default to sum
            
            aggregated_data.append({
                'timestamp': timestamp,
                'value': agg_value,
                'count': len(group_data),
                'granularity': granularity.value
            })
        
        # Sort by timestamp
        aggregated_data.sort(key=lambda x: x['timestamp'])
        
        return aggregated_data
    
    async def _generate_predictions(self, metric_ids: List[str], 
                                  historical_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate ML predictions for metrics"""
        predictions = []
        
        try:
            for metric_id in metric_ids:
                if metric_id not in self.metrics_registry:
                    continue
                
                # Get forecasting model
                forecaster = self.ml_models.get(f'{metric_id}_forecaster') or self.ml_models.get('revenue_forecaster')
                
                if not forecaster or not isinstance(forecaster, TimeSeriesForecaster):
                    continue
                
                # Prepare training data
                metric_historical = [d for d in historical_data if d.get('metric_id') == metric_id]
                if len(metric_historical) < 10:  # Need sufficient data
                    continue
                
                # Convert to DataFrame
                df = pd.DataFrame(metric_historical)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
                
                # Train model if not already trained or data is stale
                if not forecaster.is_trained or (
                    forecaster.last_training and 
                    (datetime.now() - forecaster.last_training).days > 7
                ):
                    await forecaster.train(df)
                
                # Generate predictions
                forecast = await forecaster.predict(periods=30)  # 30 days ahead
                
                for pred in forecast:
                    predictions.append({
                        'metric_id': metric_id,
                        **pred
                    })
                
                self.metrics['ml_predictions_made'] += len(forecast)
            
            logger.info("Predictions generated",
                       metrics_count=len(metric_ids),
                       predictions_count=len(predictions))
            
        except Exception as e:
            logger.error("Prediction generation failed", error=str(e))
        
        return predictions
    
    async def _generate_comparisons(self, metric_ids: List[str], 
                                  time_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Generate period-over-period comparisons"""
        comparisons = {}
        
        try:
            start_time, end_time = time_range
            period_length = end_time - start_time
            
            # Previous period
            prev_start = start_time - period_length
            prev_end = start_time
            
            for metric_id in metric_ids:
                current_data = await self._get_metric_data(
                    metric_id, (start_time, end_time), {}, TimeGranularity.DAY
                )
                prev_data = await self._get_metric_data(
                    metric_id, (prev_start, prev_end), {}, TimeGranularity.DAY
                )
                
                # Calculate totals
                current_total = sum(d['value'] for d in current_data if isinstance(d['value'], (int, float)))
                prev_total = sum(d['value'] for d in prev_data if isinstance(d['value'], (int, float)))
                
                # Calculate change
                change = current_total - prev_total
                change_percent = (change / prev_total * 100) if prev_total != 0 else 0
                
                comparisons[metric_id] = {
                    'current_period': current_total,
                    'previous_period': prev_total,
                    'absolute_change': change,
                    'percentage_change': change_percent,
                    'trend': 'up' if change > 0 else 'down' if change < 0 else 'flat'
                }
        
        except Exception as e:
            logger.error("Comparison generation failed", error=str(e))
        
        return comparisons
    
    async def _check_for_anomalies(self, metric_id: str, data_points: List[DataPoint]):
        """Check for anomalies in real-time data"""
        try:
            anomaly_detector = self.ml_models.get('anomaly_detector')
            if not anomaly_detector or not isinstance(anomaly_detector, AnomalyDetector):
                return
            
            # Prepare data for anomaly detection
            df_data = []
            for dp in data_points:
                if isinstance(dp.value, (int, float)):
                    df_data.append({
                        'timestamp': dp.timestamp,
                        'value': dp.value
                    })
            
            if not df_data:
                return
            
            df = pd.DataFrame(df_data)
            
            # Train model if not trained
            if not anomaly_detector.is_trained:
                # Get historical data for training
                historical_data = self.metric_data.get(metric_id, [])
                if len(historical_data) >= 30:  # Need sufficient history
                    hist_df = pd.DataFrame([
                        {'timestamp': d['timestamp'], 'value': d['value']}
                        for d in historical_data
                        if isinstance(d['value'], (int, float))
                    ])
                    await anomaly_detector.train(hist_df)
            
            if anomaly_detector.is_trained:
                # Detect anomalies
                anomalies = await anomaly_detector.predict(df)
                
                for anomaly in anomalies:
                    if anomaly['is_anomaly']:
                        self.metrics['anomalies_detected'] += 1
                        logger.warning("Anomaly detected",
                                     metric_id=metric_id,
                                     timestamp=anomaly['timestamp'],
                                     value=anomaly['value'],
                                     score=anomaly['anomaly_score'])
        
        except Exception as e:
            logger.error("Anomaly detection failed",
                        metric_id=metric_id,
                        error=str(e))
    
    def _generate_cache_key(self, query: AnalyticsQuery) -> str:
        """Generate cache key for query"""
        key_data = {
            'metrics': sorted(query.metrics),
            'dimensions': sorted(query.dimensions),
            'filters': sorted(query.filters.items()),
            'time_range': [query.time_range[0].isoformat(), query.time_range[1].isoformat()],
            'granularity': query.granularity.value,
            'aggregation': query.aggregation.value,
            'limit': query.limit
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[AnalyticsResult]:
        """Get cached query result"""
        if cache_key in self.query_cache:
            result, cached_at = self.query_cache[cache_key]
            
            # Check if cache is still valid (15 minutes)
            if datetime.now() - cached_at < timedelta(minutes=15):
                return result
            else:
                # Remove expired cache entry
                del self.query_cache[cache_key]
        
        return None
    
    def _cache_result(self, cache_key: str, result: AnalyticsResult):
        """Cache query result"""
        self.query_cache[cache_key] = (result, datetime.now())
        
        # Limit cache size
        if len(self.query_cache) > 1000:
            # Remove oldest entries
            sorted_cache = sorted(self.query_cache.items(), key=lambda x: x[1][1])
            for old_key, _ in sorted_cache[:100]:  # Remove oldest 100
                del self.query_cache[old_key]
    
    def _update_average_query_time(self, execution_time: float):
        """Update average query execution time"""
        total = self.metrics['total_queries']
        if total <= 1:
            self.metrics['average_query_time'] = execution_time
        else:
            current_avg = self.metrics['average_query_time']
            self.metrics['average_query_time'] = (
                (current_avg * (total - 1) + execution_time) / total
            )
    
    async def create_dashboard(self, dashboard: Dashboard) -> bool:
        """Create a new dashboard"""
        try:
            self.dashboards[dashboard.dashboard_id] = dashboard
            
            logger.info("Dashboard created",
                       dashboard_id=dashboard.dashboard_id,
                       name=dashboard.name,
                       widgets_count=len(dashboard.widgets))
            
            return True
            
        except Exception as e:
            logger.error("Dashboard creation failed",
                        dashboard_id=dashboard.dashboard_id,
                        error=str(e))
            return False
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics"""
        cache_hit_rate = 0.0
        if self.metrics['cache_hits'] + self.metrics['cache_misses'] > 0:
            cache_hit_rate = self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses'])
        
        return {
            **self.metrics,
            'cache_hit_rate': cache_hit_rate,
            'registered_metrics': len(self.metrics_registry),
            'active_dashboards': len(self.dashboards),
            'ml_models': len(self.ml_models),
            'trained_models': len([m for m in self.ml_models.values() if m.is_trained]),
            'cache_size': len(self.query_cache),
            'data_points_stored': sum(len(data) for data in self.metric_data.values()),
            'service_status': 'healthy'
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            'service': 'business_intelligence_service',
            'status': 'healthy',
            'version': '1.0.0',
            'metrics_registered': len(self.metrics_registry),
            'dashboards': len(self.dashboards),
            'ml_models': {
                model_id: {
                    'trained': model.is_trained,
                    'last_training': model.last_training.isoformat() if model.last_training else None
                }
                for model_id, model in self.ml_models.items()
            }
        }

# Example usage and testing
async def example_usage():
    """Example usage of the Business Intelligence Service"""
    
    # Initialize service
    bi_service = BusinessIntelligenceService()
    
    # Register business metrics
    revenue_metric = MetricDefinition(
        metric_id="daily_revenue",
        name="Daily Revenue",
        description="Total daily revenue from all sources",
        metric_type=MetricType.COUNTER,
        unit="USD",
        data_source=DataSource.DATABASE,
        query="SELECT SUM(amount) FROM transactions WHERE date = ?",
        aggregation_method=AggregationMethod.SUM,
        is_real_time=True,
        refresh_interval_minutes=15
    )
    
    user_growth_metric = MetricDefinition(
        metric_id="user_signups",
        name="User Signups",
        description="Number of new user registrations",
        metric_type=MetricType.COUNTER,
        unit="users",
        data_source=DataSource.API,
        query="users/signups",
        aggregation_method=AggregationMethod.COUNT,
        is_real_time=True,
        refresh_interval_minutes=5
    )
    
    await bi_service.register_metric(revenue_metric)
    await bi_service.register_metric(user_growth_metric)
    
    # Ingest sample data
    import random
    from datetime import timedelta
    
    # Generate sample revenue data for last 30 days
    revenue_data = []
    user_data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        
        # Revenue data with some trend and seasonality
        base_revenue = 1000 + i * 50  # Growing trend
        seasonal_factor = 1.2 if date.weekday() < 5 else 0.8  # Higher on weekdays
        noise = random.uniform(0.8, 1.2)
        revenue = base_revenue * seasonal_factor * noise
        
        revenue_data.append(DataPoint(
            timestamp=date,
            value=round(revenue, 2),
            dimensions={'source': 'sales', 'region': 'north_america'}
        ))
        
        # User signup data
        base_users = 50 + i * 2
        user_noise = random.uniform(0.7, 1.5)
        users = int(base_users * user_noise)
        
        user_data.append(DataPoint(
            timestamp=date,
            value=users,
            dimensions={'source': 'organic', 'platform': 'web'}
        ))
    
    await bi_service.ingest_data("daily_revenue", revenue_data)
    await bi_service.ingest_data("user_signups", user_data)
    
    # Execute analytics query
    query = AnalyticsQuery(
        metrics=["daily_revenue", "user_signups"],
        time_range=(base_date, datetime.now()),
        granularity=TimeGranularity.DAY,
        aggregation=AggregationMethod.SUM,
        include_predictions=True,
        include_comparisons=True
    )
    
    result = await bi_service.execute_analytics_query(query)
    
    print(f"Query Results:")
    print(f"- Execution time: {result.execution_time_ms:.2f}ms")
    print(f"- Row count: {result.row_count}")
    print(f"- Summary: {result.summary}")
    
    if result.predictions:
        print(f"- Predictions generated: {len(result.predictions)}")
    
    if result.comparisons:
        print(f"- Comparisons: {result.comparisons}")
    
    # Get service metrics
    metrics = await bi_service.get_service_metrics()
    print(f"Service metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(example_usage())