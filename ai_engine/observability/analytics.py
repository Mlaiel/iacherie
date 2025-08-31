"""Real-time Analytics Engine

Advanced real-time analytics system for the IA Influencer platform providing
comprehensive data analysis, business intelligence, and predictive insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""
import asyncio
import time
import json
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import logging
import threading

logger = logging.getLogger(__name__)


class AnalyticsTimeframe(Enum):
    """Analytics time frame options"""
    REAL_TIME = "real_time"           # Last few minutes
    HOURLY = "hourly"                 # Last hour
    DAILY = "daily"                   # Last 24 hours
    WEEKLY = "weekly"                 # Last 7 days
    MONTHLY = "monthly"               # Last 30 days
    QUARTERLY = "quarterly"           # Last 90 days
    YEARLY = "yearly"                 # Last 365 days


class AnalyticsMetricType(Enum):
    """Types of analytics metrics"""
    COUNT = "count"                   # Simple count
    RATE = "rate"                     # Rate over time
    PERCENTAGE = "percentage"         # Percentage value
    AVERAGE = "average"               # Average value
    DISTRIBUTION = "distribution"     # Value distribution
    TREND = "trend"                   # Trend analysis
    CORRELATION = "correlation"       # Correlation analysis


class InsightSeverity(Enum):
    """Severity levels for insights"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnalyticsDataPoint:
    """Single analytics data point"""
    timestamp: datetime
    metric_name: str
    value: Union[int, float]
    dimensions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'metric_name': self.metric_name,
            'value': self.value,
            'dimensions': self.dimensions,
            'metadata': self.metadata
        }


@dataclass
class AnalyticsResult:
    """Analytics calculation result"""
    metric_name: str
    timeframe: AnalyticsTimeframe
    metric_type: AnalyticsMetricType
    value: Union[int, float, Dict[str, Any]]
    timestamp: datetime
    dimensions: Dict[str, str] = field(default_factory=dict)
    confidence: Optional[float] = None
    trend: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'metric_name': self.metric_name,
            'timeframe': self.timeframe.value,
            'metric_type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'dimensions': self.dimensions,
            'confidence': self.confidence,
            'trend': self.trend
        }


@dataclass
class BusinessInsight:
    """Business insight generated from analytics"""
    title: str
    description: str
    severity: InsightSeverity
    category: str
    metrics: List[str]
    recommendations: List[str]
    timestamp: datetime
    confidence: float = 0.0
    impact_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'description': self.description,
            'severity': self.severity.value,
            'category': self.category,
            'metrics': self.metrics,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence,
            'impact_score': self.impact_score
        }


