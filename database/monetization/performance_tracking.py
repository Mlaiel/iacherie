"""Performance Tracking Models - Enterprise Performance Tracking System

Ultra-advanced performance tracking models for comprehensive content performance analysis
across all platforms with real-time analytics and AI-powered insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 CRITICAL LEGAL WARNING:
This code and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, distribution, or commercialization 
is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries and authorization.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Solution Architect
- Senior Backend Engineer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer & Automation Specialist
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Boolean, ForeignKey,
    Text, DECIMAL, JSON, BigInteger, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from enum import Enum
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

Base = declarative_base()

class MetricType(Enum):
    """Content performance metric types"""    VIEWS = "views"
    STREAMS = "streams"
    DOWNLOADS = "downloads"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    SAVES = "saves"
    ENGAGEMENT_RATE = "engagement_rate"
    CLICK_THROUGH_RATE = "click_through_rate"
    CONVERSION_RATE = "conversion_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    WATCH_TIME = "watch_time"
    COMPLETION_RATE = "completion_rate"
    SKIP_RATE = "skip_rate"

class PerformanceStatus(Enum):
    """Performance tracking status"""    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ContentType(Enum):
    """Content type classification"""    MUSIC = "music"
    VIDEO = "video"
    PODCAST = "podcast"
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    LIVE_STREAM = "live_stream"
    COLLABORATION = "collaboration"
    ADVERTISEMENT = "advertisement"

class PerformanceRecord(Base):
    """Individual performance tracking record"""    __tablename__ = 'performance_records'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_id = Column(String(100), nullable=False, index=True)
    
    # Performance metrics
    metric_type = Column(String(50), nullable=False)
    metric_value = Column(BigInteger, default=0)
    metric_rate = Column(Float, default=0.0)
    previous_value = Column(BigInteger, default=0)
    growth_rate = Column(Float, default=0.0)
    
    # Content information
    content_type = Column(String(50), nullable=False)
    content_title = Column(String(500))
    content_duration = Column(Integer)  # in seconds
    content_size = Column(BigInteger)  # in bytes
    
    # Temporal data
    measurement_timestamp = Column(DateTime(timezone=True), default=func.now())
    reporting_period_start = Column(DateTime(timezone=True))
    reporting_period_end = Column(DateTime(timezone=True))
    
    # Geographic and demographic data
    country_code = Column(String(2))
    region = Column(String(100))
    age_group = Column(String(20))
    gender = Column(String(20))
    device_type = Column(String(50))
    
    # Engagement details
    engagement_quality_score = Column(Float, default=0.0)
    audience_retention = Column(Float, default=0.0)
    viral_coefficient = Column(Float, default=0.0)
    
    # Status and metadata
    status = Column(String(20), default=PerformanceStatus.ACTIVE.value)
    metadata = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_performance_content_platform', 'content_id', 'platform_id'),
        Index('idx_performance_creator_date', 'creator_id', 'measurement_timestamp'),
        Index('idx_performance_metric_type', 'metric_type', 'measurement_timestamp'),
        Index('idx_performance_country', 'country_code', 'measurement_timestamp'),
    )

class PerformanceAggregation(Base):
    """Aggregated performance metrics for efficient querying"""    __tablename__ = 'performance_aggregations'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform_id = Column(String(100), nullable=False, index=True)
    
    # Aggregation period
    aggregation_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Total metrics
    total_views = Column(BigInteger, default=0)
    total_streams = Column(BigInteger, default=0)
    total_downloads = Column(BigInteger, default=0)
    total_likes = Column(BigInteger, default=0)
    total_shares = Column(BigInteger, default=0)
    total_comments = Column(BigInteger, default=0)
    total_saves = Column(BigInteger, default=0)
    
    # Average metrics
    avg_engagement_rate = Column(Float, default=0.0)
    avg_completion_rate = Column(Float, default=0.0)
    avg_watch_time = Column(Float, default=0.0)
    avg_skip_rate = Column(Float, default=0.0)
    
    # Peak performance
    peak_concurrent_viewers = Column(Integer, default=0)
    peak_hourly_streams = Column(Integer, default=0)
    best_performing_hour = Column(Integer)
    best_performing_day = Column(Integer)
    
    # Revenue correlation
    estimated_revenue = Column(DECIMAL(15, 4), default=0)
    revenue_per_view = Column(DECIMAL(10, 6), default=0)
    revenue_per_engagement = Column(DECIMAL(10, 6), default=0)
    
    # Geographic distribution
    top_countries = Column(JSONB)  # Top 10 countries with percentages
    top_regions = Column(JSONB)    # Top 10 regions with percentages
    
    # Demographic insights
    age_distribution = Column(JSONB)
    gender_distribution = Column(JSONB)
    device_distribution = Column(JSONB)
    
    # Performance indicators
    growth_rate = Column(Float, default=0.0)
    trend_direction = Column(String(20))  # increasing, decreasing, stable
    performance_score = Column(Float, default=0.0)
    market_position = Column(Integer)  # ranking in category
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_perf_agg_content_period', 'content_id', 'aggregation_type', 'period_start'),
        Index('idx_perf_agg_creator_period', 'creator_id', 'aggregation_type', 'period_start'),
        Index('idx_perf_agg_platform_period', 'platform_id', 'aggregation_type', 'period_start'),
        UniqueConstraint('content_id', 'platform_id', 'aggregation_type', 'period_start', name='uq_perf_agg_unique'),
    )

class PerformanceBenchmark(Base):
    """Industry and category performance benchmarks"""    __tablename__ = 'performance_benchmarks'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    platform_id = Column(String(100), nullable=False)
    
    # Benchmark period
    period_type = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Sample size and confidence
    sample_size = Column(Integer, nullable=False)
    confidence_level = Column(Float, default=95.0)
    margin_of_error = Column(Float, default=5.0)
    
    # Benchmark metrics (percentiles)
    views_p25 = Column(BigInteger, default=0)
    views_p50 = Column(BigInteger, default=0)
    views_p75 = Column(BigInteger, default=0)
    views_p90 = Column(BigInteger, default=0)
    views_p99 = Column(BigInteger, default=0)
    
    engagement_rate_p25 = Column(Float, default=0.0)
    engagement_rate_p50 = Column(Float, default=0.0)
    engagement_rate_p75 = Column(Float, default=0.0)
    engagement_rate_p90 = Column(Float, default=0.0)
    engagement_rate_p99 = Column(Float, default=0.0)
    
    completion_rate_p25 = Column(Float, default=0.0)
    completion_rate_p50 = Column(Float, default=0.0)
    completion_rate_p75 = Column(Float, default=0.0)
    completion_rate_p90 = Column(Float, default=0.0)
    completion_rate_p99 = Column(Float, default=0.0)
    
    # Revenue benchmarks
    revenue_per_view_p25 = Column(DECIMAL(10, 6), default=0)
    revenue_per_view_p50 = Column(DECIMAL(10, 6), default=0)
    revenue_per_view_p75 = Column(DECIMAL(10, 6), default=0)
    revenue_per_view_p90 = Column(DECIMAL(10, 6), default=0)
    revenue_per_view_p99 = Column(DECIMAL(10, 6), default=0)
    
    # Growth rate benchmarks
    monthly_growth_p25 = Column(Float, default=0.0)
    monthly_growth_p50 = Column(Float, default=0.0)
    monthly_growth_p75 = Column(Float, default=0.0)
    monthly_growth_p90 = Column(Float, default=0.0)
    monthly_growth_p99 = Column(Float, default=0.0)
    
    # Industry insights
    top_performing_factors = Column(JSONB)
    common_optimization_strategies = Column(JSONB)
    seasonal_trends = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_benchmark_category_platform', 'category', 'platform_id'),
        Index('idx_benchmark_period', 'period_type', 'period_start'),
    )

class ContentPerformanceAlert(Base):
    """Performance alerts and notifications"""    __tablename__ = 'content_performance_alerts'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    
    # Alert details
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Trigger conditions
    metric_type = Column(String(50), nullable=False)
    threshold_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    comparison_operator = Column(String(10), nullable=False)  # >, <, >=, <=, ==, !=
    
    # Alert status
    status = Column(String(20), default='active')  # active, acknowledged, resolved, dismissed
    acknowledged_by = Column(UUID(as_uuid=True))
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    
    # Notification details
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(ARRAY(String))  # email, sms, push, webhook
    
    # Timestamps
    triggered_at = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_creator_status', 'creator_id', 'status'),
        Index('idx_alert_content_severity', 'content_id', 'severity'),
        Index('idx_alert_triggered_at', 'triggered_at'),
    )

@dataclass
class PerformanceInsight:
    """Performance insight data structure"""    insight_type: str
    title: str
    description: str
    impact_score: float
    confidence_score: float
    recommendations: List[str]
    supporting_data: Dict[str, Any]
    priority: str  # low, medium, high
    
class PerformanceOptimizationSuggestion(Base):
    """AI-generated performance optimization suggestions"""    __tablename__ = 'performance_optimization_suggestions'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Suggestion details
    suggestion_type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # AI analysis
    confidence_score = Column(Float, default=0.0)
    potential_impact = Column(Float, default=0.0)
    implementation_difficulty = Column(String(20))  # easy, medium, hard
    estimated_improvement = Column(Float, default=0.0)  # percentage improvement
    
    # Supporting data
    baseline_metrics = Column(JSONB)
    target_metrics = Column(JSONB)
    benchmark_data = Column(JSONB)
    similar_cases = Column(JSONB)
    
    # Implementation tracking
    status = Column(String(20), default='pending')  # pending, in_progress, implemented, dismissed
    implemented_by = Column(UUID(as_uuid=True))
    implemented_at = Column(DateTime(timezone=True))
    results_tracked_until = Column(DateTime(timezone=True))
    
    # Results tracking
    actual_improvement = Column(Float)
    implementation_notes = Column(Text)
    success_rating = Column(Integer)  # 1-5 rating
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_suggestion_creator_status', 'creator_id', 'status'),
        Index('idx_suggestion_impact', 'potential_impact', 'confidence_score'),
        Index('idx_suggestion_generated_at', 'generated_at'),
    )

# Export all models for easy import
__all__ = [
    'MetricType',
    'PerformanceStatus',
    'ContentType',
    'PerformanceRecord',
    'PerformanceAggregation',
    'PerformanceBenchmark',
    'ContentPerformanceAlert',
    'PerformanceInsight',
    'PerformanceOptimizationSuggestion'
]
