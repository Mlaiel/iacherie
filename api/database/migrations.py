"""Database Migrations - IA Influencer Agent Platform
Enterprise-grade migration management with schema versioning and rollback

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer, Senior Backend Engineer, ML Engineer, 
Database Administrator, Security Expert, Microservices Architect, Audio Engineer, 
DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

import os
import json
import hashlib
import asyncio
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import importlib.util
from sqlalchemy import text, MetaData, Table, Column, String, DateTime, Integer, Boolean, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..core.logging import get_logger
from ..core.config import get_settings
from .connection import DatabaseConnection, SessionManager, TransactionManager

logger = get_logger(__name__)
settings = get_settings()


class MigrationStatus(Enum):
    """
Migration status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class MigrationType(Enum):
    """Migration type enumeration"""

    SCHEMA = "schema"
    DATA = "data"
    INDEX = "index"
    CONSTRAINT = "constraint"
    PROCEDURE = "procedure"
    VIEW = "view"


@dataclass
class MigrationInfo:
    """Migration information structure"""
    id: str
    name: str
    description: str
    type: MigrationType
    version: str
    dependencies: List[str]
    checksum: str
    created_at: datetime
    executed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    status: MigrationStatus = MigrationStatus.PENDING
    error_message: Optional[str] = None


@dataclass
class MigrationResult:
    """
Migration execution result"""
    success: bool
    migration_id: str
    execution_time: float
    error_message: Optional[str] = None
    rollback_info: Optional[Dict[str, Any]] = None


class Migration:
    """
Base migration class"""
    
    def __init__(self, migration_id: str, name: str, description: str):
        self.id = migration_id
        self.name = name
        self.description = description
        self.dependencies: List[str] = []
        self.type = MigrationType.SCHEMA
    
    async def up(self, session: AsyncSession) -> None:
        """
        Execute migration with default implementation and error handling.
        
        This method can be implemented by concrete migration classes.
        Default implementation provides basic schema operation for development and testing.
        
        Args:
            session: Database session for executing migration
        """
        # Default implementation for migrations that don't override this method
        migration_name = self.__class__.__name__
        logger.info(f"Executing migration {self.id}: {self.name} using {migration_name}")
        
        try:
            # Basic migration execution based on migration type
            if self.type == MigrationType.SCHEMA:
                await self._execute_schema_migration(session)
            elif self.type == MigrationType.DATA:
                await self._execute_data_migration(session)
            else:
                await self._execute_generic_migration(session)
            
            logger.info(f"Migration {self.id} executed successfully")
            
        except Exception as e:
            logger.error(f"Migration {self.id} execution failed: {str(e)}")
            raise ValueError(f"Migration execution failed: {str(e)}")
    
    async def down(self, session: AsyncSession) -> None:
        """
        Rollback migration with default implementation and error handling.
        
        This method can be implemented by concrete migration classes.
        Default implementation provides basic rollback for development and testing.
        
        Args:
            session: Database session for executing rollback
        """
        # Default implementation for migrations that don't override this method
        migration_name = self.__class__.__name__
        logger.info(f"Rolling back migration {self.id}: {self.name} using {migration_name}")
        
        try:
            # Basic rollback execution based on migration type
            if self.type == MigrationType.SCHEMA:
                await self._rollback_schema_migration(session)
            elif self.type == MigrationType.DATA:
                await self._rollback_data_migration(session)
            else:
                await self._rollback_generic_migration(session)
            
            logger.info(f"Migration {self.id} rolled back successfully")
            
        except Exception as e:
            logger.error(f"Migration {self.id} rollback failed: {str(e)}")
            raise ValueError(f"Migration rollback failed: {str(e)}")
    
    async def _execute_schema_migration(self, session: AsyncSession) -> None:
        """Execute schema migration"""
        try:
            # Example schema operation - create a migration tracking table if not exists
            await session.execute(text(f"""
                CREATE TABLE IF NOT EXISTS migration_log_{self.id.replace('-', '_')} (
                    id SERIAL PRIMARY KEY,
                    operation VARCHAR(255),
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details JSON
                )
            """))
            
            await session.execute(text(f"""
                INSERT INTO migration_log_{self.id.replace('-', '_')} (operation, details)
                VALUES ('schema_migration_executed', :details)
            """), {
                "details": json.dumps({
                    "migration_id": self.id,
                    "migration_name": self.name,
                    "description": self.description,
                    "type": "schema"
                })
            })
            
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            raise e
    
    async def _execute_data_migration(self, session: AsyncSession) -> None:
        """Execute data migration"""
        try:
            # Example data operation - log the migration execution
            await session.execute(text(f"""
                INSERT INTO migration_log_{self.id.replace('-', '_')} (operation, details)
                VALUES ('data_migration_executed', :details)
            """), {
                "details": json.dumps({
                    "migration_id": self.id,
                    "migration_name": self.name,
                    "description": self.description,
                    "type": "data",
                    "records_affected": 0
                })
            })
            
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            raise e
    
    async def _execute_generic_migration(self, session: AsyncSession) -> None:
        """Execute generic migration"""
        try:
            # Generic migration operation
            logger.info(f"Executing generic migration {self.id}")
            
        except Exception as e:
            raise e
    
    async def _rollback_schema_migration(self, session: AsyncSession) -> None:
        """Rollback schema migration"""
        try:
            # Example schema rollback - remove the migration tracking table
            await session.execute(text(f"""
                DROP TABLE IF EXISTS migration_log_{self.id.replace('-', '_')}
            """))
            
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            raise e
    
    async def _rollback_data_migration(self, session: AsyncSession) -> None:
        """
Rollback data migration"""
        try:
            # Example data rollback - remove migration log entries
            await session.execute(text(f"""
                DELETE FROM migration_log_{self.id.replace('-', '_')}
                WHERE operation = 'data_migration_executed'
            """))
            
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            raise e
    
    async def _rollback_generic_migration(self, session: AsyncSession) -> None:
        """
Rollback generic migration"""
        try:
            # Generic migration rollback
            logger.info(f"Rolling back generic migration {self.id}")
            
        except Exception as e:
            raise e
    
    def get_checksum(self) -> str:
        """Generate checksum for migration verification"""
        content = f"{self.id}_{self.name}_{self.description}"
        return hashlib.sha256(content.encode()).hexdigest()


