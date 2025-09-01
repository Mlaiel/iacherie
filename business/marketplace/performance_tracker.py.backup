"""Performance Tracker - Advanced Performance Analytics System
===========================================================

Comprehensive performance tracking and analytics for creator content
with real-time metrics and predictive insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team Specialists: Lead AI Dev, Backend Senior, ML Engineer, DBA, Security Expert, 
                         Microservices Architect, Audio Processing Expert, DevOps Engineer, 
                         AI Prompt Engineer

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code and concept are proprietary to Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Legal action will be pursued against any infringement.
"""
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import logging
import statistics

logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    """Types of performance metrics tracked"""
    VIEWS = "views"
    ENGAGEMENT_RATE = "engagement_rate"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"
    DOWNLOADS = "downloads"
    REVENUE = "revenue"
    CONVERSION_RATE = "conversion_rate"
    RETENTION_RATE = "retention_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICK_THROUGH_RATE = "click_through_rate"
    COMPLETION_RATE = "completion_rate"
    SUBSCRIBER_GROWTH = "subscriber_growth"

class TimeFrame(Enum):
    """Performance tracking time frames"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class TrendDirection(Enum):
    """Trend directions"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class PerformanceDataPoint:
    """Individual performance data point"""
    timestamp: datetime
    metric: PerformanceMetric
    value: float
    platform: str
    content_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    report_id: str
    creator_id: str
    time_frame: TimeFrame
    start_date: datetime
    end_date: datetime
    metrics_summary: Dict[PerformanceMetric, Dict[str, float]]
    trend_analysis: Dict[PerformanceMetric, TrendDirection]
    platform_breakdown: Dict[str, Dict[PerformanceMetric, float]]
    top_performing_content: List[Dict[str, Any]]
    performance_insights: List[str]
    recommendations: List[str]
    predictions: Dict[str, float]
    benchmark_comparisons: Dict[str, float]
    growth_rates: Dict[PerformanceMetric, float]
    anomaly_detections: List[Dict[str, Any]]
    generated_at: datetime = field(default_factory=datetime.utcnow)
    report_version: str = "1.0"

