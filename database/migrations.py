"""🔄 Database Migrations - Core Migration Management
from datetime import datetime

===================================================
Module: database/migrations.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Database Migration Management - Production-Ready
Responsibility: Database schema evolution and data migrations

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This migrations module provides database migration management for:
- Schema evolution and versioning
- Data migrations and transformations
- Rollback capabilities
- Migration validation and testing
"""

import os
import logging
import datetime
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

# Optional imports for production features
try:
    import sqlalchemy
    from sqlalchemy import text, inspect
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

class Migration:
    """Represents a single database migration"""
    
    def __init__(self, version -> None: str, name -> None: str, up_func -> None: Callable = None, down_func -> None: Callable = None) -> None:
        self.version = version
        self.name = name
        self.up_func = up_func
        self.down_func = down_func
        self.created_at = datetime.datetime.utcnow()
        self.applied_at = None
    
    def apply(self, connection=None) -> bool:
        """Apply the migration"""
        try:
            if self.up_func:
                if connection:
                    self.up_func(connection)
                else:
                    self.up_func()
            self.applied_at = datetime.datetime.utcnow()
            logger.info(f"Applied migration {self.version}: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply migration {self.version}: {e}")
            return False
    
    def rollback(self, connection=None) -> bool:
        """Rollback the migration"""
        try:
            if self.down_func:
                if connection:
                    self.down_func(connection)
                else:
                    self.down_func()
            self.applied_at = None
            logger.info(f"Rolled back migration {self.version}: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to rollback migration {self.version}: {e}")
            return False

class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self, connection=None) -> None:
        self.connection = connection
        self.migrations: List[Migration] = []
        self.applied_migrations: List[str] = []
        self._initialize_migrations_table()
    
    def _initialize_migrations_table(self) -> None:
        """Initialize migrations tracking table"""
        if not SQLALCHEMY_AVAILABLE or not self.connection:
            logger.warning("SQLAlchemy not available or no connection, using in-memory tracking")
            return
        
        try:
            # Create migrations table if it doesn't exist
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.connection.execute(text(create_table_sql))
            self.connection.commit()
            
            # Load applied migrations
            result = self.connection.execute(text("SELECT version FROM schema_migrations"))
            self.applied_migrations = [row[0] for row in result.fetchall()]
            
        except Exception as e:
            logger.error(f"Failed to initialize migrations table: {e}")
    
    def add_migration(self, version -> None: str, name -> None: str, up_func -> None: Callable = None, down_func -> None: Callable = None) -> None:
        """Add a new migration"""
        migration = Migration(version, name, up_func, down_func)
        self.migrations.append(migration)
        logger.info(f"Added migration {version}: {name}")
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations"""
        return [m for m in self.migrations if m.version not in self.applied_migrations]
    
    def get_applied_migrations(self) -> List[Migration]:
        """Get list of applied migrations"""
        return [m for m in self.migrations if m.version in self.applied_migrations]
    
    def migrate(self, target_version: str = None) -> bool:
        """Run migrations up to target version"""
        pending = self.get_pending_migrations()
        if not pending:
            logger.info("No pending migrations")
            return True
        
        success = True
        for migration in pending:
            if target_version and migration.version > target_version:
                break
                
            if migration.apply(self.connection):
                self._record_migration(migration.version, migration.name)
                self.applied_migrations.append(migration.version)
            else:
                success = False
                break
        
        return success
    
    def rollback(self, target_version: str = None) -> bool:
        """Rollback migrations to target version"""
        applied = sorted(self.get_applied_migrations(), key=lambda m: m.version, reverse=True)
        
        success = True
        for migration in applied:
            if target_version and migration.version <= target_version:
                break
                
            if migration.rollback(self.connection):
                self._remove_migration_record(migration.version)
                self.applied_migrations.remove(migration.version)
            else:
                success = False
                break
        
        return success
    
    def _record_migration(self, version -> None: str, name -> None: str) -> None:
        """Record migration as applied"""
        if not SQLALCHEMY_AVAILABLE or not self.connection:
            return
        
        try:
            sql = "INSERT INTO schema_migrations (version, name) VALUES (?, ?)"
            self.connection.execute(text(sql), (version, name))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to record migration {version}: {e}")
    
    def _remove_migration_record(self, version -> None: str) -> None:
        """Remove migration record"""
        if not SQLALCHEMY_AVAILABLE or not self.connection:
            return
        
        try:
            sql = "DELETE FROM schema_migrations WHERE version = ?"
            self.connection.execute(text(sql), (version,))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Failed to remove migration record {version}: {e}")
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get migration status information"""
        return {
            "total_migrations": len(self.migrations),
            "applied_count": len(self.applied_migrations),
            "pending_count": len(self.get_pending_migrations()),
            "applied_versions": self.applied_migrations,
            "pending_versions": [m.version for m in self.get_pending_migrations()]
        }

# Global migration manager
_migration_manager = None

def get_migration_manager(connection=None) -> MigrationManager:
    """Get the global migration manager"""
    global _migration_manager
    if _migration_manager is None:
        _migration_manager = MigrationManager(connection)
    return _migration_manager

def create_initial_tables(connection=None) -> None:
    """Create initial database tables"""
    if not SQLALCHEMY_AVAILABLE:
        logger.warning("SQLAlchemy not available, skipping table creation")
        return False
    
    # Import models to create tables
    try:
        from . import models
        if hasattr(models, 'Base') and models.Base and connection:
            models.Base.metadata.create_all(bind=connection.engine)
            logger.info("Created initial database tables")
            return True
    except Exception as e:
        logger.error(f"Failed to create initial tables: {e}")
    
    return False

def setup_initial_migrations() -> None:
    """Setup initial migrations"""
    manager = get_migration_manager()
    
    # Add initial migration
    def create_tables_up(connection) -> None:
        create_initial_tables(connection)
    
    def create_tables_down(connection) -> None:
        # Drop all tables (be careful!)
        if SQLALCHEMY_AVAILABLE:
            from . import models
            if hasattr(models, 'Base') and models.Base:
                models.Base.metadata.drop_all(bind=connection.engine)
    
    manager.add_migration(
        version="001",
        name="create_initial_tables",
        up_func=create_tables_up,
        down_func=create_tables_down
    )
    
    logger.info("Setup initial migrations")

def run_migrations(connection=None, target_version: str = None) -> bool:
    """Run all pending migrations"""
    manager = get_migration_manager(connection)
    setup_initial_migrations()
    return manager.migrate(target_version)

def rollback_migrations(connection=None, target_version: str = None) -> bool:
    """Rollback migrations to target version"""
    manager = get_migration_manager(connection)
    return manager.rollback(target_version)

def get_migration_info() -> Dict[str, Any]:
    """Get migration system information"""
    manager = get_migration_manager()
    return {
        "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
        "migration_status": manager.get_migration_status(),
        "has_connection": manager.connection is not None
    }