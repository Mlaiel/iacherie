"""Advanced gamification engine system

Revision ID: m9l0k1j2i3h4
Revises: l8k9j0i1h2g3
Create Date: 2025-09-05 07:00:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the advanced gamification engine with points, badges,
leaderboards, achievements, rewards automation, and engagement analytics
for enhanced user motivation and platform engagement.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'm9l0k1j2i3h4'
down_revision = 'l8k9j0i1h2g3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - Advanced gamification engine system."""
    
    # Create achievement category enum
    achievement_category_enum = sa.Enum(
        'content_creation', 'collaboration', 'engagement', 'revenue', 'learning',
        'community', 'quality', 'consistency', 'innovation', 'leadership',
        'mentorship', 'technical_skill', 'creativity', 'social_impact', 'milestone',
        name='achievement_category'
    )
    
    # Create badge rarity enum
    badge_rarity_enum = sa.Enum(
        'common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic', 'unique',
        name='badge_rarity'
    )
    
    # Create reward type enum
    reward_type_enum = sa.Enum(
        'points', 'badge', 'premium_features', 'discount', 'cash_bonus',
        'storage_upgrade', 'processing_credits', 'exclusive_access', 'merchandise',
        'consultation_time', 'collaboration_priority', 'featured_content',
        'custom_profile', 'early_access', 'nft_collectible', 'virtual_currency',
        name='reward_type'
    )
    
    # Create leaderboard type enum
    leaderboard_type_enum = sa.Enum(
        'global', 'regional', 'category', 'skill_level', 'collaboration',
        'monthly', 'weekly', 'daily', 'all_time', 'trending', 'rising_star',
        name='leaderboard_type'
    )
    
    # Create user points system table
    op.create_table('user_points_system',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('total_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('lifetime_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('points_spent', sa.BigInteger, nullable=False, default=0),
        sa.Column('content_creation_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('collaboration_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('engagement_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('quality_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('consistency_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('community_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('learning_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('mentorship_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('innovation_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('leadership_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('current_level', sa.Integer, nullable=False, default=1),
        sa.Column('experience_points', sa.BigInteger, nullable=False, default=0),
        sa.Column('points_to_next_level', sa.BigInteger, nullable=False, default=100),
        sa.Column('level_progression_history', postgresql.JSONB, nullable=False, default=[]),
        sa.Column('daily_points_earned', sa.Integer, nullable=False, default=0),
        sa.Column('weekly_points_earned', sa.Integer, nullable=False, default=0),
        sa.Column('monthly_points_earned', sa.Integer, nullable=False, default=0),
        sa.Column('point_multiplier', sa.Float, nullable=False, default=1.0),
        sa.Column('bonus_multiplier_expires_at', sa.DateTime),
        sa.Column('streak_days', sa.Integer, nullable=False, default=0),
        sa.Column('longest_streak', sa.Integer, nullable=False, default=0),
        sa.Column('last_activity_date', sa.Date),
        sa.Column('tier_level', sa.String(20), nullable=False, default='bronze'),
        sa.Column('tier_benefits', postgresql.JSONB, nullable=False, default={}),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create achievements definition table
    op.create_table('achievements_definition',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('achievement_key', sa.String(100), nullable=False, unique=True),
        sa.Column('achievement_name', sa.String(200), nullable=False),
        sa.Column('achievement_description', sa.Text, nullable=False),
        sa.Column('category', achievement_category_enum, nullable=False),
        sa.Column('difficulty_level', sa.Integer, nullable=False, default=1),
        sa.Column('points_reward', sa.Integer, nullable=False, default=0),
        sa.Column('badge_reward', sa.String(100)),
        sa.Column('unlock_criteria', postgresql.JSONB, nullable=False),
        sa.Column('progress_tracking', postgresql.JSONB, nullable=False, default={}),
        sa.Column('is_repeatable', sa.Boolean, nullable=False, default=False),
        sa.Column('cooldown_period_hours', sa.Integer, nullable=False, default=0),
        sa.Column('seasonal_achievement', sa.Boolean, nullable=False, default=False),
        sa.Column('seasonal_start_date', sa.DateTime),
        sa.Column('seasonal_end_date', sa.DateTime),
        sa.Column('prerequisite_achievements', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('hidden_until_unlocked', sa.Boolean, nullable=False, default=False),
        sa.Column('completion_count', sa.Integer, nullable=False, default=0),
        sa.Column('completion_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('average_completion_time_hours', sa.Float, nullable=False, default=0.0),
        sa.Column('icon_url', sa.String(500)),
        sa.Column('banner_url', sa.String(500)),
        sa.Column('celebration_message', sa.Text),
        sa.Column('social_share_text', sa.Text),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('display_order', sa.Integer, nullable=False, default=0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create user achievements table
    op.create_table('user_achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('achievement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('achievements_definition.id', ondelete='CASCADE'), nullable=False),
        sa.Column('progress_data', postgresql.JSONB, nullable=False, default={}),
        sa.Column('completion_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('is_completed', sa.Boolean, nullable=False, default=False),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('points_earned', sa.Integer, nullable=False, default=0),
        sa.Column('attempt_count', sa.Integer, nullable=False, default=0),
        sa.Column('first_attempt_date', sa.DateTime),
        sa.Column('last_progress_update', sa.DateTime),
        sa.Column('completion_time_hours', sa.Float),
        sa.Column('shared_socially', sa.Boolean, nullable=False, default=False),
        sa.Column('celebration_viewed', sa.Boolean, nullable=False, default=False),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create badges system table
    op.create_table('badges_system',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('badge_key', sa.String(100), nullable=False, unique=True),
        sa.Column('badge_name', sa.String(200), nullable=False),
        sa.Column('badge_description', sa.Text, nullable=False),
        sa.Column('badge_category', achievement_category_enum, nullable=False),
        sa.Column('rarity', badge_rarity_enum, nullable=False, default='common'),
        sa.Column('unlock_criteria', postgresql.JSONB, nullable=False),
        sa.Column('points_required', sa.Integer, nullable=False, default=0),
        sa.Column('achievement_requirement', sa.String(100)),
        sa.Column('badge_image_url', sa.String(500), nullable=False),
        sa.Column('badge_animation_url', sa.String(500)),
        sa.Column('display_order', sa.Integer, nullable=False, default=0),
        sa.Column('is_limited_edition', sa.Boolean, nullable=False, default=False),
        sa.Column('max_recipients', sa.Integer),
        sa.Column('current_recipients', sa.Integer, nullable=False, default=0),
        sa.Column('expiration_date', sa.DateTime),
        sa.Column('transferable', sa.Boolean, nullable=False, default=False),
        sa.Column('tradeable', sa.Boolean, nullable=False, default=False),
        sa.Column('market_value_points', sa.Integer),
        sa.Column('special_powers', postgresql.JSONB),
        sa.Column('collection_series', sa.String(100)),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create user badges table
    op.create_table('user_badges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('badge_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('badges_system.id', ondelete='CASCADE'), nullable=False),
        sa.Column('earned_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('is_displayed', sa.Boolean, nullable=False, default=True),
        sa.Column('display_order', sa.Integer, nullable=False, default=0),
        sa.Column('earning_context', postgresql.JSONB),
        sa.Column('achievement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('achievements_definition.id')),
        sa.Column('shared_socially', sa.Boolean, nullable=False, default=False),
        sa.Column('certification_hash', sa.String(256)),
        sa.Column('expires_at', sa.DateTime),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create leaderboards table
    op.create_table('leaderboards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('leaderboard_name', sa.String(200), nullable=False),
        sa.Column('leaderboard_type', leaderboard_type_enum, nullable=False),
        sa.Column('category_filter', achievement_category_enum),
        sa.Column('time_period', sa.String(20), nullable=False),
        sa.Column('ranking_criteria', postgresql.JSONB, nullable=False),
        sa.Column('participant_filters', postgresql.JSONB),
        sa.Column('geographical_scope', postgresql.ARRAY(sa.String(2)), default=[]),
        sa.Column('skill_level_filter', sa.String(20)),
        sa.Column('max_participants', sa.Integer, nullable=False, default=100),
        sa.Column('update_frequency_minutes', sa.Integer, nullable=False, default=60),
        sa.Column('last_updated', sa.DateTime),
        sa.Column('current_rankings', postgresql.JSONB, nullable=False, default=[]),
        sa.Column('historical_data', postgresql.JSONB, nullable=False, default={}),
        sa.Column('prizes_configuration', postgresql.JSONB),
        sa.Column('is_featured', sa.Boolean, nullable=False, default=False),
        sa.Column('featured_until', sa.DateTime),
        sa.Column('visibility', sa.String(20), nullable=False, default='public'),
        sa.Column('reset_schedule', sa.String(50)),
        sa.Column('next_reset_date', sa.DateTime),
        sa.Column('archived', sa.Boolean, nullable=False, default=False),
        sa.Column('display_order', sa.Integer, nullable=False, default=0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create rewards automation table
    op.create_table('rewards_automation',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('reward_name', sa.String(200), nullable=False),
        sa.Column('reward_type', reward_type_enum, nullable=False),
        sa.Column('trigger_conditions', postgresql.JSONB, nullable=False),
        sa.Column('reward_value', postgresql.JSONB, nullable=False),
        sa.Column('eligibility_criteria', postgresql.JSONB),
        sa.Column('frequency_limits', postgresql.JSONB),
        sa.Column('expiration_rules', postgresql.JSONB),
        sa.Column('personalization_rules', postgresql.JSONB),
        sa.Column('seasonal_modifiers', postgresql.JSONB),
        sa.Column('tier_multipliers', postgresql.JSONB),
        sa.Column('stack_with_other_rewards', sa.Boolean, nullable=False, default=True),
        sa.Column('requires_manual_approval', sa.Boolean, nullable=False, default=False),
        sa.Column('notification_template', postgresql.JSONB),
        sa.Column('claim_deadline_hours', sa.Integer, nullable=False, default=168),
        sa.Column('budget_allocation', sa.Numeric(15, 2)),
        sa.Column('budget_consumed', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('total_recipients', sa.Integer, nullable=False, default=0),
        sa.Column('success_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('user_satisfaction_score', sa.Float, nullable=False, default=0.0),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('start_date', sa.DateTime),
        sa.Column('end_date', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create user rewards table
    op.create_table('user_rewards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reward_automation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('rewards_automation.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reward_details', postgresql.JSONB, nullable=False),
        sa.Column('earned_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('claimed_at', sa.DateTime),
        sa.Column('expires_at', sa.DateTime),
        sa.Column('is_claimed', sa.Boolean, nullable=False, default=False),
        sa.Column('is_expired', sa.Boolean, nullable=False, default=False),
        sa.Column('claim_method', sa.String(50)),
        sa.Column('redemption_code', sa.String(100)),
        sa.Column('usage_instructions', sa.Text),
        sa.Column('redemption_url', sa.String(500)),
        sa.Column('transfer_history', postgresql.JSONB),
        sa.Column('user_feedback', sa.Text),
        sa.Column('user_rating', sa.Integer),
        sa.Column('notification_sent', sa.Boolean, nullable=False, default=False),
        sa.Column('reminder_sent', sa.Boolean, nullable=False, default=False),
        sa.Column('metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create engagement analytics table
    op.create_table('engagement_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('analytics_date', sa.Date, nullable=False),
        sa.Column('daily_login_streak', sa.Integer, nullable=False, default=0),
        sa.Column('session_duration_minutes', sa.Float, nullable=False, default=0.0),
        sa.Column('actions_completed', sa.Integer, nullable=False, default=0),
        sa.Column('content_interactions', sa.Integer, nullable=False, default=0),
        sa.Column('collaboration_activities', sa.Integer, nullable=False, default=0),
        sa.Column('achievements_earned', sa.Integer, nullable=False, default=0),
        sa.Column('badges_earned', sa.Integer, nullable=False, default=0),
        sa.Column('points_earned', sa.Integer, nullable=False, default=0),
        sa.Column('rewards_claimed', sa.Integer, nullable=False, default=0),
        sa.Column('leaderboard_positions', postgresql.JSONB),
        sa.Column('feature_usage', postgresql.JSONB),
        sa.Column('social_interactions', sa.Integer, nullable=False, default=0),
        sa.Column('content_created', sa.Integer, nullable=False, default=0),
        sa.Column('content_published', sa.Integer, nullable=False, default=0),
        sa.Column('revenue_generated', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('engagement_score', sa.Float, nullable=False, default=0.0),
        sa.Column('motivation_level', sa.Float, nullable=False, default=0.0),
        sa.Column('satisfaction_indicators', postgresql.JSONB),
        sa.Column('churn_risk_score', sa.Float, nullable=False, default=0.0),
        sa.Column('retention_probability', sa.Float, nullable=False, default=0.0),
        sa.Column('next_likely_actions', postgresql.JSONB),
        sa.Column('personalization_data', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create performance indexes
    
    # User Points System indexes
    op.create_index('idx_user_points_user_id', 'user_points_system', ['user_id'])
    op.create_index('idx_user_points_total', 'user_points_system', ['total_points'])
    op.create_index('idx_user_points_level', 'user_points_system', ['current_level'])
    op.create_index('idx_user_points_tier', 'user_points_system', ['tier_level'])
    op.create_index('idx_user_points_streak', 'user_points_system', ['streak_days'])
    op.create_index('idx_user_points_last_activity', 'user_points_system', ['last_activity_date'])
    op.create_index('idx_user_points_multiplier', 'user_points_system', ['point_multiplier'])
    op.create_index('idx_user_points_daily', 'user_points_system', ['daily_points_earned'])
    op.create_index('idx_user_points_weekly', 'user_points_system', ['weekly_points_earned'])
    op.create_index('idx_user_points_monthly', 'user_points_system', ['monthly_points_earned'])
    
    # Achievements Definition indexes
    op.create_index('idx_achievements_def_key', 'achievements_definition', ['achievement_key'])
    op.create_index('idx_achievements_def_category', 'achievements_definition', ['category'])
    op.create_index('idx_achievements_def_difficulty', 'achievements_definition', ['difficulty_level'])
    op.create_index('idx_achievements_def_repeatable', 'achievements_definition', ['is_repeatable'])
    op.create_index('idx_achievements_def_seasonal', 'achievements_definition', ['seasonal_achievement'])
    op.create_index('idx_achievements_def_active', 'achievements_definition', ['is_active'])
    op.create_index('idx_achievements_def_completion_rate', 'achievements_definition', ['completion_rate'])
    op.create_index('idx_achievements_def_display_order', 'achievements_definition', ['display_order'])
    
    # User Achievements indexes
    op.create_index('idx_user_achievements_user_id', 'user_achievements', ['user_id'])
    op.create_index('idx_user_achievements_achievement_id', 'user_achievements', ['achievement_id'])
    op.create_index('idx_user_achievements_completed', 'user_achievements', ['is_completed'])
    op.create_index('idx_user_achievements_completion_date', 'user_achievements', ['completed_at'])
    op.create_index('idx_user_achievements_progress', 'user_achievements', ['completion_percentage'])
    op.create_index('idx_user_achievements_points', 'user_achievements', ['points_earned'])
    op.create_index('idx_user_achievements_user_completed', 'user_achievements', ['user_id', 'is_completed'])
    
    # Badges System indexes
    op.create_index('idx_badges_system_key', 'badges_system', ['badge_key'])
    op.create_index('idx_badges_system_category', 'badges_system', ['badge_category'])
    op.create_index('idx_badges_system_rarity', 'badges_system', ['rarity'])
    op.create_index('idx_badges_system_limited', 'badges_system', ['is_limited_edition'])
    op.create_index('idx_badges_system_recipients', 'badges_system', ['current_recipients', 'max_recipients'])
    op.create_index('idx_badges_system_active', 'badges_system', ['is_active'])
    op.create_index('idx_badges_system_display_order', 'badges_system', ['display_order'])
    
    # User Badges indexes
    op.create_index('idx_user_badges_user_id', 'user_badges', ['user_id'])
    op.create_index('idx_user_badges_badge_id', 'user_badges', ['badge_id'])
    op.create_index('idx_user_badges_earned_at', 'user_badges', ['earned_at'])
    op.create_index('idx_user_badges_displayed', 'user_badges', ['is_displayed'])
    op.create_index('idx_user_badges_expires', 'user_badges', ['expires_at'])
    op.create_index('idx_user_badges_user_display', 'user_badges', ['user_id', 'is_displayed', 'display_order'])
    
    # Leaderboards indexes
    op.create_index('idx_leaderboards_name', 'leaderboards', ['leaderboard_name'])
    op.create_index('idx_leaderboards_type', 'leaderboards', ['leaderboard_type'])
    op.create_index('idx_leaderboards_category', 'leaderboards', ['category_filter'])
    op.create_index('idx_leaderboards_period', 'leaderboards', ['time_period'])
    op.create_index('idx_leaderboards_featured', 'leaderboards', ['is_featured'])
    op.create_index('idx_leaderboards_visibility', 'leaderboards', ['visibility'])
    op.create_index('idx_leaderboards_archived', 'leaderboards', ['archived'])
    op.create_index('idx_leaderboards_last_updated', 'leaderboards', ['last_updated'])
    op.create_index('idx_leaderboards_next_reset', 'leaderboards', ['next_reset_date'])
    
    # Rewards Automation indexes
    op.create_index('idx_rewards_automation_name', 'rewards_automation', ['reward_name'])
    op.create_index('idx_rewards_automation_type', 'rewards_automation', ['reward_type'])
    op.create_index('idx_rewards_automation_active', 'rewards_automation', ['is_active'])
    op.create_index('idx_rewards_automation_approval', 'rewards_automation', ['requires_manual_approval'])
    op.create_index('idx_rewards_automation_budget', 'rewards_automation', ['budget_allocation', 'budget_consumed'])
    op.create_index('idx_rewards_automation_success_rate', 'rewards_automation', ['success_rate'])
    op.create_index('idx_rewards_automation_period', 'rewards_automation', ['start_date', 'end_date'])
    
    # User Rewards indexes
    op.create_index('idx_user_rewards_user_id', 'user_rewards', ['user_id'])
    op.create_index('idx_user_rewards_automation_id', 'user_rewards', ['reward_automation_id'])
    op.create_index('idx_user_rewards_earned_at', 'user_rewards', ['earned_at'])
    op.create_index('idx_user_rewards_claimed', 'user_rewards', ['is_claimed'])
    op.create_index('idx_user_rewards_expired', 'user_rewards', ['is_expired'])
    op.create_index('idx_user_rewards_expires_at', 'user_rewards', ['expires_at'])
    op.create_index('idx_user_rewards_user_claimed', 'user_rewards', ['user_id', 'is_claimed'])
    
    # Engagement Analytics indexes
    op.create_index('idx_engagement_analytics_user_id', 'engagement_analytics', ['user_id'])
    op.create_index('idx_engagement_analytics_date', 'engagement_analytics', ['analytics_date'])
    op.create_index('idx_engagement_analytics_streak', 'engagement_analytics', ['daily_login_streak'])
    op.create_index('idx_engagement_analytics_session', 'engagement_analytics', ['session_duration_minutes'])
    op.create_index('idx_engagement_analytics_engagement', 'engagement_analytics', ['engagement_score'])
    op.create_index('idx_engagement_analytics_churn_risk', 'engagement_analytics', ['churn_risk_score'])
    op.create_index('idx_engagement_analytics_retention', 'engagement_analytics', ['retention_probability'])
    op.create_index('idx_engagement_analytics_user_date', 'engagement_analytics', ['user_id', 'analytics_date'])


def downgrade() -> None:
    """Downgrade database schema - Remove advanced gamification engine tables."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('engagement_analytics')
    op.drop_table('user_rewards')
    op.drop_table('rewards_automation')
    op.drop_table('leaderboards')
    op.drop_table('user_badges')
    op.drop_table('badges_system')
    op.drop_table('user_achievements')
    op.drop_table('achievements_definition')
    op.drop_table('user_points_system')
    
    # Drop ENUM types
    sa.Enum(name='leaderboard_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='reward_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='badge_rarity').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='achievement_category').drop(op.get_bind(), checkfirst=True)