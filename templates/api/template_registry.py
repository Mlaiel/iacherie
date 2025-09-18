"""
🔒 API TEMPLATE REGISTRY - ENTERPRISE TEMPLATE MANAGEMENT
=========================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Central registry for managing API templates in the Ainflue platform.
Provides template discovery, validation, and management capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Type, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging
import inspect
from datetime import datetime
import json
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Template types supported by the registry."""
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    GRPC = "grpc" 
    WEBSOCKET = "websocket"
    AUTHENTICATION = "authentication"
    SECURITY_MIDDLEWARE = "security_middleware"
    DOCUMENTATION = "documentation"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    CREATOR_ECONOMY = "creator_economy"
    MOBILE = "mobile"
    MULTI_PLATFORM = "multi_platform"
    DATABASE = "database"
    ASYNC_PROCESSING = "async_processing"
    TESTING = "testing"
    LOCALIZATION = "localization"
    AI_INTEGRATION = "ai_integration"


class TemplateCategory(Enum):
    """Template categories for organization."""
    CORE = "core"
    ADVANCED = "advanced"
    SECURITY = "security"
    INTEGRATION = "integration"
    SPECIALIZED = "specialized"
    INFRASTRUCTURE = "infrastructure"


class SecurityLevel(Enum):
    """Security levels for templates."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    AUTHORIZED = "authorized"
    ENTERPRISE = "enterprise"
    RESTRICTED = "restricted"


@dataclass
class TemplateMetadata:
    """Metadata for API templates."""
    name: str
    template_type: TemplateType
    category: TemplateCategory
    version: str
    author: str
    description: str
    security_level: SecurityLevel = SecurityLevel.AUTHENTICATED
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    file_path: Optional[str] = None
    documentation_url: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    performance_notes: str = ""
    security_notes: str = ""
    compliance_standards: List[str] = field(default_factory=list)
    enterprise_features: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "name": self.name,
            "template_type": self.template_type.value,
            "category": self.category.value,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "security_level": self.security_level.value,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "file_path": self.file_path,
            "documentation_url": self.documentation_url,
            "examples": self.examples,
            "performance_notes": self.performance_notes,
            "security_notes": self.security_notes,
            "compliance_standards": self.compliance_standards,
            "enterprise_features": self.enterprise_features
        }


class TemplateInterface(ABC):
    """Base interface for all API templates."""
    
    @property
    @abstractmethod
    def metadata(self) -> TemplateMetadata:
        """Return template metadata."""
        pass
    
    @abstractmethod
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate template code based on configuration."""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate template configuration."""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for template configuration."""
        return {}
    
    def get_examples(self) -> List[Dict[str, Any]]:
        """Return example configurations."""
        return []


