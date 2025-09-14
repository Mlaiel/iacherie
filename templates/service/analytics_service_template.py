"""
📊 Analytics Service Template - Enterprise Analytics & Insights Framework
=========================================================================

🛡️ BACKEND SENIOR - Advanced Analytics Service Template
- Real-time analytics collection and processing
- Multi-dimensional data analysis and insights
- Performance metrics and KPI tracking
- Predictive analytics and trend analysis
- Custom dashboard and reporting system
- Data warehouse integration and optimization

Author: Backend Senior Expert
Version: 1.0.0
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time
import uuid
from collections import defaultdict, deque
import statistics
import numpy as np
from abc import ABC, abstractmethod
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"

class AggregationType(Enum):
    """Aggregation types for analytics"""
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    PERCENTILE = "percentile"
    DISTINCT_COUNT = "distinct_count"

class TimeGranularity(Enum):
    """Time granularity for analytics"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

class EventCategory(Enum):
    """Event categories for analytics"""
    USER_ACTION = "user_action"
    CONTENT_INTERACTION = "content_interaction"
    SYSTEM_PERFORMANCE = "system_performance"
    BUSINESS_METRIC = "business_metric"
    ERROR_EVENT = "error_event"

@dataclass
class AnalyticsEvent:
    """Analytics event data structure"""
    event_id: str
    event_type: str
    category: EventCategory
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    platform: Optional[str] = None
    version: str = "1.0"

@dataclass
class MetricDefinition:
    """Metric definition for analytics"""
    metric_name: str
    metric_type: MetricType
    description: str
    unit: str = ""
    tags: List[str] = field(default_factory=list)
    dimensions: List[str] = field(default_factory=list)
    retention_days: int = 365
    aggregations: List[AggregationType] = field(default_factory=list)

@dataclass
class MetricDataPoint:
    """Single metric data point"""
    metric_name: str
    timestamp: datetime
    value: Union[int, float]
    dimensions: Dict[str, str] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class AnalyticsQuery:
    """Analytics query structure"""
    query_id: str
    metric_names: List[str]
    start_time: datetime
    end_time: datetime
    granularity: TimeGranularity
    aggregation: AggregationType
    filters: Dict[str, Any] = field(default_factory=dict)
    dimensions: List[str] = field(default_factory=list)
    limit: Optional[int] = None
    offset: int = 0

@dataclass
class AnalyticsResult:
    """Analytics query result"""
    query_id: str
    metric_name: str
    data_points: List[Dict[str, Any]]
    total_count: int
    aggregated_value: Optional[Union[int, float]] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Dashboard:
    """Analytics dashboard definition"""
    dashboard_id: str
    name: str
    description: str
    owner_id: str
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    layout: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    refresh_interval_seconds: int = 300
    is_public: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class MetricStorage(ABC):
    """Abstract metric storage interface"""
    
    @abstractmethod
    async def store_metric(self, metric: MetricDataPoint) -> bool:
        """Store single metric data point"""
        pass
    
    @abstractmethod
    async def store_metrics_batch(self, metrics: List[MetricDataPoint]) -> bool:
        """Store batch of metric data points"""
        pass
    
    @abstractmethod
    async def query_metrics(self, query: AnalyticsQuery) -> AnalyticsResult:
        """Query metrics based on analytics query"""
        pass

