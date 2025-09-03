"""Initial database schema for Ainflue platform

Revision ID: d21b3c27ee2c
Revises: 
Create Date: 2025-09-03 03:06:32.756749

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This migration creates the complete database schema for the Ainflue platform including:
- Core user and content management tables
- Content fingerprinting and protection systems
- Revenue tracking and monetization
- Platform integrations and analytics
- Audit logging and security features
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'd21b3c27ee2c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema - Create all core tables."""
    
    # Create ENUM types (for PostgreSQL compatibility)
    content_type_enum = sa.Enum(
        'audio', 'video', 'image', 'text', 'podcast', 'livestream', 'story', 'reel',
        name='content_type'
    )
    
    creator_type_enum = sa.Enum(
        'musician', 'podcaster', 'influencer', 'artist', 'writer', 'producer',
        name='creator_type'
    )
    
    protection_status_enum = sa.Enum(
        'active', 'inactive', 'monitoring', 'violation_detected', 'legal_action',
        name='protection_status'
    )
    
    alert_severity_enum = sa.Enum(
        'low', 'medium', 'high', 'critical',
        name='alert_severity'
    )
    
    # Create core tables
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(50), nullable=False),
        sa.Column('last_name', sa.String(50), nullable=False),
        sa.Column('creator_type', creator_type_enum, nullable=False),
        sa.Column('tenant_id', sa.String(16), nullable=False),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('subscription_tier', sa.String(20), default='free'),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # User Content table
    op.create_table(
        'user_content',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(32), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('content_type', content_type_enum, nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_size', sa.BigInteger),
        sa.Column('duration', sa.Float),
        sa.Column('file_path', sa.String(500)),
        sa.Column('thumbnail_path', sa.String(500)),
        sa.Column('metadata', sa.JSON),
        sa.Column('privacy_level', sa.String(20), default='private'),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Content Fingerprints table
    op.create_table(
        'content_fingerprints',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('content_id', sa.String(36), sa.ForeignKey('user_content.id'), nullable=False),
        sa.Column('fingerprint_hash', sa.String(64), nullable=False),
        sa.Column('algorithm', sa.String(50), nullable=False),
        sa.Column('fingerprint_data', sa.LargeBinary),
        sa.Column('metadata', sa.JSON),
        sa.Column('confidence_score', sa.Float, default=0.0),
        sa.Column('processing_status', sa.String(20), default='pending'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Protection Alerts table
    op.create_table(
        'protection_alerts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('content_id', sa.String(36), sa.ForeignKey('user_content.id'), nullable=False),
        sa.Column('user_id', sa.String(32), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('severity', alert_severity_enum, nullable=False),
        sa.Column('platform', sa.String(50)),
        sa.Column('violation_url', sa.String(500)),
        sa.Column('detection_method', sa.String(50)),
        sa.Column('confidence_score', sa.Float, default=0.0),
        sa.Column('status', protection_status_enum, default='active'),
        sa.Column('automated_action', sa.String(100)),
        sa.Column('evidence_data', sa.JSON),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Revenue Tracking table
    op.create_table(
        'revenue_tracking',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(32), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content_id', sa.String(36), sa.ForeignKey('user_content.id')),
        sa.Column('revenue_type', sa.String(50), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), default='USD'),
        sa.Column('platform', sa.String(50)),
        sa.Column('transaction_id', sa.String(100)),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('tax_amount', sa.Numeric(10, 2), default=0.0),
        sa.Column('net_amount', sa.Numeric(10, 2)),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Platform Integrations table
    op.create_table(
        'platform_integrations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(32), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('platform_user_id', sa.String(100)),
        sa.Column('access_token', sa.String(500)),
        sa.Column('refresh_token', sa.String(500)),
        sa.Column('token_expires_at', sa.DateTime),
        sa.Column('integration_status', sa.String(20), default='active'),
        sa.Column('permissions', sa.JSON),
        sa.Column('last_sync', sa.DateTime),
        sa.Column('sync_status', sa.String(20)),
        sa.Column('error_message', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Audit Logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(32), sa.ForeignKey('users.id')),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(36)),
        sa.Column('details', sa.JSON),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('session_id', sa.String(100)),
        sa.Column('security_classification', sa.String(20), default='normal'),
        sa.Column('compliance_category', sa.String(50)),
        sa.Column('log_level', sa.String(10), default='info'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )
    
    # Creator Profiles table
    op.create_table(
        'creator_profiles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(32), sa.ForeignKey('users.id'), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100)),
        sa.Column('bio', sa.Text),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('banner_url', sa.String(500)),
        sa.Column('website', sa.String(255)),
        sa.Column('social_links', sa.JSON),
        sa.Column('genres', sa.JSON),
        sa.Column('skills', sa.JSON),
        sa.Column('collaboration_preferences', sa.JSON),
        sa.Column('audience_demographics', sa.JSON),
        sa.Column('content_statistics', sa.JSON),
        sa.Column('verification_status', sa.String(20), default='unverified'),
        sa.Column('reputation_score', sa.Float, default=0.0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create performance indexes
    
    # User indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('idx_users_creator_type', 'users', ['creator_type'])
    op.create_index('idx_users_subscription_tier', 'users', ['subscription_tier'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # User Content indexes
    op.create_index('idx_user_content_user_id', 'user_content', ['user_id'])
    op.create_index('idx_user_content_type', 'user_content', ['content_type'])
    op.create_index('idx_user_content_status', 'user_content', ['status'])
    op.create_index('idx_user_content_created_at', 'user_content', ['created_at'])
    op.create_index('idx_user_content_user_type', 'user_content', ['user_id', 'content_type'])
    
    # Content Fingerprints indexes
    op.create_index('idx_fingerprints_content_id', 'content_fingerprints', ['content_id'])
    op.create_index('idx_fingerprints_hash', 'content_fingerprints', ['fingerprint_hash'])
    op.create_index('idx_fingerprints_algorithm', 'content_fingerprints', ['algorithm'])
    op.create_index('idx_fingerprints_status', 'content_fingerprints', ['processing_status'])
    op.create_index('idx_fingerprints_confidence', 'content_fingerprints', ['confidence_score'])
    
    # Protection Alerts indexes
    op.create_index('idx_alerts_content_id', 'protection_alerts', ['content_id'])
    op.create_index('idx_alerts_user_id', 'protection_alerts', ['user_id'])
    op.create_index('idx_alerts_severity', 'protection_alerts', ['severity'])
    op.create_index('idx_alerts_status', 'protection_alerts', ['status'])
    op.create_index('idx_alerts_platform', 'protection_alerts', ['platform'])
    op.create_index('idx_alerts_created_at', 'protection_alerts', ['created_at'])
    op.create_index('idx_alerts_user_status', 'protection_alerts', ['user_id', 'status'])
    
    # Revenue Tracking indexes
    op.create_index('idx_revenue_user_id', 'revenue_tracking', ['user_id'])
    op.create_index('idx_revenue_content_id', 'revenue_tracking', ['content_id'])
    op.create_index('idx_revenue_type', 'revenue_tracking', ['revenue_type'])
    op.create_index('idx_revenue_status', 'revenue_tracking', ['status'])
    op.create_index('idx_revenue_platform', 'revenue_tracking', ['platform'])
    op.create_index('idx_revenue_created_at', 'revenue_tracking', ['created_at'])
    op.create_index('idx_revenue_user_platform', 'revenue_tracking', ['user_id', 'platform'])
    
    # Platform Integrations indexes
    op.create_index('idx_integrations_user_id', 'platform_integrations', ['user_id'])
    op.create_index('idx_integrations_platform', 'platform_integrations', ['platform'])
    op.create_index('idx_integrations_status', 'platform_integrations', ['integration_status'])
    op.create_index('idx_integrations_last_sync', 'platform_integrations', ['last_sync'])
    op.create_index('idx_integrations_user_platform', 'platform_integrations', ['user_id', 'platform'])
    
    # Audit Logs indexes
    op.create_index('idx_audit_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_action_type', 'audit_logs', ['action_type'])
    op.create_index('idx_audit_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('idx_audit_entity_id', 'audit_logs', ['entity_id'])
    op.create_index('idx_audit_created_at', 'audit_logs', ['created_at'])
    op.create_index('idx_audit_security_class', 'audit_logs', ['security_classification'])
    op.create_index('idx_audit_compliance', 'audit_logs', ['compliance_category'])
    
    # Creator Profiles indexes
    op.create_index('idx_creator_profiles_user_id', 'creator_profiles', ['user_id'])
    op.create_index('idx_creator_profiles_verification', 'creator_profiles', ['verification_status'])
    op.create_index('idx_creator_profiles_reputation', 'creator_profiles', ['reputation_score'])


def downgrade() -> None:
    """Downgrade database schema - Drop all tables."""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('creator_profiles')
    op.drop_table('audit_logs')
    op.drop_table('platform_integrations')
    op.drop_table('revenue_tracking')
    op.drop_table('protection_alerts')
    op.drop_table('content_fingerprints')
    op.drop_table('user_content')
    op.drop_table('users')
    
    # Drop ENUM types (PostgreSQL specific - SQLite will ignore)
    try:
        sa.Enum(name='alert_severity').drop(op.get_bind(), checkfirst=True)
        sa.Enum(name='protection_status').drop(op.get_bind(), checkfirst=True)
        sa.Enum(name='creator_type').drop(op.get_bind(), checkfirst=True)
        sa.Enum(name='content_type').drop(op.get_bind(), checkfirst=True)
    except:
        pass  # SQLite doesn't support ENUMs, so this will fail gracefully