"""Business Configuration Index
============================

Central index and registry for all business configuration modules and components.
Provides unified access point and discovery mechanism for enterprise configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing and collaboration inquiries.
"""
from typing import Dict, List, Type, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Import all configuration modules
from .workflow_config import WorkflowConfig
from .tenant_config import TenantConfig
from .user_roles_config import UserRolesConfig
from .content_lifecycle_config import ContentLifecycleConfig
from .collaboration_config import CollaborationConfig
from .notification_config import NotificationConfig
from .feature_flags_config import FeatureFlagsConfig
from .compliance_config import ComplianceConfig


@dataclass
class ConfigurationModule:
    """Configuration module metadata."""
    name: str
    class_ref: Type
    description: str
    version: str
    category: str
    dependencies: List[str]
    last_updated: datetime
    stability: str  # stable, beta, experimental
    documentation_url: str


class BusinessConfigIndex:
    """
    Central registry and index for all business configuration modules.
    Provides unified access, discovery, and management of configuration components.
    """
    # Registry of all configuration modules
    CONFIGURATION_MODULES: Dict[str, ConfigurationModule] = {
        "workflow": ConfigurationModule(
            name="WorkflowConfig",
            class_ref=WorkflowConfig,
            description="Multi-format content processing workflows and business logic flows",
            version="2.0.0",
            category="core",
            dependencies=[],
            last_updated=datetime(2025, 8, 15),
            stability="stable",
            documentation_url="/docs/config/workflow"
        ),
        "tenant": ConfigurationModule(
            name="TenantConfig",
            class_ref=TenantConfig,
            description="Enterprise multi-tenant architecture configuration",
            version="2.0.0",
            category="core",
            dependencies=[],
            last_updated=datetime(2025, 8, 15),
            stability="stable",
            documentation_url="/docs/config/tenant"
        ),
        "user_roles": ConfigurationModule(
            name="UserRolesConfig",
            class_ref=UserRolesConfig,
            description="Role-based access control and permissions management",
            version="2.0.0",
            category="security",
            dependencies=["tenant"],
            last_updated=datetime(2025, 8, 15),
            stability="stable",
            documentation_url="/docs/config/user-roles"
        ),
        "content_lifecycle": ConfigurationModule(
            name="ContentLifecycleConfig",
            class_ref=ContentLifecycleConfig,
            description="Content lifecycle states, transitions, and business rules",
            version="2.0.0",
            category="core",
            dependencies=["workflow", "user_roles"],
            last_updated=datetime(2025, 8, 15),
            stability="stable",
            documentation_url="/docs/config/content-lifecycle"
        ),
        "collaboration": ConfigurationModule(
            name="CollaborationConfig",
            class_ref=CollaborationConfig,
            description="Creator collaboration matching and revenue sharing",
            version="2.0.0",
            category="business",
            dependencies=["user_roles", "content_lifecycle"],
            last_updated=datetime(2025, 8, 15),
            stability="stable",
            documentation_url="/docs/config/collaboration"
        ),
        "notification": ConfigurationModule(
            name="NotificationConfig",
            class_ref=NotificationConfig,
            description="Multi-channel notification system configuration",
            version="2.0.0",
            category="communication",
            dependencies=["user_roles", "tenant"],
            last_updated=datetime(2025, 8, 15),
            stability="stable",
            documentation_url="/docs/config/notification"
        ),
        "feature_flags": ConfigurationModule(
            name="FeatureFlagsConfig",
            class_ref=FeatureFlagsConfig,
            description="Feature flag management and A/B testing configuration",
            version="2.0.0",
            category="platform",
            dependencies=["tenant", "user_roles"],
            last_updated=datetime(2025, 8, 15),
            stability="stable",
            documentation_url="/docs/config/feature-flags"
        ),
        "compliance": ConfigurationModule(
            name="ComplianceConfig",
            class_ref=ComplianceConfig,
            description="Legal and regulatory compliance management",
            version="2.0.0",
            category="compliance",
            dependencies=["tenant", "user_roles"],
            last_updated=datetime(2025, 8, 15),
            stability="stable",
            documentation_url="/docs/config/compliance"
        )
    }

    # Category mappings
    CATEGORIES = {
        "core": ["workflow", "tenant", "content_lifecycle"],
        "security": ["user_roles", "compliance"],
        "business": ["collaboration"],
        "communication": ["notification"],
        "platform": ["feature_flags"],
        "compliance": ["compliance"]
    }

    # System information
    SYSTEM_INFO = {
        "name": "IA-Influencer Agent Business Configuration",
        "version": "2.0.0",
        "author": "Fahed Mlaiel <mlaiel@live.de>",
        "description": "Enterprise business configuration system for multi-format content platform",
        "license": "Proprietary - All Rights Reserved",
        "copyright": "© 2025 Fahed Mlaiel. All rights reserved.",
        "contact": "mlaiel@live.de",
        "platform": "IA-Influencer Agent + Content Protection Platform",
        "supported_python": ">=3.9",
        "dependencies": [
            "pydantic>=2.0.0",
            "python-dateutil>=2.8.0",
            "typing-extensions>=4.0.0"
        ]
    }

    @classmethod
    def get_module(cls, module_name: str) -> Optional[ConfigurationModule]:
        """Get configuration module by name."""
        return cls.CONFIGURATION_MODULES.get(module_name)

    @classmethod
    def get_module_class(cls, module_name: str) -> Optional[Type]:
        """Get configuration class by module name."""
        module = cls.get_module(module_name)
        return module.class_ref if module else None

    @classmethod
    def list_modules(cls, category: Optional[str] = None) -> List[str]:
        """List all configuration modules, optionally filtered by category."""
        if category:
            return cls.CATEGORIES.get(category, [])
        return list(cls.CONFIGURATION_MODULES.keys())

    @classmethod
    def get_modules_by_category(cls, category: str) -> Dict[str, ConfigurationModule]:
        """Get all modules in a specific category."""
        module_names = cls.CATEGORIES.get(category, [])
        return {name: cls.CONFIGURATION_MODULES[name] for name in module_names}

    @classmethod
    def get_dependency_graph(cls) -> Dict[str, List[str]]:
        """Get dependency graph of all modules."""
        return {
            name: module.dependencies 
            for name, module in cls.CONFIGURATION_MODULES.items()
        }

    @classmethod
    def get_initialization_order(cls) -> List[str]:
        """Get recommended module initialization order based on dependencies."""
        # Topological sort of dependency graph
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(module_name: str):
            if module_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {module_name}")
            if module_name in visited:
                return
            
            temp_visited.add(module_name)
            module = cls.CONFIGURATION_MODULES[module_name]
            
            for dependency in module.dependencies:
                if dependency in cls.CONFIGURATION_MODULES:
                    visit(dependency)
            
            temp_visited.remove(module_name)
            visited.add(module_name)
            order.append(module_name)
        
        for module_name in cls.CONFIGURATION_MODULES:
            if module_name not in visited:
                visit(module_name)
        
        return order

    @classmethod
    def validate_system_integrity(cls) -> Dict[str, Any]:
        """Validate the integrity of the configuration system."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "module_count": len(cls.CONFIGURATION_MODULES),
            "category_count": len(cls.CATEGORIES),
            "total_dependencies": sum(
                len(module.dependencies) 
                for module in cls.CONFIGURATION_MODULES.values()
            )
        }
        
        # Check for missing dependencies
        all_modules = set(cls.CONFIGURATION_MODULES.keys())
        for module_name, module in cls.CONFIGURATION_MODULES.items():
            for dependency in module.dependencies:
                if dependency not in all_modules:
                    validation_results["errors"].append(
                        f"Module '{module_name}' has missing dependency '{dependency}'"
                    )
                    validation_results["valid"] = False
        
        # Check for circular dependencies
        try:
            cls.get_initialization_order()
        except ValueError as e:
            validation_results["errors"].append(f"Circular dependency detected: {str(e)}")
            validation_results["valid"] = False
        
        # Check category consistency
        categorized_modules = set()
        for category_modules in cls.CATEGORIES.values():
            categorized_modules.update(category_modules)
        
        uncategorized = all_modules - categorized_modules
        if uncategorized:
            validation_results["warnings"].append(
                f"Uncategorized modules found: {list(uncategorized)}"
            )
        
        return validation_results

    @classmethod
    def get_system_statistics(cls) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        stats = {
            "modules": {
                "total": len(cls.CONFIGURATION_MODULES),
                "by_category": {
                    category: len(modules) 
                    for category, modules in cls.CATEGORIES.items()
                },
                "by_stability": {},
                "with_dependencies": 0,
                "without_dependencies": 0
            },
            "dependencies": {
                "total_connections": 0,
                "max_dependencies_per_module": 0,
                "most_depended_on": {},
                "dependency_depth": {}
            },
            "system": cls.SYSTEM_INFO.copy()
        }
        
        # Calculate stability distribution
        stability_count = {}
        dependency_count = 0
        max_deps = 0
        
        for module in cls.CONFIGURATION_MODULES.values():
            stability = module.stability
            stability_count[stability] = stability_count.get(stability, 0) + 1
            
            deps_count = len(module.dependencies)
            dependency_count += deps_count
            max_deps = max(max_deps, deps_count)
            
            if deps_count > 0:
                stats["modules"]["with_dependencies"] += 1
            else:
                stats["modules"]["without_dependencies"] += 1
        
        stats["modules"]["by_stability"] = stability_count
        stats["dependencies"]["total_connections"] = dependency_count
        stats["dependencies"]["max_dependencies_per_module"] = max_deps
        
        # Find most depended on modules
        dependency_count_map = {}
        for module in cls.CONFIGURATION_MODULES.values():
            for dep in module.dependencies:
                dependency_count_map[dep] = dependency_count_map.get(dep, 0) + 1
        
        stats["dependencies"]["most_depended_on"] = dependency_count_map
        
        return stats

    @classmethod
    def generate_documentation_index(cls) -> Dict[str, Any]:
        """Generate documentation index for all modules."""
        doc_index = {
            "system": cls.SYSTEM_INFO,
            "modules": {},
            "categories": {},
            "quick_reference": {
                "initialization_order": cls.get_initialization_order(),
                "core_modules": cls.list_modules("core"),
                "total_modules": len(cls.CONFIGURATION_MODULES)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Module documentation
        for name, module in cls.CONFIGURATION_MODULES.items():
            doc_index["modules"][name] = {
                "name": module.name,
                "description": module.description,
                "version": module.version,
                "category": module.category,
                "dependencies": module.dependencies,
                "stability": module.stability,
                "documentation_url": module.documentation_url,
                "class_name": module.class_ref.__name__,
                "module_path": f"backend.config.business.{name}_config"
            }
        
        # Category documentation
        for category, modules in cls.CATEGORIES.items():
            doc_index["categories"][category] = {
                "modules": modules,
                "description": cls._get_category_description(category)
            }
        
        return doc_index

    @classmethod
    def _get_category_description(cls, category: str) -> str:
        """Get description for a category."""
        descriptions = {
            "core": "Essential system configuration modules required for basic platform operation",
            "security": "Security-related configuration including access control and compliance",
            "business": "Business logic and workflow configuration modules",
            "communication": "Notification and communication system configuration",
            "platform": "Platform-wide feature and system configuration",
            "compliance": "Legal and regulatory compliance configuration"
        }
        return descriptions.get(category, f"Configuration modules in the {category} category")


# Export the index for external use
configuration_index = BusinessConfigIndex()

# Quick access functions
def get_config_class(module_name: str) -> Optional[Type]:
    """Quick access function to get configuration class."""
    return BusinessConfigIndex.get_module_class(module_name)

def list_config_modules(category: Optional[str] = None) -> List[str]:
    """Quick access function to list configuration modules."""
    return BusinessConfigIndex.list_modules(category)

def validate_config_system() -> Dict[str, Any]:
    """Quick access function to validate configuration system."""
    return BusinessConfigIndex.validate_system_integrity()

def get_system_info() -> Dict[str, Any]:
    """Quick access function to get system information."""
    return BusinessConfigIndex.SYSTEM_INFO.copy()

# Module exports
__all__ = [
    'BusinessConfigIndex',
    'ConfigurationModule',
    'configuration_index',
    'get_config_class',
    'list_config_modules',
    'validate_config_system',
    'get_system_info'
]
