"""Data Aggregator - Advanced Analytics Data Processing

Sophisticated data aggregation engine for time-series analytics, business intelligence,
and performance optimization for multi-format content creator platform.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
ANY unauthorized use, reproduction, or distribution is STRICTLY PROHIBITED.
Legal action will be taken against violators under German and international law.
Contact mlaiel@live.de for licensing inquiries.

Team Specialists:
- Lead IA Developer: Fahed Mlaiel (mlaiel@live.de)
- Backend Senior Engineer: Advanced microservices architecture
- ML Engineer: Deep learning & analytics algorithms
- Database Administrator: High-performance data optimization
- Security Expert: Enterprise-grade protection systems
- Microservices Architect: Scalable distributed systems
- Audio Processing Specialist: Advanced audio AI algorithms
- DevOps Engineer: Production-ready infrastructure
- IA Prompt Engineer: Optimized AI model interactions
"""import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import statistics
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from scipy import stats

from .exceptions import AggregationError, DataProcessingError
from .collector import MetricPoint, AggregatedMetric, AggregationMethod

logger = logging.getLogger(__name__)


class TimeWindow(Enum):
    """Time window for aggregation"""    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class TrendDirection(Enum):
    """Trend direction analysis"""    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class AggregationConfig:
    """Configuration for data aggregation"""    time_window: TimeWindow = TimeWindow.HOUR
    aggregation_method: AggregationMethod = AggregationMethod.AVERAGE
    include_trends: bool = True
    include_anomalies: bool = True
    percentiles: List[float] = field(default_factory=lambda: [50, 75, 90, 95, 99])
    retention_days: int = 90


@dataclass
class TimeSeriesPoint:
    """Time series data point"""    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'metadata': self.metadata
        }


@dataclass
class AggregationResult:
    """Result of data aggregation operation"""    metric_name: str
    time_window: TimeWindow
    aggregation_method: AggregationMethod
    period_start: datetime
    period_end: datetime
    data_points: List[TimeSeriesPoint]
    statistics: Dict[str, float]
    trends: Dict[str, Any]
    anomalies: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        return {
            'metric_name': self.metric_name,
            'time_window': self.time_window.value,
            'aggregation_method': self.aggregation_method.value,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'data_points': [point.to_dict() for point in self.data_points],
            'statistics': self.statistics,
            'trends': self.trends,
            'anomalies': self.anomalies
        }


