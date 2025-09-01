"""Revenue Analytics - Advanced Revenue Analysis and Business Intelligence

Enterprise-grade revenue analytics system with AI-powered insights, predictive analytics,
and comprehensive performance monitoring for content creators.

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
    Column, String, Text, DateTime, Float, Integer, Boolean, JSON, 
    ForeignKey, Index, Enum as SQLEnum, Numeric, func, and_, or_
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
import pandas as pd
from dataclasses import dataclass

Base = declarative_base()


class AnalyticsTimeframe(Enum):
    """
Analytics calculation timeframes"""

    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class MetricType(Enum):
    """Revenue metric types for analytics"""

    GROSS_REVENUE = "gross_revenue"
    NET_REVENUE = "net_revenue"
    PLATFORM_FEES = "platform_fees"
    TAX_DEDUCTIONS = "tax_deductions"
    PROFIT_MARGIN = "profit_margin"
    REVENUE_GROWTH = "revenue_growth"
    REVENUE_PER_STREAM = "revenue_per_stream"
    REVENUE_PER_CONTENT = "revenue_per_content"
    AVERAGE_TRANSACTION = "average_transaction"
    CONVERSION_RATE = "conversion_rate"
    RETENTION_RATE = "retention_rate"
    LIFETIME_VALUE = "lifetime_value"
    CHURN_RATE = "churn_rate"
    ENGAGEMENT_RATE = "engagement_rate"
    GEOGRAPHIC_DISTRIBUTION = "geographic_distribution"
    PLATFORM_PERFORMANCE = "platform_performance"
    CONTENT_PERFORMANCE = "content_performance"
    SEASONAL_TRENDS = "seasonal_trends"
    GROWTH_VELOCITY = "growth_velocity"
    REVENUE_DIVERSIFICATION = "revenue_diversification"


class AnalyticsStatus(Enum):
    """Analytics calculation status"""

    PENDING = "pending"
    CALCULATING = "calculating"
    COMPLETED = "completed"
    FAILED = "failed"
    STALE = "stale"
    ARCHIVED = "archived"


@dataclass
class RevenueMetrics:
    """Data class for revenue metrics"""
    gross_revenue: Decimal
    net_revenue: Decimal
    total_transactions: int
    average_transaction: Decimal
    growth_rate: float
    profit_margin: float
    top_platforms: List[Dict[str, Any]]
    top_content: List[Dict[str, Any]]
    geographic_breakdown: Dict[str, Decimal]
    timeframe_data: Dict[str, Any]


@dataclass
class PlatformPerformance:
    """
Platform-specific performance metrics"""
    platform: str
    total_revenue: Decimal
    transaction_count: int
    average_revenue_per_transaction: Decimal
    growth_rate: float
    market_share: float
    top_content: List[Dict[str, Any]]
    user_engagement: Dict[str, Any]


@dataclass
class ContentPerformance:
    """
