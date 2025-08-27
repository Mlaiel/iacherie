"""
Analytics Data Model
===================

Professional analytics data model for comprehensive performance tracking.
Advanced metrics, insights, and predictive analytics for content creators.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  STRICT WARNING FOR UNAUTHORIZED USE:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use without explicit written 
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

from datetime import datetime, date
from typing import Optional, Dict, List, Any
from decimal import Decimal
from enum import Enum

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, JSON, DECIMAL, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

Base = declarative_base()


class AnalyticsType(Enum):
    """Analytics type enumeration"""
    PERFORMANCE = "performance"
    AUDIENCE = "audience"
    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    GROWTH = "growth"
    CONTENT = "content"
    PLATFORM = "platform"
    GEOGRAPHIC = "geographic"
    DEMOGRAPHIC = "demographic"
    BEHAVIORAL = "behavioral"
    PREDICTIVE = "predictive"
    COMPARATIVE = "comparative"


class MetricType(Enum):
    """Metric type enumeration"""
    VIEWS = "views"
    PLAYS = "plays"
    STREAMS = "streams"
    DOWNLOADS = "downloads"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    FOLLOWERS = "followers"
    SUBSCRIBERS = "subscribers"
    IMPRESSIONS = "impressions"
    REACH = "reach"
    CLICKS = "clicks"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    RETENTION = "retention"
    ENGAGEMENT_RATE = "engagement_rate"
    GROWTH_RATE = "growth_rate"
    VIRALITY = "virality"


class TimeGranularity(Enum):
    """Time granularity enumeration"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    REAL_TIME = "real_time"


