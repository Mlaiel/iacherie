"""AI-powered collaboration matching system

Revision ID: k7j8i9h0g1f2
Revises: j6i7h8g9f0e1
Create Date: 2025-09-05 06:50:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the AI-powered collaboration matching system with
compatibility scoring, project recommendations, and collaboration analytics
for connecting creators across different formats and specializations.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'k7j8i9h0g1f2'
down_revision = 'j6i7h8g9f0e1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - AI-powered collaboration matching system."""
    
    # Create collaboration type enum
    collaboration_type_enum = sa.Enum(
        'musical_project', 'podcast_series', 'video_production', 'content_creation',
        'marketing_campaign', 'brand_partnership', 'educational_content', 
        'live_performance', 'remix_collaboration', 'cover_version', 'duet',
        'interview_series', 'documentary', 'short_film', 'web_series',
        'music_video', 'commercial', 'social_media_campaign', 'influencer_partnership',
        name='collaboration_type'
    )
    
    # Create matching algorithm enum
    matching_algorithm_enum = sa.Enum(
        'cosine_similarity', 'euclidean_distance', 'collaborative_filtering',
        'content_based_filtering', 'neural_network', 'decision_tree',
        'random_forest', 'gradient_boosting', 'svm_matching', 'kmeans_clustering',
        'deep_learning', 'transformer_model', 'graph_neural_network',
        name='matching_algorithm'
    )
    
    # Create compatibility level enum
    compatibility_level_enum = sa.Enum(
        'poor', 'below_average', 'average', 'good', 'excellent', 'perfect',
        name='compatibility_level'
    )
    
    # Create collaboration status enum
    collaboration_status_enum = sa.Enum(
        'proposed', 'pending_approval', 'accepted', 'in_progress', 'completed',
        'cancelled', 'rejected', 'on_hold', 'renegotiating', 'disputed',
        name='collaboration_status'
    )
    
    # Create creator compatibility profiles table
    op.create_table('creator_compatibility_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('collaboration_preferences', postgresql.JSONB, nullable=False, default={}),
        sa.Column('preferred_collaboration_types', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('preferred_project_duration', sa.String(50)),
        sa.Column('availability_schedule', postgresql.JSONB),
        sa.Column('timezone', sa.String(50)),
        sa.Column('communication_style', sa.String(50)),
        sa.Column('work_style_preferences', postgresql.JSONB),
        sa.Column('creative_vision_keywords', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('genre_preferences', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('skill_level_preference', sa.String(20)),
        sa.Column('budget_range_min', sa.Numeric(10, 2)),
        sa.Column('budget_range_max', sa.Numeric(10, 2)),
        sa.Column('revenue_sharing_preference', sa.Float),
        sa.Column('geographical_preference', postgresql.ARRAY(sa.String(2)), default=[]),
        sa.Column('language_preferences', postgresql.ARRAY(sa.String(10)), default=[]),
        sa.Column('collaboration_history_rating', sa.Float, nullable=False, default=0.0),
        sa.Column('reliability_score', sa.Float, nullable=False, default=0.0),
        sa.Column('creativity_score', sa.Float, nullable=False, default=0.0),
        sa.Column('technical_skill_score', sa.Float, nullable=False, default=0.0),
        sa.Column('communication_score', sa.Float, nullable=False, default=0.0),
        sa.Column('profile_completeness', sa.Float, nullable=False, default=0.0),
        sa.Column('ai_personality_vector', postgresql.ARRAY(sa.Float), default=[]),
        sa.Column('last_updated', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create AI matching scores table
    op.create_table('ai_matching_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_a_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('creator_b_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('overall_compatibility_score', sa.Float, nullable=False),
        sa.Column('compatibility_level', compatibility_level_enum, nullable=False),
        sa.Column('skill_complementarity_score', sa.Float, nullable=False, default=0.0),
        sa.Column('creative_vision_alignment', sa.Float, nullable=False, default=0.0),
        sa.Column('communication_compatibility', sa.Float, nullable=False, default=0.0),
        sa.Column('schedule_compatibility', sa.Float, nullable=False, default=0.0),
        sa.Column('budget_alignment', sa.Float, nullable=False, default=0.0),
        sa.Column('geographical_compatibility', sa.Float, nullable=False, default=0.0),
        sa.Column('genre_overlap_score', sa.Float, nullable=False, default=0.0),
        sa.Column('experience_level_match', sa.Float, nullable=False, default=0.0),
        sa.Column('collaboration_history_factor', sa.Float, nullable=False, default=0.0),
        sa.Column('mutual_follower_overlap', sa.Float, nullable=False, default=0.0),
        sa.Column('audience_synergy_score', sa.Float, nullable=False, default=0.0),
        sa.Column('algorithm_used', matching_algorithm_enum, nullable=False),
        sa.Column('algorithm_version', sa.String(20), nullable=False, default='1.0'),
        sa.Column('confidence_interval', sa.Float, nullable=False, default=0.0),
        sa.Column('feature_weights', postgresql.JSONB),
        sa.Column('detailed_breakdown', postgresql.JSONB),
        sa.Column('success_probability', sa.Float, nullable=False, default=0.0),
        sa.Column('recommendation_reason', sa.Text),
        sa.Column('potential_challenges', postgresql.JSONB),
        sa.Column('suggested_collaboration_types', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('calculated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime),
        sa.Column('feedback_collected', sa.Boolean, nullable=False, default=False),
        sa.Column('actual_collaboration_outcome', sa.String(20)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create collaboration recommendations table
    op.create_table('collaboration_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recommended_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('matching_score_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_matching_scores.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recommendation_rank', sa.Integer, nullable=False),
        sa.Column('recommendation_type', sa.String(50), nullable=False),
        sa.Column('recommended_collaboration_type', collaboration_type_enum, nullable=False),
        sa.Column('project_concept', sa.Text),
        sa.Column('estimated_duration_days', sa.Integer),
        sa.Column('estimated_budget_range', sa.String(50)),
        sa.Column('success_probability', sa.Float, nullable=False),
        sa.Column('mutual_benefit_score', sa.Float, nullable=False),
        sa.Column('audience_growth_potential', sa.Float, nullable=False),
        sa.Column('revenue_potential', sa.Float, nullable=False),
        sa.Column('learning_opportunity_score', sa.Float, nullable=False),
        sa.Column('network_expansion_value', sa.Float, nullable=False),
        sa.Column('recommended_approach', sa.Text),
        sa.Column('talking_points', postgresql.JSONB),
        sa.Column('potential_deliverables', postgresql.JSONB),
        sa.Column('risk_factors', postgresql.JSONB),
        sa.Column('mitigation_strategies', postgresql.JSONB),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('viewed_by_user', sa.Boolean, nullable=False, default=False),
        sa.Column('user_interest_level', sa.Integer),
        sa.Column('user_feedback', sa.Text),
        sa.Column('contact_initiated', sa.Boolean, nullable=False, default=False),
        sa.Column('contact_initiated_at', sa.DateTime),
        sa.Column('response_received', sa.Boolean, nullable=False, default=False),
        sa.Column('collaboration_started', sa.Boolean, nullable=False, default=False),
        sa.Column('expires_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create collaboration projects table
    op.create_table('collaboration_projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_name', sa.String(200), nullable=False),
        sa.Column('project_description', sa.Text, nullable=False),
        sa.Column('collaboration_type', collaboration_type_enum, nullable=False),
        sa.Column('status', collaboration_status_enum, nullable=False, default='proposed'),
        sa.Column('creator_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column('lead_creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('matching_score_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_matching_scores.id')),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('collaboration_recommendations.id')),
        sa.Column('project_goals', postgresql.JSONB),
        sa.Column('deliverables', postgresql.JSONB),
        sa.Column('timeline', postgresql.JSONB),
        sa.Column('budget_total', sa.Numeric(15, 2)),
        sa.Column('revenue_sharing_agreement', postgresql.JSONB),
        sa.Column('roles_and_responsibilities', postgresql.JSONB),
        sa.Column('communication_preferences', postgresql.JSONB),
        sa.Column('milestone_definitions', postgresql.JSONB),
        sa.Column('quality_standards', postgresql.JSONB),
        sa.Column('intellectual_property_terms', postgresql.JSONB),
        sa.Column('dispute_resolution_process', sa.Text),
        sa.Column('start_date', sa.DateTime),
        sa.Column('expected_completion_date', sa.DateTime),
        sa.Column('actual_completion_date', sa.DateTime),
        sa.Column('project_files_urls', postgresql.ARRAY(sa.String(500)), default=[]),
        sa.Column('progress_percentage', sa.Float, nullable=False, default=0.0),
        sa.Column('current_phase', sa.String(100)),
        sa.Column('collaboration_score', sa.Float),
        sa.Column('individual_ratings', postgresql.JSONB),
        sa.Column('lessons_learned', sa.Text),
        sa.Column('success_metrics', postgresql.JSONB),
        sa.Column('final_outcome', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create collaboration analytics table
    op.create_table('collaboration_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('analytics_date', sa.Date, nullable=False),
        sa.Column('total_collaborations_initiated', sa.Integer, nullable=False, default=0),
        sa.Column('total_collaborations_received', sa.Integer, nullable=False, default=0),
        sa.Column('collaborations_accepted', sa.Integer, nullable=False, default=0),
        sa.Column('collaborations_completed', sa.Integer, nullable=False, default=0),
        sa.Column('collaborations_cancelled', sa.Integer, nullable=False, default=0),
        sa.Column('average_collaboration_duration_days', sa.Float, nullable=False, default=0.0),
        sa.Column('average_collaboration_rating', sa.Float, nullable=False, default=0.0),
        sa.Column('success_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('total_revenue_from_collaborations', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('average_revenue_per_collaboration', sa.Numeric(10, 2), nullable=False, default=0.00),
        sa.Column('network_growth_count', sa.Integer, nullable=False, default=0),
        sa.Column('audience_growth_from_collaborations', sa.Integer, nullable=False, default=0),
        sa.Column('skill_development_score', sa.Float, nullable=False, default=0.0),
        sa.Column('creativity_enhancement_score', sa.Float, nullable=False, default=0.0),
        sa.Column('most_successful_collaboration_type', collaboration_type_enum),
        sa.Column('preferred_collaboration_partners', postgresql.JSONB),
        sa.Column('collaboration_frequency_trend', sa.Float, nullable=False, default=0.0),
        sa.Column('reputation_score_change', sa.Float, nullable=False, default=0.0),
        sa.Column('ai_recommendation_accuracy', sa.Float, nullable=False, default=0.0),
        sa.Column('user_satisfaction_score', sa.Float, nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create collaboration feedback table
    op.create_table('collaboration_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('collaboration_project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('collaboration_projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reviewee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('overall_rating', sa.Integer, nullable=False),
        sa.Column('communication_rating', sa.Integer, nullable=False),
        sa.Column('creativity_rating', sa.Integer, nullable=False),
        sa.Column('technical_skill_rating', sa.Integer, nullable=False),
        sa.Column('reliability_rating', sa.Integer, nullable=False),
        sa.Column('professionalism_rating', sa.Integer, nullable=False),
        sa.Column('would_collaborate_again', sa.Boolean, nullable=False),
        sa.Column('recommend_to_others', sa.Boolean, nullable=False),
        sa.Column('written_feedback', sa.Text),
        sa.Column('strengths_highlighted', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('areas_for_improvement', postgresql.ARRAY(sa.String(100)), default=[]),
        sa.Column('collaboration_highlights', sa.Text),
        sa.Column('challenges_faced', sa.Text),
        sa.Column('suggestions_for_future', sa.Text),
        sa.Column('anonymous_feedback', sa.Boolean, nullable=False, default=False),
        sa.Column('feedback_verified', sa.Boolean, nullable=False, default=False),
        sa.Column('helpful_votes', sa.Integer, nullable=False, default=0),
        sa.Column('disputed', sa.Boolean, nullable=False, default=False),
        sa.Column('dispute_reason', sa.Text),
        sa.Column('moderation_status', sa.String(20), nullable=False, default='approved'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create performance indexes
    
    # Creator Compatibility Profiles indexes
    op.create_index('idx_compatibility_profiles_user_id', 'creator_compatibility_profiles', ['user_id'])
    op.create_index('idx_compatibility_profiles_types', 'creator_compatibility_profiles', ['preferred_collaboration_types'], postgresql_using='gin')
    op.create_index('idx_compatibility_profiles_duration', 'creator_compatibility_profiles', ['preferred_project_duration'])
    op.create_index('idx_compatibility_profiles_timezone', 'creator_compatibility_profiles', ['timezone'])
    op.create_index('idx_compatibility_profiles_skills', 'creator_compatibility_profiles', ['skill_level_preference'])
    op.create_index('idx_compatibility_profiles_budget', 'creator_compatibility_profiles', ['budget_range_min', 'budget_range_max'])
    op.create_index('idx_compatibility_profiles_geography', 'creator_compatibility_profiles', ['geographical_preference'], postgresql_using='gin')
    op.create_index('idx_compatibility_profiles_languages', 'creator_compatibility_profiles', ['language_preferences'], postgresql_using='gin')
    op.create_index('idx_compatibility_profiles_history_rating', 'creator_compatibility_profiles', ['collaboration_history_rating'])
    op.create_index('idx_compatibility_profiles_reliability', 'creator_compatibility_profiles', ['reliability_score'])
    op.create_index('idx_compatibility_profiles_completeness', 'creator_compatibility_profiles', ['profile_completeness'])
    
    # AI Matching Scores indexes
    op.create_index('idx_ai_matching_creator_a', 'ai_matching_scores', ['creator_a_id'])
    op.create_index('idx_ai_matching_creator_b', 'ai_matching_scores', ['creator_b_id'])
    op.create_index('idx_ai_matching_overall_score', 'ai_matching_scores', ['overall_compatibility_score'])
    op.create_index('idx_ai_matching_compatibility_level', 'ai_matching_scores', ['compatibility_level'])
    op.create_index('idx_ai_matching_algorithm', 'ai_matching_scores', ['algorithm_used'])
    op.create_index('idx_ai_matching_success_probability', 'ai_matching_scores', ['success_probability'])
    op.create_index('idx_ai_matching_calculated_at', 'ai_matching_scores', ['calculated_at'])
    op.create_index('idx_ai_matching_expires_at', 'ai_matching_scores', ['expires_at'])
    op.create_index('idx_ai_matching_pair', 'ai_matching_scores', ['creator_a_id', 'creator_b_id'])
    
    # Collaboration Recommendations indexes
    op.create_index('idx_collab_recommendations_user_id', 'collaboration_recommendations', ['user_id'])
    op.create_index('idx_collab_recommendations_recommended_user', 'collaboration_recommendations', ['recommended_user_id'])
    op.create_index('idx_collab_recommendations_matching_score', 'collaboration_recommendations', ['matching_score_id'])
    op.create_index('idx_collab_recommendations_rank', 'collaboration_recommendations', ['recommendation_rank'])
    op.create_index('idx_collab_recommendations_type', 'collaboration_recommendations', ['recommended_collaboration_type'])
    op.create_index('idx_collab_recommendations_success_prob', 'collaboration_recommendations', ['success_probability'])
    op.create_index('idx_collab_recommendations_status', 'collaboration_recommendations', ['status'])
    op.create_index('idx_collab_recommendations_viewed', 'collaboration_recommendations', ['viewed_by_user'])
    op.create_index('idx_collab_recommendations_contact', 'collaboration_recommendations', ['contact_initiated'])
    op.create_index('idx_collab_recommendations_expires', 'collaboration_recommendations', ['expires_at'])
    
    # Collaboration Projects indexes
    op.create_index('idx_collab_projects_name', 'collaboration_projects', ['project_name'])
    op.create_index('idx_collab_projects_type', 'collaboration_projects', ['collaboration_type'])
    op.create_index('idx_collab_projects_status', 'collaboration_projects', ['status'])
    op.create_index('idx_collab_projects_lead_creator', 'collaboration_projects', ['lead_creator_id'])
    op.create_index('idx_collab_projects_creators', 'collaboration_projects', ['creator_ids'], postgresql_using='gin')
    op.create_index('idx_collab_projects_start_date', 'collaboration_projects', ['start_date'])
    op.create_index('idx_collab_projects_completion_date', 'collaboration_projects', ['expected_completion_date'])
    op.create_index('idx_collab_projects_progress', 'collaboration_projects', ['progress_percentage'])
    op.create_index('idx_collab_projects_budget', 'collaboration_projects', ['budget_total'])
    
    # Collaboration Analytics indexes
    op.create_index('idx_collab_analytics_user_id', 'collaboration_analytics', ['user_id'])
    op.create_index('idx_collab_analytics_date', 'collaboration_analytics', ['analytics_date'])
    op.create_index('idx_collab_analytics_success_rate', 'collaboration_analytics', ['success_rate'])
    op.create_index('idx_collab_analytics_avg_rating', 'collaboration_analytics', ['average_collaboration_rating'])
    op.create_index('idx_collab_analytics_revenue', 'collaboration_analytics', ['total_revenue_from_collaborations'])
    op.create_index('idx_collab_analytics_most_successful', 'collaboration_analytics', ['most_successful_collaboration_type'])
    op.create_index('idx_collab_analytics_user_date', 'collaboration_analytics', ['user_id', 'analytics_date'])
    
    # Collaboration Feedback indexes
    op.create_index('idx_collab_feedback_project_id', 'collaboration_feedback', ['collaboration_project_id'])
    op.create_index('idx_collab_feedback_reviewer', 'collaboration_feedback', ['reviewer_id'])
    op.create_index('idx_collab_feedback_reviewee', 'collaboration_feedback', ['reviewee_id'])
    op.create_index('idx_collab_feedback_overall_rating', 'collaboration_feedback', ['overall_rating'])
    op.create_index('idx_collab_feedback_would_collaborate', 'collaboration_feedback', ['would_collaborate_again'])
    op.create_index('idx_collab_feedback_recommend', 'collaboration_feedback', ['recommend_to_others'])
    op.create_index('idx_collab_feedback_verified', 'collaboration_feedback', ['feedback_verified'])
    op.create_index('idx_collab_feedback_moderation', 'collaboration_feedback', ['moderation_status'])


def downgrade() -> None:
    """Downgrade database schema - Remove AI-powered collaboration matching tables."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('collaboration_feedback')
    op.drop_table('collaboration_analytics')
    op.drop_table('collaboration_projects')
    op.drop_table('collaboration_recommendations')
    op.drop_table('ai_matching_scores')
    op.drop_table('creator_compatibility_profiles')
    
    # Drop ENUM types
    sa.Enum(name='collaboration_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='compatibility_level').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='matching_algorithm').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='collaboration_type').drop(op.get_bind(), checkfirst=True)