"""Dynamic Pricing Models - AI-Driven Dynamic Pricing & Revenue Optimization System

Ultra-advanced AI-powered dynamic pricing engine for optimal revenue generation
across all content types and platforms with real-time market analysis.

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

class PricingStrategy(Enum):
    """Dynamic pricing strategy types"""
    DEMAND_BASED = "demand_based"
    COMPETITOR_BASED = "competitor_based"
    VALUE_BASED = "value_based"
    PENETRATION = "penetration"
    SKIMMING = "skimming"
    PSYCHOLOGICAL = "psychological"
    BUNDLE = "bundle"
    FREEMIUM = "freemium"
    SURGE = "surge"
    PROMOTIONAL = "promotional"

class PriceAdjustmentType(Enum):
    """Price adjustment types"""
    INCREASE = "increase"
    DECREASE = "decrease"
    SURGE = "surge"
    DISCOUNT = "discount"
    PROMOTIONAL = "promotional"
    SEASONAL = "seasonal"
    DEMAND_SPIKE = "demand_spike"
    COMPETITOR_RESPONSE = "competitor_response"

class MarketCondition(Enum):
    """Market condition indicators"""
    HIGH_DEMAND = "high_demand"
    LOW_DEMAND = "low_demand"
    PEAK_HOURS = "peak_hours"
    OFF_PEAK = "off_peak"
    SEASONAL_HIGH = "seasonal_high"
    SEASONAL_LOW = "seasonal_low"
    COMPETITIVE_PRESSURE = "competitive_pressure"
    MARKET_SATURATION = "market_saturation"

class PricingRule(Base):
    """Dynamic pricing rules and strategies"""
    __tablename__ = 'pricing_rules'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String(200), nullable=False)
    rule_code = Column(String(50), unique=True, nullable=False)
    
    # Rule configuration
    strategy = Column(String(50), nullable=False)
    priority = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Target criteria
    content_types = Column(ARRAY(String))  # music, video, podcast, etc.
    platforms = Column(ARRAY(String))  # spotify, youtube, etc.
    regions = Column(ARRAY(String))  # US, EU, etc.
    customer_segments = Column(ARRAY(String))  # premium, basic, etc.
    
    # Pricing parameters
    base_price_multiplier = Column(Float, default=1.0)
    minimum_price = Column(DECIMAL(10, 4))
    maximum_price = Column(DECIMAL(10, 4))
    price_elasticity = Column(Float, default=1.0)
    
    # Trigger conditions
    demand_threshold_high = Column(Float, default=80.0)  # percentage
    demand_threshold_low = Column(Float, default=20.0)  # percentage
    competitor_price_variance = Column(Float, default=10.0)  # percentage
    inventory_threshold = Column(Float, default=90.0)  # percentage
    
    # Adjustment parameters
    max_increase_percentage = Column(Float, default=50.0)
    max_decrease_percentage = Column(Float, default=30.0)
    adjustment_frequency_minutes = Column(Integer, default=60)
    cooldown_period_minutes = Column(Integer, default=30)
    
    # Time-based rules
    time_based_active = Column(Boolean, default=False)
    peak_hours_start = Column(String(5))  # HH:MM format
    peak_hours_end = Column(String(5))  # HH:MM format
    peak_multiplier = Column(Float, default=1.2)
    off_peak_multiplier = Column(Float, default=0.9)
    
    # Seasonal adjustments
    seasonal_active = Column(Boolean, default=False)
    seasonal_patterns = Column(JSONB)  # Month-based multipliers
    holiday_multipliers = Column(JSONB)  # Special event multipliers
    
    # Performance tracking
    total_applications = Column(Integer, default=0)
    successful_applications = Column(Integer, default=0)
    revenue_impact = Column(DECIMAL(15, 4), default=0)
    last_applied_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_pricing_rule_strategy', 'strategy', 'is_active'),
        Index('idx_pricing_rule_priority', 'priority', 'is_active'),
    )

class DynamicPrice(Base):
    """Current dynamic pricing for content/services"""
    __tablename__ = 'dynamic_prices'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    service_id = Column(UUID(as_uuid=True), index=True)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Pricing details
    base_price = Column(DECIMAL(10, 4), nullable=False)
    current_price = Column(DECIMAL(10, 4), nullable=False)
    suggested_price = Column(DECIMAL(10, 4))
    minimum_price = Column(DECIMAL(10, 4))
    maximum_price = Column(DECIMAL(10, 4))
    
    # Currency and localization
    currency = Column(String(3), default='USD')
    region = Column(String(10))
    market_segment = Column(String(50))
    
    # Context information
    platform_id = Column(String(100), nullable=False)
    content_type = Column(String(50), nullable=False)
    service_type = Column(String(50))
    
    # Market conditions
    current_demand_score = Column(Float, default=0.0)
    competitor_average_price = Column(DECIMAL(10, 4))
    market_position = Column(String(20))  # premium, competitive, value
    
    # Performance metrics
    conversion_rate = Column(Float, default=0.0)
    sales_velocity = Column(Float, default=0.0)
    revenue_per_period = Column(DECIMAL(15, 4), default=0)
    price_elasticity_observed = Column(Float, default=1.0)
    
    # AI predictions
    demand_forecast = Column(Float, default=0.0)
    optimal_price_prediction = Column(DECIMAL(10, 4))
    revenue_prediction = Column(DECIMAL(15, 4))
    confidence_score = Column(Float, default=0.0)
    
    # Adjustment tracking
    last_adjustment_amount = Column(DECIMAL(10, 4), default=0)
    last_adjustment_type = Column(String(50))
    last_adjustment_reason = Column(String(200))
    adjustment_count_today = Column(Integer, default=0)
    
    # Status and control
    is_active = Column(Boolean, default=True)
    manual_override = Column(Boolean, default=False)
    override_reason = Column(String(200))
    override_until = Column(DateTime(timezone=True))
    
    # Timestamps
    price_effective_from = Column(DateTime(timezone=True), default=func.now())
    price_effective_until = Column(DateTime(timezone=True))
    last_updated_at = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_dynamic_price_content_platform', 'content_id', 'platform_id'),
        Index('idx_dynamic_price_creator_active', 'creator_id', 'is_active'),
        Index('idx_dynamic_price_effective', 'price_effective_from', 'price_effective_until'),
        UniqueConstraint('content_id', 'platform_id', 'region', name='uq_dynamic_price_unique'),
    )

class PriceHistory(Base):
    """Historical price changes and performance"""
    __tablename__ = 'price_history'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dynamic_price_id = Column(UUID(as_uuid=True), ForeignKey('dynamic_prices.id'), nullable=False)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Price change details
    previous_price = Column(DECIMAL(10, 4), nullable=False)
    new_price = Column(DECIMAL(10, 4), nullable=False)
    price_change_amount = Column(DECIMAL(10, 4), nullable=False)
    price_change_percentage = Column(Float, nullable=False)
    
    # Change context
    adjustment_type = Column(String(50), nullable=False)
    adjustment_reason = Column(String(200))
    triggered_by_rule_id = Column(UUID(as_uuid=True), ForeignKey('pricing_rules.id'))
    manual_adjustment = Column(Boolean, default=False)
    adjusted_by_user_id = Column(UUID(as_uuid=True))
    
    # Market conditions at time of change
    demand_score_at_change = Column(Float)
    competitor_price_at_change = Column(DECIMAL(10, 4))
    market_condition = Column(String(50))
    
    # Performance before change (last 24h)
    sales_before_change = Column(Integer, default=0)
    revenue_before_change = Column(DECIMAL(15, 4), default=0)
    conversion_rate_before = Column(Float, default=0.0)
    
    # Performance after change (next 24h)
    sales_after_change = Column(Integer, default=0)
    revenue_after_change = Column(DECIMAL(15, 4), default=0)
    conversion_rate_after = Column(Float, default=0.0)
    
    # Effectiveness metrics
    performance_impact_score = Column(Float, default=0.0)
    revenue_impact = Column(DECIMAL(15, 4), default=0)
    success_rating = Column(Integer)  # 1-5 rating
    
    # Time tracking
    price_effective_from = Column(DateTime(timezone=True), nullable=False)
    price_effective_until = Column(DateTime(timezone=True))
    change_timestamp = Column(DateTime(timezone=True), default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    dynamic_price = relationship("DynamicPrice", backref="price_history")
    pricing_rule = relationship("PricingRule", backref="price_changes")
    
    # Indexes
    __table_args__ = (
        Index('idx_price_history_content_date', 'content_id', 'change_timestamp'),
        Index('idx_price_history_creator_date', 'creator_id', 'change_timestamp'),
        Index('idx_price_history_rule', 'triggered_by_rule_id', 'change_timestamp'),
    )

class MarketAnalysis(Base):
    """Real-time market analysis for pricing decisions"""
    __tablename__ = 'market_analysis'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_timestamp = Column(DateTime(timezone=True), default=func.now())
    
    # Market scope
    platform_id = Column(String(100), nullable=False)
    content_category = Column(String(50), nullable=False)
    region = Column(String(10), nullable=False)
    market_segment = Column(String(50))
    
    # Market metrics
    total_market_size = Column(BigInteger, default=0)
    active_competitors = Column(Integer, default=0)
    average_market_price = Column(DECIMAL(10, 4))
    median_market_price = Column(DECIMAL(10, 4))
    price_variance = Column(Float, default=0.0)
    
    # Demand indicators
    search_volume = Column(BigInteger, default=0)
    engagement_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    demand_trend = Column(String(20))  # increasing, decreasing, stable
    demand_volatility = Column(Float, default=0.0)
    
    # Competitive landscape
    top_competitor_prices = Column(JSONB)  # Top 10 competitor prices
    price_leadership_score = Column(Float, default=0.0)  # How often we lead price changes
    competitive_advantage = Column(Float, default=0.0)  # -1 to 1 scale
    
    # Trend analysis
    price_trend_7d = Column(Float, default=0.0)  # 7-day price trend
    price_trend_30d = Column(Float, default=0.0)  # 30-day price trend
    volume_trend_7d = Column(Float, default=0.0)  # 7-day volume trend
    volume_trend_30d = Column(Float, default=0.0)  # 30-day volume trend
    
    # Seasonal patterns
    seasonal_demand_factor = Column(Float, default=1.0)
    holiday_impact_factor = Column(Float, default=1.0)
    day_of_week_factor = Column(Float, default=1.0)
    hour_of_day_factor = Column(Float, default=1.0)
    
    # Economic indicators
    economic_confidence_index = Column(Float, default=0.0)
    consumer_spending_index = Column(Float, default=0.0)
    market_volatility_index = Column(Float, default=0.0)
    
    # AI insights
    recommended_strategy = Column(String(50))
    confidence_level = Column(Float, default=0.0)
    risk_assessment = Column(String(20))  # low, medium, high
    opportunity_score = Column(Float, default=0.0)
    
    # Data sources
    data_sources = Column(JSONB)  # List of data sources used
    data_quality_score = Column(Float, default=0.0)
    last_refresh_timestamp = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_market_analysis_platform_category', 'platform_id', 'content_category'),
        Index('idx_market_analysis_region_timestamp', 'region', 'analysis_timestamp'),
        Index('idx_market_analysis_timestamp', 'analysis_timestamp'),
    )

class CompetitorPricing(Base):
    """Competitor pricing data for market analysis"""
    __tablename__ = 'competitor_pricing'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(String(100), nullable=False, index=True)
    competitor_name = Column(String(200), nullable=False)
    
    # Product/content details
    competitor_content_id = Column(String(100))
    content_category = Column(String(50), nullable=False)
    content_type = Column(String(50), nullable=False)
    platform_id = Column(String(100), nullable=False)
    
    # Pricing information
    current_price = Column(DECIMAL(10, 4), nullable=False)
    previous_price = Column(DECIMAL(10, 4))
    base_price = Column(DECIMAL(10, 4))
    promotional_price = Column(DECIMAL(10, 4))
    currency = Column(String(3), default='USD')
    
    # Market position
    market_share = Column(Float, default=0.0)
    popularity_rank = Column(Integer)
    quality_score = Column(Float, default=0.0)
    brand_strength = Column(Float, default=0.0)
    
    # Performance metrics
    estimated_sales_volume = Column(BigInteger, default=0)
    estimated_revenue = Column(DECIMAL(15, 4), default=0)
    growth_rate = Column(Float, default=0.0)
    customer_satisfaction = Column(Float, default=0.0)
    
    # Pricing strategy indicators
    pricing_frequency = Column(Integer, default=0)  # Changes per month
    price_volatility = Column(Float, default=0.0)
    discount_frequency = Column(Float, default=0.0)
    premium_positioning = Column(Boolean, default=False)
    
    # Data collection
    data_source = Column(String(100), nullable=False)
    collection_method = Column(String(50))  # api, scraping, manual
    data_confidence = Column(Float, default=0.0)
    last_verified_at = Column(DateTime(timezone=True))
    
    # Geographic data
    region = Column(String(10), nullable=False)
    country_code = Column(String(2))
    local_factors = Column(JSONB)  # Local market factors
    
    # Timestamps
    price_observed_at = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_competitor_platform_category', 'platform_id', 'content_category'),
        Index('idx_competitor_observed_at', 'price_observed_at'),
        Index('idx_competitor_name_region', 'competitor_name', 'region'),
    )

@dataclass
class PricingRecommendation:
    """AI-generated pricing recommendation"""
    recommended_price: float
    confidence_score: float
    expected_revenue_impact: float
    risk_level: str
    strategy: str
    reasoning: str
    supporting_factors: List[str]
    implementation_timeline: str

class PricingExperiment(Base):
    """A/B testing for pricing strategies"""
    __tablename__ = 'pricing_experiments'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_name = Column(String(200), nullable=False)
    experiment_code = Column(String(50), unique=True, nullable=False)
    
    # Experiment configuration
    hypothesis = Column(Text, nullable=False)
    test_type = Column(String(20), nullable=False)  # ab_test, multivariate, cohort
    status = Column(String(20), default='draft')  # draft, running, paused, completed, cancelled
    
    # Test parameters
    control_price = Column(DECIMAL(10, 4), nullable=False)
    variant_prices = Column(JSONB, nullable=False)  # Array of test prices
    traffic_allocation = Column(JSONB, nullable=False)  # Percentage allocation
    
    # Scope and targeting
    target_content_ids = Column(ARRAY(String))
    target_platforms = Column(ARRAY(String))
    target_regions = Column(ARRAY(String))
    target_segments = Column(ARRAY(String))
    
    # Duration and timing
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    minimum_sample_size = Column(Integer, default=1000)
    confidence_level = Column(Float, default=95.0)
    
    # Success metrics
    primary_metric = Column(String(50), nullable=False)  # revenue, conversion, volume
    secondary_metrics = Column(ARRAY(String))
    success_threshold = Column(Float, nullable=False)
    
    # Results tracking
    participants_control = Column(Integer, default=0)
    participants_variants = Column(JSONB)  # Participants per variant
    conversions_control = Column(Integer, default=0)
    conversions_variants = Column(JSONB)  # Conversions per variant
    revenue_control = Column(DECIMAL(15, 4), default=0)
    revenue_variants = Column(JSONB)  # Revenue per variant
    
    # Statistical analysis
    statistical_significance = Column(Float, default=0.0)
    confidence_interval = Column(JSONB)
    p_value = Column(Float, default=1.0)
    effect_size = Column(Float, default=0.0)
    
    # Results and conclusions
    winning_variant = Column(String(50))
    performance_lift = Column(Float, default=0.0)
    conclusion = Column(Text)
    recommendations = Column(JSONB)
    
    # Control and safety
    early_stopping_rules = Column(JSONB)
    safety_thresholds = Column(JSONB)
    stopped_early = Column(Boolean, default=False)
    stop_reason = Column(String(200))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_experiment_status_dates', 'status', 'start_date', 'end_date'),
        Index('idx_experiment_platforms', 'target_platforms'),
    )

# Export all models for easy import
__all__ = [
    'PricingStrategy',
    'PriceAdjustmentType',
    'MarketCondition',
    'PricingRule',
    'DynamicPrice',
    'PriceHistory',
    'MarketAnalysis',
    'CompetitorPricing',
    'PricingRecommendation',
    'PricingExperiment'
]
