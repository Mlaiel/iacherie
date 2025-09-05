"""Advanced monetization optimization system

Revision ID: i5h6g7f8e9d0
Revises: h4g5f6e7d8c9
Create Date: 2025-09-05 06:40:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the advanced monetization optimization system with
multi-tier subscriptions, AI revenue optimization, commission tracking,
and enterprise-grade revenue management.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'i5h6g7f8e9d0'
down_revision = 'h4g5f6e7d8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - Advanced monetization optimization system."""
    
    # Create subscription tier enum
    subscription_tier_enum = sa.Enum(
        'free', 'basic', 'professional', 'premium', 'enterprise', 'enterprise_plus',
        'celebrity', 'studio', 'label', 'agency', 'custom',
        name='subscription_tier'
    )
    
    # Create revenue stream type enum
    revenue_stream_type_enum = sa.Enum(
        'subscription', 'commission', 'advertising', 'sponsorship', 'licensing',
        'direct_sales', 'merchandise', 'live_streaming', 'tips', 'donations',
        'nft_sales', 'royalties', 'affiliate', 'brand_partnerships', 'courses',
        'consultations', 'premium_content', 'early_access', 'exclusive_content',
        name='revenue_stream_type'
    )
    
    # Create optimization strategy enum
    optimization_strategy_enum = sa.Enum(
        'maximize_revenue', 'maximize_engagement', 'maximize_retention', 
        'maximize_conversion', 'minimize_churn', 'balanced_growth',
        'viral_optimization', 'brand_building', 'audience_expansion',
        name='optimization_strategy'
    )
    
    # Create pricing model enum
    pricing_model_enum = sa.Enum(
        'fixed', 'dynamic', 'tiered', 'usage_based', 'performance_based',
        'auction', 'subscription', 'freemium', 'pay_per_view', 'revenue_share',
        name='pricing_model'
    )
    
    # Create subscription plans table
    op.create_table('subscription_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('plan_name', sa.String(100), nullable=False),
        sa.Column('plan_tier', subscription_tier_enum, nullable=False),
        sa.Column('display_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('base_price_monthly', sa.Numeric(10, 2), nullable=False),
        sa.Column('base_price_yearly', sa.Numeric(10, 2)),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        sa.Column('features_included', postgresql.JSONB, nullable=False, default={}),
        sa.Column('usage_limits', postgresql.JSONB, nullable=False, default={}),
        sa.Column('commission_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('ai_enhancement_quota', sa.Integer, nullable=False, default=0),
        sa.Column('storage_gb_limit', sa.Integer, nullable=False, default=1),
        sa.Column('bandwidth_gb_limit', sa.Integer, nullable=False, default=10),
        sa.Column('collaboration_slots', sa.Integer, nullable=False, default=0),
        sa.Column('priority_support', sa.Boolean, nullable=False, default=False),
        sa.Column('white_label_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('api_access_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('analytics_advanced', sa.Boolean, nullable=False, default=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('trial_period_days', sa.Integer, nullable=False, default=0),
        sa.Column('setup_fee', sa.Numeric(10, 2), nullable=False, default=0.00),
        sa.Column('cancellation_policy', sa.Text),
        sa.Column('target_audience', sa.String(200)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create revenue optimization profiles table
    op.create_table('revenue_optimization_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('optimization_strategy', optimization_strategy_enum, nullable=False),
        sa.Column('target_monthly_revenue', sa.Numeric(15, 2)),
        sa.Column('current_monthly_revenue', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('revenue_growth_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('preferred_revenue_streams', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('pricing_sensitivity', sa.Float, nullable=False, default=0.5),
        sa.Column('audience_willingness_to_pay', sa.Float, nullable=False, default=0.5),
        sa.Column('seasonal_patterns', postgresql.JSONB),
        sa.Column('geographic_preferences', postgresql.JSONB),
        sa.Column('demographic_targeting', postgresql.JSONB),
        sa.Column('competitive_analysis', postgresql.JSONB),
        sa.Column('ai_recommendations', postgresql.JSONB),
        sa.Column('optimization_score', sa.Float, nullable=False, default=0.0),
        sa.Column('last_optimization_run', sa.DateTime),
        sa.Column('next_optimization_due', sa.DateTime),
        sa.Column('auto_optimization_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create dynamic pricing rules table
    op.create_table('dynamic_pricing_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE')),
        sa.Column('rule_name', sa.String(200), nullable=False),
        sa.Column('pricing_model', pricing_model_enum, nullable=False),
        sa.Column('base_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('min_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('max_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('demand_multiplier', sa.Float, nullable=False, default=1.0),
        sa.Column('engagement_factor', sa.Float, nullable=False, default=1.0),
        sa.Column('time_decay_factor', sa.Float, nullable=False, default=1.0),
        sa.Column('scarcity_factor', sa.Float, nullable=False, default=1.0),
        sa.Column('geographic_multipliers', postgresql.JSONB),
        sa.Column('temporal_multipliers', postgresql.JSONB),
        sa.Column('audience_segment_multipliers', postgresql.JSONB),
        sa.Column('trigger_conditions', postgresql.JSONB, nullable=False),
        sa.Column('adjustment_frequency_hours', sa.Integer, nullable=False, default=24),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('performance_metrics', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create commission tracking table
    op.create_table('commission_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('transaction_id', sa.String(100), nullable=False),
        sa.Column('revenue_stream', revenue_stream_type_enum, nullable=False),
        sa.Column('gross_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('commission_rate', sa.Float, nullable=False),
        sa.Column('commission_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('net_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        sa.Column('platform_source', sa.String(100), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id')),
        sa.Column('collaboration_id', postgresql.UUID(as_uuid=True)),
        sa.Column('payout_status', sa.String(20), nullable=False, default='pending'),
        sa.Column('payout_date', sa.DateTime),
        sa.Column('payout_reference', sa.String(100)),
        sa.Column('tax_withheld', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('processing_fee', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('transaction_date', sa.DateTime, nullable=False),
        sa.Column('settlement_date', sa.DateTime),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create revenue analytics table
    op.create_table('revenue_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('analytics_date', sa.Date, nullable=False),
        sa.Column('total_revenue', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('subscription_revenue', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('commission_revenue', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('advertising_revenue', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('direct_sales_revenue', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('other_revenue', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('total_expenses', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('net_profit', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('profit_margin', sa.Float, nullable=False, default=0.0),
        sa.Column('revenue_per_user', sa.Numeric(10, 2), nullable=False, default=0.00),
        sa.Column('average_transaction_value', sa.Numeric(10, 2), nullable=False, default=0.00),
        sa.Column('conversion_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('churn_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('customer_lifetime_value', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('customer_acquisition_cost', sa.Numeric(10, 2), nullable=False, default=0.00),
        sa.Column('return_on_investment', sa.Float, nullable=False, default=0.0),
        sa.Column('revenue_growth_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('market_share_estimate', sa.Float, nullable=False, default=0.0),
        sa.Column('competitive_position', sa.String(20)),
        sa.Column('seasonality_factor', sa.Float, nullable=False, default=1.0),
        sa.Column('forecast_accuracy', sa.Float, nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create ai revenue recommendations table
    op.create_table('ai_revenue_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recommendation_type', sa.String(100), nullable=False),
        sa.Column('recommendation_title', sa.String(200), nullable=False),
        sa.Column('recommendation_description', sa.Text, nullable=False),
        sa.Column('expected_revenue_impact', sa.Numeric(15, 2)),
        sa.Column('confidence_score', sa.Float, nullable=False, default=0.0),
        sa.Column('implementation_effort', sa.String(20), nullable=False),
        sa.Column('time_to_implement_days', sa.Integer),
        sa.Column('priority_score', sa.Float, nullable=False, default=0.0),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('target_audience', sa.String(200)),
        sa.Column('success_metrics', postgresql.JSONB),
        sa.Column('implementation_steps', postgresql.JSONB),
        sa.Column('risk_factors', postgresql.JSONB),
        sa.Column('market_conditions', postgresql.JSONB),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('user_feedback', sa.Text),
        sa.Column('user_rating', sa.Integer),
        sa.Column('implemented_at', sa.DateTime),
        sa.Column('actual_revenue_impact', sa.Numeric(15, 2)),
        sa.Column('recommendation_accuracy', sa.Float),
        sa.Column('expires_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create performance indexes
    
    # Subscription Plans indexes
    op.create_index('idx_subscription_plans_tier', 'subscription_plans', ['plan_tier'])
    op.create_index('idx_subscription_plans_active', 'subscription_plans', ['is_active'])
    op.create_index('idx_subscription_plans_price', 'subscription_plans', ['base_price_monthly'])
    op.create_index('idx_subscription_plans_features', 'subscription_plans', ['features_included'], postgresql_using='gin')
    op.create_index('idx_subscription_plans_trial', 'subscription_plans', ['trial_period_days'])
    
    # Revenue Optimization Profiles indexes
    op.create_index('idx_revenue_optimization_user_id', 'revenue_optimization_profiles', ['user_id'])
    op.create_index('idx_revenue_optimization_strategy', 'revenue_optimization_profiles', ['optimization_strategy'])
    op.create_index('idx_revenue_optimization_score', 'revenue_optimization_profiles', ['optimization_score'])
    op.create_index('idx_revenue_optimization_target', 'revenue_optimization_profiles', ['target_monthly_revenue'])
    op.create_index('idx_revenue_optimization_current', 'revenue_optimization_profiles', ['current_monthly_revenue'])
    op.create_index('idx_revenue_optimization_growth', 'revenue_optimization_profiles', ['revenue_growth_rate'])
    op.create_index('idx_revenue_optimization_auto', 'revenue_optimization_profiles', ['auto_optimization_enabled'])
    
    # Dynamic Pricing Rules indexes
    op.create_index('idx_dynamic_pricing_user_id', 'dynamic_pricing_rules', ['user_id'])
    op.create_index('idx_dynamic_pricing_content_id', 'dynamic_pricing_rules', ['content_id'])
    op.create_index('idx_dynamic_pricing_model', 'dynamic_pricing_rules', ['pricing_model'])
    op.create_index('idx_dynamic_pricing_active', 'dynamic_pricing_rules', ['is_active'])
    op.create_index('idx_dynamic_pricing_base_price', 'dynamic_pricing_rules', ['base_price'])
    op.create_index('idx_dynamic_pricing_frequency', 'dynamic_pricing_rules', ['adjustment_frequency_hours'])
    
    # Commission Tracking indexes
    op.create_index('idx_commission_tracking_user_id', 'commission_tracking', ['user_id'])
    op.create_index('idx_commission_tracking_transaction', 'commission_tracking', ['transaction_id'])
    op.create_index('idx_commission_tracking_stream', 'commission_tracking', ['revenue_stream'])
    op.create_index('idx_commission_tracking_platform', 'commission_tracking', ['platform_source'])
    op.create_index('idx_commission_tracking_content', 'commission_tracking', ['content_id'])
    op.create_index('idx_commission_tracking_payout_status', 'commission_tracking', ['payout_status'])
    op.create_index('idx_commission_tracking_transaction_date', 'commission_tracking', ['transaction_date'])
    op.create_index('idx_commission_tracking_payout_date', 'commission_tracking', ['payout_date'])
    op.create_index('idx_commission_tracking_gross_amount', 'commission_tracking', ['gross_amount'])
    op.create_index('idx_commission_tracking_net_amount', 'commission_tracking', ['net_amount'])
    
    # Revenue Analytics indexes
    op.create_index('idx_revenue_analytics_user_id', 'revenue_analytics', ['user_id'])
    op.create_index('idx_revenue_analytics_date', 'revenue_analytics', ['analytics_date'])
    op.create_index('idx_revenue_analytics_total_revenue', 'revenue_analytics', ['total_revenue'])
    op.create_index('idx_revenue_analytics_net_profit', 'revenue_analytics', ['net_profit'])
    op.create_index('idx_revenue_analytics_growth_rate', 'revenue_analytics', ['revenue_growth_rate'])
    op.create_index('idx_revenue_analytics_margin', 'revenue_analytics', ['profit_margin'])
    op.create_index('idx_revenue_analytics_user_date', 'revenue_analytics', ['user_id', 'analytics_date'])
    
    # AI Revenue Recommendations indexes
    op.create_index('idx_ai_recommendations_user_id', 'ai_revenue_recommendations', ['user_id'])
    op.create_index('idx_ai_recommendations_type', 'ai_revenue_recommendations', ['recommendation_type'])
    op.create_index('idx_ai_recommendations_category', 'ai_revenue_recommendations', ['category'])
    op.create_index('idx_ai_recommendations_confidence', 'ai_revenue_recommendations', ['confidence_score'])
    op.create_index('idx_ai_recommendations_priority', 'ai_revenue_recommendations', ['priority_score'])
    op.create_index('idx_ai_recommendations_status', 'ai_revenue_recommendations', ['status'])
    op.create_index('idx_ai_recommendations_impact', 'ai_revenue_recommendations', ['expected_revenue_impact'])
    op.create_index('idx_ai_recommendations_expires', 'ai_revenue_recommendations', ['expires_at'])


def downgrade() -> None:
    """Downgrade database schema - Remove advanced monetization optimization tables."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('ai_revenue_recommendations')
    op.drop_table('revenue_analytics')
    op.drop_table('commission_tracking')
    op.drop_table('dynamic_pricing_rules')
    op.drop_table('revenue_optimization_profiles')
    op.drop_table('subscription_plans')
    
    # Drop ENUM types
    sa.Enum(name='pricing_model').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='optimization_strategy').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='revenue_stream_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='subscription_tier').drop(op.get_bind(), checkfirst=True)