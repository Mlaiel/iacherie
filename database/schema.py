"""Database Schema Creation
SQL schema for PostgreSQL database.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from sqlalchemy import text
from ..core.database import database_manager
from ..core.logging import logger


async def create_tables():
    """
Create all database tables"""
    try:
        async with database_manager.get_postgres_session() as session:
            # Users table
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(32) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    creator_type VARCHAR(20) NOT NULL CHECK (creator_type IN ('musician', 'blogger', 'photographer', 'influencer', 'comedian', 'writer', 'other')),
                    tenant_id VARCHAR(16) NOT NULL,
                    is_verified BOOLEAN DEFAULT false,
                    subscription_tier VARCHAR(20) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'premium', 'professional')),
                    active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Content table
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS content (
                    id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(32) REFERENCES users(id),
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    content_type VARCHAR(20) NOT NULL CHECK (content_type IN ('audio', 'video', 'image', 'text')),
                    filename VARCHAR(255) NOT NULL,
                    file_size BIGINT NOT NULL,
                    fingerprint_id VARCHAR(36),
                    status VARCHAR(20) DEFAULT 'processing' CHECK (status IN ('processing', 'processed', 'failed', 'deleted')),
                    active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Content monitoring table
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS content_monitoring (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(32) REFERENCES users(id),
                    content_id VARCHAR(36) REFERENCES content(id),
                    content_type VARCHAR(20) NOT NULL,
                    fingerprint_data JSONB NOT NULL,
                    platforms JSONB NOT NULL,
                    monitoring_frequency INTEGER DEFAULT 24,
                    alert_threshold FLOAT DEFAULT 0.85,
                    active BOOLEAN DEFAULT true,
                    last_checked TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Protection violations table
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS protection_violations (
                    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
                    original_content_id VARCHAR(36) REFERENCES content(id),
                    user_id VARCHAR(32) REFERENCES users(id),
                    platform VARCHAR(50) NOT NULL,
                    violation_url TEXT NOT NULL,
                    similarity_score FLOAT NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending_review' CHECK (status IN ('pending_review', 'confirmed', 'false_positive', 'resolved')),
                    evidence_data JSONB,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP
                )
            """))
            
            # Platform connections table
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS platform_connections (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(32) REFERENCES users(id),
                    platform VARCHAR(50) NOT NULL,
                    platform_username VARCHAR(100),
                    access_token TEXT,
                    refresh_token TEXT,
                    token_expires_at TIMESTAMP,
                    active BOOLEAN DEFAULT true,
                    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, platform)
                )
            """))
            
            # Create indexes for better performance
            await session.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS idx_content_user_id ON content(user_id)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS idx_content_type ON content(content_type)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS idx_content_monitoring_user_id ON content_monitoring(user_id)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS idx_content_monitoring_content_id ON content_monitoring(content_id)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS idx_violations_user_id ON protection_violations(user_id)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS idx_violations_content_id ON protection_violations(original_content_id)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS idx_violations_platform ON protection_violations(platform)"))
            await session.execute(text("CREATE INDEX IF NOT EXISTS idx_platform_connections_user_id ON platform_connections(user_id)"))
            
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise


async def drop_tables():
    """Drop all database tables (use with caution)"""
    try:
        async with database_manager.get_postgres_session() as session:
            await session.execute(text("DROP TABLE IF EXISTS platform_connections CASCADE"))
            await session.execute(text("DROP TABLE IF EXISTS protection_violations CASCADE"))
            await session.execute(text("DROP TABLE IF EXISTS content_monitoring CASCADE"))
            await session.execute(text("DROP TABLE IF EXISTS content CASCADE"))
            await session.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            
        logger.info("Database tables dropped successfully")
        
    except Exception as e:
        logger.error(f"Failed to drop database tables: {str(e)}")
        raise