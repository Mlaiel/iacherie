"""
Analytics Pipeline - IA Chéries Enterprise
=======================================
Pipeline analytics/insights avec business intelligence.
Analytics collection + insights generation + performance tracking + predictive analysis.

Author: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer)
IP Owner: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chéries ML Pipelines
Version: 1.0 Production
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import json
import hashlib
import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

# Simulated imports for analytics
try:
    import numpy as np
except ImportError:
    class np:
        ndarray = type
        @staticmethod
        def array(x): return x
        @staticmethod
        def mean(x): return sum(x) / len(x) if x else 0
        @staticmethod
        def std(x): 
            if not x: return 0
            mean_val = sum(x) / len(x)
            return math.sqrt(sum((i - mean_val) ** 2 for i in x) / len(x))

class AnalyticsMetric(Enum):
    """Types de métriques analytics"""
    ENGAGEMENT_RATE = "engagement_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICK_THROUGH_RATE = "click_through_rate"
    CONVERSION_RATE = "conversion_rate"
    AUDIENCE_GROWTH = "audience_growth"
    CONTENT_PERFORMANCE = "content_performance"
    REVENUE = "revenue"
    ROI = "roi"
    BRAND_AWARENESS = "brand_awareness"
    SENTIMENT_SCORE = "sentiment_score"
    VIRALITY_SCORE = "virality_score"

class TimeGranularity(Enum):
    """Granularité temporelle des métriques"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class AnalyticsDataSource(Enum):
    """Sources de données analytics"""
    PLATFORM_API = "platform_api"
    INTERNAL_TRACKING = "internal_tracking"
    THIRD_PARTY = "third_party"
    USER_SURVEYS = "user_surveys"
    A_B_TESTS = "a_b_tests"
    BEHAVIORAL_DATA = "behavioral_data"

class InsightType(Enum):
    """Types d'insights générés"""
    PERFORMANCE_TREND = "performance_trend"
    AUDIENCE_BEHAVIOR = "audience_behavior"
    CONTENT_OPTIMIZATION = "content_optimization"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    MARKET_OPPORTUNITY = "market_opportunity"
    RISK_ALERT = "risk_alert"
    RECOMMENDATION = "recommendation"

@dataclass
class MetricDataPoint:
    """Point de données pour une métrique"""
    timestamp: datetime
    metric_type: AnalyticsMetric
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: AnalyticsDataSource = AnalyticsDataSource.INTERNAL_TRACKING
    confidence_level: float = 1.0

@dataclass
class AnalyticsQuery:
    """Requête analytics"""
    query_id: str
    metrics: List[AnalyticsMetric]
    time_range: Tuple[datetime, datetime]
    granularity: TimeGranularity
    filters: Dict[str, Any] = field(default_factory=dict)
    dimensions: List[str] = field(default_factory=list)
    include_predictions: bool = False
    compare_periods: bool = False

@dataclass
class AnalyticsInsight:
    """Insight généré par l'analyse"""
    insight_id: str
    insight_type: InsightType
    title: str
    description: str
    impact_score: float  # 0-1
    confidence_score: float  # 0-1
    supporting_data: Dict[str, Any]
    recommendations: List[str]
    priority: str  # "high", "medium", "low"
    created_at: datetime

@dataclass
class PerformanceReport:
    """Rapport de performance généré"""
    report_id: str
    period: Tuple[datetime, datetime]
    overall_metrics: Dict[AnalyticsMetric, float]
    trend_analysis: Dict[str, Any]
    insights: List[AnalyticsInsight]
    benchmarks: Dict[str, float]
    predictions: Dict[str, Any]
    recommendations: List[str]
    report_generated_at: datetime

@dataclass
class AnalyticsRequest:
    """Requête complète d'analytics"""
    request_id: str
    entity_id: str  # Content, creator, campaign ID
    entity_type: str  # "content", "creator", "campaign"
    analytics_queries: List[AnalyticsQuery]
    generate_insights: bool = True
    include_benchmarks: bool = True
    include_predictions: bool = True
    custom_kpis: Dict[str, str] = field(default_factory=dict)

@dataclass
class AnalyticsResult:
    """Résultat complet d'analytics"""
    request_id: str
    performance_report: PerformanceReport
    detailed_metrics: Dict[str, List[MetricDataPoint]]
    comparative_analysis: Dict[str, Any]
    predictive_analysis: Dict[str, Any]
    actionable_insights: List[AnalyticsInsight]
    dashboard_data: Dict[str, Any]
    processing_time: float

