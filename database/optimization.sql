-- Database Optimization for Ainflue Platform
-- PostgreSQL performance tuning and indexing strategy
--
-- Author: Fahed Mlaiel (mlaiel@live.de)
-- Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

-- ============================================================================
-- PERFORMANCE CONFIGURATION
-- ============================================================================

-- Shared memory settings (adjust based on available RAM)
-- For 16GB RAM server:
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET work_mem = '256MB';

-- Connection settings
ALTER SYSTEM SET max_connections = '200';
ALTER SYSTEM SET max_prepared_transactions = '100';

-- Checkpoint settings for performance
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '64MB';
ALTER SYSTEM SET wal_writer_delay = '200ms';

-- Query optimization
ALTER SYSTEM SET random_page_cost = 1.1; -- For SSD storage
ALTER SYSTEM SET seq_page_cost = 1.0;
ALTER SYSTEM SET cpu_tuple_cost = 0.01;
ALTER SYSTEM SET cpu_index_tuple_cost = 0.005;
ALTER SYSTEM SET cpu_operator_cost = 0.0025;

-- Logging for monitoring
ALTER SYSTEM SET log_min_duration_statement = '1000ms'; -- Log slow queries
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_lock_waits = on;

-- Reload configuration
SELECT pg_reload_conf();

-- ============================================================================
-- CORE TABLES CREATION AND OPTIMIZATION
-- ============================================================================

-- Users table with optimized structure
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    user_type VARCHAR(20) NOT NULL DEFAULT 'creator',
    profile_data JSONB,
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Content table for all content types
CREATE TABLE IF NOT EXISTS content (
    content_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    content_type VARCHAR(50) NOT NULL, -- 'audio', 'video', 'image', 'text'
    file_path TEXT,
    file_size BIGINT,
    mime_type VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    tags TEXT[],
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'published', 'archived'
    visibility VARCHAR(20) DEFAULT 'private', -- 'private', 'public', 'unlisted'
    ai_analysis JSONB,
    seo_data JSONB,
    distribution_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE
);

