"""📋 Schema Manager - Enterprise Schema Management & Versioning System
========================================================================
Module: database/schema_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Schema Management - Enterprise-Ready
Responsibility: Advanced schema versioning, management and evolution

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This schema manager provides advanced database schema management including:
- Automated schema versioning and evolution
- Multi-environment schema deployment
- Schema validation and integrity checking
- Cross-database schema synchronization
- Performance-optimized schema design
- Business logic schema integration
"""

import os
import logging
import datetime
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Optional imports for production features
try:
    import sqlalchemy
    from sqlalchemy import create_engine, text, inspect, MetaData, Table, Column
    from sqlalchemy.engine import Engine
    from sqlalchemy.schema import CreateTable, DropTable
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

class SchemaVersion(Enum):
    """Schema version enumeration"""
    V1_0_0 = "1.0.0"
    V1_1_0 = "1.1.0"
    V1_2_0 = "1.2.0"
    V2_0_0 = "2.0.0"
    V2_1_0 = "2.1.0"

class SchemaComponent(Enum):
    """Schema component types"""
    USERS = "users"
    CONTENT = "content"
    CREATORS = "creators"
    ANALYTICS = "analytics"
    REVENUE = "revenue"
    PROTECTION = "protection"
    COLLABORATION = "collaboration"
    AI_PROCESSING = "ai_processing"
    NOTIFICATIONS = "notifications"
    SECURITY = "security"

class ChangeType(Enum):
    """Schema change types"""
    CREATE_TABLE = "create_table"
    DROP_TABLE = "drop_table"
    ADD_COLUMN = "add_column"
    DROP_COLUMN = "drop_column"
    MODIFY_COLUMN = "modify_column"
    ADD_INDEX = "add_index"
    DROP_INDEX = "drop_index"
    ADD_CONSTRAINT = "add_constraint"
    DROP_CONSTRAINT = "drop_constraint"
    CREATE_VIEW = "create_view"
    DROP_VIEW = "drop_view"

