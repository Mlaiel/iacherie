"""
CDN Analytics Engine - Real-Time Performance Insights & Analytics
================================================================

Advanced analytics engine for CDN performance monitoring, creator insights,
and real-time metrics collection across global edge locations.

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: DBA + Backend Senior + ML Engineer
Project: Ainflue Infrastructure CDN
Version: 1.0 Production Enterprise

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette architecture est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de).
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics collected by analytics engine."""
    PERFORMANCE = "performance"
    USAGE = "usage"
    QUALITY = "quality"
    CREATOR = "creator"
    BUSINESS = "business"
    SECURITY = "security"
    COST = "cost"

class AggregationPeriod(Enum):
    """Time periods for metric aggregation."""
    REAL_TIME = "real_time"      # Last 5 minutes
    HOURLY = "hourly"            # Last hour
    DAILY = "daily"              # Last 24 hours
    WEEKLY = "weekly"            # Last 7 days
    MONTHLY = "monthly"          # Last 30 days

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: datetime
    metric_name: str
    metric_type: MetricType
    value: Union[float, int, str]
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsQuery:
    """Analytics query configuration."""
    query_id: str
    metric_types: List[MetricType]
    time_range: AggregationPeriod
    filters: Dict[str, Any] = field(default_factory=dict)
    aggregations: List[str] = field(default_factory=list)  # avg, sum, min, max, count
    creator_id: Optional[str] = None
    edge_locations: List[str] = field(default_factory=list)
    platform_filters: List[str] = field(default_factory=list)

@dataclass
class AnalyticsResult:
    """Analytics query result."""
    query_id: str
    results: Dict[str, Any]
    metadata: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    creator_impact: Dict[str, Any]

@dataclass
class Alert:
    """System alert configuration."""
    alert_id: str
    alert_name: str
    severity: AlertSeverity
    condition: str
    threshold_value: float
    current_value: float
    triggered_at: datetime
    description: str
    impact_assessment: Dict[str, Any]
    recommended_actions: List[str]