-- Collaborations table
CREATE TABLE IF NOT EXISTS collaborations (
    collaboration_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_title VARCHAR(500) NOT NULL,
    project_description TEXT,
    creator_id UUID NOT NULL REFERENCES users(user_id),
    collaborators UUID[] DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'open', -- 'open', 'in_progress', 'completed', 'cancelled'
    budget_min DECIMAL(12,2),
    budget_max DECIMAL(12,2),
    deadline TIMESTAMP WITH TIME ZONE,
    skills_required TEXT[],
    requirements JSONB,
    ai_matching_score DECIMAL(3,2),
    workflow_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Gamification points and achievements
CREATE TABLE IF NOT EXISTS user_points (
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    points_type VARCHAR(50) NOT NULL, -- 'content', 'collaboration', 'social', etc.
    points_earned INTEGER NOT NULL DEFAULT 0,
    multiplier DECIMAL(3,2) DEFAULT 1.0,
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    action_details JSONB,
    PRIMARY KEY (user_id, points_type, earned_at)
);

-- SEO and analytics data
CREATE TABLE IF NOT EXISTS seo_analytics (
    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES content(content_id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    keywords TEXT[],
    search_volume JSONB,
    ranking_data JSONB,
    optimization_score DECIMAL(3,2),
    analytics_date DATE NOT NULL,
    metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Distribution tracking
CREATE TABLE IF NOT EXISTS distribution_tracking (
    distribution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL REFERENCES content(content_id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_content_id VARCHAR(255),
    status VARCHAR(20) NOT NULL, -- 'pending', 'uploaded', 'published', 'failed'
    upload_date TIMESTAMP WITH TIME ZONE,
    publish_date TIMESTAMP WITH TIME ZONE,
    metrics JSONB,
    error_details JSONB,
    sync_status VARCHAR(20) DEFAULT 'synced',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Security audit log
CREATE TABLE IF NOT EXISTS security_audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    threat_level VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Validation results cache
CREATE TABLE IF NOT EXISTS validation_cache (
    cache_key VARCHAR(64) PRIMARY KEY,
    content_hash VARCHAR(64) NOT NULL,
    validation_type VARCHAR(50) NOT NULL,
    validation_level VARCHAR(20) NOT NULL,
    result JSONB NOT NULL,
    confidence_score DECIMAL(3,2),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Monetization transactions
CREATE TABLE IF NOT EXISTS monetization_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    content_id UUID REFERENCES content(content_id),
    transaction_type VARCHAR(50) NOT NULL, -- 'payment', 'revenue', 'fee', 'payout'
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    payment_method VARCHAR(50),
    blockchain_network VARCHAR(30),
    transaction_hash VARCHAR(128),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    platform_source VARCHAR(50),
    metadata JSONB,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

-- Users table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_type_active ON users(user_type, is_active);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_last_login ON users(last_login);

-- Content table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_user_id ON content(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_type ON content(content_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_status ON content(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_visibility ON content(visibility);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_created_at ON content(created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_published_at ON content(published_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_tags ON content USING GIN(tags);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_metadata ON content USING GIN(metadata);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_user_status ON content(user_id, status);

-- Collaborations table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_collaborations_creator ON collaborations(creator_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_collaborations_status ON collaborations(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_collaborations_deadline ON collaborations(deadline);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_collaborations_budget ON collaborations(budget_min, budget_max);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_collaborations_skills ON collaborations USING GIN(skills_required);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_collaborations_ai_score ON collaborations(ai_matching_score);

-- User points indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_points_user_type ON user_points(user_id, points_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_points_earned_at ON user_points(earned_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_points_type_points ON user_points(points_type, points_earned);

-- SEO analytics indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_seo_content_platform ON seo_analytics(content_id, platform);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_seo_analytics_date ON seo_analytics(analytics_date);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_seo_keywords ON seo_analytics USING GIN(keywords);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_seo_optimization_score ON seo_analytics(optimization_score);

-- Distribution tracking indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_distribution_content ON distribution_tracking(content_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_distribution_platform ON distribution_tracking(platform);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_distribution_status ON distribution_tracking(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_distribution_upload_date ON distribution_tracking(upload_date);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_distribution_sync_status ON distribution_tracking(sync_status);

-- Security audit log indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_user_id ON security_audit_log(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_action ON security_audit_log(action);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_created_at ON security_audit_log(created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_threat_level ON security_audit_log(threat_level);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_ip_address ON security_audit_log(ip_address);

-- Validation cache indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_validation_content_hash ON validation_cache(content_hash);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_validation_type_level ON validation_cache(validation_type, validation_level);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_validation_expires_at ON validation_cache(expires_at);

-- Monetization transaction indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_monetization_user_id ON monetization_transactions(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_monetization_content_id ON monetization_transactions(content_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_monetization_type ON monetization_transactions(transaction_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_monetization_status ON monetization_transactions(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_monetization_created_at ON monetization_transactions(created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_monetization_amount ON monetization_transactions(amount);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_monetization_currency ON monetization_transactions(currency);

-- ============================================================================
-- MATERIALIZED VIEWS FOR ANALYTICS
-- ============================================================================

-- User statistics materialized view
CREATE MATERIALIZED VIEW IF NOT EXISTS user_stats AS
SELECT 
    u.user_id,
    u.username,
    u.user_type,
    COUNT(DISTINCT c.content_id) as content_count,
    COUNT(DISTINCT col.collaboration_id) as collaboration_count,
    COALESCE(SUM(up.points_earned), 0) as total_points,
    MAX(c.created_at) as last_content_date,
    u.created_at as join_date
FROM users u
LEFT JOIN content c ON u.user_id = c.user_id AND c.status = 'published'
LEFT JOIN collaborations col ON u.user_id = col.creator_id
LEFT JOIN user_points up ON u.user_id = up.user_id
WHERE u.is_active = true
GROUP BY u.user_id, u.username, u.user_type, u.created_at;

CREATE UNIQUE INDEX ON user_stats(user_id);

-- Content performance materialized view
CREATE MATERIALIZED VIEW IF NOT EXISTS content_performance AS
SELECT 
    c.content_id,
    c.title,
    c.content_type,
    c.user_id,
    COUNT(DISTINCT dt.platform) as platform_count,
    AVG(sa.optimization_score) as avg_seo_score,
    COUNT(DISTINCT sa.record_id) as seo_records,
    c.created_at,
    c.published_at
FROM content c
LEFT JOIN distribution_tracking dt ON c.content_id = dt.content_id
LEFT JOIN seo_analytics sa ON c.content_id = sa.content_id
WHERE c.status = 'published'
GROUP BY c.content_id, c.title, c.content_type, c.user_id, c.created_at, c.published_at;

CREATE UNIQUE INDEX ON content_performance(content_id);

-- Platform analytics materialized view
CREATE MATERIALIZED VIEW IF NOT EXISTS platform_analytics AS
SELECT 
    dt.platform,
    COUNT(DISTINCT dt.content_id) as content_count,
    COUNT(CASE WHEN dt.status = 'published' THEN 1 END) as published_count,
    COUNT(CASE WHEN dt.status = 'failed' THEN 1 END) as failed_count,
    AVG(CASE WHEN dt.status = 'published' THEN 
        EXTRACT(EPOCH FROM (dt.publish_date - dt.upload_date))/3600 
    END) as avg_publish_time_hours,
    DATE_TRUNC('day', dt.created_at) as activity_date
FROM distribution_tracking dt
GROUP BY dt.platform, DATE_TRUNC('day', dt.created_at);

CREATE INDEX ON platform_analytics(platform, activity_date);

-- ============================================================================
-- STORED PROCEDURES FOR COMMON OPERATIONS
-- ============================================================================

-- Update user statistics
CREATE OR REPLACE FUNCTION update_user_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY user_stats;
    REFRESH MATERIALIZED VIEW CONCURRENTLY content_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY platform_analytics;
END;
$$ LANGUAGE plpgsql;

-- Clean up expired validation cache
CREATE OR REPLACE FUNCTION cleanup_validation_cache()
RETURNS integer AS $$
DECLARE
    deleted_count integer;
BEGIN
    DELETE FROM validation_cache WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Calculate user points efficiently
CREATE OR REPLACE FUNCTION calculate_user_total_points(p_user_id UUID)
RETURNS integer AS $$
DECLARE
    total_points integer;
BEGIN
    SELECT COALESCE(SUM(points_earned * multiplier), 0)::integer
    INTO total_points
    FROM user_points
    WHERE user_id = p_user_id;
    
    RETURN total_points;
END;
$$ LANGUAGE plpgsql;

-- Get content recommendations based on user activity
CREATE OR REPLACE FUNCTION get_content_recommendations(p_user_id UUID, p_limit integer DEFAULT 10)
RETURNS TABLE(
    content_id UUID,
    title VARCHAR,
    content_type VARCHAR,
    creator_username VARCHAR,
    similarity_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.content_id,
        c.title,
        c.content_type,
        u.username as creator_username,
        -- Simple similarity based on tags and content type
        CASE 
            WHEN c.content_type = (
                SELECT content_type 
                FROM content 
                WHERE user_id = p_user_id 
                ORDER BY created_at DESC 
                LIMIT 1
            ) THEN 0.8
            ELSE 0.5
        END as similarity_score
    FROM content c
    JOIN users u ON c.user_id = u.user_id
    WHERE c.status = 'published' 
    AND c.visibility = 'public'
    AND c.user_id != p_user_id
    ORDER BY similarity_score DESC, c.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- AUTOMATED MAINTENANCE TASKS
-- ============================================================================

-- Schedule regular VACUUM and ANALYZE
-- (These would typically be set up in crontab or PostgreSQL scheduler)

-- Update table statistics daily
-- 0 2 * * * psql -d ainflue -c "ANALYZE;"

-- Update materialized views every 15 minutes
-- */15 * * * * psql -d ainflue -c "SELECT update_user_stats();"

-- Clean up expired cache every hour
-- 0 * * * * psql -d ainflue -c "SELECT cleanup_validation_cache();"

-- ============================================================================
-- MONITORING QUERIES
-- ============================================================================

-- Query to monitor slow queries
CREATE OR REPLACE VIEW slow_queries AS
SELECT 
    query,
    calls,
    total_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_time DESC;

-- Query to monitor table sizes
CREATE OR REPLACE VIEW table_sizes AS
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Query to monitor index usage
CREATE OR REPLACE VIEW index_usage AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Performance monitoring function
CREATE OR REPLACE FUNCTION get_performance_stats()
RETURNS TABLE(
    metric_name TEXT,
    metric_value TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'Database Size'::TEXT, pg_size_pretty(pg_database_size(current_database()))::TEXT
    UNION ALL
    SELECT 'Active Connections', COUNT(*)::TEXT FROM pg_stat_activity WHERE state = 'active'
    UNION ALL
    SELECT 'Cache Hit Ratio', ROUND(100.0 * sum(blks_hit) / (sum(blks_hit) + sum(blks_read)), 2)::TEXT || '%'
    FROM pg_stat_database WHERE datname = current_database()
    UNION ALL
    SELECT 'Total Transactions', sum(xact_commit + xact_rollback)::TEXT FROM pg_stat_database;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- BACKUP AND MAINTENANCE SCRIPTS
-- ============================================================================

-- Function to create a database backup
CREATE OR REPLACE FUNCTION create_backup(backup_path TEXT DEFAULT '/backups/')
RETURNS TEXT AS $$
DECLARE
    backup_filename TEXT;
    backup_command TEXT;
BEGIN
    backup_filename := backup_path || 'ainflue_backup_' || to_char(CURRENT_TIMESTAMP, 'YYYY_MM_DD_HH24_MI_SS') || '.sql';
    backup_command := 'pg_dump -h localhost -U postgres -d ainflue > ' || backup_filename;
    
    -- Note: This would need to be executed outside PostgreSQL
    RETURN 'Backup command: ' || backup_command;
END;
$$ LANGUAGE plpgsql;

-- Final configuration reload
SELECT pg_reload_conf();

-- Display optimization summary
SELECT 'Database optimization complete!' as status,
       'Tables created: 9' as tables,
       'Indexes created: 35+' as indexes,
       'Materialized views: 3' as views,
       'Stored procedures: 5+' as procedures;