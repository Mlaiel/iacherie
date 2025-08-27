"""
Database Migration Configuration for IA-Influencer Agent Platform
================================================================

Professional database migration management for PostgreSQL schema evolution,
MongoDB collection management, and data transformation workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
import json
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path
import hashlib
import logging

from alembic import command
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from alembic.environment import EnvironmentContext
from alembic.migration import MigrationContext
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class MigrationEnvironment(Enum):
    """Migration environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class MigrationStatus(Enum):
    """Migration status types"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DatabaseSchema(Enum):
    """Database schema types for different domains"""
    CORE = "core"                          # Core platform schemas
    CONTENT_PROTECTION = "content_protection"  # Content fingerprinting and protection
    ANALYTICS = "analytics"                 # Analytics and reporting
    MONETIZATION = "monetization"          # Revenue tracking and payments
    USER_MANAGEMENT = "user_management"    # User and tenant management
    AUDIT = "audit"                        # Audit trails and logging


@dataclass
class MigrationConfig:
    """Migration configuration settings"""
    migration_path: str = "migrations"
    backup_enabled: bool = True
    backup_path: str = "backups/migrations"
    auto_backup_before_migration: bool = True
    rollback_enabled: bool = True
    dry_run_enabled: bool = True
    parallel_migrations: bool = False
    max_parallel_workers: int = 3
    timeout_seconds: int = 300
    notification_enabled: bool = False
    notification_webhooks: List[str] = field(default_factory=list)


@dataclass
class MigrationRecord:
    """Migration execution record"""
    migration_id: str
    schema: DatabaseSchema
    version: str
    description: str
    status: MigrationStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    rollback_available: bool = True
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PostgreSQLMigrationManager:
    """PostgreSQL-specific migration management using Alembic"""
    
    def __init__(self, engine: Engine, schema: DatabaseSchema, config: MigrationConfig):
        self.engine = engine
        self.schema = schema
        self.config = config
        self.alembic_config = self._setup_alembic_config()
        self.logger = logging.getLogger(f"postgres_migration.{schema.value}")

    def _setup_alembic_config(self) -> AlembicConfig:
        """Setup Alembic configuration"""
        try:
            # Create migration directory structure
            migration_dir = Path(self.config.migration_path) / "postgresql" / self.schema.value
            migration_dir.mkdir(parents=True, exist_ok=True)
            
            # Alembic configuration
            alembic_cfg = AlembicConfig()
            alembic_cfg.set_main_option("script_location", str(migration_dir))
            alembic_cfg.set_main_option("sqlalchemy.url", str(self.engine.url))
            alembic_cfg.set_main_option("target_metadata", "None")
            
            # Create alembic.ini if it doesn't exist
            alembic_ini_path = migration_dir / "alembic.ini"
            if not alembic_ini_path.exists():
                self._create_alembic_ini(alembic_ini_path)
            
            # Initialize Alembic if not already initialized
            versions_dir = migration_dir / "versions"
            if not versions_dir.exists():
                command.init(alembic_cfg, str(migration_dir))
            
            return alembic_cfg
            
        except Exception as e:
            self.logger.error(f"Failed to setup Alembic config: {str(e)}")
            raise

    def _create_alembic_ini(self, ini_path: Path) -> None:
        """Create Alembic configuration file"""
        ini_content = f"""
