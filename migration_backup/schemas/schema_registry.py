"""IA Influencer Agent Platform - Schema Registry Module
Centralized schema registry for validation, versioning, and management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides a centralized registry for all schemas with:
- Schema versioning and compatibility checking
- Dynamic schema discovery and registration
- Validation pipeline management
- Schema metadata and documentation
"""

from typing import Dict, List, Optional, Type, Any, Union, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import inspect
from pydantic import BaseModel, Field, validator
from .base import BaseSchema, UUIDSchema, TimestampSchema, AuditSchema


class SchemaType(str, Enum):
    """Schema type classifications."""
    CORE = "core"
    BUSINESS = "business"
    INTEGRATION = "integration"
    INTERNAL = "internal"
    DEPRECATED = "deprecated"


class CompatibilityLevel(str, Enum):
    """Schema compatibility levels."""
    FULL = "full"          # Fully compatible
    BACKWARD = "backward"  # Backward compatible
    FORWARD = "forward"    # Forward compatible
    BREAKING = "breaking"  # Breaking changes
    NONE = "none"         # No compatibility


class ValidationMode(str, Enum):
    """Schema validation modes."""
    STRICT = "strict"      # All validations must pass
    PERMISSIVE = "permissive"  # Allow some validation failures
    DEVELOPMENT = "development"  # Relaxed validation for dev
    PRODUCTION = "production"    # Enhanced validation for prod


