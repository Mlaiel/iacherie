"""Analytics Serializer Module
===========================

Specialized serialization for analytics data and business intelligence.
Optimized for performance metrics, engagement analytics, and reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ LEGAL WARNING - INTELLECTUAL PROPERTY PROTECTION:
This code, concept, and intellectual property belong exclusively to Fahed Mlaiel (mlaiel@live.de). 
Any unauthorized copying, distribution, modification, or commercial use is STRICTLY PROHIBITED 
and will result in immediate legal action under German and International Copyright Law.

ZERO TOLERANCE POLICY: Anyone attempting to steal, copy, or misappropriate this code or concept 
will face severe legal consequences including but not limited to criminal charges, civil litigation, 
and substantial financial damages.

AUTHORIZED USE ONLY: Contact mlaiel@live.de for official licensing agreements.

Expertise combinée:
- Lead Developer IA: Architecture d'analytics prédictive intelligente
- Backend Senior: Infrastructure robuste pour big data analytics
- ML Engineer: Algorithmes d'analyse et modèles prédictifs
- DBA Expert: Optimisation de requêtes analytics complexes
- Sécurité: Protection des données d'analytics sensibles
- Microservices: Architecture distribuée pour analytics en temps réel
- Audio/Vidéo: Analytics multimédia avancées
- DevOps: Pipelines de données et monitoring analytics
- IA Prompt Engineer: Génération de rapports automatisés
"""
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
import numpy as np
from collections import defaultdict
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class AnalyticsType(Enum):
    """Types of analytics data."""    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    AUDIENCE = "audience"
    REVENUE = "revenue"
    CONTENT = "content"
    PLATFORM = "platform"
    PROTECTION = "protection"
    CONVERSION = "conversion"
    TREND = "trend"
    PREDICTIVE = "predictive"

class MetricType(Enum):
    """Types of metrics."""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    PERCENTAGE = "percentage"
    RATE = "rate"
    RATIO = "ratio"
    SCORE = "score"
    INDEX = "index"

class TimeGranularity(Enum):
    """Time granularity for analytics."""    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class AggregationType(Enum):
    """Aggregation methods."""    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    VARIANCE = "variance"
    STANDARD_DEVIATION = "standard_deviation"

@dataclass
class MetricValue:
    """Individual metric value with metadata."""    value: Union[int, float]
    timestamp: datetime
    confidence: float = 1.0
    source: str = "system"
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricSeries:
    """Time series of metric values."""    metric_name: str
    metric_type: MetricType
    values: List[MetricValue] = field(default_factory=list)
    unit: str = ""
    description: str = ""
    aggregation_method: AggregationType = AggregationType.SUM

@dataclass
class AnalyticsSnapshot:
    """Point-in-time analytics snapshot."""    snapshot_id: str
    timestamp: datetime
    platform: str
    content_id: str
    metrics: Dict[str, Union[int, float]] = field(default_factory=dict)
    dimensions: Dict[str, str] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceBenchmark:
    """Performance benchmark data."""    benchmark_id: str
    category: str
    metric_name: str
    baseline_value: float
    target_value: float
    current_value: float
    percentile_rank: Optional[float] = None
    industry_average: Optional[float] = None
    improvement_rate: Optional[float] = None