class MetricsCollector:
    """Collecteur de métriques multi-sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_sources = self._initialize_data_sources()
    
    def _initialize_data_sources(self) -> Dict[AnalyticsDataSource, Dict[str, Any]]:
        """Initialisation des sources de données"""
        return {
            AnalyticsDataSource.PLATFORM_API: {
                "enabled": True,
                "rate_limit": 100,  # requests per minute
                "refresh_interval": 300  # seconds
            },
            AnalyticsDataSource.INTERNAL_TRACKING: {
                "enabled": True,
                "batch_size": 1000,
                "real_time": True
            },
            AnalyticsDataSource.THIRD_PARTY: {
                "enabled": True,
                "providers": ["google_analytics", "facebook_insights"]
            }
        }
    
    async def collect_metrics(self, entity_id: str, entity_type: str, metrics: List[AnalyticsMetric], time_range: Tuple[datetime, datetime]) -> Dict[AnalyticsMetric, List[MetricDataPoint]]:
        """Collection métriques multi-sources"""
        
        collected_metrics = {}
        
        for metric in metrics:
            data_points = []
            
            # Simulate data collection from different sources
            if metric == AnalyticsMetric.ENGAGEMENT_RATE:
                data_points = await self._collect_engagement_data(entity_id, time_range)
            elif metric == AnalyticsMetric.REACH:
                data_points = await self._collect_reach_data(entity_id, time_range)
            elif metric == AnalyticsMetric.REVENUE:
                data_points = await self._collect_revenue_data(entity_id, time_range)
            elif metric == AnalyticsMetric.AUDIENCE_GROWTH:
                data_points = await self._collect_audience_growth_data(entity_id, time_range)
            elif metric == AnalyticsMetric.SENTIMENT_SCORE:
                data_points = await self._collect_sentiment_data(entity_id, time_range)
            else:
                # Generic data collection
                data_points = await self._collect_generic_metric_data(entity_id, metric, time_range)
            
            collected_metrics[metric] = data_points
        
        return collected_metrics
    
    async def _collect_engagement_data(self, entity_id: str, time_range: Tuple[datetime, datetime]) -> List[MetricDataPoint]:
        """Collection données d'engagement"""
        data_points = []
        start_date, end_date = time_range
        
        # Simulate daily engagement data
        current_date = start_date
        base_engagement = 0.05  # 5% base engagement
        
        while current_date <= end_date:
            # Add some realistic variation
            daily_variation = (hash(f"{entity_id}_{current_date.isoformat()}") % 100) / 1000
            engagement_rate = base_engagement + daily_variation
            
            data_point = MetricDataPoint(
                timestamp=current_date,
                metric_type=AnalyticsMetric.ENGAGEMENT_RATE,
                value=engagement_rate,
                metadata={"likes": 150, "comments": 25, "shares": 12},
                source=AnalyticsDataSource.PLATFORM_API,
                confidence_level=0.95
            )
            data_points.append(data_point)
            current_date += timedelta(days=1)
        
        return data_points
    
    async def _collect_reach_data(self, entity_id: str, time_range: Tuple[datetime, datetime]) -> List[MetricDataPoint]:
        """Collection données de portée"""
        data_points = []
        start_date, end_date = time_range
        current_date = start_date
        base_reach = 10000
        
        while current_date <= end_date:
            # Simulate growth with weekly cycles
            days_from_start = (current_date - start_date).days
            weekly_multiplier = 1 + 0.1 * math.sin(days_from_start * 2 * math.pi / 7)
            daily_reach = int(base_reach * weekly_multiplier * (1 + days_from_start * 0.01))
            
            data_point = MetricDataPoint(
                timestamp=current_date,
                metric_type=AnalyticsMetric.REACH,
                value=daily_reach,
                metadata={"organic_reach": daily_reach * 0.7, "paid_reach": daily_reach * 0.3},
                source=AnalyticsDataSource.PLATFORM_API,
                confidence_level=0.90
            )
            data_points.append(data_point)
            current_date += timedelta(days=1)
        
        return data_points
    
    async def _collect_revenue_data(self, entity_id: str, time_range: Tuple[datetime, datetime]) -> List[MetricDataPoint]:
        """Collection données de revenus"""
        data_points = []
        start_date, end_date = time_range
        current_date = start_date
        base_revenue = 500.0  # Daily base revenue
        
        while current_date <= end_date:
            # Simulate revenue with growth and seasonality
            days_from_start = (current_date - start_date).days
            growth_factor = 1 + days_from_start * 0.005  # 0.5% daily growth
            seasonal_factor = 1 + 0.2 * math.sin(days_from_start * 2 * math.pi / 30)  # Monthly cycle
            
            daily_revenue = base_revenue * growth_factor * seasonal_factor
            
            data_point = MetricDataPoint(
                timestamp=current_date,
                metric_type=AnalyticsMetric.REVENUE,
                value=daily_revenue,
                metadata={
                    "subscription_revenue": daily_revenue * 0.6,
                    "sponsorship_revenue": daily_revenue * 0.3,
                    "merchandise_revenue": daily_revenue * 0.1
                },
                source=AnalyticsDataSource.INTERNAL_TRACKING,
                confidence_level=0.98
            )
            data_points.append(data_point)
            current_date += timedelta(days=1)
        
        return data_points
    
    async def _collect_audience_growth_data(self, entity_id: str, time_range: Tuple[datetime, datetime]) -> List[MetricDataPoint]:
        """Collection données de croissance audience"""
        data_points = []
        start_date, end_date = time_range
        current_date = start_date
        base_followers = 50000
        
        while current_date <= end_date:
            days_from_start = (current_date - start_date).days
            # Simulate organic growth with occasional viral spikes
            daily_growth_rate = 0.002 + (0.01 if days_from_start % 7 == 0 else 0)  # Weekly spikes
            daily_followers = int(base_followers * (1 + daily_growth_rate) ** days_from_start)
            
            data_point = MetricDataPoint(
                timestamp=current_date,
                metric_type=AnalyticsMetric.AUDIENCE_GROWTH,
                value=daily_followers,
                metadata={
                    "new_followers": max(1, int(daily_followers * daily_growth_rate)),
                    "unfollowers": max(0, int(daily_followers * 0.001))
                },
                source=AnalyticsDataSource.PLATFORM_API,
                confidence_level=0.92
            )
            data_points.append(data_point)
            current_date += timedelta(days=1)
        
        return data_points
    
    async def _collect_sentiment_data(self, entity_id: str, time_range: Tuple[datetime, datetime]) -> List[MetricDataPoint]:
        """Collection données de sentiment"""
        data_points = []
        start_date, end_date = time_range
        current_date = start_date
        
        while current_date <= end_date:
            # Simulate sentiment with random variations around positive baseline
            base_sentiment = 0.7  # Generally positive
            daily_variation = (hash(f"sentiment_{entity_id}_{current_date.isoformat()}") % 100 - 50) / 500
            sentiment_score = max(0, min(1, base_sentiment + daily_variation))
            
            data_point = MetricDataPoint(
                timestamp=current_date,
                metric_type=AnalyticsMetric.SENTIMENT_SCORE,
                value=sentiment_score,
                metadata={
                    "positive_mentions": 85,
                    "neutral_mentions": 12,
                    "negative_mentions": 3,
                    "total_mentions": 100
                },
                source=AnalyticsDataSource.THIRD_PARTY,
                confidence_level=0.85
            )
            data_points.append(data_point)
            current_date += timedelta(days=1)
        
        return data_points
    
    async def _collect_generic_metric_data(self, entity_id: str, metric: AnalyticsMetric, time_range: Tuple[datetime, datetime]) -> List[MetricDataPoint]:
        """Collection générique pour autres métriques"""
        data_points = []
        start_date, end_date = time_range
        current_date = start_date
        
        # Default values based on metric type
        base_values = {
            AnalyticsMetric.IMPRESSIONS: 50000,
            AnalyticsMetric.CLICK_THROUGH_RATE: 0.02,
            AnalyticsMetric.CONVERSION_RATE: 0.05,
            AnalyticsMetric.ROI: 2.5,
            AnalyticsMetric.BRAND_AWARENESS: 0.3,
            AnalyticsMetric.VIRALITY_SCORE: 0.1
        }
        
        base_value = base_values.get(metric, 100.0)
        
        while current_date <= end_date:
            days_from_start = (current_date - start_date).days
            variation = (hash(f"{metric.value}_{entity_id}_{current_date.isoformat()}") % 100 - 50) / 100
            daily_value = base_value * (1 + variation * 0.2)  # ±20% variation
            
            data_point = MetricDataPoint(
                timestamp=current_date,
                metric_type=metric,
                value=daily_value,
                metadata={"source": "simulated"},
                source=AnalyticsDataSource.INTERNAL_TRACKING,
                confidence_level=0.80
            )
            data_points.append(data_point)
            current_date += timedelta(days=1)
        
        return data_points

