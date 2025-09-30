"""SEO optimization engine for multi-platform content

Revision ID: n0m1l2k3j4i5
Revises: m9l0k1j2i3h4
Create Date: 2025-09-05 07:05:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the SEO optimization engine for automatic multi-platform
SEO with AI keywords optimization, content ranking optimization, and advanced
analytics for maximum content discoverability and reach.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'n0m1l2k3j4i5'
down_revision = 'm9l0k1j2i3h4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - SEO optimization engine system."""
    
    # Create SEO strategy enum
    seo_strategy_enum = sa.Enum(
        'viral_growth', 'niche_authority', 'brand_awareness', 'conversion_focused',
        'local_seo', 'international_seo', 'long_tail_keywords', 'trending_topics',
        'evergreen_content', 'seasonal_optimization', 'competitor_analysis',
        name='seo_strategy'
    )
    
    # Create content optimization status enum
    optimization_status_enum = sa.Enum(
        'pending', 'analyzing', 'optimizing', 'optimized', 'published',
        'monitoring', 'needs_update', 'failed', 'manual_review_required',
        name='optimization_status'
    )
    
    # Create ranking factor enum
    ranking_factor_enum = sa.Enum(
        'title_optimization', 'description_optimization', 'keyword_density',
        'hashtag_strategy', 'thumbnail_optimization', 'timing_optimization',
        'engagement_rate', 'watch_time', 'click_through_rate', 'social_signals',
        'backlink_quality', 'content_freshness', 'mobile_optimization',
        'loading_speed', 'user_experience', 'semantic_relevance',
        name='ranking_factor'
    )
    
    # Create platform type enum
    platform_type_enum = sa.Enum(
        'youtube', 'tiktok', 'instagram', 'facebook', 'twitter', 'linkedin',
        'pinterest', 'snapchat', 'twitch', 'spotify', 'soundcloud', 'apple_music',
        'google_podcasts', 'medium', 'substack', 'reddit', 'discord', 'clubhouse',
        'telegram', 'whatsapp', 'wechat', 'douyin', 'weibo', 'vk', 'ok',
        'line', 'kakaotalk', 'viber', 'signal', 'mastodon', 'threads',
        'bluesky', 'vimeo', 'dailymotion', 'rumble', 'odysee',
        name='platform_type'
    )
    
    # Create SEO profiles table
    op.create_table('seo_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE')),
        sa.Column('seo_strategy', seo_strategy_enum, nullable=False, default='viral_growth'),
        sa.Column('target_platforms', postgresql.ARRAY(sa.String(50)), nullable=False, default=[]),
        sa.Column('target_keywords', postgresql.ARRAY(sa.String(100)), nullable=False, default=[]),
        sa.Column('target_hashtags', postgresql.ARRAY(sa.String(100)), nullable=False, default=[]),
        sa.Column('target_audience_demographics', postgresql.JSONB),
        sa.Column('geographical_targeting', postgresql.ARRAY(sa.String(2)), default=[]),
        sa.Column('language_targeting', postgresql.ARRAY(sa.String(10)), default=[]),
        sa.Column('content_category_focus', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('competitor_analysis', postgresql.JSONB),
        sa.Column('seasonal_patterns', postgresql.JSONB),
        sa.Column('optimization_goals', postgresql.JSONB),
        sa.Column('performance_benchmarks', postgresql.JSONB),
        sa.Column('content_calendar_integration', sa.Boolean, nullable=False, default=True),
        sa.Column('automated_optimization', sa.Boolean, nullable=False, default=True),
        sa.Column('ai_suggestion_acceptance_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('custom_rules', postgresql.JSONB),
        sa.Column('budget_allocation', sa.Numeric(10, 2)),
        sa.Column('roi_targets', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create AI keyword optimization table
    op.create_table('ai_keyword_optimization',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('seo_profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('seo_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', platform_type_enum, nullable=False),
        sa.Column('original_keywords', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('optimized_keywords', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('keyword_research_data', postgresql.JSONB),
        sa.Column('search_volume_data', postgresql.JSONB),
        sa.Column('competition_analysis', postgresql.JSONB),
        sa.Column('keyword_difficulty_scores', postgresql.JSONB),
        sa.Column('long_tail_suggestions', postgresql.ARRAY(sa.String(200)), default=[]),
        sa.Column('semantic_keywords', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('trending_keywords', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('seasonal_keywords', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('geo_specific_keywords', postgresql.JSONB),
        sa.Column('language_variations', postgresql.JSONB),
        sa.Column('ai_confidence_score', sa.Float, nullable=False, default=0.0),
        sa.Column('expected_performance_lift', sa.Float, nullable=False, default=0.0),
        sa.Column('optimization_reasoning', sa.Text),
        sa.Column('implementation_suggestions', postgresql.JSONB),
        sa.Column('monitoring_metrics', postgresql.JSONB),
        sa.Column('a_b_test_variants', postgresql.JSONB),
        sa.Column('performance_prediction', postgresql.JSONB),
        sa.Column('last_optimization_date', sa.DateTime),
        sa.Column('next_optimization_due', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create content ranking optimization table
    op.create_table('content_ranking_optimization',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', platform_type_enum, nullable=False),
        sa.Column('current_ranking_position', sa.Integer),
        sa.Column('target_ranking_position', sa.Integer),
        sa.Column('ranking_factors_analysis', postgresql.JSONB),
        sa.Column('optimization_recommendations', postgresql.JSONB),
        sa.Column('title_optimization', postgresql.JSONB),
        sa.Column('description_optimization', postgresql.JSONB),
        sa.Column('thumbnail_optimization', postgresql.JSONB),
        sa.Column('hashtag_optimization', postgresql.JSONB),
        sa.Column('timing_optimization', postgresql.JSONB),
        sa.Column('engagement_optimization', postgresql.JSONB),
        sa.Column('cross_platform_promotion', postgresql.JSONB),
        sa.Column('influencer_collaboration_suggestions', postgresql.JSONB),
        sa.Column('content_distribution_strategy', postgresql.JSONB),
        sa.Column('viral_potential_score', sa.Float, nullable=False, default=0.0),
        sa.Column('trending_probability', sa.Float, nullable=False, default=0.0),
        sa.Column('algorithm_compatibility_score', sa.Float, nullable=False, default=0.0),
        sa.Column('audience_alignment_score', sa.Float, nullable=False, default=0.0),
        sa.Column('competitive_advantage_score', sa.Float, nullable=False, default=0.0),
        sa.Column('optimization_status', optimization_status_enum, nullable=False, default='pending'),
        sa.Column('implementation_timeline', postgresql.JSONB),
        sa.Column('resource_requirements', postgresql.JSONB),
        sa.Column('success_probability', sa.Float, nullable=False, default=0.0),
        sa.Column('roi_projection', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create platform SEO analytics table
    op.create_table('platform_seo_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', platform_type_enum, nullable=False),
        sa.Column('analytics_date', sa.Date, nullable=False),
        sa.Column('impressions', sa.BigInteger, nullable=False, default=0),
        sa.Column('reach', sa.BigInteger, nullable=False, default=0),
        sa.Column('views', sa.BigInteger, nullable=False, default=0),
        sa.Column('unique_viewers', sa.BigInteger, nullable=False, default=0),
        sa.Column('click_through_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('engagement_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('average_watch_time', sa.Float, nullable=False, default=0.0),
        sa.Column('watch_time_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('shares', sa.Integer, nullable=False, default=0),
        sa.Column('comments', sa.Integer, nullable=False, default=0),
        sa.Column('likes', sa.Integer, nullable=False, default=0),
        sa.Column('saves_bookmarks', sa.Integer, nullable=False, default=0),
        sa.Column('profile_visits', sa.Integer, nullable=False, default=0),
        sa.Column('follower_growth', sa.Integer, nullable=False, default=0),
        sa.Column('search_ranking_positions', postgresql.JSONB),
        sa.Column('keyword_performance', postgresql.JSONB),
        sa.Column('hashtag_performance', postgresql.JSONB),
        sa.Column('audience_demographics', postgresql.JSONB),
        sa.Column('traffic_sources', postgresql.JSONB),
        sa.Column('geographical_data', postgresql.JSONB),
        sa.Column('device_breakdown', postgresql.JSONB),
        sa.Column('peak_engagement_times', postgresql.JSONB),
        sa.Column('competitor_comparison', postgresql.JSONB),
        sa.Column('algorithm_score', sa.Float, nullable=False, default=0.0),
        sa.Column('virality_metrics', postgresql.JSONB),
        sa.Column('sentiment_analysis', postgresql.JSONB),
        sa.Column('conversion_metrics', postgresql.JSONB),
        sa.Column('revenue_attribution', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create automated SEO campaigns table
    op.create_table('automated_seo_campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('campaign_name', sa.String(200), nullable=False),
        sa.Column('campaign_description', sa.Text),
        sa.Column('target_platforms', postgresql.ARRAY(sa.String(50)), nullable=False),
        sa.Column('campaign_objectives', postgresql.JSONB, nullable=False),
        sa.Column('content_categories', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('automation_rules', postgresql.JSONB, nullable=False),
        sa.Column('optimization_schedule', postgresql.JSONB),
        sa.Column('budget_allocation', sa.Numeric(15, 2)),
        sa.Column('performance_targets', postgresql.JSONB),
        sa.Column('content_guidelines', postgresql.JSONB),
        sa.Column('brand_safety_rules', postgresql.JSONB),
        sa.Column('compliance_requirements', postgresql.JSONB),
        sa.Column('a_b_testing_configuration', postgresql.JSONB),
        sa.Column('reporting_preferences', postgresql.JSONB),
        sa.Column('escalation_rules', postgresql.JSONB),
        sa.Column('approval_workflows', postgresql.JSONB),
        sa.Column('integration_settings', postgresql.JSONB),
        sa.Column('machine_learning_preferences', postgresql.JSONB),
        sa.Column('campaign_status', sa.String(20), nullable=False, default='draft'),
        sa.Column('start_date', sa.DateTime),
        sa.Column('end_date', sa.DateTime),
        sa.Column('total_content_optimized', sa.Integer, nullable=False, default=0),
        sa.Column('total_performance_lift', sa.Float, nullable=False, default=0.0),
        sa.Column('total_revenue_attributed', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('roi_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('success_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create SEO performance tracking table
    op.create_table('seo_performance_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('automated_seo_campaigns.id', ondelete='CASCADE')),
        sa.Column('tracking_date', sa.Date, nullable=False),
        sa.Column('optimization_implemented', postgresql.JSONB),
        sa.Column('baseline_metrics', postgresql.JSONB),
        sa.Column('current_metrics', postgresql.JSONB),
        sa.Column('performance_delta', postgresql.JSONB),
        sa.Column('percentage_improvement', sa.Float, nullable=False, default=0.0),
        sa.Column('ranking_improvements', postgresql.JSONB),
        sa.Column('traffic_growth', postgresql.JSONB),
        sa.Column('engagement_improvements', postgresql.JSONB),
        sa.Column('conversion_improvements', postgresql.JSONB),
        sa.Column('revenue_impact', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('cost_per_acquisition', sa.Numeric(10, 2)),
        sa.Column('return_on_investment', sa.Float, nullable=False, default=0.0),
        sa.Column('attribution_model', sa.String(50)),
        sa.Column('confidence_interval', sa.Float, nullable=False, default=0.0),
        sa.Column('statistical_significance', sa.Boolean, nullable=False, default=False),
        sa.Column('external_factors', postgresql.JSONB),
        sa.Column('seasonality_adjustments', postgresql.JSONB),
        sa.Column('competitive_impact', postgresql.JSONB),
        sa.Column('algorithm_changes_impact', postgresql.JSONB),
        sa.Column('optimization_insights', postgresql.JSONB),
        sa.Column('recommendations_for_improvement', postgresql.JSONB),
        sa.Column('next_optimization_suggestions', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create trending analysis table
    op.create_table('trending_analysis',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('platform', platform_type_enum, nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('trending_topics', postgresql.ARRAY(sa.String(200)), default=[]),
        sa.Column('trending_hashtags', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('trending_keywords', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('viral_content_patterns', postgresql.JSONB),
        sa.Column('algorithm_preferences', postgresql.JSONB),
        sa.Column('audience_behavior_insights', postgresql.JSONB),
        sa.Column('seasonal_trends', postgresql.JSONB),
        sa.Column('emerging_creators', postgresql.JSONB),
        sa.Column('content_format_trends', postgresql.JSONB),
        sa.Column('engagement_pattern_shifts', postgresql.JSONB),
        sa.Column('monetization_opportunities', postgresql.JSONB),
        sa.Column('risk_factors', postgresql.JSONB),
        sa.Column('prediction_accuracy', sa.Float, nullable=False, default=0.0),
        sa.Column('data_sources', postgresql.JSONB),
        sa.Column('analysis_methodology', postgresql.JSONB),
        sa.Column('confidence_metrics', postgresql.JSONB),
        sa.Column('actionable_insights', postgresql.JSONB),
        sa.Column('implementation_timeline', postgresql.JSONB),
        sa.Column('competitive_intelligence', postgresql.JSONB),
        sa.Column('geographic_variations', postgresql.JSONB),
        sa.Column('demographic_insights', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create performance indexes
    
    # SEO Profiles indexes
    op.create_index('idx_seo_profiles_user_id', 'seo_profiles', ['user_id'])
    op.create_index('idx_seo_profiles_content_id', 'seo_profiles', ['content_id'])
    op.create_index('idx_seo_profiles_strategy', 'seo_profiles', ['seo_strategy'])
    op.create_index('idx_seo_profiles_platforms', 'seo_profiles', ['target_platforms'], postgresql_using='gin')
    op.create_index('idx_seo_profiles_automated', 'seo_profiles', ['automated_optimization'])
    op.create_index('idx_seo_profiles_acceptance_rate', 'seo_profiles', ['ai_suggestion_acceptance_rate'])
    op.create_index('idx_seo_profiles_geographical', 'seo_profiles', ['geographical_targeting'], postgresql_using='gin')
    op.create_index('idx_seo_profiles_language', 'seo_profiles', ['language_targeting'], postgresql_using='gin')
    
    # AI Keyword Optimization indexes
    op.create_index('idx_keyword_optimization_content_id', 'ai_keyword_optimization', ['content_id'])
    op.create_index('idx_keyword_optimization_profile_id', 'ai_keyword_optimization', ['seo_profile_id'])
    op.create_index('idx_keyword_optimization_platform', 'ai_keyword_optimization', ['platform'])
    op.create_index('idx_keyword_optimization_confidence', 'ai_keyword_optimization', ['ai_confidence_score'])
    op.create_index('idx_keyword_optimization_performance_lift', 'ai_keyword_optimization', ['expected_performance_lift'])
    op.create_index('idx_keyword_optimization_last_date', 'ai_keyword_optimization', ['last_optimization_date'])
    op.create_index('idx_keyword_optimization_next_due', 'ai_keyword_optimization', ['next_optimization_due'])
    op.create_index('idx_keyword_optimization_keywords', 'ai_keyword_optimization', ['optimized_keywords'], postgresql_using='gin')
    
    # Content Ranking Optimization indexes
    op.create_index('idx_ranking_optimization_content_id', 'content_ranking_optimization', ['content_id'])
    op.create_index('idx_ranking_optimization_platform', 'content_ranking_optimization', ['platform'])
    op.create_index('idx_ranking_optimization_current_rank', 'content_ranking_optimization', ['current_ranking_position'])
    op.create_index('idx_ranking_optimization_target_rank', 'content_ranking_optimization', ['target_ranking_position'])
    op.create_index('idx_ranking_optimization_viral_score', 'content_ranking_optimization', ['viral_potential_score'])
    op.create_index('idx_ranking_optimization_trending_prob', 'content_ranking_optimization', ['trending_probability'])
    op.create_index('idx_ranking_optimization_algorithm_score', 'content_ranking_optimization', ['algorithm_compatibility_score'])
    op.create_index('idx_ranking_optimization_status', 'content_ranking_optimization', ['optimization_status'])
    op.create_index('idx_ranking_optimization_success_prob', 'content_ranking_optimization', ['success_probability'])
    
    # Platform SEO Analytics indexes
    op.create_index('idx_platform_analytics_content_id', 'platform_seo_analytics', ['content_id'])
    op.create_index('idx_platform_analytics_platform', 'platform_seo_analytics', ['platform'])
    op.create_index('idx_platform_analytics_date', 'platform_seo_analytics', ['analytics_date'])
    op.create_index('idx_platform_analytics_impressions', 'platform_seo_analytics', ['impressions'])
    op.create_index('idx_platform_analytics_reach', 'platform_seo_analytics', ['reach'])
    op.create_index('idx_platform_analytics_ctr', 'platform_seo_analytics', ['click_through_rate'])
    op.create_index('idx_platform_analytics_engagement', 'platform_seo_analytics', ['engagement_rate'])
    op.create_index('idx_platform_analytics_algorithm_score', 'platform_seo_analytics', ['algorithm_score'])
    op.create_index('idx_platform_analytics_revenue', 'platform_seo_analytics', ['revenue_attribution'])
    op.create_index('idx_platform_analytics_content_platform', 'platform_seo_analytics', ['content_id', 'platform'])
    
    # Automated SEO Campaigns indexes
    op.create_index('idx_seo_campaigns_user_id', 'automated_seo_campaigns', ['user_id'])
    op.create_index('idx_seo_campaigns_name', 'automated_seo_campaigns', ['campaign_name'])
    op.create_index('idx_seo_campaigns_platforms', 'automated_seo_campaigns', ['target_platforms'], postgresql_using='gin')
    op.create_index('idx_seo_campaigns_status', 'automated_seo_campaigns', ['campaign_status'])
    op.create_index('idx_seo_campaigns_start_date', 'automated_seo_campaigns', ['start_date'])
    op.create_index('idx_seo_campaigns_end_date', 'automated_seo_campaigns', ['end_date'])
    op.create_index('idx_seo_campaigns_performance_lift', 'automated_seo_campaigns', ['total_performance_lift'])
    op.create_index('idx_seo_campaigns_roi', 'automated_seo_campaigns', ['roi_percentage'])
    op.create_index('idx_seo_campaigns_success_rate', 'automated_seo_campaigns', ['success_rate'])
    
    # SEO Performance Tracking indexes
    op.create_index('idx_seo_performance_content_id', 'seo_performance_tracking', ['content_id'])
    op.create_index('idx_seo_performance_campaign_id', 'seo_performance_tracking', ['campaign_id'])
    op.create_index('idx_seo_performance_date', 'seo_performance_tracking', ['tracking_date'])
    op.create_index('idx_seo_performance_improvement', 'seo_performance_tracking', ['percentage_improvement'])
    op.create_index('idx_seo_performance_revenue', 'seo_performance_tracking', ['revenue_impact'])
    op.create_index('idx_seo_performance_roi', 'seo_performance_tracking', ['return_on_investment'])
    op.create_index('idx_seo_performance_significance', 'seo_performance_tracking', ['statistical_significance'])
    op.create_index('idx_seo_performance_confidence', 'seo_performance_tracking', ['confidence_interval'])
    
    # Trending Analysis indexes
    op.create_index('idx_trending_analysis_platform', 'trending_analysis', ['platform'])
    op.create_index('idx_trending_analysis_date', 'trending_analysis', ['analysis_date'])
    op.create_index('idx_trending_analysis_topics', 'trending_analysis', ['trending_topics'], postgresql_using='gin')
    op.create_index('idx_trending_analysis_hashtags', 'trending_analysis', ['trending_hashtags'], postgresql_using='gin')
    op.create_index('idx_trending_analysis_keywords', 'trending_analysis', ['trending_keywords'], postgresql_using='gin')
    op.create_index('idx_trending_analysis_accuracy', 'trending_analysis', ['prediction_accuracy'])
    op.create_index('idx_trending_analysis_platform_date', 'trending_analysis', ['platform', 'analysis_date'])


def downgrade() -> None:
    """Downgrade database schema - Remove SEO optimization engine tables."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('trending_analysis')
    op.drop_table('seo_performance_tracking')
    op.drop_table('automated_seo_campaigns')
    op.drop_table('platform_seo_analytics')
    op.drop_table('content_ranking_optimization')
    op.drop_table('ai_keyword_optimization')
    op.drop_table('seo_profiles')
    
    # Drop ENUM types
    sa.Enum(name='platform_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='ranking_factor').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='optimization_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='seo_strategy').drop(op.get_bind(), checkfirst=True)