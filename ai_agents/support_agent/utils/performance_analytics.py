"""
Performance Analytics - Ultra-Advanced Support Performance Monitoring System

Enterprise-grade performance analytics providing comprehensive metrics, insights,
and optimization recommendations for customer support operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import math

# Analytics and statistics
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.graph_objs as go
import plotly.express as px

# Database and caching
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of performance metrics"""
    RESPONSE_TIME = "response_time"
    RESOLUTION_TIME = "resolution_time"
    SATISFACTION_RATING = "satisfaction_rating"
    CONVERSATION_LENGTH = "conversation_length"
    ESCALATION_RATE = "escalation_rate"
    SUCCESS_RATE = "success_rate"
    KNOWLEDGE_EFFECTIVENESS = "knowledge_effectiveness"
    AGENT_WORKLOAD = "agent_workload"
    CUSTOMER_RETENTION = "customer_retention"
    ISSUE_COMPLEXITY = "issue_complexity"

class TimeInterval(Enum):
    """Time interval for analytics"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    
    # Context information
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    conversation_id: Optional[str] = None
    category: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    report_id: str
    title: str
    time_period: Tuple[datetime, datetime]
    generated_at: datetime
    
    # Core metrics
    summary_metrics: Dict[str, float] = field(default_factory=dict)
    detailed_metrics: Dict[str, List[PerformanceMetric]] = field(default_factory=dict)
    
    # Analytics insights
    trends: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    
    # Visualizations
    charts: Dict[str, Any] = field(default_factory=dict)
    
    # Comparisons
    period_comparison: Optional[Dict[str, float]] = None
    benchmark_comparison: Optional[Dict[str, float]] = None

class SupportAnalytics:
    """Ultra-advanced support performance analytics system"""
    
    def __init__(self, redis_client: aioredis.Redis, db_session: AsyncSession):
        self.redis_client = redis_client
        self.db_session = db_session
        
        # In-memory metric storage for real-time analytics
        self.real_time_metrics: Dict[MetricType, deque] = {
            metric_type: deque(maxlen=10000) for metric_type in MetricType
        }
        
        # Aggregated statistics cache
        self.aggregated_stats: Dict[str, Any] = {}
        
        # Performance benchmarks
        self.benchmarks = {
            MetricType.RESPONSE_TIME: {"excellent": 60, "good": 180, "acceptable": 300},
            MetricType.RESOLUTION_TIME: {"excellent": 600, "good": 1800, "acceptable": 3600},
            MetricType.SATISFACTION_RATING: {"excellent": 4.5, "good": 4.0, "acceptable": 3.5},
            MetricType.SUCCESS_RATE: {"excellent": 0.95, "good": 0.85, "acceptable": 0.75},
            MetricType.ESCALATION_RATE: {"excellent": 0.05, "good": 0.15, "acceptable": 0.25}
        }
        
        # Start real-time analytics processing
        asyncio.create_task(self._start_real_time_processing())
    
    async def record_metric(self, metric: PerformanceMetric):
        """Record a new performance metric"""



        try:
            # Add to real-time storage
            self.real_time_metrics[metric.metric_type].append(metric)
            
            # Store in Redis for persistence
            await self._store_metric_in_redis(metric)
            
            # Update aggregated statistics
            await self._update_aggregated_stats(metric)
            
        except Exception as e:
            logger.error(f"Failed to record metric: {str(e)}")
    
    async def get_real_time_metrics(
        self,
        metric_types: List[MetricType],
        time_window: int = 3600  # Last hour by default
    ) -> Dict[MetricType, List[PerformanceMetric]]:
        """Get real-time metrics for specified types and time window"""
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(seconds=time_window)
        
        result = {}
        
        for metric_type in metric_types:
            if metric_type in self.real_time_metrics:
                # Filter metrics within time window
                recent_metrics = [
                    metric for metric in self.real_time_metrics[metric_type]
                    if metric.timestamp >= cutoff_time
                ]
                result[metric_type] = recent_metrics
        
        return result
    
    async def generate_performance_report(
        self,
        start_time: datetime,
        end_time: datetime,
        include_trends: bool = True,
        include_recommendations: bool = True,
        include_visualizations: bool = True
    ) -> AnalyticsReport:
        """Generate comprehensive performance report"""



        try:
            report_id = f"perf_report_{int(datetime.now().timestamp())}"
            
            # Initialize report
            report = AnalyticsReport(
                report_id=report_id,
                title=f"Support Performance Report ({start_time.date()} to {end_time.date()})",
                time_period=(start_time, end_time),
                generated_at=datetime.now(timezone.utc)
            )
            
            # Collect metrics for the period
            period_metrics = await self._collect_period_metrics(start_time, end_time)
            report.detailed_metrics = period_metrics
            
            # Calculate summary metrics
            report.summary_metrics = await self._calculate_summary_metrics(period_metrics)
            
            # Trend analysis
            if include_trends:
                report.trends = await self._analyze_trends(period_metrics, start_time, end_time)
            
            # Generate recommendations
            if include_recommendations:
                report.recommendations = await self._generate_recommendations(
                    report.summary_metrics, report.trends
                )
            
            # Detect anomalies
            report.anomalies = await self._detect_anomalies(period_metrics)
            
            # Create visualizations
            if include_visualizations:
                report.charts = await self._create_visualizations(period_metrics)
            
            # Period comparison (with previous period)
            previous_start = start_time - (end_time - start_time)
            previous_end = start_time
            previous_metrics = await self._collect_period_metrics(previous_start, previous_end)
            previous_summary = await self._calculate_summary_metrics(previous_metrics)
            
            report.period_comparison = self._compare_metrics(
                report.summary_metrics, previous_summary
            )
            
            # Benchmark comparison
            report.benchmark_comparison = self._compare_with_benchmarks(
                report.summary_metrics
            )
            
            # Cache the report
            await self._cache_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {str(e)}")
            raise
    
    async def get_agent_performance_analysis(
        self,
        agent_id: str,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Get detailed performance analysis for specific agent"""



        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - time_period
            
            # Collect agent-specific metrics
            agent_metrics = await self._collect_agent_metrics(agent_id, start_time, end_time)
            
            analysis = {
                "agent_id": agent_id,
                "analysis_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "total_cases_handled": len(set([
                    m.conversation_id for metrics in agent_metrics.values() 
                    for m in metrics if m.conversation_id
                ])),
                "performance_metrics": {},
                "trends": {},
                "strengths": [],
                "improvement_areas": [],
                "ranking": {}
            }
            
            # Calculate key performance indicators
            for metric_type, metrics in agent_metrics.items():
                if not metrics:
                    continue
                
                values = [m.value for m in metrics]
                
                analysis["performance_metrics"][metric_type.value] = {
                    "average": statistics.mean(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
                
                # Compare with benchmarks
                benchmark = self.benchmarks.get(metric_type)
                if benchmark:
                    avg_value = statistics.mean(values)
                    if metric_type in [MetricType.RESPONSE_TIME, MetricType.RESOLUTION_TIME, MetricType.ESCALATION_RATE]:
                        # Lower is better
                        if avg_value <= benchmark["excellent"]:
                            performance_level = "excellent"
                        elif avg_value <= benchmark["good"]:
                            performance_level = "good"
                        elif avg_value <= benchmark["acceptable"]:
                            performance_level = "acceptable"
                        else:
                            performance_level = "needs_improvement"
                    else:
                        # Higher is better
                        if avg_value >= benchmark["excellent"]:
                            performance_level = "excellent"
                        elif avg_value >= benchmark["good"]:
                            performance_level = "good"
                        elif avg_value >= benchmark["acceptable"]:
                            performance_level = "acceptable"
                        else:
                            performance_level = "needs_improvement"
                    
                    analysis["performance_metrics"][metric_type.value]["benchmark_comparison"] = performance_level
                
                # Trend analysis
                if len(values) >= 5:
                    # Calculate trend (simple linear regression)
                    x = list(range(len(values)))
                    slope = np.polyfit(x, values, 1)[0]
                    analysis["trends"][metric_type.value] = {
                        "direction": "improving" if (
                            (metric_type in [MetricType.RESPONSE_TIME, MetricType.RESOLUTION_TIME, MetricType.ESCALATION_RATE] and slope < 0) or
                            (metric_type not in [MetricType.RESPONSE_TIME, MetricType.RESOLUTION_TIME, MetricType.ESCALATION_RATE] and slope > 0)
                        ) else "declining",
                        "slope": slope,
                        "confidence": "high" if abs(slope) > statistics.stdev(values) / 10 else "low"
                    }
            
            # Identify strengths and improvement areas
            analysis["strengths"], analysis["improvement_areas"] = await self._identify_strengths_and_improvements(
                analysis["performance_metrics"]
            )
            
            # Agent ranking compared to team
            analysis["ranking"] = await self._calculate_agent_ranking(agent_id, analysis["performance_metrics"])
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze agent performance for {agent_id}: {str(e)}")
            return {}
    
    async def get_knowledge_base_analytics(self) -> Dict[str, Any]:
        """Get analytics on knowledge base effectiveness"""



        try:
            # Get knowledge base metrics from last 30 days
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=30)
            
            kb_metrics = await self._collect_knowledge_base_metrics(start_time, end_time)
            
            analytics = {
                "analysis_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "usage_statistics": {
                    "total_searches": len([m for m in kb_metrics if m.metadata.get("action") == "search"]),
                    "total_article_views": len([m for m in kb_metrics if m.metadata.get("action") == "view"]),
                    "unique_users": len(set([m.user_id for m in kb_metrics if m.user_id])),
                    "average_search_results": statistics.mean([
                        m.metadata.get("result_count", 0) for m in kb_metrics 
                        if m.metadata.get("action") == "search"
                    ]) if any(m.metadata.get("action") == "search" for m in kb_metrics) else 0
                },
                "effectiveness_metrics": {},
                "popular_articles": [],
                "search_patterns": {},
                "gap_analysis": []
            }
            
            # Calculate effectiveness metrics
            helpful_feedback = [m for m in kb_metrics if m.metadata.get("helpful") is True]
            not_helpful_feedback = [m for m in kb_metrics if m.metadata.get("helpful") is False]
            
            total_feedback = len(helpful_feedback) + len(not_helpful_feedback)
            if total_feedback > 0:
                analytics["effectiveness_metrics"]["helpfulness_rate"] = len(helpful_feedback) / total_feedback
                analytics["effectiveness_metrics"]["total_feedback_count"] = total_feedback
            
            # Identify popular articles
            article_views = defaultdict(int)
            for metric in kb_metrics:
                if metric.metadata.get("action") == "view" and metric.metadata.get("article_id"):
                    article_views[metric.metadata["article_id"]] += 1
            
            analytics["popular_articles"] = sorted(
                article_views.items(), key=lambda x: x[1], reverse=True
            )[:10]
            
            # Analyze search patterns
            search_queries = [
                m.metadata.get("query", "").lower() for m in kb_metrics 
                if m.metadata.get("action") == "search" and m.metadata.get("query")
            ]
            
            # Count query keywords
            query_words = defaultdict(int)
            for query in search_queries:
                words = query.split()
                for word in words:
                    if len(word) > 3:  # Ignore short words
                        query_words[word] += 1
            
            analytics["search_patterns"]["top_keywords"] = sorted(
                query_words.items(), key=lambda x: x[1], reverse=True
            )[:20]
            
            # Identify knowledge gaps (searches with no results or low satisfaction)
            no_result_searches = [
                m.metadata.get("query") for m in kb_metrics
                if m.metadata.get("action") == "search" and m.metadata.get("result_count", 0) == 0
            ]
            
            low_satisfaction_searches = [
                m.metadata.get("query") for m in kb_metrics
                if (m.metadata.get("action") == "search" and 
                    m.metadata.get("user_satisfaction", 5) < 3)
            ]
            
            all_gap_queries = no_result_searches + low_satisfaction_searches
            gap_query_counts = defaultdict(int)
            for query in all_gap_queries:
                if query:
                    gap_query_counts[query] += 1
            
            analytics["gap_analysis"] = sorted(
                gap_query_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get knowledge base analytics: {str(e)}")
            return {}
    
    async def get_customer_satisfaction_insights(
        self,
        time_period: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """Get customer satisfaction insights and trends"""



        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - time_period
            
            # Collect satisfaction metrics
            satisfaction_metrics = await self._collect_period_metrics(start_time, end_time)
            satisfaction_data = satisfaction_metrics.get(MetricType.SATISFACTION_RATING, [])
            
            if not satisfaction_data:
                return {"error": "No satisfaction data available for the specified period"}
            
            ratings = [m.value for m in satisfaction_data]
            
            insights = {
                "analysis_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "overall_metrics": {
                    "average_rating": statistics.mean(ratings),
                    "median_rating": statistics.median(ratings),
                    "total_responses": len(ratings),
                    "rating_distribution": {
                        "5_star": len([r for r in ratings if r >= 4.5]),
                        "4_star": len([r for r in ratings if 3.5 <= r < 4.5]),
                        "3_star": len([r for r in ratings if 2.5 <= r < 3.5]),
                        "2_star": len([r for r in ratings if 1.5 <= r < 2.5]),
                        "1_star": len([r for r in ratings if r < 1.5])
                    }
                },
                "trends": {},
                "category_breakdown": {},
                "improvement_opportunities": []
            }
            
            # Calculate Net Promoter Score (NPS) equivalent
            promoters = len([r for r in ratings if r >= 4.5])
            detractors = len([r for r in ratings if r < 3.5])
            insights["overall_metrics"]["nps_equivalent"] = (promoters - detractors) / len(ratings) * 100
            
            # Trend analysis
            if len(ratings) >= 7:
                # Group by day and calculate daily averages
                daily_ratings = defaultdict(list)
                for metric in satisfaction_data:
                    day = metric.timestamp.date()
                    daily_ratings[day].append(metric.value)
                
                daily_averages = {
                    day: statistics.mean(ratings) 
                    for day, ratings in daily_ratings.items()
                }
                
                # Calculate trend
                days = sorted(daily_averages.keys())
                avg_values = [daily_averages[day] for day in days]
                
                if len(avg_values) >= 3:
                    trend_slope = np.polyfit(range(len(avg_values)), avg_values, 1)[0]
                    insights["trends"]["daily_trend"] = {
                        "direction": "improving" if trend_slope > 0 else "declining",
                        "slope": trend_slope,
                        "daily_averages": {day.isoformat(): avg for day, avg in daily_averages.items()}
                    }
            
            # Category breakdown
            category_ratings = defaultdict(list)
            for metric in satisfaction_data:
                category = metric.category or "general"
                category_ratings[category].append(metric.value)
            
            for category, cat_ratings in category_ratings.items():
                insights["category_breakdown"][category] = {
                    "average_rating": statistics.mean(cat_ratings),
                    "total_responses": len(cat_ratings),
                    "performance_vs_overall": statistics.mean(cat_ratings) - statistics.mean(ratings)
                }
            
            # Identify improvement opportunities
            low_rated_categories = [
                category for category, data in insights["category_breakdown"].items()
                if data["average_rating"] < insights["overall_metrics"]["average_rating"] - 0.2
            ]
            
            if low_rated_categories:
                insights["improvement_opportunities"].extend([
                    f"Focus on improving {category} support quality"
                    for category in low_rated_categories
                ])
            
            if insights["overall_metrics"]["average_rating"] < 4.0:
                insights["improvement_opportunities"].append("Overall satisfaction below target (4.0+)")
            
            recent_trend = insights.get("trends", {}).get("daily_trend", {})
            if recent_trend.get("direction") == "declining":
                insights["improvement_opportunities"].append("Address declining satisfaction trend")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get customer satisfaction insights: {str(e)}")
            return {}
    
    async def _collect_period_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[MetricType, List[PerformanceMetric]]:
        """Collect all metrics for a specific time period"""
        metrics = {metric_type: [] for metric_type in MetricType}
        
        try:
            # Check real-time storage first
            for metric_type, real_time_metrics in self.real_time_metrics.items():
                for metric in real_time_metrics:
                    if start_time <= metric.timestamp <= end_time:
                        metrics[metric_type].append(metric)
            
            # Load additional metrics from Redis if needed
            redis_metrics = await self._load_metrics_from_redis(start_time, end_time)
            for metric_type, redis_metric_list in redis_metrics.items():
                metrics[metric_type].extend(redis_metric_list)
            
            # Remove duplicates and sort by timestamp
            for metric_type in metrics:
                # Remove duplicates based on timestamp and metadata
                seen = set()
                unique_metrics = []
                for metric in metrics[metric_type]:
                    key = (metric.timestamp, metric.user_id, metric.conversation_id)
                    if key not in seen:
                        seen.add(key)
                        unique_metrics.append(metric)
                
                metrics[metric_type] = sorted(unique_metrics, key=lambda x: x.timestamp)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect period metrics: {str(e)}")
            return metrics
    
    async def _calculate_summary_metrics(
        self,
        period_metrics: Dict[MetricType, List[PerformanceMetric]]
    ) -> Dict[str, float]:
        """Calculate summary metrics from period data"""
        summary = {}
        
        for metric_type, metrics in period_metrics.items():
            if not metrics:
                continue
            
            values = [m.value for m in metrics]
            metric_name = metric_type.value
            
            summary[f"{metric_name}_avg"] = statistics.mean(values)
            summary[f"{metric_name}_median"] = statistics.median(values)
            summary[f"{metric_name}_min"] = min(values)
            summary[f"{metric_name}_max"] = max(values)
            summary[f"{metric_name}_count"] = len(values)
            
            if len(values) > 1:
                summary[f"{metric_name}_std"] = statistics.stdev(values)
            
            # Percentiles
            summary[f"{metric_name}_p95"] = np.percentile(values, 95)
            summary[f"{metric_name}_p90"] = np.percentile(values, 90)
        
        return summary
    
    async def _analyze_trends(
        self,
        period_metrics: Dict[MetricType, List[PerformanceMetric]],
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Analyze trends in the metrics"""
        trends = {}
        
        for metric_type, metrics in period_metrics.items():
            if len(metrics) < 5:  # Need minimum data points for trend analysis
                continue
            
            # Time series analysis
            timestamps = [m.timestamp for m in metrics]
            values = [m.value for m in metrics]
            
            # Convert timestamps to numerical values for regression
            time_numeric = [(t - start_time).total_seconds() for t in timestamps]
            
            # Linear regression for trend
            if len(time_numeric) >= 2:
                slope, intercept = np.polyfit(time_numeric, values, 1)
                
                # Determine trend direction and strength
                total_time = (end_time - start_time).total_seconds()
                trend_change = slope * total_time
                avg_value = statistics.mean(values)
                trend_percentage = (trend_change / avg_value) * 100 if avg_value != 0 else 0
                
                trends[metric_type.value] = {
                    "slope": slope,
                    "trend_percentage": trend_percentage,
                    "direction": "increasing" if slope > 0 else "decreasing",
                    "strength": self._calculate_trend_strength(slope, values),
                    "r_squared": self._calculate_r_squared(time_numeric, values, slope, intercept)
                }
        
        return trends
    
    def _calculate_trend_strength(self, slope: float, values: List[float]) -> str:
        """Calculate trend strength based on slope and variance"""
        if len(values) < 2:
            return "insufficient_data"
        
        std_dev = statistics.stdev(values)
        avg_value = statistics.mean(values)
        
        # Normalize slope by average value and standard deviation
        normalized_slope = abs(slope) / (avg_value + std_dev)
        
        if normalized_slope > 0.1:
            return "strong"
        elif normalized_slope > 0.05:
            return "moderate"
        elif normalized_slope > 0.01:
            return "weak"
        else:
            return "negligible"
    
    def _calculate_r_squared(
        self, 
        x: List[float], 
        y: List[float], 
        slope: float, 
        intercept: float
    ) -> float:
        """Calculate R-squared for linear regression"""
        y_mean = statistics.mean(y)
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
        
        return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    async def _generate_recommendations(
        self,
        summary_metrics: Dict[str, float],
        trends: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on metrics and trends"""
        recommendations = []
        
        # Response time recommendations
        avg_response_time = summary_metrics.get("response_time_avg", 0)
        if avg_response_time > 300:  # 5 minutes
            recommendations.append(
                "Consider increasing agent staffing during peak hours to reduce response times"
            )
        
        response_trend = trends.get("response_time", {})
        if response_trend.get("direction") == "increasing" and response_trend.get("strength") in ["moderate", "strong"]:
            recommendations.append(
                "Response times are trending upward - investigate potential bottlenecks"
            )
        
        # Satisfaction recommendations
        avg_satisfaction = summary_metrics.get("satisfaction_rating_avg", 0)
        if avg_satisfaction < 4.0:
            recommendations.append(
                "Customer satisfaction below target - consider agent training or knowledge base improvements"
            )
        
        satisfaction_trend = trends.get("satisfaction_rating", {})
        if satisfaction_trend.get("direction") == "decreasing":
            recommendations.append(
                "Declining satisfaction trend detected - urgent review of support quality needed"
            )
        
        # Escalation rate recommendations
        escalation_rate = summary_metrics.get("escalation_rate_avg", 0)
        if escalation_rate > 0.2:  # 20%
            recommendations.append(
                "High escalation rate suggests AI agent may need additional training or knowledge base updates"
            )
        
        # Resolution time recommendations
        avg_resolution_time = summary_metrics.get("resolution_time_avg", 0)
        if avg_resolution_time > 3600:  # 1 hour
            recommendations.append(
                "Consider streamlining support processes to reduce resolution times"
            )
        
        # Success rate recommendations
        success_rate = summary_metrics.get("success_rate_avg", 0)
        if success_rate < 0.8:  # 80%
            recommendations.append(
                "Low success rate indicates need for improved troubleshooting resources"
            )
        
        return recommendations
    
    async def _detect_anomalies(
        self,
        period_metrics: Dict[MetricType, List[PerformanceMetric]]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in the metrics"""
        anomalies = []
        
        for metric_type, metrics in period_metrics.items():
            if len(metrics) < 10:  # Need sufficient data for anomaly detection
                continue
            
            values = [m.value for m in metrics]
            
            # Statistical anomaly detection using z-score
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0
            
            if std_val > 0:
                for metric in metrics:
                    z_score = abs((metric.value - mean_val) / std_val)
                    
                    if z_score > 3:  # 3 standard deviations
                        anomalies.append({
                            "metric_type": metric_type.value,
                            "timestamp": metric.timestamp.isoformat(),
                            "value": metric.value,
                            "z_score": z_score,
                            "severity": "high" if z_score > 4 else "moderate",
                            "description": f"Unusual {metric_type.value} value detected"
                        })
        
        return sorted(anomalies, key=lambda x: x["z_score"], reverse=True)[:10]  # Top 10
    
    async def _create_visualizations(
        self,
        period_metrics: Dict[MetricType, List[PerformanceMetric]]
    ) -> Dict[str, Any]:
        """Create visualization data for the metrics"""
        charts = {}
        
        try:
            # Time series charts for key metrics
            for metric_type in [MetricType.RESPONSE_TIME, MetricType.SATISFACTION_RATING, MetricType.ESCALATION_RATE]:
                if metric_type not in period_metrics or not period_metrics[metric_type]:
                    continue
                
                metrics = period_metrics[metric_type]
                
                # Group by hour for better visualization
                hourly_data = defaultdict(list)
                for metric in metrics:
                    hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
                    hourly_data[hour_key].append(metric.value)
                
                # Calculate hourly averages
                chart_data = []
                for hour, values in sorted(hourly_data.items()):
                    chart_data.append({
                        "timestamp": hour.isoformat(),
                        "value": statistics.mean(values),
                        "count": len(values)
                    })
                
                charts[f"{metric_type.value}_timeline"] = chart_data
            
            # Distribution charts
            for metric_type in [MetricType.SATISFACTION_RATING, MetricType.RESPONSE_TIME]:
                if metric_type not in period_metrics or not period_metrics[metric_type]:
                    continue
                
                values = [m.value for m in period_metrics[metric_type]]
                
                # Create histogram data
                hist_data, bin_edges = np.histogram(values, bins=20)
                
                histogram_data = []
                for i in range(len(hist_data)):
                    histogram_data.append({
                        "bin_start": bin_edges[i],
                        "bin_end": bin_edges[i + 1],
                        "count": int(hist_data[i])
                    })
                
                charts[f"{metric_type.value}_distribution"] = histogram_data
            
            return charts
            
        except Exception as e:
            logger.error(f"Failed to create visualizations: {str(e)}")
            return {}
    
    def _compare_metrics(
        self,
        current_metrics: Dict[str, float],
        previous_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """Compare current metrics with previous period"""
        comparison = {}
        
        for metric_name, current_value in current_metrics.items():
            if metric_name in previous_metrics:
                previous_value = previous_metrics[metric_name]
                
                if previous_value != 0:
                    change_percentage = ((current_value - previous_value) / previous_value) * 100
                    comparison[f"{metric_name}_change_pct"] = change_percentage
                
                comparison[f"{metric_name}_change_abs"] = current_value - previous_value
        
        return comparison
    
    def _compare_with_benchmarks(
        self,
        metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """Compare metrics with established benchmarks"""
        comparison = {}
        
        for metric_type, benchmarks in self.benchmarks.items():
            metric_key = f"{metric_type.value}_avg"
            
            if metric_key in metrics:
                current_value = metrics[metric_key]
                
                # Calculate how the metric compares to each benchmark level
                for level, benchmark_value in benchmarks.items():
                    if metric_type in [MetricType.RESPONSE_TIME, MetricType.RESOLUTION_TIME, MetricType.ESCALATION_RATE]:
                        # Lower is better
                        performance_ratio = benchmark_value / current_value if current_value > 0 else float('inf')
                    else:
                        # Higher is better
                        performance_ratio = current_value / benchmark_value if benchmark_value > 0 else 0
                    
                    comparison[f"{metric_type.value}_{level}_ratio"] = performance_ratio
        
        return comparison
    
    async def _collect_agent_metrics(
        self,
        agent_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[MetricType, List[PerformanceMetric]]:
        """Collect metrics specific to an agent"""
        agent_metrics = {metric_type: [] for metric_type in MetricType}
        
        # Filter metrics by agent_id
        all_metrics = await self._collect_period_metrics(start_time, end_time)
        
        for metric_type, metrics in all_metrics.items():
            agent_specific = [m for m in metrics if m.agent_id == agent_id]
            agent_metrics[metric_type] = agent_specific
        
        return agent_metrics
    
    async def _collect_knowledge_base_metrics(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[PerformanceMetric]:
        """Collect knowledge base related metrics"""
        # This would collect metrics related to knowledge base usage
        # For now, return empty list - in real implementation would query actual data
        return []
    
    async def _identify_strengths_and_improvements(
        self,
        performance_metrics: Dict[str, Dict[str, Any]]
    ) -> Tuple[List[str], List[str]]:
        """Identify agent strengths and improvement areas"""
        strengths = []
        improvements = []
        
        for metric_name, data in performance_metrics.items():
            benchmark_comparison = data.get("benchmark_comparison")
            
            if benchmark_comparison == "excellent":
                strengths.append(f"Excellent {metric_name.replace('_', ' ')}")
            elif benchmark_comparison == "needs_improvement":
                improvements.append(f"Improve {metric_name.replace('_', ' ')}")
        
        return strengths, improvements
    
    async def _calculate_agent_ranking(
        self,
        agent_id: str,
        agent_metrics: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate agent ranking compared to team"""
        # This would compare against all agents in the system
        # For now, return placeholder data
        return {
            "overall_ranking": "top_25_percent",
            "total_agents": 10,
            "percentile": 75
        }
    
    async def _store_metric_in_redis(self, metric: PerformanceMetric):
        """Store metric in Redis for persistence"""



        try:
            metric_data = {
                "metric_type": metric.metric_type.value,
                "value": metric.value,
                "timestamp": metric.timestamp.isoformat(),
                "user_id": metric.user_id,
                "agent_id": metric.agent_id,
                "conversation_id": metric.conversation_id,
                "category": metric.category,
                "metadata": metric.metadata,
                "tags": metric.tags
            }
            
            # Store with day-based key for efficient retrieval
            day_key = metric.timestamp.strftime("%Y-%m-%d")
            redis_key = f"metrics:{day_key}:{metric.metric_type.value}"
            
            await self.redis_client.lpush(redis_key, json.dumps(metric_data, default=str))
            await self.redis_client.expire(redis_key, 86400 * 90)  # Keep for 90 days
            
        except Exception as e:
            logger.error(f"Failed to store metric in Redis: {str(e)}")
    
    async def _load_metrics_from_redis(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[MetricType, List[PerformanceMetric]]:
        """Load metrics from Redis for specified time period"""
        metrics = {metric_type: [] for metric_type in MetricType}
        
        try:
            # Generate day keys for the period
            current_date = start_time.date()
            end_date = end_time.date()
            
            while current_date <= end_date:
                day_key = current_date.strftime("%Y-%m-%d")
                
                for metric_type in MetricType:
                    redis_key = f"metrics:{day_key}:{metric_type.value}"
                    
                    # Get all metrics for this day and type
                    stored_metrics = await self.redis_client.lrange(redis_key, 0, -1)
                    
                    for stored_metric in stored_metrics:
                        try:
                            metric_data = json.loads(stored_metric)
                            
                            metric_time = datetime.fromisoformat(metric_data["timestamp"])
                            
                            # Filter by exact time range
                            if start_time <= metric_time <= end_time:
                                metric = PerformanceMetric(
                                    metric_type=MetricType(metric_data["metric_type"]),
                                    value=metric_data["value"],
                                    timestamp=metric_time,
                                    user_id=metric_data.get("user_id"),
                                    agent_id=metric_data.get("agent_id"),
                                    conversation_id=metric_data.get("conversation_id"),
                                    category=metric_data.get("category"),
                                    metadata=metric_data.get("metadata", {}),
                                    tags=metric_data.get("tags", [])
                                )
                                
                                metrics[metric_type].append(metric)
                                
                        except Exception as e:
                            logger.error(f"Failed to parse stored metric: {str(e)}")
                            continue
                
                current_date += timedelta(days=1)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to load metrics from Redis: {str(e)}")
            return metrics
    
    async def _update_aggregated_stats(self, metric: PerformanceMetric):
        """Update aggregated statistics with new metric"""



        try:
            metric_type = metric.metric_type.value
            
            # Update hourly aggregations
            hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0).isoformat()
            stats_key = f"hourly_stats:{metric_type}:{hour_key}"
            
            # Get current stats
            current_stats = await self.redis_client.get(stats_key)
            if current_stats:
                stats = json.loads(current_stats)
            else:
                stats = {"count": 0, "sum": 0, "min": float('inf'), "max": float('-inf')}
            
            # Update stats
            stats["count"] += 1
            stats["sum"] += metric.value
            stats["min"] = min(stats["min"], metric.value)
            stats["max"] = max(stats["max"], metric.value)
            stats["avg"] = stats["sum"] / stats["count"]
            
            # Store updated stats
            await self.redis_client.setex(stats_key, 86400 * 7, json.dumps(stats))  # Keep for 7 days
            
        except Exception as e:
            logger.error(f"Failed to update aggregated stats: {str(e)}")
    
    async def _cache_report(self, report: AnalyticsReport):
        """Cache the generated report"""



        try:
            report_data = {
                "report_id": report.report_id,
                "title": report.title,
                "time_period": [report.time_period[0].isoformat(), report.time_period[1].isoformat()],
                "generated_at": report.generated_at.isoformat(),
                "summary_metrics": report.summary_metrics,
                "trends": report.trends,
                "recommendations": report.recommendations,
                "anomalies": report.anomalies,
                "charts": report.charts,
                "period_comparison": report.period_comparison,
                "benchmark_comparison": report.benchmark_comparison
            }
            
            await self.redis_client.setex(
                f"analytics_report:{report.report_id}",
                86400 * 7,  # Keep for 7 days
                json.dumps(report_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to cache report: {str(e)}")
    
    async def _start_real_time_processing(self):
        """Start background task for real-time metric processing"""
        while True:
            try:
                # Process any pending aggregations
                await asyncio.sleep(60)  # Process every minute
                
                # Could add more sophisticated real-time processing here
                # such as alert generation, automatic scaling decisions, etc.
                
            except Exception as e:
                logger.error(f"Real-time processing error: {str(e)}")
                await asyncio.sleep(10)
