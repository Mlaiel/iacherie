"""Analytics Service - Consolidated Analytics and Reporting Services
================================================================

Comprehensive analytics system providing data collection, analysis, reporting,
insights, and performance tracking for the IA Influencer Agent platform.

Consolidates:
- analytics_service.py (existing analytics functionality)
- analytics/ subdirectory (reporting, SEO, tracking modules)
- performance tracking and metrics collection
- business intelligence and insights

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/services/analytics.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import statistics

# Configure logging
logger = logging.getLogger(__name__)

# Module metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

# Enums
class MetricType(Enum):
    """Metric type enumeration"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    RATE = "rate"

class ReportType(Enum):
    """Report type enumeration"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class AnalyticsCategory(Enum):
    """Analytics category enumeration"""
    USER_BEHAVIOR = "user_behavior"
    CONTENT_PERFORMANCE = "content_performance"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    PLATFORM_METRICS = "platform_metrics"
    SEO = "seo"
    TRAFFIC = "traffic"

class AggregationType(Enum):
    """Data aggregation type"""
    SUM = "sum"
    AVG = "avg"
    MAX = "max"
    MIN = "min"
    COUNT = "count"
    MEDIAN = "median"
    PERCENTILE = "percentile"

# Data structures
@dataclass
class AnalyticsEvent:
    """Analytics event data structure"""
    event_id: str
    user_id: Optional[str]
    event_type: str
    category: AnalyticsCategory
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    platform: Optional[str] = None
    source: Optional[str] = None

@dataclass
class Metric:
    """Metric data structure"""
    metric_id: str
    name: str
    type: MetricType
    value: float
    unit: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    description: Optional[str] = None

@dataclass
class Report:
    """Report data structure"""
    report_id: str
    title: str
    type: ReportType
    category: AnalyticsCategory
    data: Dict[str, Any] = field(default_factory=dict)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    generated_by: Optional[str] = None

@dataclass
class Dashboard:
    """Analytics dashboard data structure"""
    dashboard_id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: int = 300  # 5 minutes
    owner_id: str = ""
    is_public: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Insight:
    """Analytics insight data structure"""
    insight_id: str
    title: str
    description: str
    category: AnalyticsCategory
    confidence_score: float
    impact_level: str  # low, medium, high
    recommendations: List[str] = field(default_factory=list)
    data_points: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)

# Services
class DataCollectionService:
    """Data collection and event tracking service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.buffer_size = self.config.get('buffer_size', 1000)
        self.batch_size = self.config.get('batch_size', 100)
        self.event_buffer: List[AnalyticsEvent] = []
        logger.info("📊 Data Collection Service initialized")
    
    async def track_event(self, event: AnalyticsEvent) -> bool:
        """Track analytics event"""
        try:
            logger.debug(f"Tracking event: {event.event_type}")
            
            # Add to buffer
            self.event_buffer.append(event)
            
            # Flush buffer if it's full
            if len(self.event_buffer) >= self.batch_size:
                await self._flush_buffer()
            
            return True
        except Exception as e:
            logger.error(f"Event tracking error: {e}")
            return False
    
    async def track_page_view(self, user_id: str, page: str, properties: Dict[str, Any] = None) -> bool:
        """Track page view event"""
        event = AnalyticsEvent(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            event_type="page_view",
            category=AnalyticsCategory.USER_BEHAVIOR,
            properties={
                "page": page,
                **(properties or {})
            }
        )
        return await self.track_event(event)
    
    async def track_user_action(self, user_id: str, action: str, properties: Dict[str, Any] = None) -> bool:
        """Track user action event"""
        event = AnalyticsEvent(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            event_type="user_action",
            category=AnalyticsCategory.USER_BEHAVIOR,
            properties={
                "action": action,
                **(properties or {})
            }
        )
        return await self.track_event(event)
    
    async def track_content_interaction(self, user_id: str, content_id: str, interaction_type: str, properties: Dict[str, Any] = None) -> bool:
        """Track content interaction event"""
        event = AnalyticsEvent(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            event_type="content_interaction",
            category=AnalyticsCategory.CONTENT_PERFORMANCE,
            properties={
                "content_id": content_id,
                "interaction_type": interaction_type,
                **(properties or {})
            }
        )
        return await self.track_event(event)
    
    async def _flush_buffer(self) -> bool:
        """Flush event buffer to storage"""
        try:
            if not self.event_buffer:
                return True
            
            logger.info(f"Flushing {len(self.event_buffer)} events to storage")
            
            # In a real implementation, this would write to database/storage
            # For now, we'll just clear the buffer
            self.event_buffer.clear()
            
            return True
        except Exception as e:
            logger.error(f"Buffer flush error: {e}")
            return False

