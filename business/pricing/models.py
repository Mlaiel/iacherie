"""🚀 Pricing Models - Industrial-Grade Data Models for Pricing System
================================================================

Advanced data models and database schemas for comprehensive pricing management.
Supports multi-tier pricing, dynamic adjustments, usage tracking, and revenue optimization
across all content types and platforms.

Project Team Specialists:
- Lead Dev IA: Advanced AI architecture and ML optimization algorithms
- Backend Senior: Enterprise-grade API development and microservices
- ML Engineer: Machine learning models for pricing prediction and optimization
- DBA: High-performance database design and query optimization
- Security Expert: Enterprise security protocols and data protection
- Microservices Architect: Scalable distributed systems design
- Audio Engineer: Audio-specific pricing models and royalty calculations
- DevOps: CI/CD pipelines and production deployment automation
- IA Prompt Engineer: AI prompt optimization and natural language processing

Created by: Fahed Mlaiel <mlaiel@live.de>
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - UNAUTHORIZED USE PROHIBITED ⚠️

This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized copying, modification, distribution, or use of this code or its
underlying concepts without explicit written permission from Fahed Mlaiel is
strictly prohibited and will result in immediate legal action under German and
international copyright laws.

For licensing inquiries and authorization requests:
Email: mlaiel@live.de
All usage must be pre-approved in writing.

Business Logic Flow:
Creator Registration → Content Upload → Pricing Analysis → Dynamic Optimization → 
Revenue Tracking → Performance Analytics → Tier Management
================================================================
"""from sqlalchemy import Column, Integer, String, DateTime, Decimal, Boolean, JSON, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone
from decimal import Decimal as PyDecimal
from typing import Dict, List, Optional, Any
import uuid

Base = declarative_base()


class PricingStrategy(Base):
    """Pricing strategies configuration table"""    __tablename__ = 'pricing_strategies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    algorithm_config = Column(JSONB, nullable=False, default={})
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    pricing_calculations = relationship("PricingCalculation", back_populates="strategy")
    
    __table_args__ = (
        Index('idx_pricing_strategies_name', 'strategy_name'),
        Index('idx_pricing_strategies_active', 'is_active'),
    )


class PricingTierModel(Base):
    """Pricing tiers configuration table"""    __tablename__ = 'pricing_tiers'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tier_name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    base_monthly_price = Column(Decimal(10, 2), nullable=False)
    base_annual_price = Column(Decimal(10, 2), nullable=False)
    features = Column(ARRAY(String), nullable=False, default=[])
    usage_limits = Column(JSONB, nullable=False, default={})
    target_audience = Column(ARRAY(String), default=[])
    trial_days = Column(Integer, default=0)
    setup_fee = Column(Decimal(10, 2), default=PyDecimal('0'))
    cancellation_fee = Column(Decimal(10, 2), default=PyDecimal('0'))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_subscriptions = relationship("UserSubscription", back_populates="tier")
    tier_upgrades = relationship("TierUpgrade", back_populates="target_tier")
    
    __table_args__ = (
        Index('idx_pricing_tiers_name', 'tier_name'),
        Index('idx_pricing_tiers_active', 'is_active'),
        Index('idx_pricing_tiers_sort', 'sort_order'),
    )


class UserSubscription(Base):
    """User subscription management table"""    __tablename__ = 'user_subscriptions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    tier_id = Column(UUID(as_uuid=True), ForeignKey('pricing_tiers.id'), nullable=False)
    billing_cycle = Column(String(20), nullable=False)  # monthly, annual
    status = Column(String(20), nullable=False, default='active')  # active, cancelled, suspended
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    trial_start = Column(DateTime(timezone=True))
    trial_end = Column(DateTime(timezone=True))
    payment_method_id = Column(String(100))
    currency = Column(String(3), nullable=False, default='EUR')
    amount_paid = Column(Decimal(10, 2))
    tax_percentage = Column(Decimal(5, 2), default=PyDecimal('0'))
    discount_applied = Column(JSONB, default={})
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    tier = relationship("PricingTierModel", back_populates="user_subscriptions")
    usage_records = relationship("UsageRecord", back_populates="subscription")
    billing_events = relationship("BillingEvent", back_populates="subscription")
    
    __table_args__ = (
        Index('idx_user_subscriptions_user', 'user_id'),
        Index('idx_user_subscriptions_tier', 'tier_id'),
        Index('idx_user_subscriptions_status', 'status'),
        Index('idx_user_subscriptions_period', 'current_period_end'),
    )


