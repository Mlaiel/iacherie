"""Advanced intellectual property protection system

Revision ID: g3f4e5d6c7b8
Revises: f2e3d4c5b6a7
Create Date: 2025-09-05 06:30:00.000000

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the advanced intellectual property protection system
with automatic watermarking, copyright detection AI, and legal compliance
tracking for comprehensive content protection.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'g3f4e5d6c7b8'
down_revision = 'f2e3d4c5b6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - Intellectual property protection system."""
    
    # Create copyright claim status enum
    copyright_claim_status_enum = sa.Enum(
        'pending', 'investigating', 'validated', 'disputed', 'resolved', 'rejected',
        'dmca_takedown', 'counter_notice', 'legal_action',
        name='copyright_claim_status'
    )
    
    # Create watermark type enum
    watermark_type_enum = sa.Enum(
        'visible', 'invisible', 'digital_signature', 'audio_fingerprint',
        'video_steganography', 'metadata_embedding', 'blockchain_hash',
        name='watermark_type'
    )
    
    # Create protection level enum
    protection_level_enum = sa.Enum(
        'basic', 'standard', 'enhanced', 'premium', 'enterprise',
        name='protection_level'
    )
    
    # Create legal action type enum
    legal_action_type_enum = sa.Enum(
        'cease_desist', 'dmca_takedown', 'counter_notification', 'arbitration',
        'litigation', 'settlement', 'injunction', 'damages_claim',
        name='legal_action_type'
    )
    
    # Create copyright registration table
    op.create_table('copyright_registrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('registration_number', sa.String(100), unique=True),
        sa.Column('registration_jurisdiction', sa.String(100), nullable=False),
        sa.Column('registration_date', sa.DateTime, nullable=False),
        sa.Column('expiry_date', sa.DateTime),
        sa.Column('copyright_holder', sa.String(200), nullable=False),
        sa.Column('work_title', sa.String(300), nullable=False),
        sa.Column('work_description', sa.Text),
        sa.Column('creation_date', sa.Date, nullable=False),
        sa.Column('publication_date', sa.Date),
        sa.Column('protection_level', protection_level_enum, nullable=False, default='standard'),
        sa.Column('registration_certificate_url', sa.String(500)),
        sa.Column('additional_metadata', postgresql.JSONB),
        sa.Column('is_international', sa.Boolean, nullable=False, default=False),
        sa.Column('legal_representative', sa.String(200)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create watermarking system table
    op.create_table('content_watermarks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('watermark_type', watermark_type_enum, nullable=False),
        sa.Column('watermark_data', postgresql.JSONB, nullable=False),
        sa.Column('watermark_strength', sa.Float, nullable=False, default=0.5),
        sa.Column('extraction_algorithm', sa.String(100), nullable=False),
        sa.Column('robustness_level', sa.Integer, nullable=False, default=5),
        sa.Column('transparency_level', sa.Float, nullable=False, default=0.9),
        sa.Column('embedding_coordinates', postgresql.JSONB),
        sa.Column('verification_hash', sa.String(256), nullable=False),
        sa.Column('tamper_detection_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('automatic_renewal', sa.Boolean, nullable=False, default=True),
        sa.Column('renewal_interval_days', sa.Integer, nullable=False, default=365),
        sa.Column('last_verification', sa.DateTime),
        sa.Column('verification_status', sa.String(20), nullable=False, default='valid'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create copyright violation detection table
    op.create_table('copyright_violation_detection',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('original_content_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user_content.id', ondelete='CASCADE'), nullable=False),
        sa.Column('suspected_violation_url', sa.String(1000), nullable=False),
        sa.Column('detected_platform', sa.String(100), nullable=False),
        sa.Column('similarity_score', sa.Float, nullable=False),
        sa.Column('match_confidence', sa.Float, nullable=False),
        sa.Column('detection_algorithm', sa.String(100), nullable=False),
        sa.Column('violation_type', sa.String(50), nullable=False),
        sa.Column('content_segment_matches', postgresql.JSONB),
        sa.Column('visual_similarity_score', sa.Float),
        sa.Column('audio_similarity_score', sa.Float),
        sa.Column('metadata_similarity_score', sa.Float),
        sa.Column('detection_timestamp', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('verification_status', sa.String(20), nullable=False, default='pending'),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('verified_at', sa.DateTime),
        sa.Column('false_positive', sa.Boolean, nullable=False, default=False),
        sa.Column('action_taken', sa.String(100)),
        sa.Column('evidence_screenshots', postgresql.ARRAY(sa.String(500)), default=[]),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create copyright claims table
    op.create_table('copyright_claims',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('claimant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('violation_detection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('copyright_violation_detection.id', ondelete='CASCADE')),
        sa.Column('claim_number', sa.String(50), unique=True, nullable=False),
        sa.Column('status', copyright_claim_status_enum, nullable=False, default='pending'),
        sa.Column('claim_description', sa.Text, nullable=False),
        sa.Column('evidence_urls', postgresql.ARRAY(sa.String(500)), default=[]),
        sa.Column('damages_claimed', sa.Numeric(15, 2)),
        sa.Column('currency', sa.String(3), default='USD'),
        sa.Column('takedown_requested', sa.Boolean, nullable=False, default=True),
        sa.Column('takedown_url', sa.String(1000)),
        sa.Column('takedown_sent_at', sa.DateTime),
        sa.Column('takedown_response', sa.Text),
        sa.Column('platform_case_number', sa.String(100)),
        sa.Column('legal_representative', sa.String(200)),
        sa.Column('resolution_date', sa.DateTime),
        sa.Column('resolution_details', sa.Text),
        sa.Column('settlement_amount', sa.Numeric(15, 2)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create legal compliance tracking table
    op.create_table('legal_compliance_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('compliance_jurisdiction', sa.String(100), nullable=False),
        sa.Column('compliance_framework', sa.String(100), nullable=False),
        sa.Column('compliance_status', sa.String(20), nullable=False, default='compliant'),
        sa.Column('last_audit_date', sa.DateTime),
        sa.Column('next_audit_due', sa.DateTime),
        sa.Column('compliance_score', sa.Float, nullable=False, default=100.0),
        sa.Column('requirements_met', postgresql.JSONB),
        sa.Column('requirements_missing', postgresql.JSONB),
        sa.Column('remediation_plan', sa.Text),
        sa.Column('remediation_deadline', sa.DateTime),
        sa.Column('compliance_officer', sa.String(200)),
        sa.Column('certification_urls', postgresql.ARRAY(sa.String(500)), default=[]),
        sa.Column('risk_assessment', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create legal actions table
    op.create_table('legal_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('copyright_claim_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('copyright_claims.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action_type', legal_action_type_enum, nullable=False),
        sa.Column('action_status', sa.String(20), nullable=False, default='initiated'),
        sa.Column('jurisdiction', sa.String(100), nullable=False),
        sa.Column('case_number', sa.String(100)),
        sa.Column('court_name', sa.String(200)),
        sa.Column('legal_firm', sa.String(200)),
        sa.Column('attorney_name', sa.String(200)),
        sa.Column('filing_date', sa.DateTime),
        sa.Column('response_deadline', sa.DateTime),
        sa.Column('hearing_date', sa.DateTime),
        sa.Column('estimated_costs', sa.Numeric(15, 2)),
        sa.Column('actual_costs', sa.Numeric(15, 2)),
        sa.Column('outcome', sa.String(100)),
        sa.Column('damages_awarded', sa.Numeric(15, 2)),
        sa.Column('legal_documents', postgresql.ARRAY(sa.String(500)), default=[]),
        sa.Column('notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create performance indexes
    
    # Copyright Registrations indexes
    op.create_index('idx_copyright_reg_user_id', 'copyright_registrations', ['user_id'])
    op.create_index('idx_copyright_reg_content_id', 'copyright_registrations', ['content_id'])
    op.create_index('idx_copyright_reg_number', 'copyright_registrations', ['registration_number'])
    op.create_index('idx_copyright_reg_jurisdiction', 'copyright_registrations', ['registration_jurisdiction'])
    op.create_index('idx_copyright_reg_date', 'copyright_registrations', ['registration_date'])
    op.create_index('idx_copyright_reg_expiry', 'copyright_registrations', ['expiry_date'])
    op.create_index('idx_copyright_reg_protection', 'copyright_registrations', ['protection_level'])
    
    # Content Watermarks indexes
    op.create_index('idx_watermarks_content_id', 'content_watermarks', ['content_id'])
    op.create_index('idx_watermarks_type', 'content_watermarks', ['watermark_type'])
    op.create_index('idx_watermarks_verification', 'content_watermarks', ['verification_status'])
    op.create_index('idx_watermarks_hash', 'content_watermarks', ['verification_hash'])
    op.create_index('idx_watermarks_renewal', 'content_watermarks', ['automatic_renewal', 'renewal_interval_days'])
    op.create_index('idx_watermarks_last_verification', 'content_watermarks', ['last_verification'])
    
    # Copyright Violation Detection indexes
    op.create_index('idx_violation_detection_content_id', 'copyright_violation_detection', ['original_content_id'])
    op.create_index('idx_violation_detection_platform', 'copyright_violation_detection', ['detected_platform'])
    op.create_index('idx_violation_detection_similarity', 'copyright_violation_detection', ['similarity_score'])
    op.create_index('idx_violation_detection_confidence', 'copyright_violation_detection', ['match_confidence'])
    op.create_index('idx_violation_detection_timestamp', 'copyright_violation_detection', ['detection_timestamp'])
    op.create_index('idx_violation_detection_verification', 'copyright_violation_detection', ['verification_status'])
    op.create_index('idx_violation_detection_false_positive', 'copyright_violation_detection', ['false_positive'])
    
    # Copyright Claims indexes
    op.create_index('idx_copyright_claims_claimant', 'copyright_claims', ['claimant_id'])
    op.create_index('idx_copyright_claims_violation', 'copyright_claims', ['violation_detection_id'])
    op.create_index('idx_copyright_claims_number', 'copyright_claims', ['claim_number'])
    op.create_index('idx_copyright_claims_status', 'copyright_claims', ['status'])
    op.create_index('idx_copyright_claims_takedown', 'copyright_claims', ['takedown_requested'])
    op.create_index('idx_copyright_claims_resolution', 'copyright_claims', ['resolution_date'])
    op.create_index('idx_copyright_claims_damages', 'copyright_claims', ['damages_claimed'])
    
    # Legal Compliance Tracking indexes
    op.create_index('idx_compliance_user_id', 'legal_compliance_tracking', ['user_id'])
    op.create_index('idx_compliance_jurisdiction', 'legal_compliance_tracking', ['compliance_jurisdiction'])
    op.create_index('idx_compliance_framework', 'legal_compliance_tracking', ['compliance_framework'])
    op.create_index('idx_compliance_status', 'legal_compliance_tracking', ['compliance_status'])
    op.create_index('idx_compliance_audit_date', 'legal_compliance_tracking', ['last_audit_date'])
    op.create_index('idx_compliance_audit_due', 'legal_compliance_tracking', ['next_audit_due'])
    op.create_index('idx_compliance_score', 'legal_compliance_tracking', ['compliance_score'])
    
    # Legal Actions indexes
    op.create_index('idx_legal_actions_claim_id', 'legal_actions', ['copyright_claim_id'])
    op.create_index('idx_legal_actions_type', 'legal_actions', ['action_type'])
    op.create_index('idx_legal_actions_status', 'legal_actions', ['action_status'])
    op.create_index('idx_legal_actions_jurisdiction', 'legal_actions', ['jurisdiction'])
    op.create_index('idx_legal_actions_case_number', 'legal_actions', ['case_number'])
    op.create_index('idx_legal_actions_filing_date', 'legal_actions', ['filing_date'])
    op.create_index('idx_legal_actions_costs', 'legal_actions', ['estimated_costs', 'actual_costs'])


def downgrade() -> None:
    """Downgrade database schema - Remove intellectual property protection tables."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('legal_actions')
    op.drop_table('legal_compliance_tracking')
    op.drop_table('copyright_claims')
    op.drop_table('copyright_violation_detection')
    op.drop_table('content_watermarks')
    op.drop_table('copyright_registrations')
    
    # Drop ENUM types
    sa.Enum(name='legal_action_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='protection_level').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='watermark_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='copyright_claim_status').drop(op.get_bind(), checkfirst=True)