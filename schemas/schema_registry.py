"""
🗄️ Centralized Schema Registry for Ainflue Platform
Enterprise-grade schema management and discovery system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.

🎯 DBA Expert Role: Advanced database schema management and registry
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Type
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator
import hashlib
import json
from pathlib import Path

from .base import BaseSchema, TimestampSchema, UUIDSchema


class SchemaStatus(str, Enum):
    """Schema lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    MIGRATING = "migrating"


class SchemaCategory(str, Enum):
    """Schema categorization for organization"""
    CORE = "core"
    USER = "user"
    CONTENT = "content"
    AI_ML = "ai_ml"
    PROTECTION = "protection"
    SEO = "seo"
    COLLABORATION = "collaboration"
    DISTRIBUTION = "distribution"
    REVENUE = "revenue"
    ANALYTICS = "analytics"
    INFRASTRUCTURE = "infrastructure"
    BLOCKCHAIN = "blockchain"
    ADVANCED = "advanced"
    ADMIN = "admin"


class SchemaVersion(BaseSchema):
    """Schema version information"""
    major: int = Field(ge=0, description="Major version number")
    minor: int = Field(ge=0, description="Minor version number")
    patch: int = Field(ge=0, description="Patch version number")
    pre_release: Optional[str] = Field(None, description="Pre-release identifier")
    build_metadata: Optional[str] = Field(None, description="Build metadata")
    
    @property
    def version_string(self) -> str:
        """Get semantic version string"""
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            version += f"-{self.pre_release}"
        if self.build_metadata:
            version += f"+{self.build_metadata}"
        return version
    
    def __str__(self) -> str:
        return self.version_string
    
    def __lt__(self, other: "SchemaVersion") -> bool:
        """Compare versions for sorting"""
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)


class SchemaDependency(BaseSchema):
    """Schema dependency definition"""
    schema_name: str = Field(description="Name of dependent schema")
    version_constraint: str = Field(description="Version constraint (e.g., >=1.0.0, <2.0.0)")
    is_optional: bool = Field(default=False, description="Whether dependency is optional")
    description: str = Field(description="Dependency description")


class SchemaMetadata(UUIDSchema, TimestampSchema):
    """Comprehensive schema metadata"""
    name: str = Field(description="Schema name identifier")
    display_name: str = Field(description="Human-readable schema name")
    description: str = Field(description="Schema description and purpose")
    category: SchemaCategory = Field(description="Schema category")
    version: SchemaVersion = Field(description="Schema version")
    status: SchemaStatus = Field(description="Schema lifecycle status")
    
    # Schema content
    schema_content: Dict[str, Any] = Field(description="JSON schema definition")
    schema_hash: str = Field(description="SHA-256 hash of schema content")
    
    # Dependencies
    dependencies: List[SchemaDependency] = Field(default_factory=list)
    dependents: List[str] = Field(default_factory=list, description="Schemas that depend on this one")
    
    # Authoring information
    author: str = Field(description="Schema author")
    maintainer: str = Field(description="Current maintainer")
    contributors: List[str] = Field(default_factory=list)
    
    # Lifecycle management
    deprecated_since: Optional[datetime] = Field(None, description="Deprecation timestamp")
    archived_since: Optional[datetime] = Field(None, description="Archive timestamp")
    migration_path: Optional[str] = Field(None, description="Migration instructions")
    
    # Usage tracking
    usage_count: int = Field(default=0, ge=0, description="Number of times schema is used")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    
    # Documentation
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")
    tags: List[str] = Field(default_factory=list, description="Schema tags for discovery")
    
    @validator('schema_hash', always=True)
    def generate_schema_hash(cls, v, values):
        """Generate hash of schema content"""
        if 'schema_content' in values:
            content_str = json.dumps(values['schema_content'], sort_keys=True)
            return hashlib.sha256(content_str.encode()).hexdigest()
        return v


class SchemaSearchQuery(BaseSchema):
    """Schema search and discovery query"""
    query: Optional[str] = Field(None, description="Text search query")
    category: Optional[SchemaCategory] = Field(None, description="Filter by category")
    status: Optional[SchemaStatus] = Field(None, description="Filter by status")
    tags: List[str] = Field(default_factory=list, description="Filter by tags")
    author: Optional[str] = Field(None, description="Filter by author")
    version_constraint: Optional[str] = Field(None, description="Version constraint filter")
    dependencies: List[str] = Field(default_factory=list, description="Filter by dependencies")
    sort_by: str = Field(default="name", description="Sort field")
    sort_order: str = Field(default="asc", description="Sort order")
    include_deprecated: bool = Field(default=False, description="Include deprecated schemas")


