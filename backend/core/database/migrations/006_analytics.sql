-- ============================================================================
-- PostgreSQL Migration: 006_analytics.sql
-- Analytics and Business Intelligence for IA Influencer Agent Platform
-- ============================================================================
-- 
-- Author: Fahed Mlaiel <mlaiel@live.de>
-- Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
--
-- This migration creates comprehensive analytics system tables
-- supporting user behavior tracking, content performance analytics,
-- business intelligence, reporting, and data aggregation.
-- ============================================================================

-- ============================================================================
-- USER ACTIVITY LOGS TABLE
-- ============================================================================

-- Comprehensive user activity tracking
CREATE TABLE IF NOT EXISTS user_activity_logs (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users_enhanced(id) ON DELETE SET NULL,
    session_id VARCHAR(100),
    
    -- Activity information
    activity_type VARCHAR(100) NOT NULL,
    activity_category VARCHAR(50) NOT NULL CHECK (activity_category IN ('authentication', 'content', 'collaboration', 'social', 'commerce', 'navigation', 'system')),
    activity_description TEXT,
    
    -- Context and metadata
    page_url VARCHAR(1000),
    referrer_url VARCHAR(1000),
    user_agent TEXT,
    
    -- Device and location information
    device_type VARCHAR(50),
    platform VARCHAR(50),
    browser VARCHAR(100),
    ip_address INET,
    country VARCHAR(3),
    region VARCHAR(100),
    city VARCHAR(100),
    timezone VARCHAR(50),
    
    -- Activity specifics
    target_type VARCHAR(50), -- 'content', 'user', 'project', etc.
    target_id UUID,
    action_data JSONB DEFAULT '{}',
    
    -- Performance metrics
    duration_ms INTEGER,
    load_time_ms INTEGER,
    
    -- Status and results
    activity_status VARCHAR(30) DEFAULT 'completed' CHECK (activity_status IN ('started', 'completed', 'failed', 'cancelled')),
    error_code VARCHAR(50),
    error_message TEXT,
    
    -- Audit timestamp
    activity_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- CONTENT ANALYTICS TABLE
-- ============================================================================

-- Content performance analytics
CREATE TABLE IF NOT EXISTS content_analytics (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID NOT NULL REFERENCES media_content(id) ON DELETE CASCADE,
    
    -- Time period for aggregation
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('hourly', 'daily', 'weekly', 'monthly')),
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- View metrics
    total_views BIGINT DEFAULT 0,
    unique_views BIGINT DEFAULT 0,
    view_duration_avg DECIMAL(10,3) DEFAULT 0,
    view_completion_rate DECIMAL(5,2) DEFAULT 0,
    
    -- Engagement metrics
    likes_count INTEGER DEFAULT 0,
    dislikes_count INTEGER DEFAULT 0,
    shares_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    saves_count INTEGER DEFAULT 0,
    
    -- Download and usage
    downloads_count INTEGER DEFAULT 0,
    download_completion_rate DECIMAL(5,2) DEFAULT 0,
    
    -- Revenue metrics
    revenue_generated DECIMAL(12,2) DEFAULT 0,
    purchases_count INTEGER DEFAULT 0,
    revenue_per_view DECIMAL(10,4) DEFAULT 0,
    
    -- Traffic sources
    traffic_sources JSONB DEFAULT '{}', -- {source: count}
    referral_domains JSONB DEFAULT '{}',
    
    -- Geographic data
    geographic_distribution JSONB DEFAULT '{}', -- {country: views}
    top_cities JSONB DEFAULT '[]',
    
    -- Device and platform data
    device_breakdown JSONB DEFAULT '{}', -- {device_type: count}
    platform_breakdown JSONB DEFAULT '{}',
    browser_breakdown JSONB DEFAULT '{}',
    
    -- Audience demographics
    age_distribution JSONB DEFAULT '{}',
    gender_distribution JSONB DEFAULT '{}',
    
    -- Search and discovery
    search_keywords JSONB DEFAULT '[]',
    discovery_methods JSONB DEFAULT '{}',
    
    -- Performance indicators
    bounce_rate DECIMAL(5,2) DEFAULT 0,
    time_on_content DECIMAL(10,3) DEFAULT 0,
    return_visitor_rate DECIMAL(5,2) DEFAULT 0,
    
    -- Social media metrics
    social_shares JSONB DEFAULT '{}', -- {platform: shares}
    viral_coefficient DECIMAL(8,4) DEFAULT 0,
    
    -- Quality metrics
    quality_score DECIMAL(5,2) DEFAULT 0,
    user_satisfaction DECIMAL(5,2) DEFAULT 0,
    
    -- Analytics metadata
    analytics_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(content_id, period_type, period_start)
);