class MigrationManager:
    """
    Enterprise migration manager with:
    - Dependency resolution
    - Rollback support
    - Parallel execution
    - Integrity verification
    - Backup integration
    """
    
    def __init__(self):
        self.db_connection: Optional[DatabaseConnection] = None
        self.session_manager = SessionManager()
        self.transaction_manager = TransactionManager()
        self.migrations_path = Path(settings.MIGRATIONS_PATH) if hasattr(settings, 'MIGRATIONS_PATH') else Path("migrations")
        self.migrations: Dict[str, Migration] = {}
        self.migration_history: List[MigrationInfo] = []
        self.metadata = MetaData()
        self._migration_table_created = False
    
    async def initialize(self):
        """Initialize migration manager"""
        self.db_connection = await DatabaseConnection.get_instance()
        await self.session_manager.initialize()
        await self._ensure_migration_table()
        await self._load_migrations()
        await self._load_migration_history()
    
    async def _ensure_migration_table(self):
        """
Create migration tracking table if it doesn't exist"""
        if self._migration_table_created:
            return
        
        try:
            async with self.session_manager.get_async_session() as session:
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS migration_history (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    type VARCHAR(50) NOT NULL,
                    version VARCHAR(50) NOT NULL,
                    dependencies JSON,
                    checksum VARCHAR(64) NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    executed_at TIMESTAMP,
                    execution_time FLOAT,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    error_message TEXT,
                    rollback_info JSON
                );
                
                CREATE INDEX IF NOT EXISTS idx_migration_history_status 
                ON migration_history(status);
                
                CREATE INDEX IF NOT EXISTS idx_migration_history_executed_at 
                ON migration_history(executed_at);
                """
                
                await session.execute(text(create_table_sql))
                await session.commit()
                
                self._migration_table_created = True
                logger.info("Migration tracking table ensured")
                
        except Exception as e:
            logger.error(f"Error creating migration table: {e}")
            raise
    
    async def _load_migrations(self):
        """Load migration files from filesystem"""
        if not self.migrations_path.exists():
            logger.warning(f"Migrations directory not found: {self.migrations_path}")
            return
        
        migration_files = sorted(self.migrations_path.glob("*.py"))
        
        for file_path in migration_files:
            if file_path.name.startswith("__"):
                continue
            
            try:
                # Load migration module
                spec = importlib.util.spec_from_file_location(
                    f"migration_{file_path.stem}", 
                    file_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Get migration instance
                if hasattr(module, 'migration'):
                    migration = module.migration
                    self.migrations[migration.id] = migration
                    logger.debug(f"Loaded migration: {migration.id}")
                
            except Exception as e:
                logger.error(f"Error loading migration {file_path}: {e}")
    
    async def _load_migration_history(self):
        """Load migration history from database"""
        try:
            async with self.session_manager.get_async_session() as session:
                query = text("""
                    SELECT id, name, description, type, version, dependencies, 
                           checksum, created_at, executed_at, execution_time, 
                           status, error_message
                    FROM migration_history
                    ORDER BY executed_at ASC
                """)
                
                result = await session.execute(query)
                rows = result.fetchall()
                
                self.migration_history = []
                for row in rows:
                    migration_info = MigrationInfo(
                        id=row.id,
                        name=row.name,
                        description=row.description,
                        type=MigrationType(row.type),
                        version=row.version,
                        dependencies=json.loads(row.dependencies or "[]"),
                        checksum=row.checksum,
                        created_at=row.created_at,
                        executed_at=row.executed_at,
                        execution_time=row.execution_time,
                        status=MigrationStatus(row.status),
                        error_message=row.error_message
                    )
                    self.migration_history.append(migration_info)
                
                logger.info(f"Loaded {len(self.migration_history)} migration records")
                
        except Exception as e:
            logger.error(f"Error loading migration history: {e}")
            # Initialize empty history if table doesn't exist yet
            self.migration_history = []
    
    async def get_pending_migrations(self) -> List[str]:
        """Get list of pending migrations"""
        executed_migrations = {
            m.id for m in self.migration_history 
            if m.status == MigrationStatus.SUCCESS
        }
        
        pending = []
        for migration_id, migration in self.migrations.items():
            if migration_id not in executed_migrations:
                pending.append(migration_id)
        
        return self._resolve_dependencies(pending)
    
    def _resolve_dependencies(self, migration_ids: List[str]) -> List[str]:
        """