class PerformanceTracker:
    """
    Advanced performance tracking system with real-time analytics,
    trend analysis, and predictive insights for creator content.
    """
    
    def __init__(self):
        self.metric_weights = {
            PerformanceMetric.VIEWS: 0.20,
            PerformanceMetric.ENGAGEMENT_RATE: 0.25,
            PerformanceMetric.REVENUE: 0.20,
            PerformanceMetric.CONVERSION_RATE: 0.15,
            PerformanceMetric.RETENTION_RATE: 0.10,
            PerformanceMetric.SUBSCRIBER_GROWTH: 0.10
        }
        
        self.benchmark_data = {
            'industry_averages': {
                PerformanceMetric.ENGAGEMENT_RATE: 0.06,
                PerformanceMetric.CONVERSION_RATE: 0.03,
                PerformanceMetric.COMPLETION_RATE: 0.45,
                PerformanceMetric.CLICK_THROUGH_RATE: 0.02
            },
            'top_performer_thresholds': {
                PerformanceMetric.ENGAGEMENT_RATE: 0.12,
                PerformanceMetric.CONVERSION_RATE: 0.08,
                PerformanceMetric.COMPLETION_RATE: 0.70,
                PerformanceMetric.CLICK_THROUGH_RATE: 0.05
            }
        }
        
        self.trend_detection_window = 30  # days
        self.anomaly_threshold = 2.0  # standard deviations
    
    async def get_creator_performance(self, creator_id: str, time_frame: TimeFrame = TimeFrame.MONTHLY) -> PerformanceReport:
        """Get comprehensive performance report for creator"""
        try:
            # Determine time range
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(end_date, time_frame)
            
            # Collect performance data
            performance_data = await self._collect_performance_data(creator_id, start_date, end_date)
            
            # Calculate metrics summary
            metrics_summary = await self._calculate_metrics_summary(performance_data)
            
            # Analyze trends
            trend_analysis = await self._analyze_trends(performance_data, time_frame)
            
            # Platform breakdown
            platform_breakdown = await self._generate_platform_breakdown(performance_data)
            
            # Identify top performing content
            top_content = await self._identify_top_content(creator_id, performance_data)
            
            # Generate insights and recommendations
            insights = await self._generate_performance_insights(metrics_summary, trend_analysis)
            recommendations = await self._generate_recommendations(metrics_summary, trend_analysis, creator_id)
            
            # Predictive analytics
            predictions = await self._generate_predictions(performance_data, time_frame)
            
            # Benchmark comparisons
            benchmark_comparisons = await self._compare_with_benchmarks(metrics_summary)
            
            # Calculate growth rates
            growth_rates = await self._calculate_growth_rates(performance_data, time_frame)
            
            # Detect anomalies
            anomaly_detections = await self._detect_anomalies(performance_data)
            
            report = PerformanceReport(
                report_id=str(uuid.uuid4()),
                creator_id=creator_id,
                time_frame=time_frame,
                start_date=start_date,
                end_date=end_date,
                metrics_summary=metrics_summary,
                trend_analysis=trend_analysis,
                platform_breakdown=platform_breakdown,
                top_performing_content=top_content,
                performance_insights=insights,
                recommendations=recommendations,
                predictions=predictions,
                benchmark_comparisons=benchmark_comparisons,
                growth_rates=growth_rates,
                anomaly_detections=anomaly_detections
            )
            
            logger.info(f"Performance report generated for creator {creator_id}")
            return report
            
        except Exception as e:
            logger.error(f"Performance tracking failed: {str(e)}")
            raise
    
    def _calculate_start_date(self, end_date: datetime, time_frame: TimeFrame) -> datetime:
        """Calculate start date based on time frame"""
        if time_frame == TimeFrame.DAILY:
            return end_date - timedelta(days=1)
        elif time_frame == TimeFrame.WEEKLY:
            return end_date - timedelta(weeks=1)
        elif time_frame == TimeFrame.MONTHLY:
            return end_date - timedelta(days=30)
        elif time_frame == TimeFrame.QUARTERLY:
            return end_date - timedelta(days=90)
        elif time_frame == TimeFrame.YEARLY:
            return end_date - timedelta(days=365)
        else:
            return end_date - timedelta(days=30)  # Default to monthly
    
    async def _collect_performance_data(self, creator_id: str, start_date: datetime, end_date: datetime) -> List[PerformanceDataPoint]:
        """Collect performance data for the specified period"""
        # This would typically query databases and external APIs
        # For now, generating realistic sample data
        
        data_points = []
        current_date = start_date
        
        while current_date <= end_date:
            # Generate sample data points for each metric
            for metric in PerformanceMetric:
                for platform in ['youtube', 'instagram', 'spotify', 'tiktok']:
                    value = self._generate_sample_metric_value(metric, platform)
                    
                    data_point = PerformanceDataPoint(
                        timestamp=current_date,
                        metric=metric,
                        value=value,
                        platform=platform,
                        content_id=f"content_{uuid.uuid4().hex[:8]}",
                        metadata={'sample_data': True}
                    )
                    data_points.append(data_point)
            
            current_date += timedelta(days=1)
        
        return data_points
    
    def _generate_sample_metric_value(self, metric: PerformanceMetric, platform: str) -> float:
        """Generate realistic sample metric values"""
        base_values = {
            PerformanceMetric.VIEWS: {'youtube': 15000, 'instagram': 8000, 'spotify': 5000, 'tiktok': 25000},
            PerformanceMetric.ENGAGEMENT_RATE: {'youtube': 0.08, 'instagram': 0.12, 'spotify': 0.05, 'tiktok': 0.15},
            PerformanceMetric.SHARES: {'youtube': 150, 'instagram': 200, 'spotify': 80, 'tiktok': 500},
            PerformanceMetric.COMMENTS: {'youtube': 250, 'instagram': 180, 'spotify': 50, 'tiktok': 800},
            PerformanceMetric.LIKES: {'youtube': 1200, 'instagram': 1500, 'spotify': 300, 'tiktok': 3000},
            PerformanceMetric.REVENUE: {'youtube': 125.50, 'instagram': 85.25, 'spotify': 45.75, 'tiktok': 95.00},
            PerformanceMetric.CONVERSION_RATE: {'youtube': 0.04, 'instagram': 0.06, 'spotify': 0.02, 'tiktok': 0.08}
        }
        
        base_value = base_values.get(metric, {}).get(platform, 100.0)
        
        # Add some random variation (±20%)
        import random
        variation = random.uniform(-0.2, 0.2)
        return max(base_value * (1 + variation), 0)
    
    async def _calculate_metrics_summary(self, performance_data: List[PerformanceDataPoint]) -> Dict[PerformanceMetric, Dict[str, float]]:
        """Calculate summary statistics for each metric"""
        metrics_summary = {}
        
        for metric in PerformanceMetric:
            metric_data = [dp.value for dp in performance_data if dp.metric == metric]
            
            if metric_data:
                summary = {
                    'total': sum(metric_data),
                    'average': statistics.mean(metric_data),
                    'median': statistics.median(metric_data),
                    'max': max(metric_data),
                    'min': min(metric_data),
                    'std_dev': statistics.stdev(metric_data) if len(metric_data) > 1 else 0.0,
                    'count': len(metric_data)
                }
                
                # Calculate percentiles
                sorted_data = sorted(metric_data)
                summary['p25'] = sorted_data[len(sorted_data) // 4] if len(sorted_data) > 3 else summary['min']
                summary['p75'] = sorted_data[3 * len(sorted_data) // 4] if len(sorted_data) > 3 else summary['max']
                
                metrics_summary[metric] = summary
        
        return metrics_summary
    
    async def _analyze_trends(self, performance_data: List[PerformanceDataPoint], time_frame: TimeFrame) -> Dict[PerformanceMetric, TrendDirection]:
        """Analyze trends for each metric"""
        trend_analysis = {}
        
        for metric in PerformanceMetric:
            metric_data = [(dp.timestamp, dp.value) for dp in performance_data if dp.metric == metric]
            metric_data.sort(key=lambda x: x[0])  # Sort by timestamp
            
            if len(metric_data) < 3:
                trend_analysis[metric] = TrendDirection.STABLE
                continue
            
            # Calculate trend using linear regression approach
            values = [data[1] for data in metric_data]
            trend = self._calculate_trend_direction(values)
            trend_analysis[metric] = trend
        
        return trend_analysis
    
    def _calculate_trend_direction(self, values: List[float]) -> TrendDirection:
        """Calculate trend direction from a series of values"""
        if len(values) < 3:
            return TrendDirection.STABLE
        
        # Simple trend calculation
        first_half_avg = statistics.mean(values[:len(values)//2])
        second_half_avg = statistics.mean(values[len(values)//2:])
        
        change_pct = (second_half_avg - first_half_avg) / first_half_avg if first_half_avg > 0 else 0
        
        # Calculate volatility
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        mean_val = statistics.mean(values)
        volatility = (std_dev / mean_val) if mean_val > 0 else 0
        
        if volatility > 0.3:  # High volatility
            return TrendDirection.VOLATILE
        elif change_pct > 0.1:  # 10% increase
            return TrendDirection.INCREASING
        elif change_pct < -0.1:  # 10% decrease
            return TrendDirection.DECREASING
        else:
            return TrendDirection.STABLE
    
    async def _generate_platform_breakdown(self, performance_data: List[PerformanceDataPoint]) -> Dict[str, Dict[PerformanceMetric, float]]:
        """Generate performance breakdown by platform"""
        platform_breakdown = {}
        
        platforms = set(dp.platform for dp in performance_data)
        
        for platform in platforms:
            platform_data = {}
            
            for metric in PerformanceMetric:
                metric_values = [dp.value for dp in performance_data 
                               if dp.platform == platform and dp.metric == metric]
                
                if metric_values:
                    platform_data[metric] = {
                        'total': sum(metric_values),
                        'average': statistics.mean(metric_values),
                        'best': max(metric_values)
                    }
                else:
                    platform_data[metric] = {'total': 0, 'average': 0, 'best': 0}
            
            platform_breakdown[platform] = platform_data
        
        return platform_breakdown
    
    async def _identify_top_content(self, creator_id: str, performance_data: List[PerformanceDataPoint]) -> List[Dict[str, Any]]:
        """Identify top performing content"""
        # Group by content_id and calculate performance scores
        content_performance = {}
        
        for dp in performance_data:
            if dp.content_id:
                if dp.content_id not in content_performance:
                    content_performance[dp.content_id] = {}
                
                if dp.metric not in content_performance[dp.content_id]:
                    content_performance[dp.content_id][dp.metric] = []
                
                content_performance[dp.content_id][dp.metric].append(dp.value)
        
        # Calculate composite scores
        scored_content = []
        for content_id, metrics in content_performance.items():
            score = 0.0
            
            for metric, values in metrics.items():
                if values:
                    avg_value = statistics.mean(values)
                    weight = self.metric_weights.get(metric, 0.05)
                    
                    # Normalize values (this would use actual benchmarks)
                    normalized_value = min(avg_value / 1000, 1.0) if metric == PerformanceMetric.VIEWS else avg_value
                    score += normalized_value * weight
            
            scored_content.append({
                'content_id': content_id,
                'performance_score': score,
                'metrics': {metric.value: statistics.mean(values) for metric, values in metrics.items()}
            })
        
        # Return top 10 content pieces
        scored_content.sort(key=lambda x: x['performance_score'], reverse=True)
        return scored_content[:10]
    
    async def _generate_performance_insights(self, metrics_summary: Dict[PerformanceMetric, Dict[str, float]], trend_analysis: Dict[PerformanceMetric, TrendDirection]) -> List[str]:
        """Generate performance insights"""
        insights = []
        
        # Engagement insights
        if PerformanceMetric.ENGAGEMENT_RATE in metrics_summary:
            avg_engagement = metrics_summary[PerformanceMetric.ENGAGEMENT_RATE]['average']
            if avg_engagement > 0.10:
                insights.append("Excellent engagement rate - significantly above industry average")
            elif avg_engagement > 0.06:
                insights.append("Good engagement rate - above industry average")
            else:
                insights.append("Engagement rate below industry average - focus on content optimization")
        
        # Revenue insights
        if PerformanceMetric.REVENUE in metrics_summary:
            revenue_trend = trend_analysis.get(PerformanceMetric.REVENUE, TrendDirection.STABLE)
            if revenue_trend == TrendDirection.INCREASING:
                insights.append("Revenue is showing positive growth trend")
            elif revenue_trend == TrendDirection.DECREASING:
                insights.append("Revenue is declining - consider monetization strategy review")
        
        # View insights
        if PerformanceMetric.VIEWS in metrics_summary:
            view_trend = trend_analysis.get(PerformanceMetric.VIEWS, TrendDirection.STABLE)
            if view_trend == TrendDirection.VOLATILE:
                insights.append("View counts are highly variable - content consistency may improve stability")
        
        # Growth insights
        growing_metrics = [metric for metric, trend in trend_analysis.items() 
                          if trend == TrendDirection.INCREASING]
        if len(growing_metrics) >= 3:
            insights.append("Multiple metrics showing positive growth - strong overall performance")
        
        return insights
    
    async def _generate_recommendations(self, metrics_summary: Dict[PerformanceMetric, Dict[str, float]], trend_analysis: Dict[PerformanceMetric, TrendDirection], creator_id: str) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Engagement recommendations
        if PerformanceMetric.ENGAGEMENT_RATE in metrics_summary:
            avg_engagement = metrics_summary[PerformanceMetric.ENGAGEMENT_RATE]['average']
            if avg_engagement < 0.06:
                recommendations.append("Increase engagement by asking questions, creating interactive content, and responding to comments promptly")
        
        # Content frequency recommendations
        if PerformanceMetric.VIEWS in metrics_summary:
            view_trend = trend_analysis.get(PerformanceMetric.VIEWS, TrendDirection.STABLE)
            if view_trend == TrendDirection.DECREASING:
                recommendations.append("Consider increasing content posting frequency to maintain audience interest")
        
        # Monetization recommendations
        if PerformanceMetric.CONVERSION_RATE in metrics_summary:
            conversion_rate = metrics_summary[PerformanceMetric.CONVERSION_RATE]['average']
            if conversion_rate < 0.03:
                recommendations.append("Optimize call-to-actions and consider implementing lead magnets to improve conversion rates")
        
        # Platform diversification
        recommendations.append("Experiment with cross-platform content adaptation to maximize reach")
        
        # Quality improvement
        recommendations.append("Focus on high-quality content production to improve long-term performance metrics")
        
        return recommendations[:8]  # Top 8 recommendations
    
    async def _generate_predictions(self, performance_data: List[PerformanceDataPoint], time_frame: TimeFrame) -> Dict[str, float]:
        """Generate performance predictions using trend analysis"""
        predictions = {}
        
        for metric in [PerformanceMetric.VIEWS, PerformanceMetric.ENGAGEMENT_RATE, PerformanceMetric.REVENUE]:
            metric_data = [dp.value for dp in performance_data if dp.metric == metric]
            
            if len(metric_data) >= 7:  # Need at least a week of data
                recent_avg = statistics.mean(metric_data[-7:])  # Last 7 data points
                older_avg = statistics.mean(metric_data[-14:-7]) if len(metric_data) >= 14 else recent_avg
                
                growth_rate = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
                
                # Project forward based on growth rate
                if time_frame == TimeFrame.WEEKLY:
                    predicted_value = recent_avg * (1 + growth_rate)
                elif time_frame == TimeFrame.MONTHLY:
                    predicted_value = recent_avg * (1 + growth_rate * 4)  # 4 weeks
                else:
                    predicted_value = recent_avg * (1 + growth_rate)
                
                predictions[f"{metric.value}_next_period"] = max(predicted_value, 0)
        
        return predictions
    
    async def _compare_with_benchmarks(self, metrics_summary: Dict[PerformanceMetric, Dict[str, float]]) -> Dict[str, float]:
        """Compare performance with industry benchmarks"""
        comparisons = {}
        
        for metric, benchmark in self.benchmark_data['industry_averages'].items():
            if metric in metrics_summary:
                actual_value = metrics_summary[metric]['average']
                comparison_ratio = actual_value / benchmark if benchmark > 0 else 1.0
                comparisons[f"{metric.value}_vs_industry"] = comparison_ratio
                
                # Check against top performer threshold
                top_threshold = self.benchmark_data['top_performer_thresholds'].get(metric)
                if top_threshold:
                    top_ratio = actual_value / top_threshold if top_threshold > 0 else 1.0
                    comparisons[f"{metric.value}_vs_top_performers"] = top_ratio
        
        return comparisons
    
    async def _calculate_growth_rates(self, performance_data: List[PerformanceDataPoint], time_frame: TimeFrame) -> Dict[PerformanceMetric, float]:
        """Calculate growth rates for each metric"""
        growth_rates = {}
        
        for metric in PerformanceMetric:
            metric_data = [(dp.timestamp, dp.value) for dp in performance_data if dp.metric == metric]
            metric_data.sort(key=lambda x: x[0])
            
            if len(metric_data) >= 2:
                # Compare first and last periods
                period_size = len(metric_data) // 3  # Divide into thirds
                if period_size > 0:
                    early_period = [data[1] for data in metric_data[:period_size]]
                    late_period = [data[1] for data in metric_data[-period_size:]]
                    
                    early_avg = statistics.mean(early_period)
                    late_avg = statistics.mean(late_period)
                    
                    if early_avg > 0:
                        growth_rate = (late_avg - early_avg) / early_avg
                        growth_rates[metric] = growth_rate
        
        return growth_rates
    
    async def _detect_anomalies(self, performance_data: List[PerformanceDataPoint]) -> List[Dict[str, Any]]:
        """Detect performance anomalies"""
        anomalies = []
        
        for metric in PerformanceMetric:
            metric_values = [dp.value for dp in performance_data if dp.metric == metric]
            
            if len(metric_values) >= 10:  # Need sufficient data
                mean_val = statistics.mean(metric_values)
                std_dev = statistics.stdev(metric_values)
                
                for dp in performance_data:
                    if dp.metric == metric:
                        z_score = (dp.value - mean_val) / std_dev if std_dev > 0 else 0
                        
                        if abs(z_score) > self.anomaly_threshold:
                            anomaly_type = "spike" if z_score > 0 else "drop"
                            anomalies.append({
                                'timestamp': dp.timestamp,
                                'metric': metric.value,
                                'value': dp.value,
                                'expected_range': [mean_val - 2*std_dev, mean_val + 2*std_dev],
                                'anomaly_type': anomaly_type,
                                'severity': 'high' if abs(z_score) > 3 else 'medium',
                                'platform': dp.platform
                            })
        
        return anomalies[:20]  # Return top 20 anomalies
    
    async def track_real_time_metrics(self, creator_id: str) -> Dict[str, Any]:
        """Get real-time performance metrics"""
        # This would connect to real-time data streams
        current_time = datetime.utcnow()
        
        real_time_metrics = {
            'timestamp': current_time,
            'live_viewers': 1250,
            'current_engagement_rate': 0.089,
            'real_time_revenue': 45.75,
            'active_platforms': 4,
            'trending_content_count': 2,
            'notifications_pending': 12
        }
        
        return real_time_metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for performance tracker"""
        return {
            "status": "healthy",
            "tracked_metrics": len(PerformanceMetric),
            "time_frames_supported": len(TimeFrame),
            "benchmark_data_loaded": bool(self.benchmark_data),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("PerformanceTracker shutting down...")