class AnalyticsModel(Base):
    """
    Professional analytics data model for IA Influencer Agent platform.
    
    Comprehensive analytics tracking with multi-dimensional metrics,
    audience insights, performance analytics, and predictive modeling.
    """
    
    __tablename__ = "analytics"
    
    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(String(36), ForeignKey("content.id"), index=True)
    
    # Analytics basic information
    analytics_type = Column(String(30), nullable=False)  # AnalyticsType
    metric_type = Column(String(30), nullable=False)  # MetricType
    time_granularity = Column(String(20), default=TimeGranularity.DAILY.value)
    
    # Time period
    measurement_date = Column(Date, nullable=False, index=True)
    measurement_hour = Column(Integer)  # 0-23 for hourly granularity
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Platform and source information
    platform = Column(String(50))  # YouTube, Spotify, Instagram, etc.
    platform_account_id = Column(String(100))
    data_source = Column(String(50))  # API, manual, estimated
    data_quality_score = Column(Float, default=100.0)  # 0-100
    
    # Core metrics
    value = Column(DECIMAL(15, 4), nullable=False)  # Primary metric value
    previous_value = Column(DECIMAL(15, 4))  # Previous period value
    change_absolute = Column(DECIMAL(15, 4))  # Absolute change
    change_percentage = Column(DECIMAL(8, 4))  # Percentage change
    trend_direction = Column(String(20))  # up, down, stable
    
    # Engagement metrics
    views_count = Column(Integer, default=0)
    unique_views_count = Column(Integer, default=0)
    plays_count = Column(Integer, default=0)
    complete_plays_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    dislikes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    saves_count = Column(Integer, default=0)
    
    # Reach and impressions
    impressions_count = Column(Integer, default=0)
    reach_count = Column(Integer, default=0)
    organic_reach = Column(Integer, default=0)
    paid_reach = Column(Integer, default=0)
    viral_reach = Column(Integer, default=0)
    
    # Audience metrics
    followers_gained = Column(Integer, default=0)
    followers_lost = Column(Integer, default=0)
    net_followers_change = Column(Integer, default=0)
    total_followers = Column(Integer, default=0)
    active_followers = Column(Integer, default=0)
    
    # Performance rates
    engagement_rate = Column(DECIMAL(8, 4), default=0)  # %
    click_through_rate = Column(DECIMAL(8, 4), default=0)  # %
    conversion_rate = Column(DECIMAL(8, 4), default=0)  # %
    retention_rate = Column(DECIMAL(8, 4), default=0)  # %
    bounce_rate = Column(DECIMAL(8, 4), default=0)  # %
    completion_rate = Column(DECIMAL(8, 4), default=0)  # %
    
    # Time-based metrics
    average_view_duration = Column(Float)  # seconds
    total_watch_time = Column(Integer)  # seconds
    session_duration = Column(Float)  # seconds
    time_to_engagement = Column(Float)  # seconds
    
    # Revenue metrics
    revenue_generated = Column(DECIMAL(12, 4), default=0)
    revenue_per_view = Column(DECIMAL(10, 6))
    revenue_per_engagement = Column(DECIMAL(10, 6))
    cost_per_acquisition = Column(DECIMAL(10, 4))
    lifetime_value = Column(DECIMAL(12, 4))
    
    # Geographic breakdown
    top_countries = Column(JSON)  # Top performing countries
    top_cities = Column(JSON)  # Top performing cities
    geographic_distribution = Column(JSON)  # Full geographic breakdown
    
    # Demographic breakdown
    age_demographics = Column(JSON)  # Age group distribution
    gender_demographics = Column(JSON)  # Gender distribution
    language_demographics = Column(JSON)  # Language preferences
    device_demographics = Column(JSON)  # Device usage
    
    # Behavioral analytics
    traffic_sources = Column(JSON)  # How users found content
    user_journey = Column(JSON)  # User interaction patterns
    content_preferences = Column(JSON)  # Preferred content types
    engagement_patterns = Column(JSON)  # When users engage
    retention_cohorts = Column(JSON)  # Retention by user cohort
    
    # Content performance
    content_category = Column(String(100))
    content_tags = Column(ARRAY(String))
    content_quality_score = Column(Float)  # AI-assessed quality
    virality_score = Column(Float)  # Viral potential score
    trend_score = Column(Float)  # Trending score
    
    # Comparative analytics
    industry_percentile = Column(Float)  # Performance vs industry
    peer_comparison = Column(JSON)  # Comparison with similar creators
    historical_ranking = Column(Integer)  # Historical performance ranking
    competitive_position = Column(String(20))  # leading, following, etc.
    
    # Predictive analytics
    predicted_growth = Column(DECIMAL(8, 4))  # Predicted growth rate
    forecast_confidence = Column(Float)  # Prediction confidence %
    seasonality_factor = Column(DECIMAL(6, 4))  # Seasonal adjustment
    trend_momentum = Column(Float)  # Trend strength
    predicted_metrics = Column(JSON)  # Future metric predictions
    
    # AI and ML insights
    ai_insights = Column(JSON)  # AI-generated insights
    anomaly_detected = Column(Boolean, default=False)
    anomaly_score = Column(Float)  # Anomaly strength
    pattern_recognition = Column(JSON)  # Detected patterns
    recommendation_score = Column(Float)  # Content recommendation score
    
    # Quality and validation
    data_completeness = Column(Float, default=100.0)  # % of expected data
    validation_status = Column(String(20), default="unvalidated")
    confidence_interval = Column(JSON)  # Statistical confidence
    margin_of_error = Column(DECIMAL(6, 4))  # Statistical margin
    
    # Aggregation and rollup
    is_aggregated = Column(Boolean, default=False)
    aggregation_level = Column(String(20))  # daily, weekly, monthly
    child_analytics_count = Column(Integer, default=0)
    rollup_method = Column(String(30))  # sum, average, max, etc.
    
    # External benchmarks
    industry_average = Column(DECIMAL(15, 4))
    market_benchmark = Column(DECIMAL(15, 4))
    platform_average = Column(DECIMAL(15, 4))
    percentile_rank = Column(Float)  # 0-100 percentile
    
    # Metadata and context
    metadata = Column(JSON)  # Flexible metadata storage
    tags = Column(ARRAY(String))  # Analytics tags
    notes = Column(Text)  # Analysis notes
    context = Column(JSON)  # Additional context
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)  # When analytics were processed
    last_calculated_at = Column(DateTime)  # Last calculation time
    
    # Soft delete
    deleted_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="analytics")
    content = relationship("ContentModel", back_populates="analytics")
    
    def __repr__(self):
        return f"<AnalyticsModel(id='{self.id}', type='{self.analytics_type}', metric='{self.metric_type}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_id': self.content_id,
            'analytics_type': self.analytics_type,
            'metric_type': self.metric_type,
            'time_granularity': self.time_granularity,
            'measurement_date': self.measurement_date.isoformat() if self.measurement_date else None,
            'measurement_hour': self.measurement_hour,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'platform': self.platform,
            'value': float(self.value) if self.value else 0.0,
            'previous_value': float(self.previous_value) if self.previous_value else None,
            'change_absolute': float(self.change_absolute) if self.change_absolute else None,
            'change_percentage': float(self.change_percentage) if self.change_percentage else None,
            'trend_direction': self.trend_direction,
            'views_count': self.views_count,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'shares_count': self.shares_count,
            'impressions_count': self.impressions_count,
            'reach_count': self.reach_count,
            'engagement_rate': float(self.engagement_rate) if self.engagement_rate else 0.0,
            'click_through_rate': float(self.click_through_rate) if self.click_through_rate else 0.0,
            'conversion_rate': float(self.conversion_rate) if self.conversion_rate else 0.0,
            'retention_rate': float(self.retention_rate) if self.retention_rate else 0.0,
            'average_view_duration': self.average_view_duration,
            'total_watch_time': self.total_watch_time,
            'revenue_generated': float(self.revenue_generated) if self.revenue_generated else 0.0,
            'top_countries': self.top_countries,
            'age_demographics': self.age_demographics,
            'gender_demographics': self.gender_demographics,
            'traffic_sources': self.traffic_sources,
            'content_quality_score': self.content_quality_score,
            'virality_score': self.virality_score,
            'industry_percentile': self.industry_percentile,
            'predicted_growth': float(self.predicted_growth) if self.predicted_growth else None,
            'forecast_confidence': self.forecast_confidence,
            'ai_insights': self.ai_insights,
            'anomaly_detected': self.anomaly_detected,
            'data_quality_score': self.data_quality_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted
        }
    
    @property
    def is_performance_analytics(self) -> bool:
        """Check if analytics is performance type"""
        return self.analytics_type == AnalyticsType.PERFORMANCE.value
    
    @property
    def is_audience_analytics(self) -> bool:
        """Check if analytics is audience type"""
        return self.analytics_type == AnalyticsType.AUDIENCE.value
    
    @property
    def is_revenue_analytics(self) -> bool:
        """Check if analytics is revenue type"""
        return self.analytics_type == AnalyticsType.REVENUE.value
    
    @property
    def is_trending_up(self) -> bool:
        """Check if metric is trending upward"""
        return self.trend_direction == "up"
    
    @property
    def is_trending_down(self) -> bool:
        """Check if metric is trending downward"""
        return self.trend_direction == "down"
    
    @property
    def has_significant_change(self) -> bool:
        """Check if change is statistically significant"""
        if self.change_percentage:
            return abs(float(self.change_percentage)) >= 5.0  # 5% threshold
        return False
    
    @property
    def value_formatted(self) -> str:
        """Get formatted value with appropriate units"""
        if not self.value:
            return "0"
        
        value = float(self.value)
        
        # Format based on metric type
        if self.metric_type in [MetricType.REVENUE.value]:
            return f"€{value:,.2f}"
        elif self.metric_type in [MetricType.ENGAGEMENT_RATE.value, MetricType.GROWTH_RATE.value]:
            return f"{value:.2f}%"
        elif value >= 1000000:
            return f"{value/1000000:.1f}M"
        elif value >= 1000:
            return f"{value/1000:.1f}K"
        else:
            return f"{value:,.0f}"
    
    @property
    def change_formatted(self) -> str:
        """Get formatted change with direction indicator"""
        if not self.change_percentage:
            return "0%"
        
        change = float(self.change_percentage)
        direction = "▲" if change > 0 else "▼" if change < 0 else "→"
        return f"{direction} {abs(change):.1f}%"
    
    @property
    def performance_grade(self) -> str:
        """Get performance grade based on industry percentile"""
        if not self.industry_percentile:
            return "N/A"
        
        percentile = self.industry_percentile
        if percentile >= 90:
            return "A+"
        elif percentile >= 80:
            return "A"
        elif percentile >= 70:
            return "B+"
        elif percentile >= 60:
            return "B"
        elif percentile >= 50:
            return "C+"
        elif percentile >= 40:
            return "C"
        elif percentile >= 30:
            return "D+"
        elif percentile >= 20:
            return "D"
        else:
            return "F"
    
    @property
    def engagement_level(self) -> str:
        """Get engagement level category"""
        if not self.engagement_rate:
            return "Unknown"
        
        rate = float(self.engagement_rate)
        if rate >= 10.0:
            return "Exceptional"
        elif rate >= 5.0:
            return "High"
        elif rate >= 2.0:
            return "Good"
        elif rate >= 1.0:
            return "Average"
        elif rate >= 0.5:
            return "Low"
        else:
            return "Very Low"
    
    def calculate_change(self):
        """Calculate change metrics from previous value"""
        if self.previous_value and self.value:
            self.change_absolute = self.value - self.previous_value
            
            if self.previous_value != 0:
                self.change_percentage = (self.change_absolute / self.previous_value) * 100
            
            # Determine trend direction
            if self.change_absolute > 0:
                self.trend_direction = "up"
            elif self.change_absolute < 0:
                self.trend_direction = "down"
            else:
                self.trend_direction = "stable"
        
        self.updated_at = datetime.utcnow()
    
    def calculate_engagement_rate(self):
        """Calculate engagement rate based on available metrics"""
        if self.impressions_count and self.impressions_count > 0:
            total_engagements = (
                (self.likes_count or 0) +
                (self.comments_count or 0) +
                (self.shares_count or 0) +
                (self.saves_count or 0)
            )
            self.engagement_rate = (total_engagements / self.impressions_count) * 100
        elif self.views_count and self.views_count > 0:
            total_engagements = (
                (self.likes_count or 0) +
                (self.comments_count or 0) +
                (self.shares_count or 0)
            )
            self.engagement_rate = (total_engagements / self.views_count) * 100
        
        self.updated_at = datetime.utcnow()
    
    def calculate_retention_rate(self):
        """Calculate content retention rate"""
        if self.complete_plays_count and self.plays_count and self.plays_count > 0:
            self.retention_rate = (self.complete_plays_count / self.plays_count) * 100
        elif self.average_view_duration and self.content:
            # Simplified retention based on view duration vs content duration
            if hasattr(self.content, 'duration') and self.content.duration:
                self.retention_rate = min(100, (self.average_view_duration / self.content.duration) * 100)
        
        self.updated_at = datetime.utcnow()
    
    def set_demographic_data(self, demographics: Dict[str, Any]):
        """Set demographic breakdown data"""
        if 'age' in demographics:
            self.age_demographics = demographics['age']
        if 'gender' in demographics:
            self.gender_demographics = demographics['gender']
        if 'language' in demographics:
            self.language_demographics = demographics['language']
        if 'device' in demographics:
            self.device_demographics = demographics['device']
        
        self.updated_at = datetime.utcnow()
    
    def set_geographic_data(self, geographic: Dict[str, Any]):
        """Set geographic breakdown data"""
        if 'countries' in geographic:
            self.top_countries = geographic['countries']
        if 'cities' in geographic:
            self.top_cities = geographic['cities']
        if 'distribution' in geographic:
            self.geographic_distribution = geographic['distribution']
        
        self.updated_at = datetime.utcnow()
    
    def set_ai_insights(self, insights: List[str], scores: Dict[str, float] = None):
        """Set AI-generated insights"""
        self.ai_insights = {
            'insights': insights,
            'generated_at': datetime.utcnow().isoformat(),
            'scores': scores or {}
        }
        
        if scores:
            if 'quality' in scores:
                self.content_quality_score = scores['quality']
            if 'virality' in scores:
                self.virality_score = scores['virality']
            if 'trend' in scores:
                self.trend_score = scores['trend']
        
        self.updated_at = datetime.utcnow()
    
    def detect_anomaly(self, threshold: float = 2.0):
        """Detect anomalies in metrics"""
        if not self.previous_value or not self.value:
            return False
        
        # Simple z-score based anomaly detection
        change_ratio = abs(float(self.value) / float(self.previous_value))
        
        if change_ratio > threshold or change_ratio < (1 / threshold):
            self.anomaly_detected = True
            self.anomaly_score = change_ratio
            self.updated_at = datetime.utcnow()
            return True
        
        return False
    
    def set_predictions(self, predictions: Dict[str, Any], confidence: float):
        """Set predictive analytics data"""
        self.predicted_metrics = predictions
        self.forecast_confidence = confidence
        
        if 'growth_rate' in predictions:
            self.predicted_growth = Decimal(str(predictions['growth_rate']))
        
        self.updated_at = datetime.utcnow()
    
    def compare_to_industry(self, industry_avg: Decimal, percentile: float):
        """Set industry comparison data"""
        self.industry_average = industry_avg
        self.industry_percentile = percentile
        
        # Determine competitive position
        if percentile >= 90:
            self.competitive_position = "leading"
        elif percentile >= 75:
            self.competitive_position = "strong"
        elif percentile >= 50:
            self.competitive_position = "average"
        elif percentile >= 25:
            self.competitive_position = "below_average"
        else:
            self.competitive_position = "lagging"
        
        self.updated_at = datetime.utcnow()
    
    def aggregate_from_children(self, child_analytics: List['AnalyticsModel']):
        """Aggregate analytics from child records"""
        if not child_analytics:
            return
        
        # Sum numeric values
        total_value = sum(a.value for a in child_analytics if a.value)
        self.value = Decimal(str(total_value))
        
        # Aggregate other metrics
        self.views_count = sum(a.views_count or 0 for a in child_analytics)
        self.likes_count = sum(a.likes_count or 0 for a in child_analytics)
        self.comments_count = sum(a.comments_count or 0 for a in child_analytics)
        self.shares_count = sum(a.shares_count or 0 for a in child_analytics)
        self.impressions_count = sum(a.impressions_count or 0 for a in child_analytics)
        
        # Calculate weighted averages for rates
        if self.impressions_count > 0:
            self.calculate_engagement_rate()
        
        self.is_aggregated = True
        self.child_analytics_count = len(child_analytics)
        self.updated_at = datetime.utcnow()
    
    def validate_data_quality(self):
        """Validate and score data quality"""
        score = 100.0
        required_fields = ['value', 'period_start', 'period_end', 'analytics_type', 'metric_type']
        
        # Check required fields
        for field in required_fields:
            if not getattr(self, field):
                score -= 20
        
        # Check data consistency
        if self.change_percentage and not self.previous_value:
            score -= 10
        
        if self.engagement_rate and not self.impressions_count and not self.views_count:
            score -= 10
        
        # Check for impossible values
        if self.engagement_rate and self.engagement_rate > 100:
            score -= 20
        
        if self.retention_rate and self.retention_rate > 100:
            score -= 20
        
        self.data_quality_score = max(0.0, score)
        self.updated_at = datetime.utcnow()
    
    def soft_delete(self):
        """Soft delete analytics record"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def restore(self):
        """Restore soft-deleted analytics record"""
        self.is_deleted = False
        self.deleted_at = None
        self.updated_at = datetime.utcnow()
