"""
Metrics Collector - Advanced Metrics Collection System

Enterprise-grade metrics collection framework for multi-format content creators
with real-time monitoring, business intelligence, and performance analytics.

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
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import psutil

from .exceptions import MetricsError, DataValidationError, StorageError

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics that can be collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"
    DISTRIBUTION = "distribution"
    BUSINESS = "business"


class MetricScope(Enum):
    """Scope of metric collection"""
    USER = "user"
    CONTENT = "content"
    SYSTEM = "system"
    BUSINESS = "business"
    PLATFORM = "platform"
    REVENUE = "revenue"


class AggregationMethod(Enum):
    """Aggregation methods for metrics"""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"
    MEDIAN = "median"
    STANDARD_DEVIATION = "std_dev"


@dataclass
class MetricPoint:
    """Individual metric data point"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    scope: MetricScope
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric point to dictionary"""
        return {
            'name': self.name,
            'value': self.value,
            'type': self.metric_type.value,
            'scope': self.scope.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags,
            'metadata': self.metadata
        }


@dataclass
class AggregatedMetric:
    """Aggregated metric result"""
    name: str
    aggregation_method: AggregationMethod
    value: Union[int, float]
    period_start: datetime
    period_end: datetime
    sample_count: int
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregated metric to dictionary"""
        return {
            'name': self.name,
            'aggregation_method': self.aggregation_method.value,
            'value': self.value,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'sample_count': self.sample_count,
            'tags': self.tags
        }