class MemoryMetricStorage(MetricStorage):
    """In-memory metric storage implementation"""
    
    def __init__(self, max_data_points -> None: int = 1000000) -> None:
        self.data_points = defaultdict(list)  # metric_name -> list of data points
        self.max_data_points = max_data_points
        self.total_data_points = 0
    
    async def store_metric(self, metric: MetricDataPoint) -> bool:
        """Store single metric in memory"""
        try:
            # Check storage limit
            if self.total_data_points >= self.max_data_points:
                await self._cleanup_old_data()
            
            # Store data point
            data_point = {
                "timestamp": metric.timestamp,
                "value": metric.value,
                "dimensions": metric.dimensions,
                "tags": metric.tags
            }
            
            self.data_points[metric.metric_name].append(data_point)
            self.total_data_points += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store metric {metric.metric_name}: {str(e)}")
            return False
    
    async def store_metrics_batch(self, metrics: List[MetricDataPoint]) -> bool:
        """Store batch of metrics"""
        try:
            for metric in metrics:
                await self.store_metric(metric)
            return True
        except Exception as e:
            logger.error(f"Failed to store metric batch: {str(e)}")
            return False
    
    async def query_metrics(self, query: AnalyticsQuery) -> AnalyticsResult:
        """Query metrics from memory storage"""
        start_time = time.time()
        
        try:
            result_data_points = []
            
            for metric_name in query.metric_names:
                if metric_name not in self.data_points:
                    continue
                
                # Filter by time range
                filtered_points = [
                    point for point in self.data_points[metric_name]
                    if query.start_time <= point["timestamp"] <= query.end_time
                ]
                
                # Apply filters
                if query.filters:
                    filtered_points = self._apply_filters(filtered_points, query.filters)
                
                # Aggregate by granularity
                aggregated_points = self._aggregate_by_granularity(
                    filtered_points, query.granularity, query.aggregation
                )
                
                result_data_points.extend(aggregated_points)
            
            # Calculate aggregated value
            aggregated_value = None
            if result_data_points:
                values = [point["value"] for point in result_data_points]
                if query.aggregation == AggregationType.SUM:
                    aggregated_value = sum(values)
                elif query.aggregation == AggregationType.AVERAGE:
                    aggregated_value = statistics.mean(values)
                elif query.aggregation == AggregationType.COUNT:
                    aggregated_value = len(values)
                elif query.aggregation == AggregationType.MIN:
                    aggregated_value = min(values)
                elif query.aggregation == AggregationType.MAX:
                    aggregated_value = max(values)
            
            # Apply limit and offset
            if query.offset:
                result_data_points = result_data_points[query.offset:]
            if query.limit:
                result_data_points = result_data_points[:query.limit]
            
            execution_time = (time.time() - start_time) * 1000
            
            return AnalyticsResult(
                query_id=query.query_id,
                metric_name=",".join(query.metric_names),
                data_points=result_data_points,
                total_count=len(result_data_points),
                aggregated_value=aggregated_value,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"Failed to query metrics: {str(e)}")
            execution_time = (time.time() - start_time) * 1000
            return AnalyticsResult(
                query_id=query.query_id,
                metric_name=",".join(query.metric_names),
                data_points=[],
                total_count=0,
                execution_time_ms=execution_time,
                metadata={"error": str(e)}
            )
    
    def _apply_filters(self, data_points: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Apply filters to data points"""
        filtered_points = []
        
        for point in data_points:
            matches = True
            
            for filter_key, filter_value in filters.items():
                # Check dimensions
                if filter_key in point.get("dimensions", {}):
                    if point["dimensions"][filter_key] != filter_value:
                        matches = False
                        break
                
                # Check tags
                elif filter_key in point.get("tags", {}):
                    if point["tags"][filter_key] != filter_value:
                        matches = False
                        break
                
                # Check value range
                elif filter_key == "value_min" and point["value"] < filter_value:
                    matches = False
                    break
                elif filter_key == "value_max" and point["value"] > filter_value:
                    matches = False
                    break
            
            if matches:
                filtered_points.append(point)
        
        return filtered_points
    
    def _aggregate_by_granularity(self, data_points: List[Dict], 
                                 granularity: TimeGranularity,
                                 aggregation: AggregationType) -> List[Dict]:
        """Aggregate data points by time granularity"""
        if not data_points:
            return []
        
        # Group data points by time bucket
        time_buckets = defaultdict(list)
        
        for point in data_points:
            bucket_key = self._get_time_bucket(point["timestamp"], granularity)
            time_buckets[bucket_key].append(point)
        
        # Aggregate within each bucket
        aggregated_points = []
        
        for bucket_time, bucket_points in time_buckets.items():
            values = [point["value"] for point in bucket_points]
            
            if aggregation == AggregationType.SUM:
                aggregated_value = sum(values)
            elif aggregation == AggregationType.AVERAGE:
                aggregated_value = statistics.mean(values)
            elif aggregation == AggregationType.COUNT:
                aggregated_value = len(values)
            elif aggregation == AggregationType.MIN:
                aggregated_value = min(values)
            elif aggregation == AggregationType.MAX:
                aggregated_value = max(values)
            else:
                aggregated_value = sum(values)  # Default to sum
            
            aggregated_points.append({
                "timestamp": bucket_time,
                "value": aggregated_value,
                "count": len(bucket_points)
            })
        
        return sorted(aggregated_points, key=lambda x: x["timestamp"])
    
    def _get_time_bucket(self, timestamp: datetime, granularity: TimeGranularity) -> datetime:
        """Get time bucket for granularity"""
        if granularity == TimeGranularity.MINUTE:
            return timestamp.replace(second=0, microsecond=0)
        elif granularity == TimeGranularity.HOUR:
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.DAY:
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.WEEK:
            days_since_monday = timestamp.weekday()
            monday = timestamp - timedelta(days=days_since_monday)
            return monday.replace(hour=0, minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.MONTH:
            return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif granularity == TimeGranularity.YEAR:
            return timestamp.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        return timestamp
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old data points to maintain storage limit"""
        # Remove oldest 10% of data points
        cleanup_count = self.max_data_points // 10
        
        for metric_name in self.data_points:
            data_points = self.data_points[metric_name]
            if len(data_points) > cleanup_count:
                # Sort by timestamp and keep newest
                data_points.sort(key=lambda x: x["timestamp"])
                self.data_points[metric_name] = data_points[cleanup_count:]
        
        # Recalculate total count
        self.total_data_points = sum(len(points) for points in self.data_points.values())

class AnalyticsCollector:
    """Analytics event collector and processor"""
    
    def __init__(self, metric_storage -> None: MetricStorage) -> None:
        self.metric_storage = metric_storage
        self.event_buffer = deque(maxlen=10000)
        self.processing_stats = {
            "events_collected": 0,
            "events_processed": 0,
            "events_failed": 0,
            "metrics_generated": 0
        }
        self.is_processing = False
    
    async def collect_event(self, event: AnalyticsEvent) -> bool:
        """Collect analytics event"""
        try:
            self.event_buffer.append(event)
            self.processing_stats["events_collected"] += 1
            
            # Trigger processing if not already running
            if not self.is_processing:
                asyncio.create_task(self._process_events())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to collect event {event.event_id}: {str(e)}")
            return False
    
    async def _process_events(self) -> None:
        """Process collected events and generate metrics"""
        if self.is_processing:
            return
        
        self.is_processing = True
        
        try:
            while self.event_buffer:
                event = self.event_buffer.popleft()
                await self._process_single_event(event)
                
                self.processing_stats["events_processed"] += 1
                
                # Batch processing - process up to 100 events at a time
                if self.processing_stats["events_processed"] % 100 == 0:
                    await asyncio.sleep(0.01)  # Small delay to prevent blocking
                    
        except Exception as e:
            logger.error(f"Event processing error: {str(e)}")
            self.processing_stats["events_failed"] += 1
        finally:
            self.is_processing = False
    
    async def _process_single_event(self, event -> None: AnalyticsEvent) -> None:
        """Process single event and generate metrics"""
        try:
            # Generate standard metrics from event
            metrics = []
            
            # Event count metric
            metrics.append(MetricDataPoint(
                metric_name=f"event_count_{event.event_type}",
                timestamp=event.timestamp,
                value=1,
                dimensions={
                    "event_type": event.event_type,
                    "category": event.category.value,
                    "source": event.source
                },
                tags={"platform": event.platform or "unknown"}
            ))
            
            # User engagement metrics
            if event.user_id:
                metrics.append(MetricDataPoint(
                    metric_name="user_engagement",
                    timestamp=event.timestamp,
                    value=1,
                    dimensions={
                        "user_id": event.user_id,
                        "event_type": event.event_type
                    }
                ))
            
            # Session metrics
            if event.session_id:
                metrics.append(MetricDataPoint(
                    metric_name="session_activity",
                    timestamp=event.timestamp,
                    value=1,
                    dimensions={
                        "session_id": event.session_id,
                        "event_type": event.event_type
                    }
                ))
            
            # Custom property metrics
            for prop_name, prop_value in event.properties.items():
                if isinstance(prop_value, (int, float)):
                    metrics.append(MetricDataPoint(
                        metric_name=f"property_{prop_name}",
                        timestamp=event.timestamp,
                        value=prop_value,
                        dimensions={"event_type": event.event_type}
                    ))
            
            # Store all generated metrics
            if metrics:
                await self.metric_storage.store_metrics_batch(metrics)
                self.processing_stats["metrics_generated"] += len(metrics)
                
        except Exception as e:
            logger.error(f"Failed to process event {event.event_id}: {str(e)}")
            self.processing_stats["events_failed"] += 1

class AnalyticsService:
    """📊 Advanced Analytics Service for Enterprise Data Insights"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        """Initialize Analytics Service"""
        self.config = config or {}
        self.service_id = f"analytics_service_{int(time.time())}"
        
        # Storage and processing
        self.metric_storage = MemoryMetricStorage(
            max_data_points=self.config.get("max_data_points", 1000000)
        )
        self.collector = AnalyticsCollector(self.metric_storage)
        
        # Metric definitions
        self.metric_definitions = {}
        self.dashboards = {}
        
        # Query cache
        self.query_cache = {}
        self.cache_ttl_seconds = self.config.get("cache_ttl_seconds", 300)
        
        # Background tasks
        self.background_tasks = []
        self.is_running = False
        
        # Statistics
        self.service_stats = {
            "queries_executed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "dashboards_created": 0,
            "total_data_points": 0
        }
        
        # Setup default metric definitions
        self._setup_default_metrics()
        
        logger.info(f"📊 Analytics Service initialized: {self.service_id}")
    
    def _setup_default_metrics(self) -> None:
        """Setup default metric definitions"""
        default_metrics = [
            MetricDefinition(
                metric_name="page_views",
                metric_type=MetricType.COUNTER,
                description="Number of page views",
                dimensions=["page", "user_id"],
                aggregations=[AggregationType.SUM, AggregationType.COUNT]
            ),
            MetricDefinition(
                metric_name="user_engagement",
                metric_type=MetricType.COUNTER,
                description="User engagement events",
                dimensions=["user_id", "event_type"],
                aggregations=[AggregationType.SUM, AggregationType.DISTINCT_COUNT]
            ),
            MetricDefinition(
                metric_name="content_performance",
                metric_type=MetricType.GAUGE,
                description="Content performance metrics",
                dimensions=["content_id", "metric_type"],
                aggregations=[AggregationType.AVERAGE, AggregationType.MAX]
            ),
            MetricDefinition(
                metric_name="system_performance",
                metric_type=MetricType.TIMER,
                description="System performance metrics",
                unit="milliseconds",
                dimensions=["service", "operation"],
                aggregations=[AggregationType.AVERAGE, AggregationType.PERCENTILE]
            )
        ]
        
        for metric_def in default_metrics:
            self.metric_definitions[metric_def.metric_name] = metric_def
    
    async def start(self) -> None:
        """Start the analytics service"""
        logger.info("Starting Analytics Service")
        
        self.is_running = True
        
        # Start background cache cleanup task
        cache_cleanup_task = asyncio.create_task(self._cache_cleanup_loop())
        self.background_tasks.append(cache_cleanup_task)
        
        # Start metrics aggregation task
        aggregation_task = asyncio.create_task(self._metrics_aggregation_loop())
        self.background_tasks.append(aggregation_task)
        
        logger.info("✅ Analytics Service started successfully")
    
    async def stop(self) -> None:
        """Stop the analytics service"""
        logger.info("Stopping Analytics Service")
        
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("✅ Analytics Service stopped")
    
    async def track_event(self, event_type: str, 
                         category: EventCategory,
                         user_id: Optional[str] = None,
                         session_id: Optional[str] = None,
                         properties: Dict[str, Any] = None,
                         context: Dict[str, Any] = None) -> str:
        """Track analytics event"""
        
        event_id = str(uuid.uuid4())
        
        event = AnalyticsEvent(
            event_id=event_id,
            event_type=event_type,
            category=category,
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
            properties=properties or {},
            context=context or {}
        )
        
        success = await self.collector.collect_event(event)
        
        if success:
            logger.debug(f"Event tracked: {event_type} ({event_id})")
        else:
            logger.warning(f"Failed to track event: {event_type}")
        
        return event_id
    
    async def register_metric(self, metric_definition -> None: MetricDefinition) -> None:
        """Register custom metric definition"""
        self.metric_definitions[metric_definition.metric_name] = metric_definition
        logger.info(f"Metric registered: {metric_definition.metric_name}")
    
    async def record_metric(self, metric_name: str, 
                          value: Union[int, float],
                          dimensions: Dict[str, str] = None,
                          tags: Dict[str, str] = None,
                          timestamp: Optional[datetime] = None) -> bool:
        """Record custom metric value"""
        
        if metric_name not in self.metric_definitions:
            logger.warning(f"Unknown metric: {metric_name}")
            return False
        
        metric = MetricDataPoint(
            metric_name=metric_name,
            timestamp=timestamp or datetime.now(),
            value=value,
            dimensions=dimensions or {},
            tags=tags or {}
        )
        
        success = await self.metric_storage.store_metric(metric)
        
        if success:
            self.service_stats["total_data_points"] += 1
        
        return success
    
    async def query_metrics(self, metric_names: List[str],
                          start_time: datetime,
                          end_time: datetime,
                          granularity: TimeGranularity = TimeGranularity.HOUR,
                          aggregation: AggregationType = AggregationType.SUM,
                          filters: Dict[str, Any] = None,
                          dimensions: List[str] = None) -> AnalyticsResult:
        """Query metrics with specified parameters"""
        
        query_id = str(uuid.uuid4())
        
        query = AnalyticsQuery(
            query_id=query_id,
            metric_names=metric_names,
            start_time=start_time,
            end_time=end_time,
            granularity=granularity,
            aggregation=aggregation,
            filters=filters or {},
            dimensions=dimensions or []
        )
        
        # Check cache first
        cache_key = self._generate_cache_key(query)
        cached_result = self.query_cache.get(cache_key)
        
        if cached_result and self._is_cache_valid(cached_result):
            self.service_stats["cache_hits"] += 1
            logger.debug(f"Cache hit for query {query_id}")
            return cached_result["result"]
        
        # Execute query
        self.service_stats["cache_misses"] += 1
        result = await self.metric_storage.query_metrics(query)
        
        # Cache result
        self.query_cache[cache_key] = {
            "result": result,
            "timestamp": datetime.now()
        }
        
        self.service_stats["queries_executed"] += 1
        logger.info(f"Query executed: {query_id} ({result.execution_time_ms:.1f}ms)")
        
        return result
    
    async def create_dashboard(self, name: str, description: str, 
                             owner_id: str, widgets: List[Dict[str, Any]],
                             layout: Dict[str, Any] = None) -> Dashboard:
        """Create analytics dashboard"""
        
        dashboard_id = str(uuid.uuid4())
        
        dashboard = Dashboard(
            dashboard_id=dashboard_id,
            name=name,
            description=description,
            owner_id=owner_id,
            widgets=widgets,
            layout=layout or {}
        )
        
        self.dashboards[dashboard_id] = dashboard
        self.service_stats["dashboards_created"] += 1
        
        logger.info(f"Dashboard created: {dashboard_id} ({name})")
        return dashboard
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard by ID"""
        return self.dashboards.get(dashboard_id)
    
    async def update_dashboard(self, dashboard_id: str, 
                             updates: Dict[str, Any]) -> bool:
        """Update dashboard configuration"""
        
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            return False
        
        # Update allowed fields
        allowed_fields = ["name", "description", "widgets", "layout", "filters", "refresh_interval_seconds"]
        
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(dashboard, field, value)
        
        dashboard.updated_at = datetime.now()
        
        logger.info(f"Dashboard updated: {dashboard_id}")
        return True
    
    async def get_real_time_metrics(self, metric_names: List[str],
                                   duration_minutes: int = 5) -> Dict[str, Any]:
        """Get real-time metrics for the last N minutes"""
        
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=duration_minutes)
        
        result = await self.query_metrics(
            metric_names=metric_names,
            start_time=start_time,
            end_time=end_time,
            granularity=TimeGranularity.MINUTE,
            aggregation=AggregationType.SUM
        )
        
        return {
            "metrics": result.data_points,
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_minutes": duration_minutes
            },
            "total_value": result.aggregated_value
        }
    
    async def get_trending_metrics(self, metric_name: str,
                                 days: int = 7) -> Dict[str, Any]:
        """Get trending analysis for a metric"""
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Get daily data
        result = await self.query_metrics(
            metric_names=[metric_name],
            start_time=start_time,
            end_time=end_time,
            granularity=TimeGranularity.DAY,
            aggregation=AggregationType.SUM
        )
        
        # Calculate trend
        values = [point["value"] for point in result.data_points]
        
        if len(values) >= 2:
            # Simple linear trend calculation
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            first_avg = statistics.mean(first_half) if first_half else 0
            second_avg = statistics.mean(second_half) if second_half else 0
            
            trend_percentage = ((second_avg - first_avg) / max(first_avg, 1)) * 100
            trend_direction = "up" if trend_percentage > 5 else "down" if trend_percentage < -5 else "stable"
        else:
            trend_percentage = 0
            trend_direction = "stable"
        
        return {
            "metric_name": metric_name,
            "time_period_days": days,
            "data_points": result.data_points,
            "trend": {
                "direction": trend_direction,
                "percentage_change": trend_percentage,
                "total_value": sum(values) if values else 0,
                "average_daily": statistics.mean(values) if values else 0
            }
        }
    
    async def get_user_analytics(self, user_id: str,
                               days: int = 30) -> Dict[str, Any]:
        """Get analytics for specific user"""
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Query user engagement metrics
        engagement_result = await self.query_metrics(
            metric_names=["user_engagement"],
            start_time=start_time,
            end_time=end_time,
            granularity=TimeGranularity.DAY,
            aggregation=AggregationType.SUM,
            filters={"user_id": user_id}
        )
        
        # Calculate user insights
        engagement_data = engagement_result.data_points
        active_days = len([point for point in engagement_data if point["value"] > 0])
        total_engagements = sum(point["value"] for point in engagement_data)
        
        return {
            "user_id": user_id,
            "time_period_days": days,
            "engagement_summary": {
                "total_engagements": total_engagements,
                "active_days": active_days,
                "engagement_rate": (active_days / days) * 100,
                "avg_daily_engagements": total_engagements / max(active_days, 1)
            },
            "daily_engagement": engagement_data
        }
    
    def _generate_cache_key(self, query: AnalyticsQuery) -> str:
        """Generate cache key for query"""
        query_str = f"{','.join(query.metric_names)}_{query.start_time}_{query.end_time}_{query.granularity.value}_{query.aggregation.value}_{str(query.filters)}"
        return hashlib.md5(query_str.encode()).hexdigest()
    
    def _is_cache_valid(self, cached_item: Dict[str, Any]) -> bool:
        """Check if cached item is still valid"""
        cache_age = (datetime.now() - cached_item["timestamp"]).total_seconds()
        return cache_age < self.cache_ttl_seconds
    
    async def _cache_cleanup_loop(self) -> None:
        """Background task to clean up expired cache entries"""
        while self.is_running:
            try:
                current_time = datetime.now()
                expired_keys = []
                
                for cache_key, cached_item in self.query_cache.items():
                    cache_age = (current_time - cached_item["timestamp"]).total_seconds()
                    if cache_age > self.cache_ttl_seconds:
                        expired_keys.append(cache_key)
                
                # Remove expired entries
                for key in expired_keys:
                    self.query_cache.pop(key, None)
                
                if expired_keys:
                    logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                
                await asyncio.sleep(300)  # Run cleanup every 5 minutes
                
            except Exception as e:
                logger.error(f"Cache cleanup error: {str(e)}")
    
    async def _metrics_aggregation_loop(self) -> None:
        """Background task for metrics aggregation and pre-calculation"""
        while self.is_running:
            try:
                # Pre-calculate common aggregations
                current_time = datetime.now()
                
                # Daily aggregations
                start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                
                for metric_name in ["user_engagement", "content_performance"]:
                    if metric_name in self.metric_definitions:
                        await self.query_metrics(
                            metric_names=[metric_name],
                            start_time=start_time,
                            end_time=current_time,
                            granularity=TimeGranularity.HOUR,
                            aggregation=AggregationType.SUM
                        )
                
                await asyncio.sleep(3600)  # Run aggregation every hour
                
            except Exception as e:
                logger.error(f"Metrics aggregation error: {str(e)}")
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        
        collector_stats = self.collector.processing_stats
        
        return {
            **self.service_stats,
            "service_id": self.service_id,
            "collector_stats": collector_stats,
            "metric_definitions_count": len(self.metric_definitions),
            "dashboards_count": len(self.dashboards),
            "query_cache_size": len(self.query_cache),
            "cache_hit_ratio": (self.service_stats["cache_hits"] / 
                              max(1, self.service_stats["cache_hits"] + self.service_stats["cache_misses"])) * 100,
            "is_running": self.is_running
        }

