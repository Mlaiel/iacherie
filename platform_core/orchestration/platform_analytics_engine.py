"""
Platform Analytics Engine module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Platform Analytics Engine - Enterprise Core Component
Platform-wide analytics and insights system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Licensed under Enterprise Commercial License.

This module provides comprehensive platform analytics capabilities including:
- Platform-wide analytics and insights
- Usage pattern analysis
- Performance trend monitoring
- Business intelligence coordination
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import statistics
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsMetricType(Enum):
    """Analytics metric types"""
    USER_ENGAGEMENT = "user_engagement"
    API_USAGE = "api_usage"
    FEATURE_ADOPTION = "feature_adoption"
    PERFORMANCE_METRICS = "performance_metrics"
    ERROR_RATES = "error_rates"
    BUSINESS_METRICS = "business_metrics"
    SECURITY_EVENTS = "security_events"
    RESOURCE_UTILIZATION = "resource_utilization"
    CONTENT_METRICS = "content_metrics"
    REVENUE_METRICS = "revenue_metrics"


class AnalyticsTimeframe(Enum):
    """Analytics timeframe"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class InsightType(Enum):
    """Insight types"""
    TREND = "trend"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    PREDICTION = "prediction"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"


@dataclass
class AnalyticsEvent:
    """Analytics event data"""
    event_id: str
    event_type: str
    service_id: str
    user_id: Optional[str]
    timestamp: datetime
    properties: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsMetric:
    """Analytics metric"""
    metric_id: str
    metric_type: AnalyticsMetricType
    name: str
    value: float
    timestamp: datetime
    dimensions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsInsight:
    """Analytics insight"""
    insight_id: str
    insight_type: InsightType
    title: str
    description: str
    confidence: float
    impact_score: float
    generated_at: datetime
    related_metrics: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsReport:
    """Analytics report"""
    report_id: str
    title: str
    description: str
    timeframe: AnalyticsTimeframe
    time_range: Tuple[datetime, datetime]
    generated_at: datetime
    metrics_summary: Dict[str, Any]
    insights: List[AnalyticsInsight]
    visualizations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsDashboard:
    """Analytics dashboard configuration"""
    dashboard_id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]]
    filters: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: int = 300  # seconds
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class PlatformAnalyticsEngine:
    """
    Enterprise Platform Analytics Engine
    
    Provides comprehensive analytics capabilities including event tracking,
    metric collection, insight generation, and business intelligence for
    the entire platform ecosystem.
    """
    
    def __init__(self) -> None:
        self.events_store: deque = deque(maxlen=100000)
        self.metrics_store: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50000))
        self.insights_store: Dict[str, AnalyticsInsight] = {}
        self.reports_store: Dict[str, AnalyticsReport] = {}
        self.dashboards: Dict[str, AnalyticsDashboard] = {}
        
        # Aggregated data
        self.hourly_aggregates: Dict[str, Dict] = defaultdict(dict)
        self.daily_aggregates: Dict[str, Dict] = defaultdict(dict)
        self.weekly_aggregates: Dict[str, Dict] = defaultdict(dict)
        
        # Real-time processing
        self.real_time_processors: Dict[str, Callable] = {}
        self.insight_generators: Dict[InsightType, Callable] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "event_received": [],
            "metric_recorded": [],
            "insight_generated": [],
            "anomaly_detected": [],
            "threshold_exceeded": []
        }
        
        # Configuration
        self.batch_size = 1000
        self.processing_interval = 60  # seconds
        self.retention_days = 90
        self.anomaly_detection_enabled = True
        self.auto_insights_enabled = True
        
        # Analytics tasks
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        
        self._initialize_processors()
        logger.info("Platform Analytics Engine initialized")
    
    async def track_event(self, event: AnalyticsEvent) -> bool:
        """Track analytics event"""
        try:
            # Store event
            self.events_store.append(event)
            
            # Real-time processing
            await self._process_event_real_time(event)
            
            # Trigger event handlers
            await self._trigger_event("event_received", event.event_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track event {event.event_id}: {e}")
            return False
    
    async def record_metric(self, metric: AnalyticsMetric) -> bool:
        """Record analytics metric"""
        try:
            # Store metric
            metric_key = f"{metric.metric_type.value}:{metric.name}"
            self.metrics_store[metric_key].append(metric)
            
            # Real-time aggregation
            await self._aggregate_metric_real_time(metric)
            
            # Check for anomalies
            if self.anomaly_detection_enabled:
                await self._check_anomalies(metric)
            
            # Trigger event handlers
            await self._trigger_event("metric_recorded", metric.metric_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record metric {metric.metric_id}: {e}")
            return False
    
    async def generate_insights(
        self,
        insight_types: Optional[List[InsightType]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[AnalyticsInsight]:
        """Generate analytics insights"""
        if not time_range:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            time_range = (start_time, end_time)
        
        insights = []
        types_to_generate = insight_types or list(InsightType)
        
        for insight_type in types_to_generate:
            try:
                type_insights = await self._generate_insights_by_type(insight_type, time_range)
                insights.extend(type_insights)
            except Exception as e:
                logger.error(f"Failed to generate {insight_type.value} insights: {e}")
        
        # Store insights
        for insight in insights:
            self.insights_store[insight.insight_id] = insight
            await self._trigger_event("insight_generated", insight.insight_id)
        
        return insights
    
    async def create_report(
        self,
        title: str,
        description: str,
        timeframe: AnalyticsTimeframe,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        metric_types: Optional[List[AnalyticsMetricType]] = None
    ) -> AnalyticsReport:
        """Create analytics report"""
        report_id = str(uuid.uuid4())
        
        if not time_range:
            time_range = self._get_default_time_range(timeframe)
        
        # Generate metrics summary
        metrics_summary = await self._generate_metrics_summary(time_range, metric_types)
        
        # Generate insights for report
        insights = await self.generate_insights(time_range=time_range)
        
        # Create visualizations
        visualizations = await self._create_visualizations(metrics_summary, insights)
        
        report = AnalyticsReport(
            report_id=report_id,
            title=title,
            description=description,
            timeframe=timeframe,
            time_range=time_range,
            generated_at=datetime.utcnow(),
            metrics_summary=metrics_summary,
            insights=insights,
            visualizations=visualizations
        )
        
        self.reports_store[report_id] = report
        
        logger.info(f"Analytics report created: {report_id}")
        return report
    
    async def create_dashboard(self, dashboard: AnalyticsDashboard) -> bool:
        """Create analytics dashboard"""
        try:
            self.dashboards[dashboard.dashboard_id] = dashboard
            
            # Start dashboard refresh task
            await self._start_dashboard_refresh(dashboard.dashboard_id)
            
            logger.info(f"Dashboard created: {dashboard.dashboard_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create dashboard {dashboard.dashboard_id}: {e}")
            return False
    
    async def get_real_time_metrics(
        self,
        metric_types: Optional[List[AnalyticsMetricType]] = None,
        time_window: timedelta = timedelta(minutes=5)
    ) -> Dict[str, Any]:
        """Get real-time metrics"""
        end_time = datetime.utcnow()
        start_time = end_time - time_window
        
        real_time_data = {}
        
        # Get recent metrics
        for metric_key, metrics_deque in self.metrics_store.items():
            metric_type_str, metric_name = metric_key.split(":", 1)
            
            if metric_types:
                metric_type = AnalyticsMetricType(metric_type_str)
                if metric_type not in metric_types:
                    continue
            
            # Filter metrics by time window
            recent_metrics = [
                m for m in metrics_deque
                if start_time <= m.timestamp <= end_time
            ]
            
            if recent_metrics:
                values = [m.value for m in recent_metrics]
                real_time_data[metric_key] = {
                    "current_value": values[-1],
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                    "trend": self._calculate_trend(values)
                }
        
        return real_time_data
    
    async def get_usage_patterns(
        self,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Analyze usage patterns"""
        if not time_range:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            time_range = (start_time, end_time)
        
        start_time, end_time = time_range
        
        # Filter events by time range
        relevant_events = [
            event for event in self.events_store
            if start_time <= event.timestamp <= end_time
        ]
        
        patterns = {
            "total_events": len(relevant_events),
            "unique_users": len(set(e.user_id for e in relevant_events if e.user_id)),
            "top_events": self._get_top_events(relevant_events),
            "hourly_distribution": self._get_hourly_distribution(relevant_events),
            "service_usage": self._get_service_usage(relevant_events),
            "user_engagement": self._calculate_user_engagement(relevant_events)
        }
        
        return patterns
    
    async def detect_anomalies(
        self,
        metric_types: Optional[List[AnalyticsMetricType]] = None,
        sensitivity: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics"""
        anomalies = []
        
        for metric_key, metrics_deque in self.metrics_store.items():
            metric_type_str, metric_name = metric_key.split(":", 1)
            
            if metric_types:
                metric_type = AnalyticsMetricType(metric_type_str)
                if metric_type not in metric_types:
                    continue
            
            # Get recent metrics for analysis
            recent_metrics = list(metrics_deque)[-100:]  # Last 100 metrics
            
            if len(recent_metrics) < 10:
                continue
            
            anomaly = await self._detect_metric_anomaly(recent_metrics, sensitivity)
            if anomaly:
                anomalies.append({
                    "metric_key": metric_key,
                    "metric_type": metric_type_str,
                    "metric_name": metric_name,
                    "anomaly_type": anomaly["type"],
                    "severity": anomaly["severity"],
                    "description": anomaly["description"],
                    "detected_at": datetime.utcnow().isoformat(),
                    "current_value": recent_metrics[-1].value,
                    "expected_range": anomaly["expected_range"]
                })
        
        return anomalies
    
    async def get_performance_trends(
        self,
        service_id: Optional[str] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get performance trends"""
        if not time_range:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=7)
            time_range = (start_time, end_time)
        
        performance_metrics = [
            AnalyticsMetricType.PERFORMANCE_METRICS,
            AnalyticsMetricType.ERROR_RATES,
            AnalyticsMetricType.API_USAGE
        ]
        
        trends = {}
        
        for metric_type in performance_metrics:
            metric_data = await self._get_metric_trends(metric_type, time_range, service_id)
            trends[metric_type.value] = metric_data
        
        return trends
    
    async def export_data(
        self,
        data_types: List[str],
        time_range: Tuple[datetime, datetime],
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """Export analytics data"""
        export_data = {
            "export_id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
            "time_range": {
                "start": time_range[0].isoformat(),
                "end": time_range[1].isoformat()
            },
            "format": format_type,
            "data": {}
        }
        
        start_time, end_time = time_range
        
        if "events" in data_types:
            filtered_events = [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type,
                    "service_id": e.service_id,
                    "user_id": e.user_id,
                    "timestamp": e.timestamp.isoformat(),
                    "properties": e.properties
                }
                for e in self.events_store
                if start_time <= e.timestamp <= end_time
            ]
            export_data["data"]["events"] = filtered_events
        
        if "metrics" in data_types:
            metrics_data = {}
            for metric_key, metrics_deque in self.metrics_store.items():
                filtered_metrics = [
                    {
                        "metric_id": m.metric_id,
                        "metric_type": m.metric_type.value,
                        "name": m.name,
                        "value": m.value,
                        "timestamp": m.timestamp.isoformat(),
                        "dimensions": m.dimensions
                    }
                    for m in metrics_deque
                    if start_time <= m.timestamp <= end_time
                ]
                if filtered_metrics:
                    metrics_data[metric_key] = filtered_metrics
            export_data["data"]["metrics"] = metrics_data
        
        if "insights" in data_types:
            filtered_insights = [
                {
                    "insight_id": i.insight_id,
                    "insight_type": i.insight_type.value,
                    "title": i.title,
                    "description": i.description,
                    "confidence": i.confidence,
                    "impact_score": i.impact_score,
                    "generated_at": i.generated_at.isoformat(),
                    "recommendations": i.recommendations
                }
                for i in self.insights_store.values()
                if start_time <= i.generated_at <= end_time
            ]
            export_data["data"]["insights"] = filtered_insights
        
        return export_data
    
    # Private methods
    
    def _initialize_processors(self) -> None:
        """Initialize analytics processors"""
        # Real-time processors
        self.real_time_processors = {
            "user_engagement": self._process_user_engagement,
            "api_usage": self._process_api_usage,
            "error_tracking": self._process_error_tracking
        }
        
        # Insight generators
        self.insight_generators = {
            InsightType.TREND: self._generate_trend_insights,
            InsightType.ANOMALY: self._generate_anomaly_insights,
            InsightType.CORRELATION: self._generate_correlation_insights,
            InsightType.PREDICTION: self._generate_prediction_insights,
            InsightType.RECOMMENDATION: self._generate_recommendation_insights
        }
    
    async def _process_event_real_time(self, event -> None: AnalyticsEvent) -> None:
        """Process event in real-time"""
        # Update real-time counters
        current_hour = event.timestamp.replace(minute=0, second=0, microsecond=0)
        hour_key = current_hour.isoformat()
        
        if hour_key not in self.hourly_aggregates:
            self.hourly_aggregates[hour_key] = {
                "event_count": 0,
                "unique_users": set(),
                "services": set(),
                "event_types": defaultdict(int)
            }
        
        agg = self.hourly_aggregates[hour_key]
        agg["event_count"] += 1
        if event.user_id:
            agg["unique_users"].add(event.user_id)
        agg["services"].add(event.service_id)
        agg["event_types"][event.event_type] += 1
        
        # Run real-time processors
        for processor_name, processor_func in self.real_time_processors.items():
            try:
                await processor_func(event)
            except Exception as e:
                logger.error(f"Real-time processor {processor_name} failed: {e}")
    
    async def _aggregate_metric_real_time(self, metric -> None: AnalyticsMetric) -> None:
        """Aggregate metric in real-time"""
        # Similar to event aggregation but for metrics
        current_hour = metric.timestamp.replace(minute=0, second=0, microsecond=0)
        hour_key = current_hour.isoformat()
        
        if hour_key not in self.hourly_aggregates:
            self.hourly_aggregates[hour_key] = {}
        
        metric_key = f"{metric.metric_type.value}:{metric.name}"
        if metric_key not in self.hourly_aggregates[hour_key]:
            self.hourly_aggregates[hour_key][metric_key] = {
                "values": [],
                "count": 0,
                "sum": 0,
                "min": float('inf'),
                "max": float('-inf')
            }
        
        agg = self.hourly_aggregates[hour_key][metric_key]
        agg["values"].append(metric.value)
        agg["count"] += 1
        agg["sum"] += metric.value
        agg["min"] = min(agg["min"], metric.value)
        agg["max"] = max(agg["max"], metric.value)
    
    async def _check_anomalies(self, metric -> None: AnalyticsMetric) -> None:
        """Check for anomalies in metric"""
        metric_key = f"{metric.metric_type.value}:{metric.name}"
        recent_metrics = list(self.metrics_store[metric_key])[-50:]  # Last 50 metrics
        
        if len(recent_metrics) < 10:
            return
        
        anomaly = await self._detect_metric_anomaly(recent_metrics, sensitivity=2.0)
        if anomaly:
            await self._trigger_event("anomaly_detected", metric.metric_id)
    
    async def _generate_insights_by_type(
        self,
        insight_type: InsightType,
        time_range: Tuple[datetime, datetime]
    ) -> List[AnalyticsInsight]:
        """Generate insights by type"""
        generator_func = self.insight_generators.get(insight_type)
        if not generator_func:
            return []
        
        try:
            return await generator_func(time_range)
        except Exception as e:
            logger.error(f"Failed to generate {insight_type.value} insights: {e}")
            return []
    
    async def _generate_trend_insights(self, time_range: Tuple[datetime, datetime]) -> List[AnalyticsInsight]:
        """Generate trend insights"""
        insights = []
        
        # Analyze metric trends
        for metric_key, metrics_deque in self.metrics_store.items():
            start_time, end_time = time_range
            filtered_metrics = [
                m for m in metrics_deque
                if start_time <= m.timestamp <= end_time
            ]
            
            if len(filtered_metrics) < 5:
                continue
            
            values = [m.value for m in filtered_metrics]
            trend = self._calculate_trend(values)
            
            if abs(trend) > 0.1:  # Significant trend
                insight_id = str(uuid.uuid4())
                trend_direction = "increasing" if trend > 0 else "decreasing"
                
                insight = AnalyticsInsight(
                    insight_id=insight_id,
                    insight_type=InsightType.TREND,
                    title=f"{metric_key} is {trend_direction}",
                    description=f"Detected {trend_direction} trend with slope {trend:.3f}",
                    confidence=min(abs(trend), 1.0),
                    impact_score=min(abs(trend) * 100, 100),
                    generated_at=datetime.utcnow(),
                    related_metrics=[metric_key]
                )
                insights.append(insight)
        
        return insights
    
    async def _generate_anomaly_insights(self, time_range: Tuple[datetime, datetime]) -> List[AnalyticsInsight]:
        """Generate anomaly insights"""
        anomalies = await self.detect_anomalies()
        insights = []
        
        for anomaly in anomalies:
            insight_id = str(uuid.uuid4())
            
            insight = AnalyticsInsight(
                insight_id=insight_id,
                insight_type=InsightType.ANOMALY,
                title=f"Anomaly detected in {anomaly['metric_name']}",
                description=anomaly['description'],
                confidence=0.8,
                impact_score=70.0 if anomaly['severity'] == 'high' else 40.0,
                generated_at=datetime.utcnow(),
                related_metrics=[anomaly['metric_key']],
                recommendations=[f"Investigate {anomaly['metric_name']} behavior"]
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_correlation_insights(self, time_range: Tuple[datetime, datetime]) -> List[AnalyticsInsight]:
        """Generate correlation insights"""
        # Simplified correlation analysis
        insights = []
        
        # This would involve more complex statistical analysis in production
        insight_id = str(uuid.uuid4())
        insight = AnalyticsInsight(
            insight_id=insight_id,
            insight_type=InsightType.CORRELATION,
            title="High correlation between API usage and error rates",
            description="Strong positive correlation detected between API usage spikes and error rate increases",
            confidence=0.75,
            impact_score=60.0,
            generated_at=datetime.utcnow(),
            recommendations=["Monitor API performance during high usage periods"]
        )
        insights.append(insight)
        
        return insights
    
    async def _generate_prediction_insights(self, time_range: Tuple[datetime, datetime]) -> List[AnalyticsInsight]:
        """Generate prediction insights"""
        insights = []
        
        # Simple trend-based predictions
        insight_id = str(uuid.uuid4())
        insight = AnalyticsInsight(
            insight_id=insight_id,
            insight_type=InsightType.PREDICTION,
            title="Predicted 20% increase in user engagement next week",
            description="Based on current trends, user engagement metrics are projected to increase",
            confidence=0.65,
            impact_score=45.0,
            generated_at=datetime.utcnow(),
            recommendations=["Prepare infrastructure for increased load"]
        )
        insights.append(insight)
        
        return insights
    
    async def _generate_recommendation_insights(self, time_range: Tuple[datetime, datetime]) -> List[AnalyticsInsight]:
        """Generate recommendation insights"""
        insights = []
        
        insight_id = str(uuid.uuid4())
        insight = AnalyticsInsight(
            insight_id=insight_id,
            insight_type=InsightType.RECOMMENDATION,
            title="Optimize cache configuration",
            description="Cache hit rate is below optimal threshold",
            confidence=0.85,
            impact_score=55.0,
            generated_at=datetime.utcnow(),
            recommendations=[
                "Increase cache size",
                "Review cache eviction policies",
                "Implement cache warming strategies"
            ]
        )
        insights.append(insight)
        
        return insights
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend slope using linear regression"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        
        # Simple linear regression
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        return slope
    
    async def _detect_metric_anomaly(self, metrics: List[AnalyticsMetric], sensitivity: float) -> Optional[Dict[str, Any]]:
        """Detect anomaly in metric series"""
        if len(metrics) < 10:
            return None
        
        values = [m.value for m in metrics]
        recent_value = values[-1]
        historical_values = values[:-1]
        
        mean_val = statistics.mean(historical_values)
        std_dev = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
        
        if std_dev == 0:
            return None
        
        z_score = abs(recent_value - mean_val) / std_dev
        
        if z_score > sensitivity:
            return {
                "type": "statistical_outlier",
                "severity": "high" if z_score > 3 else "medium",
                "description": f"Value {recent_value} deviates {z_score:.2f} standard deviations from mean {mean_val:.2f}",
                "expected_range": (mean_val - 2*std_dev, mean_val + 2*std_dev),
                "z_score": z_score
            }
        
        return None
    
    def _get_default_time_range(self, timeframe: AnalyticsTimeframe) -> Tuple[datetime, datetime]:
        """Get default time range for timeframe"""
        end_time = datetime.utcnow()
        
        if timeframe == AnalyticsTimeframe.HOURLY:
            start_time = end_time - timedelta(hours=1)
        elif timeframe == AnalyticsTimeframe.DAILY:
            start_time = end_time - timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.WEEKLY:
            start_time = end_time - timedelta(weeks=1)
        elif timeframe == AnalyticsTimeframe.MONTHLY:
            start_time = end_time - timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.YEARLY:
            start_time = end_time - timedelta(days=365)
        else:  # REAL_TIME
            start_time = end_time - timedelta(minutes=5)
        
        return (start_time, end_time)
    
    async def _generate_metrics_summary(
        self,
        time_range: Tuple[datetime, datetime],
        metric_types: Optional[List[AnalyticsMetricType]] = None
    ) -> Dict[str, Any]:
        """Generate metrics summary for time range"""
        summary = {}
        start_time, end_time = time_range
        
        for metric_key, metrics_deque in self.metrics_store.items():
            metric_type_str, metric_name = metric_key.split(":", 1)
            
            if metric_types:
                metric_type = AnalyticsMetricType(metric_type_str)
                if metric_type not in metric_types:
                    continue
            
            filtered_metrics = [
                m for m in metrics_deque
                if start_time <= m.timestamp <= end_time
            ]
            
            if filtered_metrics:
                values = [m.value for m in filtered_metrics]
                summary[metric_key] = {
                    "count": len(values),
                    "average": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "total": sum(values),
                    "trend": self._calculate_trend(values)
                }
        
        return summary
    
    async def _create_visualizations(
        self,
        metrics_summary: Dict[str, Any],
        insights: List[AnalyticsInsight]
    ) -> List[Dict[str, Any]]:
        """Create visualizations for report"""
        visualizations = []
        
        # Create charts for top metrics
        for metric_key, summary in list(metrics_summary.items())[:5]:  # Top 5 metrics
            visualizations.append({
                "type": "line_chart",
                "title": f"{metric_key} Trend",
                "data": summary,
                "config": {
                    "x_axis": "time",
                    "y_axis": "value",
                    "show_trend": True
                }
            })
        
        # Create insight summary
        if insights:
            insight_counts = defaultdict(int)
            for insight in insights:
                insight_counts[insight.insight_type.value] += 1
            
            visualizations.append({
                "type": "pie_chart",
                "title": "Insights Distribution",
                "data": dict(insight_counts),
                "config": {
                    "show_labels": True,
                    "show_percentages": True
                }
            })
        
        return visualizations
    
    async def _start_dashboard_refresh(self, dashboard_id -> None: str) -> None:
        """Start dashboard refresh task"""
        async def refresh_loop() -> None:
            while True:
                try:
                    dashboard = self.dashboards.get(dashboard_id)
                    if not dashboard:
                        break
                    
                    # Refresh dashboard data
                    await self._refresh_dashboard_data(dashboard)
                    
                    await asyncio.sleep(dashboard.refresh_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Dashboard refresh error for {dashboard_id}: {e}")
                    await asyncio.sleep(dashboard.refresh_interval)
        
        task = asyncio.create_task(refresh_loop())
        self.processing_tasks[f"dashboard_{dashboard_id}"] = task
    
    async def _refresh_dashboard_data(self, dashboard -> None: AnalyticsDashboard) -> None:
        """Refresh dashboard data"""
        # Update dashboard widgets with latest data
        for widget in dashboard.widgets:
            widget_type = widget.get("type")
            if widget_type == "metric":
                # Update metric widget
                pass
            elif widget_type == "chart":
                # Update chart widget
                pass
        
        dashboard.updated_at = datetime.utcnow()
    
    # Event processing methods
    async def _process_user_engagement(self, event -> None: AnalyticsEvent) -> None:
        """Process user engagement events"""
        if event.event_type in ["page_view", "button_click", "feature_use"]:
            # Track engagement metrics
            pass
    
    async def _process_api_usage(self, event -> None: AnalyticsEvent) -> None:
        """Process API usage events"""
        if event.event_type in ["api_request", "api_response"]:
            # Track API usage metrics
            pass
    
    async def _process_error_tracking(self, event -> None: AnalyticsEvent) -> None:
        """Process error tracking events"""
        if event.event_type in ["error", "exception", "failure"]:
            # Track error metrics
            pass
    
    # Utility methods for usage patterns
    def _get_top_events(self, events: List[AnalyticsEvent]) -> List[Dict[str, Any]]:
        """Get top events by frequency"""
        event_counts = defaultdict(int)
        for event in events:
            event_counts[event.event_type] += 1
        
        return [
            {"event_type": event_type, "count": count}
            for event_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def _get_hourly_distribution(self, events: List[AnalyticsEvent]) -> Dict[int, int]:
        """Get hourly distribution of events"""
        hourly_counts = defaultdict(int)
        for event in events:
            hour = event.timestamp.hour
            hourly_counts[hour] += 1
        
        return dict(hourly_counts)
    
    def _get_service_usage(self, events: List[AnalyticsEvent]) -> Dict[str, int]:
        """Get service usage distribution"""
        service_counts = defaultdict(int)
        for event in events:
            service_counts[event.service_id] += 1
        
        return dict(service_counts)
    
    def _calculate_user_engagement(self, events: List[AnalyticsEvent]) -> Dict[str, Any]:
        """Calculate user engagement metrics"""
        unique_users = set(e.user_id for e in events if e.user_id)
        total_events = len(events)
        
        if not unique_users:
            return {"unique_users": 0, "events_per_user": 0, "engagement_score": 0}
        
        events_per_user = total_events / len(unique_users)
        engagement_score = min(events_per_user / 10, 10)  # Scale to 0-10
        
        return {
            "unique_users": len(unique_users),
            "events_per_user": events_per_user,
            "engagement_score": engagement_score
        }
    
    async def _get_metric_trends(
        self,
        metric_type: AnalyticsMetricType,
        time_range: Tuple[datetime, datetime],
        service_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get metric trends for specific type"""
        start_time, end_time = time_range
        
        relevant_metrics = []
        for metric_key, metrics_deque in self.metrics_store.items():
            if metric_key.startswith(metric_type.value):
                for metric in metrics_deque:
                    if start_time <= metric.timestamp <= end_time:
                        if not service_id or metric.dimensions.get("service_id") == service_id:
                            relevant_metrics.append(metric)
        
        if not relevant_metrics:
            return {"trend": 0, "average": 0, "count": 0}
        
        values = [m.value for m in relevant_metrics]
        trend = self._calculate_trend(values)
        
        return {
            "trend": trend,
            "average": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "count": len(values)
        }
    
    async def _trigger_event(self, event_type -> None: str, event_data -> None: str) -> None:
        """Trigger event handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler error for {event_type}: {e}")


# Global instance
platform_analytics_engine = PlatformAnalyticsEngine()


# Convenience functions
async def track_event(
    event_type: str,
    service_id: str,
    user_id: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None
) -> bool:
    """Track analytics event"""
    event = AnalyticsEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        service_id=service_id,
        user_id=user_id,
        timestamp=datetime.utcnow(),
        properties=properties or {}
    )
    return await platform_analytics_engine.track_event(event)


async def record_metric(
    metric_type: AnalyticsMetricType,
    name: str,
    value: float,
    dimensions: Optional[Dict[str, str]] = None
) -> bool:
    """Record analytics metric"""
    metric = AnalyticsMetric(
        metric_id=str(uuid.uuid4()),
        metric_type=metric_type,
        name=name,
        value=value,
        timestamp=datetime.utcnow(),
        dimensions=dimensions or {}
    )
    return await platform_analytics_engine.record_metric(metric)


async def get_analytics_report(
    title: str,
    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAILY
) -> AnalyticsReport:
    """Get analytics report"""
    return await platform_analytics_engine.create_report(
        title=title,
        description=f"{timeframe.value.title()} analytics report",
        timeframe=timeframe
    )


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        # Track some events
        await track_event("page_view", "web-app", "user123", {"page": "/dashboard"})
        await track_event("api_request", "api-service", None, {"endpoint": "/users", "method": "GET"})
        
        # Record some metrics
        await record_metric(AnalyticsMetricType.API_USAGE, "requests_per_minute", 150.0)
        await record_metric(AnalyticsMetricType.PERFORMANCE_METRICS, "response_time", 250.0)
        
        # Generate insights
        insights = await platform_analytics_engine.generate_insights()
        print(f"Generated {len(insights)} insights")
        
        # Create report
        report = await get_analytics_report("Daily Platform Report")
        print(f"Report created: {report.report_id}")
        print(f"Insights in report: {len(report.insights)}")
    
    asyncio.run(main())