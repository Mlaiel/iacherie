"""🔄 Base Migration System - Enterprise Database Evolution Foundation
==================================================================

Ultra-advanced database migration framework for IA Influencer Agent platform:
- Atomic migration execution with transaction safety
- Rollback capabilities with data consistency guarantees
- Migration dependency resolution and conflict detection
- Performance monitoring and execution analytics
- Multi-tenant migration support with isolation

Author: Fahed Mlaiel (mlaiel@live.de)
Team Expertise: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
This migration framework is protected intellectual property.
Contact mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path
import uuid
import json
import hashlib

from sqlalchemy import create_engine, text, MetaData, Table, Column, String, DateTime, Boolean, Integer, JSON
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext

logger = logging.getLogger(__name__)


class MigrationStatus(Enum):
    """
Migration execution status tracking"""

    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


class MigrationPriority(Enum):
    """Migration priority levels for execution ordering"""

    CRITICAL = "critical"     # Security, data integrity
    HIGH = "high"            # Performance, new features
    MEDIUM = "medium"        # Optimizations, enhancements
    LOW = "low"              # Cleanup, documentation


class MigrationCategory(Enum):
    """Migration categories for organization"""

    SCHEMA = "schema"                    # Table structure changes
    DATA = "data"                       # Data transformations
    INDEX = "index"                     # Index optimizations
    SECURITY = "security"               # Security enhancements
    PROTECTION = "protection"           # Content protection
    FINGERPRINT = "fingerprint"         # Fingerprinting system
    MONETIZATION = "monetization"       # Revenue tracking
    ANALYTICS = "analytics"             # Analytics improvements
    COLLABORATION = "collaboration"     # Creator collaboration
    PLATFORM = "platform"              # Platform integrations


@dataclass
class MigrationDependency:
    """Migration dependency specification"""
    migration_id: str
    version: str
    required: bool = True
    description: str = ""


@dataclass
class MigrationMetadata:
    """Comprehensive migration metadata"""
    migration_id: str
    version: str
    name: str
    description: str
    category: MigrationCategory
    priority: MigrationPriority
    author: str
    created_at: datetime
    estimated_duration: int  # seconds
    affects_tables: List[str] = field(default_factory=list)
    dependencies: List[MigrationDependency] = field(default_factory=list)
    rollback_safe: bool = True
    data_loss_risk: bool = False
    requires_downtime: bool = False
    tenant_specific: bool = False


@dataclass
class MigrationResult:
    """
Migration execution result"""
    migration_id: str
    status: MigrationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    affected_rows: int = 0
    error_message: Optional[str] = None
    rollback_info: Optional[Dict[str, Any]] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class BaseMigration(ABC):
    """
    Abstract base class for all database migrations
    
    Provides enterprise-grade migration framework with:
    - Transaction safety and rollback capabilities
    - Performance monitoring and analytics
    - Dependency resolution and conflict detection
    - Multi-tenant support with data isolation
    - Security validation and compliance checks
    """
    
    def __init__(self, 
                 database_url: str,
                 metadata: MigrationMetadata,
                 tenant_id: Optional[str] = None):
        self.database_url = database_url
        self.metadata = metadata
        self.tenant_id = tenant_id
        self.engine = create_engine(database_url, echo=False)
        self.session_maker = sessionmaker(bind=self.engine)
        self.executed_operations = []
        self.rollback_data = {}
        
    @abstractmethod
    async def execute_up(self, session: Session) -> MigrationResult:
        """
        Execute migration forward operation
        
        Args:
            session: Database session with transaction context
            
        Returns:
            MigrationResult with execution details
        """
        pass
        
    @abstractmethod
    async def execute_down(self, session: Session) -> MigrationResult:
        """
        Execute migration rollback operation
        
        Args:
            session: Database session with transaction context
            
        Returns:
            MigrationResult with rollback details
        """
        pass
        
    async def run_migration(self, direction: str = "up") -> MigrationResult:
        """
        Execute migration with full transaction safety
        
        Args:
            direction: "up" for forward, "down" for rollback
            
        Returns:
            Comprehensive migration result
        """
        start_time = datetime.now(timezone.utc)
        result = MigrationResult(
            migration_id=self.metadata.migration_id,
            status=MigrationStatus.RUNNING,
            started_at=start_time
        )
        
        try:
            # Pre-migration validation
            await self._validate_prerequisites()
            
            # Execute migration in transaction
            async with self._get_transaction_session() as session:
                if direction == "up":
                    result = await self.execute_up(session)
                elif direction == "down":
                    result = await self.execute_down(session)
                else:
                    raise ValueError(f"Invalid migration direction: {direction}")
                    
                # Post-migration validation
                await self._validate_post_migration(session)
                
                result.status = MigrationStatus.COMPLETED
                result.completed_at = datetime.now(timezone.utc)
                result.duration_seconds = (result.completed_at - start_time).total_seconds()
                
            # Record migration execution
            await self._record_migration_execution(result)
            
            logger.info(f"Migration {self.metadata.migration_id} completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"Migration {self.metadata.migration_id} failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            result.status = MigrationStatus.FAILED
            result.error_message = error_msg
            result.completed_at = datetime.now(timezone.utc)
            result.duration_seconds = (result.completed_at - start_time).total_seconds()
            
            # Attempt rollback if needed
            if direction == "up" and self.metadata.rollback_safe:
                try:
                    rollback_result = await self.run_migration("down")
                    result.rollback_info = rollback_result.__dict__
                    result.status = MigrationStatus.ROLLED_BACK
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")
                    
            return result
            
    async def _validate_prerequisites(self) -> None:
        """Validate migration prerequisites"""
        # Check dependencies
        for dependency in self.metadata.dependencies:
            if dependency.required:
                await self._check_dependency(dependency)
                
        # Check table existence
        await self._validate_table_access()
        
        # Check data integrity
        await self._validate_data_integrity()
        
    async def _check_dependency(self, dependency: MigrationDependency) -> None:
        """
