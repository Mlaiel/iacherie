"""
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

Service Factory for Ainflue Microservices Platform
=================================================

Enterprise-grade service factory providing patterns for:
- Dynamic service creation and configuration
- Service template instantiation
- Dependency injection and management
- Environment-specific service setup
- Service discovery integration
- Resource management and optimization
- Configuration validation and setup
- Service lifecycle management

Author: Fahed Mlaiel (mlaiel@live.de)
Microservices Architect & Backend Senior
"""

import logging
from typing import Dict, Any, Optional, Type, List, Union, Callable
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
import importlib
import os
import yaml
import json
from pathlib import Path

from pydantic import BaseModel, Field, validator
from .microservice_template import ServiceConfig, ServiceStatus
from .base_microservice import BaseMicroservice

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Service type enumeration"""
    WEB_API = "web_api"
    BACKGROUND_WORKER = "background_worker"
    EVENT_PROCESSOR = "event_processor"
    DATA_PIPELINE = "data_pipeline"
    MICROSERVICE = "microservice"
    GATEWAY = "gateway"
    PROXY = "proxy"
    SCHEDULER = "scheduler"


class DeploymentEnvironment(Enum):
    """Deployment environment enumeration"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ServiceTemplate(BaseModel):
    """Service template configuration"""
    name: str = Field(..., description="Template name")
    type: ServiceType = Field(..., description="Service type")
    class_name: str = Field(..., description="Service class name")
    module_path: str = Field(..., description="Module import path")
    default_config: Dict[str, Any] = Field(default_factory=dict, description="Default configuration")
    required_dependencies: List[str] = Field(default_factory=list, description="Required dependencies")
    optional_dependencies: List[str] = Field(default_factory=list, description="Optional dependencies")
    environment_configs: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Environment-specific configs")
    health_check_config: Dict[str, Any] = Field(default_factory=dict, description="Health check configuration")
    monitoring_config: Dict[str, Any] = Field(default_factory=dict, description="Monitoring configuration")
    security_config: Dict[str, Any] = Field(default_factory=dict, description="Security configuration")


