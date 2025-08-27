"""
Analytics Processor - Enterprise Business Intelligence & Advanced Analytics Engine

Comprehensive multi-dimensional analytics processing, predictive modeling, performance tracking, 
competitive analysis, audience insights, revenue attribution, and business intelligence across 
all social media platforms with integrated content protection and monetization analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL NOTICE:
This analytics engine and business intelligence system are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, reverse engineering, or commercialization without 
explicit written permission is strictly prohibited and will result in immediate legal action.
Contact: mlaiel@live.de for licensing inquiries only.

Expert Development Team Specialties:
- Lead AI Developer & ML Engineer - Advanced ML algorithms and predictive analytics
- Backend Senior Architect - Enterprise-level analytics processing architecture
- Database Administrator (DBA) - Analytics data modeling and performance optimization
- Security & Microservices Expert - Secure analytics processing and data protection
- Audio Processing Specialist - Audio content analytics and insights
- DevOps & Infrastructure Engineer - Analytics infrastructure and real-time processing
- AI Prompt Engineering Expert - Natural language analytics and content insights
- Content Protection Specialist - Protected content analytics and revenue tracking
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
import logging
import json
import statistics
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from collections import defaultdict, Counter
import math

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Comprehensive social media and business metrics"""
    # Engagement Metrics
    ENGAGEMENT = "engagement"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    REACTIONS = "reactions"
    
    # Reach & Visibility Metrics
    REACH = "reach"
    IMPRESSIONS = "impressions"
    UNIQUE_VIEWS = "unique_views"
    ORGANIC_REACH = "organic_reach"
    PAID_REACH = "paid_reach"
    
    # Traffic & Conversion Metrics
    CLICKS = "clicks"
    WEBSITE_VISITS = "website_visits"
    CONVERSIONS = "conversions"
    CONVERSION_RATE = "conversion_rate"
    BOUNCE_RATE = "bounce_rate"
    TIME_ON_SITE = "time_on_site"
    
    # Audience Metrics
    FOLLOWERS = "followers"
    FOLLOWER_GROWTH = "follower_growth"
    AUDIENCE_DEMOGRAPHICS = "audience_demographics"
    AUDIENCE_INTERESTS = "audience_interests"
    AUDIENCE_BEHAVIOR = "audience_behavior"
    
    # Video-Specific Metrics
    WATCH_TIME = "watch_time"
    VIEW_DURATION = "view_duration"
    COMPLETION_RATE = "completion_rate"
    RETENTION_RATE = "retention_rate"
    REPLAYS = "replays"
    
    # Revenue & Monetization Metrics
    REVENUE = "revenue"
    ROI = "roi"
    ROAS = "roas"
    CPM = "cpm"
    CPC = "cpc"
    CPA = "cpa"
    LIFETIME_VALUE = "lifetime_value"
    
    # Content Performance Metrics
    ENGAGEMENT_RATE = "engagement_rate"
    VIRAL_COEFFICIENT = "viral_coefficient"
    SHARE_RATE = "share_rate"
    COMMENT_RATE = "comment_rate"
    SAVE_RATE = "save_rate"
    
    # Brand & Sentiment Metrics
    BRAND_MENTIONS = "brand_mentions"
    SENTIMENT_SCORE = "sentiment_score"
    BRAND_AWARENESS = "brand_awareness"
    SHARE_OF_VOICE = "share_of_voice"
    
    # Competitive Metrics
    COMPETITOR_PERFORMANCE = "competitor_performance"
    MARKET_SHARE = "market_share"
    RELATIVE_PERFORMANCE = "relative_performance"
    
    # Content Protection Metrics
    CONTENT_THEFT_INCIDENTS = "content_theft_incidents"
    DMCA_TAKEDOWNS = "dmca_takedowns"
    PROTECTED_CONTENT_REVENUE = "protected_content_revenue"
    INFRINGEMENT_RECOVERY = "infringement_recovery"

class AnalyticsReportType(Enum):
    """Types of analytics reports"""
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_PERFORMANCE = "weekly_performance"
    MONTHLY_OVERVIEW = "monthly_overview"
    QUARTERLY_BUSINESS = "quarterly_business"
    ANNUAL_REVIEW = "annual_review"
    CAMPAIGN_ANALYSIS = "campaign_analysis"
    PLATFORM_COMPARISON = "platform_comparison"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    AUDIENCE_INSIGHTS = "audience_insights"
    CONTENT_PERFORMANCE = "content_performance"
    REVENUE_ATTRIBUTION = "revenue_attribution"
    PROTECTION_SUMMARY = "protection_summary"
    ROI_ANALYSIS = "roi_analysis"
    CUSTOM_REPORT = "custom_report"

