"""
🗂️ Schema Manager - Enterprise Database Schema Evolution Controller
===================================================================

Ultra-advanced database schema management system for IA Influencer Agent:
- Dynamic schema versioning and evolution tracking
- Multi-tenant schema isolation and synchronization
- Content protection schema optimization
- Fingerprinting database structure management
- Monetization data model evolution

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This schema management system is protected intellectual property.
Contact mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from dataclasses import dataclass, field
import json
import hashlib
from pathlib import Path

from sqlalchemy import (
    create_engine, MetaData, Table, Column, String, DateTime, Boolean, 
    Integer, JSON, Text, Float, ARRAY, Index, ForeignKey, UniqueConstraint,
    CheckConstraint, text, inspect, select, and_, or_
)
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects import postgresql
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

logger = logging.getLogger(__name__)
Base = declarative_base()


class SchemaVersion(Enum):
    """Schema version management"""
    V1_0_0 = "1.0.0"    # Initial schema
    V1_1_0 = "1.1.0"    # Content protection additions
    V1_2_0 = "1.2.0"    # Fingerprinting enhancements
    V1_3_0 = "1.3.0"    # Monetization features
    V2_0_0 = "2.0.0"    # Major platform integration
    V2_1_0 = "2.1.0"    # Analytics improvements
    V2_2_0 = "2.2.0"    # Collaboration features
    LATEST = "2.2.0"


class SchemaComponent(Enum):
    """Schema component categories"""
    CORE = "core"                      # Core user and content tables
    PROTECTION = "protection"          # Content protection tables
    FINGERPRINT = "fingerprint"        # Fingerprinting system
    MONETIZATION = "monetization"      # Revenue tracking
    ANALYTICS = "analytics"            # Analytics and reporting
    COLLABORATION = "collaboration"    # Creator collaboration
    SECURITY = "security"              # Security and audit
    INTEGRATION = "integration"        # Platform integrations


@dataclass
class SchemaChange:
    """Schema change specification"""
    change_id: str
    version: SchemaVersion
    component: SchemaComponent
    operation: str  # CREATE, ALTER, DROP, INDEX
    target: str     # table, column, index name
    sql_statement: str
    rollback_statement: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    validation_query: Optional[str] = None


@dataclass
class SchemaState:
    """Current schema state information"""
    current_version: SchemaVersion
    installed_components: Set[SchemaComponent]
    pending_changes: List[SchemaChange]
    last_update: datetime
    schema_hash: str
    validation_status: bool = True


class SchemaManager:
    """
    Enterprise-grade database schema management system
    
    Manages complete database schema evolution for IA Influencer Agent:
    - Content protection and fingerprinting tables
    - Creator monetization and collaboration schemas
    - Multi-tenant data isolation structures
    - Performance optimization indices
    - Security and audit logging tables
    """
    
    def __init__(self, database_url: str, tenant_id: Optional[str] = None):
        self.database_url = database_url
        self.tenant_id = tenant_id
        self.engine = create_engine(database_url, echo=False)
        self.session_maker = sessionmaker(bind=self.engine)
        self.metadata = MetaData()
        self.schema_changes: List[SchemaChange] = []
        
    async def initialize_schema(self, target_version: SchemaVersion = SchemaVersion.LATEST) -> SchemaState:
        """
        Initialize complete database schema
        
        Args:
            target_version: Target schema version to achieve
            
        Returns:
            Current schema state after initialization
        """
        logger.info(f"Initializing schema to version {target_version.value}")
        
        try:
            # Create migration tracking table
            await self._create_migration_tracking_tables()
            
            # Get current schema state
            current_state = await self.get_schema_state()
            
            # Apply schema changes to reach target version
            if current_state.current_version != target_version:
                await self._apply_schema_evolution(current_state.current_version, target_version)
                
            # Validate final schema state
            final_state = await self.get_schema_state()
            await self._validate_schema_integrity(final_state)
            
            logger.info(f"Schema initialization completed: {final_state.current_version.value}")
            return final_state
            
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            raise
            
    async def get_schema_state(self) -> SchemaState:
        """Get current database schema state"""
        async with self._get_session() as session:
            try:
                # Get current version
                version_query = text("""
                    SELECT version FROM schema_version 
                    WHERE is_current = true
                    ORDER BY applied_at DESC LIMIT 1
                """)
                version_result = await session.execute(version_query)
                current_version_row = version_result.fetchone()
                current_version = SchemaVersion(current_version_row[0]) if current_version_row else SchemaVersion.V1_0_0
                
                # Get installed components
                components_query = text("""
                    SELECT DISTINCT component FROM schema_changes 
                    WHERE status = 'applied'
                """)
                components_result = await session.execute(components_query)
                installed_components = {SchemaComponent(row[0]) for row in components_result.fetchall()}
                
                # Get pending changes
                pending_query = text("""
                    SELECT change_id, version, component, operation, target, sql_statement, rollback_statement
                    FROM schema_changes 
                    WHERE status = 'pending'
                    ORDER BY created_at
                """)
                pending_result = await session.execute(pending_query)
                pending_changes = [
                    SchemaChange(
                        change_id=row[0],
                        version=SchemaVersion(row[1]),
                        component=SchemaComponent(row[2]),
                        operation=row[3],
                        target=row[4],
                        sql_statement=row[5],
                        rollback_statement=row[6]
                    )
                    for row in pending_result.fetchall()
                ]
                
                # Calculate schema hash
                schema_hash = await self._calculate_schema_hash()
                
                return SchemaState(
                    current_version=current_version,
                    installed_components=installed_components,
                    pending_changes=pending_changes,
                    last_update=datetime.now(timezone.utc),
                    schema_hash=schema_hash
                )
                
            except SQLAlchemyError as e:
                logger.error(f"Failed to get schema state: {e}")
                raise
                
    async def create_content_protection_schema(self) -> None:
        """Create content protection related tables"""
        schema_changes = [
            # Content fingerprints table
            SchemaChange(
                change_id="content_fingerprints_v1",
                version=SchemaVersion.V1_1_0,
                component=SchemaComponent.FINGERPRINT,
                operation="CREATE",
                target="content_fingerprints",
                sql_statement="""
                    CREATE TABLE IF NOT EXISTS content_fingerprints (
                        fingerprint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        content_id UUID NOT NULL,
                        user_id UUID NOT NULL,
                        tenant_id UUID,
                        content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('audio', 'video', 'image', 'text', 'composite')),
                        fingerprint_type VARCHAR(50) NOT NULL,
                        quality_level VARCHAR(20) NOT NULL CHECK (quality_level IN ('basic', 'standard', 'advanced', 'ultra')),
                        hash_fingerprint VARCHAR(255) NOT NULL,
                        feature_fingerprint BYTEA,
                        embedding_fingerprint BYTEA,
                        metadata JSONB DEFAULT '{}',
                        extraction_params JSONB DEFAULT '{}',
                        quality_metrics JSONB DEFAULT '{}',
                        file_size BIGINT,
                        duration_seconds FLOAT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        expires_at TIMESTAMP WITH TIME ZONE,
                        CONSTRAINT unique_content_fingerprint UNIQUE (content_id, fingerprint_type)
                    )
                """,
                rollback_statement="DROP TABLE IF EXISTS content_fingerprints CASCADE"
            ),
            
            # Protection alerts table
            SchemaChange(
                change_id="protection_alerts_v1",
                version=SchemaVersion.V1_1_0,
                component=SchemaComponent.PROTECTION,
                operation="CREATE",
                target="protection_alerts",
                sql_statement="""
                    CREATE TABLE IF NOT EXISTS protection_alerts (
                        alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        fingerprint_id UUID NOT NULL REFERENCES content_fingerprints(fingerprint_id),
                        detected_url TEXT NOT NULL,
                        platform VARCHAR(50) NOT NULL,
                        similarity_score FLOAT NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
                        alert_status VARCHAR(20) DEFAULT 'pending' CHECK (alert_status IN ('pending', 'investigating', 'confirmed', 'false_positive', 'resolved')),
                        evidence_data JSONB DEFAULT '{}',
                        screenshot_url TEXT,
                        detection_method VARCHAR(50),
                        priority_level VARCHAR(20) DEFAULT 'medium' CHECK (priority_level IN ('low', 'medium', 'high', 'critical')),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        resolved_at TIMESTAMP WITH TIME ZONE
                    )
                """,
                rollback_statement="DROP TABLE IF EXISTS protection_alerts CASCADE"
            ),
            
            # Revenue tracking table
            SchemaChange(
                change_id="revenue_tracking_v1",
                version=SchemaVersion.V1_3_0,
                component=SchemaComponent.MONETIZATION,
                operation="CREATE",
                target="revenue_tracking",
                sql_statement="""
                    CREATE TABLE IF NOT EXISTS revenue_tracking (
                        revenue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        user_id UUID NOT NULL,
                        content_id UUID REFERENCES content_fingerprints(content_id),
                        platform VARCHAR(50) NOT NULL,
                        revenue_amount DECIMAL(15,4) NOT NULL,
                        currency VARCHAR(3) DEFAULT 'EUR',
                        revenue_type VARCHAR(30) NOT NULL CHECK (revenue_type IN ('streaming', 'licensing', 'advertisement', 'subscription', 'download', 'other')),
                        period_start DATE NOT NULL,
                        period_end DATE NOT NULL,
                        transaction_id VARCHAR(100),
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        processed_at TIMESTAMP WITH TIME ZONE
                    )
                """,
                rollback_statement="DROP TABLE IF EXISTS revenue_tracking CASCADE"
            ),
            
            # Collaboration requests table
            SchemaChange(
                change_id="collaboration_requests_v1",
                version=SchemaVersion.V2_2_0,
                component=SchemaComponent.COLLABORATION,
                operation="CREATE",
                target="collaboration_requests",
                sql_statement="""
                    CREATE TABLE IF NOT EXISTS collaboration_requests (
                        request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        requester_id UUID NOT NULL,
                        target_creator_id UUID NOT NULL,
                        content_id UUID,
                        collaboration_type VARCHAR(50) NOT NULL CHECK (collaboration_type IN ('feature', 'remix', 'sample', 'cover', 'duet', 'collaboration')),
                        request_status VARCHAR(20) DEFAULT 'pending' CHECK (request_status IN ('pending', 'accepted', 'rejected', 'expired', 'completed')),
                        message TEXT,
                        terms JSONB DEFAULT '{}',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        expires_at TIMESTAMP WITH TIME ZONE,
                        responded_at TIMESTAMP WITH TIME ZONE,
                        completed_at TIMESTAMP WITH TIME ZONE
                    )
                """,
                rollback_statement="DROP TABLE IF EXISTS collaboration_requests CASCADE"
            )
        ]
        
        await self._apply_schema_changes(schema_changes)
        
    async def create_performance_indices(self) -> None:
        """Create performance optimization indices"""
        index_changes = [
            # Fingerprints indices
            SchemaChange(
                change_id="idx_fingerprints_content_type",
                version=SchemaVersion.V1_1_0,
                component=SchemaComponent.FINGERPRINT,
                operation="INDEX",
                target="content_fingerprints",
                sql_statement="CREATE INDEX IF NOT EXISTS idx_fingerprints_content_type ON content_fingerprints(content_type)",
                rollback_statement="DROP INDEX IF EXISTS idx_fingerprints_content_type"
            ),
            SchemaChange(
                change_id="idx_fingerprints_user_tenant",
                version=SchemaVersion.V1_1_0,
                component=SchemaComponent.FINGERPRINT,
                operation="INDEX",
                target="content_fingerprints",
                sql_statement="CREATE INDEX IF NOT EXISTS idx_fingerprints_user_tenant ON content_fingerprints(user_id, tenant_id)",
                rollback_statement="DROP INDEX IF EXISTS idx_fingerprints_user_tenant"
            ),
            SchemaChange(
                change_id="idx_fingerprints_hash",
                version=SchemaVersion.V1_1_0,
                component=SchemaComponent.FINGERPRINT,
                operation="INDEX",
                target="content_fingerprints",
                sql_statement="CREATE INDEX IF NOT EXISTS idx_fingerprints_hash ON content_fingerprints USING HASH (hash_fingerprint)",
                rollback_statement="DROP INDEX IF EXISTS idx_fingerprints_hash"
            ),
            SchemaChange(
                change_id="idx_fingerprints_created",
                version=SchemaVersion.V1_1_0,
                component=SchemaComponent.FINGERPRINT,
                operation="INDEX",
                target="content_fingerprints",
                sql_statement="CREATE INDEX IF NOT EXISTS idx_fingerprints_created ON content_fingerprints(created_at DESC)",
                rollback_statement="DROP INDEX IF EXISTS idx_fingerprints_created"
            ),
            
            # Protection alerts indices
            SchemaChange(
                change_id="idx_alerts_fingerprint",
                version=SchemaVersion.V1_1_0,
                component=SchemaComponent.PROTECTION,
                operation="INDEX",
                target="protection_alerts",
                sql_statement="CREATE INDEX IF NOT EXISTS idx_alerts_fingerprint ON protection_alerts(fingerprint_id)",
                rollback_statement="DROP INDEX IF EXISTS idx_alerts_fingerprint"
            ),
            SchemaChange(
                change_id="idx_alerts_platform_status",
                version=SchemaVersion.V1_1_0,
                component=SchemaComponent.PROTECTION,
                operation="INDEX",
                target="protection_alerts",
                sql_statement="CREATE INDEX IF NOT EXISTS idx_alerts_platform_status ON protection_alerts(platform, alert_status)",
                rollback_statement="DROP INDEX IF EXISTS idx_alerts_platform_status"
            ),
            
            # Revenue tracking indices
            SchemaChange(
                change_id="idx_revenue_user_period",
                version=SchemaVersion.V1_3_0,
                component=SchemaComponent.MONETIZATION,
                operation="INDEX",
                target="revenue_tracking",
                sql_statement="CREATE INDEX IF NOT EXISTS idx_revenue_user_period ON revenue_tracking(user_id, period_start, period_end)",
                rollback_statement="DROP INDEX IF EXISTS idx_revenue_user_period"
            ),
            SchemaChange(
                change_id="idx_revenue_platform_type",
                version=SchemaVersion.V1_3_0,
                component=SchemaComponent.MONETIZATION,
                operation="INDEX",
                target="revenue_tracking",
                sql_statement="CREATE INDEX IF NOT EXISTS idx_revenue_platform_type ON revenue_tracking(platform, revenue_type)",
                rollback_statement="DROP INDEX IF EXISTS idx_revenue_platform_type"
            )
        ]
        
        await self._apply_schema_changes(index_changes)
        
    async def create_security_schema(self) -> None:
        """Create security and audit tables"""
        security_changes = [
            # Audit log table
            SchemaChange(
                change_id="audit_logs_v1",
                version=SchemaVersion.V1_0_0,
                component=SchemaComponent.SECURITY,
                operation="CREATE",
                target="audit_logs",
                sql_statement="""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        user_id UUID,
                        tenant_id UUID,
                        action VARCHAR(100) NOT NULL,
                        resource_type VARCHAR(50) NOT NULL,
                        resource_id VARCHAR(100),
                        old_values JSONB,
                        new_values JSONB,
                        ip_address INET,
                        user_agent TEXT,
                        session_id VARCHAR(100),
                        success BOOLEAN DEFAULT true,
                        error_message TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """,
                rollback_statement="DROP TABLE IF EXISTS audit_logs CASCADE"
            ),
            
            # API access logs
            SchemaChange(
                change_id="api_access_logs_v1",
                version=SchemaVersion.V1_0_0,
                component=SchemaComponent.SECURITY,
                operation="CREATE",
                target="api_access_logs",
                sql_statement="""
                    CREATE TABLE IF NOT EXISTS api_access_logs (
                        access_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        user_id UUID,
                        tenant_id UUID,
                        endpoint VARCHAR(200) NOT NULL,
                        method VARCHAR(10) NOT NULL,
                        status_code INTEGER NOT NULL,
                        response_time_ms INTEGER,
                        request_size_bytes INTEGER,
                        response_size_bytes INTEGER,
                        ip_address INET,
                        user_agent TEXT,
                        api_key_id VARCHAR(100),
                        rate_limit_remaining INTEGER,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """,
                rollback_statement="DROP TABLE IF EXISTS api_access_logs CASCADE"
            )
        ]
        
        await self._apply_schema_changes(security_changes)
        
    async def _create_migration_tracking_tables(self) -> None:
        """Create migration and schema tracking tables"""
        async with self._get_session() as session:
            try:
                # Schema version table
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        version VARCHAR(20) NOT NULL,
                        description TEXT,
                        is_current BOOLEAN DEFAULT false,
                        applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        applied_by VARCHAR(100)
                    )
                """))
                
                # Schema changes table
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS schema_changes (
                        change_id VARCHAR(100) PRIMARY KEY,
                        version VARCHAR(20) NOT NULL,
                        component VARCHAR(50) NOT NULL,
                        operation VARCHAR(20) NOT NULL,
                        target VARCHAR(100) NOT NULL,
                        sql_statement TEXT NOT NULL,
                        rollback_statement TEXT,
                        status VARCHAR(20) DEFAULT 'pending',
                        applied_at TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """))
                
                # Migration history table
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS migration_history (
                        history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        migration_id VARCHAR(100) NOT NULL,
                        version VARCHAR(20) NOT NULL,
                        name VARCHAR(200) NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        started_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        completed_at TIMESTAMP WITH TIME ZONE,
                        duration_seconds FLOAT,
                        affected_rows INTEGER,
                        error_message TEXT,
                        tenant_id UUID,
                        metadata JSONB DEFAULT '{}'
                    )
                """))
                
                await session.commit()
                
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Failed to create migration tracking tables: {e}")
                raise
                
    async def _apply_schema_evolution(self, current_version: SchemaVersion, target_version: SchemaVersion) -> None:
        """Apply schema evolution from current to target version"""
        version_order = [v for v in SchemaVersion if v != SchemaVersion.LATEST]
        
        current_idx = version_order.index(current_version)
        target_idx = version_order.index(target_version)
        
        if target_idx > current_idx:
            # Forward evolution
            for i in range(current_idx + 1, target_idx + 1):
                await self._apply_version_changes(version_order[i])
        elif target_idx < current_idx:
            # Backward evolution (rollback)
            for i in range(current_idx, target_idx, -1):
                await self._rollback_version_changes(version_order[i])
                
    async def _apply_version_changes(self, version: SchemaVersion) -> None:
        """Apply all changes for a specific version"""
        if version == SchemaVersion.V1_1_0:
            await self.create_content_protection_schema()
            await self.create_performance_indices()
        elif version == SchemaVersion.V1_3_0:
            # Additional monetization changes
            pass
        elif version == SchemaVersion.V2_2_0:
            # Additional collaboration changes
            pass
            
    async def _apply_schema_changes(self, changes: List[SchemaChange]) -> None:
        """Apply list of schema changes"""
        async with self._get_session() as session:
            try:
                for change in changes:
                    # Execute the change
                    await session.execute(text(change.sql_statement))
                    
                    # Record the change
                    await session.execute(text("""
                        INSERT INTO schema_changes 
                        (change_id, version, component, operation, target, sql_statement, rollback_statement, status, applied_at)
                        VALUES (:change_id, :version, :component, :operation, :target, :sql_statement, :rollback_statement, 'applied', NOW())
                        ON CONFLICT (change_id) DO UPDATE SET status = 'applied', applied_at = NOW()
                    """), {
                        "change_id": change.change_id,
                        "version": change.version.value,
                        "component": change.component.value,
                        "operation": change.operation,
                        "target": change.target,
                        "sql_statement": change.sql_statement,
                        "rollback_statement": change.rollback_statement
                    })
                    
                await session.commit()
                logger.info(f"Applied {len(changes)} schema changes")
                
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Failed to apply schema changes: {e}")
                raise
                
    async def _validate_schema_integrity(self, schema_state: SchemaState) -> None:
        """Validate schema integrity and consistency"""
        async with self._get_session() as session:
            # Check table existence
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            required_tables = [
                'content_fingerprints', 'protection_alerts', 'revenue_tracking',
                'collaboration_requests', 'audit_logs', 'api_access_logs'
            ]
            
            missing_tables = [table for table in required_tables if table not in tables]
            if missing_tables:
                raise ValueError(f"Missing required tables: {missing_tables}")
                
            # Check foreign key constraints
            await self._validate_foreign_keys()
            
            logger.info("Schema integrity validation passed")
            
    async def _validate_foreign_keys(self) -> None:
        """Validate foreign key constraints"""
        # Override in subclasses for specific validation
        pass
        
    async def _calculate_schema_hash(self) -> str:
        """Calculate hash of current schema structure"""
        inspector = inspect(self.engine)
        
        schema_info = {
            'tables': {},
            'indices': {}
        }
        
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            schema_info['tables'][table_name] = {
                'columns': [(col['name'], str(col['type'])) for col in columns]
            }
            
        schema_json = json.dumps(schema_info, sort_keys=True)
        return hashlib.sha256(schema_json.encode()).hexdigest()
        
    async def _get_session(self) -> Session:
        """Get database session"""
        return self.session_maker()
        
    async def _rollback_version_changes(self, version: SchemaVersion) -> None:
        """Rollback changes for a specific version"""
        # Implementation for rollback logic
        pass