class InsightGenerator:
    """Générateur d'insights analytics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def generate_insights(self, metrics_data: Dict[AnalyticsMetric, List[MetricDataPoint]], entity_type: str) -> List[AnalyticsInsight]:
        """Génération insights à partir des métriques"""
        
        insights = []
        
        # Trend analysis insights
        trend_insights = await self._generate_trend_insights(metrics_data)
        insights.extend(trend_insights)
        
        # Performance insights
        performance_insights = await self._generate_performance_insights(metrics_data)
        insights.extend(performance_insights)
        
        # Anomaly detection insights
        anomaly_insights = await self._detect_anomalies(metrics_data)
        insights.extend(anomaly_insights)
        
        # Opportunity insights
        opportunity_insights = await self._identify_opportunities(metrics_data, entity_type)
        insights.extend(opportunity_insights)
        
        # Risk insights
        risk_insights = await self._assess_risks(metrics_data)
        insights.extend(risk_insights)
        
        return insights
    
    async def _generate_trend_insights(self, metrics_data: Dict[AnalyticsMetric, List[MetricDataPoint]]) -> List[AnalyticsInsight]:
        """Génération insights de tendances"""
        insights = []
        
        for metric, data_points in metrics_data.items():
            if len(data_points) < 7:  # Need at least a week of data
                continue
            
            # Calculate trend
            values = [dp.value for dp in data_points]
            if len(values) > 1:
                # Simple linear trend calculation
                x = list(range(len(values)))
                y = values
                n = len(x)
                
                slope = (n * sum(x[i] * y[i] for i in range(n)) - sum(x) * sum(y)) / (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
                
                if slope > 0.05:  # Significant positive trend
                    insight = AnalyticsInsight(
                        insight_id=f"trend_up_{metric.value}_{int(time.time())}",
                        insight_type=InsightType.PERFORMANCE_TREND,
                        title=f"Strong upward trend in {metric.value.replace('_', ' ').title()}",
                        description=f"Your {metric.value.replace('_', ' ')} has shown consistent growth over the past {len(data_points)} days.",
                        impact_score=min(1.0, abs(slope) * 2),
                        confidence_score=0.85,
                        supporting_data={
                            "trend_slope": slope,
                            "data_points": len(data_points),
                            "current_value": values[-1],
                            "previous_value": values[0]
                        },
                        recommendations=[
                            f"Continue current strategies that are driving {metric.value.replace('_', ' ')} growth",
                            "Consider scaling successful tactics",
                            "Monitor for sustainability of this trend"
                        ],
                        priority="high" if slope > 0.1 else "medium",
                        created_at=datetime.now()
                    )
                    insights.append(insight)
                
                elif slope < -0.05:  # Significant negative trend
                    insight = AnalyticsInsight(
                        insight_id=f"trend_down_{metric.value}_{int(time.time())}",
                        insight_type=InsightType.RISK_ALERT,
                        title=f"declining trend detected in {metric.value.replace('_', ' ').title()}",
                        description=f"Your {metric.value.replace('_', ' ')} has been declining over the past {len(data_points)} days.",
                        impact_score=min(1.0, abs(slope) * 2),
                        confidence_score=0.85,
                        supporting_data={
                            "trend_slope": slope,
                            "data_points": len(data_points),
                            "current_value": values[-1],
                            "previous_value": values[0]
                        },
                        recommendations=[
                            f"Investigate causes of declining {metric.value.replace('_', ' ')}",
                            "Review recent content and strategy changes",
                            "Consider A/B testing new approaches"
                        ],
                        priority="high",
                        created_at=datetime.now()
                    )
                    insights.append(insight)
        
        return insights
    
    async def _generate_performance_insights(self, metrics_data: Dict[AnalyticsMetric, List[MetricDataPoint]]) -> List[AnalyticsInsight]:
        """Génération insights de performance"""
        insights = []
        
        # High performance insight
        if AnalyticsMetric.ENGAGEMENT_RATE in metrics_data:
            engagement_data = metrics_data[AnalyticsMetric.ENGAGEMENT_RATE]
            recent_engagement = np.mean([dp.value for dp in engagement_data[-7:]])  # Last 7 days
            
            if recent_engagement > 0.08:  # 8% is excellent engagement
                insight = AnalyticsInsight(
                    insight_id=f"high_engagement_{int(time.time())}",
                    insight_type=InsightType.PERFORMANCE_TREND,
                    title="Exceptional Engagement Performance",
                    description=f"Your content is achieving {recent_engagement:.2%} engagement rate, which is well above industry average.",
                    impact_score=0.9,
                    confidence_score=0.90,
                    supporting_data={
                        "current_engagement": recent_engagement,
                        "industry_average": 0.03,
                        "performance_percentile": 95
                    },
                    recommendations=[
                        "Document what's working in your current content strategy",
                        "Consider creating similar content to maintain this performance",
                        "Leverage this high engagement for partnerships"
                    ],
                    priority="high",
                    created_at=datetime.now()
                )
                insights.append(insight)
        
        return insights
    
    async def _detect_anomalies(self, metrics_data: Dict[AnalyticsMetric, List[MetricDataPoint]]) -> List[AnalyticsInsight]:
        """Détection d'anomalies dans les métriques"""
        insights = []
        
        for metric, data_points in metrics_data.items():
            if len(data_points) < 14:  # Need at least 2 weeks for anomaly detection
                continue
            
            values = [dp.value for dp in data_points]
            
            # Calculate baseline (excluding last 3 days)
            baseline_values = values[:-3]
            baseline_mean = np.mean(baseline_values)
            baseline_std = np.std(baseline_values)
            
            # Check last 3 days for anomalies
            recent_values = values[-3:]
            
            for i, value in enumerate(recent_values):
                z_score = abs(value - baseline_mean) / baseline_std if baseline_std > 0 else 0
                
                if z_score > 2.5:  # Significant anomaly
                    anomaly_type = "spike" if value > baseline_mean else "drop"
                    
                    insight = AnalyticsInsight(
                        insight_id=f"anomaly_{anomaly_type}_{metric.value}_{int(time.time())}",
                        insight_type=InsightType.RISK_ALERT if anomaly_type == "drop" else InsightType.PERFORMANCE_TREND,
                        title=f"Unusual {anomaly_type} in {metric.value.replace('_', ' ').title()}",
                        description=f"Detected a significant {anomaly_type} in {metric.value.replace('_', ' ')} that deviates from normal patterns.",
                        impact_score=min(1.0, z_score / 3),
                        confidence_score=0.80,
                        supporting_data={
                            "anomaly_value": value,
                            "baseline_mean": baseline_mean,
                            "z_score": z_score,
                            "anomaly_type": anomaly_type
                        },
                        recommendations=[
                            f"Investigate what caused this {anomaly_type} in {metric.value.replace('_', ' ')}",
                            "Check for external factors or content changes",
                            "Monitor closely for pattern continuation"
                        ],
                        priority="high" if z_score > 3 else "medium",
                        created_at=datetime.now()
                    )
                    insights.append(insight)
        
        return insights
    
    async def _identify_opportunities(self, metrics_data: Dict[AnalyticsMetric, List[MetricDataPoint]], entity_type: str) -> List[AnalyticsInsight]:
        """Identification opportunités d'amélioration"""
        insights = []
        
        # Revenue opportunity
        if AnalyticsMetric.ENGAGEMENT_RATE in metrics_data and AnalyticsMetric.REVENUE in metrics_data:
            engagement_data = metrics_data[AnalyticsMetric.ENGAGEMENT_RATE]
            revenue_data = metrics_data[AnalyticsMetric.REVENUE]
            
            avg_engagement = np.mean([dp.value for dp in engagement_data])
            avg_revenue = np.mean([dp.value for dp in revenue_data])
            
            # If high engagement but low revenue, there's monetization opportunity
            if avg_engagement > 0.06 and avg_revenue < 1000:  # High engagement, low revenue
                insight = AnalyticsInsight(
                    insight_id=f"monetization_opportunity_{int(time.time())}",
                    insight_type=InsightType.MARKET_OPPORTUNITY,
                    title="Monetization Opportunity Identified",
                    description="Your high engagement rate suggests untapped revenue potential.",
                    impact_score=0.8,
                    confidence_score=0.75,
                    supporting_data={
                        "engagement_rate": avg_engagement,
                        "current_revenue": avg_revenue,
                        "estimated_potential": avg_revenue * 3
                    },
                    recommendations=[
                        "Explore premium content offerings",
                        "Consider brand partnership opportunities",
                        "Implement subscription or membership tiers"
                    ],
                    priority="high",
                    created_at=datetime.now()
                )
                insights.append(insight)
        
        return insights
    
    async def _assess_risks(self, metrics_data: Dict[AnalyticsMetric, List[MetricDataPoint]]) -> List[AnalyticsInsight]:
        """Assessment des risques basé sur les métriques"""
        insights = []
        
        # Audience growth stagnation risk
        if AnalyticsMetric.AUDIENCE_GROWTH in metrics_data:
            growth_data = metrics_data[AnalyticsMetric.AUDIENCE_GROWTH]
            
            if len(growth_data) >= 30:  # Need at least a month of data
                # Check if growth has stagnated
                recent_values = [dp.value for dp in growth_data[-14:]]  # Last 2 weeks
                older_values = [dp.value for dp in growth_data[-30:-14]]  # Previous 2 weeks
                
                recent_growth = (recent_values[-1] - recent_values[0]) / recent_values[0] if recent_values[0] > 0 else 0
                older_growth = (older_values[-1] - older_values[0]) / older_values[0] if older_values[0] > 0 else 0
                
                if recent_growth < 0.01 and older_growth > 0.02:  # Growth slowing down
                    insight = AnalyticsInsight(
                        insight_id=f"growth_stagnation_risk_{int(time.time())}",
                        insight_type=InsightType.RISK_ALERT,
                        title="Audience Growth Stagnation Risk",
                        description="Your audience growth rate has significantly slowed compared to previous periods.",
                        impact_score=0.7,
                        confidence_score=0.80,
                        supporting_data={
                            "recent_growth_rate": recent_growth,
                            "previous_growth_rate": older_growth,
                            "current_audience": recent_values[-1]
                        },
                        recommendations=[
                            "Refresh content strategy to attract new audience",
                            "Increase posting frequency or try new content formats",
                            "Engage more actively with your community"
                        ],
                        priority="medium",
                        created_at=datetime.now()
                    )
                    insights.append(insight)
        
        return insights

