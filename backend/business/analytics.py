"""Business Analytics - IA Influencer Agent Platform
=================================================

Advanced business intelligence and analytics for content performance,
revenue tracking, audience insights, platform metrics, and enterprise
decision support with AI-powered analytics and predictive modeling.

Enhanced Features (Phase 3):
- Advanced business intelligence & data mining
- Predictive analytics & machine learning models
- Real-time dashboard automation
- Cross-platform analytics integration
- Enterprise decision support systems
- AI-powered insights generation

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import statistics
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict, Counter

# Optional imports for advanced analytics
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of analytics metrics."""
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    CONTENT = "content"
    AUDIENCE = "audience"
    PERFORMANCE = "performance"
    COLLABORATION = "collaboration"
    CONVERSION = "conversion"
    RETENTION = "retention"
    PARTNERSHIP = "partnership"
    MARKET_INTELLIGENCE = "market_intelligence"
    RISK = "risk"
    INNOVATION = "innovation"


class AggregationPeriod(Enum):
    """Time periods for data aggregation."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AnalyticsFramework(Enum):
    """Analytics framework types."""
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"


@dataclass
class BusinessMetric:
    """Business metric representation with enhanced features."""
    metric_id: str
    name: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    dimensions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 1.0
    data_source: str = "business_analytics"
    trend_direction: Optional[str] = None
    benchmark_comparison: Optional[Dict[str, float]] = None


@dataclass
class AnalyticsInsight:
    """AI-generated analytics insight."""
    insight_id: str
    title: str
    description: str
    category: str
    confidence_score: float
    impact_level: str  # "high", "medium", "low"
    actionable_recommendations: List[str]
    supporting_data: Dict[str, Any]
    generated_at: datetime
    expires_at: Optional[datetime] = None


class BusinessAnalytics:
    """Enhanced business analytics with AI-powered insights and predictive modeling."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize business analytics with enhanced capabilities."""
        self.config = config or {}
        self.metrics_store: Dict[str, List[BusinessMetric]] = defaultdict(list)
        self.insights_cache: Dict[str, AnalyticsInsight] = {}
        self.ml_models: Dict[str, Any] = {}
        self.dashboard_configs: Dict[str, Dict[str, Any]] = {}
        
    async def analyze_business_performance(
        self,
        analysis_scope: str,
        metrics_to_analyze: List[MetricType],
        time_period: AggregationPeriod,
        include_predictions: bool = True,
        include_insights: bool = True
    ) -> Dict[str, Any]:
        """Comprehensive business performance analysis with AI insights."""
        try:
            analysis_id = str(uuid.uuid4())
            
            performance_analysis = {
                "analysis_id": analysis_id,
                "analysis_scope": analysis_scope,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                "time_period": time_period.value,
                "metrics_analyzed": [metric.value for metric in metrics_to_analyze],
                "performance_summary": {},
                "trend_analysis": {},
                "comparative_analysis": {},
                "kpi_dashboard": {},
                "insights": [],
                "predictions": {},
                "recommendations": []
            }
            
            # Analyze each metric type
            for metric_type in metrics_to_analyze:
                metric_analysis = await self._analyze_metric_type(
                    metric_type, time_period, analysis_scope
                )
                performance_analysis["performance_summary"][metric_type.value] = metric_analysis
            
            # Generate trend analysis
            performance_analysis["trend_analysis"] = await self._generate_trend_analysis(
                metrics_to_analyze, time_period
            )
            
            # Perform comparative analysis
            performance_analysis["comparative_analysis"] = await self._perform_comparative_analysis(
                performance_analysis["performance_summary"]
            )
            
            # Create KPI dashboard
            performance_analysis["kpi_dashboard"] = await self._create_kpi_dashboard(
                performance_analysis["performance_summary"]
            )
            
            # Generate AI insights
            if include_insights:
                performance_analysis["insights"] = await self._generate_ai_insights(
                    performance_analysis
                )
            
            # Generate predictions
            if include_predictions:
                performance_analysis["predictions"] = await self._generate_performance_predictions(
                    performance_analysis
                )
            
            # Generate actionable recommendations
            performance_analysis["recommendations"] = await self._generate_actionable_recommendations(
                performance_analysis
            )
            
            logger.info(f"Business performance analysis completed: {analysis_id}")
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Business performance analysis failed: {e}")
            raise

    async def create_real_time_dashboard(
        self,
        dashboard_name: str,
        metrics_config: Dict[str, Any],
        refresh_interval_seconds: int = 60,
        include_alerts: bool = True
    ) -> Dict[str, Any]:
        """Create real-time business analytics dashboard."""
        try:
            dashboard_id = str(uuid.uuid4())
            
            dashboard_config = {
                "dashboard_id": dashboard_id,
                "name": dashboard_name,
                "metrics_config": metrics_config,
                "refresh_interval": refresh_interval_seconds,
                "include_alerts": include_alerts,
                "widgets": [],
                "alert_rules": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "active"
            }
            
            # Create dashboard widgets
            widgets = await self._create_dashboard_widgets(metrics_config)
            dashboard_config["widgets"] = widgets
            
            # Setup alert rules
            if include_alerts:
                alert_rules = await self._setup_dashboard_alerts(metrics_config)
                dashboard_config["alert_rules"] = alert_rules
            
            # Initialize real-time data feeds
            data_feeds = await self._initialize_real_time_feeds(dashboard_config)
            dashboard_config["data_feeds"] = data_feeds
            
            # Store dashboard configuration
            self.dashboard_configs[dashboard_id] = dashboard_config
            
            logger.info(f"Real-time dashboard created: {dashboard_name}")
            return dashboard_config
            
        except Exception as e:
            logger.error(f"Dashboard creation failed: {e}")
            raise

    async def generate_executive_summary(
        self,
        reporting_period: Tuple[datetime, datetime],
        focus_areas: List[str],
        audience: str = "executive"
    ) -> Dict[str, Any]:
        """Generate executive summary with key insights and recommendations."""
        try:
            start_date, end_date = reporting_period
            summary_id = str(uuid.uuid4())
            
            executive_summary = {
                "summary_id": summary_id,
                "reporting_period": f"{start_date.isoformat()} - {end_date.isoformat()}",
                "audience": audience,
                "focus_areas": focus_areas,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "key_highlights": {},
                "performance_scorecard": {},
                "strategic_insights": [],
                "risk_indicators": [],
                "opportunities": [],
                "executive_recommendations": [],
                "appendix": {}
            }
            
            # Generate key highlights
            executive_summary["key_highlights"] = await self._generate_key_highlights(
                reporting_period, focus_areas
            )
            
            # Create performance scorecard
            executive_summary["performance_scorecard"] = await self._create_performance_scorecard(
                reporting_period
            )
            
            # Generate strategic insights
            executive_summary["strategic_insights"] = await self._generate_strategic_insights(
                executive_summary["key_highlights"], focus_areas
            )
            
            # Identify risk indicators
            executive_summary["risk_indicators"] = await self._identify_risk_indicators(
                executive_summary["performance_scorecard"]
            )
            
            # Identify opportunities
            executive_summary["opportunities"] = await self._identify_business_opportunities(
                executive_summary
            )
            
            # Generate executive recommendations
            executive_summary["executive_recommendations"] = await self._generate_executive_recommendations(
                executive_summary, audience
            )
            
            logger.info(f"Executive summary generated: {summary_id}")
            return executive_summary
            
        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            raise

    async def _analyze_metric_type(
        self,
        metric_type: MetricType,
        time_period: AggregationPeriod,
        analysis_scope: str
    ) -> Dict[str, Any]:
        """Analyze specific metric type with enhanced analytics."""
        # Get relevant metrics
        metrics = await self._get_metrics_by_type(metric_type, analysis_scope)
        
        if not metrics:
            return {
                "metric_type": metric_type.value,
                "status": "no_data",
                "message": f"No data available for {metric_type.value}"
            }
        
        # Calculate basic statistics
        values = [metric.value for metric in metrics]
        
        analysis = {
            "metric_type": metric_type.value,
            "data_points": len(metrics),
            "current_value": values[-1] if values else 0,
            "average": statistics.mean(values) if values else 0,
            "median": statistics.median(values) if values else 0,
            "std_deviation": statistics.stdev(values) if len(values) > 1 else 0,
            "min_value": min(values) if values else 0,
            "max_value": max(values) if values else 0,
            "trend": await self._calculate_trend(values),
            "growth_rate": await self._calculate_growth_rate(values),
            "seasonality": await self._detect_seasonality(values),
            "anomalies": await self._detect_anomalies(values)
        }
        
        return analysis

    async def _generate_trend_analysis(
        self,
        metrics_types: List[MetricType],
        time_period: AggregationPeriod
    ) -> Dict[str, Any]:
        """Generate comprehensive trend analysis."""
        trend_analysis = {
            "overall_trend": "stable",
            "metric_trends": {},
            "correlation_matrix": {},
            "trend_strength": 0.0,
            "trend_consistency": 0.0
        }
        
        # Analyze trends for each metric type
        trends = []
        for metric_type in metrics_types:
            metrics = await self._get_metrics_by_type(metric_type, "global")
            if metrics:
                values = [metric.value for metric in metrics]
                trend = await self._calculate_trend(values)
                trend_analysis["metric_trends"][metric_type.value] = trend
                trends.append(1 if trend == "increasing" else -1 if trend == "decreasing" else 0)
        
        # Determine overall trend
        if trends:
            avg_trend = statistics.mean(trends)
            if avg_trend > 0.3:
                trend_analysis["overall_trend"] = "increasing"
            elif avg_trend < -0.3:
                trend_analysis["overall_trend"] = "decreasing"
            else:
                trend_analysis["overall_trend"] = "stable"
            
            trend_analysis["trend_strength"] = abs(avg_trend)
            trend_analysis["trend_consistency"] = 1.0 - statistics.stdev(trends) if len(trends) > 1 else 1.0
        
        return trend_analysis

    async def _generate_ai_insights(self, analysis_data: Dict[str, Any]) -> List[AnalyticsInsight]:
        """Generate AI-powered insights from analysis data."""
        insights = []
        
        # Revenue insights
        if "revenue" in analysis_data["performance_summary"]:
            revenue_data = analysis_data["performance_summary"]["revenue"]
            if revenue_data.get("growth_rate", 0) > 0.2:
                insights.append(AnalyticsInsight(
                    insight_id=str(uuid.uuid4()),
                    title="Strong Revenue Growth Detected",
                    description=f"Revenue growing at {revenue_data.get('growth_rate', 0):.1%} rate",
                    category="performance",
                    confidence_score=0.9,
                    impact_level="high",
                    actionable_recommendations=[
                        "Scale successful revenue channels",
                        "Investigate growth drivers for replication",
                        "Increase investment in high-performing areas"
                    ],
                    supporting_data=revenue_data,
                    generated_at=datetime.now(timezone.utc)
                ))
        
        # Engagement insights
        if "engagement" in analysis_data["performance_summary"]:
            engagement_data = analysis_data["performance_summary"]["engagement"]
            if engagement_data.get("trend") == "decreasing":
                insights.append(AnalyticsInsight(
                    insight_id=str(uuid.uuid4()),
                    title="Declining Engagement Trend",
                    description="Audience engagement showing downward trend",
                    category="engagement",
                    confidence_score=0.8,
                    impact_level="medium",
                    actionable_recommendations=[
                        "Review content strategy",
                        "Analyze audience preferences",
                        "Test new engagement formats"
                    ],
                    supporting_data=engagement_data,
                    generated_at=datetime.now(timezone.utc)
                ))
        
        # Performance insights
        overall_trend = analysis_data.get("trend_analysis", {}).get("overall_trend", "stable")
        if overall_trend == "increasing":
            insights.append(AnalyticsInsight(
                insight_id=str(uuid.uuid4()),
                title="Positive Business Momentum",
                description="Multiple metrics showing positive trends",
                category="overall_performance",
                confidence_score=0.85,
                impact_level="high",
                actionable_recommendations=[
                    "Maintain current strategies",
                    "Scale successful initiatives",
                    "Prepare for growth challenges"
                ],
                supporting_data=analysis_data["trend_analysis"],
                generated_at=datetime.now(timezone.utc)
            ))
        
        return insights

    async def _generate_performance_predictions(
        self,
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate performance predictions using ML models."""
        predictions = {
            "prediction_horizon_days": 30,
            "confidence_level": 0.8,
            "metric_predictions": {},
            "scenario_analysis": {},
            "prediction_accuracy": "estimated"
        }
        
        # Generate predictions for each metric type
        for metric_type, metric_data in analysis_data["performance_summary"].items():
            if metric_data.get("status") != "no_data":
                current_value = metric_data.get("current_value", 0)
                growth_rate = metric_data.get("growth_rate", 0)
                
                # Simple prediction model (in production would use ML)
                predicted_value = current_value * (1 + growth_rate * 0.1)  # 10% of growth rate applied
                
                predictions["metric_predictions"][metric_type] = {
                    "current_value": current_value,
                    "predicted_value": predicted_value,
                    "growth_projection": growth_rate,
                    "confidence": 0.75,
                    "prediction_range": {
                        "low": predicted_value * 0.9,
                        "high": predicted_value * 1.1
                    }
                }
        
        return predictions

    async def _get_metrics_by_type(
        self,
        metric_type: MetricType,
        scope: str
    ) -> List[BusinessMetric]:
        """Get metrics filtered by type and scope."""
        # Mock data - in production would query actual metrics database
        mock_metrics = []
        
        for i in range(30):  # 30 days of data
            timestamp = datetime.now(timezone.utc) - timedelta(days=i)
            value = 100 + (i * 2) + (10 * (i % 7))  # Mock trending data
            
            mock_metrics.append(BusinessMetric(
                metric_id=str(uuid.uuid4()),
                name=f"{metric_type.value}_metric",
                metric_type=metric_type,
                value=value,
                unit="count",
                timestamp=timestamp,
                data_source=scope
            ))
        
        return mock_metrics

    async def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear regression slope
        n = len(values)
        x_values = list(range(n))
        
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"

    async def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate growth rate from values."""
        if len(values) < 2:
            return 0.0
        
        first_value = values[0]
        last_value = values[-1]
        
        if first_value == 0:
            return 0.0
        
        return (last_value - first_value) / first_value

    async def _detect_seasonality(self, values: List[float]) -> Dict[str, Any]:
        """Detect seasonality patterns in data."""
        if len(values) < 14:  # Need at least 2 weeks of data
            return {"has_seasonality": False, "pattern": "insufficient_data"}
        
        # Simple weekly pattern detection
        weekly_averages = []
        for i in range(7):
            week_values = [values[j] for j in range(i, len(values), 7)]
            if week_values:
                weekly_averages.append(statistics.mean(week_values))
        
        if len(weekly_averages) == 7:
            weekly_std = statistics.stdev(weekly_averages)
            weekly_mean = statistics.mean(weekly_averages)
            
            # Check if there's significant variation
            coefficient_of_variation = weekly_std / weekly_mean if weekly_mean > 0 else 0
            
            return {
                "has_seasonality": coefficient_of_variation > 0.1,
                "pattern": "weekly" if coefficient_of_variation > 0.1 else "none",
                "strength": coefficient_of_variation
            }
        
        return {"has_seasonality": False, "pattern": "unknown"}

    async def _detect_anomalies(self, values: List[float]) -> List[Dict[str, Any]]:
        """Detect anomalies in data using statistical methods."""
        if len(values) < 10:
            return []
        
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        threshold = 2 * std_val  # 2-sigma threshold
        
        anomalies = []
        for i, value in enumerate(values):
            if abs(value - mean_val) > threshold:
                anomalies.append({
                    "index": i,
                    "value": value,
                    "deviation": abs(value - mean_val),
                    "severity": "high" if abs(value - mean_val) > 3 * std_val else "medium"
                })
        
        return anomalies
    """Aggregation time periods."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class AnalyticsMetric:
    """Individual analytics metric."""
    metric_id: str
    name: str
    metric_type: MetricType
    value: Union[int, float, Dict[str, Any]]
    unit: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    dimensions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsQuery:
    """Analytics query definition."""
    query_id: str
    metric_types: List[MetricType]
    start_date: datetime
    end_date: datetime
    aggregation: AggregationPeriod
    filters: Dict[str, Any] = field(default_factory=dict)
    dimensions: List[str] = field(default_factory=list)
    limit: Optional[int] = None


@dataclass
class AnalyticsReport:
    """Analytics report result."""
    report_id: str
    query: AnalyticsQuery
    metrics: List[AnalyticsMetric]
    summary: Dict[str, Any]
    generated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BusinessAnalytics:
    """
    Consolidated business analytics engine for the IA Influencer platform.
    
    Provides comprehensive analytics for content performance, revenue tracking,
    audience insights, engagement metrics, and business intelligence.
    """
    
    def __init__(self):
        """Initialize the business analytics engine."""
        self.metrics_store: List[AnalyticsMetric] = []
        self.reports_cache: Dict[str, AnalyticsReport] = {}
        self.logger = logging.getLogger(__name__)
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample analytics data for demonstration."""
        current_time = datetime.utcnow()
        
        # Sample engagement metrics
        for i in range(30):
            date = current_time - timedelta(days=i)
            
            # Daily engagement metrics
            import random
            self.metrics_store.append(AnalyticsMetric(
                metric_id=f"engagement_daily_{i}",
                name="Daily Engagement Rate",
                metric_type=MetricType.ENGAGEMENT,
                value=round(random.normalvariate(0.15, 0.05), 3),
                unit="percentage",
                timestamp=date,
                dimensions={"period": "daily", "platform": "all"}
            ))
            
            # Daily revenue metrics
            self.metrics_store.append(AnalyticsMetric(
                metric_id=f"revenue_daily_{i}",
                name="Daily Revenue",
                metric_type=MetricType.REVENUE,
                value=round(random.normalvariate(1500, 500), 2),
                unit="USD",
                timestamp=date,
                dimensions={"period": "daily", "currency": "USD"}
            ))
            
            # Content performance metrics
            self.metrics_store.append(AnalyticsMetric(
                metric_id=f"content_views_{i}",
                name="Daily Content Views",
                metric_type=MetricType.CONTENT,
                value=int(random.normalvariate(10000, 3000)),
                unit="views",
                timestamp=date,
                dimensions={"period": "daily", "content_type": "all"}
            ))
            
            # Audience growth metrics
            self.metrics_store.append(AnalyticsMetric(
                metric_id=f"audience_growth_{i}",
                name="Daily Audience Growth",
                metric_type=MetricType.AUDIENCE,
                value=int(random.normalvariate(50, 20)),
                unit="followers",
                timestamp=date,
                dimensions={"period": "daily", "platform": "all"}
            ))
    
    async def track_metric(self, metric: AnalyticsMetric) -> str:
        """Track a new analytics metric."""
        try:
            self.metrics_store.append(metric)
            self.logger.info(f"Tracked metric: {metric.name} = {metric.value}")
            return metric.metric_id
        except Exception as e:
            self.logger.error(f"Failed to track metric: {str(e)}")
            raise
    
    async def query_metrics(self, query: AnalyticsQuery) -> AnalyticsReport:
        """Query analytics metrics."""
        try:
            # Filter metrics based on query parameters
            filtered_metrics = []
            
            for metric in self.metrics_store:
                # Check metric type
                if metric.metric_type not in query.metric_types:
                    continue
                
                # Check date range
                if metric.timestamp < query.start_date or metric.timestamp > query.end_date:
                    continue
                
                # Check filters
                include_metric = True
                for filter_key, filter_value in query.filters.items():
                    if filter_key in metric.dimensions:
                        if metric.dimensions[filter_key] != filter_value:
                            include_metric = False
                            break
                    elif filter_key in metric.metadata:
                        if metric.metadata[filter_key] != filter_value:
                            include_metric = False
                            break
                
                if include_metric:
                    filtered_metrics.append(metric)
            
            # Apply aggregation
            aggregated_metrics = await self._aggregate_metrics(filtered_metrics, query.aggregation)
            
            # Apply limit
            if query.limit:
                aggregated_metrics = aggregated_metrics[:query.limit]
            
            # Generate summary
            summary = await self._generate_summary(aggregated_metrics, query)
            
            report = AnalyticsReport(
                report_id=str(uuid.uuid4()),
                query=query,
                metrics=aggregated_metrics,
                summary=summary
            )
            
            # Cache the report
            self.reports_cache[report.report_id] = report
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error querying metrics: {str(e)}")
            raise
    
    async def _aggregate_metrics(self, metrics: List[AnalyticsMetric], period: AggregationPeriod) -> List[AnalyticsMetric]:
        """Aggregate metrics by time period."""
        try:
            if not metrics:
                return []
            
            # Group metrics by type and time period
            grouped_metrics = defaultdict(lambda: defaultdict(list))
            
            for metric in metrics:
                # Determine the time bucket based on aggregation period
                time_bucket = self._get_time_bucket(metric.timestamp, period)
                grouped_metrics[metric.metric_type][time_bucket].append(metric)
            
            aggregated = []
            
            for metric_type, time_groups in grouped_metrics.items():
                for time_bucket, metric_list in time_groups.items():
                    # Aggregate values
                    if metric_list[0].name.endswith("Rate") or "percentage" in metric_list[0].unit.lower():
                        # For rates and percentages, use average
                        aggregated_value = statistics.mean([m.value for m in metric_list])
                    else:
                        # For counts and amounts, use sum
                        aggregated_value = sum([m.value for m in metric_list])
                    
                    # Create aggregated metric
                    aggregated_metric = AnalyticsMetric(
                        metric_id=f"agg_{metric_type.value}_{time_bucket}",
                        name=f"Aggregated {metric_list[0].name}",
                        metric_type=metric_type,
                        value=round(aggregated_value, 2),
                        unit=metric_list[0].unit,
                        timestamp=time_bucket,
                        dimensions={
                            "aggregation": period.value,
                            "count": len(metric_list)
                        }
                    )
                    
                    aggregated.append(aggregated_metric)
            
            # Sort by timestamp
            aggregated.sort(key=lambda m: m.timestamp)
            
            return aggregated
            
        except Exception as e:
            self.logger.error(f"Error aggregating metrics: {str(e)}")
            return metrics
    
    def _get_time_bucket(self, timestamp: datetime, period: AggregationPeriod) -> datetime:
        """Get time bucket for aggregation."""
        if period == AggregationPeriod.HOURLY:
            return timestamp.replace(minute=0, second=0, microsecond=0)
        elif period == AggregationPeriod.DAILY:
            return timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == AggregationPeriod.WEEKLY:
            days_since_monday = timestamp.weekday()
            start_of_week = timestamp - timedelta(days=days_since_monday)
            return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == AggregationPeriod.MONTHLY:
            return timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == AggregationPeriod.QUARTERLY:
            quarter_start_month = ((timestamp.month - 1) // 3) * 3 + 1
            return timestamp.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == AggregationPeriod.YEARLY:
            return timestamp.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return timestamp
    
    async def _generate_summary(self, metrics: List[AnalyticsMetric], query: AnalyticsQuery) -> Dict[str, Any]:
        """Generate summary statistics for metrics."""
        try:
            if not metrics:
                return {"total_metrics": 0, "message": "No metrics found"}
            
            summary = {
                "total_metrics": len(metrics),
                "date_range": {
                    "start": query.start_date.isoformat(),
                    "end": query.end_date.isoformat()
                },
                "aggregation": query.aggregation.value,
                "metric_types": [mt.value for mt in query.metric_types]
            }
            
            # Summary by metric type
            by_type = defaultdict(list)
            for metric in metrics:
                by_type[metric.metric_type].append(metric.value)
            
            for metric_type, values in by_type.items():
                if values:
                    summary[f"{metric_type.value}_summary"] = {
                        "count": len(values),
                        "total": sum(values),
                        "average": statistics.mean(values),
                        "min": min(values),
                        "max": max(values),
                        "median": statistics.median(values)
                    }
            
            # Trends analysis
            summary["trends"] = await self._analyze_trends(metrics)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            return {"error": str(e)}
    
    async def _analyze_trends(self, metrics: List[AnalyticsMetric]) -> Dict[str, Any]:
        """Analyze trends in metrics."""
        try:
            trends = {}
            
            # Group by metric type
            by_type = defaultdict(list)
            for metric in metrics:
                by_type[metric.metric_type].append((metric.timestamp, metric.value))
            
            for metric_type, time_values in by_type.items():
                if len(time_values) < 2:
                    continue
                
                # Sort by timestamp
                time_values.sort(key=lambda x: x[0])
                
                # Calculate trend
                values = [tv[1] for tv in time_values]
                if len(values) >= 2:
                    # Simple linear trend
                    x = list(range(len(values)))
                    y = values
                    
                    # Calculate correlation coefficient as trend indicator
                    if len(x) > 1:
                        if NUMPY_AVAILABLE:
                            correlation = np.corrcoef(x, y)[0, 1] if len(set(y)) > 1 else 0
                        else:
                            # Simple correlation calculation without numpy
                            mean_x = sum(x) / len(x)
                            mean_y = sum(y) / len(y)
                            numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
                            sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(len(x)))
                            sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(len(y)))
                            denominator = (sum_sq_x * sum_sq_y) ** 0.5
                            correlation = numerator / denominator if denominator != 0 else 0
                        
                        # Calculate percentage change
                        first_value = values[0]
                        last_value = values[-1]
                        pct_change = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
                        
                        trends[metric_type.value] = {
                            "direction": "increasing" if correlation > 0.1 else "decreasing" if correlation < -0.1 else "stable",
                            "correlation": round(correlation, 3),
                            "percentage_change": round(pct_change, 2),
                            "first_value": first_value,
                            "last_value": last_value
                        }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {str(e)}")
            return {}
    
    async def get_engagement_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get engagement analytics."""
        try:
            query = AnalyticsQuery(
                query_id=str(uuid.uuid4()),
                metric_types=[MetricType.ENGAGEMENT],
                start_date=start_date,
                end_date=end_date,
                aggregation=AggregationPeriod.DAILY
            )
            
            report = await self.query_metrics(query)
            
            return {
                "engagement_summary": report.summary.get("engagement_summary", {}),
                "trends": report.summary.get("trends", {}),
                "daily_metrics": [
                    {
                        "date": m.timestamp.date().isoformat(),
                        "engagement_rate": m.value,
                        "unit": m.unit
                    } for m in report.metrics
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting engagement analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_revenue_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get revenue analytics."""
        try:
            query = AnalyticsQuery(
                query_id=str(uuid.uuid4()),
                metric_types=[MetricType.REVENUE],
                start_date=start_date,
                end_date=end_date,
                aggregation=AggregationPeriod.DAILY
            )
            
            report = await self.query_metrics(query)
            
            return {
                "revenue_summary": report.summary.get("revenue_summary", {}),
                "trends": report.summary.get("trends", {}),
                "daily_revenue": [
                    {
                        "date": m.timestamp.date().isoformat(),
                        "revenue": m.value,
                        "currency": m.unit
                    } for m in report.metrics
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting revenue analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_content_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get content performance analytics."""
        try:
            query = AnalyticsQuery(
                query_id=str(uuid.uuid4()),
                metric_types=[MetricType.CONTENT],
                start_date=start_date,
                end_date=end_date,
                aggregation=AggregationPeriod.DAILY
            )
            
            report = await self.query_metrics(query)
            
            return {
                "content_summary": report.summary.get("content_summary", {}),
                "trends": report.summary.get("trends", {}),
                "daily_views": [
                    {
                        "date": m.timestamp.date().isoformat(),
                        "views": m.value,
                        "unit": m.unit
                    } for m in report.metrics
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting content analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_audience_analytics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get audience growth analytics."""
        try:
            query = AnalyticsQuery(
                query_id=str(uuid.uuid4()),
                metric_types=[MetricType.AUDIENCE],
                start_date=start_date,
                end_date=end_date,
                aggregation=AggregationPeriod.DAILY
            )
            
            report = await self.query_metrics(query)
            
            return {
                "audience_summary": report.summary.get("audience_summary", {}),
                "trends": report.summary.get("trends", {}),
                "daily_growth": [
                    {
                        "date": m.timestamp.date().isoformat(),
                        "growth": m.value,
                        "unit": m.unit
                    } for m in report.metrics
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting audience analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_comprehensive_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Query all metric types
            query = AnalyticsQuery(
                query_id=str(uuid.uuid4()),
                metric_types=list(MetricType),
                start_date=start_date,
                end_date=end_date,
                aggregation=AggregationPeriod.DAILY
            )
            
            report = await self.query_metrics(query)
            
            # Get individual analytics
            engagement_data = await self.get_engagement_analytics(start_date, end_date)
            revenue_data = await self.get_revenue_analytics(start_date, end_date)
            content_data = await self.get_content_analytics(start_date, end_date)
            audience_data = await self.get_audience_analytics(start_date, end_date)
            
            return {
                "period": {
                    "start_date": start_date.date().isoformat(),
                    "end_date": end_date.date().isoformat(),
                    "days": days
                },
                "overall_summary": report.summary,
                "engagement": engagement_data,
                "revenue": revenue_data,
                "content": content_data,
                "audience": audience_data,
                "key_metrics": {
                    "total_revenue": report.summary.get("revenue_summary", {}).get("total", 0),
                    "avg_engagement": report.summary.get("engagement_summary", {}).get("average", 0),
                    "total_views": report.summary.get("content_summary", {}).get("total", 0),
                    "total_audience_growth": report.summary.get("audience_summary", {}).get("total", 0)
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting comprehensive dashboard: {str(e)}")
            return {"error": str(e)}
    
    async def generate_insights(self, metric_types: List[MetricType], days: int = 30) -> Dict[str, Any]:
        """Generate AI-powered insights from analytics data."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = AnalyticsQuery(
                query_id=str(uuid.uuid4()),
                metric_types=metric_types,
                start_date=start_date,
                end_date=end_date,
                aggregation=AggregationPeriod.DAILY
            )
            
            report = await self.query_metrics(query)
            
            insights = {
                "period": f"Last {days} days",
                "insights": [],
                "recommendations": [],
                "alerts": []
            }
            
            # Analyze trends and generate insights
            trends = report.summary.get("trends", {})
            
            for metric_type, trend_data in trends.items():
                direction = trend_data.get("direction", "stable")
                pct_change = trend_data.get("percentage_change", 0)
                
                if direction == "increasing" and pct_change > 10:
                    insights["insights"].append({
                        "type": "positive_trend",
                        "metric": metric_type,
                        "message": f"{metric_type.title()} is showing strong growth ({pct_change:.1f}% increase)",
                        "impact": "positive"
                    })
                    insights["recommendations"].append({
                        "metric": metric_type,
                        "action": f"Continue current strategies for {metric_type} as they're showing positive results"
                    })
                
                elif direction == "decreasing" and pct_change < -10:
                    insights["insights"].append({
                        "type": "negative_trend",
                        "metric": metric_type,
                        "message": f"{metric_type.title()} is declining ({pct_change:.1f}% decrease)",
                        "impact": "negative"
                    })
                    insights["alerts"].append({
                        "severity": "medium",
                        "metric": metric_type,
                        "message": f"Declining {metric_type} requires attention"
                    })
                    insights["recommendations"].append({
                        "metric": metric_type,
                        "action": f"Review and optimize strategies for {metric_type} improvement"
                    })
                
                elif direction == "stable":
                    insights["insights"].append({
                        "type": "stable_trend",
                        "metric": metric_type,
                        "message": f"{metric_type.title()} remains stable",
                        "impact": "neutral"
                    })
            
            # Performance benchmarks
            for metric_type in metric_types:
                summary = report.summary.get(f"{metric_type.value}_summary", {})
                avg_value = summary.get("average", 0)
                
                # Simple benchmarking logic
                if metric_type == MetricType.ENGAGEMENT and avg_value > 0.20:
                    insights["insights"].append({
                        "type": "benchmark",
                        "metric": metric_type.value,
                        "message": f"Engagement rate of {avg_value:.1%} is above industry average",
                        "impact": "positive"
                    })
                elif metric_type == MetricType.ENGAGEMENT and avg_value < 0.05:
                    insights["alerts"].append({
                        "severity": "high",
                        "metric": metric_type.value,
                        "message": f"Engagement rate of {avg_value:.1%} is below recommended threshold"
                    })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {str(e)}")
            return {"error": str(e)}
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary of analytics system."""
        try:
            current_time = datetime.utcnow()
            last_24h = current_time - timedelta(hours=24)
            
            recent_metrics = [m for m in self.metrics_store if m.timestamp >= last_24h]
            
            return {
                "total_metrics": len(self.metrics_store),
                "recent_metrics_24h": len(recent_metrics),
                "cached_reports": len(self.reports_cache),
                "metric_types_available": [mt.value for mt in MetricType],
                "aggregation_periods": [ap.value for ap in AggregationPeriod],
                "metrics_by_type": {
                    mt.value: len([m for m in self.metrics_store if m.metric_type == mt])
                    for mt in MetricType
                },
                "oldest_metric": min(self.metrics_store, key=lambda m: m.timestamp).timestamp.isoformat() if self.metrics_store else None,
                "newest_metric": max(self.metrics_store, key=lambda m: m.timestamp).timestamp.isoformat() if self.metrics_store else None
            }
        except Exception as e:
            self.logger.error(f"Error getting analytics summary: {str(e)}")
            return {}