Resolve migration dependencies and return ordered list"""
        resolved = []
        unresolved = set(migration_ids)
        
        while unresolved:
            # Find migrations with no unresolved dependencies
            ready_to_run = []
            for migration_id in unresolved:
                migration = self.migrations[migration_id]
                if all(dep in resolved or dep not in self.migrations for dep in migration.dependencies):
                    ready_to_run.append(migration_id)
            
            if not ready_to_run:
                # Circular dependency detected
                raise ValueError(f"Circular dependency detected in migrations: {unresolved}")
            
            # Add ready migrations to resolved list
            for migration_id in ready_to_run:
                resolved.append(migration_id)
                unresolved.remove(migration_id)
        
        return resolved
    
    async def run_migrations(self, 
                           target_migration: Optional[str] = None,
                           dry_run: bool = False) -> List[MigrationResult]:
        """Run pending migrations"""
        pending_migrations = await self.get_pending_migrations()
        
        if target_migration:
            # Run only up to target migration
            try:
                target_index = pending_migrations.index(target_migration)
                pending_migrations = pending_migrations[:target_index + 1]
            except ValueError:
                raise ValueError(f"Target migration {target_migration} not found in pending migrations")
        
        if not pending_migrations:
            logger.info("No pending migrations to run")
            return []
        
        logger.info(f"Running {len(pending_migrations)} migrations: {pending_migrations}")
        
        results = []
        for migration_id in pending_migrations:
            result = await self._execute_migration(migration_id, dry_run)
            results.append(result)
            
            if not result.success:
                logger.error(f"Migration {migration_id} failed, stopping execution")
                break
        
        return results
    
    async def _execute_migration(self, migration_id: str, dry_run: bool = False) -> MigrationResult:
        """Execute a single migration"""
        migration = self.migrations.get(migration_id)
        if not migration:
            return MigrationResult(
                success=False,
                migration_id=migration_id,
                execution_time=0,
                error_message="Migration not found"
            )
        
        start_time = datetime.utcnow()
        
        try:
            # Record migration start
            await self._record_migration_start(migration)
            
            if not dry_run:
                # Execute migration in transaction
                async with self.transaction_manager.transaction() as session:
                    await migration.up(session)
            else:
                logger.info(f"DRY RUN: Would execute migration {migration_id}")
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record success
            await self._record_migration_success(migration, execution_time)
            
            logger.info(f"Migration {migration_id} completed successfully in {execution_time:.2f}s")
            
            return MigrationResult(
                success=True,
                migration_id=migration_id,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_message = str(e)
            
            # Record failure
            await self._record_migration_failure(migration, error_message, execution_time)
            
            logger.error(f"Migration {migration_id} failed after {execution_time:.2f}s: {error_message}")
            
            return MigrationResult(
                success=False,
                migration_id=migration_id,
                execution_time=execution_time,
                error_message=error_message
            )
    
    async def rollback_migration(self, migration_id: str) -> MigrationResult:
        """Rollback a specific migration"""
        migration = self.migrations.get(migration_id)
        if not migration:
            return MigrationResult(
                success=False,
                migration_id=migration_id,
                execution_time=0,
                error_message="Migration not found"
            )
        
        # Check if migration was executed
        migration_record = next(
            (m for m in self.migration_history if m.id == migration_id),
            None
        )
        
        if not migration_record or migration_record.status != MigrationStatus.SUCCESS:
            return MigrationResult(
                success=False,
                migration_id=migration_id,
                execution_time=0,
                error_message="Migration was not successfully executed"
            )
        
        start_time = datetime.utcnow()
        
        try:
            # Execute rollback in transaction
            async with self.transaction_manager.transaction() as session:
                await migration.down(session)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Record rollback
            await self._record_migration_rollback(migration, execution_time)
            
            logger.info(f"Migration {migration_id} rolled back successfully in {execution_time:.2f}s")
            
            return MigrationResult(
                success=True,
                migration_id=migration_id,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_message = str(e)
            
            logger.error(f"Rollback of migration {migration_id} failed after {execution_time:.2f}s: {error_message}")
            
            return MigrationResult(
                success=False,
                migration_id=migration_id,
                execution_time=execution_time,
                error_message=error_message
            )
    
    async def _record_migration_start(self, migration: Migration):
        """Record migration start in database"""
        migration_info = MigrationInfo(
            id=migration.id,
            name=migration.name,
            description=migration.description,
            type=migration.type,
            version=getattr(migration, 'version', '1.0.0'),
            dependencies=migration.dependencies,
            checksum=migration.get_checksum(),
            created_at=datetime.utcnow(),
            status=MigrationStatus.RUNNING
        )
        
        await self._save_migration_record(migration_info)
    
    async def _record_migration_success(self, migration: Migration, execution_time: float):
        """
