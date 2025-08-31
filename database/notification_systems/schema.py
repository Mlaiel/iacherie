"""Notification Systems Database Schema

Schémas de base de données pour les systèmes de notifications.
Tables pour emails, push, alertes, queues et communications temps réel.

Auteur: Fahed Mlaiel <mlaiel@live.de>
Équipe: Lead AI Developer, Backend Senior, DBA Expert
Copyright © 2025 Fahed Mlaiel. Tous droits réservés.

AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution non autorisée
est strictement interdite et constitue une violation des droits d'auteur.
Les contrevenants s'exposent à des poursuites judiciaires.
"""# Email Tables
EMAIL_MESSAGES_TABLE = """CREATE TABLE IF NOT EXISTS email_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    to_email VARCHAR(255) NOT NULL,
    to_name VARCHAR(255),
    from_email VARCHAR(255) NOT NULL,
    from_name VARCHAR(255),
    subject TEXT NOT NULL,
    html_content TEXT,
    text_content TEXT,
    template_id UUID,
    template_data JSONB DEFAULT '{}',
    priority VARCHAR(50) DEFAULT 'normal',
    scheduled_at TIMESTAMP WITH TIME ZONE,
    provider VARCHAR(50) DEFAULT 'smtp',
    tracking_enabled BOOLEAN DEFAULT true,
    attachments JSONB DEFAULT '[]',
    headers JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_email_messages_to_email (to_email),
    INDEX idx_email_messages_scheduled (scheduled_at),
    INDEX idx_email_messages_created (created_at),
    INDEX idx_email_messages_template (template_id)
);
"""EMAIL_DELIVERIES_TABLE = """CREATE TABLE IF NOT EXISTS email_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES email_messages(id) ON DELETE CASCADE,
    delivery_status VARCHAR(50) DEFAULT 'pending',
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    bounced_at TIMESTAMP WITH TIME ZONE,
    bounce_reason TEXT,
    provider_message_id VARCHAR(255),
    provider_response JSONB DEFAULT '{}',
    retry_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_email_deliveries_status (delivery_status),
    INDEX idx_email_deliveries_delivered (delivered_at),
    INDEX idx_email_deliveries_message (message_id)
);
"""# Fingerprint Integration Tables
FINGERPRINT_NOTIFICATIONS_TABLE = """CREATE TABLE IF NOT EXISTS fingerprint_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    content_id UUID NOT NULL,
    fingerprint_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    content_type VARCHAR(20) NOT NULL,
    quality_score DECIMAL(3,2) NOT NULL,
    processing_time DECIMAL(8,3) NOT NULL,
    similarity_matches JSONB DEFAULT '[]',
    message_data JSONB NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal',
    category VARCHAR(50) DEFAULT 'general',
    action_required BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_fingerprint_notifications_user (user_id),
    INDEX idx_fingerprint_notifications_content (content_id),
    INDEX idx_fingerprint_notifications_event (event_type),
    INDEX idx_fingerprint_notifications_created (created_at),
    INDEX idx_fingerprint_notifications_quality (quality_score),
    INDEX idx_fingerprint_notifications_priority (priority)
);
"""CONTENT_VIOLATION_EVIDENCE_TABLE = """CREATE TABLE IF NOT EXISTS content_violation_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL,
    fingerprint_id UUID,
    evidence_data JSONB NOT NULL,
    violation_type VARCHAR(50),
    platform VARCHAR(50),
    detected_url TEXT,
    screenshot_urls JSONB DEFAULT '[]',
    legal_status VARCHAR(30) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_violation_evidence_content (content_id),
    INDEX idx_violation_evidence_platform (platform),
    INDEX idx_violation_evidence_status (legal_status),
    INDEX idx_violation_evidence_created (created_at)
);
"""# Crawler Surveillance Tables
CRAWLER_SURVEILLANCE_NOTIFICATIONS_TABLE = """CREATE TABLE IF NOT EXISTS crawler_surveillance_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    content_id UUID NOT NULL,
    platform VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    detected_url TEXT NOT NULL,
    similarity_score DECIMAL(5,4) NOT NULL,
    violation_type VARCHAR(50),
    severity VARCHAR(20) NOT NULL,
    violator_profile JSONB,
    evidence_urls JSONB DEFAULT '[]',
    automated_actions JSONB DEFAULT '[]',
    crawler_metadata JSONB DEFAULT '{}',
    message_data JSONB NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal',
    category VARCHAR(50) DEFAULT 'general',
    action_required BOOLEAN DEFAULT false,
    investigation_id UUID,
    legal_action_taken BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_surveillance_notifications_user (user_id),
    INDEX idx_surveillance_notifications_platform (platform),
    INDEX idx_surveillance_notifications_severity (severity),
    INDEX idx_surveillance_notifications_event (event_type),
    INDEX idx_surveillance_notifications_similarity (similarity_score),
    INDEX idx_surveillance_notifications_created (created_at),
    INDEX idx_surveillance_notifications_action (action_required)
);
"""PLATFORM_MONITORING_SESSIONS_TABLE = """CREATE TABLE IF NOT EXISTS platform_monitoring_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    content_id UUID NOT NULL,
    platform VARCHAR(50) NOT NULL,
    monitoring_status VARCHAR(20) DEFAULT 'active',
    scan_frequency INTEGER DEFAULT 3600,  -- en secondes
    last_scan_at TIMESTAMP WITH TIME ZONE,
    next_scan_at TIMESTAMP WITH TIME ZONE,
    total_scans INTEGER DEFAULT 0,
    violations_found INTEGER DEFAULT 0,
    monitoring_config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_monitoring_sessions_user (user_id),
    INDEX idx_monitoring_sessions_platform (platform),
    INDEX idx_monitoring_sessions_status (monitoring_status),
    INDEX idx_monitoring_sessions_next_scan (next_scan_at),
    UNIQUE(user_id, content_id, platform)
);
"""# Licensing Monetization Tables
LICENSING_MONETIZATION_NOTIFICATIONS_TABLE = """CREATE TABLE IF NOT EXISTS licensing_monetization_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    content_id UUID NOT NULL,
    license_id UUID,
    event_type VARCHAR(50) NOT NULL,
    revenue_source VARCHAR(50) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    licensee_info JSONB DEFAULT '{}',
    contract_details JSONB DEFAULT '{}',
    payment_details JSONB DEFAULT '{}',
    payment_status VARCHAR(20),
    license_duration INTEGER,  -- en jours
    territory VARCHAR(100),
    usage_rights JSONB DEFAULT '[]',
    royalty_rate DECIMAL(5,4),
    licensing_metadata JSONB DEFAULT '{}',
    message_data JSONB NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal',
    category VARCHAR(50) DEFAULT 'general',
    action_required BOOLEAN DEFAULT false,
    tax_document_generated BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_licensing_notifications_user (user_id),
    INDEX idx_licensing_notifications_content (content_id),
    INDEX idx_licensing_notifications_event (event_type),
    INDEX idx_licensing_notifications_revenue_source (revenue_source),
    INDEX idx_licensing_notifications_amount (amount),
    INDEX idx_licensing_notifications_currency (currency),
    INDEX idx_licensing_notifications_created (created_at),
    INDEX idx_licensing_notifications_payment_status (payment_status)
);
"""REVENUE_MILESTONES_TABLE = """CREATE TABLE IF NOT EXISTS revenue_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    milestone_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    achieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_revenue_at_achievement DECIMAL(12,2) NOT NULL,
    celebration_content JSONB DEFAULT '{}',
    shared_on_social BOOLEAN DEFAULT false,
    notification_sent BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_revenue_milestones_user (user_id),
    INDEX idx_revenue_milestones_amount (milestone_amount),
    INDEX idx_revenue_milestones_achieved (achieved_at),
    UNIQUE(user_id, milestone_amount, currency)
);
"""LICENSING_CONTRACTS_TABLE = """CREATE TABLE IF NOT EXISTS licensing_contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    content_id UUID NOT NULL,
    license_id UUID NOT NULL,
    licensee_name VARCHAR(255) NOT NULL,
    licensee_email VARCHAR(255),
    contract_type VARCHAR(50) NOT NULL,
    revenue_source VARCHAR(50) NOT NULL,
    base_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    royalty_rate DECIMAL(5,4),
    license_start_date DATE NOT NULL,
    license_end_date DATE,
    territory VARCHAR(100),
    usage_rights JSONB DEFAULT '[]',
    exclusivity BOOLEAN DEFAULT false,
    auto_renewal BOOLEAN DEFAULT false,
    contract_status VARCHAR(20) DEFAULT 'active',
    payment_schedule VARCHAR(20) DEFAULT 'monthly',
    contract_document_url TEXT,
    digital_signature_hash VARCHAR(128),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_licensing_contracts_user (user_id),
    INDEX idx_licensing_contracts_content (content_id),
    INDEX idx_licensing_contracts_licensee (licensee_email),
    INDEX idx_licensing_contracts_status (contract_status),
    INDEX idx_licensing_contracts_dates (license_start_date, license_end_date),
    INDEX idx_licensing_contracts_revenue_source (revenue_source)
);
"""# Tables pour les nouveaux gestionnaires SEO et Collaboration
SEO_OPTIMIZATION_NOTIFICATIONS_TABLE = """CREATE TABLE IF NOT EXISTS seo_optimization_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    content_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    keyword VARCHAR(255),
    search_engine VARCHAR(50) NOT NULL,
    current_ranking INTEGER,
    previous_ranking INTEGER,
    search_volume INTEGER,
    url TEXT,
    optimization_suggestions JSONB NOT NULL DEFAULT '[]',
    competitor_data JSONB NOT NULL DEFAULT '{}',
    seo_metadata JSONB NOT NULL DEFAULT '{}',
    priority_score DECIMAL(3,2) NOT NULL DEFAULT 0.5,
    target_audience VARCHAR(255),
    content_type VARCHAR(100),
    message_data JSONB NOT NULL DEFAULT '{}',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    category VARCHAR(100) NOT NULL DEFAULT 'seo',
    action_required BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    
    INDEX idx_seo_optimization_user_keyword (user_id, keyword),
    INDEX idx_seo_optimization_ranking (current_ranking),
    INDEX idx_seo_optimization_engine (search_engine),
    INDEX idx_seo_optimization_created (created_at)
);
"""COLLABORATION_MATCHING_NOTIFICATIONS_TABLE = """CREATE TABLE IF NOT EXISTS collaboration_matching_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    collaboration_type VARCHAR(100) NOT NULL,
    opportunity_id VARCHAR(255),
    matched_collaborator_id VARCHAR(255),
    project_id VARCHAR(255),
    proposal_id VARCHAR(255),
    match_score DECIMAL(3,2) NOT NULL DEFAULT 0.0,
    compatibility_factors JSONB NOT NULL DEFAULT '{}',
    recommendation_reasons JSONB NOT NULL DEFAULT '[]',
    priority_score DECIMAL(3,2) NOT NULL DEFAULT 0.5,
    metadata JSONB NOT NULL DEFAULT '{}',
    message_data JSONB NOT NULL DEFAULT '{}',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    category VARCHAR(100) NOT NULL DEFAULT 'collaboration',
    action_required BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    INDEX idx_collaboration_matching_user_type (user_id, collaboration_type),
    INDEX idx_collaboration_matching_score (match_score),
    INDEX idx_collaboration_matching_project (project_id),
    INDEX idx_collaboration_matching_created (created_at)
);
"""# Advanced Analytics Tables
NOTIFICATION_ANALYTICS_TABLE = """CREATE TABLE IF NOT EXISTS notification_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id UUID NOT NULL,
    user_id UUID NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    delivery_status VARCHAR(20) NOT NULL,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    action_taken_at TIMESTAMP WITH TIME ZONE,
    engagement_score DECIMAL(3,2) DEFAULT 0.0,
    device_type VARCHAR(20),
    platform VARCHAR(20),
    location_country VARCHAR(2),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_notification_analytics_notification (notification_id),
    INDEX idx_notification_analytics_user (user_id),
    INDEX idx_notification_analytics_type (notification_type),
    INDEX idx_notification_analytics_channel (channel),
    INDEX idx_notification_analytics_status (delivery_status),
    INDEX idx_notification_analytics_delivered (delivered_at),
    INDEX idx_notification_analytics_engagement (engagement_score)
);
"""USER_NOTIFICATION_PREFERENCES_TABLE = """CREATE TABLE IF NOT EXISTS user_notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    notification_category VARCHAR(50) NOT NULL,
    email_enabled BOOLEAN DEFAULT true,
    push_enabled BOOLEAN DEFAULT true,
    sms_enabled BOOLEAN DEFAULT false,
    websocket_enabled BOOLEAN DEFAULT true,
    dashboard_enabled BOOLEAN DEFAULT true,
    frequency VARCHAR(20) DEFAULT 'immediate',  -- immediate, hourly, daily, weekly
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    timezone VARCHAR(50) DEFAULT 'UTC',
    priority_threshold VARCHAR(20) DEFAULT 'normal',  -- low, normal, high, urgent
    language VARCHAR(5) DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_user_notification_prefs_user (user_id),
    INDEX idx_user_notification_prefs_category (notification_category),
    UNIQUE(user_id, notification_category)
);
"""NOTIFICATION_QUEUE_MANAGEMENT_TABLE = """CREATE TABLE IF NOT EXISTS notification_queue_management (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    queue_name VARCHAR(100) NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    priority_level INTEGER NOT NULL,
    max_retry_count INTEGER DEFAULT 3,
    retry_delay_seconds INTEGER DEFAULT 60,
    batch_size INTEGER DEFAULT 100,
    rate_limit_per_minute INTEGER DEFAULT 1000,
    circuit_breaker_threshold INTEGER DEFAULT 10,
    dead_letter_enabled BOOLEAN DEFAULT true,
    queue_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_queue_management_name (queue_name),
    INDEX idx_queue_management_type (notification_type),
    INDEX idx_queue_management_priority (priority_level),
    INDEX idx_queue_management_status (queue_status),
    UNIQUE(queue_name, notification_type)
);
"""# AI-Powered Insights Tables
NOTIFICATION_AI_INSIGHTS_TABLE = """CREATE TABLE IF NOT EXISTS notification_ai_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    content_id UUID,
    insight_type VARCHAR(50) NOT NULL,
    insight_category VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    insight_data JSONB NOT NULL,
    recommendations JSONB DEFAULT '[]',
    predicted_outcome JSONB DEFAULT '{}',
    model_version VARCHAR(20),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    acted_upon BOOLEAN DEFAULT false,
    feedback_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_ai_insights_user (user_id),
    INDEX idx_ai_insights_content (content_id),
    INDEX idx_ai_insights_type (insight_type),
    INDEX idx_ai_insights_category (insight_category),
    INDEX idx_ai_insights_confidence (confidence_score),
    INDEX idx_ai_insights_generated (generated_at),
    INDEX idx_ai_insights_expires (expires_at)
);
"""CROSS_PLATFORM_SYNC_TABLE = """CREATE TABLE IF NOT EXISTS cross_platform_sync (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    content_id UUID NOT NULL,
    source_platform VARCHAR(50) NOT NULL,
    target_platforms JSONB NOT NULL,
    sync_status VARCHAR(20) DEFAULT 'pending',
    sync_config JSONB DEFAULT '{}',
    last_sync_at TIMESTAMP WITH TIME ZONE,
    next_sync_at TIMESTAMP WITH TIME ZONE,
    sync_errors JSONB DEFAULT '[]',
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_cross_platform_sync_user (user_id),
    INDEX idx_cross_platform_sync_content (content_id),
    INDEX idx_cross_platform_sync_source (source_platform),
    INDEX idx_cross_platform_sync_status (sync_status),
    INDEX idx_cross_platform_sync_next (next_sync_at)
);
"""    similarity_score FLOAT NOT NULL,
    content_segment JSONB DEFAULT '{}',
    evidence_data JSONB DEFAULT '{}',
    legal_action_required BOOLEAN DEFAULT false,
    revenue_impact DECIMAL(12,2) DEFAULT 0.00,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending',
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_violations_user (user_id),
    INDEX idx_violations_platform (platform),
    INDEX idx_violations_severity (severity),
    INDEX idx_violations_detected (detected_at)
);
"""ESCALATION_JOBS_TABLE = """CREATE TABLE IF NOT EXISTS escalation_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    violation_id UUID NOT NULL REFERENCES content_protection_violations(id),
    rule_id VARCHAR(100) NOT NULL,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    executed_at TIMESTAMP WITH TIME ZONE,
    actions JSONB DEFAULT '[]',
    channels JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'pending',
    result JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_escalation_scheduled (scheduled_time),
    INDEX idx_escalation_violation (violation_id)
);
"""# Revenue Tables
REVENUE_TRANSACTIONS_TABLE = """CREATE TABLE IF NOT EXISTS revenue_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    content_id UUID,
    source VARCHAR(50) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    description TEXT,
    platform VARCHAR(50),
    reference_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settlement_date TIMESTAMP WITH TIME ZONE,
    fees DECIMAL(12,2) DEFAULT 0.00,
    net_amount DECIMAL(12,2) NOT NULL,
    tax_amount DECIMAL(12,2) DEFAULT 0.00,
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_revenue_user (user_id),
    INDEX idx_revenue_source (source),
    INDEX idx_revenue_date (transaction_date),
    INDEX idx_revenue_platform (platform)
);
"""REVENUE_GOALS_TABLE = """CREATE TABLE IF NOT EXISTS revenue_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    target_amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    period_type VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    current_amount DECIMAL(12,2) DEFAULT 0.00,
    progress_percentage FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT true,
    achievement_date TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_revenue_goals_user (user_id),
    INDEX idx_revenue_goals_active (is_active),
    INDEX idx_revenue_goals_period (period_type, end_date)
);
"""REVENUE_NOTIFICATIONS_TABLE = """CREATE TABLE IF NOT EXISTS revenue_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    trigger VARCHAR(50) NOT NULL,
    threshold_amount DECIMAL(12,2) DEFAULT 0.00,
    frequency VARCHAR(20) DEFAULT 'immediate',
    channels JSONB DEFAULT '["email"]',
    is_active BOOLEAN DEFAULT true,
    last_triggered TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_revenue_notifications_user (user_id),
    INDEX idx_revenue_notifications_trigger (trigger)
);
"""# Collaboration Tables
ARTIST_PROFILES_TABLE = """CREATE TABLE IF NOT EXISTS artist_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    artist_name VARCHAR(255) NOT NULL,
    genres JSONB DEFAULT '[]',
    skills JSONB DEFAULT '[]',
    location VARCHAR(255),
    languages JSONB DEFAULT '[]',
    collaboration_preferences JSONB DEFAULT '{}',
    past_collaborations JSONB DEFAULT '[]',
    availability JSONB DEFAULT '{}',
    social_metrics JSONB DEFAULT '{}',
    music_style_vector JSONB DEFAULT '[]',
    reputation_score FLOAT DEFAULT 5.0,
    response_rate FLOAT DEFAULT 1.0,
    completion_rate FLOAT DEFAULT 1.0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_artist_profiles_user (user_id),
    INDEX idx_artist_profiles_location (location),
    INDEX idx_artist_profiles_reputation (reputation_score)
);
"""COLLABORATION_OPPORTUNITIES_TABLE = """CREATE TABLE IF NOT EXISTS collaboration_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    initiator_id UUID NOT NULL,
    target_id UUID NOT NULL,
    collaboration_type VARCHAR(50) NOT NULL,
    match_quality INTEGER NOT NULL,
    compatibility_score FLOAT NOT NULL,
    mutual_benefits JSONB DEFAULT '[]',
    project_description TEXT,
    estimated_timeline VARCHAR(255),
    proposed_terms JSONB DEFAULT '{}',
    ai_reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'suggested',
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_collab_ops_initiator (initiator_id),
    INDEX idx_collab_ops_target (target_id),
    INDEX idx_collab_ops_type (collaboration_type),
    INDEX idx_collab_ops_status (status)
);
"""COLLABORATION_PROJECTS_TABLE = """CREATE TABLE IF NOT EXISTS collaboration_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    participants JSONB NOT NULL,
    collaboration_type VARCHAR(50) NOT NULL,
    description TEXT,
    timeline JSONB DEFAULT '{}',
    milestones JSONB DEFAULT '[]',
    shared_resources JSONB DEFAULT '[]',
    revenue_split JSONB DEFAULT '{}',
    contracts JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_collab_projects_status (status),
    INDEX idx_collab_projects_type (collaboration_type),
    INDEX idx_collab_projects_created (created_at)
);
"""# Performance Analytics Tables
PERFORMANCE_DATA_POINTS_TABLE = """CREATE TABLE IF NOT EXISTS performance_data_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    content_id UUID,
    platform VARCHAR(50) NOT NULL,
    metric VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_performance_user (user_id),
    INDEX idx_performance_platform (platform),
    INDEX idx_performance_metric (metric),
    INDEX idx_performance_timestamp (timestamp),
    INDEX idx_performance_composite (user_id, platform, metric, timestamp)
);
"""PERFORMANCE_INSIGHTS_TABLE = """CREATE TABLE IF NOT EXISTS performance_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    confidence_score FLOAT NOT NULL,
    actionable_recommendations JSONB DEFAULT '[]',
    supporting_data JSONB DEFAULT '{}',
    predicted_impact JSONB DEFAULT '{}',
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    priority INTEGER DEFAULT 1,
    visualization TEXT,
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_insights_user (user_id),
    INDEX idx_insights_type (insight_type),
    INDEX idx_insights_priority (priority),
    INDEX idx_insights_generated (generated_at)
);
"""PERFORMANCE_GOALS_TABLE = """CREATE TABLE IF NOT EXISTS performance_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    metric VARCHAR(50) NOT NULL,
    target_value FLOAT NOT NULL,
    current_value FLOAT DEFAULT 0.0,
    target_date DATE,
    platform VARCHAR(50),
    progress_percentage FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    achieved_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_perf_goals_user (user_id),
    INDEX idx_perf_goals_metric (metric),
    INDEX idx_perf_goals_active (is_active)
);
"""# Distribution Tables
DISTRIBUTION_JOBS_TABLE = """CREATE TABLE IF NOT EXISTS distribution_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    content_id UUID,
    content_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    tags JSONB DEFAULT '[]',
    optimization_strategy VARCHAR(50) DEFAULT 'balanced',
    scheduled_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending',
    results JSONB DEFAULT '{}',
    errors JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_dist_jobs_user (user_id),
    INDEX idx_dist_jobs_status (status),
    INDEX idx_dist_jobs_created (created_at)
);
"""PLATFORM_PUBLICATIONS_TABLE = """CREATE TABLE IF NOT EXISTS platform_publications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    distribution_job_id UUID NOT NULL REFERENCES distribution_jobs(id),
    platform VARCHAR(50) NOT NULL,
    platform_content_id VARCHAR(255),
    platform_url TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    upload_progress FLOAT DEFAULT 0.0,
    published_at TIMESTAMP WITH TIME ZONE,
    views INTEGER DEFAULT 0,
    engagement_metrics JSONB DEFAULT '{}',
    revenue_data JSONB DEFAULT '{}',
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_platform_pubs_job (distribution_job_id),
    INDEX idx_platform_pubs_platform (platform),
    INDEX idx_platform_pubs_status (status),
    INDEX idx_platform_pubs_published (published_at)
);
"""# Notification System Core Tables
NOTIFICATION_QUEUE_TABLE = """CREATE TABLE IF NOT EXISTS notification_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 3,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    template_data JSONB DEFAULT '{}',
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_notification_queue_user (user_id),
    INDEX idx_notification_queue_status (status),
    INDEX idx_notification_queue_scheduled (scheduled_at),
    INDEX idx_notification_queue_priority (priority)
);
"""NOTIFICATION_PREFERENCES_TABLE = """CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    enabled BOOLEAN DEFAULT true,
    frequency VARCHAR(20) DEFAULT 'immediate',
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    timezone VARCHAR(50) DEFAULT 'UTC',
    metadata JSONB DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, notification_type, channel),
    INDEX idx_notification_prefs_user (user_id),
    INDEX idx_notification_prefs_type (notification_type)
);
"""# Analytics and Metrics Tables
NOTIFICATION_METRICS_TABLE = """CREATE TABLE IF NOT EXISTS notification_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    notification_type VARCHAR(50) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    sent_count INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    opened_count INTEGER DEFAULT 0,
    clicked_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    delivery_rate FLOAT DEFAULT 0.0,
    open_rate FLOAT DEFAULT 0.0,
    click_rate FLOAT DEFAULT 0.0,
    average_delivery_time FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, notification_type, channel, date),
    INDEX idx_notification_metrics_date (date),
    INDEX idx_notification_metrics_user (user_id),
    INDEX idx_notification_metrics_type (notification_type)
);
"""# WebSocket and Real-time Tables
REALTIME_CONNECTIONS_TABLE = """CREATE TABLE IF NOT EXISTS realtime_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    connection_id VARCHAR(255) NOT NULL UNIQUE,
    socket_type VARCHAR(20) DEFAULT 'websocket',
    room_id VARCHAR(255),
    user_agent TEXT,
    ip_address INET,
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_realtime_user (user_id),
    INDEX idx_realtime_room (room_id),
    INDEX idx_realtime_status (status),
    INDEX idx_realtime_activity (last_activity)
);
"""REALTIME_MESSAGES_TABLE = """CREATE TABLE IF NOT EXISTS realtime_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL,
    room_id VARCHAR(255) NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    attachments JSONB DEFAULT '[]',
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    delivered_to JSONB DEFAULT '[]',
    read_by JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_realtime_messages_room (room_id),
    INDEX idx_realtime_messages_sender (sender_id),
    INDEX idx_realtime_messages_sent (sent_at)
);
"""# Push Notification Tables
PUSH_DEVICES_TABLE = """CREATE TABLE IF NOT EXISTS push_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    device_token VARCHAR(500) NOT NULL UNIQUE,
    device_type VARCHAR(20) NOT NULL, -- ios, android, web
    platform VARCHAR(50), -- fcm, apns, webpush
    app_version VARCHAR(50),
    os_version VARCHAR(50),
    device_info JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_push_devices_user (user_id),
    INDEX idx_push_devices_type (device_type),
    INDEX idx_push_devices_active (is_active)
);
"""PUSH_MESSAGES_TABLE = """CREATE TABLE IF NOT EXISTS push_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    device_token VARCHAR(500) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    badge INTEGER DEFAULT 0,
    sound VARCHAR(100) DEFAULT 'default',
    click_action VARCHAR(255),
    data JSONB DEFAULT '{}',
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending',
    provider_response JSONB DEFAULT '{}',
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_push_messages_user (user_id),
    INDEX idx_push_messages_device (device_token),
    INDEX idx_push_messages_status (status),
    INDEX idx_push_messages_sent (sent_at)
);
"""# Complete schema creation script
ALL_NOTIFICATION_TABLES = [
    EMAIL_MESSAGES_TABLE,
    EMAIL_DELIVERIES_TABLE,
    CONTENT_PROTECTION_VIOLATIONS_TABLE,
    ESCALATION_JOBS_TABLE,
    REVENUE_TRANSACTIONS_TABLE,
    REVENUE_GOALS_TABLE,
    REVENUE_NOTIFICATIONS_TABLE,
    ARTIST_PROFILES_TABLE,
    COLLABORATION_OPPORTUNITIES_TABLE,
    COLLABORATION_PROJECTS_TABLE,
    PERFORMANCE_DATA_POINTS_TABLE,
    PERFORMANCE_INSIGHTS_TABLE,
    PERFORMANCE_GOALS_TABLE,
    DISTRIBUTION_JOBS_TABLE,
    PLATFORM_PUBLICATIONS_TABLE,
    NOTIFICATION_QUEUE_TABLE,
    NOTIFICATION_PREFERENCES_TABLE,
    NOTIFICATION_METRICS_TABLE,
    REALTIME_CONNECTIONS_TABLE,
    REALTIME_MESSAGES_TABLE,
    PUSH_DEVICES_TABLE,
    PUSH_MESSAGES_TABLE
]

def create_notification_schema_sql() -> str:
    """Génère le script SQL complet pour créer le schéma de notifications"""    sql_parts = [
        "-- Enterprise Notification Systems Database Schema",
        "-- Auteur: Fahed Mlaiel <mlaiel@live.de>",
        "-- Copyright © 2025 Fahed Mlaiel. Tous droits réservés.",
        "",
        "-- Enable required extensions",
        "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
        "CREATE EXTENSION IF NOT EXISTS \"pg_stat_statements\";",
        ""
    ]
    
    sql_parts.extend(ALL_NOTIFICATION_TABLES)
    
    # Triggers et fonctions
    sql_parts.extend([
        """-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';
