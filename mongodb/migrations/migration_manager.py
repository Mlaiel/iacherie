"""Migration Manager for MongoDB
=============================

Comprehensive migration execution engine with version control,
dependency management, and automated rollback capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class MigrationStatus(Enum):
    """Migration execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class MigrationType(Enum):
    """Types of migrations."""
    SCHEMA_CHANGE = "schema_change"
    DATA_TRANSFORMATION = "data_transformation"
    INDEX_MANAGEMENT = "index_management"
    COLLECTION_MANAGEMENT = "collection_management"
    SECURITY_UPDATE = "security_update"

@dataclass
class Migration:
    """Individual migration definition."""
    migration_id: str
    name: str
    description: str
    migration_type: MigrationType
    version: str
    dependencies: List[str] = field(default_factory=list)
    up_operations: List[Dict[str, Any]] = field(default_factory=list)
    down_operations: List[Dict[str, Any]] = field(default_factory=list)
    requires_downtime: bool = False
    estimated_duration_seconds: int = 60
    created_at: datetime = field(default_factory=datetime.utcnow)
    checksum: Optional[str] = None

@dataclass
class MigrationExecution:
    """Migration execution record."""
    execution_id: str
    migration_id: str
    status: MigrationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    rollback_available: bool = True
    applied_by: Optional[str] = None

