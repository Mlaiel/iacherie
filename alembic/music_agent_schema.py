"""🎵 Music Agent Schema - Enterprise AI Music Generation & Analysis
================================================================
Module: alembic/music_agent_schema.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Enterprise Music Agent Database Schema - Ultra-Industrial AI-Powered
Responsibility: Database schema for AI music generation, analysis, and content protection
================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

Music Agent Database Schema for:
- AI music generation and composition
- Audio fingerprinting and content matching
- Music analytics and performance tracking
- Copyright protection and monetization
- Multi-platform music distribution
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime, timezone
import uuid

# revision identifiers
revision = 'music_agent_001'
down_revision = None
branch_labels = ('music_agent',)
depends_on = None


def upgrade() -> None:
    """Upgrade: Create music agent tables"""
    
    # Music Agent Core Configuration
    op.create_table(
        'music_agents',
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('agent_name', sa.String(255), nullable=False),
        sa.Column('agent_type', sa.String(100), nullable=False),  # composer, analyzer, fingerprinter, etc.
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('model_config', postgresql.JSONB, nullable=False),
        sa.Column('training_data_version', sa.String(100)),
        sa.Column('capabilities', postgresql.JSONB, nullable=False),
        sa.Column('performance_metrics', postgresql.JSONB),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False),
        
        # Indexes
        sa.Index('idx_music_agents_type', 'agent_type'),
        sa.Index('idx_music_agents_active', 'is_active'),
        sa.Index('idx_music_agents_created', 'created_at'),
    )
    
    # Music Generation Sessions
    op.create_table(
        'music_generation_sessions',
        sa.Column('session_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('music_agents.agent_id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Generation parameters
        sa.Column('generation_prompt', sa.Text, nullable=False),
        sa.Column('music_style', sa.String(100)),
        sa.Column('genre', sa.String(100)),
        sa.Column('tempo_bpm', sa.Integer),
        sa.Column('key_signature', sa.String(10)),
        sa.Column('time_signature', sa.String(10)),
        sa.Column('duration_seconds', sa.Integer),
        sa.Column('instrumentation', postgresql.JSONB),
        sa.Column('mood_tags', postgresql.JSONB),
        
        # Generation results
        sa.Column('generated_audio_url', sa.String(500)),
        sa.Column('generated_midi_url', sa.String(500)),
        sa.Column('generated_sheet_music_url', sa.String(500)),
        sa.Column('audio_fingerprint', sa.String(1000)),
        sa.Column('spectral_analysis', postgresql.JSONB),
        sa.Column('harmonic_analysis', postgresql.JSONB),
        
        # Metadata
        sa.Column('generation_quality_score', sa.Float),
        sa.Column('processing_time_seconds', sa.Float),
        sa.Column('model_confidence', sa.Float),
        sa.Column('status', sa.String(50), default='pending', nullable=False),
        sa.Column('error_message', sa.Text),
        
        # Compliance and rights
        sa.Column('copyright_status', sa.String(50), default='original', nullable=False),
        sa.Column('rights_clearance', postgresql.JSONB),
        sa.Column('content_id_registered', sa.Boolean, default=False),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
        
        # Indexes
        sa.Index('idx_music_sessions_agent', 'agent_id'),
        sa.Index('idx_music_sessions_user', 'user_id'),
        sa.Index('idx_music_sessions_tenant', 'tenant_id'),
        sa.Index('idx_music_sessions_status', 'status'),
        sa.Index('idx_music_sessions_created', 'created_at'),
        sa.Index('idx_music_sessions_genre', 'genre'),
        sa.Index('idx_music_sessions_fingerprint', 'audio_fingerprint'),
    )
    
    # Music Library and Catalog
    op.create_table(
        'music_catalog',
        sa.Column('track_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('music_generation_sessions.session_id')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Track metadata
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('artist', sa.String(255)),
        sa.Column('album', sa.String(255)),
        sa.Column('genre', sa.String(100)),
        sa.Column('subgenre', sa.String(100)),
        sa.Column('mood', sa.String(100)),
        sa.Column('energy_level', sa.String(50)),
        sa.Column('tags', postgresql.JSONB),
        
        # Technical metadata
        sa.Column('duration_seconds', sa.Float, nullable=False),
        sa.Column('tempo_bpm', sa.Integer),
        sa.Column('key_signature', sa.String(10)),
        sa.Column('time_signature', sa.String(10)),
        sa.Column('audio_format', sa.String(20)),
        sa.Column('sample_rate_hz', sa.Integer),
        sa.Column('bit_depth', sa.Integer),
        sa.Column('channels', sa.Integer),
        sa.Column('file_size_bytes', sa.BigInteger),
        
        # Content and storage
        sa.Column('audio_file_url', sa.String(500), nullable=False),
        sa.Column('audio_file_hash', sa.String(128)),
        sa.Column('thumbnail_url', sa.String(500)),
        sa.Column('waveform_data', postgresql.JSONB),
        sa.Column('lyrics', sa.Text),
        sa.Column('midi_data_url', sa.String(500)),
        sa.Column('sheet_music_url', sa.String(500)),
        
        # Audio analysis
        sa.Column('audio_fingerprint', sa.String(1000), nullable=False),
        sa.Column('chromagram', postgresql.JSONB),
        sa.Column('spectral_centroid', postgresql.JSONB),
        sa.Column('spectral_rolloff', postgresql.JSONB),
        sa.Column('mfcc_features', postgresql.JSONB),
        sa.Column('loudness_lufs', sa.Float),
        sa.Column('dynamic_range', sa.Float),
        
        # Rights and monetization
        sa.Column('copyright_owner', sa.String(255)),
        sa.Column('license_type', sa.String(100)),
        sa.Column('usage_rights', postgresql.JSONB),
        sa.Column('monetization_enabled', sa.Boolean, default=True),
        sa.Column('royalty_splits', postgresql.JSONB),
        
        # Publishing and distribution
        sa.Column('publication_status', sa.String(50), default='draft'),
        sa.Column('visibility', sa.String(50), default='private'),
        sa.Column('distribution_platforms', postgresql.JSONB),
        sa.Column('content_id_registered', sa.Boolean, default=False),
        sa.Column('isrc_code', sa.String(20)),
        sa.Column('upc_code', sa.String(20)),
        
        # Analytics
        sa.Column('play_count', sa.BigInteger, default=0),
        sa.Column('download_count', sa.BigInteger, default=0),
        sa.Column('like_count', sa.BigInteger, default=0),
        sa.Column('share_count', sa.BigInteger, default=0),
        sa.Column('revenue_generated', sa.Numeric(10, 2), default=0),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False),
        sa.Column('published_at', sa.TIMESTAMP(timezone=True)),
        
        # Indexes
        sa.Index('idx_music_catalog_user', 'user_id'),
        sa.Index('idx_music_catalog_tenant', 'tenant_id'),
        sa.Index('idx_music_catalog_genre', 'genre'),
        sa.Index('idx_music_catalog_status', 'publication_status'),
        sa.Index('idx_music_catalog_fingerprint', 'audio_fingerprint'),
        sa.Index('idx_music_catalog_created', 'created_at'),
        sa.Index('idx_music_catalog_plays', 'play_count'),
        sa.Index('idx_music_catalog_title_search', 'title'),
        
        # Full-text search
        sa.Index('idx_music_catalog_search', 'title', 'artist', 'album', postgresql_using='gin'),
    )
    
    # Music Analytics and Performance
    op.create_table(
        'music_analytics',
        sa.Column('analytics_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('track_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('music_catalog.track_id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Temporal metrics
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('hour', sa.Integer),  # 0-23 for hourly analytics
        
        # Platform-specific metrics
        sa.Column('platform', sa.String(100), nullable=False),  # spotify, youtube, etc.
        sa.Column('plays', sa.BigInteger, default=0),
        sa.Column('unique_listeners', sa.BigInteger, default=0),
        sa.Column('completion_rate', sa.Float),  # Percentage of track completed
        sa.Column('skip_rate', sa.Float),
        sa.Column('replay_rate', sa.Float),
        
        # Engagement metrics
        sa.Column('likes', sa.BigInteger, default=0),
        sa.Column('dislikes', sa.BigInteger, default=0),
        sa.Column('shares', sa.BigInteger, default=0),
        sa.Column('comments', sa.BigInteger, default=0),
        sa.Column('saves', sa.BigInteger, default=0),
        sa.Column('playlist_adds', sa.BigInteger, default=0),
        
        # Geographic data
        sa.Column('country_code', sa.String(3)),
        sa.Column('region', sa.String(100)),
        sa.Column('city', sa.String(100)),
        
        # Demographic data
        sa.Column('age_group', sa.String(20)),
        sa.Column('gender', sa.String(20)),
        
        # Revenue metrics
        sa.Column('streams_revenue', sa.Numeric(10, 4), default=0),
        sa.Column('download_revenue', sa.Numeric(10, 4), default=0),
        sa.Column('licensing_revenue', sa.Numeric(10, 4), default=0),
        
        # Technical metrics
        sa.Column('audio_quality', sa.String(20)),  # 128k, 320k, lossless
        sa.Column('device_type', sa.String(50)),
        sa.Column('bandwidth_used_mb', sa.Float),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        
        # Indexes
        sa.Index('idx_music_analytics_track', 'track_id'),
        sa.Index('idx_music_analytics_date', 'date'),
        sa.Index('idx_music_analytics_platform', 'platform'),
        sa.Index('idx_music_analytics_country', 'country_code'),
        sa.Index('idx_music_analytics_composite', 'track_id', 'date', 'platform'),
    )
    
    # Music Collaboration and Projects
    op.create_table(
        'music_collaborations',
        sa.Column('collaboration_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_name', sa.String(255), nullable=False),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('collaborators', postgresql.JSONB, nullable=False),  # Array of user IDs and roles
        
        # Project details
        sa.Column('description', sa.Text),
        sa.Column('target_genre', sa.String(100)),
        sa.Column('target_duration', sa.Integer),
        sa.Column('target_mood', sa.String(100)),
        sa.Column('inspiration_tracks', postgresql.JSONB),
        
        # Collaboration workflow
        sa.Column('status', sa.String(50), default='active', nullable=False),
        sa.Column('current_stage', sa.String(100)),  # composition, arrangement, production, mixing, mastering
        sa.Column('deadline', sa.TIMESTAMP(timezone=True)),
        sa.Column('workflow_config', postgresql.JSONB),
        
        # Version control
        sa.Column('current_version', sa.Integer, default=1),
        sa.Column('track_versions', postgresql.JSONB),
        
        # Rights and revenue sharing
        sa.Column('rights_agreement', postgresql.JSONB),
        sa.Column('revenue_split', postgresql.JSONB),
        sa.Column('contract_terms', postgresql.JSONB),
        
        # Final output
        sa.Column('final_track_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('music_catalog.track_id')),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
        
        # Indexes
        sa.Index('idx_music_collab_creator', 'creator_id'),
        sa.Index('idx_music_collab_status', 'status'),
        sa.Index('idx_music_collab_genre', 'target_genre'),
        sa.Index('idx_music_collab_created', 'created_at'),
    )
    
    # Music Content Protection and Monitoring
    op.create_table(
        'music_content_protection',
        sa.Column('protection_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('track_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('music_catalog.track_id'), nullable=False),
        sa.Column('fingerprint_hash', sa.String(128), nullable=False),
        
        # Protection configuration
        sa.Column('protection_level', sa.String(50), default='standard', nullable=False),
        sa.Column('monitoring_platforms', postgresql.JSONB, nullable=False),
        sa.Column('content_id_system', sa.String(100)),  # YouTube Content ID, Facebook Rights Manager, etc.
        sa.Column('content_id_reference', sa.String(255)),
        
        # Detection settings
        sa.Column('similarity_threshold', sa.Float, default=0.8),
        sa.Column('segment_duration_seconds', sa.Integer, default=30),
        sa.Column('detection_sensitivity', sa.String(20), default='medium'),
        
        # Enforcement actions
        sa.Column('enforcement_policy', postgresql.JSONB),
        sa.Column('automatic_actions', postgresql.JSONB),
        sa.Column('manual_review_required', sa.Boolean, default=False),
        
        # Status and monitoring
        sa.Column('protection_status', sa.String(50), default='active'),
        sa.Column('last_scan_date', sa.TIMESTAMP(timezone=True)),
        sa.Column('violations_detected', sa.Integer, default=0),
        sa.Column('claims_filed', sa.Integer, default=0),
        sa.Column('revenue_recovered', sa.Numeric(10, 2), default=0),
        
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc), nullable=False),
        
        # Indexes
        sa.Index('idx_music_protection_track', 'track_id'),
        sa.Index('idx_music_protection_fingerprint', 'fingerprint_hash'),
        sa.Index('idx_music_protection_status', 'protection_status'),
        sa.Index('idx_music_protection_scan', 'last_scan_date'),
    )
    
    # Add constraints and foreign keys
    op.create_foreign_key('fk_music_sessions_agent', 'music_generation_sessions', 'music_agents', ['agent_id'], ['agent_id'])
    op.create_foreign_key('fk_music_catalog_session', 'music_catalog', 'music_generation_sessions', ['session_id'], ['session_id'])
    op.create_foreign_key('fk_music_analytics_track', 'music_analytics', 'music_catalog', ['track_id'], ['track_id'])
    op.create_foreign_key('fk_music_collab_track', 'music_collaborations', 'music_catalog', ['final_track_id'], ['track_id'])
    op.create_foreign_key('fk_music_protection_track', 'music_content_protection', 'music_catalog', ['track_id'], ['track_id'])


def downgrade() -> None:
    """Downgrade: Drop music agent tables"""
    
    # Drop tables in reverse order to handle foreign key dependencies
    op.drop_table('music_content_protection')
    op.drop_table('music_collaborations')
    op.drop_table('music_analytics')
    op.drop_table('music_catalog')
    op.drop_table('music_generation_sessions')
    op.drop_table('music_agents')