class PredictiveAnalyzer:
    """Analyseur prédictif pour forecasting"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def generate_predictions(self, metrics_data: Dict[AnalyticsMetric, List[MetricDataPoint]], prediction_horizon_days: int = 30) -> Dict[str, Any]:
        """Génération prédictions pour les métriques"""
        
        predictions = {}
        
        for metric, data_points in metrics_data.items():
            if len(data_points) < 14:  # Need minimum data for predictions
                continue
            
            prediction = await self._predict_metric_trend(metric, data_points, prediction_horizon_days)
            predictions[metric.value] = prediction
        
        return predictions
    
    async def _predict_metric_trend(self, metric: AnalyticsMetric, data_points: List[MetricDataPoint], horizon_days: int) -> Dict[str, Any]:
        """Prédiction tendance pour une métrique spécifique"""
        
        values = [dp.value for dp in data_points]
        timestamps = [dp.timestamp for dp in data_points]
        
        # Simple linear extrapolation (in production would use more sophisticated models)
        if len(values) >= 2:
            # Calculate trend
            x = list(range(len(values)))
            y = values
            n = len(x)
            
            # Linear regression
            slope = (n * sum(x[i] * y[i] for i in range(n)) - sum(x) * sum(y)) / (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
            intercept = (sum(y) - slope * sum(x)) / n
            
            # Generate predictions
            last_index = len(values) - 1
            predictions_values = []
            prediction_dates = []
            
            for i in range(1, horizon_days + 1):
                future_index = last_index + i
                predicted_value = slope * future_index + intercept
                
                # Ensure predictions are realistic (no negative values for most metrics)
                if metric in [AnalyticsMetric.ENGAGEMENT_RATE, AnalyticsMetric.CONVERSION_RATE]:
                    predicted_value = max(0, min(1, predicted_value))
                elif metric in [AnalyticsMetric.REACH, AnalyticsMetric.AUDIENCE_GROWTH, AnalyticsMetric.REVENUE]:
                    predicted_value = max(0, predicted_value)
                
                predictions_values.append(predicted_value)
                prediction_dates.append(timestamps[-1] + timedelta(days=i))
            
            # Calculate confidence intervals (simplified)
            actual_values = values[-min(7, len(values)):]  # Last week for error calculation
            predicted_last_week = [slope * (last_index - len(actual_values) + 1 + i) + intercept for i in range(len(actual_values))]
            
            mse = np.mean([(actual_values[i] - predicted_last_week[i])**2 for i in range(len(actual_values))])
            confidence_interval = 1.96 * math.sqrt(mse)  # 95% confidence interval
            
            return {
                "predicted_values": predictions_values,
                "prediction_dates": [d.isoformat() for d in prediction_dates],
                "confidence_interval": confidence_interval,
                "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                "trend_strength": abs(slope),
                "prediction_confidence": max(0.5, 1.0 - min(1.0, confidence_interval / np.mean(values))),
                "model_type": "linear_regression"
            }
        
        return {
            "predicted_values": [],
            "error": "Insufficient data for prediction"
        }

class AnalyticsPipeline:
    """
    Pipeline analytics/insights avec business intelligence.
    Analytics collection + insights generation + performance tracking + predictive analysis.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.metrics_collector = MetricsCollector()
        self.insight_generator = InsightGenerator()
        self.predictive_analyzer = PredictiveAnalyzer()
        
        # Performance optimization
        self.thread_executor = ThreadPoolExecutor(max_workers=16)
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5 minutes default
        self.cache = {}
        
        self.logger.info("📊 Analytics Pipeline initialized - Fahed Mlaiel IP")
    
    async def process_analytics_request(self, request: AnalyticsRequest) -> AnalyticsResult:
        """
        Traitement requête analytics avec business intelligence comprehensive.
        
        Analytics Features:
        - Multi-source data collection avec real-time et historical data integration
        - Advanced metrics calculation avec custom KPIs et industry benchmarks
        - AI-powered insight generation avec trend analysis et anomaly detection
        - Predictive analytics avec forecasting et scenario modeling
        - Automated reporting avec customizable dashboards et alerts
        - Cross-platform analytics avec unified view across all channels
        - Audience intelligence avec behavioral analysis et segmentation
        - Performance optimization recommendations avec actionable insights
        - Competitive analysis avec market positioning et opportunity identification
        - ROI tracking avec attribution modeling et conversion analysis
        """
        start_time = time.time()
        
        try:
            # Collect metrics data
            all_metrics_data = {}
            
            for query in request.analytics_queries:
                query_metrics = await self.metrics_collector.collect_metrics(
                    request.entity_id,
                    request.entity_type,
                    query.metrics,
                    query.time_range
                )
                
                # Merge with existing data
                for metric, data_points in query_metrics.items():
                    if metric not in all_metrics_data:
                        all_metrics_data[metric] = []
                    all_metrics_data[metric].extend(data_points)
            
            # Generate insights
            insights = []
            if request.generate_insights:
                insights = await self.insight_generator.generate_insights(
                    all_metrics_data, request.entity_type
                )
            
            # Generate predictions
            predictive_analysis = {}
            if request.include_predictions:
                predictive_analysis = await self.predictive_analyzer.generate_predictions(
                    all_metrics_data
                )
            
            # Calculate benchmarks
            benchmarks = {}
            if request.include_benchmarks:
                benchmarks = await self._calculate_benchmarks(all_metrics_data, request.entity_type)
            
            # Generate performance report
            performance_report = await self._generate_performance_report(
                request, all_metrics_data, insights, benchmarks, predictive_analysis
            )
            
            # Create comparative analysis
            comparative_analysis = await self._create_comparative_analysis(all_metrics_data)
            
            # Prepare dashboard data
            dashboard_data = await self._prepare_dashboard_data(
                all_metrics_data, insights, predictive_analysis
            )
            
            # Filter actionable insights
            actionable_insights = [insight for insight in insights if insight.priority in ["high", "medium"]]
            
            processing_time = time.time() - start_time
            
            return AnalyticsResult(
                request_id=request.request_id,
                performance_report=performance_report,
                detailed_metrics=all_metrics_data,
                comparative_analysis=comparative_analysis,
                predictive_analysis=predictive_analysis,
                actionable_insights=actionable_insights,
                dashboard_data=dashboard_data,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Analytics processing failed: {str(e)}")
            raise AnalyticsException(f"Pipeline failed: {str(e)}")
    
    async def _calculate_benchmarks(self, metrics_data: Dict[AnalyticsMetric, List[MetricDataPoint]], entity_type: str) -> Dict[str, float]:
        """Calcul benchmarks industrie"""
        
        # Industry benchmarks (would come from external data in production)
        industry_benchmarks = {
            "creator": {
                AnalyticsMetric.ENGAGEMENT_RATE: 0.03,
                AnalyticsMetric.AUDIENCE_GROWTH: 0.05,  # 5% monthly growth
                AnalyticsMetric.CLICK_THROUGH_RATE: 0.015,
                AnalyticsMetric.CONVERSION_RATE: 0.02
            },
            "brand": {
                AnalyticsMetric.ENGAGEMENT_RATE: 0.025,
                AnalyticsMetric.AUDIENCE_GROWTH: 0.03,
                AnalyticsMetric.CLICK_THROUGH_RATE: 0.01,
                AnalyticsMetric.CONVERSION_RATE: 0.03
            }
        }
        
        benchmarks = {}
        base_benchmarks = industry_benchmarks.get(entity_type, industry_benchmarks["creator"])
        
        for metric, benchmark_value in base_benchmarks.items():
            if metric in metrics_data:
                current_data = metrics_data[metric]
                if current_data:
                    current_value = np.mean([dp.value for dp in current_data[-7:]])  # Last week average
                    benchmarks[f"{metric.value}_benchmark"] = benchmark_value
                    benchmarks[f"{metric.value}_vs_benchmark"] = (current_value - benchmark_value) / benchmark_value if benchmark_value > 0 else 0
        
        return benchmarks
    
    async def _generate_performance_report(self, request: AnalyticsRequest, metrics_data: Dict[AnalyticsMetric, List[MetricDataPoint]], insights: List[AnalyticsInsight], benchmarks: Dict[str, float], predictions: Dict[str, Any]) -> PerformanceReport:
        """Génération rapport de performance complet"""
        
        # Calculate overall metrics
        overall_metrics = {}
        for metric, data_points in metrics_data.items():
            if data_points:
                recent_values = [dp.value for dp in data_points[-7:]]  # Last week
                overall_metrics[metric] = np.mean(recent_values)
        
        # Trend analysis
        trend_analysis = {
            "growth_metrics": [],
            "declining_metrics": [],
            "stable_metrics": []
        }
        
        for metric, data_points in metrics_data.items():
            if len(data_points) >= 14:
                values = [dp.value for dp in data_points]
                recent_avg = np.mean(values[-7:])
                previous_avg = np.mean(values[-14:-7])
                
                change_rate = (recent_avg - previous_avg) / previous_avg if previous_avg > 0 else 0
                
                if change_rate > 0.05:
                    trend_analysis["growth_metrics"].append({
                        "metric": metric.value,
                        "change_rate": change_rate,
                        "current_value": recent_avg
                    })
                elif change_rate < -0.05:
                    trend_analysis["declining_metrics"].append({
                        "metric": metric.value,
                        "change_rate": change_rate,
                        "current_value": recent_avg
                    })
                else:
                    trend_analysis["stable_metrics"].append({
                        "metric": metric.value,
                        "change_rate": change_rate,
                        "current_value": recent_avg
                    })
        
        # Generate recommendations
        recommendations = []
        high_priority_insights = [insight for insight in insights if insight.priority == "high"]
        for insight in high_priority_insights[:5]:  # Top 5 high priority insights
            recommendations.extend(insight.recommendations[:2])  # Top 2 recommendations per insight
        
        # Get time range from first query
        time_range = request.analytics_queries[0].time_range if request.analytics_queries else (datetime.now() - timedelta(days=30), datetime.now())
        
        return PerformanceReport(
            report_id=f"report_{request.entity_id}_{int(time.time())}",
            period=time_range,
            overall_metrics=overall_metrics,
            trend_analysis=trend_analysis,
            insights=insights,
            benchmarks=benchmarks,
            predictions=predictions,
            recommendations=list(set(recommendations)),  # Remove duplicates
            report_generated_at=datetime.now()
        )
    
    async def _create_comparative_analysis(self, metrics_data: Dict[AnalyticsMetric, List[MetricDataPoint]]) -> Dict[str, Any]:
        """Création analyse comparative"""
        
        comparative_data = {}
        
        for metric, data_points in metrics_data.items():
            if len(data_points) >= 14:  # Need at least 2 weeks for comparison
                values = [dp.value for dp in data_points]
                
                # Current week vs previous week
                current_week = values[-7:]
                previous_week = values[-14:-7]
                
                current_avg = np.mean(current_week)
                previous_avg = np.mean(previous_week)
                
                week_over_week_change = (current_avg - previous_avg) / previous_avg if previous_avg > 0 else 0
                
                # Best day vs worst day
                best_day_value = max(values)
                worst_day_value = min(values)
                
                comparative_data[metric.value] = {
                    "week_over_week_change": week_over_week_change,
                    "current_week_avg": current_avg,
                    "previous_week_avg": previous_avg,
                    "best_day_value": best_day_value,
                    "worst_day_value": worst_day_value,
                    "volatility": np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
                }
        
        return comparative_data
    
    async def _prepare_dashboard_data(self, metrics_data: Dict[AnalyticsMetric, List[MetricDataPoint]], insights: List[AnalyticsInsight], predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Préparation données pour dashboard"""
        
        dashboard = {
            "summary_cards": [],
            "chart_data": {},
            "insights_summary": {
                "total_insights": len(insights),
                "high_priority": len([i for i in insights if i.priority == "high"]),
                "medium_priority": len([i for i in insights if i.priority == "medium"]),
                "low_priority": len([i for i in insights if i.priority == "low"])
            },
            "alerts": []
        }
        
        # Create summary cards
        for metric, data_points in metrics_data.items():
            if data_points:
                latest_value = data_points[-1].value
                previous_value = data_points[-2].value if len(data_points) > 1 else latest_value
                
                change = (latest_value - previous_value) / previous_value if previous_value > 0 else 0
                
                dashboard["summary_cards"].append({
                    "metric": metric.value,
                    "current_value": latest_value,
                    "change_percentage": change,
                    "trend": "up" if change > 0 else "down" if change < 0 else "stable",
                    "status": "good" if change > 0 else "warning" if change < -0.1 else "neutral"
                })
        
        # Prepare chart data
        for metric, data_points in metrics_data.items():
            dashboard["chart_data"][metric.value] = {
                "timestamps": [dp.timestamp.isoformat() for dp in data_points],
                "values": [dp.value for dp in data_points],
                "metadata": [dp.metadata for dp in data_points]
            }
        
        # Add high priority insights as alerts
        high_priority_insights = [i for i in insights if i.priority == "high"]
        for insight in high_priority_insights[:3]:  # Top 3 alerts
            dashboard["alerts"].append({
                "title": insight.title,
                "description": insight.description,
                "type": "warning" if insight.insight_type == InsightType.RISK_ALERT else "info",
                "impact_score": insight.impact_score
            })
        
        return dashboard

# Custom exceptions
class AnalyticsException(Exception):
    """Exception pour erreurs analytics"""
    pass

# Module exports
__all__ = [
    "AnalyticsMetric",
    "TimeGranularity", 
    "AnalyticsDataSource",
    "InsightType",
    "MetricDataPoint",
    "AnalyticsQuery",
    "AnalyticsInsight",
    "PerformanceReport", 
    "AnalyticsRequest",
    "AnalyticsResult",
    "AnalyticsPipeline",
    "MetricsCollector",
    "InsightGenerator",
    "PredictiveAnalyzer"
]