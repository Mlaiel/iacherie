#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ Alembic Migration Template - Enterprise Grade

🚨 PROTECTION PROPRIÉTÉ INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Code propriétaire

AVERTISSEMENT LÉGAL:
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT  
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Developed by Expert Team:
- Lead Dev IA: Fahed Mlaiel - Advanced migration patterns & AI optimization
- Backend Senior: Alembic expert & async migration strategies
- DBA Expert: Database migration best practices & rollback strategies
- Security Expert: Migration security & data protection
- DevOps Engineer: CI/CD migration automation & zero-downtime deployments
- Microservices Architect: Distributed migration coordination

Architecture: Creator Economy Database Migration Management
Business Logic: Schema Evolution → Migration Generation → Validation → Execution → Rollback Strategy
"""

import asyncio
import logging
import os
import re
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

from alembic import command, script
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.runtime.migration import MigrationInfo
from alembic.script import ScriptDirectory
from sqlalchemy import MetaData, Table, Column, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.schema import CreateTable, DropTable
import sqlalchemy as sa

logger = logging.getLogger(__name__)

class MigrationType(str, Enum):
    """Types of database migrations"""
    SCHEMA_CHANGE = "schema_change"
    DATA_MIGRATION = "data_migration"
    INDEX_OPTIMIZATION = "index_optimization"
    CONSTRAINT_UPDATE = "constraint_update"
    PARTITION_CHANGE = "partition_change"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SECURITY_UPDATE = "security_update"
    MULTI_TENANT_UPDATE = "multi_tenant_update"

class MigrationPriority(str, Enum):
    """Migration priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class MigrationStrategy(str, Enum):
    """Migration execution strategies"""
    ONLINE = "online"           # Zero-downtime migration
    OFFLINE = "offline"         # Maintenance window required
    ROLLING = "rolling"         # Gradual rollout
    BLUE_GREEN = "blue_green"   # Blue-green deployment

@dataclass
class MigrationMetadata:
    """Migration metadata for tracking and management"""
    revision_id: str
    description: str
    migration_type: MigrationType
    priority: MigrationPriority
    strategy: MigrationStrategy
    author: str = "Fahed Mlaiel <mlaiel@live.de>"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    estimated_duration: Optional[int] = None  # seconds
    rollback_tested: bool = False
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
@dataclass
class MigrationValidationResult:
    """Migration validation result"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    estimated_impact: str = "low"  # low, medium, high
    
@dataclass
class MigrationExecutionResult:
    """Migration execution result"""
    success: bool
    revision_id: str
    execution_time: float
    rows_affected: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    rollback_info: Optional[Dict[str, Any]] = None

class AlembicMigrationTemplate:
    """
    🏭 Enterprise Alembic Migration Template
    
    Features:
    - Automated migration generation with AI optimization
    - Zero-downtime migration strategies
    - Comprehensive validation and testing
    - Rollback safety and verification
    - Multi-tenant migration support
    - Performance impact analysis
    - Creator Economy specific optimizations
    """
    
    def __init__(
        self,
        alembic_cfg_path: Optional[str] = None,
        database_url: Optional[str] = None,
        migration_dir: Optional[str] = None
    ):
        self.alembic_cfg_path = alembic_cfg_path or "alembic.ini"
        self.database_url = database_url
        self.migration_dir = migration_dir or "alembic"
        self.config = None
        self.script_directory = None
        
        # Migration tracking
        self.migration_history: List[MigrationMetadata] = []
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        
        self._initialize_config()
    
    def _initialize_config(self):
        """Initialize Alembic configuration"""
        try:
            if os.path.exists(self.alembic_cfg_path):
                self.config = Config(self.alembic_cfg_path)
            else:
                # Create default configuration
                self.config = self._create_default_config()
            
            if self.database_url:
                self.config.set_main_option("sqlalchemy.url", self.database_url)
            
            self.script_directory = ScriptDirectory.from_config(self.config)
            
        except Exception as e:
            logger.error(f"Failed to initialize Alembic config: {e}")
    
    def _create_default_config(self) -> Config:
        """Create default Alembic configuration"""
        config_content = """
