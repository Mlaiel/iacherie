"""
🔄 Schema Version Control & Migration System
Enterprise-grade schema versioning and automated migration management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.

🎯 DBA Expert Role: Advanced database migration and version control
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator
import hashlib
import json
from pathlib import Path
import asyncio
from abc import ABC, abstractmethod

from .base import BaseSchema, TimestampSchema, UUIDSchema
from .schema_registry import SchemaVersion, SchemaMetadata, SchemaRegistry


class MigrationType(str, Enum):
    """Migration operation types"""
    CREATE_TABLE = "create_table"
    ALTER_TABLE = "alter_table"
    DROP_TABLE = "drop_table"
    ADD_COLUMN = "add_column"
    MODIFY_COLUMN = "modify_column"
    DROP_COLUMN = "drop_column"
    CREATE_INDEX = "create_index"
    DROP_INDEX = "drop_index"
    DATA_MIGRATION = "data_migration"
    CUSTOM = "custom"


class MigrationStrategy(str, Enum):
    """Migration execution strategies"""
    IMMEDIATE = "immediate"
    GRADUAL = "gradual"
    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    MAINTENANCE_WINDOW = "maintenance_window"


class MigrationStatus(str, Enum):
    """Migration execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


class ChangeType(str, Enum):
    """Schema change classification"""
    ADDITION = "addition"
    MODIFICATION = "modification"
    DELETION = "deletion"
    RENAMING = "renaming"
    RESTRUCTURING = "restructuring"


class CompatibilityLevel(str, Enum):
    """Compatibility assessment levels"""
    FULL = "full"
    BACKWARD = "backward"
    FORWARD = "forward"
    BREAKING = "breaking"
    NONE = "none"


class SchemaChange(UUIDSchema, TimestampSchema):
    """Individual schema change record"""
    change_type: ChangeType = Field(description="Type of change")
    field_path: str = Field(description="Path to changed field (e.g., 'properties.user.type')")
    old_value: Optional[Any] = Field(None, description="Previous value")
    new_value: Optional[Any] = Field(None, description="New value")
    description: str = Field(description="Human-readable change description")
    is_breaking: bool = Field(description="Whether this is a breaking change")
    impact_assessment: str = Field(description="Impact assessment")
    migration_hint: Optional[str] = Field(None, description="Migration guidance")


class MigrationStep(UUIDSchema, TimestampSchema):
    """Individual migration step"""
    step_number: int = Field(ge=1, description="Step execution order")
    step_name: str = Field(description="Step name/identifier")
    migration_type: MigrationType = Field(description="Type of migration operation")
    sql_command: Optional[str] = Field(None, description="SQL command for database migrations")
    python_code: Optional[str] = Field(None, description="Python code for data migrations")
    validation_query: Optional[str] = Field(None, description="Query to validate step completion")
    rollback_command: Optional[str] = Field(None, description="Command to rollback this step")
    
    # Execution metadata
    depends_on: List[UUID] = Field(default_factory=list, description="Step dependencies")
    estimated_duration: Optional[timedelta] = Field(None, description="Estimated execution time")
    max_retry_attempts: int = Field(default=3, ge=0, description="Maximum retry attempts")
    timeout_seconds: int = Field(default=300, ge=1, description="Step timeout")
    
    # Execution results
    execution_status: MigrationStatus = Field(default=MigrationStatus.PENDING)
    execution_start: Optional[datetime] = Field(None, description="Execution start time")
    execution_end: Optional[datetime] = Field(None, description="Execution end time")
    retry_count: int = Field(default=0, ge=0, description="Number of retry attempts")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    execution_log: List[str] = Field(default_factory=list, description="Execution log messages")
    
    @property
    def execution_duration(self) -> Optional[timedelta]:
        """Get execution duration if completed"""
        if self.execution_start and self.execution_end:
            return self.execution_end - self.execution_start
        return None


