"""Multi-platform distribution channels system

Revision ID: o1n2m3l4k5j6
Revises: n0m1l2k3j4i5
Create Date: 2025-09-05 07:10:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the multi-platform distribution channels system with
35+ platform integrations, automated publishing queues, cross-platform
analytics, and revenue attribution for maximum content reach.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'o1n2m3l4k5j6'
down_revision = 'n0m1l2k3j4i5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - Multi-platform distribution channels system."""
    
    # Create distribution platform enum
    distribution_platform_enum = sa.Enum(
        'youtube', 'tiktok', 'instagram', 'facebook', 'twitter', 'linkedin',
        'pinterest', 'snapchat', 'twitch', 'spotify', 'apple_music', 'soundcloud',
        'bandcamp', 'google_podcasts', 'apple_podcasts', 'anchor', 'medium',
        'substack', 'reddit', 'discord', 'clubhouse', 'telegram', 'whatsapp',
        'wechat', 'douyin', 'weibo', 'vk', 'ok', 'line', 'kakaotalk',
        'viber', 'signal', 'mastodon', 'threads', 'bluesky', 'vimeo',
        'dailymotion', 'rumble', 'odysee', 'peertube', 'dtube', 'bitchute',
        'brighteon', 'patreon', 'onlyfans', 'fanhouse', 'cameo', 'super',
        name='distribution_platform'
    )
    
    # Create publishing status enum
    publishing_status_enum = sa.Enum(
        'queued', 'preparing', 'uploading', 'processing', 'published',
        'failed', 'rejected', 'scheduled', 'draft', 'unlisted', 'private',
        'monetized', 'demonetized', 'age_restricted', 'geo_blocked',
        name='publishing_status'
    )
    
    # Create content format enum
    content_format_enum = sa.Enum(
        'video_vertical', 'video_horizontal', 'video_square', 'video_story',
        'audio_podcast', 'audio_music', 'audio_audiobook', 'audio_live',
        'image_post', 'image_story', 'image_carousel', 'image_reel',
        'text_post', 'text_article', 'text_thread', 'text_blog',
        'live_stream', 'live_audio', 'live_video', 'live_interactive',
        name='content_format'
    )
    
    # Create automation level enum
    automation_level_enum = sa.Enum(
        'manual', 'semi_automatic', 'fully_automatic', 'ai_optimized',
        'batch_processing', 'scheduled_automation', 'triggered_automation',
        name='automation_level'
    )
    
    # Create platform integrations table
    op.create_table('platform_integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', distribution_platform_enum, nullable=False),
        sa.Column('platform_display_name', sa.String(100), nullable=False),
        sa.Column('integration_status', sa.String(20), nullable=False, default='disconnected'),
        sa.Column('authentication_data', postgresql.JSONB),
        sa.Column('access_token_encrypted', sa.Text),
        sa.Column('refresh_token_encrypted', sa.Text),
        sa.Column('token_expires_at', sa.DateTime),
        sa.Column('platform_user_id', sa.String(200)),
        sa.Column('platform_username', sa.String(200)),
        sa.Column('platform_profile_url', sa.String(500)),
        sa.Column('api_rate_limits', postgresql.JSONB),
        sa.Column('supported_content_formats', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('upload_capabilities', postgresql.JSONB),
        sa.Column('monetization_settings', postgresql.JSONB),
        sa.Column('analytics_access', sa.Boolean, nullable=False, default=False),
        sa.Column('automation_permissions', postgresql.JSONB),
        sa.Column('content_policies', postgresql.JSONB),
        sa.Column('geographical_restrictions', postgresql.ARRAY(sa.String(2)), default=[]),
        sa.Column('age_restrictions', postgresql.JSONB),
        sa.Column('copyright_settings', postgresql.JSONB),
        sa.Column('custom_settings', postgresql.JSONB),
        sa.Column('integration_health_score', sa.Float, nullable=False, default=100.0),
        sa.Column('last_successful_sync', sa.DateTime),
        sa.Column('last_error_message', sa.Text),
        sa.Column('error_count', sa.Integer, nullable=False, default=0),
        sa.Column('auto_retry_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('notification_preferences', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create distribution queues table
    op.create_table('distribution_queues',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform_integration_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('platform_integrations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('distribution_name', sa.String(200), nullable=False),
        sa.Column('priority', sa.Integer, nullable=False, default=5),
        sa.Column('status', publishing_status_enum, nullable=False, default='queued'),
        sa.Column('automation_level', automation_level_enum, nullable=False, default='manual'),
        sa.Column('scheduled_publish_time', sa.DateTime),
        sa.Column('content_format', content_format_enum, nullable=False),
        sa.Column('platform_specific_settings', postgresql.JSONB),
        sa.Column('title_optimizations', postgresql.JSONB),
        sa.Column('description_optimizations', postgresql.JSONB),
        sa.Column('hashtag_sets', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('thumbnail_variants', postgresql.ARRAY(sa.String(500)), default=[]),
        sa.Column('content_adaptations', postgresql.JSONB),
        sa.Column('monetization_config', postgresql.JSONB),
        sa.Column('privacy_settings', postgresql.JSONB),
        sa.Column('audience_targeting', postgresql.JSONB),
        sa.Column('promotional_settings', postgresql.JSONB),
        sa.Column('cross_promotion_config', postgresql.JSONB),
        sa.Column('analytics_tracking', postgresql.JSONB),
        sa.Column('a_b_test_variants', postgresql.JSONB),
        sa.Column('retry_configuration', postgresql.JSONB),
        sa.Column('processing_logs', postgresql.JSONB, nullable=False, default=[]),
        sa.Column('platform_response_data', postgresql.JSONB),
        sa.Column('platform_content_id', sa.String(200)),
        sa.Column('platform_content_url', sa.String(1000)),
        sa.Column('upload_progress_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('estimated_processing_time', sa.Integer),
        sa.Column('actual_processing_time', sa.Integer),
        sa.Column('error_details', postgresql.JSONB),
        sa.Column('retry_count', sa.Integer, nullable=False, default=0),
        sa.Column('max_retries', sa.Integer, nullable=False, default=3),
        sa.Column('next_retry_at', sa.DateTime),
        sa.Column('started_at', sa.DateTime),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create cross-platform analytics table
    op.create_table('cross_platform_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('distribution_queue_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('distribution_queues.id', ondelete='CASCADE')),
        sa.Column('platform', distribution_platform_enum, nullable=False),
        sa.Column('analytics_date', sa.Date, nullable=False),
        sa.Column('views_impressions', sa.BigInteger, nullable=False, default=0),
        sa.Column('unique_viewers', sa.BigInteger, nullable=False, default=0),
        sa.Column('engagement_total', sa.BigInteger, nullable=False, default=0),
        sa.Column('likes', sa.BigInteger, nullable=False, default=0),
        sa.Column('dislikes', sa.BigInteger, nullable=False, default=0),
        sa.Column('comments', sa.BigInteger, nullable=False, default=0),
        sa.Column('shares', sa.BigInteger, nullable=False, default=0),
        sa.Column('saves_bookmarks', sa.BigInteger, nullable=False, default=0),
        sa.Column('click_throughs', sa.BigInteger, nullable=False, default=0),
        sa.Column('profile_visits', sa.BigInteger, nullable=False, default=0),
        sa.Column('follower_growth', sa.Integer, nullable=False, default=0),
        sa.Column('watch_time_total_minutes', sa.BigInteger, nullable=False, default=0),
        sa.Column('average_watch_time_seconds', sa.Float, nullable=False, default=0.0),
        sa.Column('completion_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('engagement_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('viral_coefficient', sa.Float, nullable=False, default=0.0),
        sa.Column('reach_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('trending_score', sa.Float, nullable=False, default=0.0),
        sa.Column('algorithm_favorability', sa.Float, nullable=False, default=0.0),
        sa.Column('audience_demographics', postgresql.JSONB),
        sa.Column('traffic_sources', postgresql.JSONB),
        sa.Column('geographical_breakdown', postgresql.JSONB),
        sa.Column('device_breakdown', postgresql.JSONB),
        sa.Column('peak_engagement_times', postgresql.JSONB),
        sa.Column('content_performance_insights', postgresql.JSONB),
        sa.Column('competitive_analysis', postgresql.JSONB),
        sa.Column('optimization_suggestions', postgresql.JSONB),
        sa.Column('sentiment_analysis', postgresql.JSONB),
        sa.Column('spam_detection_metrics', postgresql.JSONB),
        sa.Column('monetization_metrics', postgresql.JSONB),
        sa.Column('conversion_funnel_data', postgresql.JSONB),
        sa.Column('attribution_data', postgresql.JSONB),
        sa.Column('data_freshness', sa.DateTime),
        sa.Column('data_quality_score', sa.Float, nullable=False, default=100.0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create revenue attribution table
    op.create_table('revenue_attribution',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', distribution_platform_enum, nullable=False),
        sa.Column('revenue_date', sa.Date, nullable=False),
        sa.Column('revenue_type', sa.String(50), nullable=False),
        sa.Column('gross_revenue', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('platform_fee', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('processing_fee', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('tax_withheld', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('net_revenue', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        sa.Column('exchange_rate', sa.Float, nullable=False, default=1.0),
        sa.Column('revenue_usd', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('attribution_model', sa.String(50), nullable=False),
        sa.Column('attribution_weight', sa.Float, nullable=False, default=1.0),
        sa.Column('traffic_source', sa.String(100)),
        sa.Column('audience_segment', sa.String(100)),
        sa.Column('content_category', sa.String(100)),
        sa.Column('monetization_method', sa.String(100)),
        sa.Column('subscriber_tier', sa.String(50)),
        sa.Column('geographical_region', sa.String(100)),
        sa.Column('device_category', sa.String(50)),
        sa.Column('engagement_quality_score', sa.Float, nullable=False, default=0.0),
        sa.Column('lifetime_value_contribution', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('acquisition_cost_offset', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('cross_platform_synergy_bonus', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('collaboration_revenue_share', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('organic_vs_paid_split', postgresql.JSONB),
        sa.Column('performance_bonuses', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('penalty_deductions', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('settlement_status', sa.String(20), nullable=False, default='pending'),
        sa.Column('settlement_date', sa.DateTime),
        sa.Column('payment_reference', sa.String(100)),
        sa.Column('audit_trail', postgresql.JSONB),
        sa.Column('verification_status', sa.String(20), nullable=False, default='unverified'),
        sa.Column('discrepancy_notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create automated publishing campaigns table
    op.create_table('automated_publishing_campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('campaign_name', sa.String(200), nullable=False),
        sa.Column('campaign_description', sa.Text),
        sa.Column('target_platforms', postgresql.ARRAY(sa.String(50)), nullable=False),
        sa.Column('content_filters', postgresql.JSONB),
        sa.Column('publishing_schedule', postgresql.JSONB),
        sa.Column('automation_rules', postgresql.JSONB, nullable=False),
        sa.Column('content_adaptation_rules', postgresql.JSONB),
        sa.Column('optimization_preferences', postgresql.JSONB),
        sa.Column('approval_workflow', postgresql.JSONB),
        sa.Column('quality_gates', postgresql.JSONB),
        sa.Column('performance_thresholds', postgresql.JSONB),
        sa.Column('budget_allocation', sa.Numeric(15, 2)),
        sa.Column('roi_targets', postgresql.JSONB),
        sa.Column('risk_management_rules', postgresql.JSONB),
        sa.Column('compliance_checks', postgresql.JSONB),
        sa.Column('brand_safety_filters', postgresql.JSONB),
        sa.Column('audience_segmentation', postgresql.JSONB),
        sa.Column('cross_promotion_settings', postgresql.JSONB),
        sa.Column('analytics_preferences', postgresql.JSONB),
        sa.Column('notification_settings', postgresql.JSONB),
        sa.Column('escalation_procedures', postgresql.JSONB),
        sa.Column('machine_learning_config', postgresql.JSONB),
        sa.Column('campaign_status', sa.String(20), nullable=False, default='draft'),
        sa.Column('start_date', sa.DateTime),
        sa.Column('end_date', sa.DateTime),
        sa.Column('content_published_count', sa.Integer, nullable=False, default=0),
        sa.Column('total_reach', sa.BigInteger, nullable=False, default=0),
        sa.Column('total_engagement', sa.BigInteger, nullable=False, default=0),
        sa.Column('total_revenue_generated', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('campaign_roi', sa.Float, nullable=False, default=0.0),
        sa.Column('success_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('automation_efficiency', sa.Float, nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create platform performance comparison table
    op.create_table('platform_performance_comparison',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('comparison_date', sa.Date, nullable=False),
        sa.Column('content_category', sa.String(100)),
        sa.Column('time_period_days', sa.Integer, nullable=False, default=30),
        sa.Column('platform_metrics', postgresql.JSONB, nullable=False),
        sa.Column('cross_platform_insights', postgresql.JSONB),
        sa.Column('audience_overlap_analysis', postgresql.JSONB),
        sa.Column('content_format_performance', postgresql.JSONB),
        sa.Column('optimal_posting_times', postgresql.JSONB),
        sa.Column('engagement_quality_comparison', postgresql.JSONB),
        sa.Column('monetization_effectiveness', postgresql.JSONB),
        sa.Column('growth_rate_analysis', postgresql.JSONB),
        sa.Column('algorithm_favorability_scores', postgresql.JSONB),
        sa.Column('competitive_positioning', postgresql.JSONB),
        sa.Column('resource_allocation_recommendations', postgresql.JSONB),
        sa.Column('priority_platform_ranking', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('underperforming_platforms', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('emerging_opportunities', postgresql.JSONB),
        sa.Column('saturation_analysis', postgresql.JSONB),
        sa.Column('synergy_opportunities', postgresql.JSONB),
        sa.Column('optimization_suggestions', postgresql.JSONB),
        sa.Column('risk_assessment', postgresql.JSONB),
        sa.Column('trend_predictions', postgresql.JSONB),
        sa.Column('action_items', postgresql.JSONB),
        sa.Column('confidence_score', sa.Float, nullable=False, default=0.0),
        sa.Column('data_quality_assessment', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create performance indexes
    
    # Platform Integrations indexes
    op.create_index('idx_platform_integrations_user_id', 'platform_integrations', ['user_id'])
    op.create_index('idx_platform_integrations_platform', 'platform_integrations', ['platform'])
    op.create_index('idx_platform_integrations_status', 'platform_integrations', ['integration_status'])
    op.create_index('idx_platform_integrations_health', 'platform_integrations', ['integration_health_score'])
    op.create_index('idx_platform_integrations_last_sync', 'platform_integrations', ['last_successful_sync'])
    op.create_index('idx_platform_integrations_error_count', 'platform_integrations', ['error_count'])
    op.create_index('idx_platform_integrations_token_expires', 'platform_integrations', ['token_expires_at'])
    op.create_index('idx_platform_integrations_user_platform', 'platform_integrations', ['user_id', 'platform'])
    
    # Distribution Queues indexes
    op.create_index('idx_distribution_queues_user_id', 'distribution_queues', ['user_id'])
    op.create_index('idx_distribution_queues_content_id', 'distribution_queues', ['content_id'])
    op.create_index('idx_distribution_queues_platform_id', 'distribution_queues', ['platform_integration_id'])
    op.create_index('idx_distribution_queues_status', 'distribution_queues', ['status'])
    op.create_index('idx_distribution_queues_priority', 'distribution_queues', ['priority'])
    op.create_index('idx_distribution_queues_automation', 'distribution_queues', ['automation_level'])
    op.create_index('idx_distribution_queues_scheduled', 'distribution_queues', ['scheduled_publish_time'])
    op.create_index('idx_distribution_queues_format', 'distribution_queues', ['content_format'])
    op.create_index('idx_distribution_queues_progress', 'distribution_queues', ['upload_progress_percentage'])
    op.create_index('idx_distribution_queues_retry', 'distribution_queues', ['retry_count', 'max_retries'])
    op.create_index('idx_distribution_queues_next_retry', 'distribution_queues', ['next_retry_at'])
    
    # Cross-Platform Analytics indexes
    op.create_index('idx_cross_platform_analytics_content_id', 'cross_platform_analytics', ['content_id'])
    op.create_index('idx_cross_platform_analytics_queue_id', 'cross_platform_analytics', ['distribution_queue_id'])
    op.create_index('idx_cross_platform_analytics_platform', 'cross_platform_analytics', ['platform'])
    op.create_index('idx_cross_platform_analytics_date', 'cross_platform_analytics', ['analytics_date'])
    op.create_index('idx_cross_platform_analytics_views', 'cross_platform_analytics', ['views_impressions'])
    op.create_index('idx_cross_platform_analytics_engagement', 'cross_platform_analytics', ['engagement_total'])
    op.create_index('idx_cross_platform_analytics_engagement_rate', 'cross_platform_analytics', ['engagement_rate'])
    op.create_index('idx_cross_platform_analytics_viral', 'cross_platform_analytics', ['viral_coefficient'])
    op.create_index('idx_cross_platform_analytics_trending', 'cross_platform_analytics', ['trending_score'])
    op.create_index('idx_cross_platform_analytics_algorithm', 'cross_platform_analytics', ['algorithm_favorability'])
    op.create_index('idx_cross_platform_analytics_quality', 'cross_platform_analytics', ['data_quality_score'])
    op.create_index('idx_cross_platform_analytics_content_platform', 'cross_platform_analytics', ['content_id', 'platform'])
    
    # Revenue Attribution indexes
    op.create_index('idx_revenue_attribution_user_id', 'revenue_attribution', ['user_id'])
    op.create_index('idx_revenue_attribution_content_id', 'revenue_attribution', ['content_id'])
    op.create_index('idx_revenue_attribution_platform', 'revenue_attribution', ['platform'])
    op.create_index('idx_revenue_attribution_date', 'revenue_attribution', ['revenue_date'])
    op.create_index('idx_revenue_attribution_type', 'revenue_attribution', ['revenue_type'])
    op.create_index('idx_revenue_attribution_gross', 'revenue_attribution', ['gross_revenue'])
    op.create_index('idx_revenue_attribution_net', 'revenue_attribution', ['net_revenue'])
    op.create_index('idx_revenue_attribution_usd', 'revenue_attribution', ['revenue_usd'])
    op.create_index('idx_revenue_attribution_settlement', 'revenue_attribution', ['settlement_status'])
    op.create_index('idx_revenue_attribution_verification', 'revenue_attribution', ['verification_status'])
    op.create_index('idx_revenue_attribution_user_platform', 'revenue_attribution', ['user_id', 'platform'])
    
    # Automated Publishing Campaigns indexes
    op.create_index('idx_publishing_campaigns_user_id', 'automated_publishing_campaigns', ['user_id'])
    op.create_index('idx_publishing_campaigns_name', 'automated_publishing_campaigns', ['campaign_name'])
    op.create_index('idx_publishing_campaigns_platforms', 'automated_publishing_campaigns', ['target_platforms'], postgresql_using='gin')
    op.create_index('idx_publishing_campaigns_status', 'automated_publishing_campaigns', ['campaign_status'])
    op.create_index('idx_publishing_campaigns_start_date', 'automated_publishing_campaigns', ['start_date'])
    op.create_index('idx_publishing_campaigns_end_date', 'automated_publishing_campaigns', ['end_date'])
    op.create_index('idx_publishing_campaigns_content_count', 'automated_publishing_campaigns', ['content_published_count'])
    op.create_index('idx_publishing_campaigns_roi', 'automated_publishing_campaigns', ['campaign_roi'])
    op.create_index('idx_publishing_campaigns_success_rate', 'automated_publishing_campaigns', ['success_rate'])
    op.create_index('idx_publishing_campaigns_efficiency', 'automated_publishing_campaigns', ['automation_efficiency'])
    
    # Platform Performance Comparison indexes
    op.create_index('idx_platform_comparison_user_id', 'platform_performance_comparison', ['user_id'])
    op.create_index('idx_platform_comparison_date', 'platform_performance_comparison', ['comparison_date'])
    op.create_index('idx_platform_comparison_category', 'platform_performance_comparison', ['content_category'])
    op.create_index('idx_platform_comparison_period', 'platform_performance_comparison', ['time_period_days'])
    op.create_index('idx_platform_comparison_confidence', 'platform_performance_comparison', ['confidence_score'])
    op.create_index('idx_platform_comparison_priority_platforms', 'platform_performance_comparison', ['priority_platform_ranking'], postgresql_using='gin')
    op.create_index('idx_platform_comparison_underperforming', 'platform_performance_comparison', ['underperforming_platforms'], postgresql_using='gin')
    op.create_index('idx_platform_comparison_user_date', 'platform_performance_comparison', ['user_id', 'comparison_date'])


def downgrade() -> None:
    """Downgrade database schema - Remove multi-platform distribution channels tables."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('platform_performance_comparison')
    op.drop_table('automated_publishing_campaigns')
    op.drop_table('revenue_attribution')
    op.drop_table('cross_platform_analytics')
    op.drop_table('distribution_queues')
    op.drop_table('platform_integrations')
    
    # Drop ENUM types
    sa.Enum(name='automation_level').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='content_format').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='publishing_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='distribution_platform').drop(op.get_bind(), checkfirst=True)