class MetricsCollector:
    """
    Advanced metrics collection system for IA influencer platform.
    
    Collects, validates, and stores metrics from various sources with
    real-time processing and business intelligence capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage for metrics
        self.metrics_buffer = deque(maxlen=self.config.get('buffer_size', 10000))
        self.aggregated_metrics = defaultdict(list)
        
        # Performance tracking
        self.collection_stats = {
            'total_collected': 0,
            'total_processed': 0,
            'errors': 0,
            'last_collection': None
        }
        
        # Configuration
        self.batch_size = self.config.get('batch_size', 100)
        self.flush_interval = self.config.get('flush_interval', 60)  # seconds
        self.max_retries = self.config.get('max_retries', 3)
        
        # Background processing
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def initialize(self) -> None:
        """Initialize the metrics collector"""
        try:
            self.logger.info("Initializing MetricsCollector...")
            
            # Start background processing
            self.is_running = True
            asyncio.create_task(self._background_processor())
            
            self.logger.info("MetricsCollector initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MetricsCollector: {str(e)}")
            raise MetricsError(f"Initialization failed: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown the metrics collector"""
        try:
            self.logger.info("Shutting down MetricsCollector...")
            
            self.is_running = False
            
            # Flush remaining metrics
            await self._flush_metrics()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            self.logger.info("MetricsCollector shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error shutting down MetricsCollector: {str(e)}")
            raise MetricsError(f"Shutdown failed: {str(e)}")
    
    async def collect_metric(self, metric: MetricPoint) -> None:
        """Collect a single metric point"""
        try:
            # Validate metric
            self._validate_metric(metric)
            
            # Add to buffer
            self.metrics_buffer.append(metric)
            
            # Update stats
            self.collection_stats['total_collected'] += 1
            self.collection_stats['last_collection'] = datetime.now()
            
            self.logger.debug(f"Collected metric: {metric.name} = {metric.value}")
            
        except Exception as e:
            self.collection_stats['errors'] += 1
            self.logger.error(f"Error collecting metric: {str(e)}")
            raise MetricsError(f"Metric collection failed: {str(e)}")
    
    async def collect_metrics_batch(self, metrics: List[MetricPoint]) -> None:
        """Collect multiple metrics in batch"""
        try:
            valid_metrics = []
            
            for metric in metrics:
                try:
                    self._validate_metric(metric)
                    valid_metrics.append(metric)
                except Exception as e:
                    self.logger.warning(f"Invalid metric skipped: {str(e)}")
                    self.collection_stats['errors'] += 1
            
            # Add valid metrics to buffer
            self.metrics_buffer.extend(valid_metrics)
            
            # Update stats
            self.collection_stats['total_collected'] += len(valid_metrics)
            self.collection_stats['last_collection'] = datetime.now()
            
            self.logger.info(f"Collected batch of {len(valid_metrics)} metrics")
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics batch: {str(e)}")
            raise MetricsError(f"Batch collection failed: {str(e)}")
    
    async def get_metrics(
        self,
        name_pattern: Optional[str] = None,
        scope: Optional[MetricScope] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[MetricPoint]:
        """Retrieve metrics based on filters"""
        try:
            filtered_metrics = []
            
            for metric in self.metrics_buffer:
                if self._matches_filters(metric, name_pattern, scope, start_time, end_time, tags):
                    filtered_metrics.append(metric)
            
            self.logger.debug(f"Retrieved {len(filtered_metrics)} metrics with filters")
            return filtered_metrics
            
        except Exception as e:
            self.logger.error(f"Error retrieving metrics: {str(e)}")
            raise MetricsError(f"Metrics retrieval failed: {str(e)}")
    
    async def aggregate_metrics(
        self,
        name: str,
        method: AggregationMethod,
        period_start: datetime,
        period_end: datetime,
        tags: Optional[Dict[str, str]] = None
    ) -> Optional[AggregatedMetric]:
        """Aggregate metrics over a time period"""
        try:
            # Get metrics for aggregation
            metrics = await self.get_metrics(
                name_pattern=name,
                start_time=period_start,
                end_time=period_end,
                tags=tags
            )
            
            if not metrics:
                return None
            
            # Extract values
            values = [metric.value for metric in metrics]
            
            # Calculate aggregated value
            aggregated_value = self._calculate_aggregation(values, method)
            
            aggregated_metric = AggregatedMetric(
                name=name,
                aggregation_method=method,
                value=aggregated_value,
                period_start=period_start,
                period_end=period_end,
                sample_count=len(values),
                tags=tags or {}
            )
            
            # Store aggregated metric
            self.aggregated_metrics[name].append(aggregated_metric)
            
            self.logger.debug(f"Aggregated {len(values)} values for {name}: {aggregated_value}")
            return aggregated_metric
            
        except Exception as e:
            self.logger.error(f"Error aggregating metrics: {str(e)}")
            raise MetricsError(f"Metrics aggregation failed: {str(e)}")
    
    async def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics summary"""
        try:
            current_time = datetime.now()
            last_hour = current_time - timedelta(hours=1)
            
            # Get recent metrics
            recent_metrics = await self.get_metrics(start_time=last_hour)
            
            # Group by scope
            metrics_by_scope = defaultdict(list)
            for metric in recent_metrics:
                metrics_by_scope[metric.scope.value].append(metric)
            
            summary = {
                'timestamp': current_time.isoformat(),
                'total_metrics': len(recent_metrics),
                'collection_stats': self.collection_stats.copy(),
                'metrics_by_scope': {}
            }
            
            # Calculate statistics by scope
            for scope, scope_metrics in metrics_by_scope.items():
                if scope_metrics:
                    values = [m.value for m in scope_metrics]
                    summary['metrics_by_scope'][scope] = {
                        'count': len(scope_metrics),
                        'avg': statistics.mean(values),
                        'min': min(values),
                        'max': max(values),
                        'std_dev': statistics.stdev(values) if len(values) > 1 else 0
                    }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting realtime metrics: {str(e)}")
            raise MetricsError(f"Realtime metrics failed: {str(e)}")
    
    async def export_metrics(
        self,
        format_type: str = "json",
        include_aggregated: bool = True
    ) -> Union[str, bytes]:
        """Export metrics in specified format"""
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'raw_metrics': [metric.to_dict() for metric in self.metrics_buffer],
                'collection_stats': self.collection_stats
            }
            
            if include_aggregated:
                export_data['aggregated_metrics'] = {}
                for name, metrics in self.aggregated_metrics.items():
                    export_data['aggregated_metrics'][name] = [
                        metric.to_dict() for metric in metrics
                    ]
            
            if format_type == "json":
                return json.dumps(export_data, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {str(e)}")
            raise MetricsError(f"Metrics export failed: {str(e)}")
    
    # Private Methods
    
    def _validate_metric(self, metric: MetricPoint) -> None:
        """Validate metric point"""
        if not metric.name:
            raise DataValidationError("Metric name is required")
        
        if metric.value is None:
            raise DataValidationError("Metric value is required")
        
        if not isinstance(metric.value, (int, float)):
            raise DataValidationError("Metric value must be numeric")
        
        if not isinstance(metric.metric_type, MetricType):
            raise DataValidationError("Invalid metric type")
        
        if not isinstance(metric.scope, MetricScope):
            raise DataValidationError("Invalid metric scope")
    
    def _matches_filters(
        self,
        metric: MetricPoint,
        name_pattern: Optional[str],
        scope: Optional[MetricScope],
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        tags: Optional[Dict[str, str]]
    ) -> bool:
        """Check if metric matches filters"""
        # Name pattern filter
        if name_pattern and name_pattern not in metric.name:
            return False
        
        # Scope filter
        if scope and metric.scope != scope:
            return False
        
        # Time range filter
        if start_time and metric.timestamp < start_time:
            return False
        
        if end_time and metric.timestamp > end_time:
            return False
        
        # Tags filter
        if tags:
            for key, value in tags.items():
                if key not in metric.tags or metric.tags[key] != value:
                    return False
        
        return True
    
    def _calculate_aggregation(
        self,
        values: List[Union[int, float]],
        method: AggregationMethod
    ) -> Union[int, float]:
        """Calculate aggregated value"""
        if not values:
            return 0
        
        if method == AggregationMethod.SUM:
            return sum(values)
        elif method == AggregationMethod.AVERAGE:
            return statistics.mean(values)
        elif method == AggregationMethod.MIN:
            return min(values)
        elif method == AggregationMethod.MAX:
            return max(values)
        elif method == AggregationMethod.COUNT:
            return len(values)
        elif method == AggregationMethod.MEDIAN:
            return statistics.median(values)
        elif method == AggregationMethod.PERCENTILE:
            return np.percentile(values, 95)  # Default 95th percentile
        elif method == AggregationMethod.STANDARD_DEVIATION:
            return statistics.stdev(values) if len(values) > 1 else 0
        else:
            raise ValueError(f"Unsupported aggregation method: {method}")
    
    async def _background_processor(self) -> None:
        """Background task for processing metrics"""
        while self.is_running:
            try:
                # Process metrics every flush interval
                await asyncio.sleep(self.flush_interval)
                
                if not self.is_running:
                    break
                
                await self._flush_metrics()
                
            except Exception as e:
                self.logger.error(f"Error in background processor: {str(e)}")
                await asyncio.sleep(5)
    
    async def _flush_metrics(self) -> None:
        """Flush metrics to storage"""
        try:
            if not self.metrics_buffer:
                return
            
            # Get batch of metrics to process
            batch_metrics = []
            while self.metrics_buffer and len(batch_metrics) < self.batch_size:
                batch_metrics.append(self.metrics_buffer.popleft())
            
            if batch_metrics:
                # Process batch in thread pool
                await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self._process_metrics_batch,
                    batch_metrics
                )
                
                self.collection_stats['total_processed'] += len(batch_metrics)
                self.logger.debug(f"Processed batch of {len(batch_metrics)} metrics")
            
        except Exception as e:
            self.logger.error(f"Error flushing metrics: {str(e)}")
            # Return metrics to buffer on error
            self.metrics_buffer.extendleft(reversed(batch_metrics))
    
    def _process_metrics_batch(self, metrics: List[MetricPoint]) -> None:
        """Process batch of metrics (CPU intensive operations)"""
        try:
            # Perform CPU-intensive processing here
            # For now, just update processing stats
            for metric in metrics:
                # Could perform additional validation, transformation, etc.
                pass
                
        except Exception as e:
            self.logger.error(f"Error processing metrics batch: {str(e)}")
            raise


class BusinessMetricsCollector(MetricsCollector):
    """
    Specialized metrics collector for business-critical metrics.
    
    Extends base collector with business-specific functionality and
    enhanced monitoring for revenue, user engagement, and platform performance.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Business-specific metrics storage
        self.business_metrics = {
            'revenue': defaultdict(list),
            'user_engagement': defaultdict(list),
            'content_performance': defaultdict(list),
            'platform_usage': defaultdict(list)
        }
        
        # Business KPIs
        self.kpi_thresholds = self.config.get('kpi_thresholds', {
            'daily_revenue': 1000.0,
            'user_retention': 0.8,
            'content_quality_score': 0.85,
            'platform_uptime': 0.995
        })
    
    async def track_revenue_metric(
        self,
        amount: float,
        currency: str = "EUR",
        source: str = "platform",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track revenue-related metrics"""
        try:
            metric = MetricPoint(
                name=f"revenue_{source}",
                value=amount,
                metric_type=MetricType.BUSINESS,
                scope=MetricScope.REVENUE,
                tags={
                    'currency': currency,
                    'source': source
                },
                metadata=metadata or {}
            )
            
            await self.collect_metric(metric)
            self.business_metrics['revenue'][source].append(metric)
            
            self.logger.info(f"Tracked revenue metric: {amount} {currency} from {source}")
            
        except Exception as e:
            self.logger.error(f"Error tracking revenue metric: {str(e)}")
            raise MetricsError(f"Revenue tracking failed: {str(e)}")
    
    async def track_user_engagement_metric(
        self,
        user_id: str,
        engagement_type: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track user engagement metrics"""
        try:
            metric = MetricPoint(
                name=f"engagement_{engagement_type}",
                value=value,
                metric_type=MetricType.BUSINESS,
                scope=MetricScope.USER,
                tags={
                    'user_id': user_id,
                    'engagement_type': engagement_type
                },
                metadata=metadata or {}
            )
            
            await self.collect_metric(metric)
            self.business_metrics['user_engagement'][engagement_type].append(metric)
            
            self.logger.debug(f"Tracked engagement metric: {engagement_type} = {value} for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error tracking engagement metric: {str(e)}")
            raise MetricsError(f"Engagement tracking failed: {str(e)}")
    
    async def track_content_performance_metric(
        self,
        content_id: str,
        performance_type: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track content performance metrics"""
        try:
            metric = MetricPoint(
                name=f"content_{performance_type}",
                value=value,
                metric_type=MetricType.BUSINESS,
                scope=MetricScope.CONTENT,
                tags={
                    'content_id': content_id,
                    'performance_type': performance_type
                },
                metadata=metadata or {}
            )
            
            await self.collect_metric(metric)
            self.business_metrics['content_performance'][performance_type].append(metric)
            
            self.logger.debug(f"Tracked content metric: {performance_type} = {value} for content {content_id}")
            
        except Exception as e:
            self.logger.error(f"Error tracking content metric: {str(e)}")
            raise MetricsError(f"Content tracking failed: {str(e)}")
    
    async def get_business_kpis(self) -> Dict[str, Any]:
        """Get current business KPIs"""
        try:
            current_time = datetime.now()
            today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            kpis = {
                'timestamp': current_time.isoformat(),
                'kpis': {},
                'thresholds': self.kpi_thresholds,
                'alerts': []
            }
            
            # Calculate daily revenue
            daily_revenue_metrics = await self.get_metrics(
                name_pattern="revenue_",
                start_time=today_start,
                scope=MetricScope.REVENUE
            )
            
            if daily_revenue_metrics:
                daily_revenue = sum(m.value for m in daily_revenue_metrics)
                kpis['kpis']['daily_revenue'] = daily_revenue
                
                if daily_revenue < self.kpi_thresholds['daily_revenue']:
                    kpis['alerts'].append({
                        'type': 'revenue_below_threshold',
                        'current': daily_revenue,
                        'threshold': self.kpi_thresholds['daily_revenue']
                    })
            
            # Add more KPI calculations here...
            
            return kpis
            
        except Exception as e:
            self.logger.error(f"Error getting business KPIs: {str(e)}")
            raise MetricsError(f"Business KPIs retrieval failed: {str(e)}")
    
    async def generate_business_summary(self) -> Dict[str, Any]:
        """Generate business metrics summary"""
        try:
            summary = {
                'generated_at': datetime.now().isoformat(),
                'revenue_summary': await self._get_revenue_summary(),
                'engagement_summary': await self._get_engagement_summary(),
                'content_summary': await self._get_content_summary(),
                'platform_summary': await self._get_platform_summary()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating business summary: {str(e)}")
            raise MetricsError(f"Business summary generation failed: {str(e)}")
    
    # Private Methods
    
    async def _get_revenue_summary(self) -> Dict[str, Any]:
        """Get revenue metrics summary"""
        # Implementation for revenue summary
        return {'total_revenue': 0, 'revenue_sources': {}}
    
    async def _get_engagement_summary(self) -> Dict[str, Any]:
        """Get engagement metrics summary"""
        # Implementation for engagement summary
        return {'avg_engagement': 0, 'engagement_trends': {}}
    
    async def _get_content_summary(self) -> Dict[str, Any]:
        """Get content metrics summary"""
        # Implementation for content summary
        return {'total_content': 0, 'performance_trends': {}}
    
    async def _get_platform_summary(self) -> Dict[str, Any]:
        """Get platform metrics summary"""
        # Implementation for platform summary
        return {'uptime': 0, 'active_users': 0}