class DataAggregator:
    """    Advanced data aggregation engine for analytics processing.
    
    Provides sophisticated time-series aggregation, statistical analysis,
    trend detection, and anomaly identification for business intelligence.
    """    
    def __init__(self, config: Optional[AggregationConfig] = None):
        self.config = config or AggregationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Storage for aggregated data
        self.aggregated_data = defaultdict(list)
        self.time_series_cache = defaultdict(deque)
        
        # Processing state
        self.processing_stats = {
            'total_processed': 0,
            'aggregations_created': 0,
            'anomalies_detected': 0,
            'last_processing': None
        }
        
        # Thread pool for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Cache for expensive calculations
        self.calculation_cache = {}
    
    async def initialize(self) -> None:
        """Initialize the data aggregator"""        try:
            self.logger.info("Initializing DataAggregator...")
            
            # Initialize any required resources
            await self._initialize_storage()
            
            self.logger.info("DataAggregator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize DataAggregator: {str(e)}")
            raise AggregationError(f"Initialization failed: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown the data aggregator"""        try:
            self.logger.info("Shutting down DataAggregator...")
            
            # Process any remaining data
            await self.process_batch()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            self.logger.info("DataAggregator shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error shutting down DataAggregator: {str(e)}")
            raise AggregationError(f"Shutdown failed: {str(e)}")
    
    async def aggregate_metrics(
        self,
        metrics: List[MetricPoint],
        time_window: Optional[TimeWindow] = None,
        aggregation_method: Optional[AggregationMethod] = None
    ) -> List[AggregationResult]:
        """Aggregate metrics by time window"""        try:
            time_window = time_window or self.config.time_window
            aggregation_method = aggregation_method or self.config.aggregation_method
            
            # Group metrics by name and time window
            grouped_metrics = self._group_metrics_by_time_window(metrics, time_window)
            
            results = []
            for metric_name, time_groups in grouped_metrics.items():
                for time_key, metric_group in time_groups.items():
                    result = await self._aggregate_metric_group(
                        metric_name,
                        metric_group,
                        time_window,
                        aggregation_method
                    )
                    results.append(result)
            
            self.processing_stats['aggregations_created'] += len(results)
            self.logger.info(f"Created {len(results)} aggregation results")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error aggregating metrics: {str(e)}")
            raise AggregationError(f"Metrics aggregation failed: {str(e)}")
    
    async def get_time_series(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        time_window: Optional[TimeWindow] = None
    ) -> List[TimeSeriesPoint]:
        """Get time series data for a metric"""        try:
            time_window = time_window or self.config.time_window
            
            # Check cache first
            cache_key = f"{metric_name}_{start_time.isoformat()}_{end_time.isoformat()}_{time_window.value}"
            if cache_key in self.calculation_cache:
                return self.calculation_cache[cache_key]
            
            # Generate time series from aggregated data
            time_series = []
            
            # Get relevant aggregated data
            for result in self.aggregated_data[metric_name]:
                if (result.period_start >= start_time and 
                    result.period_end <= end_time and 
                    result.time_window == time_window):
                    time_series.extend(result.data_points)
            
            # Sort by timestamp
            time_series.sort(key=lambda x: x.timestamp)
            
            # Cache result
            self.calculation_cache[cache_key] = time_series
            
            return time_series
            
        except Exception as e:
            self.logger.error(f"Error getting time series: {str(e)}")
            raise AggregationError(f"Time series retrieval failed: {str(e)}")
    
    async def analyze_trends(
        self,
        metric_name: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze trends for a metric over specified period"""        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=period_days)
            
            # Get time series data
            time_series = await self.get_time_series(
                metric_name, start_time, end_time, TimeWindow.DAY
            )
            
            if len(time_series) < 3:
                return {'trend': TrendDirection.STABLE.value, 'confidence': 0.0}
            
            # Perform trend analysis in thread pool
            trend_analysis = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._perform_trend_analysis,
                time_series
            )
            
            return trend_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {str(e)}")
            raise AggregationError(f"Trend analysis failed: {str(e)}")
    
    async def detect_anomalies(
        self,
        metric_name: str,
        sensitivity: float = 2.0,
        period_days: int = 7
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in metric data"""        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=period_days)
            
            # Get time series data
            time_series = await self.get_time_series(
                metric_name, start_time, end_time, TimeWindow.HOUR
            )
            
            if len(time_series) < 10:
                return []
            
            # Perform anomaly detection in thread pool
            anomalies = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._detect_anomalies_statistical,
                time_series,
                sensitivity
            )
            
            self.processing_stats['anomalies_detected'] += len(anomalies)
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {str(e)}")
            raise AggregationError(f"Anomaly detection failed: {str(e)}")
    
    async def calculate_percentiles(
        self,
        metric_name: str,
        percentiles: Optional[List[float]] = None,
        period_days: int = 30
    ) -> Dict[str, float]:
        """Calculate percentiles for a metric"""        try:
            percentiles = percentiles or self.config.percentiles
            
            end_time = datetime.now()
            start_time = end_time - timedelta(days=period_days)
            
            # Get time series data
            time_series = await self.get_time_series(
                metric_name, start_time, end_time
            )
            
            if not time_series:
                return {}
            
            values = [point.value for point in time_series]
            
            # Calculate percentiles
            percentile_results = {}
            for p in percentiles:
                percentile_results[f'p{p}'] = np.percentile(values, p)
            
            return percentile_results
            
        except Exception as e:
            self.logger.error(f"Error calculating percentiles: {str(e)}")
            raise AggregationError(f"Percentile calculation failed: {str(e)}")
    
    async def get_aggregation_summary(self) -> Dict[str, Any]:
        """Get summary of aggregation operations"""        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'processing_stats': self.processing_stats.copy(),
                'metrics_aggregated': len(self.aggregated_data),
                'cache_size': len(self.calculation_cache),
                'time_windows_available': [tw.value for tw in TimeWindow],
                'aggregation_methods_available': [am.value for am in AggregationMethod]
            }
            
            # Add metrics breakdown
            summary['metrics_breakdown'] = {}
            for metric_name, results in self.aggregated_data.items():
                summary['metrics_breakdown'][metric_name] = {
                    'total_aggregations': len(results),
                    'latest_aggregation': results[-1].period_end.isoformat() if results else None
                }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting aggregation summary: {str(e)}")
            raise AggregationError(f"Summary generation failed: {str(e)}")
    
    async def process_batch(self) -> None:
        """Process batch operations"""        try:
            # Clean up old data
            await self._cleanup_old_data()
            
            # Clear cache if too large
            if len(self.calculation_cache) > 1000:
                self.calculation_cache.clear()
            
            self.processing_stats['last_processing'] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error in batch processing: {str(e)}")
            raise AggregationError(f"Batch processing failed: {str(e)}")
    
    # Private Methods
    
    async def _initialize_storage(self) -> None:
        """Initialize storage for aggregated data"""        # Initialize any required storage connections/setup
        pass
    
    def _group_metrics_by_time_window(
        self,
        metrics: List[MetricPoint],
        time_window: TimeWindow
    ) -> Dict[str, Dict[str, List[MetricPoint]]]:
        """Group metrics by name and time window"""        grouped = defaultdict(lambda: defaultdict(list))
        
        for metric in metrics:
            time_key = self._get_time_window_key(metric.timestamp, time_window)
            grouped[metric.name][time_key].append(metric)
        
        return grouped
    
    def _get_time_window_key(self, timestamp: datetime, time_window: TimeWindow) -> str:
        """Get time window key for grouping"""        if time_window == TimeWindow.MINUTE:
            return timestamp.strftime("%Y-%m-%d %H:%M")
        elif time_window == TimeWindow.HOUR:
            return timestamp.strftime("%Y-%m-%d %H")
        elif time_window == TimeWindow.DAY:
            return timestamp.strftime("%Y-%m-%d")
        elif time_window == TimeWindow.WEEK:
            year, week, _ = timestamp.isocalendar()
            return f"{year}-W{week:02d}"
        elif time_window == TimeWindow.MONTH:
            return timestamp.strftime("%Y-%m")
        elif time_window == TimeWindow.QUARTER:
            quarter = (timestamp.month - 1) // 3 + 1
            return f"{timestamp.year}-Q{quarter}"
        elif time_window == TimeWindow.YEAR:
            return str(timestamp.year)
        else:
            return timestamp.isoformat()
    
    async def _aggregate_metric_group(
        self,
        metric_name: str,
        metrics: List[MetricPoint],
        time_window: TimeWindow,
        aggregation_method: AggregationMethod
    ) -> AggregationResult:
        """Aggregate a group of metrics"""        if not metrics:
            raise ValueError("No metrics to aggregate")
        
        # Sort metrics by timestamp
        metrics.sort(key=lambda x: x.timestamp)
        
        # Calculate period boundaries
        period_start = metrics[0].timestamp
        period_end = metrics[-1].timestamp
        
        # Extract values
        values = [metric.value for metric in metrics]
        
        # Calculate aggregated value
        if aggregation_method == AggregationMethod.SUM:
            aggregated_value = sum(values)
        elif aggregation_method == AggregationMethod.AVERAGE:
            aggregated_value = statistics.mean(values)
        elif aggregation_method == AggregationMethod.MIN:
            aggregated_value = min(values)
        elif aggregation_method == AggregationMethod.MAX:
            aggregated_value = max(values)
        elif aggregation_method == AggregationMethod.COUNT:
            aggregated_value = len(values)
        elif aggregation_method == AggregationMethod.MEDIAN:
            aggregated_value = statistics.median(values)
        else:
            aggregated_value = statistics.mean(values)  # Default to average
        
        # Create time series points
        data_points = [
            TimeSeriesPoint(
                timestamp=metric.timestamp,
                value=metric.value,
                metadata=metric.metadata
            )
            for metric in metrics
        ]
        
        # Calculate statistics
        statistics_dict = {
            'count': len(values),
            'sum': sum(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
        }
        
        # Calculate trends if enabled
        trends = {}
        if self.config.include_trends and len(values) > 2:
            trends = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._calculate_basic_trend,
                values
            )
        
        # Detect anomalies if enabled
        anomalies = []
        if self.config.include_anomalies and len(values) > 5:
            anomalies = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._detect_anomalies_statistical,
                data_points,
                2.0  # Default sensitivity
            )
        
        result = AggregationResult(
            metric_name=metric_name,
            time_window=time_window,
            aggregation_method=aggregation_method,
            period_start=period_start,
            period_end=period_end,
            data_points=data_points,
            statistics=statistics_dict,
            trends=trends,
            anomalies=anomalies
        )
        
        # Store result
        self.aggregated_data[metric_name].append(result)
        
        return result
    
    def _perform_trend_analysis(self, time_series: List[TimeSeriesPoint]) -> Dict[str, Any]:
        """Perform trend analysis on time series data"""        values = [point.value for point in time_series]
        timestamps = [point.timestamp for point in time_series]
        
        # Convert timestamps to numeric values for regression
        timestamp_values = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
        
        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(timestamp_values, values)
        
        # Determine trend direction
        if abs(slope) < std_err:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING
        
        # Calculate volatility
        volatility = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
        
        if volatility > 0.3:  # High volatility threshold
            direction = TrendDirection.VOLATILE
        
        return {
            'trend': direction.value,
            'slope': slope,
            'correlation': r_value,
            'p_value': p_value,
            'confidence': max(0, 1 - p_value),
            'volatility': volatility,
            'trend_strength': abs(r_value)
        }
    
    def _calculate_basic_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate basic trend information"""        if len(values) < 3:
            return {'trend': 'insufficient_data'}
        
        # Calculate simple moving averages
        window_size = min(5, len(values) // 2)
        if window_size < 2:
            return {'trend': 'insufficient_data'}
        
        early_avg = statistics.mean(values[:window_size])
        late_avg = statistics.mean(values[-window_size:])
        
        trend_change = (late_avg - early_avg) / early_avg if early_avg != 0 else 0
        
        if abs(trend_change) < 0.05:  # Less than 5% change
            direction = TrendDirection.STABLE
        elif trend_change > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING
        
        return {
            'trend': direction.value,
            'trend_change_percent': trend_change * 100,
            'early_average': early_avg,
            'late_average': late_avg
        }
    
    def _detect_anomalies_statistical(
        self,
        time_series: List[TimeSeriesPoint],
        sensitivity: float
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using statistical methods"""        if len(time_series) < 10:
            return []
        
        values = [point.value for point in time_series]
        
        # Calculate mean and standard deviation
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        # Z-score method
        anomalies = []
        threshold = sensitivity * std_dev
        
        for i, point in enumerate(time_series):
            z_score = abs(point.value - mean_value) / std_dev if std_dev > 0 else 0
            
            if z_score > sensitivity:
                anomalies.append({
                    'timestamp': point.timestamp.isoformat(),
                    'value': point.value,
                    'z_score': z_score,
                    'severity': 'high' if z_score > sensitivity * 1.5 else 'medium',
                    'deviation_from_mean': point.value - mean_value,
                    'index': i
                })
        
        return anomalies
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old aggregated data"""        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
            
            for metric_name in list(self.aggregated_data.keys()):
                # Remove old aggregation results
                self.aggregated_data[metric_name] = [
                    result for result in self.aggregated_data[metric_name]
                    if result.period_end > cutoff_date
                ]
                
                # Remove empty entries
                if not self.aggregated_data[metric_name]:
                    del self.aggregated_data[metric_name]
            
            self.logger.debug(f"Cleaned up data older than {cutoff_date}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {str(e)}")


class TimeSeriesAggregator(DataAggregator):
    """    Specialized aggregator for time-series data with advanced forecasting
    and seasonal analysis capabilities.
    """    
    def __init__(self, config: Optional[AggregationConfig] = None):
        super().__init__(config)
        
        # Time series specific configuration
        self.seasonal_detection_enabled = True
        self.forecasting_enabled = True
        self.forecast_horizon_days = 7
    
    async def analyze_seasonality(
        self,
        metric_name: str,
        period_days: int = 90
    ) -> Dict[str, Any]:
        """Analyze seasonal patterns in time series data"""        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=period_days)
            
            # Get hourly time series data
            time_series = await self.get_time_series(
                metric_name, start_time, end_time, TimeWindow.HOUR
            )
            
            if len(time_series) < 168:  # Need at least a week of hourly data
                return {'seasonality': 'insufficient_data'}
            
            # Perform seasonality analysis in thread pool
            seasonality_analysis = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._analyze_seasonal_patterns,
                time_series
            )
            
            return seasonality_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing seasonality: {str(e)}")
            raise AggregationError(f"Seasonality analysis failed: {str(e)}")
    
    async def generate_forecast(
        self,
        metric_name: str,
        forecast_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate forecast for metric values"""        try:
            forecast_days = forecast_days or self.forecast_horizon_days
            
            # Get historical data (at least 30 days for good forecast)
            end_time = datetime.now()
            start_time = end_time - timedelta(days=max(30, forecast_days * 4))
            
            time_series = await self.get_time_series(
                metric_name, start_time, end_time, TimeWindow.DAY
            )
            
            if len(time_series) < 14:  # Need at least 2 weeks of data
                return {'forecast': 'insufficient_data'}
            
            # Generate forecast in thread pool
            forecast = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._generate_simple_forecast,
                time_series,
                forecast_days
            )
            
            return forecast
            
        except Exception as e:
            self.logger.error(f"Error generating forecast: {str(e)}")
            raise AggregationError(f"Forecast generation failed: {str(e)}")
    
    def _analyze_seasonal_patterns(self, time_series: List[TimeSeriesPoint]) -> Dict[str, Any]:
        """Analyze seasonal patterns in time series"""        if len(time_series) < 168:  # Less than a week
            return {'seasonality': 'insufficient_data'}
        
        # Group by hour of day
        hourly_patterns = defaultdict(list)
        daily_patterns = defaultdict(list)
        
        for point in time_series:
            hour = point.timestamp.hour
            day_of_week = point.timestamp.weekday()
            
            hourly_patterns[hour].append(point.value)
            daily_patterns[day_of_week].append(point.value)
        
        # Calculate hourly averages
        hourly_averages = {}
        for hour, values in hourly_patterns.items():
            hourly_averages[hour] = statistics.mean(values)
        
        # Calculate daily averages
        daily_averages = {}
        for day, values in daily_patterns.items():
            daily_averages[day] = statistics.mean(values)
        
        # Detect patterns
        hour_values = list(hourly_averages.values())
        day_values = list(daily_averages.values())
        
        hour_variance = statistics.variance(hour_values) if len(hour_values) > 1 else 0
        day_variance = statistics.variance(day_values) if len(day_values) > 1 else 0
        
        return {
            'seasonality': 'detected' if (hour_variance > 0 or day_variance > 0) else 'none',
            'hourly_patterns': hourly_averages,
            'daily_patterns': daily_averages,
            'hour_variance': hour_variance,
            'day_variance': day_variance,
            'peak_hour': max(hourly_averages, key=hourly_averages.get) if hourly_averages else None,
            'peak_day': max(daily_averages, key=daily_averages.get) if daily_averages else None
        }
    
    def _generate_simple_forecast(
        self,
        time_series: List[TimeSeriesPoint],
        forecast_days: int
    ) -> Dict[str, Any]:
        """Generate simple forecast using trend analysis"""        values = [point.value for point in time_series]
        
        # Calculate trend
        if len(values) < 7:
            return {'forecast': 'insufficient_data'}
        
        # Simple linear trend
        x = list(range(len(values)))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # Generate forecast points
        forecast_points = []
        last_timestamp = time_series[-1].timestamp
        
        for i in range(1, forecast_days + 1):
            forecast_timestamp = last_timestamp + timedelta(days=i)
            forecast_value = slope * (len(values) + i - 1) + intercept
            
            # Add some confidence intervals (simple approach)
            confidence_interval = std_err * 1.96  # 95% confidence
            
            forecast_points.append({
                'timestamp': forecast_timestamp.isoformat(),
                'value': max(0, forecast_value),  # Ensure non-negative
                'confidence_lower': max(0, forecast_value - confidence_interval),
                'confidence_upper': forecast_value + confidence_interval
            })
        
        return {
            'forecast': 'generated',
            'forecast_points': forecast_points,
            'trend_slope': slope,
            'trend_confidence': max(0, 1 - p_value),
            'forecast_accuracy_estimate': max(0, abs(r_value)),
            'method': 'linear_trend'
        }
