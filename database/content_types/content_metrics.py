"""Content Performance Metrics Module - Advanced Analytics & KPI Tracking System

Module avancé pour le suivi des performances, analytics et KPIs du contenu
dans la plateforme IA Influencer Agent selon la logique métier.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Data Analytics Expert, Performance Optimization Specialist, BI Engineer
Copyright: Fahed Mlaiel - All rights reserved

⚠️  AVERTISSEMENT LÉGAL ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et fera l'objet de poursuites judiciaires.
Contact: mlaiel@live.de

🎯 LOGIQUE MÉTIER PERFORMANCE :
Upload → IA Processing → Protection → Distribution → Performance Tracking → Revenue Optimization
"""
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
import logging
import json
import uuid
import statistics
from collections import defaultdict

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from .content_models import Base, ContentType

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of performance metrics"""
    ENGAGEMENT = "engagement"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    VIEWS = "views"
    CLICKS = "clicks"
    SHARES = "shares"
    LIKES = "likes"
    COMMENTS = "comments"
    SAVES = "saves"
    DOWNLOADS = "downloads"
    REVENUE = "revenue"
    CONVERSION = "conversion"
    RETENTION = "retention"
    GROWTH = "growth"

class TimeFrame(Enum):
    """Time frame for metrics aggregation"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    REAL_TIME = "real_time"

class PlatformMetrics(Enum):
    """Platform-specific metric types"""
    YOUTUBE_VIEWS = "youtube_views"
    YOUTUBE_WATCH_TIME = "youtube_watch_time"
    YOUTUBE_SUBSCRIBERS = "youtube_subscribers"
    INSTAGRAM_REACH = "instagram_reach"
    INSTAGRAM_IMPRESSIONS = "instagram_impressions"
    TIKTOK_VIEWS = "tiktok_views"
    TIKTOK_SHARES = "tiktok_shares"
    SPOTIFY_STREAMS = "spotify_streams"
    SPOTIFY_MONTHLY_LISTENERS = "spotify_monthly_listeners"
    FACEBOOK_ENGAGEMENT = "facebook_engagement"
    TWITTER_IMPRESSIONS = "twitter_impressions"

class TrendDirection(Enum):
    """Trend direction indicators"""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"
    PEAK = "peak"
    TROUGH = "trough"

class PerformanceLevel(Enum):
    """Performance level classifications"""
    POOR = "poor"
    BELOW_AVERAGE = "below_average"
    AVERAGE = "average"
    ABOVE_AVERAGE = "above_average"
    EXCELLENT = "excellent"
    VIRAL = "viral"

