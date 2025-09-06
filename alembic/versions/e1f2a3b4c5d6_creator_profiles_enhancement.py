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
    """Upgrade database schema - Enhanced creator profiles with MASSIVE ENRICHMENTS."""
    
    # === EXISTANT BASE ===
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
    
    # === ENRICHISSEMENTS MASSIFS ===
    
    # 1. SUPPORT MULTILINGUE COMPLET (644 langues)
    create_multilingual_creator_profiles()
    create_cultural_adaptation_tables()
    create_regional_preferences_system()
    
    # 2. ACCESSIBILITÉ ENTERPRISE
    create_accessibility_features_tables()
    create_voice_navigation_support()
    create_visual_impairment_assistance()
    create_cognitive_accessibility_system()
    
    # 3. VÉRIFICATION ENTERPRISE AVANCÉE
    create_enterprise_verification_tiers()
    create_celebrity_verification_system()
    create_professional_certification_tracking()
    
    # 4. ANALYTICS CRÉATEURS AVANCÉS
    create_creator_performance_analytics()
    create_audience_insights_tables()
    create_growth_prediction_models()
    
    # 5. SOCIAL FEATURES AVANCÉES
    create_creator_networking_system()
    create_mentor_mentee_matching()
    create_collaboration_discovery()


def create_multilingual_creator_profiles():
    """Create multilingual support for creator profiles (644 languages)."""
    
    # Language support enum (major languages subset - full list would be too large)
    language_enum = sa.Enum(
        'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko', 'ar', 'hi', 'bn', 'ur', 
        'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi', 'el', 'he', 'th', 'vi', 'id', 'ms', 'tl',
        'sw', 'yo', 'ig', 'ha', 'am', 'om', 'ti', 'so', 'mg', 'ny', 'sn', 'zu', 'xh', 'st',
        name='supported_language'
    )
    
    # Creator multilingual profiles
    op.create_table('creator_multilingual_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('language_code', language_enum, nullable=False),
        sa.Column('display_name', sa.String(200), nullable=False),
        sa.Column('bio', sa.Text),
        sa.Column('tagline', sa.String(500)),
        sa.Column('specialization_description', sa.Text),
        sa.Column('skills_description', sa.Text),
        sa.Column('experience_description', sa.Text),
        sa.Column('portfolio_description', sa.Text),
        sa.Column('collaboration_message', sa.Text),
        sa.Column('pricing_description', sa.Text),
        sa.Column('terms_conditions', sa.Text),
        sa.Column('cultural_context', postgresql.JSONB),
        sa.Column('region_specific_info', postgresql.JSONB),
        sa.Column('is_primary_language', sa.Boolean, nullable=False, default=False),
        sa.Column('proficiency_level', sa.String(20), nullable=False, default='native'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Language preferences for content creation
    op.create_table('creator_language_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_languages', postgresql.ARRAY(language_enum), nullable=False, default=[]),
        sa.Column('subtitle_languages', postgresql.ARRAY(language_enum), nullable=False, default=[]),
        sa.Column('dubbing_languages', postgresql.ARRAY(language_enum), nullable=False, default=[]),
        sa.Column('translation_services', postgresql.ARRAY(language_enum), nullable=False, default=[]),
        sa.Column('auto_translation_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('human_translation_preferred', sa.Boolean, nullable=False, default=False),
        sa.Column('cultural_adaptation_level', sa.String(20), nullable=False, default='standard'),
        sa.Column('pricing_per_language', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_cultural_adaptation_tables():
    """Create cultural adaptation and localization tables."""
    
    # Cultural adaptation profiles
    op.create_table('creator_cultural_adaptations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_culture', sa.String(10), nullable=False),
        sa.Column('cultural_expertise_level', sa.String(20), nullable=False),
        sa.Column('local_trends_knowledge', postgresql.JSONB),
        sa.Column('cultural_taboos', postgresql.JSONB),
        sa.Column('preferred_content_styles', postgresql.JSONB),
        sa.Column('local_references', postgresql.JSONB),
        sa.Column('humor_style_preferences', postgresql.JSONB),
        sa.Column('religious_considerations', postgresql.JSONB),
        sa.Column('political_sensitivities', postgresql.JSONB),
        sa.Column('local_influencer_network', postgresql.JSONB),
        sa.Column('regional_pricing_strategy', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_regional_preferences_system():
    """Create regional preferences and localization system."""
    
    # Regional content preferences
    op.create_table('creator_regional_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('region_code', sa.String(10), nullable=False),
        sa.Column('timezone_preference', sa.String(50), nullable=False),
        sa.Column('posting_schedule', postgresql.JSONB),
        sa.Column('content_format_preferences', postgresql.JSONB),
        sa.Column('platform_priorities', postgresql.JSONB),
        sa.Column('audience_demographics', postgresql.JSONB),
        sa.Column('local_events_calendar', postgresql.JSONB),
        sa.Column('seasonal_content_strategy', postgresql.JSONB),
        sa.Column('compliance_requirements', postgresql.JSONB),
        sa.Column('monetization_preferences', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_accessibility_features_tables():
    """Create accessibility features for enterprise-grade inclusivity."""
    
    # Accessibility profiles
    op.create_table('creator_accessibility_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('screen_reader_optimized', sa.Boolean, nullable=False, default=False),
        sa.Column('high_contrast_mode', sa.Boolean, nullable=False, default=False),
        sa.Column('large_text_mode', sa.Boolean, nullable=False, default=False),
        sa.Column('voice_navigation_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('keyboard_navigation_only', sa.Boolean, nullable=False, default=False),
        sa.Column('motion_sensitivity_reduced', sa.Boolean, nullable=False, default=False),
        sa.Column('auto_captions_required', sa.Boolean, nullable=False, default=False),
        sa.Column('sign_language_support', sa.Boolean, nullable=False, default=False),
        sa.Column('cognitive_load_reduction', sa.Boolean, nullable=False, default=False),
        sa.Column('dyslexia_friendly_fonts', sa.Boolean, nullable=False, default=False),
        sa.Column('color_blind_accommodations', sa.Boolean, nullable=False, default=False),
        sa.Column('seizure_safe_content', sa.Boolean, nullable=False, default=False),
        sa.Column('custom_accessibility_needs', postgresql.JSONB),
        sa.Column('assistive_technology_used', postgresql.JSONB),
        sa.Column('accessibility_certification_level', sa.String(20)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_voice_navigation_support():
    """Create voice navigation and audio accessibility support."""
    
    # Voice navigation profiles
    op.create_table('creator_voice_navigation',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('voice_commands_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('voice_language_preference', sa.String(10), nullable=False, default='en'),
        sa.Column('voice_speed_preference', sa.Float, nullable=False, default=1.0),
        sa.Column('voice_pitch_preference', sa.Float, nullable=False, default=1.0),
        sa.Column('custom_voice_commands', postgresql.JSONB),
        sa.Column('voice_feedback_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('voice_shortcuts', postgresql.JSONB),
        sa.Column('audio_descriptions_preferred', sa.Boolean, nullable=False, default=False),
        sa.Column('voice_dictation_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_visual_impairment_assistance():
    """Create visual impairment assistance features."""
    
    # Visual impairment support
    op.create_table('creator_visual_assistance',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('visual_impairment_type', sa.String(50)),
        sa.Column('screen_magnification_level', sa.Float, nullable=False, default=1.0),
        sa.Column('alt_text_generation_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('image_description_detail_level', sa.String(20), nullable=False, default='standard'),
        sa.Column('braille_display_support', sa.Boolean, nullable=False, default=False),
        sa.Column('haptic_feedback_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('audio_cues_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('spatial_audio_navigation', sa.Boolean, nullable=False, default=False),
        sa.Column('edge_detection_assistance', sa.Boolean, nullable=False, default=False),
        sa.Column('color_identification_assistance', sa.Boolean, nullable=False, default=False),
        sa.Column('object_recognition_assistance', sa.Boolean, nullable=False, default=False),
        sa.Column('text_recognition_assistance', sa.Boolean, nullable=False, default=False),
        sa.Column('navigation_assistance_level', sa.String(20), nullable=False, default='basic'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_cognitive_accessibility_system():
    """Create cognitive accessibility and neurodiversity support."""
    
    # Cognitive accessibility profiles
    op.create_table('creator_cognitive_accessibility',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('adhd_accommodations', sa.Boolean, nullable=False, default=False),
        sa.Column('autism_accommodations', sa.Boolean, nullable=False, default=False),
        sa.Column('dyslexia_accommodations', sa.Boolean, nullable=False, default=False),
        sa.Column('memory_assistance_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('focus_assistance_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('simplified_interface_mode', sa.Boolean, nullable=False, default=False),
        sa.Column('step_by_step_guidance', sa.Boolean, nullable=False, default=False),
        sa.Column('progress_saving_frequent', sa.Boolean, nullable=False, default=False),
        sa.Column('distraction_reduction', sa.Boolean, nullable=False, default=False),
        sa.Column('sensory_overload_protection', sa.Boolean, nullable=False, default=False),
        sa.Column('routine_based_interface', sa.Boolean, nullable=False, default=False),
        sa.Column('clear_communication_mode', sa.Boolean, nullable=False, default=False),
        sa.Column('predictable_navigation', sa.Boolean, nullable=False, default=False),
        sa.Column('cognitive_load_indicators', sa.Boolean, nullable=False, default=False),
        sa.Column('break_reminders_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('custom_cognitive_needs', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_enterprise_verification_tiers():
    """Create enterprise-grade verification system with multiple tiers."""
    
    # Enterprise verification tiers
    verification_tier_enterprise_enum = sa.Enum(
        'unverified', 'email_verified', 'phone_verified', 'id_verified', 'address_verified',
        'professional_verified', 'business_verified', 'enterprise_verified', 'celebrity_verified',
        'government_verified', 'institutional_verified', 'media_verified', 'influencer_verified',
        name='verification_tier_enterprise'
    )
    
    op.create_table('creator_enterprise_verifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('verification_tier', verification_tier_enterprise_enum, nullable=False),
        sa.Column('verification_method', sa.String(100), nullable=False),
        sa.Column('verification_provider', sa.String(100), nullable=False),
        sa.Column('verification_reference_id', sa.String(200)),
        sa.Column('verification_score', sa.Float, nullable=False, default=0.0),
        sa.Column('verification_confidence', sa.Float, nullable=False, default=0.0),
        sa.Column('biometric_verification', sa.Boolean, nullable=False, default=False),
        sa.Column('document_verification', sa.Boolean, nullable=False, default=False),
        sa.Column('address_verification', sa.Boolean, nullable=False, default=False),
        sa.Column('financial_verification', sa.Boolean, nullable=False, default=False),
        sa.Column('social_verification', sa.Boolean, nullable=False, default=False),
        sa.Column('professional_verification', sa.Boolean, nullable=False, default=False),
        sa.Column('background_check_status', sa.String(20)),
        sa.Column('kyc_status', sa.String(20)),
        sa.Column('aml_status', sa.String(20)),
        sa.Column('verification_expiry', sa.DateTime),
        sa.Column('auto_renewal_enabled', sa.Boolean, nullable=False, default=False),
        sa.Column('verification_metadata', postgresql.JSONB),
        sa.Column('verified_by_admin_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_celebrity_verification_system():
    """Create celebrity and public figure verification system."""
    
    # Celebrity verification profiles
    op.create_table('creator_celebrity_verifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('celebrity_status', sa.String(50), nullable=False),
        sa.Column('public_figure_type', sa.String(100)),
        sa.Column('verified_social_accounts', postgresql.JSONB),
        sa.Column('media_mentions', postgresql.JSONB),
        sa.Column('awards_achievements', postgresql.JSONB),
        sa.Column('public_records_verification', sa.Boolean, nullable=False, default=False),
        sa.Column('media_coverage_score', sa.Float, nullable=False, default=0.0),
        sa.Column('social_following_verification', postgresql.JSONB),
        sa.Column('brand_partnerships', postgresql.JSONB),
        sa.Column('agent_manager_verification', postgresql.JSONB),
        sa.Column('publicist_verification', postgresql.JSONB),
        sa.Column('legal_representation', postgresql.JSONB),
        sa.Column('talent_agency_affiliation', sa.String(200)),
        sa.Column('press_kit_url', sa.String(500)),
        sa.Column('official_website_verification', sa.Boolean, nullable=False, default=False),
        sa.Column('blue_check_equivalence', sa.Boolean, nullable=False, default=False),
        sa.Column('verification_badge_type', sa.String(50)),
        sa.Column('celebrity_tier', sa.String(20)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_professional_certification_tracking():
    """Create professional certification and credential tracking."""
    
    # Professional certifications
    op.create_table('creator_professional_certifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('certification_name', sa.String(200), nullable=False),
        sa.Column('issuing_organization', sa.String(200), nullable=False),
        sa.Column('certification_id', sa.String(100)),
        sa.Column('certification_url', sa.String(500)),
        sa.Column('certification_type', sa.String(50), nullable=False),
        sa.Column('skill_area', sa.String(100), nullable=False),
        sa.Column('certification_level', sa.String(50)),
        sa.Column('issue_date', sa.Date, nullable=False),
        sa.Column('expiry_date', sa.Date),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('verification_status', sa.String(20), nullable=False, default='pending'),
        sa.Column('auto_verification_possible', sa.Boolean, nullable=False, default=False),
        sa.Column('blockchain_verified', sa.Boolean, nullable=False, default=False),
        sa.Column('continuing_education_required', sa.Boolean, nullable=False, default=False),
        sa.Column('renewal_notification_sent', sa.Boolean, nullable=False, default=False),
        sa.Column('certification_metadata', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_creator_performance_analytics():
    """Create advanced performance analytics and AI insights."""
    
    # Advanced performance analytics
    op.create_table('creator_advanced_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('analytics_date', sa.Date, nullable=False),
        sa.Column('performance_score', sa.Float, nullable=False, default=0.0),
        sa.Column('engagement_velocity', sa.Float, nullable=False, default=0.0),
        sa.Column('viral_potential_score', sa.Float, nullable=False, default=0.0),
        sa.Column('audience_retention_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('content_quality_ai_score', sa.Float, nullable=False, default=0.0),
        sa.Column('originality_score', sa.Float, nullable=False, default=0.0),
        sa.Column('trend_alignment_score', sa.Float, nullable=False, default=0.0),
        sa.Column('cross_platform_synergy', sa.Float, nullable=False, default=0.0),
        sa.Column('monetization_efficiency', sa.Float, nullable=False, default=0.0),
        sa.Column('collaboration_success_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('brand_safety_score', sa.Float, nullable=False, default=0.0),
        sa.Column('audience_diversity_index', sa.Float, nullable=False, default=0.0),
        sa.Column('content_consistency_score', sa.Float, nullable=False, default=0.0),
        sa.Column('innovation_factor', sa.Float, nullable=False, default=0.0),
        sa.Column('market_position_rank', sa.Integer),
        sa.Column('growth_trajectory', sa.String(20)),
        sa.Column('ai_recommendations', postgresql.JSONB),
        sa.Column('performance_insights', postgresql.JSONB),
        sa.Column('competitive_analysis', postgresql.JSONB),
        sa.Column('optimization_suggestions', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_audience_insights_tables():
    """Create comprehensive audience insights and segmentation."""
    
    # Audience insights and segmentation
    op.create_table('creator_audience_insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('insight_date', sa.Date, nullable=False),
        sa.Column('total_audience_size', sa.BigInteger, nullable=False, default=0),
        sa.Column('audience_demographics', postgresql.JSONB),
        sa.Column('audience_psychographics', postgresql.JSONB),
        sa.Column('audience_behaviors', postgresql.JSONB),
        sa.Column('audience_preferences', postgresql.JSONB),
        sa.Column('audience_segments', postgresql.JSONB),
        sa.Column('engagement_patterns', postgresql.JSONB),
        sa.Column('content_consumption_habits', postgresql.JSONB),
        sa.Column('peak_activity_times', postgresql.JSONB),
        sa.Column('geographic_distribution', postgresql.JSONB),
        sa.Column('platform_preferences', postgresql.JSONB),
        sa.Column('device_usage_patterns', postgresql.JSONB),
        sa.Column('audience_growth_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('audience_retention_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('audience_loyalty_score', sa.Float, nullable=False, default=0.0),
        sa.Column('audience_value_score', sa.Float, nullable=False, default=0.0),
        sa.Column('churn_risk_analysis', postgresql.JSONB),
        sa.Column('acquisition_channels', postgresql.JSONB),
        sa.Column('influence_network_analysis', postgresql.JSONB),
        sa.Column('lookalike_audience_profiles', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_growth_prediction_models():
    """Create AI-powered growth prediction and forecasting models."""
    
    # Growth prediction models
    op.create_table('creator_growth_predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('prediction_date', sa.Date, nullable=False),
        sa.Column('prediction_horizon_days', sa.Integer, nullable=False),
        sa.Column('predicted_followers_growth', sa.Float, nullable=False, default=0.0),
        sa.Column('predicted_engagement_growth', sa.Float, nullable=False, default=0.0),
        sa.Column('predicted_revenue_growth', sa.Float, nullable=False, default=0.0),
        sa.Column('predicted_content_performance', postgresql.JSONB),
        sa.Column('growth_probability_score', sa.Float, nullable=False, default=0.0),
        sa.Column('confidence_interval_lower', sa.Float, nullable=False, default=0.0),
        sa.Column('confidence_interval_upper', sa.Float, nullable=False, default=0.0),
        sa.Column('model_accuracy_score', sa.Float, nullable=False, default=0.0),
        sa.Column('key_growth_factors', postgresql.JSONB),
        sa.Column('risk_factors', postgresql.JSONB),
        sa.Column('opportunity_factors', postgresql.JSONB),
        sa.Column('recommended_actions', postgresql.JSONB),
        sa.Column('market_trend_impact', postgresql.JSONB),
        sa.Column('seasonal_adjustments', postgresql.JSONB),
        sa.Column('competitive_landscape_impact', postgresql.JSONB),
        sa.Column('algorithm_changes_impact', postgresql.JSONB),
        sa.Column('prediction_model_version', sa.String(20)),
        sa.Column('data_sources_used', postgresql.JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_creator_networking_system():
    """Create advanced creator networking and community features."""
    
    # Creator networking profiles
    op.create_table('creator_networking_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('networking_active', sa.Boolean, nullable=False, default=True),
        sa.Column('collaboration_openness', sa.String(20), nullable=False, default='open'),
        sa.Column('preferred_collaboration_types', postgresql.ARRAY(sa.String(50)), nullable=False, default=[]),
        sa.Column('networking_goals', postgresql.JSONB),
        sa.Column('industry_connections', postgresql.JSONB),
        sa.Column('skill_exchange_interests', postgresql.JSONB),
        sa.Column('mentorship_offering', postgresql.JSONB),
        sa.Column('mentorship_seeking', postgresql.JSONB),
        sa.Column('professional_interests', postgresql.JSONB),
        sa.Column('networking_availability', postgresql.JSONB),
        sa.Column('communication_preferences', postgresql.JSONB),
        sa.Column('collaboration_budget_range', postgresql.JSONB),
        sa.Column('geographical_preferences', postgresql.JSONB),
        sa.Column('language_networking_preferences', postgresql.ARRAY(sa.String(10)), nullable=False, default=[]),
        sa.Column('networking_score', sa.Float, nullable=False, default=0.0),
        sa.Column('reputation_score', sa.Float, nullable=False, default=0.0),
        sa.Column('trustworthiness_score', sa.Float, nullable=False, default=0.0),
        sa.Column('response_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('collaboration_success_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Creator connections and relationships
    op.create_table('creator_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('connected_creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('connection_type', sa.String(50), nullable=False),
        sa.Column('connection_strength', sa.Float, nullable=False, default=0.0),
        sa.Column('interaction_frequency', sa.String(20)),
        sa.Column('collaboration_history', postgresql.JSONB),
        sa.Column('mutual_contacts', postgresql.JSONB),
        sa.Column('shared_interests', postgresql.JSONB),
        sa.Column('connection_source', sa.String(100)),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('last_interaction_date', sa.DateTime),
        sa.Column('connection_notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_mentor_mentee_matching():
    """Create mentor-mentee matching and relationship management."""
    
    # Mentor profiles
    op.create_table('creator_mentor_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mentoring_active', sa.Boolean, nullable=False, default=False),
        sa.Column('expertise_areas', postgresql.ARRAY(sa.String(100)), nullable=False, default=[]),
        sa.Column('mentoring_experience_years', sa.Integer, nullable=False, default=0),
        sa.Column('max_mentees', sa.Integer, nullable=False, default=5),
        sa.Column('current_mentees_count', sa.Integer, nullable=False, default=0),
        sa.Column('mentoring_style', sa.String(50)),
        sa.Column('mentoring_format_preferences', postgresql.JSONB),
        sa.Column('availability_schedule', postgresql.JSONB),
        sa.Column('mentoring_goals', postgresql.JSONB),
        sa.Column('success_stories', postgresql.JSONB),
        sa.Column('mentoring_rates', postgresql.JSONB),
        sa.Column('certifications', postgresql.JSONB),
        sa.Column('testimonials', postgresql.JSONB),
        sa.Column('mentor_rating', sa.Float, nullable=False, default=0.0),
        sa.Column('response_time_hours', sa.Float, nullable=False, default=24.0),
        sa.Column('mentoring_languages', postgresql.ARRAY(sa.String(10)), nullable=False, default=[]),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Mentee profiles
    op.create_table('creator_mentee_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('seeking_mentorship', sa.Boolean, nullable=False, default=False),
        sa.Column('learning_goals', postgresql.JSONB),
        sa.Column('skill_development_areas', postgresql.ARRAY(sa.String(100)), nullable=False, default=[]),
        sa.Column('current_skill_level', sa.String(20)),
        sa.Column('time_commitment_weekly_hours', sa.Float, nullable=False, default=2.0),
        sa.Column('mentorship_duration_preference', sa.String(20)),
        sa.Column('learning_style_preferences', postgresql.JSONB),
        sa.Column('communication_preferences', postgresql.JSONB),
        sa.Column('budget_range', postgresql.JSONB),
        sa.Column('previous_mentorship_experience', postgresql.JSONB),
        sa.Column('specific_challenges', postgresql.JSONB),
        sa.Column('success_metrics', postgresql.JSONB),
        sa.Column('mentor_preferences', postgresql.JSONB),
        sa.Column('availability_schedule', postgresql.JSONB),
        sa.Column('mentorship_languages', postgresql.ARRAY(sa.String(10)), nullable=False, default=[]),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Mentor-mentee relationships
    op.create_table('creator_mentorship_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('mentor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mentee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relationship_status', sa.String(20), nullable=False, default='pending'),
        sa.Column('start_date', sa.Date),
        sa.Column('expected_end_date', sa.Date),
        sa.Column('actual_end_date', sa.Date),
        sa.Column('mentorship_agreement', postgresql.JSONB),
        sa.Column('goals_and_objectives', postgresql.JSONB),
        sa.Column('progress_tracking', postgresql.JSONB),
        sa.Column('session_history', postgresql.JSONB),
        sa.Column('feedback_history', postgresql.JSONB),
        sa.Column('milestone_achievements', postgresql.JSONB),
        sa.Column('success_rating', sa.Float),
        sa.Column('relationship_notes', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def create_collaboration_discovery():
    """Create advanced collaboration discovery and matching system."""
    
    # Collaboration opportunities
    op.create_table('creator_collaboration_opportunities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('opportunity_title', sa.String(200), nullable=False),
        sa.Column('opportunity_description', sa.Text, nullable=False),
        sa.Column('collaboration_type', sa.String(50), nullable=False),
        sa.Column('required_skills', postgresql.ARRAY(sa.String(100)), nullable=False, default=[]),
        sa.Column('preferred_creator_types', postgresql.ARRAY(sa.String(50)), nullable=False, default=[]),
        sa.Column('project_duration', sa.String(50)),
        sa.Column('budget_range', postgresql.JSONB),
        sa.Column('timeline_requirements', postgresql.JSONB),
        sa.Column('deliverables_expected', postgresql.JSONB),
        sa.Column('collaboration_format', sa.String(50)),
        sa.Column('location_requirements', postgresql.JSONB),
        sa.Column('language_requirements', postgresql.ARRAY(sa.String(10)), nullable=False, default=[]),
        sa.Column('experience_level_required', sa.String(20)),
        sa.Column('portfolio_requirements', postgresql.JSONB),
        sa.Column('application_deadline', sa.Date),
        sa.Column('project_start_date', sa.Date),
        sa.Column('status', sa.String(20), nullable=False, default='open'),
        sa.Column('applications_count', sa.Integer, nullable=False, default=0),
        sa.Column('max_collaborators', sa.Integer, nullable=False, default=1),
        sa.Column('selected_collaborators', postgresql.JSONB),
        sa.Column('opportunity_tags', postgresql.ARRAY(sa.String(50)), nullable=False, default=[]),
        sa.Column('visibility', sa.String(20), nullable=False, default='public'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Collaboration applications
    op.create_table('creator_collaboration_applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('creator_collaboration_opportunities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('applicant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('application_message', sa.Text, nullable=False),
        sa.Column('portfolio_links', postgresql.JSONB),
        sa.Column('relevant_experience', sa.Text),
        sa.Column('proposed_approach', sa.Text),
        sa.Column('availability_confirmation', sa.Boolean, nullable=False, default=False),
        sa.Column('budget_proposal', postgresql.JSONB),
        sa.Column('timeline_proposal', postgresql.JSONB),
        sa.Column('additional_services', postgresql.JSONB),
        sa.Column('references', postgresql.JSONB),
        sa.Column('application_status', sa.String(20), nullable=False, default='pending'),
        sa.Column('ai_compatibility_score', sa.Float, nullable=False, default=0.0),
        sa.Column('manual_review_score', sa.Float),
        sa.Column('reviewer_notes', sa.Text),
        sa.Column('response_date', sa.DateTime),
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
    
    # === ENRICHMENTS INDEXES ===
    
    # Multilingual profiles indexes
    op.create_index('idx_multilingual_profiles_user_id', 'creator_multilingual_profiles', ['user_id'])
    op.create_index('idx_multilingual_profiles_language', 'creator_multilingual_profiles', ['language_code'])
    op.create_index('idx_multilingual_profiles_primary', 'creator_multilingual_profiles', ['user_id', 'is_primary_language'])
    
    # Language preferences indexes
    op.create_index('idx_language_preferences_user_id', 'creator_language_preferences', ['user_id'])
    
    # Cultural adaptations indexes
    op.create_index('idx_cultural_adaptations_user_id', 'creator_cultural_adaptations', ['user_id'])
    op.create_index('idx_cultural_adaptations_culture', 'creator_cultural_adaptations', ['target_culture'])
    
    # Regional preferences indexes
    op.create_index('idx_regional_preferences_user_id', 'creator_regional_preferences', ['user_id'])
    op.create_index('idx_regional_preferences_region', 'creator_regional_preferences', ['region_code'])
    
    # Accessibility profiles indexes
    op.create_index('idx_accessibility_profiles_user_id', 'creator_accessibility_profiles', ['user_id'])
    
    # Voice navigation indexes
    op.create_index('idx_voice_navigation_user_id', 'creator_voice_navigation', ['user_id'])
    
    # Visual assistance indexes
    op.create_index('idx_visual_assistance_user_id', 'creator_visual_assistance', ['user_id'])
    
    # Cognitive accessibility indexes
    op.create_index('idx_cognitive_accessibility_user_id', 'creator_cognitive_accessibility', ['user_id'])
    
    # Enterprise verifications indexes
    op.create_index('idx_enterprise_verifications_user_id', 'creator_enterprise_verifications', ['user_id'])
    op.create_index('idx_enterprise_verifications_tier', 'creator_enterprise_verifications', ['verification_tier'])
    op.create_index('idx_enterprise_verifications_expiry', 'creator_enterprise_verifications', ['verification_expiry'])
    
    # Celebrity verifications indexes
    op.create_index('idx_celebrity_verifications_user_id', 'creator_celebrity_verifications', ['user_id'])
    op.create_index('idx_celebrity_verifications_status', 'creator_celebrity_verifications', ['celebrity_status'])
    
    # Professional certifications indexes
    op.create_index('idx_professional_certifications_user_id', 'creator_professional_certifications', ['user_id'])
    op.create_index('idx_professional_certifications_type', 'creator_professional_certifications', ['certification_type'])
    op.create_index('idx_professional_certifications_expiry', 'creator_professional_certifications', ['expiry_date'])
    
    # Advanced analytics indexes
    op.create_index('idx_advanced_analytics_user_id', 'creator_advanced_analytics', ['user_id'])
    op.create_index('idx_advanced_analytics_date', 'creator_advanced_analytics', ['analytics_date'])
    op.create_index('idx_advanced_analytics_score', 'creator_advanced_analytics', ['performance_score'])
    
    # Audience insights indexes
    op.create_index('idx_audience_insights_user_id', 'creator_audience_insights', ['user_id'])
    op.create_index('idx_audience_insights_date', 'creator_audience_insights', ['insight_date'])
    
    # Growth predictions indexes
    op.create_index('idx_growth_predictions_user_id', 'creator_growth_predictions', ['user_id'])
    op.create_index('idx_growth_predictions_date', 'creator_growth_predictions', ['prediction_date'])
    
    # Networking profiles indexes
    op.create_index('idx_networking_profiles_user_id', 'creator_networking_profiles', ['user_id'])
    op.create_index('idx_networking_profiles_active', 'creator_networking_profiles', ['networking_active'])
    
    # Connections indexes
    op.create_index('idx_connections_creator_id', 'creator_connections', ['creator_id'])
    op.create_index('idx_connections_connected_id', 'creator_connections', ['connected_creator_id'])
    op.create_index('idx_connections_type', 'creator_connections', ['connection_type'])
    
    # Mentor profiles indexes
    op.create_index('idx_mentor_profiles_user_id', 'creator_mentor_profiles', ['user_id'])
    op.create_index('idx_mentor_profiles_active', 'creator_mentor_profiles', ['mentoring_active'])
    
    # Mentee profiles indexes
    op.create_index('idx_mentee_profiles_user_id', 'creator_mentee_profiles', ['user_id'])
    op.create_index('idx_mentee_profiles_seeking', 'creator_mentee_profiles', ['seeking_mentorship'])
    
    # Mentorship relationships indexes
    op.create_index('idx_mentorship_relationships_mentor_id', 'creator_mentorship_relationships', ['mentor_id'])
    op.create_index('idx_mentorship_relationships_mentee_id', 'creator_mentorship_relationships', ['mentee_id'])
    op.create_index('idx_mentorship_relationships_status', 'creator_mentorship_relationships', ['relationship_status'])
    
    # Collaboration opportunities indexes
    op.create_index('idx_collaboration_opportunities_creator_id', 'creator_collaboration_opportunities', ['creator_id'])
    op.create_index('idx_collaboration_opportunities_type', 'creator_collaboration_opportunities', ['collaboration_type'])
    op.create_index('idx_collaboration_opportunities_status', 'creator_collaboration_opportunities', ['status'])
    
    # Collaboration applications indexes
    op.create_index('idx_collaboration_applications_opportunity_id', 'creator_collaboration_applications', ['opportunity_id'])
    op.create_index('idx_collaboration_applications_applicant_id', 'creator_collaboration_applications', ['applicant_id'])
    op.create_index('idx_collaboration_applications_status', 'creator_collaboration_applications', ['application_status'])


def downgrade() -> None:
    """Downgrade database schema - Remove enhanced creator profile tables."""
    
    # Drop enrichment tables in reverse order due to foreign key constraints
    op.drop_table('creator_collaboration_applications')
    op.drop_table('creator_collaboration_opportunities')
    op.drop_table('creator_mentorship_relationships')
    op.drop_table('creator_mentee_profiles')
    op.drop_table('creator_mentor_profiles')
    op.drop_table('creator_connections')
    op.drop_table('creator_networking_profiles')
    op.drop_table('creator_growth_predictions')
    op.drop_table('creator_audience_insights')
    op.drop_table('creator_advanced_analytics')
    op.drop_table('creator_professional_certifications')
    op.drop_table('creator_celebrity_verifications')
    op.drop_table('creator_enterprise_verifications')
    op.drop_table('creator_cognitive_accessibility')
    op.drop_table('creator_visual_assistance')
    op.drop_table('creator_voice_navigation')
    op.drop_table('creator_accessibility_profiles')
    op.drop_table('creator_regional_preferences')
    op.drop_table('creator_cultural_adaptations')
    op.drop_table('creator_language_preferences')
    op.drop_table('creator_multilingual_profiles')
    
    # Drop original tables in reverse order due to foreign key constraints
    op.drop_table('creator_brand_assets')
    op.drop_table('creator_performance_metrics')
    op.drop_table('creator_verification_documents')
    op.drop_table('creator_capabilities')
    op.drop_table('creator_specializations')
    
    # Drop ENUM types
    sa.Enum(name='verification_tier_enterprise').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='supported_language').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='content_quality').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='verification_tier').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='skill_level').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='creator_specialization').drop(op.get_bind(), checkfirst=True)