class DataVisualizationType(Enum):
    """Data visualization formats"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEAT_MAP = "heat_map"
    FUNNEL_CHART = "funnel_chart"
    DASHBOARD = "dashboard"
    INFOGRAPHIC = "infographic"
    TABLE = "table"
    WORD_CLOUD = "word_cloud"
    VIEWS = "views"
    FOLLOWERS = "followers"
    CONVERSION = "conversion"
    REVENUE = "revenue"

class TimeFrame(Enum):
    """Analysis time frames"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class TrendDirection(Enum):
    """Trend directions"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class MetricData:
    """Individual metric data point"""
    platform: str
    content_id: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsSnapshot:
    """Analytics snapshot for a specific time period"""
    platform: str
    time_frame: TimeFrame
    start_time: datetime
    end_time: datetime
    metrics: Dict[MetricType, float]
    growth_rates: Dict[MetricType, float] = field(default_factory=dict)
    benchmarks: Dict[str, float] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)

@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    report_id: str
    platform: str
    time_period: Tuple[datetime, datetime]
    total_posts: int
    top_performing_content: List[Dict[str, Any]]
    audience_insights: Dict[str, Any]
    engagement_trends: Dict[str, Any]
    growth_metrics: Dict[str, float]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CompetitorAnalysis:
    """Competitor analysis data"""
    competitor_id: str
    platform: str
    metrics_comparison: Dict[MetricType, Dict[str, float]]  # our_value, competitor_value, difference
    content_analysis: Dict[str, Any]
    strategy_insights: List[str]
    opportunities: List[str]
    analyzed_at: datetime = field(default_factory=datetime.utcnow)

class MetricsCalculator:
    """Calculate derived metrics and KPIs"""
    
    @staticmethod
    def calculate_engagement_rate(likes: int, comments: int, shares: int, impressions: int) -> float:
        """Calculate engagement rate"""
        if impressions == 0:
            return 0.0
        total_engagement = likes + comments + shares
        return (total_engagement / impressions) * 100
    
    @staticmethod
    def calculate_reach_rate(reach: int, followers: int) -> float:
        """Calculate reach rate"""
        if followers == 0:
            return 0.0
        return (reach / followers) * 100
    
    @staticmethod
    def calculate_virality_score(shares: int, likes: int, comments: int, impressions: int) -> float:
        """Calculate virality score (0-1)"""
        if impressions == 0:
            return 0.0
        
        # Weighted scoring: shares worth more than likes/comments
        weighted_engagement = (shares * 3) + (likes * 1) + (comments * 2)
        virality_ratio = weighted_engagement / impressions
        
        # Normalize to 0-1 scale
        return min(1.0, virality_ratio)
    
    @staticmethod
    def calculate_growth_rate(current_value: float, previous_value: float) -> float:
        """Calculate growth rate percentage"""
        if previous_value == 0:
            return 0.0 if current_value == 0 else 100.0
        return ((current_value - previous_value) / previous_value) * 100
    
    @staticmethod
    def calculate_ctr(clicks: int, impressions: int) -> float:
        """Calculate click-through rate"""
        if impressions == 0:
            return 0.0
        return (clicks / impressions) * 100
    
    @staticmethod
    def calculate_conversion_rate(conversions: int, clicks: int) -> float:
        """Calculate conversion rate"""
        if clicks == 0:
            return 0.0
        return (conversions / clicks) * 100
    
    @staticmethod
    def calculate_roi(revenue: float, cost: float) -> float:
        """Calculate return on investment"""
        if cost == 0:
            return 0.0 if revenue == 0 else 100.0
        return ((revenue - cost) / cost) * 100

class TrendAnalyzer:
    """Analyze trends in social media metrics"""
    
    def __init__(self, min_data_points: int = 5):
        self.min_data_points = min_data_points
    
    def analyze_trend(self, values: List[float], timestamps: List[datetime]) -> Dict[str, Any]:
        """Analyze trend in time series data"""
        if len(values) < self.min_data_points:
            return {'direction': TrendDirection.STABLE, 'confidence': 0.0, 'strength': 0.0}
        
        # Calculate trend direction using linear regression
        x = np.arange(len(values))
        y = np.array(values)
        
        # Remove NaN values
        valid_indices = ~np.isnan(y)
        x = x[valid_indices]
        y = y[valid_indices]
        
        if len(y) < 2:
            return {'direction': TrendDirection.STABLE, 'confidence': 0.0, 'strength': 0.0}
        
        # Linear regression
        slope = np.corrcoef(x, y)[0, 1] * (np.std(y) / np.std(x))
        correlation = np.corrcoef(x, y)[0, 1]
        
        # Determine trend direction
        if abs(slope) < 0.01:  # Very small slope
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING
        
        # Calculate volatility
        volatility = np.std(y) / np.mean(y) if np.mean(y) != 0 else 0
        if volatility > 0.3:  # High volatility threshold
            direction = TrendDirection.VOLATILE
        
        # Confidence based on correlation strength
        confidence = abs(correlation) if not np.isnan(correlation) else 0.0
        strength = abs(slope)
        
        return {
            'direction': direction,
            'confidence': confidence,
            'strength': strength,
            'slope': slope,
            'volatility': volatility,
            'correlation': correlation
        }
    
    def detect_anomalies(self, values: List[float], threshold: float = 2.0) -> List[int]:
        """Detect anomalies using z-score method"""
        if len(values) < 3:
            return []
        
        values_array = np.array(values)
        mean_val = np.mean(values_array)
        std_val = np.std(values_array)
        
        if std_val == 0:
            return []
        
        z_scores = np.abs((values_array - mean_val) / std_val)
        anomaly_indices = np.where(z_scores > threshold)[0].tolist()
        
        return anomaly_indices
    
    def calculate_seasonality(self, values: List[float], timestamps: List[datetime]) -> Dict[str, Any]:
        """Detect seasonal patterns in data"""
        if len(values) < 14:  # Need at least 2 weeks of data
            return {'has_seasonality': False, 'pattern': None}
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'value': values
        })
        
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        
        # Analyze hourly patterns
        hourly_avg = df.groupby('hour')['value'].mean()
        hourly_variation = hourly_avg.std() / hourly_avg.mean() if hourly_avg.mean() != 0 else 0
        
        # Analyze weekly patterns
        weekly_avg = df.groupby('day_of_week')['value'].mean()
        weekly_variation = weekly_avg.std() / weekly_avg.mean() if weekly_avg.mean() != 0 else 0
        
        # Determine if there's significant seasonality
        has_hourly_pattern = hourly_variation > 0.2
        has_weekly_pattern = weekly_variation > 0.15
        
        return {
            'has_seasonality': has_hourly_pattern or has_weekly_pattern,
            'hourly_pattern': {
                'exists': has_hourly_pattern,
                'variation': hourly_variation,
                'peak_hour': int(hourly_avg.idxmax()),
                'low_hour': int(hourly_avg.idxmin())
            },
            'weekly_pattern': {
                'exists': has_weekly_pattern,
                'variation': weekly_variation,
                'peak_day': int(weekly_avg.idxmax()),  # 0=Monday
                'low_day': int(weekly_avg.idxmin())
            }
        }

class AudienceSegmenter:
    """Segment audience based on engagement patterns"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = None
        
    def segment_audience(self, audience_data: List[Dict[str, Any]], n_segments: int = 5) -> Dict[str, Any]:
        """Segment audience using machine learning"""
        if len(audience_data) < n_segments * 2:
            return {'segments': [], 'error': 'Insufficient data for segmentation'}
        
        # Prepare feature matrix
        features = []
        for user in audience_data:
            feature_vector = [
                user.get('engagement_rate', 0),
                user.get('avg_session_duration', 0),
                user.get('posts_per_week', 0),
                user.get('likes_given', 0),
                user.get('comments_made', 0),
                user.get('shares_count', 0),
                user.get('follower_count', 0)
            ]
            features.append(feature_vector)
        
        # Scale features
        X = self.scaler.fit_transform(np.array(features))
        
        # Apply K-means clustering
        self.kmeans = KMeans(n_clusters=n_segments, random_state=42, n_init=10)
        cluster_labels = self.kmeans.fit_predict(X)
        
        # Analyze segments
        segments = []
        for cluster_id in range(n_segments):
            cluster_users = [user for i, user in enumerate(audience_data) if cluster_labels[i] == cluster_id]
            
            if not cluster_users:
                continue
            
            segment = self._analyze_segment(cluster_users, cluster_id)
            segments.append(segment)
        
        return {
            'segments': segments,
            'total_users': len(audience_data),
            'segmentation_quality': self._calculate_segmentation_quality(X, cluster_labels)
        }
    
    def _analyze_segment(self, users: List[Dict[str, Any]], segment_id: int) -> Dict[str, Any]:
        """Analyze characteristics of a user segment"""
        if not users:
            return {}
        
        # Calculate segment statistics
        engagement_rates = [u.get('engagement_rate', 0) for u in users]
        session_durations = [u.get('avg_session_duration', 0) for u in users]
        follower_counts = [u.get('follower_count', 0) for u in users]
        
        # Determine segment characteristics
        avg_engagement = statistics.mean(engagement_rates) if engagement_rates else 0
        avg_session = statistics.mean(session_durations) if session_durations else 0
        avg_followers = statistics.mean(follower_counts) if follower_counts else 0
        
        # Classify segment type
        segment_type = self._classify_segment_type(avg_engagement, avg_session, avg_followers)
        
        return {
            'segment_id': segment_id,
            'size': len(users),
            'percentage': 0,  # Will be calculated later
            'type': segment_type,
            'characteristics': {
                'avg_engagement_rate': avg_engagement,
                'avg_session_duration': avg_session,
                'avg_follower_count': avg_followers,
                'engagement_std': statistics.stdev(engagement_rates) if len(engagement_rates) > 1 else 0
            },
            'behavior_patterns': self._identify_behavior_patterns(users)
        }
    
    def _classify_segment_type(self, engagement: float, session_duration: float, followers: float) -> str:
        """Classify segment type based on characteristics"""
        if engagement > 0.1 and session_duration > 300:  # High engagement, long sessions
            return "highly_engaged"
        elif engagement > 0.05 and followers > 1000:  # Moderate engagement, many followers
            return "influencers"
        elif session_duration < 60:  # Short sessions
            return "browsers"
        elif engagement < 0.02:  # Low engagement
            return "passive_viewers"
        else:
            return "casual_users"
    
    def _identify_behavior_patterns(self, users: List[Dict[str, Any]]) -> List[str]:
        """Identify common behavior patterns in segment"""
        patterns = []
        
        # Analyze posting times
        posting_hours = []
        for user in users:
            if 'preferred_posting_hours' in user:
                posting_hours.extend(user['preferred_posting_hours'])
        
        if posting_hours:
            most_common_hour = Counter(posting_hours).most_common(1)[0][0]
            patterns.append(f"Most active at {most_common_hour}:00")
        
        # Analyze content preferences
        content_types = []
        for user in users:
            if 'preferred_content_types' in user:
                content_types.extend(user['preferred_content_types'])
        
        if content_types:
            top_content = Counter(content_types).most_common(2)
            for content_type, count in top_content:
                patterns.append(f"Prefers {content_type} content")
        
        return patterns
    
    def _calculate_segmentation_quality(self, X: np.ndarray, labels: np.ndarray) -> float:
        """Calculate silhouette score to measure segmentation quality"""
        try:
            from sklearn.metrics import silhouette_score
            return silhouette_score(X, labels)
        except:
            return 0.0

