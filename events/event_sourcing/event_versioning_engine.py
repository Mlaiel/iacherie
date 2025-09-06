"""Event Versioning Engine - Advanced Implementation

Enterprise-grade event versioning system with schema evolution, migration,
backward compatibility, and breaking change detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import logging
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Type, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
from uuid import uuid4
import copy

from . import DomainEvent

logger = logging.getLogger(__name__)


class VersionType(Enum):
    """Version type classification"""
    MAJOR = "major"  # Breaking changes
    MINOR = "minor"  # New features, backward compatible
    PATCH = "patch"  # Bug fixes, backward compatible
    HOTFIX = "hotfix"  # Emergency fixes


class CompatibilityLevel(Enum):
    """Compatibility levels between versions"""
    FULL = "full"  # Fully compatible
    BACKWARD = "backward"  # Backward compatible only
    FORWARD = "forward"  # Forward compatible only
    BREAKING = "breaking"  # Not compatible


class SchemaChangeType(Enum):
    """Types of schema changes"""
    FIELD_ADDED = "field_added"
    FIELD_REMOVED = "field_removed"
    FIELD_RENAMED = "field_renamed"
    FIELD_TYPE_CHANGED = "field_type_changed"
    FIELD_REQUIRED_CHANGED = "field_required_changed"
    ENUM_VALUE_ADDED = "enum_value_added"
    ENUM_VALUE_REMOVED = "enum_value_removed"
    STRUCTURE_CHANGED = "structure_changed"


@dataclass
class SemanticVersion:
    """Semantic version representation"""
    major: int
    minor: int
    patch: int
    prerelease: str = ""
    build: str = ""
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version
    
    def __eq__(self, other: 'SemanticVersion') -> bool:
        return (self.major == other.major and 
                self.minor == other.minor and 
                self.patch == other.patch and
                self.prerelease == other.prerelease)
    
    def __lt__(self, other: 'SemanticVersion') -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        return self.prerelease < other.prerelease
    
    @classmethod
    def parse(cls, version_str: str) -> 'SemanticVersion':
        """Parse version string"""
        try:
            # Remove build metadata
            main_version, build = version_str.split('+', 1) if '+' in version_str else (version_str, "")
            
            # Remove prerelease
            version_parts, prerelease = main_version.split('-', 1) if '-' in main_version else (main_version, "")
            
            # Parse major.minor.patch
            parts = version_parts.split('.')
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            
            return cls(major=major, minor=minor, patch=patch, prerelease=prerelease, build=build)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid version format: {version_str}") from e


@dataclass
class SchemaField:
    """Schema field definition"""
    name: str
    type: str
    required: bool = False
    default: Any = None
    description: str = ""
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EventSchema:
    """Event schema definition"""
    event_type: str
    version: SemanticVersion
    fields: List[SchemaField]
    description: str = ""
    examples: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "version": str(self.version),
            "fields": [field.to_dict() for field in self.fields],
            "description": self.description,
            "examples": self.examples,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventSchema':
        fields = [SchemaField(**field_data) for field_data in data.get("fields", [])]
        return cls(
            event_type=data["event_type"],
            version=SemanticVersion.parse(data["version"]),
            fields=fields,
            description=data.get("description", ""),
            examples=data.get("examples", []),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now(timezone.utc).isoformat())),
            created_by=data.get("created_by", "system"),
            tags=data.get("tags", [])
        )


@dataclass
class SchemaChange:
    """Schema change description"""
    change_type: SchemaChangeType
    field_name: str
    old_value: Any = None
    new_value: Any = None
    description: str = ""
    breaking: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "change_type": self.change_type.value,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "description": self.description,
            "breaking": self.breaking
        }


@dataclass
class MigrationRule:
    """Migration rule for version transition"""
    from_version: SemanticVersion
    to_version: SemanticVersion
    transformation_func: str  # Function name or code
    description: str = ""
    automatic: bool = True
    validation_func: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_version": str(self.from_version),
            "to_version": str(self.to_version),
            "transformation_func": self.transformation_func,
            "description": self.description,
            "automatic": self.automatic,
            "validation_func": self.validation_func
        }


@dataclass
class VersionMetadata:
    """Version metadata and statistics"""
    version: SemanticVersion
    event_type: str
    usage_count: int = 0
    first_used: Optional[datetime] = None
    last_used: Optional[datetime] = None
    deprecation_date: Optional[datetime] = None
    end_of_life_date: Optional[datetime] = None
    is_deprecated: bool = False
    replacement_version: Optional[SemanticVersion] = None
    breaking_changes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": str(self.version),
            "event_type": self.event_type,
            "usage_count": self.usage_count,
            "first_used": self.first_used.isoformat() if self.first_used else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "deprecation_date": self.deprecation_date.isoformat() if self.deprecation_date else None,
            "end_of_life_date": self.end_of_life_date.isoformat() if self.end_of_life_date else None,
            "is_deprecated": self.is_deprecated,
            "replacement_version": str(self.replacement_version) if self.replacement_version else None,
            "breaking_changes": self.breaking_changes
        }


class SchemaRegistryInterface(ABC):
    """Interface for schema registry implementations"""
    
    @abstractmethod
    async def register_schema(self, schema: EventSchema) -> bool:
        """Register a new schema version"""
        pass
    
    @abstractmethod
    async def get_schema(self, event_type: str, version: SemanticVersion) -> Optional[EventSchema]:
        """Get specific schema version"""
        pass
    
    @abstractmethod
    async def get_latest_schema(self, event_type: str) -> Optional[EventSchema]:
        """Get latest schema for event type"""
        pass
    
    @abstractmethod
    async def list_schemas(self, event_type: str) -> List[EventSchema]:
        """List all schemas for event type"""
        pass
    
    @abstractmethod
    async def deprecate_schema(self, event_type: str, version: SemanticVersion, 
                             replacement_version: SemanticVersion = None) -> bool:
        """Mark schema as deprecated"""
        pass


class MemorySchemaRegistry(SchemaRegistryInterface):
    """In-memory schema registry for testing"""
    
    def __init__(self):
        self.schemas: Dict[str, Dict[str, EventSchema]] = {}  # event_type -> version -> schema
        self.metadata: Dict[str, Dict[str, VersionMetadata]] = {}
    
    async def register_schema(self, schema: EventSchema) -> bool:
        """Register schema in memory"""
        try:
            if schema.event_type not in self.schemas:
                self.schemas[schema.event_type] = {}
                self.metadata[schema.event_type] = {}
            
            version_str = str(schema.version)
            self.schemas[schema.event_type][version_str] = schema
            
            # Initialize metadata
            self.metadata[schema.event_type][version_str] = VersionMetadata(
                version=schema.version,
                event_type=schema.event_type
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to register schema: {e}")
            return False
    
    async def get_schema(self, event_type: str, version: SemanticVersion) -> Optional[EventSchema]:
        """Get schema from memory"""
        if event_type in self.schemas:
            return self.schemas[event_type].get(str(version))
        return None
    
    async def get_latest_schema(self, event_type: str) -> Optional[EventSchema]:
        """Get latest schema version"""
        if event_type not in self.schemas:
            return None
        
        schemas = self.schemas[event_type]
        if not schemas:
            return None
        
        # Find latest version
        latest_version = None
        latest_schema = None
        
        for version_str, schema in schemas.items():
            if latest_version is None or schema.version > latest_version:
                latest_version = schema.version
                latest_schema = schema
        
        return latest_schema
    
    async def list_schemas(self, event_type: str) -> List[EventSchema]:
        """List all schemas for event type"""
        if event_type in self.schemas:
            return list(self.schemas[event_type].values())
        return []
    
    async def deprecate_schema(self, event_type: str, version: SemanticVersion, 
                             replacement_version: SemanticVersion = None) -> bool:
        """Deprecate schema version"""
        try:
            version_str = str(version)
            if event_type in self.metadata and version_str in self.metadata[event_type]:
                metadata = self.metadata[event_type][version_str]
                metadata.is_deprecated = True
                metadata.deprecation_date = datetime.now(timezone.utc)
                metadata.replacement_version = replacement_version
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to deprecate schema: {e}")
            return False


class SchemaComparator:
    """Compare schemas and detect changes"""
    
    @staticmethod
    def compare_schemas(old_schema: EventSchema, new_schema: EventSchema) -> List[SchemaChange]:
        """Compare two schemas and return list of changes"""
        changes = []
        
        # Create field maps for easier comparison
        old_fields = {field.name: field for field in old_schema.fields}
        new_fields = {field.name: field for field in new_schema.fields}
        
        # Check for removed fields
        for field_name in old_fields:
            if field_name not in new_fields:
                changes.append(SchemaChange(
                    change_type=SchemaChangeType.FIELD_REMOVED,
                    field_name=field_name,
                    old_value=old_fields[field_name].to_dict(),
                    breaking=old_fields[field_name].required
                ))
        
        # Check for added fields
        for field_name in new_fields:
            if field_name not in old_fields:
                changes.append(SchemaChange(
                    change_type=SchemaChangeType.FIELD_ADDED,
                    field_name=field_name,
                    new_value=new_fields[field_name].to_dict(),
                    breaking=new_fields[field_name].required and new_fields[field_name].default is None
                ))
        
        # Check for changed fields
        for field_name in old_fields:
            if field_name in new_fields:
                old_field = old_fields[field_name]
                new_field = new_fields[field_name]
                
                # Check type change
                if old_field.type != new_field.type:
                    changes.append(SchemaChange(
                        change_type=SchemaChangeType.FIELD_TYPE_CHANGED,
                        field_name=field_name,
                        old_value=old_field.type,
                        new_value=new_field.type,
                        breaking=True
                    ))
                
                # Check required change
                if old_field.required != new_field.required:
                    changes.append(SchemaChange(
                        change_type=SchemaChangeType.FIELD_REQUIRED_CHANGED,
                        field_name=field_name,
                        old_value=old_field.required,
                        new_value=new_field.required,
                        breaking=new_field.required and not old_field.required
                    ))
        
        return changes
    
    @staticmethod
    def determine_compatibility(changes: List[SchemaChange]) -> CompatibilityLevel:
        """Determine compatibility level based on changes"""
        if not changes:
            return CompatibilityLevel.FULL
        
        has_breaking_changes = any(change.breaking for change in changes)
        
        if has_breaking_changes:
            return CompatibilityLevel.BREAKING
        
        # Check if only additions (forward compatible)
        only_additions = all(
            change.change_type == SchemaChangeType.FIELD_ADDED 
            for change in changes
        )
        
        if only_additions:
            return CompatibilityLevel.FORWARD
        
        # Otherwise, backward compatible
        return CompatibilityLevel.BACKWARD


class EventMigrator:
    """Event data migrator between versions"""
    
    def __init__(self):
        self.migration_functions: Dict[str, Callable] = {}
        self.validation_functions: Dict[str, Callable] = {}
    
    def register_migration(self, from_version: str, to_version: str, 
                         migration_func: Callable, validation_func: Callable = None) -> None:
        """Register migration function"""
        key = f"{from_version}->{to_version}"
        self.migration_functions[key] = migration_func
        if validation_func:
            self.validation_functions[key] = validation_func
    
    async def migrate_event(self, event: DomainEvent, from_version: SemanticVersion, 
                          to_version: SemanticVersion) -> Optional[DomainEvent]:
        """Migrate event data from one version to another"""
        try:
            key = f"{from_version}->{to_version}"
            
            if key not in self.migration_functions:
                logger.warning(f"No migration function found for {key}")
                return None
            
            migration_func = self.migration_functions[key]
            
            # Create new event with migrated data
            migrated_data = migration_func(event.event_data)
            
            # Validate if validation function exists
            if key in self.validation_functions:
                validation_func = self.validation_functions[key]
                if not validation_func(migrated_data):
                    logger.error(f"Migration validation failed for {key}")
                    return None
            
            migrated_event = DomainEvent(
                event_id=event.event_id,
                aggregate_id=event.aggregate_id,
                aggregate_type=event.aggregate_type,
                event_type=event.event_type,
                event_data=migrated_data,
                event_version=event.event_version,
                occurred_at=event.occurred_at
            )
            
            return migrated_event
            
        except Exception as e:
            logger.error(f"Event migration failed: {e}")
            return None


class EventValidator:
    """Validate events against schemas"""
    
    def __init__(self, schema_registry: SchemaRegistryInterface):
        self.schema_registry = schema_registry
    
    async def validate_event(self, event: DomainEvent, 
                           schema_version: SemanticVersion = None) -> bool:
        """Validate event against schema"""
        try:
            # Get schema
            if schema_version:
                schema = await self.schema_registry.get_schema(event.event_type, schema_version)
            else:
                schema = await self.schema_registry.get_latest_schema(event.event_type)
            
            if not schema:
                logger.warning(f"No schema found for event type {event.event_type}")
                return False
            
            return self._validate_against_schema(event.event_data, schema)
            
        except Exception as e:
            logger.error(f"Event validation failed: {e}")
            return False
    
    def _validate_against_schema(self, event_data: Dict[str, Any], schema: EventSchema) -> bool:
        """Validate event data against schema"""
        try:
            # Check required fields
            schema_fields = {field.name: field for field in schema.fields}
            
            for field in schema.fields:
                if field.required and field.name not in event_data:
                    logger.error(f"Required field {field.name} missing")
                    return False
            
            # Check field types (basic validation)
            for field_name, field_value in event_data.items():
                if field_name in schema_fields:
                    expected_type = schema_fields[field_name].type
                    if not self._check_type(field_value, expected_type):
                        logger.error(f"Field {field_name} type mismatch: expected {expected_type}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Basic type checking"""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True  # Unknown types pass