@dataclass
class MetricSnapshot:
    """Single metric measurement at a point in time"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    platform: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'metric_type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'platform': self.platform,
            'metadata': self.metadata
        }

@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    direction: TrendDirection
    velocity: float  # Rate of change
    confidence: float  # Confidence in trend prediction
    predicted_next_value: float
    time_to_peak: Optional[timedelta] = None
    seasonality_detected: bool = False
    anomalies_detected: List[datetime] = field(default_factory=list)

class ContentPerformanceMetrics(Base):
    """Database model for content performance metrics"""
    __tablename__ = "content_performance_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Content identification
    content_type = Column(String(20), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    content_url = Column(Text, nullable=True)
    
    # Core engagement metrics
    views = Column(Integer, nullable=False, default=0)
    unique_views = Column(Integer, nullable=False, default=0)
    likes = Column(Integer, nullable=False, default=0)
    dislikes = Column(Integer, nullable=False, default=0)
    shares = Column(Integer, nullable=False, default=0)
    comments = Column(Integer, nullable=False, default=0)
    saves = Column(Integer, nullable=False, default=0)
    downloads = Column(Integer, nullable=False, default=0)
    
    # Reach and impressions
    impressions = Column(Integer, nullable=False, default=0)
    reach = Column(Integer, nullable=False, default=0)
    organic_reach = Column(Integer, nullable=False, default=0)
    paid_reach = Column(Integer, nullable=False, default=0)
    
    # Engagement rates
    engagement_rate = Column(Float, nullable=False, default=0.0)
    click_through_rate = Column(Float, nullable=False, default=0.0)
    conversion_rate = Column(Float, nullable=False, default=0.0)
    retention_rate = Column(Float, nullable=False, default=0.0)
    
    # Time-based metrics
    average_view_duration = Column(Float, nullable=False, default=0.0)  # seconds
    total_watch_time = Column(Float, nullable=False, default=0.0)  # seconds
    bounce_rate = Column(Float, nullable=False, default=0.0)
    session_duration = Column(Float, nullable=False, default=0.0)
    
    # Revenue metrics
    revenue_generated = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    ad_revenue = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    sponsorship_revenue = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    licensing_revenue = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    currency = Column(String(3), nullable=False, default='EUR')
    
    # Performance scores
    viral_score = Column(Float, nullable=False, default=0.0)  # 0-100
    quality_score = Column(Float, nullable=False, default=0.0)  # 0-100
    engagement_quality_score = Column(Float, nullable=False, default=0.0)  # 0-100
    performance_level = Column(String(20), nullable=False, default='average')
    
    # Growth metrics
    follower_growth = Column(Integer, nullable=False, default=0)
    subscriber_growth = Column(Integer, nullable=False, default=0)
    view_growth_rate = Column(Float, nullable=False, default=0.0)
    engagement_growth_rate = Column(Float, nullable=False, default=0.0)
    
    # Demographic insights
    top_countries = Column(ARRAY(String), nullable=False, default=[])
    top_age_groups = Column(ARRAY(String), nullable=False, default=[])
    gender_distribution = Column(JSONB, nullable=False, default={})
    device_breakdown = Column(JSONB, nullable=False, default={})
    
    # Traffic sources
    organic_traffic_percentage = Column(Float, nullable=False, default=0.0)
    social_traffic_percentage = Column(Float, nullable=False, default=0.0)
    direct_traffic_percentage = Column(Float, nullable=False, default=0.0)
    referral_traffic_percentage = Column(Float, nullable=False, default=0.0)
    
    # Platform-specific metrics
    platform_specific_metrics = Column(JSONB, nullable=False, default={})
    
    # Competition analysis
    competitor_comparison = Column(JSONB, nullable=False, default={})
    market_position = Column(String(20), nullable=True)
    benchmark_score = Column(Float, nullable=False, default=0.0)
    
    # Prediction and trends
    predicted_performance = Column(JSONB, nullable=False, default={})
    trend_analysis = Column(JSONB, nullable=False, default={})
    
    # Time tracking
    measurement_period_start = Column(DateTime(timezone=True), nullable=False)
    measurement_period_end = Column(DateTime(timezone=True), nullable=False)
    measured_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ContentPerformanceMetrics(content_id={self.content_id}, platform={self.platform}, views={self.views})>"
    
    def calculate_engagement_rate(self) -> float:
        """Calculate engagement rate"""
        if self.impressions == 0:
            return 0.0
        return ((self.likes + self.comments + self.shares) / self.impressions) * 100
    
    def calculate_viral_score(self) -> float:
        """Calculate viral potential score"""
        if self.views == 0:
            return 0.0
        
        # Viral indicators: high share ratio, rapid growth, high engagement
        share_ratio = (self.shares / self.views) * 100 if self.views > 0 else 0
        engagement_ratio = self.calculate_engagement_rate()
        
        # Weighted score
        viral_score = (share_ratio * 0.4) + (engagement_ratio * 0.3) + (min(100, self.view_growth_rate) * 0.3)
        return min(100.0, viral_score)

class PerformanceTrend(Base):
    """Database model for performance trend tracking"""
    __tablename__ = "performance_trends"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    metric_type = Column(String(30), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    
    # Trend data
    trend_direction = Column(String(20), nullable=False)
    trend_velocity = Column(Float, nullable=False, default=0.0)
    trend_confidence = Column(Float, nullable=False, default=0.0)
    
    # Values
    current_value = Column(Float, nullable=False)
    previous_value = Column(Float, nullable=False)
    predicted_value = Column(Float, nullable=True)
    percentage_change = Column(Float, nullable=False, default=0.0)
    
    # Time analysis
    time_frame = Column(String(20), nullable=False)
    seasonality_detected = Column(Boolean, nullable=False, default=False)
    anomaly_detected = Column(Boolean, nullable=False, default=False)
    
    # Metadata
    trend_metadata = Column(JSONB, nullable=False, default={})
    
    # Timestamps
    analysis_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<PerformanceTrend(metric={self.metric_type}, direction={self.trend_direction}, change={self.percentage_change}%)>"

class PerformanceBenchmark(Base):
    """Database model for performance benchmarks"""
    __tablename__ = "performance_benchmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_type = Column(String(20), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    industry_category = Column(String(100), nullable=True)
    
    # Benchmark values
    metric_type = Column(String(30), nullable=False, index=True)
    percentile_10 = Column(Float, nullable=False)  # Bottom 10%
    percentile_25 = Column(Float, nullable=False)  # Bottom quartile
    percentile_50 = Column(Float, nullable=False)  # Median
    percentile_75 = Column(Float, nullable=False)  # Top quartile
    percentile_90 = Column(Float, nullable=False)  # Top 10%
    average_value = Column(Float, nullable=False)
    
    # Sample information
    sample_size = Column(Integer, nullable=False)
    confidence_level = Column(Float, nullable=False, default=95.0)
    
    # Validity period
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_performance_level(self, value: float) -> PerformanceLevel:
        """Determine performance level based on benchmark"""
        if value >= self.percentile_90:
            return PerformanceLevel.VIRAL
        elif value >= self.percentile_75:
            return PerformanceLevel.EXCELLENT
        elif value >= self.percentile_50:
            return PerformanceLevel.ABOVE_AVERAGE
        elif value >= self.percentile_25:
            return PerformanceLevel.AVERAGE
        elif value >= self.percentile_10:
            return PerformanceLevel.BELOW_AVERAGE
        else:
            return PerformanceLevel.POOR

class PerformanceAnalyzer:
    """Advanced performance analysis engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.trend_window_days = self.config.get('trend_window_days', 30)
        self.anomaly_threshold = self.config.get('anomaly_threshold', 2.0)  # Standard deviations
    
    async def analyze_content_performance(self, content_id: str, 
                                        start_date: datetime = None,
                                        end_date: datetime = None) -> Dict[str, Any]:
        """Perform comprehensive performance analysis"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=self.trend_window_days)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get performance metrics for the period
            # In production, this would query the database
            metrics = await self._get_metrics_for_period(content_id, start_date, end_date)
            
            if not metrics:
                return {'error': 'No metrics found for the specified period'}
            
            # Perform various analyses
            analysis = {
                'content_id': content_id,
                'analysis_period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': self._generate_summary(metrics),
                'trends': await self._analyze_trends(metrics),
                'engagement_analysis': self._analyze_engagement(metrics),
                'revenue_analysis': self._analyze_revenue(metrics),
                'audience_insights': self._analyze_audience(metrics),
                'platform_comparison': self._compare_platforms(metrics),
                'benchmarking': await self._benchmark_performance(metrics),
                'predictions': await self._generate_predictions(metrics),
                'recommendations': self._generate_recommendations(metrics),
                'anomalies': self._detect_anomalies(metrics),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed: {e}")
            raise
    
    async def _get_metrics_for_period(self, content_id: str, 
                                    start_date: datetime, 
                                    end_date: datetime) -> List[ContentPerformanceMetrics]:
        """Retrieve metrics for analysis period"""
        # Placeholder - in production would query database
        # For now, return sample data structure
        return []
    
    def _generate_summary(self, metrics: List[ContentPerformanceMetrics]) -> Dict[str, Any]:
        """Generate performance summary"""
        if not metrics:
            return {}
        
        total_views = sum(m.views for m in metrics)
        total_engagement = sum(m.likes + m.comments + m.shares for m in metrics)
        total_revenue = sum(float(m.revenue_generated) for m in metrics)
        avg_engagement_rate = statistics.mean([m.calculate_engagement_rate() for m in metrics])
        
        return {
            'total_views': total_views,
            'total_engagement': total_engagement,
            'total_revenue': total_revenue,
            'average_engagement_rate': round(avg_engagement_rate, 2),
            'platforms_analyzed': list(set(m.platform for m in metrics)),
            'measurement_points': len(metrics),
            'best_performing_platform': max(metrics, key=lambda m: m.views).platform if metrics else None,
            'viral_content_detected': any(m.viral_score > 80 for m in metrics)
        }
    
    async def _analyze_trends(self, metrics: List[ContentPerformanceMetrics]) -> Dict[str, TrendAnalysis]:
        """Analyze performance trends"""
        trends = {}
        
        if len(metrics) < 2:
            return trends
        
        # Sort metrics by date
        sorted_metrics = sorted(metrics, key=lambda m: m.measured_at)
        
        # Analyze different metric types
        metric_types = [MetricType.VIEWS, MetricType.ENGAGEMENT, MetricType.REVENUE]
        
        for metric_type in metric_types:
            values = []
            timestamps = []
            
            for metric in sorted_metrics:
                if metric_type == MetricType.VIEWS:
                    values.append(metric.views)
                elif metric_type == MetricType.ENGAGEMENT:
                    values.append(metric.likes + metric.comments + metric.shares)
                elif metric_type == MetricType.REVENUE:
                    values.append(float(metric.revenue_generated))
                
                timestamps.append(metric.measured_at)
            
            if len(values) >= 2:
                trend = self._calculate_trend(values, timestamps)
                trends[metric_type.value] = trend
        
        return trends
    
    def _calculate_trend(self, values: List[float], timestamps: List[datetime]) -> TrendAnalysis:
        """Calculate trend for a metric"""
        if len(values) < 2:
            return TrendAnalysis(
                direction=TrendDirection.STABLE,
                velocity=0.0,
                confidence=0.0,
                predicted_next_value=values[0] if values else 0.0
            )
        
        # Calculate rate of change
        recent_values = values[-5:]  # Last 5 measurements
        if len(recent_values) >= 2:
            velocity = (recent_values[-1] - recent_values[0]) / len(recent_values)
        else:
            velocity = values[-1] - values[-2]
        
        # Determine direction
        if abs(velocity) < (statistics.stdev(values) * 0.1):
            direction = TrendDirection.STABLE
        elif velocity > 0:
            direction = TrendDirection.RISING
        else:
            direction = TrendDirection.FALLING
        
        # Calculate confidence based on consistency
        changes = [values[i] - values[i-1] for i in range(1, len(values))]
        consistency = 1.0 - (statistics.stdev(changes) / max(statistics.mean(values), 1))
        confidence = max(0.0, min(1.0, consistency))
        
        # Predict next value
        predicted_next = values[-1] + velocity
        predicted_next = max(0, predicted_next)  # Ensure non-negative
        
        return TrendAnalysis(
            direction=direction,
            velocity=velocity,
            confidence=confidence,
            predicted_next_value=predicted_next
        )
    
    def _analyze_engagement(self, metrics: List[ContentPerformanceMetrics]) -> Dict[str, Any]:
        """Analyze engagement patterns"""
        if not metrics:
            return {}
        
        engagement_rates = [m.calculate_engagement_rate() for m in metrics]
        viral_scores = [m.calculate_viral_score() for m in metrics]
        
        return {
            'average_engagement_rate': statistics.mean(engagement_rates),
            'peak_engagement_rate': max(engagement_rates),
            'engagement_consistency': 1.0 - (statistics.stdev(engagement_rates) / max(statistics.mean(engagement_rates), 1)),
            'viral_potential': max(viral_scores),
            'engagement_growth': self._calculate_growth_rate([m.likes + m.comments + m.shares for m in metrics]),
            'best_engagement_platform': max(metrics, key=lambda m: m.calculate_engagement_rate()).platform,
            'engagement_breakdown': {
                'likes_percentage': statistics.mean([m.likes / max(m.likes + m.comments + m.shares, 1) * 100 for m in metrics]),
                'comments_percentage': statistics.mean([m.comments / max(m.likes + m.comments + m.shares, 1) * 100 for m in metrics]),
                'shares_percentage': statistics.mean([m.shares / max(m.likes + m.comments + m.shares, 1) * 100 for m in metrics])
            }
        }
    
    def _analyze_revenue(self, metrics: List[ContentPerformanceMetrics]) -> Dict[str, Any]:
        """Analyze revenue performance"""
        if not metrics:
            return {}
        
        total_revenue = sum(float(m.revenue_generated) for m in metrics)
        revenue_per_view = total_revenue / max(sum(m.views for m in metrics), 1)
        
        return {
            'total_revenue': total_revenue,
            'revenue_per_view': revenue_per_view,
            'revenue_growth_rate': self._calculate_growth_rate([float(m.revenue_generated) for m in metrics]),
            'best_revenue_platform': max(metrics, key=lambda m: float(m.revenue_generated)).platform if metrics else None,
            'revenue_streams': {
                'ad_revenue': sum(float(m.ad_revenue) for m in metrics),
                'sponsorship_revenue': sum(float(m.sponsorship_revenue) for m in metrics),
                'licensing_revenue': sum(float(m.licensing_revenue) for m in metrics)
            },
            'monetization_rate': len([m for m in metrics if float(m.revenue_generated) > 0]) / len(metrics) * 100
        }
    
    def _analyze_audience(self, metrics: List[ContentPerformanceMetrics]) -> Dict[str, Any]:
        """Analyze audience insights"""
        if not metrics:
            return {}
        
        # Aggregate demographic data
        all_countries = []
        all_age_groups = []
        for metric in metrics:
            all_countries.extend(metric.top_countries)
            all_age_groups.extend(metric.top_age_groups)
        
        country_counts = defaultdict(int)
        age_counts = defaultdict(int)
        
        for country in all_countries:
            country_counts[country] += 1
        
        for age in all_age_groups:
            age_counts[age] += 1
        
        return {
            'top_countries': sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'top_age_groups': sorted(age_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'audience_growth': self._calculate_growth_rate([m.follower_growth for m in metrics]),
            'retention_rate': statistics.mean([m.retention_rate for m in metrics if m.retention_rate > 0]),
            'new_vs_returning': {
                'new_viewers_percentage': statistics.mean([(m.views - m.unique_views) / max(m.views, 1) * 100 for m in metrics]),
                'returning_viewers_percentage': statistics.mean([m.unique_views / max(m.views, 1) * 100 for m in metrics])
            }
        }
    
    def _compare_platforms(self, metrics: List[ContentPerformanceMetrics]) -> Dict[str, Any]:
        """Compare performance across platforms"""
        platform_data = defaultdict(list)
        
        for metric in metrics:
            platform_data[metric.platform].append(metric)
        
        comparison = {}
        for platform, platform_metrics in platform_data.items():
            comparison[platform] = {
                'total_views': sum(m.views for m in platform_metrics),
                'average_engagement_rate': statistics.mean([m.calculate_engagement_rate() for m in platform_metrics]),
                'total_revenue': sum(float(m.revenue_generated) for m in platform_metrics),
                'measurement_count': len(platform_metrics)
            }
        
        return comparison
    
    async def _benchmark_performance(self, metrics: List[ContentPerformanceMetrics]) -> Dict[str, Any]:
        """Benchmark performance against industry standards"""
        # In production, would query benchmark database
        # For now, return placeholder data
        return {
            'industry_percentile': 65,  # 65th percentile
            'performance_level': 'above_average',
            'top_performing_metrics': ['engagement_rate', 'retention_rate'],
            'improvement_opportunities': ['reach', 'conversion_rate']
        }
    
    async def _generate_predictions(self, metrics: List[ContentPerformanceMetrics]) -> Dict[str, Any]:
        """Generate performance predictions"""
        if len(metrics) < 3:
            return {'error': 'Insufficient data for predictions'}
        
        # Simple linear prediction based on recent trends
        recent_views = [m.views for m in metrics[-5:]]
        recent_engagement = [m.likes + m.comments + m.shares for m in metrics[-5:]]
        
        view_trend = self._calculate_growth_rate(recent_views)
        engagement_trend = self._calculate_growth_rate(recent_engagement)
        
        return {
            'next_period_views': recent_views[-1] * (1 + view_trend / 100),
            'next_period_engagement': recent_engagement[-1] * (1 + engagement_trend / 100),
            'confidence_level': 0.7,  # 70% confidence
            'prediction_horizon': '7_days',
            'factors_considered': ['historical_trends', 'seasonality', 'platform_algorithms']
        }
    
    def _generate_recommendations(self, metrics: List[ContentPerformanceMetrics]) -> List[Dict[str, str]]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if not metrics:
            return recommendations
        
        avg_engagement_rate = statistics.mean([m.calculate_engagement_rate() for m in metrics])
        
        if avg_engagement_rate < 2.0:
            recommendations.append({
                'category': 'engagement',
                'priority': 'high',
                'title': 'Improve Engagement Rate',
                'description': 'Your engagement rate is below industry average',
                'action': 'Focus on creating more interactive content and engaging with your audience'
            })
        
        total_revenue = sum(float(m.revenue_generated) for m in metrics)
        if total_revenue == 0:
            recommendations.append({
                'category': 'monetization',
                'priority': 'medium',
                'title': 'Explore Monetization Opportunities',
                'description': 'No revenue detected from content',
                'action': 'Consider enabling ads, sponsorships, or licensing options'
            })
        
        return recommendations
    
    def _detect_anomalies(self, metrics: List[ContentPerformanceMetrics]) -> List[Dict[str, Any]]:
        """Detect performance anomalies"""
        anomalies = []
        
        if len(metrics) < 5:
            return anomalies
        
        # Check for view anomalies
        views = [m.views for m in metrics]
        view_mean = statistics.mean(views)
        view_std = statistics.stdev(views)
        
        for i, metric in enumerate(metrics):
            z_score = abs(metric.views - view_mean) / max(view_std, 1)
            if z_score > self.anomaly_threshold:
                anomalies.append({
                    'type': 'views',
                    'date': metric.measured_at.isoformat(),
                    'value': metric.views,
                    'expected_range': f"{view_mean - view_std:.0f} - {view_mean + view_std:.0f}",
                    'severity': 'high' if z_score > 3 else 'medium'
                })
        
        return anomalies
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate growth rate for a series of values"""
        if len(values) < 2:
            return 0.0
        
        # Remove zeros to avoid division errors
        non_zero_values = [v for v in values if v != 0]
        if len(non_zero_values) < 2:
            return 0.0
        
        start_value = non_zero_values[0]
        end_value = non_zero_values[-1]
        
        growth_rate = ((end_value - start_value) / start_value) * 100
        return growth_rate