class CompetitorAnalyzer:
    """Analyze competitor performance and strategies"""
    
    def __init__(self):
        self.competitor_cache: Dict[str, Dict[str, Any]] = {}
    
    async def analyze_competitor(self, competitor_id: str, platform: str, 
                               our_metrics: Dict[MetricType, float],
                               competitor_metrics: Dict[MetricType, float]) -> CompetitorAnalysis:
        """Comprehensive competitor analysis"""
        
        # Compare metrics
        metrics_comparison = {}
        for metric in MetricType:
            our_value = our_metrics.get(metric, 0)
            competitor_value = competitor_metrics.get(metric, 0)
            
            if competitor_value > 0:
                difference_pct = ((our_value - competitor_value) / competitor_value) * 100
            else:
                difference_pct = 0
            
            metrics_comparison[metric] = {
                'our_value': our_value,
                'competitor_value': competitor_value,
                'difference_pct': difference_pct,
                'we_lead': our_value > competitor_value
            }
        
        # Analyze content strategy
        content_analysis = await self._analyze_competitor_content(competitor_id, platform)
        
        # Generate strategy insights
        strategy_insights = self._generate_strategy_insights(metrics_comparison, content_analysis)
        
        # Identify opportunities
        opportunities = self._identify_opportunities(metrics_comparison, content_analysis)
        
        return CompetitorAnalysis(
            competitor_id=competitor_id,
            platform=platform,
            metrics_comparison=metrics_comparison,
            content_analysis=content_analysis,
            strategy_insights=strategy_insights,
            opportunities=opportunities
        )
    
    async def _analyze_competitor_content(self, competitor_id: str, platform: str) -> Dict[str, Any]:
        """Analyze competitor's content strategy"""
        # This would typically fetch competitor's content data
        # For now, return simulated analysis
        
        return {
            'posting_frequency': 3.2,  # posts per day
            'best_performing_content_types': ['video', 'carousel', 'image'],
            'optimal_posting_times': [9, 12, 18, 20],
            'hashtag_strategy': {
                'avg_hashtags_per_post': 12,
                'most_used_hashtags': ['#marketing', '#business', '#growth'],
                'hashtag_performance': 'high'
            },
            'engagement_patterns': {
                'avg_engagement_rate': 4.2,
                'peak_engagement_days': ['Tuesday', 'Thursday'],
                'content_with_highest_engagement': 'educational_videos'
            }
        }
    
    def _generate_strategy_insights(self, metrics_comparison: Dict[MetricType, Dict[str, float]], 
                                  content_analysis: Dict[str, Any]) -> List[str]:
        """Generate strategic insights based on competitor analysis"""
        insights = []
        
        # Engagement insights
        engagement_comparison = metrics_comparison.get(MetricType.ENGAGEMENT, {})
        if engagement_comparison.get('difference_pct', 0) < -20:
            insights.append("Competitor has significantly higher engagement rate - analyze their content strategy")
        
        # Reach insights
        reach_comparison = metrics_comparison.get(MetricType.REACH, {})
        if reach_comparison.get('difference_pct', 0) < -30:
            insights.append("Competitor has much better reach - consider their posting times and hashtag strategy")
        
        # Content frequency insights
        posting_freq = content_analysis.get('posting_frequency', 1)
        if posting_freq > 2:
            insights.append(f"Competitor posts {posting_freq:.1f} times daily - consider increasing posting frequency")
        
        # Hashtag insights
        hashtag_data = content_analysis.get('hashtag_strategy', {})
        avg_hashtags = hashtag_data.get('avg_hashtags_per_post', 0)
        if avg_hashtags > 8:
            insights.append(f"Competitor uses {avg_hashtags} hashtags on average - optimize hashtag strategy")
        
        return insights
    
    def _identify_opportunities(self, metrics_comparison: Dict[MetricType, Dict[str, float]], 
                              content_analysis: Dict[str, Any]) -> List[str]:
        """Identify opportunities based on competitor analysis"""
        opportunities = []
        
        # Look for areas where we're underperforming
        weak_metrics = []
        for metric, comparison in metrics_comparison.items():
            if comparison.get('difference_pct', 0) < -15:  # We're 15% behind
                weak_metrics.append(metric.value)
        
        if MetricType.ENGAGEMENT.value in weak_metrics:
            opportunities.append("Focus on creating more engaging content types")
            opportunities.append("Experiment with interactive content formats")
        
        if MetricType.REACH.value in weak_metrics:
            opportunities.append("Optimize posting times based on competitor's schedule")
            opportunities.append("Expand hashtag strategy")
        
        if MetricType.SHARES.value in weak_metrics:
            opportunities.append("Create more shareable content")
            opportunities.append("Add call-to-action for sharing")
        
        # Content-specific opportunities
        best_content = content_analysis.get('best_performing_content_types', [])
        if 'video' in best_content:
            opportunities.append("Increase video content production")
        
        if 'carousel' in best_content:
            opportunities.append("Create more carousel posts")
        
        return opportunities

