#!/usr/bin/env python3
"""
IA Chéries Platform - Monitoring Data Aggregation Engine
===================================================

Enterprise-grade data aggregation engine for Creator Economy monitoring.
Handles multi-source data aggregation, creator metrics consolidation,
time-series data processing, cross-domain analytics correlation, and historical trend analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import hashlib
import uuid
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Data source types for aggregation"""
    BUSINESS_MONITORING = "business_monitoring"
    CREATOR_ECONOMY = "creator_economy"
    CONTENT_PROCESSING = "content_processing"
    AI_MONITORING = "ai_monitoring"
    COLLABORATION = "collaboration"
    SEO_PERFORMANCE = "seo_performance"
    DISTRIBUTION = "distribution"
    GAMIFICATION = "gamification"
    REAL_TIME_EVENTS = "real_time_events"

class AggregationPeriod(Enum):
    """Time periods for data aggregation"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class MetricType(Enum):
    """Types of metrics for aggregation"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"

@dataclass
class DataPoint:
    """Individual data point for aggregation"""
    source: DataSource
    metric_name: str
    metric_type: MetricType
    value: Union[float, int, Dict[str, Any]]
    timestamp: datetime
    creator_id: Optional[str] = None
    content_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AggregatedMetric:
    """Aggregated metric result"""
    metric_name: str
    source: DataSource
    period: AggregationPeriod
    start_time: datetime
    end_time: datetime
    aggregated_value: Union[float, Dict[str, Any]]
    data_points_count: int
    aggregation_method: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CrossDomainCorrelation:
    """Cross-domain analytics correlation"""
    correlation_id: str
    primary_metric: str
    secondary_metric: str
    correlation_coefficient: float
    confidence_level: float
    sample_size: int
    time_period: AggregationPeriod
    insights: List[str] = field(default_factory=list)
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class TrendAnalysis:
    """Historical trend analysis result"""
    metric_name: str
    trend_direction: str  # "increasing", "decreasing", "stable", "volatile"
    trend_strength: float  # 0.0 to 1.0
    seasonal_patterns: Dict[str, float]
    anomalies: List[Dict[str, Any]]
    forecasted_values: List[float]
    analysis_period: AggregationPeriod
    confidence_interval: Tuple[float, float]
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class MonitoringDataAggregationEngine:
    """
    Enterprise monitoring data aggregation engine for Creator Economy platform.
    
    Capabilities:
    - Multi-source data aggregation
    - Creator metrics consolidation
    - Time-series data processing
    - Cross-domain analytics correlation
    - Historical data trend analysis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.data_points: deque = deque(maxlen=100000)  # Rolling buffer for data points
        self.aggregated_metrics: Dict[str, List[AggregatedMetric]] = defaultdict(list)
        self.correlations: Dict[str, CrossDomainCorrelation] = {}
        self.trend_analyses: Dict[str, TrendAnalysis] = {}
        self.aggregation_active = False
        
        # Initialize aggregation systems
        self._initialize_aggregation_rules()
        self._initialize_correlation_engine()
        self._initialize_trend_analysis()
        self._initialize_data_storage()
        
        logger.info("MonitoringDataAggregationEngine initialized successfully")
    
    def _initialize_aggregation_rules(self):
        """Initialize data aggregation rules and configurations."""
        self.aggregation_rules = {
            MetricType.COUNTER: {
                "methods": ["sum", "count", "rate"],
                "default_method": "sum"
            },
            MetricType.GAUGE: {
                "methods": ["avg", "min", "max", "last"],
                "default_method": "avg"
            },
            MetricType.HISTOGRAM: {
                "methods": ["percentile", "avg", "distribution"],
                "default_method": "percentile"
            },
            MetricType.RATE: {
                "methods": ["avg", "moving_avg", "weighted_avg"],
                "default_method": "avg"
            },
            MetricType.PERCENTAGE: {
                "methods": ["avg", "weighted_avg"],
                "default_method": "weighted_avg"
            },
            MetricType.CURRENCY: {
                "methods": ["sum", "avg", "total"],
                "default_method": "sum"
            }
        }
        
        self.aggregation_schedules = {
            AggregationPeriod.MINUTE: {"interval_seconds": 60, "retention_hours": 24},
            AggregationPeriod.HOUR: {"interval_seconds": 3600, "retention_days": 30},
            AggregationPeriod.DAY: {"interval_seconds": 86400, "retention_days": 365},
            AggregationPeriod.WEEK: {"interval_seconds": 604800, "retention_weeks": 104},
            AggregationPeriod.MONTH: {"interval_seconds": 2592000, "retention_months": 60},
            AggregationPeriod.QUARTER: {"interval_seconds": 7776000, "retention_quarters": 20},
            AggregationPeriod.YEAR: {"interval_seconds": 31536000, "retention_years": 10}
        }
        
        self.priority_metrics = [
            "creator_revenue",
            "content_engagement_rate",
            "collaboration_success_rate",
            "seo_performance_score",
            "distribution_reach",
            "gamification_engagement"
        ]
    
    def _initialize_correlation_engine(self):
        """Initialize cross-domain correlation analysis."""
        self.correlation_pairs = [
            ("creator_revenue", "content_engagement_rate"),
            ("seo_performance_score", "distribution_reach"),
            ("collaboration_success_rate", "creator_revenue"),
            ("gamification_engagement", "content_engagement_rate"),
            ("ai_processing_quality", "content_engagement_rate"),
            ("distribution_reach", "creator_revenue")
        ]
        
        self.correlation_thresholds = {
            "strong_correlation": 0.7,
            "moderate_correlation": 0.5,
            "weak_correlation": 0.3,
            "minimum_sample_size": 30,
            "confidence_level": 0.95
        }
        
        self.correlation_cache: Dict[str, Dict] = {}
    
    def _initialize_trend_analysis(self):
        """Initialize trend analysis systems."""
        self.trend_algorithms = {
            "linear_regression": self._calculate_linear_trend,
            "moving_average": self._calculate_moving_average_trend,
            "exponential_smoothing": self._calculate_exponential_smoothing_trend,
            "seasonal_decomposition": self._calculate_seasonal_trend
        }
        
        self.trend_detection_config = {
            "minimum_data_points": 10,
            "trend_threshold": 0.1,  # 10% change to be considered trending
            "volatility_threshold": 0.2,  # 20% variance for volatility detection
            "anomaly_detection_std": 2.5,  # Standard deviations for anomaly detection
            "forecast_periods": 5  # Number of periods to forecast
        }
        
        self.seasonal_patterns = {
            AggregationPeriod.HOUR: ["hour_of_day"],
            AggregationPeriod.DAY: ["day_of_week", "day_of_month"],
            AggregationPeriod.WEEK: ["week_of_month", "week_of_quarter"],
            AggregationPeriod.MONTH: ["month_of_quarter", "month_of_year"],
            AggregationPeriod.QUARTER: ["quarter_of_year"]
        }
    
    def _initialize_data_storage(self):
        """Initialize data storage and indexing."""
        self.metric_index: Dict[str, Set[str]] = defaultdict(set)
        self.creator_index: Dict[str, Set[str]] = defaultdict(set)
        self.time_index: Dict[str, Set[str]] = defaultdict(set)
        self.source_index: Dict[DataSource, Set[str]] = defaultdict(set)
        
        self.compression_config = {
            "enable_compression": True,
            "compression_threshold_age_hours": 24,
            "compression_ratio_target": 0.1,
            "archive_threshold_age_days": 90
        }
    
    async def start_aggregation(self):
        """Start data aggregation engine."""
        if self.aggregation_active:
            logger.warning("Data aggregation already active")
            return
        
        self.aggregation_active = True
        logger.info("Starting monitoring data aggregation engine...")
        
        # Start aggregation tasks
        tasks = [
            asyncio.create_task(self._process_data_aggregation()),
            asyncio.create_task(self._calculate_correlations()),
            asyncio.create_task(self._analyze_trends()),
            asyncio.create_task(self._maintain_data_storage()),
            asyncio.create_task(self._generate_insights()),
            asyncio.create_task(self._export_aggregated_data())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in data aggregation: {e}")
            self.aggregation_active = False
            raise
    
    async def stop_aggregation(self):
        """Stop data aggregation engine."""
        self.aggregation_active = False
        logger.info("Monitoring data aggregation engine stopped")
    
    async def ingest_data_point(self, data_point_data: Dict[str, Any]) -> str:
        """Ingest individual data point for aggregation."""
        data_point_id = str(uuid.uuid4())
        
        data_point = DataPoint(
            source=DataSource(data_point_data.get('source')),
            metric_name=data_point_data.get('metric_name'),
            metric_type=MetricType(data_point_data.get('metric_type', 'gauge')),
            value=data_point_data.get('value'),
            timestamp=datetime.fromisoformat(data_point_data.get('timestamp', datetime.now(timezone.utc).isoformat())),
            creator_id=data_point_data.get('creator_id'),
            content_id=data_point_data.get('content_id'),
            metadata=data_point_data.get('metadata', {})
        )
        
        # Add to rolling buffer
        self.data_points.append(data_point)
        
        # Update indexes
        await self._update_indexes(data_point_id, data_point)
        
        logger.debug(f"Ingested data point: {data_point.metric_name} from {data_point.source.value}")
        return data_point_id
    
    async def aggregate_metrics(self, 
                              metric_names: Optional[List[str]] = None,
                              period: AggregationPeriod = AggregationPeriod.HOUR,
                              start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None) -> List[AggregatedMetric]:
        """Aggregate metrics for specified parameters."""
        
        if not end_time:
            end_time = datetime.now(timezone.utc)
        if not start_time:
            start_time = end_time - timedelta(hours=1)
        
        target_metrics = metric_names or self.priority_metrics
        aggregated_results = []
        
        for metric_name in target_metrics:
            # Get data points for metric within time range
            data_points = [
                dp for dp in self.data_points
                if dp.metric_name == metric_name and start_time <= dp.timestamp <= end_time
            ]
            
            if not data_points:
                continue
            
            # Group by source and aggregate
            source_groups = defaultdict(list)
            for dp in data_points:
                source_groups[dp.source].append(dp)
            
            for source, source_data_points in source_groups.items():
                if source_data_points:
                    aggregated_metric = await self._aggregate_data_points(
                        metric_name, source, period, source_data_points, start_time, end_time
                    )
                    aggregated_results.append(aggregated_metric)
        
        return aggregated_results
    
    async def get_creator_consolidated_metrics(self, creator_id: str, period: AggregationPeriod = AggregationPeriod.DAY) -> Dict[str, Any]:
        """Get consolidated metrics for specific creator."""
        creator_data_points = [
            dp for dp in self.data_points
            if dp.creator_id == creator_id
        ]
        
        if not creator_data_points:
            return {"creator_id": creator_id, "status": "no_data"}
        
        # Group by metric name
        metric_groups = defaultdict(list)
        for dp in creator_data_points:
            metric_groups[dp.metric_name].append(dp)
        
        consolidated_metrics = {
            "creator_id": creator_id,
            "period": period.value,
            "metrics": {},
            "summary": {},
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        total_revenue = 0
        total_engagement = 0
        content_count = 0
        
        for metric_name, data_points in metric_groups.items():
            if data_points:
                latest_value = data_points[-1].value
                avg_value = statistics.mean([dp.value for dp in data_points if isinstance(dp.value, (int, float))])
                
                consolidated_metrics["metrics"][metric_name] = {
                    "latest_value": latest_value,
                    "average_value": avg_value,
                    "data_points_count": len(data_points),
                    "trend": await self._calculate_simple_trend(data_points)
                }
                
                # Accumulate summary metrics
                if "revenue" in metric_name.lower():
                    total_revenue += avg_value
                elif "engagement" in metric_name.lower():
                    total_engagement += avg_value
                elif "content" in metric_name.lower():
                    content_count += avg_value
        
        consolidated_metrics["summary"] = {
            "total_revenue": total_revenue,
            "average_engagement": total_engagement,
            "content_count": content_count,
            "performance_score": await self._calculate_creator_performance_score(creator_id)
        }
        
        return consolidated_metrics
    
    async def calculate_cross_domain_correlations(self) -> List[CrossDomainCorrelation]:
        """Calculate cross-domain analytics correlations."""
        correlations = []
        
        for primary_metric, secondary_metric in self.correlation_pairs:
            correlation = await self._calculate_metric_correlation(primary_metric, secondary_metric)
            if correlation:
                correlations.append(correlation)
        
        return correlations
    
    async def analyze_historical_trends(self, 
                                      metric_names: Optional[List[str]] = None,
                                      period: AggregationPeriod = AggregationPeriod.DAY) -> List[TrendAnalysis]:
        """Analyze historical trends for metrics."""
        
        target_metrics = metric_names or self.priority_metrics
        trend_analyses = []
        
        for metric_name in target_metrics:
            trend_analysis = await self._perform_trend_analysis(metric_name, period)
            if trend_analysis:
                trend_analyses.append(trend_analysis)
        
        return trend_analyses
    
    async def _process_data_aggregation(self):
        """Process scheduled data aggregations."""
        while self.aggregation_active:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Process aggregations for different periods
                for period, config in self.aggregation_schedules.items():
                    interval_seconds = config["interval_seconds"]
                    
                    # Check if it's time to aggregate for this period
                    last_aggregation_key = f"last_aggregation_{period.value}"
                    last_aggregation = getattr(self, last_aggregation_key, None)
                    
                    if (not last_aggregation or 
                        (current_time - last_aggregation).total_seconds() >= interval_seconds):
                        
                        await self._perform_scheduled_aggregation(period)
                        setattr(self, last_aggregation_key, current_time)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in data aggregation processing: {e}")
                await asyncio.sleep(300)
    
    async def _calculate_correlations(self):
        """Calculate cross-domain correlations periodically."""
        while self.aggregation_active:
            try:
                correlations = await self.calculate_cross_domain_correlations()
                
                for correlation in correlations:
                    self.correlations[correlation.correlation_id] = correlation
                
                # Clean up old correlations
                cutoff_time = datetime.now(timezone.utc) - timedelta(days=30)
                self.correlations = {
                    k: v for k, v in self.correlations.items()
                    if v.calculated_at > cutoff_time
                }
                
                await asyncio.sleep(3600)  # Calculate every hour
                
            except Exception as e:
                logger.error(f"Error calculating correlations: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_trends(self):
        """Analyze trends periodically."""
        while self.aggregation_active:
            try:
                trend_analyses = await self.analyze_historical_trends()
                
                for trend_analysis in trend_analyses:
                    self.trend_analyses[trend_analysis.metric_name] = trend_analysis
                
                await asyncio.sleep(7200)  # Analyze every 2 hours
                
            except Exception as e:
                logger.error(f"Error analyzing trends: {e}")
                await asyncio.sleep(300)
    
    async def _maintain_data_storage(self):
        """Maintain data storage and perform cleanup."""
        while self.aggregation_active:
            try:
                # Clean up old aggregated metrics
                for metric_name, aggregated_list in self.aggregated_metrics.items():
                    cutoff_time = datetime.now(timezone.utc) - timedelta(days=90)
                    self.aggregated_metrics[metric_name] = [
                        am for am in aggregated_list if am.end_time > cutoff_time
                    ]
                
                # Compress old data if configured
                if self.compression_config.get("enable_compression", False):
                    await self._compress_old_data()
                
                await asyncio.sleep(3600)  # Maintain every hour
                
            except Exception as e:
                logger.error(f"Error maintaining data storage: {e}")
                await asyncio.sleep(300)
    
    async def _generate_insights(self):
        """Generate insights from aggregated data."""
        while self.aggregation_active:
            try:
                insights = {
                    "data_quality": await self._assess_data_quality(),
                    "performance_insights": await self._generate_performance_insights(),
                    "correlation_insights": await self._generate_correlation_insights(),
                    "trend_insights": await self._generate_trend_insights()
                }
                
                logger.info(f"Generated aggregation insights: {json.dumps(insights, default=str)}")
                
                await asyncio.sleep(86400)  # Generate daily
                
            except Exception as e:
                logger.error(f"Error generating insights: {e}")
                await asyncio.sleep(300)
    
    async def _export_aggregated_data(self):
        """Export aggregated data for external systems."""
        while self.aggregation_active:
            try:
                # Export to external analytics systems
                export_data = await self._prepare_export_data()
                
                # In production, send to data warehouse, BI tools, etc.
                logger.info(f"Exported aggregated data: {len(export_data)} records")
                
                await asyncio.sleep(3600)  # Export every hour
                
            except Exception as e:
                logger.error(f"Error exporting aggregated data: {e}")
                await asyncio.sleep(300)
    
    async def _aggregate_data_points(self, 
                                   metric_name: str,
                                   source: DataSource,
                                   period: AggregationPeriod,
                                   data_points: List[DataPoint],
                                   start_time: datetime,
                                   end_time: datetime) -> AggregatedMetric:
        """Aggregate list of data points."""
        
        if not data_points:
            return None
        
        # Determine aggregation method based on metric type
        metric_type = data_points[0].metric_type
        aggregation_methods = self.aggregation_rules.get(metric_type, {})
        method = aggregation_methods.get("default_method", "avg")
        
        # Extract numeric values
        numeric_values = [dp.value for dp in data_points if isinstance(dp.value, (int, float))]
        
        if not numeric_values:
            return None
        
        # Calculate aggregated value based on method
        if method == "sum":
            aggregated_value = sum(numeric_values)
        elif method == "avg":
            aggregated_value = statistics.mean(numeric_values)
        elif method == "min":
            aggregated_value = min(numeric_values)
        elif method == "max":
            aggregated_value = max(numeric_values)
        elif method == "count":
            aggregated_value = len(numeric_values)
        elif method == "rate":
            time_span = (end_time - start_time).total_seconds()
            aggregated_value = sum(numeric_values) / (time_span / 3600) if time_span > 0 else 0  # per hour
        else:
            aggregated_value = statistics.mean(numeric_values)  # default to average
        
        aggregated_metric = AggregatedMetric(
            metric_name=metric_name,
            source=source,
            period=period,
            start_time=start_time,
            end_time=end_time,
            aggregated_value=aggregated_value,
            data_points_count=len(data_points),
            aggregation_method=method,
            metadata={
                "min_value": min(numeric_values),
                "max_value": max(numeric_values),
                "std_dev": statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
            }
        )
        
        return aggregated_metric
    
    async def _calculate_metric_correlation(self, primary_metric: str, secondary_metric: str) -> Optional[CrossDomainCorrelation]:
        """Calculate correlation between two metrics."""
        
        # Get data points for both metrics
        primary_data = [dp for dp in self.data_points if dp.metric_name == primary_metric]
        secondary_data = [dp for dp in self.data_points if dp.metric_name == secondary_metric]
        
        if len(primary_data) < self.correlation_thresholds["minimum_sample_size"] or \
           len(secondary_data) < self.correlation_thresholds["minimum_sample_size"]:
            return None
        
        # Align data points by timestamp (simplified approach)
        primary_values = [dp.value for dp in primary_data if isinstance(dp.value, (int, float))]
        secondary_values = [dp.value for dp in secondary_data if isinstance(dp.value, (int, float))]
        
        if len(primary_values) < 2 or len(secondary_values) < 2:
            return None
        
        # Calculate correlation coefficient (simplified Pearson correlation)
        correlation_coefficient = await self._calculate_pearson_correlation(primary_values, secondary_values)
        
        # Generate insights based on correlation strength
        insights = []
        abs_correlation = abs(correlation_coefficient)
        
        if abs_correlation >= self.correlation_thresholds["strong_correlation"]:
            insights.append(f"Strong {'positive' if correlation_coefficient > 0 else 'negative'} correlation detected")
        elif abs_correlation >= self.correlation_thresholds["moderate_correlation"]:
            insights.append(f"Moderate {'positive' if correlation_coefficient > 0 else 'negative'} correlation detected")
        elif abs_correlation >= self.correlation_thresholds["weak_correlation"]:
            insights.append(f"Weak {'positive' if correlation_coefficient > 0 else 'negative'} correlation detected")
        else:
            insights.append("No significant correlation detected")
        
        correlation = CrossDomainCorrelation(
            correlation_id=str(uuid.uuid4()),
            primary_metric=primary_metric,
            secondary_metric=secondary_metric,
            correlation_coefficient=correlation_coefficient,
            confidence_level=self.correlation_thresholds["confidence_level"],
            sample_size=min(len(primary_values), len(secondary_values)),
            time_period=AggregationPeriod.DAY,
            insights=insights
        )
        
        return correlation
    
    async def _perform_trend_analysis(self, metric_name: str, period: AggregationPeriod) -> Optional[TrendAnalysis]:
        """Perform trend analysis for specific metric."""
        
        # Get historical data for metric
        metric_data = [dp for dp in self.data_points if dp.metric_name == metric_name]
        
        if len(metric_data) < self.trend_detection_config["minimum_data_points"]:
            return None
        
        # Extract values and timestamps
        values = [dp.value for dp in metric_data if isinstance(dp.value, (int, float))]
        timestamps = [dp.timestamp for dp in metric_data if isinstance(dp.value, (int, float))]
        
        if len(values) < self.trend_detection_config["minimum_data_points"]:
            return None
        
        # Calculate trend direction and strength
        trend_direction, trend_strength = await self._calculate_linear_trend(values)
        
        # Detect seasonal patterns
        seasonal_patterns = await self._detect_seasonal_patterns(values, timestamps, period)
        
        # Detect anomalies
        anomalies = await self._detect_anomalies(values, timestamps)
        
        # Generate forecast
        forecasted_values = await self._generate_forecast(values)
        
        # Calculate confidence interval
        confidence_interval = await self._calculate_confidence_interval(values)
        
        trend_analysis = TrendAnalysis(
            metric_name=metric_name,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            seasonal_patterns=seasonal_patterns,
            anomalies=anomalies,
            forecasted_values=forecasted_values,
            analysis_period=period,
            confidence_interval=confidence_interval
        )
        
        return trend_analysis
    
    async def _calculate_linear_trend(self, values: List[float]) -> Tuple[str, float]:
        """Calculate linear trend direction and strength."""
        if len(values) < 2:
            return "stable", 0.0
        
        # Simple linear regression
        n = len(values)
        x = list(range(n))
        
        # Calculate slope
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable", 0.0
        
        slope = numerator / denominator
        
        # Determine direction and strength
        threshold = self.trend_detection_config["trend_threshold"]
        
        if slope > threshold:
            direction = "increasing"
        elif slope < -threshold:
            direction = "decreasing"
        else:
            direction = "stable"
        
        # Strength is normalized absolute slope
        max_value = max(values) if values else 1
        strength = min(1.0, abs(slope) / max_value) if max_value > 0 else 0.0
        
        return direction, strength
    
    async def _calculate_moving_average_trend(self, values: List[float]) -> Tuple[str, float]:
        """Calculate moving average trend."""
        window_size = min(5, len(values) // 2)
        if window_size < 2:
            return "stable", 0.0
        
        moving_averages = []
        for i in range(window_size, len(values)):
            avg = statistics.mean(values[i-window_size:i])
            moving_averages.append(avg)
        
        return await self._calculate_linear_trend(moving_averages)
    
    async def _calculate_exponential_smoothing_trend(self, values: List[float]) -> Tuple[str, float]:
        """Calculate exponential smoothing trend."""
        if len(values) < 2:
            return "stable", 0.0
        
        alpha = 0.3  # Smoothing factor
        smoothed_values = [values[0]]
        
        for i in range(1, len(values)):
            smoothed_value = alpha * values[i] + (1 - alpha) * smoothed_values[-1]
            smoothed_values.append(smoothed_value)
        
        return await self._calculate_linear_trend(smoothed_values)
    
    async def _calculate_seasonal_trend(self, values: List[float]) -> Tuple[str, float]:
        """Calculate seasonal decomposition trend."""
        # Simplified seasonal analysis
        if len(values) < 12:  # Need at least 12 data points for seasonal analysis
            return await self._calculate_linear_trend(values)
        
        # Calculate seasonal component (simplified)
        season_length = min(12, len(values) // 3)
        seasonal_averages = []
        
        for i in range(season_length):
            season_values = values[i::season_length]
            if season_values:
                seasonal_averages.append(statistics.mean(season_values))
        
        return await self._calculate_linear_trend(seasonal_averages)
    
    async def _detect_seasonal_patterns(self, values: List[float], timestamps: List[datetime], period: AggregationPeriod) -> Dict[str, float]:
        """Detect seasonal patterns in data."""
        patterns = {}
        
        if period == AggregationPeriod.HOUR and len(timestamps) >= 24:
            # Hour of day patterns
            hourly_avg = defaultdict(list)
            for value, timestamp in zip(values, timestamps):
                hourly_avg[timestamp.hour].append(value)
            
            patterns["hour_of_day"] = statistics.stdev([
                statistics.mean(hour_values) for hour_values in hourly_avg.values()
            ]) if len(hourly_avg) > 1 else 0.0
        
        elif period == AggregationPeriod.DAY and len(timestamps) >= 7:
            # Day of week patterns
            daily_avg = defaultdict(list)
            for value, timestamp in zip(values, timestamps):
                daily_avg[timestamp.weekday()].append(value)
            
            patterns["day_of_week"] = statistics.stdev([
                statistics.mean(day_values) for day_values in daily_avg.values()
            ]) if len(daily_avg) > 1 else 0.0
        
        return patterns
    
    async def _detect_anomalies(self, values: List[float], timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Detect anomalies in data."""
        if len(values) < 10:
            return []
        
        anomalies = []
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        threshold = self.trend_detection_config["anomaly_detection_std"]
        
        for i, (value, timestamp) in enumerate(zip(values, timestamps)):
            if std_dev > 0 and abs(value - mean_value) > threshold * std_dev:
                anomalies.append({
                    "timestamp": timestamp.isoformat(),
                    "value": value,
                    "deviation": abs(value - mean_value) / std_dev,
                    "type": "outlier"
                })
        
        return anomalies
    
    async def _generate_forecast(self, values: List[float]) -> List[float]:
        """Generate simple forecast for values."""
        if len(values) < 3:
            return []
        
        # Simple linear extrapolation
        recent_values = values[-5:]  # Use last 5 values
        trend_direction, trend_strength = await self._calculate_linear_trend(recent_values)
        
        forecast_periods = self.trend_detection_config["forecast_periods"]
        last_value = values[-1]
        
        # Calculate trend increment
        if len(recent_values) >= 2:
            increment = (recent_values[-1] - recent_values[0]) / len(recent_values)
        else:
            increment = 0
        
        forecasted_values = []
        for i in range(1, forecast_periods + 1):
            forecasted_value = last_value + (increment * i)
            forecasted_values.append(forecasted_value)
        
        return forecasted_values
    
    async def _calculate_confidence_interval(self, values: List[float]) -> Tuple[float, float]:
        """Calculate confidence interval for values."""
        if len(values) < 2:
            return (0.0, 0.0)
        
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        # 95% confidence interval (approximate)
        margin_of_error = 1.96 * std_dev / (len(values) ** 0.5)
        
        return (mean_value - margin_of_error, mean_value + margin_of_error)
    
    async def _calculate_pearson_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0
        
        # Take minimum length for alignment
        min_length = min(len(x_values), len(y_values))
        x_values = x_values[:min_length]
        y_values = y_values[:min_length]
        
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        
        x_variance = sum((x - x_mean) ** 2 for x in x_values)
        y_variance = sum((y - y_mean) ** 2 for y in y_values)
        
        denominator = (x_variance * y_variance) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    async def _calculate_simple_trend(self, data_points: List[DataPoint]) -> str:
        """Calculate simple trend for data points."""
        if len(data_points) < 2:
            return "stable"
        
        values = [dp.value for dp in data_points if isinstance(dp.value, (int, float))]
        if len(values) < 2:
            return "stable"
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        if not first_half or not second_half:
            return "stable"
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        change_percent = (second_avg - first_avg) / first_avg if first_avg != 0 else 0
        
        if change_percent > 0.05:  # 5% increase
            return "increasing"
        elif change_percent < -0.05:  # 5% decrease
            return "decreasing"
        else:
            return "stable"
    
    async def _calculate_creator_performance_score(self, creator_id: str) -> float:
        """Calculate overall performance score for creator."""
        creator_data = [dp for dp in self.data_points if dp.creator_id == creator_id]
        
        if not creator_data:
            return 0.0
        
        # Weight different metrics for performance score
        score_weights = {
            "revenue": 0.3,
            "engagement": 0.25,
            "content_quality": 0.2,
            "collaboration": 0.15,
            "seo": 0.1
        }
        
        metric_scores = {}
        for metric_name, weight in score_weights.items():
            matching_data = [dp for dp in creator_data if metric_name in dp.metric_name.lower()]
            if matching_data:
                values = [dp.value for dp in matching_data if isinstance(dp.value, (int, float))]
                if values:
                    # Normalize to 0-100 scale (simplified)
                    normalized_score = min(100, max(0, statistics.mean(values)))
                    metric_scores[metric_name] = normalized_score * weight
        
        return sum(metric_scores.values())
    
    async def _update_indexes(self, data_point_id: str, data_point: DataPoint):
        """Update data indexes for efficient querying."""
        self.metric_index[data_point.metric_name].add(data_point_id)
        
        if data_point.creator_id:
            self.creator_index[data_point.creator_id].add(data_point_id)
        
        time_key = data_point.timestamp.strftime("%Y-%m-%d-%H")
        self.time_index[time_key].add(data_point_id)
        
        self.source_index[data_point.source].add(data_point_id)
    
    async def _perform_scheduled_aggregation(self, period: AggregationPeriod):
        """Perform scheduled aggregation for specific period."""
        end_time = datetime.now(timezone.utc)
        
        if period == AggregationPeriod.MINUTE:
            start_time = end_time - timedelta(minutes=1)
        elif period == AggregationPeriod.HOUR:
            start_time = end_time - timedelta(hours=1)
        elif period == AggregationPeriod.DAY:
            start_time = end_time - timedelta(days=1)
        else:
            start_time = end_time - timedelta(hours=1)  # Default
        
        aggregated_metrics = await self.aggregate_metrics(period=period, start_time=start_time, end_time=end_time)
        
        # Store aggregated metrics
        for metric in aggregated_metrics:
            self.aggregated_metrics[metric.metric_name].append(metric)
        
        logger.info(f"Completed scheduled aggregation for {period.value}: {len(aggregated_metrics)} metrics")
    
    async def _compress_old_data(self):
        """Compress old data to save storage."""
        # In production, implement data compression
        logger.debug("Data compression completed (simulated)")
    
    async def _assess_data_quality(self) -> Dict[str, Any]:
        """Assess data quality metrics."""
        total_data_points = len(self.data_points)
        
        if total_data_points == 0:
            return {"status": "no_data"}
        
        # Calculate completeness
        complete_data_points = len([dp for dp in self.data_points if dp.value is not None])
        completeness = complete_data_points / total_data_points
        
        # Calculate freshness
        now = datetime.now(timezone.utc)
        recent_data_points = len([dp for dp in self.data_points if (now - dp.timestamp).total_seconds() < 3600])
        freshness = recent_data_points / total_data_points
        
        return {
            "total_data_points": total_data_points,
            "completeness": completeness,
            "freshness": freshness,
            "sources_active": len(set(dp.source for dp in self.data_points)),
            "metrics_tracked": len(set(dp.metric_name for dp in self.data_points))
        }
    
    async def _generate_performance_insights(self) -> List[str]:
        """Generate performance insights."""
        insights = []
        
        # Analyze aggregation performance
        processing_rate = len(self.data_points) / max(1, (datetime.now(timezone.utc) - getattr(self, '_start_time', datetime.now(timezone.utc))).total_seconds())
        
        if processing_rate > 100:
            insights.append("High data ingestion rate detected")
        elif processing_rate < 10:
            insights.append("Low data ingestion rate - consider increasing monitoring frequency")
        
        return insights
    
    async def _generate_correlation_insights(self) -> List[str]:
        """Generate correlation insights."""
        insights = []
        
        strong_correlations = [c for c in self.correlations.values() if abs(c.correlation_coefficient) >= 0.7]
        
        if strong_correlations:
            insights.append(f"Found {len(strong_correlations)} strong correlations between metrics")
        
        return insights
    
    async def _generate_trend_insights(self) -> List[str]:
        """Generate trend insights."""
        insights = []
        
        increasing_trends = [t for t in self.trend_analyses.values() if t.trend_direction == "increasing"]
        decreasing_trends = [t for t in self.trend_analyses.values() if t.trend_direction == "decreasing"]
        
        if increasing_trends:
            insights.append(f"{len(increasing_trends)} metrics showing positive trends")
        
        if decreasing_trends:
            insights.append(f"{len(decreasing_trends)} metrics showing negative trends")
        
        return insights
    
    async def _prepare_export_data(self) -> List[Dict[str, Any]]:
        """Prepare aggregated data for export."""
        export_data = []
        
        for metric_name, aggregated_list in self.aggregated_metrics.items():
            for aggregated_metric in aggregated_list[-10:]:  # Export last 10 records
                export_data.append(asdict(aggregated_metric))
        
        return export_data
    
    async def get_aggregation_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive aggregation monitoring dashboard data."""
        data_quality = await self._assess_data_quality()
        
        return {
            "data_ingestion": {
                "total_data_points": len(self.data_points),
                "data_sources_active": len(set(dp.source for dp in self.data_points)),
                "metrics_tracked": len(set(dp.metric_name for dp in self.data_points)),
                "creators_monitored": len(set(dp.creator_id for dp in self.data_points if dp.creator_id))
            },
            "aggregation_status": {
                "metrics_aggregated": len(self.aggregated_metrics),
                "correlations_calculated": len(self.correlations),
                "trends_analyzed": len(self.trend_analyses)
            },
            "data_quality": data_quality,
            "recent_insights": {
                "performance": await self._generate_performance_insights(),
                "correlations": await self._generate_correlation_insights(),
                "trends": await self._generate_trend_insights()
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on aggregation systems."""
        return {
            "status": "healthy" if self.aggregation_active else "inactive",
            "data_points_buffer_size": len(self.data_points),
            "aggregated_metrics_count": sum(len(metrics) for metrics in self.aggregated_metrics.values()),
            "correlations_tracked": len(self.correlations),
            "trends_analyzed": len(self.trend_analyses),
            "last_check": datetime.now(timezone.utc).isoformat()
        }