@dataclass
class SchemaChange:
    """Represents a schema change"""
    change_id: str
    version: SchemaVersion
    component: SchemaComponent
    change_type: ChangeType
    target: str  # Table, column, index name
    sql_statement: str
    rollback_statement: str
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    applied_at: Optional[datetime.datetime] = None
    checksum: str = field(init=False)
    
    def __post_init__(self):
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate change checksum for integrity validation"""
        content = f"{self.change_id}{self.sql_statement}{self.rollback_statement}"
        return hashlib.sha256(content.encode()).hexdigest()

@dataclass
class SchemaState:
    """Current schema state information"""
    current_version: SchemaVersion
    installed_components: Set[SchemaComponent]
    pending_changes: List[SchemaChange]
    last_update: datetime.datetime
    schema_hash: str
    validation_status: bool = True

@dataclass
class SchemaDefinition:
    """Complete schema definition for a component"""
    component: SchemaComponent
    version: SchemaVersion
    tables: Dict[str, Dict[str, Any]]
    indexes: Dict[str, Dict[str, Any]]
    constraints: Dict[str, Dict[str, Any]]
    views: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    functions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    triggers: Dict[str, Dict[str, Any]] = field(default_factory=dict)

class SchemaManager:
    """Enterprise schema management system"""
    
    def __init__(self, database_url: str = None, config: Dict[str, Any] = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///./database.db')
        self.config = config or {}
        self.engine = None
        self.metadata = None
        self.schema_changes: List[SchemaChange] = []
        self.schema_definitions: Dict[SchemaComponent, SchemaDefinition] = {}
        self._initialize_engine()
        self._load_schema_definitions()
    
    def _initialize_engine(self):
        """Initialize database engine"""
        if SQLALCHEMY_AVAILABLE:
            try:
                self.engine = create_engine(
                    self.database_url,
                    echo=self.config.get('echo', False),
                    pool_pre_ping=True
                )
                self.metadata = MetaData()
                logger.info("Schema manager initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize schema manager: {e}")
                raise
        else:
            logger.warning("SQLAlchemy not available, schema manager will run in limited mode")
    
    def _load_schema_definitions(self):
        """Load schema definitions for all components"""
        # Initialize core schema definitions
        self._define_users_schema()
        self._define_content_schema()
        self._define_creators_schema()
        self._define_analytics_schema()
        self._define_revenue_schema()
        self._define_protection_schema()
        self._define_collaboration_schema()
        self._define_ai_processing_schema()
        self._define_notifications_schema()
        self._define_security_schema()
    
    def _define_users_schema(self):
        """Define users component schema"""
        tables = {
            "users": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "username", "type": "VARCHAR(100) UNIQUE NOT NULL"},
                    {"name": "email", "type": "VARCHAR(255) UNIQUE NOT NULL"},
                    {"name": "password_hash", "type": "VARCHAR(255) NOT NULL"},
                    {"name": "user_type", "type": "VARCHAR(50) DEFAULT 'creator'"},
                    {"name": "status", "type": "VARCHAR(50) DEFAULT 'active'"},
                    {"name": "subscription_tier", "type": "VARCHAR(50) DEFAULT 'free'"},
                    {"name": "profile_data", "type": "JSONB DEFAULT '{}'"},
                    {"name": "preferences", "type": "JSONB DEFAULT '{}'"},
                    {"name": "verification_status", "type": "VARCHAR(50) DEFAULT 'pending'"},
                    {"name": "created_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "last_login_at", "type": "TIMESTAMP WITH TIME ZONE"},
                    {"name": "deleted_at", "type": "TIMESTAMP WITH TIME ZONE"}
                ]
            },
            "user_sessions": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "user_id", "type": "UUID NOT NULL REFERENCES users(id)"},
                    {"name": "session_token", "type": "VARCHAR(255) UNIQUE NOT NULL"},
                    {"name": "expires_at", "type": "TIMESTAMP WITH TIME ZONE NOT NULL"},
                    {"name": "device_info", "type": "JSONB DEFAULT '{}'"},
                    {"name": "ip_address", "type": "INET"},
                    {"name": "created_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"}
                ]
            }
        }
        
        indexes = {
            "idx_users_email": {"table": "users", "columns": ["email"], "unique": True},
            "idx_users_username": {"table": "users", "columns": ["username"], "unique": True},
            "idx_users_status": {"table": "users", "columns": ["status"]},
            "idx_users_created": {"table": "users", "columns": ["created_at"]},
            "idx_sessions_token": {"table": "user_sessions", "columns": ["session_token"], "unique": True},
            "idx_sessions_user": {"table": "user_sessions", "columns": ["user_id"]},
            "idx_sessions_expires": {"table": "user_sessions", "columns": ["expires_at"]}
        }
        
        constraints = {
            "chk_users_user_type": {
                "table": "users",
                "type": "check",
                "expression": "user_type IN ('creator', 'viewer', 'admin', 'enterprise')"
            },
            "chk_users_status": {
                "table": "users",
                "type": "check",
                "expression": "status IN ('active', 'inactive', 'suspended', 'deleted')"
            }
        }
        
        self.schema_definitions[SchemaComponent.USERS] = SchemaDefinition(
            component=SchemaComponent.USERS,
            version=SchemaVersion.V2_0_0,
            tables=tables,
            indexes=indexes,
            constraints=constraints
        )
    
    def _define_content_schema(self):
        """Define content component schema"""
        tables = {
            "content_items": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "creator_id", "type": "UUID NOT NULL REFERENCES users(id)"},
                    {"name": "title", "type": "VARCHAR(500) NOT NULL"},
                    {"name": "description", "type": "TEXT"},
                    {"name": "content_type", "type": "VARCHAR(100) NOT NULL"},
                    {"name": "file_path", "type": "VARCHAR(1000)"},
                    {"name": "file_size", "type": "BIGINT"},
                    {"name": "mime_type", "type": "VARCHAR(200)"},
                    {"name": "duration", "type": "INTEGER"},
                    {"name": "dimensions", "type": "JSONB"},
                    {"name": "metadata", "type": "JSONB DEFAULT '{}'"},
                    {"name": "tags", "type": "JSONB DEFAULT '[]'"},
                    {"name": "status", "type": "VARCHAR(50) DEFAULT 'draft'"},
                    {"name": "visibility", "type": "VARCHAR(50) DEFAULT 'private'"},
                    {"name": "monetization_enabled", "type": "BOOLEAN DEFAULT false"},
                    {"name": "protection_enabled", "type": "BOOLEAN DEFAULT true"},
                    {"name": "ai_analysis", "type": "JSONB DEFAULT '{}'"},
                    {"name": "fingerprint_data", "type": "JSONB DEFAULT '{}'"},
                    {"name": "seo_data", "type": "JSONB DEFAULT '{}'"},
                    {"name": "created_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "published_at", "type": "TIMESTAMP WITH TIME ZONE"},
                    {"name": "deleted_at", "type": "TIMESTAMP WITH TIME ZONE"}
                ]
            },
            "content_versions": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "content_id", "type": "UUID NOT NULL REFERENCES content_items(id)"},
                    {"name": "version_number", "type": "INTEGER NOT NULL"},
                    {"name": "changes", "type": "JSONB NOT NULL"},
                    {"name": "created_by", "type": "UUID NOT NULL REFERENCES users(id)"},
                    {"name": "created_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"}
                ]
            }
        }
        
        indexes = {
            "idx_content_creator": {"table": "content_items", "columns": ["creator_id"]},
            "idx_content_status": {"table": "content_items", "columns": ["status"]},
            "idx_content_type": {"table": "content_items", "columns": ["content_type"]},
            "idx_content_created": {"table": "content_items", "columns": ["created_at"]},
            "idx_content_published": {"table": "content_items", "columns": ["published_at"]},
            "idx_content_tags": {"table": "content_items", "columns": ["tags"], "type": "gin"},
            "idx_content_metadata": {"table": "content_items", "columns": ["metadata"], "type": "gin"},
            "idx_versions_content": {"table": "content_versions", "columns": ["content_id"]},
            "idx_versions_number": {"table": "content_versions", "columns": ["content_id", "version_number"], "unique": True}
        }
        
        constraints = {
            "chk_content_status": {
                "table": "content_items",
                "type": "check",
                "expression": "status IN ('draft', 'processing', 'published', 'archived', 'deleted')"
            },
            "chk_content_visibility": {
                "table": "content_items",
                "type": "check",
                "expression": "visibility IN ('private', 'public', 'unlisted', 'premium')"
            }
        }
        
        self.schema_definitions[SchemaComponent.CONTENT] = SchemaDefinition(
            component=SchemaComponent.CONTENT,
            version=SchemaVersion.V2_0_0,
            tables=tables,
            indexes=indexes,
            constraints=constraints
        )
    
    def _define_analytics_schema(self):
        """Define analytics component schema"""
        tables = {
            "analytics_events": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "event_type", "type": "VARCHAR(100) NOT NULL"},
                    {"name": "entity_type", "type": "VARCHAR(50)"},
                    {"name": "entity_id", "type": "UUID"},
                    {"name": "user_id", "type": "UUID REFERENCES users(id)"},
                    {"name": "session_id", "type": "VARCHAR(255)"},
                    {"name": "event_data", "type": "JSONB DEFAULT '{}'"},
                    {"name": "platform", "type": "VARCHAR(50)"},
                    {"name": "device_type", "type": "VARCHAR(50)"},
                    {"name": "location_data", "type": "JSONB"},
                    {"name": "timestamp", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"}
                ]
            },
            "performance_metrics": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "metric_name", "type": "VARCHAR(100) NOT NULL"},
                    {"name": "metric_value", "type": "DECIMAL(15,6) NOT NULL"},
                    {"name": "unit", "type": "VARCHAR(50)"},
                    {"name": "tags", "type": "JSONB DEFAULT '{}'"},
                    {"name": "timestamp", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"}
                ]
            }
        }
        
        indexes = {
            "idx_events_type": {"table": "analytics_events", "columns": ["event_type"]},
            "idx_events_entity": {"table": "analytics_events", "columns": ["entity_type", "entity_id"]},
            "idx_events_user": {"table": "analytics_events", "columns": ["user_id"]},
            "idx_events_timestamp": {"table": "analytics_events", "columns": ["timestamp"]},
            "idx_events_platform": {"table": "analytics_events", "columns": ["platform"]},
            "idx_metrics_name": {"table": "performance_metrics", "columns": ["metric_name"]},
            "idx_metrics_timestamp": {"table": "performance_metrics", "columns": ["timestamp"]},
            "idx_metrics_tags": {"table": "performance_metrics", "columns": ["tags"], "type": "gin"}
        }
        
        constraints = {}
        
        self.schema_definitions[SchemaComponent.ANALYTICS] = SchemaDefinition(
            component=SchemaComponent.ANALYTICS,
            version=SchemaVersion.V2_0_0,
            tables=tables,
            indexes=indexes,
            constraints=constraints
        )
    
    def _define_revenue_schema(self):
        """Define revenue component schema"""
        tables = {
            "revenue_transactions": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "creator_id", "type": "UUID NOT NULL REFERENCES users(id)"},
                    {"name": "content_id", "type": "UUID REFERENCES content_items(id)"},
                    {"name": "transaction_type", "type": "VARCHAR(50) NOT NULL"},
                    {"name": "amount", "type": "DECIMAL(15,2) NOT NULL"},
                    {"name": "currency", "type": "VARCHAR(3) NOT NULL"},
                    {"name": "platform_fee", "type": "DECIMAL(15,2)"},
                    {"name": "net_amount", "type": "DECIMAL(15,2)"},
                    {"name": "payment_method", "type": "VARCHAR(100)"},
                    {"name": "payment_provider", "type": "VARCHAR(100)"},
                    {"name": "external_transaction_id", "type": "VARCHAR(255)"},
                    {"name": "status", "type": "VARCHAR(50) DEFAULT 'pending'"},
                    {"name": "metadata", "type": "JSONB DEFAULT '{}'"},
                    {"name": "created_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "processed_at", "type": "TIMESTAMP WITH TIME ZONE"}
                ]
            },
            "subscription_plans": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "creator_id", "type": "UUID NOT NULL REFERENCES users(id)"},
                    {"name": "name", "type": "VARCHAR(200) NOT NULL"},
                    {"name": "description", "type": "TEXT"},
                    {"name": "price", "type": "DECIMAL(15,2) NOT NULL"},
                    {"name": "currency", "type": "VARCHAR(3) NOT NULL"},
                    {"name": "billing_cycle", "type": "VARCHAR(50) NOT NULL"},
                    {"name": "features", "type": "JSONB DEFAULT '{}'"},
                    {"name": "is_active", "type": "BOOLEAN DEFAULT true"},
                    {"name": "created_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"}
                ]
            }
        }
        
        indexes = {
            "idx_revenue_creator": {"table": "revenue_transactions", "columns": ["creator_id"]},
            "idx_revenue_content": {"table": "revenue_transactions", "columns": ["content_id"]},
            "idx_revenue_type": {"table": "revenue_transactions", "columns": ["transaction_type"]},
            "idx_revenue_status": {"table": "revenue_transactions", "columns": ["status"]},
            "idx_revenue_created": {"table": "revenue_transactions", "columns": ["created_at"]},
            "idx_plans_creator": {"table": "subscription_plans", "columns": ["creator_id"]},
            "idx_plans_active": {"table": "subscription_plans", "columns": ["is_active"]}
        }
        
        constraints = {
            "chk_revenue_amount": {
                "table": "revenue_transactions",
                "type": "check",
                "expression": "amount > 0"
            },
            "chk_revenue_currency": {
                "table": "revenue_transactions",
                "type": "check",
                "expression": "LENGTH(currency) = 3"
            }
        }
        
        self.schema_definitions[SchemaComponent.REVENUE] = SchemaDefinition(
            component=SchemaComponent.REVENUE,
            version=SchemaVersion.V2_0_0,
            tables=tables,
            indexes=indexes,
            constraints=constraints
        )
    
    def _define_protection_schema(self):
        """Define content protection component schema"""
        tables = {
            "content_fingerprints": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "content_id", "type": "UUID NOT NULL REFERENCES content_items(id)"},
                    {"name": "fingerprint_type", "type": "VARCHAR(50) NOT NULL"},
                    {"name": "fingerprint_hash", "type": "VARCHAR(255) NOT NULL"},
                    {"name": "fingerprint_data", "type": "JSONB DEFAULT '{}'"},
                    {"name": "algorithm_version", "type": "VARCHAR(50)"},
                    {"name": "confidence_score", "type": "DECIMAL(5,4)"},
                    {"name": "created_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"}
                ]
            },
            "protection_alerts": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "content_id", "type": "UUID NOT NULL REFERENCES content_items(id)"},
                    {"name": "alert_type", "type": "VARCHAR(50) NOT NULL"},
                    {"name": "severity", "type": "VARCHAR(20) NOT NULL"},
                    {"name": "detected_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "source_url", "type": "VARCHAR(2000)"},
                    {"name": "match_confidence", "type": "DECIMAL(5,4)"},
                    {"name": "evidence_data", "type": "JSONB DEFAULT '{}'"},
                    {"name": "status", "type": "VARCHAR(50) DEFAULT 'pending'"},
                    {"name": "resolved_at", "type": "TIMESTAMP WITH TIME ZONE"},
                    {"name": "resolution_notes", "type": "TEXT"}
                ]
            }
        }
        
        indexes = {
            "idx_fingerprints_content": {"table": "content_fingerprints", "columns": ["content_id"]},
            "idx_fingerprints_hash": {"table": "content_fingerprints", "columns": ["fingerprint_hash"]},
            "idx_fingerprints_type": {"table": "content_fingerprints", "columns": ["fingerprint_type"]},
            "idx_alerts_content": {"table": "protection_alerts", "columns": ["content_id"]},
            "idx_alerts_type": {"table": "protection_alerts", "columns": ["alert_type"]},
            "idx_alerts_severity": {"table": "protection_alerts", "columns": ["severity"]},
            "idx_alerts_status": {"table": "protection_alerts", "columns": ["status"]},
            "idx_alerts_detected": {"table": "protection_alerts", "columns": ["detected_at"]}
        }
        
        constraints = {
            "chk_alerts_severity": {
                "table": "protection_alerts",
                "type": "check",
                "expression": "severity IN ('low', 'medium', 'high', 'critical')"
            }
        }
        
        self.schema_definitions[SchemaComponent.PROTECTION] = SchemaDefinition(
            component=SchemaComponent.PROTECTION,
            version=SchemaVersion.V2_0_0,
            tables=tables,
            indexes=indexes,
            constraints=constraints
        )
    
    def _define_collaboration_schema(self):
        """Define collaboration component schema"""
        tables = {
            "collaboration_projects": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "title", "type": "VARCHAR(500) NOT NULL"},
                    {"name": "description", "type": "TEXT"},
                    {"name": "initiator_id", "type": "UUID NOT NULL REFERENCES users(id)"},
                    {"name": "collaborators", "type": "JSONB DEFAULT '[]'"},
                    {"name": "project_type", "type": "VARCHAR(100)"},
                    {"name": "status", "type": "VARCHAR(50) DEFAULT 'active'"},
                    {"name": "budget", "type": "DECIMAL(15,2)"},
                    {"name": "deadline", "type": "TIMESTAMP WITH TIME ZONE"},
                    {"name": "metadata", "type": "JSONB DEFAULT '{}'"},
                    {"name": "created_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"}
                ]
            }
        }
        
        indexes = {
            "idx_collab_initiator": {"table": "collaboration_projects", "columns": ["initiator_id"]},
            "idx_collab_status": {"table": "collaboration_projects", "columns": ["status"]},
            "idx_collab_created": {"table": "collaboration_projects", "columns": ["created_at"]},
            "idx_collab_collaborators": {"table": "collaboration_projects", "columns": ["collaborators"], "type": "gin"}
        }
        
        constraints = {}
        
        self.schema_definitions[SchemaComponent.COLLABORATION] = SchemaDefinition(
            component=SchemaComponent.COLLABORATION,
            version=SchemaVersion.V2_0_0,
            tables=tables,
            indexes=indexes,
            constraints=constraints
        )
    
    def _define_ai_processing_schema(self):
        """Define AI processing component schema"""
        tables = {
            "ai_processing_jobs": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "content_id", "type": "UUID NOT NULL REFERENCES content_items(id)"},
                    {"name": "job_type", "type": "VARCHAR(100) NOT NULL"},
                    {"name": "status", "type": "VARCHAR(50) DEFAULT 'queued'"},
                    {"name": "priority", "type": "INTEGER DEFAULT 5"},
                    {"name": "input_data", "type": "JSONB DEFAULT '{}'"},
                    {"name": "output_data", "type": "JSONB DEFAULT '{}'"},
                    {"name": "error_message", "type": "TEXT"},
                    {"name": "progress_percentage", "type": "INTEGER DEFAULT 0"},
                    {"name": "started_at", "type": "TIMESTAMP WITH TIME ZONE"},
                    {"name": "completed_at", "type": "TIMESTAMP WITH TIME ZONE"},
                    {"name": "created_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"}
                ]
            }
        }
        
        indexes = {
            "idx_ai_jobs_content": {"table": "ai_processing_jobs", "columns": ["content_id"]},
            "idx_ai_jobs_status": {"table": "ai_processing_jobs", "columns": ["status"]},
            "idx_ai_jobs_type": {"table": "ai_processing_jobs", "columns": ["job_type"]},
            "idx_ai_jobs_priority": {"table": "ai_processing_jobs", "columns": ["priority"]},
            "idx_ai_jobs_created": {"table": "ai_processing_jobs", "columns": ["created_at"]}
        }
        
        constraints = {}
        
        self.schema_definitions[SchemaComponent.AI_PROCESSING] = SchemaDefinition(
            component=SchemaComponent.AI_PROCESSING,
            version=SchemaVersion.V2_0_0,
            tables=tables,
            indexes=indexes,
            constraints=constraints
        )
    
    def _define_notifications_schema(self):
        """Define notifications component schema"""
        tables = {
            "notifications": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "user_id", "type": "UUID NOT NULL REFERENCES users(id)"},
                    {"name": "type", "type": "VARCHAR(100) NOT NULL"},
                    {"name": "title", "type": "VARCHAR(500) NOT NULL"},
                    {"name": "message", "type": "TEXT"},
                    {"name": "data", "type": "JSONB DEFAULT '{}'"},
                    {"name": "is_read", "type": "BOOLEAN DEFAULT false"},
                    {"name": "priority", "type": "VARCHAR(20) DEFAULT 'normal'"},
                    {"name": "delivery_channels", "type": "JSONB DEFAULT '[]'"},
                    {"name": "created_at", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "read_at", "type": "TIMESTAMP WITH TIME ZONE"}
                ]
            }
        }
        
        indexes = {
            "idx_notifications_user": {"table": "notifications", "columns": ["user_id"]},
            "idx_notifications_type": {"table": "notifications", "columns": ["type"]},
            "idx_notifications_read": {"table": "notifications", "columns": ["is_read"]},
            "idx_notifications_created": {"table": "notifications", "columns": ["created_at"]}
        }
        
        constraints = {}
        
        self.schema_definitions[SchemaComponent.NOTIFICATIONS] = SchemaDefinition(
            component=SchemaComponent.NOTIFICATIONS,
            version=SchemaVersion.V2_0_0,
            tables=tables,
            indexes=indexes,
            constraints=constraints
        )
    
    def _define_security_schema(self):
        """Define security component schema"""
        tables = {
            "audit_logs": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "user_id", "type": "UUID REFERENCES users(id)"},
                    {"name": "action", "type": "VARCHAR(100) NOT NULL"},
                    {"name": "resource_type", "type": "VARCHAR(100)"},
                    {"name": "resource_id", "type": "UUID"},
                    {"name": "details", "type": "JSONB DEFAULT '{}'"},
                    {"name": "ip_address", "type": "INET"},
                    {"name": "user_agent", "type": "TEXT"},
                    {"name": "timestamp", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"}
                ]
            },
            "api_access_logs": {
                "columns": [
                    {"name": "id", "type": "UUID PRIMARY KEY DEFAULT gen_random_uuid()"},
                    {"name": "user_id", "type": "UUID REFERENCES users(id)"},
                    {"name": "endpoint", "type": "VARCHAR(500) NOT NULL"},
                    {"name": "method", "type": "VARCHAR(10) NOT NULL"},
                    {"name": "status_code", "type": "INTEGER NOT NULL"},
                    {"name": "response_time_ms", "type": "INTEGER"},
                    {"name": "ip_address", "type": "INET"},
                    {"name": "user_agent", "type": "TEXT"},
                    {"name": "request_data", "type": "JSONB"},
                    {"name": "response_data", "type": "JSONB"},
                    {"name": "timestamp", "type": "TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"}
                ]
            }
        }
        
        indexes = {
            "idx_audit_user": {"table": "audit_logs", "columns": ["user_id"]},
            "idx_audit_action": {"table": "audit_logs", "columns": ["action"]},
            "idx_audit_resource": {"table": "audit_logs", "columns": ["resource_type", "resource_id"]},
            "idx_audit_timestamp": {"table": "audit_logs", "columns": ["timestamp"]},
            "idx_api_user": {"table": "api_access_logs", "columns": ["user_id"]},
            "idx_api_endpoint": {"table": "api_access_logs", "columns": ["endpoint"]},
            "idx_api_status": {"table": "api_access_logs", "columns": ["status_code"]},
            "idx_api_timestamp": {"table": "api_access_logs", "columns": ["timestamp"]}
        }
        
        constraints = {}
        
        self.schema_definitions[SchemaComponent.SECURITY] = SchemaDefinition(
            component=SchemaComponent.SECURITY,
            version=SchemaVersion.V2_0_0,
            tables=tables,
            indexes=indexes,
            constraints=constraints
        )
    
    def _define_creators_schema(self):
        """Define creators component schema (placeholder for future implementation)"""
        # This would be implemented with creator-specific tables like profiles,
        # portfolios, skills, etc.
        pass
    
    async def get_current_version(self) -> SchemaVersion:
        """Get current database schema version"""
        if not SQLALCHEMY_AVAILABLE or not self.engine:
            return SchemaVersion.V1_0_0
        
        try:
            with self.engine.connect() as conn:
                # Ensure schema version table exists
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version VARCHAR(20) PRIMARY KEY,
                        applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        is_current BOOLEAN DEFAULT false
                    )
                """))
                
                result = conn.execute(text(
                    "SELECT version FROM schema_version WHERE is_current = true ORDER BY applied_at DESC LIMIT 1"
                ))
                row = result.fetchone()
                
                if row:
                    return SchemaVersion(row[0])
                else:
                    # No version found, assume initial state
                    return SchemaVersion.V1_0_0
                    
        except Exception as e:
            logger.error(f"Failed to get current schema version: {e}")
            return SchemaVersion.V1_0_0
    
    async def get_schema_state(self) -> SchemaState:
        """Get current database schema state"""
        if not SQLALCHEMY_AVAILABLE or not self.engine:
            return SchemaState(
                current_version=SchemaVersion.V1_0_0,
                installed_components=set(),
                pending_changes=[],
                last_update=datetime.datetime.utcnow(),
                schema_hash="",
                validation_status=False
            )
        
        with self.engine.connect() as conn:
            try:
                # Get current version
                version_query = text("""
                    SELECT version FROM schema_version 
                    WHERE is_current = true
                    ORDER BY applied_at DESC LIMIT 1
                """)
                version_result = conn.execute(version_query)
                current_version_row = version_result.fetchone()
                current_version = SchemaVersion(current_version_row[0]) if current_version_row else SchemaVersion.V1_0_0
                
                # Get installed components
                components_query = text("""
                    SELECT DISTINCT component FROM schema_changes 
                    WHERE status = 'applied'
                """)
                components_result = conn.execute(components_query)
                installed_components = {SchemaComponent(row[0]) for row in components_result.fetchall()}
                
                # Get pending changes
                pending_query = text("""
                    SELECT change_id, version, component, change_type, target, sql_statement, rollback_statement
                    FROM schema_changes 
                    WHERE status = 'pending'
                    ORDER BY created_at
                """)
                pending_result = conn.execute(pending_query)
                pending_changes = [
                    SchemaChange(
                        change_id=row[0],
                        version=SchemaVersion(row[1]),
                        component=SchemaComponent(row[2]),
                        change_type=ChangeType(row[3]),
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
                    last_update=datetime.datetime.utcnow(),
                    schema_hash=schema_hash
                )
                
            except Exception as e:
                logger.error(f"Failed to get schema state: {e}")
                raise
    
    async def _calculate_schema_hash(self) -> str:
        """Calculate current schema hash for integrity checking"""
        if not SQLALCHEMY_AVAILABLE or not self.engine:
            return ""
        
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            schema_content = ""
            for table in sorted(tables):
                columns = inspector.get_columns(table)
                schema_content += f"table:{table};"
                for col in sorted(columns, key=lambda x: x['name']):
                    schema_content += f"col:{col['name']}:{col['type']};"
            
            return hashlib.sha256(schema_content.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to calculate schema hash: {e}")
            return ""
    
    async def validate_schema(self) -> Dict[str, Any]:
        """Validate current schema against definitions"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_tables': [],
            'missing_indexes': [],
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        
        if not SQLALCHEMY_AVAILABLE or not self.engine:
            validation_result['valid'] = False
            validation_result['errors'].append("SQLAlchemy not available")
            return validation_result
        
        try:
            inspector = inspect(self.engine)
            existing_tables = set(inspector.get_table_names())
            
            for component, definition in self.schema_definitions.items():
                # Check tables
                for table_name in definition.tables.keys():
                    if table_name not in existing_tables:
                        validation_result['missing_tables'].append(table_name)
                        validation_result['valid'] = False
                
                # Check indexes (simplified check)
                for index_name, index_def in definition.indexes.items():
                    table_name = index_def['table']
                    if table_name in existing_tables:
                        try:
                            table_indexes = inspector.get_indexes(table_name)
                            index_names = [idx['name'] for idx in table_indexes]
                            if index_name not in index_names:
                                validation_result['missing_indexes'].append(f"{table_name}.{index_name}")
                                validation_result['warnings'].append(f"Missing index: {index_name}")
                        except Exception as e:
                            validation_result['warnings'].append(f"Could not check indexes for {table_name}: {e}")
            
            if validation_result['missing_tables'] or validation_result['missing_indexes']:
                validation_result['valid'] = False
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Schema validation failed: {e}")
        
        return validation_result
    
    async def create_migration(self, name: str, component: SchemaComponent, 
                              sql_statements: List[str], rollback_statements: List[str]) -> SchemaChange:
        """Create a new schema migration"""
        change_id = f"m_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{component.value}_{name.replace(' ', '_')}"
        
        change = SchemaChange(
            change_id=change_id,
            version=SchemaVersion.V2_0_0,  # Would be determined dynamically
            component=component,
            change_type=ChangeType.CREATE_TABLE,  # Would be determined from SQL
            target=name,
            sql_statement="; ".join(sql_statements),
            rollback_statement="; ".join(rollback_statements),
            description=name
        )
        
        self.schema_changes.append(change)
        logger.info(f"Created migration: {change_id}")
        return change
    
    async def apply_migration(self, change: SchemaChange) -> bool:
        """Apply a schema migration"""
        if not SQLALCHEMY_AVAILABLE or not self.engine:
            logger.error("Cannot apply migration: SQLAlchemy not available")
            return False
        
        try:
            with self.engine.connect() as conn:
                # Apply the change
                conn.execute(text(change.sql_statement))
                
                # Record the migration
                conn.execute(text("""
                    INSERT INTO schema_changes (change_id, version, component, change_type, target, 
                                              sql_statement, rollback_statement, status, applied_at)
                    VALUES (:change_id, :version, :component, :change_type, :target, 
                           :sql_statement, :rollback_statement, 'applied', CURRENT_TIMESTAMP)
                """), {
                    'change_id': change.change_id,
                    'version': change.version.value,
                    'component': change.component.value,
                    'change_type': change.change_type.value,
                    'target': change.target,
                    'sql_statement': change.sql_statement,
                    'rollback_statement': change.rollback_statement
                })
                
                change.applied_at = datetime.datetime.utcnow()
                logger.info(f"Applied migration: {change.change_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to apply migration {change.change_id}: {e}")
            return False
    
    async def rollback_migration(self, change: SchemaChange) -> bool:
        """Rollback a schema migration"""
        if not SQLALCHEMY_AVAILABLE or not self.engine:
            logger.error("Cannot rollback migration: SQLAlchemy not available")
            return False
        
        try:
            with self.engine.connect() as conn:
                # Apply rollback
                conn.execute(text(change.rollback_statement))
                
                # Update migration status
                conn.execute(text("""
                    UPDATE schema_changes 
                    SET status = 'rolled_back', rolled_back_at = CURRENT_TIMESTAMP
                    WHERE change_id = :change_id
                """), {'change_id': change.change_id})
                
                change.applied_at = None
                logger.info(f"Rolled back migration: {change.change_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to rollback migration {change.change_id}: {e}")
            return False
    
    async def upgrade_to_version(self, target_version: SchemaVersion) -> bool:
        """Upgrade schema to target version"""
        current_version = await self.get_current_version()
        
        if current_version == target_version:
            logger.info(f"Already at target version {target_version.value}")
            return True
        
        # For this implementation, we'll apply all component schemas
        # In a real system, this would be more sophisticated with version-specific migrations
        
        try:
            with self.engine.connect() as conn:
                for component, definition in self.schema_definitions.items():
                    await self._apply_component_schema(conn, definition)
                
                # Update schema version
                conn.execute(text("UPDATE schema_version SET is_current = false"))
                conn.execute(text("""
                    INSERT INTO schema_version (version, is_current) 
                    VALUES (:version, true)
                    ON CONFLICT (version) DO UPDATE SET is_current = true
                """), {'version': target_version.value})
                
                logger.info(f"Upgraded schema to version {target_version.value}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to upgrade schema to {target_version.value}: {e}")
            return False
    
    async def _apply_component_schema(self, conn, definition: SchemaDefinition):
        """Apply schema definition for a component"""
        # Create tables
        for table_name, table_def in definition.tables.items():
            columns_sql = []
            for col in table_def['columns']:
                columns_sql.append(f"{col['name']} {col['type']}")
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns_sql)})"
            conn.execute(text(create_sql))
        
        # Create indexes
        for index_name, index_def in definition.indexes.items():
            table_name = index_def['table']
            columns = index_def['columns']
            unique = "UNIQUE " if index_def.get('unique', False) else ""
            index_type = f"USING {index_def['type']} " if 'type' in index_def else ""
            
            create_index_sql = f"CREATE {unique}INDEX IF NOT EXISTS {index_name} ON {table_name} {index_type}({', '.join(columns)})"
            try:
                conn.execute(text(create_index_sql))
            except Exception as e:
                logger.warning(f"Could not create index {index_name}: {e}")
        
        # Create constraints
        for constraint_name, constraint_def in definition.constraints.items():
            table_name = constraint_def['table']
            constraint_type = constraint_def['type']
            
            if constraint_type == 'check':
                alter_sql = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} CHECK ({constraint_def['expression']})"
                try:
                    conn.execute(text(alter_sql))
                except Exception as e:
                    logger.warning(f"Could not create constraint {constraint_name}: {e}")
    
    def export_schema(self, format: str = 'json') -> str:
        """Export schema definitions"""
        if format == 'json':
            schema_export = {}
            for component, definition in self.schema_definitions.items():
                schema_export[component.value] = {
                    'version': definition.version.value,
                    'tables': definition.tables,
                    'indexes': definition.indexes,
                    'constraints': definition.constraints
                }
            return json.dumps(schema_export, indent=2, default=str)
        
        elif format == 'sql':
            sql_statements = []
            for component, definition in self.schema_definitions.items():
                sql_statements.append(f"-- {component.value.upper()} COMPONENT")
                
                # Table creation statements
                for table_name, table_def in definition.tables.items():
                    columns_sql = []
                    for col in table_def['columns']:
                        columns_sql.append(f"  {col['name']} {col['type']}")
                    
                    create_sql = f"CREATE TABLE {table_name} (\n{','.join(columns_sql)}\n);"
                    sql_statements.append(create_sql)
                
                sql_statements.append("")
            
            return "\n".join(sql_statements)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Export main classes
__all__ = [
    'SchemaManager',
    'SchemaChange',
    'SchemaState',
    'SchemaDefinition',
    'SchemaVersion',
    'SchemaComponent',
    'ChangeType'
]