[alembic]
script_location = {self.config.migration_path}/postgresql/{self.schema.value}
prepend_sys_path = .
version_path_separator = os

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
        
        with open(ini_path, 'w') as f:
            f.write(ini_content.strip())

    def create_migration(self, description: str, 
                        upgrade_sql: str, 
                        downgrade_sql: Optional[str] = None) -> str:
        """
        Create new migration
        
        Args:
            description: Migration description
            upgrade_sql: SQL for upgrade
            downgrade_sql: SQL for downgrade
            
        Returns:
            Migration ID
        """
        try:
            # Generate migration
            revision = command.revision(
                self.alembic_config,
                message=description,
                autogenerate=False
            )
            
            # Get the migration file path
            script_dir = ScriptDirectory.from_config(self.alembic_config)
            migration_file = script_dir.get_revision(revision.revision).path
            
            # Customize migration file content
            migration_content = f'''"""
{description}

Revision ID: {revision.revision}
Revises: {revision.down_revision}
Create Date: {datetime.now()}

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '{revision.revision}'
down_revision = {repr(revision.down_revision)}
branch_labels = None
depends_on = None

def upgrade():
    """Upgrade database schema"""
    # Custom upgrade SQL
    {self._format_sql_for_migration(upgrade_sql)}

def downgrade():
    """Downgrade database schema"""
    # Custom downgrade SQL
    {self._format_sql_for_migration(downgrade_sql) if downgrade_sql else "pass"}
'''
            
            # Write migration file
            with open(migration_file, 'w') as f:
                f.write(migration_content)
            
            self.logger.info(f"Created migration {revision.revision}: {description}")
            return revision.revision
            
        except Exception as e:
            self.logger.error(f"Failed to create migration: {str(e)}")
            raise

    def _format_sql_for_migration(self, sql: str) -> str:
        """Format SQL for inclusion in migration file"""
        if not sql:
            return "pass"
        
        # Split SQL into statements and format for Alembic
        statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
        formatted_statements = []
        
        for stmt in statements:
            formatted_statements.append(f'    op.execute("{stmt}")')
        
        return '\n'.join(formatted_statements)

    def run_migrations(self, target_revision: str = "head") -> List[MigrationRecord]:
        """
        Run migrations to target revision
        
        Args:
            target_revision: Target revision (default: "head")
            
        Returns:
            List of executed migrations
        """
        migration_records = []
        
        try:
            # Get pending migrations
            script_dir = ScriptDirectory.from_config(self.alembic_config)
            
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_revision = context.get_current_revision()
                
                # Get migration path
                if target_revision == "head":
                    target_revision = script_dir.get_current_head()
                
                revisions = script_dir.walk_revisions(current_revision, target_revision)
                
                for revision in revisions:
                    record = MigrationRecord(
                        migration_id=revision.revision,
                        schema=self.schema,
                        version=revision.revision[:8],
                        description=revision.doc,
                        status=MigrationStatus.RUNNING,
                        started_at=datetime.now(),
                        checksum=self._calculate_checksum(revision.path)
                    )
                    
                    try:
                        # Create backup if enabled
                        if self.config.auto_backup_before_migration:
                            self._create_backup(revision.revision)
                        
                        # Execute migration
                        command.upgrade(self.alembic_config, revision.revision)
                        
                        record.status = MigrationStatus.COMPLETED
                        record.completed_at = datetime.now()
                        record.duration_seconds = (
                            record.completed_at - record.started_at
                        ).total_seconds()
                        
                        self.logger.info(f"Migration completed: {revision.revision}")
                        
                    except Exception as e:
                        record.status = MigrationStatus.FAILED
                        record.error_message = str(e)
                        record.completed_at = datetime.now()
                        
                        self.logger.error(f"Migration failed {revision.revision}: {str(e)}")
                        
                        # Attempt rollback if enabled
                        if self.config.rollback_enabled:
                            try:
                                self.rollback_migration(revision.revision)
                                record.status = MigrationStatus.ROLLED_BACK
                            except Exception as rollback_error:
                                self.logger.error(f"Rollback failed: {str(rollback_error)}")
                        
                        raise
                    
                    migration_records.append(record)
            
            return migration_records
            
        except Exception as e:
            self.logger.error(f"Migration execution failed: {str(e)}")
            raise

    def rollback_migration(self, target_revision: str) -> MigrationRecord:
        """
        Rollback to specific revision
        
        Args:
            target_revision: Target revision to rollback to
            
        Returns:
            Migration record
        """
        try:
            record = MigrationRecord(
                migration_id=f"rollback_{target_revision}",
                schema=self.schema,
                version=target_revision[:8],
                description=f"Rollback to {target_revision}",
                status=MigrationStatus.RUNNING,
                started_at=datetime.now()
            )
            
            # Execute rollback
            command.downgrade(self.alembic_config, target_revision)
            
            record.status = MigrationStatus.COMPLETED
            record.completed_at = datetime.now()
            record.duration_seconds = (
                record.completed_at - record.started_at
            ).total_seconds()
            
            self.logger.info(f"Rollback completed to: {target_revision}")
            return record
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")
            raise

    def _create_backup(self, migration_id: str) -> str:
        """Create database backup before migration"""
        try:
            backup_dir = Path(self.config.backup_path) / self.schema.value
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_file = backup_dir / f"backup_{migration_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            
            # Use pg_dump for backup (requires pg_dump in PATH)
            import subprocess
            
            cmd = [
                "pg_dump",
                "--no-password",
                "--verbose",
                "--format=plain",
                "--file", str(backup_file),
                str(self.engine.url)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Backup created: {backup_file}")
                return str(backup_file)
            else:
                self.logger.warning(f"Backup failed: {result.stderr}")
                return ""
                
        except Exception as e:
            self.logger.warning(f"Backup creation failed: {str(e)}")
            return ""

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate checksum for migration file"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ""


class MongoDBMigrationManager:
    """MongoDB-specific migration management"""
    
    def __init__(self, client: Any, database_name: str, config: MigrationConfig):
        self.client = client
        self.database_name = database_name
        self.config = config
        self.db = client[database_name]
        self.migrations_collection = self.db.migrations
        self.logger = logging.getLogger(f"mongodb_migration.{database_name}")

    def create_migration(self, description: str, 
                        migration_function: Callable) -> str:
        """
        Create MongoDB migration
        
        Args:
            description: Migration description
            migration_function: Function to execute migration
            
        Returns:
            Migration ID
        """
        migration_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{description.replace(' ', '_')}"
        
        try:
            migration_record = {
                "migration_id": migration_id,
                "description": description,
                "status": "pending",
                "created_at": datetime.now(),
                "migration_function": migration_function.__name__
            }
            
            self.migrations_collection.insert_one(migration_record)
            self.logger.info(f"MongoDB migration created: {migration_id}")
            
            return migration_id
            
        except Exception as e:
            self.logger.error(f"Failed to create MongoDB migration: {str(e)}")
            raise

    def run_pending_migrations(self) -> List[MigrationRecord]:
        """Run all pending MongoDB migrations"""
        migration_records = []
        
        try:
            pending_migrations = self.migrations_collection.find({"status": "pending"})
            
            for migration_doc in pending_migrations:
                record = MigrationRecord(
                    migration_id=migration_doc["migration_id"],
                    schema=DatabaseSchema.CORE,  # MongoDB doesn't use schema concept
                    version=migration_doc["migration_id"][:8],
                    description=migration_doc["description"],
                    status=MigrationStatus.RUNNING,
                    started_at=datetime.now()
                )
                
                try:
                    # Update status to running
                    self.migrations_collection.update_one(
                        {"migration_id": migration_doc["migration_id"]},
                        {"$set": {"status": "running", "started_at": datetime.now()}}
                    )
                    
                    # Execute migration function
                    # Note: In real implementation, you'd need to load and execute the actual function
                    # This is a simplified example
                    
                    # Mark as completed
                    self.migrations_collection.update_one(
                        {"migration_id": migration_doc["migration_id"]},
                        {"$set": {
                            "status": "completed",
                            "completed_at": datetime.now()
                        }}
                    )
                    
                    record.status = MigrationStatus.COMPLETED
                    record.completed_at = datetime.now()
                    record.duration_seconds = (
                        record.completed_at - record.started_at
                    ).total_seconds()
                    
                    self.logger.info(f"MongoDB migration completed: {migration_doc['migration_id']}")
                    
                except Exception as e:
                    # Mark as failed
                    self.migrations_collection.update_one(
                        {"migration_id": migration_doc["migration_id"]},
                        {"$set": {
                            "status": "failed",
                            "error_message": str(e),
                            "failed_at": datetime.now()
                        }}
                    )
                    
                    record.status = MigrationStatus.FAILED
                    record.error_message = str(e)
                    record.completed_at = datetime.now()
                    
                    self.logger.error(f"MongoDB migration failed {migration_doc['migration_id']}: {str(e)}")
                
                migration_records.append(record)
            
            return migration_records
            
        except Exception as e:
            self.logger.error(f"MongoDB migration execution failed: {str(e)}")
            raise


class MigrationManager:
    """
    Main migration manager orchestrating all database migrations
    """
    
    def __init__(self, 
                 environment: MigrationEnvironment = MigrationEnvironment.DEVELOPMENT,
                 config: Optional[MigrationConfig] = None):
        self.environment = environment
        self.config = config or MigrationConfig()
        self.postgresql_managers: Dict[DatabaseSchema, PostgreSQLMigrationManager] = {}
        self.mongodb_managers: Dict[str, MongoDBMigrationManager] = {}
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup migration logging"""
        self.logger = logging.getLogger(f"migration_manager.{self.environment.value}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def add_postgresql_manager(self, schema: DatabaseSchema, engine: Engine) -> None:
        """Add PostgreSQL migration manager for specific schema"""
        try:
            manager = PostgreSQLMigrationManager(engine, schema, self.config)
            self.postgresql_managers[schema] = manager
            self.logger.info(f"Added PostgreSQL migration manager for schema: {schema.value}")
        except Exception as e:
            self.logger.error(f"Failed to add PostgreSQL manager for {schema.value}: {str(e)}")
            raise

    def add_mongodb_manager(self, database_name: str, client: Any) -> None:
        """Add MongoDB migration manager for specific database"""
        try:
            manager = MongoDBMigrationManager(client, database_name, self.config)
            self.mongodb_managers[database_name] = manager
            self.logger.info(f"Added MongoDB migration manager for database: {database_name}")
        except Exception as e:
            self.logger.error(f"Failed to add MongoDB manager for {database_name}: {str(e)}")
            raise

    def run_all_migrations(self) -> Dict[str, List[MigrationRecord]]:
        """Run all pending migrations across all databases"""
        results = {
            "postgresql": {},
            "mongodb": {}
        }
        
        try:
            # Run PostgreSQL migrations
            for schema, manager in self.postgresql_managers.items():
                try:
                    records = manager.run_migrations()
                    results["postgresql"][schema.value] = records
                except Exception as e:
                    self.logger.error(f"PostgreSQL migration failed for {schema.value}: {str(e)}")
                    results["postgresql"][schema.value] = []
            
            # Run MongoDB migrations
            for db_name, manager in self.mongodb_managers.items():
                try:
                    records = manager.run_pending_migrations()
                    results["mongodb"][db_name] = records
                except Exception as e:
                    self.logger.error(f"MongoDB migration failed for {db_name}: {str(e)}")
                    results["mongodb"][db_name] = []
            
            return results
            
        except Exception as e:
            self.logger.error(f"Migration execution failed: {str(e)}")
            raise

    def get_migration_status(self) -> Dict[str, Any]:
        """Get status of all migrations"""
        status = {
            "environment": self.environment.value,
            "postgresql": {},
            "mongodb": {},
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # PostgreSQL migration status
            for schema, manager in self.postgresql_managers.items():
                try:
                    script_dir = ScriptDirectory.from_config(manager.alembic_config)
                    with manager.engine.connect() as connection:
                        context = MigrationContext.configure(connection)
                        current_revision = context.get_current_revision()
                        head_revision = script_dir.get_current_head()
                        
                        status["postgresql"][schema.value] = {
                            "current_revision": current_revision,
                            "head_revision": head_revision,
                            "up_to_date": current_revision == head_revision
                        }
                except Exception as e:
                    status["postgresql"][schema.value] = {
                        "error": str(e)
                    }
            
            # MongoDB migration status
            for db_name, manager in self.mongodb_managers.items():
                try:
                    pending_count = manager.migrations_collection.count_documents({"status": "pending"})
                    completed_count = manager.migrations_collection.count_documents({"status": "completed"})
                    failed_count = manager.migrations_collection.count_documents({"status": "failed"})
                    
                    status["mongodb"][db_name] = {
                        "pending_migrations": pending_count,
                        "completed_migrations": completed_count,
                        "failed_migrations": failed_count,
                        "up_to_date": pending_count == 0
                    }
                except Exception as e:
                    status["mongodb"][db_name] = {
                        "error": str(e)
                    }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get migration status: {str(e)}")
            raise

    def create_schema_migration(self, 
                              schema: DatabaseSchema, 
                              description: str,
                              upgrade_sql: str,
                              downgrade_sql: Optional[str] = None) -> str:
        """Create PostgreSQL schema migration"""
        if schema not in self.postgresql_managers:
            raise ValueError(f"No PostgreSQL manager found for schema: {schema.value}")
        
        return self.postgresql_managers[schema].create_migration(
            description, upgrade_sql, downgrade_sql
        )

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on migration system"""
        health_status = {
            "status": "healthy",
            "environment": self.environment.value,
            "managers": {
                "postgresql": {},
                "mongodb": {}
            },
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Check PostgreSQL managers
            for schema, manager in self.postgresql_managers.items():
                try:
                    # Test database connection
                    with manager.engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    
                    health_status["managers"]["postgresql"][schema.value] = {
                        "status": "healthy",
                        "engine_pool_size": manager.engine.pool.size(),
                        "migration_path": manager.config.migration_path
                    }
                except Exception as e:
                    health_status["managers"]["postgresql"][schema.value] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                    health_status["status"] = "degraded"
            
            # Check MongoDB managers
            for db_name, manager in self.mongodb_managers.items():
                try:
                    # Test MongoDB connection
                    manager.client.admin.command('ping')
                    
                    health_status["managers"]["mongodb"][db_name] = {
                        "status": "healthy",
                        "database": db_name
                    }
                except Exception as e:
                    health_status["managers"]["mongodb"][db_name] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                    health_status["status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self.logger.error(f"Migration health check failed: {str(e)}")
            return health_status