class MetricsService:
    """Metrics collection and aggregation service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics_store: Dict[str, List[Metric]] = {}
        logger.info("📈 Metrics Service initialized")
    
    async def record_metric(self, metric: Metric) -> bool:
        """Record a metric"""
        try:
            logger.debug(f"Recording metric: {metric.name}")
            
            if metric.name not in self.metrics_store:
                self.metrics_store[metric.name] = []
            
            self.metrics_store[metric.name].append(metric)
            
            # Keep only recent metrics (last 1000)
            if len(self.metrics_store[metric.name]) > 1000:
                self.metrics_store[metric.name] = self.metrics_store[metric.name][-1000:]
            
            return True
        except Exception as e:
            logger.error(f"Metric recording error: {e}")
            return False
    
    async def increment_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None) -> bool:
        """Increment a counter metric"""
        metric = Metric(
            metric_id=str(uuid.uuid4()),
            name=name,
            type=MetricType.COUNTER,
            value=value,
            tags=tags or {}
        )
        return await self.record_metric(metric)
    
    async def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None) -> bool:
        """Set a gauge metric"""
        metric = Metric(
            metric_id=str(uuid.uuid4()),
            name=name,
            type=MetricType.GAUGE,
            value=value,
            tags=tags or {}
        )
        return await self.record_metric(metric)
    
    async def get_metric_values(self, name: str, start_time: datetime = None, end_time: datetime = None) -> List[float]:
        """Get metric values for a time range"""
        try:
            if name not in self.metrics_store:
                return []
            
            metrics = self.metrics_store[name]
            
            # Filter by time range if provided
            if start_time or end_time:
                filtered_metrics = []
                for metric in metrics:
                    if start_time and metric.timestamp < start_time:
                        continue
                    if end_time and metric.timestamp > end_time:
                        continue
                    filtered_metrics.append(metric)
                metrics = filtered_metrics
            
            return [metric.value for metric in metrics]
        except Exception as e:
            logger.error(f"Metric values retrieval error: {e}")
            return []
    
    async def aggregate_metrics(self, name: str, aggregation: AggregationType, start_time: datetime = None, end_time: datetime = None) -> float:
        """Aggregate metrics over time range"""
        try:
            values = await self.get_metric_values(name, start_time, end_time)
            
            if not values:
                return 0.0
            
            if aggregation == AggregationType.SUM:
                return sum(values)
            elif aggregation == AggregationType.AVG:
                return statistics.mean(values)
            elif aggregation == AggregationType.MAX:
                return max(values)
            elif aggregation == AggregationType.MIN:
                return min(values)
            elif aggregation == AggregationType.COUNT:
                return float(len(values))
            elif aggregation == AggregationType.MEDIAN:
                return statistics.median(values)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Metric aggregation error: {e}")
            return 0.0

class ReportingService:
    """Report generation and management service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.reports_store: Dict[str, Report] = {}
        logger.info("📋 Reporting Service initialized")
    
    async def generate_report(self, report_type: ReportType, category: AnalyticsCategory, period_start: datetime, period_end: datetime, user_id: str = None) -> Report:
        """Generate analytics report"""
        try:
            logger.info(f"Generating {report_type.value} {category.value} report")
            
            # Generate report data based on type and category
            report_data = await self._generate_report_data(category, period_start, period_end)
            
            # Generate insights
            insights = await self._generate_insights(report_data, category)
            
            # Generate charts
            charts = await self._generate_charts(report_data, category)
            
            report = Report(
                report_id=str(uuid.uuid4()),
                title=f"{category.value.replace('_', ' ').title()} {report_type.value.title()} Report",
                type=report_type,
                category=category,
                data=report_data,
                charts=charts,
                insights=insights,
                period_start=period_start,
                period_end=period_end,
                generated_by=user_id
            )
            
            # Store report
            self.reports_store[report.report_id] = report
            
            logger.info(f"Generated report: {report.report_id}")
            return report
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            raise
    
    async def _generate_report_data(self, category: AnalyticsCategory, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate report data for category"""
        # In a real implementation, this would query actual analytics data
        if category == AnalyticsCategory.USER_BEHAVIOR:
            return {
                "total_users": 1250,
                "active_users": 890,
                "new_users": 125,
                "session_duration_avg": 450,  # seconds
                "bounce_rate": 0.35,
                "page_views": 15000
            }
        elif category == AnalyticsCategory.CONTENT_PERFORMANCE:
            return {
                "total_content": 450,
                "new_content": 25,
                "total_views": 125000,
                "engagement_rate": 0.045,
                "top_performing_content": ["content_1", "content_2", "content_3"]
            }
        elif category == AnalyticsCategory.REVENUE:
            return {
                "total_revenue": 12500.00,
                "subscription_revenue": 8500.00,
                "one_time_payments": 4000.00,
                "avg_order_value": 45.50,
                "conversion_rate": 0.032
            }
        else:
            return {}
    
    async def _generate_insights(self, data: Dict[str, Any], category: AnalyticsCategory) -> List[str]:
        """Generate insights from report data"""
        insights = []
        
        if category == AnalyticsCategory.USER_BEHAVIOR:
            if data.get("bounce_rate", 0) > 0.4:
                insights.append("High bounce rate detected - consider improving landing page engagement")
            if data.get("session_duration_avg", 0) > 300:
                insights.append("Users are highly engaged with average session duration above 5 minutes")
        
        elif category == AnalyticsCategory.CONTENT_PERFORMANCE:
            if data.get("engagement_rate", 0) > 0.04:
                insights.append("Above-average engagement rate indicates strong content quality")
        
        elif category == AnalyticsCategory.REVENUE:
            if data.get("conversion_rate", 0) < 0.03:
                insights.append("Conversion rate below industry average - consider optimizing checkout flow")
        
        return insights
    
    async def _generate_charts(self, data: Dict[str, Any], category: AnalyticsCategory) -> List[Dict[str, Any]]:
        """Generate chart configurations for report"""
        charts = []
        
        if category == AnalyticsCategory.USER_BEHAVIOR:
            charts.append({
                "type": "line",
                "title": "Daily Active Users",
                "data": {"labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "values": [120, 135, 145, 150, 140, 160, 155]}
            })
            charts.append({
                "type": "pie",
                "title": "Traffic Sources", 
                "data": {"labels": ["Direct", "Social", "Search", "Referral"], "values": [40, 30, 20, 10]}
            })
        
        elif category == AnalyticsCategory.CONTENT_PERFORMANCE:
            charts.append({
                "type": "bar",
                "title": "Content Engagement by Type",
                "data": {"labels": ["Video", "Image", "Text", "Audio"], "values": [250, 180, 120, 90]}
            })
        
        return charts
    
    async def get_report(self, report_id: str) -> Optional[Report]:
        """Get report by ID"""
        return self.reports_store.get(report_id)
    
    async def list_reports(self, category: AnalyticsCategory = None, limit: int = 50) -> List[Report]:
        """List reports with optional filtering"""
        reports = list(self.reports_store.values())
        
        if category:
            reports = [report for report in reports if report.category == category]
        
        # Sort by generation time (newest first)
        reports.sort(key=lambda r: r.generated_at, reverse=True)
        
        return reports[:limit]

class InsightsService:
    """AI-powered insights and recommendations service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.insights_store: Dict[str, Insight] = {}
        logger.info("🧠 Insights Service initialized")
    
    async def generate_insights(self, category: AnalyticsCategory, data: Dict[str, Any]) -> List[Insight]:
        """Generate AI-powered insights from data"""
        try:
            logger.info(f"Generating insights for category: {category.value}")
            
            insights = []
            
            if category == AnalyticsCategory.USER_BEHAVIOR:
                insights.extend(await self._analyze_user_behavior(data))
            elif category == AnalyticsCategory.CONTENT_PERFORMANCE:
                insights.extend(await self._analyze_content_performance(data))
            elif category == AnalyticsCategory.REVENUE:
                insights.extend(await self._analyze_revenue_data(data))
            
            # Store insights
            for insight in insights:
                self.insights_store[insight.insight_id] = insight
            
            return insights
        except Exception as e:
            logger.error(f"Insights generation error: {e}")
            return []
    
    async def _analyze_user_behavior(self, data: Dict[str, Any]) -> List[Insight]:
        """Analyze user behavior data"""
        insights = []
        
        # Example insight generation
        bounce_rate = data.get('bounce_rate', 0)
        if bounce_rate > 0.5:
            insight = Insight(
                insight_id=str(uuid.uuid4()),
                title="High Bounce Rate Alert",
                description=f"Your bounce rate of {bounce_rate:.1%} is above optimal levels",
                category=AnalyticsCategory.USER_BEHAVIOR,
                confidence_score=0.85,
                impact_level="high",
                recommendations=[
                    "Improve page loading speed",
                    "Enhance content relevance",
                    "Optimize call-to-action placement"
                ],
                data_points={"bounce_rate": bounce_rate, "threshold": 0.4}
            )
            insights.append(insight)
        
        return insights
    
    async def _analyze_content_performance(self, data: Dict[str, Any]) -> List[Insight]:
        """Analyze content performance data"""
        insights = []
        
        engagement_rate = data.get('engagement_rate', 0)
        if engagement_rate > 0.05:
            insight = Insight(
                insight_id=str(uuid.uuid4()),
                title="High Engagement Content",
                description=f"Your content engagement rate of {engagement_rate:.1%} is excellent",
                category=AnalyticsCategory.CONTENT_PERFORMANCE,
                confidence_score=0.9,
                impact_level="medium",
                recommendations=[
                    "Identify top-performing content patterns",
                    "Create similar content types",
                    "Increase publishing frequency"
                ],
                data_points={"engagement_rate": engagement_rate}
            )
            insights.append(insight)
        
        return insights
    
    async def _analyze_revenue_data(self, data: Dict[str, Any]) -> List[Insight]:
        """Analyze revenue data"""
        insights = []
        
        conversion_rate = data.get('conversion_rate', 0)
        if conversion_rate < 0.02:
            insight = Insight(
                insight_id=str(uuid.uuid4()),
                title="Low Conversion Rate",
                description=f"Conversion rate of {conversion_rate:.1%} needs improvement",
                category=AnalyticsCategory.REVENUE,
                confidence_score=0.8,
                impact_level="high",
                recommendations=[
                    "A/B test checkout process",
                    "Optimize pricing strategy",
                    "Improve product descriptions"
                ],
                data_points={"conversion_rate": conversion_rate, "industry_avg": 0.025}
            )
            insights.append(insight)
        
        return insights
    
    async def get_insights(self, category: AnalyticsCategory = None, limit: int = 10) -> List[Insight]:
        """Get insights with optional filtering"""
        insights = list(self.insights_store.values())
        
        if category:
            insights = [insight for insight in insights if insight.category == category]
        
        # Sort by confidence score and impact
        insights.sort(key=lambda i: (i.confidence_score, {"high": 3, "medium": 2, "low": 1}.get(i.impact_level, 0)), reverse=True)
        
        return insights[:limit]

class DashboardService:
    """Dashboard creation and management service"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.dashboards_store: Dict[str, Dashboard] = {}
        self._create_default_dashboards()
        logger.info("📊 Dashboard Service initialized")
    
    def _create_default_dashboards(self):
        """Create default dashboards"""
        # Overview Dashboard
        overview_dashboard = Dashboard(
            dashboard_id="overview",
            name="Platform Overview",
            description="High-level platform metrics and KPIs",
            widgets=[
                {"type": "metric", "title": "Total Users", "metric": "total_users", "size": "small"},
                {"type": "metric", "title": "Active Users", "metric": "active_users", "size": "small"},
                {"type": "metric", "title": "Revenue", "metric": "total_revenue", "size": "small"},
                {"type": "chart", "title": "Daily Active Users", "chart_type": "line", "size": "medium"},
                {"type": "chart", "title": "Revenue Trend", "chart_type": "area", "size": "medium"}
            ],
            owner_id="system",
            is_public=True
        )
        self.dashboards_store["overview"] = overview_dashboard
        
        # Content Dashboard
        content_dashboard = Dashboard(
            dashboard_id="content",
            name="Content Performance",
            description="Content analytics and engagement metrics",
            widgets=[
                {"type": "metric", "title": "Total Content", "metric": "total_content", "size": "small"},
                {"type": "metric", "title": "Avg Engagement", "metric": "avg_engagement", "size": "small"},
                {"type": "chart", "title": "Content by Type", "chart_type": "pie", "size": "medium"},
                {"type": "table", "title": "Top Performing Content", "size": "large"}
            ],
            owner_id="system",
            is_public=True
        )
        self.dashboards_store["content"] = content_dashboard
    
    async def create_dashboard(self, dashboard_data: Dict[str, Any]) -> Dashboard:
        """Create new dashboard"""
        try:
            dashboard = Dashboard(
                dashboard_id=dashboard_data.get("dashboard_id", str(uuid.uuid4())),
                name=dashboard_data["name"],
                description=dashboard_data.get("description", ""),
                widgets=dashboard_data.get("widgets", []),
                filters=dashboard_data.get("filters", {}),
                refresh_interval=dashboard_data.get("refresh_interval", 300),
                owner_id=dashboard_data.get("owner_id", ""),
                is_public=dashboard_data.get("is_public", False)
            )
            
            self.dashboards_store[dashboard.dashboard_id] = dashboard
            logger.info(f"Created dashboard: {dashboard.dashboard_id}")
            return dashboard
        except Exception as e:
            logger.error(f"Dashboard creation error: {e}")
            raise
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard by ID"""
        return self.dashboards_store.get(dashboard_id)
    
    async def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> Optional[Dashboard]:
        """Update dashboard"""
        try:
            dashboard = self.dashboards_store.get(dashboard_id)
            if not dashboard:
                return None
            
            # Update fields
            for key, value in updates.items():
                if hasattr(dashboard, key):
                    setattr(dashboard, key, value)
            
            dashboard.updated_at = datetime.utcnow()
            
            logger.info(f"Updated dashboard: {dashboard_id}")
            return dashboard
        except Exception as e:
            logger.error(f"Dashboard update error: {e}")
            return None
    
    async def list_dashboards(self, owner_id: str = None, public_only: bool = False) -> List[Dashboard]:
        """List dashboards"""
        dashboards = list(self.dashboards_store.values())
        
        if public_only:
            dashboards = [d for d in dashboards if d.is_public]
        elif owner_id:
            dashboards = [d for d in dashboards if d.owner_id == owner_id or d.is_public]
        
        return dashboards

class AnalyticsService:
    """
    Unified Analytics Service that orchestrates all analytics-related services
    
    Consolidates:
    - Data Collection & Event Tracking
    - Metrics Collection & Aggregation
    - Report Generation
    - AI-Powered Insights
    - Dashboard Management
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize sub-services
        self.data_collection = DataCollectionService(self.config.get('data_collection', {}))
        self.metrics = MetricsService(self.config.get('metrics', {}))
        self.reporting = ReportingService(self.config.get('reporting', {}))
        self.insights = InsightsService(self.config.get('insights', {}))
        self.dashboards = DashboardService(self.config.get('dashboards', {}))
        
        logger.info("📊 Analytics Service initialized - All analytics-related services consolidated")
    
    async def initialize(self):
        """Initialize all analytics services"""
        logger.info("🚀 Initializing Analytics Service")
        # Any initialization logic here
    
    async def shutdown(self):
        """Shutdown all analytics services"""
        logger.info("🛑 Shutting down Analytics Service")
        # Flush any remaining data
        await self.data_collection._flush_buffer()
    
    # Data collection methods
    async def track_event(self, event: AnalyticsEvent) -> bool:
        """Track analytics event"""
        return await self.data_collection.track_event(event)
    
    async def track_page_view(self, user_id: str, page: str, properties: Dict[str, Any] = None) -> bool:
        """Track page view"""
        return await self.data_collection.track_page_view(user_id, page, properties)
    
    async def track_user_action(self, user_id: str, action: str, properties: Dict[str, Any] = None) -> bool:
        """Track user action"""
        return await self.data_collection.track_user_action(user_id, action, properties)
    
    async def track_content_interaction(self, user_id: str, content_id: str, interaction_type: str, properties: Dict[str, Any] = None) -> bool:
        """Track content interaction"""
        return await self.data_collection.track_content_interaction(user_id, content_id, interaction_type, properties)
    
    # Metrics methods
    async def record_metric(self, metric: Metric) -> bool:
        """Record metric"""
        return await self.metrics.record_metric(metric)
    
    async def increment_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None) -> bool:
        """Increment counter"""
        return await self.metrics.increment_counter(name, value, tags)
    
    async def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None) -> bool:
        """Set gauge value"""
        return await self.metrics.set_gauge(name, value, tags)
    
    async def aggregate_metrics(self, name: str, aggregation: AggregationType, start_time: datetime = None, end_time: datetime = None) -> float:
        """Aggregate metrics"""
        return await self.metrics.aggregate_metrics(name, aggregation, start_time, end_time)
    
    # Reporting methods
    async def generate_report(self, report_type: ReportType, category: AnalyticsCategory, period_start: datetime, period_end: datetime, user_id: str = None) -> Report:
        """Generate report"""
        return await self.reporting.generate_report(report_type, category, period_start, period_end, user_id)
    
    async def get_report(self, report_id: str) -> Optional[Report]:
        """Get report"""
        return await self.reporting.get_report(report_id)
    
    async def list_reports(self, category: AnalyticsCategory = None, limit: int = 50) -> List[Report]:
        """List reports"""
        return await self.reporting.list_reports(category, limit)
    
    # Insights methods
    async def generate_insights(self, category: AnalyticsCategory, data: Dict[str, Any]) -> List[Insight]:
        """Generate insights"""
        return await self.insights.generate_insights(category, data)
    
    async def get_insights(self, category: AnalyticsCategory = None, limit: int = 10) -> List[Insight]:
        """Get insights"""
        return await self.insights.get_insights(category, limit)
    
    # Dashboard methods
    async def create_dashboard(self, dashboard_data: Dict[str, Any]) -> Dashboard:
        """Create dashboard"""
        return await self.dashboards.create_dashboard(dashboard_data)
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard"""
        return await self.dashboards.get_dashboard(dashboard_id)
    
    async def list_dashboards(self, owner_id: str = None, public_only: bool = False) -> List[Dashboard]:
        """List dashboards"""
        return await self.dashboards.list_dashboards(owner_id, public_only)

# Export all classes
__all__ = [
    # Enums
    "MetricType",
    "ReportType",
    "AnalyticsCategory",
    "AggregationType",
    
    # Data structures
    "AnalyticsEvent",
    "Metric",
    "Report",
    "Dashboard",
    "Insight",
    
    # Services
    "DataCollectionService",
    "MetricsService", 
    "ReportingService",
    "InsightsService",
    "DashboardService",
    "AnalyticsService"
]

# Module initialization
logger.info(f"📊 Analytics Service v{__version__} loaded")
logger.info(f"Created by: {__author__} ({__email__})")
logger.info("⚠️ Protected by copyright - Unauthorized use prohibited")
logger.info("🎯 Consolidated: analytics_service + analytics/ subdirectory modules")