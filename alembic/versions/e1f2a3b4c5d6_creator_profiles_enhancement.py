"""Enhanced creator profiles for multi-format content creation

Revision ID: e1f2a3b4c5d6
Revises: d21b3c27ee2c
Create Date: 2025-09-05 06:20:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration enhances creator profiles to support multi-format content creation
including musicians, bloggers, photographers, influencers, and comedians with
specialized tracking and capabilities.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e1f2a3b4c5d6'
down_revision = 'd21b3c27ee2c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - Enhanced creator profiles."""
    
    # Create enhanced specialization enum
    specialization_enum = sa.Enum(
        'musician', 'podcaster', 'blogger', 'photographer', 'videographer',
        'influencer', 'comedian', 'voice_actor', 'producer', 'composer',
        'sound_engineer', 'video_editor', 'graphic_designer', 'animator',
        'writer', 'journalist', 'interviewer', 'reviewer', 'educator',
        name='creator_specialization'
    )
    
    # Create skill level enum
    skill_level_enum = sa.Enum(
        'beginner', 'intermediate', 'advanced', 'expert', 'master',
        name='skill_level'
    )
    
    # Create verification tier enum
    verification_tier_enum = sa.Enum(
        'unverified', 'basic', 'professional', 'enterprise', 'celebrity',
        name='verification_tier'
    )
    
    # Create content quality enum
    content_quality_enum = sa.Enum(
        'standard', 'high', 'premium', 'ultra', 'studio',
        name='content_quality'
    )
    
    # Create enhanced creator specializations table
    op.create_table('creator_specializations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('specialization', specialization_enum, nullable=False),
        sa.Column('skill_level', skill_level_enum, nullable=False, default='beginner'),
        sa.Column('experience_years', sa.Integer, nullable=False, default=0),
        sa.Column('portfolio_url', sa.String(500)),
        sa.Column('certification_url', sa.String(500)),
        sa.Column('is_primary', sa.Boolean, nullable=False, default=False),
        sa.Column('verified_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create creator capabilities table
    op.create_table('creator_capabilities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_formats', postgresql.ARRAY(sa.String(50)), nullable=False, default=[]),
        sa.Column('supported_languages', postgresql.ARRAY(sa.String(10)), nullable=False, default=[]),
        sa.Column('equipment_list', postgresql.JSONB),
        sa.Column('software_proficiency', postgresql.JSONB),
        sa.Column('max_content_quality', content_quality_enum, nullable=False, default='standard'),
        sa.Column('turnaround_time_hours', sa.Integer, nullable=False, default=72),
        sa.Column('availability_schedule', postgresql.JSONB),
        sa.Column('collaboration_preferences', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create creator verification documents table
    op.create_table('creator_verification_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_type', sa.String(100), nullable=False),
        sa.Column('document_url', sa.String(500), nullable=False),
        sa.Column('verification_tier', verification_tier_enum, nullable=False),
        sa.Column('verification_status', sa.String(20), nullable=False, default='pending'),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('reviewed_at', sa.DateTime),
        sa.Column('expiry_date', sa.DateTime),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create creator performance metrics table
    op.create_table('creator_performance_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('metric_date', sa.Date, nullable=False),
        sa.Column('content_created_count', sa.Integer, nullable=False, default=0),
        sa.Column('content_published_count', sa.Integer, nullable=False, default=0),
        sa.Column('total_views', sa.BigInteger, nullable=False, default=0),
        sa.Column('total_likes', sa.BigInteger, nullable=False, default=0),
        sa.Column('total_shares', sa.BigInteger, nullable=False, default=0),
        sa.Column('total_comments', sa.BigInteger, nullable=False, default=0),
        sa.Column('engagement_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('revenue_generated', sa.Numeric(15, 2), nullable=False, default=0.00),
        sa.Column('collaborations_completed', sa.Integer, nullable=False, default=0),
        sa.Column('quality_score', sa.Float, nullable=False, default=0.0),
        sa.Column('consistency_score', sa.Float, nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create creator brand assets table
    op.create_table('creator_brand_assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asset_type', sa.String(50), nullable=False),
        sa.Column('asset_name', sa.String(200), nullable=False),
        sa.Column('asset_url', sa.String(500), nullable=False),
        sa.Column('usage_rights', sa.String(100), nullable=False),
        sa.Column('color_palette', postgresql.JSONB),
        sa.Column('brand_guidelines', sa.Text),
        sa.Column('is_public', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create performance indexes
    
    # Creator Specializations indexes
    op.create_index('idx_creator_specializations_user_id', 'creator_specializations', ['user_id'])
    op.create_index('idx_creator_specializations_type', 'creator_specializations', ['specialization'])
    op.create_index('idx_creator_specializations_skill', 'creator_specializations', ['skill_level'])
    op.create_index('idx_creator_specializations_primary', 'creator_specializations', ['user_id', 'is_primary'])
    op.create_index('idx_creator_specializations_verified', 'creator_specializations', ['verified_at'])
    
    # Creator Capabilities indexes
    op.create_index('idx_creator_capabilities_user_id', 'creator_capabilities', ['user_id'])
    op.create_index('idx_creator_capabilities_quality', 'creator_capabilities', ['max_content_quality'])
    op.create_index('idx_creator_capabilities_turnaround', 'creator_capabilities', ['turnaround_time_hours'])
    
    # Creator Verification Documents indexes
    op.create_index('idx_verification_docs_user_id', 'creator_verification_documents', ['user_id'])
    op.create_index('idx_verification_docs_type', 'creator_verification_documents', ['document_type'])
    op.create_index('idx_verification_docs_tier', 'creator_verification_documents', ['verification_tier'])
    op.create_index('idx_verification_docs_status', 'creator_verification_documents', ['verification_status'])
    op.create_index('idx_verification_docs_expiry', 'creator_verification_documents', ['expiry_date'])
    
    # Creator Performance Metrics indexes
    op.create_index('idx_performance_metrics_user_id', 'creator_performance_metrics', ['user_id'])
    op.create_index('idx_performance_metrics_date', 'creator_performance_metrics', ['metric_date'])
    op.create_index('idx_performance_metrics_revenue', 'creator_performance_metrics', ['revenue_generated'])
    op.create_index('idx_performance_metrics_engagement', 'creator_performance_metrics', ['engagement_rate'])
    op.create_index('idx_performance_metrics_quality', 'creator_performance_metrics', ['quality_score'])
    op.create_index('idx_performance_metrics_user_date', 'creator_performance_metrics', ['user_id', 'metric_date'])
    
    # Creator Brand Assets indexes
    op.create_index('idx_brand_assets_user_id', 'creator_brand_assets', ['user_id'])
    op.create_index('idx_brand_assets_type', 'creator_brand_assets', ['asset_type'])
    op.create_index('idx_brand_assets_public', 'creator_brand_assets', ['is_public'])


def downgrade() -> None:
    """Downgrade database schema - Remove enhanced creator profile tables."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('creator_brand_assets')
    op.drop_table('creator_performance_metrics')
    op.drop_table('creator_verification_documents')
    op.drop_table('creator_capabilities')
    op.drop_table('creator_specializations')
    
    # Drop ENUM types
    sa.Enum(name='content_quality').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='verification_tier').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='skill_level').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='creator_specialization').drop(op.get_bind(), checkfirst=True)