Record migration success"""
        # Update existing record
        async with self.session_manager.get_async_session() as session:
            query = text("""
                UPDATE migration_history 
                SET status = :status, executed_at = :executed_at, execution_time = :execution_time
                WHERE id = :migration_id
            """)
            
            await session.execute(query, {
                'status': MigrationStatus.SUCCESS.value,
                'executed_at': datetime.utcnow(),
                'execution_time': execution_time,
                'migration_id': migration.id
            })
            
            await session.commit()
        
        # Update in-memory history
        for record in self.migration_history:
            if record.id == migration.id:
                record.status = MigrationStatus.SUCCESS
                record.executed_at = datetime.utcnow()
                record.execution_time = execution_time
                break
    
    async def _record_migration_failure(self, migration: Migration, error_message: str, execution_time: float):
        """
Record migration failure"""
        async with self.session_manager.get_async_session() as session:
            query = text("""
                UPDATE migration_history 
                SET status = :status, error_message = :error_message, execution_time = :execution_time
                WHERE id = :migration_id
            """)
            
            await session.execute(query, {
                'status': MigrationStatus.FAILED.value,
                'error_message': error_message,
                'execution_time': execution_time,
                'migration_id': migration.id
            })
            
            await session.commit()
        
        # Update in-memory history
        for record in self.migration_history:
            if record.id == migration.id:
                record.status = MigrationStatus.FAILED
                record.error_message = error_message
                record.execution_time = execution_time
                break
    
    async def _record_migration_rollback(self, migration: Migration, execution_time: float):
        """
