"""Advanced content fingerprinting system for duplicate detection

Revision ID: h4g5f6e7d8c9
Revises: g3f4e5d6c7b8
Create Date: 2025-09-05 06:35:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the advanced content fingerprinting system for
audio/video/image content with duplicate detection, violation tracking,
and cross-platform content monitoring.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'h4g5f6e7d8c9'
down_revision = 'g3f4e5d6c7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - Advanced content fingerprinting system."""
    
    # Create fingerprint algorithm enum
    fingerprint_algorithm_enum = sa.Enum(
        'perceptual_hash', 'chromaprint', 'mfcc', 'spectral_centroid',
        'zero_crossing_rate', 'mel_spectrogram', 'cnn_embedding',
        'wavelet_transform', 'fourier_transform', 'sift_features',
        'orb_features', 'surf_features', 'lbp_histogram', 'color_histogram',
        'edge_histogram', 'texture_analysis', 'deep_cnn', 'vgg16_features',
        'resnet_features', 'clip_embeddings', 'wav2vec2_embeddings',
        name='fingerprint_algorithm'
    )
    
    # Create fingerprint status enum
    fingerprint_status_enum = sa.Enum(
        'pending', 'processing', 'completed', 'failed', 'outdated', 'verified',
        name='fingerprint_status'
    )
    
    # Create match confidence enum
    match_confidence_enum = sa.Enum(
        'low', 'medium', 'high', 'very_high', 'exact',
        name='match_confidence'
    )
    
    # Create violation severity enum
    violation_severity_enum = sa.Enum(
        'minor', 'moderate', 'major', 'critical', 'legal',
        name='violation_severity'
    )
    
    # Create advanced content fingerprints table
    op.create_table('advanced_content_fingerprints',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('fingerprint_algorithm', fingerprint_algorithm_enum, nullable=False),
        sa.Column('fingerprint_version', sa.String(20), nullable=False, default='1.0'),
        sa.Column('fingerprint_data', postgresql.JSONB, nullable=False),
        sa.Column('fingerprint_hash', sa.String(512), nullable=False),
        sa.Column('perceptual_hash', sa.String(256)),
        sa.Column('feature_vector', postgresql.ARRAY(sa.Float), default=[]),
        sa.Column('segment_fingerprints', postgresql.JSONB),
        sa.Column('temporal_segments', postgresql.JSONB),
        sa.Column('frequency_bands', postgresql.JSONB),
        sa.Column('robustness_score', sa.Float, nullable=False, default=0.0),
        sa.Column('uniqueness_score', sa.Float, nullable=False, default=0.0),
        sa.Column('processing_duration_ms', sa.Integer),
        sa.Column('status', fingerprint_status_enum, nullable=False, default='pending'),
        sa.Column('quality_metrics', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create duplicate detection matches table
    op.create_table('duplicate_detection_matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('original_fingerprint_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('advanced_content_fingerprints.id', ondelete='CASCADE'), nullable=False),
        sa.Column('duplicate_fingerprint_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('advanced_content_fingerprints.id', ondelete='CASCADE'), nullable=False),
        sa.Column('similarity_score', sa.Float, nullable=False),
        sa.Column('match_confidence', match_confidence_enum, nullable=False),
        sa.Column('matching_segments', postgresql.JSONB),
        sa.Column('temporal_alignment', postgresql.JSONB),
        sa.Column('frequency_correlation', sa.Float),
        sa.Column('visual_similarity', sa.Float),
        sa.Column('audio_similarity', sa.Float),
        sa.Column('structural_similarity', sa.Float),
        sa.Column('detection_algorithm', sa.String(100), nullable=False),
        sa.Column('false_positive_probability', sa.Float, nullable=False, default=0.0),
        sa.Column('verification_status', sa.String(20), nullable=False, default='unverified'),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('verified_at', sa.DateTime),
        sa.Column('match_metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create cross-platform monitoring table
    op.create_table('cross_platform_monitoring',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform_name', sa.String(100), nullable=False),
        sa.Column('platform_content_id', sa.String(200)),
        sa.Column('platform_url', sa.String(1000)),
        sa.Column('scan_frequency_hours', sa.Integer, nullable=False, default=24),
        sa.Column('last_scan_at', sa.DateTime),
        sa.Column('next_scan_at', sa.DateTime),
        sa.Column('scan_status', sa.String(20), nullable=False, default='active'),
        sa.Column('violations_detected', sa.Integer, nullable=False, default=0),
        sa.Column('false_positives', sa.Integer, nullable=False, default=0),
        sa.Column('monitoring_since', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('api_rate_limit', sa.Integer),
        sa.Column('api_quota_used', sa.Integer, nullable=False, default=0),
        sa.Column('monitoring_cost', sa.Numeric(10, 4), nullable=False, default=0.0000),
        sa.Column('alert_thresholds', postgresql.JSONB),
        sa.Column('exclusion_patterns', postgresql.ARRAY(sa.String(200)), default=[]),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create violation tracking table
    op.create_table('violation_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('original_content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('monitoring_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cross_platform_monitoring.id', ondelete='CASCADE')),
        sa.Column('duplicate_match_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('duplicate_detection_matches.id', ondelete='CASCADE')),
        sa.Column('violation_type', sa.String(50), nullable=False),
        sa.Column('severity', violation_severity_enum, nullable=False),
        sa.Column('violating_url', sa.String(1000), nullable=False),
        sa.Column('violating_platform', sa.String(100), nullable=False),
        sa.Column('violator_account', sa.String(200)),
        sa.Column('violation_description', sa.Text),
        sa.Column('evidence_urls', postgresql.ARRAY(sa.String(500)), default=[]),
        sa.Column('similarity_evidence', postgresql.JSONB),
        sa.Column('detection_confidence', sa.Float, nullable=False),
        sa.Column('financial_impact_estimate', sa.Numeric(15, 2)),
        sa.Column('view_count_lost', sa.BigInteger),
        sa.Column('revenue_lost_estimate', sa.Numeric(15, 2)),
        sa.Column('first_detected_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('last_verified_at', sa.DateTime),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('response_actions', postgresql.JSONB),
        sa.Column('resolution_date', sa.DateTime),
        sa.Column('resolution_method', sa.String(100)),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create fingerprint performance metrics table
    op.create_table('fingerprint_performance_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('algorithm', fingerprint_algorithm_enum, nullable=False),
        sa.Column('metric_date', sa.Date, nullable=False),
        sa.Column('total_fingerprints_generated', sa.Integer, nullable=False, default=0),
        sa.Column('successful_generations', sa.Integer, nullable=False, default=0),
        sa.Column('failed_generations', sa.Integer, nullable=False, default=0),
        sa.Column('average_generation_time_ms', sa.Float, nullable=False, default=0.0),
        sa.Column('average_robustness_score', sa.Float, nullable=False, default=0.0),
        sa.Column('average_uniqueness_score', sa.Float, nullable=False, default=0.0),
        sa.Column('total_matches_detected', sa.Integer, nullable=False, default=0),
        sa.Column('true_positives', sa.Integer, nullable=False, default=0),
        sa.Column('false_positives', sa.Integer, nullable=False, default=0),
        sa.Column('true_negatives', sa.Integer, nullable=False, default=0),
        sa.Column('false_negatives', sa.Integer, nullable=False, default=0),
        sa.Column('precision', sa.Float, nullable=False, default=0.0),
        sa.Column('recall', sa.Float, nullable=False, default=0.0),
        sa.Column('f1_score', sa.Float, nullable=False, default=0.0),
        sa.Column('accuracy', sa.Float, nullable=False, default=0.0),
        sa.Column('processing_cost', sa.Numeric(10, 4), nullable=False, default=0.0000),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create similarity clusters table for grouping similar content
    op.create_table('similarity_clusters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('cluster_name', sa.String(200), nullable=False),
        sa.Column('cluster_algorithm', sa.String(100), nullable=False),
        sa.Column('representative_content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id')),
        sa.Column('member_content_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), default=[]),
        sa.Column('cluster_center', postgresql.ARRAY(sa.Float), default=[]),
        sa.Column('average_similarity', sa.Float, nullable=False, default=0.0),
        sa.Column('cluster_size', sa.Integer, nullable=False, default=0),
        sa.Column('cluster_cohesion', sa.Float, nullable=False, default=0.0),
        sa.Column('cluster_separation', sa.Float, nullable=False, default=0.0),
        sa.Column('last_updated', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('auto_update_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('update_frequency_hours', sa.Integer, nullable=False, default=168),
        sa.Column('cluster_metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create performance indexes
    
    # Advanced Content Fingerprints indexes
    op.create_index('idx_advanced_fingerprints_content_id', 'advanced_content_fingerprints', ['content_id'])
    op.create_index('idx_advanced_fingerprints_algorithm', 'advanced_content_fingerprints', ['fingerprint_algorithm'])
    op.create_index('idx_advanced_fingerprints_hash', 'advanced_content_fingerprints', ['fingerprint_hash'])
    op.create_index('idx_advanced_fingerprints_perceptual', 'advanced_content_fingerprints', ['perceptual_hash'])
    op.create_index('idx_advanced_fingerprints_status', 'advanced_content_fingerprints', ['status'])
    op.create_index('idx_advanced_fingerprints_robustness', 'advanced_content_fingerprints', ['robustness_score'])
    op.create_index('idx_advanced_fingerprints_uniqueness', 'advanced_content_fingerprints', ['uniqueness_score'])
    op.create_index('idx_advanced_fingerprints_version', 'advanced_content_fingerprints', ['fingerprint_version'])
    
    # Duplicate Detection Matches indexes
    op.create_index('idx_duplicate_matches_original', 'duplicate_detection_matches', ['original_fingerprint_id'])
    op.create_index('idx_duplicate_matches_duplicate', 'duplicate_detection_matches', ['duplicate_fingerprint_id'])
    op.create_index('idx_duplicate_matches_similarity', 'duplicate_detection_matches', ['similarity_score'])
    op.create_index('idx_duplicate_matches_confidence', 'duplicate_detection_matches', ['match_confidence'])
    op.create_index('idx_duplicate_matches_verification', 'duplicate_detection_matches', ['verification_status'])
    op.create_index('idx_duplicate_matches_algorithm', 'duplicate_detection_matches', ['detection_algorithm'])
    op.create_index('idx_duplicate_matches_false_positive', 'duplicate_detection_matches', ['false_positive_probability'])
    
    # Cross-Platform Monitoring indexes
    op.create_index('idx_platform_monitoring_content_id', 'cross_platform_monitoring', ['content_id'])
    op.create_index('idx_platform_monitoring_platform', 'cross_platform_monitoring', ['platform_name'])
    op.create_index('idx_platform_monitoring_status', 'cross_platform_monitoring', ['scan_status'])
    op.create_index('idx_platform_monitoring_last_scan', 'cross_platform_monitoring', ['last_scan_at'])
    op.create_index('idx_platform_monitoring_next_scan', 'cross_platform_monitoring', ['next_scan_at'])
    op.create_index('idx_platform_monitoring_violations', 'cross_platform_monitoring', ['violations_detected'])
    op.create_index('idx_platform_monitoring_cost', 'cross_platform_monitoring', ['monitoring_cost'])
    
    # Violation Tracking indexes
    op.create_index('idx_violation_tracking_content_id', 'violation_tracking', ['original_content_id'])
    op.create_index('idx_violation_tracking_monitoring', 'violation_tracking', ['monitoring_id'])
    op.create_index('idx_violation_tracking_duplicate', 'violation_tracking', ['duplicate_match_id'])
    op.create_index('idx_violation_tracking_type', 'violation_tracking', ['violation_type'])
    op.create_index('idx_violation_tracking_severity', 'violation_tracking', ['severity'])
    op.create_index('idx_violation_tracking_platform', 'violation_tracking', ['violating_platform'])
    op.create_index('idx_violation_tracking_status', 'violation_tracking', ['status'])
    op.create_index('idx_violation_tracking_detected', 'violation_tracking', ['first_detected_at'])
    op.create_index('idx_violation_tracking_confidence', 'violation_tracking', ['detection_confidence'])
    op.create_index('idx_violation_tracking_financial', 'violation_tracking', ['financial_impact_estimate'])
    
    # Fingerprint Performance Metrics indexes
    op.create_index('idx_fingerprint_metrics_algorithm', 'fingerprint_performance_metrics', ['algorithm'])
    op.create_index('idx_fingerprint_metrics_date', 'fingerprint_performance_metrics', ['metric_date'])
    op.create_index('idx_fingerprint_metrics_precision', 'fingerprint_performance_metrics', ['precision'])
    op.create_index('idx_fingerprint_metrics_recall', 'fingerprint_performance_metrics', ['recall'])
    op.create_index('idx_fingerprint_metrics_f1', 'fingerprint_performance_metrics', ['f1_score'])
    op.create_index('idx_fingerprint_metrics_accuracy', 'fingerprint_performance_metrics', ['accuracy'])
    op.create_index('idx_fingerprint_metrics_cost', 'fingerprint_performance_metrics', ['processing_cost'])
    
    # Similarity Clusters indexes
    op.create_index('idx_similarity_clusters_name', 'similarity_clusters', ['cluster_name'])
    op.create_index('idx_similarity_clusters_algorithm', 'similarity_clusters', ['cluster_algorithm'])
    op.create_index('idx_similarity_clusters_representative', 'similarity_clusters', ['representative_content_id'])
    op.create_index('idx_similarity_clusters_size', 'similarity_clusters', ['cluster_size'])
    op.create_index('idx_similarity_clusters_cohesion', 'similarity_clusters', ['cluster_cohesion'])
    op.create_index('idx_similarity_clusters_updated', 'similarity_clusters', ['last_updated'])
    op.create_index('idx_similarity_clusters_auto_update', 'similarity_clusters', ['auto_update_enabled'])


def downgrade() -> None:
    """Downgrade database schema - Remove advanced content fingerprinting tables."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('similarity_clusters')
    op.drop_table('fingerprint_performance_metrics')
    op.drop_table('violation_tracking')
    op.drop_table('cross_platform_monitoring')
    op.drop_table('duplicate_detection_matches')
    op.drop_table('advanced_content_fingerprints')
    
    # Drop ENUM types
    sa.Enum(name='violation_severity').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='match_confidence').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='fingerprint_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='fingerprint_algorithm').drop(op.get_bind(), checkfirst=True)