class RealTimeAnalytics:
    """
    Real-time analytics engine providing live insights and metrics
    
    Features:
    - Real-time data processing
    - Stream analytics
    - Live dashboards support
    - Instant alerts and notifications
    - Performance monitoring
    - User behavior tracking
    - Content engagement analysis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize real-time analytics"""
        self.config = config or {}
        
        # Configuration
        self.processing_interval = self.config.get('processing_interval', 5)  # seconds
        self.buffer_size = self.config.get('buffer_size', 10000)
        self.retention_minutes = self.config.get('retention_minutes', 60)
        
        # Data storage
        self.data_buffer: deque = deque(maxlen=self.buffer_size)
        self.processed_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.live_counters: Dict[str, float] = defaultdict(float)
        
        # Processing state
        self.is_processing = False
        self.processing_task = None
        self.last_processed = datetime.now(timezone.utc)
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Callbacks for real-time events
        self.event_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Metrics cache for quick access
        self.metrics_cache: Dict[str, Any] = {}
        self.cache_ttl = self.config.get('cache_ttl', 30)  # seconds
        self.last_cache_update = datetime.now(timezone.utc)
    
    async def start_processing(self):
        """Start real-time processing"""
        try:
            logger.info("Starting real-time analytics processing")
            self.is_processing = True
            self.processing_task = asyncio.create_task(self._processing_loop())
            
        except Exception as e:
            logger.error(f"Failed to start real-time processing: {str(e)}")
    
    async def stop_processing(self):
        """Stop real-time processing"""
        try:
            logger.info("Stopping real-time analytics processing")
            self.is_processing = False
            
            if self.processing_task:
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            
        except Exception as e:
            logger.error(f"Failed to stop real-time processing: {str(e)}")
    
    async def _processing_loop(self):
        """Main processing loop"""
        while self.is_processing:
            try:
                # Process buffered data
                await self._process_buffered_data()
                
                # Update metrics cache
                await self._update_metrics_cache()
                
                # Cleanup old data
                await self._cleanup_old_data()
                
                # Wait for next processing interval
                await asyncio.sleep(self.processing_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in real-time processing loop: {str(e)}")
                await asyncio.sleep(1)  # Brief pause on error
    
    def ingest_data_point(self, data_point: AnalyticsDataPoint):
        """Ingest a single data point"""
        try:
            with self._lock:
                self.data_buffer.append(data_point)
                
                # Update live counters immediately
                metric_key = f"{data_point.metric_name}"
                if data_point.dimensions:
                    dimension_str = "_".join(f"{k}:{v}" for k, v in data_point.dimensions.items())
                    metric_key += f"_{dimension_str}"
                
                self.live_counters[metric_key] += data_point.value
                
                # Trigger real-time callbacks
                asyncio.create_task(self._trigger_callbacks(data_point))
                
        except Exception as e:
            logger.error(f"Failed to ingest data point: {str(e)}")
    
    def ingest_batch(self, data_points: List[AnalyticsDataPoint]):
        """Ingest multiple data points"""
        try:
            with self._lock:
                for data_point in data_points:
                    self.data_buffer.append(data_point)
                
                # Update live counters
                for data_point in data_points:
                    metric_key = f"{data_point.metric_name}"
                    if data_point.dimensions:
                        dimension_str = "_".join(f"{k}:{v}" for k, v in data_point.dimensions.items())
                        metric_key += f"_{dimension_str}"
                    
                    self.live_counters[metric_key] += data_point.value
                
                # Trigger batch callbacks
                asyncio.create_task(self._trigger_batch_callbacks(data_points))
                
        except Exception as e:
            logger.error(f"Failed to ingest batch: {str(e)}")
    
    async def _process_buffered_data(self):
        """Process data from buffer"""
        try:
            if not self.data_buffer:
                return
            
            # Get data to process
            with self._lock:
                data_to_process = list(self.data_buffer)
                self.data_buffer.clear()
            
            # Group by metric and time windows
            metrics_by_time = self._group_by_time_windows(data_to_process)
            
            # Process each time window
            for time_window, metrics_data in metrics_by_time.items():
                processed_results = await self._process_time_window(time_window, metrics_data)
                
                # Store processed results
                for result in processed_results:
                    metric_key = f"{result.metric_name}_{result.timeframe.value}"
                    self.processed_metrics[metric_key].append(result)
            
        except Exception as e:
            logger.error(f"Failed to process buffered data: {str(e)}")
    
    def _group_by_time_windows(self, data_points: List[AnalyticsDataPoint]) -> Dict[datetime, List[AnalyticsDataPoint]]:
        """Group data points by time windows"""
        windows = {}
        
        for data_point in data_points:
            # Round to minute for grouping
            window_time = data_point.timestamp.replace(second=0, microsecond=0)
            
            if window_time not in windows:
                windows[window_time] = []
            
            windows[window_time].append(data_point)
        
        return windows
    
    async def _process_time_window(self, time_window: datetime, 
                                 data_points: List[AnalyticsDataPoint]) -> List[AnalyticsResult]:
        """Process data for a specific time window"""
        results = []
        
        try:
            # Group by metric name
            metrics_data = defaultdict(list)
            for data_point in data_points:
                metrics_data[data_point.metric_name].append(data_point)
            
            # Process each metric
            for metric_name, metric_data in metrics_data.items():
                # Calculate various analytics
                results.extend(await self._calculate_metric_analytics(metric_name, metric_data, time_window))
            
        except Exception as e:
            logger.error(f"Failed to process time window: {str(e)}")
        
        return results
    
    async def _calculate_metric_analytics(self, metric_name: str, 
                                        data_points: List[AnalyticsDataPoint], 
                                        time_window: datetime) -> List[AnalyticsResult]:
        """Calculate analytics for a specific metric"""
        results = []
        
        try:
            values = [dp.value for dp in data_points]
            
            # Basic count
            results.append(AnalyticsResult(
                metric_name=metric_name,
                timeframe=AnalyticsTimeframe.REAL_TIME,
                metric_type=AnalyticsMetricType.COUNT,
                value=len(values),
                timestamp=time_window
            ))
            
            if values:
                # Average
                results.append(AnalyticsResult(
                    metric_name=metric_name,
                    timeframe=AnalyticsTimeframe.REAL_TIME,
                    metric_type=AnalyticsMetricType.AVERAGE,
                    value=sum(values) / len(values),
                    timestamp=time_window
                ))
                
                # Rate (per second)
                rate = len(values) / 60.0  # Per minute window
                results.append(AnalyticsResult(
                    metric_name=metric_name,
                    timeframe=AnalyticsTimeframe.REAL_TIME,
                    metric_type=AnalyticsMetricType.RATE,
                    value=rate,
                    timestamp=time_window
                ))
                
                # Distribution analysis
                if len(values) > 1:
                    distribution = {
                        'min': min(values),
                        'max': max(values),
                        'median': statistics.median(values),
                        'std': statistics.stdev(values)
                    }
                    
                    results.append(AnalyticsResult(
                        metric_name=metric_name,
                        timeframe=AnalyticsTimeframe.REAL_TIME,
                        metric_type=AnalyticsMetricType.DISTRIBUTION,
                        value=distribution,
                        timestamp=time_window
                    ))
            
        except Exception as e:
            logger.error(f"Failed to calculate analytics for {metric_name}: {str(e)}")
        
        return results
    
    async def _update_metrics_cache(self):
        """Update metrics cache for quick access"""
        try:
            current_time = datetime.now(timezone.utc)
            
            if (current_time - self.last_cache_update).total_seconds() < self.cache_ttl:
                return
            
            # Build cache
            cache = {
                'live_counters': dict(self.live_counters),
                'recent_metrics': {},
                'summary_stats': {},
                'timestamp': current_time.isoformat()
            }
            
            # Add recent processed metrics
            cutoff_time = current_time - timedelta(minutes=5)
            for metric_key, results in self.processed_metrics.items():
                recent_results = [r for r in results if r.timestamp >= cutoff_time]
                if recent_results:
                    cache['recent_metrics'][metric_key] = [r.to_dict() for r in recent_results[-10:]]
            
            # Calculate summary statistics
            cache['summary_stats'] = await self._calculate_summary_stats()
            
            self.metrics_cache = cache
            self.last_cache_update = current_time
            
        except Exception as e:
            logger.error(f"Failed to update metrics cache: {str(e)}")
    
    async def _calculate_summary_stats(self) -> Dict[str, Any]:
        """Calculate summary statistics"""
        try:
            stats = {
                'total_data_points': len(self.data_buffer),
                'active_metrics': len(self.live_counters),
                'processing_rate': 0.0,
                'top_metrics': {}
            }
            
            # Calculate processing rate
            if hasattr(self, '_last_processed_count'):
                current_count = sum(len(results) for results in self.processed_metrics.values())
                stats['processing_rate'] = current_count - self._last_processed_count
                self._last_processed_count = current_count
            else:
                self._last_processed_count = sum(len(results) for results in self.processed_metrics.values())
            
            # Top metrics by value
            sorted_counters = sorted(self.live_counters.items(), key=lambda x: x[1], reverse=True)
            stats['top_metrics'] = dict(sorted_counters[:10])
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to calculate summary stats: {str(e)}")
            return {}
    
    async def _cleanup_old_data(self):
        """Clean up old data"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=self.retention_minutes)
            
            # Clean processed metrics
            for metric_key in list(self.processed_metrics.keys()):
                results = self.processed_metrics[metric_key]
                recent_results = deque(
                    [r for r in results if r.timestamp >= cutoff_time],
                    maxlen=results.maxlen
                )
                self.processed_metrics[metric_key] = recent_results
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {str(e)}")
    
    async def _trigger_callbacks(self, data_point: AnalyticsDataPoint):
        """Trigger real-time callbacks"""
        try:
            metric_callbacks = self.event_callbacks.get(data_point.metric_name, [])
            global_callbacks = self.event_callbacks.get('*', [])
            
            for callback in metric_callbacks + global_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data_point)
                    else:
                        callback(data_point)
                except Exception as e:
                    logger.error(f"Error in callback: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Failed to trigger callbacks: {str(e)}")
    
    async def _trigger_batch_callbacks(self, data_points: List[AnalyticsDataPoint]):
        """Trigger batch callbacks"""
        try:
            batch_callbacks = self.event_callbacks.get('batch', [])
            
            for callback in batch_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data_points)
                    else:
                        callback(data_points)
                except Exception as e:
                    logger.error(f"Error in batch callback: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Failed to trigger batch callbacks: {str(e)}")
    
    # Public API methods
    def register_callback(self, metric_name: str, callback: Callable):
        """Register callback for metric events"""
        self.event_callbacks[metric_name].append(callback)
    
    def get_live_metrics(self) -> Dict[str, Any]:
        """Get current live metrics"""
        return self.metrics_cache.copy()
    
    def get_metric_value(self, metric_name: str, dimensions: Optional[Dict[str, str]] = None) -> float:
        """Get current value for a specific metric"""
        metric_key = metric_name
        if dimensions:
            dimension_str = "_".join(f"{k}:{v}" for k, v in dimensions.items())
            metric_key += f"_{dimension_str}"
        
        return self.live_counters.get(metric_key, 0.0)
    
    async def get_creator_performance_insights(self, creator_id: str) -> Dict[str, Any]:
        """Get performance insights for a specific creator"""
        try:
            insights = {
                'creator_id': creator_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'metrics': {},
                'trends': {},
                'recommendations': []
            }
            
            # Get creator-specific metrics
            creator_metrics = {
                k: v for k, v in self.live_counters.items()
                if f"creator_id:{creator_id}" in k
            }
            
            insights['metrics'] = creator_metrics
            
            # Analyze trends (simplified)
            if creator_metrics:
                total_activity = sum(creator_metrics.values())
                insights['trends']['total_activity'] = total_activity
                
                # Generate recommendations based on activity level
                if total_activity > 100:
                    insights['recommendations'].append("High activity detected - consider premium features")
                elif total_activity < 10:
                    insights['recommendations'].append("Low activity - engagement boost recommended")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get creator insights for {creator_id}: {str(e)}")
            return {}
    
    async def get_content_performance(self, content_id: str) -> Dict[str, Any]:
        """Get performance metrics for specific content"""
        try:
            performance = {
                'content_id': content_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'engagement': {},
                'protection': {},
                'monetization': {}
            }
            
            # Get content-specific metrics
            content_metrics = {
                k: v for k, v in self.live_counters.items()
                if f"content_id:{content_id}" in k
            }
            
            # Categorize metrics
            for metric_key, value in content_metrics.items():
                if 'view' in metric_key or 'like' in metric_key or 'share' in metric_key:
                    performance['engagement'][metric_key] = value
                elif 'protection' in metric_key or 'fingerprint' in metric_key:
                    performance['protection'][metric_key] = value
                elif 'revenue' in metric_key or 'monetization' in metric_key:
                    performance['monetization'][metric_key] = value
            
            return performance
            
        except Exception as e:
            logger.error(f"Failed to get content performance for {content_id}: {str(e)}")
            return {}


class HistoricalAnalytics:
    """
    Historical analytics engine for long-term trends and insights
    
    Features:
    - Long-term trend analysis
    - Historical comparisons
    - Seasonal pattern detection
    - Growth analysis
    - Performance benchmarking
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize historical analytics"""
        self.config = config or {}
        
        # Storage configuration
        self.data_retention_days = self.config.get('retention_days', 365)
        self.aggregation_intervals = self.config.get('intervals', [3600, 86400, 604800])  # 1h, 1d, 1w
        
        # Historical data storage (in production, this would be a database)
        self.historical_data: Dict[str, List[AnalyticsDataPoint]] = defaultdict(list)
        self.aggregated_data: Dict[str, Dict[str, List[AnalyticsResult]]] = defaultdict(lambda: defaultdict(list))
        
        # Analysis cache
        self.analysis_cache: Dict[str, Any] = {}
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 hour
        
        # Thread pool for heavy computations
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def store_data_point(self, data_point: AnalyticsDataPoint):
        """Store a data point for historical analysis"""
        try:
            metric_key = data_point.metric_name
            self.historical_data[metric_key].append(data_point)
            
            # Maintain retention limit
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.data_retention_days)
            self.historical_data[metric_key] = [
                dp for dp in self.historical_data[metric_key]
                if dp.timestamp >= cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"Failed to store historical data point: {str(e)}")
    
    async def analyze_trends(self, metric_name: str, timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Analyze trends for a specific metric"""
        try:
            cache_key = f"trends_{metric_name}_{timeframe.value}"
            
            # Check cache
            if cache_key in self.analysis_cache:
                cached_result = self.analysis_cache[cache_key]
                if (datetime.now(timezone.utc) - cached_result['timestamp']).total_seconds() < self.cache_ttl:
                    return cached_result['data']
            
            # Get historical data
            data_points = self.historical_data.get(metric_name, [])
            if not data_points:
                return {'error': 'No historical data available'}
            
            # Filter by timeframe
            filtered_data = self._filter_by_timeframe(data_points, timeframe)
            if not filtered_data:
                return {'error': 'No data available for specified timeframe'}
            
            # Perform trend analysis
            trend_analysis = await self._perform_trend_analysis(filtered_data, timeframe)
            
            # Cache result
            self.analysis_cache[cache_key] = {
                'timestamp': datetime.now(timezone.utc),
                'data': trend_analysis
            }
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze trends for {metric_name}: {str(e)}")
            return {'error': str(e)}
    
    def _filter_by_timeframe(self, data_points: List[AnalyticsDataPoint], 
                           timeframe: AnalyticsTimeframe) -> List[AnalyticsDataPoint]:
        """Filter data points by timeframe"""
        now = datetime.now(timezone.utc)
        
        timeframe_deltas = {
            AnalyticsTimeframe.HOURLY: timedelta(hours=1),
            AnalyticsTimeframe.DAILY: timedelta(days=1),
            AnalyticsTimeframe.WEEKLY: timedelta(weeks=1),
            AnalyticsTimeframe.MONTHLY: timedelta(days=30),
            AnalyticsTimeframe.QUARTERLY: timedelta(days=90),
            AnalyticsTimeframe.YEARLY: timedelta(days=365)
        }
        
        delta = timeframe_deltas.get(timeframe, timedelta(days=1))
        cutoff_time = now - delta
        
        return [dp for dp in data_points if dp.timestamp >= cutoff_time]
    
    async def _perform_trend_analysis(self, data_points: List[AnalyticsDataPoint], 
                                    timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Perform detailed trend analysis"""
        try:
            # Sort by timestamp
            sorted_data = sorted(data_points, key=lambda x: x.timestamp)
            values = [dp.value for dp in sorted_data]
            timestamps = [dp.timestamp for dp in sorted_data]
            
            analysis = {
                'timeframe': timeframe.value,
                'data_points_count': len(values),
                'start_time': timestamps[0].isoformat() if timestamps else None,
                'end_time': timestamps[-1].isoformat() if timestamps else None,
                'basic_stats': {},
                'trend_indicators': {},
                'seasonal_patterns': {},
                'growth_analysis': {}
            }
            
            if not values:
                return analysis
            
            # Basic statistics
            analysis['basic_stats'] = {
                'min': min(values),
                'max': max(values),
                'average': sum(values) / len(values),
                'median': statistics.median(values),
                'total': sum(values)
            }
            
            if len(values) > 1:
                analysis['basic_stats']['std_deviation'] = statistics.stdev(values)
            
            # Trend indicators
            trend_indicators = await self._calculate_trend_indicators(values, timestamps)
            analysis['trend_indicators'] = trend_indicators
            
            # Growth analysis
            if len(values) >= 2:
                first_value = values[0]
                last_value = values[-1]
                
                growth_rate = ((last_value - first_value) / max(abs(first_value), 1)) * 100
                
                analysis['growth_analysis'] = {
                    'absolute_growth': last_value - first_value,
                    'growth_rate_percent': growth_rate,
                    'compound_growth_rate': self._calculate_cagr(values, timestamps)
                }
            
            # Seasonal patterns (if enough data)
            if len(values) > 24:  # Need sufficient data for pattern detection
                seasonal_patterns = await self._detect_seasonal_patterns(values, timestamps)
                analysis['seasonal_patterns'] = seasonal_patterns
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to perform trend analysis: {str(e)}")
            return {'error': str(e)}
    
    async def _calculate_trend_indicators(self, values: List[float], 
                                        timestamps: List[datetime]) -> Dict[str, Any]:
        """Calculate trend indicators"""
        try:
            indicators = {}
            
            if len(values) < 2:
                return indicators
            
            # Linear trend (slope)
            x_values = list(range(len(values)))
            slope = self._calculate_linear_regression_slope(x_values, values)
            
            indicators['linear_trend_slope'] = slope
            indicators['trend_direction'] = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
            
            # Moving averages
            if len(values) >= 7:
                ma_7 = self._calculate_moving_average(values, 7)
                indicators['moving_average_7'] = ma_7[-1] if ma_7 else None
                
                if len(values) >= 30:
                    ma_30 = self._calculate_moving_average(values, 30)
                    indicators['moving_average_30'] = ma_30[-1] if ma_30 else None
                    
                    # Trend strength based on moving averages
                    if ma_7 and ma_30:
                        ma_ratio = ma_7[-1] / ma_30[-1] if ma_30[-1] != 0 else 1
                        indicators['trend_strength'] = abs(ma_ratio - 1)
            
            # Volatility
            if len(values) > 1:
                volatility = statistics.stdev(values) / (sum(values) / len(values))
                indicators['volatility'] = volatility
            
            # Momentum (rate of change)
            if len(values) >= 10:
                recent_avg = sum(values[-5:]) / 5
                older_avg = sum(values[-10:-5]) / 5
                momentum = ((recent_avg - older_avg) / max(abs(older_avg), 1)) * 100
                indicators['momentum_percent'] = momentum
            
            return indicators
            
        except Exception as e:
            logger.error(f"Failed to calculate trend indicators: {str(e)}")
            return {}
    
    def _calculate_linear_regression_slope(self, x_values: List[int], y_values: List[float]) -> float:
        """Calculate linear regression slope"""
        n = len(x_values)
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0
    
    def _calculate_moving_average(self, values: List[float], window: int) -> List[float]:
        """Calculate moving average"""
        if len(values) < window:
            return []
        
        moving_averages = []
        for i in range(window - 1, len(values)):
            window_values = values[i - window + 1:i + 1]
            moving_averages.append(sum(window_values) / window)
        
        return moving_averages
    
    def _calculate_cagr(self, values: List[float], timestamps: List[datetime]) -> Optional[float]:
        """Calculate Compound Annual Growth Rate"""
        if len(values) < 2 or values[0] == 0:
            return None
        
        try:
            initial_value = values[0]
            final_value = values[-1]
            
            time_diff = (timestamps[-1] - timestamps[0]).total_seconds()
            years = time_diff / (365.25 * 24 * 3600)  # Convert to years
            
            if years <= 0:
                return None
            
            cagr = ((final_value / initial_value) ** (1 / years)) - 1
            return cagr * 100  # Convert to percentage
            
        except Exception:
            return None
    
    async def _detect_seasonal_patterns(self, values: List[float], 
                                      timestamps: List[datetime]) -> Dict[str, Any]:
        """Detect seasonal patterns in data"""
        try:
            patterns = {
                'hourly_pattern': {},
                'daily_pattern': {},
                'weekly_pattern': {},
                'monthly_pattern': {}
            }
            
            # Group by time components
            hourly_groups = defaultdict(list)
            daily_groups = defaultdict(list)
            weekly_groups = defaultdict(list)
            monthly_groups = defaultdict(list)
            
            for i, timestamp in enumerate(timestamps):
                value = values[i]
                
                hourly_groups[timestamp.hour].append(value)
                daily_groups[timestamp.day].append(value)
                weekly_groups[timestamp.weekday()].append(value)
                monthly_groups[timestamp.month].append(value)
            
            # Calculate averages for each pattern
            for hour, hour_values in hourly_groups.items():
                patterns['hourly_pattern'][hour] = sum(hour_values) / len(hour_values)
            
            for day, day_values in daily_groups.items():
                patterns['daily_pattern'][day] = sum(day_values) / len(day_values)
            
            for weekday, weekday_values in weekly_groups.items():
                patterns['weekly_pattern'][weekday] = sum(weekday_values) / len(weekday_values)
            
            for month, month_values in monthly_groups.items():
                patterns['monthly_pattern'][month] = sum(month_values) / len(month_values)
            
            # Calculate pattern strength
            for pattern_type, pattern_data in patterns.items():
                if pattern_data:
                    pattern_values = list(pattern_data.values())
                    if len(pattern_values) > 1:
                        pattern_std = statistics.stdev(pattern_values)
                        pattern_mean = sum(pattern_values) / len(pattern_values)
                        pattern_strength = (pattern_std / max(pattern_mean, 1)) * 100
                        patterns[f'{pattern_type}_strength'] = pattern_strength
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to detect seasonal patterns: {str(e)}")
            return {}
    
    async def compare_periods(self, metric_name: str, 
                            period1_start: datetime, period1_end: datetime,
                            period2_start: datetime, period2_end: datetime) -> Dict[str, Any]:
        """Compare two time periods for a metric"""
        try:
            data_points = self.historical_data.get(metric_name, [])
            
            # Filter data for each period
            period1_data = [dp for dp in data_points 
                           if period1_start <= dp.timestamp <= period1_end]
            period2_data = [dp for dp in data_points 
                           if period2_start <= dp.timestamp <= period2_end]
            
            if not period1_data or not period2_data:
                return {'error': 'Insufficient data for comparison'}
            
            # Calculate statistics for each period
            period1_values = [dp.value for dp in period1_data]
            period2_values = [dp.value for dp in period2_data]
            
            comparison = {
                'metric_name': metric_name,
                'period1': {
                    'start': period1_start.isoformat(),
                    'end': period1_end.isoformat(),
                    'data_points': len(period1_values),
                    'total': sum(period1_values),
                    'average': sum(period1_values) / len(period1_values),
                    'min': min(period1_values),
                    'max': max(period1_values)
                },
                'period2': {
                    'start': period2_start.isoformat(),
                    'end': period2_end.isoformat(),
                    'data_points': len(period2_values),
                    'total': sum(period2_values),
                    'average': sum(period2_values) / len(period2_values),
                    'min': min(period2_values),
                    'max': max(period2_values)
                },
                'comparison': {}
            }
            
            # Calculate comparison metrics
            total_change = comparison['period2']['total'] - comparison['period1']['total']
            total_change_percent = (total_change / max(abs(comparison['period1']['total']), 1)) * 100
            
            avg_change = comparison['period2']['average'] - comparison['period1']['average']
            avg_change_percent = (avg_change / max(abs(comparison['period1']['average']), 1)) * 100
            
            comparison['comparison'] = {
                'total_change': total_change,
                'total_change_percent': total_change_percent,
                'average_change': avg_change,
                'average_change_percent': avg_change_percent,
                'performance': 'improved' if total_change > 0 else 'declined' if total_change < 0 else 'stable'
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare periods for {metric_name}: {str(e)}")
            return {'error': str(e)}


class PredictiveAnalytics:
    """
    Predictive analytics engine for forecasting and trend prediction
    
    Features:
    - Time series forecasting
    - Machine learning predictions
    - Trend extrapolation
    - Confidence intervals
    - Alert predictions
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize predictive analytics"""
        self.config = config or {}
        
        # Prediction configuration
        self.prediction_horizon = self.config.get('prediction_horizon', 24)  # hours
        self.confidence_level = self.config.get('confidence_level', 0.95)
        self.min_data_points = self.config.get('min_data_points', 50)
        
        # Prediction models cache
        self.models_cache: Dict[str, Any] = {}
        self.predictions_cache: Dict[str, Any] = {}
        
        # Thread pool for model training
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def predict_metric_values(self, metric_name: str, 
                                   historical_data: List[AnalyticsDataPoint],
                                   hours_ahead: int = 24) -> Dict[str, Any]:
        """Predict future values for a metric"""
        try:
            if len(historical_data) < self.min_data_points:
                return {'error': f'Insufficient data points. Need at least {self.min_data_points}'}
            
            # Prepare data
            sorted_data = sorted(historical_data, key=lambda x: x.timestamp)
            values = [dp.value for dp in sorted_data]
            timestamps = [dp.timestamp for dp in sorted_data]
            
            # Generate predictions
            predictions = await self._generate_predictions(values, timestamps, hours_ahead)
            
            return {
                'metric_name': metric_name,
                'prediction_horizon_hours': hours_ahead,
                'confidence_level': self.confidence_level,
                'historical_data_points': len(values),
                'predictions': predictions,
                'model_info': {
                    'type': 'linear_trend',
                    'accuracy': 'estimated'
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to predict values for {metric_name}: {str(e)}")
            return {'error': str(e)}
    
    async def _generate_predictions(self, values: List[float], 
                                  timestamps: List[datetime],
                                  hours_ahead: int) -> List[Dict[str, Any]]:
        """Generate predictions using trend analysis"""
        try:
            predictions = []
            
            # Calculate trend
            x_values = list(range(len(values)))
            slope = self._calculate_slope(x_values, values)
            intercept = sum(values) / len(values) - slope * sum(x_values) / len(x_values)
            
            # Calculate prediction confidence based on data variability
            residuals = [values[i] - (slope * x_values[i] + intercept) for i in range(len(values))]
            mse = sum(r**2 for r in residuals) / len(residuals)
            confidence_interval = 1.96 * (mse ** 0.5)  # 95% confidence interval
            
            # Generate hourly predictions
            last_timestamp = timestamps[-1]
            for hour in range(1, hours_ahead + 1):
                prediction_timestamp = last_timestamp + timedelta(hours=hour)
                x_pred = len(values) + hour
                predicted_value = slope * x_pred + intercept
                
                predictions.append({
                    'timestamp': prediction_timestamp.isoformat(),
                    'predicted_value': max(0, predicted_value),  # Ensure non-negative
                    'lower_bound': max(0, predicted_value - confidence_interval),
                    'upper_bound': predicted_value + confidence_interval,
                    'confidence': self.confidence_level
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to generate predictions: {str(e)}")
            return []
    
    def _calculate_slope(self, x_values: List[int], y_values: List[float]) -> float:
        """Calculate linear regression slope"""
        n = len(x_values)
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0
    
    async def detect_anomaly_predictions(self, metric_name: str,
                                       historical_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Predict potential anomalies"""
        try:
            if len(historical_data) < 20:
                return {'error': 'Insufficient data for anomaly prediction'}
            
            # Calculate baseline statistics
            values = [dp.value for dp in historical_data]
            mean_value = sum(values) / len(values)
            std_value = statistics.stdev(values) if len(values) > 1 else 0
            
            # Define anomaly thresholds
            upper_threshold = mean_value + 2 * std_value
            lower_threshold = max(0, mean_value - 2 * std_value)
            
            # Predict future values
            predictions = await self.predict_metric_values(metric_name, historical_data, 6)
            
            if 'error' in predictions:
                return predictions
            
            # Check predictions for potential anomalies
            anomaly_alerts = []
            for pred in predictions.get('predictions', []):
                predicted_value = pred['predicted_value']
                
                if predicted_value > upper_threshold:
                    anomaly_alerts.append({
                        'timestamp': pred['timestamp'],
                        'type': 'high_value_anomaly',
                        'predicted_value': predicted_value,
                        'threshold': upper_threshold,
                        'severity': 'high' if predicted_value > upper_threshold * 1.5 else 'medium',
                        'confidence': pred['confidence']
                    })
                elif predicted_value < lower_threshold:
                    anomaly_alerts.append({
                        'timestamp': pred['timestamp'],
                        'type': 'low_value_anomaly',
                        'predicted_value': predicted_value,
                        'threshold': lower_threshold,
                        'severity': 'medium',
                        'confidence': pred['confidence']
                    })
            
            return {
                'metric_name': metric_name,
                'baseline_mean': mean_value,
                'baseline_std': std_value,
                'anomaly_thresholds': {
                    'upper': upper_threshold,
                    'lower': lower_threshold
                },
                'predicted_anomalies': anomaly_alerts,
                'risk_level': 'high' if any(a['severity'] == 'high' for a in anomaly_alerts) else 'medium' if anomaly_alerts else 'low'
            }
            
        except Exception as e:
            logger.error(f"Failed to detect anomaly predictions: {str(e)}")
            return {'error': str(e)}


# Specialized analytics classes for different domains
class ContentAnalytics(RealTimeAnalytics):
    """Specialized analytics for content performance"""
    
    async def analyze_content_engagement(self, content_id: str) -> Dict[str, Any]:
        """Analyze engagement metrics for specific content"""
        engagement_metrics = [
            f"content_views_content_id:{content_id}",
            f"content_likes_content_id:{content_id}",
            f"content_shares_content_id:{content_id}",
            f"content_comments_content_id:{content_id}"
        ]
        
        engagement_data = {}
        for metric in engagement_metrics:
            value = self.get_metric_value(metric.replace("_content_id:", ""), {"content_id": content_id})
            engagement_data[metric.split("_")[1]] = value
        
        # Calculate engagement score
        engagement_score = (
            engagement_data.get('views', 0) * 1 +
            engagement_data.get('likes', 0) * 3 +
            engagement_data.get('shares', 0) * 5 +
            engagement_data.get('comments', 0) * 4
        )
        
        return {
            'content_id': content_id,
            'engagement_metrics': engagement_data,
            'engagement_score': engagement_score,
            'performance_tier': self._calculate_performance_tier(engagement_score)
        }
    
    def _calculate_performance_tier(self, engagement_score: float) -> str:
        """Calculate performance tier based on engagement score"""
        if engagement_score > 1000:
            return 'viral'
        elif engagement_score > 500:
            return 'high'
        elif engagement_score > 100:
            return 'medium'
        elif engagement_score > 10:
            return 'low'
        else:
            return 'minimal'


class UserAnalytics(RealTimeAnalytics):
    """Specialized analytics for user behavior"""
    
    async def analyze_user_journey(self, user_id: str) -> Dict[str, Any]:
        """Analyze user journey and behavior patterns"""
        user_metrics = {
            k: v for k, v in self.live_counters.items()
            if f"user_id:{user_id}" in k
        }
        
        journey_analysis = {
            'user_id': user_id,
            'activity_metrics': user_metrics,
            'behavior_patterns': {},
            'engagement_level': 'unknown'
        }
        
        # Calculate activity level
        total_activity = sum(user_metrics.values())
        if total_activity > 100:
            journey_analysis['engagement_level'] = 'high'
        elif total_activity > 50:
            journey_analysis['engagement_level'] = 'medium'
        elif total_activity > 10:
            journey_analysis['engagement_level'] = 'low'
        else:
            journey_analysis['engagement_level'] = 'minimal'
        
        return journey_analysis


class PerformanceAnalytics(RealTimeAnalytics):
    """Specialized analytics for system performance"""
    
    async def analyze_system_health(self) -> Dict[str, Any]:
        """Analyze overall system health"""
        performance_metrics = {
            k: v for k, v in self.live_counters.items()
            if any(perf_key in k.lower() for perf_key in ['response_time', 'latency', 'cpu', 'memory', 'error'])
        }
        
        health_analysis = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'performance_metrics': performance_metrics,
            'health_score': 0,
            'alerts': [],
            'recommendations': []
        }
        
        # Calculate health score and generate alerts
        error_count = sum(v for k, v in performance_metrics.items() if 'error' in k.lower())
        if error_count > 10:
            health_analysis['alerts'].append({
                'type': 'high_error_rate',
                'severity': 'high',
                'message': f'High error rate detected: {error_count} errors'
            })
        
        return health_analysis