class ServiceFactoryConfig(BaseModel):
    """Service factory configuration"""
    environment: DeploymentEnvironment = Field(default=DeploymentEnvironment.DEVELOPMENT, description="Deployment environment")
    service_registry_url: Optional[str] = Field(default=None, description="Service registry URL")
    config_server_url: Optional[str] = Field(default=None, description="Configuration server URL")
    template_directory: str = Field(default="./templates", description="Template directory path")
    enable_auto_discovery: bool = Field(default=True, description="Enable automatic service discovery")
    enable_health_monitoring: bool = Field(default=True, description="Enable health monitoring")
    enable_metrics_collection: bool = Field(default=True, description="Enable metrics collection")
    default_timeout: int = Field(default=30, description="Default operation timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    circuit_breaker_threshold: int = Field(default=5, description="Circuit breaker failure threshold")


class ServiceFactoryError(Exception):
    """Service factory error"""
    pass


class TemplateNotFoundError(ServiceFactoryError):
    """Template not found error"""
    pass


class ServiceCreationError(ServiceFactoryError):
    """Service creation error"""
    pass


class ConfigurationError(ServiceFactoryError):
    """Configuration error"""
    pass


class ServiceFactory:
    """
    Enterprise service factory for creating and managing microservices
    
    Provides comprehensive patterns for:
    - Dynamic service instantiation from templates
    - Environment-specific configuration management
    - Dependency injection and validation
    - Service discovery integration
    - Resource allocation and optimization
    - Configuration validation and merging
    - Service lifecycle management
    - Template-based service creation
    """
    
    def __init__(self, config: ServiceFactoryConfig):
        """Initialize service factory"""
        self.config = config
        self.templates: Dict[str, ServiceTemplate] = {}
        self.created_services: Dict[str, BaseMicroservice] = {}
        self.service_configs: Dict[str, ServiceConfig] = {}
        
        # Initialize factory
        self._load_templates()
        self._setup_configuration_sources()
        
        logger.info(f"Service factory initialized for {config.environment.value} environment")
    
    def _load_templates(self):
        """Load service templates from directory"""
        template_path = Path(self.config.template_directory)
        
        if not template_path.exists():
            logger.warning(f"Template directory not found: {template_path}")
            return
        
        # Load built-in templates
        self._load_builtin_templates()
        
        # Load custom templates from files
        for template_file in template_path.glob("*.yaml"):
            try:
                with open(template_file, 'r') as f:
                    template_data = yaml.safe_load(f)
                    template = ServiceTemplate(**template_data)
                    self.templates[template.name] = template
                    logger.info(f"Loaded template: {template.name}")
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {str(e)}")
    
    def _load_builtin_templates(self):
        """Load built-in service templates"""
        builtin_templates = [
            ServiceTemplate(
                name="rest_api",
                type=ServiceType.WEB_API,
                class_name="RestApiTemplate",
                module_path="templates.microservices.core_services.rest_api_template",
                default_config={
                    "port": 8000,
                    "enable_cors": True,
                    "enable_gzip": True,
                    "workers": 1
                },
                required_dependencies=["fastapi", "uvicorn"],
                health_check_config={"interval": 30, "timeout": 5},
                monitoring_config={"enable_metrics": True, "metrics_port": 9090}
            ),
            ServiceTemplate(
                name="graphql_api",
                type=ServiceType.WEB_API,
                class_name="GraphqlApiTemplate",
                module_path="templates.microservices.core_services.graphql_api_template",
                default_config={
                    "port": 8000,
                    "enable_cors": True,
                    "enable_introspection": True
                },
                required_dependencies=["strawberry-graphql", "fastapi"],
                health_check_config={"interval": 30, "timeout": 5}
            ),
            ServiceTemplate(
                name="grpc_service",
                type=ServiceType.MICROSERVICE,
                class_name="GrpcServiceTemplate",
                module_path="templates.microservices.core_services.grpc_service_template",
                default_config={
                    "port": 50051,
                    "enable_reflection": True,
                    "max_workers": 10
                },
                required_dependencies=["grpcio", "grpcio-tools"],
                health_check_config={"interval": 30, "timeout": 5}
            ),
            ServiceTemplate(
                name="background_worker",
                type=ServiceType.BACKGROUND_WORKER,
                class_name="BackgroundWorkerTemplate",
                module_path="templates.microservices.core_services.background_worker_template",
                default_config={
                    "concurrency": 4,
                    "prefetch_count": 10,
                    "enable_monitoring": True
                },
                required_dependencies=["celery", "redis"],
                health_check_config={"interval": 60, "timeout": 10}
            ),
            ServiceTemplate(
                name="event_processor",
                type=ServiceType.EVENT_PROCESSOR,
                class_name="EventProcessorTemplate",
                module_path="templates.microservices.core_services.event_processor_template",
                default_config={
                    "batch_size": 100,
                    "processing_timeout": 30,
                    "retry_attempts": 3
                },
                required_dependencies=["kafka-python", "redis"],
                health_check_config={"interval": 30, "timeout": 5}
            ),
            ServiceTemplate(
                name="data_pipeline",
                type=ServiceType.DATA_PIPELINE,
                class_name="DataPipelineTemplate",
                module_path="templates.microservices.core_services.data_pipeline_template",
                default_config={
                    "pipeline_workers": 4,
                    "chunk_size": 1000,
                    "enable_parallelization": True
                },
                required_dependencies=["pandas", "sqlalchemy"],
                health_check_config={"interval": 60, "timeout": 15}
            )
        ]
        
        for template in builtin_templates:
            self.templates[template.name] = template
            logger.info(f"Loaded built-in template: {template.name}")
    
    def _setup_configuration_sources(self):
        """Setup configuration sources"""
        # Setup environment-based configuration
        env_config_file = f"config/{self.config.environment.value}.yaml"
        if os.path.exists(env_config_file):
            try:
                with open(env_config_file, 'r') as f:
                    env_config = yaml.safe_load(f)
                    logger.info(f"Loaded environment configuration: {env_config_file}")
            except Exception as e:
                logger.error(f"Failed to load environment config: {str(e)}")
    
    def create_service(
        self,
        service_name: str,
        template_name: str,
        config_overrides: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None
    ) -> BaseMicroservice:
        """
        Create a new service instance from template
        
        Args:
            service_name: Unique service name
            template_name: Template to use for creation
            config_overrides: Configuration overrides
            dependencies: Additional service dependencies
            
        Returns:
            Configured microservice instance
            
        Raises:
            TemplateNotFoundError: If template not found
            ServiceCreationError: If service creation fails
        """
        if template_name not in self.templates:
            raise TemplateNotFoundError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        
        try:
            # Build service configuration
            service_config = self._build_service_config(
                service_name, template, config_overrides, dependencies
            )
            
            # Validate dependencies
            self._validate_dependencies(template, dependencies)
            
            # Create service instance
            service_instance = self._instantiate_service(template, service_config)
            
            # Register service
            self.created_services[service_name] = service_instance
            self.service_configs[service_name] = service_config
            
            logger.info(f"Created service '{service_name}' from template '{template_name}'")
            return service_instance
            
        except Exception as e:
            logger.error(f"Failed to create service '{service_name}': {str(e)}")
            raise ServiceCreationError(f"Service creation failed: {str(e)}")
    
    def _build_service_config(
        self,
        service_name: str,
        template: ServiceTemplate,
        config_overrides: Optional[Dict[str, Any]],
        dependencies: Optional[List[str]]
    ) -> ServiceConfig:
        """Build comprehensive service configuration"""
        
        # Start with template defaults
        config_data = template.default_config.copy()
        
        # Apply environment-specific configuration
        env_config = template.environment_configs.get(self.config.environment.value, {})
        config_data.update(env_config)
        
        # Apply factory-level defaults
        factory_defaults = {
            "enable_metrics": self.config.enable_metrics_collection,
            "circuit_breaker_threshold": self.config.circuit_breaker_threshold,
            "health_check_interval": template.health_check_config.get("interval", 30)
        }
        config_data.update(factory_defaults)
        
        # Apply user overrides
        if config_overrides:
            config_data.update(config_overrides)
        
        # Set required fields
        config_data["name"] = service_name
        config_data["dependencies"] = (
            template.required_dependencies + 
            template.optional_dependencies + 
            (dependencies or [])
        )
        
        return ServiceConfig(**config_data)
    
    def _validate_dependencies(self, template: ServiceTemplate, additional_deps: Optional[List[str]]):
        """Validate service dependencies"""
        all_deps = template.required_dependencies + (additional_deps or [])
        
        for dep in all_deps:
            if dep in self.created_services:
                dep_service = self.created_services[dep]
                if dep_service.status != ServiceStatus.HEALTHY:
                    logger.warning(f"Dependency '{dep}' is not healthy")
            else:
                logger.info(f"Dependency '{dep}' will be resolved at runtime")
    
    def _instantiate_service(self, template: ServiceTemplate, config: ServiceConfig) -> BaseMicroservice:
        """Instantiate service from template"""
        try:
            # Import service class
            module = importlib.import_module(template.module_path)
            service_class = getattr(module, template.class_name)
            
            # Verify it's a BaseMicroservice subclass
            if not issubclass(service_class, BaseMicroservice):
                raise ServiceCreationError(
                    f"Service class {template.class_name} must inherit from BaseMicroservice"
                )
            
            # Create instance
            service_instance = service_class(config)
            
            return service_instance
            
        except ImportError as e:
            raise ServiceCreationError(f"Failed to import service module: {str(e)}")
        except AttributeError as e:
            raise ServiceCreationError(f"Service class not found: {str(e)}")
        except Exception as e:
            raise ServiceCreationError(f"Service instantiation failed: {str(e)}")
    
    def get_service(self, service_name: str) -> Optional[BaseMicroservice]:
        """Get created service by name"""
        return self.created_services.get(service_name)
    
    def list_services(self) -> Dict[str, Dict[str, Any]]:
        """List all created services with their status"""
        services_info = {}
        
        for name, service in self.created_services.items():
            services_info[name] = {
                "status": service.status.value,
                "config": self.service_configs[name].dict(),
                "uptime": (datetime.utcnow() - service.start_time).total_seconds(),
                "service_id": service.service_id
            }
        
        return services_info
    
    def list_templates(self) -> Dict[str, Dict[str, Any]]:
        """List all available templates"""
        templates_info = {}
        
        for name, template in self.templates.items():
            templates_info[name] = {
                "type": template.type.value,
                "class_name": template.class_name,
                "module_path": template.module_path,
                "required_dependencies": template.required_dependencies,
                "optional_dependencies": template.optional_dependencies
            }
        
        return templates_info
    
    def register_template(self, template: ServiceTemplate):
        """Register a new service template"""
        self.templates[template.name] = template
        logger.info(f"Registered new template: {template.name}")
    
    def remove_service(self, service_name: str) -> bool:
        """Remove and cleanup a service"""
        if service_name not in self.created_services:
            logger.warning(f"Service '{service_name}' not found")
            return False
        
        try:
            service = self.created_services[service_name]
            
            # Cleanup service
            if hasattr(service, 'cleanup_connections'):
                # This would need to be called in async context in real implementation
                logger.info(f"Service '{service_name}' cleanup initiated")
            
            # Remove from tracking
            del self.created_services[service_name]
            del self.service_configs[service_name]
            
            logger.info(f"Removed service: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove service '{service_name}': {str(e)}")
            return False
    
    def create_service_cluster(
        self,
        cluster_config: Dict[str, Any]
    ) -> Dict[str, BaseMicroservice]:
        """Create a cluster of related services"""
        services = {}
        
        try:
            # Create services in dependency order
            for service_def in cluster_config.get("services", []):
                service_name = service_def["name"]
                template_name = service_def["template"]
                config_overrides = service_def.get("config", {})
                dependencies = service_def.get("dependencies", [])
                
                service = self.create_service(
                    service_name, template_name, config_overrides, dependencies
                )
                services[service_name] = service
            
            logger.info(f"Created service cluster with {len(services)} services")
            return services
            
        except Exception as e:
            logger.error(f"Failed to create service cluster: {str(e)}")
            # Cleanup created services
            for service_name in services:
                self.remove_service(service_name)
            raise ServiceCreationError(f"Cluster creation failed: {str(e)}")
    
    def get_factory_stats(self) -> Dict[str, Any]:
        """Get factory statistics"""
        total_services = len(self.created_services)
        healthy_services = sum(
            1 for service in self.created_services.values() 
            if service.status == ServiceStatus.HEALTHY
        )
        
        service_types = {}
        for service in self.created_services.values():
            service_type = type(service).__name__
            service_types[service_type] = service_types.get(service_type, 0) + 1
        
        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "total_templates": len(self.templates),
            "environment": self.config.environment.value,
            "service_types": service_types,
            "factory_uptime": datetime.utcnow().isoformat()
        }