class AnalyticsData(BaseModel):
    """    Comprehensive analytics data model.
    
    Represents analytics metrics, performance data, and business intelligence
    for content optimization in the IA-Influencer-Agent platform.
    """    
    # Basic identification
    analytics_id: str = Field(..., description="Unique analytics identifier")
    report_id: str = Field(..., description="Analytics report identifier")
    analytics_type: AnalyticsType = Field(..., description="Type of analytics")
    granularity: TimeGranularity = Field(..., description="Time granularity")
    
    # Content and source information
    content_id: str = Field(..., description="Associated content identifier")
    creator_id: str = Field(..., description="Content creator identifier")
    platform_name: str = Field(..., description="Platform name")
    content_type: str = Field(..., description="Content type")
    
    # Time period
    period_start: datetime = Field(..., description="Analytics period start")
    period_end: datetime = Field(..., description="Analytics period end")
    timezone: str = Field(default="UTC", description="Timezone for data")
    
    # Core metrics
    views: int = Field(default=0, description="Total views")
    unique_views: int = Field(default=0, description="Unique views")
    likes: int = Field(default=0, description="Likes count")
    dislikes: int = Field(default=0, description="Dislikes count")
    comments: int = Field(default=0, description="Comments count")
    shares: int = Field(default=0, description="Shares count")
    downloads: int = Field(default=0, description="Downloads count")
    saves: int = Field(default=0, description="Saves count")
    
    # Engagement metrics
    engagement_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall engagement rate")
    click_through_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Click-through rate")
    conversion_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Conversion rate")
    retention_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Audience retention rate")
    bounce_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Bounce rate")
    
    # Watch/listen time metrics
    total_watch_time_minutes: float = Field(default=0.0, description="Total watch time in minutes")
    average_watch_time_minutes: float = Field(default=0.0, description="Average watch time")
    watch_time_percentage: float = Field(default=0.0, ge=0.0, le=1.0, description="Percentage watched")
    replay_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Replay rate")
    
    # Audience demographics
    audience_age_groups: Dict[str, int] = Field(default_factory=dict, description="Age group distribution")
    audience_gender: Dict[str, int] = Field(default_factory=dict, description="Gender distribution")
    audience_locations: Dict[str, int] = Field(default_factory=dict, description="Geographic distribution")
    audience_devices: Dict[str, int] = Field(default_factory=dict, description="Device distribution")
    audience_sources: Dict[str, int] = Field(default_factory=dict, description="Traffic sources")
    
    # Revenue metrics
    revenue_total: float = Field(default=0.0, description="Total revenue")
    revenue_currency: str = Field(default="EUR", description="Revenue currency")
    revenue_per_view: float = Field(default=0.0, description="Revenue per view")
    revenue_per_engagement: float = Field(default=0.0, description="Revenue per engagement")
    monetization_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Monetization rate")
    
    # Performance scores
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Content quality score")
    viral_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Viral potential score")
    seo_score: float = Field(default=0.0, ge=0.0, le=1.0, description="SEO optimization score")
    algorithm_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Platform algorithm score")
    
    # Protection metrics
    violations_detected: int = Field(default=0, description="Copyright violations detected")
    protection_coverage: float = Field(default=0.0, ge=0.0, le=1.0, description="Protection coverage")
    false_positive_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="False positive rate")
    enforcement_success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Enforcement success rate")
    
    # Trend analysis
    growth_rate_daily: float = Field(default=0.0, description="Daily growth rate")
    growth_rate_weekly: float = Field(default=0.0, description="Weekly growth rate")
    growth_rate_monthly: float = Field(default=0.0, description="Monthly growth rate")
    trend_direction: str = Field(default="stable", description="Trend direction")
    seasonality_factor: float = Field(default=1.0, description="Seasonality factor")
    
    # Comparative analysis
    previous_period_comparison: Dict[str, float] = Field(default_factory=dict, description="Previous period comparison")
    industry_benchmark: Dict[str, float] = Field(default_factory=dict, description="Industry benchmarks")
    competitor_comparison: Dict[str, Any] = Field(default_factory=dict, description="Competitor comparison")
    
    # Time series data
    metric_series: List[MetricSeries] = Field(default_factory=list, description="Time series metrics")
    snapshots: List[AnalyticsSnapshot] = Field(default_factory=list, description="Analytics snapshots")
    benchmarks: List[PerformanceBenchmark] = Field(default_factory=list, description="Performance benchmarks")
    
    # Data quality
    data_completeness: float = Field(default=1.0, ge=0.0, le=1.0, description="Data completeness score")
    data_accuracy: float = Field(default=1.0, ge=0.0, le=1.0, description="Data accuracy score")
    sample_size: int = Field(default=0, description="Sample size for analytics")
    confidence_interval: float = Field(default=0.95, ge=0.0, le=1.0, description="Statistical confidence")
    
    # Processing metadata
    calculated_at: datetime = Field(default_factory=datetime.now, description="Calculation timestamp")
    calculation_method: str = Field(default="automatic", description="Calculation method")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used")
    processing_time_ms: float = Field(default=0.0, description="Processing time in milliseconds")
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list, description="Analytics tags")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    custom_metrics: Dict[str, Any] = Field(default_factory=dict, description="Custom metrics")
    
    @validator('analytics_type', pre=True)
    def validate_analytics_type(cls, v):
        if isinstance(v, str):
            return AnalyticsType(v.lower())
        return v
    
    @validator('granularity', pre=True)
    def validate_granularity(cls, v):
        if isinstance(v, str):
            return TimeGranularity(v.lower())
        return v
    
    @validator('period_end')
    def validate_period_end(cls, v, values):
        if 'period_start' in values and v <= values['period_start']:
            raise ValueError("Period end must be after period start")
        return v