# Global aggregation engine instance
monitoring_data_aggregation_engine = MonitoringDataAggregationEngine()

async def main():
    """Main function for testing data aggregation."""
    engine = MonitoringDataAggregationEngine()
    
    # Test data ingestion
    data_points = [
        {
            'source': 'creator_economy',
            'metric_name': 'creator_revenue',
            'metric_type': 'currency',
            'value': 1500.50,
            'creator_id': 'creator_1',
            'timestamp': datetime.now(timezone.utc).isoformat()
        },
        {
            'source': 'seo_performance',
            'metric_name': 'seo_performance_score',
            'metric_type': 'percentage',
            'value': 85.5,
            'creator_id': 'creator_1',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    ]
    
    for data_point in data_points:
        await engine.ingest_data_point(data_point)
    
    # Test aggregation
    aggregated_metrics = await engine.aggregate_metrics(['creator_revenue'])
    print(f"Aggregated metrics: {len(aggregated_metrics)}")
    
    # Test creator consolidation
    creator_metrics = await engine.get_creator_consolidated_metrics('creator_1')
    print(f"Creator metrics: {json.dumps(creator_metrics, indent=2, default=str)}")
    
    # Get dashboard data
    dashboard = await engine.get_aggregation_dashboard_data()
    print(f"Dashboard data: {json.dumps(dashboard, indent=2, default=str)}")
    
    # Health check
    health = await engine.health_check()
    print(f"Health check: {json.dumps(health, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())