# Usage Example and Template Testing
async def main() -> None:
    """Example usage of Analytics Service Template"""
    
    # Initialize the service
    service = AnalyticsService(config={
        "max_data_points": 100000,
        "cache_ttl_seconds": 300
    })
    
    try:
        # Start the service
        await service.start()
        
        # Track some events
        await service.track_event(
            event_type="page_view",
            category=EventCategory.USER_ACTION,
            user_id="user_123",
            session_id="session_456",
            properties={
                "page": "/dashboard",
                "load_time": 250,
                "source": "direct"
            }
        )
        
        await service.track_event(
            event_type="content_view",
            category=EventCategory.CONTENT_INTERACTION,
            user_id="user_123",
            properties={
                "content_id": "video_789",
                "view_duration": 45,
                "engagement_score": 8.5
            }
        )
        
        await service.track_event(
            event_type="user_signup",
            category=EventCategory.BUSINESS_METRIC,
            user_id="user_124",
            properties={
                "signup_source": "organic",
                "plan_type": "premium"
            }
        )
        
        print("✅ Events tracked successfully")
        
        # Record custom metrics
        await service.record_metric(
            metric_name="content_performance",
            value=8.5,
            dimensions={"content_id": "video_789", "metric_type": "engagement"},
            tags={"content_type": "video"}
        )
        
        await service.record_metric(
            metric_name="system_performance",
            value=120,
            dimensions={"service": "api", "operation": "get_content"},
            tags={"region": "us-east-1"}
        )
        
        print("✅ Custom metrics recorded")
        
        # Wait for event processing
        await asyncio.sleep(1.0)
        
        # Query metrics
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        
        result = await service.query_metrics(
            metric_names=["user_engagement"],
            start_time=start_time,
            end_time=end_time,
            granularity=TimeGranularity.MINUTE,
            aggregation=AggregationType.SUM
        )
        
        print(f"✅ Query executed: {len(result.data_points)} data points found")
        print(f"   Execution time: {result.execution_time_ms:.1f}ms")
        print(f"   Aggregated value: {result.aggregated_value}")
        
        # Get real-time metrics
        real_time = await service.get_real_time_metrics(
            metric_names=["user_engagement"],
            duration_minutes=5
        )
        
        print(f"✅ Real-time metrics: {real_time['total_value']} total engagements")
        
        # Get trending analysis
        trending = await service.get_trending_metrics(
            metric_name="user_engagement",
            days=7
        )
        
        print(f"✅ Trending analysis: {trending['trend']['direction']} trend")
        print(f"   Change: {trending['trend']['percentage_change']:.1f}%")
        
        # Get user analytics
        user_analytics = await service.get_user_analytics(
            user_id="user_123",
            days=30
        )
        
        print(f"✅ User analytics for user_123:")
        print(f"   Total engagements: {user_analytics['engagement_summary']['total_engagements']}")
        print(f"   Engagement rate: {user_analytics['engagement_summary']['engagement_rate']:.1f}%")
        
        # Create dashboard
        dashboard = await service.create_dashboard(
            name="Content Performance Dashboard",
            description="Dashboard for monitoring content performance metrics",
            owner_id="admin",
            widgets=[
                {
                    "type": "line_chart",
                    "title": "User Engagement Over Time",
                    "metric": "user_engagement",
                    "time_range": "24h"
                },
                {
                    "type": "gauge",
                    "title": "Average Content Performance",
                    "metric": "content_performance",
                    "aggregation": "average"
                }
            ]
        )
        
        print(f"✅ Dashboard created: {dashboard.dashboard_id}")
        
        # Get service statistics
        stats = service.get_service_stats()
        print(f"\n📊 Service Statistics:")
        print(f"  Queries Executed: {stats['queries_executed']}")
        print(f"  Cache Hit Ratio: {stats['cache_hit_ratio']:.1f}%")
        print(f"  Total Data Points: {stats['total_data_points']}")
        print(f"  Events Collected: {stats['collector_stats']['events_collected']}")
        print(f"  Events Processed: {stats['collector_stats']['events_processed']}")
        print(f"  Metrics Generated: {stats['collector_stats']['metrics_generated']}")
        print(f"  Dashboards Created: {stats['dashboards_created']}")
        
        print(f"\n✅ Analytics Service demonstration completed!")
        
    except Exception as e:
        logger.error(f"Error in analytics service demo: {str(e)}")
    finally:
        # Stop the service
        await service.stop()

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
    print("📊 Analytics Service Template demonstration completed!")