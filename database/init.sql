#!/bin/bash
# PostgreSQL Master/Slave Setup and Optimization Script for Ainflue Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -e

echo "🚀 Initializing Ainflue PostgreSQL Master Database..."

# Create replication user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create replication user
    CREATE USER replication_user REPLICATION LOGIN ENCRYPTED PASSWORD '$POSTGRES_REPLICATION_PASSWORD';
    
    -- Grant necessary privileges
    GRANT USAGE ON SCHEMA public TO replication_user;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO replication_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO replication_user;
    
    -- Create pg_stat_statements extension for query monitoring
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
    
    -- Create btree_gin extension for optimized indexes
    CREATE EXTENSION IF NOT EXISTS btree_gin;
    
    -- Create uuid extension for content fingerprinting
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Create crypto extension for security
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
    
    -- Create full text search extensions for content analysis
    CREATE EXTENSION IF NOT EXISTS unaccent;
    
    EOSQL

echo "📊 Creating optimized indexes for content protection..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    -- Performance monitoring views
    CREATE OR REPLACE VIEW pg_stat_activity_summary AS
    SELECT 
        state,
        COUNT(*) as connection_count,
        AVG(EXTRACT(epoch FROM (now() - query_start))) as avg_query_duration
    FROM pg_stat_activity 
    WHERE state IS NOT NULL 
    GROUP BY state;

    -- Slow query monitoring
    CREATE OR REPLACE VIEW slow_queries AS
    SELECT 
        query,
        calls,
        total_time,
        mean_time,
        rows,
        100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
    FROM pg_stat_statements 
    ORDER BY mean_time DESC;

    -- Index usage statistics
    CREATE OR REPLACE VIEW index_usage_stats AS
    SELECT 
        schemaname,
        tablename,
        indexname,
        idx_tup_read,
        idx_tup_fetch,
        CASE WHEN idx_tup_read > 0 
             THEN round((idx_tup_fetch::numeric / idx_tup_read::numeric) * 100, 2)
             ELSE 0 
        END AS usage_ratio
    FROM pg_stat_user_indexes
    ORDER BY usage_ratio DESC;

    -- Table size monitoring
    CREATE OR REPLACE VIEW table_sizes AS
    SELECT 
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
        pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
    FROM pg_tables 
    WHERE schemaname = 'public'
    ORDER BY size_bytes DESC;

EOSQL

echo "🔧 Setting up database optimization parameters..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    -- Optimize for content fingerprinting workloads
    ALTER SYSTEM SET effective_cache_size = '1GB';
    ALTER SYSTEM SET shared_buffers = '256MB';
    ALTER SYSTEM SET work_mem = '8MB';
    ALTER SYSTEM SET maintenance_work_mem = '128MB';
    
    -- Optimize for high write workloads (content uploads)
    ALTER SYSTEM SET checkpoint_timeout = '15min';
    ALTER SYSTEM SET checkpoint_completion_target = 0.9;
    ALTER SYSTEM SET wal_buffers = '16MB';
    
    -- Optimize autovacuum for content protection tables
    ALTER SYSTEM SET autovacuum_naptime = '30s';
    ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.1;
    ALTER SYSTEM SET autovacuum_analyze_scale_factor = 0.05;
    
    -- Enable query monitoring
    ALTER SYSTEM SET log_min_duration_statement = 1000;
    ALTER SYSTEM SET log_statement = 'ddl';
    ALTER SYSTEM SET track_io_timing = 'on';
    
    SELECT pg_reload_conf();

EOSQL

echo "📈 Creating backup and monitoring procedures..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    -- Function to get database health metrics
    CREATE OR REPLACE FUNCTION get_db_health_metrics()
    RETURNS TABLE(
        metric_name TEXT,
        metric_value TEXT,
        metric_description TEXT
    ) AS \$\$
    BEGIN
        RETURN QUERY
        SELECT 'active_connections'::TEXT, 
               COUNT(*)::TEXT, 
               'Number of active database connections'::TEXT
        FROM pg_stat_activity WHERE state = 'active'
        UNION ALL
        SELECT 'cache_hit_ratio'::TEXT,
               ROUND(100.0 * sum(blks_hit) / (sum(blks_hit) + sum(blks_read)), 2)::TEXT || '%',
               'Cache hit ratio percentage'::TEXT
        FROM pg_stat_database
        UNION ALL
        SELECT 'total_queries'::TEXT,
               sum(numbackends)::TEXT,
               'Total number of backend processes'::TEXT
        FROM pg_stat_database;
    END;
    \$\$ LANGUAGE plpgsql;

    -- Function to optimize indexes
    CREATE OR REPLACE FUNCTION optimize_indexes()
    RETURNS TEXT AS \$\$
    DECLARE
        rec RECORD;
        result TEXT := '';
    BEGIN
        FOR rec IN 
            SELECT schemaname, tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        LOOP
            EXECUTE 'REINDEX TABLE ' || rec.schemaname || '.' || rec.tablename;
            result := result || 'Reindexed ' || rec.tablename || E'\n';
        END LOOP;
        RETURN result;
    END;
    \$\$ LANGUAGE plpgsql;

EOSQL

echo "✅ PostgreSQL Master database initialization completed!"
echo "🔄 Ready for replication setup..."