class MigrationManager:
    """Database migration execution manager."""
    
    def __init__(self) -> None:
        """Initialize migration manager."""
        self._migrations: Dict[str, Migration] = {}
        self._executions: List[MigrationExecution] = []
        self._current_version = "0.0.0"
        self._locked = False
        
        # Load built-in migrations
        self._load_builtin_migrations()
    
    def _load_builtin_migrations(self) -> None:
        """Load built-in migrations for Ainflue platform."""
        # Initial schema migration
        initial_migration = Migration(
            migration_id="001_initial_schema",
            name="Initial Schema Setup",
            description="Create initial collections and indexes for Ainflue platform",
            migration_type=MigrationType.SCHEMA_CHANGE,
            version="1.0.0",
            up_operations=[
                {
                    "operation": "create_collection",
                    "collection": "users",
                    "options": {
                        "validator": {
                            "$jsonSchema": {
                                "bsonType": "object",
                                "required": ["user_id", "email", "username"],
                                "properties": {
                                    "user_id": {"bsonType": "string"},
                                    "email": {"bsonType": "string"},
                                    "username": {"bsonType": "string"}
                                }
                            }
                        }
                    }
                },
                {
                    "operation": "create_index",
                    "collection": "users",
                    "index": {"user_id": 1},
                    "options": {"unique": True}
                }
            ],
            down_operations=[
                {
                    "operation": "drop_collection",
                    "collection": "users"
                }
            ]
        )
        
        # Content schema migration
        content_migration = Migration(
            migration_id="002_content_schema",
            name="Content Management Schema",
            description="Create content collections and analytics indexes",
            migration_type=MigrationType.SCHEMA_CHANGE,
            version="1.1.0",
            dependencies=["001_initial_schema"],
            up_operations=[
                {
                    "operation": "create_collection",
                    "collection": "media_content",
                    "options": {
                        "validator": {
                            "$jsonSchema": {
                                "bsonType": "object",
                                "required": ["content_id", "user_id", "content_type"],
                                "properties": {
                                    "content_id": {"bsonType": "string"},
                                    "user_id": {"bsonType": "string"},
                                    "content_type": {"bsonType": "string"}
                                }
                            }
                        }
                    }
                },
                {
                    "operation": "create_index",
                    "collection": "media_content",
                    "index": {"content_id": 1},
                    "options": {"unique": True}
                },
                {
                    "operation": "create_index",
                    "collection": "media_content",
                    "index": {"user_id": 1, "created_at": -1}
                }
            ],
            down_operations=[
                {
                    "operation": "drop_collection",
                    "collection": "media_content"
                }
            ]
        )
        
        # Register built-in migrations
        for migration in [initial_migration, content_migration]:
            migration.checksum = self._calculate_migration_checksum(migration)
            self._migrations[migration.migration_id] = migration
        
        logger.info("Loaded built-in migrations")
    
    def register_migration(self, migration: Migration) -> bool:
        """Register a new migration."""
        try:
            # Validate migration
            if migration.migration_id in self._migrations:
                logger.warning(f"Migration already exists: {migration.migration_id}")
                return False
            
            # Check dependencies
            for dep in migration.dependencies:
                if dep not in self._migrations:
                    raise ValueError(f"Dependency not found: {dep}")
            
            # Calculate checksum
            migration.checksum = self._calculate_migration_checksum(migration)
            
            # Register migration
            self._migrations[migration.migration_id] = migration
            logger.info(f"Registered migration: {migration.migration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register migration {migration.migration_id}: {e}")
            return False
    
    def apply_migration(self, migration_id: str, applied_by: str = None) -> bool:
        """Apply a specific migration."""
        if self._locked:
            logger.error("Migration system is locked")
            return False
        
        if migration_id not in self._migrations:
            logger.error(f"Migration not found: {migration_id}")
            return False
        
        migration = self._migrations[migration_id]
        
        # Check if already applied
        if self._is_migration_applied(migration_id):
            logger.info(f"Migration already applied: {migration_id}")
            return True
        
        # Check dependencies
        for dep in migration.dependencies:
            if not self._is_migration_applied(dep):
                logger.error(f"Dependency not satisfied: {dep}")
                return False
        
        # Execute migration
        execution_id = f"{migration_id}_{int(datetime.utcnow().timestamp())}"
        execution = MigrationExecution(
            execution_id=execution_id,
            migration_id=migration_id,
            status=MigrationStatus.RUNNING,
            started_at=datetime.utcnow(),
            applied_by=applied_by
        )
        
        try:
            self._locked = True
            logger.info(f"Applying migration: {migration_id}")
            
            # Execute up operations
            for operation in migration.up_operations:
                self._execute_operation(operation)
            
            # Mark as completed
            execution.completed_at = datetime.utcnow()
            execution.execution_time_seconds = (execution.completed_at - execution.started_at).total_seconds()
            execution.status = MigrationStatus.COMPLETED
            
            self._executions.append(execution)
            logger.info(f"Migration completed successfully: {migration_id}")
            return True
            
        except Exception as e:
            execution.status = MigrationStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            self._executions.append(execution)
            
            logger.error(f"Migration failed: {migration_id}: {e}")
            return False
        
        finally:
            self._locked = False
    
    def rollback_migration(self, migration_id: str, rolled_back_by: str = None) -> bool:
        """Rollback a specific migration."""
        if self._locked:
            logger.error("Migration system is locked")
            return False
        
        if not self._is_migration_applied(migration_id):
            logger.warning(f"Migration not applied, cannot rollback: {migration_id}")
            return False
        
        migration = self._migrations[migration_id]
        
        # Check if rollback operations exist
        if not migration.down_operations:
            logger.error(f"No rollback operations defined for migration: {migration_id}")
            return False
        
        # Execute rollback
        execution_id = f"rollback_{migration_id}_{int(datetime.utcnow().timestamp())}"
        execution = MigrationExecution(
            execution_id=execution_id,
            migration_id=migration_id,
            status=MigrationStatus.RUNNING,
            started_at=datetime.utcnow(),
            applied_by=rolled_back_by
        )
        
        try:
            self._locked = True
            logger.info(f"Rolling back migration: {migration_id}")
            
            # Execute down operations
            for operation in migration.down_operations:
                self._execute_operation(operation)
            
            # Mark as rolled back
            execution.completed_at = datetime.utcnow()
            execution.execution_time_seconds = (execution.completed_at - execution.started_at).total_seconds()
            execution.status = MigrationStatus.ROLLED_BACK
            
            self._executions.append(execution)
            logger.info(f"Migration rolled back successfully: {migration_id}")
            return True
            
        except Exception as e:
            execution.status = MigrationStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            self._executions.append(execution)
            
            logger.error(f"Migration rollback failed: {migration_id}: {e}")
            return False
        
        finally:
            self._locked = False
    
    def _execute_operation(self, operation -> None: Dict[str, Any]) -> None:
        """Execute a single migration operation."""
        op_type = operation.get("operation")
        
        if op_type == "create_collection":
            logger.info(f"Creating collection: {operation['collection']}")
            # In real implementation, this would interact with MongoDB
            
        elif op_type == "drop_collection":
            logger.info(f"Dropping collection: {operation['collection']}")
            
        elif op_type == "create_index":
            logger.info(f"Creating index on {operation['collection']}: {operation['index']}")
            
        elif op_type == "drop_index":
            logger.info(f"Dropping index on {operation['collection']}: {operation['index']}")
            
        else:
            raise ValueError(f"Unknown operation type: {op_type}")
    
    def _is_migration_applied(self, migration_id: str) -> bool:
        """Check if migration has been successfully applied."""
        for execution in self._executions:
            if (execution.migration_id == migration_id and 
                execution.status == MigrationStatus.COMPLETED):
                return True
        return False
    
    def _calculate_migration_checksum(self, migration: Migration) -> str:
        """Calculate checksum for migration integrity."""
        content = f"{migration.name}:{migration.version}:{str(migration.up_operations)}:{str(migration.down_operations)}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get overall migration status."""
        total_migrations = len(self._migrations)
        applied_migrations = len([m for m in self._migrations.keys() if self._is_migration_applied(m)])
        
        return {
            "total_migrations": total_migrations,
            "applied_migrations": applied_migrations,
            "pending_migrations": total_migrations - applied_migrations,
            "current_version": self._current_version,
            "is_locked": self._locked,
            "last_execution": max(self._executions, key=lambda x: x.started_at) if self._executions else None
        }
    
    def list_migrations(self, status_filter: MigrationStatus = None) -> List[Dict[str, Any]]:
        """List all migrations with their status."""
        migrations_list = []
        
        for migration in self._migrations.values():
            is_applied = self._is_migration_applied(migration.migration_id)
            migration_status = MigrationStatus.COMPLETED if is_applied else MigrationStatus.PENDING
            
            if status_filter is None or migration_status == status_filter:
                migrations_list.append({
                    "migration_id": migration.migration_id,
                    "name": migration.name,
                    "version": migration.version,
                    "type": migration.migration_type.value,
                    "status": migration_status.value,
                    "requires_downtime": migration.requires_downtime,
                    "dependencies": migration.dependencies,
                    "created_at": migration.created_at.isoformat()
                })
        
        return sorted(migrations_list, key=lambda x: x["created_at"])

# Global migration manager instance
_default_manager: Optional[MigrationManager] = None

def get_migration_manager() -> MigrationManager:
    """Get or create default migration manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = MigrationManager()
    return _default_manager

# Export main classes and functions
__all__ = [
    'MigrationStatus',
    'MigrationType',
    'Migration',
    'MigrationExecution',
    'MigrationManager',
    'get_migration_manager'
]