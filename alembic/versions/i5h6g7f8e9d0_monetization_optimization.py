"""Advanced monetization optimization system

Revision ID: i5h6g7f8e9d0
Revises: h4g5f6e7d8c9
Create Date: 2025-09-05 06:40:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the advanced monetization optimization system with
multi-tier subscriptions, AI revenue optimization, commission tracking,
and enterprise-grade revenue management.

ENRICHISSEMENTS MASSIFS - VERSION 6.0 CONSOLIDATION INTELLIGENTE:
- NFT & Blockchain monetization
- IA revenue optimization
- Monetization avancée
- Analytics revenus
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
    """Upgrade database schema - Advanced monetization optimization system with MASSIVE ENRICHMENTS."""
    
    # === EXISTANT BASE ===
    create_monetization_base()
    
    # === ENRICHISSEMENTS MASSIFS ===
    
    # 1. NFT & BLOCKCHAIN MONETIZATION
    create_nft_marketplace_tables()
    create_crypto_token_economy()
    create_smart_contracts_revenue()
    create_decentralized_royalties()
    
    # 2. IA REVENUE OPTIMIZATION
    create_dynamic_pricing_ai()
    create_revenue_prediction_models()
    create_market_analysis_engine()
    create_competitor_pricing_intelligence()
    
    # 3. MONETIZATION AVANCÉE
    create_micro_transaction_system()
    create_subscription_optimization()
    create_freemium_conversion_engine()
    create_lifetime_value_prediction()
    
    # 4. ANALYTICS REVENUS
    create_revenue_attribution_system()
    create_profit_margin_optimization()
    create_tax_optimization_engine()


def create_monetization_base() -> None:
    """Create base monetization functionality - EXISTING"""
    
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


def create_nft_marketplace_tables() -> None:
    """1. NFT & BLOCKCHAIN MONETIZATION - NFT Marketplace"""
    
    # NFT collection management
    op.create_table('nft_collections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('collection_name', sa.String(255), nullable=False),
        sa.Column('collection_symbol', sa.String(10), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('blockchain_network', sa.String(100), nullable=False),  # Ethereum, Polygon, Solana
        sa.Column('contract_address', sa.String(255), nullable=True),
        sa.Column('contract_type', sa.String(50), nullable=False),  # ERC721, ERC1155
        sa.Column('total_supply', sa.Integer, nullable=True),
        sa.Column('minted_count', sa.Integer, nullable=False, default=0),
        sa.Column('floor_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('royalty_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('marketplace_commission', sa.Float, nullable=False, default=2.5),
        sa.Column('is_verified', sa.Boolean, nullable=False, default=False),
        sa.Column('metadata_uri', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    
    # Individual NFT tokens
    op.create_table('nft_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('collection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('nft_collections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=True),  # Link to original content
        sa.Column('token_id', sa.String(255), nullable=False),
        sa.Column('token_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('rarity_rank', sa.Integer, nullable=True),
        sa.Column('rarity_score', sa.Float, nullable=True),
        sa.Column('attributes', sa.JSON, nullable=True),
        sa.Column('metadata_uri', sa.String(500), nullable=True),
        sa.Column('image_uri', sa.String(500), nullable=True),
        sa.Column('animation_uri', sa.String(500), nullable=True),
        sa.Column('current_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('last_sale_price', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('highest_bid', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('is_listed', sa.Boolean, nullable=False, default=False),
        sa.Column('owner_address', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_crypto_token_economy() -> None:
    """1. NFT & BLOCKCHAIN MONETIZATION - Crypto Token Economy"""
    
    # Platform token system
    op.create_table('platform_token_economy',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('token_name', sa.String(100), nullable=False),
        sa.Column('token_symbol', sa.String(10), nullable=False),
        sa.Column('contract_address', sa.String(255), nullable=False),
        sa.Column('blockchain_network', sa.String(100), nullable=False),
        sa.Column('total_supply', sa.Numeric(precision=30, scale=0), nullable=False),
        sa.Column('circulating_supply', sa.Numeric(precision=30, scale=0), nullable=False),
        sa.Column('current_price_usd', sa.Numeric(precision=20, scale=8), nullable=True),
        sa.Column('market_cap_usd', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('utility_functions', sa.JSON, nullable=False),  # governance, staking, rewards
        sa.Column('staking_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('governance_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('reward_distribution_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('burn_mechanism_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
    
    # User token balances and transactions
    op.create_table('user_token_balances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_economy_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('platform_token_economy.id'), nullable=False),
        sa.Column('wallet_address', sa.String(255), nullable=False),
        sa.Column('balance', sa.Numeric(precision=30, scale=8), nullable=False, default=0),
        sa.Column('staked_amount', sa.Numeric(precision=30, scale=8), nullable=False, default=0),
        sa.Column('locked_amount', sa.Numeric(precision=30, scale=8), nullable=False, default=0),
        sa.Column('earned_rewards', sa.Numeric(precision=30, scale=8), nullable=False, default=0),
        sa.Column('voting_power', sa.Numeric(precision=30, scale=8), nullable=False, default=0),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'token_economy_id', name='unique_user_token_balance')
    )


def create_smart_contracts_revenue() -> None:
    """1. NFT & BLOCKCHAIN MONETIZATION - Smart Contracts Revenue"""
    
    # Smart contract revenue management
    op.create_table('smart_contract_revenue',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('contract_address', sa.String(255), nullable=False),
        sa.Column('contract_type', sa.String(100), nullable=False),  # NFT, DeFi, DAO, etc.
        sa.Column('revenue_sharing_rules', sa.JSON, nullable=False),
        sa.Column('automatic_distribution', sa.Boolean, nullable=False, default=True),
        sa.Column('royalty_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('platform_fee_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('gas_optimization_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('multi_sig_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('governance_token_rewards', sa.Boolean, nullable=False, default=False),
        sa.Column('liquidity_mining_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('yield_farming_apy', sa.Float, nullable=True),
        sa.Column('total_revenue_generated', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_decentralized_royalties() -> None:
    """1. NFT & BLOCKCHAIN MONETIZATION - Decentralized Royalties"""
    
    # Decentralized royalty distribution system
    op.create_table('decentralized_royalties',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('original_creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('smart_contract_address', sa.String(255), nullable=False),
        sa.Column('royalty_distribution_rules', sa.JSON, nullable=False),
        sa.Column('collaborator_shares', sa.JSON, nullable=True),  # revenue sharing with collaborators
        sa.Column('platform_share_percentage', sa.Float, nullable=False, default=5.0),
        sa.Column('creator_share_percentage', sa.Float, nullable=False, default=95.0),
        sa.Column('minimum_payout_threshold', sa.Numeric(precision=20, scale=8), nullable=False),
        sa.Column('payout_frequency', sa.String(50), nullable=False, default='monthly'),
        sa.Column('automatic_compound_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('dao_governance_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('total_royalties_earned', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('total_royalties_distributed', sa.Numeric(precision=20, scale=8), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_dynamic_pricing_ai() -> None:
    """2. IA REVENUE OPTIMIZATION - Dynamic Pricing AI"""
    
    # AI-powered dynamic pricing system
    op.create_table('dynamic_pricing_ai',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('pricing_model_version', sa.String(100), nullable=False),
        sa.Column('base_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('current_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('recommended_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('demand_score', sa.Float, nullable=False),  # 0-100
        sa.Column('competition_analysis', sa.JSON, nullable=True),
        sa.Column('market_trends', sa.JSON, nullable=True),
        sa.Column('seasonality_factors', sa.JSON, nullable=True),
        sa.Column('price_elasticity', sa.Float, nullable=True),
        sa.Column('conversion_optimization', sa.JSON, nullable=True),
        sa.Column('revenue_maximization_score', sa.Float, nullable=False),
        sa.Column('confidence_level', sa.Float, nullable=False),
        sa.Column('last_price_update', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_revenue_prediction_models() -> None:
    """2. IA REVENUE OPTIMIZATION - Revenue Prediction Models"""
    
    # Advanced revenue prediction system
    op.create_table('revenue_prediction_models',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('model_type', sa.String(100), nullable=False),  # LSTM, ARIMA, Prophet, XGBoost
        sa.Column('prediction_horizon', sa.String(50), nullable=False),  # daily, weekly, monthly, yearly
        sa.Column('historical_data_points', sa.Integer, nullable=False),
        sa.Column('feature_importance', sa.JSON, nullable=False),
        sa.Column('model_accuracy', sa.Float, nullable=False),
        sa.Column('mean_absolute_error', sa.Float, nullable=True),
        sa.Column('predicted_revenue_next_month', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('predicted_revenue_next_quarter', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('predicted_revenue_next_year', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('growth_trajectory', sa.JSON, nullable=True),
        sa.Column('risk_factors', sa.JSON, nullable=True),
        sa.Column('optimization_opportunities', sa.JSON, nullable=True),
        sa.Column('confidence_intervals', sa.JSON, nullable=True),
        sa.Column('model_last_trained', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_market_analysis_engine() -> None:
    """2. IA REVENUE OPTIMIZATION - Market Analysis Engine"""
    
    # Comprehensive market analysis system
    op.create_table('market_analysis_engine',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('analysis_scope', sa.String(100), nullable=False),  # platform, niche, global
        sa.Column('market_size_estimation', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('growth_rate_analysis', sa.JSON, nullable=False),
        sa.Column('competitive_landscape', sa.JSON, nullable=False),
        sa.Column('trend_analysis', sa.JSON, nullable=False),
        sa.Column('opportunity_assessment', sa.JSON, nullable=False),
        sa.Column('threat_analysis', sa.JSON, nullable=False),
        sa.Column('market_saturation_level', sa.Float, nullable=True),  # 0-100
        sa.Column('entry_barriers', sa.JSON, nullable=True),
        sa.Column('success_factors', sa.JSON, nullable=True),
        sa.Column('revenue_potential_score', sa.Float, nullable=False),
        sa.Column('recommended_strategies', sa.JSON, nullable=True),
        sa.Column('analysis_confidence', sa.Float, nullable=False),
        sa.Column('data_sources', sa.JSON, nullable=False),
        sa.Column('analysis_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_competitor_pricing_intelligence() -> None:
    """2. IA REVENUE OPTIMIZATION - Competitor Pricing Intelligence"""
    
    # Competitor pricing analysis system
    op.create_table('competitor_pricing_intelligence',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('competitor_analysis_scope', sa.String(200), nullable=False),
        sa.Column('identified_competitors', sa.JSON, nullable=False),
        sa.Column('price_comparison_matrix', sa.JSON, nullable=False),
        sa.Column('competitive_advantages', sa.JSON, nullable=True),
        sa.Column('pricing_gaps', sa.JSON, nullable=True),
        sa.Column('market_positioning', sa.JSON, nullable=False),
        sa.Column('price_elasticity_comparison', sa.JSON, nullable=True),
        sa.Column('value_proposition_analysis', sa.JSON, nullable=True),
        sa.Column('optimal_pricing_strategy', sa.JSON, nullable=False),
        sa.Column('expected_market_response', sa.JSON, nullable=True),
        sa.Column('risk_assessment', sa.JSON, nullable=True),
        sa.Column('monitoring_frequency', sa.String(50), nullable=False, default='daily'),
        sa.Column('last_analysis_update', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_micro_transaction_system() -> None:
    """3. MONETIZATION AVANCÉE - Micro Transaction System"""
    
    # Micro-transaction management system
    op.create_table('micro_transaction_system',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('transaction_type', sa.String(100), nullable=False),  # tip, super_chat, gift, etc.
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('platform_fee', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('creator_earning', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('payment_method', sa.String(100), nullable=False),
        sa.Column('transaction_context', sa.JSON, nullable=True),  # live stream, post, etc.
        sa.Column('user_message', sa.Text, nullable=True),
        sa.Column('is_anonymous', sa.Boolean, nullable=False, default=False),
        sa.Column('processing_status', sa.String(50), nullable=False, default='pending'),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_subscription_optimization() -> None:
    """3. MONETIZATION AVANCÉE - Subscription Optimization"""
    
    # Advanced subscription optimization system
    op.create_table('subscription_optimization',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('optimization_strategy', sa.String(100), nullable=False),
        sa.Column('current_tier_structure', sa.JSON, nullable=False),
        sa.Column('recommended_tier_structure', sa.JSON, nullable=False),
        sa.Column('pricing_psychology_insights', sa.JSON, nullable=True),
        sa.Column('value_perception_analysis', sa.JSON, nullable=True),
        sa.Column('churn_risk_factors', sa.JSON, nullable=True),
        sa.Column('retention_strategies', sa.JSON, nullable=True),
        sa.Column('upselling_opportunities', sa.JSON, nullable=True),
        sa.Column('cross_selling_potential', sa.JSON, nullable=True),
        sa.Column('lifetime_value_optimization', sa.JSON, nullable=True),
        sa.Column('engagement_correlation', sa.JSON, nullable=True),
        sa.Column('seasonal_adjustments', sa.JSON, nullable=True),
        sa.Column('a_b_test_recommendations', sa.JSON, nullable=True),
        sa.Column('implementation_roadmap', sa.JSON, nullable=True),
        sa.Column('expected_revenue_impact', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_freemium_conversion_engine() -> None:
    """3. MONETIZATION AVANCÉE - Freemium Conversion Engine"""
    
    # Freemium to premium conversion optimization
    op.create_table('freemium_conversion_engine',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('conversion_score', sa.Float, nullable=False),  # 0-100 likelihood to convert
        sa.Column('engagement_metrics', sa.JSON, nullable=False),
        sa.Column('usage_patterns', sa.JSON, nullable=False),
        sa.Column('content_consumption_behavior', sa.JSON, nullable=False),
        sa.Column('interaction_frequency', sa.Float, nullable=False),
        sa.Column('premium_feature_interests', sa.JSON, nullable=True),
        sa.Column('price_sensitivity', sa.Float, nullable=True),
        sa.Column('conversion_barriers', sa.JSON, nullable=True),
        sa.Column('personalized_offers', sa.JSON, nullable=True),
        sa.Column('optimal_conversion_timing', sa.JSON, nullable=True),
        sa.Column('conversion_funnel_stage', sa.String(100), nullable=False),
        sa.Column('recommended_actions', sa.JSON, nullable=True),
        sa.Column('conversion_probability', sa.Float, nullable=False),
        sa.Column('last_interaction_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_lifetime_value_prediction() -> None:
    """3. MONETIZATION AVANCÉE - Lifetime Value Prediction"""
    
    # Customer lifetime value prediction system
    op.create_table('lifetime_value_prediction',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('predicted_ltv', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('confidence_interval', sa.JSON, nullable=False),
        sa.Column('prediction_model_version', sa.String(100), nullable=False),
        sa.Column('customer_segment', sa.String(100), nullable=False),
        sa.Column('acquisition_cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('break_even_time_months', sa.Float, nullable=True),
        sa.Column('retention_probability', sa.Float, nullable=False),
        sa.Column('churn_risk_score', sa.Float, nullable=False),
        sa.Column('upselling_potential', sa.Float, nullable=False),
        sa.Column('engagement_value_correlation', sa.Float, nullable=True),
        sa.Column('seasonal_impact_factors', sa.JSON, nullable=True),
        sa.Column('value_drivers', sa.JSON, nullable=False),
        sa.Column('optimization_recommendations', sa.JSON, nullable=True),
        sa.Column('model_accuracy_score', sa.Float, nullable=False),
        sa.Column('prediction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_revenue_attribution_system() -> None:
    """4. ANALYTICS REVENUS - Revenue Attribution System"""
    
    # Advanced revenue attribution tracking
    op.create_table('revenue_attribution_system',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('revenue_transaction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('attribution_model', sa.String(100), nullable=False),  # first_touch, last_touch, multi_touch
        sa.Column('touchpoint_journey', sa.JSON, nullable=False),
        sa.Column('channel_attribution', sa.JSON, nullable=False),
        sa.Column('content_attribution', sa.JSON, nullable=False),
        sa.Column('campaign_attribution', sa.JSON, nullable=True),
        sa.Column('time_to_conversion', sa.Integer, nullable=True),  # hours
        sa.Column('conversion_path_length', sa.Integer, nullable=False),
        sa.Column('assisted_conversions', sa.JSON, nullable=True),
        sa.Column('direct_revenue_impact', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('assisted_revenue_impact', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('attribution_confidence', sa.Float, nullable=False),
        sa.Column('cross_device_tracking', sa.JSON, nullable=True),
        sa.Column('view_through_attribution', sa.JSON, nullable=True),
        sa.Column('incrementality_impact', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_profit_margin_optimization() -> None:
    """4. ANALYTICS REVENUS - Profit Margin Optimization"""
    
    # Profit margin analysis and optimization
    op.create_table('profit_margin_optimization',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('analysis_period', sa.String(50), nullable=False),  # monthly, quarterly, yearly
        sa.Column('gross_revenue', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('direct_costs', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('platform_fees', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('processing_fees', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('marketing_costs', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('content_production_costs', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('equipment_depreciation', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('net_profit', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('profit_margin_percentage', sa.Float, nullable=False),
        sa.Column('cost_breakdown_analysis', sa.JSON, nullable=False),
        sa.Column('optimization_opportunities', sa.JSON, nullable=False),
        sa.Column('cost_reduction_strategies', sa.JSON, nullable=True),
        sa.Column('revenue_enhancement_strategies', sa.JSON, nullable=True),
        sa.Column('benchmark_comparison', sa.JSON, nullable=True),
        sa.Column('efficiency_metrics', sa.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )


def create_tax_optimization_engine() -> None:
    """4. ANALYTICS REVENUS - Tax Optimization Engine"""
    
    # Automated tax optimization and compliance
    op.create_table('tax_optimization_engine',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tax_jurisdiction', sa.String(100), nullable=False),
        sa.Column('tax_year', sa.Integer, nullable=False),
        sa.Column('total_income', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('deductible_expenses', sa.JSON, nullable=False),
        sa.Column('equipment_depreciation_schedule', sa.JSON, nullable=True),
        sa.Column('business_expense_categories', sa.JSON, nullable=False),
        sa.Column('estimated_tax_liability', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('quarterly_payment_schedule', sa.JSON, nullable=True),
        sa.Column('tax_optimization_strategies', sa.JSON, nullable=False),
        sa.Column('retirement_contribution_recommendations', sa.JSON, nullable=True),
        sa.Column('business_structure_optimization', sa.JSON, nullable=True),
        sa.Column('international_tax_considerations', sa.JSON, nullable=True),
        sa.Column('compliance_requirements', sa.JSON, nullable=False),
        sa.Column('document_requirements', sa.JSON, nullable=False),
        sa.Column('potential_savings', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('risk_assessment', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    )
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