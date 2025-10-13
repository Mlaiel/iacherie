#!/usr/bin/env python3
"""
🏭 Microservices Templates - IA Chérie Enterprise
==============================================
Point d'entrée principal pour templates microservices.
Factory patterns + template discovery + code generation.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Microservices Templates
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture microservices et tous ses templates sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, 
distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est 
STRICTEMENT INTERDITE et sera poursuivie en justice avec la PLEINE RIGUEUR de la loi.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Type, Any
from datetime import datetime

# Core imports
from .service_template import EnterpriseServiceBase, ServiceConfig
from . import (
    TEMPLATES_REGISTRY,
    get_template,
    get_available_templates,
    TemplateFactory
)

# Template imports with error handling
try:
    from .api_service_template import APIServiceTemplate
    from .message_service_template import MessageServiceTemplate
    from .data_service_template import DataServiceTemplate
    from .ml_service_template import MLServiceTemplate
    from .authentication_service_template import AuthServiceTemplate
    from .monitoring_service_template import MonitoringServiceTemplate
    from .notification_service_template import NotificationServiceTemplate
    from .cache_service_template import CacheServiceTemplate
    TEMPLATES_LOADED = True
except ImportError as e:
    logging.warning(f"Some templates could not be loaded: {e}")
    TEMPLATES_LOADED = False

# Template factory configuration
TEMPLATE_FACTORY_CONFIG = {
    'base_template': EnterpriseServiceBase,
    'default_config': ServiceConfig,
    'template_discovery': True,
    'code_generation': True,
    'validation_enabled': True,
    'auto_import': True,
    'enterprise_features': True
}

# Set up logging
logger = logging.getLogger(__name__)


class EnterpriseTemplateFactory:
    """
    🏭 Factory enterprise pour création templates microservices.
    
    Features:
    - Template discovery automatique
    - Code generation depuis templates
    - Validation configuration enterprise
    - Pattern enforcement
    - Observability intégrée
    """
    
    def __init__(self):
        """Initialize enterprise template factory."""
        self.templates = TEMPLATES_REGISTRY.copy()
        self.generated_services: Dict[str, EnterpriseServiceBase] = {}
        self.factory_metrics = {
            'services_created': 0,
            'templates_used': set(),
            'creation_errors': 0,
            'validation_errors': 0
        }
        
        logger.info(f"🏭 Enterprise Template Factory initialized with {len(self.templates)} templates")
    
    def create_service_from_template(self, template_type: str, config: Dict[str, Any]) -> Optional[EnterpriseServiceBase]:
        """
        Création service depuis template avec validation enterprise.
        
        Args:
            template_type: Type de template ('api', 'messaging', 'data', etc.)
            config: Configuration du service
        
        Returns:
            Instance du service créé ou None si erreur
        """
        try:
            # Validate template type
            if template_type not in self.templates:
                logger.error(f"Template type '{template_type}' not available. Available: {list(self.templates.keys())}")
                self.factory_metrics['validation_errors'] += 1
                return None
            
            # Create service config
            service_config = self._create_service_config(config)
            if not service_config:
                self.factory_metrics['validation_errors'] += 1
                return None
            
            # Get template class
            template_class = self.templates[template_type]
            
            # Create service instance
            service_instance = template_class(service_config)
            
            # Store generated service
            service_id = f"{template_type}_{service_config.service_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.generated_services[service_id] = service_instance
            
            # Update metrics
            self.factory_metrics['services_created'] += 1
            self.factory_metrics['templates_used'].add(template_type)
            
            logger.info(f"✅ Service created successfully: {service_config.service_name} ({template_type})")
            return service_instance
            
        except Exception as e:
            logger.error(f"❌ Failed to create service from template '{template_type}': {e}")
            self.factory_metrics['creation_errors'] += 1
            return None
    
    def generate_service_code(self, template_type: str, service_name: str, config: Optional[Dict] = None) -> Optional[str]:
        """
        Génération code service depuis template.
        
        Args:
            template_type: Type de template
            service_name: Nom du service
            config: Configuration optionnelle
        
        Returns:
            Code généré ou None si erreur
        """
        try:
            if template_type not in self.templates:
                logger.error(f"Template type '{template_type}' not available")
                return None
            
            # Generate service code
            code_template = self._get_code_template(template_type)
            if not code_template:
                return None
            
            # Replace placeholders
            generated_code = code_template.format(
                service_name=service_name,
                template_type=template_type,
                timestamp=datetime.now().isoformat(),
                author="Fahed Mlaiel (mlaiel@live.de)",
                config=config or {}
            )
            
            logger.info(f"✅ Code generated for service: {service_name} ({template_type})")
            return generated_code
            
        except Exception as e:
            logger.error(f"❌ Failed to generate code for '{service_name}': {e}")
            return None
    
    def discover_available_templates(self) -> List[str]:
        """
        Découverte templates disponibles avec metadata.
        
        Returns:
            Liste des templates avec informations détaillées
        """
        try:
            templates_info = []
            
            for template_name, template_class in self.templates.items():
                template_info = {
                    'name': template_name,
                    'class': template_class.__name__,
                    'module': template_class.__module__,
                    'description': self._get_template_description(template_class),
                    'features': self._get_template_features(template_class),
                    'enterprise_ready': True
                }
                templates_info.append(template_info)
            
            logger.info(f"📋 Discovered {len(templates_info)} templates")
            return templates_info
            
        except Exception as e:
            logger.error(f"❌ Template discovery failed: {e}")
            return []
    
    def validate_template_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validation configuration template enterprise.
        
        Args:
            config: Configuration à valider
        
        Returns:
            True si configuration valide
        """
        try:
            # Basic validation
            required_fields = ['service_name', 'service_version']
            for field in required_fields:
                if field not in config:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Service name validation
            service_name = config['service_name']
            if not service_name or len(service_name) < 3:
                logger.error("Service name must be at least 3 characters")
                return False
            
            # Port validation
            port = config.get('port', 8000)
            if not isinstance(port, int) or port <= 0 or port > 65535:
                logger.error("Port must be between 1 and 65535")
                return False
            
            # Enterprise validation
            if not self._validate_enterprise_requirements(config):
                return False
            
            logger.info(f"✅ Configuration validation passed for: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration validation failed: {e}")
            return False
    
    def get_factory_metrics(self) -> Dict[str, Any]:
        """Get factory performance metrics."""
        return {
            'services_created': self.factory_metrics['services_created'],
            'templates_available': len(self.templates),
            'templates_used': list(self.factory_metrics['templates_used']),
            'creation_errors': self.factory_metrics['creation_errors'],
            'validation_errors': self.factory_metrics['validation_errors'],
            'generated_services_count': len(self.generated_services),
            'enterprise_features_enabled': TEMPLATE_FACTORY_CONFIG['enterprise_features']
        }
    
    def _create_service_config(self, config: Dict[str, Any]) -> Optional[ServiceConfig]:
        """Create ServiceConfig from dictionary."""
        try:
            if not self.validate_template_configuration(config):
                return None
            
            return ServiceConfig(
                service_name=config['service_name'],
                service_version=config.get('service_version', '1.0.0'),
                description=config.get('description', ''),
                port=config.get('port', 8000),
                health_check_interval=config.get('health_check_interval', 30),
                max_retries=config.get('max_retries', 3),
                timeout=config.get('timeout', 30),
                tags=config.get('tags', []),
                dependencies=config.get('dependencies', [])
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create service config: {e}")
            return None
    
    def _get_code_template(self, template_type: str) -> Optional[str]:
        """Get code template for service generation."""
        code_templates = {
            'api': '''#!/usr/bin/env python3
"""
Generated API Service: {service_name}
====================================
Generated from template: {template_type}
Author: {author}
Generated: {timestamp}
"""

from microservices._templates import APIServiceTemplate, ServiceConfig

class {service_name}Service(APIServiceTemplate):
    """Generated API service implementation."""
    
    async def configure_custom_routes(self):
        """Configure service-specific routes."""
        return []
    
    async def configure_custom_middleware(self):
        """Configure service-specific middleware."""
        return []

# Service configuration
config = ServiceConfig(
    service_name="{service_name}",
    service_version="1.0.0",
    description="Generated API service",
    port=8000
)

# Create service instance
service = {service_name}Service(config)

if __name__ == "__main__":
    import asyncio
    
    async def main():
        await service.start()
        print(f"🚀 {service_name} service started on port {config.port}")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await service.stop()
            print(f"🛑 {service_name} service stopped")
    
    asyncio.run(main())
''',
            'messaging': '''#!/usr/bin/env python3
"""
Generated Messaging Service: {service_name}
==========================================
Generated from template: {template_type}
Author: {author}
Generated: {timestamp}
"""

from microservices._templates import MessageServiceTemplate, ServiceConfig

class {service_name}Service(MessageServiceTemplate):
    """Generated messaging service implementation."""
    
    async def configure_custom_handlers(self):
        """Configure service-specific event handlers."""
        return []
    
    async def configure_custom_brokers(self):
        """Configure service-specific message brokers."""
        return {{}}

# Service configuration
config = ServiceConfig(
    service_name="{service_name}",
    service_version="1.0.0",
    description="Generated messaging service",
    port=8001
)

# Create service instance
service = {service_name}Service(config)

if __name__ == "__main__":
    import asyncio
    
    async def main():
        await service.start()
        print(f"📨 {service_name} service started")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await service.stop()
            print(f"🛑 {service_name} service stopped")
    
    asyncio.run(main())
'''
        }
        
        return code_templates.get(template_type)
    
    def _get_template_description(self, template_class: Type) -> str:
        """Get template description from docstring."""
        doc = template_class.__doc__
        if doc:
            # Extract first line of docstring
            lines = doc.strip().split('\n')
            return lines[0].strip() if lines else "No description available"
        return "No description available"
    
    def _get_template_features(self, template_class: Type) -> List[str]:
        """Extract features from template docstring."""
        doc = template_class.__doc__
        features = []
        
        if doc and "Features:" in doc:
            lines = doc.split("Features:")[1].split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("-"):
                    features.append(line[1:].strip())
                elif not line or line.startswith("*"):
                    break
        
        return features
    
    def _validate_enterprise_requirements(self, config: Dict[str, Any]) -> bool:
        """Validate enterprise-specific requirements."""
        # Check for required enterprise fields
        enterprise_fields = ['service_name', 'service_version']
        for field in enterprise_fields:
            if field not in config:
                logger.error(f"Enterprise requirement missing: {field}")
                return False
        
        # Validate naming conventions
        service_name = config['service_name']
        if not service_name.replace('_', '').replace('-', '').isalnum():
            logger.error("Service name must contain only alphanumeric characters, hyphens, and underscores")
            return False
        
        return True


# Global factory instance
template_factory = EnterpriseTemplateFactory()


def create_service(template_type: str, config: Dict[str, Any]) -> Optional[EnterpriseServiceBase]:
    """
    Create service using template factory.
    
    Args:
        template_type: Type of template to use
        config: Service configuration
    
    Returns:
        Created service instance
    """
    return template_factory.create_service_from_template(template_type, config)


def generate_code(template_type: str, service_name: str, config: Optional[Dict] = None) -> Optional[str]:
    """
    Generate service code from template.
    
    Args:
        template_type: Type of template
        service_name: Name of the service
        config: Optional configuration
    
    Returns:
        Generated code
    """
    return template_factory.generate_service_code(template_type, service_name, config)


def list_templates() -> List[str]:
    """
    List available templates.
    
    Returns:
        List of available template names
    """
    return list(template_factory.templates.keys())


def get_template_info(template_type: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a template.
    
    Args:
        template_type: Type of template
    
    Returns:
        Template information dictionary
    """
    if template_type not in template_factory.templates:
        return None
    
    template_class = template_factory.templates[template_type]
    return {
        'name': template_type,
        'class': template_class.__name__,
        'module': template_class.__module__,
        'description': template_factory._get_template_description(template_class),
        'features': template_factory._get_template_features(template_class)
    }


async def demo_templates():
    """Demo function showing template usage."""
    print("🏭 IA Chérie Microservices Templates Demo")
    print("=" * 50)
    
    # List available templates
    templates = list_templates()
    print(f"📋 Available templates: {', '.join(templates)}")
    
    # Show template info
    for template in templates[:3]:  # Show first 3
        info = get_template_info(template)
        if info:
            print(f"\n📦 {template.upper()} Template:")
            print(f"   Description: {info['description']}")
            print(f"   Features: {len(info['features'])} enterprise features")
    
    # Create demo service
    config = {
        'service_name': 'demo_api_service',
        'service_version': '1.0.0',
        'description': 'Demo API service',
        'port': 8080
    }
    
    service = create_service('api', config)
    if service:
        print(f"\n✅ Demo service created: {service.config.service_name}")
        print(f"   Status: {service.status}")
        print(f"   Service ID: {service.service_id}")
    
    # Show factory metrics
    metrics = template_factory.get_factory_metrics()
    print(f"\n📊 Factory Metrics:")
    print(f"   Services created: {metrics['services_created']}")
    print(f"   Templates available: {metrics['templates_available']}")
    print(f"   Enterprise features: {metrics['enterprise_features_enabled']}")


if __name__ == "__main__":
    # Demo usage
    print("🏭 IA Chérie Microservices Templates - Enterprise Factory")
    print(f"Author: Fahed Mlaiel (mlaiel@live.de)")
    print(f"Templates loaded: {TEMPLATES_LOADED}")
    print(f"Available templates: {len(TEMPLATES_REGISTRY)}")
    
    # Run demo
    asyncio.run(demo_templates())