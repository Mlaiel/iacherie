"""
Statistics Manager for IA-Influencer-Agent Platform

Advanced statistics collection, analysis, and reporting for database indexing operations.
Comprehensive performance metrics, trend analysis, and predictive insights.

 Enterprise Team Project Specialties:
 Lead Dev + Architecte Développeur IA
 Développeur Backend Senior (Python/FastAPI/Django)  
 Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
 DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
 Spécialiste Sécurité Backend
 Architecte Microservices
 Développeur Audio
 DevOps Engineer
 IA Prompt Engineer

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING 
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.
"""

import asyncio
import logging
import statistics
import json
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

from ..core.database_manager import DatabaseManager
from ..monitoring.performance_tracker import PerformanceTracker

logger = logging.getLogger(__name__)

class StatisticType(Enum):
    """Types of statistics collected"""
    INDEX_USAGE = "index_usage"
    QUERY_PERFORMANCE = "query_performance"
    STORAGE_METRICS = "storage_metrics"
    CACHE_EFFICIENCY = "cache_efficiency"
    SYSTEM_RESOURCES = "system_resources"
    ERROR_RATES = "error_rates"
    THROUGHPUT = "throughput"
    LATENCY = "latency"

class AggregationPeriod(Enum):
    """Time periods for aggregation"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

class TrendDirection(Enum):
    """Trend direction indicators"""
    IMPROVING = "improving"
    DEGRADING = "degrading"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class StatisticEntry:
    """Single statistic entry"""
    timestamp: datetime
    metric_type: StatisticType
    metric_name: str
    value: float
    unit: str
    dimensions: Dict[str, Any]
    tags: List[str]

@dataclass
class AggregatedStatistic:
    """Aggregated statistic data"""
    period: AggregationPeriod
    start_time: datetime
    end_time: datetime
    metric_type: StatisticType
    metric_name: str
    count: int
    min_value: float
    max_value: float
    avg_value: float
    median_value: float
    std_dev: float
    percentiles: Dict[str, float]

@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    metric_name: str
    period: AggregationPeriod
    direction: TrendDirection
    slope: float
    correlation: float
    confidence: float
    forecast: List[float]
    anomalies: List[datetime]

class StatisticsManager:
    """
    Ultra-advanced statistics manager for IA-Influencer platform indexing
    
    Features:
    - Real-time statistics collection and aggregation
    - Multi-dimensional metric analysis
    - Advanced trend detection and forecasting
    - Anomaly detection and alerting
    - Statistical correlation analysis
    - Performance baseline establishment
    - Predictive analytics for capacity planning
    - Custom metric definitions and tracking
    - Historical data retention and archival
    - Comprehensive reporting and visualization
    """
    
    def __init__(self):
        """Initialize statistics manager"""
        self.db_manager = DatabaseManager()
        self.performance_tracker = PerformanceTracker()
        
        # Statistics storage
        self.raw_statistics = deque(maxlen=100000)  # Recent raw data
        self.aggregated_statistics = {}
        self.trend_analysis_cache = {}
        
        # Configuration
        self.collection_interval = 60  # seconds
        self.aggregation_intervals = {
            AggregationPeriod.MINUTE: 60,
            AggregationPeriod.HOUR: 3600,
            AggregationPeriod.DAY: 86400,
            AggregationPeriod.WEEK: 604800,
            AggregationPeriod.MONTH: 2592000
        }
        
        # Retention policies (in days)
        self.retention_policies = {
            AggregationPeriod.MINUTE: 1,      # 1 day
            AggregationPeriod.HOUR: 7,       # 1 week
            AggregationPeriod.DAY: 90,       # 3 months
            AggregationPeriod.WEEK: 365,     # 1 year
            AggregationPeriod.MONTH: 1825    # 5 years
        }
        
        # Anomaly detection parameters
        self.anomaly_threshold = 2.5  # Standard deviations
        self.trend_window = 30  # Data points for trend analysis
        self.forecast_horizon = 10  # Future data points to predict
        
        # Collection state
        self.collection_active = False
        self.collection_task = None
        self.aggregation_task = None
        
        # Custom metrics registry
        self.custom_metrics = {}
        
        # Baseline values for comparison
        self.baselines = {}
        
        logger.info("StatisticsManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize statistics manager"""



        try:
            # Initialize database connection
            await self.db_manager.initialize()
            
            # Initialize performance tracker
            await self.performance_tracker.initialize()
            
            # Load historical statistics
            await self._load_historical_statistics()
            
            # Load baselines
            await self._load_baselines()
            
            # Start collection tasks
            await self.start_collection()
            
            logger.info("StatisticsManager initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize StatisticsManager: {str(e)}")
            return False
    
    async def start_collection(self):
        """Start statistics collection"""



        try:
            if self.collection_active:
                logger.warning("Statistics collection already active")
                return
            
            self.collection_active = True
            
            # Start collection task
            self.collection_task = asyncio.create_task(self._collection_loop())
            
            # Start aggregation task
            self.aggregation_task = asyncio.create_task(self._aggregation_loop())
            
            logger.info("Statistics collection started")
            
        except Exception as e:
            logger.error(f"Failed to start statistics collection: {str(e)}")
    
    async def stop_collection(self):
        """Stop statistics collection"""



        try:
            self.collection_active = False
            
            # Cancel tasks
            if self.collection_task:
                self.collection_task.cancel()
                try:
                    await self.collection_task
                except asyncio.CancelledError:
                    pass
            
            if self.aggregation_task:
                self.aggregation_task.cancel()
                try:
                    await self.aggregation_task
                except asyncio.CancelledError:
                    pass
            
            # Save pending statistics
            await self._save_pending_statistics()
            
            logger.info("Statistics collection stopped")
            
        except Exception as e:
            logger.error(f"Error stopping statistics collection: {str(e)}")
    
    async def _collection_loop(self):
        """Main statistics collection loop"""
        while self.collection_active:
            try:
                # Collect index usage statistics
                await self._collect_index_usage_stats()
                
                # Collect query performance statistics
                await self._collect_query_performance_stats()
                
                # Collect storage metrics
                await self._collect_storage_metrics()
                
                # Collect cache efficiency metrics
                await self._collect_cache_efficiency_stats()
                
                # Collect system resource metrics
                await self._collect_system_resource_stats()
                
                # Collect error rates
                await self._collect_error_rate_stats()
                
                # Collect custom metrics
                await self._collect_custom_metrics()
                
                # Wait for next collection interval
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in statistics collection loop: {str(e)}")
                await asyncio.sleep(5.0)  # Brief pause before retrying
    
    async def _aggregation_loop(self):
        """Statistics aggregation loop"""
        while self.collection_active:
            try:
                # Perform aggregations for different periods
                for period in AggregationPeriod:
                    await self._aggregate_statistics(period)
                
                # Perform trend analysis
                await self._update_trend_analysis()
                
                # Detect anomalies
                await self._detect_anomalies()
                
                # Clean old data
                await self._cleanup_old_data()
                
                # Wait before next aggregation cycle
                await asyncio.sleep(300)  # 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in statistics aggregation loop: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _collect_index_usage_stats(self):
        """Collect index usage statistics"""



        try:
            timestamp = datetime.now()
            
            # Get index usage from database
            index_stats = await self._get_database_index_stats()
            
            for index_name, stats in index_stats.items():
                # Index scans
                await self._record_statistic(
                    StatisticEntry(
                        timestamp=timestamp,
                        metric_type=StatisticType.INDEX_USAGE,
                        metric_name="index_scans",
                        value=stats.get('scans', 0),
                        unit="count",
                        dimensions={'index_name': index_name},
                        tags=['database', 'performance']
                    )
                )
                
                # Index seeks
                await self._record_statistic(
                    StatisticEntry(
                        timestamp=timestamp,
                        metric_type=StatisticType.INDEX_USAGE,
                        metric_name="index_seeks",
                        value=stats.get('seeks', 0),
                        unit="count",
                        dimensions={'index_name': index_name},
                        tags=['database', 'performance']
                    )
                )
                
                # Index size
                await self._record_statistic(
                    StatisticEntry(
                        timestamp=timestamp,
                        metric_type=StatisticType.STORAGE_METRICS,
                        metric_name="index_size",
                        value=stats.get('size_bytes', 0),
                        unit="bytes",
                        dimensions={'index_name': index_name},
                        tags=['storage', 'size']
                    )
                )
                
        except Exception as e:
            logger.debug(f"Error collecting index usage stats: {str(e)}")
    
    async def _collect_query_performance_stats(self):
        """Collect query performance statistics"""



        try:
            timestamp = datetime.now()
            
            # Get query performance metrics
            query_stats = await self._get_query_performance_metrics()
            
            # Average query time
            if 'avg_query_time' in query_stats:
                await self._record_statistic(
                    StatisticEntry(
                        timestamp=timestamp,
                        metric_type=StatisticType.QUERY_PERFORMANCE,
                        metric_name="avg_query_time",
                        value=query_stats['avg_query_time'],
                        unit="seconds",
                        dimensions={},
                        tags=['query', 'performance']
                    )
                )
            
            # Query throughput
            if 'queries_per_second' in query_stats:
                await self._record_statistic(
                    StatisticEntry(
                        timestamp=timestamp,
                        metric_type=StatisticType.THROUGHPUT,
                        metric_name="queries_per_second",
                        value=query_stats['queries_per_second'],
                        unit="qps",
                        dimensions={},
                        tags=['query', 'throughput']
                    )
                )
            
            # Slow query count
            if 'slow_query_count' in query_stats:
                await self._record_statistic(
                    StatisticEntry(
                        timestamp=timestamp,
                        metric_type=StatisticType.QUERY_PERFORMANCE,
                        metric_name="slow_query_count",
                        value=query_stats['slow_query_count'],
                        unit="count",
                        dimensions={},
                        tags=['query', 'performance', 'slow']
                    )
                )
                
        except Exception as e:
            logger.debug(f"Error collecting query performance stats: {str(e)}")
    
    async def _collect_storage_metrics(self):
        """Collect storage-related metrics"""



        try:
            timestamp = datetime.now()
            
            # Get storage metrics
            storage_stats = await self._get_storage_metrics()
            
            for metric_name, value in storage_stats.items():
                await self._record_statistic(
                    StatisticEntry(
                        timestamp=timestamp,
                        metric_type=StatisticType.STORAGE_METRICS,
                        metric_name=metric_name,
                        value=value,
                        unit="bytes" if "size" in metric_name else "count",
                        dimensions={},
                        tags=['storage']
                    )
                )
                
        except Exception as e:
            logger.debug(f"Error collecting storage metrics: {str(e)}")
    
    async def _collect_cache_efficiency_stats(self):
        """Collect cache efficiency statistics"""



        try:
            timestamp = datetime.now()
            
            # Get cache metrics
            cache_stats = await self._get_cache_metrics()
            
            # Cache hit rate
            if 'hit_rate' in cache_stats:
                await self._record_statistic(
                    StatisticEntry(
                        timestamp=timestamp,
                        metric_type=StatisticType.CACHE_EFFICIENCY,
                        metric_name="cache_hit_rate",
                        value=cache_stats['hit_rate'],
                        unit="percentage",
                        dimensions={},
                        tags=['cache', 'efficiency']
                    )
                )
            
            # Cache memory usage
            if 'memory_usage' in cache_stats:
                await self._record_statistic(
                    StatisticEntry(
                        timestamp=timestamp,
                        metric_type=StatisticType.SYSTEM_RESOURCES,
                        metric_name="cache_memory_usage",
                        value=cache_stats['memory_usage'],
                        unit="bytes",
                        dimensions={},
                        tags=['cache', 'memory']
                    )
                )
                
        except Exception as e:
            logger.debug(f"Error collecting cache efficiency stats: {str(e)}")
    
    async def _collect_system_resource_stats(self):
        """Collect system resource statistics"""



        try:
            timestamp = datetime.now()
            
            # Get system metrics from performance tracker
            if hasattr(self.performance_tracker, 'get_system_metrics'):
                system_stats = await self.performance_tracker.get_system_metrics()
                
                for metric_name, value in system_stats.items():
                    await self._record_statistic(
                        StatisticEntry(
                            timestamp=timestamp,
                            metric_type=StatisticType.SYSTEM_RESOURCES,
                            metric_name=metric_name,
                            value=value,
                            unit="percentage" if "usage" in metric_name else "bytes",
                            dimensions={},
                            tags=['system', 'resources']
                        )
                    )
                    
        except Exception as e:
            logger.debug(f"Error collecting system resource stats: {str(e)}")
    
    async def _collect_error_rate_stats(self):
        """Collect error rate statistics"""



        try:
            timestamp = datetime.now()
            
            # Get error metrics
            error_stats = await self._get_error_metrics()
            
            for error_type, count in error_stats.items():
                await self._record_statistic(
                    StatisticEntry(
                        timestamp=timestamp,
                        metric_type=StatisticType.ERROR_RATES,
                        metric_name=f"{error_type}_errors",
                        value=count,
                        unit="count",
                        dimensions={'error_type': error_type},
                        tags=['error', 'reliability']
                    )
                )
                
        except Exception as e:
            logger.debug(f"Error collecting error rate stats: {str(e)}")
    
    async def _collect_custom_metrics(self):
        """Collect custom-defined metrics"""



        try:
            timestamp = datetime.now()
            
            for metric_name, metric_config in self.custom_metrics.items():
                try:
                    # Execute custom metric collection
                    value = await self._execute_custom_metric(metric_config)
                    
                    await self._record_statistic(
                        StatisticEntry(
                            timestamp=timestamp,
                            metric_type=StatisticType(metric_config.get('type', 'custom')),
                            metric_name=metric_name,
                            value=value,
                            unit=metric_config.get('unit', 'count'),
                            dimensions=metric_config.get('dimensions', {}),
                            tags=metric_config.get('tags', [])
                        )
                    )
                    
                except Exception as e:
                    logger.debug(f"Error collecting custom metric {metric_name}: {str(e)}")
                    
        except Exception as e:
            logger.debug(f"Error collecting custom metrics: {str(e)}")
    
    async def _record_statistic(self, entry: StatisticEntry):
        """Record a statistic entry"""



        try:
            # Add to raw statistics buffer
            self.raw_statistics.append(entry)
            
            # Log to performance tracker
            await self.performance_tracker.log_index_operation(
                f"stat_{entry.metric_type.value}_{entry.metric_name}",
                "collect",
                0.001,  # Minimal time for statistic collection
                {
                    'metric_value': entry.value,
                    'metric_unit': entry.unit,
                    'dimensions': entry.dimensions,
                    'tags': entry.tags
                }
            )
            
        except Exception as e:
            logger.debug(f"Error recording statistic: {str(e)}")
    
    async def _aggregate_statistics(self, period: AggregationPeriod):
        """Aggregate statistics for given period"""



        try:
            now = datetime.now()
            interval_seconds = self.aggregation_intervals[period]
            
            # Calculate aggregation window
            if period == AggregationPeriod.MINUTE:
                start_time = now.replace(second=0, microsecond=0)
            elif period == AggregationPeriod.HOUR:
                start_time = now.replace(minute=0, second=0, microsecond=0)
            elif period == AggregationPeriod.DAY:
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == AggregationPeriod.WEEK:
                days_since_monday = now.weekday()
                start_time = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == AggregationPeriod.MONTH:
                start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                return
            
            end_time = start_time + timedelta(seconds=interval_seconds)
            
            # Skip if we already have aggregation for this period
            agg_key = f"{period.value}_{start_time.isoformat()}"
            if agg_key in self.aggregated_statistics:
                return
            
            # Group statistics by metric type and name
            grouped_stats = defaultdict(list)
            
            for entry in self.raw_statistics:
                if start_time <= entry.timestamp < end_time:
                    key = (entry.metric_type, entry.metric_name)
                    grouped_stats[key].append(entry.value)
            
            # Create aggregated statistics
            aggregated = {}
            for (metric_type, metric_name), values in grouped_stats.items():
                if not values:
                    continue
                
                # Calculate statistics
                values_array = np.array(values)
                percentiles = {
                    'p50': np.percentile(values_array, 50),
                    'p90': np.percentile(values_array, 90),
                    'p95': np.percentile(values_array, 95),
                    'p99': np.percentile(values_array, 99)
                }
                
                agg_stat = AggregatedStatistic(
                    period=period,
                    start_time=start_time,
                    end_time=end_time,
                    metric_type=metric_type,
                    metric_name=metric_name,
                    count=len(values),
                    min_value=float(np.min(values_array)),
                    max_value=float(np.max(values_array)),
                    avg_value=float(np.mean(values_array)),
                    median_value=float(np.median(values_array)),
                    std_dev=float(np.std(values_array)),
                    percentiles=percentiles
                )
                
                stat_key = f"{metric_type.value}_{metric_name}"
                aggregated[stat_key] = agg_stat
            
            # Store aggregated statistics
            self.aggregated_statistics[agg_key] = aggregated
            
            logger.debug(f"Aggregated {len(aggregated)} statistics for period {period.value}")
            
        except Exception as e:
            logger.debug(f"Error aggregating statistics for period {period.value}: {str(e)}")
    
    async def _update_trend_analysis(self):
        """Update trend analysis for metrics"""



        try:
            # Analyze trends for each metric
            for period in [AggregationPeriod.HOUR, AggregationPeriod.DAY]:
                await self._analyze_trends_for_period(period)
                
        except Exception as e:
            logger.debug(f"Error updating trend analysis: {str(e)}")
    
    async def _analyze_trends_for_period(self, period: AggregationPeriod):
        """Analyze trends for specific period"""



        try:
            # Get recent aggregated data
            recent_data = await self._get_recent_aggregated_data(period, self.trend_window)
            
            # Group by metric
            metric_data = defaultdict(list)
            for timestamp, aggregations in recent_data.items():
                for metric_key, agg_stat in aggregations.items():
                    metric_data[metric_key].append((timestamp, agg_stat.avg_value))
            
            # Analyze trends for each metric
            for metric_key, data_points in metric_data.items():
                if len(data_points) < 5:  # Need minimum data points
                    continue
                
                # Sort by timestamp
                data_points.sort(key=lambda x: x[0])
                
                # Extract values for analysis
                timestamps = [dp[0] for dp in data_points]
                values = [dp[1] for dp in data_points]
                
                # Perform trend analysis
                trend = await self._calculate_trend(metric_key, timestamps, values, period)
                
                # Cache trend analysis
                cache_key = f"{metric_key}_{period.value}"
                self.trend_analysis_cache[cache_key] = trend
                
        except Exception as e:
            logger.debug(f"Error analyzing trends for period {period.value}: {str(e)}")
    
    async def _calculate_trend(self, metric_key: str, timestamps: List[datetime], 
                             values: List[float], period: AggregationPeriod) -> TrendAnalysis:
        """Calculate trend for metric"""



        try:
            # Convert timestamps to numeric values for regression
            start_time = timestamps[0]
            x_values = [(ts - start_time).total_seconds() for ts in timestamps]
            y_values = values
            
            # Calculate linear regression
            x_array = np.array(x_values)
            y_array = np.array(y_values)
            
            # Polynomial fit (degree 1 for linear trend)
            coefficients = np.polyfit(x_array, y_array, 1)
            slope = coefficients[0]
            
            # Calculate correlation coefficient
            correlation = np.corrcoef(x_array, y_array)[0, 1] if len(x_array) > 1 else 0
            
            # Determine trend direction
            if abs(slope) < 0.01:  # Threshold for stability
                direction = TrendDirection.STABLE
            elif slope > 0:
                direction = TrendDirection.IMPROVING if "error" not in metric_key.lower() else TrendDirection.DEGRADING
            else:
                direction = TrendDirection.DEGRADING if "error" not in metric_key.lower() else TrendDirection.IMPROVING
            
            # Check for volatility
            if np.std(y_array) > np.mean(y_array) * 0.5:  # High volatility threshold
                direction = TrendDirection.VOLATILE
            
            # Calculate confidence based on correlation and data points
            confidence = abs(correlation) * min(1.0, len(values) / 20.0)
            
            # Generate forecast
            forecast = await self._generate_forecast(x_array, y_array, self.forecast_horizon)
            
            # Detect anomalies
            anomalies = await self._detect_metric_anomalies(timestamps, values)
            
            return TrendAnalysis(
                metric_name=metric_key,
                period=period,
                direction=direction,
                slope=slope,
                correlation=correlation,
                confidence=confidence,
                forecast=forecast,
                anomalies=anomalies
            )
            
        except Exception as e:
            logger.debug(f"Error calculating trend for {metric_key}: {str(e)}")
            return TrendAnalysis(
                metric_name=metric_key,
                period=period,
                direction=TrendDirection.STABLE,
                slope=0.0,
                correlation=0.0,
                confidence=0.0,
                forecast=[],
                anomalies=[]
            )
    
    async def _detect_anomalies(self):
        """Detect anomalies in recent statistics"""



        try:
            # Look for anomalies in recent data
            for period in [AggregationPeriod.HOUR, AggregationPeriod.DAY]:
                recent_data = await self._get_recent_aggregated_data(period, 24)  # Last 24 periods
                
                for timestamp, aggregations in recent_data.items():
                    for metric_key, agg_stat in aggregations.items():
                        # Check if value is anomalous
                        is_anomaly = await self._is_anomalous_value(metric_key, agg_stat.avg_value, period)
                        
                        if is_anomaly:
                            logger.warning(f"Anomaly detected in {metric_key}: {agg_stat.avg_value} at {timestamp}")
                            
                            # Could trigger alerts here
                            await self._handle_anomaly(metric_key, agg_stat, timestamp)
                            
        except Exception as e:
            logger.debug(f"Error detecting anomalies: {str(e)}")
    
    async def get_statistics_report(self, 
                                  period: AggregationPeriod = AggregationPeriod.DAY,
                                  metric_types: Optional[List[StatisticType]] = None,
                                  hours_back: int = 24) -> Dict[str, Any]:
        """Generate comprehensive statistics report"""



        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            report = {
                'period': period.value,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'summary': {},
                'metrics': {},
                'trends': {},
                'anomalies': [],
                'recommendations': []
            }
            
            # Filter metric types
            target_types = metric_types or list(StatisticType)
            
            # Get aggregated data for period
            aggregated_data = await self._get_aggregated_data_for_period(period, start_time, end_time)
            
            # Generate summary statistics
            for metric_type in target_types:
                type_metrics = {}
                
                for agg_key, aggregations in aggregated_data.items():
                    for metric_key, agg_stat in aggregations.items():
                        if agg_stat.metric_type == metric_type:
                            type_metrics[agg_stat.metric_name] = {
                                'count': agg_stat.count,
                                'avg': agg_stat.avg_value,
                                'min': agg_stat.min_value,
                                'max': agg_stat.max_value,
                                'std_dev': agg_stat.std_dev,
                                'percentiles': agg_stat.percentiles
                            }
                
                if type_metrics:
                    report['metrics'][metric_type.value] = type_metrics
            
            # Add trend analysis
            for cache_key, trend in self.trend_analysis_cache.items():
                if trend.period == period:
                    report['trends'][trend.metric_name] = {
                        'direction': trend.direction.value,
                        'slope': trend.slope,
                        'correlation': trend.correlation,
                        'confidence': trend.confidence,
                        'forecast': trend.forecast[:5],  # First 5 forecast points
                        'anomaly_count': len(trend.anomalies)
                    }
            
            # Generate recommendations
            report['recommendations'] = await self._generate_recommendations(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating statistics report: {str(e)}")
            return {'error': str(e)}
    
    # Helper methods (simplified implementations)
    async def _load_historical_statistics(self):
        """Load historical statistics from storage"""
        # Implementation would load from persistent storage
        pass
    
    async def _load_baselines(self):
        """Load performance baselines"""
        # Implementation would load baseline values
        pass
    
    async def _get_database_index_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get index statistics from database"""
        # Implementation would query database for index stats
        return {
            'content_idx': {'scans': 1000, 'seeks': 5000, 'size_bytes': 1024000},
            'vector_idx': {'scans': 500, 'seeks': 2000, 'size_bytes': 2048000}
        }
    
    async def _get_query_performance_metrics(self) -> Dict[str, float]:
        """Get query performance metrics"""



        return {
            'avg_query_time': 0.5,
            'queries_per_second': 150.0,
            'slow_query_count': 5
        }
    
    async def _get_storage_metrics(self) -> Dict[str, float]:
        """Get storage metrics"""



        return {
            'total_size': 10737418240,  # 10GB
            'index_size': 1073741824,   # 1GB
            'table_size': 9663676416    # 9GB
        }
    
    async def _get_cache_metrics(self) -> Dict[str, float]:
        """Get cache metrics"""



        return {
            'hit_rate': 85.0,
            'memory_usage': 536870912  # 512MB
        }
    
    async def _get_error_metrics(self) -> Dict[str, int]:
        """Get error metrics"""



        return {
            'connection_errors': 2,
            'query_errors': 1,
            'timeout_errors': 0
        }
    
    async def _execute_custom_metric(self, config: Dict[str, Any]) -> float:
        """Execute custom metric collection"""
        # Implementation would execute custom metric logic
        return 42.0
    
    async def _save_pending_statistics(self):
        """Save pending statistics to persistent storage"""
        # Implementation would save to database/file
        pass
    
    async def _get_recent_aggregated_data(self, period: AggregationPeriod, count: int) -> Dict[str, Dict[str, AggregatedStatistic]]:
        """Get recent aggregated data"""
        # Implementation would retrieve recent aggregated data
        return {}
    
    async def _get_aggregated_data_for_period(self, period: AggregationPeriod, 
                                            start_time: datetime, end_time: datetime) -> Dict[str, Dict[str, AggregatedStatistic]]:
        """Get aggregated data for time period"""
        # Implementation would retrieve data for period
        return {}
    
    async def _generate_forecast(self, x_values: np.ndarray, y_values: np.ndarray, horizon: int) -> List[float]:
        """Generate forecast values"""



        try:
            # Simple linear extrapolation
            coefficients = np.polyfit(x_values, y_values, 1)
            last_x = x_values[-1]
            
            forecast = []
            for i in range(1, horizon + 1):
                next_x = last_x + (x_values[-1] - x_values[-2]) * i
                next_y = np.polyval(coefficients, next_x)
                forecast.append(float(next_y))
            
            return forecast
        except Exception:
            return []
    
    async def _detect_metric_anomalies(self, timestamps: List[datetime], values: List[float]) -> List[datetime]:
        """Detect anomalies in metric values"""



        try:
            if len(values) < 3:
                return []
            
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            anomalies = []
            for i, (timestamp, value) in enumerate(zip(timestamps, values)):
                if abs(value - mean_val) > self.anomaly_threshold * std_val:
                    anomalies.append(timestamp)
            
            return anomalies
        except Exception:
            return []
    
    async def _is_anomalous_value(self, metric_key: str, value: float, period: AggregationPeriod) -> bool:
        """Check if value is anomalous"""
        # Implementation would check against baselines and historical data
        return False
    
    async def _handle_anomaly(self, metric_key: str, agg_stat: AggregatedStatistic, timestamp: datetime):
        """Handle detected anomaly"""
        # Implementation would trigger alerts or notifications
        pass
    
    async def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on statistics"""
        recommendations = []
        
        try:
            # Analyze trends for recommendations
            trends = report.get('trends', {})
            
            for metric_name, trend_data in trends.items():
                direction = trend_data['direction']
                confidence = trend_data['confidence']
                
                if confidence > 0.7:  # High confidence threshold
                    if direction == 'degrading':
                        if 'query_time' in metric_name:
                            recommendations.append(f"Query performance is degrading for {metric_name}, consider index optimization")
                        elif 'cache_hit_rate' in metric_name:
                            recommendations.append(f"Cache efficiency is declining, review caching strategy")
                        elif 'error' in metric_name:
                            recommendations.append(f"Error rate is increasing for {metric_name}, investigate root causes")
                    
                    elif direction == 'volatile':
                        recommendations.append(f"Metric {metric_name} shows high volatility, investigate instability causes")
            
            # Check metric thresholds
            metrics = report.get('metrics', {})
            
            if 'query_performance' in metrics:
                avg_query_time = metrics['query_performance'].get('avg_query_time', {}).get('avg', 0)
                if avg_query_time > 2.0:
                    recommendations.append("Average query time exceeds 2 seconds, consider performance optimization")
            
            if 'cache_efficiency' in metrics:
                cache_hit_rate = metrics['cache_efficiency'].get('cache_hit_rate', {}).get('avg', 100)
                if cache_hit_rate < 70.0:
                    recommendations.append("Cache hit rate is below 70%, review cache configuration")
            
            if not recommendations:
                recommendations.append("All metrics are within normal ranges")
                
        except Exception as e:
            logger.debug(f"Error generating recommendations: {str(e)}")
            recommendations.append("Unable to generate recommendations due to analysis error")
        
        return recommendations
    
    async def _cleanup_old_data(self):
        """Clean up old statistics data"""



        try:
            current_time = datetime.now()
            
            # Clean aggregated statistics based on retention policies
            keys_to_remove = []
            for agg_key, aggregations in self.aggregated_statistics.items():
                # Parse period from key
                try:
                    period_str = agg_key.split('_')[0]
                    period = AggregationPeriod(period_str)
                    
                    # Extract timestamp from key
                    timestamp_str = '_'.join(agg_key.split('_')[1:])
                    timestamp = datetime.fromisoformat(timestamp_str)
                    
                    # Check if data is too old
                    retention_days = self.retention_policies.get(period, 30)
                    if (current_time - timestamp).days > retention_days:
                        keys_to_remove.append(agg_key)
                        
                except Exception:
                    continue
            
            # Remove old data
            for key in keys_to_remove:
                del self.aggregated_statistics[key]
            
            if keys_to_remove:
                logger.debug(f"Cleaned up {len(keys_to_remove)} old aggregated statistics entries")
                
        except Exception as e:
            logger.debug(f"Error cleaning up old data: {str(e)}")
    
    async def register_custom_metric(self, metric_name: str, config: Dict[str, Any]):
        """Register custom metric for collection"""
        self.custom_metrics[metric_name] = config
        logger.info(f"Registered custom metric: {metric_name}")
    
    async def cleanup(self):
        """Cleanup statistics manager"""



        try:
            # Stop collection
            await self.stop_collection()
            
            # Cleanup components
            if self.db_manager:
                await self.db_manager.cleanup()
            
            if self.performance_tracker:
                await self.performance_tracker.cleanup()
            
            # Clear data
            self.raw_statistics.clear()
            self.aggregated_statistics.clear()
            self.trend_analysis_cache.clear()
            self.custom_metrics.clear()
            
            logger.info("StatisticsManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during StatisticsManager cleanup: {str(e)}")
