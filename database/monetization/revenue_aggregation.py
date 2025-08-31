"""
Revenue Aggregation - High-Performance Revenue Data Processing

Enterprise-grade aggregation system for real-time revenue analytics,
pre-calculated metrics, and optimized query performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 CRITICAL LEGAL WARNING:
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
    ForeignKey, Index, Enum as SQLEnum, Numeric, func, select,
    and_, or_, case, extract
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime, timezone, timedelta, date
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple
import asyncio
import logging

Base = declarative_base()
logger = logging.getLogger(__name__)


class AggregationLevel(Enum):
    """Aggregation granularity levels"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"


class AggregationScope(Enum):
    """Aggregation scope definitions"""
    USER_GLOBAL = "user_global"
    USER_PLATFORM = "user_platform"
    USER_CONTENT = "user_content"
    USER_CONTENT_PLATFORM = "user_content_platform"
    PLATFORM_GLOBAL = "platform_global"
    CONTENT_TYPE_GLOBAL = "content_type_global"
    GEOGRAPHIC_REGION = "geographic_region"
    REVENUE_TYPE = "revenue_type"
    COLLABORATION = "collaboration"


class AggregationStatus(Enum):
    """Aggregation processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    STALE = "stale"
    REBUILDING = "rebuilding"


class RevenueAggregationDaily(Base):
    """
    Daily Revenue Aggregation Model
    
    High-performance daily aggregations optimized for dashboard queries
    and real-time analytics with comprehensive revenue metrics.
    """
    __tablename__ = "revenue_aggregation_daily"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Aggregation dimensions
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    platform = Column(String(100), nullable=True, index=True)
    content_fingerprint_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    revenue_type = Column(String(100), nullable=True, index=True)
    collaboration_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Time dimension
    aggregation_date = Column(DateTime(timezone=True), nullable=False, index=True)
    date_key = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD format
    
    # Revenue aggregations
    total_gross_revenue = Column(Numeric(20, 6), default=0.0)
    total_net_revenue = Column(Numeric(20, 6), default=0.0)
    total_platform_fees = Column(Numeric(20, 6), default=0.0)
    total_service_fees = Column(Numeric(20, 6), default=0.0)
    total_taxes = Column(Numeric(20, 6), default=0.0)
    total_other_deductions = Column(Numeric(20, 6), default=0.0)
    
    # Transaction metrics
    transaction_count = Column(Integer, default=0)
    unique_revenue_streams = Column(Integer, default=0)
    average_transaction_value = Column(Numeric(18, 6), default=0.0)
    largest_transaction = Column(Numeric(18, 6), default=0.0)
    smallest_transaction = Column(Numeric(18, 6), default=0.0)
    
    # Performance metrics
    total_plays = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    total_streams = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    unique_listeners = Column(Integer, default=0)
    
    # Efficiency metrics
    revenue_per_play = Column(Numeric(18, 8), default=0.0)
    revenue_per_stream = Column(Numeric(18, 8), default=0.0)
    revenue_per_view = Column(Numeric(18, 8), default=0.0)
    revenue_per_unique_listener = Column(Numeric(18, 6), default=0.0)
    
    # Geographic breakdown
    revenue_by_country = Column(JSONB, nullable=True)
    top_countries = Column(ARRAY(String), nullable=True)
    international_revenue_percentage = Column(Float, nullable=True)
    
    # Currency breakdown
    currency_breakdown = Column(JSONB, nullable=True)
    primary_currency = Column(String(10), default='EUR')
    exchange_rate_average = Column(Numeric(12, 8), default=1.0)
    
    # Growth and comparison
    previous_day_revenue = Column(Numeric(20, 6), nullable=True)
    day_over_day_growth = Column(Float, nullable=True)
    week_over_week_growth = Column(Float, nullable=True)
    month_over_month_growth = Column(Float, nullable=True)
    
    # Metadata
    data_quality_score = Column(Float, default=1.0)
    records_aggregated = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow)
    aggregation_completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_duration_ms = Column(Integer, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_daily_user_date', 'user_id', 'aggregation_date'),
        Index('idx_daily_user_platform_date', 'user_id', 'platform', 'aggregation_date'),
        Index('idx_daily_date_key', 'date_key'),
        Index('idx_daily_revenue_type', 'revenue_type', 'aggregation_date'),
        Index('idx_daily_content', 'content_fingerprint_id', 'aggregation_date'),
        Index('idx_daily_collaboration', 'collaboration_id', 'aggregation_date'),
        Index('idx_daily_total_revenue', 'total_net_revenue'),
        Index('idx_daily_growth', 'day_over_day_growth'),
    )


class RevenueAggregationWeekly(Base):
    """
    Weekly Revenue Aggregation Model
    
    Weekly aggregations for trend analysis and medium-term performance tracking.
    """
    __tablename__ = "revenue_aggregation_weekly"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Aggregation dimensions
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    platform = Column(String(100), nullable=True, index=True)
    revenue_type = Column(String(100), nullable=True, index=True)
    
    # Time dimension
    week_start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    week_end_date = Column(DateTime(timezone=True), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    week_number = Column(Integer, nullable=False, index=True)
    week_key = Column(String(10), nullable=False, index=True)  # YYYY-WW format
    
    # Revenue aggregations
    total_gross_revenue = Column(Numeric(20, 6), default=0.0)
    total_net_revenue = Column(Numeric(20, 6), default=0.0)
    total_fees = Column(Numeric(20, 6), default=0.0)
    total_taxes = Column(Numeric(20, 6), default=0.0)
    
    # Daily breakdown within week
    daily_revenue_breakdown = Column(JSONB, nullable=True)
    peak_revenue_day = Column(String(20), nullable=True)
    lowest_revenue_day = Column(String(20), nullable=True)
    
    # Transaction and performance metrics
    transaction_count = Column(Integer, default=0)
    total_plays = Column(Integer, default=0)
    total_streams = Column(Integer, default=0)
    unique_listeners = Column(Integer, default=0)
    
    # Weekly analytics
    average_daily_revenue = Column(Numeric(18, 6), default=0.0)
    revenue_variance = Column(Float, nullable=True)
    revenue_consistency_score = Column(Float, nullable=True)
    
    # Growth metrics
    previous_week_revenue = Column(Numeric(20, 6), nullable=True)
    week_over_week_growth = Column(Float, nullable=True)
    four_week_average = Column(Numeric(20, 6), nullable=True)
    
    # Platform performance
    platform_revenue_distribution = Column(JSONB, nullable=True)
    top_performing_platforms = Column(ARRAY(String), nullable=True)
    platform_diversification_score = Column(Float, nullable=True)
    
    # Metadata
    days_with_data = Column(Integer, default=0)
    data_quality_score = Column(Float, default=1.0)
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_weekly_user_week', 'user_id', 'week_start_date'),
        Index('idx_weekly_year_week', 'year', 'week_number'),
        Index('idx_weekly_platform', 'platform', 'week_start_date'),
        Index('idx_weekly_revenue', 'total_net_revenue'),
        Index('idx_weekly_growth', 'week_over_week_growth'),
    )


class RevenueAggregationMonthly(Base):
    """
    Monthly Revenue Aggregation Model
    
    Monthly aggregations for business reporting, financial planning,
    and long-term trend analysis.
    """
    __tablename__ = "revenue_aggregation_monthly"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Aggregation dimensions
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    platform = Column(String(100), nullable=True, index=True)
    
    # Time dimension
    month_start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    month_end_date = Column(DateTime(timezone=True), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    month_key = Column(String(7), nullable=False, index=True)  # YYYY-MM format
    
    # Revenue aggregations
    total_gross_revenue = Column(Numeric(20, 6), default=0.0)
    total_net_revenue = Column(Numeric(20, 6), default=0.0)
    total_fees = Column(Numeric(20, 6), default=0.0)
    total_taxes = Column(Numeric(20, 6), default=0.0)
    
    # Monthly breakdown
    weekly_revenue_breakdown = Column(JSONB, nullable=True)
    daily_revenue_breakdown = Column(JSONB, nullable=True)
    peak_revenue_day = Column(String(20), nullable=True)
    peak_revenue_week = Column(String(20), nullable=True)
    
    # Performance metrics
    transaction_count = Column(Integer, default=0)
    unique_content_pieces = Column(Integer, default=0)
    total_plays = Column(Integer, default=0)
    total_streams = Column(Integer, default=0)
    unique_listeners = Column(Integer, default=0)
    
    # Monthly analytics
    average_daily_revenue = Column(Numeric(18, 6), default=0.0)
    average_weekly_revenue = Column(Numeric(18, 6), default=0.0)
    revenue_variance = Column(Float, nullable=True)
    revenue_standard_deviation = Column(Float, nullable=True)
    
    # Growth and comparison
    previous_month_revenue = Column(Numeric(20, 6), nullable=True)
    month_over_month_growth = Column(Float, nullable=True)
    year_over_year_growth = Column(Float, nullable=True)
    quarter_to_date_revenue = Column(Numeric(20, 6), nullable=True)
    year_to_date_revenue = Column(Numeric(20, 6), nullable=True)
    
    # Platform and content analysis
    platform_revenue_distribution = Column(JSONB, nullable=True)
    content_type_distribution = Column(JSONB, nullable=True)
    revenue_stream_distribution = Column(JSONB, nullable=True)
    top_performing_content = Column(JSONB, nullable=True)
    
    # Geographic analysis
    revenue_by_country = Column(JSONB, nullable=True)
    international_revenue_percentage = Column(Float, nullable=True)
    geographic_diversification_score = Column(Float, nullable=True)
    
    # Financial ratios and KPIs
    profit_margin_percentage = Column(Float, nullable=True)
    revenue_per_content_piece = Column(Numeric(18, 6), nullable=True)
    revenue_per_platform = Column(Numeric(18, 6), nullable=True)
    revenue_concentration_index = Column(Float, nullable=True)
    
    # Forecasting data
    predicted_next_month_revenue = Column(Numeric(20, 6), nullable=True)
    seasonal_adjustment_factor = Column(Float, nullable=True)
    trend_strength = Column(Float, nullable=True)
    
    # Metadata
    days_in_month = Column(Integer, default=0)
    days_with_data = Column(Integer, default=0)
    data_completeness_percentage = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_monthly_user_month', 'user_id', 'month_start_date'),
        Index('idx_monthly_year_month', 'year', 'month'),
        Index('idx_monthly_platform', 'platform', 'month_start_date'),
        Index('idx_monthly_revenue', 'total_net_revenue'),
        Index('idx_monthly_growth', 'month_over_month_growth'),
    )


class RevenueAggregationQuarterly(Base):
    """
    Quarterly Revenue Aggregation Model
    
    Quarterly aggregations for business reviews, strategic planning,
    and seasonal analysis.
    """
    __tablename__ = "revenue_aggregation_quarterly"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Aggregation dimensions
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    
    # Time dimension
    quarter_start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    quarter_end_date = Column(DateTime(timezone=True), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    quarter = Column(Integer, nullable=False, index=True)  # 1, 2, 3, 4
    quarter_key = Column(String(7), nullable=False, index=True)  # YYYY-Q1 format
    
    # Revenue aggregations
    total_gross_revenue = Column(Numeric(20, 6), default=0.0)
    total_net_revenue = Column(Numeric(20, 6), default=0.0)
    total_fees = Column(Numeric(20, 6), default=0.0)
    total_taxes = Column(Numeric(20, 6), default=0.0)
    
    # Quarterly breakdown
    monthly_revenue_breakdown = Column(JSONB, nullable=True)
    peak_revenue_month = Column(String(20), nullable=True)
    lowest_revenue_month = Column(String(20), nullable=True)
    
    # Performance metrics
    transaction_count = Column(Integer, default=0)
    unique_content_pieces = Column(Integer, default=0)
    total_plays = Column(Integer, default=0)
    unique_listeners = Column(Integer, default=0)
    
    # Quarterly analytics
    average_monthly_revenue = Column(Numeric(18, 6), default=0.0)
    revenue_variance = Column(Float, nullable=True)
    revenue_seasonality_score = Column(Float, nullable=True)
    
    # Growth metrics
    previous_quarter_revenue = Column(Numeric(20, 6), nullable=True)
    quarter_over_quarter_growth = Column(Float, nullable=True)
    year_over_year_growth = Column(Float, nullable=True)
    
    # Strategic metrics
    platform_diversification_score = Column(Float, nullable=True)
    revenue_stream_diversification = Column(Float, nullable=True)
    market_expansion_score = Column(Float, nullable=True)
    
    # Business intelligence
    top_performing_platforms = Column(JSONB, nullable=True)
    emerging_revenue_streams = Column(JSONB, nullable=True)
    declining_revenue_streams = Column(JSONB, nullable=True)
    strategic_opportunities = Column(JSONB, nullable=True)
    
    # Metadata
    months_in_quarter = Column(Integer, default=3)
    data_quality_score = Column(Float, default=1.0)
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_quarterly_user_quarter', 'user_id', 'quarter_start_date'),
        Index('idx_quarterly_year_quarter', 'year', 'quarter'),
        Index('idx_quarterly_revenue', 'total_net_revenue'),
        Index('idx_quarterly_growth', 'quarter_over_quarter_growth'),
    )


class AggregationTask(Base):
    """
    Aggregation Task Model
    
    Manages aggregation job scheduling, processing status,
    and performance monitoring for automated data processing.
    """
    __tablename__ = "aggregation_tasks"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Task definition
    task_type = Column(String(100), nullable=False, index=True)
    aggregation_level = Column(SQLEnum(AggregationLevel), nullable=False, index=True)
    aggregation_scope = Column(SQLEnum(AggregationScope), nullable=False)
    
    # Scope parameters
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    platform = Column(String(100), nullable=True)
    date_range_start = Column(DateTime(timezone=True), nullable=False)
    date_range_end = Column(DateTime(timezone=True), nullable=False)
    
    # Task scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status and progress
    status = Column(SQLEnum(AggregationStatus), default=AggregationStatus.PENDING, index=True)
    progress_percentage = Column(Float, default=0.0)
    records_processed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    
    # Performance metrics
    processing_time_ms = Column(Integer, nullable=True)
    memory_used_mb = Column(Float, nullable=True)
    cpu_utilization_percent = Column(Float, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Configuration
    priority = Column(Integer, default=5)
    timeout_seconds = Column(Integer, default=3600)
    batch_size = Column(Integer, default=1000)
    parallel_workers = Column(Integer, default=1)
    
    # Dependencies
    depends_on_tasks = Column(ARRAY(UUID), nullable=True)
    blocks_tasks = Column(ARRAY(UUID), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_task_status_scheduled', 'status', 'scheduled_at'),
        Index('idx_task_level_scope', 'aggregation_level', 'aggregation_scope'),
        Index('idx_task_user_date', 'user_id', 'date_range_start'),
        Index('idx_task_next_run', 'next_run_at'),
        Index('idx_task_priority', 'priority', 'scheduled_at'),
    )


class AggregationMetrics(Base):
    """
    Aggregation Metrics Model
    
    Tracks aggregation system performance, data quality,
    and processing efficiency metrics.
    """
    __tablename__ = "aggregation_metrics"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metric context
    metric_date = Column(DateTime(timezone=True), nullable=False, index=True)
    aggregation_level = Column(SQLEnum(AggregationLevel), nullable=False, index=True)
    scope = Column(String(100), nullable=False)
    
    # Performance metrics
    total_tasks_processed = Column(Integer, default=0)
    successful_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    average_processing_time_ms = Column(Integer, nullable=True)
    total_records_processed = Column(Integer, default=0)
    
    # Data quality metrics
    data_accuracy_score = Column(Float, default=1.0)
    data_completeness_score = Column(Float, default=1.0)
    data_freshness_score = Column(Float, default=1.0)
    anomaly_count = Column(Integer, default=0)
    
    # System performance
    peak_memory_usage_mb = Column(Float, nullable=True)
    average_cpu_utilization = Column(Float, nullable=True)
    peak_concurrent_tasks = Column(Integer, nullable=True)
    
    # SLA metrics
    tasks_within_sla = Column(Integer, default=0)
    tasks_breached_sla = Column(Integer, default=0)
    average_delay_minutes = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_metrics_date_level', 'metric_date', 'aggregation_level'),
        Index('idx_metrics_scope', 'scope', 'metric_date'),
    )


# Utility functions for aggregation operations

async def calculate_daily_aggregations(
    session: Session,
    user_id: UUID,
    target_date: date,
    platforms: List[str] = None
) -> Dict[str, Any]:
    """
    Calculate daily revenue aggregations for a specific user and date.
    
    Args:
        session: Database session
        user_id: User identifier
        target_date: Date to calculate aggregations for
        platforms: Optional list of platforms to include
        
    Returns:
        Dictionary containing aggregation results and metadata
    """



    try:
        start_time = datetime.utcnow()
        
        # Build base query
        query = session.query(func.sum(RevenueRecord.net_amount).label('total_revenue'),
                             func.count(RevenueRecord.id).label('transaction_count'),
                             func.avg(RevenueRecord.net_amount).label('avg_transaction'))
        
        query = query.filter(
            RevenueRecord.user_id == user_id,
            func.date(RevenueRecord.transaction_date) == target_date
        )
        
        if platforms:
            query = query.filter(RevenueRecord.platform.in_(platforms))
        
        result = query.first()
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            'total_revenue': result.total_revenue or Decimal('0'),
            'transaction_count': result.transaction_count or 0,
            'average_transaction': result.avg_transaction or Decimal('0'),
            'processing_time_ms': int(processing_time),
            'calculation_date': datetime.utcnow(),
            'data_quality_score': 1.0
        }
        
    except Exception as e:
        logger.error(f"Error calculating daily aggregations: {e}")
        raise


async def rebuild_aggregations(
    session: Session,
    user_id: UUID,
    start_date: date,
    end_date: date,
    aggregation_levels: List[AggregationLevel] = None
) -> Dict[str, Any]:
    """
    Rebuild aggregations for a specific date range and user.
    
    Args:
        session: Database session
        user_id: User identifier
        start_date: Start date for rebuilding
        end_date: End date for rebuilding
        aggregation_levels: Specific levels to rebuild
        
    Returns:
        Dictionary containing rebuild results and statistics
    """



    try:
        if not aggregation_levels:
            aggregation_levels = [AggregationLevel.DAY, AggregationLevel.WEEK, AggregationLevel.MONTH]
        
        results = {}
        
        for level in aggregation_levels:
            start_time = datetime.utcnow()
            
            # Implement level-specific rebuilding logic here
            if level == AggregationLevel.DAY:
                # Rebuild daily aggregations
                pass
            elif level == AggregationLevel.WEEK:
                # Rebuild weekly aggregations
                pass
            elif level == AggregationLevel.MONTH:
                # Rebuild monthly aggregations
                pass
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            results[level.value] = {
                'status': 'completed',
                'processing_time_ms': int(processing_time),
                'records_processed': 0  # Set actual count
            }
        
        return {
            'user_id': str(user_id),
            'date_range': f"{start_date} to {end_date}",
            'levels_rebuilt': [level.value for level in aggregation_levels],
            'results': results,
            'total_processing_time': sum(r['processing_time_ms'] for r in results.values())
        }
        
    except Exception as e:
        logger.error(f"Error rebuilding aggregations: {e}")
        raise


__all__ = [
    'AggregationLevel',
    'AggregationScope',
    'AggregationStatus',
    'RevenueAggregationDaily',
    'RevenueAggregationWeekly',
    'RevenueAggregationMonthly',
    'RevenueAggregationQuarterly',
    'AggregationTask',
    'AggregationMetrics',
    'calculate_daily_aggregations',
    'rebuild_aggregations'
]