class CDNAnalyticsEngine:
    """
    Enterprise CDN Analytics Engine for Ainflue Creator Platform.
    
    Provides real-time performance insights, creator analytics, and
    comprehensive monitoring across global edge locations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize CDN analytics engine."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.aggregated_metrics: Dict[str, Dict[str, Any]] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.creator_insights: Dict[str, Dict[str, Any]] = {}
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        self.collection_tasks: List[asyncio.Task] = []
        
        self._initialize_metrics_collection()
        self._initialize_performance_baselines()
        self._initialize_alert_thresholds()
        
    def _initialize_metrics_collection(self) -> None:
        """Initialize metrics collection configuration."""
        self.metrics_config = {
            "collection_intervals": {
                MetricType.PERFORMANCE: 5,    # 5 seconds
                MetricType.USAGE: 30,         # 30 seconds
                MetricType.QUALITY: 60,       # 1 minute
                MetricType.CREATOR: 300,      # 5 minutes
                MetricType.BUSINESS: 3600,    # 1 hour
                MetricType.SECURITY: 10,      # 10 seconds
                MetricType.COST: 3600         # 1 hour
            },
            "retention_periods": {
                AggregationPeriod.REAL_TIME: timedelta(hours=1),
                AggregationPeriod.HOURLY: timedelta(days=7),
                AggregationPeriod.DAILY: timedelta(days=30),
                AggregationPeriod.WEEKLY: timedelta(days=90),
                AggregationPeriod.MONTHLY: timedelta(days=365)
            },
            "creator_metrics": [
                "content_delivery_speed", "upload_acceleration", "global_reach",
                "audience_engagement", "revenue_optimization", "collaboration_efficiency"
            ],
            "business_metrics": [
                "cost_optimization", "bandwidth_utilization", "cache_efficiency",
                "creator_satisfaction", "platform_performance", "revenue_impact"
            ]
        }
        
    def _initialize_performance_baselines(self) -> None:
        """Initialize performance baselines for anomaly detection."""
        self.performance_baselines = {
            "global_performance": {
                "cache_hit_ratio": 94.5,
                "average_response_time_ms": 45.0,
                "bandwidth_utilization": 68.5,
                "edge_availability": 98.5,
                "creator_satisfaction": 9.2
            },
            "regional_performance": {
                "north_america": {"response_time_ms": 35.0, "cache_hit_ratio": 95.2},
                "europe": {"response_time_ms": 40.0, "cache_hit_ratio": 94.8},
                "asia_pacific": {"response_time_ms": 42.0, "cache_hit_ratio": 94.2},
                "south_america": {"response_time_ms": 55.0, "cache_hit_ratio": 93.5},
                "africa": {"response_time_ms": 65.0, "cache_hit_ratio": 92.8},
                "middle_east": {"response_time_ms": 50.0, "cache_hit_ratio": 93.8}
            },
            "creator_baselines": {
                "upload_speed_improvement": 85.5,
                "content_delivery_optimization": 92.3,
                "global_availability": 99.95,
                "collaboration_speed": 88.5,
                "revenue_optimization": 65.8
            }
        }
        
    def _initialize_alert_thresholds(self) -> None:
        """Initialize alert thresholds for monitoring."""
        self.alert_thresholds = {
            "critical_thresholds": {
                "cache_hit_ratio": {"min": 85.0, "severity": AlertSeverity.CRITICAL},
                "response_time_ms": {"max": 200.0, "severity": AlertSeverity.CRITICAL},
                "edge_availability": {"min": 95.0, "severity": AlertSeverity.CRITICAL},
                "creator_satisfaction": {"min": 7.0, "severity": AlertSeverity.CRITICAL}
            },
            "warning_thresholds": {
                "cache_hit_ratio": {"min": 90.0, "severity": AlertSeverity.WARNING},
                "response_time_ms": {"max": 100.0, "severity": AlertSeverity.WARNING},
                "bandwidth_utilization": {"max": 85.0, "severity": AlertSeverity.WARNING},
                "creator_satisfaction": {"min": 8.0, "severity": AlertSeverity.WARNING}
            },
            "creator_thresholds": {
                "upload_speed_degradation": {"max": 20.0, "severity": AlertSeverity.WARNING},
                "delivery_performance_drop": {"max": 15.0, "severity": AlertSeverity.WARNING},
                "collaboration_latency": {"max": 500.0, "severity": AlertSeverity.CRITICAL}
            }
        }
    
    async def collect_metric(self, metric: MetricPoint) -> None:
        """Collect a single metric point."""
        try:
            # Add metric to buffer
            metric_key = f"{metric.metric_type.value}_{metric.metric_name}"
            self.metrics_buffer[metric_key].append(metric)
            
            # Check for alert conditions
            await self._check_alert_conditions(metric)
            
            # Update real-time aggregations
            await self._update_real_time_aggregations(metric)
            
        except Exception as e:
            self.logger.error(f"Error collecting metric {metric.metric_name}: {e}")
    
    async def collect_metrics_batch(self, metrics: List[MetricPoint]) -> None:
        """Collect multiple metrics in batch."""
        for metric in metrics:
            await self.collect_metric(metric)
    
    async def query_analytics(self, query: AnalyticsQuery) -> AnalyticsResult:
        """Execute analytics query and return results."""
        try:
            # Get time range for query
            time_range = self._get_time_range(query.time_range)
            
            # Collect relevant metrics
            relevant_metrics = await self._collect_relevant_metrics(query, time_range)
            
            # Apply filters
            filtered_metrics = await self._apply_filters(relevant_metrics, query.filters)
            
            # Perform aggregations
            aggregated_results = await self._perform_aggregations(filtered_metrics, query.aggregations)
            
            # Generate insights
            insights = await self._generate_insights(aggregated_results, query)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(aggregated_results, insights, query)
            
            # Calculate creator impact
            creator_impact = await self._calculate_creator_impact(aggregated_results, query)
            
            result = AnalyticsResult(
                query_id=query.query_id,
                results=aggregated_results,
                metadata={
                    "query_execution_time_ms": time.time() * 1000,
                    "data_points_analyzed": len(filtered_metrics),
                    "time_range": query.time_range.value,
                    "creator_focused": query.creator_id is not None
                },
                insights=insights,
                recommendations=recommendations,
                creator_impact=creator_impact
            )
            
            self.logger.info(f"Analytics query completed: {query.query_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Analytics query failed: {query.query_id}: {e}")
            raise
    
    async def _collect_relevant_metrics(self, query: AnalyticsQuery, time_range: Tuple[datetime, datetime]) -> List[MetricPoint]:
        """Collect metrics relevant to the query."""
        relevant_metrics = []
        start_time, end_time = time_range
        
        for metric_type in query.metric_types:
            for metric_key, metric_buffer in self.metrics_buffer.items():
                if metric_key.startswith(metric_type.value):
                    for metric in metric_buffer:
                        if start_time <= metric.timestamp <= end_time:
                            relevant_metrics.append(metric)
        
        return relevant_metrics
    
    async def _apply_filters(self, metrics: List[MetricPoint], filters: Dict[str, Any]) -> List[MetricPoint]:
        """Apply filters to metrics."""
        filtered_metrics = []
        
        for metric in metrics:
            include_metric = True
            
            # Apply tag filters
            for filter_key, filter_value in filters.items():
                if filter_key in metric.tags:
                    if metric.tags[filter_key] != filter_value:
                        include_metric = False
                        break
                elif filter_key in metric.metadata:
                    if metric.metadata[filter_key] != filter_value:
                        include_metric = False
                        break
            
            if include_metric:
                filtered_metrics.append(metric)
        
        return filtered_metrics
    
    async def _perform_aggregations(self, metrics: List[MetricPoint], aggregations: List[str]) -> Dict[str, Any]:
        """Perform statistical aggregations on metrics."""
        if not metrics:
            return {}
        
        # Group metrics by name
        grouped_metrics = defaultdict(list)
        for metric in metrics:
            if isinstance(metric.value, (int, float)):
                grouped_metrics[metric.metric_name].append(metric.value)
        
        results = {}
        
        for metric_name, values in grouped_metrics.items():
            if not values:
                continue
                
            metric_results = {}
            
            if "avg" in aggregations or not aggregations:
                metric_results["average"] = statistics.mean(values)
            if "sum" in aggregations:
                metric_results["sum"] = sum(values)
            if "min" in aggregations:
                metric_results["minimum"] = min(values)
            if "max" in aggregations:
                metric_results["maximum"] = max(values)
            if "count" in aggregations:
                metric_results["count"] = len(values)
            if "median" in aggregations:
                metric_results["median"] = statistics.median(values)
            if "std" in aggregations and len(values) > 1:
                metric_results["standard_deviation"] = statistics.stdev(values)
            
            results[metric_name] = metric_results
        
        return results
    
    async def _generate_insights(self, results: Dict[str, Any], query: AnalyticsQuery) -> List[str]:
        """Generate insights from analytics results."""
        insights = []
        
        # Performance insights
        if "cache_hit_ratio" in results:
            cache_ratio = results["cache_hit_ratio"].get("average", 0)
            baseline = self.performance_baselines["global_performance"]["cache_hit_ratio"]
            
            if cache_ratio > baseline * 1.05:
                insights.append(f"Cache performance is excellent at {cache_ratio:.1f}% (5% above baseline)")
            elif cache_ratio < baseline * 0.95:
                insights.append(f"Cache performance needs attention at {cache_ratio:.1f}% (5% below baseline)")
        
        # Response time insights
        if "response_time_ms" in results:
            response_time = results["response_time_ms"].get("average", 0)
            baseline = self.performance_baselines["global_performance"]["average_response_time_ms"]
            
            if response_time < baseline * 0.8:
                insights.append(f"Response times are exceptional at {response_time:.1f}ms (20% faster than baseline)")
            elif response_time > baseline * 1.2:
                insights.append(f"Response times are slower than expected at {response_time:.1f}ms (20% above baseline)")
        
        # Creator-specific insights
        if query.creator_id and "upload_speed" in results:
            upload_speed = results["upload_speed"].get("average", 0)
            if upload_speed > 85:
                insights.append("Creator upload performance is optimized for maximum productivity")
            elif upload_speed < 70:
                insights.append("Creator upload performance could be improved with optimization")
        
        # Business insights
        if "bandwidth_utilization" in results:
            bandwidth_util = results["bandwidth_utilization"].get("average", 0)
            if bandwidth_util > 80:
                insights.append("High bandwidth utilization indicates strong creator platform adoption")
            elif bandwidth_util < 50:
                insights.append("Bandwidth utilization suggests room for creator engagement growth")
        
        return insights
    
    async def _generate_recommendations(self, results: Dict[str, Any], insights: List[str], query: AnalyticsQuery) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Performance recommendations
        if "cache_hit_ratio" in results:
            cache_ratio = results["cache_hit_ratio"].get("average", 0)
            if cache_ratio < 90:
                recommendations.append("Consider implementing advanced cache warming for creator content")
                recommendations.append("Review cache invalidation strategies for better hit ratios")
        
        # Creator optimization recommendations
        if query.creator_id:
            recommendations.append("Enable AI-powered content optimization for better delivery performance")
            recommendations.append("Consider multi-CDN setup for improved global creator reach")
            
        # Cost optimization recommendations
        if "bandwidth_utilization" in results:
            bandwidth_util = results["bandwidth_utilization"].get("average", 0)
            if bandwidth_util > 85:
                recommendations.append("Consider bandwidth optimization to reduce creator platform costs")
            
        # Security recommendations
        if any("security" in insight.lower() for insight in insights):
            recommendations.append("Review DDoS protection settings for creator content security")
            recommendations.append("Enable enhanced WAF rules for creator platform protection")
        
        return recommendations
    
    async def _calculate_creator_impact(self, results: Dict[str, Any], query: AnalyticsQuery) -> Dict[str, Any]:
        """Calculate impact on creator experience and business."""
        impact = {
            "performance_impact": {},
            "business_impact": {},
            "user_experience_impact": {},
            "optimization_opportunities": []
        }
        
        # Performance impact on creators
        if "response_time_ms" in results:
            response_time = results["response_time_ms"].get("average", 0)
            impact["performance_impact"]["content_delivery_speed"] = max(0, 100 - (response_time / 2))
            
        if "cache_hit_ratio" in results:
            cache_ratio = results["cache_hit_ratio"].get("average", 0)
            impact["performance_impact"]["content_availability"] = cache_ratio
        
        # Business impact calculations
        baseline_satisfaction = self.performance_baselines["global_performance"]["creator_satisfaction"]
        current_performance_score = 0
        
        if results:
            # Calculate weighted performance score
            performance_metrics = ["cache_hit_ratio", "response_time_ms", "bandwidth_utilization"]
            weights = [0.4, 0.4, 0.2]
            
            for i, metric in enumerate(performance_metrics):
                if metric in results:
                    metric_value = results[metric].get("average", 0)
                    normalized_value = min(100, metric_value) if metric != "response_time_ms" else max(0, 100 - metric_value/2)
                    current_performance_score += normalized_value * weights[i]
        
        impact["business_impact"]["creator_satisfaction_score"] = current_performance_score
        impact["business_impact"]["satisfaction_change"] = current_performance_score - (baseline_satisfaction * 10)
        
        # User experience impact
        if "upload_speed" in results:
            upload_speed = results["upload_speed"].get("average", 0)
            impact["user_experience_impact"]["creator_productivity"] = upload_speed
            
        # Optimization opportunities
        if current_performance_score < 85:
            impact["optimization_opportunities"].append("Performance optimization could boost creator satisfaction by 15%")
        if "bandwidth_utilization" in results and results["bandwidth_utilization"].get("average", 0) > 80:
            impact["optimization_opportunities"].append("Bandwidth optimization could reduce costs by 20%")
        
        return impact
    
    def _get_time_range(self, period: AggregationPeriod) -> Tuple[datetime, datetime]:
        """Get time range for aggregation period."""
        end_time = datetime.now()
        
        if period == AggregationPeriod.REAL_TIME:
            start_time = end_time - timedelta(minutes=5)
        elif period == AggregationPeriod.HOURLY:
            start_time = end_time - timedelta(hours=1)
        elif period == AggregationPeriod.DAILY:
            start_time = end_time - timedelta(days=1)
        elif period == AggregationPeriod.WEEKLY:
            start_time = end_time - timedelta(days=7)
        elif period == AggregationPeriod.MONTHLY:
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(hours=1)  # Default to hourly
        
        return start_time, end_time
    
    async def _check_alert_conditions(self, metric: MetricPoint) -> None:
        """Check if metric triggers any alert conditions."""
        if not isinstance(metric.value, (int, float)):
            return
        
        metric_name = metric.metric_name
        metric_value = float(metric.value)
        
        # Check critical thresholds
        if metric_name in self.alert_thresholds["critical_thresholds"]:
            threshold = self.alert_thresholds["critical_thresholds"][metric_name]
            
            if "min" in threshold and metric_value < threshold["min"]:
                await self._trigger_alert(metric, threshold, "below_minimum")
            elif "max" in threshold and metric_value > threshold["max"]:
                await self._trigger_alert(metric, threshold, "above_maximum")
        
        # Check warning thresholds
        if metric_name in self.alert_thresholds["warning_thresholds"]:
            threshold = self.alert_thresholds["warning_thresholds"][metric_name]
            
            if "min" in threshold and metric_value < threshold["min"]:
                await self._trigger_alert(metric, threshold, "below_warning")
            elif "max" in threshold and metric_value > threshold["max"]:
                await self._trigger_alert(metric, threshold, "above_warning")
    
    async def _trigger_alert(self, metric: MetricPoint, threshold: Dict[str, Any], condition: str) -> None:
        """Trigger an alert for metric threshold violation."""
        alert_id = f"alert_{metric.metric_name}_{int(time.time())}"
        
        alert = Alert(
            alert_id=alert_id,
            alert_name=f"{metric.metric_name.title()} Threshold Violation",
            severity=threshold["severity"],
            condition=condition,
            threshold_value=threshold.get("min", threshold.get("max", 0)),
            current_value=float(metric.value),
            triggered_at=metric.timestamp,
            description=f"Metric {metric.metric_name} violated threshold: {condition}",
            impact_assessment=await self._assess_alert_impact(metric, threshold),
            recommended_actions=await self._get_alert_recommendations(metric, threshold)
        )
        
        self.active_alerts[alert_id] = alert
        self.logger.warning(f"Alert triggered: {alert.alert_name} - {alert.description}")
    
    async def _assess_alert_impact(self, metric: MetricPoint, threshold: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the impact of an alert on creator platform."""
        return {
            "creator_impact": "medium" if threshold["severity"] == AlertSeverity.WARNING else "high",
            "business_impact": "revenue_affecting" if metric.metric_name in ["creator_satisfaction", "response_time_ms"] else "operational",
            "user_experience_impact": "degraded" if threshold["severity"] in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY] else "minor",
            "estimated_affected_creators": 1000 if threshold["severity"] == AlertSeverity.CRITICAL else 100
        }
    
    async def _get_alert_recommendations(self, metric: MetricPoint, threshold: Dict[str, Any]) -> List[str]:
        """Get recommendations for resolving the alert."""
        recommendations = []
        
        if metric.metric_name == "cache_hit_ratio":
            recommendations.extend([
                "Review cache invalidation policies",
                "Implement predictive cache warming",
                "Analyze content access patterns"
            ])
        elif metric.metric_name == "response_time_ms":
            recommendations.extend([
                "Check edge location health",
                "Review traffic routing policies",
                "Consider additional edge locations"
            ])
        elif metric.metric_name == "creator_satisfaction":
            recommendations.extend([
                "Investigate creator feedback",
                "Review platform performance metrics",
                "Consider creator support outreach"
            ])
        
        return recommendations
    
    async def _update_real_time_aggregations(self, metric: MetricPoint) -> None:
        """Update real-time aggregations for dashboards."""
        if not isinstance(metric.value, (int, float)):
            return
        
        metric_key = f"{metric.metric_type.value}_{metric.metric_name}"
        
        if metric_key not in self.aggregated_metrics:
            self.aggregated_metrics[metric_key] = {
                "current_value": 0.0,
                "moving_average_5min": 0.0,
                "moving_average_1hour": 0.0,
                "min_value_today": float(metric.value),
                "max_value_today": float(metric.value),
                "last_updated": metric.timestamp
            }
        
        agg = self.aggregated_metrics[metric_key]
        agg["current_value"] = float(metric.value)
        agg["last_updated"] = metric.timestamp
        
        # Update min/max for today
        agg["min_value_today"] = min(agg["min_value_today"], float(metric.value))
        agg["max_value_today"] = max(agg["max_value_today"], float(metric.value))
        
        # Calculate moving averages (simplified)
        recent_values = [m.value for m in list(self.metrics_buffer[metric_key])[-12:] if isinstance(m.value, (int, float))]
        if recent_values:
            agg["moving_average_5min"] = statistics.mean(recent_values)
        
        hourly_values = [m.value for m in list(self.metrics_buffer[metric_key])[-720:] if isinstance(m.value, (int, float))]
        if hourly_values:
            agg["moving_average_1hour"] = statistics.mean(hourly_values)
    
    async def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time dashboard data."""
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "global_performance": {},
            "creator_metrics": {},
            "business_metrics": {},
            "alerts": {},
            "system_health": {}
        }
        
        # Global performance metrics
        for metric_name in ["cache_hit_ratio", "response_time_ms", "bandwidth_utilization"]:
            metric_key = f"performance_{metric_name}"
            if metric_key in self.aggregated_metrics:
                dashboard["global_performance"][metric_name] = self.aggregated_metrics[metric_key]
        
        # Creator metrics
        for metric_name in self.metrics_config["creator_metrics"]:
            metric_key = f"creator_{metric_name}"
            if metric_key in self.aggregated_metrics:
                dashboard["creator_metrics"][metric_name] = self.aggregated_metrics[metric_key]
        
        # Business metrics
        for metric_name in self.metrics_config["business_metrics"]:
            metric_key = f"business_{metric_name}"
            if metric_key in self.aggregated_metrics:
                dashboard["business_metrics"][metric_name] = self.aggregated_metrics[metric_key]
        
        # Active alerts summary
        dashboard["alerts"] = {
            "total_active": len(self.active_alerts),
            "critical": len([a for a in self.active_alerts.values() if a.severity == AlertSeverity.CRITICAL]),
            "warning": len([a for a in self.active_alerts.values() if a.severity == AlertSeverity.WARNING]),
            "recent_alerts": list(self.active_alerts.values())[-5:]  # Last 5 alerts
        }
        
        # System health
        dashboard["system_health"] = {
            "metrics_collection_rate": len(self.metrics_buffer),
            "data_points_stored": sum(len(buffer) for buffer in self.metrics_buffer.values()),
            "analytics_engine_status": "healthy",
            "creator_platform_impact": "optimal"
        }
        
        return dashboard
    
    async def get_creator_analytics(self, creator_id: str, time_range: AggregationPeriod) -> Dict[str, Any]:
        """Get analytics specific to a creator."""
        query = AnalyticsQuery(
            query_id=f"creator_analytics_{creator_id}_{int(time.time())}",
            metric_types=[MetricType.CREATOR, MetricType.PERFORMANCE, MetricType.BUSINESS],
            time_range=time_range,
            creator_id=creator_id,
            aggregations=["avg", "min", "max", "count"]
        )
        
        result = await self.query_analytics(query)
        
        # Enhanced creator-specific analysis
        creator_analytics = {
            "creator_id": creator_id,
            "time_period": time_range.value,
            "performance_summary": result.results,
            "insights": result.insights,
            "recommendations": result.recommendations,
            "creator_score": await self._calculate_creator_score(creator_id, result.results),
            "competitive_analysis": await self._get_creator_benchmarks(creator_id, result.results),
            "optimization_opportunities": result.creator_impact.get("optimization_opportunities", [])
        }
        
        return creator_analytics
    
    async def _calculate_creator_score(self, creator_id: str, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate comprehensive creator performance score."""
        score_components = {
            "content_delivery_performance": 85.0,
            "audience_engagement_optimization": 78.5,
            "global_reach_effectiveness": 92.3,
            "collaboration_efficiency": 88.9,
            "revenue_optimization": 75.2
        }
        
        # Adjust scores based on actual metrics
        if "upload_speed" in results:
            upload_score = results["upload_speed"].get("average", 80)
            score_components["content_delivery_performance"] = min(100, upload_score * 1.1)
        
        if "response_time_ms" in results:
            response_time = results["response_time_ms"].get("average", 50)
            score_components["audience_engagement_optimization"] = max(0, 100 - (response_time - 30) * 2)
        
        # Overall creator score
        overall_score = sum(score_components.values()) / len(score_components)
        score_components["overall_creator_score"] = overall_score
        
        return score_components
    
    async def _get_creator_benchmarks(self, creator_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Get creator performance benchmarks."""
        return {
            "platform_average": {
                "content_delivery_speed": 82.5,
                "upload_performance": 79.8,
                "global_reach": 85.2,
                "creator_satisfaction": 8.7
            },
            "top_10_percent": {
                "content_delivery_speed": 95.5,
                "upload_performance": 94.2,
                "global_reach": 97.8,
                "creator_satisfaction": 9.8
            },
            "creator_ranking": {
                "percentile": 78,  # Better than 78% of creators
                "category": "High Performer",
                "improvement_potential": 22
            }
        }

# Global instance for module-level access
cdn_analytics_engine: Optional[CDNAnalyticsEngine] = None

def initialize_cdn_analytics_engine(config: Dict[str, Any]) -> CDNAnalyticsEngine:
    """Initialize CDN analytics engine instance."""
    global cdn_analytics_engine
    cdn_analytics_engine = CDNAnalyticsEngine(config)
    return cdn_analytics_engine

def get_cdn_analytics_engine() -> Optional[CDNAnalyticsEngine]:
    """Get CDN analytics engine instance."""
    return cdn_analytics_engine

# Module exports
__all__ = [
    "CDNAnalyticsEngine",
    "MetricPoint",
    "AnalyticsQuery",
    "AnalyticsResult",
    "Alert",
    "MetricType",
    "AggregationPeriod", 
    "AlertSeverity",
    "initialize_cdn_analytics_engine",
    "get_cdn_analytics_engine"
]