@dataclass
class TemplateRegistration:
    """Registration information for a template."""
    template_class: Type[TemplateInterface]
    metadata: TemplateMetadata
    instance: Optional[TemplateInterface] = None
    checksum: str = ""
    registration_time: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate checksum after initialization."""
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate template checksum for integrity verification."""
        content = f"{self.template_class.__name__}{self.metadata.version}{self.metadata.author}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class APITemplateRegistry:
    """Central registry for API templates."""
    
    def __init__(self):
        self._templates: Dict[str, TemplateRegistration] = {}
        self._categories: Dict[TemplateCategory, Set[str]] = {
            category: set() for category in TemplateCategory
        }
        self._types: Dict[TemplateType, Set[str]] = {
            template_type: set() for template_type in TemplateType
        }
        self._tags: Dict[str, Set[str]] = {}
        self._security_levels: Dict[SecurityLevel, Set[str]] = {
            level: set() for level in SecurityLevel
        }
        self._dependencies: Dict[str, Set[str]] = {}
        
        logger.info("API Template Registry initialized")
    
    def register_template(
        self,
        template_class: Type[TemplateInterface],
        metadata: Optional[TemplateMetadata] = None
    ) -> bool:
        """Register a new template."""
        try:
            # Get metadata from class if not provided
            if metadata is None:
                if hasattr(template_class, 'metadata'):
                    metadata = template_class.metadata
                else:
                    raise ValueError(f"Template {template_class.__name__} must provide metadata")
            
            # Validate template class
            if not issubclass(template_class, TemplateInterface):
                raise ValueError(f"Template {template_class.__name__} must implement TemplateInterface")
            
            # Check for existing registration
            if metadata.name in self._templates:
                existing = self._templates[metadata.name]
                if existing.metadata.version == metadata.version:
                    logger.warning(f"Template {metadata.name} v{metadata.version} already registered")
                    return False
            
            # Create registration
            registration = TemplateRegistration(
                template_class=template_class,
                metadata=metadata
            )
            
            # Store in registry
            self._templates[metadata.name] = registration
            
            # Update indices
            self._categories[metadata.category].add(metadata.name)
            self._types[metadata.template_type].add(metadata.name)
            self._security_levels[metadata.security_level].add(metadata.name)
            
            # Index tags
            for tag in metadata.tags:
                if tag not in self._tags:
                    self._tags[tag] = set()
                self._tags[tag].add(metadata.name)
            
            # Index dependencies
            for dep in metadata.dependencies:
                if dep not in self._dependencies:
                    self._dependencies[dep] = set()
                self._dependencies[dep].add(metadata.name)
            
            logger.info(f"Template {metadata.name} v{metadata.version} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register template {template_class.__name__}: {e}")
            return False
    
    def get_template(self, name: str) -> Optional[TemplateInterface]:
        """Get template instance by name."""
        if name not in self._templates:
            return None
        
        registration = self._templates[name]
        
        # Create instance if not cached
        if registration.instance is None:
            try:
                registration.instance = registration.template_class()
            except Exception as e:
                logger.error(f"Failed to instantiate template {name}: {e}")
                return None
        
        return registration.instance
    
    def has_template(self, name: str) -> bool:
        """Check if template exists in registry."""
        return name in self._templates
    
    def list_templates(
        self,
        category: Optional[TemplateCategory] = None,
        template_type: Optional[TemplateType] = None,
        security_level: Optional[SecurityLevel] = None,
        tags: Optional[List[str]] = None
    ) -> List[TemplateMetadata]:
        """List templates with optional filtering."""
        templates = []
        
        # Get candidate template names
        candidates = set(self._templates.keys())
        
        # Apply filters
        if category:
            candidates &= self._categories[category]
        
        if template_type:
            candidates &= self._types[template_type]
        
        if security_level:
            candidates &= self._security_levels[security_level]
        
        if tags:
            for tag in tags:
                if tag in self._tags:
                    candidates &= self._tags[tag]
                else:
                    candidates = set()  # Tag not found, no matches
                    break
        
        # Collect metadata for matching templates
        for name in candidates:
            templates.append(self._templates[name].metadata)
        
        # Sort by name
        templates.sort(key=lambda t: t.name)
        
        return templates
    
    def get_templates_by_category(self, category: TemplateCategory) -> List[str]:
        """Get template names by category."""
        return list(self._categories[category])
    
    def get_templates_by_type(self, template_type: TemplateType) -> List[str]:
        """Get template names by type."""
        return list(self._types[template_type])
    
    def get_templates_by_tag(self, tag: str) -> List[str]:
        """Get template names by tag."""
        return list(self._tags.get(tag, set()))
    
    def get_template_dependencies(self, name: str) -> List[str]:
        """Get dependencies for a template."""
        if name not in self._templates:
            return []
        return self._templates[name].metadata.dependencies.copy()
    
    def get_dependent_templates(self, dependency: str) -> List[str]:
        """Get templates that depend on a given dependency."""
        return list(self._dependencies.get(dependency, set()))
    
    def validate_template(self, name: str) -> Dict[str, Any]:
        """Validate template integrity and compliance."""
        if name not in self._templates:
            return {"valid": False, "error": "Template not found"}
        
        registration = self._templates[name]
        validation_result = {
            "valid": True,
            "template_name": name,
            "version": registration.metadata.version,
            "checksum": registration.checksum,
            "security_level": registration.metadata.security_level.value,
            "compliance_standards": registration.metadata.compliance_standards,
            "warnings": [],
            "errors": []
        }
        
        try:
            # Validate template class
            if not issubclass(registration.template_class, TemplateInterface):
                validation_result["errors"].append("Template does not implement TemplateInterface")
            
            # Validate metadata
            metadata = registration.metadata
            if not metadata.author:
                validation_result["warnings"].append("No author specified")
            
            if not metadata.description:
                validation_result["warnings"].append("No description provided")
            
            if not metadata.version:
                validation_result["errors"].append("No version specified")
            
            # Check dependencies
            missing_deps = []
            for dep in metadata.dependencies:
                if dep not in self._templates:
                    missing_deps.append(dep)
            
            if missing_deps:
                validation_result["warnings"].append(f"Missing dependencies: {missing_deps}")
            
            # Validate instance creation
            try:
                instance = self.get_template(name)
                if instance is None:
                    validation_result["errors"].append("Failed to create template instance")
                else:
                    # Test basic functionality
                    try:
                        instance.get_schema()
                        instance.get_examples()
                    except Exception as e:
                        validation_result["warnings"].append(f"Template methods error: {e}")
            except Exception as e:
                validation_result["errors"].append(f"Instance creation failed: {e}")
            
            validation_result["valid"] = len(validation_result["errors"]) == 0
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error: {e}")
        
        return validation_result
    
    def export_registry(self) -> Dict[str, Any]:
        """Export registry to dictionary for serialization."""
        export_data = {
            "registry_info": {
                "total_templates": len(self._templates),
                "categories": {cat.value: len(templates) for cat, templates in self._categories.items()},
                "types": {t_type.value: len(templates) for t_type, templates in self._types.items()},
                "security_levels": {level.value: len(templates) for level, templates in self._security_levels.items()},
                "export_time": datetime.now().isoformat()
            },
            "templates": {}
        }
        
        for name, registration in self._templates.items():
            export_data["templates"][name] = registration.metadata.to_dict()
        
        return export_data
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_templates": len(self._templates),
            "categories": {cat.value: len(templates) for cat, templates in self._categories.items()},
            "types": {t_type.value: len(templates) for t_type, templates in self._types.items()},
            "security_levels": {level.value: len(templates) for level, templates in self._security_levels.items()},
            "total_tags": len(self._tags),
            "total_dependencies": len(self._dependencies),
            "most_used_tags": sorted(
                [(tag, len(templates)) for tag, templates in self._tags.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "most_common_dependencies": sorted(
                [(dep, len(templates)) for dep, templates in self._dependencies.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }


# Global registry instance
_global_registry = APITemplateRegistry()


def register_template(
    template_class: Type[TemplateInterface],
    metadata: Optional[TemplateMetadata] = None
) -> bool:
    """Register template in global registry."""
    return _global_registry.register_template(template_class, metadata)


def get_template(name: str) -> Optional[TemplateInterface]:
    """Get template from global registry."""
    return _global_registry.get_template(name)


def list_templates(**filters) -> List[TemplateMetadata]:
    """List templates from global registry."""
    return _global_registry.list_templates(**filters)


def get_templates_by_category(category: TemplateCategory) -> List[str]:
    """Get templates by category from global registry."""
    return _global_registry.get_templates_by_category(category)


def get_registry_stats() -> Dict[str, Any]:
    """Get global registry statistics."""
    return _global_registry.get_registry_stats()