-- ============================================================================
-- USER ANALYTICS TABLE
-- ============================================================================

-- User behavior and performance analytics
CREATE TABLE IF NOT EXISTS user_analytics (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Time period for aggregation
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')),
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Activity metrics
    total_sessions INTEGER DEFAULT 0,
    total_time_spent INTEGER DEFAULT 0, -- in minutes
    average_session_duration DECIMAL(8,2) DEFAULT 0,
    pages_per_session DECIMAL(8,2) DEFAULT 0,
    
    -- Content metrics
    content_uploads INTEGER DEFAULT 0,
    content_views BIGINT DEFAULT 0,
    content_likes_received INTEGER DEFAULT 0,
    content_shares_received INTEGER DEFAULT 0,
    content_downloads INTEGER DEFAULT 0,
    
    -- Collaboration metrics
    collaborations_initiated INTEGER DEFAULT 0,
    collaborations_joined INTEGER DEFAULT 0,
    collaborations_completed INTEGER DEFAULT 0,
    collaboration_rating_avg DECIMAL(3,2) DEFAULT 0,
    
    -- Social metrics
    profile_views INTEGER DEFAULT 0,
    followers_gained INTEGER DEFAULT 0,
    followers_lost INTEGER DEFAULT 0,
    connections_made INTEGER DEFAULT 0,
    
    -- Financial metrics
    revenue_earned DECIMAL(12,2) DEFAULT 0,
    content_sales INTEGER DEFAULT 0,
    subscription_revenue DECIMAL(12,2) DEFAULT 0,
    collaboration_earnings DECIMAL(12,2) DEFAULT 0,
    
    -- Engagement metrics
    likes_given INTEGER DEFAULT 0,
    comments_posted INTEGER DEFAULT 0,
    shares_performed INTEGER DEFAULT 0,
    messages_sent INTEGER DEFAULT 0,
    
    -- Learning and growth
    skills_learned TEXT[],
    achievements_earned INTEGER DEFAULT 0,
    level_progress INTEGER DEFAULT 0,
    xp_gained INTEGER DEFAULT 0,
    
    -- Platform usage
    features_used TEXT[],
    most_used_tools TEXT[],
    subscription_tier VARCHAR(20),
    
    -- Performance indicators
    productivity_score DECIMAL(5,2) DEFAULT 0,
    engagement_score DECIMAL(5,2) DEFAULT 0,
    influence_score DECIMAL(8,2) DEFAULT 0,
    
    -- Analytics metadata
    analytics_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, period_type, period_start)
);

-- ============================================================================
-- PLATFORM ANALYTICS TABLE
-- ============================================================================