""",
        
        """-- Apply update triggers
CREATE TRIGGER update_artist_profiles_updated_at 
    BEFORE UPDATE ON artist_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_preferences_updated_at 
    BEFORE UPDATE ON notification_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
""",
        
        """-- Performance optimization views
CREATE OR REPLACE VIEW notification_dashboard_summary AS
SELECT 
    user_id,
    COUNT(*) as total_notifications,
    COUNT(*) FILTER (WHERE status = 'sent') as sent_count,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_count,
    AVG(CASE WHEN sent_at IS NOT NULL 
        THEN EXTRACT(EPOCH FROM (sent_at - created_at)) 
        ELSE NULL END) as avg_delivery_time
FROM notification_queue 
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY user_id;
""",
        
        """-- Revenue performance view
CREATE OR REPLACE VIEW revenue_dashboard_summary AS
SELECT 
    user_id,
    SUM(net_amount) as total_revenue,
    COUNT(*) as transaction_count,
    AVG(net_amount) as avg_transaction,
    MAX(transaction_date) as last_transaction
FROM revenue_transactions 
WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY user_id;
"""    ])
    
    return "\n".join(sql_parts)
    provider_message_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    provider VARCHAR(50) NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    bounced_at TIMESTAMP WITH TIME ZONE,
    bounce_reason TEXT,
    tracking_data JSONB DEFAULT '{}',
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_email_deliveries_message (message_id),
    INDEX idx_email_deliveries_status (status),
    INDEX idx_email_deliveries_provider (provider),
    INDEX idx_email_deliveries_sent (sent_at)
);
"""EMAIL_TEMPLATES_TABLE = """CREATE TABLE IF NOT EXISTS email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    subject TEXT NOT NULL,
    html_content TEXT,
    text_content TEXT,
    category VARCHAR(100),
    variables JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_email_templates_name (name),
    INDEX idx_email_templates_category (category),
    INDEX idx_email_templates_active (is_active)
);
"""# Push Notification Tables
PUSH_DEVICES_TABLE = """CREATE TABLE IF NOT EXISTS push_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    platform VARCHAR(50) NOT NULL,
    token TEXT NOT NULL,
    endpoint TEXT,
    p256dh_key TEXT,
    auth_key TEXT,
    app_version VARCHAR(50),
    os_version VARCHAR(50),
    device_model VARCHAR(100),
    timezone VARCHAR(50),
    language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT true,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_push_devices_user (user_id),
    INDEX idx_push_devices_platform (platform),
    INDEX idx_push_devices_token (token),
    INDEX idx_push_devices_active (is_active),
    UNIQUE(user_id, platform, token)
);
"""PUSH_NOTIFICATIONS_TABLE = """CREATE TABLE IF NOT EXISTS push_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    device_id UUID,
    platform VARCHAR(50),
    notification_type VARCHAR(100) DEFAULT 'system_alert',
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    icon TEXT,
    image TEXT,
    badge INTEGER,
    sound VARCHAR(100),
    priority VARCHAR(50) DEFAULT 'normal',
    ttl INTEGER DEFAULT 86400,
    collapse_key VARCHAR(255),
    data JSONB DEFAULT '{}',
    actions JSONB DEFAULT '[]',
    scheduled_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    click_action TEXT,
    deep_link TEXT,
    tracking_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_push_notifications_user (user_id),
    INDEX idx_push_notifications_device (device_id),
    INDEX idx_push_notifications_type (notification_type),
    INDEX idx_push_notifications_scheduled (scheduled_at),
    INDEX idx_push_notifications_created (created_at)
);
"""PUSH_DELIVERIES_TABLE = """CREATE TABLE IF NOT EXISTS push_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id UUID NOT NULL REFERENCES push_notifications(id) ON DELETE CASCADE,
    device_id UUID NOT NULL REFERENCES push_devices(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    provider_message_id VARCHAR(255),
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    dismissed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    response_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_push_deliveries_notification (notification_id),
    INDEX idx_push_deliveries_device (device_id),
    INDEX idx_push_deliveries_status (status),
    INDEX idx_push_deliveries_platform (platform)
);
"""# Real-time Communication Tables
REALTIME_MESSAGES_TABLE = """CREATE TABLE IF NOT EXISTS realtime_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(100) NOT NULL,
    sender_id UUID NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    priority VARCHAR(50) DEFAULT 'normal',
    ttl INTEGER,
    delivery_receipt BOOLEAN DEFAULT false,
    read_receipt BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    INDEX idx_realtime_messages_sender (sender_id),
    INDEX idx_realtime_messages_target (target_type, target_id),
    INDEX idx_realtime_messages_type (type),
    INDEX idx_realtime_messages_created (created_at)
);
"""COMMUNICATION_ROOMS_TABLE = """CREATE TABLE IF NOT EXISTS communication_rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) DEFAULT 'general',
    owner_id UUID NOT NULL,
    members JSONB DEFAULT '[]',
    permissions JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    
    INDEX idx_communication_rooms_owner (owner_id),
    INDEX idx_communication_rooms_type (type),
    INDEX idx_communication_rooms_active (is_active)
);
"""# Alert Management Tables
ALERT_RULES_TABLE = """CREATE TABLE IF NOT EXISTS alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    conditions JSONB NOT NULL,
    threshold_value DOUBLE PRECISION,
    threshold_operator VARCHAR(10) DEFAULT '>',
    time_window INTEGER DEFAULT 300,
    occurrence_count INTEGER DEFAULT 1,
    suppression_time INTEGER DEFAULT 3600,
    auto_resolve_time INTEGER,
    tags JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    
    INDEX idx_alert_rules_type (alert_type),
    INDEX idx_alert_rules_severity (severity),
    INDEX idx_alert_rules_active (is_active),
    INDEX idx_alert_rules_name (name)
);
"""ALERTS_TABLE = """CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id UUID NOT NULL REFERENCES alert_rules(id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    title TEXT NOT NULL,
    description TEXT,
    source VARCHAR(255),
    entity_id VARCHAR(255),
    entity_type VARCHAR(100),
    current_value DOUBLE PRECISION,
    threshold_value DOUBLE PRECISION,
    occurrence_count INTEGER DEFAULT 1,
    first_occurrence TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_occurrence TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by UUID,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID,
    resolution_notes TEXT,
    suppressed_until TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    tags JSONB DEFAULT '[]',
    context JSONB DEFAULT '{}',
    escalation_level INTEGER DEFAULT 0,
    next_escalation_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_alerts_rule (rule_id),
    INDEX idx_alerts_status (status),
    INDEX idx_alerts_severity (severity),
    INDEX idx_alerts_type (alert_type),
    INDEX idx_alerts_entity (entity_type, entity_id),
    INDEX idx_alerts_escalation (next_escalation_at),
    INDEX idx_alerts_created (created_at)
);
"""ESCALATION_POLICIES_TABLE = """CREATE TABLE IF NOT EXISTS escalation_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    alert_types JSONB DEFAULT '[]',
    severity_levels JSONB DEFAULT '[]',
    steps JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_escalation_policies_name (name),
    INDEX idx_escalation_policies_active (is_active)
);
"""ALERT_NOTIFICATIONS_TABLE = """CREATE TABLE IF NOT EXISTS alert_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    escalation_step INTEGER DEFAULT 0,
    action VARCHAR(100) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    recipient_type VARCHAR(50) DEFAULT 'user',
    message TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    failure_reason TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_alert_notifications_alert (alert_id),
    INDEX idx_alert_notifications_status (status),
    INDEX idx_alert_notifications_recipient (recipient)
);
"""# Queue Management Tables
NOTIFICATION_QUEUE_AUDIT_TABLE = """CREATE TABLE IF NOT EXISTS notification_queue_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL,
    queue_type VARCHAR(100) NOT NULL,
    priority INTEGER NOT NULL,
    payload JSONB NOT NULL,
    headers JSONB DEFAULT '{}',
    routing_key VARCHAR(255),
    exchange VARCHAR(255),
    scheduled_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    max_retries INTEGER DEFAULT 3,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_notification_queue_audit_message (message_id),
    INDEX idx_notification_queue_audit_queue (queue_type),
    INDEX idx_notification_queue_audit_created (created_at)
);
"""NOTIFICATION_QUEUE_STATS_TABLE = """CREATE TABLE IF NOT EXISTS notification_queue_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    queue_name VARCHAR(100) NOT NULL,
    total_messages BIGINT DEFAULT 0,
    pending_messages BIGINT DEFAULT 0,
    processing_messages BIGINT DEFAULT 0,
    completed_messages BIGINT DEFAULT 0,
    failed_messages BIGINT DEFAULT 0,
    dead_messages BIGINT DEFAULT 0,
    avg_processing_time DOUBLE PRECISION DEFAULT 0,
    throughput_per_minute DOUBLE PRECISION DEFAULT 0,
    last_processed_at TIMESTAMP WITH TIME ZONE,
    snapshot_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_notification_queue_stats_queue (queue_name),
    INDEX idx_notification_queue_stats_snapshot (snapshot_at)
);
"""# Create all tables
ALL_TABLES = [
    # Email tables
    EMAIL_MESSAGES_TABLE,
    EMAIL_DELIVERIES_TABLE,
    EMAIL_TEMPLATES_TABLE,
    
    # Push notification tables
    PUSH_DEVICES_TABLE,
    PUSH_NOTIFICATIONS_TABLE,
    PUSH_DELIVERIES_TABLE,
    
    # Real-time communication tables
    REALTIME_MESSAGES_TABLE,
    COMMUNICATION_ROOMS_TABLE,
    
    # Alert management tables
    ALERT_RULES_TABLE,
    ALERTS_TABLE,
    ESCALATION_POLICIES_TABLE,
    ALERT_NOTIFICATIONS_TABLE,
    
    # Queue management tables
    NOTIFICATION_QUEUE_AUDIT_TABLE,
    NOTIFICATION_QUEUE_STATS_TABLE
]

