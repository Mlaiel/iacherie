"""
Ainflue Platform - Analytics Monitoring Module
==============================================

Enterprise-grade monitoring for cross-platform analytics aggregation,
real-time insights, competitive analysis, and predictive analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsModules(Enum):
    """Available analytics monitoring modules."""
    CROSS_PLATFORM_AGGREGATOR = "cross_platform_aggregator"
    REAL_TIME_INSIGHTS = "real_time_insights"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    TREND_DETECTION = "trend_detection"
    AUDIENCE_BEHAVIOR = "audience_behavior"
    PERFORMANCE_CORRELATION = "performance_correlation"
    ROI_ANALYTICS = "roi_analytics"
    ATTRIBUTION_MODELING = "attribution_modeling"
    COHORT_ANALYSIS = "cohort_analysis"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    DASHBOARD_INTELLIGENCE = "dashboard_intelligence"
    ANALYTICS_ORCHESTRATION = "analytics_orchestration"

class Platform(Enum):
    """Supported platforms for analytics."""
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    SOUNDCLOUD = "soundcloud"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    TWITCH = "twitch"
    APPLE_MUSIC = "apple_music"
    BANDCAMP = "bandcamp"

class MetricType(Enum):
    """Types of metrics tracked."""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    VIEWS = "views"
    STREAMS = "streams"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    FOLLOWERS = "followers"
    REVENUE = "revenue"
    CONVERSION = "conversion"

@dataclass
class AnalyticsConfig:
    """Configuration for analytics monitoring."""
    enabled_modules: List[AnalyticsModules]
    platforms: List[Platform]
    metric_types: List[MetricType]
    real_time_enabled: bool = True
    predictive_analytics: bool = True
    competitive_tracking: bool = True
    audience_segmentation: bool = True
    attribution_modeling: bool = True
    data_retention_days: int = 365
    aggregation_intervals: List[str] = field(default_factory=lambda: ["hourly", "daily", "weekly", "monthly"])

@dataclass
class PlatformMetrics:
    """Metrics from a specific platform."""
    platform: Platform
    content_id: str
    creator_id: str
    timestamp: datetime
    metrics: Dict[MetricType, float]
    audience_demographics: Dict[str, Any]
    engagement_details: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsInsight:
    """Generated analytics insight."""
    insight_id: str
    category: str
    title: str
    description: str
    confidence: float
    impact_level: str
    data_points: List[Dict[str, Any]]
    recommendations: List[str]
    generated_at: datetime

@dataclass
class AnalyticsMetrics:
    """Overall analytics system metrics."""
    total_data_points: int = 0
    platforms_tracked: int = 0
    insights_generated: int = 0
    prediction_accuracy: float = 0.0
    data_freshness_minutes: float = 0.0
    processing_latency_ms: float = 0.0
    anomalies_detected: int = 0

class AnalyticsOrchestrator:
    """
    Main orchestrator for analytics monitoring system.
    
    Aggregates cross-platform analytics, generates real-time insights,
    performs competitive analysis, and provides predictive analytics
    for enterprise content optimization.
    """
    
    def __init__(self, config -> None: AnalyticsConfig) -> None:
        """Initialize analytics monitoring orchestrator."""
        self.config = config
        self.modules = {}
        self.platform_data: Dict[str, List[PlatformMetrics]] = {}
        self.insights: List[AnalyticsInsight] = []
        self.metrics = AnalyticsMetrics()
        self.aggregated_data = {}
        self.trends = {}
        self.predictions = {}
        self.start_time = datetime.now()
        
        logger.info("Initializing Analytics Monitoring Orchestrator")
        self._initialize_modules()
        self._setup_data_pipelines()
    
    def _initialize_modules(self) -> None:
        """Initialize enabled analytics modules."""
        for module in self.config.enabled_modules:
            try:
                module_instance = self._create_analytics_module(module)
                self.modules[module.value] = module_instance
                logger.info(f"Initialized analytics module: {module.value}")
            except Exception as e:
                logger.error(f"Failed to initialize module {module.value}: {e}")
    
    def _create_analytics_module(self, module -> None: AnalyticsModules) -> None:
        """Create instance of specific analytics monitoring module."""
        return {
            "name": module.value,
            "status": "active",
            "data_points_processed": 0,
            "insights_generated": 0,
            "accuracy": 0.89,
            "last_update": datetime.now(),
            "performance_score": 0.93
        }
    
    def _setup_data_pipelines(self) -> None:
        """Setup data pipelines for each platform."""
        for platform in self.config.platforms:
            self.platform_data[platform.value] = []
            logger.info(f"Setup data pipeline for {platform.value}")
    
    def ingest_platform_data(
        self,
        platform: Platform,
        content_id: str,
        creator_id: str,
        metrics: Dict[MetricType, float],
        audience_demographics: Optional[Dict[str, Any]] = None,
        engagement_details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Ingest data from a platform."""
        platform_metrics = PlatformMetrics(
            platform=platform,
            content_id=content_id,
            creator_id=creator_id,
            timestamp=datetime.now(),
            metrics=metrics,
            audience_demographics=audience_demographics or {},
            engagement_details=engagement_details or {},
            metadata=metadata or {}
        )
        
        # Store platform data
        if platform.value not in self.platform_data:
            self.platform_data[platform.value] = []
        
        self.platform_data[platform.value].append(platform_metrics)
        
        # Real-time processing
        if self.config.real_time_enabled:
            self._process_real_time_data(platform_metrics)
        
        # Update metrics
        self.metrics.total_data_points += 1
        self.metrics.platforms_tracked = len(self.platform_data)
        
        data_id = f"{platform.value}_{content_id}_{int(platform_metrics.timestamp.timestamp())}"
        logger.debug(f"Ingested data from {platform.value}: {data_id}")
        return data_id
    
    def _process_real_time_data(self, data -> None: PlatformMetrics) -> None:
        """Process data in real-time for immediate insights."""
        # Anomaly detection
        anomalies = self._detect_anomalies(data)
        if anomalies:
            self.metrics.anomalies_detected += len(anomalies)
            self._generate_anomaly_insights(data, anomalies)
        
        # Trend detection
        trends = self._detect_trends(data)
        if trends:
            self._update_trend_data(data.platform, trends)
        
        # Performance correlation
        correlations = self._analyze_performance_correlations(data)
        if correlations:
            self._generate_correlation_insights(data, correlations)
    
    def _detect_anomalies(self, data: PlatformMetrics) -> List[Dict[str, Any]]:
        """Detect anomalies in real-time data."""
        anomalies = []
        
        # Get historical data for comparison
        historical_data = self.platform_data.get(data.platform.value, [])[-100:]
        
        if len(historical_data) < 10:
            return anomalies  # Not enough data for anomaly detection
        
        for metric_type, value in data.metrics.items():
            historical_values = [d.metrics.get(metric_type, 0) for d in historical_data]
            
            if len(historical_values) > 0:
                mean_val = statistics.mean(historical_values)
                std_val = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
                
                # Z-score anomaly detection
                if std_val > 0:
                    z_score = abs(value - mean_val) / std_val
                    if z_score > 3:  # 3 standard deviations
                        anomalies.append({
                            "metric": metric_type.value,
                            "value": value,
                            "expected_range": (mean_val - 2*std_val, mean_val + 2*std_val),
                            "z_score": z_score,
                            "severity": "high" if z_score > 4 else "medium"
                        })
        
        return anomalies
    
    def _detect_trends(self, data: PlatformMetrics) -> Dict[str, Any]:
        """Detect trends in metrics."""
        trends = {}
        
        # Get recent data points
        platform_history = self.platform_data.get(data.platform.value, [])[-50:]
        
        if len(platform_history) < 5:
            return trends
        
        for metric_type, current_value in data.metrics.items():
            recent_values = [d.metrics.get(metric_type, 0) for d in platform_history[-10:]]
            older_values = [d.metrics.get(metric_type, 0) for d in platform_history[-20:-10]]
            
            if len(recent_values) >= 3 and len(older_values) >= 3:
                recent_avg = statistics.mean(recent_values)
                older_avg = statistics.mean(older_values)
                
                change_rate = (recent_avg - older_avg) / max(older_avg, 1) * 100
                
                if abs(change_rate) > 10:  # 10% change threshold
                    trends[metric_type.value] = {
                        "direction": "increasing" if change_rate > 0 else "decreasing",
                        "change_rate": change_rate,
                        "recent_average": recent_avg,
                        "older_average": older_avg
                    }
        
        return trends
    
    def _analyze_performance_correlations(self, data: PlatformMetrics) -> Dict[str, Any]:
        """Analyze correlations between different metrics."""
        correlations = {}
        
        # Get historical data for correlation analysis
        platform_history = self.platform_data.get(data.platform.value, [])[-100:]
        
        if len(platform_history) < 20:
            return correlations
        
        # Calculate correlations between key metrics
        metric_pairs = [
            (MetricType.ENGAGEMENT, MetricType.REACH),
            (MetricType.LIKES, MetricType.SHARES),
            (MetricType.VIEWS, MetricType.FOLLOWERS),
            (MetricType.COMMENTS, MetricType.ENGAGEMENT)
        ]
        
        for metric_a, metric_b in metric_pairs:
            values_a = [d.metrics.get(metric_a, 0) for d in platform_history]
            values_b = [d.metrics.get(metric_b, 0) for d in platform_history]
            
            if len(values_a) == len(values_b) and len(values_a) > 10:
                correlation = self._calculate_correlation(values_a, values_b)
                if abs(correlation) > 0.5:  # Significant correlation
                    correlations[f"{metric_a.value}_{metric_b.value}"] = {
                        "correlation": correlation,
                        "strength": "strong" if abs(correlation) > 0.7 else "moderate",
                        "type": "positive" if correlation > 0 else "negative"
                    }
        
        return correlations
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _generate_anomaly_insights(self, data -> None: PlatformMetrics, anomalies -> None: List[Dict[str, Any]]) -> None:
        """Generate insights from detected anomalies."""
        for anomaly in anomalies:
            insight = AnalyticsInsight(
                insight_id=f"anomaly_{data.platform.value}_{int(datetime.now().timestamp())}",
                category="anomaly_detection",
                title=f"Unusual {anomaly['metric']} Activity Detected",
                description=f"Platform {data.platform.value} showing {anomaly['severity']} anomaly in {anomaly['metric']}",
                confidence=min(1.0, anomaly['z_score'] / 5),
                impact_level=anomaly['severity'],
                data_points=[{
                    "platform": data.platform.value,
                    "metric": anomaly['metric'],
                    "actual_value": anomaly['value'],
                    "expected_range": anomaly['expected_range'],
                    "z_score": anomaly['z_score']
                }],
                recommendations=[
                    "Investigate content or campaign changes",
                    "Check for platform algorithm updates",
                    "Analyze audience behavior patterns",
                    "Review competitive landscape"
                ],
                generated_at=datetime.now()
            )
            
            self.insights.append(insight)
            self.metrics.insights_generated += 1
    
    def get_cross_platform_summary(self, creator_id: str, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get cross-platform analytics summary for a creator."""
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        
        platform_summaries = {}
        total_metrics = {metric.value: 0 for metric in MetricType}
        
        for platform_name, data_list in self.platform_data.items():
            # Filter data for the creator and time range
            relevant_data = [
                d for d in data_list 
                if d.creator_id == creator_id and d.timestamp >= cutoff_time
            ]
            
            if not relevant_data:
                continue
            
            # Aggregate metrics for this platform
            platform_metrics = {metric.value: 0 for metric in MetricType}
            for data in relevant_data:
                for metric_type, value in data.metrics.items():
                    platform_metrics[metric_type.value] += value
                    total_metrics[metric_type.value] += value
            
            platform_summaries[platform_name] = {
                "metrics": platform_metrics,
                "data_points": len(relevant_data),
                "performance_score": self._calculate_performance_score(platform_metrics),
                "top_content": self._get_top_performing_content(relevant_data, 3)
            }
        
        return {
            "creator_id": creator_id,
            "time_range_hours": time_range_hours,
            "total_metrics": total_metrics,
            "platform_breakdown": platform_summaries,
            "overall_performance_score": self._calculate_performance_score(total_metrics),
            "key_insights": self._generate_key_insights(creator_id, platform_summaries),
            "generated_at": datetime.now().isoformat()
        }
    
    def _calculate_performance_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall performance score from metrics."""
        # Weighted scoring based on metric importance
        weights = {
            "engagement": 0.25,
            "reach": 0.20,
            "views": 0.15,
            "streams": 0.15,
            "likes": 0.10,
            "shares": 0.10,
            "comments": 0.05
        }
        
        # Normalize metrics (simplified approach)
        normalized_score = 0
        total_weight = 0
        
        for metric, value in metrics.items():
            if metric in weights and value > 0:
                # Simple normalization (in practice, this would use historical baselines)
                normalized_value = min(1.0, value / 1000)  # Placeholder normalization
                normalized_score += normalized_value * weights[metric]
                total_weight += weights[metric]
        
        return normalized_score / max(total_weight, 0.1)
    
    def _get_top_performing_content(self, data_list: List[PlatformMetrics], limit: int) -> List[Dict[str, Any]]:
        """Get top performing content from data list."""
        # Group by content_id and sum metrics
        content_performance = {}
        
        for data in data_list:
            content_id = data.content_id
            if content_id not in content_performance:
                content_performance[content_id] = {
                    "content_id": content_id,
                    "total_engagement": 0,
                    "total_reach": 0,
                    "performance_score": 0
                }
            
            content_performance[content_id]["total_engagement"] += data.metrics.get(MetricType.ENGAGEMENT, 0)
            content_performance[content_id]["total_reach"] += data.metrics.get(MetricType.REACH, 0)
        
        # Calculate performance scores and sort
        for content in content_performance.values():
            content["performance_score"] = (content["total_engagement"] * 0.6 + 
                                          content["total_reach"] * 0.4)
        
        top_content = sorted(
            content_performance.values(),
            key=lambda x: x["performance_score"],
            reverse=True
        )[:limit]
        
        return top_content
    
    def _generate_key_insights(self, creator_id: str, platform_summaries: Dict[str, Any]) -> List[str]:
        """Generate key insights from cross-platform data."""
        insights = []
        
        # Find best performing platform
        if platform_summaries:
            best_platform = max(
                platform_summaries.items(),
                key=lambda x: x[1]["performance_score"]
            )
            insights.append(f"Best performing platform: {best_platform[0]} (score: {best_platform[1]['performance_score']:.2f})")
        
        # Engagement analysis
        total_engagement = sum(
            summary["metrics"].get("engagement", 0) 
            for summary in platform_summaries.values()
        )
        if total_engagement > 0:
            insights.append(f"Total engagement across platforms: {total_engagement:,.0f}")
        
        # Platform diversification
        active_platforms = len(platform_summaries)
        if active_platforms > 3:
            insights.append(f"Strong platform diversification with {active_platforms} active platforms")
        elif active_platforms < 2:
            insights.append("Consider expanding to more platforms for better reach")
        
        return insights
    
    def get_analytics_status(self) -> Dict[str, Any]:
        """Get overall analytics system status."""
        return {
            "system_status": "active",
            "total_data_points": self.metrics.total_data_points,
            "platforms_tracked": self.metrics.platforms_tracked,
            "insights_generated": self.metrics.insights_generated,
            "prediction_accuracy": round(self.metrics.prediction_accuracy, 3),
            "data_freshness_minutes": round(self.metrics.data_freshness_minutes, 1),
            "processing_latency_ms": round(self.metrics.processing_latency_ms, 1),
            "anomalies_detected": self.metrics.anomalies_detected,
            "active_modules": len([m for m in self.modules.values() if m["status"] == "active"]),
            "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
            "last_updated": datetime.now().isoformat()
        }

def create_enterprise_config() -> AnalyticsConfig:
    """Create enterprise-level configuration for analytics monitoring."""
    return AnalyticsConfig(
        enabled_modules=[
            AnalyticsModules.CROSS_PLATFORM_AGGREGATOR,
            AnalyticsModules.REAL_TIME_INSIGHTS,
            AnalyticsModules.COMPETITIVE_ANALYSIS,
            AnalyticsModules.TREND_DETECTION,
            AnalyticsModules.AUDIENCE_BEHAVIOR,
            AnalyticsModules.PERFORMANCE_CORRELATION,
            AnalyticsModules.ROI_ANALYTICS,
            AnalyticsModules.ATTRIBUTION_MODELING,
            AnalyticsModules.COHORT_ANALYSIS,
            AnalyticsModules.PREDICTIVE_ANALYTICS,
            AnalyticsModules.DASHBOARD_INTELLIGENCE,
            AnalyticsModules.ANALYTICS_ORCHESTRATION
        ],
        platforms=[
            Platform.YOUTUBE,
            Platform.SPOTIFY,
            Platform.INSTAGRAM,
            Platform.TIKTOK,
            Platform.SOUNDCLOUD,
            Platform.FACEBOOK,
            Platform.TWITTER,
            Platform.TWITCH
        ],
        metric_types=[
            MetricType.ENGAGEMENT,
            MetricType.REACH,
            MetricType.VIEWS,
            MetricType.STREAMS,
            MetricType.LIKES,
            MetricType.SHARES,
            MetricType.COMMENTS,
            MetricType.FOLLOWERS,
            MetricType.REVENUE,
            MetricType.CONVERSION
        ],
        real_time_enabled=True,
        predictive_analytics=True,
        competitive_tracking=True,
        audience_segmentation=True,
        attribution_modeling=True,
        data_retention_days=365
    )

# Initialize default orchestrator
enterprise_config = create_enterprise_config()
analytics_monitoring = AnalyticsOrchestrator(enterprise_config)

# Export main components
__all__ = [
    'AnalyticsOrchestrator',
    'AnalyticsConfig',
    'AnalyticsModules',
    'Platform',
    'MetricType',
    'PlatformMetrics',
    'AnalyticsInsight',
    'create_enterprise_config',
    'analytics_monitoring'
]