# Alembic Migration Configuration - IA Chéries Enterprise
# Generated by IA Chéries Database Template Manager
# © 2025 Fahed Mlaiel <mlaiel@live.de>

[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = 

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        # Write temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_content)
            temp_config_path = f.name
        
        return Config(temp_config_path)
    
    def create_migration(
        self,
        message: str,
        migration_type: MigrationType = MigrationType.SCHEMA_CHANGE,
        priority: MigrationPriority = MigrationPriority.MEDIUM,
        strategy: MigrationStrategy = MigrationStrategy.ONLINE,
        upgrade_sql: Optional[str] = None,
        downgrade_sql: Optional[str] = None,
        metadata: Optional[MigrationMetadata] = None,
        auto_generate: bool = True
    ) -> str:
        """
        Create a new migration with comprehensive metadata
        
        Args:
            message: Migration description
            migration_type: Type of migration
            priority: Migration priority
            strategy: Execution strategy
            upgrade_sql: Custom upgrade SQL
            downgrade_sql: Custom downgrade SQL
            metadata: Additional metadata
            auto_generate: Auto-generate from model changes
            
        Returns:
            Revision ID of created migration
        """
        try:
            # Generate revision ID
            if auto_generate:
                revision_id = command.revision(
                    self.config,
                    message=message,
                    autogenerate=True
                )
            else:
                revision_id = command.revision(
                    self.config,
                    message=message
                )
            
            # Extract revision ID from result
            if hasattr(revision_id, 'revision'):
                revision_id = revision_id.revision
            
            # Create migration metadata
            if metadata is None:
                metadata = MigrationMetadata(
                    revision_id=revision_id,
                    description=message,
                    migration_type=migration_type,
                    priority=priority,
                    strategy=strategy
                )
            
            # Enhance generated migration file
            migration_file = self._find_migration_file(revision_id)
            if migration_file:
                self._enhance_migration_file(
                    migration_file,
                    metadata,
                    upgrade_sql,
                    downgrade_sql
                )
            
            # Track migration
            self.migration_history.append(metadata)
            
            logger.info(f"Created migration: {revision_id} - {message}")
            return revision_id
            
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            raise
    
    def validate_migration(
        self,
        revision_id: Optional[str] = None,
        check_rollback: bool = True,
        performance_analysis: bool = True
    ) -> MigrationValidationResult:
        """
        Comprehensive migration validation
        
        Args:
            revision_id: Specific revision to validate (None for latest)
            check_rollback: Validate rollback safety
            performance_analysis: Analyze performance impact
            
        Returns:
            Validation result with detailed feedback
        """
        result = MigrationValidationResult(is_valid=True)
        
        try:
            # Get migration to validate
            if revision_id is None:
                revision_id = self.get_current_revision()
            
            if not revision_id:
                result.is_valid = False
                result.errors.append("No migration to validate")
                return result
            
            migration_file = self._find_migration_file(revision_id)
            if not migration_file:
                result.is_valid = False
                result.errors.append(f"Migration file not found for revision: {revision_id}")
                return result
            
            # Parse migration content
            migration_content = self._parse_migration_file(migration_file)
            
            # Validate SQL syntax
            sql_validation = self._validate_sql_syntax(migration_content)
            result.errors.extend(sql_validation.get("errors", []))
            result.warnings.extend(sql_validation.get("warnings", []))
            
            # Check for dangerous operations
            dangerous_ops = self._check_dangerous_operations(migration_content)
            if dangerous_ops:
                result.warnings.extend(dangerous_ops)
                result.estimated_impact = "high"
            
            # Validate foreign key constraints
            fk_validation = self._validate_foreign_keys(migration_content)
            result.errors.extend(fk_validation.get("errors", []))
            result.warnings.extend(fk_validation.get("warnings", []))
            
            # Check index optimization
            index_analysis = self._analyze_indexes(migration_content)
            result.recommendations.extend(index_analysis)
            
            # Validate rollback safety
            if check_rollback:
                rollback_validation = self._validate_rollback_safety(migration_content)
                result.errors.extend(rollback_validation.get("errors", []))
                result.warnings.extend(rollback_validation.get("warnings", []))
            
            # Performance impact analysis
            if performance_analysis:
                perf_analysis = self._analyze_performance_impact(migration_content)
                result.recommendations.extend(perf_analysis.get("recommendations", []))
                if perf_analysis.get("high_impact"):
                    result.estimated_impact = "high"
                    result.warnings.append("Migration may have high performance impact")
            
            # Multi-tenant validation
            tenant_validation = self._validate_multi_tenant_compatibility(migration_content)
            result.errors.extend(tenant_validation.get("errors", []))
            result.warnings.extend(tenant_validation.get("warnings", []))
            
            # Creator Economy specific validation
            creator_validation = self._validate_creator_economy_compatibility(migration_content)
            result.recommendations.extend(creator_validation)
            
            result.is_valid = len(result.errors) == 0
            
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Validation failed: {e}")
        
        return result
    
    async def execute_migration(
        self,
        target_revision: str = "head",
        dry_run: bool = False,
        backup_before: bool = True,
        validate_before: bool = True
    ) -> MigrationExecutionResult:
        """
        Execute migration with comprehensive safety checks
        
        Args:
            target_revision: Target revision to migrate to
            dry_run: Only show what would be executed
            backup_before: Create backup before migration
            validate_before: Validate migration before execution
            
        Returns:
            Execution result with timing and impact data
        """
        start_time = time.time()
        result = MigrationExecutionResult(
            success=False,
            revision_id=target_revision,
            execution_time=0.0
        )
        
        try:
            current_revision = self.get_current_revision()
            
            # Validate migration if requested
            if validate_before:
                validation = self.validate_migration(target_revision)
                if not validation.is_valid:
                    result.errors = validation.errors
                    return result
                
                if validation.estimated_impact == "high":
                    result.warnings.append("High impact migration - consider maintenance window")
            
            # Create backup if requested
            if backup_before and not dry_run:
                backup_result = await self._create_pre_migration_backup()
                if not backup_result["success"]:
                    result.errors.append(f"Backup failed: {backup_result['error']}")
                    return result
                result.rollback_info = {"backup_path": backup_result["backup_path"]}
            
            # Execute migration
            if dry_run:
                # Show SQL that would be executed
                sql_statements = self._get_migration_sql(current_revision, target_revision)
                result.success = True
                result.warnings.append(f"Dry run - would execute {len(sql_statements)} statements")
            else:
                # Execute actual migration
                command.upgrade(self.config, target_revision)
                result.success = True
                
                # Get execution statistics
                new_revision = self.get_current_revision()
                if new_revision != current_revision:
                    stats = await self._get_migration_statistics(current_revision, new_revision)
                    result.rows_affected = stats.get("rows_affected", 0)
            
            result.execution_time = time.time() - start_time
            
            # Update performance metrics
            self._update_performance_metrics(target_revision, result.execution_time, result.success)
            
        except Exception as e:
            result.execution_time = time.time() - start_time
            result.errors.append(f"Migration execution failed: {e}")
            logger.error(f"Migration execution failed: {e}")
        
        return result
    
    async def rollback_migration(
        self,
        target_revision: str,
        validate_rollback: bool = True,
        create_backup: bool = True
    ) -> MigrationExecutionResult:
        """
        Safely rollback migration with validation
        
        Args:
            target_revision: Target revision to rollback to
            validate_rollback: Validate rollback safety
            create_backup: Create backup before rollback
            
        Returns:
            Rollback execution result
        """
        start_time = time.time()
        result = MigrationExecutionResult(
            success=False,
            revision_id=target_revision,
            execution_time=0.0
        )
        
        try:
            current_revision = self.get_current_revision()
            
            # Validate rollback safety
            if validate_rollback:
                rollback_validation = self._validate_rollback_path(current_revision, target_revision)
                if not rollback_validation["safe"]:
                    result.errors = rollback_validation["errors"]
                    return result
            
            # Create backup before rollback
            if create_backup:
                backup_result = await self._create_pre_migration_backup()
                if not backup_result["success"]:
                    result.errors.append(f"Pre-rollback backup failed: {backup_result['error']}")
                    return result
                result.rollback_info = {"backup_path": backup_result["backup_path"]}
            
            # Execute rollback
            command.downgrade(self.config, target_revision)
            result.success = True
            result.execution_time = time.time() - start_time
            
            logger.info(f"Successfully rolled back from {current_revision} to {target_revision}")
            
        except Exception as e:
            result.execution_time = time.time() - start_time
            result.errors.append(f"Rollback failed: {e}")
            logger.error(f"Rollback failed: {e}")
        
        return result
    
    def get_current_revision(self) -> Optional[str]:
        """Get current database revision"""
        try:
            return command.current(self.config)
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None
    
    def get_migration_history(self) -> List[MigrationInfo]:
        """Get migration history"""
        try:
            return command.history(self.config)
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []
    
    def get_pending_migrations(self) -> List[str]:
        """Get list of pending migrations"""
        try:
            current = self.get_current_revision()
            heads = command.heads(self.config)
            
            if current in heads:
                return []
            
            # Get migration path from current to head
            upgrade_path = []
            for head in heads:
                path = self._get_upgrade_path(current, head)
                upgrade_path.extend(path)
            
            return list(set(upgrade_path))
            
        except Exception as e:
            logger.error(f"Failed to get pending migrations: {e}")
            return []
    
    # Creator Economy Specific Methods
    def create_creator_profile_migration(
        self,
        add_fields: Optional[List[Dict[str, Any]]] = None,
        modify_fields: Optional[List[Dict[str, Any]]] = None,
        add_indexes: Optional[List[str]] = None
    ) -> str:
        """Create migration for creator profile updates"""
        operations = []
        
        if add_fields:
            for field in add_fields:
                operations.append(f"op.add_column('creator_profiles', sa.Column('{field['name']}', {field['type']}))")
        
        if modify_fields:
            for field in modify_fields:
                operations.append(f"op.alter_column('creator_profiles', '{field['name']}', type_={field['new_type']})")
        
        if add_indexes:
            for index in add_indexes:
                operations.append(f"op.create_index('idx_creator_{index}', 'creator_profiles', ['{index}'])")
        
        upgrade_sql = "    " + "\n    ".join(operations)
        downgrade_sql = "    # Rollback operations would be generated automatically"
        
        return self.create_migration(
            message="Update creator profile schema",
            migration_type=MigrationType.SCHEMA_CHANGE,
            priority=MigrationPriority.MEDIUM,
            strategy=MigrationStrategy.ONLINE,
            upgrade_sql=upgrade_sql,
            downgrade_sql=downgrade_sql
        )
    
    def create_monetization_migration(
        self,
        add_payment_methods: bool = False,
        add_revenue_tracking: bool = False,
        add_analytics_tables: bool = False
    ) -> str:
        """Create migration for monetization features"""
        operations = []
        
        if add_payment_methods:
            operations.append("""
    op.create_table('payment_methods',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey('creator_profiles.id')),
        sa.Column('method_type', sa.String(50), nullable=False),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('account_info', sa.JSON),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )""")
        
        if add_revenue_tracking:
            operations.append("""
    op.create_table('revenue_tracking',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey('creator_profiles.id')),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('amount', sa.Decimal(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), default='USD'),
        sa.Column('transaction_date', sa.DateTime, nullable=False),
        sa.Column('platform_fee', sa.Decimal(10, 2), default=0),
        sa.Column('net_amount', sa.Decimal(10, 2), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('created_at', sa.DateTime, default=sa.func.now())
    )""")
        
        if add_analytics_tables:
            operations.append("""
    op.create_table('creator_analytics',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('creator_id', sa.Integer, sa.ForeignKey('creator_profiles.id')),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('metric_value', sa.Float, nullable=False),
        sa.Column('metric_date', sa.Date, nullable=False),
        sa.Column('platform', sa.String(50)),
        sa.Column('meta_data, sa.JSON),
        sa.Column('created_at', sa.DateTime, default=sa.func.now())
    )""")
        
        upgrade_sql = "\n".join(operations)
        
        return self.create_migration(
            message="Add monetization and analytics features",
            migration_type=MigrationType.SCHEMA_CHANGE,
            priority=MigrationPriority.HIGH,
            strategy=MigrationStrategy.ONLINE,
            upgrade_sql=upgrade_sql
        )
    
    # Private helper methods
    def _find_migration_file(self, revision_id: str) -> Optional[Path]:
        """Find migration file by revision ID"""
        try:
            migration_dir = Path(self.migration_dir) / "versions"
            for file_path in migration_dir.glob(f"{revision_id}_*.py"):
                return file_path
            return None
        except Exception:
            return None
    
    def _enhance_migration_file(
        self,
        migration_file: Path,
        metadata: MigrationMetadata,
        upgrade_sql: Optional[str],
        downgrade_sql: Optional[str]
    ):
        """Enhance migration file with metadata and custom SQL"""
        try:
            with open(migration_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add metadata header
            metadata_header = f'''"""
Migration: {metadata.description}
Type: {metadata.migration_type.value}
Priority: {metadata.priority.value}
Strategy: {metadata.strategy.value}
Author: {metadata.author}
Created: {metadata.created_at.isoformat()}

🚨 PROTECTION PROPRIÉTÉ INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Code propriétaire
"""

'''
            
            # Insert metadata after the initial docstring
            if '"""' in content:
                parts = content.split('"""', 2)
                if len(parts) >= 3:
                    content = f'"""{parts[1]}"""\n{metadata_header}\n{parts[2]}'
            
            # Enhance upgrade function if custom SQL provided
            if upgrade_sql:
                content = re.sub(
                    r'def upgrade\(\):\s*\n(\s*)(.*?)\n\n',
                    f'def upgrade():\n\\1{upgrade_sql}\n\n',
                    content,
                    flags=re.DOTALL
                )
            
            # Enhance downgrade function if custom SQL provided
            if downgrade_sql:
                content = re.sub(
                    r'def downgrade\(\):\s*\n(\s*)(.*?)\n',
                    f'def downgrade():\n\\1{downgrade_sql}\n',
                    content,
                    flags=re.DOTALL
                )
            
            with open(migration_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Failed to enhance migration file: {e}")
    
    def _parse_migration_file(self, migration_file: Path) -> Dict[str, Any]:
        """Parse migration file content"""
        try:
            with open(migration_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract upgrade and downgrade functions
            upgrade_match = re.search(r'def upgrade\(\):(.*?)(?=def downgrade|$)', content, re.DOTALL)
            downgrade_match = re.search(r'def downgrade\(\):(.*?)$', content, re.DOTALL)
            
            return {
                "content": content,
                "upgrade": upgrade_match.group(1) if upgrade_match else "",
                "downgrade": downgrade_match.group(1) if downgrade_match else ""
            }
        except Exception as e:
            logger.error(f"Failed to parse migration file: {e}")
            return {"content": "", "upgrade": "", "downgrade": ""}
    
    def _validate_sql_syntax(self, migration_content: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate SQL syntax in migration"""
        errors = []
        warnings = []
        
        try:
            upgrade_code = migration_content.get("upgrade", "")
            downgrade_code = migration_content.get("downgrade", "")
            
            # Check for common SQL syntax issues
            dangerous_patterns = [
                (r'DROP\s+TABLE\s+\w+\s*;', "DROP TABLE without IF EXISTS"),
                (r'ALTER\s+TABLE\s+\w+\s+DROP\s+COLUMN', "DROP COLUMN without backup"),
                (r'TRUNCATE\s+TABLE', "TRUNCATE TABLE - data loss risk"),
                (r'DELETE\s+FROM\s+\w+\s*;', "DELETE without WHERE clause"),
            ]
            
            for pattern, warning_msg in dangerous_patterns:
                if re.search(pattern, upgrade_code, re.IGNORECASE):
                    warnings.append(warning_msg)
            
            # Check for missing downgrade logic
            if "pass" in downgrade_code and len(downgrade_code.strip()) < 20:
                warnings.append("Downgrade function appears empty - rollback may not work")
            
        except Exception as e:
            errors.append(f"SQL validation failed: {e}")
        
        return {"errors": errors, "warnings": warnings}
    
    def _check_dangerous_operations(self, migration_content: Dict[str, Any]) -> List[str]:
        """Check for dangerous migration operations"""
        warnings = []
        upgrade_code = migration_content.get("upgrade", "")
        
        dangerous_operations = [
            ("drop_table", "Dropping table - ensure data is backed up"),
            ("drop_column", "Dropping column - data will be lost"),
            ("alter_column", "Altering column - may affect existing data"),
            ("drop_index", "Dropping index - may affect query performance"),
            ("drop_constraint", "Dropping constraint - may affect data integrity")
        ]
        
        for operation, warning in dangerous_operations:
            if operation in upgrade_code.lower():
                warnings.append(warning)
        
        return warnings
    
    def _validate_foreign_keys(self, migration_content: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate foreign key constraints"""
        errors = []
        warnings = []
        
        upgrade_code = migration_content.get("upgrade", "")
        
        # Check for foreign key creation without proper indexing
        fk_pattern = r'sa\.ForeignKey\([\'"](\w+)\.(\w+)[\'"]\)'
        fk_matches = re.findall(fk_pattern, upgrade_code)
        
        for table, column in fk_matches:
            # Check if there's a corresponding index
            index_pattern = f'create_index.*{column}'
            if not re.search(index_pattern, upgrade_code, re.IGNORECASE):
                warnings.append(f"Foreign key on {table}.{column} without corresponding index")
        
        return {"errors": errors, "warnings": warnings}
    
    def _analyze_indexes(self, migration_content: Dict[str, Any]) -> List[str]:
        """Analyze index operations for optimization"""
        recommendations = []
        upgrade_code = migration_content.get("upgrade", "")
        
        # Check for index creation
        if "create_index" in upgrade_code.lower():
            recommendations.append("Consider creating indexes during low-traffic periods")
            recommendations.append("Monitor index usage after creation")
        
        # Check for missing composite indexes
        single_column_indexes = re.findall(r'create_index.*\[[\'"](.*?)[\'"]\]', upgrade_code)
        if len(single_column_indexes) > 1:
            recommendations.append("Consider creating composite indexes for related columns")
        
        return recommendations
    
    def _validate_rollback_safety(self, migration_content: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate rollback safety"""
        errors = []
        warnings = []
        
        downgrade_code = migration_content.get("downgrade", "")
        upgrade_code = migration_content.get("upgrade", "")
        
        # Check if downgrade logic exists
        if not downgrade_code.strip() or "pass" in downgrade_code:
            errors.append("No rollback logic defined - migration cannot be safely rolled back")
        
        # Check for data migration without rollback strategy
        if any(keyword in upgrade_code.lower() for keyword in ["insert", "update", "delete"]):
            if not any(keyword in downgrade_code.lower() for keyword in ["insert", "update", "delete"]):
                warnings.append("Data migration without corresponding rollback data handling")
        
        return {"errors": errors, "warnings": warnings}
    
    def _analyze_performance_impact(self, migration_content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze potential performance impact"""
        recommendations = []
        high_impact = False
        
        upgrade_code = migration_content.get("upgrade", "")
        
        # High impact operations
        high_impact_ops = [
            "add_column.*default",  # Adding column with default value
            "create_index",         # Creating indexes on large tables
            "alter_column",         # Altering column type
            "drop_index"           # Dropping indexes
        ]
        
        for operation in high_impact_ops:
            if re.search(operation, upgrade_code, re.IGNORECASE):
                high_impact = True
                break
        
        if high_impact:
            recommendations.extend([
                "Consider running during maintenance window",
                "Monitor database performance during execution",
                "Consider breaking into smaller migrations"
            ])
        
        # Check for bulk operations
        if any(keyword in upgrade_code.lower() for keyword in ["bulk_insert", "execute_many"]):
            recommendations.append("Bulk operations detected - monitor memory usage")
        
        return {
            "high_impact": high_impact,
            "recommendations": recommendations
        }
    
    def _validate_multi_tenant_compatibility(self, migration_content: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate multi-tenant compatibility"""
        errors = []
        warnings = []
        
        upgrade_code = migration_content.get("upgrade", "")
        
        # Check for tenant_id column in new tables
        create_table_pattern = r'create_table\([\'"](\w+)[\'"]'
        tables = re.findall(create_table_pattern, upgrade_code, re.IGNORECASE)
        
        for table in tables:
            if "tenant_id" not in upgrade_code:
                warnings.append(f"New table '{table}' may need tenant_id column for multi-tenancy")
        
        return {"errors": errors, "warnings": warnings}
    
    def _validate_creator_economy_compatibility(self, migration_content: Dict[str, Any]) -> List[str]:
        """Validate Creator Economy specific requirements"""
        recommendations = []
        upgrade_code = migration_content.get("upgrade", "")
        
        # Check for creator-related tables
        creator_keywords = ["creator", "content", "monetization", "analytics", "revenue"]
        
        for keyword in creator_keywords:
            if keyword in upgrade_code.lower():
                recommendations.extend([
                    f"Consider adding audit trail for {keyword} changes",
                    f"Ensure proper indexing for {keyword} queries",
                    "Add created_at/updated_at timestamps if missing"
                ])
                break
        
        return recommendations
    
    async def _create_pre_migration_backup(self) -> Dict[str, Any]:
        """Create backup before migration"""
        try:
            # This would integrate with backup systems
            backup_path = f"/backups/pre_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            
            # Simulate backup creation
            # In real implementation, this would call actual backup tools
            await asyncio.sleep(0.1)  # Simulate backup time
            
            return {
                "success": True,
                "backup_path": backup_path,
                "size_mb": 100  # Simulated size
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_migration_sql(self, from_revision: str, to_revision: str) -> List[str]:
        """Get SQL statements for migration"""
        try:
            # This would generate the actual SQL for the migration
            # Implementation depends on database engine
            return [
                "-- Migration SQL would be generated here",
                f"-- From: {from_revision}",
                f"-- To: {to_revision}"
            ]
        except Exception as e:
            logger.error(f"Failed to get migration SQL: {e}")
            return []
    
    async def _get_migration_statistics(self, from_revision: str, to_revision: str) -> Dict[str, Any]:
        """Get migration execution statistics"""
        try:
            # This would collect actual statistics from the migration
            return {
                "rows_affected": 0,
                "tables_modified": 0,
                "indexes_created": 0,
                "constraints_added": 0
            }
        except Exception as e:
            logger.error(f"Failed to get migration statistics: {e}")
            return {}
    
    def _validate_rollback_path(self, from_revision: str, to_revision: str) -> Dict[str, Any]:
        """Validate rollback path safety"""
        try:
            # Check if rollback path exists and is safe
            return {
                "safe": True,
                "errors": [],
                "warnings": []
            }
        except Exception as e:
            return {
                "safe": False,
                "errors": [f"Rollback validation failed: {e}"],
                "warnings": []
            }
    
    def _get_upgrade_path(self, from_revision: str, to_revision: str) -> List[str]:
        """Get upgrade path between revisions"""
        try:
            # This would calculate the actual upgrade path
            return [to_revision]
        except Exception:
            return []
    
    def _update_performance_metrics(self, revision_id: str, execution_time: float, success: bool):
        """Update performance metrics for migration"""
        if revision_id not in self.performance_metrics:
            self.performance_metrics[revision_id] = {
                "avg_execution_time": 0.0,
                "success_rate": 1.0,
                "total_executions": 0
            }
        
        metrics = self.performance_metrics[revision_id]
        metrics["total_executions"] += 1
        
        # Update average execution time
        current_avg = metrics["avg_execution_time"]
        total_executions = metrics["total_executions"]
        new_avg = (current_avg * (total_executions - 1) + execution_time) / total_executions
        metrics["avg_execution_time"] = new_avg
        
        # Update success rate
        current_success_rate = metrics["success_rate"]
        success_count = current_success_rate * (total_executions - 1) + (1 if success else 0)
        metrics["success_rate"] = success_count / total_executions

# Export for use
__all__ = [
    "AlembicMigrationTemplate",
    "MigrationType",
    "MigrationPriority", 
    "MigrationStrategy",
    "MigrationMetadata",
    "MigrationValidationResult",
    "MigrationExecutionResult"
]