# Database functions and triggers
DATABASE_FUNCTIONS = """-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_email_messages_updated_at 
    BEFORE UPDATE ON email_messages 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_push_devices_updated_at 
    BEFORE UPDATE ON push_devices 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alert_rules_updated_at 
    BEFORE UPDATE ON alert_rules 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at 
    BEFORE UPDATE ON alerts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_escalation_policies_updated_at 
    BEFORE UPDATE ON escalation_policies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
-- Function to automatically expire old messages
CREATE OR REPLACE FUNCTION cleanup_expired_realtime_messages()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM realtime_messages 
    WHERE expires_at IS NOT NULL AND expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE 'plpgsql';

-- Function to get queue statistics
CREATE OR REPLACE FUNCTION get_notification_queue_summary()
RETURNS TABLE (
    queue_type VARCHAR(100),
    total_messages BIGINT,
    success_rate DOUBLE PRECISION,
    avg_processing_time DOUBLE PRECISION,
    last_activity TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        nqa.queue_type,
        COUNT(*) as total_messages,
        CASE 
            WHEN COUNT(*) > 0 THEN 
                (COUNT(*) FILTER (WHERE nqs.completed_messages > 0)::DOUBLE PRECISION / COUNT(*)::DOUBLE PRECISION) * 100
            ELSE 0
        END as success_rate,
        AVG(nqs.avg_processing_time) as avg_processing_time,
        MAX(nqa.created_at) as last_activity
    FROM notification_queue_audit nqa
    LEFT JOIN notification_queue_stats nqs ON nqa.queue_type = nqs.queue_name
    WHERE nqa.created_at > NOW() - INTERVAL '24 hours'
    GROUP BY nqa.queue_type;
END;
$$ LANGUAGE 'plpgsql';
"""# Initial data and configurations
INITIAL_EMAIL_TEMPLATES = """-- Welcome email template
INSERT INTO email_templates (name, subject, html_content, text_content, category, variables) VALUES
('welcome_user', 'Bienvenue sur IA Influencer Agent !', 
'<h1>Bienvenue {{user_name}} !</h1><p>Votre compte a été créé avec succès. Vous pouvez maintenant commencer à protéger et monétiser votre contenu créatif.</p>',
'Bienvenue {{user_name}} ! Votre compte a été créé avec succès. Vous pouvez maintenant commencer à protéger et monétiser votre contenu créatif.',
'onboarding', '["user_name", "account_type"]'),

('content_protection_alert', 'Alerte de Protection de Contenu',
'<h2>Violation Détectée</h2><p>Nous avons détecté une utilisation non autorisée de votre contenu "{{content_title}}".</p><p>Plateforme: {{platform}}</p><p>Action recommandée: {{recommended_action}}</p>',
'Violation Détectée: Nous avons détecté une utilisation non autorisée de votre contenu "{{content_title}}" sur {{platform}}. Action recommandée: {{recommended_action}}',
'security', '["content_title", "platform", "recommended_action"]'),

('revenue_update', 'Mise à jour de vos Revenus',
'<h2>Vos Revenus du Mois</h2><p>Bonjour {{user_name}},</p><p>Voici votre rapport de revenus pour {{period}}:</p><ul><li>Total: {{total_revenue}}€</li><li>Évolution: {{revenue_change}}%</li></ul>',
'Vos Revenus du Mois - Bonjour {{user_name}}, voici votre rapport de revenus pour {{period}}: Total: {{total_revenue}}€, Évolution: {{revenue_change}}%',
'finance', '["user_name", "period", "total_revenue", "revenue_change"]'),

('collaboration_request', 'Nouvelle Demande de Collaboration',
'<h2>Demande de Collaboration</h2><p>{{requester_name}} souhaite collaborer avec vous sur le projet "{{project_title}}".</p><p>Type: {{collaboration_type}}</p><p><a href="{{collaboration_link}}">Voir les détails</a></p>',
'Nouvelle Demande de Collaboration: {{requester_name}} souhaite collaborer avec vous sur "{{project_title}}". Type: {{collaboration_type}}. Lien: {{collaboration_link}}',
'collaboration', '["requester_name", "project_title", "collaboration_type", "collaboration_link"]');
"""INITIAL_ESCALATION_POLICIES = """-- Security escalation policy
INSERT INTO escalation_policies (name, description, alert_types, severity_levels, steps) VALUES
('security_escalation', 'Politique d''escalade pour les alertes de sécurité',
'["security_breach", "copyright_infringement", "user_suspicious_activity"]',
'["high", "critical", "emergency"]',
'[
    {
        "delay": 300,
        "actions": [
            {
                "type": "email",
                "recipients": ["security@company.com"],
                "message_template": "Alerte de sécurité: {title}\nSévérité: {severity}\nDescription: {description}"
            }
        ]
    },
    {
        "delay": 900,
        "actions": [
            {
                "type": "push",
                "recipients": ["security_team"],
                "message_template": "URGENT: {title}"
            },
            {
                "type": "webhook",
                "recipients": ["https://hooks.slack.com/security-alerts"],
                "message_template": "Alerte sécurité non résolue: {title}"
            }
        ]
    }
]'),

-- System escalation policy  
('system_escalation', 'Politique d''escalade pour les alertes système',
'["system_error", "performance_degradation", "storage_full", "api_rate_limit"]',
'["medium", "high", "critical"]',
'[
    {
        "delay": 600,
        "actions": [
            {
                "type": "email",
                "recipients": ["devops@company.com"],
                "message_template": "Alerte système: {title}\nValeur: {current_value}\nSeuil: {threshold_value}"
            }
        ]
    },
    {
        "delay": 1800,
        "actions": [
            {
                "type": "push",
                "recipients": ["devops_team"],
                "message_template": "SYSTÈME: {title} - Action requise"
            }
        ]
    }
]');
"""# Database initialization script
async def initialize_notification_database(db_pool):
    """Initialize the notification systems database"""    async with db_pool.acquire() as conn:
        try:
            # Create tables
            for table_sql in ALL_TABLES:
                await conn.execute(table_sql)
            
            # Create functions and triggers
            await conn.execute(DATABASE_FUNCTIONS)
            
            # Insert initial templates
            await conn.execute(INITIAL_EMAIL_TEMPLATES)
            
            # Insert initial escalation policies
            await conn.execute(INITIAL_ESCALATION_POLICIES)
            
            print("✅ Base de données notification systems initialisée avec succès")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
            raise
