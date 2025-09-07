"""Add monetization enterprise tables

Revision ID: 001_add_monetization_tables
Revises: 
Create Date: 2025-09-07 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_monetization_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add monetization enterprise tables."""
    
    # Create creator_monetization_profiles table
    op.create_table('creator_monetization_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('creator_type', sa.Enum('musician', 'blogger', 'photographer', 'influencer', 'comedian', 'podcaster', 'video_creator', 'artist', name='creatortype'), nullable=False),
        sa.Column('monetization_preferences', sa.JSON(), nullable=True),
        sa.Column('revenue_goals', sa.JSON(), nullable=True),
        sa.Column('preferred_payment_methods', sa.JSON(), nullable=True),
        sa.Column('tax_settings', sa.JSON(), nullable=True),
        sa.Column('payout_schedule', sa.Enum('daily', 'weekly', 'monthly', 'on_demand', name='payoutschedule'), nullable=True),
        sa.Column('minimum_payout_threshold', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('auto_optimization_enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_creator_monetization_profiles_creator_id'), 'creator_monetization_profiles', ['creator_id'], unique=False)
    op.create_index(op.f('ix_creator_monetization_profiles_creator_type'), 'creator_monetization_profiles', ['creator_type'], unique=False)

    # Create ai_revenue_optimizations table
    op.create_table('ai_revenue_optimizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('optimization_type', sa.Enum('pricing', 'platform_selection', 'timing', 'audience_targeting', 'collaboration_matching', name='optimizationtype'), nullable=False),
        sa.Column('ai_model_version', sa.String(length=50), nullable=True),
        sa.Column('optimization_suggestions', sa.JSON(), nullable=False),
        sa.Column('predicted_revenue_increase', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('confidence_score', sa.DECIMAL(precision=5, scale=4), nullable=True),
        sa.Column('implementation_status', sa.Enum('pending', 'implemented', 'rejected', 'expired', name='implementationstatus'), nullable=True),
        sa.Column('actual_revenue_impact', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('implementation_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['creator_monetization_profiles.creator_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_revenue_optimizations_confidence_score'), 'ai_revenue_optimizations', ['confidence_score'], unique=False)
    op.create_index(op.f('ix_ai_revenue_optimizations_implementation_status'), 'ai_revenue_optimizations', ['implementation_status'], unique=False)
    op.create_index(op.f('ix_ai_revenue_optimizations_optimization_type'), 'ai_revenue_optimizations', ['optimization_type'], unique=False)

    # Create collaboration_revenue_contracts table
    op.create_table('collaboration_revenue_contracts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contract_type', sa.Enum('revenue_sharing', 'fixed_payment', 'hybrid', 'milestone_based', name='contracttype'), nullable=False),
        sa.Column('participants', sa.JSON(), nullable=False),
        sa.Column('revenue_split_rules', sa.JSON(), nullable=False),
        sa.Column('payment_schedule', sa.JSON(), nullable=True),
        sa.Column('contract_terms', sa.JSON(), nullable=True),
        sa.Column('auto_distribution_enabled', sa.Boolean(), nullable=True),
        sa.Column('tax_handling', sa.Enum('individual', 'collective', 'platform_managed', name='taxhandling'), nullable=True),
        sa.Column('contract_status', sa.Enum('draft', 'pending_signatures', 'active', 'completed', 'disputed', 'cancelled', name='contractstatus'), nullable=True),
        sa.Column('total_revenue_distributed', sa.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_collaboration_revenue_contracts_auto_distribution_enabled'), 'collaboration_revenue_contracts', ['auto_distribution_enabled'], unique=False)
    op.create_index(op.f('ix_collaboration_revenue_contracts_contract_status'), 'collaboration_revenue_contracts', ['contract_status'], unique=False)
    op.create_index(op.f('ix_collaboration_revenue_contracts_project_id'), 'collaboration_revenue_contracts', ['project_id'], unique=False)

    # Create protection_revenue_recovery table
    op.create_table('protection_revenue_recovery',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('violation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recovery_type', sa.Enum('dmca_settlement', 'legal_action', 'platform_compensation', 'negotiated_settlement', name='recoverytype'), nullable=False),
        sa.Column('claimed_amount', sa.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('recovered_amount', sa.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('recovery_status', sa.Enum('identified', 'claimed', 'negotiating', 'settled', 'rejected', 'litigation', name='recoverystatus'), nullable=True),
        sa.Column('recovery_fees', sa.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('net_recovery', sa.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('recovery_date', sa.DateTime(), nullable=True),
        sa.Column('settlement_terms', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['content.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_protection_revenue_recovery_content_id'), 'protection_revenue_recovery', ['content_id'], unique=False)
    op.create_index(op.f('ix_protection_revenue_recovery_recovered_amount'), 'protection_revenue_recovery', ['recovered_amount'], unique=False)
    op.create_index(op.f('ix_protection_revenue_recovery_recovery_status'), 'protection_revenue_recovery', ['recovery_status'], unique=False)

    # Create gamification_monetization_rewards table
    op.create_table('gamification_monetization_rewards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('achievement_type', sa.String(length=100), nullable=True),
        sa.Column('reward_type', sa.Enum('cash_bonus', 'revenue_multiplier', 'platform_credits', 'premium_features', 'collaboration_boost', name='rewardtype'), nullable=False),
        sa.Column('reward_value', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('reward_description', sa.Text(), nullable=True),
        sa.Column('eligibility_criteria', sa.JSON(), nullable=True),
        sa.Column('redemption_status', sa.Enum('earned', 'pending', 'redeemed', 'expired', name='redemptionstatus'), nullable=True),
        sa.Column('earned_date', sa.DateTime(), nullable=True),
        sa.Column('redeemed_date', sa.DateTime(), nullable=True),
        sa.Column('expiry_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['creator_monetization_profiles.creator_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gamification_monetization_rewards_creator_id'), 'gamification_monetization_rewards', ['creator_id', 'earned_date'], unique=False)
    op.create_index(op.f('ix_gamification_monetization_rewards_redemption_status'), 'gamification_monetization_rewards', ['redemption_status'], unique=False)
    op.create_index(op.f('ix_gamification_monetization_rewards_reward_type'), 'gamification_monetization_rewards', ['reward_type'], unique=False)

    # Create seo_revenue_optimization table
    op.create_table('seo_revenue_optimization',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('seo_strategy', sa.JSON(), nullable=True),
        sa.Column('target_keywords', sa.JSON(), nullable=True),
        sa.Column('optimization_goals', sa.JSON(), nullable=True),
        sa.Column('predicted_traffic_increase', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('predicted_revenue_increase', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('actual_traffic_impact', sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column('actual_revenue_impact', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('optimization_roi', sa.DECIMAL(precision=8, scale=4), nullable=True),
        sa.Column('optimization_status', sa.Enum('planned', 'implementing', 'monitoring', 'completed', 'failed', name='optimizationstatus'), nullable=True),
        sa.Column('implementation_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['content.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_seo_revenue_optimization_content_id'), 'seo_revenue_optimization', ['content_id'], unique=False)
    op.create_index(op.f('ix_seo_revenue_optimization_optimization_roi'), 'seo_revenue_optimization', ['optimization_roi'], unique=False)
    op.create_index(op.f('ix_seo_revenue_optimization_optimization_status'), 'seo_revenue_optimization', ['optimization_status'], unique=False)


def downgrade() -> None:
    """Drop monetization enterprise tables."""
    
    # Drop tables in reverse order
    op.drop_table('seo_revenue_optimization')
    op.drop_table('gamification_monetization_rewards')
    op.drop_table('protection_revenue_recovery')
    op.drop_table('collaboration_revenue_contracts')
    op.drop_table('ai_revenue_optimizations')
    op.drop_table('creator_monetization_profiles')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS optimizationstatus")
    op.execute("DROP TYPE IF EXISTS redemptionstatus")
    op.execute("DROP TYPE IF EXISTS rewardtype")
    op.execute("DROP TYPE IF EXISTS recoverystatus")
    op.execute("DROP TYPE IF EXISTS recoverytype")
    op.execute("DROP TYPE IF EXISTS contractstatus")
    op.execute("DROP TYPE IF EXISTS taxhandling")
    op.execute("DROP TYPE IF EXISTS contracttype")
    op.execute("DROP TYPE IF EXISTS implementationstatus")
    op.execute("DROP TYPE IF EXISTS optimizationtype")
    op.execute("DROP TYPE IF EXISTS payoutschedule")
    op.execute("DROP TYPE IF EXISTS creatortype")