class AnalyticsSerializer:
    """    Advanced analytics data serialization system.
    
    Handles efficient serialization and deserialization of analytics data,
    performance metrics, and business intelligence for content optimization.
    """    
    def __init__(self):
        """Initialize analytics serializer."""        self.time_series_compression_threshold = 1000  # Compress if > 1000 data points
        self.decimal_precision = 6  # Precision for floating point values
        
        logger.info("Analytics serializer initialized")
    
    def serialize_analytics(
        self,
        analytics: AnalyticsData,
        include_time_series: bool = True,
        include_snapshots: bool = True,
        compress_time_series: bool = True
    ) -> Dict[str, Any]:
        """        Serialize analytics data to dictionary format.
        
        Args:
            analytics: Analytics data to serialize
            include_time_series: Whether to include time series data
            include_snapshots: Whether to include snapshots
            compress_time_series: Whether to compress large time series
            
        Returns:
            Serialized analytics dictionary
        """        try:
            # Convert to dictionary
            data = analytics.dict()
            
            # Handle datetime conversions
            data['period_start'] = analytics.period_start.isoformat()
            data['period_end'] = analytics.period_end.isoformat()
            data['calculated_at'] = analytics.calculated_at.isoformat()
            
            # Round floating point values
            self._round_numeric_values(data)
            
            # Serialize time series data
            if include_time_series and analytics.metric_series:
                data['metric_series'] = [
                    self._serialize_metric_series(series, compress_time_series)
                    for series in analytics.metric_series
                ]
            elif not include_time_series:
                data.pop('metric_series', None)
            
            # Serialize snapshots
            if include_snapshots and analytics.snapshots:
                data['snapshots'] = [
                    self._serialize_analytics_snapshot(snapshot)
                    for snapshot in analytics.snapshots
                ]
            elif not include_snapshots:
                data.pop('snapshots', None)
            
            # Serialize benchmarks
            if analytics.benchmarks:
                data['benchmarks'] = [
                    self._serialize_performance_benchmark(benchmark)
                    for benchmark in analytics.benchmarks
                ]
            
            # Convert enums
            data['analytics_type'] = analytics.analytics_type.value
            data['granularity'] = analytics.granularity.value
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'includes_time_series': include_time_series,
                'includes_snapshots': include_snapshots,
                'time_series_compressed': compress_time_series,
                'analytics_type': analytics.analytics_type.value,
                'decimal_precision': self.decimal_precision
            }
            
            logger.debug(f"Serialized analytics {analytics.analytics_id}")
            return data
            
        except Exception as e:
            logger.error(f"Analytics serialization failed: {e}")
            raise
    
    def deserialize_analytics(
        self,
        data: Dict[str, Any]
    ) -> AnalyticsData:
        """        Deserialize analytics data from dictionary format.
        
        Args:
            data: Serialized analytics dictionary
            
        Returns:
            Deserialized AnalyticsData object
        """        try:
            # Handle datetime conversions
            datetime_fields = ['period_start', 'period_end', 'calculated_at']
            
            for field in datetime_fields:
                if isinstance(data.get(field), str):
                    data[field] = datetime.fromisoformat(data[field])
            
            # Deserialize time series data
            if 'metric_series' in data and data['metric_series']:
                data['metric_series'] = [
                    self._deserialize_metric_series(series_data)
                    for series_data in data['metric_series']
                ]
            
            # Deserialize snapshots
            if 'snapshots' in data and data['snapshots']:
                data['snapshots'] = [
                    self._deserialize_analytics_snapshot(snapshot_data)
                    for snapshot_data in data['snapshots']
                ]
            
            # Deserialize benchmarks
            if 'benchmarks' in data and data['benchmarks']:
                data['benchmarks'] = [
                    self._deserialize_performance_benchmark(benchmark_data)
                    for benchmark_data in data['benchmarks']
                ]
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            
            # Create AnalyticsData object
            analytics = AnalyticsData(**data)
            
            logger.debug(f"Deserialized analytics {analytics.analytics_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics deserialization failed: {e}")
            raise
    
    def serialize_analytics_batch(
        self,
        analytics_list: List[AnalyticsData],
        compact_mode: bool = True
    ) -> List[Dict[str, Any]]:
        """Serialize multiple analytics records efficiently."""        try:
            serialized_list = []
            
            for analytics in analytics_list:
                serialized = self.serialize_analytics(
                    analytics,
                    include_time_series=not compact_mode,
                    include_snapshots=not compact_mode,
                    compress_time_series=compact_mode
                )
                serialized_list.append(serialized)
            
            logger.info(f"Serialized {len(analytics_list)} analytics records")
            return serialized_list
            
        except Exception as e:
            logger.error(f"Analytics batch serialization failed: {e}")
            raise
    
    def deserialize_analytics_batch(
        self,
        data_list: List[Dict[str, Any]]
    ) -> List[AnalyticsData]:
        """Deserialize multiple analytics records efficiently."""        try:
            analytics_list = []
            
            for data in data_list:
                analytics = self.deserialize_analytics(data)
                analytics_list.append(analytics)
            
            logger.info(f"Deserialized {len(data_list)} analytics records")
            return analytics_list
            
        except Exception as e:
            logger.error(f"Analytics batch deserialization failed: {e}")
            raise
    
    def _serialize_metric_series(
        self,
        series: MetricSeries,
        compress: bool = True
    ) -> Dict[str, Any]:
        """Serialize metric series."""        try:
            data = {
                'metric_name': series.metric_name,
                'metric_type': series.metric_type.value,
                'unit': series.unit,
                'description': series.description,
                'aggregation_method': series.aggregation_method.value
            }
            
            # Serialize values
            if len(series.values) > self.time_series_compression_threshold and compress:
                data['values'] = self._compress_metric_values(series.values)
                data['_values_compressed'] = True
            else:
                data['values'] = [
                    self._serialize_metric_value(value)
                    for value in series.values
                ]
                data['_values_compressed'] = False
            
            return data
            
        except Exception as e:
            logger.error(f"Metric series serialization failed: {e}")
            raise
    
    def _deserialize_metric_series(
        self,
        data: Dict[str, Any]
    ) -> MetricSeries:
        """Deserialize metric series."""        try:
            # Handle compressed values
            if data.get('_values_compressed', False):
                values = self._decompress_metric_values(data['values'])
            else:
                values = [
                    self._deserialize_metric_value(value_data)
                    for value_data in data['values']
                ]
            
            # Handle enum conversions
            metric_type = MetricType(data['metric_type'])
            aggregation_method = AggregationType(data['aggregation_method'])
            
            # Remove compression metadata
            data.pop('_values_compressed', None)
            
            return MetricSeries(
                metric_name=data['metric_name'],
                metric_type=metric_type,
                values=values,
                unit=data['unit'],
                description=data['description'],
                aggregation_method=aggregation_method
            )
            
        except Exception as e:
            logger.error(f"Metric series deserialization failed: {e}")
            raise
    
    def _serialize_metric_value(self, value: MetricValue) -> Dict[str, Any]:
        """Serialize metric value."""        return {
            'value': round(value.value, self.decimal_precision),
            'timestamp': value.timestamp.isoformat(),
            'confidence': round(value.confidence, self.decimal_precision),
            'source': value.source,
            'tags': value.tags,
            'metadata': value.metadata
        }
    
    def _deserialize_metric_value(self, data: Dict[str, Any]) -> MetricValue:
        """Deserialize metric value."""        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return MetricValue(**data)
    
    def _serialize_analytics_snapshot(self, snapshot: AnalyticsSnapshot) -> Dict[str, Any]:
        """Serialize analytics snapshot."""        data = {
            'snapshot_id': snapshot.snapshot_id,
            'timestamp': snapshot.timestamp.isoformat(),
            'platform': snapshot.platform,
            'content_id': snapshot.content_id,
            'metrics': snapshot.metrics,
            'dimensions': snapshot.dimensions,
            'context': snapshot.context
        }
        
        # Round metric values
        for key, value in data['metrics'].items():
            if isinstance(value, float):
                data['metrics'][key] = round(value, self.decimal_precision)
        
        return data
    
    def _deserialize_analytics_snapshot(self, data: Dict[str, Any]) -> AnalyticsSnapshot:
        """Deserialize analytics snapshot."""        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return AnalyticsSnapshot(**data)
    
    def _serialize_performance_benchmark(self, benchmark: PerformanceBenchmark) -> Dict[str, Any]:
        """Serialize performance benchmark."""        return {
            'benchmark_id': benchmark.benchmark_id,
            'category': benchmark.category,
            'metric_name': benchmark.metric_name,
            'baseline_value': round(benchmark.baseline_value, self.decimal_precision),
            'target_value': round(benchmark.target_value, self.decimal_precision),
            'current_value': round(benchmark.current_value, self.decimal_precision),
            'percentile_rank': round(benchmark.percentile_rank, self.decimal_precision) if benchmark.percentile_rank else None,
            'industry_average': round(benchmark.industry_average, self.decimal_precision) if benchmark.industry_average else None,
            'improvement_rate': round(benchmark.improvement_rate, self.decimal_precision) if benchmark.improvement_rate else None
        }
    
    def _deserialize_performance_benchmark(self, data: Dict[str, Any]) -> PerformanceBenchmark:
        """Deserialize performance benchmark."""        return PerformanceBenchmark(**data)
    
    def _compress_metric_values(self, values: List[MetricValue]) -> str:
        """Compress metric values using sampling and encoding."""        try:
            # Sample data points if too many
            if len(values) > self.time_series_compression_threshold:
                step = len(values) // self.time_series_compression_threshold
                sampled_values = values[::step]
            else:
                sampled_values = values
            
            # Convert to compressed format
            compressed_data = []
            for value in sampled_values:
                compressed_data.append({
                    'v': round(value.value, self.decimal_precision),
                    't': int(value.timestamp.timestamp()),
                    'c': round(value.confidence, 2),
                    's': value.source
                })
            
            # Encode as JSON string
            import json
            return json.dumps(compressed_data)
            
        except Exception as e:
            logger.error(f"Metric values compression failed: {e}")
            # Return uncompressed if compression fails
            return [self._serialize_metric_value(v) for v in values]
    
    def _decompress_metric_values(self, compressed_data: str) -> List[MetricValue]:
        """Decompress metric values."""        try:
            import json
            
            if isinstance(compressed_data, str):
                data = json.loads(compressed_data)
            else:
                data = compressed_data
            
            values = []
            for item in data:
                if isinstance(item, dict) and 'v' in item and 't' in item:
                    # Compressed format
                    value = MetricValue(
                        value=item['v'],
                        timestamp=datetime.fromtimestamp(item['t'], tz=timezone.utc),
                        confidence=item.get('c', 1.0),
                        source=item.get('s', 'system')
                    )
                    values.append(value)
                else:
                    # Fallback to full format
                    values.append(self._deserialize_metric_value(item))
            
            return values
            
        except Exception as e:
            logger.error(f"Metric values decompression failed: {e}")
            return []
    
    def _round_numeric_values(self, data: Dict[str, Any], max_depth: int = 3) -> None:
        """Round numeric values in nested dictionary."""        if max_depth <= 0:
            return
        
        for key, value in data.items():
            if isinstance(value, float):
                data[key] = round(value, self.decimal_precision)
            elif isinstance(value, dict):
                self._round_numeric_values(value, max_depth - 1)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                for item in value:
                    if isinstance(item, dict):
                        self._round_numeric_values(item, max_depth - 1)
    
    def calculate_analytics_summary(
        self,
        analytics: AnalyticsData
    ) -> Dict[str, Any]:
        """Calculate summary statistics for analytics data."""        try:
            period_duration = (analytics.period_end - analytics.period_start).days + 1
            
            summary = {
                'analytics_id': analytics.analytics_id,
                'analytics_type': analytics.analytics_type.value,
                'platform_name': analytics.platform_name,
                'content_type': analytics.content_type,
                'period_duration_days': period_duration,
                'data_quality': {
                    'completeness': analytics.data_completeness,
                    'accuracy': analytics.data_accuracy,
                    'sample_size': analytics.sample_size,
                    'confidence_interval': analytics.confidence_interval
                },
                'engagement_summary': {
                    'total_views': analytics.views,
                    'unique_views': analytics.unique_views,
                    'engagement_rate': analytics.engagement_rate,
                    'total_interactions': analytics.likes + analytics.comments + analytics.shares,
                    'watch_time_minutes': analytics.total_watch_time_minutes,
                    'retention_rate': analytics.retention_rate
                },
                'performance_scores': {
                    'quality_score': analytics.quality_score,
                    'viral_score': analytics.viral_score,
                    'seo_score': analytics.seo_score,
                    'algorithm_score': analytics.algorithm_score
                },
                'revenue_summary': {
                    'total_revenue': analytics.revenue_total,
                    'currency': analytics.revenue_currency,
                    'revenue_per_view': analytics.revenue_per_view,
                    'monetization_rate': analytics.monetization_rate
                },
                'protection_summary': {
                    'violations_detected': analytics.violations_detected,
                    'protection_coverage': analytics.protection_coverage,
                    'enforcement_success_rate': analytics.enforcement_success_rate
                },
                'growth_trends': {
                    'daily_growth': analytics.growth_rate_daily,
                    'weekly_growth': analytics.growth_rate_weekly,
                    'monthly_growth': analytics.growth_rate_monthly,
                    'trend_direction': analytics.trend_direction
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Analytics summary calculation failed: {e}")
            return {'error': str(e)}
    
    def aggregate_analytics_metrics(
        self,
        analytics_list: List[AnalyticsData],
        groupby: str = "platform_name"
    ) -> Dict[str, Any]:
        """Aggregate metrics across multiple analytics records."""        try:
            if not analytics_list:
                return {}
            
            # Group analytics by specified field
            groups = defaultdict(list)
            for analytics in analytics_list:
                group_key = getattr(analytics, groupby, "unknown")
                groups[group_key].append(analytics)
            
            aggregated = {}
            
            for group_key, group_analytics in groups.items():
                # Calculate aggregated metrics
                total_views = sum(a.views for a in group_analytics)
                total_revenue = sum(a.revenue_total for a in group_analytics)
                avg_engagement = statistics.mean([a.engagement_rate for a in group_analytics])
                avg_quality = statistics.mean([a.quality_score for a in group_analytics])
                
                aggregated[group_key] = {
                    'count': len(group_analytics),
                    'total_views': total_views,
                    'total_revenue': total_revenue,
                    'average_engagement_rate': round(avg_engagement, 4),
                    'average_quality_score': round(avg_quality, 4),
                    'total_violations': sum(a.violations_detected for a in group_analytics),
                    'period_range': {
                        'start': min(a.period_start for a in group_analytics).isoformat(),
                        'end': max(a.period_end for a in group_analytics).isoformat()
                    }
                }
            
            return {
                'grouped_by': groupby,
                'groups': aggregated,
                'total_records': len(analytics_list),
                'aggregated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Analytics metrics aggregation failed: {e}")
            return {'error': str(e)}


# Export main classes
__all__ = [
    'AnalyticsSerializer',
    'AnalyticsData',
    'MetricValue',
    'MetricSeries',
    'AnalyticsSnapshot',
    'PerformanceBenchmark',
    'AnalyticsType',
    'MetricType',
    'TimeGranularity',
    'AggregationType'
]Serializer Module
===========================

Specialized serialization for analytics data and performance metrics.
Optimized for crawler analytics, performance tracking, and reporting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of analytics metrics."""    PERFORMANCE = "performance"
    ENGAGEMENT = "engagement"
    TRAFFIC = "traffic"
    CONVERSION = "conversion"
    REVENUE = "revenue"
    PROTECTION = "protection"
    VIOLATION = "violation"
    SYSTEM = "system"

class AggregationType(Enum):
    """Data aggregation types."""    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MAX = "max"
    MIN = "min"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    TREND = "trend"

class TimeInterval(Enum):
    """Time interval for analytics."""    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class MetricValue:
    """Individual metric value with timestamp."""    timestamp: datetime
    value: Union[int, float, str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    source: Optional[str] = None

@dataclass
class MetricSeries:
    """Time series of metric values."""    metric_name: str
    metric_type: MetricType
    values: List[MetricValue] = field(default_factory=list)
    unit: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass
class PerformanceMetrics:
    """System performance metrics."""    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: float = 0.0
    response_time: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0
    uptime: float = 100.0

@dataclass
class CrawlerMetrics:
    """Crawler-specific metrics."""    pages_crawled: int = 0
    content_discovered: int = 0
    violations_detected: int = 0
    crawl_speed: float = 0.0
    success_rate: float = 100.0
    error_count: int = 0
    bandwidth_used: float = 0.0
    average_response_time: float = 0.0

@dataclass
class ProtectionMetrics:
    """Content protection metrics."""    content_protected: int = 0
    fingerprints_generated: int = 0
    matches_found: int = 0
    takedowns_issued: int = 0
    takedowns_successful: int = 0
    revenue_protected: float = 0.0
    false_positives: int = 0
    false_negatives: int = 0

class AnalyticsData(BaseModel):
    """    Comprehensive analytics data model.
    
    Represents analytics metrics, performance data, and reporting
    for the IA-Influencer-Agent crawler and protection platform.
    """    
    # Basic information
    analytics_id: str = Field(..., description="Unique analytics identifier")
    report_name: str = Field(..., description="Analytics report name")
    report_type: str = Field(default="general", description="Type of analytics report")
    
    # Time period
    start_time: datetime = Field(..., description="Analytics period start")
    end_time: datetime = Field(..., description="Analytics period end")
    time_interval: TimeInterval = Field(default=TimeInterval.HOUR)
    timezone: str = Field(default="UTC")
    
    # Metric series
    metric_series: List[MetricSeries] = Field(default_factory=list)
    aggregated_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance data
    performance: Optional[PerformanceMetrics] = Field(default=None)
    crawler_metrics: Optional[CrawlerMetrics] = Field(default=None)
    protection_metrics: Optional[ProtectionMetrics] = Field(default=None)
    
    # Platform-specific metrics
    platform_metrics: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    content_metrics: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Trends and insights
    trends: List[Dict[str, Any]] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    anomalies: List[Dict[str, Any]] = Field(default_factory=list)
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Comparison data
    previous_period_comparison: Optional[Dict[str, Any]] = Field(default=None)
    baseline_comparison: Optional[Dict[str, Any]] = Field(default=None)
    
    # Data quality
    data_quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    data_completeness: float = Field(default=1.0, ge=0.0, le=1.0)
    missing_data_points: int = Field(default=0)
    
    # Generation metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    generation_duration: Optional[float] = Field(default=None)
    data_sources: List[str] = Field(default_factory=list)
    
    # Configuration
    filters_applied: Dict[str, Any] = Field(default_factory=dict)
    grouping_criteria: List[str] = Field(default_factory=list)
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('time_interval', pre=True)
    def validate_time_interval(cls, v):
        if isinstance(v, str):
            return TimeInterval(v.lower())
        return v
    
    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError("End time must be after start time")
        return v

class AnalyticsSerializer:
    """    Advanced analytics data serialization system.
    
    Handles efficient serialization and deserialization of analytics
    metrics, performance data, and reporting with optimization for large datasets.
    """    
    def __init__(self):
        """Initialize analytics serializer."""        self.max_series_points = 10000  # Maximum points per metric series
        self.compression_threshold = 1000  # Compress series with more than 1000 points
        
        logger.info("Analytics serializer initialized")
    
    def serialize_analytics(
        self,
        analytics: AnalyticsData,
        compress_series: bool = True,
        include_raw_data: bool = True
    ) -> Dict[str, Any]:
        """        Serialize analytics data to dictionary format.
        
        Args:
            analytics: Analytics data to serialize
            compress_series: Whether to compress large metric series
            include_raw_data: Whether to include raw metric data
            
        Returns:
            Serialized analytics dictionary
        """        try:
            # Convert to dictionary
            data = analytics.dict()
            
            # Handle datetime conversions
            data['start_time'] = analytics.start_time.isoformat()
            data['end_time'] = analytics.end_time.isoformat()
            data['generated_at'] = analytics.generated_at.isoformat()
            
            # Serialize metric series
            if analytics.metric_series and include_raw_data:
                data['metric_series'] = [
                    self._serialize_metric_series(series, compress_series)
                    for series in analytics.metric_series
                ]
            elif not include_raw_data:
                # Remove raw series data, keep only aggregated metrics
                data.pop('metric_series', None)
            
            # Serialize performance metrics
            if analytics.performance:
                data['performance'] = self._serialize_performance_metrics(analytics.performance)
            
            if analytics.crawler_metrics:
                data['crawler_metrics'] = self._serialize_crawler_metrics(analytics.crawler_metrics)
            
            if analytics.protection_metrics:
                data['protection_metrics'] = self._serialize_protection_metrics(analytics.protection_metrics)
            
            # Convert enum
            data['time_interval'] = analytics.time_interval.value
            
            # Add serialization metadata
            data['_serialization'] = {
                'version': '2.0.0',
                'serialized_at': datetime.now().isoformat(),
                'series_compressed': compress_series,
                'includes_raw_data': include_raw_data,
                'report_type': analytics.report_type
            }
            
            logger.debug(f"Serialized analytics report {analytics.analytics_id}")
            return data
            
        except Exception as e:
            logger.error(f"Analytics serialization failed: {e}")
            raise
    
    def deserialize_analytics(
        self,
        data: Dict[str, Any]
    ) -> AnalyticsData:
        """        Deserialize analytics data from dictionary format.
        
        Args:
            data: Serialized analytics dictionary
            
        Returns:
            Deserialized AnalyticsData object
        """        try:
            # Handle datetime conversions
            if isinstance(data.get('start_time'), str):
                data['start_time'] = datetime.fromisoformat(data['start_time'])
            
            if isinstance(data.get('end_time'), str):
                data['end_time'] = datetime.fromisoformat(data['end_time'])
            
            if isinstance(data.get('generated_at'), str):
                data['generated_at'] = datetime.fromisoformat(data['generated_at'])
            
            # Deserialize metric series
            if 'metric_series' in data and data['metric_series']:
                data['metric_series'] = [
                    self._deserialize_metric_series(series_data)
                    for series_data in data['metric_series']
                ]
            
            # Deserialize performance metrics
            if 'performance' in data and data['performance']:
                data['performance'] = self._deserialize_performance_metrics(data['performance'])
            
            if 'crawler_metrics' in data and data['crawler_metrics']:
                data['crawler_metrics'] = self._deserialize_crawler_metrics(data['crawler_metrics'])
            
            if 'protection_metrics' in data and data['protection_metrics']:
                data['protection_metrics'] = self._deserialize_protection_metrics(data['protection_metrics'])
            
            # Remove serialization metadata
            data.pop('_serialization', None)
            
            # Create AnalyticsData object
            analytics = AnalyticsData(**data)
            
            logger.debug(f"Deserialized analytics report {analytics.analytics_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics deserialization failed: {e}")
            raise
    
    def serialize_analytics_batch(
        self,
        analytics_list: List[AnalyticsData],
        compact_mode: bool = True
    ) -> List[Dict[str, Any]]:
        """Serialize multiple analytics reports efficiently."""        try:
            serialized_list = []
            
            for analytics in analytics_list:
                serialized = self.serialize_analytics(
                    analytics,
                    compress_series=compact_mode,
                    include_raw_data=not compact_mode
                )
                serialized_list.append(serialized)
            
            logger.info(f"Serialized {len(analytics_list)} analytics reports")
            return serialized_list
            
        except Exception as e:
            logger.error(f"Analytics batch serialization failed: {e}")
            raise
    
    def deserialize_analytics_batch(
        self,
        data_list: List[Dict[str, Any]]
    ) -> List[AnalyticsData]:
        """Deserialize multiple analytics reports efficiently."""        try:
            analytics_list = []
            
            for data in data_list:
                analytics = self.deserialize_analytics(data)
                analytics_list.append(analytics)
            
            logger.info(f"Deserialized {len(data_list)} analytics reports")
            return analytics_list
            
        except Exception as e:
            logger.error(f"Analytics batch deserialization failed: {e}")
            raise
    
    def _serialize_metric_series(
        self,
        series: MetricSeries,
        compress: bool = True
    ) -> Dict[str, Any]:
        """Serialize metric series."""        data = {
            'metric_name': series.metric_name,
            'metric_type': series.metric_type.value,
            'unit': series.unit,
            'description': series.description,
            'tags': series.tags
        }
        
        # Serialize metric values
        if series.values:
            if compress and len(series.values) > self.compression_threshold:
                data['values'] = self._compress_metric_values(series.values)
                data['_values_compressed'] = True
            else:
                data['values'] = [
                    {
                        'timestamp': value.timestamp.isoformat(),
                        'value': value.value,
                        'metadata': value.metadata,
                        'confidence': value.confidence,
                        'source': value.source
                    }
                    for value in series.values
                ]
                data['_values_compressed'] = False
        else:
            data['values'] = []
            data['_values_compressed'] = False
        
        return data
    
    def _deserialize_metric_series(self, data: Dict[str, Any]) -> MetricSeries:
        """Deserialize metric series."""        # Handle metric type enum
        if isinstance(data.get('metric_type'), str):
            data['metric_type'] = MetricType(data['metric_type'])
        
        # Deserialize metric values
        values = []
        if data.get('values'):
            if data.get('_values_compressed', False):
                values = self._decompress_metric_values(data['values'])
            else:
                for value_data in data['values']:
                    if isinstance(value_data.get('timestamp'), str):
                        value_data['timestamp'] = datetime.fromisoformat(value_data['timestamp'])
                    values.append(MetricValue(**value_data))
        
        # Remove compression metadata
        data.pop('_values_compressed', None)
        data['values'] = values
        
        return MetricSeries(**data)
    
    def _compress_metric_values(self, values: List[MetricValue]) -> str:
        """Compress metric values for storage efficiency."""        try:
            import gzip
            import pickle
            import base64
            
            # Convert to serializable format
            serializable_values = [
                {
                    'timestamp': value.timestamp.timestamp(),
                    'value': value.value,
                    'confidence': value.confidence,
                    'source': value.source
                }
                for value in values
            ]
            
            # Pickle and compress
            pickled = pickle.dumps(serializable_values)
            compressed = gzip.compress(pickled)
            encoded = base64.b64encode(compressed).decode('utf-8')
            
            return f"gzip_pickle:{encoded}"
            
        except Exception as e:
            logger.error(f"Metric values compression failed: {e}")
            # Fallback to JSON serialization
            return json.dumps([
                {
                    'timestamp': value.timestamp.isoformat(),
                    'value': value.value,
                    'confidence': value.confidence,
                    'source': value.source
                }
                for value in values
            ])
    
    def _decompress_metric_values(self, compressed_data: str) -> List[MetricValue]:
        """Decompress metric values."""        try:
            if compressed_data.startswith('gzip_pickle:'):
                import gzip
                import pickle
                import base64
                
                # Remove prefix and decode
                encoded = compressed_data[12:]
                compressed = base64.b64decode(encoded)
                pickled = gzip.decompress(compressed)
                serializable_values = pickle.loads(pickled)
                
                # Convert back to MetricValue objects
                values = []
                for value_data in serializable_values:
                    value_data['timestamp'] = datetime.fromtimestamp(value_data['timestamp'])
                    values.append(MetricValue(**value_data))
                
                return values
            else:
                # JSON fallback
                value_list = json.loads(compressed_data)
                values = []
                for value_data in value_list:
                    value_data['timestamp'] = datetime.fromisoformat(value_data['timestamp'])
                    values.append(MetricValue(**value_data))
                
                return values
                
        except Exception as e:
            logger.error(f"Metric values decompression failed: {e}")
            return []
    
    def _serialize_performance_metrics(self, perf: PerformanceMetrics) -> Dict[str, Any]:
        """Serialize performance metrics."""        return {
            'cpu_usage': perf.cpu_usage,
            'memory_usage': perf.memory_usage,
            'disk_usage': perf.disk_usage,
            'network_io': perf.network_io,
            'response_time': perf.response_time,
            'throughput': perf.throughput,
            'error_rate': perf.error_rate,
            'uptime': perf.uptime
        }
    
    def _deserialize_performance_metrics(self, data: Dict[str, Any]) -> PerformanceMetrics:
        """Deserialize performance metrics."""        return PerformanceMetrics(**data)
    
    def _serialize_crawler_metrics(self, crawler: CrawlerMetrics) -> Dict[str, Any]:
        """Serialize crawler metrics."""        return {
            'pages_crawled': crawler.pages_crawled,
            'content_discovered': crawler.content_discovered,
            'violations_detected': crawler.violations_detected,
            'crawl_speed': crawler.crawl_speed,
            'success_rate': crawler.success_rate,
            'error_count': crawler.error_count,
            'bandwidth_used': crawler.bandwidth_used,
            'average_response_time': crawler.average_response_time
        }
    
    def _deserialize_crawler_metrics(self, data: Dict[str, Any]) -> CrawlerMetrics:
        """Deserialize crawler metrics."""        return CrawlerMetrics(**data)
    
    def _serialize_protection_metrics(self, protection: ProtectionMetrics) -> Dict[str, Any]:
        """Serialize protection metrics."""        return {
            'content_protected': protection.content_protected,
            'fingerprints_generated': protection.fingerprints_generated,
            'matches_found': protection.matches_found,
            'takedowns_issued': protection.takedowns_issued,
            'takedowns_successful': protection.takedowns_successful,
            'revenue_protected': protection.revenue_protected,
            'false_positives': protection.false_positives,
            'false_negatives': protection.false_negatives
        }
    
    def _deserialize_protection_metrics(self, data: Dict[str, Any]) -> ProtectionMetrics:
        """Deserialize protection metrics."""        return ProtectionMetrics(**data)
    
    def calculate_metric_statistics(
        self,
        series: MetricSeries
    ) -> Dict[str, Any]:
        """Calculate statistical summary for metric series."""        try:
            if not series.values:
                return {}
            
            # Extract numeric values
            numeric_values = []
            for value in series.values:
                if isinstance(value.value, (int, float)):
                    numeric_values.append(float(value.value))
            
            if not numeric_values:
                return {'count': len(series.values)}
            
            stats = {
                'count': len(numeric_values),
                'sum': sum(numeric_values),
                'mean': statistics.mean(numeric_values),
                'min': min(numeric_values),
                'max': max(numeric_values),
                'range': max(numeric_values) - min(numeric_values)
            }
            
            if len(numeric_values) > 1:
                stats['median'] = statistics.median(numeric_values)
                stats['stdev'] = statistics.stdev(numeric_values)
                stats['variance'] = statistics.variance(numeric_values)
            
            # Calculate percentiles
            if len(numeric_values) >= 4:
                sorted_values = sorted(numeric_values)
                stats['q1'] = statistics.quantiles(sorted_values, n=4)[0]
                stats['q3'] = statistics.quantiles(sorted_values, n=4)[2]
                stats['iqr'] = stats['q3'] - stats['q1']
            
            return stats
            
        except Exception as e:
            logger.error(f"Metric statistics calculation failed: {e}")
            return {}
    
    def detect_anomalies(
        self,
        series: MetricSeries,
        threshold_multiplier: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in metric series using statistical methods."""        try:
            anomalies = []
            
            if len(series.values) < 10:  # Need minimum data points
                return anomalies
            
            # Extract numeric values with timestamps
            data_points = []
            for value in series.values:
                if isinstance(value.value, (int, float)):
                    data_points.append({
                        'timestamp': value.timestamp,
                        'value': float(value.value)
                    })
            
            if len(data_points) < 10:
                return anomalies
            
            # Calculate rolling statistics
            values = [point['value'] for point in data_points]
            mean_value = statistics.mean(values)
            stdev_value = statistics.stdev(values) if len(values) > 1 else 0
            
            # Detect outliers using z-score method
            for point in data_points:
                if stdev_value > 0:
                    z_score = abs(point['value'] - mean_value) / stdev_value
                    
                    if z_score > threshold_multiplier:
                        anomalies.append({
                            'timestamp': point['timestamp'].isoformat(),
                            'value': point['value'],
                            'z_score': z_score,
                            'anomaly_type': 'statistical_outlier',
                            'severity': 'high' if z_score > 3.0 else 'medium'
                        })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def create_analytics_summary(
        self,
        analytics: AnalyticsData
    ) -> Dict[str, Any]:
        """Create compact summary of analytics report."""        try:
            period_duration = analytics.end_time - analytics.start_time
            
            summary = {
                'analytics_id': analytics.analytics_id,
                'report_name': analytics.report_name,
                'report_type': analytics.report_type,
                'period_duration_hours': period_duration.total_seconds() / 3600,
                'time_interval': analytics.time_interval.value,
                'metric_series_count': len(analytics.metric_series),
                'data_quality_score': analytics.data_quality_score,
                'generated_at': analytics.generated_at.isoformat()
            }
            
            # Add key metrics summary
            if analytics.performance:
                summary['performance_summary'] = {
                    'cpu_usage': analytics.performance.cpu_usage,
                    'memory_usage': analytics.performance.memory_usage,
                    'response_time': analytics.performance.response_time,
                    'error_rate': analytics.performance.error_rate
                }
            
            if analytics.crawler_metrics:
                summary['crawler_summary'] = {
                    'pages_crawled': analytics.crawler_metrics.pages_crawled,
                    'content_discovered': analytics.crawler_metrics.content_discovered,
                    'violations_detected': analytics.crawler_metrics.violations_detected,
                    'success_rate': analytics.crawler_metrics.success_rate
                }
            
            if analytics.protection_metrics:
                summary['protection_summary'] = {
                    'content_protected': analytics.protection_metrics.content_protected,
                    'matches_found': analytics.protection_metrics.matches_found,
                    'takedowns_successful': analytics.protection_metrics.takedowns_successful,
                    'revenue_protected': analytics.protection_metrics.revenue_protected
                }
            
            # Add insights and alerts count
            summary['insights_count'] = len(analytics.insights)
            summary['anomalies_count'] = len(analytics.anomalies)
            summary['alerts_count'] = len(analytics.alerts)
            
            return summary
            
        except Exception as e:
            logger.error(f"Analytics summary creation failed: {e}")
            return {'error': str(e)}


# Export main classes
__all__ = [
    'AnalyticsSerializer',
    'AnalyticsData',
    'MetricSeries',
    'MetricValue',
    'PerformanceMetrics',
    'CrawlerMetrics',
    'ProtectionMetrics',
    'MetricType',
    'AggregationType',
    'TimeInterval'
]
