#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ Ainflue Database Templates Module - Enterprise Grade

🚨 PROTECTION PROPRIÉTÉ INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Code propriétaire

AVERTISSEMENT LÉGAL:
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT  
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Developed by Expert Team:
- Lead Dev IA: Fahed Mlaiel - Advanced database architecture
- Backend Senior: Enterprise SQLAlchemy & async patterns
- DBA Expert: Performance optimization & multi-tenant design
- Security Expert: Encryption, audit trails & compliance frameworks
- ML Engineer: Analytics database templates & time-series optimization
- Microservices Architect: Distributed database patterns
- DevOps Engineer: Migration strategies & backup systems
- IA Prompt Engineer: AI-powered database intelligence

Architecture: Creator Economy Database Templates
Business Logic: Upload → AI Processing → Database Templates → Protection → Monetization → Distribution
"""

from typing import Dict, List, Type, Any
import importlib
import logging
from pathlib import Path

# Core Model Templates
from .sqlalchemy_model_template import (
    SQLAlchemyModelTemplate,
    BaseEntity,
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin
)

from .pydantic_model_template import (
    PydanticModelTemplate,
    BaseModel,
    CreatorModel,
    ContentModel,
    ValidationError
)

from .mongodb_model_template import (
    MongoDBModelTemplate,
    BaseDocument,
    CreatorDocument,
    ContentDocument,
    DocumentValidationError
)

from .multi_tenant_model_template import (
    MultiTenantModelTemplate,
    TenantIsolatedModel,
    TenantContext,
    CrossTenantValidationError
)

from .time_series_model_template import (
    TimeSeriesModelTemplate,
    TimeSeriesData,
    MetricsCollector,
    AnalyticsEngine
)

from .repository_template import (
    RepositoryTemplate,
    BaseRepository,
    AsyncRepository,
    CachedRepository,
    RepositoryError
)

from .enum_template import (
    EnumTemplate,
    StatusEnum,
    TypeEnum,
    PriorityEnum,
    CategoryEnum
)

# Migration Templates (NEW)
try:
    from .alembic_migration_template import AlembicMigrationTemplate
    from .schema_versioning_template import SchemaVersioningTemplate
    from .data_seeding_template import DataSeedingTemplate
    from .rollback_strategy_template import RollbackStrategyTemplate
except ImportError:
    # Migration templates will be available after implementation
    pass

# Performance Templates (NEW)
try:
    from .query_optimization_template import QueryOptimizationTemplate
    from .index_strategy_template import IndexStrategyTemplate
    from .connection_pooling_template import ConnectionPoolingTemplate
    from .database_sharding_template import DatabaseShardingTemplate
except ImportError:
    # Performance templates will be available after implementation
    pass

# Security Templates (NEW)
try:
    from .encryption_at_rest_template import EncryptionAtRestTemplate
    from .access_control_template import AccessControlTemplate
    from .audit_logging_template import AuditLoggingTemplate
    from .data_masking_template import DataMaskingTemplate
except ImportError:
    # Security templates will be available after implementation
    pass

# Creator Economy Templates (NEW)
try:
    from .creator_profile_template import CreatorProfileTemplate
    from .content_metadata_template import ContentMetadataTemplate
    from .monetization_data_template import MonetizationDataTemplate
    from .analytics_data_template import AnalyticsDataTemplate
except ImportError:
    # Creator Economy templates will be available after implementation
    pass

__version__ = "4.1.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary"

logger = logging.getLogger(__name__)

# Template Registry
TEMPLATE_REGISTRY: Dict[str, Type] = {
    # Core Model Templates
    "sqlalchemy": SQLAlchemyModelTemplate,
    "pydantic": PydanticModelTemplate,
    "mongodb": MongoDBModelTemplate,
    "multi_tenant": MultiTenantModelTemplate,
    "time_series": TimeSeriesModelTemplate,
    "repository": RepositoryTemplate,
    "enum": EnumTemplate,
}

# Template Categories
TEMPLATE_CATEGORIES = {
    "core_models": [
        "sqlalchemy", "pydantic", "mongodb", "enum"
    ],
    "repositories": [
        "repository"
    ],
    "multi_tenant": [
        "multi_tenant"
    ],
    "specialized": [
        "time_series"
    ],
    "migration": [
        "alembic_migration", "schema_versioning", "data_seeding", "rollback_strategy"
    ],
    "performance": [
        "query_optimization", "index_strategy", "connection_pooling", "database_sharding"
    ],
    "security": [
        "encryption_at_rest", "access_control", "audit_logging", "data_masking"
    ],
    "creator_economy": [
        "creator_profile", "content_metadata", "monetization_data", "analytics_data"
    ]
}

class DatabaseTemplateManager:
    """
    🏭 Enterprise Database Template Manager
    
    Centralizes access to all database templates with:
    - Template discovery and registration
    - Category-based organization
    - Validation and error handling
    - Performance monitoring
    """
    
    def __init__(self):
        self.templates = TEMPLATE_REGISTRY.copy()
        self.categories = TEMPLATE_CATEGORIES.copy()
        
    def get_template(self, template_name: str) -> Type:
        """Get template class by name"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        return self.templates[template_name]
    
    def get_templates_by_category(self, category: str) -> List[Type]:
        """Get all templates in a category"""
        if category not in self.categories:
            raise ValueError(f"Category '{category}' not found")
        
        templates = []
        for template_name in self.categories[category]:
            if template_name in self.templates:
                templates.append(self.templates[template_name])
        
        return templates
    
    def list_available_templates(self) -> List[str]:
        """List all available template names"""
        return list(self.templates.keys())
    
    def list_categories(self) -> List[str]:
        """List all template categories"""
        return list(self.categories.keys())
    
    def register_template(self, name: str, template_class: Type, category: str = None):
        """Register a new template"""
        self.templates[name] = template_class
        
        if category and category in self.categories:
            if name not in self.categories[category]:
                self.categories[category].append(name)
        
        logger.info(f"Registered template: {name}")
    
    def validate_template(self, template_name: str) -> bool:
        """Validate a template exists and is properly configured"""
        try:
            template_class = self.get_template(template_name)
            # Basic validation - template should have required methods
            required_methods = ['create', 'validate']
            for method in required_methods:
                if not hasattr(template_class, method):
                    logger.warning(f"Template {template_name} missing method: {method}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Template validation failed for {template_name}: {e}")
            return False