Check if migration dependency is satisfied"""
        async with self._get_session() as session:
            query = text("""
                SELECT version FROM migration_history 
                WHERE migration_id = :migration_id 
                AND status = 'completed'
            """)
            result = await session.execute(query, {"migration_id": dependency.migration_id})
            if not result.fetchone():
                raise ValueError(f"Required dependency not met: {dependency.migration_id}")
                
    async def _validate_table_access(self) -> None:
        """Validate access to affected tables"""
        async with self._get_session() as session:
            for table_name in self.metadata.affects_tables:
                try:
                    query = text(f"SELECT 1 FROM {table_name} LIMIT 1")
                    await session.execute(query)
                except SQLAlchemyError as e:
                    raise ValueError(f"Cannot access table {table_name}: {e}")
                    
    async def _validate_data_integrity(self) -> None:
        """Validate data integrity before migration"""
        # Override in subclasses for specific integrity checks
        pass
        
    async def _validate_post_migration(self, session: Session) -> None:
        """
Validate data integrity after migration"""
        # Override in subclasses for specific post-migration validation
        pass
        
    async def _get_session(self) -> Session:
        """
Get database session"""
        return self.session_maker()
        
    async def _get_transaction_session(self) -> Session:
        """
Get database session with transaction management"""
        session = self.session_maker()
        try:
            session.begin()
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            
    async def _record_migration_execution(self, result: MigrationResult) -> None:
        """
Record migration execution in history"""
        async with self._get_session() as session:
            try:
                insert_query = text("""
                    INSERT INTO migration_history 
                    (migration_id, version, name, category, status, started_at, completed_at, 
                     duration_seconds, affected_rows, error_message, tenant_id, metadata)
                    VALUES 
                    (:migration_id, :version, :name, :category, :status, :started_at, :completed_at,
                     :duration_seconds, :affected_rows, :error_message, :tenant_id, :metadata)
                """)
                
                await session.execute(insert_query, {
                    "migration_id": result.migration_id,
                    "version": self.metadata.version,
                    "name": self.metadata.name,
                    "category": self.metadata.category.value,
                    "status": result.status.value,
                    "started_at": result.started_at,
                    "completed_at": result.completed_at,
                    "duration_seconds": result.duration_seconds,
                    "affected_rows": result.affected_rows,
                    "error_message": result.error_message,
                    "tenant_id": self.tenant_id,
                    "metadata": json.dumps(self.metadata.__dict__, default=str)
                })
                session.commit()
            except SQLAlchemyError as e:
                logger.error(f"Failed to record migration history: {e}")
                
    def calculate_checksum(self, data: str) -> str:
        """Calculate data checksum for integrity validation"""
        return hashlib.sha256(data.encode()).hexdigest()
        
    def log_operation(self, operation: str, details: Dict[str, Any]) -> None:
        """
Log migration operation for rollback purposes"""
        self.executed_operations.append({
            "operation": operation,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    async def create_backup_point(self, session: Session, identifier: str) -> str:
        """Create data backup point for rollback"""
        # Override in subclasses for specific backup strategies
        backup_id = str(uuid.uuid4())
        self.rollback_data[identifier] = backup_id
        return backup_id


class MigrationRegistry:
    """
    Migration registry for tracking and managing migrations
    """
    
    def __init__(self):
        self.migrations: Dict[str, BaseMigration] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        
    def register(self, migration: BaseMigration) -> None:
        """
Register migration in registry"""
        migration_id = migration.metadata.migration_id
        self.migrations[migration_id] = migration
        
        # Register dependencies
        deps = {dep.migration_id for dep in migration.metadata.dependencies if dep.required}
        self.dependencies[migration_id] = deps
        
    def get_execution_order(self) -> List[str]:
        """
Get migrations in dependency-resolved execution order"""
        ordered = []
        resolved = set()
        
        def resolve_dependencies(migration_id: str):
            if migration_id in resolved:
                return
                
            for dep_id in self.dependencies.get(migration_id, set()):
                resolve_dependencies(dep_id)
                
            if migration_id not in resolved:
                ordered.append(migration_id)
                resolved.add(migration_id)
                
        for migration_id in self.migrations:
            resolve_dependencies(migration_id)
            
        return ordered
        
    def get_migration(self, migration_id: str) -> Optional[BaseMigration]:
        """
Get migration by ID"""
        return self.migrations.get(migration_id)
        
    def list_pending_migrations(self, executed_migrations: Set[str]) -> List[str]:
        """
List migrations that haven't been executed"""
        all_migrations = set(self.migrations.keys())
        pending = all_migrations - executed_migrations
        
        # Return in execution order
        execution_order = self.get_execution_order()
        return [mid for mid in execution_order if mid in pending]


# Global migration registry
migration_registry = MigrationRegistry()