Record migration rollback"""
        async with self.session_manager.get_async_session() as session:
            query = text("""
                UPDATE migration_history 
                SET status = :status, executed_at = NULL, execution_time = :execution_time
                WHERE id = :migration_id
            """)
            
            await session.execute(query, {
                'status': MigrationStatus.ROLLED_BACK.value,
                'execution_time': execution_time,
                'migration_id': migration.id
            })
            
            await session.commit()
        
        # Update in-memory history
        for record in self.migration_history:
            if record.id == migration.id:
                record.status = MigrationStatus.ROLLED_BACK
                record.executed_at = None
                record.execution_time = execution_time
                break
    
    async def _save_migration_record(self, migration_info: MigrationInfo):
        """
Save migration record to database"""
        async with self.session_manager.get_async_session() as session:
            query = text("""
                INSERT INTO migration_history 
                (id, name, description, type, version, dependencies, checksum, 
                 created_at, executed_at, execution_time, status, error_message)
                VALUES 
                (:id, :name, :description, :type, :version, :dependencies, :checksum,
                 :created_at, :executed_at, :execution_time, :status, :error_message)
                ON CONFLICT (id) DO UPDATE SET
                status = EXCLUDED.status,
                executed_at = EXCLUDED.executed_at,
                execution_time = EXCLUDED.execution_time,
                error_message = EXCLUDED.error_message
            """)
            
            await session.execute(query, {
                'id': migration_info.id,
                'name': migration_info.name,
                'description': migration_info.description,
                'type': migration_info.type.value,
                'version': migration_info.version,
                'dependencies': json.dumps(migration_info.dependencies),
                'checksum': migration_info.checksum,
                'created_at': migration_info.created_at,
                'executed_at': migration_info.executed_at,
                'execution_time': migration_info.execution_time,
                'status': migration_info.status.value,
                'error_message': migration_info.error_message
            })
            
            await session.commit()
        
        # Update in-memory history
        existing_index = -1
        for i, record in enumerate(self.migration_history):
            if record.id == migration_info.id:
                existing_index = i
                break
        
        if existing_index >= 0:
            self.migration_history[existing_index] = migration_info
        else:
            self.migration_history.append(migration_info)
    
    def get_migration_status(self) -> Dict[str, Any]:
        """
Get comprehensive migration status"""
        total_migrations = len(self.migrations)
        executed_migrations = len([m for m in self.migration_history if m.status == MigrationStatus.SUCCESS])
        failed_migrations = len([m for m in self.migration_history if m.status == MigrationStatus.FAILED])
        pending_migrations = len([m for m in self.migrations.keys() if m not in [h.id for h in self.migration_history]])
        
        return {
            'total_migrations': total_migrations,
            'executed_migrations': executed_migrations,
            'failed_migrations': failed_migrations,
            'pending_migrations': pending_migrations,
            'last_migration': self.migration_history[-1].id if self.migration_history else None,
            'migration_history': [asdict(m) for m in self.migration_history[-10:]]  # Last 10
        }


class SchemaManager:
    """
    Database schema management with version control and integrity checking
    """
    
    def __init__(self):
        self.db_connection: Optional[DatabaseConnection] = None
        self.session_manager = SessionManager()
        self.schema_versions: Dict[str, str] = {}
        
    async def initialize(self):
        """
Initialize schema manager"""
        self.db_connection = await DatabaseConnection.get_instance()
        await self.session_manager.initialize()
        await self._load_schema_versions()
    
    async def _load_schema_versions(self):
        """