@dataclass
class SchemaInfo:
    """Schema information metadata."""
    name: str
    version: str
    schema_type: SchemaType
    description: str
    created_at: datetime
    updated_at: datetime
    author: str
    deprecated: bool = False
    replacement: Optional[str] = None
    tags: Set[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = set()


class SchemaRegistration(BaseSchema):
    """Schema registration request."""
    
    name: str = Field(..., description="Unique schema name")
    version: str = Field(..., pattern="^\\d+\\.\\d+\\.\\d+$", description="Semantic version")
    schema_type: SchemaType = Field(..., description="Schema classification")
    description: str = Field(..., min_length=10, description="Schema description")
    author: str = Field(..., description="Schema author")
    tags: List[str] = Field(default=[], description="Schema tags")
    schema_class: str = Field(..., description="Fully qualified schema class name")
    dependencies: List[str] = Field(default=[], description="Schema dependencies")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate schema name format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Schema name must be alphanumeric with underscores/hyphens')
        return v.lower()


class SchemaCompatibilityCheck(UUIDSchema, TimestampSchema):
    """Schema compatibility check result."""
    
    source_schema: str = Field(..., description="Source schema name")
    source_version: str = Field(..., description="Source schema version")
    target_schema: str = Field(..., description="Target schema name")
    target_version: str = Field(..., description="Target schema version")
    compatibility_level: CompatibilityLevel = Field(..., description="Compatibility assessment")
    issues: List[str] = Field(default=[], description="Compatibility issues found")
    recommendations: List[str] = Field(default=[], description="Upgrade recommendations")
    automated_migration: bool = Field(False, description="Can be migrated automatically")


class SchemaValidationRule(UUIDSchema, TimestampSchema):
    """Custom validation rule for schemas."""
    
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    schema_pattern: str = Field(..., description="Schema name pattern (regex)")
    validation_function: str = Field(..., description="Validation function reference")
    severity: str = Field("error", pattern="^(error|warning|info)$", description="Rule severity")
    enabled: bool = Field(True, description="Rule enabled status")
    parameters: Dict[str, Any] = Field(default={}, description="Rule parameters")


class SchemaDiscovery(BaseSchema):
    """Schema discovery configuration."""
    
    auto_discover: bool = Field(True, description="Enable automatic schema discovery")
    discovery_paths: List[str] = Field(default=[], description="Paths to scan for schemas")
    exclude_patterns: List[str] = Field(default=[], description="Patterns to exclude")
    refresh_interval: int = Field(300, ge=60, description="Discovery refresh interval (seconds)")
    validate_on_discovery: bool = Field(True, description="Validate schemas on discovery")


class SchemaRegistry:
    """Centralized schema registry for the Ainflue platform."""
    
    def __init__(self):
        self._schemas: Dict[str, Dict[str, SchemaInfo]] = {}
        self._classes: Dict[str, Type[BaseModel]] = {}
        self._validation_rules: List[SchemaValidationRule] = []
        self._discovery_config = SchemaDiscovery()
        self._compatibility_cache: Dict[str, SchemaCompatibilityCheck] = {}
    
    def register_schema(
        self,
        name: str,
        schema_class: Type[BaseModel],
        version: str = "1.0.0",
        schema_type: SchemaType = SchemaType.BUSINESS,
        description: str = "",
        author: str = "Fahed Mlaiel",
        tags: List[str] = None
    ) -> bool:
        """Register a schema in the registry."""
        try:
            if tags is None:
                tags = []
            
            # Create schema info
            schema_info = SchemaInfo(
                name=name,
                version=version,
                schema_type=schema_type,
                description=description or f"Schema for {name}",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                author=author,
                tags=set(tags)
            )
            
            # Store schema
            if name not in self._schemas:
                self._schemas[name] = {}
            
            self._schemas[name][version] = schema_info
            self._classes[f"{name}:{version}"] = schema_class
            
            return True
            
        except Exception as e:
            raise ValueError(f"Failed to register schema {name}: {str(e)}")
    
    def get_schema(self, name: str, version: str = None) -> Optional[Type[BaseModel]]:
        """Get a schema class by name and version."""
        if name not in self._schemas:
            return None
        
        if version is None:
            # Get latest version
            versions = sorted(self._schemas[name].keys(), reverse=True)
            version = versions[0] if versions else None
        
        if version and version in self._schemas[name]:
            return self._classes.get(f"{name}:{version}")
        
        return None
    
    def list_schemas(
        self,
        schema_type: Optional[SchemaType] = None,
        tags: Optional[List[str]] = None,
        deprecated: bool = False
    ) -> List[SchemaInfo]:
        """List schemas matching criteria."""
        result = []
        
        for schema_versions in self._schemas.values():
            for schema_info in schema_versions.values():
                # Filter by type
                if schema_type and schema_info.schema_type != schema_type:
                    continue
                
                # Filter by deprecated status
                if schema_info.deprecated != deprecated and deprecated is not None:
                    continue
                
                # Filter by tags
                if tags:
                    if not any(tag in schema_info.tags for tag in tags):
                        continue
                
                result.append(schema_info)
        
        return sorted(result, key=lambda x: (x.name, x.version))
    
    def check_compatibility(
        self,
        source_name: str,
        source_version: str,
        target_name: str,
        target_version: str
    ) -> SchemaCompatibilityCheck:
        """Check compatibility between two schemas."""
        cache_key = f"{source_name}:{source_version}->{target_name}:{target_version}"
        
        if cache_key in self._compatibility_cache:
            return self._compatibility_cache[cache_key]
        
        # Get schemas
        source_schema = self.get_schema(source_name, source_version)
        target_schema = self.get_schema(target_name, target_version)
        
        if not source_schema or not target_schema:
            compatibility = CompatibilityLevel.NONE
            issues = ["One or both schemas not found"]
        else:
            compatibility, issues = self._analyze_compatibility(source_schema, target_schema)
        
        result = SchemaCompatibilityCheck(
            source_schema=source_name,
            source_version=source_version,
            target_schema=target_name,
            target_version=target_version,
            compatibility_level=compatibility,
            issues=issues,
            recommendations=self._generate_recommendations(compatibility, issues)
        )
        
        self._compatibility_cache[cache_key] = result
        return result
    
    def _analyze_compatibility(
        self,
        source_schema: Type[BaseModel],
        target_schema: Type[BaseModel]
    ) -> tuple[CompatibilityLevel, List[str]]:
        """Analyze compatibility between two schema classes."""
        issues = []
        
        # Get field information
        source_fields = source_schema.__fields__ if hasattr(source_schema, '__fields__') else {}
        target_fields = target_schema.__fields__ if hasattr(target_schema, '__fields__') else {}
        
        # Check for removed fields
        removed_fields = set(source_fields.keys()) - set(target_fields.keys())
        if removed_fields:
            issues.append(f"Removed fields: {', '.join(removed_fields)}")
        
        # Check for new required fields
        new_required = []
        for field_name, field_info in target_fields.items():
            if field_name not in source_fields:
                if hasattr(field_info, 'default') and field_info.default is ...:
                    new_required.append(field_name)
        
        if new_required:
            issues.append(f"New required fields: {', '.join(new_required)}")
        
        # Determine compatibility level
        if not issues:
            return CompatibilityLevel.FULL, issues
        elif removed_fields or new_required:
            return CompatibilityLevel.BREAKING, issues
        else:
            return CompatibilityLevel.BACKWARD, issues
    
    def _generate_recommendations(
        self,
        compatibility: CompatibilityLevel,
        issues: List[str]
    ) -> List[str]:
        """Generate upgrade recommendations based on compatibility analysis."""
        recommendations = []
        
        if compatibility == CompatibilityLevel.BREAKING:
            recommendations.append("Review breaking changes before upgrading")
            recommendations.append("Consider gradual migration strategy")
            recommendations.append("Update client code to handle changes")
        
        elif compatibility == CompatibilityLevel.BACKWARD:
            recommendations.append("Safe to upgrade with backward compatibility")
            recommendations.append("Test thoroughly before production deployment")
        
        elif compatibility == CompatibilityLevel.FULL:
            recommendations.append("Safe to upgrade with full compatibility")
        
        return recommendations
    
    def validate_schema(self, schema_name: str, data: Dict[str, Any]) -> List[str]:
        """Validate data against a registered schema."""
        schema_class = self.get_schema(schema_name)
        if not schema_class:
            return [f"Schema {schema_name} not found"]
        
        try:
            schema_class(**data)
            return []
        except Exception as e:
            return [str(e)]
    
    def auto_discover_schemas(self) -> int:
        """Automatically discover and register schemas from configured paths."""
        discovered_count = 0
        
        if not self._discovery_config.auto_discover:
            return discovered_count
        
        # Implementation for auto-discovery would go here
        # This would scan the configured paths and register found schemas
        
        return discovered_count


# Global registry instance
schema_registry = SchemaRegistry()


class SchemaRegistryManager(UUIDSchema, TimestampSchema, AuditSchema):
    """Schema registry management interface."""
    
    name: str = Field(..., description="Registry name")
    description: str = Field(..., description="Registry description")
    version: str = Field("1.0.0", description="Registry version")
    schemas_count: int = Field(0, ge=0, description="Number of registered schemas")
    validation_mode: ValidationMode = Field(ValidationMode.PRODUCTION, description="Validation mode")
    discovery_config: SchemaDiscovery = Field(default_factory=SchemaDiscovery)
    health_status: str = Field("healthy", description="Registry health status")
    last_discovery: Optional[datetime] = Field(None, description="Last discovery run")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SchemaMetrics(UUIDSchema, TimestampSchema):
    """Schema registry metrics and statistics."""
    
    total_schemas: int = Field(0, ge=0, description="Total number of schemas")
    active_schemas: int = Field(0, ge=0, description="Active schemas count")
    deprecated_schemas: int = Field(0, ge=0, description="Deprecated schemas count")
    validation_requests: int = Field(0, ge=0, description="Validation requests count")
    validation_failures: int = Field(0, ge=0, description="Validation failures count")
    compatibility_checks: int = Field(0, ge=0, description="Compatibility checks count")
    discovery_runs: int = Field(0, ge=0, description="Discovery runs count")
    average_validation_time: float = Field(0.0, ge=0, description="Average validation time (ms)")
    
    @property
    def validation_success_rate(self) -> float:
        """Calculate validation success rate."""
        if self.validation_requests == 0:
            return 100.0
        return ((self.validation_requests - self.validation_failures) / self.validation_requests) * 100