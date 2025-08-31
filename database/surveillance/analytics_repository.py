"""Analytics Repository Module
==========================

Advanced analytics system for surveillance monitoring data.
Provides comprehensive metrics, trends analysis, and reporting.

Author: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All Rights Reserved.
"""import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json
import statistics
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric type enumeration."""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AggregationType(Enum):
    """Aggregation type enumeration."""    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"


@dataclass
class Metric:
    """Metric data structure."""    name: str
    metric_type: MetricType
    value: float
    labels: Dict[str, str]
    timestamp: datetime
    description: Optional[str] = None


@dataclass
class AnalyticsQuery:
    """Analytics query structure."""    metric_names: List[str]
    start_time: datetime
    end_time: datetime
    aggregation: AggregationType
    group_by: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = None


@dataclass
class TrendData:
    """Trend analysis data structure."""    metric_name: str
    time_series: List[Tuple[datetime, float]]
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0.0 to 1.0
    seasonal_patterns: Dict[str, Any]
    anomalies: List[Dict[str, Any]]


class SurveillanceAnalytics:
    """    Main surveillance analytics engine.
    
    Collects, stores, and analyzes surveillance metrics for
    performance monitoring and optimization.
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_buffer: List[Metric] = []
        self.buffer_size = config.get("buffer_size", 1000)
        self.flush_interval = config.get("flush_interval", 60)
        self.storage_backend = None
        self.analytics_tasks: set = set()
        
    async def initialize(self) -> bool:
        """Initialize surveillance analytics."""        try:
            # Initialize storage backend
            await self._initialize_storage()
            
            # Start metrics processor
            await self._start_metrics_processor()
            
            # Initialize predefined metrics
            await self._initialize_predefined_metrics()
            
            logger.info("SurveillanceAnalytics initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SurveillanceAnalytics: {e}")
            return False
    
    async def _initialize_storage(self) -> None:
        """Initialize analytics storage backend."""        storage_config = self.config.get("storage", {})
        storage_type = storage_config.get("type", "elasticsearch")
        
        if storage_type == "elasticsearch":
            from .storage.elasticsearch_backend import ElasticsearchBackend
            self.storage_backend = ElasticsearchBackend(storage_config)
        elif storage_type == "prometheus":
            from .storage.prometheus_backend import PrometheusBackend
            self.storage_backend = PrometheusBackend(storage_config)
        elif storage_type == "influxdb":
            from .storage.influxdb_backend import InfluxDBBackend
            self.storage_backend = InfluxDBBackend(storage_config)
        else:
            # Default to memory backend for development
            from .storage.memory_backend import MemoryBackend
            self.storage_backend = MemoryBackend(storage_config)
        
        await self.storage_backend.initialize()
        logger.info(f"Initialized {storage_type} storage backend")
    
    async def _start_metrics_processor(self) -> None:
        """Start metrics processing task."""        processor_task = asyncio.create_task(self._metrics_processor())
        self.analytics_tasks.add(processor_task)
        processor_task.add_done_callback(self.analytics_tasks.discard)
        logger.info("Metrics processor started")
    
    async def _metrics_processor(self) -> None:
        """Process and flush metrics buffer."""        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                
                if self.metrics_buffer:
                    # Copy and clear buffer
                    metrics_to_flush = self.metrics_buffer.copy()
                    self.metrics_buffer.clear()
                    
                    # Store metrics
                    await self.storage_backend.store_metrics(metrics_to_flush)
                    logger.debug(f"Flushed {len(metrics_to_flush)} metrics to storage")
                
            except Exception as e:
                logger.error(f"Error in metrics processor: {e}")
                await asyncio.sleep(5)
    
    async def _initialize_predefined_metrics(self) -> None:
        """Initialize predefined surveillance metrics."""        predefined_metrics = [
            ("surveillance.violations.detected", MetricType.COUNTER, "Total violations detected"),
            ("surveillance.violations.resolved", MetricType.COUNTER, "Total violations resolved"),
            ("surveillance.scans.completed", MetricType.COUNTER, "Total scans completed"),
            ("surveillance.scan.duration", MetricType.HISTOGRAM, "Scan duration in seconds"),
            ("surveillance.similarity.score", MetricType.HISTOGRAM, "Similarity scores"),
            ("surveillance.confidence.level", MetricType.HISTOGRAM, "Confidence levels"),
            ("surveillance.active.targets", MetricType.GAUGE, "Active monitoring targets"),
            ("surveillance.platform.coverage", MetricType.GAUGE, "Platform coverage percentage"),
            ("surveillance.detection.accuracy", MetricType.GAUGE, "Detection accuracy percentage"),
            ("surveillance.false.positives", MetricType.COUNTER, "False positive detections"),
            ("surveillance.alert.response.time", MetricType.HISTOGRAM, "Alert response time"),
            ("surveillance.evidence.collected", MetricType.COUNTER, "Evidence items collected")
        ]
        
        for metric_name, metric_type, description in predefined_metrics:
            await self._ensure_metric_exists(metric_name, metric_type, description)
        
        logger.info(f"Initialized {len(predefined_metrics)} predefined metrics")
    
    async def _ensure_metric_exists(self, name: str, metric_type: MetricType, description: str) -> None:
        """Ensure metric definition exists in storage."""        try:
            await self.storage_backend.create_metric_definition(name, metric_type, description)
        except Exception as e:
            logger.debug(f"Metric {name} already exists or error creating: {e}")
    
    async def record_metric(self, 
                          name: str, 
                          value: float, 
                          labels: Optional[Dict[str, str]] = None,
                          timestamp: Optional[datetime] = None) -> None:
        """Record a metric value."""        try:
            metric = Metric(
                name=name,
                metric_type=MetricType.COUNTER,  # Default, will be updated based on definition
                value=value,
                labels=labels or {},
                timestamp=timestamp or datetime.utcnow()
            )
            
            self.metrics_buffer.append(metric)
            
            # Flush buffer if it's full
            if len(self.metrics_buffer) >= self.buffer_size:
                metrics_to_flush = self.metrics_buffer.copy()
                self.metrics_buffer.clear()
                await self.storage_backend.store_metrics(metrics_to_flush)
            
        except Exception as e:
            logger.error(f"Error recording metric {name}: {e}")
    
    async def increment_counter(self, 
                              name: str, 
                              increment: float = 1.0,
                              labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""        await self.record_metric(name, increment, labels)
    
    async def set_gauge(self, 
                       name: str, 
                       value: float,
                       labels: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric value."""        await self.record_metric(name, value, labels)
    
    async def record_histogram(self, 
                             name: str, 
                             value: float,
                             labels: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram metric value."""        await self.record_metric(name, value, labels)
    
    async def query_metrics(self, query: AnalyticsQuery) -> List[Dict[str, Any]]:
        """Query metrics from storage."""        try:
            return await self.storage_backend.query_metrics(query)
        except Exception as e:
            logger.error(f"Error querying metrics: {e}")
            return []
    
    async def get_user_analytics(self, 
                               user_id: str, 
                               date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get analytics data for specific user."""        try:
            # Define date range
            if date_range:
                start_time = datetime.fromisoformat(date_range["start"])
                end_time = datetime.fromisoformat(date_range["end"])
            else:
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=30)
            
            # Query user-specific metrics
            user_labels = {"user_id": user_id}
            
            # Violations detected
            violations_query = AnalyticsQuery(
                metric_names=["surveillance.violations.detected"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.SUM,
                filters={"labels": user_labels}
            )
            violations_data = await self.query_metrics(violations_query)
            
            # Scans completed
            scans_query = AnalyticsQuery(
                metric_names=["surveillance.scans.completed"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.SUM,
                filters={"labels": user_labels}
            )
            scans_data = await self.query_metrics(scans_query)
            
            # Average scan duration
            duration_query = AnalyticsQuery(
                metric_names=["surveillance.scan.duration"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.AVERAGE,
                filters={"labels": user_labels}
            )
            duration_data = await self.query_metrics(duration_query)
            
            # Detection accuracy
            accuracy_query = AnalyticsQuery(
                metric_names=["surveillance.detection.accuracy"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.AVERAGE,
                filters={"labels": user_labels}
            )
            accuracy_data = await self.query_metrics(accuracy_query)
            
            # Evidence collected
            evidence_query = AnalyticsQuery(
                metric_names=["surveillance.evidence.collected"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.SUM,
                filters={"labels": user_labels}
            )
            evidence_data = await self.query_metrics(evidence_query)
            
            # Compile analytics data
            analytics = {
                "user_id": user_id,
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "violations_count": violations_data[0]["value"] if violations_data else 0,
                "scans_count": scans_data[0]["value"] if scans_data else 0,
                "avg_scan_duration": duration_data[0]["value"] if duration_data else 0,
                "detection_accuracy": accuracy_data[0]["value"] if accuracy_data else 0,
                "evidence_count": evidence_data[0]["value"] if evidence_data else 0,
                "platforms_count": await self._get_user_platforms_count(user_id, start_time, end_time),
                "effectiveness_score": await self._calculate_effectiveness_score(user_id, start_time, end_time),
                "avg_detection_time": await self._get_average_detection_time(user_id, start_time, end_time)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting user analytics for {user_id}: {e}")
            return {}
    
    async def _get_user_platforms_count(self, user_id: str, start_time: datetime, end_time: datetime) -> int:
        """Get count of platforms monitored for user."""        try:
            # Query platform-specific metrics
            platforms_query = AnalyticsQuery(
                metric_names=["surveillance.scans.completed"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.COUNT,
                group_by=["platform"],
                filters={"labels": {"user_id": user_id}}
            )
            platforms_data = await self.query_metrics(platforms_query)
            return len(platforms_data)
            
        except Exception as e:
            logger.error(f"Error getting platforms count: {e}")
            return 0
    
    async def _calculate_effectiveness_score(self, user_id: str, start_time: datetime, end_time: datetime) -> float:
        """Calculate surveillance effectiveness score."""        try:
            # Get violations detected and false positives
            violations_query = AnalyticsQuery(
                metric_names=["surveillance.violations.detected"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.SUM,
                filters={"labels": {"user_id": user_id}}
            )
            violations_data = await self.query_metrics(violations_query)
            total_violations = violations_data[0]["value"] if violations_data else 0
            
            false_positives_query = AnalyticsQuery(
                metric_names=["surveillance.false.positives"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.SUM,
                filters={"labels": {"user_id": user_id}}
            )
            false_positives_data = await self.query_metrics(false_positives_query)
            false_positives = false_positives_data[0]["value"] if false_positives_data else 0
            
            # Calculate effectiveness score
            if total_violations > 0:
                effectiveness = (total_violations - false_positives) / total_violations
                return max(0.0, min(1.0, effectiveness))
            
            return 1.0  # Perfect score if no violations
            
        except Exception as e:
            logger.error(f"Error calculating effectiveness score: {e}")
            return 0.0
    
    async def _get_average_detection_time(self, user_id: str, start_time: datetime, end_time: datetime) -> float:
        """Get average detection time for user."""        try:
            detection_time_query = AnalyticsQuery(
                metric_names=["surveillance.alert.response.time"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.AVERAGE,
                filters={"labels": {"user_id": user_id}}
            )
            detection_time_data = await self.query_metrics(detection_time_query)
            return detection_time_data[0]["value"] if detection_time_data else 0.0
            
        except Exception as e:
            logger.error(f"Error getting average detection time: {e}")
            return 0.0
    
    async def get_platform_analytics(self, platform: str, date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get analytics data for specific platform."""        try:
            # Define date range
            if date_range:
                start_time = datetime.fromisoformat(date_range["start"])
                end_time = datetime.fromisoformat(date_range["end"])
            else:
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=7)
            
            platform_labels = {"platform": platform}
            
            # Platform-specific queries
            scans_query = AnalyticsQuery(
                metric_names=["surveillance.scans.completed"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.SUM,
                filters={"labels": platform_labels}
            )
            
            violations_query = AnalyticsQuery(
                metric_names=["surveillance.violations.detected"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.SUM,
                filters={"labels": platform_labels}
            )
            
            # Execute queries
            scans_data = await self.query_metrics(scans_query)
            violations_data = await self.query_metrics(violations_query)
            
            platform_analytics = {
                "platform": platform,
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "scans_completed": scans_data[0]["value"] if scans_data else 0,
                "violations_detected": violations_data[0]["value"] if violations_data else 0,
                "violation_rate": self._calculate_violation_rate(scans_data, violations_data)
            }
            
            return platform_analytics
            
        except Exception as e:
            logger.error(f"Error getting platform analytics for {platform}: {e}")
            return {}
    
    def _calculate_violation_rate(self, scans_data: List[Dict], violations_data: List[Dict]) -> float:
        """Calculate violation rate from scans and violations data."""        scans = scans_data[0]["value"] if scans_data else 0
        violations = violations_data[0]["value"] if violations_data else 0
        
        if scans > 0:
            return violations / scans
        return 0.0
    
    async def get_trend_analysis(self, 
                               metric_name: str,
                               period_days: int = 30,
                               user_id: Optional[str] = None) -> TrendData:
        """Get trend analysis for specific metric."""        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=period_days)
            
            # Build query filters
            filters = {}
            if user_id:
                filters["labels"] = {"user_id": user_id}
            
            # Query time series data
            query = AnalyticsQuery(
                metric_names=[metric_name],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.AVERAGE,
                filters=filters
            )
            
            time_series_data = await self.storage_backend.query_time_series(query)
            
            # Analyze trends
            trend_analysis = await self._analyze_trend(metric_name, time_series_data)
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Error getting trend analysis for {metric_name}: {e}")
            return TrendData(
                metric_name=metric_name,
                time_series=[],
                trend_direction="unknown",
                trend_strength=0.0,
                seasonal_patterns={},
                anomalies=[]
            )
    
    async def _analyze_trend(self, metric_name: str, time_series_data: List[Tuple[datetime, float]]) -> TrendData:
        """Analyze trend from time series data."""        if not time_series_data:
            return TrendData(
                metric_name=metric_name,
                time_series=[],
                trend_direction="unknown",
                trend_strength=0.0,
                seasonal_patterns={},
                anomalies=[]
            )
        
        # Extract values for analysis
        values = [point[1] for point in time_series_data]
        
        # Calculate trend direction and strength
        if len(values) >= 2:
            # Simple linear trend calculation
            first_half_avg = statistics.mean(values[:len(values)//2])
            second_half_avg = statistics.mean(values[len(values)//2:])
            
            if second_half_avg > first_half_avg * 1.1:
                trend_direction = "increasing"
                trend_strength = min(1.0, (second_half_avg - first_half_avg) / first_half_avg)
            elif second_half_avg < first_half_avg * 0.9:
                trend_direction = "decreasing"
                trend_strength = min(1.0, (first_half_avg - second_half_avg) / first_half_avg)
            else:
                trend_direction = "stable"
                trend_strength = 0.0
        else:
            trend_direction = "unknown"
            trend_strength = 0.0
        
        # Detect anomalies (simple outlier detection)
        anomalies = self._detect_anomalies(time_series_data)
        
        # Detect seasonal patterns
        seasonal_patterns = self._detect_seasonal_patterns(time_series_data)
        
        return TrendData(
            metric_name=metric_name,
            time_series=time_series_data,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            seasonal_patterns=seasonal_patterns,
            anomalies=anomalies
        )
    
    def _detect_anomalies(self, time_series_data: List[Tuple[datetime, float]]) -> List[Dict[str, Any]]:
        """Detect anomalies in time series data."""        if len(time_series_data) < 10:
            return []
        
        values = [point[1] for point in time_series_data]
        mean_value = statistics.mean(values)
        stdev_value = statistics.stdev(values) if len(values) > 1 else 0
        
        anomalies = []
        threshold = 2.0  # 2 standard deviations
        
        for timestamp, value in time_series_data:
            if stdev_value > 0:
                z_score = abs(value - mean_value) / stdev_value
                if z_score > threshold:
                    anomalies.append({
                        "timestamp": timestamp.isoformat(),
                        "value": value,
                        "z_score": z_score,
                        "type": "outlier"
                    })
        
        return anomalies
    
    def _detect_seasonal_patterns(self, time_series_data: List[Tuple[datetime, float]]) -> Dict[str, Any]:
        """Detect seasonal patterns in time series data."""        if len(time_series_data) < 24:  # Need at least 24 data points
            return {}
        
        # Group by hour of day
        hourly_values = defaultdict(list)
        daily_values = defaultdict(list)
        
        for timestamp, value in time_series_data:
            hourly_values[timestamp.hour].append(value)
            daily_values[timestamp.weekday()].append(value)
        
        # Calculate hourly patterns
        hourly_patterns = {}
        for hour, values in hourly_values.items():
            if len(values) >= 3:
                hourly_patterns[str(hour)] = {
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
        
        # Calculate daily patterns
        daily_patterns = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day_num, values in daily_values.items():
            if len(values) >= 3:
                daily_patterns[days[day_num]] = {
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
        
        return {
            "hourly": hourly_patterns,
            "daily": daily_patterns
        }
    
    async def generate_analytics_summary(self, date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate comprehensive analytics summary."""        try:
            # Define date range
            if date_range:
                start_time = datetime.fromisoformat(date_range["start"])
                end_time = datetime.fromisoformat(date_range["end"])
            else:
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=7)
            
            # Query overall metrics
            total_violations_query = AnalyticsQuery(
                metric_names=["surveillance.violations.detected"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.SUM
            )
            
            total_scans_query = AnalyticsQuery(
                metric_names=["surveillance.scans.completed"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.SUM
            )
            
            avg_accuracy_query = AnalyticsQuery(
                metric_names=["surveillance.detection.accuracy"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.AVERAGE
            )
            
            # Execute queries
            violations_data = await self.query_metrics(total_violations_query)
            scans_data = await self.query_metrics(total_scans_query)
            accuracy_data = await self.query_metrics(avg_accuracy_query)
            
            # Platform breakdown
            platform_breakdown = await self._get_platform_breakdown(start_time, end_time)
            
            # Top users by violations
            top_users = await self._get_top_users_by_violations(start_time, end_time)
            
            summary = {
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "overall_metrics": {
                    "total_violations": violations_data[0]["value"] if violations_data else 0,
                    "total_scans": scans_data[0]["value"] if scans_data else 0,
                    "average_accuracy": accuracy_data[0]["value"] if accuracy_data else 0,
                    "violation_rate": self._calculate_violation_rate(scans_data, violations_data)
                },
                "platform_breakdown": platform_breakdown,
                "top_users": top_users,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating analytics summary: {e}")
            return {}
    
    async def _get_platform_breakdown(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get platform breakdown of violations."""        try:
            platform_query = AnalyticsQuery(
                metric_names=["surveillance.violations.detected"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.SUM,
                group_by=["platform"]
            )
            
            platform_data = await self.query_metrics(platform_query)
            
            breakdown = {}
            for item in platform_data:
                platform = item.get("labels", {}).get("platform", "unknown")
                breakdown[platform] = item["value"]
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error getting platform breakdown: {e}")
            return {}
    
    async def _get_top_users_by_violations(self, start_time: datetime, end_time: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users by violation count."""        try:
            users_query = AnalyticsQuery(
                metric_names=["surveillance.violations.detected"],
                start_time=start_time,
                end_time=end_time,
                aggregation=AggregationType.SUM,
                group_by=["user_id"],
                limit=limit
            )
            
            users_data = await self.query_metrics(users_query)
            
            top_users = []
            for item in users_data:
                user_id = item.get("labels", {}).get("user_id", "unknown")
                top_users.append({
                    "user_id": user_id,
                    "violations_count": item["value"]
                })
            
            # Sort by violations count
            top_users.sort(key=lambda x: x["violations_count"], reverse=True)
            
            return top_users[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top users: {e}")
            return []
    
    async def shutdown(self) -> None:
        """Shutdown surveillance analytics."""        logger.info("Shutting down SurveillanceAnalytics...")
        
        # Flush remaining metrics
        if self.metrics_buffer:
            await self.storage_backend.store_metrics(self.metrics_buffer)
            self.metrics_buffer.clear()
        
        # Cancel analytics tasks
        for task in self.analytics_tasks:
            task.cancel()
        
        if self.analytics_tasks:
            await asyncio.gather(*self.analytics_tasks, return_exceptions=True)
        
        # Shutdown storage backend
        if self.storage_backend:
            await self.storage_backend.shutdown()
        
        logger.info("SurveillanceAnalytics shutdown complete")


class MetricsCollector:
    """    Metrics collector for surveillance system.
    
    Collects metrics from various surveillance components
    and forwards them to analytics engine.
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.analytics_engine: Optional[SurveillanceAnalytics] = None
        self.collection_interval = config.get("collection_interval", 30)
        self.collector_tasks: set = set()
        
    async def initialize(self, analytics_engine: SurveillanceAnalytics) -> bool:
        """Initialize metrics collector."""        try:
            self.analytics_engine = analytics_engine
            
            # Start metrics collection
            await self._start_metrics_collection()
            
            logger.info("MetricsCollector initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MetricsCollector: {e}")
            return False
    
    async def _start_metrics_collection(self) -> None:
        """Start metrics collection tasks."""        collection_task = asyncio.create_task(self._metrics_collection_loop())
        self.collector_tasks.add(collection_task)
        collection_task.add_done_callback(self.collector_tasks.discard)
        logger.info("Metrics collection started")
    
    async def _metrics_collection_loop(self) -> None:
        """Main metrics collection loop."""        while True:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect surveillance metrics
                await self._collect_surveillance_metrics()
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(10)
    
    async def _collect_system_metrics(self) -> None:
        """Collect system-level metrics."""        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            await self.analytics_engine.set_gauge("system.cpu.usage", cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            await self.analytics_engine.set_gauge("system.memory.usage", memory.percent)
            await self.analytics_engine.set_gauge("system.memory.available", memory.available)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            await self.analytics_engine.set_gauge("system.disk.usage", (disk.used / disk.total) * 100)
            
        except Exception as e:
            logger.debug(f"Error collecting system metrics: {e}")
    
    async def _collect_surveillance_metrics(self) -> None:
        """Collect surveillance-specific metrics."""        try:
            # Get monitoring engine status
            from .monitoring_engines import ContentMonitoringEngine
            # This would typically query the monitoring engine for current metrics
            
            # Example: Active targets count
            # active_targets = await monitoring_engine.get_active_targets_count()
            # await self.analytics_engine.set_gauge("surveillance.active.targets", active_targets)
            
            pass
            
        except Exception as e:
            logger.debug(f"Error collecting surveillance metrics: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown metrics collector."""        logger.info("Shutting down MetricsCollector...")
        
        # Cancel collector tasks
        for task in self.collector_tasks:
            task.cancel()
        
        if self.collector_tasks:
            await asyncio.gather(*self.collector_tasks, return_exceptions=True)
        
        logger.info("MetricsCollector shutdown complete")


class TrendAnalyzer:
    """    Trend analyzer for surveillance metrics.
    
    Analyzes trends and patterns in surveillance data
    to provide insights and optimization recommendations.
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.analysis_models: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """Initialize trend analyzer."""        try:
            # Initialize analysis models
            await self._initialize_analysis_models()
            
            logger.info("TrendAnalyzer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize TrendAnalyzer: {e}")
            return False
    
    async def _initialize_analysis_models(self) -> None:
        """Initialize trend analysis models."""        models_config = self.config.get("analysis_models", {})
        
        # Simple moving average model
        self.analysis_models["moving_average"] = {
            "window_size": models_config.get("moving_average", {}).get("window_size", 10)
        }
        
        # Exponential smoothing model
        self.analysis_models["exponential_smoothing"] = {
            "alpha": models_config.get("exponential_smoothing", {}).get("alpha", 0.3)
        }
        
        logger.info(f"Initialized {len(self.analysis_models)} analysis models")
    
    async def analyze_metric_trend(self, 
                                 metric_name: str,
                                 time_series_data: List[Tuple[datetime, float]],
                                 model_type: str = "moving_average") -> Dict[str, Any]:
        """Analyze trend for specific metric."""        try:
            if model_type not in self.analysis_models:
                logger.error(f"Unknown analysis model: {model_type}")
                return {}
            
            if model_type == "moving_average":
                return await self._moving_average_analysis(metric_name, time_series_data)
            elif model_type == "exponential_smoothing":
                return await self._exponential_smoothing_analysis(metric_name, time_series_data)
            
            return {}
            
        except Exception as e:
            logger.error(f"Error analyzing trend for {metric_name}: {e}")
            return {}
    
    async def _moving_average_analysis(self, 
                                     metric_name: str,
                                     time_series_data: List[Tuple[datetime, float]]) -> Dict[str, Any]:
        """Perform moving average trend analysis."""        if not time_series_data:
            return {}
        
        window_size = self.analysis_models["moving_average"]["window_size"]
        values = [point[1] for point in time_series_data]
        
        if len(values) < window_size:
            return {"error": "Insufficient data for moving average analysis"}
        
        # Calculate moving averages
        moving_averages = []
        for i in range(window_size - 1, len(values)):
            window = values[i - window_size + 1:i + 1]
            moving_averages.append(statistics.mean(window))
        
        # Analyze trend
        if len(moving_averages) >= 2:
            first_avg = moving_averages[0]
            last_avg = moving_averages[-1]
            
            trend_change = (last_avg - first_avg) / first_avg if first_avg != 0 else 0
            
            if trend_change > 0.1:
                trend_direction = "increasing"
            elif trend_change < -0.1:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "unknown"
            trend_change = 0
        
        return {
            "metric_name": metric_name,
            "analysis_type": "moving_average",
            "trend_direction": trend_direction,
            "trend_change": trend_change,
            "moving_averages": moving_averages,
            "window_size": window_size
        }
    
    async def _exponential_smoothing_analysis(self, 
                                            metric_name: str,
                                            time_series_data: List[Tuple[datetime, float]]) -> Dict[str, Any]:
        """Perform exponential smoothing trend analysis."""        if not time_series_data:
            return {}
        
        alpha = self.analysis_models["exponential_smoothing"]["alpha"]
        values = [point[1] for point in time_series_data]
        
        if len(values) < 2:
            return {"error": "Insufficient data for exponential smoothing analysis"}
        
        # Calculate exponential smoothing
        smoothed_values = [values[0]]  # Start with first value
        
        for i in range(1, len(values)):
            smoothed_value = alpha * values[i] + (1 - alpha) * smoothed_values[-1]
            smoothed_values.append(smoothed_value)
        
        # Analyze trend
        first_smoothed = smoothed_values[0]
        last_smoothed = smoothed_values[-1]
        
        trend_change = (last_smoothed - first_smoothed) / first_smoothed if first_smoothed != 0 else 0
        
        if trend_change > 0.05:
            trend_direction = "increasing"
        elif trend_change < -0.05:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        return {
            "metric_name": metric_name,
            "analysis_type": "exponential_smoothing",
            "trend_direction": trend_direction,
            "trend_change": trend_change,
            "smoothed_values": smoothed_values,
            "alpha": alpha
        }


class ReportGenerator:
    """    Report generator for surveillance analytics.
    
    Generates comprehensive reports based on analytics data
    for different stakeholders and use cases.
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.report_templates: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """Initialize report generator."""        try:
            # Load report templates
            await self._load_report_templates()
            
            logger.info("ReportGenerator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize ReportGenerator: {e}")
            return False
    
    async def _load_report_templates(self) -> None:
        """Load report templates."""        templates_config = self.config.get("report_templates", {})
        
        # Default templates
        default_templates = {
            "executive_summary": {
                "sections": ["overview", "key_metrics", "trends", "recommendations"],
                "format": "html"
            },
            "technical_report": {
                "sections": ["system_performance", "detection_accuracy", "platform_analysis", "optimization"],
                "format": "html"
            },
            "user_dashboard": {
                "sections": ["user_metrics", "violations", "alerts", "evidence"],
                "format": "json"
            }
        }
        
        self.report_templates = templates_config or default_templates
        logger.info(f"Loaded {len(self.report_templates)} report templates")
    
    async def generate_report(self, 
                            report_type: str,
                            analytics_data: Dict[str, Any],
                            date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate report based on analytics data."""        try:
            if report_type not in self.report_templates:
                logger.error(f"Unknown report type: {report_type}")
                return {}
            
            template = self.report_templates[report_type]
            
            if report_type == "executive_summary":
                return await self._generate_executive_summary(analytics_data, date_range)
            elif report_type == "technical_report":
                return await self._generate_technical_report(analytics_data, date_range)
            elif report_type == "user_dashboard":
                return await self._generate_user_dashboard(analytics_data, date_range)
            
            return {}
            
        except Exception as e:
            logger.error(f"Error generating {report_type} report: {e}")
            return {}
    
    async def _generate_executive_summary(self, 
                                        analytics_data: Dict[str, Any],
                                        date_range: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Generate executive summary report."""        return {
            "report_type": "executive_summary",
            "generated_at": datetime.utcnow().isoformat(),
            "period": date_range,
            "overview": {
                "total_violations": analytics_data.get("total_violations", 0),
                "detection_accuracy": analytics_data.get("detection_accuracy", 0),
                "platforms_monitored": analytics_data.get("platforms_count", 0),
                "effectiveness_score": analytics_data.get("effectiveness_score", 0)
            },
            "key_metrics": analytics_data,
            "recommendations": await self._generate_recommendations(analytics_data)
        }
    
    async def _generate_technical_report(self, 
                                       analytics_data: Dict[str, Any],
                                       date_range: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Generate technical report."""        return {
            "report_type": "technical_report",
            "generated_at": datetime.utcnow().isoformat(),
            "period": date_range,
            "system_performance": {
                "scan_duration": analytics_data.get("avg_scan_duration", 0),
                "detection_time": analytics_data.get("avg_detection_time", 0),
                "accuracy": analytics_data.get("detection_accuracy", 0)
            },
            "platform_analysis": analytics_data.get("platform_breakdown", {}),
            "optimization_opportunities": await self._identify_optimization_opportunities(analytics_data)
        }
    
    async def _generate_user_dashboard(self, 
                                     analytics_data: Dict[str, Any],
                                     date_range: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Generate user dashboard data."""        return {
            "report_type": "user_dashboard",
            "generated_at": datetime.utcnow().isoformat(),
            "period": date_range,
            "user_metrics": {
                "violations_detected": analytics_data.get("violations_count", 0),
                "evidence_collected": analytics_data.get("evidence_count", 0),
                "platforms_monitored": analytics_data.get("platforms_count", 0),
                "effectiveness": analytics_data.get("effectiveness_score", 0)
            },
            "recent_activity": analytics_data.get("recent_activity", []),
            "alerts_summary": analytics_data.get("alerts_summary", {})
        }
    
    async def _generate_recommendations(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analytics data."""        recommendations = []
        
        effectiveness = analytics_data.get("effectiveness_score", 0)
        if effectiveness < 0.8:
            recommendations.append("Consider adjusting detection thresholds to improve accuracy")
        
        avg_detection_time = analytics_data.get("avg_detection_time", 0)
        if avg_detection_time > 300:  # 5 minutes
            recommendations.append("Optimize scanning frequency to reduce detection time")
        
        platforms_count = analytics_data.get("platforms_count", 0)
        if platforms_count < 3:
            recommendations.append("Expand monitoring to additional platforms for better coverage")
        
        return recommendations
    
    async def _identify_optimization_opportunities(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Identify optimization opportunities."""        opportunities = []
        
        scan_duration = analytics_data.get("avg_scan_duration", 0)
        if scan_duration > 60:  # 1 minute
            opportunities.append("Optimize scanning algorithms to reduce scan duration")
        
        false_positive_rate = analytics_data.get("false_positive_rate", 0)
        if false_positive_rate > 0.1:  # 10%
            opportunities.append("Improve fingerprinting accuracy to reduce false positives")
        
        return opportunities
