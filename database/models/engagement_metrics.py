"""Engagement Metrics Database Model

Enterprise-grade SQLAlchemy model for tracking comprehensive engagement metrics,
analytics, and performance indicators across all platforms and content types.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class MetricType(Enum):
    """Engagement metric type enumeration"""    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    SAVES = "saves"
    DOWNLOADS = "downloads"
    PLAYS = "plays"
    STREAMS = "streams"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    REACTIONS = "reactions"
    FOLLOWS = "follows"
    UNFOLLOWS = "unfollows"
    MENTIONS = "mentions"
    TAGS = "tags"
    REPOSTS = "reposts"
    STORY_VIEWS = "story_views"
    PROFILE_VISITS = "profile_visits"
    WEBSITE_CLICKS = "website_clicks"


class Platform(Enum):
    """Platform enumeration"""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    TUMBLR = "tumblr"
    VIMEO = "vimeo"
    PATREON = "patreon"
    SUBSTACK = "substack"
    MEDIUM = "medium"
    PODCAST = "podcast"
    WEBSITE = "website"
    EMAIL = "email"
    ALL_PLATFORMS = "all_platforms"


class TimeFrame(Enum):
    """Time frame for metrics aggregation"""    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    REAL_TIME = "real_time"
    CUSTOM = "custom"


class AudienceSegment(Enum):
    """Audience segment enumeration"""    ALL = "all"
    AGE_13_17 = "age_13_17"
    AGE_18_24 = "age_18_24"
    AGE_25_34 = "age_25_34"
    AGE_35_44 = "age_35_44"
    AGE_45_54 = "age_45_54"
    AGE_55_PLUS = "age_55_plus"
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    NEW_FOLLOWERS = "new_followers"
    RETURNING_USERS = "returning_users"
    PREMIUM_USERS = "premium_users"
    FREE_USERS = "free_users"
    GEOGRAPHIC = "geographic"
    INTEREST_BASED = "interest_based"


class EngagementQuality(Enum):
    """Engagement quality enumeration"""    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    POOR = "poor"
    SPAM = "spam"
    AUTHENTIC = "authentic"
    ORGANIC = "organic"
    PAID = "paid"
    BOT_SUSPECTED = "bot_suspected"


class TrendDirection(Enum):
    """Trend direction enumeration"""    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"
    EXPONENTIAL = "exponential"
    DECLINING = "declining"
    SEASONAL = "seasonal"
    CYCLICAL = "cyclical"


class EngagementMetrics(Base):
    """    Enterprise Engagement Metrics Model
    
    Comprehensive engagement tracking with real-time analytics,
    trend analysis, audience segmentation, and performance insights.
    """    __tablename__ = 'engagement_metrics'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # References
    content_id = Column(UUID(as_uuid=True), ForeignKey('user_contents.id'), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_profile_id = Column(UUID(as_uuid=True), ForeignKey('creator_profiles.id'), nullable=True, index=True)
    distribution_id = Column(UUID(as_uuid=True), ForeignKey('content_distributions.id'), nullable=True, index=True)
    
    # Metric classification
    metric_type = Column(SQLEnum(MetricType), nullable=False, index=True)
    platform = Column(SQLEnum(Platform), nullable=False, index=True)
    time_frame = Column(SQLEnum(TimeFrame), nullable=False, default=TimeFrame.DAILY, index=True)
    audience_segment = Column(SQLEnum(AudienceSegment), nullable=False, default=AudienceSegment.ALL, index=True)
    
    # Timing information
    recorded_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Core metric values
    value = Column(Integer, nullable=False, default=0)
    previous_value = Column(Integer, nullable=True)
    percentage_change = Column(Float, nullable=True)
    absolute_change = Column(Integer, nullable=True)
    
    # Calculated metrics
    rate = Column(Float, nullable=True)  # Rate per hour/day/etc
    normalized_value = Column(Float, nullable=True)  # Normalized to 0-100 scale
    percentile_rank = Column(Float, nullable=True)  # Percentile among similar content
    z_score = Column(Float, nullable=True)  # Statistical z-score
    
    # Quality metrics
    engagement_quality = Column(SQLEnum(EngagementQuality), nullable=False, default=EngagementQuality.AVERAGE, index=True)
    authenticity_score = Column(Float, nullable=True)  # 0-100 authenticity
    organic_percentage = Column(Float, nullable=True)  # % organic vs paid
    bot_detection_score = Column(Float, nullable=True)  # 0-100 bot likelihood
    
    # Trend analysis
    trend_direction = Column(SQLEnum(TrendDirection), nullable=True, index=True)
    trend_strength = Column(Float, nullable=True)  # 0-1 strength
    trend_velocity = Column(Float, nullable=True)  # Rate of change
    volatility_index = Column(Float, nullable=True)  # Stability measure
    momentum_score = Column(Float, nullable=True)  # Momentum indicator
    
    # Comparative analytics
    benchmark_value = Column(Integer, nullable=True)  # Industry benchmark
    competitor_average = Column(Float, nullable=True)
    platform_average = Column(Float, nullable=True)
    personal_best = Column(Integer, nullable=True)
    performance_vs_benchmark = Column(Float, nullable=True)  # % vs benchmark
    
    # Audience insights
    unique_users = Column(Integer, nullable=True)
    returning_users = Column(Integer, nullable=True)
    new_users = Column(Integer, nullable=True)
    user_retention_rate = Column(Float, nullable=True)
    audience_overlap = Column(Float, nullable=True)  # With other content
    
    # Geographic metrics
    top_countries = Column(JSONB, nullable=True)  # {country: count}
    top_cities = Column(JSONB, nullable=True)  # {city: count}
    geographic_distribution = Column(JSONB, nullable=True)
    international_percentage = Column(Float, nullable=True)
    
    # Temporal patterns
    hourly_distribution = Column(JSONB, nullable=True)  # Hour of day patterns
    daily_distribution = Column(JSONB, nullable=True)   # Day of week patterns
    seasonal_patterns = Column(JSONB, nullable=True)
    peak_hours = Column(ARRAY(Integer), nullable=True)  # Best performing hours
    
    # Platform-specific metrics
    platform_specific_data = Column(JSONB, nullable=True)
    algorithm_score = Column(Float, nullable=True)
    viral_coefficient = Column(Float, nullable=True)
    shareability_index = Column(Float, nullable=True)
    stickiness_factor = Column(Float, nullable=True)
    
    # Revenue correlation
    revenue_generated = Column(Numeric(10, 2), nullable=True)
    cost_per_engagement = Column(Numeric(8, 2), nullable=True)
    roi_percentage = Column(Float, nullable=True)
    conversion_rate = Column(Float, nullable=True)
    click_through_rate = Column(Float, nullable=True)
    
    # Advanced analytics
    sentiment_analysis = Column(JSONB, nullable=True)  # Comment sentiment
    topic_analysis = Column(JSONB, nullable=True)     # Content topics
    influence_score = Column(Float, nullable=True)     # Influence measurement
    reach_efficiency = Column(Float, nullable=True)    # Reach per follower
    
    # Engagement patterns
    engagement_velocity = Column(Float, nullable=True)  # Speed of engagement
    engagement_decay = Column(Float, nullable=True)     # How quickly it drops
    viral_timeline = Column(JSONB, nullable=True)       # Viral spread timeline
    peak_engagement_time = Column(DateTime(timezone=True), nullable=True)
    
    # Audience behavior
    average_watch_time = Column(Integer, nullable=True)  # Seconds
    completion_rate = Column(Float, nullable=True)       # % who finished
    replay_rate = Column(Float, nullable=True)           # % who replayed
    skip_rate = Column(Float, nullable=True)             # % who skipped
    interaction_depth = Column(Float, nullable=True)     # Depth of interaction
    
    # Cross-platform metrics
    cross_platform_reach = Column(Integer, nullable=True)
    platform_contribution = Column(Float, nullable=True)  # % of total engagement
    platform_efficiency = Column(Float, nullable=True)    # Engagement per follower
    cannibalization_effect = Column(Float, nullable=True) # Impact on other platforms
    
    # Predictive metrics
    predicted_24h = Column(Integer, nullable=True)        # 24h prediction
    predicted_7d = Column(Integer, nullable=True)         # 7 day prediction
    predicted_30d = Column(Integer, nullable=True)        # 30 day prediction
    confidence_interval = Column(Float, nullable=True)    # Prediction confidence
    
    # Quality assurance
    data_quality_score = Column(Float, nullable=False, default=100.0)
    anomaly_detected = Column(Boolean, nullable=False, default=False)
    anomaly_score = Column(Float, nullable=True)
    validation_status = Column(String(50), nullable=False, default="valid")
    
    # Data source tracking
    data_source = Column(String(100), nullable=False)
    collection_method = Column(String(100), nullable=False, default="api")
    data_freshness = Column(Integer, nullable=True)  # Minutes since collection
    api_rate_limit_hit = Column(Boolean, nullable=False, default=False)
    
    # Metadata
    tags = Column(ARRAY(String), nullable=True)
    notes = Column(Text, nullable=True)
    external_references = Column(JSONB, nullable=True)
    custom_attributes = Column(JSONB, nullable=True)
    
    # Administrative fields
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_public = Column(Boolean, nullable=False, default=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_anomaly = Column(Boolean, nullable=False, default=False, index=True)
    
    # Audit trail
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=True)
    collection_source = Column(String(100), nullable=False, default="automated")
    version = Column(String(20), nullable=False, default="1.0.0")
    
    # Advanced indexing
    __table_args__ = (
        Index('idx_engagement_metrics_content_platform', 'content_id', 'platform'),
        Index('idx_engagement_metrics_user_type', 'user_id', 'metric_type'),
        Index('idx_engagement_metrics_time_period', 'recorded_at', 'time_frame'),
        Index('idx_engagement_metrics_platform_segment', 'platform', 'audience_segment'),
        Index('idx_engagement_metrics_trend_direction', 'trend_direction', 'trend_strength'),
        Index('idx_engagement_metrics_quality', 'engagement_quality', 'authenticity_score'),
        Index('idx_engagement_metrics_performance', 'value', 'percentile_rank'),
        Index('idx_engagement_metrics_period_range', 'period_start', 'period_end'),
        Index('idx_engagement_metrics_revenue', 'revenue_generated'),
        Index('idx_engagement_metrics_anomaly', 'is_anomaly', 'anomaly_score'),
    )
    
    # Relationships
    content = relationship("UserContent", back_populates="engagement_metrics")
    creator_profile = relationship("CreatorProfile", back_populates="engagement_metrics")
    distribution = relationship("ContentDistribution", back_populates="engagement_metrics")
    
    def __repr__(self):
        return f"<EngagementMetrics(id={self.id}, type={self.metric_type.value}, platform={self.platform.value}, value={self.value})>"
    
    @classmethod
    def record_metric(
        cls, 
        user_id: str, 
        metric_type: MetricType, 
        platform: Platform, 
        value: int,
        period_start: datetime,
        period_end: datetime,
        **kwargs
    ) -> 'EngagementMetrics':
        """Record a new engagement metric"""        return cls(
            user_id=user_id,
            metric_type=metric_type,
            platform=platform,
            value=value,
            period_start=period_start,
            period_end=period_end,
            metric_id=f"{metric_type.value}_{platform.value}_{int(datetime.now().timestamp())}",
            created_by=kwargs.get('created_by', 'system'),
            **{k: v for k, v in kwargs.items() if k != 'created_by'}
        )
    
    def calculate_percentage_change(self) -> float:
        """Calculate percentage change from previous value"""        if self.previous_value and self.previous_value > 0:
            self.percentage_change = ((self.value - self.previous_value) / self.previous_value) * 100
            self.absolute_change = self.value - self.previous_value
        else:
            self.percentage_change = 0.0
            self.absolute_change = self.value
        
        return self.percentage_change
    
    def calculate_engagement_rate(self, total_followers: int) -> float:
        """Calculate engagement rate based on followers"""        if total_followers > 0:
            self.rate = (self.value / total_followers) * 100
        else:
            self.rate = 0.0
        
        return self.rate
    
    def detect_anomaly(self, threshold: float = 2.0) -> bool:
        """Detect if metric value is anomalous using z-score"""        if self.z_score and abs(self.z_score) > threshold:
            self.is_anomaly = True
            self.anomaly_score = abs(self.z_score)
            self.anomaly_detected = True
        else:
            self.is_anomaly = False
            self.anomaly_detected = False
        
        return self.is_anomaly
    
    def update_trend_analysis(self, historical_values: List[int]) -> None:
        """Update trend analysis based on historical data"""        if len(historical_values) < 2:
            return
        
        # Calculate trend direction
        recent_trend = sum(historical_values[-3:]) / 3 if len(historical_values) >= 3 else historical_values[-1]
        older_trend = sum(historical_values[-6:-3]) / 3 if len(historical_values) >= 6 else historical_values[0]
        
        if recent_trend > older_trend * 1.1:
            self.trend_direction = TrendDirection.RISING
        elif recent_trend < older_trend * 0.9:
            self.trend_direction = TrendDirection.FALLING
        else:
            self.trend_direction = TrendDirection.STABLE
        
        # Calculate trend strength
        if len(historical_values) > 1:
            variance = sum((x - sum(historical_values)/len(historical_values))**2 for x in historical_values) / len(historical_values)
            self.volatility_index = variance / (sum(historical_values)/len(historical_values)) if sum(historical_values) > 0 else 0
        
        # Calculate velocity
        if len(historical_values) >= 2:
            self.trend_velocity = (historical_values[-1] - historical_values[-2]) / max(1, historical_values[-2])
    
    def calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""        scores = []
        
        # Percentile rank contribution
        if self.percentile_rank is not None:
            scores.append(self.percentile_rank)
        
        # Engagement quality contribution
        quality_scores = {
            EngagementQuality.EXCELLENT: 100,
            EngagementQuality.GOOD: 80,
            EngagementQuality.AVERAGE: 60,
            EngagementQuality.BELOW_AVERAGE: 40,
            EngagementQuality.POOR: 20,
            EngagementQuality.SPAM: 0
        }
        scores.append(quality_scores.get(self.engagement_quality, 60))
        
        # Authenticity contribution
        if self.authenticity_score is not None:
            scores.append(self.authenticity_score)
        
        # Trend contribution
        trend_scores = {
            TrendDirection.EXPONENTIAL: 100,
            TrendDirection.RISING: 80,
            TrendDirection.STABLE: 60,
            TrendDirection.FALLING: 40,
            TrendDirection.DECLINING: 20
        }
        if self.trend_direction:
            scores.append(trend_scores.get(self.trend_direction, 60))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def get_audience_insights(self) -> Dict[str, Any]:
        """Get comprehensive audience insights"""        return {
            'demographics': {
                'unique_users': self.unique_users,
                'returning_users': self.returning_users,
                'new_users': self.new_users,
                'retention_rate': self.user_retention_rate
            },
            'geographic': {
                'top_countries': self.top_countries or {},
                'top_cities': self.top_cities or {},
                'international_percentage': self.international_percentage
            },
            'temporal': {
                'peak_hours': self.peak_hours or [],
                'hourly_distribution': self.hourly_distribution or {},
                'daily_distribution': self.daily_distribution or {}
            },
            'behavior': {
                'average_watch_time': self.average_watch_time,
                'completion_rate': self.completion_rate,
                'replay_rate': self.replay_rate,
                'interaction_depth': self.interaction_depth
            }
        }
    
    def predict_future_engagement(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Predict future engagement based on trends"""        base_value = self.value
        
        # Simple trend-based prediction
        if self.trend_velocity and self.trend_direction:
            if self.trend_direction in [TrendDirection.RISING, TrendDirection.EXPONENTIAL]:
                growth_rate = abs(self.trend_velocity) * 0.8  # Conservative estimate
                predicted_value = int(base_value * (1 + growth_rate)**days_ahead)
            elif self.trend_direction in [TrendDirection.FALLING, TrendDirection.DECLINING]:
                decay_rate = abs(self.trend_velocity) * 0.6
                predicted_value = int(base_value * (1 - decay_rate)**days_ahead)
            else:
                predicted_value = base_value
        else:
            predicted_value = base_value
        
        # Calculate confidence based on volatility
        confidence = max(0.1, 1.0 - (self.volatility_index or 0.5))
        
        return {
            'predicted_value': max(0, predicted_value),
            'confidence': confidence,
            'prediction_date': (datetime.now() + timedelta(days=days_ahead)).isoformat(),
            'trend_direction': self.trend_direction.value if self.trend_direction else None,
            'methodology': 'trend_based'
        }
    
    def compare_with_benchmark(self, benchmark_value: int) -> Dict[str, Any]:
        """Compare performance with benchmark"""        self.benchmark_value = benchmark_value
        
        if benchmark_value > 0:
            self.performance_vs_benchmark = ((self.value - benchmark_value) / benchmark_value) * 100
        else:
            self.performance_vs_benchmark = 0.0
        
        return {
            'current_value': self.value,
            'benchmark_value': benchmark_value,
            'difference': self.value - benchmark_value,
            'percentage_difference': self.performance_vs_benchmark,
            'performance_rating': 'above_benchmark' if self.value > benchmark_value else 'below_benchmark' if self.value < benchmark_value else 'at_benchmark'
        }