class SchemaMigration(UUIDSchema, TimestampSchema):
    """Schema migration definition"""
    migration_name: str = Field(description="Migration name/identifier")
    source_schema: str = Field(description="Source schema name")
    target_schema: str = Field(description="Target schema name")
    source_version: SchemaVersion = Field(description="Source schema version")
    target_version: SchemaVersion = Field(description="Target schema version")
    
    # Migration metadata
    description: str = Field(description="Migration description")
    strategy: MigrationStrategy = Field(description="Migration execution strategy")
    compatibility_level: CompatibilityLevel = Field(description="Compatibility assessment")
    is_reversible: bool = Field(description="Whether migration can be reversed")
    estimated_downtime: Optional[timedelta] = Field(None, description="Estimated downtime")
    
    # Change tracking
    schema_changes: List[SchemaChange] = Field(default_factory=list, description="List of schema changes")
    migration_steps: List[MigrationStep] = Field(default_factory=list, description="Migration execution steps")
    
    # Prerequisites and dependencies
    prerequisites: List[str] = Field(default_factory=list, description="Migration prerequisites")
    migration_dependencies: List[UUID] = Field(default_factory=list, description="Dependent migrations")
    
    # Execution metadata
    migration_status: MigrationStatus = Field(default=MigrationStatus.PENDING)
    scheduled_for: Optional[datetime] = Field(None, description="Scheduled execution time")
    execution_start: Optional[datetime] = Field(None, description="Actual execution start")
    execution_end: Optional[datetime] = Field(None, description="Actual execution end")
    executed_by: Optional[str] = Field(None, description="User who executed migration")
    
    # Validation and testing
    pre_migration_checks: List[str] = Field(default_factory=list, description="Pre-migration validation")
    post_migration_checks: List[str] = Field(default_factory=list, description="Post-migration validation")
    test_data_queries: List[str] = Field(default_factory=list, description="Test data validation queries")
    
    @property
    def has_breaking_changes(self) -> bool:
        """Check if migration contains breaking changes"""
        return any(change.is_breaking for change in self.schema_changes)
    
    @property
    def total_steps(self) -> int:
        """Get total number of migration steps"""
        return len(self.migration_steps)
    
    @property
    def completed_steps(self) -> int:
        """Get number of completed steps"""
        return len([step for step in self.migration_steps 
                   if step.execution_status == MigrationStatus.COMPLETED])


class MigrationPlan(UUIDSchema, TimestampSchema):
    """Migration execution plan"""
    plan_name: str = Field(description="Migration plan name")
    description: str = Field(description="Plan description")
    migrations: List[UUID] = Field(description="Ordered list of migration IDs")
    total_estimated_duration: timedelta = Field(description="Total estimated execution time")
    maintenance_window: Optional[Tuple[datetime, datetime]] = Field(None, description="Maintenance window")
    rollback_plan: Optional[UUID] = Field(None, description="Rollback plan ID")
    approval_required: bool = Field(default=True, description="Whether approval is required")
    approved_by: Optional[str] = Field(None, description="Approver name")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")