class PerformanceReportGenerator:
    """Generate comprehensive performance reports"""
    
    def __init__(self, analyzer: PerformanceAnalyzer = None):
        self.analyzer = analyzer or PerformanceAnalyzer()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def generate_comprehensive_report(self, content_id: str,
                                          report_type: str = 'monthly') -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            # Determine time period based on report type
            if report_type == 'daily':
                start_date = datetime.utcnow() - timedelta(days=1)
            elif report_type == 'weekly':
                start_date = datetime.utcnow() - timedelta(weeks=1)
            elif report_type == 'monthly':
                start_date = datetime.utcnow() - timedelta(days=30)
            elif report_type == 'quarterly':
                start_date = datetime.utcnow() - timedelta(days=90)
            else:
                start_date = datetime.utcnow() - timedelta(days=30)
            
            # Perform analysis
            analysis = await self.analyzer.analyze_content_performance(
                content_id, start_date
            )
            
            # Generate report
            report = {
                'report_metadata': {
                    'content_id': content_id,
                    'report_type': report_type,
                    'generated_at': datetime.utcnow().isoformat(),
                    'period_analyzed': analysis.get('analysis_period', {}),
                    'data_points': analysis.get('summary', {}).get('measurement_points', 0)
                },
                'executive_summary': self._generate_executive_summary(analysis),
                'detailed_analysis': analysis,
                'visualizations': self._generate_visualization_config(analysis),
                'action_items': self._generate_action_items(analysis),
                'next_steps': self._generate_next_steps(analysis)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise
    
    def _generate_executive_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        summary = analysis.get('summary', {})
        trends = analysis.get('trends', {})
        
        return {
            'key_metrics': {
                'total_views': summary.get('total_views', 0),
                'total_engagement': summary.get('total_engagement', 0),
                'total_revenue': summary.get('total_revenue', 0),
                'engagement_rate': summary.get('average_engagement_rate', 0)
            },
            'performance_highlights': [
                f"Content generated {summary.get('total_views', 0):,} views",
                f"Achieved {summary.get('average_engagement_rate', 0):.1f}% average engagement rate",
                f"Active on {len(summary.get('platforms_analyzed', []))} platforms"
            ],
            'key_trends': {
                'views_trend': trends.get('views', {}).get('direction', 'stable'),
                'engagement_trend': trends.get('engagement', {}).get('direction', 'stable'),
                'revenue_trend': trends.get('revenue', {}).get('direction', 'stable')
            },
            'recommendations_count': len(analysis.get('recommendations', [])),
            'anomalies_detected': len(analysis.get('anomalies', []))
        }
    
    def _generate_visualization_config(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate configuration for data visualizations"""
        return {
            'charts': [
                {
                    'type': 'line',
                    'title': 'Views Over Time',
                    'data_source': 'metrics.views',
                    'x_axis': 'date',
                    'y_axis': 'views'
                },
                {
                    'type': 'bar',
                    'title': 'Platform Comparison',
                    'data_source': 'platform_comparison',
                    'x_axis': 'platform',
                    'y_axis': 'total_views'
                },
                {
                    'type': 'pie',
                    'title': 'Revenue Sources',
                    'data_source': 'revenue_analysis.revenue_streams'
                },
                {
                    'type': 'scatter',
                    'title': 'Engagement vs Views',
                    'data_source': 'metrics',
                    'x_axis': 'views',
                    'y_axis': 'engagement_rate'
                }
            ],
            'dashboards': [
                'performance_overview',
                'engagement_deep_dive',
                'revenue_analytics',
                'audience_insights'
            ]
        }
    
    def _generate_action_items(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable items from analysis"""
        action_items = []
        recommendations = analysis.get('recommendations', [])
        
        for rec in recommendations:
            action_items.append({
                'priority': rec.get('priority', 'medium'),
                'category': rec.get('category', 'general'),
                'action': rec.get('action', rec.get('title', '')),
                'expected_outcome': rec.get('description', ''),
                'timeline': 'next_7_days'
            })
        
        # Add anomaly-based action items
        anomalies = analysis.get('anomalies', [])
        if anomalies:
            action_items.append({
                'priority': 'high',
                'category': 'investigation',
                'action': f'Investigate {len(anomalies)} performance anomalies detected',
                'expected_outcome': 'Understand unusual performance patterns',
                'timeline': 'immediate'
            })
        
        return action_items
    
    def _generate_next_steps(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate next steps recommendations"""
        next_steps = []
        
        summary = analysis.get('summary', {})
        
        if summary.get('viral_content_detected'):
            next_steps.append("Capitalize on viral content momentum with follow-up posts")
        
        if len(summary.get('platforms_analyzed', [])) < 3:
            next_steps.append("Expand content distribution to additional platforms")
        
        engagement_analysis = analysis.get('engagement_analysis', {})
        if engagement_analysis.get('average_engagement_rate', 0) < 2.0:
            next_steps.append("Implement engagement improvement strategies")
        
        revenue_analysis = analysis.get('revenue_analysis', {})
        if revenue_analysis.get('total_revenue', 0) == 0:
            next_steps.append("Explore monetization opportunities")
        
        return next_steps

# Export all classes and enums
__all__ = [
    'MetricType',
    'TimeFrame',
    'PlatformMetrics',
    'TrendDirection',
    'PerformanceLevel',
    'MetricSnapshot',
    'TrendAnalysis',
    'ContentPerformanceMetrics',
    'PerformanceTrend',
    'PerformanceBenchmark',
    'PerformanceAnalyzer',
    'PerformanceReportGenerator'
]
