
# Security headers enforcement - Added by Security Expert
# X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 1; mode=block
"""Security Template Registry for iacherie Enterprise Platform

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
Enterprise Security Architecture Expert
"""

import logging
import inspect
from typing import Dict, Any, Optional, List, Type, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
import importlib
import pkgutil
from pathlib import Path
import json

from pydantic import BaseModel, Field, validator
from threading import Lock
import asyncio

from core.config import get_settings
from utils.exceptions import SecurityError, RegistryError, TemplateError
from monitoring.security_metrics import SecurityMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class TemplateCategory(Enum):
    """Security template categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    PROTECTION = "protection"
    CONTENT_PROTECTION = "content_protection"
    THREAT_DETECTION = "threat_detection"
    ANALYTICS = "analytics"
    NETWORK_SECURITY = "network_security"
    DATA_PROTECTION = "data_protection"
    CREATOR_SECURITY = "creator_security"
    MOBILE_SECURITY = "mobile_security"
    CLOUD_SECURITY = "cloud_security"
    INCIDENT_MANAGEMENT = "incident_management"
    COMPLIANCE = "compliance"
    TESTING = "testing"


class TemplateStatus(Enum):
    """Template status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    MAINTENANCE = "maintenance"


class SecurityLevel(Enum):
    """Security levels for templates"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    MILITARY_GRADE = "military_grade"


class TemplateMetadata(BaseModel):
    """Template metadata model"""
    template_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    category: TemplateCategory
    version: str = Field(default="1.0.0")
    author: str = Field(default="Fahed Mlaiel")
    created_date: datetime = Field(default_factory=datetime.utcnow)
    updated_date: datetime = Field(default_factory=datetime.utcnow)
    status: TemplateStatus = TemplateStatus.ACTIVE
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    documentation_url: Optional[str] = None
    example_usage: Optional[str] = None
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('template_id')
    def validate_template_id(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Template ID must be alphanumeric with underscores/hyphens")
        return v


class TemplateRegistration(BaseModel):
    """Template registration information"""
    metadata: TemplateMetadata
    template_class: Type
    initialization_params: Dict[str, Any] = Field(default_factory=dict)
    health_check_method: Optional[str] = None
    configuration_schema: Optional[Dict[str, Any]] = None
    usage_statistics: Dict[str, int] = Field(default_factory=dict)
    last_accessed: Optional[datetime] = None
    error_count: int = 0
    success_count: int = 0


class SecurityTemplateRegistry:
    """Central registry for all security templates in the iacherie platform"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize security template registry
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.metrics = SecurityMetricsCollector()
        
        # Thread-safe registry storage
        self._registry_lock = Lock()
        self._templates: Dict[str, TemplateRegistration] = {}
        self._category_index: Dict[TemplateCategory, List[str]] = {}
        self._tag_index: Dict[str, List[str]] = {}
        self._dependency_graph: Dict[str, List[str]] = {}
        
        # Template instances cache
        self._instance_cache: Dict[str, Any] = {}
        self._cache_lock = Lock()
        
        # Registry state
        self._initialized = False
        self._auto_discovery_enabled = self.config.get('auto_discovery', True)
        
        # Initialize registry
        self._initialize_registry()
    
    def _initialize_registry(self) -> None:
        """Initialize the template registry system"""
        try:
            self.logger.info("Initializing security template registry")
            
            # Initialize category index
            for category in TemplateCategory:
                self._category_index[category] = []
            
            # Auto-discover templates if enabled
            if self._auto_discovery_enabled:
                self._auto_discover_templates()
            
            # Register core templates manually
            self._register_core_templates()
            
            # Build dependency graph
            self._build_dependency_graph()
            
            # Validate registry integrity
            self._validate_registry_integrity()
            
            self._initialized = True
            self.logger.info(f"Security template registry initialized with {len(self._templates)} templates")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize template registry: {e}")
            raise RegistryError(f"Registry initialization failed: {e}")
    
    def register_template(self, metadata: TemplateMetadata, template_class: Type,
                         initialization_params: Optional[Dict[str, Any]] = None,
                         health_check_method: Optional[str] = None) -> bool:
        """Register a security template
        
        Args:
            metadata: Template metadata
            template_class: Template class
            initialization_params: Optional initialization parameters
            health_check_method: Optional health check method name
            
        Returns:
            True if registration successful
        """
        try:
            with self._registry_lock:
                self.logger.info(f"Registering template: {metadata.template_id}")
                
                # Validate template class
                if not self._validate_template_class(template_class):
                    raise TemplateError(f"Invalid template class: {template_class}")
                
                # Check for conflicts
                if metadata.template_id in self._templates:
                    existing = self._templates[metadata.template_id]
                    if existing.metadata.version != metadata.version:
                        self.logger.warning(f"Updating template {metadata.template_id} from version {existing.metadata.version} to {metadata.version}")
                    else:
                        raise RegistryError(f"Template {metadata.template_id} already registered")
                
                # Create registration
                registration = TemplateRegistration(
                    metadata=metadata,
                    template_class=template_class,
                    initialization_params=initialization_params or {},
                    health_check_method=health_check_method,
                    configuration_schema=self._extract_configuration_schema(template_class)
                )
                
                # Store in registry
                self._templates[metadata.template_id] = registration
                
                # Update indexes
                self._update_category_index(metadata.template_id, metadata.category)
                self._update_tag_index(metadata.template_id, metadata.tags)
                
                # Log registration
                self.metrics.increment_counter('templates_registered', {
                    'category': metadata.category.value,
                    'template_id': metadata.template_id
                })
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to register template {metadata.template_id}: {e}")
            self.metrics.increment_counter('template_registration_errors')
            raise RegistryError(f"Template registration failed: {e}")
    
    def get_template(self, template_id: str, use_cache: bool = True) -> Optional[Any]:
        """Get template instance by ID
        
        Args:
            template_id: Template identifier
            use_cache: Whether to use cached instance
            
        Returns:
            Template instance or None if not found
        """
        try:
            # Check cache first if enabled
            if use_cache:
                with self._cache_lock:
                    if template_id in self._instance_cache:
                        self._update_access_statistics(template_id, success=True)
                        return self._instance_cache[template_id]
            
            # Get from registry
            with self._registry_lock:
                registration = self._templates.get(template_id)
                if not registration:
                    self.logger.warning(f"Template not found: {template_id}")
                    return None
                
                # Check template status
                if registration.metadata.status != TemplateStatus.ACTIVE:
                    self.logger.warning(f"Template {template_id} is not active (status: {registration.metadata.status})")
                    return None
                
                # Create instance
                instance = self._create_template_instance(registration)
                
                # Cache instance if enabled
                if use_cache:
                    with self._cache_lock:
                        self._instance_cache[template_id] = instance
                
                # Update statistics
                self._update_access_statistics(template_id, success=True)
                
                self.logger.debug(f"Retrieved template instance: {template_id}")
                return instance
                
        except Exception as e:
            self.logger.error(f"Failed to get template {template_id}: {e}")
            self._update_access_statistics(template_id, success=False)
            self.metrics.increment_counter('template_retrieval_errors')
            return None
    
    def list_templates(self, category: Optional[TemplateCategory] = None,
                      status: Optional[TemplateStatus] = None,
                      tags: Optional[List[str]] = None) -> List[TemplateMetadata]:
        """List templates with optional filtering
        
        Args:
            category: Optional category filter
            status: Optional status filter
            tags: Optional tags filter
            
        Returns:
            List of template metadata
        """
        try:
            with self._registry_lock:
                templates = []
                
                for template_id, registration in self._templates.items():
                    metadata = registration.metadata
                    
                    # Apply filters
                    if category and metadata.category != category:
                        continue
                    
                    if status and metadata.status != status:
                        continue
                    
                    if tags:
                        if not any(tag in metadata.tags for tag in tags):
                            continue
                    
                    templates.append(metadata)
                
                # Sort by category and name
                templates.sort(key=lambda x: (x.category.value, x.name))
                
                return templates
                
        except Exception as e:
            self.logger.error(f"Failed to list templates: {e}")
            return []
    
    def get_templates_by_category(self, category: TemplateCategory) -> List[str]:
        """Get template IDs by category
        
        Args:
            category: Template category
            
        Returns:
            List of template IDs in the category
        """
        with self._registry_lock:
            return self._category_index.get(category, []).copy()
    
    def get_template_dependencies(self, template_id: str) -> List[str]:
        """Get template dependencies
        
        Args:
            template_id: Template identifier
            
        Returns:
            List of dependency template IDs
        """
        with self._registry_lock:
            registration = self._templates.get(template_id)
            if registration:
                return registration.metadata.dependencies.copy()
            return []
    
    def resolve_dependencies(self, template_id: str) -> List[str]:
        """Resolve all dependencies for a template in correct order
        
        Args:
            template_id: Template identifier
            
        Returns:
            List of template IDs in dependency order
        """
        try:
            resolved = []
            visited = set()
            
            def resolve_recursive(tid: str):
                if tid in visited:
                    return
                
                visited.add(tid)
                dependencies = self.get_template_dependencies(tid)
                
                for dep_id in dependencies:
                    if dep_id not in self._templates:
                        self.logger.warning(f"Dependency {dep_id} not found for template {tid}")
                        continue
                    resolve_recursive(dep_id)
                
                if tid not in resolved:
                    resolved.append(tid)
            
            resolve_recursive(template_id)
            return resolved
            
        except Exception as e:
            self.logger.error(f"Failed to resolve dependencies for {template_id}: {e}")
            return [template_id]
    
    def health_check_template(self, template_id: str) -> Dict[str, Any]:
        """Perform health check on template
        
        Args:
            template_id: Template identifier
            
        Returns:
            Health check results
        """
        try:
            with self._registry_lock:
                registration = self._templates.get(template_id)
                if not registration:
                    return {'status': 'not_found', 'error': f'Template {template_id} not found'}
                
                health_result = {
                    'template_id': template_id,
                    'status': 'healthy',
                    'timestamp': datetime.utcnow(),
                    'checks': {}
                }
                
                # Check template status
                if registration.metadata.status != TemplateStatus.ACTIVE:
                    health_result['status'] = 'inactive'
                    health_result['checks']['status'] = f"Template status: {registration.metadata.status.value}"
                
                # Check dependencies
                missing_deps = []
                for dep_id in registration.metadata.dependencies:
                    if dep_id not in self._templates:
                        missing_deps.append(dep_id)
                
                if missing_deps:
                    health_result['status'] = 'unhealthy'
                    health_result['checks']['dependencies'] = f"Missing dependencies: {missing_deps}"
                
                # Perform custom health check if available
                if registration.health_check_method:
                    try:
                        instance = self.get_template(template_id, use_cache=False)
                        if instance and hasattr(instance, registration.health_check_method):
                            method = getattr(instance, registration.health_check_method)
                            custom_result = method()
                            health_result['checks']['custom'] = custom_result
                            
                            if isinstance(custom_result, dict) and not custom_result.get('healthy', True):
                                health_result['status'] = 'unhealthy'
                    except Exception as e:
                        health_result['status'] = 'unhealthy'
                        health_result['checks']['custom'] = f"Health check failed: {e}"
                
                # Check error rate
                total_access = registration.success_count + registration.error_count
                if total_access > 0:
                    error_rate = registration.error_count / total_access
                    health_result['checks']['error_rate'] = error_rate
                    
                    if error_rate > 0.1:  # 10% error rate threshold
                        health_result['status'] = 'degraded'
                
                return health_result
                
        except Exception as e:
            self.logger.error(f"Health check failed for template {template_id}: {e}")
            return {
                'template_id': template_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
    
    def bulk_health_check(self) -> Dict[str, Any]:
        """Perform health check on all registered templates
        
        Returns:
            Bulk health check results
        """
        try:
            results = {
                'overall_status': 'healthy',
                'timestamp': datetime.utcnow(),
                'total_templates': len(self._templates),
                'healthy_count': 0,
                'unhealthy_count': 0,
                'degraded_count': 0,
                'inactive_count': 0,
                'template_results': {}
            }
            
            for template_id in self._templates:
                health_result = self.health_check_template(template_id)
                results['template_results'][template_id] = health_result
                
                status = health_result['status']
                if status == 'healthy':
                    results['healthy_count'] += 1
                elif status == 'unhealthy':
                    results['unhealthy_count'] += 1
                elif status == 'degraded':
                    results['degraded_count'] += 1
                elif status == 'inactive':
                    results['inactive_count'] += 1
            
            # Determine overall status
            if results['unhealthy_count'] > 0:
                results['overall_status'] = 'unhealthy'
            elif results['degraded_count'] > 0:
                results['overall_status'] = 'degraded'
            elif results['inactive_count'] == results['total_templates']:
                results['overall_status'] = 'inactive'
            
            return results
            
        except Exception as e:
            self.logger.error(f"Bulk health check failed: {e}")
            return {
                'overall_status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics
        
        Returns:
            Registry statistics
        """
        try:
            with self._registry_lock:
                stats = {
                    'total_templates': len(self._templates),
                    'templates_by_category': {},
                    'templates_by_status': {},
                    'templates_by_security_level': {},
                    'most_used_templates': [],
                    'error_statistics': {},
                    'cache_statistics': {},
                    'dependency_statistics': {}
                }
                
                # Count by category
                for category in TemplateCategory:
                    count = len(self._category_index.get(category, []))
                    stats['templates_by_category'][category.value] = count
                
                # Count by status and security level
                for registration in self._templates.values():
                    metadata = registration.metadata
                    
                    # Status count
                    status = metadata.status.value
                    stats['templates_by_status'][status] = stats['templates_by_status'].get(status, 0) + 1
                    
                    # Security level count
                    level = metadata.security_level.value
                    stats['templates_by_security_level'][level] = stats['templates_by_security_level'].get(level, 0) + 1
                
                # Most used templates
                usage_list = [(tid, reg.usage_statistics.get('total_access', 0)) 
                             for tid, reg in self._templates.items()]
                usage_list.sort(key=lambda x: x[1], reverse=True)
                stats['most_used_templates'] = usage_list[:10]
                
                # Cache statistics
                with self._cache_lock:
                    stats['cache_statistics'] = {
                        'cached_instances': len(self._instance_cache),
                        'cache_hit_rate': self._calculate_cache_hit_rate()
                    }
                
                # Dependency statistics
                total_deps = sum(len(reg.metadata.dependencies) for reg in self._templates.values())
                stats['dependency_statistics'] = {
                    'total_dependencies': total_deps,
                    'avg_dependencies_per_template': total_deps / len(self._templates) if self._templates else 0,
                    'templates_with_dependencies': sum(1 for reg in self._templates.values() if reg.metadata.dependencies)
                }
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get registry statistics: {e}")
            return {}
    
    def export_registry_config(self) -> Dict[str, Any]:
        """Export registry configuration for backup/migration
        
        Returns:
            Registry configuration data
        """
        try:
            with self._registry_lock:
                config = {
                    'version': '1.0.0',
                    'export_timestamp': datetime.utcnow().isoformat(),
                    'templates': {}
                }
                
                for template_id, registration in self._templates.items():
                    config['templates'][template_id] = {
                        'metadata': registration.metadata.dict(),
                        'class_name': registration.template_class.__name__,
                        'module_name': registration.template_class.__module__,
                        'initialization_params': registration.initialization_params,
                        'health_check_method': registration.health_check_method,
                        'usage_statistics': registration.usage_statistics
                    }
                
                return config
                
        except Exception as e:
            self.logger.error(f"Failed to export registry config: {e}")
            return {}
    
    # Helper methods
    def _auto_discover_templates(self) -> None:
        """Auto-discover templates in the security module"""
        try:
            import templates.security as security_module
            
            # Walk through all modules in the security package
            for importer, modname, ispkg in pkgutil.iter_modules(security_module.__path__):
                if modname.endswith('_template'):
                    try:
                        module = importlib.import_module(f'templates.security.{modname}')
                        self._discover_templates_in_module(module)
                    except Exception as e:
                        self.logger.warning(f"Failed to load template module {modname}: {e}")
                        
        except Exception as e:
            self.logger.warning(f"Auto-discovery failed: {e}")
    
    def _discover_templates_in_module(self, module) -> None:
        """Discover templates in a specific module"""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (name.endswith('Template') and 
                hasattr(obj, '__module__') and 
                obj.__module__ == module.__name__):
                
                try:
                    # Try to extract metadata from class
                    metadata = self._extract_template_metadata(obj)
                    if metadata:
                        self.register_template(metadata, obj)
                except Exception as e:
                    self.logger.warning(f"Failed to auto-register template {name}: {e}")
    
    def _register_core_templates(self) -> None:
        """Register core security templates manually"""
        try:
            # Import and register core templates
            from .authentication_template import AuthenticationTemplate
            from .authorization_template import AuthorizationTemplate
            from .csrf_protection_template import CSRFProtectionTemplate
            from .encryption_template import EncryptionTemplate
            from .input_validation_template import InputValidationTemplate
            from .security_middleware_template import SecurityMiddlewareTemplate
            
            # Import content protection templates
            from .content_watermarking_template import ContentWatermarkingTemplate
            from .digital_rights_management_template import DigitalRightsManagementTemplate
            from .content_fingerprinting_template import ContentFingerprintingTemplate
            from .plagiarism_detection_template import PlagiarismDetectionTemplate
            
            # Register each template
            core_templates = [
                (AuthenticationTemplate, TemplateCategory.AUTHENTICATION),
                (AuthorizationTemplate, TemplateCategory.AUTHORIZATION),
                (CSRFProtectionTemplate, TemplateCategory.PROTECTION),
                (EncryptionTemplate, TemplateCategory.PROTECTION),
                (InputValidationTemplate, TemplateCategory.PROTECTION),
                (SecurityMiddlewareTemplate, TemplateCategory.PROTECTION),
                (ContentWatermarkingTemplate, TemplateCategory.CONTENT_PROTECTION),
                (DigitalRightsManagementTemplate, TemplateCategory.CONTENT_PROTECTION),
                (ContentFingerprintingTemplate, TemplateCategory.CONTENT_PROTECTION),
                (PlagiarismDetectionTemplate, TemplateCategory.CONTENT_PROTECTION)
            ]
            
            for template_class, category in core_templates:
                metadata = self._create_core_template_metadata(template_class, category)
                self.register_template(metadata, template_class)
                
        except Exception as e:
            self.logger.warning(f"Failed to register some core templates: {e}")
    
    def _create_core_template_metadata(self, template_class: Type, category: TemplateCategory) -> TemplateMetadata:
        """Create metadata for core templates"""
        class_name = template_class.__name__
        template_id = class_name.lower().replace('template', '').replace('_', '_')
        
        return TemplateMetadata(
            template_id=template_id,
            name=class_name,
            description=f"Core {category.value} template for iacherie platform",
            category=category,
            version="4.0.0",
            author="Fahed Mlaiel",
            security_level=SecurityLevel.HIGH,
            tags=[category.value, 'core', 'enterprise']
        )
    
    # Additional helper methods would be implemented here...
    # (Instance creation, validation, caching, etc.)


# Global registry instance
_registry_instance = None
_registry_lock = Lock()


def get_security_registry() -> SecurityTemplateRegistry:
    """Get global security template registry instance
    
    Returns:
        Security template registry instance
    """
    global _registry_instance
    
    if _registry_instance is None:
        with _registry_lock:
            if _registry_instance is None:
                _registry_instance = SecurityTemplateRegistry()
    
    return _registry_instance


# Export main components
__all__ = [
    'SecurityTemplateRegistry',
    'TemplateMetadata',
    'TemplateRegistration',
    'TemplateCategory',
    'TemplateStatus',
    'SecurityLevel',
    'get_security_registry'
]