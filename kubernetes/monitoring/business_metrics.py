"""Business Metrics Collector for IA Influencer Agent Platform
===========================================================

Industrial-grade business intelligence and KPI tracking system specialized
for content protection, AI fingerprinting, revenue optimization, and
multi-platform influencer collaboration metrics.

Core Business Domains:
- Content Protection & Fingerprinting Analytics
- Revenue Tracking & Monetization Optimization
- User Engagement & Platform Performance
- AI Engine Performance & Accuracy Metrics
- Multi-Platform Integration Monitoring
- Collaboration & Creator Success Metrics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use, distribution, or modification prohibited
"""
import asyncio
import time
import logging
import statistics
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import aioredis
import json
import numpy as np
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Enhanced business metric types for comprehensive analytics"""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    DURATION = "duration"
    THROUGHPUT = "throughput"


class BusinessDomain(Enum):
    """Business domain classification for metrics"""    CONTENT_PROTECTION = "content_protection"
    AI_FINGERPRINTING = "ai_fingerprinting"
    REVENUE_TRACKING = "revenue_tracking"
    USER_ENGAGEMENT = "user_engagement"
    PLATFORM_PERFORMANCE = "platform_performance"
    COLLABORATION = "collaboration"
    SECURITY = "security"
    OPERATIONAL = "operational"


@dataclass
class BusinessMetric:
    """Enhanced business metric with domain context and impact assessment"""    name: str
    value: Union[int, float]
    metric_type: MetricType
    domain: BusinessDomain
    timestamp: datetime
    dimensions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    unit: str = "count"
    business_impact: str = "medium"  # low, medium, high, critical
    confidence_score: float = 1.0
    trend_direction: str = "stable"  # increasing, decreasing, stable
    target_value: Optional[float] = None
    sla_relevant: bool = False


@dataclass
class MetricAggregation:
    """Enhanced metric aggregation with statistical analysis"""    name: str
    domain: BusinessDomain
    period: str
    sum_value: float = 0.0
    avg_value: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    median_value: float = 0.0
    std_deviation: float = 0.0
    count: int = 0
    unique_dimensions: int = 0
    percentile_95: float = 0.0
    percentile_99: float = 0.0
    trend_coefficient: float = 0.0
    anomaly_score: float = 0.0


@dataclass
class BusinessKPI:
    """Key Performance Indicator definition and tracking"""    name: str
    description: str
    metric_source: str
    target_value: float
    current_value: float = 0.0
    achievement_rate: float = 0.0
    trend: str = "stable"
    business_impact: str = "high"
    calculation_method: str = ""
    update_frequency: int = 3600  # seconds


class ContentProtectionMetrics:
    """Specialized metrics for content protection and fingerprinting"""    
    def __init__(self, db_engine: AsyncEngine):
        self.db_engine = db_engine
    
    async def collect_fingerprint_metrics(self) -> List[BusinessMetric]:
        """Collect AI fingerprinting performance metrics"""        metrics = []
        
        try:
            async with self.db_engine.begin() as conn:
                # Fingerprint processing metrics
                result = await conn.execute(text("""                    SELECT 
                        content_type,
                        COUNT(*) as total_fingerprints,
                        COUNT(CASE WHEN created_at > NOW() - INTERVAL '1 hour' THEN 1 END) as hourly_fingerprints,
                        AVG(CASE WHEN processing_time IS NOT NULL THEN processing_time END) as avg_processing_time,
                        COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_fingerprints
                    FROM content_fingerprints 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY content_type
                """))
                
                for row in result:
                    content_type = row.content_type
                    success_rate = (row.successful_fingerprints / row.total_fingerprints) * 100 if row.total_fingerprints > 0 else 0
                    
                    # Fingerprint success rate
                    metrics.append(BusinessMetric(
                        name="fingerprint_success_rate",
                        value=success_rate,
                        metric_type=MetricType.PERCENTAGE,
                        domain=BusinessDomain.AI_FINGERPRINTING,
                        timestamp=datetime.utcnow(),
                        dimensions={"content_type": content_type},
                        unit="percent",
                        business_impact="critical",
                        target_value=95.0,
                        sla_relevant=True
                    ))
                    
                    # Processing throughput
                    metrics.append(BusinessMetric(
                        name="fingerprint_throughput_hourly",
                        value=row.hourly_fingerprints,
                        metric_type=MetricType.RATE,
                        domain=BusinessDomain.AI_FINGERPRINTING,
                        timestamp=datetime.utcnow(),
                        dimensions={"content_type": content_type},
                        unit="fingerprints/hour",
                        business_impact="high"
                    ))
                    
                    # Average processing time
                    if row.avg_processing_time:
                        metrics.append(BusinessMetric(
                            name="fingerprint_processing_time",
                            value=float(row.avg_processing_time),
                            metric_type=MetricType.DURATION,
                            domain=BusinessDomain.AI_FINGERPRINTING,
                            timestamp=datetime.utcnow(),
                            dimensions={"content_type": content_type},
                            unit="seconds",
                            business_impact="medium",
                            target_value=5.0
                        ))
                
                # Protection alert metrics
                result = await conn.execute(text("""                    SELECT 
                        platform,
                        COUNT(*) as total_alerts,
                        COUNT(CASE WHEN status = 'confirmed' THEN 1 END) as confirmed_violations,
                        AVG(similarity_score) as avg_similarity_score,
                        COUNT(CASE WHEN created_at > NOW() - INTERVAL '1 hour' THEN 1 END) as hourly_alerts
                    FROM protection_alerts 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY platform
                """))
                
                for row in result:
                    platform = row.platform
                    
                    # Violation detection rate
                    detection_rate = (row.confirmed_violations / row.total_alerts) * 100 if row.total_alerts > 0 else 0
                    metrics.append(BusinessMetric(
                        name="violation_detection_rate",
                        value=detection_rate,
                        metric_type=MetricType.PERCENTAGE,
                        domain=BusinessDomain.CONTENT_PROTECTION,
                        timestamp=datetime.utcnow(),
                        dimensions={"platform": platform},
                        unit="percent",
                        business_impact="critical",
                        target_value=90.0
                    ))
                    
                    # Alert volume
                    metrics.append(BusinessMetric(
                        name="protection_alerts_hourly",
                        value=row.hourly_alerts,
                        metric_type=MetricType.RATE,
                        domain=BusinessDomain.CONTENT_PROTECTION,
                        timestamp=datetime.utcnow(),
                        dimensions={"platform": platform},
                        unit="alerts/hour",
                        business_impact="high"
                    ))
                    
                    # Average similarity score
                    if row.avg_similarity_score:
                        metrics.append(BusinessMetric(
                            name="similarity_score_average",
                            value=float(row.avg_similarity_score),
                            metric_type=MetricType.GAUGE,
                            domain=BusinessDomain.AI_FINGERPRINTING,
                            timestamp=datetime.utcnow(),
                            dimensions={"platform": platform},
                            unit="score",
                            business_impact="medium",
                            target_value=0.85
                        ))
                
        except Exception as e:
            logger.error(f"Error collecting fingerprint metrics: {e}")
            
        return metrics


class RevenueTrackingMetrics:
    """Specialized metrics for revenue tracking and monetization"""    
    def __init__(self, db_engine: AsyncEngine):
        self.db_engine = db_engine
    
    async def collect_revenue_metrics(self) -> List[BusinessMetric]:
        """Collect revenue and monetization metrics"""        metrics = []
        
        try:
            async with self.db_engine.begin() as conn:
                # Revenue tracking metrics
                result = await conn.execute(text("""                    SELECT 
                        platform,
                        currency,
                        COUNT(*) as revenue_records,
                        SUM(revenue_amount) as total_revenue,
                        AVG(revenue_amount) as avg_revenue_per_record,
                        COUNT(DISTINCT user_id) as unique_creators
                    FROM revenue_tracking 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY platform, currency
                """))
                
                total_daily_revenue = 0.0
                total_creators = set()
                
                for row in result:
                    platform = row.platform
                    currency = row.currency
                    
                    # Platform revenue
                    metrics.append(BusinessMetric(
                        name="platform_revenue_daily",
                        value=float(row.total_revenue),
                        metric_type=MetricType.CURRENCY,
                        domain=BusinessDomain.REVENUE_TRACKING,
                        timestamp=datetime.utcnow(),
                        dimensions={"platform": platform, "currency": currency},
                        unit=currency.lower(),
                        business_impact="critical",
                        sla_relevant=True
                    ))
                    
                    # Average revenue per creator
                    avg_per_creator = float(row.total_revenue) / row.unique_creators if row.unique_creators > 0 else 0
                    metrics.append(BusinessMetric(
                        name="avg_revenue_per_creator",
                        value=avg_per_creator,
                        metric_type=MetricType.CURRENCY,
                        domain=BusinessDomain.REVENUE_TRACKING,
                        timestamp=datetime.utcnow(),
                        dimensions={"platform": platform, "currency": currency},
                        unit=f"{currency.lower()}/creator",
                        business_impact="high"
                    ))
                    
                    # Revenue record count (data health indicator)
                    metrics.append(BusinessMetric(
                        name="revenue_records_daily",
                        value=row.revenue_records,
                        metric_type=MetricType.COUNTER,
                        domain=BusinessDomain.REVENUE_TRACKING,
                        timestamp=datetime.utcnow(),
                        dimensions={"platform": platform},
                        unit="records",
                        business_impact="medium"
                    ))
                    
                    # Track for global metrics
                    if currency == "EUR":  # Normalize to EUR for global metrics
                        total_daily_revenue += float(row.total_revenue)
                    total_creators.update([row.unique_creators])
                
                # Global revenue metrics
                metrics.append(BusinessMetric(
                    name="total_platform_revenue_daily",
                    value=total_daily_revenue,
                    metric_type=MetricType.CURRENCY,
                    domain=BusinessDomain.REVENUE_TRACKING,
                    timestamp=datetime.utcnow(),
                    dimensions={"currency": "EUR"},
                    unit="eur",
                    business_impact="critical",
                    target_value=50000.0,  # 50K EUR daily target
                    sla_relevant=True
                ))
                
                # Revenue growth metrics
                result = await conn.execute(text("""                    SELECT 
                        SUM(CASE WHEN created_at > NOW() - INTERVAL '7 days' THEN revenue_amount ELSE 0 END) as week_revenue,
                        SUM(CASE WHEN created_at BETWEEN NOW() - INTERVAL '14 days' AND NOW() - INTERVAL '7 days' THEN revenue_amount ELSE 0 END) as prev_week_revenue
                    FROM revenue_tracking
                    WHERE currency = 'EUR'
                """))
                
                growth_data = result.fetchone()
                if growth_data and growth_data.prev_week_revenue > 0:
                    growth_rate = ((growth_data.week_revenue - growth_data.prev_week_revenue) / growth_data.prev_week_revenue) * 100
                    metrics.append(BusinessMetric(
                        name="revenue_growth_rate_weekly",
                        value=growth_rate,
                        metric_type=MetricType.PERCENTAGE,
                        domain=BusinessDomain.REVENUE_TRACKING,
                        timestamp=datetime.utcnow(),
                        dimensions={"period": "weekly"},
                        unit="percent",
                        business_impact="critical",
                        target_value=5.0,  # 5% weekly growth target
                        sla_relevant=True
                    ))
                
        except Exception as e:
            logger.error(f"Error collecting revenue metrics: {e}")
            
        return metrics


class UserEngagementMetrics:
    """User engagement and platform usage metrics"""    
    def __init__(self, db_engine: AsyncEngine):
        self.db_engine = db_engine
    
    async def collect_engagement_metrics(self) -> List[BusinessMetric]:
        """Collect user engagement and activity metrics"""        metrics = []
        
        try:
            async with self.db_engine.begin() as conn:
                # User activity metrics
                result = await conn.execute(text("""                    SELECT 
                        COUNT(DISTINCT user_id) as daily_active_users,
                        COUNT(DISTINCT CASE WHEN created_at > NOW() - INTERVAL '1 hour' THEN user_id END) as hourly_active_users,
                        COUNT(*) as total_user_actions
                    FROM user_activities 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """))
                
                activity_data = result.fetchone()
                if activity_data:
                    # Daily Active Users
                    metrics.append(BusinessMetric(
                        name="daily_active_users",
                        value=activity_data.daily_active_users,
                        metric_type=MetricType.GAUGE,
                        domain=BusinessDomain.USER_ENGAGEMENT,
                        timestamp=datetime.utcnow(),
                        dimensions={},
                        unit="users",
                        business_impact="critical",
                        target_value=1000.0,
                        sla_relevant=True
                    ))
                    
                    # Hourly Active Users
                    metrics.append(BusinessMetric(
                        name="hourly_active_users",
                        value=activity_data.hourly_active_users,
                        metric_type=MetricType.GAUGE,
                        domain=BusinessDomain.USER_ENGAGEMENT,
                        timestamp=datetime.utcnow(),
                        dimensions={},
                        unit="users",
                        business_impact="high"
                    ))
                    
                    # User Action Volume
                    metrics.append(BusinessMetric(
                        name="user_actions_daily",
                        value=activity_data.total_user_actions,
                        metric_type=MetricType.COUNTER,
                        domain=BusinessDomain.USER_ENGAGEMENT,
                        timestamp=datetime.utcnow(),
                        dimensions={},
                        unit="actions",
                        business_impact="medium"
                    ))
                
                # Content creation metrics
                result = await conn.execute(text("""                    SELECT 
                        content_type,
                        COUNT(*) as content_uploads,
                        COUNT(DISTINCT user_id) as unique_creators,
                        AVG(content_size_mb) as avg_content_size
                    FROM content_uploads 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                    GROUP BY content_type
                """))
                
                for row in result:
                    content_type = row.content_type
                    
                    # Content upload volume
                    metrics.append(BusinessMetric(
                        name="content_uploads_daily",
                        value=row.content_uploads,
                        metric_type=MetricType.COUNTER,
                        domain=BusinessDomain.USER_ENGAGEMENT,
                        timestamp=datetime.utcnow(),
                        dimensions={"content_type": content_type},
                        unit="uploads",
                        business_impact="high",
                        target_value=500.0 if content_type == "audio" else 200.0
                    ))
                    
                    # Creator engagement rate
                    creator_engagement = (row.unique_creators / activity_data.daily_active_users) * 100 if activity_data.daily_active_users > 0 else 0
                    metrics.append(BusinessMetric(
                        name="creator_engagement_rate",
                        value=creator_engagement,
                        metric_type=MetricType.PERCENTAGE,
                        domain=BusinessDomain.USER_ENGAGEMENT,
                        timestamp=datetime.utcnow(),
                        dimensions={"content_type": content_type},
                        unit="percent",
                        business_impact="high",
                        target_value=25.0
                    ))
                
                # Collaboration metrics
                result = await conn.execute(text("""                    SELECT 
                        COUNT(*) as collaboration_requests,
                        COUNT(CASE WHEN status = 'accepted' THEN 1 END) as accepted_collaborations,
                        COUNT(DISTINCT requester_id) as unique_requesters,
                        COUNT(DISTINCT target_id) as unique_targets
                    FROM collaboration_requests 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """))
                
                collab_data = result.fetchone()
                if collab_data:
                    # Collaboration acceptance rate
                    acceptance_rate = (collab_data.accepted_collaborations / collab_data.collaboration_requests) * 100 if collab_data.collaboration_requests > 0 else 0
                    metrics.append(BusinessMetric(
                        name="collaboration_acceptance_rate",
                        value=acceptance_rate,
                        metric_type=MetricType.PERCENTAGE,
                        domain=BusinessDomain.COLLABORATION,
                        timestamp=datetime.utcnow(),
                        dimensions={},
                        unit="percent",
                        business_impact="high",
                        target_value=40.0
                    ))
                    
                    # Daily collaboration volume
                    metrics.append(BusinessMetric(
                        name="collaboration_requests_daily",
                        value=collab_data.collaboration_requests,
                        metric_type=MetricType.COUNTER,
                        domain=BusinessDomain.COLLABORATION,
                        timestamp=datetime.utcnow(),
                        dimensions={},
                        unit="requests",
                        business_impact="medium",
                        target_value=100.0
                    ))
                
        except Exception as e:
            logger.error(f"Error collecting engagement metrics: {e}")
            
        return metrics


class PlatformPerformanceMetrics:
    """Platform performance and operational metrics"""    
    def __init__(self, db_engine: AsyncEngine):
        self.db_engine = db_engine
    
    async def collect_performance_metrics(self) -> List[BusinessMetric]:
        """Collect platform performance metrics"""        metrics = []
        
        try:
            async with self.db_engine.begin() as conn:
                # API performance metrics
                result = await conn.execute(text("""                    SELECT 
                        endpoint,
                        COUNT(*) as request_count,
                        AVG(response_time_ms) as avg_response_time,
                        COUNT(CASE WHEN status_code >= 200 AND status_code < 300 THEN 1 END) as successful_requests,
                        COUNT(CASE WHEN status_code >= 500 THEN 1 END) as server_errors
                    FROM api_requests 
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                    GROUP BY endpoint
                """))
                
                for row in result:
                    endpoint = row.endpoint
                    success_rate = (row.successful_requests / row.request_count) * 100 if row.request_count > 0 else 0
                    error_rate = (row.server_errors / row.request_count) * 100 if row.request_count > 0 else 0
                    
                    # API success rate
                    metrics.append(BusinessMetric(
                        name="api_success_rate",
                        value=success_rate,
                        metric_type=MetricType.PERCENTAGE,
                        domain=BusinessDomain.PLATFORM_PERFORMANCE,
                        timestamp=datetime.utcnow(),
                        dimensions={"endpoint": endpoint},
                        unit="percent",
                        business_impact="critical",
                        target_value=99.5,
                        sla_relevant=True
                    ))
                    
                    # API response time
                    metrics.append(BusinessMetric(
                        name="api_response_time",
                        value=float(row.avg_response_time),
                        metric_type=MetricType.DURATION,
                        domain=BusinessDomain.PLATFORM_PERFORMANCE,
                        timestamp=datetime.utcnow(),
                        dimensions={"endpoint": endpoint},
                        unit="milliseconds",
                        business_impact="high",
                        target_value=500.0
                    ))
                    
                    # Error rate
                    metrics.append(BusinessMetric(
                        name="api_error_rate",
                        value=error_rate,
                        metric_type=MetricType.PERCENTAGE,
                        domain=BusinessDomain.PLATFORM_PERFORMANCE,
                        timestamp=datetime.utcnow(),
                        dimensions={"endpoint": endpoint},
                        unit="percent",
                        business_impact="critical",
                        target_value=0.5
                    ))
                
                # System resource utilization
                result = await conn.execute(text("""                    SELECT 
                        AVG(cpu_usage_percent) as avg_cpu,
                        AVG(memory_usage_percent) as avg_memory,
                        AVG(disk_usage_percent) as avg_disk
                    FROM system_metrics 
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                """))
                
                resource_data = result.fetchone()
                if resource_data:
                    # CPU utilization
                    metrics.append(BusinessMetric(
                        name="system_cpu_utilization",
                        value=float(resource_data.avg_cpu),
                        metric_type=MetricType.PERCENTAGE,
                        domain=BusinessDomain.PLATFORM_PERFORMANCE,
                        timestamp=datetime.utcnow(),
                        dimensions={},
                        unit="percent",
                        business_impact="high",
                        target_value=70.0
                    ))
                    
                    # Memory utilization
                    metrics.append(BusinessMetric(
                        name="system_memory_utilization",
                        value=float(resource_data.avg_memory),
                        metric_type=MetricType.PERCENTAGE,
                        domain=BusinessDomain.PLATFORM_PERFORMANCE,
                        timestamp=datetime.utcnow(),
                        dimensions={},
                        unit="percent",
                        business_impact="high",
                        target_value=80.0
                    ))
                
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            
        return metrics


class BusinessMetricsCollector:
    """    Industrial-grade business metrics collection system specialized for
    IA Influencer Agent Platform with comprehensive KPI tracking,
    predictive analytics, and automated business intelligence.
    """    
    def __init__(
        self,
        redis_client: Optional[aioredis.Redis] = None,
        db_engine: Optional[AsyncEngine] = None,
        collection_interval: int = 60,
        aggregation_intervals: List[int] = None,
        enable_predictive_analytics: bool = True
    ):
        self.redis_client = redis_client
        self.db_engine = db_engine
        self.collection_interval = collection_interval
        self.aggregation_intervals = aggregation_intervals or [300, 3600, 86400]  # 5min, 1h, 1day
        self.enable_predictive_analytics = enable_predictive_analytics
        
        # Metric storage and processing
        self._metrics_buffer: List[BusinessMetric] = []
        self._metric_definitions: Dict[str, Dict[str, Any]] = {}
        self._aggregations: Dict[str, Dict[str, MetricAggregation]] = defaultdict(dict)
        
        # Collection state
        self._collecting = False
        self._collection_task: Optional[asyncio.Task] = None
        self._aggregation_task: Optional[asyncio.Task] = None
        self._kpi_calculation_task: Optional[asyncio.Task] = None
        
        # Specialized metric collectors
        self._content_protection = ContentProtectionMetrics(db_engine) if db_engine else None
        self._revenue_tracking = RevenueTrackingMetrics(db_engine) if db_engine else None
        self._user_engagement = UserEngagementMetrics(db_engine) if db_engine else None
        self._platform_performance = PlatformPerformanceMetrics(db_engine) if db_engine else None
        
        # KPI definitions and tracking
        self._kpis: Dict[str, BusinessKPI] = {}
        self._kpi_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Analytics and prediction
        self._trend_analysis: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        self._anomaly_detection: Dict[str, Tuple[float, float]] = {}
        
        # Initialize KPIs
        self._initialize_business_kpis()
        
    def _initialize_business_kpis(self):
        """Initialize key business KPIs for the platform"""        
        # Content Protection KPIs
        self._kpis["fingerprint_success_rate"] = BusinessKPI(
            name="AI Fingerprint Success Rate",
            description="Percentage of successful content fingerprinting operations",
            metric_source="fingerprint_success_rate",
            target_value=95.0,
            business_impact="critical",
            calculation_method="(successful_fingerprints / total_fingerprints) * 100"
        )
        
        self._kpis["violation_detection_accuracy"] = BusinessKPI(
            name="Content Violation Detection Accuracy",
            description="Accuracy of automated content violation detection",
            metric_source="violation_detection_rate",
            target_value=90.0,
            business_impact="critical",
            calculation_method="(confirmed_violations / total_alerts) * 100"
        )
        
        # Revenue KPIs
        self._kpis["daily_revenue_target"] = BusinessKPI(
            name="Daily Revenue Target Achievement",
            description="Achievement rate of daily revenue targets",
            metric_source="total_platform_revenue_daily",
            target_value=50000.0,
            business_impact="critical",
            calculation_method="current_revenue / target_revenue * 100"
        )
        
        self._kpis["revenue_growth_rate"] = BusinessKPI(
            name="Weekly Revenue Growth Rate",
            description="Week-over-week revenue growth percentage",
            metric_source="revenue_growth_rate_weekly",
            target_value=5.0,
            business_impact="critical",
            calculation_method="(current_week - previous_week) / previous_week * 100"
        )
        
        # User Engagement KPIs
        self._kpis["daily_active_users"] = BusinessKPI(
            name="Daily Active Users",
            description="Number of unique users active per day",
            metric_source="daily_active_users",
            target_value=1000.0,
            business_impact="critical",
            calculation_method="COUNT(DISTINCT user_id) per day"
        )
        
        self._kpis["creator_engagement_rate"] = BusinessKPI(
            name="Creator Engagement Rate",
            description="Percentage of active users who create content",
            metric_source="creator_engagement_rate",
            target_value=25.0,
            business_impact="high",
            calculation_method="(unique_creators / daily_active_users) * 100"
        )
        
        # Platform Performance KPIs
        self._kpis["api_availability"] = BusinessKPI(
            name="API Availability",
            description="Overall API uptime and availability",
            metric_source="api_success_rate",
            target_value=99.5,
            business_impact="critical",
            calculation_method="(successful_requests / total_requests) * 100"
        )
        
        self._kpis["avg_response_time"] = BusinessKPI(
            name="Average API Response Time",
            description="Average response time across all API endpoints",
            metric_source="api_response_time",
            target_value=500.0,
            business_impact="high",
            calculation_method="AVG(response_time_ms) across all endpoints"
        )
        
        # Collaboration KPIs
        self._kpis["collaboration_success_rate"] = BusinessKPI(
            name="Collaboration Success Rate",
            description="Percentage of collaboration requests that are accepted",
            metric_source="collaboration_acceptance_rate",
            target_value=40.0,
            business_impact="high",
            calculation_method="(accepted_collaborations / total_requests) * 100"
        )
        """Register default business metrics"""        
        # Content protection metrics
        self.register_metric("content.fingerprints.created", MetricType.COUNTER, "count")
        self.register_metric("content.fingerprints.processed", MetricType.COUNTER, "count")
        self.register_metric("content.protection.alerts", MetricType.COUNTER, "count")
        self.register_metric("content.protection.violations", MetricType.COUNTER, "count")
        self.register_metric("content.protection.takedowns", MetricType.COUNTER, "count")
        
        # Revenue metrics
        self.register_metric("revenue.tracked.amount", MetricType.GAUGE, "currency")
        self.register_metric("revenue.recovered.amount", MetricType.GAUGE, "currency")
        self.register_metric("revenue.commissions.earned", MetricType.GAUGE, "currency")
        self.register_metric("revenue.payouts.processed", MetricType.COUNTER, "count")
        
        # User engagement metrics
        self.register_metric("users.active.daily", MetricType.GAUGE, "count")
        self.register_metric("users.active.monthly", MetricType.GAUGE, "count")
        self.register_metric("users.new.registrations", MetricType.COUNTER, "count")
        self.register_metric("users.sessions.count", MetricType.COUNTER, "count")
        self.register_metric("users.sessions.duration", MetricType.HISTOGRAM, "seconds")
        
        # Platform metrics
        self.register_metric("platform.api.requests", MetricType.COUNTER, "count")
        self.register_metric("platform.api.errors", MetricType.COUNTER, "count")
        self.register_metric("platform.storage.usage", MetricType.GAUGE, "bytes")
        self.register_metric("platform.queue.size", MetricType.GAUGE, "count")
        
        # AI/ML metrics
        self.register_metric("ai.fingerprint.accuracy", MetricType.GAUGE, "percentage")
        self.register_metric("ai.matching.precision", MetricType.GAUGE, "percentage")
        self.register_metric("ai.processing.time", MetricType.HISTOGRAM, "milliseconds")
        
    async def start_collection(self):
        """Start business metrics collection"""        if self._collecting:
            logger.warning("Business metrics collection already running")
            return
            
        self._collecting = True
        self._collection_task = asyncio.create_task(self._collection_loop())
        self._aggregation_task = asyncio.create_task(self._aggregation_loop())
        
        logger.info("Business metrics collection started")
        
    async def stop_collection(self):
        """Stop business metrics collection"""        self._collecting = False
        
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
                
        if self._aggregation_task:
            self._aggregation_task.cancel()
            try:
                await self._aggregation_task
            except asyncio.CancelledError:
                pass
                
        # Final metric flush
        await self._process_metrics_buffer()
        
        logger.info("Business metrics collection stopped")
        
    async def _collection_loop(self):
        """Main collection loop"""        while self._collecting:
            try:
                await self._collect_platform_metrics()
                await self._collect_content_metrics()
                await self._collect_revenue_metrics()
                await self._collect_user_metrics()
                await self._process_metrics_buffer()
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in business metrics collection loop: {e}")
                await asyncio.sleep(10)
                
    async def _aggregation_loop(self):
        """Aggregation processing loop"""        while self._collecting:
            try:
                await self._process_aggregations()
                await asyncio.sleep(60)  # Run aggregations every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in aggregation loop: {e}")
                await asyncio.sleep(10)
                
    async def _collect_platform_metrics(self):
        """Collect platform-level metrics"""        metrics = await self._platform_metrics.collect()
        for metric in metrics:
            self._metrics_buffer.append(metric)
            
    async def _collect_content_metrics(self):
        """Collect content protection metrics"""        metrics = await self._content_metrics.collect()
        for metric in metrics:
            self._metrics_buffer.append(metric)
            
    async def _collect_revenue_metrics(self):
        """Collect revenue tracking metrics"""        metrics = await self._revenue_metrics.collect()
        for metric in metrics:
            self._metrics_buffer.append(metric)
            
    async def _collect_user_metrics(self):
        """Collect user engagement metrics"""        metrics = await self._user_metrics.collect()
        for metric in metrics:
            self._metrics_buffer.append(metric)
            
    async def _process_metrics_buffer(self):
        """Process metrics buffer"""        if not self._metrics_buffer:
            return
            
        metrics_to_process = self._metrics_buffer.copy()
        self._metrics_buffer.clear()
        
        # Store metrics in Redis
        if self.redis_client:
            await self._store_metrics(metrics_to_process)
            
        # Update aggregations
        await self._update_aggregations(metrics_to_process)
        
    async def _store_metrics(self, metrics: List[BusinessMetric]):
        """Store metrics in Redis"""        try:
            pipeline = self.redis_client.pipeline()
            
            for metric in metrics:
                # Store individual metric
                key = f"business_metrics:{metric.name}"
                value = {
                    "value": metric.value,
                    "metric_type": metric.metric_type.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "dimensions": metric.dimensions,
                    "metadata": metric.metadata,
                    "unit": metric.unit
                }
                
                # Store in time series
                pipeline.zadd(key, {json.dumps(value): metric.timestamp.timestamp()})
                
                # Store current value
                current_key = f"business_metrics:current:{metric.name}"
                pipeline.set(current_key, json.dumps(value), ex=3600)
                
                # Cleanup old data (keep 30 days)
                cutoff = time.time() - (30 * 24 * 3600)
                pipeline.zremrangebyscore(key, 0, cutoff)
                
            await pipeline.execute()
            
        except Exception as e:
            logger.error(f"Error storing business metrics: {e}")
            
    async def _update_aggregations(self, metrics: List[BusinessMetric]):
        """Update metric aggregations"""        for metric in metrics:
            for interval in self.aggregation_intervals:
                period_key = self._get_period_key(metric.timestamp, interval)
                agg_key = f"{metric.name}:{period_key}"
                
                if agg_key not in self._aggregations[metric.name]:
                    self._aggregations[metric.name][agg_key] = MetricAggregation(
                        name=metric.name,
                        period=period_key
                    )
                    
                agg = self._aggregations[metric.name][agg_key]
                
                # Update aggregation
                if metric.metric_type == MetricType.COUNTER:
                    agg.sum_value += metric.value
                elif metric.metric_type == MetricType.GAUGE:
                    agg.sum_value += metric.value
                    agg.min_value = min(agg.min_value, metric.value) if agg.count > 0 else metric.value
                    agg.max_value = max(agg.max_value, metric.value)
                    
                agg.count += 1
                agg.avg_value = agg.sum_value / agg.count
                
                # Track unique dimensions
                dim_key = json.dumps(metric.dimensions, sort_keys=True)
                if not hasattr(agg, '_unique_dims'):
                    agg._unique_dims = set()
                agg._unique_dims.add(dim_key)
                agg.unique_dimensions = len(agg._unique_dims)
                
    async def _process_aggregations(self):
        """Process and store aggregations"""        if not self.redis_client:
            return
            
        try:
            pipeline = self.redis_client.pipeline()
            
            for metric_name, aggregations in self._aggregations.items():
                for agg_key, agg in aggregations.items():
                    key = f"business_metrics:agg:{agg_key}"
                    value = {
                        "name": agg.name,
                        "period": agg.period,
                        "sum_value": agg.sum_value,
                        "avg_value": agg.avg_value,
                        "min_value": agg.min_value,
                        "max_value": agg.max_value,
                        "count": agg.count,
                        "unique_dimensions": agg.unique_dimensions
                    }
                    
                    pipeline.set(key, json.dumps(value), ex=7 * 24 * 3600)  # 7 days TTL
                    
            await pipeline.execute()
            
        except Exception as e:
            logger.error(f"Error processing aggregations: {e}")
            
    def _get_period_key(self, timestamp: datetime, interval: int) -> str:
        """Get period key for aggregation"""        epoch = int(timestamp.timestamp())
        period_start = (epoch // interval) * interval
        return f"{interval}s_{period_start}"
        
    # Public interface methods
    def register_metric(self, name: str, metric_type: MetricType, unit: str = "count"):
        """Register a business metric"""        self._metric_definitions[name] = {
            "type": metric_type,
            "unit": unit,
            "registered_at": datetime.utcnow().isoformat()
        }
        logger.info(f"Registered business metric: {name}")
        
    async def record_metric(
        self,
        name: str,
        value: Union[int, float],
        dimensions: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a business metric"""        if name not in self._metric_definitions:
            logger.warning(f"Unknown metric: {name}")
            return
            
        metric_def = self._metric_definitions[name]
        
        metric = BusinessMetric(
            name=name,
            value=value,
            metric_type=metric_def["type"],
            timestamp=datetime.utcnow(),
            dimensions=dimensions or {},
            metadata=metadata or {},
            unit=metric_def["unit"]
        )
        
        self._metrics_buffer.append(metric)
        
    async def get_metric_current(self, name: str) -> Optional[Dict[str, Any]]:
        """Get current value of a metric"""        if not self.redis_client:
            return None
            
        try:
            key = f"business_metrics:current:{name}"
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting current metric {name}: {e}")
            
        return None
        
    async def get_metric_history(
        self,
        name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get metric history"""        if not self.redis_client:
            return []
            
        try:
            key = f"business_metrics:{name}"
            
            start_score = start_time.timestamp() if start_time else 0
            end_score = end_time.timestamp() if end_time else "+inf"
            
            values = await self.redis_client.zrangebyscore(
                key, start_score, end_score, withscores=True
            )
            
            history = []
            for value_json, timestamp in values:
                metric_data = json.loads(value_json)
                metric_data['timestamp'] = datetime.fromtimestamp(timestamp)
                history.append(metric_data)
                
            return history
            
        except Exception as e:
            logger.error(f"Error getting metric history for {name}: {e}")
            return []
            
    async def get_aggregated_metrics(
        self,
        names: Optional[List[str]] = None,
        interval: int = 3600
    ) -> Dict[str, Dict[str, Any]]:
        """Get aggregated metrics"""        if not self.redis_client:
            return {}
            
        metric_names = names or list(self._metric_definitions.keys())
        results = {}
        
        try:
            for metric_name in metric_names:
                # Get recent aggregations for this metric
                pattern = f"business_metrics:agg:{metric_name}:{interval}s_*"
                keys = await self.redis_client.keys(pattern)
                
                aggregations = []
                for key in keys:
                    value = await self.redis_client.get(key)
                    if value:
                        agg_data = json.loads(value)
                        aggregations.append(agg_data)
                        
                if aggregations:
                    # Sort by period
                    aggregations.sort(key=lambda x: x['period'])
                    results[metric_name] = aggregations
                    
        except Exception as e:
            logger.error(f"Error getting aggregated metrics: {e}")
            
        return results
        
    async def get_business_kpis(self) -> Dict[str, Any]:
        """Get key business KPIs"""        kpis = {}
        
        try:
            # Content protection KPIs
            fingerprints_created = await self.get_metric_current("content.fingerprints.created")
            protection_alerts = await self.get_metric_current("content.protection.alerts")
            violations_detected = await self.get_metric_current("content.protection.violations")
            
            kpis["content_protection"] = {
                "fingerprints_created": fingerprints_created["value"] if fingerprints_created else 0,
                "alerts_generated": protection_alerts["value"] if protection_alerts else 0,
                "violations_detected": violations_detected["value"] if violations_detected else 0
            }
            
            # Revenue KPIs
            revenue_tracked = await self.get_metric_current("revenue.tracked.amount")
            revenue_recovered = await self.get_metric_current("revenue.recovered.amount")
            commissions_earned = await self.get_metric_current("revenue.commissions.earned")
            
            kpis["revenue"] = {
                "total_tracked": revenue_tracked["value"] if revenue_tracked else 0,
                "total_recovered": revenue_recovered["value"] if revenue_recovered else 0,
                "commissions_earned": commissions_earned["value"] if commissions_earned else 0
            }
            
            # User engagement KPIs
            daily_active = await self.get_metric_current("users.active.daily")
            monthly_active = await self.get_metric_current("users.active.monthly")
            new_registrations = await self.get_metric_current("users.new.registrations")
            
            kpis["user_engagement"] = {
                "daily_active_users": daily_active["value"] if daily_active else 0,
                "monthly_active_users": monthly_active["value"] if monthly_active else 0,
                "new_registrations": new_registrations["value"] if new_registrations else 0
            }
            
            # Platform KPIs
            api_requests = await self.get_metric_current("platform.api.requests")
            api_errors = await self.get_metric_current("platform.api.errors")
            storage_usage = await self.get_metric_current("platform.storage.usage")
            
            kpis["platform"] = {
                "api_requests": api_requests["value"] if api_requests else 0,
                "api_errors": api_errors["value"] if api_errors else 0,
                "storage_usage_gb": (storage_usage["value"] / (1024**3)) if storage_usage else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting business KPIs: {e}")
            
        return kpis
        
    def get_metric_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get all metric definitions"""        return self._metric_definitions.copy()


class PlatformMetricsTracker:
    """Track platform-level metrics"""    
    def __init__(self, db_engine: Optional[AsyncEngine]):
        self.db_engine = db_engine
        
    async def collect(self) -> List[BusinessMetric]:
        """Collect platform metrics"""        metrics = []
        timestamp = datetime.utcnow()
        
        if self.db_engine:
            try:
                async with self.db_engine.begin() as conn:
                    # API request count (last hour)
                    result = await conn.execute(text("""                        SELECT COUNT(*) FROM api_requests 
                        WHERE created_at > NOW() - INTERVAL '1 hour'
                    """))
                    api_requests = result.scalar() or 0
                    
                    metrics.append(BusinessMetric(
                        name="platform.api.requests",
                        value=api_requests,
                        metric_type=MetricType.GAUGE,
                        timestamp=timestamp,
                        unit="count"
                    ))
                    
                    # Storage usage
                    result = await conn.execute(text("SELECT pg_database_size(current_database())"))
                    storage_bytes = result.scalar() or 0
                    
                    metrics.append(BusinessMetric(
                        name="platform.storage.usage",
                        value=storage_bytes,
                        metric_type=MetricType.GAUGE,
                        timestamp=timestamp,
                        unit="bytes"
                    ))
                    
            except Exception as e:
                logger.error(f"Error collecting platform metrics: {e}")
                
        return metrics


class ContentMetricsTracker:
    """Track content protection metrics"""    
    def __init__(self, db_engine: Optional[AsyncEngine]):
        self.db_engine = db_engine
        
    async def collect(self) -> List[BusinessMetric]:
        """Collect content metrics"""        metrics = []
        timestamp = datetime.utcnow()
        
        if self.db_engine:
            try:
                async with self.db_engine.begin() as conn:
                    # Fingerprints created (last hour)
                    result = await conn.execute(text("""                        SELECT content_type, COUNT(*) 
                        FROM content_fingerprints 
                        WHERE created_at > NOW() - INTERVAL '1 hour'
                        GROUP BY content_type
                    """))
                    
                    for row in result:
                        content_type, count = row
                        metrics.append(BusinessMetric(
                            name="content.fingerprints.created",
                            value=count,
                            metric_type=MetricType.COUNTER,
                            timestamp=timestamp,
                            dimensions={"content_type": content_type},
                            unit="count"
                        ))
                        
                    # Protection alerts (last hour)
                    result = await conn.execute(text("""                        SELECT platform, status, COUNT(*) 
                        FROM protection_alerts 
                        WHERE created_at > NOW() - INTERVAL '1 hour'
                        GROUP BY platform, status
                    """))
                    
                    for row in result:
                        platform, status, count = row
                        metrics.append(BusinessMetric(
                            name="content.protection.alerts",
                            value=count,
                            metric_type=MetricType.COUNTER,
                            timestamp=timestamp,
                            dimensions={"platform": platform, "status": status},
                            unit="count"
                        ))
                        
            except Exception as e:
                logger.error(f"Error collecting content metrics: {e}")
                
        return metrics


class RevenueMetricsTracker:
    """Track revenue metrics"""    
    def __init__(self, db_engine: Optional[AsyncEngine]):
        self.db_engine = db_engine
        
    async def collect(self) -> List[BusinessMetric]:
        """Collect revenue metrics"""        metrics = []
        timestamp = datetime.utcnow()
        
        if self.db_engine:
            try:
                async with self.db_engine.begin() as conn:
                    # Revenue tracked (last 24 hours)
                    result = await conn.execute(text("""                        SELECT platform, currency, SUM(revenue_amount) 
                        FROM revenue_tracking 
                        WHERE created_at > NOW() - INTERVAL '1 day'
                        GROUP BY platform, currency
                    """))
                    
                    for row in result:
                        platform, currency, amount = row
                        metrics.append(BusinessMetric(
                            name="revenue.tracked.amount",
                            value=float(amount),
                            metric_type=MetricType.GAUGE,
                            timestamp=timestamp,
                            dimensions={"platform": platform, "currency": currency},
                            unit="currency"
                        ))
                        
            except Exception as e:
                logger.error(f"Error collecting revenue metrics: {e}")
                
        return metrics


class UserMetricsTracker:
    """Track user engagement metrics"""    
    def __init__(self, db_engine: Optional[AsyncEngine]):
        self.db_engine = db_engine
        
    async def collect(self) -> List[BusinessMetric]:
        """Collect user metrics"""        metrics = []
        timestamp = datetime.utcnow()
        
        if self.db_engine:
            try:
                async with self.db_engine.begin() as conn:
                    # Daily active users
                    result = await conn.execute(text("""                        SELECT COUNT(DISTINCT user_id) 
                        FROM user_sessions 
                        WHERE created_at > NOW() - INTERVAL '1 day'
                    """))
                    daily_active = result.scalar() or 0
                    
                    metrics.append(BusinessMetric(
                        name="users.active.daily",
                        value=daily_active,
                        metric_type=MetricType.GAUGE,
                        timestamp=timestamp,
                        unit="count"
                    ))
                    
                    # New registrations (last 24 hours)
                    result = await conn.execute(text("""                        SELECT COUNT(*) 
                        FROM users 
                        WHERE created_at > NOW() - INTERVAL '1 day'
                    """))
                    new_registrations = result.scalar() or 0
                    
                    metrics.append(BusinessMetric(
                        name="users.new.registrations",
                        value=new_registrations,
                        metric_type=MetricType.COUNTER,
                        timestamp=timestamp,
                        unit="count"
                    ))
                    
            except Exception as e:
                logger.error(f"Error collecting user metrics: {e}")
                
        return metrics
