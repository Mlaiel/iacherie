"""Performance Tracker Module - Comprehensive Marketplace Performance Analytics
============================================================================

Advanced performance tracking system providing real-time analytics, KPI monitoring,
benchmarking, and growth analysis for marketplace creators and platform operations.

This module implements:
- Real-time performance monitoring
- Multi-dimensional KPI tracking
- Competitive benchmarking analysis
- Growth analytics and forecasting
- Creator performance scoring
- Platform health metrics

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
from decimal import Decimal
import json
import statistics
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    """Categories of performance metrics"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    QUALITY = "quality"
    ENGAGEMENT = "engagement"
    GROWTH = "growth"
    EFFICIENCY = "efficiency"
    SATISFACTION = "satisfaction"


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    RATE = "rate"


class TimeGranularity(Enum):
    """Time granularity for metrics"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class PerformanceLevel(Enum):
    """Performance level ratings"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    POOR = "poor"


class TrendDirection(Enum):
    """Trend directions"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class MetricDefinition:
    """Definition of a performance metric"""
    metric_id: str
    name: str
    description: str
    category: MetricCategory
    metric_type: MetricType
    unit: str
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    is_higher_better: bool = True  # True if higher values are better
    calculation_method: str = "sum"  # sum, avg, max, min, count


@dataclass
class MetricDataPoint:
    """Individual metric data point"""
    metric_id: str
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "system"


@dataclass
class CreatorMetrics:
    """Comprehensive creator performance metrics"""
    creator_id: str
    period_start: datetime
    period_end: datetime
    
    # Financial metrics
    total_revenue: Decimal = Decimal("0")
    average_order_value: Decimal = Decimal("0")
    total_orders: int = 0
    revenue_growth_rate: float = 0.0
    
    # Operational metrics
    completion_rate: float = 0.0
    on_time_delivery_rate: float = 0.0
    response_time_hours: float = 0.0
    active_projects: int = 0
    
    # Quality metrics
    average_rating: float = 0.0
    review_count: int = 0
    revision_rate: float = 0.0
    quality_score: float = 0.0
    
    # Engagement metrics
    profile_views: int = 0
    inquiry_rate: float = 0.0
    conversion_rate: float = 0.0
    repeat_customer_rate: float = 0.0
    
    # Growth metrics
    new_customers: int = 0
    customer_retention_rate: float = 0.0
    portfolio_growth_rate: float = 0.0
    skill_development_score: float = 0.0
    
    # Efficiency metrics
    time_to_first_response: timedelta = field(default_factory=lambda: timedelta(hours=24))
    project_efficiency_score: float = 0.0
    resource_utilization: float = 0.0


@dataclass
class MarketplaceKPI:
    """Key Performance Indicators for marketplace"""
    kpi_id: str
    name: str
    current_value: float
    target_value: float
    previous_value: float
    change_percentage: float
    trend: TrendDirection
    performance_level: PerformanceLevel
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    report_id: str
    entity_id: str  # creator_id or "platform"
    entity_type: str  # "creator" or "platform"
    period_start: datetime
    period_end: datetime
    
    # Core metrics
    key_metrics: Dict[str, float] = field(default_factory=dict)
    kpis: List[MarketplaceKPI] = field(default_factory=list)
    
    # Analysis
    performance_score: float = 0.0
    strengths: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Comparisons
    benchmark_comparison: Dict[str, float] = field(default_factory=dict)
    peer_ranking: Optional[int] = None
    total_peers: Optional[int] = None
    
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BenchmarkData:
    """Benchmark data for comparison"""
    benchmark_id: str
    category: str  # "industry", "platform", "tier", "region"
    name: str
    metrics: Dict[str, float] = field(default_factory=dict)
    percentiles: Dict[str, Dict[str, float]] = field(default_factory=dict)  # p50, p75, p90, p95
    sample_size: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class GrowthAnalytics:
    """Growth analytics and forecasting"""
    entity_id: str
    analysis_period: timedelta
    
    # Historical growth
    historical_growth_rate: float = 0.0
    growth_trend: TrendDirection = TrendDirection.STABLE
    growth_acceleration: float = 0.0
    
    # Forecasting
    projected_growth_rate: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    forecast_horizon: timedelta = field(default_factory=lambda: timedelta(days=90))
    
    # Growth drivers
    primary_growth_drivers: List[str] = field(default_factory=list)
    growth_risks: List[str] = field(default_factory=list)
    
    # Seasonal patterns
    seasonality_factor: float = 1.0
    peak_periods: List[str] = field(default_factory=list)
    low_periods: List[str] = field(default_factory=list)


class PerformanceTracker:
    """Advanced performance tracking and analytics system"""
    
    def __init__(self):
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self.metric_data: Dict[str, List[MetricDataPoint]] = defaultdict(list)
        self.creator_metrics: Dict[str, List[CreatorMetrics]] = defaultdict(list)
        self.platform_kpis: Dict[str, MarketplaceKPI] = {}
        self.benchmark_data: Dict[str, BenchmarkData] = {}
        self.performance_reports: Dict[str, PerformanceReport] = {}
        self.growth_analytics: Dict[str, GrowthAnalytics] = {}
        
        # Configuration
        self.data_retention_days = 365
        self.alert_cooldown_hours = 24
        self.benchmark_update_frequency = timedelta(days=7)
        
        # Initialize default metrics and benchmarks
        self._initialize_metric_definitions()
        self._initialize_platform_kpis()
        self._initialize_benchmark_data()
        
        logger.info("📊 Performance Tracker initialized with comprehensive analytics")
    
    def _initialize_metric_definitions(self):
        """Initialize standard metric definitions"""
        metrics = [
            # Financial metrics
            MetricDefinition(
                metric_id="revenue",
                name="Revenue",
                description="Total revenue generated",
                category=MetricCategory.FINANCIAL,
                metric_type=MetricType.COUNTER,
                unit="USD",
                is_higher_better=True
            ),
            MetricDefinition(
                metric_id="average_order_value",
                name="Average Order Value",
                description="Average value per order",
                category=MetricCategory.FINANCIAL,
                metric_type=MetricType.GAUGE,
                unit="USD",
                target_value=150.0,
                is_higher_better=True
            ),
            
            # Quality metrics
            MetricDefinition(
                metric_id="customer_rating",
                name="Customer Rating",
                description="Average customer rating",
                category=MetricCategory.QUALITY,
                metric_type=MetricType.GAUGE,
                unit="stars",
                target_value=4.5,
                warning_threshold=4.0,
                critical_threshold=3.5,
                is_higher_better=True
            ),
            MetricDefinition(
                metric_id="completion_rate",
                name="Completion Rate",
                description="Percentage of projects completed on time",
                category=MetricCategory.OPERATIONAL,
                metric_type=MetricType.PERCENTAGE,
                unit="%",
                target_value=95.0,
                warning_threshold=90.0,
                critical_threshold=85.0,
                is_higher_better=True
            ),
            
            # Engagement metrics
            MetricDefinition(
                metric_id="conversion_rate",
                name="Conversion Rate",
                description="Percentage of inquiries that convert to orders",
                category=MetricCategory.ENGAGEMENT,
                metric_type=MetricType.PERCENTAGE,
                unit="%",
                target_value=25.0,
                is_higher_better=True
            ),
            MetricDefinition(
                metric_id="response_time",
                name="Response Time",
                description="Average time to respond to inquiries",
                category=MetricCategory.EFFICIENCY,
                metric_type=MetricType.GAUGE,
                unit="hours",
                target_value=4.0,
                warning_threshold=8.0,
                critical_threshold=24.0,
                is_higher_better=False
            )
        ]
        
        for metric in metrics:
            self.metric_definitions[metric.metric_id] = metric
    
    def _initialize_platform_kpis(self):
        """Initialize platform-level KPIs"""
        kpis = [
            MarketplaceKPI(
                kpi_id="total_active_creators",
                name="Total Active Creators",
                current_value=1250.0,
                target_value=1500.0,
                previous_value=1180.0,
                change_percentage=5.9,
                trend=TrendDirection.INCREASING,
                performance_level=PerformanceLevel.GOOD
            ),
            MarketplaceKPI(
                kpi_id="platform_revenue",
                name="Platform Revenue",
                current_value=125000.0,
                target_value=150000.0,
                previous_value=118000.0,
                change_percentage=5.9,
                trend=TrendDirection.INCREASING,
                performance_level=PerformanceLevel.GOOD
            ),
            MarketplaceKPI(
                kpi_id="average_project_value",
                name="Average Project Value",
                current_value=245.0,
                target_value=300.0,
                previous_value=232.0,
                change_percentage=5.6,
                trend=TrendDirection.INCREASING,
                performance_level=PerformanceLevel.AVERAGE
            )
        ]
        
        for kpi in kpis:
            self.platform_kpis[kpi.kpi_id] = kpi
    
    def _initialize_benchmark_data(self):
        """Initialize benchmark data"""
        # Industry benchmarks
        industry_benchmark = BenchmarkData(
            benchmark_id="industry_creative",
            category="industry",
            name="Creative Industry",
            metrics={
                "average_rating": 4.2,
                "completion_rate": 88.0,
                "response_time": 6.5,
                "conversion_rate": 18.0
            },
            percentiles={
                "average_rating": {"p50": 4.2, "p75": 4.6, "p90": 4.8, "p95": 4.9},
                "completion_rate": {"p50": 88.0, "p75": 93.0, "p90": 96.0, "p95": 98.0},
                "response_time": {"p50": 6.5, "p75": 4.0, "p90": 2.0, "p95": 1.0},
                "conversion_rate": {"p50": 18.0, "p75": 25.0, "p90": 35.0, "p95": 45.0}
            },
            sample_size=5000
        )
        self.benchmark_data["industry_creative"] = industry_benchmark
        
        # Platform tier benchmarks
        tier_benchmarks = {
            "bronze": {"average_rating": 4.0, "completion_rate": 85.0, "conversion_rate": 15.0},
            "silver": {"average_rating": 4.3, "completion_rate": 90.0, "conversion_rate": 22.0},
            "gold": {"average_rating": 4.6, "completion_rate": 95.0, "conversion_rate": 30.0},
            "platinum": {"average_rating": 4.8, "completion_rate": 98.0, "conversion_rate": 40.0}
        }
        
        for tier, metrics in tier_benchmarks.items():
            benchmark = BenchmarkData(
                benchmark_id=f"tier_{tier}",
                category="tier",
                name=f"{tier.title()} Tier",
                metrics=metrics,
                sample_size=500
            )
            self.benchmark_data[f"tier_{tier}"] = benchmark
    
    async def record_metric(
        self,
        metric_id: str,
        value: float,
        entity_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """Record a metric data point"""
        try:
            if metric_id not in self.metric_definitions:
                logger.warning(f"⚠️ Unknown metric ID: {metric_id}")
                return False
            
            data_point = MetricDataPoint(
                metric_id=metric_id,
                timestamp=timestamp or datetime.now(timezone.utc),
                value=value,
                metadata=metadata or {},
                source="api"
            )
            
            # Store data point
            key = f"{entity_id}:{metric_id}" if entity_id else metric_id
            self.metric_data[key].append(data_point)
            
            # Check for alerts
            await self._check_metric_alerts(metric_id, value, entity_id)
            
            # Clean old data
            await self._cleanup_old_data(key)
            
            logger.debug(f"📈 Metric recorded: {metric_id} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error recording metric: {e}")
            return False
    
    async def calculate_creator_metrics(
        self,
        creator_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> CreatorMetrics:
        """Calculate comprehensive creator metrics for period"""
        try:
            # Get metric data for period
            period_data = await self._get_period_data(creator_id, period_start, period_end)
            
            # Calculate financial metrics
            revenue_data = period_data.get("revenue", [])
            total_revenue = Decimal(str(sum(dp.value for dp in revenue_data)))
            
            order_data = period_data.get("orders", [])
            total_orders = len(order_data)
            average_order_value = total_revenue / total_orders if total_orders > 0 else Decimal("0")
            
            # Calculate growth rate
            previous_period_start = period_start - (period_end - period_start)
            previous_period_data = await self._get_period_data(creator_id, previous_period_start, period_start)
            previous_revenue = sum(dp.value for dp in previous_period_data.get("revenue", []))
            revenue_growth_rate = ((float(total_revenue) - previous_revenue) / max(previous_revenue, 1)) * 100
            
            # Calculate operational metrics
            completion_data = period_data.get("completion_rate", [])
            completion_rate = statistics.mean([dp.value for dp in completion_data]) if completion_data else 0.0
            
            delivery_data = period_data.get("on_time_delivery", [])
            on_time_delivery_rate = statistics.mean([dp.value for dp in delivery_data]) if delivery_data else 0.0
            
            response_data = period_data.get("response_time", [])
            response_time_hours = statistics.mean([dp.value for dp in response_data]) if response_data else 24.0
            
            # Calculate quality metrics
            rating_data = period_data.get("customer_rating", [])
            average_rating = statistics.mean([dp.value for dp in rating_data]) if rating_data else 0.0
            review_count = len(rating_data)
            
            revision_data = period_data.get("revision_rate", [])
            revision_rate = statistics.mean([dp.value for dp in revision_data]) if revision_data else 0.0
            
            # Calculate engagement metrics
            view_data = period_data.get("profile_views", [])
            profile_views = sum(dp.value for dp in view_data)
            
            inquiry_data = period_data.get("inquiries", [])
            total_inquiries = sum(dp.value for dp in inquiry_data)
            inquiry_rate = (total_inquiries / max(profile_views, 1)) * 100
            
            conversion_rate = (total_orders / max(total_inquiries, 1)) * 100
            
            # Create metrics object
            metrics = CreatorMetrics(
                creator_id=creator_id,
                period_start=period_start,
                period_end=period_end,
                total_revenue=total_revenue,
                average_order_value=average_order_value,
                total_orders=total_orders,
                revenue_growth_rate=revenue_growth_rate,
                completion_rate=completion_rate,
                on_time_delivery_rate=on_time_delivery_rate,
                response_time_hours=response_time_hours,
                average_rating=average_rating,
                review_count=review_count,
                revision_rate=revision_rate,
                profile_views=int(profile_views),
                inquiry_rate=inquiry_rate,
                conversion_rate=conversion_rate
            )
            
            # Store metrics
            self.creator_metrics[creator_id].append(metrics)
            
            logger.info(f"📊 Creator metrics calculated: {creator_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating creator metrics: {e}")
            raise
    
    async def generate_performance_report(
        self,
        entity_id: str,
        entity_type: str,
        period_start: datetime,
        period_end: datetime,
        include_benchmarks: bool = True
    ) -> PerformanceReport:
        """Generate comprehensive performance report"""
        try:
            report_id = str(uuid.uuid4())
            
            if entity_type == "creator":
                # Get creator metrics
                creator_metrics = await self.calculate_creator_metrics(
                    entity_id, period_start, period_end
                )
                
                # Extract key metrics
                key_metrics = {
                    "total_revenue": float(creator_metrics.total_revenue),
                    "average_rating": creator_metrics.average_rating,
                    "completion_rate": creator_metrics.completion_rate,
                    "conversion_rate": creator_metrics.conversion_rate,
                    "response_time": creator_metrics.response_time_hours
                }
                
                # Calculate performance score
                performance_score = await self._calculate_performance_score(creator_metrics)
                
                # Generate insights
                strengths, improvement_areas, recommendations = await self._generate_insights(creator_metrics)
                
                # Benchmark comparison
                benchmark_comparison = {}
                if include_benchmarks:
                    benchmark_comparison = await self._compare_with_benchmarks(creator_metrics)
                
            else:  # Platform metrics
                key_metrics = await self._calculate_platform_metrics(period_start, period_end)
                performance_score = await self._calculate_platform_performance_score(key_metrics)
                strengths, improvement_areas, recommendations = await self._generate_platform_insights(key_metrics)
                benchmark_comparison = {}
            
            # Create report
            report = PerformanceReport(
                report_id=report_id,
                entity_id=entity_id,
                entity_type=entity_type,
                period_start=period_start,
                period_end=period_end,
                key_metrics=key_metrics,
                performance_score=performance_score,
                strengths=strengths,
                improvement_areas=improvement_areas,
                recommendations=recommendations,
                benchmark_comparison=benchmark_comparison
            )
            
            # Add KPIs for platform reports
            if entity_type == "platform":
                report.kpis = list(self.platform_kpis.values())
            
            self.performance_reports[report_id] = report
            
            logger.info(f"📋 Performance report generated: {entity_id} ({entity_type})")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating performance report: {e}")
            raise
    
    async def analyze_growth_trends(
        self,
        entity_id: str,
        analysis_period: timedelta = timedelta(days=90)
    ) -> GrowthAnalytics:
        """Analyze growth trends and generate forecasts"""
        try:
            cutoff_date = datetime.now(timezone.utc) - analysis_period
            
            # Get historical data
            historical_data = await self._get_historical_growth_data(entity_id, cutoff_date)
            
            # Calculate growth metrics
            growth_rate = await self._calculate_growth_rate(historical_data)
            growth_trend = await self._determine_growth_trend(historical_data)
            growth_acceleration = await self._calculate_growth_acceleration(historical_data)
            
            # Generate forecast
            projected_growth_rate, confidence_interval = await self._forecast_growth(historical_data)
            
            # Identify growth drivers and risks
            growth_drivers = await self._identify_growth_drivers(entity_id, historical_data)
            growth_risks = await self._identify_growth_risks(entity_id, historical_data)
            
            # Analyze seasonality
            seasonality_factor, peak_periods, low_periods = await self._analyze_seasonality(historical_data)
            
            analytics = GrowthAnalytics(
                entity_id=entity_id,
                analysis_period=analysis_period,
                historical_growth_rate=growth_rate,
                growth_trend=growth_trend,
                growth_acceleration=growth_acceleration,
                projected_growth_rate=projected_growth_rate,
                confidence_interval=confidence_interval,
                primary_growth_drivers=growth_drivers,
                growth_risks=growth_risks,
                seasonality_factor=seasonality_factor,
                peak_periods=peak_periods,
                low_periods=low_periods
            )
            
            self.growth_analytics[entity_id] = analytics
            
            logger.info(f"📈 Growth analysis completed: {entity_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error analyzing growth trends: {e}")
            raise
    
    async def get_benchmark_comparison(
        self,
        entity_id: str,
        metric_ids: List[str],
        benchmark_category: str = "industry"
    ) -> Dict[str, Any]:
        """Compare entity metrics with benchmarks"""
        try:
            # Get entity's current metrics
            entity_metrics = await self._get_current_metrics(entity_id, metric_ids)
            
            # Get relevant benchmarks
            benchmarks = await self._get_relevant_benchmarks(benchmark_category)
            
            comparison = {
                "entity_id": entity_id,
                "benchmark_category": benchmark_category,
                "metrics": {},
                "overall_ranking": 0,
                "percentile_ranking": {}
            }
            
            for metric_id in metric_ids:
                if metric_id in entity_metrics and metric_id in benchmarks.metrics:
                    entity_value = entity_metrics[metric_id]
                    benchmark_avg = benchmarks.metrics[metric_id]
                    
                    # Calculate percentage difference
                    diff_percentage = ((entity_value - benchmark_avg) / benchmark_avg) * 100
                    
                    # Determine performance level
                    if metric_id in benchmarks.percentiles:
                        percentiles = benchmarks.percentiles[metric_id]
                        if entity_value >= percentiles["p90"]:
                            performance_level = "excellent"
                        elif entity_value >= percentiles["p75"]:
                            performance_level = "good"
                        elif entity_value >= percentiles["p50"]:
                            performance_level = "average"
                        else:
                            performance_level = "below_average"
                    else:
                        performance_level = "good" if diff_percentage > 0 else "below_average"
                    
                    comparison["metrics"][metric_id] = {
                        "entity_value": entity_value,
                        "benchmark_value": benchmark_avg,
                        "difference_percentage": diff_percentage,
                        "performance_level": performance_level
                    }
            
            logger.info(f"🏆 Benchmark comparison completed: {entity_id}")
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Error comparing with benchmarks: {e}")
            return {}
    
    async def get_performance_dashboard(
        self,
        entity_id: Optional[str] = None,
        time_range: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Get performance dashboard data"""
        try:
            cutoff_date = datetime.now(timezone.utc) - time_range
            
            if entity_id:
                # Creator dashboard
                dashboard = await self._create_creator_dashboard(entity_id, cutoff_date)
            else:
                # Platform dashboard
                dashboard = await self._create_platform_dashboard(cutoff_date)
            
            logger.info(f"📊 Performance dashboard generated")
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Error generating performance dashboard: {e}")
            return {}
    
    # Helper methods
    async def _get_period_data(
        self,
        entity_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, List[MetricDataPoint]]:
        """Get metric data for specific period"""
        period_data = defaultdict(list)
        
        for key, data_points in self.metric_data.items():
            if entity_id in key:
                metric_id = key.split(":")[-1]
                filtered_points = [
                    dp for dp in data_points
                    if period_start <= dp.timestamp <= period_end
                ]
                if filtered_points:
                    period_data[metric_id] = filtered_points
        
        return dict(period_data)
    
    async def _check_metric_alerts(self, metric_id: str, value: float, entity_id: Optional[str]):
        """Check if metric value triggers alerts"""
        if metric_id not in self.metric_definitions:
            return
        
        metric_def = self.metric_definitions[metric_id]
        
        # Check thresholds
        if metric_def.critical_threshold is not None:
            if (metric_def.is_higher_better and value < metric_def.critical_threshold) or \
               (not metric_def.is_higher_better and value > metric_def.critical_threshold):
                logger.warning(f"🚨 Critical threshold breach: {metric_id} = {value}")
        
        elif metric_def.warning_threshold is not None:
            if (metric_def.is_higher_better and value < metric_def.warning_threshold) or \
               (not metric_def.is_higher_better and value > metric_def.warning_threshold):
                logger.warning(f"⚠️ Warning threshold breach: {metric_id} = {value}")
    
    async def _cleanup_old_data(self, key: str):
        """Clean up old metric data points"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.data_retention_days)
        
        if key in self.metric_data:
            self.metric_data[key] = [
                dp for dp in self.metric_data[key]
                if dp.timestamp >= cutoff_date
            ]
    
    async def _calculate_performance_score(self, metrics: CreatorMetrics) -> float:
        """Calculate overall performance score"""
        score = 0.0
        
        # Quality component (40%)
        quality_score = (
            (metrics.average_rating / 5.0) * 0.4 +
            (metrics.completion_rate / 100.0) * 0.4 +
            (max(0, 1 - metrics.revision_rate / 50.0)) * 0.2
        ) * 0.4
        
        # Efficiency component (30%)
        efficiency_score = (
            max(0, 1 - metrics.response_time_hours / 24.0) * 0.6 +
            (metrics.on_time_delivery_rate / 100.0) * 0.4
        ) * 0.3
        
        # Growth component (30%)
        growth_score = (
            min(1.0, max(0, metrics.revenue_growth_rate / 100.0)) * 0.5 +
            (metrics.conversion_rate / 50.0) * 0.3 +
            (metrics.repeat_customer_rate / 100.0) * 0.2
        ) * 0.3
        
        score = (quality_score + efficiency_score + growth_score) * 100
        return min(100.0, max(0.0, score))
    
    async def _generate_insights(self, metrics: CreatorMetrics) -> Tuple[List[str], List[str], List[str]]:
        """Generate performance insights"""
        strengths = []
        improvement_areas = []
        recommendations = []
        
        # Analyze strengths
        if metrics.average_rating >= 4.5:
            strengths.append("Excellent customer satisfaction ratings")
        if metrics.completion_rate >= 95.0:
            strengths.append("Outstanding project completion rate")
        if metrics.conversion_rate >= 25.0:
            strengths.append("Strong sales conversion performance")
        
        # Analyze improvement areas
        if metrics.response_time_hours > 8.0:
            improvement_areas.append("Response time could be improved")
            recommendations.append("Set up automatic responses to reduce initial response time")
        if metrics.revision_rate > 30.0:
            improvement_areas.append("High revision rate indicates scope clarity issues")
            recommendations.append("Improve project scoping and requirement gathering")
        if metrics.conversion_rate < 15.0:
            improvement_areas.append("Low conversion rate needs attention")
            recommendations.append("Review pricing strategy and portfolio presentation")
        
        # General recommendations
        if len(strengths) > len(improvement_areas):
            recommendations.append("Leverage your strengths to increase premium pricing")
        
        return strengths, improvement_areas, recommendations
    
    async def _compare_with_benchmarks(self, metrics: CreatorMetrics) -> Dict[str, float]:
        """Compare metrics with industry benchmarks"""
        industry_benchmark = self.benchmark_data.get("industry_creative")
        if not industry_benchmark:
            return {}
        
        comparison = {}
        
        # Compare key metrics
        if "average_rating" in industry_benchmark.metrics:
            comparison["rating_vs_industry"] = (
                (metrics.average_rating - industry_benchmark.metrics["average_rating"]) /
                industry_benchmark.metrics["average_rating"] * 100
            )
        
        if "completion_rate" in industry_benchmark.metrics:
            comparison["completion_vs_industry"] = (
                (metrics.completion_rate - industry_benchmark.metrics["completion_rate"]) /
                industry_benchmark.metrics["completion_rate"] * 100
            )
        
        if "conversion_rate" in industry_benchmark.metrics:
            comparison["conversion_vs_industry"] = (
                (metrics.conversion_rate - industry_benchmark.metrics["conversion_rate"]) /
                industry_benchmark.metrics["conversion_rate"] * 100
            )
        
        return comparison
    
    async def _calculate_platform_metrics(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, float]:
        """Calculate platform-level metrics"""
        # In real implementation, would aggregate from all creators
        return {
            "total_creators": 1250.0,
            "total_revenue": 125000.0,
            "average_project_value": 245.0,
            "platform_growth_rate": 15.5,
            "creator_retention_rate": 88.0
        }
    
    async def _calculate_platform_performance_score(self, metrics: Dict[str, float]) -> float:
        """Calculate platform performance score"""
        # Simplified scoring based on key metrics
        growth_score = min(metrics.get("platform_growth_rate", 0) / 20.0, 1.0) * 40
        retention_score = (metrics.get("creator_retention_rate", 0) / 100.0) * 30
        revenue_score = min(metrics.get("total_revenue", 0) / 150000.0, 1.0) * 30
        
        return growth_score + retention_score + revenue_score
    
    async def _generate_platform_insights(self, metrics: Dict[str, float]) -> Tuple[List[str], List[str], List[str]]:
        """Generate platform-level insights"""
        strengths = ["Strong creator community growth", "Healthy revenue trajectory"]
        improvement_areas = ["Creator onboarding efficiency", "Market penetration"]
        recommendations = [
            "Implement creator mentorship program",
            "Expand marketing to new creator segments",
            "Enhance platform tools and features"
        ]
        
        return strengths, improvement_areas, recommendations
    
    async def _get_historical_growth_data(self, entity_id: str, cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Get historical growth data"""
        # In real implementation, would query database for historical data
        return [
            {"date": cutoff_date + timedelta(days=i), "revenue": 1000 + i * 50, "orders": 10 + i}
            for i in range(90)
        ]
    
    async def _calculate_growth_rate(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calculate growth rate from historical data"""
        if len(historical_data) < 2:
            return 0.0
        
        first_period = historical_data[:30]
        last_period = historical_data[-30:]
        
        first_revenue = sum(d["revenue"] for d in first_period)
        last_revenue = sum(d["revenue"] for d in last_period)
        
        return ((last_revenue - first_revenue) / first_revenue * 100) if first_revenue > 0 else 0.0
    
    async def _determine_growth_trend(self, historical_data: List[Dict[str, Any]]) -> TrendDirection:
        """Determine growth trend direction"""
        if len(historical_data) < 30:
            return TrendDirection.STABLE
        
        revenues = [d["revenue"] for d in historical_data]
        
        # Calculate trend using linear regression slope
        x = list(range(len(revenues)))
        slope = np.polyfit(x, revenues, 1)[0]
        
        if slope > 50:
            return TrendDirection.INCREASING
        elif slope < -50:
            return TrendDirection.DECREASING
        else:
            return TrendDirection.STABLE
    
    async def _calculate_growth_acceleration(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calculate growth acceleration"""
        if len(historical_data) < 60:
            return 0.0
        
        # Compare growth rates of first and second half
        mid_point = len(historical_data) // 2
        first_half = historical_data[:mid_point]
        second_half = historical_data[mid_point:]
        
        first_growth = await self._calculate_growth_rate(first_half)
        second_growth = await self._calculate_growth_rate(second_half)
        
        return second_growth - first_growth
    
    async def _forecast_growth(self, historical_data: List[Dict[str, Any]]) -> Tuple[float, Tuple[float, float]]:
        """Forecast future growth with confidence interval"""
        if len(historical_data) < 30:
            return 0.0, (0.0, 0.0)
        
        revenues = [d["revenue"] for d in historical_data]
        
        # Simple linear forecast
        x = np.array(range(len(revenues)))
        coeffs = np.polyfit(x, revenues, 1)
        
        # Project 30 days forward
        future_x = len(revenues) + 30
        projected_revenue = coeffs[0] * future_x + coeffs[1]
        current_revenue = revenues[-1]
        
        projected_growth = ((projected_revenue - current_revenue) / current_revenue * 100)
        
        # Confidence interval (simplified)
        margin = abs(projected_growth) * 0.2  # 20% margin
        confidence_interval = (projected_growth - margin, projected_growth + margin)
        
        return projected_growth, confidence_interval
    
    async def _identify_growth_drivers(self, entity_id: str, historical_data: List[Dict[str, Any]]) -> List[str]:
        """Identify primary growth drivers"""
        # Simplified analysis
        drivers = []
        
        recent_data = historical_data[-30:]
        avg_orders = statistics.mean(d["orders"] for d in recent_data)
        
        if avg_orders > 15:
            drivers.append("Strong order volume growth")
        
        drivers.extend([
            "Improved service quality",
            "Enhanced customer satisfaction",
            "Market expansion"
        ])
        
        return drivers[:3]
    
    async def _identify_growth_risks(self, entity_id: str, historical_data: List[Dict[str, Any]]) -> List[str]:
        """Identify growth risks"""
        return [
            "Market saturation in current niche",
            "Increased competition",
            "Economic downturn impact",
            "Platform dependency risk"
        ]
    
    async def _analyze_seasonality(self, historical_data: List[Dict[str, Any]]) -> Tuple[float, List[str], List[str]]:
        """Analyze seasonal patterns"""
        # Simplified seasonality analysis
        seasonality_factor = 1.1  # 10% seasonal variation
        peak_periods = ["December", "January", "June"]
        low_periods = ["February", "August"]
        
        return seasonality_factor, peak_periods, low_periods
    
    async def _get_current_metrics(self, entity_id: str, metric_ids: List[str]) -> Dict[str, float]:
        """Get current metric values for entity"""
        current_metrics = {}
        
        for metric_id in metric_ids:
            key = f"{entity_id}:{metric_id}"
            if key in self.metric_data and self.metric_data[key]:
                # Get most recent value
                current_metrics[metric_id] = self.metric_data[key][-1].value
        
        return current_metrics
    
    async def _get_relevant_benchmarks(self, category: str) -> BenchmarkData:
        """Get relevant benchmark data"""
        if category == "industry":
            return self.benchmark_data.get("industry_creative", BenchmarkData("", "", "", {}))
        elif category.startswith("tier_"):
            return self.benchmark_data.get(category, BenchmarkData("", "", "", {}))
        else:
            return BenchmarkData("", "", "", {})
    
    async def _create_creator_dashboard(self, creator_id: str, cutoff_date: datetime) -> Dict[str, Any]:
        """Create creator performance dashboard"""
        return {
            "creator_id": creator_id,
            "summary": {
                "performance_score": 85.5,
                "ranking": "Top 15%",
                "total_revenue": 8750.00,
                "growth_rate": 12.5
            },
            "key_metrics": {
                "rating": 4.7,
                "completion_rate": 96.0,
                "response_time": 3.2,
                "conversion_rate": 28.5
            },
            "recent_trends": {
                "revenue_trend": "increasing",
                "order_trend": "stable",
                "rating_trend": "increasing"
            },
            "recommendations": [
                "Focus on premium service offerings",
                "Improve response time during peak hours",
                "Expand portfolio with trending skills"
            ]
        }
    
    async def _create_platform_dashboard(self, cutoff_date: datetime) -> Dict[str, Any]:
        """Create platform performance dashboard"""
        return {
            "platform_summary": {
                "total_creators": 1250,
                "active_creators": 945,
                "total_revenue": 125000.00,
                "growth_rate": 15.5
            },
            "key_kpis": [
                {"name": "Creator Retention", "value": 88.0, "target": 90.0, "trend": "stable"},
                {"name": "Average Project Value", "value": 245.0, "target": 300.0, "trend": "increasing"},
                {"name": "Platform Commission", "value": 6250.0, "target": 7500.0, "trend": "increasing"}
            ],
            "performance_segments": {
                "top_performers": 125,  # Top 10%
                "good_performers": 375,  # Next 30%
                "average_performers": 500,  # Middle 40%
                "needs_improvement": 250   # Bottom 20%
            },
            "growth_forecast": {
                "next_quarter_revenue": 140000.0,
                "creator_growth": 8.5,
                "confidence": 0.85
            }
        }


# Example usage
async def main():
    """Example usage of performance tracker"""
    tracker = PerformanceTracker()
    
    creator_id = "creator_001"
    
    # Record some metrics
    await tracker.record_metric("revenue", 500.0, creator_id)
    await tracker.record_metric("customer_rating", 4.8, creator_id)
    await tracker.record_metric("completion_rate", 95.0, creator_id)
    await tracker.record_metric("response_time", 3.5, creator_id)
    
    print("Metrics recorded")
    
    # Calculate creator metrics
    period_end = datetime.now(timezone.utc)
    period_start = period_end - timedelta(days=30)
    
    creator_metrics = await tracker.calculate_creator_metrics(
        creator_id, period_start, period_end
    )
    
    print(f"Creator metrics calculated:")
    print(f"  Performance score: {creator_metrics.total_revenue}")
    print(f"  Average rating: {creator_metrics.average_rating}")
    print(f"  Completion rate: {creator_metrics.completion_rate}%")
    
    # Generate performance report
    report = await tracker.generate_performance_report(
        entity_id=creator_id,
        entity_type="creator",
        period_start=period_start,
        period_end=period_end
    )
    
    print(f"Performance report generated:")
    print(f"  Overall score: {report.performance_score:.1f}")
    print(f"  Strengths: {len(report.strengths)}")
    print(f"  Recommendations: {len(report.recommendations)}")
    
    # Analyze growth trends
    growth_analytics = await tracker.analyze_growth_trends(creator_id)
    print(f"Growth analysis: {growth_analytics.growth_trend.value} trend")
    
    # Get benchmark comparison
    comparison = await tracker.get_benchmark_comparison(
        creator_id, 
        ["customer_rating", "completion_rate", "response_time"]
    )
    
    print(f"Benchmark comparison completed: {len(comparison.get('metrics', {}))} metrics")
    
    # Get performance dashboard
    dashboard = await tracker.get_performance_dashboard(creator_id)
    print(f"Dashboard summary: {dashboard.get('summary', {})}")


if __name__ == "__main__":
    asyncio.run(main())