class SchemaCompatibility(BaseSchema):
    """Schema compatibility analysis result"""
    source_schema: str = Field(description="Source schema name")
    target_schema: str = Field(description="Target schema name")
    source_version: SchemaVersion = Field(description="Source version")
    target_version: SchemaVersion = Field(description="Target version")
    is_compatible: bool = Field(description="Whether schemas are compatible")
    compatibility_level: str = Field(description="Compatibility level (forward/backward/full)")
    breaking_changes: List[str] = Field(default_factory=list, description="List of breaking changes")
    warnings: List[str] = Field(default_factory=list, description="Compatibility warnings")
    migration_required: bool = Field(description="Whether migration is required")
    migration_complexity: str = Field(description="Migration complexity level")


class SchemaRegistry:
    """
    Enterprise-grade centralized schema registry
    Provides schema discovery, versioning, and dependency management
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("./schema_registry")
        self.schemas: Dict[str, List[SchemaMetadata]] = {}
        self.schema_cache: Dict[str, SchemaMetadata] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize registry storage"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._load_schemas()
    
    def _load_schemas(self):
        """Load schemas from storage"""
        for schema_file in self.storage_path.glob("*.json"):
            try:
                with open(schema_file, 'r') as f:
                    schema_data = json.load(f)
                    schema = SchemaMetadata(**schema_data)
                    self._add_schema_to_registry(schema)
            except Exception as e:
                print(f"Error loading schema {schema_file}: {e}")
    
    def _add_schema_to_registry(self, schema: SchemaMetadata):
        """Add schema to in-memory registry"""
        if schema.name not in self.schemas:
            self.schemas[schema.name] = []
        
        self.schemas[schema.name].append(schema)
        self.schemas[schema.name].sort(key=lambda s: s.version, reverse=True)
        
        # Update cache with latest version
        self.schema_cache[schema.name] = self.schemas[schema.name][0]
        
        # Update dependency graph
        self._update_dependency_graph(schema)
    
    def _update_dependency_graph(self, schema: SchemaMetadata):
        """Update dependency graph"""
        if schema.name not in self.dependency_graph:
            self.dependency_graph[schema.name] = set()
        
        for dep in schema.dependencies:
            self.dependency_graph[schema.name].add(dep.schema_name)
    
    def register_schema(self, schema_metadata: SchemaMetadata) -> bool:
        """
        Register a new schema or version
        Returns True if successfully registered
        """
        try:
            # Validate schema content
            self._validate_schema_content(schema_metadata)
            
            # Check for conflicts
            if self._has_version_conflict(schema_metadata):
                raise ValueError(f"Version conflict for schema {schema_metadata.name}")
            
            # Validate dependencies
            self._validate_dependencies(schema_metadata)
            
            # Add to registry
            self._add_schema_to_registry(schema_metadata)
            
            # Persist to storage
            self._persist_schema(schema_metadata)
            
            return True
            
        except Exception as e:
            print(f"Error registering schema: {e}")
            return False
    
    def _validate_schema_content(self, schema: SchemaMetadata):
        """Validate schema content structure"""
        required_fields = ["type", "properties"]
        if not all(field in schema.schema_content for field in required_fields):
            raise ValueError("Schema content must include 'type' and 'properties'")
    
    def _has_version_conflict(self, schema: SchemaMetadata) -> bool:
        """Check for version conflicts"""
        if schema.name in self.schemas:
            existing_versions = [s.version for s in self.schemas[schema.name]]
            return schema.version in existing_versions
        return False
    
    def _validate_dependencies(self, schema: SchemaMetadata):
        """Validate schema dependencies exist"""
        for dep in schema.dependencies:
            if not self.schema_exists(dep.schema_name):
                if not dep.is_optional:
                    raise ValueError(f"Required dependency '{dep.schema_name}' not found")
    
    def _persist_schema(self, schema: SchemaMetadata):
        """Persist schema to storage"""
        filename = f"{schema.name}_v{schema.version.version_string}.json"
        filepath = self.storage_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(schema.dict(), f, indent=2, default=str)
    
    def get_schema(self, name: str, version: Optional[str] = None) -> Optional[SchemaMetadata]:
        """Get schema by name and optional version"""
        if name not in self.schemas:
            return None
        
        if version is None:
            return self.schema_cache.get(name)
        
        for schema in self.schemas[name]:
            if schema.version.version_string == version:
                return schema
        
        return None
    
    def search_schemas(self, query: SchemaSearchQuery) -> List[SchemaMetadata]:
        """Search schemas based on query criteria"""
        results = []
        
        for schema_list in self.schemas.values():
            for schema in schema_list:
                if self._matches_query(schema, query):
                    results.append(schema)
        
        # Sort results
        results.sort(key=lambda s: getattr(s, query.sort_by, ""), 
                    reverse=(query.sort_order == "desc"))
        
        return results
    
    def _matches_query(self, schema: SchemaMetadata, query: SchemaSearchQuery) -> bool:
        """Check if schema matches search query"""
        # Text search
        if query.query:
            text_fields = [schema.name, schema.display_name, schema.description]
            text_content = " ".join(text_fields).lower()
            if query.query.lower() not in text_content:
                return False
        
        # Category filter
        if query.category and schema.category != query.category:
            return False
        
        # Status filter
        if query.status and schema.status != query.status:
            return False
        
        # Include deprecated check
        if not query.include_deprecated and schema.status == SchemaStatus.DEPRECATED:
            return False
        
        # Tags filter
        if query.tags and not any(tag in schema.tags for tag in query.tags):
            return False
        
        # Author filter
        if query.author and schema.author != query.author:
            return False
        
        return True
    
    def get_schema_dependencies(self, schema_name: str) -> List[str]:
        """Get all dependencies for a schema"""
        return list(self.dependency_graph.get(schema_name, set()))
    
    def get_schema_dependents(self, schema_name: str) -> List[str]:
        """Get all schemas that depend on this schema"""
        dependents = []
        for name, deps in self.dependency_graph.items():
            if schema_name in deps:
                dependents.append(name)
        return dependents
    
    def schema_exists(self, name: str, version: Optional[str] = None) -> bool:
        """Check if schema exists"""
        return self.get_schema(name, version) is not None
    
    def list_schema_versions(self, name: str) -> List[SchemaVersion]:
        """List all versions of a schema"""
        if name not in self.schemas:
            return []
        return [schema.version for schema in self.schemas[name]]
    
    def deprecate_schema(self, name: str, version: Optional[str] = None, 
                        migration_path: Optional[str] = None) -> bool:
        """Deprecate a schema version"""
        schema = self.get_schema(name, version)
        if not schema:
            return False
        
        schema.status = SchemaStatus.DEPRECATED
        schema.deprecated_since = datetime.utcnow()
        if migration_path:
            schema.migration_path = migration_path
        
        self._persist_schema(schema)
        return True
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        total_schemas = sum(len(versions) for versions in self.schemas.values())
        active_schemas = sum(1 for schema_list in self.schemas.values() 
                           for schema in schema_list if schema.status == SchemaStatus.ACTIVE)
        
        category_distribution = {}
        for schema_list in self.schemas.values():
            for schema in schema_list:
                cat = schema.category.value
                category_distribution[cat] = category_distribution.get(cat, 0) + 1
        
        return {
            "total_schemas": total_schemas,
            "unique_schemas": len(self.schemas),
            "active_schemas": active_schemas,
            "deprecated_schemas": total_schemas - active_schemas,
            "category_distribution": category_distribution,
            "dependency_count": sum(len(deps) for deps in self.dependency_graph.values())
        }


# Global registry instance
_global_registry: Optional[SchemaRegistry] = None


def get_schema_registry() -> SchemaRegistry:
    """Get global schema registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = SchemaRegistry()
    return _global_registry


def register_schema(schema_metadata: SchemaMetadata) -> bool:
    """Register schema in global registry"""
    return get_schema_registry().register_schema(schema_metadata)


def get_schema(name: str, version: Optional[str] = None) -> Optional[SchemaMetadata]:
    """Get schema from global registry"""
    return get_schema_registry().get_schema(name, version)


# Export all classes and functions
__all__ = [
    'SchemaStatus',
    'SchemaCategory', 
    'SchemaVersion',
    'SchemaDependency',
    'SchemaMetadata',
    'SchemaSearchQuery',
    'SchemaCompatibility',
    'SchemaRegistry',
    'get_schema_registry',
    'register_schema',
    'get_schema'
]