# Global template manager instance
template_manager = DatabaseTemplateManager()

# Convenience functions
def get_template(name: str) -> Type:
    """Get template class by name"""
    return template_manager.get_template(name)

def get_templates_by_category(category: str) -> List[Type]:
    """Get templates by category"""
    return template_manager.get_templates_by_category(category)

def list_templates() -> List[str]:
    """List all available templates"""
    return template_manager.list_available_templates()

def list_categories() -> List[str]:
    """List all template categories"""
    return template_manager.list_categories()

# Export everything
__all__ = [
    # Core Classes
    "SQLAlchemyModelTemplate", "BaseEntity", "AuditMixin", "SoftDeleteMixin", "TimestampMixin",
    "PydanticModelTemplate", "BaseModel", "CreatorModel", "ContentModel", "ValidationError",
    "MongoDBModelTemplate", "BaseDocument", "CreatorDocument", "ContentDocument",
    "MultiTenantModelTemplate", "TenantIsolatedModel", "TenantContext",
    "TimeSeriesModelTemplate", "TimeSeriesData", "MetricsCollector", "AnalyticsEngine",
    "RepositoryTemplate", "BaseRepository", "AsyncRepository", "CachedRepository",
    "EnumTemplate", "StatusEnum", "TypeEnum", "PriorityEnum", "CategoryEnum",
    
    # Template Manager
    "DatabaseTemplateManager", "template_manager",
    
    # Convenience Functions
    "get_template", "get_templates_by_category", "list_templates", "list_categories",
    
    # Constants
    "TEMPLATE_REGISTRY", "TEMPLATE_CATEGORIES",
    
    # Metadata
    "__version__", "__author__", "__copyright__", "__license__"
]

# Initialize template discovery
def _discover_templates():
    """Discover and register templates dynamically"""
    template_dir = Path(__file__).parent
    template_files = template_dir.glob("*_template.py")
    
    for template_file in template_files:
        template_name = template_file.stem
        if template_name not in template_manager.templates:
            try:
                module = importlib.import_module(f".{template_name}", package=__name__)
                # Look for template classes in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        attr_name.endswith('Template') and 
                        attr_name != 'BaseTemplate'):
                        template_manager.register_template(
                            template_name.replace('_template', ''), 
                            attr
                        )
                        break
            except ImportError as e:
                logger.debug(f"Could not import {template_name}: {e}")

# Discover templates on import
_discover_templates()

logger.info(f"Database Templates Module initialized - {len(template_manager.templates)} templates available")