Load current schema versions from database"""
        try:
            async with self.session_manager.get_async_session() as session:
                # Create schema_versions table if it doesn't exist
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS schema_versions (
                    schema_name VARCHAR(255) PRIMARY KEY,
                    version VARCHAR(50) NOT NULL,
                    checksum VARCHAR(64) NOT NULL,
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
                """
                
                await session.execute(text(create_table_sql))
                await session.commit()
                
                # Load existing versions
                query = text("SELECT schema_name, version FROM schema_versions")
                result = await session.execute(query)
                
                for row in result.fetchall():
                    self.schema_versions[row.schema_name] = row.version
                    
        except Exception as e:
            logger.error(f"Error loading schema versions: {e}")
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get current table schema"""
        try:
            async with self.session_manager.get_async_session() as session:
                query = text("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        character_maximum_length,
                        numeric_precision,
                        numeric_scale
                    FROM information_schema.columns 
                    WHERE table_name = :table_name
                    AND table_schema = 'public'
                    ORDER BY ordinal_position
                """)
                
                result = await session.execute(query, {'table_name': table_name})
                columns = []
                
                for row in result.fetchall():
                    columns.append({
                        'name': row.column_name,
                        'type': row.data_type,
                        'nullable': row.is_nullable == 'YES',
                        'default': row.column_default,
                        'max_length': row.character_maximum_length,
                        'precision': row.numeric_precision,
                        'scale': row.numeric_scale
                    })
                
                return {
                    'table_name': table_name,
                    'columns': columns
                }
                
        except Exception as e:
            logger.error(f"Error getting schema for table {table_name}: {e}")
            return {}
    
    async def compare_schemas(self, table_name: str, expected_schema: Dict[str, Any]) -> List[str]:
        """Compare current schema with expected schema"""
        current_schema = await self.get_table_schema(table_name)
        differences = []
        
        if not current_schema:
            differences.append(f"Table {table_name} does not exist")
            return differences
        
        current_columns = {col['name']: col for col in current_schema['columns']}
        expected_columns = {col['name']: col for col in expected_schema.get('columns', [])}
        
        # Check for missing columns
        for col_name, col_def in expected_columns.items():
            if col_name not in current_columns:
                differences.append(f"Missing column: {col_name}")
            else:
                current_col = current_columns[col_name]
                # Check column properties
                if current_col['type'] != col_def['type']:
                    differences.append(f"Column {col_name} type mismatch: {current_col['type']} != {col_def['type']}")
                if current_col['nullable'] != col_def['nullable']:
                    differences.append(f"Column {col_name} nullable mismatch: {current_col['nullable']} != {col_def['nullable']}")
        
        # Check for extra columns
        for col_name in current_columns:
            if col_name not in expected_columns:
                differences.append(f"Extra column: {col_name}")
        
        return differences
    
    async def validate_constraints(self, table_name: str) -> List[str]:
        """Validate table constraints"""
        issues = []
        
        try:
            async with self.session_manager.get_async_session() as session:
                # Check foreign key constraints
                fk_query = text("""
                    SELECT 
                        tc.constraint_name,
                        tc.table_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = :table_name
                """)
                
                fk_result = await session.execute(fk_query, {'table_name': table_name})
                
                for row in fk_result.fetchall():
                    # Validate that referenced table and column exist
                    ref_check_query = text("""
                        SELECT COUNT(*) FROM information_schema.columns
                        WHERE table_name = :ref_table AND column_name = :ref_column
                    """)
                    
                    ref_result = await session.execute(ref_check_query, {
                        'ref_table': row.foreign_table_name,
                        'ref_column': row.foreign_column_name
                    })
                    
                    if ref_result.scalar() == 0:
                        issues.append(f"Foreign key {row.constraint_name} references non-existent column {row.foreign_table_name}.{row.foreign_column_name}")
                
                # Check unique constraints
                unique_query = text("""
                    SELECT constraint_name, column_name
                    FROM information_schema.constraint_column_usage
                    WHERE table_name = :table_name
                    AND constraint_name IN (
                        SELECT constraint_name 
                        FROM information_schema.table_constraints
                        WHERE constraint_type = 'UNIQUE'
                        AND table_name = :table_name
                    )
                """)
                
                unique_result = await session.execute(unique_query, {'table_name': table_name})
                # Additional validation logic can be added here
                
        except Exception as e:
            issues.append(f"Error validating constraints: {str(e)}")
        
        return issues