class AnalyticsProcessor:
    """
    Advanced Social Media Analytics & Intelligence Engine
    Comprehensive analytics processing, performance tracking, and business intelligence
    """
    
    def __init__(self):
        self.metrics_data: List[MetricData] = []
        self.snapshots: List[AnalyticsSnapshot] = []
        self.reports_cache: Dict[str, PerformanceReport] = {}
        self.trend_analyzer = TrendAnalyzer()
        self.audience_segmenter = AudienceSegmenter()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.metrics_calculator = MetricsCalculator()
        self.real_time_callbacks: List[Callable] = []
        
    async def process_metrics(self, metrics: List[MetricData]):
        """Process new metrics data"""
        self.metrics_data.extend(metrics)
        
        # Limit data size to prevent memory issues
        if len(self.metrics_data) > 50000:
            self.metrics_data = self.metrics_data[-40000:]
        
        # Trigger real-time processing
        await self._process_real_time_alerts(metrics)
        
        logger.info(f"Processed {len(metrics)} new metric data points")
    
    async def _process_real_time_alerts(self, new_metrics: List[MetricData]):
        """Process real-time alerts and notifications"""
        for metric in new_metrics:
            # Check for significant changes
            recent_values = self._get_recent_values(metric.platform, metric.metric_type, hours=24)
            
            if len(recent_values) >= 2:
                current_value = recent_values[-1]
                previous_avg = statistics.mean(recent_values[:-1])
                
                # Check for sudden spike or drop
                if current_value > previous_avg * 1.5:  # 50% increase
                    await self._trigger_alert("spike", metric, current_value, previous_avg)
                elif current_value < previous_avg * 0.5:  # 50% decrease
                    await self._trigger_alert("drop", metric, current_value, previous_avg)
    
    def _get_recent_values(self, platform: str, metric_type: MetricType, hours: int = 24) -> List[float]:
        """Get recent metric values"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_data = [
            data for data in self.metrics_data
            if (data.platform == platform and 
                data.metric_type == metric_type and 
                data.timestamp > cutoff_time)
        ]
        
        return [data.value for data in sorted(recent_data, key=lambda x: x.timestamp)]
    
    async def _trigger_alert(self, alert_type: str, metric: MetricData, 
                           current_value: float, previous_avg: float):
        """Trigger alert for significant metric changes"""
        alert_data = {
            'type': alert_type,
            'platform': metric.platform,
            'metric': metric.metric_type.value,
            'current_value': current_value,
            'previous_average': previous_avg,
            'change_percentage': ((current_value - previous_avg) / previous_avg) * 100,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Call registered callbacks
        for callback in self.real_time_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                logger.error(f"Alert callback failed: {str(e)}")
    
    def register_real_time_callback(self, callback: Callable):
        """Register callback for real-time alerts"""
        self.real_time_callbacks.append(callback)
    
    async def generate_analytics_snapshot(self, platform: str, time_frame: TimeFrame,
                                        start_time: datetime, end_time: datetime) -> AnalyticsSnapshot:
        """Generate analytics snapshot for specified time period"""
        
        # Filter data for time period
        period_data = [
            data for data in self.metrics_data
            if (data.platform == platform and 
                start_time <= data.timestamp <= end_time)
        ]
        
        # Calculate aggregated metrics
        metrics = {}
        for metric_type in MetricType:
            metric_values = [data.value for data in period_data if data.metric_type == metric_type]
            if metric_values:
                metrics[metric_type] = sum(metric_values)
            else:
                metrics[metric_type] = 0.0
        
        # Calculate growth rates
        growth_rates = await self._calculate_growth_rates(platform, time_frame, start_time, metrics)
        
        # Get benchmarks
        benchmarks = await self._get_industry_benchmarks(platform)
        
        # Generate insights
        insights = await self._generate_insights(metrics, growth_rates, benchmarks)
        
        snapshot = AnalyticsSnapshot(
            platform=platform,
            time_frame=time_frame,
            start_time=start_time,
            end_time=end_time,
            metrics=metrics,
            growth_rates=growth_rates,
            benchmarks=benchmarks,
            insights=insights
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    async def _calculate_growth_rates(self, platform: str, time_frame: TimeFrame,
                                    current_start: datetime, current_metrics: Dict[MetricType, float]) -> Dict[MetricType, float]:
        """Calculate growth rates compared to previous period"""
        growth_rates = {}
        
        # Determine previous period
        if time_frame == TimeFrame.DAILY:
            previous_start = current_start - timedelta(days=1)
            previous_end = current_start
        elif time_frame == TimeFrame.WEEKLY:
            previous_start = current_start - timedelta(weeks=1)
            previous_end = current_start
        elif time_frame == TimeFrame.MONTHLY:
            previous_start = current_start - timedelta(days=30)
            previous_end = current_start
        else:
            return growth_rates  # Not implemented for other time frames
        
        # Get previous period data
        previous_data = [
            data for data in self.metrics_data
            if (data.platform == platform and 
                previous_start <= data.timestamp <= previous_end)
        ]
        
        # Calculate previous metrics
        previous_metrics = {}
        for metric_type in MetricType:
            metric_values = [data.value for data in previous_data if data.metric_type == metric_type]
            previous_metrics[metric_type] = sum(metric_values) if metric_values else 0.0
        
        # Calculate growth rates
        for metric_type in MetricType:
            current_value = current_metrics.get(metric_type, 0)
            previous_value = previous_metrics.get(metric_type, 0)
            growth_rates[metric_type] = self.metrics_calculator.calculate_growth_rate(current_value, previous_value)
        
        return growth_rates
    
    async def _get_industry_benchmarks(self, platform: str) -> Dict[str, float]:
        """Get industry benchmarks for comparison"""
        # These would typically come from industry data APIs
        benchmarks = {
            'engagement_rate': {
                'instagram': 1.22,
                'facebook': 0.15,
                'twitter': 0.045,
                'linkedin': 0.54,
                'tiktok': 5.96
            }.get(platform.lower(), 1.0),
            
            'reach_rate': {
                'instagram': 35.0,
                'facebook': 12.0,
                'twitter': 8.0,
                'linkedin': 25.0,
                'tiktok': 45.0
            }.get(platform.lower(), 20.0),
            
            'click_through_rate': {
                'instagram': 0.52,
                'facebook': 0.90,
                'twitter': 1.64,
                'linkedin': 0.44,
                'tiktok': 1.0
            }.get(platform.lower(), 1.0)
        }
        
        return benchmarks
    
    async def _generate_insights(self, metrics: Dict[MetricType, float], 
                               growth_rates: Dict[MetricType, float],
                               benchmarks: Dict[str, float]) -> List[str]:
        """Generate insights based on metrics analysis"""
        insights = []
        
        # Engagement insights
        engagement = metrics.get(MetricType.ENGAGEMENT, 0)
        engagement_benchmark = benchmarks.get('engagement_rate', 1.0)
        
        if engagement > engagement_benchmark * 1.2:
            insights.append("Engagement rate is 20% above industry benchmark - excellent performance!")
        elif engagement < engagement_benchmark * 0.8:
            insights.append("Engagement rate is below industry benchmark - consider content optimization")
        
        # Growth insights
        engagement_growth = growth_rates.get(MetricType.ENGAGEMENT, 0)
        if engagement_growth > 20:
            insights.append(f"Engagement grew by {engagement_growth:.1f}% - strong upward trend")
        elif engagement_growth < -20:
            insights.append(f"Engagement declined by {abs(engagement_growth):.1f}% - needs attention")
        
        # Reach insights
        reach_growth = growth_rates.get(MetricType.REACH, 0)
        if reach_growth > 15:
            insights.append("Reach is expanding rapidly - content resonating well with audience")
        
        # Follower growth insights
        follower_growth = growth_rates.get(MetricType.FOLLOWERS, 0)
        if follower_growth > 10:
            insights.append("Strong follower growth indicates increasing brand awareness")
        
        return insights
    
    async def generate_performance_report(self, platform: str, days_back: int = 30) -> PerformanceReport:
        """Generate comprehensive performance report"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days_back)
        
        # Get data for time period
        period_data = [
            data for data in self.metrics_data
            if (data.platform == platform and 
                start_time <= data.timestamp <= end_time)
        ]
        
        # Count total posts
        unique_content_ids = set(data.content_id for data in period_data)
        total_posts = len(unique_content_ids)
        
        # Find top performing content
        top_performing_content = await self._get_top_performing_content(platform, start_time, end_time)
        
        # Analyze audience
        audience_insights = await self._analyze_audience_insights(platform, start_time, end_time)
        
        # Analyze engagement trends
        engagement_trends = await self._analyze_engagement_trends(platform, start_time, end_time)
        
        # Calculate growth metrics
        growth_metrics = await self._calculate_period_growth_metrics(platform, start_time, end_time)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(platform, period_data, growth_metrics)
        
        report = PerformanceReport(
            report_id=f"report_{platform}_{int(end_time.timestamp())}",
            platform=platform,
            time_period=(start_time, end_time),
            total_posts=total_posts,
            top_performing_content=top_performing_content,
            audience_insights=audience_insights,
            engagement_trends=engagement_trends,
            growth_metrics=growth_metrics,
            recommendations=recommendations
        )
        
        # Cache report
        self.reports_cache[report.report_id] = report
        
        return report
    
    async def _get_top_performing_content(self, platform: str, start_time: datetime, 
                                        end_time: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing content for the period"""
        # Group data by content_id and calculate total engagement
        content_performance = defaultdict(lambda: {'total_engagement': 0, 'metrics': {}})
        
        period_data = [
            data for data in self.metrics_data
            if (data.platform == platform and 
                start_time <= data.timestamp <= end_time)
        ]
        
        for data in period_data:
            content_id = data.content_id
            content_performance[content_id]['metrics'][data.metric_type] = data.value
            
            # Calculate engagement score
            if data.metric_type in [MetricType.LIKES, MetricType.COMMENTS, MetricType.SHARES]:
                content_performance[content_id]['total_engagement'] += data.value
        
        # Sort by total engagement and return top content
        sorted_content = sorted(
            content_performance.items(),
            key=lambda x: x[1]['total_engagement'],
            reverse=True
        )
        
        top_content = []
        for content_id, performance in sorted_content[:limit]:
            top_content.append({
                'content_id': content_id,
                'total_engagement': performance['total_engagement'],
                'metrics': {metric.value: value for metric, value in performance['metrics'].items()}
            })
        
        return top_content
    
    async def _analyze_audience_insights(self, platform: str, start_time: datetime, 
                                       end_time: datetime) -> Dict[str, Any]:
        """Analyze audience behavior and demographics"""
        # This would typically integrate with platform APIs for detailed audience data
        # For now, return simulated insights based on our metrics
        
        period_data = [
            data for data in self.metrics_data
            if (data.platform == platform and 
                start_time <= data.timestamp <= end_time)
        ]
        
        # Analyze posting time performance
        hourly_performance = defaultdict(list)
        for data in period_data:
            hour = data.timestamp.hour
            if data.metric_type == MetricType.ENGAGEMENT:
                hourly_performance[hour].append(data.value)
        
        # Find best performing hours
        hourly_avg = {}
        for hour, values in hourly_performance.items():
            if values:
                hourly_avg[hour] = statistics.mean(values)
        
        best_hours = sorted(hourly_avg.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'most_active_hours': [hour for hour, _ in best_hours],
            'peak_engagement_hour': best_hours[0][0] if best_hours else 12,
            'audience_growth_rate': 5.2,  # Would come from actual data
            'top_demographics': {
                'age_groups': {'18-24': 35, '25-34': 40, '35-44': 25},
                'locations': ['United States', 'United Kingdom', 'Canada']
            }
        }
    
    async def _analyze_engagement_trends(self, platform: str, start_time: datetime, 
                                       end_time: datetime) -> Dict[str, Any]:
        """Analyze engagement trends over the period"""
        engagement_data = [
            data for data in self.metrics_data
            if (data.platform == platform and 
                data.metric_type == MetricType.ENGAGEMENT and
                start_time <= data.timestamp <= end_time)
        ]
        
        if not engagement_data:
            return {'trend': 'no_data', 'analysis': {}}
        
        values = [data.value for data in engagement_data]
        timestamps = [data.timestamp for data in engagement_data]
        
        trend_analysis = self.trend_analyzer.analyze_trend(values, timestamps)
        seasonality = self.trend_analyzer.calculate_seasonality(values, timestamps)
        anomalies = self.trend_analyzer.detect_anomalies(values)
        
        return {
            'trend': trend_analysis,
            'seasonality': seasonality,
            'anomalies': len(anomalies),
            'volatility': trend_analysis.get('volatility', 0),
            'average_engagement': statistics.mean(values),
            'peak_engagement': max(values),
            'low_engagement': min(values)
        }
    
    async def _calculate_period_growth_metrics(self, platform: str, start_time: datetime, 
                                             end_time: datetime) -> Dict[str, float]:
        """Calculate growth metrics for the period"""
        growth_metrics = {}
        
        # Split period in half to compare
        mid_point = start_time + (end_time - start_time) / 2
        
        for metric_type in MetricType:
            first_half_data = [
                data.value for data in self.metrics_data
                if (data.platform == platform and 
                    data.metric_type == metric_type and
                    start_time <= data.timestamp <= mid_point)
            ]
            
            second_half_data = [
                data.value for data in self.metrics_data
                if (data.platform == platform and 
                    data.metric_type == metric_type and
                    mid_point < data.timestamp <= end_time)
            ]
            
            if first_half_data and second_half_data:
                first_half_avg = statistics.mean(first_half_data)
                second_half_avg = statistics.mean(second_half_data)
                
                growth_rate = self.metrics_calculator.calculate_growth_rate(second_half_avg, first_half_avg)
                growth_metrics[f'{metric_type.value}_growth'] = growth_rate
        
        return growth_metrics
    
    async def _generate_recommendations(self, platform: str, period_data: List[MetricData],
                                      growth_metrics: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Engagement recommendations
        engagement_growth = growth_metrics.get('engagement_growth', 0)
        if engagement_growth < -10:
            recommendations.append("Engagement is declining - focus on creating more interactive content")
            recommendations.append("Consider experimenting with different content formats")
        
        # Reach recommendations
        reach_growth = growth_metrics.get('reach_growth', 0)
        if reach_growth < 0:
            recommendations.append("Reach is declining - optimize posting times and hashtag strategy")
        
        # Follower growth recommendations
        follower_growth = growth_metrics.get('followers_growth', 0)
        if follower_growth < 5:
            recommendations.append("Slow follower growth - increase posting frequency and engage more with audience")
        
        # Platform-specific recommendations
        if platform.lower() == 'instagram':
            recommendations.append("Use Instagram Stories and Reels to boost engagement")
        elif platform.lower() == 'tiktok':
            recommendations.append("Focus on trending hashtags and music for better reach")
        elif platform.lower() == 'linkedin':
            recommendations.append("Share more professional insights and industry news")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def get_real_time_analytics(self, platform: str, hours: int = 1) -> Dict[str, Any]:
        """Get real-time analytics for immediate insights"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_data = [
            data for data in self.metrics_data
            if (data.platform == platform and data.timestamp > cutoff_time)
        ]
        
        if not recent_data:
            return {'message': 'No recent data available'}
        
        # Calculate real-time metrics
        current_metrics = {}
        for metric_type in MetricType:
            metric_values = [data.value for data in recent_data if data.metric_type == metric_type]
            if metric_values:
                current_metrics[metric_type.value] = {
                    'current_value': metric_values[-1] if metric_values else 0,
                    'total': sum(metric_values),
                    'average': statistics.mean(metric_values),
                    'trend': 'up' if len(metric_values) > 1 and metric_values[-1] > metric_values[-2] else 'down'
                }
        
        return {
            'platform': platform,
            'time_window_hours': hours,
            'last_updated': datetime.utcnow().isoformat(),
            'metrics': current_metrics,
            'total_data_points': len(recent_data)
        }