Content-specific performance metrics"""
    content_id: str
    content_title: str
    total_revenue: Decimal
    platforms: List[str]
    total_plays: int
    revenue_per_play: Decimal
    geographic_performance: Dict[str, Any]
    time_series_data: Dict[str, Any]


class RevenueAnalytics(Base):
    """
    Revenue Analytics Model
    
    Stores calculated analytics and metrics for revenue performance,
    trends analysis, and business intelligence reporting.
    """
    __tablename__ = "revenue_analytics"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Scope and context
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    platform = Column(String(100), nullable=True, index=True)
    content_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Analytics metadata
    metric_type = Column(SQLEnum(MetricType), nullable=False, index=True)
    timeframe = Column(SQLEnum(AnalyticsTimeframe), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Calculated metrics
    metric_value = Column(Numeric(18, 6), nullable=True)
    metric_percentage = Column(Float, nullable=True)
    metric_count = Column(Integer, nullable=True)
    metric_data = Column(JSONB, nullable=True)
    
    # Comparison and trends
    previous_period_value = Column(Numeric(18, 6), nullable=True)
    growth_rate = Column(Float, nullable=True)
    trend_direction = Column(String(20), nullable=True)  # up, down, stable
    confidence_score = Column(Float, default=1.0)
    
    # Statistical data
    standard_deviation = Column(Float, nullable=True)
    variance = Column(Float, nullable=True)
    percentile_rank = Column(Float, nullable=True)
    outlier_score = Column(Float, nullable=True)
    
    # Forecasting
    predicted_next_period = Column(Numeric(18, 6), nullable=True)
    forecast_confidence = Column(Float, nullable=True)
    seasonality_factor = Column(Float, nullable=True)
    
    # Processing metadata
    calculation_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    calculation_duration_ms = Column(Integer, nullable=True)
    data_sources = Column(ARRAY(String), nullable=True)
    calculation_method = Column(String(100), nullable=True)
    status = Column(SQLEnum(AnalyticsStatus), default=AnalyticsStatus.PENDING)
    
    # Quality and validation
    data_quality_score = Column(Float, default=1.0)
    validation_errors = Column(JSON, nullable=True)
    sample_size = Column(Integer, nullable=True)
    confidence_interval = Column(JSON, nullable=True)
    
    # Additional context
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_analytics_user_metric', 'user_id', 'metric_type'),
        Index('idx_analytics_timeframe_period', 'timeframe', 'period_start', 'period_end'),
        Index('idx_analytics_platform_metric', 'platform', 'metric_type'),
        Index('idx_analytics_status', 'status'),
        Index('idx_analytics_calculation_time', 'calculation_timestamp'),
        Index('idx_analytics_trend', 'trend_direction', 'growth_rate'),
    )


class RevenueSnapshot(Base):
    """
    Revenue Snapshot Model
    
    Point-in-time snapshots of revenue data for historical tracking
    and trend analysis across different time periods.
    """
    __tablename__ = "revenue_snapshots"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Snapshot metadata
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    snapshot_date = Column(DateTime(timezone=True), nullable=False, index=True)
    snapshot_type = Column(String(50), nullable=False, index=True)  # daily, weekly, monthly, etc.
    
    # Revenue totals
    total_gross_revenue = Column(Numeric(18, 6), default=0.0)
    total_net_revenue = Column(Numeric(18, 6), default=0.0)
    total_fees = Column(Numeric(18, 6), default=0.0)
    total_taxes = Column(Numeric(18, 6), default=0.0)
    currency = Column(String(10), default='EUR')
    
    # Transaction metrics
    total_transactions = Column(Integer, default=0)
    average_transaction_value = Column(Numeric(18, 6), default=0.0)
    largest_transaction = Column(Numeric(18, 6), default=0.0)
    smallest_transaction = Column(Numeric(18, 6), default=0.0)
    
    # Platform breakdown
    platform_revenue_breakdown = Column(JSONB, nullable=True)
    platform_transaction_counts = Column(JSONB, nullable=True)
    top_performing_platforms = Column(ARRAY(String), nullable=True)
    
    # Content performance
    content_revenue_breakdown = Column(JSONB, nullable=True)
    top_performing_content = Column(JSONB, nullable=True)
    content_engagement_metrics = Column(JSONB, nullable=True)
    
    # Geographic distribution
    revenue_by_country = Column(JSONB, nullable=True)
    revenue_by_region = Column(JSONB, nullable=True)
    international_revenue_percentage = Column(Float, nullable=True)
    
    # Growth metrics
    revenue_growth_rate = Column(Float, nullable=True)
    transaction_growth_rate = Column(Float, nullable=True)
    platform_growth_rates = Column(JSONB, nullable=True)
    
    # Performance indicators
    revenue_per_content_piece = Column(Numeric(18, 6), nullable=True)
    revenue_per_platform = Column(Numeric(18, 6), nullable=True)
    profit_margin_percentage = Column(Float, nullable=True)
    fee_percentage = Column(Float, nullable=True)
    
    # Forecasting data
    predicted_next_period_revenue = Column(Numeric(18, 6), nullable=True)
    forecast_confidence_level = Column(Float, nullable=True)
    seasonal_adjustment_factor = Column(Float, nullable=True)
    
    # Data quality
    data_completeness_score = Column(Float, default=1.0)
    outlier_count = Column(Integer, default=0)
    data_sources_count = Column(Integer, default=0)
    
    # Processing metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    calculation_completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_duration_ms = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_snapshot_user_date', 'user_id', 'snapshot_date'),
        Index('idx_snapshot_type_date', 'snapshot_type', 'snapshot_date'),
        Index('idx_snapshot_revenue', 'total_net_revenue'),
        Index('idx_snapshot_growth', 'revenue_growth_rate'),
    )


class PlatformAnalytics(Base):
    """
    Platform-Specific Analytics Model
    
    Detailed analytics for performance on individual platforms,
    including engagement metrics, audience insights, and optimization recommendations.
    """
    __tablename__ = "platform_analytics"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Scope
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    platform = Column(String(100), nullable=False, index=True)
    analysis_date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Revenue metrics
    total_revenue = Column(Numeric(18, 6), default=0.0)
    revenue_growth_rate = Column(Float, nullable=True)
    revenue_per_transaction = Column(Numeric(18, 6), nullable=True)
    revenue_market_share = Column(Float, nullable=True)
    
    # Engagement metrics
    total_plays = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    unique_listeners = Column(Integer, default=0)
    
    # Performance ratios
    engagement_rate = Column(Float, nullable=True)
    conversion_rate = Column(Float, nullable=True)
    retention_rate = Column(Float, nullable=True)
    bounce_rate = Column(Float, nullable=True)
    
    # Audience insights
    audience_demographics = Column(JSONB, nullable=True)
    audience_geographic_distribution = Column(JSONB, nullable=True)
    audience_behavior_patterns = Column(JSONB, nullable=True)
    audience_growth_metrics = Column(JSONB, nullable=True)
    
    # Content performance
    top_performing_content = Column(JSONB, nullable=True)
    content_category_performance = Column(JSONB, nullable=True)
    content_length_optimization = Column(JSONB, nullable=True)
    content_timing_analysis = Column(JSONB, nullable=True)
    
    # Platform-specific metrics
    platform_specific_metrics = Column(JSONB, nullable=True)
    algorithm_performance_score = Column(Float, nullable=True)
    discoverability_score = Column(Float, nullable=True)
    monetization_efficiency = Column(Float, nullable=True)
    
    # Competitive analysis
    industry_benchmark_comparison = Column(JSONB, nullable=True)
    competitive_positioning = Column(Float, nullable=True)
    market_opportunity_score = Column(Float, nullable=True)
    
    # Recommendations
    optimization_recommendations = Column(JSONB, nullable=True)
    growth_opportunities = Column(JSONB, nullable=True)
    risk_factors = Column(JSONB, nullable=True)
    action_items = Column(JSONB, nullable=True)
    
    # Quality and confidence
    data_quality_score = Column(Float, default=1.0)
    analysis_confidence = Column(Float, default=1.0)
    sample_size = Column(Integer, nullable=True)
    
    # Processing metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_platform_analytics_user_platform', 'user_id', 'platform'),
        Index('idx_platform_analytics_date', 'analysis_date'),
        Index('idx_platform_analytics_revenue', 'total_revenue'),
        Index('idx_platform_analytics_engagement', 'engagement_rate'),
    )


class PerformanceBenchmark(Base):
    """
    Performance Benchmark Model
    
    Industry benchmarks and comparative performance metrics
    for evaluating creator performance against market standards.
    """
    __tablename__ = "performance_benchmarks"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Benchmark scope
    industry_category = Column(String(100), nullable=False, index=True)
    content_type = Column(String(100), nullable=False, index=True)
    platform = Column(String(100), nullable=False, index=True)
    geographic_region = Column(String(100), nullable=True, index=True)
    
    # Benchmark period
    benchmark_date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String(50), nullable=False)  # monthly, quarterly, yearly
    
    # Revenue benchmarks
    median_revenue_per_creator = Column(Numeric(18, 6), nullable=True)
    average_revenue_per_creator = Column(Numeric(18, 6), nullable=True)
    percentile_90_revenue = Column(Numeric(18, 6), nullable=True)
    percentile_75_revenue = Column(Numeric(18, 6), nullable=True)
    percentile_25_revenue = Column(Numeric(18, 6), nullable=True)
    percentile_10_revenue = Column(Numeric(18, 6), nullable=True)
    
    # Engagement benchmarks
    median_engagement_rate = Column(Float, nullable=True)
    average_engagement_rate = Column(Float, nullable=True)
    median_follower_growth = Column(Float, nullable=True)
    average_content_performance = Column(Float, nullable=True)
    
    # Monetization benchmarks
    average_rpm = Column(Numeric(18, 6), nullable=True)  # Revenue per mille
    average_conversion_rate = Column(Float, nullable=True)
    average_retention_rate = Column(Float, nullable=True)
    average_platform_fees = Column(Float, nullable=True)
    
    # Distribution data
    revenue_distribution = Column(JSONB, nullable=True)
    engagement_distribution = Column(JSONB, nullable=True)
    creator_count_in_segment = Column(Integer, nullable=True)
    
    # Metadata
    data_source = Column(String(200), nullable=True)
    confidence_level = Column(Float, default=0.95)
    sample_size = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_benchmark_category_platform', 'industry_category', 'platform'),
        Index('idx_benchmark_date', 'benchmark_date'),
        Index('idx_benchmark_content_type', 'content_type'),
    )


class RevenueTrend(Base):
    """
    Revenue Trend Model
    
    Tracks revenue trends, patterns, and forecasting data
    for predictive analytics and strategic planning.
    """
    __tablename__ = "revenue_trends"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Trend scope
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    trend_type = Column(String(50), nullable=False, index=True)  # linear, exponential, seasonal, etc.
    trend_scope = Column(String(50), nullable=False)  # overall, platform, content_type
    scope_identifier = Column(String(100), nullable=True)  # platform name, content category, etc.
    
    # Trend period
    trend_start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    trend_end_date = Column(DateTime(timezone=True), nullable=False)
    analysis_date = Column(DateTime(timezone=True), nullable=False)
    
    # Trend metrics
    trend_strength = Column(Float, nullable=True)  # -1 to 1, negative for declining trends
    trend_consistency = Column(Float, nullable=True)  # 0 to 1, higher means more consistent
    trend_acceleration = Column(Float, nullable=True)  # Rate of change in trend
    
    # Statistical measures
    correlation_coefficient = Column(Float, nullable=True)
    r_squared = Column(Float, nullable=True)
    standard_error = Column(Float, nullable=True)
    confidence_interval = Column(JSON, nullable=True)
    
    # Trend equation parameters
    slope = Column(Float, nullable=True)
    intercept = Column(Float, nullable=True)
    polynomial_coefficients = Column(ARRAY(Float), nullable=True)
    seasonal_parameters = Column(JSON, nullable=True)
    
    # Forecasting
    forecast_next_30_days = Column(Numeric(18, 6), nullable=True)
    forecast_next_90_days = Column(Numeric(18, 6), nullable=True)
    forecast_next_365_days = Column(Numeric(18, 6), nullable=True)
    forecast_confidence = Column(Float, nullable=True)
    
    # Seasonality
    seasonal_pattern_detected = Column(Boolean, default=False)
    seasonal_strength = Column(Float, nullable=True)
    peak_seasons = Column(ARRAY(String), nullable=True)
    low_seasons = Column(ARRAY(String), nullable=True)
    
    # Anomaly detection
    anomalies_detected = Column(Integer, default=0)
    anomaly_dates = Column(ARRAY(DateTime), nullable=True)
    anomaly_values = Column(ARRAY(Float), nullable=True)
    
    # Model performance
    model_accuracy = Column(Float, nullable=True)
    prediction_error_margin = Column(Float, nullable=True)
    model_type = Column(String(100), nullable=True)
    
    # Metadata
    data_points_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_trend_user_type', 'user_id', 'trend_type'),
        Index('idx_trend_scope', 'trend_scope', 'scope_identifier'),
        Index('idx_trend_strength', 'trend_strength'),
        Index('idx_trend_date', 'trend_start_date', 'trend_end_date'),
    )


class AnalyticsJob(Base):
    """
    Analytics Job Model
    
    Tracks analytics calculation jobs, scheduling, and processing status
    for automated analytics generation and monitoring.
    """
    __tablename__ = "analytics_jobs"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Job definition
    job_type = Column(String(100), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    scope = Column(String(100), nullable=False)  # user, platform, global
    parameters = Column(JSONB, nullable=True)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    frequency = Column(String(50), nullable=True)  # once, daily, weekly, monthly
    
    # Status and results
    status = Column(SQLEnum(AnalyticsStatus), default=AnalyticsStatus.PENDING, index=True)
    progress_percentage = Column(Float, default=0.0)
    result_summary = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Performance metrics
    processing_time_ms = Column(Integer, nullable=True)
    records_processed = Column(Integer, nullable=True)
    memory_used_mb = Column(Float, nullable=True)
    cpu_time_ms = Column(Integer, nullable=True)
    
    # Priority and configuration
    priority = Column(Integer, default=5)  # 1=highest, 10=lowest
    timeout_seconds = Column(Integer, default=3600)
    dependencies = Column(ARRAY(UUID), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_job_status_scheduled', 'status', 'scheduled_at'),
        Index('idx_job_type_user', 'job_type', 'user_id'),
        Index('idx_job_next_run', 'next_run_at'),
        Index('idx_job_priority', 'priority', 'scheduled_at'),
    )


__all__ = [
    'AnalyticsTimeframe',
    'MetricType',
    'AnalyticsStatus',
    'RevenueMetrics',
    'PlatformPerformance',
    'ContentPerformance',
    'RevenueAnalytics',
    'RevenueSnapshot',
    'PlatformAnalytics',
    'PerformanceBenchmark',
    'RevenueTrend',
    'AnalyticsJob'
]