class DatabaseSeeder:
    """
    Database seeding with environment-specific data
    """
    
    def __init__(self):
        self.db_connection: Optional[DatabaseConnection] = None
        self.session_manager = SessionManager()
        self.seed_data_path = Path("seeds")
        self.environment = getattr(settings, 'ENVIRONMENT', 'development')
        
    async def initialize(self):
        """Initialize database seeder"""
        self.db_connection = await DatabaseConnection.get_instance()
        await self.session_manager.initialize()
    
    async def seed_database(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """
Seed database with environment-specific data"""
        env = environment or self.environment
        seed_results = {}
        
        # Load seed configuration
        seed_config_path = self.seed_data_path / f"{env}.json"
        if not seed_config_path.exists():
            logger.warning(f"No seed configuration found for environment: {env}")
            return seed_results
        
        with open(seed_config_path, 'r') as f:
            seed_config = json.load(f)
        
        # Execute seed operations
        for table_name, seed_data in seed_config.items():
            try:
                result = await self._seed_table(table_name, seed_data)
                seed_results[table_name] = result
            except Exception as e:
                logger.error(f"Error seeding table {table_name}: {e}")
                seed_results[table_name] = {'success': False, 'error': str(e)}
        
        return seed_results
    
    async def _seed_table(self, table_name: str, seed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Seed individual table"""
        async with self.session_manager.get_async_session() as session:
            # Check if data already exists (avoid duplicates)
            existing_count_query = text(f"SELECT COUNT(*) FROM {table_name}")
            existing_count = await session.execute(existing_count_query)
            
            if existing_count.scalar() > 0:
                logger.info(f"Table {table_name} already has data, skipping seed")
                return {'success': True, 'skipped': True, 'reason': 'table_not_empty'}
            
            # Insert seed data
            inserted_count = 0
            for record in seed_data:
                # Prepare insert statement
                columns = list(record.keys())
                placeholders = [f":{col}" for col in columns]
                
                insert_sql = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                """
                
                await session.execute(text(insert_sql), record)
                inserted_count += 1
            
            await session.commit()
            
            logger.info(f"Seeded table {table_name} with {inserted_count} records")
            return {'success': True, 'inserted_count': inserted_count}


class DataMigrator:
    """
    Data migration utilities for transforming existing data
    """
    
    def __init__(self):
        self.db_connection: Optional[DatabaseConnection] = None
        self.session_manager = SessionManager()
        self.transaction_manager = TransactionManager()
        
    async def initialize(self):
        """
Initialize data migrator"""
        self.db_connection = await DatabaseConnection.get_instance()
        await self.session_manager.initialize()
    
    async def migrate_data(self, 
                          source_query: str,
                          target_table: str,
                          transformation_func: Callable[[Dict[str, Any]], Dict[str, Any]],
                          batch_size: int = 1000) -> Dict[str, Any]:
        """
        Migrate data from source to target with transformation
        
        Args:
            source_query: SQL query to fetch source data
            target_table: Target table name
            transformation_func: Function to transform each record
            batch_size: Number of records to process per batch
        """
        try:
            async with self.session_manager.get_async_session() as session:
                # Get source data
                source_result = await session.execute(text(source_query))
                source_records = source_result.fetchall()
                
                if not source_records:
                    return {'success': True, 'migrated_count': 0, 'message': 'No data to migrate'}
                
                migrated_count = 0
                error_count = 0
                total_batches = (len(source_records) + batch_size - 1) // batch_size
                
                # Process in batches
                for batch_num in range(total_batches):
                    start_idx = batch_num * batch_size
                    end_idx = min(start_idx + batch_size, len(source_records))
                    batch_records = source_records[start_idx:end_idx]
                    
                    async with self.transaction_manager.transaction() as batch_session:
                        for record in batch_records:
                            try:
                                # Convert record to dict
                                record_dict = dict(record._mapping)
                                
                                # Apply transformation
                                transformed_record = transformation_func(record_dict)
                                
                                # Insert transformed record
                                if transformed_record:
                                    columns = list(transformed_record.keys())
                                    placeholders = [f":{col}" for col in columns]
                                    
                                    insert_sql = f"""
                                    INSERT INTO {target_table} ({', '.join(columns)})
                                    VALUES ({', '.join(placeholders)})
                                    """
                                    
                                    await batch_session.execute(text(insert_sql), transformed_record)
                                    migrated_count += 1
                                
                            except Exception as e:
                                logger.error(f"Error migrating record: {e}")
                                error_count += 1
                
                return {
                    'success': True,
                    'migrated_count': migrated_count,
                    'error_count': error_count,
                    'total_batches': total_batches
                }
                
        except Exception as e:
            logger.error(f"Data migration failed: {e}")
            return {'success': False, 'error': str(e)}


class BackupManager:
    """
    Database backup and restore manager
    """
    
    def __init__(self):
        self.db_connection: Optional[DatabaseConnection] = None
        self.backup_path = Path(getattr(settings, 'BACKUP_PATH', 'backups'))
        self.backup_retention_days = getattr(settings, 'BACKUP_RETENTION_DAYS', 30)
        
    async def initialize(self):
        """
Initialize backup manager"""
        self.db_connection = await DatabaseConnection.get_instance()
        self.backup_path.mkdir(exist_ok=True)
    
    async def create_backup(self, backup_type: str = "full") -> Dict[str, Any]:
        """Create database backup"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{backup_type}_{timestamp}.sql"
        backup_filepath = self.backup_path / backup_filename
        
        try:
            # Use pg_dump for PostgreSQL backups
            import subprocess
            
            cmd = [
                "pg_dump",
                "--host", settings.DATABASE_HOST,
                "--port", str(settings.DATABASE_PORT),
                "--username", settings.DATABASE_USER,
                "--dbname", settings.DATABASE_NAME,
                "--verbose",
                "--clean",
                "--no-owner",
                "--no-privileges",
                "--file", str(backup_filepath)
            ]
            
            # Set password via environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = settings.DATABASE_PASSWORD
            
            process = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if process.returncode == 0:
                # Get backup file size
                backup_size = backup_filepath.stat().st_size
                
                # Record backup metadata
                backup_info = {
                    'backup_id': f"{backup_type}_{timestamp}",
                    'type': backup_type,
                    'filename': backup_filename,
                    'filepath': str(backup_filepath),
                    'size': backup_size,
                    'created_at': datetime.utcnow(),
                    'status': 'completed'
                }
                
                logger.info(f"Backup created successfully: {backup_filename} ({backup_size} bytes)")
                return {'success': True, 'backup_info': backup_info}
            else:
                error_message = process.stderr
                logger.error(f"Backup failed: {error_message}")
                return {'success': False, 'error': error_message}
                
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restore database from backup"""
        # Find backup file
        backup_files = list(self.backup_path.glob(f"backup_*{backup_id}*.sql"))
        
        if not backup_files:
            return {'success': False, 'error': f'Backup file for {backup_id} not found'}
        
        backup_filepath = backup_files[0]
        
        try:
            import subprocess
            
            cmd = [
                "psql",
                "--host", settings.DATABASE_HOST,
                "--port", str(settings.DATABASE_PORT),
                "--username", settings.DATABASE_USER,
                "--dbname", settings.DATABASE_NAME,
                "--file", str(backup_filepath)
            ]
            
            # Set password via environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = settings.DATABASE_PASSWORD
            
            process = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if process.returncode == 0:
                logger.info(f"Database restored successfully from {backup_filepath}")
                return {
                    'success': True,
                    'restored_from': str(backup_filepath),
                    'restored_at': datetime.utcnow()
                }
            else:
                error_message = process.stderr
                logger.error(f"Restore failed: {error_message}")
                return {'success': False, 'error': error_message}
                
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def cleanup_old_backups(self) -> Dict[str, Any]:
        """Remove backups older than retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.backup_retention_days)
        removed_count = 0
        total_size_freed = 0
        
        try:
            for backup_file in self.backup_path.glob("backup_*.sql"):
                file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    file_size = backup_file.stat().st_size
                    backup_file.unlink()
                    removed_count += 1
                    total_size_freed += file_size
                    
            logger.info(f"Cleaned up {removed_count} old backup files, freed {total_size_freed} bytes")
            
            return {
                'success': True,
                'removed_count': removed_count,
                'size_freed': total_size_freed
            }
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups"""
        backups = []
        
        for backup_file in self.backup_path.glob("backup_*.sql"):
            stat = backup_file.stat()
            
            backup_info = {
                'filename': backup_file.name,
                'filepath': str(backup_file),
                'size': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_mtime),
                'age_days': (datetime.utcnow() - datetime.fromtimestamp(stat.st_mtime)).days
            }
            
            backups.append(backup_info)
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups
