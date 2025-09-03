-- ============================================================================
-- PostgreSQL Migration: 001_users_extended.sql
-- Extended User Management for IA Influencer Agent Platform
-- ============================================================================
-- 
-- Author: Fahed Mlaiel <mlaiel@live.de>
-- Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
--
-- This migration extends the basic user schema to support advanced
-- influencer platform features including creator profiles, subscriptions,
-- multi-factor authentication, and comprehensive user management.
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";

-- ============================================================================
-- ENHANCED USERS TABLE
-- ============================================================================

-- Create enhanced users table with comprehensive fields
CREATE TABLE IF NOT EXISTS users_enhanced (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email CITEXT UNIQUE NOT NULL,
    
    -- Authentication
    password_hash VARCHAR(255) NOT NULL,
    password_salt VARCHAR(255) NOT NULL,
    password_last_changed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP WITH TIME ZONE,
    
    -- Multi-factor authentication
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    mfa_backup_codes TEXT[],
    mfa_last_used TIMESTAMP WITH TIME ZONE,
    
    -- Profile information
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    display_name VARCHAR(150),
    bio TEXT,
    avatar_url VARCHAR(500),
    cover_image_url VARCHAR(500),
    website VARCHAR(255),
    location VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    
    -- Contact information
    phone_number VARCHAR(20),
    phone_verified BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    
    -- Creator information
    creator_type VARCHAR(50) CHECK (creator_type IN ('musician', 'photographer', 'videographer', 'blogger', 'podcaster', 'influencer', 'comedian', 'artist', 'other')),
    creator_category VARCHAR(100),
    creator_tags TEXT[],
    creator_verified BOOLEAN DEFAULT FALSE,
    creator_verification_date TIMESTAMP WITH TIME ZONE,
    
    -- Subscription and billing
    subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'professional', 'enterprise')),
    subscription_status VARCHAR(20) DEFAULT 'active' CHECK (subscription_status IN ('active', 'inactive', 'cancelled', 'suspended')),
    subscription_start_date TIMESTAMP WITH TIME ZONE,
    subscription_end_date TIMESTAMP WITH TIME ZONE,
    billing_customer_id VARCHAR(100),
    
    -- Account status and moderation
    account_status VARCHAR(20) DEFAULT 'active' CHECK (account_status IN ('active', 'inactive', 'suspended', 'banned', 'pending_verification')),
    suspension_reason TEXT,
    suspension_until TIMESTAMP WITH TIME ZONE,
    
    -- Privacy and preferences
    privacy_level VARCHAR(20) DEFAULT 'public' CHECK (privacy_level IN ('public', 'friends', 'private')),
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    marketing_emails BOOLEAN DEFAULT FALSE,
    analytics_opt_in BOOLEAN DEFAULT TRUE,
    
    -- Platform integrations
    social_profiles JSONB DEFAULT '{}',
    platform_connections JSONB DEFAULT '{}',
    integration_settings JSONB DEFAULT '{}',
    
    -- Content and collaboration preferences
    collaboration_open BOOLEAN DEFAULT TRUE,
    content_licensing JSONB DEFAULT '{}',
    revenue_sharing_enabled BOOLEAN DEFAULT FALSE,
    
    -- Statistics and metrics
    total_content_uploads INTEGER DEFAULT 0,
    total_collaborations INTEGER DEFAULT 0,
    total_revenue DECIMAL(12,2) DEFAULT 0.00,
    content_views BIGINT DEFAULT 0,
    follower_count INTEGER DEFAULT 0,
    
    -- Compliance and legal
    terms_accepted BOOLEAN DEFAULT FALSE,
    terms_accepted_date TIMESTAMP WITH TIME ZONE,
    privacy_policy_accepted BOOLEAN DEFAULT FALSE,
    privacy_policy_accepted_date TIMESTAMP WITH TIME ZONE,
    age_verified BOOLEAN DEFAULT FALSE,
    country_code VARCHAR(3),
    
    -- Technical metadata
    api_key_hash VARCHAR(255),
    api_rate_limit INTEGER DEFAULT 1000,
    last_login TIMESTAMP WITH TIME ZONE,
    last_activity TIMESTAMP WITH TIME ZONE,
    login_count INTEGER DEFAULT 0,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP WITH TIME ZONE,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional metadata
    user_metadata JSONB DEFAULT '{}',
    system_metadata JSONB DEFAULT '{}'
);

-- ============================================================================
-- USER PROFILES TABLE
-- ============================================================================

-- Extended profile information for creators
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Professional information
    professional_title VARCHAR(200),
    years_experience INTEGER,
    specializations TEXT[],
    achievements TEXT[],
    awards TEXT[],
    
    -- Portfolio and showcase
    portfolio_url VARCHAR(500),
    demo_reel_url VARCHAR(500),
    featured_content JSONB DEFAULT '[]',
    portfolio_description TEXT,
    
    -- Business information
    business_name VARCHAR(200),
    business_type VARCHAR(50),
    tax_id VARCHAR(50),
    business_address JSONB,
    
    -- Rates and pricing
    hourly_rate DECIMAL(10,2),
    project_rates JSONB DEFAULT '{}',
    currency VARCHAR(3) DEFAULT 'USD',
    payment_terms TEXT,
    
    -- Availability and scheduling
    availability_status VARCHAR(20) DEFAULT 'available' CHECK (availability_status IN ('available', 'busy', 'unavailable')),
    working_hours JSONB DEFAULT '{}',
    time_zone VARCHAR(50) DEFAULT 'UTC',
    booking_calendar_url VARCHAR(500),
    
    -- Equipment and technical specs
    equipment JSONB DEFAULT '[]',
    software_tools JSONB DEFAULT '[]',
    technical_specifications JSONB DEFAULT '{}',
    
    -- Statistics and performance
    completion_rate DECIMAL(5,2) DEFAULT 100.00,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    total_reviews INTEGER DEFAULT 0,
    response_time_hours INTEGER DEFAULT 24,
    
    -- Social proof
    testimonials JSONB DEFAULT '[]',
    client_logos JSONB DEFAULT '[]',
    press_mentions JSONB DEFAULT '[]',
    
    -- SEO and discoverability
    seo_keywords TEXT[],
    search_visibility BOOLEAN DEFAULT TRUE,
    featured_creator BOOLEAN DEFAULT FALSE,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER SETTINGS TABLE
-- ============================================================================

-- Comprehensive user settings and preferences
CREATE TABLE IF NOT EXISTS user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Notification preferences
    email_notifications JSONB DEFAULT '{}',
    push_notifications JSONB DEFAULT '{}',
    sms_notifications JSONB DEFAULT '{}',
    
    -- Privacy settings
    profile_visibility VARCHAR(20) DEFAULT 'public',
    content_visibility VARCHAR(20) DEFAULT 'public',
    contact_visibility VARCHAR(20) DEFAULT 'public',
    analytics_sharing BOOLEAN DEFAULT TRUE,
    
    -- Content preferences
    content_quality VARCHAR(20) DEFAULT 'high',
    auto_upload_settings JSONB DEFAULT '{}',
    watermark_settings JSONB DEFAULT '{}',
    metadata_settings JSONB DEFAULT '{}',
    
    -- Collaboration preferences
    collaboration_settings JSONB DEFAULT '{}',
    auto_accept_collaborations BOOLEAN DEFAULT FALSE,
    collaboration_rate_limits JSONB DEFAULT '{}',
    
    -- AI and automation preferences
    ai_generation_enabled BOOLEAN DEFAULT TRUE,
    ai_analysis_enabled BOOLEAN DEFAULT TRUE,
    auto_tagging_enabled BOOLEAN DEFAULT TRUE,
    content_optimization BOOLEAN DEFAULT TRUE,
    
    -- Platform integration settings
    auto_post_settings JSONB DEFAULT '{}',
    cross_platform_sync BOOLEAN DEFAULT FALSE,
    platform_specific_settings JSONB DEFAULT '{}',
    
    -- Security preferences
    two_factor_required BOOLEAN DEFAULT FALSE,
    session_timeout INTEGER DEFAULT 480,  -- 8 hours in minutes
    ip_restrictions INET[],
    trusted_devices JSONB DEFAULT '[]',
    
    -- Language and localization
    preferred_language VARCHAR(10) DEFAULT 'en',
    date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
    time_format VARCHAR(10) DEFAULT '24h',
    currency VARCHAR(3) DEFAULT 'USD',
    number_format VARCHAR(20) DEFAULT 'US',
    
    -- Dashboard and UI preferences
    dashboard_layout JSONB DEFAULT '{}',
    theme VARCHAR(20) DEFAULT 'light',
    sidebar_collapsed BOOLEAN DEFAULT FALSE,
    advanced_mode BOOLEAN DEFAULT FALSE,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER AUTHENTICATION LOGS
-- ============================================================================

-- Authentication and security event logging
CREATE TABLE IF NOT EXISTS user_auth_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users_enhanced(id) ON DELETE SET NULL,
    
    -- Event information
    event_type VARCHAR(50) NOT NULL,
    event_status VARCHAR(20) NOT NULL,
    event_description TEXT,
    
    -- Authentication details
    login_method VARCHAR(50),
    mfa_method VARCHAR(50),
    oauth_provider VARCHAR(50),
    
    -- Session information
    session_id VARCHAR(255),
    user_agent TEXT,
    ip_address INET,
    country VARCHAR(3),
    city VARCHAR(100),
    
    -- Security metadata
    risk_score INTEGER DEFAULT 0,
    anomaly_detected BOOLEAN DEFAULT FALSE,
    blocked BOOLEAN DEFAULT FALSE,
    
    -- Audit timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- USER DEVICES TABLE
-- ============================================================================

-- Track user devices for security and analytics
CREATE TABLE IF NOT EXISTS user_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users_enhanced(id) ON DELETE CASCADE,
    
    -- Device identification
    device_id VARCHAR(255) UNIQUE NOT NULL,
    device_name VARCHAR(200),
    device_type VARCHAR(50),
    
    -- Device information
    platform VARCHAR(50),
    browser VARCHAR(100),
    browser_version VARCHAR(50),
    os VARCHAR(100),
    os_version VARCHAR(50),
    
    -- Device settings
    is_trusted BOOLEAN DEFAULT FALSE,
    is_primary BOOLEAN DEFAULT FALSE,
    push_notifications_enabled BOOLEAN DEFAULT TRUE,
    
    -- Security information
    fingerprint_hash VARCHAR(255),
    last_ip_address INET,
    
    -- Activity tracking
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_logins INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Audit timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Primary lookup indexes
CREATE INDEX idx_users_enhanced_email ON users_enhanced(email);
CREATE INDEX idx_users_enhanced_username ON users_enhanced(username);
CREATE INDEX idx_users_enhanced_creator_type ON users_enhanced(creator_type);
CREATE INDEX idx_users_enhanced_subscription_tier ON users_enhanced(subscription_tier);
CREATE INDEX idx_users_enhanced_account_status ON users_enhanced(account_status);
CREATE INDEX idx_users_enhanced_created_at ON users_enhanced(created_at);
CREATE INDEX idx_users_enhanced_last_activity ON users_enhanced(last_activity);

-- Profile indexes
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_availability ON user_profiles(availability_status);
CREATE INDEX idx_user_profiles_featured ON user_profiles(featured_creator);

-- Settings indexes
CREATE INDEX idx_user_settings_user_id ON user_settings(user_id);

-- Authentication log indexes
CREATE INDEX idx_user_auth_logs_user_id ON user_auth_logs(user_id);
CREATE INDEX idx_user_auth_logs_event_type ON user_auth_logs(event_type);
CREATE INDEX idx_user_auth_logs_created_at ON user_auth_logs(created_at);
CREATE INDEX idx_user_auth_logs_ip_address ON user_auth_logs(ip_address);

-- Device indexes
CREATE INDEX idx_user_devices_user_id ON user_devices(user_id);
CREATE INDEX idx_user_devices_device_id ON user_devices(device_id);
CREATE INDEX idx_user_devices_is_trusted ON user_devices(is_trusted);
CREATE INDEX idx_user_devices_last_seen ON user_devices(last_seen);

-- Composite indexes for common queries
CREATE INDEX idx_users_enhanced_type_tier ON users_enhanced(creator_type, subscription_tier);
CREATE INDEX idx_users_enhanced_status_activity ON users_enhanced(account_status, last_activity);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_enhanced_updated_at 
    BEFORE UPDATE ON users_enhanced 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at 
    BEFORE UPDATE ON user_settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_devices_updated_at 
    BEFORE UPDATE ON user_devices 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Comprehensive user view combining all user data
CREATE OR REPLACE VIEW user_complete_profile AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.display_name,
    u.creator_type,
    u.creator_verified,
    u.subscription_tier,
    u.account_status,
    u.last_activity,
    u.created_at,
    
    -- Profile information
    p.professional_title,
    p.years_experience,
    p.portfolio_url,
    p.availability_status,
    p.average_rating,
    p.completion_rate,
    
    -- Statistics
    u.total_content_uploads,
    u.total_collaborations,
    u.content_views,
    u.follower_count
    
FROM users_enhanced u
LEFT JOIN user_profiles p ON u.id = p.user_id
WHERE u.deleted_at IS NULL;

-- Active creators view
CREATE OR REPLACE VIEW active_creators AS
SELECT 
    u.*,
    p.availability_status,
    p.average_rating,
    p.portfolio_url
FROM users_enhanced u
LEFT JOIN user_profiles p ON u.id = p.user_id
WHERE u.account_status = 'active' 
    AND u.creator_type IS NOT NULL
    AND u.deleted_at IS NULL;

-- ============================================================================
-- SECURITY POLICIES (Row Level Security)
-- ============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE users_enhanced ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_auth_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_devices ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY user_own_data ON users_enhanced
    FOR ALL TO authenticated_users
    USING (id = current_user_id());

CREATE POLICY user_own_profile ON user_profiles
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());

CREATE POLICY user_own_settings ON user_settings
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());

CREATE POLICY user_own_devices ON user_devices
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());

-- Auth logs are read-only for users
CREATE POLICY user_own_auth_logs ON user_auth_logs
    FOR SELECT TO authenticated_users
    USING (user_id = current_user_id());

-- Admin access policy
CREATE POLICY admin_access ON users_enhanced
    FOR ALL TO admin_users
    USING (true);

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to get current user ID (to be implemented by application)
CREATE OR REPLACE FUNCTION current_user_id()
RETURNS UUID AS $$
BEGIN
    -- This would be implemented by the application
    -- Return the current authenticated user's ID
    RETURN '00000000-0000-0000-0000-000000000000'::UUID;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create complete user profile
CREATE OR REPLACE FUNCTION create_user_with_profile(
    p_username VARCHAR(50),
    p_email CITEXT,
    p_password_hash VARCHAR(255),
    p_creator_type VARCHAR(50) DEFAULT NULL,
    p_display_name VARCHAR(150) DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    new_user_id UUID;
BEGIN
    -- Insert user
    INSERT INTO users_enhanced (username, email, password_hash, password_salt, creator_type, display_name)
    VALUES (p_username, p_email, p_password_hash, gen_salt('bf'), p_creator_type, p_display_name)
    RETURNING id INTO new_user_id;
    
    -- Insert default profile
    INSERT INTO user_profiles (user_id) VALUES (new_user_id);
    
    -- Insert default settings
    INSERT INTO user_settings (user_id) VALUES (new_user_id);
    
    RETURN new_user_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE users_enhanced IS 'Enhanced users table with comprehensive creator platform features';
COMMENT ON TABLE user_profiles IS 'Extended profile information for creators and professionals';
COMMENT ON TABLE user_settings IS 'User preferences and configuration settings';
COMMENT ON TABLE user_auth_logs IS 'Authentication and security event logging';
COMMENT ON TABLE user_devices IS 'User device tracking for security and analytics';

-- Column comments for key fields
COMMENT ON COLUMN users_enhanced.creator_type IS 'Type of creator: musician, photographer, blogger, etc.';
COMMENT ON COLUMN users_enhanced.subscription_tier IS 'Subscription level: free, professional, enterprise';
COMMENT ON COLUMN users_enhanced.social_profiles IS 'JSON object containing social media profile links';
COMMENT ON COLUMN users_enhanced.platform_connections IS 'JSON object tracking connected platform accounts';
COMMENT ON COLUMN user_profiles.featured_content IS 'JSON array of featured content items for portfolio';
COMMENT ON COLUMN user_settings.collaboration_settings IS 'JSON object with collaboration preferences and rules';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================