def create_service_factory(
    environment: str = "development",
    config_overrides: Optional[Dict[str, Any]] = None
) -> ServiceFactory:
    """Factory function to create configured ServiceFactory"""
    
    factory_config_data = {
        "environment": DeploymentEnvironment(environment),
        "enable_auto_discovery": True,
        "enable_health_monitoring": True,
        "enable_metrics_collection": True
    }
    
    if config_overrides:
        factory_config_data.update(config_overrides)
    
    factory_config = ServiceFactoryConfig(**factory_config_data)
    return ServiceFactory(factory_config)


# Example usage patterns
def create_microservices_cluster_example():
    """Example of creating a microservices cluster"""
    
    # Initialize factory
    factory = create_service_factory("development")
    
    # Define cluster configuration
    cluster_config = {
        "services": [
            {
                "name": "user-service",
                "template": "rest_api",
                "config": {"port": 8001},
                "dependencies": []
            },
            {
                "name": "notification-service", 
                "template": "background_worker",
                "config": {"concurrency": 2},
                "dependencies": ["user-service"]
            },
            {
                "name": "analytics-service",
                "template": "event_processor",
                "config": {"port": 8003},
                "dependencies": ["user-service"]
            }
        ]
    }
    
    # Create cluster
    try:
        services = factory.create_service_cluster(cluster_config)
        logger.info(f"Created cluster with services: {list(services.keys())}")
        return services
    except Exception as e:
        logger.error(f"Cluster creation failed: {str(e)}")
        return {}


if __name__ == "__main__":
    # Example usage
    services = create_microservices_cluster_example()