class EventVersioningEngine:
    """Enterprise event versioning engine"""
    
    def __init__(self, schema_registry: SchemaRegistryInterface):
        self.schema_registry = schema_registry
        self.comparator = SchemaComparator()
        self.migrator = EventMigrator()
        self.validator = EventValidator(schema_registry)
        self.migration_rules: Dict[str, List[MigrationRule]] = {}
        
        # Register default migration functions
        self._register_default_migrations()
    
    def _register_default_migrations(self) -> None:
        """Register default migration functions"""
        # Identity migration (no changes)
        def identity_migration(data: Dict[str, Any]) -> Dict[str, Any]:
            return data.copy()
        
        # Add default values migration
        def add_defaults_migration(data: Dict[str, Any]) -> Dict[str, Any]:
            # This would be customized based on specific schema changes
            return data.copy()
        
        # Remove fields migration
        def remove_fields_migration(data: Dict[str, Any]) -> Dict[str, Any]:
            # This would be customized based on specific schema changes
            return data.copy()
        
        # Register migrations
        self.migrator.register_migration("1.0.0", "1.0.1", identity_migration)
        self.migrator.register_migration("1.0.0", "1.1.0", add_defaults_migration)
    
    async def register_schema_version(self, schema: EventSchema) -> bool:
        """Register new schema version"""
        try:
            # Check if this is a new version
            existing_schemas = await self.schema_registry.list_schemas(schema.event_type)
            
            if existing_schemas:
                # Compare with latest version
                latest_schema = max(existing_schemas, key=lambda s: s.version)
                
                if schema.version <= latest_schema.version:
                    logger.error(f"New version {schema.version} must be greater than latest {latest_schema.version}")
                    return False
                
                # Analyze changes
                changes = self.comparator.compare_schemas(latest_schema, schema)
                compatibility = self.comparator.determine_compatibility(changes)
                
                # Determine version type based on changes
                version_type = self._determine_version_type(latest_schema.version, schema.version, compatibility)
                
                logger.info(f"Schema version {schema.version} registered with {len(changes)} changes, compatibility: {compatibility.value}")
            
            # Register schema
            success = await self.schema_registry.register_schema(schema)
            
            if success:
                logger.info(f"Successfully registered schema {schema.event_type} v{schema.version}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to register schema version: {e}")
            return False
    
    async def migrate_event_to_version(self, event: DomainEvent, 
                                     target_version: SemanticVersion) -> Optional[DomainEvent]:
        """Migrate event to specific version"""
        try:
            # Get current schema
            current_schema = await self.schema_registry.get_latest_schema(event.event_type)
            if not current_schema:
                logger.error(f"No schema found for event type {event.event_type}")
                return None
            
            # Get target schema
            target_schema = await self.schema_registry.get_schema(event.event_type, target_version)
            if not target_schema:
                logger.error(f"Target schema version {target_version} not found")
                return None
            
            # If versions are the same, return original event
            if current_schema.version == target_version:
                return event
            
            # Migrate event
            migrated_event = await self.migrator.migrate_event(
                event, current_schema.version, target_version
            )
            
            if migrated_event:
                # Validate migrated event
                if await self.validator.validate_event(migrated_event, target_version):
                    return migrated_event
                else:
                    logger.error("Migrated event failed validation")
            
            return None
            
        except Exception as e:
            logger.error(f"Event migration failed: {e}")
            return None
    
    async def get_compatible_versions(self, event_type: str, 
                                    version: SemanticVersion) -> List[SemanticVersion]:
        """Get list of compatible versions for given version"""
        try:
            schemas = await self.schema_registry.list_schemas(event_type)
            compatible_versions = []
            
            base_schema = None
            for schema in schemas:
                if schema.version == version:
                    base_schema = schema
                    break
            
            if not base_schema:
                return []
            
            for schema in schemas:
                if schema.version == version:
                    continue
                
                changes = self.comparator.compare_schemas(base_schema, schema)
                compatibility = self.comparator.determine_compatibility(changes)
                
                if compatibility in [CompatibilityLevel.FULL, CompatibilityLevel.BACKWARD, CompatibilityLevel.FORWARD]:
                    compatible_versions.append(schema.version)
            
            return sorted(compatible_versions)
            
        except Exception as e:
            logger.error(f"Failed to get compatible versions: {e}")
            return []
    
    async def deprecate_version(self, event_type: str, version: SemanticVersion,
                              replacement_version: SemanticVersion = None,
                              deprecation_period_days: int = 90) -> bool:
        """Deprecate a schema version"""
        try:
            success = await self.schema_registry.deprecate_schema(
                event_type, version, replacement_version
            )
            
            if success:
                logger.info(f"Deprecated {event_type} v{version}, replacement: {replacement_version}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to deprecate version: {e}")
            return False
    
    async def get_migration_path(self, event_type: str, 
                               from_version: SemanticVersion,
                               to_version: SemanticVersion) -> List[SemanticVersion]:
        """Get migration path between versions"""
        try:
            schemas = await self.schema_registry.list_schemas(event_type)
            version_map = {schema.version: schema for schema in schemas}
            
            if from_version not in version_map or to_version not in version_map:
                return []
            
            # For simplicity, return direct path if available
            # In a real implementation, this would use graph algorithms
            # to find the optimal migration path
            if from_version < to_version:
                # Forward migration
                intermediate_versions = [
                    v for v in version_map.keys() 
                    if from_version < v <= to_version
                ]
                return sorted(intermediate_versions)
            else:
                # Backward migration
                intermediate_versions = [
                    v for v in version_map.keys() 
                    if to_version <= v < from_version
                ]
                return sorted(intermediate_versions, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to get migration path: {e}")
            return []
    
    def _determine_version_type(self, old_version: SemanticVersion, 
                              new_version: SemanticVersion,
                              compatibility: CompatibilityLevel) -> VersionType:
        """Determine version type based on changes"""
        if compatibility == CompatibilityLevel.BREAKING:
            return VersionType.MAJOR
        
        if new_version.major > old_version.major:
            return VersionType.MAJOR
        elif new_version.minor > old_version.minor:
            return VersionType.MINOR
        elif new_version.patch > old_version.patch:
            return VersionType.PATCH
        else:
            return VersionType.HOTFIX
    
    async def get_version_statistics(self, event_type: str) -> Dict[str, Any]:
        """Get version usage statistics"""
        try:
            schemas = await self.schema_registry.list_schemas(event_type)
            
            stats = {
                "total_versions": len(schemas),
                "latest_version": str(max(schemas, key=lambda s: s.version).version) if schemas else None,
                "deprecated_versions": [],
                "breaking_changes_count": 0,
                "version_timeline": []
            }
            
            for schema in sorted(schemas, key=lambda s: s.version):
                stats["version_timeline"].append({
                    "version": str(schema.version),
                    "created_at": schema.created_at.isoformat(),
                    "created_by": schema.created_by
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get version statistics: {e}")
            return {}
    
    async def health_check(self) -> bool:
        """Check versioning engine health"""
        try:
            # Check if schema registry is accessible
            test_schemas = await self.schema_registry.list_schemas("_health_check")
            return True
        except Exception as e:
            logger.error(f"Versioning engine health check failed: {e}")
            return False