-- Platform-wide analytics and KPIs
CREATE TABLE IF NOT EXISTS platform_analytics (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Time period for aggregation
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('hourly', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly')),
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- User metrics
    total_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    new_registrations INTEGER DEFAULT 0,
    user_retention_rate DECIMAL(5,2) DEFAULT 0,
    churn_rate DECIMAL(5,2) DEFAULT 0,
    
    -- Content metrics
    total_content BIGINT DEFAULT 0,
    content_uploads INTEGER DEFAULT 0,
    content_views BIGINT DEFAULT 0,
    content_downloads BIGINT DEFAULT 0,
    storage_used_gb DECIMAL(12,2) DEFAULT 0,
    
    -- Collaboration metrics
    active_collaborations INTEGER DEFAULT 0,
    new_collaborations INTEGER DEFAULT 0,
    completed_collaborations INTEGER DEFAULT 0,
    collaboration_success_rate DECIMAL(5,2) DEFAULT 0,
    
    -- Financial metrics
    total_revenue DECIMAL(15,2) DEFAULT 0,
    subscription_revenue DECIMAL(15,2) DEFAULT 0,
    transaction_revenue DECIMAL(15,2) DEFAULT 0,
    average_revenue_per_user DECIMAL(10,2) DEFAULT 0,
    
    -- Engagement metrics
    total_interactions BIGINT DEFAULT 0,
    messages_sent BIGINT DEFAULT 0,
    likes_given BIGINT DEFAULT 0,
    shares_performed BIGINT DEFAULT 0,
    
    -- Performance metrics
    api_requests BIGINT DEFAULT 0,
    average_response_time_ms DECIMAL(8,2) DEFAULT 0,
    error_rate DECIMAL(5,4) DEFAULT 0,
    uptime_percentage DECIMAL(5,2) DEFAULT 100.0,
    
    -- Traffic metrics
    page_views BIGINT DEFAULT 0,
    unique_visitors BIGINT DEFAULT 0,
    bounce_rate DECIMAL(5,2) DEFAULT 0,
    average_session_duration DECIMAL(8,2) DEFAULT 0,
    
    -- Geographic distribution
    top_countries JSONB DEFAULT '[]',
    traffic_by_region JSONB DEFAULT '{}',
    
    -- Device and platform
    mobile_usage_percentage DECIMAL(5,2) DEFAULT 0,
    desktop_usage_percentage DECIMAL(5,2) DEFAULT 0,
    browser_distribution JSONB DEFAULT '{}',
    
    -- Feature adoption
    feature_usage JSONB DEFAULT '{}',
    ai_feature_usage JSONB DEFAULT '{}',
    
    -- Support and satisfaction
    support_tickets INTEGER DEFAULT 0,
    average_resolution_time_hours DECIMAL(8,2) DEFAULT 0,
    customer_satisfaction DECIMAL(3,2) DEFAULT 0,
    
    -- Analytics metadata
    analytics_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(period_type, period_start)
);

-- ============================================================================
-- REPORTS TABLE
-- ============================================================================

-- Saved reports and dashboards
CREATE TABLE IF NOT EXISTS reports (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_by UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Report information
    report_name VARCHAR(255) NOT NULL,
    report_description TEXT,
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN ('dashboard', 'chart', 'table', 'export', 'scheduled')),
    report_category VARCHAR(100) NOT NULL,
    
    -- Report configuration
    data_sources TEXT[] NOT NULL,
    filters JSONB DEFAULT '{}',
    metrics JSONB NOT NULL,
    dimensions JSONB DEFAULT '[]',
    
    -- Visualization settings
    chart_type VARCHAR(50),
    chart_config JSONB DEFAULT '{}',
    layout_config JSONB DEFAULT '{}',
    
    -- Time and scheduling
    time_range JSONB NOT NULL,
    refresh_frequency VARCHAR(30) DEFAULT 'manual' CHECK (refresh_frequency IN ('manual', 'real_time', 'hourly', 'daily', 'weekly', 'monthly')),
    next_refresh TIMESTAMP WITH TIME ZONE,
    
    -- Sharing and access
    visibility VARCHAR(20) DEFAULT 'private' CHECK (visibility IN ('private', 'team', 'public')),
    shared_with UUID[],
    
    -- Report status
    is_active BOOLEAN DEFAULT TRUE,
    is_favorite BOOLEAN DEFAULT FALSE,
    
    -- Performance tracking
    view_count INTEGER DEFAULT 0,
    last_viewed TIMESTAMP WITH TIME ZONE,
    generation_time_ms INTEGER,
    
    -- Report metadata
    report_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- REPORT EXECUTIONS TABLE
-- ============================================================================

-- Report execution history and results
CREATE TABLE IF NOT EXISTS report_executions (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    executed_by UUID REFERENCES users_enhanced(id) ON DELETE SET NULL,
    
    -- Execution details
    execution_type VARCHAR(30) NOT NULL CHECK (execution_type IN ('manual', 'scheduled', 'api', 'export')),
    execution_status VARCHAR(30) DEFAULT 'running' CHECK (execution_status IN ('running', 'completed', 'failed', 'cancelled')),
    
    -- Performance metrics
    execution_time_ms INTEGER,
    data_rows_processed BIGINT,
    result_size_bytes BIGINT,
    
    -- Results
    result_data JSONB,
    result_format VARCHAR(20) DEFAULT 'json' CHECK (result_format IN ('json', 'csv', 'pdf', 'excel')),
    result_url VARCHAR(1000),
    
    -- Error handling
    error_code VARCHAR(50),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Execution metadata
    execution_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- EVENT TRACKING TABLE
-- ============================================================================

-- Custom event tracking for analytics
CREATE TABLE IF NOT EXISTS event_tracking (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users_enhanced(id) ON DELETE SET NULL,
    session_id VARCHAR(100),
    
    -- Event information
    event_name VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) NOT NULL,
    event_action VARCHAR(100),
    event_label VARCHAR(200),
    
    -- Event value and properties
    event_value DECIMAL(12,4),
    event_properties JSONB DEFAULT '{}',
    
    -- Context information
    page_url VARCHAR(1000),
    referrer_url VARCHAR(1000),
    campaign_source VARCHAR(100),
    campaign_medium VARCHAR(100),
    campaign_name VARCHAR(100),
    
    -- Device and location
    device_info JSONB DEFAULT '{}',
    location_info JSONB DEFAULT '{}',
    
    -- Timing
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Event metadata
    event_metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- CONVERSION FUNNELS TABLE
-- ============================================================================

-- Conversion funnel tracking and analytics
CREATE TABLE IF NOT EXISTS conversion_funnels (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Funnel information
    funnel_name VARCHAR(200) NOT NULL,
    funnel_description TEXT,
    funnel_type VARCHAR(50) NOT NULL CHECK (funnel_type IN ('registration', 'subscription', 'content_creation', 'collaboration', 'purchase')),
    
    -- Funnel steps
    funnel_steps JSONB NOT NULL, -- Array of step definitions
    
    -- Time period
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Funnel metrics
    total_entries INTEGER DEFAULT 0,
    step_conversions JSONB DEFAULT '{}', -- {step_index: count}
    conversion_rates JSONB DEFAULT '{}', -- {step_index: rate}
    overall_conversion_rate DECIMAL(5,4) DEFAULT 0,
    
    -- Drop-off analysis
    drop_off_points JSONB DEFAULT '{}',
    average_time_to_convert DECIMAL(10,3) DEFAULT 0,
    
    -- Segmentation
    segment_performance JSONB DEFAULT '{}',
    
    -- Funnel metadata
    funnel_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- A/B TESTS TABLE
-- ============================================================================

-- A/B testing and experimentation
CREATE TABLE IF NOT EXISTS ab_tests (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_by UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Test information
    test_name VARCHAR(200) NOT NULL,
    test_description TEXT,
    hypothesis TEXT,
    
    -- Test configuration
    test_type VARCHAR(50) NOT NULL CHECK (test_type IN ('simple_ab', 'multivariate', 'split_url', 'feature_flag')),
    variants JSONB NOT NULL, -- Array of variant definitions
    traffic_allocation JSONB NOT NULL, -- {variant_id: percentage}
    
    -- Targeting and segmentation
    target_audience JSONB DEFAULT '{}',
    inclusion_criteria JSONB DEFAULT '{}',
    exclusion_criteria JSONB DEFAULT '{}',
    
    -- Test timeline
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    expected_duration_days INTEGER,
    
    -- Success metrics
    primary_metric VARCHAR(100) NOT NULL,
    secondary_metrics TEXT[],
    success_criteria JSONB NOT NULL,
    
    -- Test status
    test_status VARCHAR(30) DEFAULT 'draft' CHECK (test_status IN ('draft', 'running', 'paused', 'completed', 'cancelled')),
    
    -- Results and analysis
    results JSONB DEFAULT '{}',
    statistical_significance DECIMAL(5,4),
    confidence_level DECIMAL(5,2) DEFAULT 95.0,
    winner_variant VARCHAR(100),
    
    -- Test metadata
    test_metadata JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER TEST ASSIGNMENTS TABLE
-- ============================================================================

-- User assignments to A/B tests
CREATE TABLE IF NOT EXISTS user_test_assignments (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users_enhanced(id) ON DELETE CASCADE,
    test_id UUID NOT NULL REFERENCES ab_tests(id) ON DELETE CASCADE,
    
    -- Assignment details
    variant_id VARCHAR(100) NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Participation tracking
    first_exposure TIMESTAMP WITH TIME ZONE,
    last_exposure TIMESTAMP WITH TIME ZONE,
    exposure_count INTEGER DEFAULT 0,
    
    -- Conversion tracking
    converted BOOLEAN DEFAULT FALSE,
    conversion_value DECIMAL(12,4),
    conversion_timestamp TIMESTAMP WITH TIME ZONE,
    
    -- Assignment metadata
    assignment_metadata JSONB DEFAULT '{}',
    
    -- Constraints
    UNIQUE(user_id, test_id)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- User activity log indexes
CREATE INDEX idx_user_activity_logs_user_id ON user_activity_logs(user_id);
CREATE INDEX idx_user_activity_logs_activity_type ON user_activity_logs(activity_type);
CREATE INDEX idx_user_activity_logs_category ON user_activity_logs(activity_category);
CREATE INDEX idx_user_activity_logs_timestamp ON user_activity_logs(activity_timestamp);
CREATE INDEX idx_user_activity_logs_session_id ON user_activity_logs(session_id);

-- Content analytics indexes
CREATE INDEX idx_content_analytics_content_id ON content_analytics(content_id);
CREATE INDEX idx_content_analytics_period ON content_analytics(period_type, period_start);
CREATE INDEX idx_content_analytics_views ON content_analytics(total_views);

-- User analytics indexes
CREATE INDEX idx_user_analytics_user_id ON user_analytics(user_id);
CREATE INDEX idx_user_analytics_period ON user_analytics(period_type, period_start);

-- Platform analytics indexes
CREATE INDEX idx_platform_analytics_period ON platform_analytics(period_type, period_start);

-- Report indexes
CREATE INDEX idx_reports_created_by ON reports(created_by);
CREATE INDEX idx_reports_type ON reports(report_type);
CREATE INDEX idx_reports_category ON reports(report_category);
CREATE INDEX idx_reports_active ON reports(is_active);

-- Report execution indexes
CREATE INDEX idx_report_executions_report_id ON report_executions(report_id);
CREATE INDEX idx_report_executions_status ON report_executions(execution_status);
CREATE INDEX idx_report_executions_started_at ON report_executions(started_at);

-- Event tracking indexes
CREATE INDEX idx_event_tracking_user_id ON event_tracking(user_id);
CREATE INDEX idx_event_tracking_event_name ON event_tracking(event_name);
CREATE INDEX idx_event_tracking_category ON event_tracking(event_category);
CREATE INDEX idx_event_tracking_timestamp ON event_tracking(event_timestamp);
CREATE INDEX idx_event_tracking_session_id ON event_tracking(session_id);

-- A/B test indexes
CREATE INDEX idx_ab_tests_created_by ON ab_tests(created_by);
CREATE INDEX idx_ab_tests_status ON ab_tests(test_status);
CREATE INDEX idx_ab_tests_dates ON ab_tests(start_date, end_date);

-- User test assignment indexes
CREATE INDEX idx_user_test_assignments_user_id ON user_test_assignments(user_id);
CREATE INDEX idx_user_test_assignments_test_id ON user_test_assignments(test_id);
CREATE INDEX idx_user_test_assignments_variant ON user_test_assignments(variant_id);

-- Composite indexes for common queries
CREATE INDEX idx_activity_logs_user_timestamp ON user_activity_logs(user_id, activity_timestamp);
CREATE INDEX idx_content_analytics_content_period ON content_analytics(content_id, period_type, period_start);
CREATE INDEX idx_event_tracking_user_timestamp ON event_tracking(user_id, event_timestamp);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update report view count
CREATE OR REPLACE FUNCTION update_report_view_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE reports SET
        view_count = view_count + 1,
        last_viewed = NOW(),
        updated_at = NOW()
    WHERE id = NEW.report_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply report view count trigger
CREATE TRIGGER update_report_view_count_trigger
    AFTER INSERT ON report_executions
    FOR EACH ROW EXECUTE FUNCTION update_report_view_count();

-- Apply updated_at triggers
CREATE TRIGGER update_content_analytics_updated_at 
    BEFORE UPDATE ON content_analytics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_analytics_updated_at 
    BEFORE UPDATE ON user_analytics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_platform_analytics_updated_at 
    BEFORE UPDATE ON platform_analytics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reports_updated_at 
    BEFORE UPDATE ON reports 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversion_funnels_updated_at 
    BEFORE UPDATE ON conversion_funnels 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ab_tests_updated_at 
    BEFORE UPDATE ON ab_tests 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Real-time analytics dashboard view
CREATE OR REPLACE VIEW analytics_dashboard AS
SELECT 
    -- Current period metrics
    (SELECT COUNT(*) FROM users_enhanced WHERE created_at >= CURRENT_DATE) as new_users_today,
    (SELECT COUNT(*) FROM user_activity_logs WHERE activity_timestamp >= CURRENT_DATE) as activities_today,
    (SELECT COUNT(*) FROM media_content WHERE uploaded_at >= CURRENT_DATE) as content_uploaded_today,
    (SELECT COUNT(*) FROM collaboration_projects WHERE created_at >= CURRENT_DATE) as new_collaborations_today,
    
    -- Top content
    (SELECT json_agg(
        json_build_object(
            'content_id', ca.content_id,
            'title', mc.title,
            'views', ca.total_views
        ) ORDER BY ca.total_views DESC
    ) FROM content_analytics ca 
    JOIN media_content mc ON ca.content_id = mc.id 
    WHERE ca.period_type = 'daily' AND ca.period_start = CURRENT_DATE
    LIMIT 10) as top_content_today,
    
    -- Active users
    (SELECT COUNT(DISTINCT user_id) FROM user_activity_logs WHERE activity_timestamp >= NOW() - INTERVAL '1 hour') as active_users_last_hour,
    (SELECT COUNT(DISTINCT user_id) FROM user_activity_logs WHERE activity_timestamp >= CURRENT_DATE) as active_users_today;

-- Content performance summary view
CREATE OR REPLACE VIEW content_performance_summary AS
SELECT 
    mc.id,
    mc.title,
    mc.content_type,
    mc.user_id,
    u.username,
    
    -- Current period metrics
    COALESCE(ca_daily.total_views, 0) as views_today,
    COALESCE(ca_weekly.total_views, 0) as views_this_week,
    COALESCE(ca_monthly.total_views, 0) as views_this_month,
    
    -- Engagement metrics
    COALESCE(ca_daily.likes_count, 0) as likes_today,
    COALESCE(ca_daily.shares_count, 0) as shares_today,
    COALESCE(ca_daily.comments_count, 0) as comments_today,
    
    -- Revenue metrics
    COALESCE(ca_monthly.revenue_generated, 0) as revenue_this_month,
    COALESCE(ca_monthly.purchases_count, 0) as purchases_this_month
    
FROM media_content mc
JOIN users_enhanced u ON mc.user_id = u.id
LEFT JOIN content_analytics ca_daily ON mc.id = ca_daily.content_id 
    AND ca_daily.period_type = 'daily' 
    AND ca_daily.period_start = CURRENT_DATE
LEFT JOIN content_analytics ca_weekly ON mc.id = ca_weekly.content_id 
    AND ca_weekly.period_type = 'weekly' 
    AND ca_weekly.period_start >= DATE_TRUNC('week', CURRENT_DATE)
LEFT JOIN content_analytics ca_monthly ON mc.id = ca_monthly.content_id 
    AND ca_monthly.period_type = 'monthly' 
    AND ca_monthly.period_start >= DATE_TRUNC('month', CURRENT_DATE)
WHERE mc.deleted_at IS NULL;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to track custom events
CREATE OR REPLACE FUNCTION track_event(
    p_user_id UUID,
    p_event_name VARCHAR(100),
    p_event_category VARCHAR(50),
    p_event_properties JSONB DEFAULT '{}',
    p_event_value DECIMAL(12,4) DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    new_event_id UUID;
BEGIN
    INSERT INTO event_tracking (
        user_id, event_name, event_category, 
        event_properties, event_value
    )
    VALUES (
        p_user_id, p_event_name, p_event_category,
        p_event_properties, p_event_value
    )
    RETURNING id INTO new_event_id;
    
    RETURN new_event_id;
END;
$$ LANGUAGE plpgsql;

-- Function to aggregate content analytics
CREATE OR REPLACE FUNCTION aggregate_content_analytics(
    p_content_id UUID,
    p_period_type VARCHAR(20),
    p_period_start TIMESTAMP WITH TIME ZONE,
    p_period_end TIMESTAMP WITH TIME ZONE
)
RETURNS BOOLEAN AS $$
DECLARE
    analytics_record RECORD;
BEGIN
    -- Calculate analytics for the specified period
    SELECT 
        COUNT(DISTINCT ual.user_id) as unique_views,
        COUNT(*) as total_views,
        AVG(ual.duration_ms) as avg_duration,
        COUNT(*) FILTER (WHERE ual.activity_type = 'content_like') as likes,
        COUNT(*) FILTER (WHERE ual.activity_type = 'content_share') as shares,
        COUNT(*) FILTER (WHERE ual.activity_type = 'content_comment') as comments,
        COUNT(*) FILTER (WHERE ual.activity_type = 'content_download') as downloads,
        COALESCE(SUM(t.amount), 0) as revenue
    INTO analytics_record
    FROM user_activity_logs ual
    LEFT JOIN transactions t ON ual.target_id::TEXT = t.content_id::TEXT 
        AND t.transaction_type = 'content_purchase'
        AND t.transaction_status = 'completed'
    WHERE ual.target_id = p_content_id
        AND ual.activity_timestamp BETWEEN p_period_start AND p_period_end
        AND ual.target_type = 'content';
    
    -- Insert or update analytics record
    INSERT INTO content_analytics (
        content_id, period_type, period_start, period_end,
        total_views, unique_views, view_duration_avg,
        likes_count, shares_count, comments_count, downloads_count,
        revenue_generated
    )
    VALUES (
        p_content_id, p_period_type, p_period_start, p_period_end,
        analytics_record.total_views, analytics_record.unique_views, analytics_record.avg_duration,
        analytics_record.likes, analytics_record.shares, analytics_record.comments, analytics_record.downloads,
        analytics_record.revenue
    )
    ON CONFLICT (content_id, period_type, period_start)
    DO UPDATE SET
        total_views = EXCLUDED.total_views,
        unique_views = EXCLUDED.unique_views,
        view_duration_avg = EXCLUDED.view_duration_avg,
        likes_count = EXCLUDED.likes_count,
        shares_count = EXCLUDED.shares_count,
        comments_count = EXCLUDED.comments_count,
        downloads_count = EXCLUDED.downloads_count,
        revenue_generated = EXCLUDED.revenue_generated,
        updated_at = NOW();
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SECURITY POLICIES (Row Level Security)
-- ============================================================================

-- Enable RLS
ALTER TABLE user_activity_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Activity log policies (users can see their own activities)
CREATE POLICY user_own_activity_logs ON user_activity_logs
    FOR SELECT TO authenticated_users
    USING (user_id = current_user_id());

-- Content analytics policies (content owners can see their analytics)
CREATE POLICY content_owner_analytics ON content_analytics
    FOR SELECT TO authenticated_users
    USING (
        content_id IN (
            SELECT id FROM media_content WHERE user_id = current_user_id()
        )
    );

-- User analytics policies (users can see their own analytics)
CREATE POLICY user_own_analytics ON user_analytics
    FOR SELECT TO authenticated_users
    USING (user_id = current_user_id());

-- Report policies (report creators and shared users can access)
CREATE POLICY report_access ON reports
    FOR ALL TO authenticated_users
    USING (
        created_by = current_user_id() 
        OR current_user_id() = ANY(shared_with)
        OR visibility = 'public'
    );

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE user_activity_logs IS 'Comprehensive user activity tracking for behavior analysis';
COMMENT ON TABLE content_analytics IS 'Content performance analytics with aggregated metrics';
COMMENT ON TABLE user_analytics IS 'User behavior and performance analytics over time';
COMMENT ON TABLE platform_analytics IS 'Platform-wide analytics and key performance indicators';
COMMENT ON TABLE reports IS 'Saved reports and custom dashboards for analytics';
COMMENT ON TABLE report_executions IS 'Report execution history and results storage';
COMMENT ON TABLE event_tracking IS 'Custom event tracking for detailed analytics';
COMMENT ON TABLE conversion_funnels IS 'Conversion funnel tracking and optimization';
COMMENT ON TABLE ab_tests IS 'A/B testing and experimentation framework';
COMMENT ON TABLE user_test_assignments IS 'User assignments to A/B tests and variants';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================