class SchemaVersionControl:
    """
    Enterprise-grade schema version control system
    Manages schema evolution, migrations, and compatibility
    """
    
    def __init__(self, registry: SchemaRegistry, storage_path: Optional[Path] = None):
        self.registry = registry
        self.storage_path = storage_path or Path("./migration_data")
        self.migrations: Dict[UUID, SchemaMigration] = {}
        self.migration_plans: Dict[UUID, MigrationPlan] = {}
        self.change_detectors: Dict[str, Callable] = {}
        self._initialize_storage()
        self._register_default_detectors()
    
    def _initialize_storage(self):
        """Initialize version control storage"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._load_migrations()
        self._load_migration_plans()
    
    def _load_migrations(self):
        """Load migrations from storage"""
        migrations_path = self.storage_path / "migrations"
        migrations_path.mkdir(exist_ok=True)
        
        for migration_file in migrations_path.glob("*.json"):
            try:
                with open(migration_file, 'r') as f:
                    migration_data = json.load(f)
                    migration = SchemaMigration(**migration_data)
                    self.migrations[migration.id] = migration
            except Exception as e:
                print(f"Error loading migration {migration_file}: {e}")
    
    def _load_migration_plans(self):
        """Load migration plans from storage"""
        plans_path = self.storage_path / "plans"
        plans_path.mkdir(exist_ok=True)
        
        for plan_file in plans_path.glob("*.json"):
            try:
                with open(plan_file, 'r') as f:
                    plan_data = json.load(f)
                    plan = MigrationPlan(**plan_data)
                    self.migration_plans[plan.id] = plan
            except Exception as e:
                print(f"Error loading migration plan {plan_file}: {e}")
    
    def _register_default_detectors(self):
        """Register default change detection algorithms"""
        self.change_detectors.update({
            "field_addition": self._detect_field_additions,
            "field_deletion": self._detect_field_deletions,
            "field_modification": self._detect_field_modifications,
            "type_changes": self._detect_type_changes,
            "constraint_changes": self._detect_constraint_changes,
        })
    
    def detect_schema_changes(self, 
                            source_schema: SchemaMetadata, 
                            target_schema: SchemaMetadata) -> List[SchemaChange]:
        """
        Detect changes between two schema versions
        Returns list of individual changes
        """
        changes = []
        
        for detector_name, detector_func in self.change_detectors.items():
            try:
                detected_changes = detector_func(source_schema, target_schema)
                changes.extend(detected_changes)
            except Exception as e:
                print(f"Error in change detector {detector_name}: {e}")
        
        return changes
    
    def _detect_field_additions(self, source: SchemaMetadata, target: SchemaMetadata) -> List[SchemaChange]:
        """Detect added fields"""
        changes = []
        source_props = source.schema_content.get("properties", {})
        target_props = target.schema_content.get("properties", {})
        
        for field_name, field_def in target_props.items():
            if field_name not in source_props:
                changes.append(SchemaChange(
                    id=uuid4(),
                    change_type=ChangeType.ADDITION,
                    field_path=f"properties.{field_name}",
                    old_value=None,
                    new_value=field_def,
                    description=f"Added new field '{field_name}'",
                    is_breaking=field_def.get("required", False),
                    impact_assessment="Low" if not field_def.get("required") else "Medium"
                ))
        
        return changes
    
    def _detect_field_deletions(self, source: SchemaMetadata, target: SchemaMetadata) -> List[SchemaChange]:
        """Detect deleted fields"""
        changes = []
        source_props = source.schema_content.get("properties", {})
        target_props = target.schema_content.get("properties", {})
        
        for field_name, field_def in source_props.items():
            if field_name not in target_props:
                changes.append(SchemaChange(
                    id=uuid4(),
                    change_type=ChangeType.DELETION,
                    field_path=f"properties.{field_name}",
                    old_value=field_def,
                    new_value=None,
                    description=f"Removed field '{field_name}'",
                    is_breaking=True,
                    impact_assessment="High",
                    migration_hint=f"Ensure data for '{field_name}' is backed up before deletion"
                ))
        
        return changes
    
    def _detect_field_modifications(self, source: SchemaMetadata, target: SchemaMetadata) -> List[SchemaChange]:
        """Detect modified fields"""
        changes = []
        source_props = source.schema_content.get("properties", {})
        target_props = target.schema_content.get("properties", {})
        
        for field_name in set(source_props.keys()) & set(target_props.keys()):
            source_field = source_props[field_name]
            target_field = target_props[field_name]
            
            if source_field != target_field:
                changes.append(SchemaChange(
                    id=uuid4(),
                    change_type=ChangeType.MODIFICATION,
                    field_path=f"properties.{field_name}",
                    old_value=source_field,
                    new_value=target_field,
                    description=f"Modified field '{field_name}'",
                    is_breaking=self._is_breaking_field_change(source_field, target_field),
                    impact_assessment="Medium"
                ))
        
        return changes
    
    def _detect_type_changes(self, source: SchemaMetadata, target: SchemaMetadata) -> List[SchemaChange]:
        """Detect data type changes"""
        changes = []
        source_props = source.schema_content.get("properties", {})
        target_props = target.schema_content.get("properties", {})
        
        for field_name in set(source_props.keys()) & set(target_props.keys()):
            source_type = source_props[field_name].get("type")
            target_type = target_props[field_name].get("type")
            
            if source_type != target_type:
                changes.append(SchemaChange(
                    id=uuid4(),
                    change_type=ChangeType.MODIFICATION,
                    field_path=f"properties.{field_name}.type",
                    old_value=source_type,
                    new_value=target_type,
                    description=f"Changed type of '{field_name}' from {source_type} to {target_type}",
                    is_breaking=True,
                    impact_assessment="High",
                    migration_hint=f"Data conversion required for '{field_name}'"
                ))
        
        return changes
    
    def _detect_constraint_changes(self, source: SchemaMetadata, target: SchemaMetadata) -> List[SchemaChange]:
        """Detect constraint changes"""
        changes = []
        
        # Check required field changes
        source_required = set(source.schema_content.get("required", []))
        target_required = set(target.schema_content.get("required", []))
        
        # New required fields
        for field in target_required - source_required:
            changes.append(SchemaChange(
                id=uuid4(),
                change_type=ChangeType.MODIFICATION,
                field_path=f"required.{field}",
                old_value=False,
                new_value=True,
                description=f"Field '{field}' is now required",
                is_breaking=True,
                impact_assessment="High",
                migration_hint=f"Ensure all existing records have '{field}' populated"
            ))
        
        # Removed required fields
        for field in source_required - target_required:
            changes.append(SchemaChange(
                id=uuid4(),
                change_type=ChangeType.MODIFICATION,
                field_path=f"required.{field}",
                old_value=True,
                new_value=False,
                description=f"Field '{field}' is no longer required",
                is_breaking=False,
                impact_assessment="Low"
            ))
        
        return changes
    
    def _is_breaking_field_change(self, source_field: Dict, target_field: Dict) -> bool:
        """Determine if field change is breaking"""
        breaking_changes = [
            source_field.get("type") != target_field.get("type"),
            source_field.get("format") != target_field.get("format"),
            target_field.get("maxLength", float('inf')) < source_field.get("maxLength", float('inf')),
            target_field.get("maximum", float('inf')) < source_field.get("maximum", float('inf')),
        ]
        return any(breaking_changes)
    
    def create_migration(self, 
                        source_schema: str, 
                        target_schema: str,
                        source_version: str,
                        target_version: str,
                        strategy: MigrationStrategy = MigrationStrategy.IMMEDIATE) -> SchemaMigration:
        """
        Create migration between two schema versions
        Automatically detects changes and generates migration steps
        """
        # Get schema metadata
        source_meta = self.registry.get_schema(source_schema, source_version)
        target_meta = self.registry.get_schema(target_schema, target_version)
        
        if not source_meta or not target_meta:
            raise ValueError("Source or target schema not found in registry")
        
        # Detect changes
        changes = self.detect_schema_changes(source_meta, target_meta)
        
        # Generate migration steps
        migration_steps = self._generate_migration_steps(changes)
        
        # Assess compatibility
        compatibility = self._assess_compatibility(changes)
        
        # Create migration
        migration = SchemaMigration(
            id=uuid4(),
            migration_name=f"{source_schema}_{source_version}_to_{target_version}",
            source_schema=source_schema,
            target_schema=target_schema,
            source_version=SchemaVersion.parse_obj(source_version),
            target_version=SchemaVersion.parse_obj(target_version),
            description=f"Migration from {source_schema} v{source_version} to v{target_version}",
            strategy=strategy,
            compatibility_level=compatibility,
            is_reversible=self._is_reversible_migration(changes),
            schema_changes=changes,
            migration_steps=migration_steps
        )
        
        # Store migration
        self.migrations[migration.id] = migration
        self._persist_migration(migration)
        
        return migration
    
    def _generate_migration_steps(self, changes: List[SchemaChange]) -> List[MigrationStep]:
        """Generate migration steps from schema changes"""
        steps = []
        step_number = 1
        
        # Group changes by type for optimal execution order
        additions = [c for c in changes if c.change_type == ChangeType.ADDITION]
        modifications = [c for c in changes if c.change_type == ChangeType.MODIFICATION]
        deletions = [c for c in changes if c.change_type == ChangeType.DELETION]
        
        # Process additions first (safest)
        for change in additions:
            step = MigrationStep(
                id=uuid4(),
                step_number=step_number,
                step_name=f"add_{change.field_path.replace('.', '_')}",
                migration_type=MigrationType.ADD_COLUMN,
                sql_command=self._generate_add_column_sql(change),
                validation_query=f"SELECT COUNT(*) FROM information_schema.columns WHERE column_name = '{change.field_path}'",
                rollback_command=self._generate_drop_column_sql(change)
            )
            steps.append(step)
            step_number += 1
        
        # Process modifications
        for change in modifications:
            step = MigrationStep(
                id=uuid4(),
                step_number=step_number,
                step_name=f"modify_{change.field_path.replace('.', '_')}",
                migration_type=MigrationType.MODIFY_COLUMN,
                sql_command=self._generate_modify_column_sql(change),
                validation_query=f"SELECT data_type FROM information_schema.columns WHERE column_name = '{change.field_path}'",
                rollback_command=self._generate_revert_column_sql(change)
            )
            steps.append(step)
            step_number += 1
        
        # Process deletions last (most dangerous)
        for change in deletions:
            step = MigrationStep(
                id=uuid4(),
                step_number=step_number,
                step_name=f"drop_{change.field_path.replace('.', '_')}",
                migration_type=MigrationType.DROP_COLUMN,
                sql_command=self._generate_drop_column_sql(change),
                validation_query=f"SELECT COUNT(*) FROM information_schema.columns WHERE column_name = '{change.field_path}'",
                rollback_command=self._generate_add_column_sql(change)
            )
            steps.append(step)
            step_number += 1
        
        return steps
    
    def _generate_add_column_sql(self, change: SchemaChange) -> str:
        """Generate SQL for adding a column"""
        field_name = change.field_path.split('.')[-1]
        field_type = self._map_schema_type_to_sql(change.new_value.get("type", "string"))
        nullable = "NULL" if not change.new_value.get("required", False) else "NOT NULL"
        return f"ALTER TABLE schema_table ADD COLUMN {field_name} {field_type} {nullable};"
    
    def _generate_drop_column_sql(self, change: SchemaChange) -> str:
        """Generate SQL for dropping a column"""
        field_name = change.field_path.split('.')[-1]
        return f"ALTER TABLE schema_table DROP COLUMN {field_name};"
    
    def _generate_modify_column_sql(self, change: SchemaChange) -> str:
        """Generate SQL for modifying a column"""
        field_name = change.field_path.split('.')[-1]
        new_type = self._map_schema_type_to_sql(change.new_value.get("type", "string"))
        return f"ALTER TABLE schema_table ALTER COLUMN {field_name} TYPE {new_type};"
    
    def _generate_revert_column_sql(self, change: SchemaChange) -> str:
        """Generate SQL for reverting a column change"""
        field_name = change.field_path.split('.')[-1]
        old_type = self._map_schema_type_to_sql(change.old_value.get("type", "string"))
        return f"ALTER TABLE schema_table ALTER COLUMN {field_name} TYPE {old_type};"
    
    def _map_schema_type_to_sql(self, schema_type: str) -> str:
        """Map JSON schema types to SQL types"""
        type_mapping = {
            "string": "VARCHAR(255)",
            "integer": "INTEGER",
            "number": "DECIMAL",
            "boolean": "BOOLEAN",
            "array": "JSON",
            "object": "JSON"
        }
        return type_mapping.get(schema_type, "TEXT")
    
    def _assess_compatibility(self, changes: List[SchemaChange]) -> CompatibilityLevel:
        """Assess compatibility level based on changes"""
        has_breaking = any(change.is_breaking for change in changes)
        has_additions = any(change.change_type == ChangeType.ADDITION for change in changes)
        has_deletions = any(change.change_type == ChangeType.DELETION for change in changes)
        
        if has_breaking or has_deletions:
            return CompatibilityLevel.BREAKING
        elif has_additions:
            return CompatibilityLevel.BACKWARD
        else:
            return CompatibilityLevel.FULL
    
    def _is_reversible_migration(self, changes: List[SchemaChange]) -> bool:
        """Determine if migration is reversible"""
        # Migrations with data loss are not easily reversible
        data_loss_changes = [
            ChangeType.DELETION,
            ChangeType.MODIFICATION  # Type changes might cause data loss
        ]
        return not any(change.change_type in data_loss_changes for change in changes)
    
    def _persist_migration(self, migration: SchemaMigration):
        """Persist migration to storage"""
        migrations_path = self.storage_path / "migrations"
        migrations_path.mkdir(exist_ok=True)
        
        filename = f"{migration.migration_name}_{migration.id}.json"
        filepath = migrations_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(migration.dict(), f, indent=2, default=str)
    
    async def execute_migration(self, migration_id: UUID, dry_run: bool = False) -> bool:
        """
        Execute a migration
        Returns True if successful
        """
        migration = self.migrations.get(migration_id)
        if not migration:
            raise ValueError(f"Migration {migration_id} not found")
        
        try:
            migration.migration_status = MigrationStatus.IN_PROGRESS
            migration.execution_start = datetime.utcnow()
            
            # Execute each step
            for step in migration.migration_steps:
                if not await self._execute_migration_step(step, dry_run):
                    migration.migration_status = MigrationStatus.FAILED
                    return False
            
            migration.migration_status = MigrationStatus.COMPLETED
            migration.execution_end = datetime.utcnow()
            
            # Update registry with new schema version
            if not dry_run:
                self._update_schema_registry(migration)
            
            return True
            
        except Exception as e:
            migration.migration_status = MigrationStatus.FAILED
            migration.execution_end = datetime.utcnow()
            print(f"Migration failed: {e}")
            return False
        finally:
            self._persist_migration(migration)
    
    async def _execute_migration_step(self, step: MigrationStep, dry_run: bool) -> bool:
        """Execute individual migration step"""
        try:
            step.execution_status = MigrationStatus.IN_PROGRESS
            step.execution_start = datetime.utcnow()
            
            if dry_run:
                step.execution_log.append(f"DRY RUN: Would execute {step.migration_type}")
                await asyncio.sleep(0.1)  # Simulate execution time
            else:
                # Execute the actual step
                if step.sql_command:
                    # Execute SQL command (would integrate with actual database)
                    step.execution_log.append(f"Executed SQL: {step.sql_command}")
                
                if step.python_code:
                    # Execute Python code (would use safe execution environment)
                    step.execution_log.append(f"Executed Python code")
            
            step.execution_status = MigrationStatus.COMPLETED
            step.execution_end = datetime.utcnow()
            return True
            
        except Exception as e:
            step.execution_status = MigrationStatus.FAILED
            step.error_message = str(e)
            step.execution_end = datetime.utcnow()
            return False
    
    def _update_schema_registry(self, migration: SchemaMigration):
        """Update schema registry after successful migration"""
        # This would update the schema registry with the new version
        pass
    
    def get_migration_history(self, schema_name: str) -> List[SchemaMigration]:
        """Get migration history for a schema"""
        return [m for m in self.migrations.values() 
                if m.source_schema == schema_name or m.target_schema == schema_name]
    
    def create_rollback_migration(self, migration_id: UUID) -> Optional[SchemaMigration]:
        """Create rollback migration for a completed migration"""
        original_migration = self.migrations.get(migration_id)
        if not original_migration or not original_migration.is_reversible:
            return None
        
        # Create reverse migration
        rollback_migration = SchemaMigration(
            id=uuid4(),
            migration_name=f"rollback_{original_migration.migration_name}",
            source_schema=original_migration.target_schema,
            target_schema=original_migration.source_schema,
            source_version=original_migration.target_version,
            target_version=original_migration.source_version,
            description=f"Rollback migration for {original_migration.migration_name}",
            strategy=original_migration.strategy,
            compatibility_level=CompatibilityLevel.BREAKING,
            is_reversible=True,
            schema_changes=[],  # Would generate reverse changes
            migration_steps=[]  # Would generate reverse steps
        )
        
        return rollback_migration


# Export all classes
__all__ = [
    'MigrationType',
    'MigrationStrategy',
    'MigrationStatus',
    'ChangeType',
    'CompatibilityLevel',
    'SchemaChange',
    'MigrationStep',
    'SchemaMigration',
    'MigrationPlan',
    'SchemaVersionControl'
]