class PricingCalculation(Base):
    """Pricing calculations and recommendations table"""    __tablename__ = 'pricing_calculations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('content.id'), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey('pricing_strategies.id'), nullable=False)
    content_type = Column(String(50), nullable=False)
    platform = Column(String(50), nullable=False)
    base_price = Column(Decimal(10, 2), nullable=False)
    optimized_price = Column(Decimal(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default='EUR')
    geographic_market = Column(String(10), nullable=False)
    pricing_factors = Column(JSONB, nullable=False, default={})
    market_analysis = Column(JSONB, nullable=False, default={})
    confidence_score = Column(Decimal(3, 2), nullable=False)
    predicted_conversion_rate = Column(Decimal(5, 4))
    estimated_roi = Column(Decimal(10, 2))
    calculation_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    is_applied = Column(Boolean, default=False)
    applied_at = Column(DateTime(timezone=True))
    performance_metrics = Column(JSONB, default={})
    
    # Relationships
    strategy = relationship("PricingStrategy", back_populates="pricing_calculations")
    
    __table_args__ = (
        Index('idx_pricing_calc_content', 'content_id'),
        Index('idx_pricing_calc_creator', 'creator_id'),
        Index('idx_pricing_calc_strategy', 'strategy_id'),
        Index('idx_pricing_calc_timestamp', 'calculation_timestamp'),
        Index('idx_pricing_calc_expires', 'expires_at'),
    )


class UsageRecord(Base):
    """Usage tracking for subscription limits"""    __tablename__ = 'usage_records'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('user_subscriptions.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    metric_name = Column(String(50), nullable=False)  # monthly_uploads, storage_gb, etc.
    metric_value = Column(Decimal(15, 2), nullable=False)
    usage_date = Column(DateTime(timezone=True), server_default=func.now())
    billing_period_start = Column(DateTime(timezone=True), nullable=False)
    billing_period_end = Column(DateTime(timezone=True), nullable=False)
    resource_id = Column(String(100))  # ID of resource that generated usage
    metadata = Column(JSONB, default={})
    
    # Relationships
    subscription = relationship("UserSubscription", back_populates="usage_records")
    
    __table_args__ = (
        Index('idx_usage_records_subscription', 'subscription_id'),
        Index('idx_usage_records_user', 'user_id'),
        Index('idx_usage_records_metric', 'metric_name'),
        Index('idx_usage_records_period', 'billing_period_start', 'billing_period_end'),
        Index('idx_usage_records_date', 'usage_date'),
    )


class TierUpgrade(Base):
    """Tier upgrade recommendations and history"""    __tablename__ = 'tier_upgrades'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    current_tier_id = Column(UUID(as_uuid=True), ForeignKey('pricing_tiers.id'))
    target_tier_id = Column(UUID(as_uuid=True), ForeignKey('pricing_tiers.id'), nullable=False)
    recommendation_reason = Column(Text)
    usage_analysis = Column(JSONB, nullable=False, default={})
    financial_impact = Column(JSONB, nullable=False, default={})
    roi_projection = Column(JSONB, default={})
    confidence_score = Column(Decimal(3, 2))
    status = Column(String(20), default='recommended')  # recommended, accepted, declined, completed
    recommended_at = Column(DateTime(timezone=True), server_default=func.now())
    response_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    target_tier = relationship("PricingTierModel", back_populates="tier_upgrades")
    
    __table_args__ = (
        Index('idx_tier_upgrades_user', 'user_id'),
        Index('idx_tier_upgrades_target', 'target_tier_id'),
        Index('idx_tier_upgrades_status', 'status'),
        Index('idx_tier_upgrades_recommended', 'recommended_at'),
    )


class BillingEvent(Base):
    """Billing events and payment history"""    __tablename__ = 'billing_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('user_subscriptions.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    event_type = Column(String(50), nullable=False)  # invoice_created, payment_succeeded, etc.
    amount = Column(Decimal(10, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    payment_method = Column(String(50))
    payment_processor = Column(String(50))  # stripe, paypal, wise
    processor_event_id = Column(String(200))
    status = Column(String(50), nullable=False)
    failure_reason = Column(Text)
    billing_period_start = Column(DateTime(timezone=True))
    billing_period_end = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True))
    invoice_url = Column(String(500))
    receipt_url = Column(String(500))
    tax_amount = Column(Decimal(10, 2))
    discount_amount = Column(Decimal(10, 2))
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    subscription = relationship("UserSubscription", back_populates="billing_events")
    
    __table_args__ = (
        Index('idx_billing_events_subscription', 'subscription_id'),
        Index('idx_billing_events_user', 'user_id'),
        Index('idx_billing_events_type', 'event_type'),
        Index('idx_billing_events_status', 'status'),
        Index('idx_billing_events_date', 'created_at'),
    )


class PricingAuditLog(Base):
    """Audit log for pricing changes and decisions"""    __tablename__ = 'pricing_audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)  # content, tier, strategy
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    action = Column(String(100), nullable=False)  # created, updated, calculated, applied
    old_values = Column(JSONB, default={})
    new_values = Column(JSONB, default={})
    change_reason = Column(Text)
    impact_analysis = Column(JSONB, default={})
    automated = Column(Boolean, default=True)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    session_id = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_pricing_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_pricing_audit_user', 'user_id'),
        Index('idx_pricing_audit_action', 'action'),
        Index('idx_pricing_audit_date', 'created_at'),
    )


class MarketIntelligence(Base):
    """Market intelligence data for pricing decisions"""    __tablename__ = 'market_intelligence'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_segment = Column(String(100), nullable=False)
    content_type = Column(String(50), nullable=False)
    geographic_market = Column(String(10), nullable=False)
    platform = Column(String(50), nullable=False)
    data_source = Column(String(100), nullable=False)
    average_price = Column(Decimal(10, 2))
    price_range_min = Column(Decimal(10, 2))
    price_range_max = Column(Decimal(10, 2))
    market_size = Column(Integer)
    competition_density = Column(Decimal(3, 2))
    demand_score = Column(Decimal(3, 2))
    growth_rate = Column(Decimal(5, 2))
    seasonal_patterns = Column(JSONB, default={})
    trend_indicators = Column(JSONB, default={})
    competitor_analysis = Column(JSONB, default={})
    data_quality_score = Column(Decimal(3, 2))
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    __table_args__ = (
        Index('idx_market_intel_segment', 'market_segment'),
        Index('idx_market_intel_content_type', 'content_type'),
        Index('idx_market_intel_geo', 'geographic_market'),
        Index('idx_market_intel_platform', 'platform'),
        Index('idx_market_intel_collected', 'collected_at'),
        Index('idx_market_intel_expires', 'expires_at'),
    )


class PricingExperiment(Base):
    """A/B testing for pricing strategies"""    __tablename__ = 'pricing_experiments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_name = Column(String(200), nullable=False)
    description = Column(Text)
    hypothesis = Column(Text)
    creator_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    content_type = Column(String(50))
    platform = Column(String(50))
    target_audience = Column(JSONB, default={})
    control_strategy = Column(JSONB, nullable=False)
    test_strategies = Column(JSONB, nullable=False)
    traffic_allocation = Column(JSONB, nullable=False)  # percentage split
    success_metrics = Column(ARRAY(String), nullable=False)
    minimum_sample_size = Column(Integer, default=100)
    confidence_level = Column(Decimal(3, 2), default=PyDecimal('0.95'))
    status = Column(String(20), default='draft')  # draft, running, completed, cancelled
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    results = Column(JSONB, default={})
    winner_strategy = Column(String(100))
    statistical_significance = Column(Boolean)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_pricing_exp_creator', 'creator_id'),
        Index('idx_pricing_exp_status', 'status'),
        Index('idx_pricing_exp_dates', 'start_date', 'end_date'),
    )


class DynamicPricingRule(Base):
    """Dynamic pricing rules and triggers"""    __tablename__ = 'dynamic_pricing_rules'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String(200), nullable=False)
    description = Column(Text)
    trigger_conditions = Column(JSONB, nullable=False)  # conditions that activate rule
    pricing_adjustments = Column(JSONB, nullable=False)  # how to adjust pricing
    applies_to = Column(JSONB, nullable=False)  # content types, tiers, etc.
    priority = Column(Integer, default=0)  # higher priority rules execute first
    max_adjustment_percent = Column(Decimal(5, 2))  # maximum adjustment allowed
    cooldown_hours = Column(Integer, default=24)  # minimum time between applications
    is_active = Column(Boolean, default=True)
    effectiveness_score = Column(Decimal(3, 2))
    usage_count = Column(Integer, default=0)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_applied_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('idx_dynamic_rules_active', 'is_active'),
        Index('idx_dynamic_rules_priority', 'priority'),
        Index('idx_dynamic_rules_effectiveness', 'effectiveness_score'),
    )
